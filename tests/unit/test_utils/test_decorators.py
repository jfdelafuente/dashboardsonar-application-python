"""
Unit tests for infocodest.utils.decorators module

Tests all decorator functions:
    - inject_service: Service injection
    - log_execution_time: Execution time logging
    - deprecated: Deprecation warnings
    - retry: Retry mechanism
    - _service_class_to_param_name: Helper function

Created: Phase 6 - Test Coverage Improvements
Updated: Priority 3 - Added pytest markers
"""

import pytest

# Mark all tests in this module as unit and utils tests
pytestmark = [pytest.mark.unit, pytest.mark.utils]
import time
import warnings
from unittest.mock import Mock, patch, MagicMock
from infocodest.utils.decorators import (
    inject_service,
    log_execution_time,
    deprecated,
    retry,
    _service_class_to_param_name
)


# ============================================================================
# Test Classes/Fixtures
# ============================================================================

class DummyService:
    """Dummy service for testing inject_service decorator"""
    def __init__(self):
        self.name = "DummyService"
        self.data = {"test": "data"}

    def get_data(self):
        return self.data


class MetricaService:
    """Mock MetricaService for testing"""
    def __init__(self):
        self.name = "MetricaService"

    def get_all(self):
        return []


class DashboardService:
    """Mock DashboardService for testing"""
    def __init__(self):
        self.name = "DashboardService"


# ============================================================================
# Tests for inject_service
# ============================================================================

class TestInjectService:
    """Test suite for inject_service decorator"""

    def test_inject_service_basic(self):
        """
        GIVEN a function decorated with inject_service
        WHEN the function is called
        THEN the service instance is injected as keyword argument
        """
        @inject_service(DummyService)
        def my_view(dummy_service=None):
            return dummy_service

        result = my_view()

        assert result is not None
        assert isinstance(result, DummyService)
        assert result.name == "DummyService"

    def test_inject_service_with_args(self):
        """
        GIVEN a function with positional args decorated with inject_service
        WHEN the function is called with args
        THEN args are passed through and service is injected
        """
        @inject_service(DummyService)
        def my_view(arg1, arg2, dummy_service=None):
            return arg1, arg2, dummy_service

        result = my_view("hello", "world")

        assert result[0] == "hello"
        assert result[1] == "world"
        assert isinstance(result[2], DummyService)

    def test_inject_service_with_kwargs(self):
        """
        GIVEN a function with kwargs decorated with inject_service
        WHEN the function is called with kwargs
        THEN kwargs are passed through and service is injected
        """
        @inject_service(DummyService)
        def my_view(name="default", dummy_service=None):
            return name, dummy_service

        result = my_view(name="custom")

        assert result[0] == "custom"
        assert isinstance(result[1], DummyService)

    def test_inject_service_param_name_generation(self):
        """
        GIVEN various service classes
        WHEN inject_service is used
        THEN parameter names are generated correctly
        """
        @inject_service(MetricaService)
        def view1(metrica_service=None):
            return metrica_service

        @inject_service(DashboardService)
        def view2(dashboard_service=None):
            return dashboard_service

        result1 = view1()
        result2 = view2()

        assert isinstance(result1, MetricaService)
        assert isinstance(result2, DashboardService)

    def test_inject_service_preserves_function_metadata(self):
        """
        GIVEN a function with docstring and name
        WHEN decorated with inject_service
        THEN function metadata is preserved (functools.wraps)
        """
        @inject_service(DummyService)
        def my_special_view(dummy_service=None):
            """This is my special view"""
            return dummy_service

        assert my_special_view.__name__ == "my_special_view"
        assert my_special_view.__doc__ == "This is my special view"

    def test_inject_service_can_access_service_methods(self):
        """
        GIVEN a service with methods
        WHEN injected into a function
        THEN the function can call service methods
        """
        @inject_service(DummyService)
        def my_view(dummy_service=None):
            return dummy_service.get_data()

        result = my_view()

        assert result == {"test": "data"}


# ============================================================================
# Tests for log_execution_time
# ============================================================================

