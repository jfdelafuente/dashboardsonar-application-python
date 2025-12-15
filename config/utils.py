"""
Configuration utilities shared across the application.

This module provides utility functions used by configuration classes:
- mask_db_uri: Mask passwords in database URIs for secure logging
- str_to_bool: Convert string environment variables to boolean values safely
"""
from typing import Optional


def mask_db_uri(uri: str) -> str:
    """
    Mask password in database URI for secure logging.

    Converts: postgresql://user:password@host/db
    To:       postgresql://user:***@host/db

    Args:
        uri: Database connection URI

    Returns:
        URI with masked password

    Examples:
        >>> mask_db_uri('postgresql://user:pass123@localhost/db')
        'postgresql://user:***@localhost/db'

        >>> mask_db_uri('sqlite:///path/to/db.sqlite3')
        'sqlite:///path/to/db.sqlite3'
    """
    if not uri:
        return uri

    # Format: scheme://user:password@host/path
    if '@' in uri and ':' in uri:
        parts = uri.split('@')
        if ':' in parts[0]:
            protocol_and_user = parts[0].rsplit(':', 1)
            return f"{protocol_and_user[0]}:***@{parts[1]}"

    return uri


def str_to_bool(value: Optional[str], default: bool = False) -> bool:
    """
    Convert string to boolean safely.

    Accepts: 'true', '1', 'yes', 'on' (case-insensitive) for True
    Accepts: 'false', '0', 'no', 'off' (case-insensitive) for False
    Returns default if value is None or empty.

    Args:
        value: String value to convert
        default: Default boolean value if conversion fails

    Returns:
        Boolean value

    Examples:
        >>> str_to_bool('true')
        True
        >>> str_to_bool('FALSE')
        False
        >>> str_to_bool('1')
        True
        >>> str_to_bool(None, default=True)
        True
    """
    if not value:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')
