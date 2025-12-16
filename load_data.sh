#!/bin/bash
# ============================================================
# Data Loading Script for Linux/macOS
# ============================================================
#
# This script loads data from CSV files into the database
#
# Usage:
#   ./load_data.sh [config] [options]
#
# Examples:
#   ./load_data.sh                           (Development mode)
#   ./load_data.sh Production                (Production mode)
#   ./load_data.sh Development --batch-size 500
#
# ============================================================

echo ""
echo "============================================================"
echo "  Dashboard Sonar - Data Loading"
echo "============================================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[!] Virtual environment not activated"
    echo ""
    echo "Please activate your virtual environment first:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "[+] Virtual environment: $VIRTUAL_ENV"
echo ""

# Load environment variables from .env file
if [ -f .env ]; then
    echo "[+] Loading environment variables from .env file..."
    # Export variables from .env, ignoring comments and empty lines
    set -a
    source <(grep -v '^#' .env | grep -v '^$' | sed 's/\r$//')
    set +a
    echo "[+] Environment variables loaded successfully"
    echo ""
else
    echo "[!] Warning: .env file not found"
    echo ""
fi

# Determine configuration (default: Development)
CONFIG="Development"
EXTRA_ARGS=""

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        Development|Production|Testing)
            CONFIG="$1"
            shift
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
    esac
done

echo "[+] Configuration: $CONFIG"
if [ -n "$EXTRA_ARGS" ]; then
    echo "[+] Extra arguments:$EXTRA_ARGS"
fi
echo ""

# Run the data loading script
python scripts/data/load_data.py --config "$CONFIG" $EXTRA_ARGS

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "  Data loading completed successfully!"
    echo "============================================================"
else
    echo ""
    echo "============================================================"
    echo "  Data loading failed with errors"
    echo "============================================================"
    exit 1
fi

echo ""
