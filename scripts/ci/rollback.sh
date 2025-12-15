#!/bin/bash
#
# Rollback Script
# ===============
#
# Rolls back production deployment to previous version from backup.
#
# Usage:
#   ./scripts/ci/rollback.sh [OPTIONS]
#
# Options:
#   --version VERSION    Version that was deployed (for reference)
#   --timestamp TS       Backup timestamp to restore
#   --list-backups       List available backups
#   --force              Skip confirmation prompts
#   --dry-run            Show what would be done without executing
#
# Environment Variables (required):
#   PRODUCTION_HOST       Production server hostname or IP
#   PRODUCTION_USER       SSH username
#   PRODUCTION_PATH       Deployment path on server
#   PRODUCTION_SSH_KEY    Path to SSH private key (optional)
#
# Exit codes:
#   0 - Rollback successful
#   1 - Rollback failed
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
VERSION=""
TIMESTAMP=""
LIST_BACKUPS=false
FORCE=false
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --timestamp)
            TIMESTAMP="$2"
            shift 2
            ;;
        --list-backups)
            LIST_BACKUPS=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--version VERSION] [--timestamp TIMESTAMP] [--list-backups] [--force] [--dry-run]"
            exit 1
            ;;
    esac
done

# Validate required environment variables
if [ -z "$PRODUCTION_HOST" ] || [ -z "$PRODUCTION_USER" ] || [ -z "$PRODUCTION_PATH" ]; then
    echo -e "${RED}✗ Missing required environment variables${NC}"
    echo ""
    echo "Required:"
    echo "  PRODUCTION_HOST       - Production server hostname"
    echo "  PRODUCTION_USER       - SSH username"
    echo "  PRODUCTION_PATH       - Deployment path"
    exit 1
fi

# Setup SSH options
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
if [ -n "$PRODUCTION_SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $PRODUCTION_SSH_KEY"
fi

SSH_CMD="ssh $SSH_OPTS $PRODUCTION_USER@$PRODUCTION_HOST"

# List backups if requested
if [ "$LIST_BACKUPS" = true ]; then
    echo "============================================================"
    echo "Available Backups"
    echo "============================================================"
    $SSH_CMD "cd ${PRODUCTION_PATH}/../backups && ls -lht production-backup-*.tar.gz | head -10" || echo "No backups found"
    exit 0
fi

# Validate timestamp is provided
if [ -z "$TIMESTAMP" ]; then
    echo -e "${RED}✗ Error: --timestamp is required${NC}"
    echo ""
    echo "Usage: $0 --timestamp TIMESTAMP"
    echo ""
    echo "To see available backups:"
    echo "  $0 --list-backups"
    exit 1
fi

echo "============================================================"
echo -e "${MAGENTA}PRODUCTION ROLLBACK${NC}"
echo "============================================================"
echo -e "${BLUE}Target:${NC} $PRODUCTION_USER@$PRODUCTION_HOST:$PRODUCTION_PATH"
[ -n "$VERSION" ] && echo -e "${BLUE}Rolling back from:${NC} $VERSION"
echo -e "${BLUE}Restore backup:${NC} $TIMESTAMP"
[ "$DRY_RUN" = true ] && echo -e "${YELLOW}Mode:${NC} DRY RUN"
echo "============================================================"
echo ""

# Safety confirmation
if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
    echo -e "${YELLOW}⚠ WARNING: You are about to ROLLBACK PRODUCTION${NC}"
    echo ""
    echo "This will:"
    echo "  - Stop current application"
    echo "  - Restore from backup: $TIMESTAMP"
    echo "  - Restart application"
    echo "  - Affect live users"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${YELLOW}Rollback cancelled by user${NC}"
        exit 0
    fi
    echo ""
fi

# Function to execute command (respects dry-run)
execute() {
    local description=$1
    local command=$2

    echo -e "${CYAN}▶${NC} $description..."

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} Would execute: $command"
        return 0
    fi

    if eval "$command"; then
        echo -e "${GREEN}✓${NC} $description completed"
        return 0
    else
        echo -e "${RED}✗${NC} $description failed"
        return 1
    fi
}

