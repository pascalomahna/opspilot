#!/usr/bin/env bash
set -e

echo "Running Ruff lint..."
uv run ruff check .

echo "Runing Ruff formatting..."
uv run ruff format --check .

echo "Running mypy..."
uv run mypy src tests

echo "Running pytest..."
uv run pytest

echo "All checks passed."