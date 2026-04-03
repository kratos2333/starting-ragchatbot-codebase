# Code Quality Tooling Changes

## Summary

Added `black` for automatic Python code formatting and created development scripts for running quality checks.

## Changes

### `pyproject.toml`
- Added `[dependency-groups] dev` section with `black>=24.0.0`
- Added `[tool.black]` configuration: `line-length = 88`, `target-version = ["py312"]`, excludes `.git`, `.venv`, `__pycache__`, `chroma_db`

### `format.sh` (new)
- Runs `uv run black backend/ main.py` to auto-format all Python source files in place

### `lint.sh` (new)
- Runs `uv run black --check backend/ main.py` to verify formatting without modifying files
- Exits non-zero if any file is not formatted, making it safe to use in CI

### `backend/*.py`, `main.py`
- Reformatted 9 files with black (consistent spacing, trailing commas, line lengths)
- `main.py` was already compliant and left unchanged

## Usage

```bash
# Auto-format
./format.sh

# Check formatting (CI-safe, no writes)
./lint.sh
```
