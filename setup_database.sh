#!/bin/bash
# ============================================================
# Database Setup Script for Linux/macOS
# ============================================================
#
# This script initializes the database and creates an admin user
#
# Usage:
#   ./setup_database.sh [config]
#
# Examples:
#   ./setup_database.sh              (Development mode)
#   ./setup_database.sh Production   (Production mode)
#   ./setup_database.sh Testing      (Testing mode)
#
# ============================================================

echo ""
echo "============================================================"
echo "  Dashboard Sonar - Database Setup"
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

# Determine configuration (default: Development)
CONFIG="${1:-Development}"

echo "[+] Configuration: $CONFIG"
echo ""

# Run the setup script
python scripts/setup_database.py --config "$CONFIG"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "  Setup completed successfully!"
    echo "============================================================"
else
    echo ""
    echo "============================================================"
    echo "  Setup failed with errors"
    echo "============================================================"
    exit 1
fi

echo ""
