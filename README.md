<!-- @format -->

# Python Virtual Environment Cleaner

<p align="center">
  <img src="./docs/logo.png" width="360">
</p>

## Overview

This script searches for old virtual environments and deletes them.

## Features

- Search for old virtual environments in a given directory.
- Delete old virtual environments.
- Dry run mode.

### Deletion Criteria

A directory is considered for deletion when:

1. It is identified as a virtual environment if:

   - It contains a `pyvenv.cfg` file, or
   - It contains `bin/activate` (Unix-like systems), or
   - It contains `Scripts/activate.bat` (Windows systems)

2. OR it is a cache directory:

   - `.mypy_cache`
   - `.ruff_cache`
   - `.pytest_cache`

3. AND it has Python package management files in its parent directory:

   - `pyproject.toml`
   - `poetry.lock`
   - `uv.lock`
   - `requirements.txt`
   - `setup.py`
   - `setup.cfg`
   - `requirements-dev.txt`
   - `Pipfile`
   - `Pipfile.lock`
   - `environment.yml`
   - `conda-env.yml`
   - Or if it's inside a `.tox` directory

4. AND it was last modified more than the specified number of days ago (default: 180 days).

## Requirements

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) - Python package manager

## Installation

Install dependencies:

```bash
uv sync
```

## Usage

### Basic Usage

Dry run (preview what will be deleted):

```bash
uv run main.py --directory <path> --days <days>
```

Execute deletions:

```bash
uv run main.py --directory <path> --days <days> --execute
```

### Options

- `--directory`: Path to the directory to search for virtual environments (required)
- `--days`: Days threshold to remove old venvs (default: 180)
- `--execute`: Actually delete the virtual environments (without this flag, it's a dry run)

## Examples

### Dry run

Example:

```bash
uv run main.py --directory ../dev --days 100
```

Log Example:

```bash
2025-05-07 08:50:00.229 | INFO     | __main__:main:208 - Searching for virtual environments older than 100 days in '..'...
2025-05-07 08:50:00.229 | INFO     | __main__:search_and_remove_old_venvs:107 - Searching for virtual environments older than 2025-01-27
2025-05-07 08:50:00.229 | INFO     | __main__:search_and_remove_old_venvs:110 - Dry run: yes

2025-05-07 08:50:16.230 | INFO     | __main__:search_and_remove_old_venvs:135 - 🔎 Found old virtual environment: ../hoge-project/app/.venv
2025-05-07 08:50:16.231 | INFO     | __main__:search_and_remove_old_venvs:136 -    📅 Last modified: 2025-01-09
2025-05-07 08:50:16.231 | INFO     | __main__:search_and_remove_old_venvs:139 -    💾 Size: 1028.01 MB
2025-05-07 08:50:16.231 | INFO     | __main__:search_and_remove_old_venvs:151 -    🚫 Dry run: not deleted
2025-05-07 08:50:16.231 | INFO     | __main__:search_and_remove_old_venvs:154 -
2025-05-07 08:50:16.947 | INFO     | __main__:search_and_remove_old_venvs:135 - 🔎 Found old virtual environment: ../hoge-project/app/.mypy_cache
2025-05-07 08:50:16.947 | INFO     | __main__:search_and_remove_old_venvs:136 -    📅 Last modified: 2025-01-09
2025-05-07 08:50:16.947 | INFO     | __main__:search_and_remove_old_venvs:139 -    💾 Size: 356.78 MB
2025-05-07 08:50:16.947 | INFO     | __main__:search_and_remove_old_venvs:151 -    🚫 Dry run: not deleted
2025-05-07 08:50:16.948 | INFO     | __main__:search_and_remove_old_venvs:154 -
2025-05-07 08:50:17.221 | INFO     | __main__:search_and_remove_old_venvs:135 - 🔎 Found old virtual environment: ../hoge-project/app/.mypy_cache
2025-05-07 08:50:17.221 | INFO     | __main__:search_and_remove_old_venvs:136 -    📅 Last modified: 2025-01-24
2025-05-07 08:50:17.221 | INFO     | __main__:search_and_remove_old_venvs:139 -    💾 Size: 81.31 MB
2025-05-07 08:50:17.221 | INFO     | __main__:search_and_remove_old_venvs:151 -    🚫 Dry run: not deleted
2025-05-07 08:50:17.221 | INFO     | __main__:search_and_remove_old_venvs:154 -
...
2025-05-07 08:51:04.599 | INFO     | __main__:main:220 -
Result summary:
2025-05-07 08:51:04.600 | INFO     | __main__:main:221 - - Detected old virtual environments: 63
2025-05-07 08:51:04.600 | INFO     | __main__:main:222 - - Freed total capacity: 13468.58 MB
```

### Execute deletion

```bash
uv run main.py --directory ../dev --days 100 --execute
```

## Development

### Code Quality

Lint code with Ruff:

```bash
uv run ruff check .
```

Auto-fix linting issues:

```bash
uv run ruff check --fix .
```

Format code with Black:

```bash
uv run black .
```

Type check with mypy:

```bash
uv run mypy .
```

Run all checks with tox:

```bash
uv run tox
```

### Project Structure

```
.
├── main.py         # Core logic and CLI entry point
├── constants.py    # Configuration constants (cache dirs, package files)
└── pyproject.toml  # Project configuration and dependencies
```

### Code Standards

- Python 3.12+
- Type hints required for all functions
- Google-style docstrings
- Line length: 79 characters
- Use `pathlib.Path` for file operations
