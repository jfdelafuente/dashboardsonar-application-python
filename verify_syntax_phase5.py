"""
Syntax Verification Script for Phase 5
======================================

Verifies Python syntax for all Phase 5 exception files.

Usage:
    python verify_syntax_phase5.py

Exit codes:
    0: All files valid
    1: Syntax errors found
"""

import ast
import sys
from pathlib import Path

files_to_check = [
    'infocodest/exceptions/base.py',
    'infocodest/exceptions/business_exceptions.py',
    'infocodest/exceptions/__init__.py',
    'infocodest/errorhandlers.py',
]

errors = []

print("=" * 60)
print("Phase 5 - Syntax Verification")
print("=" * 60)
print()

for file_path in files_to_check:
    try:
        path = Path(file_path)
        if not path.exists():
            errors.append(f"[FAIL] {file_path}: File not found")
            continue

        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()

        ast.parse(code)
        print(f"[OK] {file_path}: Syntax OK")
    except SyntaxError as e:
        errors.append(f"[FAIL] {file_path}: {e}")

print()
print("=" * 60)

if errors:
    print("Errors found:")
    print()
    for error in errors:
        print(f"  {error}")
    print()
    print("=" * 60)
    sys.exit(1)
else:
    print("[SUCCESS] All files have valid syntax!")
    print(f"[INFO] {len(files_to_check)} files checked")
    print("=" * 60)
    sys.exit(0)
