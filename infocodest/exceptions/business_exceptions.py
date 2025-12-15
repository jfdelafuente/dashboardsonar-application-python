"""
Business-Specific Exceptions
============================

Provides domain-specific exceptions for application business logic.

Modules:
    - Metric-related exceptions
    - Application-related exceptions
    - Provider-related exceptions
    - Authentication-related exceptions

Usage:
    from infocodest.exceptions.business_exceptions import (
        ApplicationNotFoundException,
        InvalidDateRangeException
    )

    if not app:
        raise ApplicationNotFoundException(app_name)

Created: Phase 5 - Exception Handling System
"""

from typing import Optional, Any
from datetime import date

from infocodest.exceptions.base import (
    BusinessException,
    ValidationException,
    NotFoundException
)


# ============================================================================
# Application Exceptions
# ============================================================================

class ApplicationNotFoundException(NotFoundException):
    """
    Exception raised when an application is not found.

    Example:
        >>> raise ApplicationNotFoundException("my-app")

    Attributes:
        app_name: Name of the application not found
    """

    def __init__(self, app_name: str):
        """
        Initialize exception.

        Args:
            app_name: Application name that was not found
        """
        super().__init__(resource="Application", identifier=app_name)
        self.app_name = app_name


class InvalidApplicationNameException(ValidationException):
    """
    Exception raised when application name is invalid.

    Example:
        >>> raise InvalidApplicationNameException("", reason="Empty name")
    """

    def __init__(self, app_name: str, reason: Optional[str] = None):
        """
        Initialize exception.

        Args:
            app_name: Invalid application name
            reason: Reason why name is invalid
        """
        message = f"Invalid application name: {app_name}"
        if reason:
            message += f" ({reason})"
        super().__init__(message, field="application_name")


# ============================================================================
# Metric Exceptions
# ============================================================================

class MetricNotFoundException(NotFoundException):
    """
    Exception raised when a metric is not found.

    Example:
        >>> raise MetricNotFoundException(metric_id=123)
    """

    def __init__(self, metric_id: Optional[int] = None, **kwargs):
        """
        Initialize exception.

        Args:
            metric_id: ID of metric not found
            **kwargs: Additional identifiers (app_name, date, etc.)
        """
        identifier = metric_id
        if not identifier and kwargs:
            identifier = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        super().__init__(resource="Metric", identifier=identifier)


class InvalidMetricValueException(ValidationException):
    """
    Exception raised when a metric value is invalid.

    Example:
        >>> raise InvalidMetricValueException("coverage", -5, "Must be >= 0")
    """

    def __init__(
        self,
        metric_name: str,
        value: Any,
        reason: str
    ):
        """
        Initialize exception.

        Args:
            metric_name: Name of the metric
            value: Invalid value
            reason: Why the value is invalid
        """
        message = f"Invalid value for {metric_name}: {value} ({reason})"
        super().__init__(message, field=metric_name, payload={'value': value})


# ============================================================================
# Date/Time Exceptions
# ============================================================================

class InvalidDateRangeException(ValidationException):
    """
    Exception raised when date range is invalid.

    Example:
        >>> raise InvalidDateRangeException(
        ...     start_date=date(2025, 1, 10),
        ...     end_date=date(2025, 1, 1)
        ... )
    """

    def __init__(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        reason: Optional[str] = None
    ):
        """
        Initialize exception.

        Args:
            start_date: Start date of invalid range
            end_date: End date of invalid range
            reason: Specific reason for invalidity
        """
        message = "Invalid date range"

        payload = {}
        if start_date:
            payload['start_date'] = start_date.isoformat()
        if end_date:
            payload['end_date'] = end_date.isoformat()

        if reason:
            message += f": {reason}"
        elif start_date and end_date:
            message += f": start date ({start_date}) must be <= end date ({end_date})"

        super().__init__(message, field="date_range", payload=payload)


class InvalidDateFormatException(ValidationException):
    """
    Exception raised when date format is invalid.

    Example:
        >>> raise InvalidDateFormatException("2025-99-99")
    """

    def __init__(self, date_str: str, expected_format: Optional[str] = None):
        """
        Initialize exception.

        Args:
            date_str: Invalid date string
            expected_format: Expected date format (e.g., "YYYY-MM-DD")
        """
        message = f"Invalid date format: {date_str}"
        if expected_format:
            message += f" (expected: {expected_format})"
        super().__init__(message, field="date")


# ============================================================================
# Provider Exceptions
# ============================================================================

class ProviderNotFoundException(NotFoundException):
    """
    Exception raised when a provider is not found.

    Example:
        >>> raise ProviderNotFoundException(provider_name="github")
    """

    def __init__(self, provider_name: str):
        """
        Initialize exception.

        Args:
            provider_name: Name of provider not found
        """
        super().__init__(resource="Provider", identifier=provider_name)


# ============================================================================
# Authentication/Authorization Exceptions
# ============================================================================

class AuthenticationException(BusinessException):
    """
    Exception raised for authentication failures.

    Example:
        >>> raise AuthenticationException("Invalid credentials")
    """

    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize exception.

        Args:
            message: Authentication error message
        """
        super().__init__(message, status_code=401)


class AuthorizationException(BusinessException):
    """
    Exception raised for authorization failures.

    Example:
        >>> raise AuthorizationException("Insufficient permissions")
    """

    def __init__(self, message: str = "Authorization failed"):
        """
        Initialize exception.

        Args:
            message: Authorization error message
        """
        super().__init__(message, status_code=403)


# ============================================================================
# Data Export Exceptions
# ============================================================================

class ExportException(BusinessException):
    """
    Exception raised when data export fails.

    Example:
        >>> raise ExportException("CSV", "Invalid data format")
    """

    def __init__(self, export_format: str, reason: str):
        """
        Initialize exception.

        Args:
            export_format: Export format that failed (CSV, PDF, etc.)
            reason: Reason for export failure
        """
        message = f"Failed to export as {export_format}: {reason}"
        super().__init__(message, payload={'format': export_format})


# ============================================================================
# Configuration Exceptions
# ============================================================================

class ConfigurationException(BusinessException):
    """
    Exception raised for configuration errors.

    Example:
        >>> raise ConfigurationException("DATABASE_URL", "Missing required config")
    """

    def __init__(self, config_key: str, reason: str):
        """
        Initialize exception.

        Args:
            config_key: Configuration key with error
            reason: Reason for configuration error
        """
        message = f"Configuration error for '{config_key}': {reason}"
        super().__init__(
            message,
            status_code=500,
            payload={'config_key': config_key}
        )
