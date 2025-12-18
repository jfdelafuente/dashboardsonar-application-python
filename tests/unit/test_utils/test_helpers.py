"""
Unit tests for infocodest.utils.helpers module

Tests all helper functions:
    - format_percentage: Format numbers as percentages
    - calculate_variation: Calculate variation between values
    - safe_division: Division with zero handling
    - parse_date_string: Parse dates from strings
    - get_variation_trend: Determine trend from variation
    - truncate_string: Truncate strings with suffix
    - get_quality_gate_color: Get color for quality gate status
    - get_rating_color: Get color for rating (A-E)

Created: Phase 6 - Test Coverage Improvements
Updated: Priority 3 - Added pytest markers
"""

import pytest
from datetime import date
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

# Mark all tests in this module as unit and utils tests
pytestmark = [pytest.mark.unit, pytest.mark.utils]


# ============================================================================
# Tests for format_percentage
# ============================================================================

class TestFormatPercentage:
    """Test suite for format_percentage function"""

    def test_format_percentage_positive(self):
        """
        GIVEN a positive number
        WHEN formatted as percentage
        THEN it includes + sign
        """
        assert format_percentage(12.34) == "+12.34%"
        assert format_percentage(5.0) == "+5.00%"
        assert format_percentage(0.5) == "+0.50%"

    def test_format_percentage_negative(self):
        """
        GIVEN a negative number
        WHEN formatted as percentage
        THEN it includes - sign
        """
        assert format_percentage(-12.34) == "-12.34%"
        assert format_percentage(-5.0) == "-5.00%"
        assert format_percentage(-0.5) == "-0.50%"

    def test_format_percentage_zero(self):
        """
        GIVEN zero
        WHEN formatted as percentage
        THEN it has no sign
        """
        assert format_percentage(0) == "0.00%"
        assert format_percentage(0.0) == "0.00%"

    def test_format_percentage_custom_decimals(self):
        """
        GIVEN custom decimal places
        WHEN formatting percentage
        THEN correct decimal places are used
        """
        assert format_percentage(12.345, decimals=1) == "+12.3%"
        assert format_percentage(12.345, decimals=3) == "+12.345%"
        assert format_percentage(12.345, decimals=0) == "+12%"

    def test_format_percentage_no_sign(self):
        """
        GIVEN include_sign=False
        WHEN formatting positive number
        THEN no + sign is included
        """
        assert format_percentage(12.34, include_sign=False) == "12.34%"
        assert format_percentage(-12.34, include_sign=False) == "-12.34%"
        assert format_percentage(0, include_sign=False) == "0.00%"

    def test_format_percentage_large_numbers(self):
        """
        GIVEN large numbers
        WHEN formatted
        THEN correct formatting is applied
        """
        assert format_percentage(999.99) == "+999.99%"
        assert format_percentage(-999.99) == "-999.99%"


# ============================================================================
# Tests for calculate_variation
# ============================================================================

class TestCalculateVariation:
    """Test suite for calculate_variation function"""

    def test_calculate_variation_increase(self):
        """
        GIVEN current > old value
        WHEN calculating variation
        THEN positive percentage is returned
        """
        assert calculate_variation(120, 100) == 20.0
        assert calculate_variation(150, 100) == 50.0
        assert calculate_variation(200, 100) == 100.0

    def test_calculate_variation_decrease(self):
        """
        GIVEN current < old value
        WHEN calculating variation
        THEN negative percentage is returned
        """
        assert calculate_variation(80, 100) == -20.0
        assert calculate_variation(50, 100) == -50.0
        assert calculate_variation(25, 100) == -75.0

    def test_calculate_variation_no_change(self):
        """
        GIVEN current == old value
        WHEN calculating variation
        THEN 0.0 is returned
        """
        assert calculate_variation(100, 100) == 0.0
        assert calculate_variation(50, 50) == 0.0

    def test_calculate_variation_from_zero(self):
        """
        GIVEN old_value is 0
        WHEN calculating variation
        THEN 100% or 0% is returned
        """
        assert calculate_variation(50, 0) == 100.0
        assert calculate_variation(100, 0) == 100.0
        assert calculate_variation(0, 0) == 0.0

    def test_calculate_variation_as_decimal(self):
        """
        GIVEN as_percentage=False
        WHEN calculating variation
        THEN decimal is returned instead of percentage
        """
        assert abs(calculate_variation(120, 100, as_percentage=False) - 0.2) < 0.01
        assert abs(calculate_variation(80, 100, as_percentage=False) - (-0.2)) < 0.01
        assert calculate_variation(100, 100, as_percentage=False) == 0.0
        assert calculate_variation(50, 0, as_percentage=False) == 1.0

    def test_calculate_variation_float_precision(self):
        """
        GIVEN float values
        WHEN calculating variation
        THEN precise calculation is returned
        """
        result = calculate_variation(123.45, 100.0)
        assert abs(result - 23.45) < 0.01


