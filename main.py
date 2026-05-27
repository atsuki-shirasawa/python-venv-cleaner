"""Search for and delete old Python virtual environments and caches."""

import datetime
import shutil
import sys
from pathlib import Path

import click
from loguru import logger

from constants import CACHE_DIRS, PACKAGE_FILES

_VENV_MARKERS: tuple[Path, ...] = (
    Path("pyvenv.cfg"),
    Path("bin") / "activate",
    Path("Scripts") / "activate.bat",
)

# Directory names skipped when computing the latest code mtime so that
# tool-managed files don't mask the real source modification time.
_NON_CODE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".tox",
        "__pycache__",
        "node_modules",
    },
)

# Directory names never descended into during the candidate search.
# ``.tox`` is intentionally absent: tox stores venvs inside it that we
# do want to find. Venvs and cache directories are pruned separately
# via ``is_venv_directory()``.
_NEVER_DESCEND_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        "__pycache__",
        "node_modules",
    },
)


def is_venv_directory(directory_path: Path) -> bool:
    """Determine whether the directory is a venv or cache directory.

    A directory is considered a virtual environment when it contains
    any of ``pyvenv.cfg``, ``bin/activate`` or ``Scripts/activate.bat``.
    A directory is considered a cache directory when its name matches
    a known cache name (see ``CACHE_DIRS``).

    Args:
        directory_path: Directory to inspect.

    Returns:
        True if the directory is a virtual environment or cache
        directory, False otherwise.
    """
    if directory_path.name in CACHE_DIRS:
        return True
    return any((directory_path / marker).exists() for marker in _VENV_MARKERS)


def has_python_package_files(directory_path: Path) -> bool:
    """Check whether the parent directory has Python package files.

    Directories whose parent is named ``.tox`` are always treated as if
    package files exist, since tox manages them on behalf of a project.

    Args:
        directory_path: Directory whose parent is inspected.

    Returns:
        True if the parent directory contains any known package
        management file, False otherwise.
    """
    parent = directory_path.parent
    if parent.name == ".tox":
        return True
    return any((parent / file).exists() for file in PACKAGE_FILES)


def get_project_directory(candidate: Path) -> Path:
    """Return the project directory that owns ``candidate``.

    Normally the candidate's parent is the project directory. When the
    candidate sits inside a ``.tox`` tree, the project is one level
    higher because tox manages its own venvs per project.

    Args:
        candidate: A venv or cache directory under evaluation.

    Returns:
        The project directory whose code modification time is relevant.
    """
    parent = candidate.parent
    if parent.name == ".tox":
        return parent.parent
    return parent


def get_latest_code_mtime(
    project_dir: Path,
    cutoff: datetime.datetime | None = None,
) -> datetime.datetime | None:
    """Return the latest mtime of source files under ``project_dir``.

    Subdirectories that look like virtual environments or cache
    directories, plus common tool-managed directories such as ``.git``,
    ``.tox``, ``__pycache__`` and ``node_modules``, are pruned from the
    walk so that auto-regenerated files don't mask the real code
    modification time.

    When ``cutoff`` is given, the walk exits as soon as one file with
    ``mtime >= cutoff`` is seen. This is sound because callers only need
    to know whether the project is older than the cutoff, not its exact
    age, when the project is still active.

    Args:
        project_dir: Project root to scan.
        cutoff: When provided, enables early-exit on the first file
            modified at or after this timestamp.

    Returns:
        ``datetime.datetime`` of the most recently modified source file,
        or ``None`` when no scannable file exists under the directory.
    """
    cutoff_ts = cutoff.timestamp() if cutoff is not None else None
    latest: float | None = None
    for root, dirs, files in project_dir.walk(on_error=lambda _e: None):
        dirs[:] = [
            d
            for d in dirs
            if d not in _NON_CODE_DIRS and not is_venv_directory(root / d)
        ]
        for name in files:
            file_path = root / name
            if file_path.is_symlink():
                continue
            try:
                mtime = file_path.stat().st_mtime
            except OSError:
                continue
            if latest is None or mtime > latest:
                latest = mtime
            if cutoff_ts is not None and mtime >= cutoff_ts:
                return datetime.datetime.fromtimestamp(latest)

    if latest is None:
        return None
    return datetime.datetime.fromtimestamp(latest)


def get_directory_size(directory_path: Path) -> int:
    """Calculate the total size of the directory in bytes.

    Permission errors encountered while walking are logged and skipped
    so that one unreadable subtree does not abort the calculation.

    Args:
        directory_path: Directory to measure.

    Returns:
        Total size in bytes of all regular files under the directory.
    """
    total_size = 0
    try:
        for path in directory_path.rglob("*"):
            if path.is_file() and not path.is_symlink():
                total_size += path.stat().st_size
    except (PermissionError, OSError) as e:
        logger.debug(f"Error calculating size for {directory_path}: {e}")
    return total_size


def format_size(size_bytes: int) -> str:
    """Format a byte count as a human readable string.

    Args:
        size_bytes: Number of bytes.

    Returns:
        Size formatted in GB when the value reaches one gibibyte, in MB
        otherwise (e.g. ``"512.30 MB"`` or ``"1.50 GB"``).
    """
    size_mb = size_bytes / (1024 * 1024)
    if size_mb >= 1024:
        return f"{size_mb / 1024:.2f} GB"
    return f"{size_mb:.2f} MB"


