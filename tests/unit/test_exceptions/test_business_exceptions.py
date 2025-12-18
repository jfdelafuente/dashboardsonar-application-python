"""
Unit tests for business exception classes.

Tests custom business exceptions and their attributes.

Updated: Priority 3 - Added pytest markers
"""

import pytest
from datetime import date
from infocodest.exceptions.base import (
    ApplicationException,
    BusinessException,
    ValidationException,
    NotFoundException
)
from infocodest.exceptions.business_exceptions import (
    ApplicationNotFoundException,
    InvalidApplicationNameException,
    MetricNotFoundException,
    InvalidMetricValueException,
    InvalidDateRangeException
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestApplicationException:
    """Test suite for base ApplicationException."""

    def test_create_with_message(self):
        """Test creating exception with message."""
        exc = ApplicationException("Test error")

        assert exc.message == "Test error"
        assert exc.status_code == 500  # Default
        assert exc.payload == {}

    def test_create_with_custom_status_code(self):
        """Test creating exception with custom status code."""
        exc = ApplicationException("Test error", status_code=400)

        assert exc.message == "Test error"
        assert exc.status_code == 400

    def test_create_with_payload(self):
        """Test creating exception with additional payload."""
        payload = {"field": "value", "code": 123}
        exc = ApplicationException("Test error", payload=payload)

        assert exc.message == "Test error"
        assert exc.payload == payload

    def test_to_dict(self):
        """Test converting exception to dictionary."""
        exc = ApplicationException("Test error", payload={"extra": "data"})
        result = exc.to_dict()

        assert result['error'] == 'ApplicationException'
        assert result['message'] == 'Test error'
        assert result['extra'] == 'data'

    def test_to_dict_no_payload(self):
        """Test to_dict with no payload."""
        exc = ApplicationException("Test error")
        result = exc.to_dict()

        assert result['error'] == 'ApplicationException'
        assert result['message'] == 'Test error'
        assert 'extra' not in result

    def test_exception_can_be_raised(self):
        """Test exception can be raised and caught."""
        with pytest.raises(ApplicationException) as exc_info:
            raise ApplicationException("Test error")

        assert "Test error" in str(exc_info.value)

    def test_exception_str_representation(self):
        """Test string representation of exception."""
        exc = ApplicationException("Test error")
        assert str(exc) == "Test error"


class TestBusinessException:
    """Test suite for BusinessException."""

    def test_default_status_code(self):
        """Test BusinessException has correct default status code."""
        exc = BusinessException("Business error")

        assert exc.status_code == 422  # Unprocessable Entity
        assert exc.message == "Business error"

    def test_custom_status_code(self):
        """Test BusinessException with custom status code."""
        exc = BusinessException("Business error", status_code=400)

        assert exc.status_code == 400

    def test_inherits_from_application_exception(self):
        """Test BusinessException is an ApplicationException."""
        exc = BusinessException("Business error")

        assert isinstance(exc, ApplicationException)
        assert isinstance(exc, BusinessException)

    def test_to_dict(self):
        """Test BusinessException to_dict."""
        exc = BusinessException("Business error", payload={"rule": "violated"})
        result = exc.to_dict()

        assert result['error'] == 'BusinessException'
        assert result['message'] == 'Business error'
        assert result['rule'] == 'violated'


class TestValidationException:
    """Test suite for ValidationException."""

    def test_create_with_field(self):
        """Test creating validation exception with field name."""
        exc = ValidationException("Invalid value", field="email")

        assert exc.message == "Invalid value"
        assert exc.payload.get('field') == "email"

    def test_to_dict_includes_field(self):
        """Test to_dict includes field information."""
        exc = ValidationException("Invalid email", field="email")
        result = exc.to_dict()

        assert result['error'] == 'ValidationException'
        assert result['message'] == 'Invalid email'
        assert result['field'] == 'email'

    def test_inherits_from_business_exception(self):
        """Test ValidationException is a BusinessException."""
        exc = ValidationException("Invalid value")

        assert isinstance(exc, BusinessException)
        assert isinstance(exc, ApplicationException)


class TestNotFoundException:
    """Test suite for NotFoundException."""

    def test_default_status_code(self):
        """Test NotFoundException has 404 status code."""
        exc = NotFoundException(resource="User", identifier="123")

        assert exc.status_code == 404

    def test_message_format(self):
        """Test NotFoundException formats message correctly."""
        exc = NotFoundException(resource="User", identifier="123")

        assert "User" in exc.message
        assert "123" in exc.message
        assert "not found" in exc.message.lower()

    def test_to_dict(self):
        """Test NotFoundException to_dict."""
        exc = NotFoundException(resource="Application", identifier="myapp")
        result = exc.to_dict()

        assert result['error'] == 'NotFoundException'
        assert 'Application' in result['message']
        assert 'myapp' in result['message']

    def test_inherits_from_business_exception(self):
        """Test NotFoundException is a BusinessException."""
        exc = NotFoundException(resource="Test", identifier="1")

        assert isinstance(exc, BusinessException)
        assert isinstance(exc, ApplicationException)


class TestApplicationNotFoundException:
    """Test suite for ApplicationNotFoundException."""

    def test_create_with_app_name(self):
        """Test creating exception with application name."""
        exc = ApplicationNotFoundException("my-app")

        assert exc.app_name == "my-app"
        assert "my-app" in exc.message
        assert "Application" in exc.message

    def test_status_code_is_404(self):
        """Test exception has 404 status code."""
        exc = ApplicationNotFoundException("my-app")

        assert exc.status_code == 404

    def test_inherits_from_not_found(self):
        """Test ApplicationNotFoundException is a NotFoundException."""
        exc = ApplicationNotFoundException("my-app")

        assert isinstance(exc, NotFoundException)
        assert isinstance(exc, BusinessException)

    def test_can_be_raised_and_caught(self):
        """Test exception can be raised and caught."""
        with pytest.raises(ApplicationNotFoundException) as exc_info:
            raise ApplicationNotFoundException("test-app")

        assert exc_info.value.app_name == "test-app"


class TestInvalidApplicationNameException:
    """Test suite for InvalidApplicationNameException."""

    def test_create_with_name_only(self):
        """Test creating exception with just app name."""
        exc = InvalidApplicationNameException("invalid name")

        assert "invalid name" in exc.message
        assert "Invalid application name" in exc.message

    def test_create_with_reason(self):
        """Test creating exception with reason."""
        exc = InvalidApplicationNameException("", reason="Empty name not allowed")

        assert "Empty name not allowed" in exc.message

    def test_status_code_is_422(self):
        """Test exception has 422 status code."""
        exc = InvalidApplicationNameException("bad-name")

        assert exc.status_code == 422

    def test_field_in_payload(self):
        """Test exception includes field in payload."""
        exc = InvalidApplicationNameException("bad-name")
        result = exc.to_dict()

        assert result['field'] == 'application_name'

    def test_inherits_from_validation_exception(self):
        """Test exception is a ValidationException."""
        exc = InvalidApplicationNameException("bad-name")

        assert isinstance(exc, ValidationException)
        assert isinstance(exc, BusinessException)


class TestMetricNotFoundException:
    """Test suite for MetricNotFoundException."""

    def test_create_with_metric_id(self):
        """Test creating exception with metric ID."""
        exc = MetricNotFoundException(metric_id=123)

        assert "123" in exc.message
        assert "Metric" in exc.message

    def test_create_with_kwargs(self):
        """Test creating exception with keyword arguments."""
        exc = MetricNotFoundException(app_name="myapp", date="2025-12-01")

        assert "app_name" in exc.message
        assert "myapp" in exc.message
        assert "date" in exc.message

    def test_create_with_no_identifier(self):
        """Test creating exception with no identifier."""
        exc = MetricNotFoundException()

        assert "Metric" in exc.message

    def test_status_code_is_404(self):
        """Test exception has 404 status code."""
        exc = MetricNotFoundException(metric_id=123)

        assert exc.status_code == 404

    def test_inherits_from_not_found(self):
        """Test exception is a NotFoundException."""
        exc = MetricNotFoundException(metric_id=123)

        assert isinstance(exc, NotFoundException)
        assert isinstance(exc, BusinessException)


class TestInvalidMetricValueException:
    """Test suite for InvalidMetricValueException."""

    def test_create_with_all_params(self):
        """Test creating exception with all parameters."""
        exc = InvalidMetricValueException(
            metric_name="coverage",
            value=-5,
            reason="Must be >= 0"
        )

        assert "coverage" in exc.message
        assert "-5" in exc.message
        assert "Must be >= 0" in exc.message

    def test_value_in_payload(self):
        """Test value is included in payload."""
        exc = InvalidMetricValueException(
            metric_name="bugs",
            value="invalid",
            reason="Must be integer"
        )
        result = exc.to_dict()

        assert result['value'] == "invalid"

    def test_field_is_metric_name(self):
        """Test field is set to metric name."""
        exc = InvalidMetricValueException(
            metric_name="coverage",
            value=-5,
            reason="Must be >= 0"
        )
        result = exc.to_dict()

        assert result['field'] == "coverage"

    def test_status_code_is_422(self):
        """Test exception has 422 status code."""
        exc = InvalidMetricValueException(
            metric_name="coverage",
            value=-5,
            reason="Invalid"
        )

        assert exc.status_code == 422

    def test_inherits_from_validation_exception(self):
        """Test exception is a ValidationException."""
        exc = InvalidMetricValueException(
            metric_name="test",
            value=0,
            reason="Invalid"
        )

        assert isinstance(exc, ValidationException)
        assert isinstance(exc, BusinessException)


class TestInvalidDateRangeException:
    """Test suite for InvalidDateRangeException."""

    def test_create_with_dates(self):
        """Test creating exception with date range."""
        start = date(2025, 12, 31)
        end = date(2025, 1, 1)
        exc = InvalidDateRangeException(start_date=start, end_date=end)

        assert "2025-12-31" in exc.message
        assert "2025-01-01" in exc.message
        assert "start date" in exc.message.lower()

    def test_dates_in_payload(self):
        """Test dates are included in payload."""
        start = date(2025, 12, 31)
        end = date(2025, 1, 1)
        exc = InvalidDateRangeException(start_date=start, end_date=end)
        result = exc.to_dict()

        # Dates should be in payload
        assert 'start_date' in result or '2025-12-31' in exc.message
        assert 'end_date' in result or '2025-01-01' in exc.message

    def test_status_code_is_422(self):
        """Test exception has 422 status code."""
        exc = InvalidDateRangeException(
            start_date=date(2025, 12, 31),
            end_date=date(2025, 1, 1)
        )

        assert exc.status_code == 422

    def test_inherits_from_validation_exception(self):
        """Test exception is a ValidationException."""
        exc = InvalidDateRangeException(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 10)
        )

        assert isinstance(exc, ValidationException)
        assert isinstance(exc, BusinessException)