# ============================================================================
# Tests for safe_division
# ============================================================================

class TestSafeDivision:
    """Test suite for safe_division function"""

    def test_safe_division_normal(self):
        """
        GIVEN normal division
        WHEN denominator is not zero
        THEN correct result is returned
        """
        assert safe_division(10, 2) == 5.0
        assert safe_division(100, 4) == 25.0
        assert safe_division(7, 2) == 3.5

    def test_safe_division_by_zero(self):
        """
        GIVEN denominator is zero
        WHEN dividing
        THEN default value is returned
        """
        assert safe_division(10, 0) == 0.0
        assert safe_division(100, 0) == 0.0

    def test_safe_division_custom_default(self):
        """
        GIVEN custom default value
        WHEN dividing by zero
        THEN custom default is returned
        """
        assert safe_division(10, 0, default=-1) == -1
        assert safe_division(10, 0, default=None) is None
        assert safe_division(10, 0, default=999) == 999

    def test_safe_division_negative_numbers(self):
        """
        GIVEN negative numbers
        WHEN dividing
        THEN correct signed result is returned
        """
        assert safe_division(-10, 2) == -5.0
        assert safe_division(10, -2) == -5.0
        assert safe_division(-10, -2) == 5.0

    def test_safe_division_float_inputs(self):
        """
        GIVEN float inputs
        WHEN dividing
        THEN correct float result is returned
        """
        assert safe_division(10.5, 2.0) == 5.25
        assert safe_division(7.5, 2.5) == 3.0


# ============================================================================
# Tests for parse_date_string
# ============================================================================

