#!/usr/bin/env bash
#
# run-coverage.sh - Clean coverage reporting with parallel test execution
#
# This script works around pytest-xdist terminal corruption issues by
# separating test execution from coverage reporting.
#

set -e

# Clean up old coverage data
rm -f .coverage .coverage.*
rm -rf htmlcov/

# Run tests with coverage in parallel (no terminal report to avoid corruption)
echo "Running tests with coverage..."
pytest --cov-branch --cov=pyvider.cty -n auto --cov-report= "$@"

# Combine coverage data from parallel workers
echo ""
echo "Combining coverage data..."
coverage combine

# Generate clean terminal report
echo ""
echo "Coverage Report:"
echo "================"
coverage report --show-missing --skip-covered

# Optionally generate HTML report
if [ "$HTML" = "1" ]; then
    echo ""
    echo "Generating HTML coverage report..."
    coverage html
    echo "HTML report available at: htmlcov/index.html"
fi
