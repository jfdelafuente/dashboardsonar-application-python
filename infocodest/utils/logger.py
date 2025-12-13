"""
Logging System Module
=====================

Provides structured logging with request context and file rotation.

Features:
    - Request-aware logging with URL, method, and IP address
    - Rotating file handlers (10MB per file, 10 backups)
    - Separate log files by severity (info.log, error.log)
    - Console output with environment-aware log levels
    - Integration with Flask application context

Usage:
    from infocodest.utils.logger import setup_logging

    # In application factory
    app = Flask(__name__)
    setup_logging(app)

    # In code
    app.logger.info("Processing request")
    app.logger.error("Failed to process", exc_info=True)

Created: Phase 4 - Utilities System
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

try:
    from flask import Flask, has_request_context, request
except ImportError:
    # Fallback for testing without Flask
    Flask = None
    has_request_context = lambda: False
    request = None


class RequestFormatter(logging.Formatter):
    """
    Custom formatter that includes Flask request context.

    Adds request URL, HTTP method, and client IP to log records
    when running within a Flask request context.

    Attributes:
        Inherits from logging.Formatter
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with request context if available.

        Args:
            record: Log record to format

        Returns:
            Formatted log message string
        """
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None

        return super().format(record)


def setup_logging(app: 'Flask') -> None:
    """
    Configure structured logging for the Flask application.

    Creates rotating file handlers for different log levels and
    configures console output based on the environment.

    Log Files:
        - logs/info.log: INFO and above (10MB rotation, 10 backups)
        - logs/error.log: ERROR and above (10MB rotation, 10 backups)
        - Console: DEBUG in development, WARNING in production

    Args:
        app: Flask application instance

    Side Effects:
        - Creates logs/ directory if it doesn't exist
        - Configures app.logger with multiple handlers
        - Removes default Flask stream handlers

    Example:
        >>> from flask import Flask
        >>> from infocodest.utils.logger import setup_logging
        >>> app = Flask(__name__)
        >>> setup_logging(app)
        >>> app.logger.info("Application started")
    """
    if app is None:
        raise ValueError("Flask app instance is required")

    # Create logs directory
    logs_dir = Path(app.root_path).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)

    # Define log formats
    file_formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d: %(message)s'
        ' [%(method)s %(url)s from %(remote_addr)s]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create rotating file handler for INFO level
    info_handler = RotatingFileHandler(
        logs_dir / 'info.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(file_formatter)

    # Create rotating file handler for ERROR level
    error_handler = RotatingFileHandler(
        logs_dir / 'error.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_level = logging.DEBUG if app.config.get('DEBUG', False) else logging.WARNING
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)

    # Configure app logger
    app.logger.setLevel(logging.DEBUG)

    # Remove default handlers to avoid duplicates
    app.logger.handlers.clear()

    # Add our custom handlers
    app.logger.addHandler(info_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)

    # Prevent propagation to root logger
    app.logger.propagate = False

    app.logger.info(f'Logging system initialized - Console level: {logging.getLevelName(console_level)}')


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance for use outside Flask context.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)

    Returns:
        Configured Logger instance

    Example:
        >>> from infocodest.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Script started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
