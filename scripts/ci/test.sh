#!/bin/bash
#
# Test Script - Run Test Suite
# =============================
#
# Runs the complete test suite with coverage reporting.
# Used by CI/CD pipelines and can be run locally.
#
# Usage:
#   ./scripts/ci/test.sh [OPTIONS]
#
# Options:
#   --unit           Run only unit tests (default: all)
#   --integration    Run only integration tests
#   --coverage       Generate coverage report (default: enabled)
#   --no-coverage    Skip coverage reporting
#   --html           Generate HTML coverage report
#   --verbose        Verbose output
#   --markers MARK   Run tests with specific marker
#
# Environment Variables:
#   TESTING=True                 Enable testing mode
#   SQLITE_DB_FILE=test.sqlite3  Use test database
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
TEST_PATH="tests/"
COVERAGE_ENABLED=true
HTML_REPORT=false
VERBOSE=""
MARKERS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_PATH="tests/unit/"
            shift
            ;;
        --integration)
            TEST_PATH="tests/integration/"
            MARKERS="-m integration"
            shift
            ;;
        --coverage)
            COVERAGE_ENABLED=true
            shift
            ;;
        --no-coverage)
            COVERAGE_ENABLED=false
            shift
            ;;
        --html)
            HTML_REPORT=true
            shift
            ;;
        --verbose)
            VERBOSE="-vv"
            shift
            ;;
        --markers)
            MARKERS="-m $2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--unit|--integration] [--coverage|--no-coverage] [--html] [--verbose] [--markers MARK]"
            exit 1
            ;;
    esac
done

echo "============================================================"
echo "Test Suite"
echo "============================================================"
echo -e "${BLUE}Test path:${NC} $TEST_PATH"
echo -e "${BLUE}Coverage:${NC} $([ "$COVERAGE_ENABLED" = true ] && echo "Enabled" || echo "Disabled")"
echo -e "${BLUE}HTML report:${NC} $([ "$HTML_REPORT" = true ] && echo "Yes" || echo "No")"
[ -n "$MARKERS" ] && echo -e "${BLUE}Markers:${NC} $MARKERS"
echo "============================================================"
echo ""

# Set test environment variables
export TESTING=True
export FLASK_APP=run.py
export FLASK_DEBUG=0
export DEBUG=False
export SECRET_KEY=test-secret-key-for-ci
export SQLITE_DB_FILE=test.sqlite3

# Create necessary directories and files
echo -e "${YELLOW}▶${NC} Setting up test environment..."
mkdir -p datos
touch datos/metricas.csv 2>/dev/null || true
touch datos/historico.csv 2>/dev/null || true
touch datos/proveedores.csv 2>/dev/null || true
echo ""

# Build pytest command
PYTEST_CMD="pytest $TEST_PATH $VERBOSE $MARKERS"

if [ "$COVERAGE_ENABLED" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=infocodest --cov-report=term-missing --cov-report=xml"

    if [ "$HTML_REPORT" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=html"
    fi
fi

# Run tests
echo -e "${YELLOW}▶${NC} Running tests..."
echo ""

if eval "$PYTEST_CMD"; then
    EXIT_CODE=0
    echo ""
    echo "============================================================"
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "============================================================"
else
    EXIT_CODE=1
    echo ""
    echo "============================================================"
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "============================================================"
fi

# Display coverage summary if enabled
if [ "$COVERAGE_ENABLED" = true ] && [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${BLUE}Coverage report generated:${NC}"
    echo "  - Terminal: shown above"
    echo "  - XML: coverage.xml"
    [ "$HTML_REPORT" = true ] && echo "  - HTML: htmlcov/index.html"
fi

# Cleanup
echo ""
echo -e "${YELLOW}▶${NC} Cleaning up test artifacts..."
rm -f test.sqlite3 2>/dev/null || true
rm -f .coverage 2>/dev/null || true

exit $EXIT_CODE
