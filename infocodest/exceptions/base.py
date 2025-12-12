"""
Base Exception Classes
======================

Provides base exception hierarchy for the application.

Features:
    - HTTP status code support
    - Custom error messages
    - Exception categorization
    - Logging integration

Usage:
    from infocodest.exceptions.base import ApplicationException, BusinessException

    raise BusinessException("Invalid operation", status_code=422)

Created: Phase 5 - Exception Handling System
"""

from typing import Optional, Dict, Any


class ApplicationException(Exception):
    """
    Base exception for all application errors.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (default: 500)
        payload: Additional error context

    Example:
        >>> raise ApplicationException("Database connection failed", status_code=503)

    Notes:
        - All custom exceptions should inherit from this class
        - Automatically logged by error handlers
        - Can include additional payload for debugging
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        payload: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize application exception.

        Args:
            message: Error description
            status_code: HTTP status code
            payload: Optional additional context
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON serialization.

        Returns:
            Dictionary with error, message, and payload

        Example:
            >>> exc = ApplicationException("Error", payload={"field": "value"})
            >>> exc.to_dict()
            {'error': 'ApplicationException', 'message': 'Error', 'field': 'value'}
        """
        result = dict(self.payload)
        result['error'] = self.__class__.__name__
        result['message'] = self.message
        return result


class BusinessException(ApplicationException):
    """
    Exception for business logic violations.

    Represents errors in business rules, validation failures,
    and domain-specific constraints.

    Example:
        >>> raise BusinessException("Application not found")

    Notes:
        - Default status code: 422 (Unprocessable Entity)
        - Used for validation errors and business rule violations
        - Should be caught and presented to user
    """

    def __init__(
        self,
        message: str,
        status_code: int = 422,
        payload: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize business exception.

        Args:
            message: Business rule violation description
            status_code: HTTP status code (default: 422)
            payload: Optional validation context
        """
        super().__init__(message, status_code, payload)


class ValidationException(BusinessException):
    """
    Exception for input validation failures.

    Example:
        >>> raise ValidationException("Invalid email format", field="email")

    Notes:
        - Subclass of BusinessException
        - Includes field information in payload
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize validation exception.

        Args:
            message: Validation error description
            field: Field that failed validation
            payload: Additional validation context
        """
        payload = payload or {}
        if field:
            payload['field'] = field
        super().__init__(message, status_code=422, payload=payload)


class NotFoundException(ApplicationException):
    """
    Exception for resource not found errors.

    Example:
        >>> raise NotFoundException("User", user_id=123)

    Notes:
        - Status code: 404
        - Includes resource type and identifier
    """

    def __init__(
        self,
        resource: str,
        identifier: Optional[Any] = None,
        payload: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize not found exception.

        Args:
            resource: Type of resource not found
            identifier: Resource identifier
            payload: Additional context
        """
        message = f"{resource} not found"
        if identifier is not None:
            message += f": {identifier}"

        payload = payload or {}
        payload['resource'] = resource
        if identifier is not None:
            payload['identifier'] = str(identifier)

        super().__init__(message, status_code=404, payload=payload)


class DatabaseException(ApplicationException):
    """
    Exception for database operation failures.

    Example:
        >>> raise DatabaseException("Failed to save metric")

    Notes:
        - Status code: 500
        - Used for DB connection, query, or integrity errors
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize database exception.

        Args:
            message: Error description
            operation: DB operation that failed (select, insert, etc.)
            payload: Additional context
        """
        payload = payload or {}
        if operation:
            payload['operation'] = operation
        super().__init__(message, status_code=500, payload=payload)
