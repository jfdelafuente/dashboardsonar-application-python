"""
Requirements Testing Script
============================

Simple script to test that requirements files can be parsed correctly.

Usage:
    python scripts/test_requirements.py

Exit codes:
    0: Requirements files are valid
    1: Requirements files have errors

Created: Phase 7 - Dependencies Optimization
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent

def test_requirements_file(filepath):
    """Test that a requirements file is valid."""
    print(f"\nTesting {filepath.name}...")

    if not filepath.exists():
        print(f"  [FAIL] File does not exist: {filepath}")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"  [OK] File is readable (UTF-8)")
        print(f"  [OK] Total lines: {len(lines)}")

        # Count packages (non-comment, non-empty, non-include lines)
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-r'):
                packages.append(line)

        print(f"  [OK] Packages listed: {len(packages)}")

        # Check for version pinning
        unpinned = []
        for pkg in packages:
            if '==' not in pkg:
                unpinned.append(pkg)

        if unpinned:
            print(f"  [WARN] Unpinned packages: {unpinned}")
        else:
            print(f"  [OK] All packages have pinned versions")

        # Check for duplicates
        pkg_names = [p.split('==')[0].lower() for p in packages]
        duplicates = set([name for name in pkg_names if pkg_names.count(name) > 1])

        if duplicates:
            print(f"  [FAIL] Duplicate packages: {duplicates}")
            return False
        else:
            print(f"  [OK] No duplicate packages")

        return True

    except UnicodeDecodeError as e:
        print(f"  [FAIL] Encoding error (not UTF-8): {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Error reading file: {e}")
        return False

def main():
    print("=" * 60)
    print("Requirements Files Verification")
    print("=" * 60)

    requirements_txt = project_root / 'requirements.txt'
    requirements_dev = project_root / 'requirements-dev.txt'

    success = True

    # Test requirements.txt
    if not test_requirements_file(requirements_txt):
        success = False

    # Test requirements-dev.txt
    if not test_requirements_file(requirements_dev):
        success = False

    print()
    print("=" * 60)

    if success:
        print("[SUCCESS] All requirements files are valid!")
        print()
        print("To install:")
        print("  Production: pip install -r requirements.txt")
        print("  Development: pip install -r requirements-dev.txt")
        sys.exit(0)
    else:
        print("[FAIL] Some requirements files have errors")
        sys.exit(1)

if __name__ == '__main__':
    main()
