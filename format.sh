#!/bin/bash
# Auto-format all Python source files with black

set -e

echo "=== Formatting Python files with black ==="
uv run black backend/ main.py

echo "Done."
