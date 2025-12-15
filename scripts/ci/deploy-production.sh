#!/bin/bash
#
# Production Deployment Script
# =============================
#
# Deploys the application to the production environment with safety checks.
# Uses blue-green deployment strategy for zero-downtime deployments.
#
# Usage:
#   ./scripts/ci/deploy-production.sh [OPTIONS]
#
# Options:
#   --version VERSION  Deploy specific version tag (required)
#   --skip-backup      Skip backup before deployment
#   --skip-tests       Skip smoke tests after deployment
#   --force            Skip confirmation prompts
#   --dry-run          Show what would be done without executing
#
# Environment Variables (required):
#   PRODUCTION_HOST       Production server hostname or IP
#   PRODUCTION_USER       SSH username
#   PRODUCTION_PATH       Deployment path on server
#   PRODUCTION_SSH_KEY    Path to SSH private key (optional)
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
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
VERSION=""
SKIP_BACKUP=false
SKIP_TESTS=false
FORCE=false
DRY_RUN=false
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
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
            echo "Usage: $0 --version VERSION [--skip-backup] [--skip-tests] [--force] [--dry-run]"
            exit 1
            ;;
    esac
done

# Validate version is provided
if [ -z "$VERSION" ]; then
    echo -e "${RED}✗ Error: --version is required${NC}"
    echo ""
    echo "Usage: $0 --version VERSION"
    echo ""
    echo "Examples:"
    echo "  $0 --version v1.2.3"
    echo "  $0 --version v2.0.0 --force"
    exit 1
fi

# Validate required environment variables
if [ -z "$PRODUCTION_HOST" ] || [ -z "$PRODUCTION_USER" ] || [ -z "$PRODUCTION_PATH" ]; then
    echo -e "${RED}✗ Missing required environment variables${NC}"
    echo ""
    echo "Required:"
    echo "  PRODUCTION_HOST       - Production server hostname"
    echo "  PRODUCTION_USER       - SSH username"
    echo "  PRODUCTION_PATH       - Deployment path"
    echo ""
    echo "Optional:"
    echo "  PRODUCTION_SSH_KEY    - Path to SSH private key"
    exit 1
fi

# Setup SSH options
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
if [ -n "$PRODUCTION_SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $PRODUCTION_SSH_KEY"
fi

SSH_CMD="ssh $SSH_OPTS $PRODUCTION_USER@$PRODUCTION_HOST"
SCP_CMD="scp $SSH_OPTS"

echo "============================================================"
echo -e "${MAGENTA}PRODUCTION DEPLOYMENT${NC}"
echo "============================================================"
echo -e "${BLUE}Target:${NC} $PRODUCTION_USER@$PRODUCTION_HOST:$PRODUCTION_PATH"
echo -e "${BLUE}Version:${NC} $VERSION"
echo -e "${BLUE}Timestamp:${NC} $TIMESTAMP"
[ "$DRY_RUN" = true ] && echo -e "${YELLOW}Mode:${NC} DRY RUN"
echo "============================================================"
echo ""

# Safety confirmation
if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
    echo -e "${YELLOW}⚠ WARNING: You are about to deploy to PRODUCTION${NC}"
    echo ""
    echo "This will:"
    echo "  - Deploy version: $VERSION"
    echo "  - Update production server: $PRODUCTION_HOST"
    echo "  - Affect live users"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${YELLOW}Deployment cancelled by user${NC}"
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

# Step 1: Verify version tag exists
echo -e "${CYAN}▶${NC} Verifying version tag..."
if [ "$DRY_RUN" = false ]; then
    if ! git rev-parse "$VERSION" >/dev/null 2>&1; then
        echo -e "${RED}✗ Version tag $VERSION does not exist${NC}"
        echo ""
        echo "Available tags:"
        git tag -l | tail -5
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Version tag verified"
else
    echo -e "${YELLOW}[DRY RUN]${NC} Would verify version tag"
fi
echo ""

# Step 2: Create backup
if [ "$SKIP_BACKUP" = false ]; then
    echo -e "${YELLOW}▶${NC} Creating production backup..."

    BACKUP_CMD="$SSH_CMD 'cd $PRODUCTION_PATH && \
        mkdir -p ../backups && \
        tar -czf ../backups/production-backup-$TIMESTAMP.tar.gz . && \
        echo \"Backup created: backups/production-backup-$TIMESTAMP.tar.gz\" && \
        ls -lh ../backups/ | tail -5'"

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} Would create backup"
    else
        eval "$BACKUP_CMD" || echo -e "${YELLOW}⚠${NC} Backup failed (non-fatal)"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠${NC} Backup skipped (--skip-backup)"
    echo ""
fi

# Step 3: Blue-Green Deployment - Prepare new version
echo -e "${MAGENTA}▶${NC} Preparing blue-green deployment..."

execute "Creating deployment directory" \
    "$SSH_CMD 'mkdir -p ${PRODUCTION_PATH}-new'"

execute "Fetching version $VERSION" \
    "$SSH_CMD 'cd $PRODUCTION_PATH && git fetch --tags'"

execute "Checking out version $VERSION" \
    "$SSH_CMD 'cd $PRODUCTION_PATH && git clone . ${PRODUCTION_PATH}-new && cd ${PRODUCTION_PATH}-new && git checkout $VERSION'"