# Step 1: Verify backup exists
echo -e "${CYAN}▶${NC} Verifying backup exists..."

if [ "$DRY_RUN" = false ]; then
    if ! $SSH_CMD "test -f ${PRODUCTION_PATH}/../backups/production-backup-${TIMESTAMP}.tar.gz"; then
        echo -e "${RED}✗ Backup file not found: production-backup-${TIMESTAMP}.tar.gz${NC}"
        echo ""
        echo "Available backups:"
        $SSH_CMD "cd ${PRODUCTION_PATH}/../backups && ls -lht production-backup-*.tar.gz | head -5"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Backup verified"
else
    echo -e "${YELLOW}[DRY RUN]${NC} Would verify backup"
fi
echo ""

# Step 2: Stop application
execute "Stopping application" \
    "$SSH_CMD 'sudo systemctl stop dashboardsonar || sudo supervisorctl stop dashboardsonar || echo \"Manual stop required\"'"
echo ""

# Step 3: Move current version
execute "Moving current version to failed backup" \
    "$SSH_CMD 'mv $PRODUCTION_PATH ${PRODUCTION_PATH}-rollback-$(date +%Y%m%d_%H%M%S)'"
echo ""

# Step 4: Extract backup
execute "Extracting backup" \
    "$SSH_CMD 'mkdir -p $PRODUCTION_PATH && cd $PRODUCTION_PATH && tar -xzf ../backups/production-backup-${TIMESTAMP}.tar.gz'"
echo ""

# Step 5: Restore dependencies (may be cached in venv)
execute "Verifying dependencies" \
    "$SSH_CMD 'cd $PRODUCTION_PATH && if [ -d venv ]; then echo \"Using existing venv\"; else python -m venv venv && source venv/bin/activate && pip install -r requirements.txt; fi'"
echo ""

# Step 6: Restart application
execute "Restarting application" \
    "$SSH_CMD 'sudo systemctl restart dashboardsonar || sudo supervisorctl restart dashboardsonar || echo \"Manual restart required\"'"
echo ""

# Step 7: Wait for application to start
echo -e "${CYAN}▶${NC} Waiting for application to start..."
if [ "$DRY_RUN" = false ]; then
    sleep 10
    echo -e "${GREEN}✓${NC} Wait completed"
else
    echo -e "${YELLOW}[DRY RUN]${NC} Would wait 10 seconds"
fi
echo ""

# Step 8: Verify application is running
echo -e "${CYAN}▶${NC} Verifying application health..."

if [ "$DRY_RUN" = false ]; then
    if curl --max-time 10 --fail "http://$PRODUCTION_HOST/" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Application is responding"
    else
        echo -e "${RED}✗${NC} Application is not responding"
        echo ""
        echo "Please investigate manually:"
        echo "  ssh $PRODUCTION_USER@$PRODUCTION_HOST 'tail -f $PRODUCTION_PATH/logs/app.log'"
        exit 1
    fi
else
    echo -e "${YELLOW}[DRY RUN]${NC} Would verify health"
fi
echo ""

# Summary
echo "============================================================"
echo -e "${GREEN}✓ ROLLBACK SUCCESSFUL${NC}"
echo "============================================================"
echo -e "${BLUE}Server:${NC} $PRODUCTION_HOST"
echo -e "${BLUE}Restored from:${NC} $TIMESTAMP"
echo ""
echo "Application URL: http://$PRODUCTION_HOST"
echo ""
echo "Next steps:"
echo "  1. Verify application functionality"
echo "  2. Check logs for any issues"
echo "  3. Monitor application performance"
echo "  4. Investigate what went wrong with the deployment"
echo ""
echo "Failed deployment saved at: ${PRODUCTION_PATH}-rollback-*"
echo "============================================================"

exit 0
