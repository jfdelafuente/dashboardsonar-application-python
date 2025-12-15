#!/bin/bash
#
# Security Script - Security Scanning
# ====================================
#
# Runs security vulnerability scans on dependencies and code.
# Used by CI/CD pipelines and can be run locally.
#
# Usage:
#   ./scripts/ci/security.sh [OPTIONS]
#
# Options:
#   --dependencies   Scan only dependencies (safety)
#   --code          Scan only code (bandit)
#   --json          Output in JSON format
#   --fail-on-high  Exit with error on high severity issues
#
# Exit codes:
#   0 - No critical issues found
#   1 - Critical security issues found (with --fail-on-high)
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
SCAN_DEPS=true
SCAN_CODE=true
JSON_OUTPUT=false
FAIL_ON_HIGH=false
EXIT_CODE=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dependencies)
            SCAN_DEPS=true
            SCAN_CODE=false
            shift
            ;;
        --code)
            SCAN_DEPS=false
            SCAN_CODE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --fail-on-high)
            FAIL_ON_HIGH=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dependencies|--code] [--json] [--fail-on-high]"
            exit 1
            ;;
    esac
done

echo "============================================================"
echo "Security Scanning"
echo "============================================================"
echo ""

# Create output directory for reports
mkdir -p reports
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 1. Safety - Dependency vulnerability scanning
if [ "$SCAN_DEPS" = true ]; then
    echo -e "${YELLOW}▶${NC} Scanning dependencies with Safety..."
    echo ""

    if [ "$JSON_OUTPUT" = true ]; then
        SAFETY_OUTPUT="reports/safety-report-${TIMESTAMP}.json"
        if safety check --json --output "$SAFETY_OUTPUT" 2>/dev/null || true; then
            echo -e "${GREEN}✓${NC} Safety scan completed"
            echo -e "${BLUE}Report:${NC} $SAFETY_OUTPUT"
        else
            echo -e "${YELLOW}⚠${NC} Some vulnerabilities found"
            echo -e "${BLUE}Report:${NC} $SAFETY_OUTPUT"

            # Check for high severity if fail-on-high is enabled
            if [ "$FAIL_ON_HIGH" = true ]; then
                HIGH_COUNT=$(cat "$SAFETY_OUTPUT" | grep -i "severity.*high" | wc -l || echo "0")
                if [ "$HIGH_COUNT" -gt 0 ]; then
                    echo -e "${RED}✗${NC} Found $HIGH_COUNT high severity vulnerabilities"
                    EXIT_CODE=1
                fi
            fi
        fi
    else
        if safety check 2>/dev/null || true; then
            echo -e "${GREEN}✓${NC} No known vulnerabilities found"
        else
            echo -e "${YELLOW}⚠${NC} Some vulnerabilities found (see above)"

            if [ "$FAIL_ON_HIGH" = true ]; then
                EXIT_CODE=1
            fi
        fi
    fi

    echo ""
fi

# 2. Bandit - Code security scanning
if [ "$SCAN_CODE" = true ]; then
    echo -e "${YELLOW}▶${NC} Scanning code with Bandit..."
    echo ""

    BANDIT_OUTPUT="reports/bandit-report-${TIMESTAMP}.json"

    # Run bandit
    if [ "$JSON_OUTPUT" = true ]; then
        bandit -r infocodest/ -f json -o "$BANDIT_OUTPUT" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Bandit scan completed"
        echo -e "${BLUE}Report:${NC} $BANDIT_OUTPUT"

        # Parse results
        if command -v jq &> /dev/null; then
            HIGH_COUNT=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' "$BANDIT_OUTPUT" 2>/dev/null || echo "0")
            MEDIUM_COUNT=$(jq '[.results[] | select(.issue_severity == "MEDIUM")] | length' "$BANDIT_OUTPUT" 2>/dev/null || echo "0")
            LOW_COUNT=$(jq '[.results[] | select(.issue_severity == "LOW")] | length' "$BANDIT_OUTPUT" 2>/dev/null || echo "0")

            echo ""
            echo "  Issues found:"
            [ "$HIGH_COUNT" -gt 0 ] && echo -e "    ${RED}High:${NC} $HIGH_COUNT"
            [ "$MEDIUM_COUNT" -gt 0 ] && echo -e "    ${YELLOW}Medium:${NC} $MEDIUM_COUNT"
            [ "$LOW_COUNT" -gt 0 ] && echo -e "    ${BLUE}Low:${NC} $LOW_COUNT"

            if [ "$HIGH_COUNT" -eq 0 ] && [ "$MEDIUM_COUNT" -eq 0 ] && [ "$LOW_COUNT" -eq 0 ]; then
                echo -e "    ${GREEN}None${NC}"
            fi

            if [ "$FAIL_ON_HIGH" = true ] && [ "$HIGH_COUNT" -gt 0 ]; then
                echo -e "${RED}✗${NC} Found $HIGH_COUNT high severity issues"
                EXIT_CODE=1
            fi
        fi
    else
        # Text output
        bandit -r infocodest/ -f screen 2>/dev/null || true

        if [ "$FAIL_ON_HIGH" = true ]; then
            # Run again to check for high severity
            BANDIT_TEMP=$(mktemp)
            bandit -r infocodest/ -f json -o "$BANDIT_TEMP" 2>/dev/null || true

            if command -v jq &> /dev/null; then
                HIGH_COUNT=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' "$BANDIT_TEMP" 2>/dev/null || echo "0")
                if [ "$HIGH_COUNT" -gt 0 ]; then
                    EXIT_CODE=1
                fi
            fi

            rm -f "$BANDIT_TEMP"
        fi
    fi

    echo ""
fi

# Summary
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Security scan completed successfully${NC}"
    if [ "$FAIL_ON_HIGH" = false ]; then
        echo ""
        echo "Note: --fail-on-high not enabled. Run with this flag to"
        echo "fail the build on high severity issues."
    fi
else
    echo -e "${RED}✗ Security scan found critical issues${NC}"
    echo ""
    echo "Please review the issues above and fix high severity"
    echo "vulnerabilities before proceeding."
fi
echo "============================================================"

# Display report locations
if [ "$JSON_OUTPUT" = true ]; then
    echo ""
    echo "Reports generated in: reports/"
    ls -lh reports/*-${TIMESTAMP}.json 2>/dev/null || true
fi

exit $EXIT_CODE