def should_process_directory(dir_path: Path) -> bool:
    """Decide whether the directory is a deletion candidate.

    A directory qualifies when it looks like a virtual environment or a
    cache directory. Virtual environments additionally require Python
    package files in the parent directory, while cache directories are
    always considered.

    Args:
        dir_path: Directory to evaluate.

    Returns:
        True if the directory should be processed for deletion, False
        otherwise.
    """
    if not is_venv_directory(dir_path):
        return False

    if dir_path.name in CACHE_DIRS:
        return True

    if not has_python_package_files(dir_path):
        logger.debug(
            f"Skipping {dir_path}: No package management files found",
        )
        return False

    return True


def log_directory_info(
    dir_path: Path,
    code_mtime: datetime.datetime,
    dir_size: int,
    dry_run: bool,
) -> None:
    """Log details about a directory selected for removal.

    Args:
        dir_path: Directory being reported.
        code_mtime: Latest mtime of source code in the owning project.
        dir_size: Directory size in bytes.
        dry_run: When True, an extra "not deleted" line is logged.
    """
    logger.info(f"🔎 Found old directory: {dir_path}")
    logger.info(
        f"   📅 Last code change: {code_mtime.strftime('%Y-%m-%d')}",
    )
    logger.info(f"   💾 Size: {format_size(dir_size)}")
    if dry_run:
        logger.info("   🚫 Dry run: not deleted")


def remove_directory(dir_path: Path) -> bool:
    """Delete a directory recursively and log the outcome.

    Args:
        dir_path: Directory to remove.

    Returns:
        True on successful removal, False when an ``OSError`` occurs.
    """
    try:
        logger.info("   🗑️ Deleting...")
        shutil.rmtree(dir_path)
        logger.info("   ✅ Deleted")
        return True
    except OSError as e:
        logger.error(f"   ❌ Delete error: {e}")
        return False


def search_and_remove_old_venvs(
    base_dir: Path,
    days_threshold: int,
    dry_run: bool = True,
) -> tuple[int, int]:
    """Search a tree and remove venvs and caches older than the threshold.

    Args:
        base_dir: Directory to recursively search.
        days_threshold: Age in days above which directories are removed.
        dry_run: When True, candidates are reported but not deleted.

    Returns:
        Tuple of ``(directories_processed, bytes_freed)``. In dry-run
        mode these reflect what would have been removed.
    """
    cutoff_date = datetime.datetime.now() - datetime.timedelta(
        days=days_threshold,
    )
    removed_count = 0
    total_size_freed = 0
    code_mtime_cache: dict[Path, datetime.datetime | None] = {}

    logger.info(
        "Searching for projects whose code has not been modified since "
        f"{cutoff_date.strftime('%Y-%m-%d')}",
    )
    logger.info(f"Dry run: {'yes' if dry_run else 'no'}\n")

    for root, dirs, _files in base_dir.walk(on_error=lambda _e: None):
        for d in dirs:
            sub = root / d
            if not should_process_directory(sub):
                continue

            project_dir = get_project_directory(sub)
            if project_dir not in code_mtime_cache:
                code_mtime_cache[project_dir] = get_latest_code_mtime(
                    project_dir,
                    cutoff_date,
                )
            code_mtime = code_mtime_cache[project_dir]
            if code_mtime is None or code_mtime >= cutoff_date:
                continue

            dir_size = get_directory_size(sub)
            log_directory_info(sub, code_mtime, dir_size, dry_run)

            if dry_run or remove_directory(sub):
                removed_count += 1
                total_size_freed += dir_size

            logger.info("")

        # Don't descend into venvs, caches, or other noisy trees: their
        # contents are never candidates and they can be huge.
        dirs[:] = [
            d
            for d in dirs
            if d not in _NEVER_DESCEND_NAMES
            and not is_venv_directory(root / d)
        ]

    return removed_count, total_size_freed


@click.command()
@click.option(
    "--directory",
    type=Path,
    required=True,
    help="Directory to start search",
)
@click.option(
    "--days",
    type=int,
    default=180,
    help=(
        "Delete virtual environments older than this number of days "
        "(default: 180)"
    ),
)
@click.option(
    "--execute",
    is_flag=True,
    help=(
        "If this flag is specified, actually delete the virtual "
        "environments"
    ),
)
def main(directory: Path, days: int = 180, execute: bool = False) -> None:
    """Search and remove old venvs.

    Args:
        directory: Directory to start search.
        days: Age threshold in days. Defaults to 180.
        execute: When True, actually delete the directories. When False
            (the default), runs in dry-run mode.
    """
    if not directory.exists():
        logger.error(f"Error: '{directory}' is not a valid directory")
        sys.exit(1)

    logger.info(
        f"Searching for projects whose code has not been modified "
        f"for {days} days in '{directory}'...",
    )

    removed_count, total_size_freed = search_and_remove_old_venvs(
        directory,
        days,
        dry_run=not execute,
    )

    logger.info("\nResult summary:")
    logger.info(f"- Detected old virtual environments: {removed_count}")
    logger.info(f"- Freed total capacity: {format_size(total_size_freed)}")

    if not execute and removed_count > 0:
        logger.info("\nTo actually delete, add the --execute flag")


if __name__ == "__main__":
    main()
