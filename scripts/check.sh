#!/usr/bin/env bash
set -e

echo "Running Ruff lint..."
uv run ruff check .

echo "Runing Ruff formatting..."
uv run ruff format --check .

echo "Running mypy..."
uv run mypy src tests

echo "Running Bandit..."
uv run bandit -r src

echo "Running pytest..."
uv run pytest

echo "Running pip-audit..."
uv run pip-audit

echo "All checks passed."