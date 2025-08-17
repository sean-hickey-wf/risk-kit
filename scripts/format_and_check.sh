#!/bin/bash
set -e

echo "Running linter checks and formatting code..."

echo "🔍 Running ruff check..."
ruff check --fix src/ tests/

echo "🔍 Running black check..."
black src/ tests/

echo "🔍 Running mypy check..."
mypy src/ tests/

echo "✅ All linter checks passed!"
