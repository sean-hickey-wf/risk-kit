#!/bin/bash
set -e

echo "Running full test suite..."

echo "🔍 Running linter checks..."
echo "  - Running ruff check..."
ruff check src/ tests/

echo "  - Running black check..."
black --check src/ tests/

echo "  - Running mypy check..."
mypy src/ tests/

echo "✅ All linter checks passed!"

echo "🧪 Running tests with pytest..."
pytest tests/ --cov=src --cov-report=term-missing

echo "✅ All tests completed successfully!"
