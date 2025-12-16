#!/usr/bin/env bash
# ============================================================================
# Data Pipeline Orchestrator - Linux/macOS Wrapper
# ============================================================================
#
# Executes all data processing scripts in the correct order.
# Automatically loads environment variables from .env file.
#
# Usage:
#     ./run_data_pipeline.sh [CONFIG] [EXTRA_ARGS...]
#
# Examples:
#     ./run_data_pipeline.sh
#     ./run_data_pipeline.sh Production
#     ./run_data_pipeline.sh Development --clear-stats
#     ./run_data_pipeline.sh Production --data-dir ./custom_datos
#
# Created: 2025-12-16
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo ""
    echo -e "${RED}[!] Error: Virtual environment is not activated${NC}"
    echo "[!] Please activate it first:"
    echo "[!]   source venv/bin/activate"
    echo ""
    exit 1
fi

echo "============================================================================"
echo "Data Pipeline Orchestrator"
echo "============================================================================"
echo ""

# Load environment variables from .env file
if [ -f .env ]; then
    echo "[+] Loading environment variables from .env file..."
    set -a
    source <(grep -v '^#' .env | grep -v '^$' | sed 's/\r$//')
    set +a
    echo "[+] Environment variables loaded successfully"
    echo ""
else
    echo -e "${YELLOW}[!] Warning: .env file not found${NC}"
    echo "[!] Database configuration must be set via environment variables"
    echo ""
fi

# Parse arguments
CONFIG=""
EXTRA_ARGS=()

# Check if first argument is a config name
if [ $# -gt 0 ]; then
    if [[ "$1" == "Development" || "$1" == "Testing" || "$1" == "Production" ]]; then
        CONFIG="$1"
        shift
    fi
fi

# Collect remaining arguments
EXTRA_ARGS=("$@")

# Build command
CMD="python scripts/data/run_all_data_scripts.py"

if [ -n "$CONFIG" ]; then
    CMD="$CMD --config $CONFIG"
fi

if [ ${#EXTRA_ARGS[@]} -gt 0 ]; then
    CMD="$CMD ${EXTRA_ARGS[@]}"
fi

echo "[*] Executing: $CMD"
echo ""

# Execute the script
set +e  # Don't exit on error, capture exit code
$CMD
EXIT_CODE=$?
set -e

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS] Data pipeline completed successfully${NC}"
else
    echo -e "${RED}[FAILED] Data pipeline failed with exit code $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