class TestExceptionInheritanceHierarchy:
    """Test suite for exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test all custom exceptions inherit from ApplicationException."""
        exceptions = [
            ApplicationException("test"),
            BusinessException("test"),
            ValidationException("test"),
            NotFoundException("Resource", "123"),
            ApplicationNotFoundException("app"),
            InvalidApplicationNameException("name"),
            MetricNotFoundException(metric_id=1),
            InvalidMetricValueException("metric", 0, "reason"),
            InvalidDateRangeException(date(2025, 1, 1), date(2025, 1, 10))
        ]

        for exc in exceptions:
            assert isinstance(exc, ApplicationException)

    def test_business_exceptions_inherit_correctly(self):
        """Test business exceptions inherit from BusinessException."""
        business_exceptions = [
            BusinessException("test"),
            ValidationException("test"),
            NotFoundException("Resource", "123"),
            ApplicationNotFoundException("app"),
            InvalidApplicationNameException("name"),
        ]

        for exc in business_exceptions:
            assert isinstance(exc, BusinessException)

    def test_validation_exceptions_inherit_correctly(self):
        """Test validation exceptions inherit from ValidationException."""
        validation_exceptions = [
            ValidationException("test"),
            InvalidApplicationNameException("name"),
            InvalidMetricValueException("metric", 0, "reason"),
            InvalidDateRangeException(date(2025, 1, 1), date(2025, 1, 10))
        ]

        for exc in validation_exceptions:
            assert isinstance(exc, ValidationException)

    def test_not_found_exceptions_inherit_correctly(self):
        """Test not found exceptions inherit from NotFoundException."""
        not_found_exceptions = [
            NotFoundException("Resource", "123"),
            ApplicationNotFoundException("app"),
            MetricNotFoundException(metric_id=1),
        ]

        for exc in not_found_exceptions:
            assert isinstance(exc, NotFoundException)
