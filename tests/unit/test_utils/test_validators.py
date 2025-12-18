"""
Unit tests for input validators.

Tests validation functions for dates, emails, names, metrics, etc.

Updated: Priority 3 - Added pytest markers
"""

import pytest
from datetime import date
from infocodest.utils.validators import (
    validate_date_range,
    validate_application_name,
    validate_metric_value,
    validate_email,
    validate_repository_name,
    validate_percentage,
    validate_rating
)

# Mark all tests in this module as unit and utils tests
pytestmark = [pytest.mark.unit, pytest.mark.utils]


class TestValidateDateRange:
    """Test suite for date range validation."""

    def test_valid_date_range(self):
        """Test valid date range (start before end)."""
        start = date(2025, 1, 1)
        end = date(2025, 12, 31)
        assert validate_date_range(start, end) is True

    def test_same_dates(self):
        """Test same start and end dates."""
        same_date = date(2025, 6, 15)
        assert validate_date_range(same_date, same_date) is True

    def test_invalid_range_reversed(self):
        """Test invalid range where start is after end."""
        start = date(2025, 12, 31)
        end = date(2025, 1, 1)
        assert validate_date_range(start, end) is False

    def test_none_start_date(self):
        """Test None start date is valid."""
        end = date(2025, 12, 31)
        assert validate_date_range(None, end) is True

    def test_none_end_date(self):
        """Test None end date is valid."""
        start = date(2025, 1, 1)
        assert validate_date_range(start, None) is True

    def test_both_dates_none(self):
        """Test both dates None is valid."""
        assert validate_date_range(None, None) is True


class TestValidateApplicationName:
    """Test suite for application name validation."""

    def test_valid_name_with_hyphens(self):
        """Test valid application name with hyphens."""
        assert validate_application_name("my-app") is True
        assert validate_application_name("my-cool-app") is True

    def test_valid_name_with_underscores(self):
        """Test valid application name with underscores."""
        assert validate_application_name("my_app") is True
        assert validate_application_name("my_app_123") is True

    def test_valid_alphanumeric(self):
        """Test valid alphanumeric application name."""
        assert validate_application_name("myapp123") is True
        assert validate_application_name("App1") is True

    def test_valid_mixed_format(self):
        """Test valid name with mixed hyphens and underscores."""
        assert validate_application_name("my-app_v1") is True

    def test_empty_string(self):
        """Test empty string is invalid."""
        assert validate_application_name("") is False

    def test_too_long(self):
        """Test name longer than 255 characters is invalid."""
        long_name = "a" * 256
        assert validate_application_name(long_name) is False

    def test_max_length_allowed(self):
        """Test name exactly 255 characters is valid."""
        max_name = "a" * 255
        assert validate_application_name(max_name) is True

    def test_special_characters_invalid(self):
        """Test names with special characters are invalid."""
        assert validate_application_name("my app") is False  # space
        assert validate_application_name("my@app") is False  # @
        assert validate_application_name("my.app") is False  # dot
        assert validate_application_name("my#app") is False  # hash

    def test_unicode_invalid(self):
        """Test names with unicode characters are invalid."""
        assert validate_application_name("app-ñ") is False
        assert validate_application_name("app_ü") is False


class TestValidateMetricValue:
    """Test suite for metric value validation."""

    def test_valid_value_in_range(self):
        """Test valid value within min and max bounds."""
        assert validate_metric_value(50, min_value=0, max_value=100) is True
        assert validate_metric_value(0, min_value=0, max_value=100) is True
        assert validate_metric_value(100, min_value=0, max_value=100) is True

    def test_valid_float_value(self):
        """Test valid float value."""
        assert validate_metric_value(75.5, min_value=0, max_value=100) is True

    def test_value_below_minimum(self):
        """Test value below minimum is invalid."""
        assert validate_metric_value(-10, min_value=0) is False
        assert validate_metric_value(-0.1, min_value=0, max_value=100) is False

    def test_value_above_maximum(self):
        """Test value above maximum is invalid."""
        assert validate_metric_value(150, max_value=100) is False
        assert validate_metric_value(100.1, min_value=0, max_value=100) is False

    def test_no_min_bound(self):
        """Test validation with no minimum bound."""
        assert validate_metric_value(-1000, max_value=100) is True
        assert validate_metric_value(50, max_value=100) is True

    def test_no_max_bound(self):
        """Test validation with no maximum bound."""
        assert validate_metric_value(1000, min_value=0) is True
        assert validate_metric_value(50, min_value=0) is True

    def test_no_bounds(self):
        """Test validation with no bounds (any numeric value valid)."""
        assert validate_metric_value(-1000) is True
        assert validate_metric_value(0) is True
        assert validate_metric_value(1000) is True
        assert validate_metric_value(99.99) is True

    def test_non_numeric_value(self):
        """Test non-numeric values are invalid."""
        assert validate_metric_value("100") is False
        assert validate_metric_value("invalid") is False
        assert validate_metric_value(None) is False
        assert validate_metric_value([100]) is False
        assert validate_metric_value({"value": 100}) is False


