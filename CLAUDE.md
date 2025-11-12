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
- `should_process_directory()`: Determines if a directory should be processed for deletion
- `log_directory_info()`: Logs information about directories to be removed
- `remove_directory()`: Handles directory deletion with error handling and logging
- `search_and_remove_old_venvs()`: Main search and deletion logic with dry-run support

The deletion logic uses a recursive glob pattern (`**/`) to traverse directories, checks each for venv/cache markers, validates the presence of package management files in the parent directory, and removes directories older than the threshold. The code is organized into separate functions for better maintainability and readability.

## Code Standards

This project enforces strict type hints and follows Google-style docstrings:

- All functions must have type annotations (enforced by mypy's `disallow_untyped_defs`)
- Line length: 79 characters (Black and Ruff)
- Python version: 3.12+
- Docstring convention: Google style (enforced by Ruff pydocstyle)
- Maximum cyclomatic complexity: 10 (enforced by Ruff mccabe)
- Use pathlib.Path for all file operations (enforced by Ruff PTH rules)

The Ruff configuration includes extensive linting rules (pycodestyle, pyflakes, flake8-bugbear, flake8-bandit, isort, pydocstyle, pyupgrade) with auto-fix disabled for unused imports and variables to prevent accidental code removal.

## Git Workflow

### Commit Messages

Follow Conventional Commits specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Branch Naming

Pattern: `{type}/{issue-number}-{short-description}`

Examples:
- `feature/123-add-user-authentication`
- `fix/456-handle-permission-errors`
- `docs/789-update-readme`

### Pull Requests

**Title Format**: `{type}({scope}): {description}`

Example: `feat(auth): implement JWT authentication`

**Description**: Follow the template in `.github/pull_request_template.md` when creating pull requests. The template includes sections for:
- Overview
- Related Issues
- Type of Change
- Testing checklist
- Code Review Checklist
- Additional Notes

**Size Guidelines**:
- Maximum 500 lines of code changes per PR
- Split larger changes into multiple PRs for easier review

**Approval Requirements**:
- Minimum 1 approval from team members
- All CI checks must pass (linting, type checking, tests)
- No unresolved conversations

**Merge Strategy**:
1. **Squash and Merge** (Default)
   - Clean commit history
   - One commit per feature
   - Commit message follows Conventional Commits

2. **Rebase and Merge** (For dependent PRs)
   - Preserve commit history
   - Use when commits need to be kept separate

**Required Labels**:
- Size: `size/XS`, `size/S`, `size/M`, `size/L`, `size/XL`
- Status: `status/ready-for-review`, `status/in-progress`, `status/blocked`
- Type: `type/feature`, `type/bug`, `type/docs`, `type/refactor`
- Priority: `priority/low`, `priority/medium`, `priority/high`, `priority/urgent`

**Post-Merge Actions**:
- Delete branch after successful merge
- Update related issues
- Deploy if applicable
- Notify team members if needed

## Implementation Notes

### Cache Directory Handling

Cache directories (`.mypy_cache`, `.ruff_cache`, `.pytest_cache`) are treated differently from virtual environments:

- They don't require parent directories to have package management files (main.py:99-104)
- They are always considered for deletion if older than the threshold
- The special handling is in the `should_process_directory()` function

### Directory Traversal

The tool uses `base_dir.glob("**/")` to recursively find all directories (main.py:189). Key behaviors:

- Symlinks are skipped to avoid following external links (main.py:190)
- Directories are processed in sorted order by path length
- Permission errors during size calculation are logged but don't stop execution (main.py:232)
