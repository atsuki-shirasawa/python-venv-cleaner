"""Constants used to identify cleanup candidates."""

CACHE_DIRS: frozenset[str] = frozenset(
    {
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
    },
)

PACKAGE_FILES: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "poetry.lock",
        "uv.lock",
        "requirements.txt",
        "requirements-dev.txt",
        "setup.py",
        "setup.cfg",
        "Pipfile",
        "Pipfile.lock",
        "environment.yml",
        "conda-env.yml",
    },
)
