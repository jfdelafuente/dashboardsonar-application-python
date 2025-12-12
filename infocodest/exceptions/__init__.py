"""
Exceptions Module
=================

Provides custom exception hierarchy for the application.

Modules:
    - base: Base exception classes
    - business_exceptions: Domain-specific exceptions

Usage:
    from infocodest.exceptions import (
        ApplicationNotFoundException,
        InvalidDateRangeException,
        ValidationException
    )

    raise ApplicationNotFoundException("my-app")

Created: Phase 5 - Exception Handling System
"""

# Base exceptions
from infocodest.exceptions.base import (
    ApplicationException,
    BusinessException,
    ValidationException,
    NotFoundException,
    DatabaseException
)

# Domain-specific exceptions
from infocodest.exceptions.business_exceptions import (
    # Application
    ApplicationNotFoundException,
    InvalidApplicationNameException,

    # Metrics
    MetricNotFoundException,
    InvalidMetricValueException,

    # Dates
    InvalidDateRangeException,
    InvalidDateFormatException,

    # Providers
    ProviderNotFoundException,

    # Auth
    AuthenticationException,
    AuthorizationException,

    # Export
    ExportException,

    # Configuration
    ConfigurationException
)

__all__ = [
    # Base
    'ApplicationException',
    'BusinessException',
    'ValidationException',
    'NotFoundException',
    'DatabaseException',

    # Application
    'ApplicationNotFoundException',
    'InvalidApplicationNameException',

    # Metrics
    'MetricNotFoundException',
    'InvalidMetricValueException',

    # Dates
    'InvalidDateRangeException',
    'InvalidDateFormatException',

    # Providers
    'ProviderNotFoundException',

    # Auth
    'AuthenticationException',
    'AuthorizationException',

    # Export
    'ExportException',

    # Configuration
    'ConfigurationException',
]
