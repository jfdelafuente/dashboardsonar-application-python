"""
Security utilities for password hashing and verification.

This module provides secure password hashing and verification functions
using PBKDF2-HMAC-SHA512 with salting.

Migrated from: infocodest/models/util.py (reorganization cleanup)
Original Copyright (c) 2019 - present AppSeed.us
Inspiration: https://www.vitoshacademy.com/hashing-passwords-in-python/
"""

import binascii
import hashlib
import os


def hash_pass(password):
    """Hash a password for storing.

    Uses PBKDF2-HMAC-SHA512 with 100,000 iterations and a random salt.

    Args:
        password (str): Plain text password to hash

    Returns:
        bytes: Salt + hashed password (for storage in database)

    Example:
        >>> hashed = hash_pass("mypassword")
        >>> # Store hashed in database
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return salt + pwdhash  # return bytes


def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user.

    Args:
        provided_password (str): Plain text password provided by user
        stored_password (bytes): Hashed password from database (salt + hash)

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> stored = hash_pass("mypassword")
        >>> verify_pass("mypassword", stored)
        True
        >>> verify_pass("wrongpassword", stored)
        False
    """
    stored_password = stored_password.decode("ascii")
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return pwdhash == stored_password