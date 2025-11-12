"""cleanup old venvs"""

import datetime
import shutil
import sys
from pathlib import Path

import click
from loguru import logger

from constants import CACHE_DIRS, PACKAGE_FILES


def is_venv_directory(directory_path: Path) -> bool:
    """Determine if the specified directory is a virtual environment or cache directory

    Virtual environment determination method:
    - pyvenv.cfg file exists
    - bin/activate or Scripts/activate.bat exists

    Cache directory determination method:
    - Directory name is .mypy_cache or .ruff_cache

    Args:
        directory_path (Path): Directory path to check

    Returns:
        bool: True if the directory is a virtual environment or cache directory, False otherwise

    """
    path = Path(directory_path)

    # Check if it's a cache directory
    if path.name in CACHE_DIRS:
        return True

    # check if pyvenv.cfg exists
    if (path / "pyvenv.cfg").exists():
        return True

    # check if bin/activate exists (Unix-like)
    if (path / "bin" / "activate").exists():
        return True

    # check if Scripts/activate.bat exists (Windows)
    if (path / "Scripts" / "activate.bat").exists():
        return True

    return False


def has_python_package_files(directory_path: Path) -> bool:
    """Check if directory has python package management files

    Args:
        directory_path (Path): Directory path to check

    Returns:
        bool: True if directory has package management files, False otherwise
    """
    if directory_path.parents[0].name == ".tox":
        return True

    # Check parent directory for package management files
    parent_dir = directory_path.parent

    for file in PACKAGE_FILES:
        if (parent_dir / file).exists():
            return True

    return False


def get_last_modified_date(directory_path: Path) -> datetime.datetime:
    """Get the last modified date of the directory

    Args:
        directory_path (Path): Directory path to get the last modified date

    Returns:
        datetime.datetime: Last modified date
    """
    return datetime.datetime.fromtimestamp(directory_path.stat().st_mtime)


def should_process_directory(dir_path: Path) -> bool:
    """Check if directory should be processed for deletion.

    Args:
        dir_path (Path): Directory path to check

    Returns:
        bool: True if directory should be processed, False otherwise
    """
    # Check if it's a virtual environment or cache directory
    if not is_venv_directory(dir_path):
        return False

    # Cache directories are always processed
    if dir_path.name in CACHE_DIRS:
        return True

    # For venvs, check if it has python package management files
    if not has_python_package_files(dir_path):
        logger.debug(
            f"Skipping {dir_path}: No package management files found",
        )
        return False

    return True


def log_directory_info(
    dir_path: Path,
    last_modified: datetime.datetime,
    dir_size: int,
    dry_run: bool,
) -> None:
    """Log information about a directory to be removed.

    Args:
        dir_path (Path): Directory path
        last_modified (datetime.datetime): Last modified date
        dir_size (int): Directory size in bytes
        dry_run (bool): True if dry run, False if actually remove
    """
    size_mb = dir_size / (1024 * 1024)

    logger.info(f"🔎 Found old virtual environment: {dir_path}")
    logger.info(
        f"   📅 Last modified: {last_modified.strftime('%Y-%m-%d')}",
    )

    if size_mb > 1000:
        size_gb = size_mb / 1024
        logger.info(f"   💾 Size: {size_gb:.2f} GB")
    else:
        logger.info(f"   💾 Size: {size_mb:.2f} MB")

    if dry_run:
        logger.info("   🚫 Dry run: not deleted")


def remove_directory(dir_path: Path) -> bool:
    """Remove directory and log the result.

    Args:
        dir_path (Path): Directory path to remove

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("   🗑️ Deleting...")
        shutil.rmtree(dir_path)
        logger.info("   ✅ Deleted")
        return True
    except Exception as e:
        logger.error(f"   ❌ Delete error: {e}")
        return False


def search_and_remove_old_venvs(
    base_dir: Path,
    days_threshold: int,
    dry_run: bool = True,
) -> tuple[int, int]:
    """Search and remove old venvs

    Args:
        base_dir (Path): Base directory to start search
        days_threshold (int): Days threshold to remove old venvs
        dry_run (bool): True if dry run, False if actually remove

    Returns:
        tuple: (number of removed venvs, total size freed (bytes))
    """
    cutoff_date = datetime.datetime.now() - datetime.timedelta(
        days=days_threshold,
    )
    removed_count = 0
    total_size_freed = 0

    logger.info(
        f"Searching for virtual environments older than {cutoff_date.strftime('%Y-%m-%d')}",
    )
    logger.info(f"Dry run: {'yes' if dry_run else 'no'}\n")

    for dir_path in sorted(base_dir.glob("**/"), key=lambda p: len(str(p))):
        if not dir_path.is_dir() or dir_path.is_symlink():
            continue

        # Check if directory should be processed
        if not should_process_directory(dir_path):
            continue

        # Get directory information
        last_modified = get_last_modified_date(dir_path)
        dir_size = get_directory_size(dir_path)

        # Check if the directory is older than the threshold
        if last_modified < cutoff_date:
            log_directory_info(dir_path, last_modified, dir_size, dry_run)

            if not dry_run:
                if remove_directory(dir_path):
                    removed_count += 1
                    total_size_freed += dir_size
            else:
                removed_count += 1
                total_size_freed += dir_size

            logger.info("")

    return removed_count, total_size_freed


def get_directory_size(directory_path: Path) -> int:
    """Calculate the total size of the directory (in bytes)

    Args:
        directory_path (Path): Directory path to calculate the total size

    Returns:
        int: Total size of the directory
    """
    total_size = 0
    try:
        for path in directory_path.rglob("*"):
            if path.is_file() and not path.is_symlink():
                total_size += path.stat().st_size
    except (PermissionError, OSError) as e:
        logger.debug(f"Error calculating size for {directory_path}: {e}")
    return total_size


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
    help="Delete virtual environments older than this number of days (default: 180)",
)
@click.option(
    "--execute",
    is_flag=True,
    help="If this flag is specified, actually delete the virtual environments",
)
def main(directory: Path, days: int = 180, execute: bool = False) -> None:
    """Search and remove old venvs

    Args:
        directory (Path): Directory to start search
        days (int, optional): Days threshold to remove old venvs. Defaults to 180.
        execute (bool, optional): True if actually delete the virtual environments, False otherwise. Defaults to False.
    """
    if not directory.exists():
        logger.error(f"Error: '{directory}' is not a valid directory")
        sys.exit(1)

    logger.info(
        f"Searching for virtual environments older than {days} days in '{directory}'...",
    )

    removed_count, total_size_freed = search_and_remove_old_venvs(
        directory,
        days,
        dry_run=not execute,
    )

    size_mb = total_size_freed / (1024 * 1024)  # convert bytes to MB

    logger.info("\nResult summary:")
    logger.info(f"- Detected old virtual environments: {removed_count}")
    if size_mb > 1000:
        size_gb = size_mb / 1024
        logger.info(f"- Freed total capacity: {size_gb:.2f} GB")
    else:
        logger.info(f"- Freed total capacity: {size_mb:.2f} MB")

    if not execute and removed_count > 0:
        logger.info("\nTo actually delete, add the --execute flag")


if __name__ == "__main__":
    main()
