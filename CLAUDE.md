<!-- @format -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python Virtual Environment Cleaner is a CLI tool that searches for and deletes old Python virtual environments and cache directories to free up disk space.

The tool identifies virtual environments and cache directories based on specific markers (pyvenv.cfg, bin/activate, Scripts/activate.bat, or cache directory names) and only deletes them if:

1. They are in a directory with Python package management files (pyproject.toml, requirements.txt, etc.)
2. They haven't been modified in a specified number of days (default: 180)

## Development Setup

Install dependencies using uv:

```bash
uv sync
```

## Running the Tool

Dry run (preview deletions without executing):

```bash
uv run main.py --directory <path> --days <days>
```

Execute deletions:

```bash
uv run main.py --directory <path> --days <days> --execute
```

## Code Quality Commands

Linting with Ruff:

```bash
uv run ruff check .
```

Auto-fix Ruff issues:

```bash
uv run ruff check --fix .
```

Format code with Black:

```bash
uv run black .
```

Type checking with mypy:

```bash
uv run mypy .
```

Run all checks with tox:

```bash
uv run tox
```

## Architecture

The codebase consists of three main files:

- `main.py`: Core logic with CLI entry point using Click
- `constants.py`: Configuration for cache directories and package file patterns
- `pyproject.toml`: Project configuration, dependencies, and tool settings

Key functions in main.py:

- `is_venv_directory()`: Identifies virtual environments and cache directories
- `has_python_package_files()`: Validates parent directory contains Python project files
- `get_last_modified_date()`: Retrieves directory modification timestamp
- `get_directory_size()`: Calculates total directory size recursively
- `search_and_remove_old_venvs()`: Main search and deletion logic with dry-run support

The deletion logic uses a recursive glob pattern (`**/`) to traverse directories, checks each for venv/cache markers, validates the presence of package management files in the parent directory, and removes directories older than the threshold.

## Code Standards

This project enforces strict type hints and follows Google-style docstrings:

- All functions must have type annotations (enforced by mypy's `disallow_untyped_defs`)
- Line length: 79 characters (Black and Ruff)
- Python version: 3.12+
- Docstring convention: Google style (enforced by Ruff pydocstyle)
- Maximum cyclomatic complexity: 10 (enforced by Ruff mccabe)
- Use pathlib.Path for all file operations (enforced by Ruff PTH rules)

The Ruff configuration includes extensive linting rules (pycodestyle, pyflakes, flake8-bugbear, flake8-bandit, isort, pydocstyle, pyupgrade) with auto-fix disabled for unused imports and variables to prevent accidental code removal.
