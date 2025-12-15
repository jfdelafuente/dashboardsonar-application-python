# GitHub Workflows

This directory contains GitHub Actions workflows for Continuous Integration and Continuous Deployment (CI/CD).

## Overview

The CI/CD pipeline is designed to ensure code quality, security, and reliability through automated testing and deployment processes.

## Workflows

### CI - Pull Request Validation (`ci-pull-request.yml`)

**Trigger**: Runs on Pull Requests to `develop` or `main` branches

**Purpose**: Validates code quality, security, and functionality before merging

**Jobs**:

1. **Code Quality & Linting**
   - Runs Flake8 for code style validation
   - Runs Black formatter check
   - Ensures consistent code formatting

2. **Security Scanning**
   - Safety check for vulnerable dependencies
   - Bandit security scan for common security issues
   - Generates security reports

3. **Unit Tests**
   - Runs on Python 3.10, 3.11, and 3.12
   - Executes pytest with coverage reporting
   - Uploads coverage to Codecov
   - Generates HTML coverage reports

4. **Integration Tests**
   - Tests full application integration
   - Validates database setup and operations
   - Tests end-to-end workflows

5. **Build Validation**
   - Verifies package imports
   - Checks for syntax errors
   - Validates configuration

6. **PR Summary**
   - Aggregates all job results
   - Provides final PR status

**Requirements**:
- All jobs must pass for PR to be mergeable
- Integration tests failures are warnings only
- Code quality issues are reported but don't block

---

### CD - Staging Deployment (`cd-staging.yml`)

**Trigger**: Automatic on push to `develop` branch, or manual via `workflow_dispatch`

**Purpose**: Automatically deploy to staging environment for testing

**Jobs**:

1. **Pre-Deployment Validation**
   - Quick syntax check of all Python files
   - Run critical unit tests (fail-fast mode)
   - Ensure code compiles before deployment

2. **Deploy to Staging**
   - Connect to staging server via SSH
   - Pull latest code from `develop` branch
   - Install/update dependencies
   - Run database migrations
   - Restart application service
   - Uses GitHub Environment: `staging`

3. **Smoke Tests**
   - Wait for application to stabilize
   - Test critical endpoints (root, login, API)
   - Verify response times < 3 seconds
   - Check for error pages
   - Validate HTTP status codes

4. **Deployment Notification**
   - Send Slack notification (if configured)
   - Create deployment summary
   - Report deployment status

**Requirements**:

- GitHub Environment `staging` must be configured
- Required secrets: `STAGING_SSH_KEY`, `STAGING_HOST`, `STAGING_USER`, `STAGING_PATH`
- Optional: `SLACK_WEBHOOK_URL` for notifications

**Deployment URL**: Displayed in GitHub Environment after deployment

## Environment Variables

The workflows use the following environment variables:

- `PYTHON_VERSION`: Default Python version (3.11)
- `FLASK_APP`: Flask application entry point (run.py)
- `FLASK_DEBUG`: Debug mode (0 for CI)
- `DEBUG`: Application debug flag (False)
- `TESTING`: Testing mode flag (True)
- `SECRET_KEY`: Secret key for sessions (test value)
- `SQLITE_DB_FILE`: SQLite database file for tests

## Artifacts

The following artifacts are generated and stored:

- **Security Reports**: Bandit JSON report (30 days retention)
- **Coverage Reports**: HTML coverage report (30 days retention)

## Local Testing

To run the same checks locally before pushing:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Code quality
flake8 infocodest/
black --check infocodest/

# Security scanning
safety check
bandit -r infocodest/

# Tests
pytest tests/ -v --cov=infocodest

# Configuration validation
python scripts/verification/verify_config.py
```

## Troubleshooting

### Workflow fails on "Install dependencies"

**Cause**: Missing or incompatible dependencies

**Solution**:
- Update `requirements.txt` or `requirements-dev.txt`
- Ensure all dependencies are pinned to specific versions
- Check for Python version compatibility

### Unit tests fail

**Cause**: Test environment not properly configured

**Solution**:
- Ensure `TESTING=True` environment variable is set
- Check that test database is created
- Verify all required CSV files exist

### Security scan reports vulnerabilities

**Cause**: Outdated or vulnerable dependencies

**Solution**:
- Update vulnerable packages: `pip install --upgrade <package>`
- Review Bandit report for code security issues
- Update `requirements.txt` with patched versions

## GitHub Secrets Required

For future deployment workflows, the following secrets will be required:

- `STAGING_SSH_KEY`: SSH key for staging deployment
- `STAGING_HOST`: Staging server hostname
- `STAGING_USER`: Staging server username
- `PRODUCTION_SSH_KEY`: SSH key for production deployment
- `PRODUCTION_HOST`: Production server hostname
- `PRODUCTION_USER`: Production server username
- `DOCKERHUB_USERNAME`: Docker Hub username (if using containers)
- `DOCKERHUB_TOKEN`: Docker Hub access token

## Contributing

When adding new workflows:

1. Follow the existing naming convention: `{purpose}-{target}.yml`
2. Add comprehensive job names and descriptions
3. Use appropriate triggers (push, pull_request, schedule, etc.)
4. Include error handling and artifact uploads
5. Update this README with new workflow documentation

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
