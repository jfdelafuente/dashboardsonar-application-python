"""
Utilities Module
================

Provides cross-cutting utilities for the application.

Modules:
    - logger: Structured logging system
    - decorators: Utility decorators (DI, timing, deprecation, retry)
    - validators: Input validation functions
    - helpers: Common helper functions

Usage:
    from infocodest.utils import setup_logging, inject_service
    from infocodest.utils import validate_date_range, format_percentage

Created: Phase 4 - Utilities System
"""

# Logger
from infocodest.utils.logger import (
    setup_logging,
    get_logger,
    RequestFormatter
)

# Decorators
from infocodest.utils.decorators import (
    inject_service,
    log_execution_time,
    deprecated,
    retry
)

# Validators
from infocodest.utils.validators import (
    validate_date_range,
    validate_application_name,
    validate_metric_value,
    validate_email,
    validate_repository_name,
    validate_percentage,
    validate_rating
)

# Helpers
from infocodest.utils.helpers import (
    format_percentage,
    calculate_variation,
    safe_division,
    parse_date_string,
    get_variation_trend,
    truncate_string,
    get_quality_gate_color,
    get_rating_color
)

__all__ = [
    # Logger
    'setup_logging',
    'get_logger',
    'RequestFormatter',

    # Decorators
    'inject_service',
    'log_execution_time',
    'deprecated',
    'retry',

    # Validators
    'validate_date_range',
    'validate_application_name',
    'validate_metric_value',
    'validate_email',
    'validate_repository_name',
    'validate_percentage',
    'validate_rating',

    # Helpers
    'format_percentage',
    'calculate_variation',
    'safe_division',
    'parse_date_string',
    'get_variation_trend',
    'truncate_string',
    'get_quality_gate_color',
    'get_rating_color',
]