class TestParseDateString:
    """Test suite for parse_date_string function"""

    def test_parse_date_string_iso_format(self):
        """
        GIVEN ISO format date string (YYYY-MM-DD)
        WHEN parsing
        THEN correct date object is returned
        """
        result = parse_date_string("2025-12-12")
        assert result == date(2025, 12, 12)

        result = parse_date_string("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_parse_date_string_spanish_slash_format(self):
        """
        GIVEN Spanish format with slashes (DD/MM/YYYY)
        WHEN parsing
        THEN correct date object is returned
        """
        result = parse_date_string("12/12/2025")
        assert result == date(2025, 12, 12)

        result = parse_date_string("31/01/2024")
        assert result == date(2024, 1, 31)

    def test_parse_date_string_spanish_dash_format(self):
        """
        GIVEN Spanish format with dashes (DD-MM-YYYY)
        WHEN parsing
        THEN correct date object is returned
        """
        result = parse_date_string("12-12-2025")
        assert result == date(2025, 12, 12)

        result = parse_date_string("15-06-2024")
        assert result == date(2024, 6, 15)

    def test_parse_date_string_iso_slash_format(self):
        """
        GIVEN ISO format with slashes (YYYY/MM/DD)
        WHEN parsing
        THEN correct date object is returned
        """
        result = parse_date_string("2025/12/12")
        assert result == date(2025, 12, 12)

    def test_parse_date_string_compact_format(self):
        """
        GIVEN compact format (YYYYMMDD)
        WHEN parsing
        THEN correct date object is returned
        """
        result = parse_date_string("20251212")
        assert result == date(2025, 12, 12)

        result = parse_date_string("20240115")
        assert result == date(2024, 1, 15)

    def test_parse_date_string_invalid(self):
        """
        GIVEN invalid date string
        WHEN parsing
        THEN None is returned
        """
        assert parse_date_string("invalid") is None
        assert parse_date_string("not-a-date") is None
        assert parse_date_string("2025-13-45") is None  # Invalid month/day

    def test_parse_date_string_custom_formats(self):
        """
        GIVEN custom format list
        WHEN parsing
        THEN only those formats are tried
        """
        result = parse_date_string("12.12.2025", formats=['%d.%m.%Y'])
        assert result == date(2025, 12, 12)

        result = parse_date_string("2025-12-12", formats=['%d.%m.%Y'])
        assert result is None  # Format doesn't match


# ============================================================================
# Tests for get_variation_trend
# ============================================================================

class TestGetVariationTrend:
    """Test suite for get_variation_trend function"""

    def test_get_variation_trend_increase(self):
        """
        GIVEN variation > threshold
        WHEN getting trend
        THEN "Increase" is returned
        """
        assert get_variation_trend(5.0) == "Increase"
        assert get_variation_trend(10.0) == "Increase"
        assert get_variation_trend(0.2) == "Increase"

    def test_get_variation_trend_decrease(self):
        """
        GIVEN variation < -threshold
        WHEN getting trend
        THEN "Decrease" is returned
        """
        assert get_variation_trend(-5.0) == "Decrease"
        assert get_variation_trend(-10.0) == "Decrease"
        assert get_variation_trend(-0.2) == "Decrease"

    def test_get_variation_trend_stable(self):
        """
        GIVEN variation within threshold
        WHEN getting trend
        THEN "Stable" is returned
        """
        assert get_variation_trend(0.0) == "Stable"
        assert get_variation_trend(0.05) == "Stable"
        assert get_variation_trend(-0.05) == "Stable"

    def test_get_variation_trend_custom_threshold(self):
        """
        GIVEN custom threshold
        WHEN getting trend
        THEN threshold is applied correctly
        """
        assert get_variation_trend(0.5, threshold=1.0) == "Stable"
        assert get_variation_trend(1.5, threshold=1.0) == "Increase"
        assert get_variation_trend(-1.5, threshold=1.0) == "Decrease"

    def test_get_variation_trend_edge_cases(self):
        """
        GIVEN values at threshold boundaries
        WHEN getting trend
        THEN correct classification is returned
        """
        # Exactly at threshold
        assert get_variation_trend(0.1, threshold=0.1) == "Stable"
        assert get_variation_trend(-0.1, threshold=0.1) == "Stable"

        # Just above threshold
        assert get_variation_trend(0.11, threshold=0.1) == "Increase"
        assert get_variation_trend(-0.11, threshold=0.1) == "Decrease"


# ============================================================================
# Tests for truncate_string
# ============================================================================

class TestTruncateString:
    """Test suite for truncate_string function"""

    def test_truncate_string_shorter_than_max(self):
        """
        GIVEN string shorter than max_length
        WHEN truncating
        THEN original string is returned
        """
        assert truncate_string("Hello", 10) == "Hello"
        assert truncate_string("Test", 10) == "Test"

    def test_truncate_string_longer_than_max(self):
        """
        GIVEN string longer than max_length
        WHEN truncating
        THEN truncated string with suffix is returned
        """
        assert truncate_string("Hello World", 8) == "Hello..."
        assert truncate_string("This is a long text", 10) == "This is..."

    def test_truncate_string_custom_suffix(self):
        """
        GIVEN custom suffix
        WHEN truncating
        THEN custom suffix is used
        """
        assert truncate_string("Long text here", 10, suffix='»') == "Long text»"
        assert truncate_string("Long text here", 12, suffix='...') == "Long text..."

    def test_truncate_string_exact_length(self):
        """
        GIVEN string exactly at max_length
        WHEN truncating
        THEN original string is returned
        """
        assert truncate_string("12345678", 8) == "12345678"

    def test_truncate_string_invalid_max_length(self):
        """
        GIVEN max_length smaller than suffix length
        WHEN truncating
        THEN ValueError is raised
        """
        with pytest.raises(ValueError, match="max_length must be"):
            truncate_string("Hello", 2, suffix="...")

    def test_truncate_string_empty(self):
        """
        GIVEN empty string
        WHEN truncating
        THEN empty string is returned
        """
        assert truncate_string("", 10) == ""


# ============================================================================
# Tests for get_quality_gate_color
# ============================================================================

class TestGetQualityGateColor:
    """Test suite for get_quality_gate_color function"""

    def test_get_quality_gate_color_success(self):
        """
        GIVEN success status values
        WHEN getting color
        THEN green is returned
        """
        assert get_quality_gate_color("OK") == "green"
        assert get_quality_gate_color("PASSED") == "green"
        assert get_quality_gate_color("SUCCESS") == "green"

    def test_get_quality_gate_color_failure(self):
        """
        GIVEN failure status values
        WHEN getting color
        THEN red is returned
        """
        assert get_quality_gate_color("ERROR") == "red"
        assert get_quality_gate_color("FAILED") == "red"
        assert get_quality_gate_color("FAILURE") == "red"

    def test_get_quality_gate_color_warning(self):
        """
        GIVEN warning status values
        WHEN getting color
        THEN yellow is returned
        """
        assert get_quality_gate_color("WARN") == "yellow"
        assert get_quality_gate_color("WARNING") == "yellow"
        assert get_quality_gate_color("PENDING") == "yellow"

    def test_get_quality_gate_color_case_insensitive(self):
        """
        GIVEN mixed case status values
        WHEN getting color
        THEN correct color is returned (case-insensitive)
        """
        assert get_quality_gate_color("ok") == "green"
        assert get_quality_gate_color("Ok") == "green"
        assert get_quality_gate_color("error") == "red"
        assert get_quality_gate_color("Error") == "red"

    def test_get_quality_gate_color_unknown(self):
        """
        GIVEN unknown status
        WHEN getting color
        THEN gray is returned
        """
        assert get_quality_gate_color("UNKNOWN") == "gray"
        assert get_quality_gate_color("INVALID") == "gray"
        assert get_quality_gate_color("") == "gray"

    def test_get_quality_gate_color_none(self):
        """
        GIVEN None value
        WHEN getting color
        THEN gray is returned
        """
        assert get_quality_gate_color(None) == "gray"


# ============================================================================
# Tests for get_rating_color
# ============================================================================

class TestGetRatingColor:
    """Test suite for get_rating_color function"""

    def test_get_rating_color_a(self):
        """
        GIVEN rating A
        WHEN getting color
        THEN green is returned
        """
        assert get_rating_color("A") == "green"

    def test_get_rating_color_b(self):
        """
        GIVEN rating B
        WHEN getting color
        THEN lightgreen is returned
        """
        assert get_rating_color("B") == "lightgreen"

    def test_get_rating_color_c(self):
        """
        GIVEN rating C
        WHEN getting color
        THEN yellow is returned
        """
        assert get_rating_color("C") == "yellow"

    def test_get_rating_color_d(self):
        """
        GIVEN rating D
        WHEN getting color
        THEN orange is returned
        """
        assert get_rating_color("D") == "orange"

    def test_get_rating_color_e(self):
        """
        GIVEN rating E
        WHEN getting color
        THEN red is returned
        """
        assert get_rating_color("E") == "red"

    def test_get_rating_color_case_insensitive(self):
        """
        GIVEN lowercase ratings
        WHEN getting color
        THEN correct color is returned (case-insensitive)
        """
        assert get_rating_color("a") == "green"
        assert get_rating_color("b") == "lightgreen"
        assert get_rating_color("c") == "yellow"
        assert get_rating_color("d") == "orange"
        assert get_rating_color("e") == "red"

    def test_get_rating_color_unknown(self):
        """
        GIVEN unknown rating
        WHEN getting color
        THEN gray is returned
        """
        assert get_rating_color("F") == "gray"
        assert get_rating_color("X") == "gray"
        assert get_rating_color("") == "gray"

    def test_get_rating_color_none(self):
        """
        GIVEN None value
        WHEN getting color
        THEN gray is returned
        """
        assert get_rating_color(None) == "gray"


# ============================================================================
# Integration Tests
# ============================================================================

class TestHelpersIntegration:
    """Integration tests combining multiple helpers"""

    def test_variation_formatting_workflow(self):
        """
        GIVEN current and old metrics
        WHEN calculating and formatting variation
        THEN complete workflow produces correct output
        """
        current = 120
        old = 100

        variation = calculate_variation(current, old)
        formatted = format_percentage(variation)
        trend = get_variation_trend(variation)

        assert variation == 20.0
        assert formatted == "+20.00%"
        assert trend == "Increase"

    def test_safe_division_with_formatting(self):
        """
        GIVEN division that might be by zero
        WHEN using safe_division and formatting
        THEN workflow handles edge cases
        """
        coverage = safe_division(75, 100) * 100
        formatted = format_percentage(coverage, include_sign=False)

        assert formatted == "75.00%"

        # Edge case: division by zero
        coverage_zero = safe_division(75, 0, default=0.0) * 100
        formatted_zero = format_percentage(coverage_zero, include_sign=False)

        assert formatted_zero == "0.00%"

    def test_date_parsing_and_comparison(self):
        """
        GIVEN multiple date formats
        WHEN parsing dates
        THEN all formats produce comparable date objects
        """
        date1 = parse_date_string("2025-12-12")
        date2 = parse_date_string("12/12/2025")
        date3 = parse_date_string("20251212")

        assert date1 == date2 == date3
        assert date1 == date(2025, 12, 12)
