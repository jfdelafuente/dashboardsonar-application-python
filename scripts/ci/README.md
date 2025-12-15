# CI/CD Scripts

This directory contains reusable scripts for Continuous Integration and Continuous Deployment workflows.

## Overview

These scripts are used by GitHub Actions workflows but can also be run locally for testing before pushing code.

## Available Scripts

### 🔍 lint.sh - Code Quality Checks

Runs all linting and code quality checks.

**Tools used**:
- Black - Code formatting
- isort - Import sorting
- Flake8 - Style guide enforcement
- Pylint - Additional linting (informational)
- mypy - Type checking (informational)

**Usage**:
```bash
# Check code quality
./scripts/ci/lint.sh

# Auto-fix issues where possible
./scripts/ci/lint.sh --fix
```

**Exit codes**:
- `0` - All checks passed
- `1` - One or more checks failed

---

### 🧪 test.sh - Test Suite

Runs the complete test suite with coverage reporting.

**Features**:
- Unit tests
- Integration tests
- Coverage reporting (terminal, XML, HTML)
- Configurable test paths and markers

**Usage**:
```bash
# Run all tests with coverage
./scripts/ci/test.sh

# Run only unit tests
./scripts/ci/test.sh --unit

# Run only integration tests
./scripts/ci/test.sh --integration

# Run with HTML coverage report
./scripts/ci/test.sh --html

# Run with verbose output
./scripts/ci/test.sh --verbose

# Run tests with specific marker
./scripts/ci/test.sh --markers slow

# Skip coverage
./scripts/ci/test.sh --no-coverage
```

**Exit codes**:
- `0` - All tests passed
- `1` - One or more tests failed

**Generated files**:
- `coverage.xml` - XML coverage report (for Codecov)
- `htmlcov/` - HTML coverage report (with `--html`)
- `.coverage` - Coverage data file (cleaned up automatically)

---

### 🔐 security.sh - Security Scanning

Runs security vulnerability scans on dependencies and code.

**Tools used**:
- Safety - Dependency vulnerability scanning
- Bandit - Code security analysis

**Usage**:
```bash
# Run all security scans
./scripts/ci/security.sh

# Scan only dependencies
./scripts/ci/security.sh --dependencies

# Scan only code
./scripts/ci/security.sh --code

# Output in JSON format
./scripts/ci/security.sh --json

# Fail on high severity issues
./scripts/ci/security.sh --fail-on-high
```

**Exit codes**:
- `0` - No critical issues found
- `1` - Critical security issues found (with `--fail-on-high`)

**Generated files** (with `--json`):
- `reports/safety-report-{timestamp}.json` - Dependency vulnerabilities
- `reports/bandit-report-{timestamp}.json` - Code security issues

---

## Running All Checks Locally

To run all checks before pushing:

```bash
# 1. Code quality
./scripts/ci/lint.sh

# 2. Security scanning
./scripts/ci/security.sh

# 3. Tests with coverage
./scripts/ci/test.sh --html
```

Or run them all in sequence:

```bash
./scripts/ci/lint.sh && \
./scripts/ci/security.sh && \
./scripts/ci/test.sh
```

## Prerequisites

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Script Permissions

Make scripts executable (Unix/Linux/Mac):

```bash
chmod +x scripts/ci/*.sh
```

On Windows with Git Bash:

```bash
git update-index --chmod=+x scripts/ci/lint.sh
git update-index --chmod=+x scripts/ci/test.sh
git update-index --chmod=+x scripts/ci/security.sh
```

## Environment Variables

Scripts use these environment variables (automatically set by CI):

**Testing** (`test.sh`):
- `TESTING=True` - Enable testing mode
- `FLASK_APP=run.py` - Flask application entry point
- `FLASK_DEBUG=0` - Disable debug mode
- `DEBUG=False` - Disable application debug
- `SECRET_KEY=test-secret-key-for-ci` - Test secret key
- `SQLITE_DB_FILE=test.sqlite3` - Test database file

## Continuous Integration Usage

These scripts are automatically run by GitHub Actions workflows:

- **lint.sh** - Used by `ci-pull-request.yml` → Code Quality job
- **test.sh** - Used by `ci-pull-request.yml` → Unit Tests job
- **security.sh** - Used by `ci-pull-request.yml` → Security Scan job

See [.github/workflows/](./.github/workflows/) for workflow definitions.

## Troubleshooting

### Script not found or permission denied

**Unix/Linux/Mac**:
```bash
chmod +x scripts/ci/lint.sh
```

**Windows (Git Bash)**:
```bash
bash scripts/ci/lint.sh
```

### Tests fail with "No module named 'infocodest'"

Make sure you're running from the project root:
```bash
cd /path/to/dashboardsonar-application-python
./scripts/ci/test.sh
```

### Safety check fails

Update `requirements.txt` with patched versions:
```bash
pip install --upgrade <vulnerable-package>
pip freeze > requirements.txt
```

### Bandit reports false positives

Add `# nosec` comment to the line:
```python
password = get_env_variable('PASSWORD')  # nosec B105
```

## CI/CD Integration

For complete CI/CD pipeline documentation, see:

- [.github/README.md](../../.github/README.md) - Workflows documentation
- [docs/plan/PLAN_CICD_AUTOMATION.md](../../docs/plan/PLAN_CICD_AUTOMATION.md) - Implementation plan

## Contributing

When adding new CI scripts:

1. Follow the existing naming convention: `{purpose}.sh`
2. Add comprehensive help text at the top of the script
3. Use color-coded output (RED, GREEN, YELLOW, BLUE)
4. Support `--help` option
5. Return appropriate exit codes (0 = success, 1 = failure)
6. Update this README with usage instructions