class TestValidateEmail:
    """Test suite for email validation."""

    def test_valid_simple_email(self):
        """Test valid simple email address."""
        assert validate_email("user@example.com") is True

    def test_valid_email_with_subdomain(self):
        """Test valid email with subdomain."""
        assert validate_email("user@mail.example.com") is True

    def test_valid_email_with_plus(self):
        """Test valid email with plus sign."""
        assert validate_email("user+tag@example.com") is True

    def test_valid_email_with_dots(self):
        """Test valid email with dots in local part."""
        assert validate_email("first.last@example.com") is True

    def test_valid_email_with_numbers(self):
        """Test valid email with numbers."""
        assert validate_email("user123@example456.com") is True

    def test_invalid_no_at_sign(self):
        """Test email without @ is invalid."""
        assert validate_email("userexample.com") is False

    def test_invalid_multiple_at_signs(self):
        """Test email with multiple @ is invalid."""
        assert validate_email("user@@example.com") is False

    def test_invalid_no_local_part(self):
        """Test email without local part is invalid."""
        assert validate_email("@example.com") is False

    def test_invalid_no_domain(self):
        """Test email without domain is invalid."""
        assert validate_email("user@") is False

    def test_invalid_no_tld(self):
        """Test email without TLD is invalid."""
        assert validate_email("user@example") is False

    def test_invalid_empty_string(self):
        """Test empty string is invalid."""
        assert validate_email("") is False

    def test_invalid_none(self):
        """Test None is invalid."""
        assert validate_email(None) is False

    def test_invalid_not_string(self):
        """Test non-string is invalid."""
        assert validate_email(123) is False


class TestValidateRepositoryName:
    """Test suite for repository name validation."""

    def test_valid_simple_name(self):
        """Test valid simple repository name."""
        assert validate_repository_name("my-repo") is True

    def test_valid_with_slash(self):
        """Test valid name with slash (org/repo format)."""
        assert validate_repository_name("org/repo") is True
        assert validate_repository_name("owner/project-name") is True

    def test_valid_with_dots(self):
        """Test valid name with dots."""
        assert validate_repository_name("my.repo") is True
        assert validate_repository_name("my.cool.repo") is True

    def test_valid_with_underscores(self):
        """Test valid name with underscores."""
        assert validate_repository_name("my_repo") is True

    def test_valid_mixed_characters(self):
        """Test valid name with mixed allowed characters."""
        assert validate_repository_name("org/my-repo_v1.0") is True

    def test_empty_string(self):
        """Test empty string is invalid."""
        assert validate_repository_name("") is False

    def test_too_long(self):
        """Test name longer than 255 characters is invalid."""
        long_name = "a" * 256
        assert validate_repository_name(long_name) is False

    def test_max_length_allowed(self):
        """Test name exactly 255 characters is valid."""
        max_name = "a" * 255
        assert validate_repository_name(max_name) is True

    def test_special_characters_invalid(self):
        """Test names with invalid special characters."""
        assert validate_repository_name("my repo") is False  # space
        assert validate_repository_name("my@repo") is False  # @
        assert validate_repository_name("my#repo") is False  # hash


class TestValidatePercentage:
    """Test suite for percentage validation."""

    def test_valid_zero(self):
        """Test 0% is valid."""
        assert validate_percentage(0) is True
        assert validate_percentage(0.0) is True

    def test_valid_hundred(self):
        """Test 100% is valid."""
        assert validate_percentage(100) is True
        assert validate_percentage(100.0) is True

    def test_valid_middle_value(self):
        """Test middle percentage values."""
        assert validate_percentage(50) is True
        assert validate_percentage(75.5) is True
        assert validate_percentage(33.33) is True

    def test_invalid_negative(self):
        """Test negative percentage is invalid."""
        assert validate_percentage(-1) is False
        assert validate_percentage(-0.1) is False

    def test_invalid_over_hundred(self):
        """Test percentage over 100 is invalid."""
        assert validate_percentage(101) is False
        assert validate_percentage(100.1) is False
        assert validate_percentage(200) is False

    def test_invalid_non_numeric(self):
        """Test non-numeric values are invalid."""
        assert validate_percentage("50") is False
        assert validate_percentage("50%") is False
        assert validate_percentage(None) is False


class TestValidateRating:
    """Test suite for rating validation."""

    def test_valid_letter_ratings(self):
        """Test valid letter ratings A-E."""
        assert validate_rating("A") is True
        assert validate_rating("B") is True
        assert validate_rating("C") is True
        assert validate_rating("D") is True
        assert validate_rating("E") is True

    def test_valid_lowercase_letters(self):
        """Test lowercase letters are valid (converted to uppercase)."""
        assert validate_rating("a") is True
        assert validate_rating("b") is True
        assert validate_rating("e") is True

    def test_valid_numeric_ratings(self):
        """Test valid numeric ratings 1-5."""
        assert validate_rating(1) is True
        assert validate_rating(2) is True
        assert validate_rating(3) is True
        assert validate_rating(4) is True
        assert validate_rating(5) is True

    def test_invalid_letter_f(self):
        """Test letter F is invalid."""
        assert validate_rating("F") is False
        assert validate_rating("f") is False

    def test_invalid_number_zero(self):
        """Test number 0 is invalid."""
        assert validate_rating(0) is False

    def test_invalid_number_six(self):
        """Test number 6 is invalid."""
        assert validate_rating(6) is False

    def test_invalid_negative_number(self):
        """Test negative number is invalid."""
        assert validate_rating(-1) is False

    def test_invalid_string_number(self):
        """Test string representation of number is invalid."""
        assert validate_rating("1") is False
        assert validate_rating("5") is False

    def test_invalid_float(self):
        """Test float is invalid."""
        assert validate_rating(1.5) is False

    def test_invalid_none(self):
        """Test None is invalid."""
        assert validate_rating(None) is False

    def test_invalid_list(self):
        """Test list is invalid."""
        assert validate_rating(["A"]) is False
