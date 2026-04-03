#!/bin/bash
# Run code quality checks

set -e

echo "=== Code Quality Checks ==="

echo ""
echo "-- black (format check) --"
uv run black --check backend/ main.py

echo ""
echo "All checks passed."
