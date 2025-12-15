#!/bin/bash
#
# Lint Script - Code Quality Checks
# ==================================
#
# Runs all linting and code quality checks for the project.
# Used by CI/CD pipelines and can be run locally.
#
# Usage:
#   ./scripts/ci/lint.sh [--fix]
#
# Options:
#   --fix    Automatically fix issues where possible
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FIX_MODE=false
EXIT_CODE=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--fix]"
            exit 1
            ;;
    esac
done

echo "============================================================"
echo "Code Quality Checks"
echo "============================================================"
echo ""

# Function to run a check
run_check() {
    local name=$1
    local command=$2

    echo -e "${YELLOW}▶${NC} Running $name..."

    if eval "$command"; then
        echo -e "${GREEN}✓${NC} $name passed"
        echo ""
        return 0
    else
        echo -e "${RED}✗${NC} $name failed"
        echo ""
        EXIT_CODE=1
        return 1
    fi
}

# 1. Black - Code formatting
if [ "$FIX_MODE" = true ]; then
    run_check "Black (autofix)" "black infocodest/ tests/ scripts/"
else
    run_check "Black" "black --check --diff infocodest/ tests/ scripts/"
fi

# 2. isort - Import sorting
if [ "$FIX_MODE" = true ]; then
    run_check "isort (autofix)" "isort infocodest/ tests/ scripts/"
else
    run_check "isort" "isort --check-only --diff infocodest/ tests/ scripts/"
fi

# 3. Flake8 - Style guide enforcement
run_check "Flake8" "flake8 infocodest/ tests/ --count --statistics --max-line-length=127 --extend-ignore=E203,W503"

# 4. Pylint - Additional linting (continue on error)
echo -e "${YELLOW}▶${NC} Running Pylint (informational)..."
pylint infocodest/ --max-line-length=127 --disable=C0114,C0115,C0116 --exit-zero || true
echo ""

# 5. mypy - Type checking (continue on error)
echo -e "${YELLOW}▶${NC} Running mypy (informational)..."
mypy infocodest/ --ignore-missing-imports --no-strict-optional --exit-zero || true
echo ""

# Summary
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All code quality checks passed!${NC}"
else
    echo -e "${RED}✗ Some code quality checks failed${NC}"
    if [ "$FIX_MODE" = false ]; then
        echo ""
        echo "Tip: Run with --fix to automatically fix some issues:"
        echo "  ./scripts/ci/lint.sh --fix"
    fi
fi
echo "============================================================"

exit $EXIT_CODE