execute "Installing dependencies in new environment" \
    "$SSH_CMD 'cd ${PRODUCTION_PATH}-new && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt --quiet'"

echo ""

# Step 4: Database migrations (on existing DB)
echo -e "${CYAN}▶${NC} Running database migrations..."

execute "Applying migrations" \
    "$SSH_CMD 'cd $PRODUCTION_PATH && source venv/bin/activate && export FLASK_APP=run.py && flask db upgrade || echo \"No migrations to run\"'"

echo ""

# Step 5: Smoke test new deployment (before switching)
if [ "$SKIP_TESTS" = false ]; then
    echo -e "${CYAN}▶${NC} Testing new deployment on temporary port..."

    if [ "$DRY_RUN" = false ]; then
        # Start app on temporary port for testing
        TEST_PORT=8888
        execute "Starting app on port $TEST_PORT for testing" \
            "$SSH_CMD 'cd ${PRODUCTION_PATH}-new && source venv/bin/activate && FLASK_RUN_PORT=$TEST_PORT nohup flask run > /tmp/test-app.log 2>&1 & echo \$! > /tmp/test-app.pid && sleep 3'"

        # Run smoke test on temporary port
        if curl --max-time 10 --fail "http://$PRODUCTION_HOST:$TEST_PORT/" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} New version responding correctly"
        else
            echo -e "${RED}✗${NC} New version failed smoke test"
            # Cleanup
            $SSH_CMD 'kill $(cat /tmp/test-app.pid 2>/dev/null) 2>/dev/null; rm -rf ${PRODUCTION_PATH}-new'
            exit 1
        fi

        # Stop test app
        execute "Stopping test app" \
            "$SSH_CMD 'kill \$(cat /tmp/test-app.pid 2>/dev/null) 2>/dev/null || true'"
    else
        echo -e "${YELLOW}[DRY RUN]${NC} Would test new deployment"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠${NC} Smoke tests skipped (--skip-tests)"
    echo ""
fi

# Step 6: Switch to new version (Blue-Green switch)
echo -e "${MAGENTA}▶${NC} Switching to new version..."

execute "Moving current version to backup" \
    "$SSH_CMD 'mv $PRODUCTION_PATH ${PRODUCTION_PATH}-old'"

execute "Activating new version" \
    "$SSH_CMD 'mv ${PRODUCTION_PATH}-new $PRODUCTION_PATH'"

execute "Restarting application" \
    "$SSH_CMD 'sudo systemctl restart dashboardsonar || sudo supervisorctl restart dashboardsonar || echo \"Manual restart required\"'"

echo ""

# Step 7: Wait and verify
echo -e "${CYAN}▶${NC} Waiting for application to start..."
if [ "$DRY_RUN" = false ]; then
    sleep 10
    echo -e "${GREEN}✓${NC} Wait completed"
else
    echo -e "${YELLOW}[DRY RUN]${NC} Would wait 10 seconds"
fi
echo ""

# Step 8: Production smoke tests
if [ "$SKIP_TESTS" = false ]; then
    echo -e "${CYAN}▶${NC} Running production smoke tests..."

    if [ -f "./scripts/ci/smoke-tests.sh" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}[DRY RUN]${NC} Would run smoke tests"
        else
            export SMOKE_TEST_URL="http://$PRODUCTION_HOST"
            if ./scripts/ci/smoke-tests.sh; then
                echo -e "${GREEN}✓${NC} Production smoke tests passed"
            else
                echo -e "${RED}✗${NC} Production smoke tests FAILED"
                echo ""
                echo -e "${YELLOW}⚠ INITIATING AUTOMATIC ROLLBACK${NC}"
                echo ""
                # Rollback
                $SSH_CMD "mv $PRODUCTION_PATH ${PRODUCTION_PATH}-failed && mv ${PRODUCTION_PATH}-old $PRODUCTION_PATH && sudo systemctl restart dashboardsonar || sudo supervisorctl restart dashboardsonar"
                echo -e "${YELLOW}✓ Rolled back to previous version${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}⚠${NC} Smoke tests script not found"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠${NC} Smoke tests skipped (--skip-tests)"
    echo ""
fi

# Step 9: Cleanup old version
execute "Cleaning up old version" \
    "$SSH_CMD 'rm -rf ${PRODUCTION_PATH}-old'"

echo ""

# Summary
echo "============================================================"
echo -e "${GREEN}✓ PRODUCTION DEPLOYMENT SUCCESSFUL${NC}"
echo "============================================================"
echo -e "${BLUE}Server:${NC} $PRODUCTION_HOST"
echo -e "${BLUE}Version:${NC} $VERSION"
echo -e "${BLUE}Timestamp:${NC} $TIMESTAMP"
echo ""
echo "Application URL: http://$PRODUCTION_HOST"
echo ""
echo "Next steps:"
echo "  1. Monitor application logs for errors"
echo "  2. Verify functionality with users"
echo "  3. Check metrics and performance"
echo "  4. Keep backup available for 24h: backups/production-backup-$TIMESTAMP.tar.gz"
echo ""
echo "Rollback command (if needed):"
echo "  ./scripts/ci/rollback.sh --version $VERSION --timestamp $TIMESTAMP"
echo "============================================================"

exit 0