class TestLogExecutionTime:
    """Test suite for log_execution_time decorator"""

    def test_log_execution_time_basic(self):
        """
        GIVEN a function decorated with log_execution_time
        WHEN the function is called
        THEN it executes and returns the result
        """
        @log_execution_time
        def my_function():
            return "result"

        result = my_function()

        assert result == "result"

    def test_log_execution_time_measures_time(self, capsys):
        """
        GIVEN a function that takes time to execute
        WHEN decorated with log_execution_time
        THEN execution time is logged
        """
        @log_execution_time
        def slow_function():
            time.sleep(0.1)
            return "done"

        result = slow_function()
        captured = capsys.readouterr()

        assert result == "done"
        assert "slow_function executed in" in captured.out
        assert "s" in captured.out

    def test_log_execution_time_with_args(self):
        """
        GIVEN a function with args decorated with log_execution_time
        WHEN called with args
        THEN args are passed through correctly
        """
        @log_execution_time
        def my_function(a, b, c=None):
            return a + b + (c or 0)

        result = my_function(1, 2, c=3)

        assert result == 6

    def test_log_execution_time_with_exception(self, capsys):
        """
        GIVEN a function that raises an exception
        WHEN decorated with log_execution_time
        THEN time is still logged before exception propagates
        """
        @log_execution_time
        def failing_function():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            failing_function()

        captured = capsys.readouterr()
        assert "failing_function executed in" in captured.out

    def test_log_execution_time_preserves_metadata(self):
        """
        GIVEN a function with metadata
        WHEN decorated with log_execution_time
        THEN metadata is preserved
        """
        @log_execution_time
        def my_function():
            """My docstring"""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring"

    def test_log_execution_time_uses_flask_logger(self, app):
        """
        GIVEN a Flask application context
        WHEN log_execution_time decorator is used
        THEN it logs to current_app.logger
        """
        with app.app_context():
            with patch.object(app.logger, 'info') as mock_info:
                @log_execution_time
                def my_function():
                    return "result"

                result = my_function()

                assert result == "result"
                assert mock_info.called
                call_args = mock_info.call_args[0][0]
                assert "my_function executed in" in call_args


# ============================================================================
# Tests for deprecated
# ============================================================================

class TestDeprecated:
    """Test suite for deprecated decorator"""

    def test_deprecated_basic(self):
        """
        GIVEN a function decorated with @deprecated
        WHEN the function is called
        THEN it emits a DeprecationWarning
        """
        @deprecated(reason="Use new_function instead")
        def old_function():
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()

            assert result == "result"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_function" in str(w[0].message)
            assert "Use new_function instead" in str(w[0].message)

    def test_deprecated_with_version(self):
        """
        GIVEN a deprecated function with version info
        WHEN called
        THEN warning includes version number
        """
        @deprecated(reason="Use new_api", version="1.4.0")
        def old_api():
            return "data"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_api()

            assert result == "data"
            assert len(w) == 1
            assert "[v1.4.0]" in str(w[0].message)
            assert "Use new_api" in str(w[0].message)

    def test_deprecated_still_executes(self):
        """
        GIVEN a deprecated function
        WHEN called
        THEN it still executes normally despite warning
        """
        @deprecated(reason="Test")
        def my_function(x, y):
            return x + y

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = my_function(5, 10)

            assert result == 15

    def test_deprecated_preserves_metadata(self):
        """
        GIVEN a function with metadata
        WHEN decorated with @deprecated
        THEN metadata is preserved
        """
        @deprecated(reason="Test", version="1.0.0")
        def my_function():
            """My docstring"""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring"


# ============================================================================
# Tests for retry
# ============================================================================

