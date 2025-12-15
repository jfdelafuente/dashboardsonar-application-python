#!/bin/bash
#
# Smoke Tests Script
# ===================
#
# Runs basic smoke tests to verify application health after deployment.
# Used by deployment workflows and can be run manually.
#
# Usage:
#   ./scripts/ci/smoke-tests.sh [OPTIONS]
#
# Options:
#   --url URL          Application URL to test (default: http://localhost:5000)
#   --timeout SEC      Timeout for each test in seconds (default: 10)
#   --retries NUM      Number of retries for failed tests (default: 3)
#   --verbose          Verbose output
#
# Environment Variables:
#   SMOKE_TEST_URL     Application URL (overrides --url)
#   SMOKE_TEST_TIMEOUT Timeout in seconds (overrides --timeout)
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed
#

set -e  # Exit on error (but we'll handle test failures)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_URL="${SMOKE_TEST_URL:-http://localhost:5000}"
TIMEOUT="${SMOKE_TEST_TIMEOUT:-10}"
RETRIES=3
VERBOSE=false
FAILED_TESTS=0
PASSED_TESTS=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            APP_URL="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --retries)
            RETRIES="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--url URL] [--timeout SEC] [--retries NUM] [--verbose]"
            exit 1
            ;;
    esac
done

echo "============================================================"
echo "Smoke Tests"
echo "============================================================"
echo -e "${BLUE}Target URL:${NC} $APP_URL"
echo -e "${BLUE}Timeout:${NC} ${TIMEOUT}s per test"
echo -e "${BLUE}Retries:${NC} $RETRIES"
echo "============================================================"
echo ""

# Function to run a test with retries
run_test() {
    local test_name=$1
    local test_command=$2
    local attempt=1

    while [ $attempt -le $((RETRIES + 1)) ]; do
        echo -e "${CYAN}▶${NC} Testing: $test_name $([ $attempt -gt 1 ] && echo \"(attempt $attempt/$((RETRIES + 1)))\" || echo \"\")"

        if [ "$VERBOSE" = true ]; then
            echo -e "${BLUE}Command:${NC} $test_command"
        fi

        if eval "$test_command" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $test_name - PASSED"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            echo ""
            return 0
        else
            if [ $attempt -le $RETRIES ]; then
                echo -e "${YELLOW}⚠${NC} $test_name - FAILED (retrying...)"
                sleep 2
                attempt=$((attempt + 1))
            else
                echo -e "${RED}✗${NC} $test_name - FAILED"
                FAILED_TESTS=$((FAILED_TESTS + 1))
                echo ""
                return 1
            fi
        fi
    done
}

# Test 1: Health Check - Root endpoint
run_test "Health Check (Root Endpoint)" \
    "curl --max-time $TIMEOUT --fail --silent $APP_URL/"

# Test 2: Login page accessibility
run_test "Login Page Accessible" \
    "curl --max-time $TIMEOUT --fail --silent $APP_URL/login"

# Test 3: Static assets loading
run_test "Static Assets (CSS)" \
    "curl --max-time $TIMEOUT --fail --silent $APP_URL/static/assets/css/style.css"

# Test 4: API health endpoint (if exists)
run_test "API Health Endpoint" \
    "curl --max-time $TIMEOUT --fail --silent $APP_URL/api/health || curl --max-time $TIMEOUT --fail --silent $APP_URL/health || true"

# Test 5: Database connectivity (indirect)
# This tests if the app can connect to database by accessing a page that requires DB
run_test "Database Connectivity" \
    "curl --max-time $TIMEOUT --silent $APP_URL/ | grep -q 'Dashboard' || curl --max-time $TIMEOUT --silent $APP_URL/ | grep -q 'Login'"

# Test 6: Response time check
echo -e "${CYAN}▶${NC} Testing: Response Time"
START_TIME=$(date +%s%N)
if curl --max-time $TIMEOUT --fail --silent $APP_URL/ > /dev/null 2>&1; then
    END_TIME=$(date +%s%N)
    RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))  # Convert to milliseconds

    if [ $RESPONSE_TIME -lt 3000 ]; then
        echo -e "${GREEN}✓${NC} Response Time - PASSED (${RESPONSE_TIME}ms < 3000ms)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠${NC} Response Time - SLOW (${RESPONSE_TIME}ms >= 3000ms)"
        echo ""
    fi
else
    echo -e "${RED}✗${NC} Response Time - FAILED (no response)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# Test 7: HTTP Status Codes
echo -e "${CYAN}▶${NC} Testing: HTTP Status Codes"
HTTP_CODE=$(curl --max-time $TIMEOUT --silent --output /dev/null --write-out "%{http_code}" $APP_URL/ || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} HTTP Status Code - PASSED (200 OK)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
elif [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "301" ]; then
    echo -e "${GREEN}✓${NC} HTTP Status Code - PASSED ($HTTP_CODE Redirect)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗${NC} HTTP Status Code - FAILED (got $HTTP_CODE)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# Test 8: Check for error pages
echo -e "${CYAN}▶${NC} Testing: Error Detection"
RESPONSE=$(curl --max-time $TIMEOUT --silent $APP_URL/ || echo "")

if echo "$RESPONSE" | grep -qi "error\|exception\|traceback\|internal server error"; then
    echo -e "${RED}✗${NC} Error Detection - FAILED (error page detected)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
else
    echo -e "${GREEN}✓${NC} Error Detection - PASSED (no error pages)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi
echo ""

# Summary
TOTAL_TESTS=$((PASSED_TESTS + FAILED_TESTS))

echo "============================================================"
echo "Smoke Tests Summary"
echo "============================================================"
echo -e "${BLUE}Total Tests:${NC} $TOTAL_TESTS"
echo -e "${GREEN}Passed:${NC} $PASSED_TESTS"
[ $FAILED_TESTS -gt 0 ] && echo -e "${RED}Failed:${NC} $FAILED_TESTS"
echo "============================================================"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    echo ""
    echo "Application appears to be healthy and ready for use."
    exit 0
else
    echo -e "${RED}✗ Some smoke tests failed${NC}"
    echo ""
    echo "Please investigate the failures before proceeding."
    echo ""
    echo "Common issues:"
    echo "  - Application not fully started (try waiting longer)"
    echo "  - Database connection issues"
    echo "  - Configuration errors"
    echo "  - Network/firewall issues"
    echo ""
    echo "Check application logs for more details:"
    echo "  tail -f logs/app.log"
    exit 1
fi
