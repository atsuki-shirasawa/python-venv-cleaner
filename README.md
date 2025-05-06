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

- [uv](https://docs.astral.sh/uv//)

## Usage

1. Install dependencies

   ```bash
   uv sync
   ```

2. Run the script

   ```bash
   uv run main.py --directory <path> --days <days> --execute
   ```

   - `--directory`: Path to the directory to search for virtual environments.
   - `--days`: Days threshold to remove old venvs. Defaults to 180 days.
   - `--execute`: If this flag is specified, actually delete the virtual environments.

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

### Search and delete old venvs in the current directory

```bash
uv run main.py --directory ../dev --days 100 --execute
```