class TestRetry:
    """Test suite for retry decorator"""

    def test_retry_success_first_attempt(self):
        """
        GIVEN a function that succeeds on first attempt
        WHEN decorated with @retry
        THEN it executes once and returns result
        """
        call_count = []

        @retry(max_attempts=3, delay=0.01)
        def successful_function():
            call_count.append(1)
            return "success"

        result = successful_function()

        assert result == "success"
        assert len(call_count) == 1

    def test_retry_success_after_failures(self, capsys):
        """
        GIVEN a function that fails twice then succeeds
        WHEN decorated with @retry(max_attempts=3)
        THEN it retries and eventually succeeds
        """
        call_count = []

        @retry(max_attempts=3, delay=0.01)
        def flaky_function():
            call_count.append(1)
            if len(call_count) < 3:
                raise ValueError("Temporary error")
            return "success"

        result = flaky_function()

        assert result == "success"
        assert len(call_count) == 3

        captured = capsys.readouterr()
        assert "Attempt 1/3 failed" in captured.out
        assert "Attempt 2/3 failed" in captured.out

    def test_retry_all_attempts_fail(self, capsys):
        """
        GIVEN a function that always fails
        WHEN decorated with @retry(max_attempts=3)
        THEN it retries 3 times and raises exception
        """
        call_count = []

        @retry(max_attempts=3, delay=0.01)
        def failing_function():
            call_count.append(1)
            raise ValueError("Permanent error")

        with pytest.raises(ValueError, match="Permanent error"):
            failing_function()

        assert len(call_count) == 3

        captured = capsys.readouterr()
        assert "Attempt 1/3 failed" in captured.out
        assert "Attempt 2/3 failed" in captured.out
        assert "All 3 attempts failed" in captured.out

    def test_retry_specific_exceptions(self):
        """
        GIVEN a function that can raise different exceptions
        WHEN decorated with @retry(exceptions=(ValueError,))
        THEN only specified exceptions trigger retry
        """
        call_count = []

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def mixed_exceptions():
            call_count.append(1)
            if len(call_count) == 1:
                raise ValueError("Retryable")
            elif len(call_count) == 2:
                raise TypeError("Not retryable")
            return "success"

        with pytest.raises(TypeError, match="Not retryable"):
            mixed_exceptions()

        # Should have retried once for ValueError, then hit TypeError
        assert len(call_count) == 2

    def test_retry_with_args(self):
        """
        GIVEN a function with arguments
        WHEN decorated with @retry
        THEN arguments are passed correctly on each retry
        """
        call_count = []

        @retry(max_attempts=2, delay=0.01)
        def function_with_args(x, y):
            call_count.append(1)
            if len(call_count) < 2:
                raise ValueError("Retry")
            return x + y

        result = function_with_args(5, 10)

        assert result == 15
        assert len(call_count) == 2

    def test_retry_preserves_metadata(self):
        """
        GIVEN a function with metadata
        WHEN decorated with @retry
        THEN metadata is preserved
        """
        @retry(max_attempts=3)
        def my_function():
            """My docstring"""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring"

    def test_retry_uses_flask_logger(self, app):
        """
        GIVEN a Flask application context
        WHEN retry decorator logs messages
        THEN it uses current_app.logger
        """
        with app.app_context():
            with patch.object(app.logger, 'warning') as mock_warning:
                call_count = []

                @retry(max_attempts=2, delay=0.01)
                def failing_function():
                    call_count.append(1)
                    if len(call_count) < 2:
                        raise ValueError("Test error")
                    return "success"

                result = failing_function()

                assert result == "success"
                assert mock_warning.called


# ============================================================================
# Tests for _service_class_to_param_name
# ============================================================================

class TestServiceClassToParamName:
    """Test suite for _service_class_to_param_name helper"""

    def test_service_class_to_param_name_simple(self):
        """
        GIVEN simple service class names
        WHEN converted to param names
        THEN correct snake_case is returned
        """
        assert _service_class_to_param_name("MetricaService") == "metrica_service"
        assert _service_class_to_param_name("AuthService") == "auth_service"
        assert _service_class_to_param_name("UserService") == "user_service"

    def test_service_class_to_param_name_multi_word(self):
        """
        GIVEN multi-word service class names
        WHEN converted to param names
        THEN correct snake_case is returned
        """
        assert _service_class_to_param_name("DashboardService") == "dashboard_service"
        assert _service_class_to_param_name("ApplicationMetricaService") == "application_metrica_service"

    def test_service_class_to_param_name_without_service_suffix(self):
        """
        GIVEN class names without 'Service' suffix
        WHEN converted to param names
        THEN _service is still appended
        """
        assert _service_class_to_param_name("Metrica") == "metrica_service"
        assert _service_class_to_param_name("Dashboard") == "dashboard_service"

    def test_service_class_to_param_name_single_letter(self):
        """
        GIVEN single-letter class names
        WHEN converted to param names
        THEN correct format is returned
        """
        assert _service_class_to_param_name("AService") == "a_service"
        assert _service_class_to_param_name("XService") == "x_service"


# ============================================================================
# Integration Tests
# ============================================================================

class TestDecoratorsCombined:
    """Test combining multiple decorators"""

    def test_multiple_decorators(self, capsys):
        """
        GIVEN a function with multiple decorators
        WHEN the function is called
        THEN all decorators work correctly together
        """
        @inject_service(DummyService)
        @log_execution_time
        def my_view(dummy_service=None):
            return dummy_service.get_data()

        result = my_view()

        assert result == {"test": "data"}

        captured = capsys.readouterr()
        assert "my_view executed in" in captured.out

    def test_retry_with_log_execution_time(self, capsys):
        """
        GIVEN a function with @retry and @log_execution_time
        WHEN the function is called
        THEN both decorators function correctly
        """
        call_count = []

        @retry(max_attempts=2, delay=0.01)
        @log_execution_time
        def flaky_function():
            call_count.append(1)
            if len(call_count) < 2:
                raise ValueError("Retry")
            return "success"

        result = flaky_function()

        assert result == "success"
        assert len(call_count) == 2

        captured = capsys.readouterr()
        # Should log execution time for each attempt
        assert "flaky_function executed in" in captured.out
