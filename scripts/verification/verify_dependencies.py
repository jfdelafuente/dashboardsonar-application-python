"""
Dependency Verification Script
===============================

Verifies that all required dependencies are installed and compatible.

Usage:
    python scripts/verify_dependencies.py

Exit codes:
    0: All dependencies verified successfully
    1: Missing or incompatible dependencies

Created: Phase 7 - Dependencies Optimization
"""

import sys
import importlib
import pkg_resources
from typing import List, Tuple

# Required packages with minimum versions
REQUIRED_PACKAGES = {
    'flask': '3.0.0',
    'sqlalchemy': '2.0.0',
    'flask_login': '0.6.0',
    'flask_wtf': '1.2.0',
    'flask_sqlalchemy': '3.1.0',
    'flask_migrate': '4.0.0',
    'flask_bcrypt': '1.0.0',
    'wtforms': '3.1.0',
    'alembic': '1.12.0',
    'bcrypt': '4.0.0',
    'email_validator': '2.1.0',
    'python_decouple': '3.8',
    'schedule': '1.2.0',
}

# Development-only packages (optional)
DEV_PACKAGES = {
    'pytest': '7.4.0',
    'pytest_cov': '4.1.0',
    'black': '23.12.0',
    'flake8': '6.1.0',
    'mypy': '1.7.0',
}


def check_package(package_name: str, min_version: str) -> Tuple[bool, str]:
    """
    Check if package is installed and meets minimum version.

    Args:
        package_name: Name of the package (with underscores)
        min_version: Minimum required version

    Returns:
        (success, message)
    """
    try:
        # Try to import
        importlib.import_module(package_name.replace('-', '_'))

        # Check version
        dist_name = package_name.replace('_', '-')
        installed_version = pkg_resources.get_distribution(dist_name).version

        if pkg_resources.parse_version(installed_version) >= pkg_resources.parse_version(min_version):
            return True, f"[OK] {dist_name} {installed_version} (>= {min_version})"
        else:
            return False, f"[FAIL] {dist_name} {installed_version} (< {min_version} required)"

    except ImportError:
        return False, f"[FAIL] {package_name.replace('_', '-')} not installed"
    except Exception as e:
        return False, f"[ERROR] {package_name.replace('_', '-')} error: {str(e)}"


def main():
    """Main verification function."""
    print("=" * 60)
    print("Dependency Verification - Dashboard Sonar")
    print("=" * 60)
    print()

    # Check production dependencies
    print("Production Dependencies:")
    print("-" * 60)
    prod_failures = []

    for package, min_version in sorted(REQUIRED_PACKAGES.items()):
        success, message = check_package(package, min_version)
        print(message)

        if not success:
            prod_failures.append(package)

    print()

    # Check development dependencies (optional)
    print("Development Dependencies (optional):")
    print("-" * 60)
    dev_failures = []

    for package, min_version in sorted(DEV_PACKAGES.items()):
        success, message = check_package(package, min_version)
        print(message)

        if not success:
            dev_failures.append(package)

    print()
    print("=" * 60)

    # Report results
    if prod_failures:
        print(f"[FAIL] {len(prod_failures)} production package(s) missing or incompatible:")
        for package in prod_failures:
            print(f"  - {package}")
        print()
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    elif dev_failures:
        print(f"[WARN] {len(dev_failures)} development package(s) missing (optional):")
        for package in dev_failures:
            print(f"  - {package}")
        print()
        print("Run: pip install -r requirements-dev.txt")
        print()
        print("[SUCCESS] All production dependencies verified!")
        sys.exit(0)
    else:
        print("[SUCCESS] All dependencies verified!")
        print("  Production dependencies: OK")
        print("  Development dependencies: OK")
        sys.exit(0)


if __name__ == '__main__':
    main()
