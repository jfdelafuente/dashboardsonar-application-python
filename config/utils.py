"""
Configuration utilities shared across the application.

This module provides utility functions used by configuration classes:
- mask_db_uri: Mask passwords in database URIs for secure logging
- str_to_bool: Convert string environment variables to boolean values safely
- build_database_uri: Build SQLAlchemy database URIs with proper escaping
"""
from typing import Optional
from pathlib import Path
from urllib.parse import quote_plus


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


def build_database_uri(
    engine: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    sqlite_path: Optional[Path] = None
) -> str:
    """
    Build a SQLAlchemy database URI with proper escaping.

    Supports SQLite and server-based databases (PostgreSQL, MySQL, etc.).
    Automatically escapes special characters in username and password using URL encoding.

    Args:
        engine: Database engine (postgresql, mysql, sqlite)
        username: Database username (not needed for SQLite)
        password: Database password (optional)
        host: Database host (not needed for SQLite)
        port: Database port (not needed for SQLite)
        database: Database name
        sqlite_path: Path to SQLite file (only for SQLite engine)

    Returns:
        Properly formatted database URI

    Raises:
        ValueError: If required parameters are missing for the specified engine

    Examples:
        >>> from pathlib import Path
        >>> build_database_uri('sqlite', sqlite_path=Path('db.sqlite3'))
        'sqlite:///db.sqlite3'

        >>> build_database_uri(
        ...     'postgresql',
        ...     username='user',
        ...     password='my@pass',
        ...     host='localhost',
        ...     port=5432,
        ...     database='mydb'
        ... )
        'postgresql://user:my%40pass@localhost:5432/mydb'

        >>> build_database_uri(
        ...     'mysql',
        ...     username='root',
        ...     host='localhost',
        ...     database='test'
        ... )
        'mysql://root@localhost/test'
    """
    engine = engine.lower()

    if engine == 'sqlite':
        if not sqlite_path:
            raise ValueError("sqlite_path is required for SQLite engine")
        return f"sqlite:///{sqlite_path}"

    # For other engines, validate required parameters
    if not all([username, database]):
        raise ValueError(
            f"username and database are required for {engine} engine"
        )

    # Build URI with escaping for special characters
    username_escaped = quote_plus(username)

    if password:
        password_escaped = quote_plus(password)
        credentials = f"{username_escaped}:{password_escaped}"
    else:
        credentials = username_escaped

    # Host and port with defaults
    host = host or 'localhost'

    if port:
        host_port = f"{host}:{port}"
    else:
        host_port = host

    return f"{engine}://{credentials}@{host_port}/{database}"
