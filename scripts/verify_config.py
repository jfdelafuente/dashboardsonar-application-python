"""
Configuration Verification Script
==================================

Verifies that all configuration classes load correctly.

Usage:
    python scripts/verify_config.py

Exit codes:
    0: All configurations verified successfully
    1: Import errors or validation failures

Created: Phase 6 - Configuration System
"""

import sys

print("=" * 60)
print("Configuration Verification")
print("=" * 60)
print()

# Test 1: Import all config classes
print("[TEST 1] Importing config classes...")
try:
    from config import (
        BaseConfig,
        DevelopmentConfig,
        TestingConfig,
        ProductionConfig,
        config_dict
    )
    print("[OK] All config classes imported successfully")
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Verify config_dict structure
print("\n[TEST 2] Verifying config_dict structure...")
expected_keys = {'Production', 'Testing', 'Development', 'base'}
actual_keys = set(config_dict.keys())

if expected_keys == actual_keys:
    print(f"[OK] config_dict has all expected keys: {expected_keys}")
else:
    print(f"[FAIL] config_dict keys mismatch")
    print(f"  Expected: {expected_keys}")
    print(f"  Actual: {actual_keys}")
    sys.exit(1)

# Test 3: Verify each config class has required attributes
print("\n[TEST 3] Verifying required attributes...")
required_attributes = [
    'SECRET_KEY',
    'SQLALCHEMY_TRACK_MODIFICATIONS',
    'SQLALCHEMY_DATABASE_URI',
    'init_app'
]

for name, config_class in config_dict.items():
    print(f"\n  Testing {name}Config...")
    missing_attrs = []

    for attr in required_attributes:
        if not hasattr(config_class, attr):
            missing_attrs.append(attr)

    if missing_attrs:
        print(f"  [FAIL] {name}: Missing attributes: {missing_attrs}")
        sys.exit(1)
    else:
        print(f"  [OK] {name}: All required attributes present")

# Test 4: Verify inheritance
print("\n[TEST 4] Verifying inheritance...")
if issubclass(DevelopmentConfig, BaseConfig):
    print("  [OK] DevelopmentConfig inherits from BaseConfig")
else:
    print("  [FAIL] DevelopmentConfig does not inherit from BaseConfig")
    sys.exit(1)

if issubclass(TestingConfig, BaseConfig):
    print("  [OK] TestingConfig inherits from BaseConfig")
else:
    print("  [FAIL] TestingConfig does not inherit from BaseConfig")
    sys.exit(1)

if issubclass(ProductionConfig, BaseConfig):
    print("  [OK] ProductionConfig inherits from BaseConfig")
else:
    print("  [FAIL] ProductionConfig does not inherit from BaseConfig")
    sys.exit(1)

# Test 5: Verify environment-specific settings
print("\n[TEST 5] Verifying environment-specific settings...")

# Development should have DEBUG=True
if hasattr(DevelopmentConfig, 'DEBUG') and DevelopmentConfig.DEBUG:
    print("  [OK] DevelopmentConfig has DEBUG=True")
else:
    print("  [FAIL] DevelopmentConfig should have DEBUG=True")
    sys.exit(1)

# Production should have DEBUG=False
if hasattr(ProductionConfig, 'DEBUG') and not ProductionConfig.DEBUG:
    print("  [OK] ProductionConfig has DEBUG=False")
else:
    print("  [FAIL] ProductionConfig should have DEBUG=False")
    sys.exit(1)

# Testing should have TESTING=True
if hasattr(TestingConfig, 'TESTING') and TestingConfig.TESTING:
    print("  [OK] TestingConfig has TESTING=True")
else:
    print("  [FAIL] TestingConfig should have TESTING=True")
    sys.exit(1)

print()
print("=" * 60)
print("[SUCCESS] All configurations verified!")
print(f"[INFO] {len(config_dict)} configuration classes validated")
print("=" * 60)
sys.exit(0)
