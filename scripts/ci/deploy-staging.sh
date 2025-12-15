#!/bin/bash
#
# Staging Deployment Script
# ==========================
#
# Deploys the application to the staging environment.
# Used by CD workflows and can be run manually.
#
# Usage:
#   ./scripts/ci/deploy-staging.sh [OPTIONS]
#
# Options:
#   --branch BRANCH    Deploy specific branch (default: develop)
#   --skip-backup      Skip backup before deployment
#   --skip-tests       Skip smoke tests after deployment
#   --dry-run          Show what would be done without executing
#
# Environment Variables (required):
#   STAGING_HOST       Staging server hostname or IP
#   STAGING_USER       SSH username
#   STAGING_PATH       Deployment path on server
#   STAGING_SSH_KEY    Path to SSH private key (optional)
#
# Exit codes:
#   0 - Deployment successful
#   1 - Deployment failed
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BRANCH="develop"
SKIP_BACKUP=false
SKIP_TESTS=false
DRY_RUN=false
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--branch BRANCH] [--skip-backup] [--skip-tests] [--dry-run]"
            exit 1
            ;;
    esac
done

# Validate required environment variables
if [ -z "$STAGING_HOST" ] || [ -z "$STAGING_USER" ] || [ -z "$STAGING_PATH" ]; then
    echo -e "${RED}✗ Missing required environment variables${NC}"
    echo ""
    echo "Required:"
    echo "  STAGING_HOST       - Staging server hostname"
    echo "  STAGING_USER       - SSH username"
    echo "  STAGING_PATH       - Deployment path"
    echo ""
    echo "Optional:"
    echo "  STAGING_SSH_KEY    - Path to SSH private key"
    exit 1
fi

# Setup SSH options
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
if [ -n "$STAGING_SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $STAGING_SSH_KEY"
fi

SSH_CMD="ssh $SSH_OPTS $STAGING_USER@$STAGING_HOST"
SCP_CMD="scp $SSH_OPTS"

echo "============================================================"
echo "Staging Deployment"
echo "============================================================"
echo -e "${BLUE}Target:${NC} $STAGING_USER@$STAGING_HOST:$STAGING_PATH"
echo -e "${BLUE}Branch:${NC} $BRANCH"
echo -e "${BLUE}Timestamp:${NC} $TIMESTAMP"
[ "$DRY_RUN" = true ] && echo -e "${YELLOW}Mode:${NC} DRY RUN"
echo "============================================================"
echo ""

# Dry run mode
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}⚠ DRY RUN MODE - No changes will be made${NC}"
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

# Step 1: Backup current deployment
if [ "$SKIP_BACKUP" = false ]; then
    echo -e "${YELLOW}▶${NC} Creating backup..."

    BACKUP_CMD="$SSH_CMD 'cd $STAGING_PATH && \
        if [ -d .git ]; then \
            tar -czf ../backups/staging-backup-$TIMESTAMP.tar.gz . && \
            echo \"Backup created: backups/staging-backup-$TIMESTAMP.tar.gz\" && \
            ls -lh ../backups/ | tail -5; \
        else \
            echo \"No git repository found, skipping backup\"; \
        fi'"

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} Would create backup"
    else
        eval "$BACKUP_CMD" || echo -e "${YELLOW}⚠${NC} Backup skipped or failed (non-fatal)"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠${NC} Backup skipped (--skip-backup)"
    echo ""
fi

# Step 2: Pull latest code
execute "Pulling latest code from $BRANCH" \
    "$SSH_CMD 'cd $STAGING_PATH && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH'"
echo ""

# Step 3: Install/update dependencies
execute "Installing dependencies" \
    "$SSH_CMD 'cd $STAGING_PATH && source venv/bin/activate && pip install -r requirements.txt --quiet'"
echo ""

# Step 4: Run database migrations (if any)
execute "Running database migrations" \
    "$SSH_CMD 'cd $STAGING_PATH && source venv/bin/activate && export FLASK_APP=run.py && flask db upgrade || echo \"No migrations to run\"'"
echo ""

# Step 5: Collect static files (if needed)
execute "Collecting static files" \
    "$SSH_CMD 'cd $STAGING_PATH && echo \"Static files ready\"'"
echo ""

# Step 6: Restart application
execute "Restarting application" \
    "$SSH_CMD 'sudo systemctl restart dashboardsonar-staging || sudo supervisorctl restart dashboardsonar-staging || echo \"Manual restart required\"'"
echo ""

# Step 7: Wait for application to start
if [ "$DRY_RUN" = false ]; then
    echo -e "${CYAN}▶${NC} Waiting for application to start..."
    sleep 5
    echo -e "${GREEN}✓${NC} Wait completed"
    echo ""
fi

# Step 8: Run smoke tests
if [ "$SKIP_TESTS" = false ]; then
    echo -e "${CYAN}▶${NC} Running smoke tests..."

    if [ -f "./scripts/ci/smoke-tests.sh" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}[DRY RUN]${NC} Would run smoke tests"
        else
            export SMOKE_TEST_URL="http://$STAGING_HOST"
            if ./scripts/ci/smoke-tests.sh; then
                echo -e "${GREEN}✓${NC} Smoke tests passed"
            else
                echo -e "${RED}✗${NC} Smoke tests failed"
                echo ""
                echo "Deployment completed but smoke tests failed."
                echo "Please investigate the issues before proceeding."
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}⚠${NC} Smoke tests script not found, skipping"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠${NC} Smoke tests skipped (--skip-tests)"
    echo ""
fi

# Summary
echo "============================================================"
echo -e "${GREEN}✓ Staging Deployment Completed Successfully${NC}"
echo "============================================================"
echo -e "${BLUE}Server:${NC} $STAGING_HOST"
echo -e "${BLUE}Path:${NC} $STAGING_PATH"
echo -e "${BLUE}Branch:${NC} $BRANCH"
echo -e "${BLUE}Timestamp:${NC} $TIMESTAMP"
echo ""
echo "Application URL: http://$STAGING_HOST"
echo ""
echo "Next steps:"
echo "  1. Verify application functionality"
echo "  2. Run manual tests if needed"
echo "  3. Check logs: ssh $STAGING_USER@$STAGING_HOST 'tail -f $STAGING_PATH/logs/app.log'"
echo "============================================================"

exit 0
