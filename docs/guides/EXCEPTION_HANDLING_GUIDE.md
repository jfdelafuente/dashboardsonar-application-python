# Exception Handling Guide

**Created**: Phase 5 - Exception Handling System
**Last Updated**: 2025-12-12

---

## Overview

This guide explains how to use the custom exception system in the Dashboard Sonar application.

## Exception Hierarchy

```
Exception (Python built-in)
└── ApplicationException (base)
    ├── BusinessException
    │   ├── ValidationException
    │   ├── AuthenticationException
    │   ├── AuthorizationException
    │   ├── ExportException
    │   └── ConfigurationException
    ├── NotFoundException
    │   ├── ApplicationNotFoundException
    │   ├── MetricNotFoundException
    │   └── ProviderNotFoundException
    └── DatabaseException
```

## Quick Reference

### Import Exceptions

```python
from infocodest.exceptions import (
    ApplicationNotFoundException,
    InvalidDateRangeException,
    ValidationException,
    DatabaseException
)
```

### Usage Examples

#### 1. Resource Not Found

```python
from infocodest.exceptions import ApplicationNotFoundException

def get_application(app_name: str):
    app = Application.query.filter_by(name=app_name).first()
    if not app:
        raise ApplicationNotFoundException(app_name)
    return app
```

#### 2. Input Validation

```python
from infocodest.exceptions import InvalidDateRangeException
from datetime import date

def validate_date_range(start: date, end: date):
    if start > end:
        raise InvalidDateRangeException(
            start_date=start,
            end_date=end,
            reason="Start date must be before or equal to end date"
        )
```

#### 3. Metric Validation

```python
from infocodest.exceptions import InvalidMetricValueException

def validate_coverage(coverage: float):
    if coverage < 0 or coverage > 100:
        raise InvalidMetricValueException(
            metric_name="coverage",
            value=coverage,
            reason="Must be between 0 and 100"
        )
```

#### 4. Database Errors

```python
from infocodest.exceptions import DatabaseException
from sqlalchemy.exc import SQLAlchemyError

try:
    db.session.commit()
except SQLAlchemyError as e:
    raise DatabaseException(
        "Failed to save metric",
        operation="insert"
    )
```

#### 5. Authentication/Authorization

```python
from infocodest.exceptions import AuthenticationException

if not valid_credentials(username, password):
    raise AuthenticationException("Invalid credentials")
```

## Exception Types

### Base Exceptions

| Exception | Status Code | Use Case |
|-----------|-------------|----------|
| `ApplicationException` | 500 | Generic app errors |
| `BusinessException` | 422 | Business rule violations |
| `ValidationException` | 422 | Input validation failures |
| `NotFoundException` | 404 | Resource not found |
| `DatabaseException` | 500 | Database operation failures |

### Domain-Specific Exceptions

| Exception | Inherits From | Purpose |
|-----------|---------------|---------|
| `ApplicationNotFoundException` | NotFoundException | Application not found |
| `MetricNotFoundException` | NotFoundException | Metric not found |
| `ProviderNotFoundException` | NotFoundException | Provider not found |
| `InvalidApplicationNameException` | ValidationException | Invalid app name |
| `InvalidMetricValueException` | ValidationException | Invalid metric value |
| `InvalidDateRangeException` | ValidationException | Invalid date range |
| `InvalidDateFormatException` | ValidationException | Invalid date format |
| `AuthenticationException` | BusinessException | Auth failures (401) |
| `AuthorizationException` | BusinessException | Permission errors (403) |
| `ExportException` | BusinessException | Export failures |
| `ConfigurationException` | BusinessException | Config errors |

## Best Practices

### ✅ DO: Use Specific Exceptions

```python
# Good
if not app:
    raise ApplicationNotFoundException(app_name)
```

```python
# Bad
if not app:
    raise Exception("App not found")
```

### ✅ DO: Include Context

```python
# Good
raise ValidationException(
    "Invalid email format",
    field="email",
    payload={'value': email, 'pattern': EMAIL_REGEX}
)
```

```python
# Bad
raise ValidationException("Invalid data")
```

### ✅ DO: Let Error Handlers Handle HTTP

```python
# Good - in service layer
def my_service_method():
    if error:
        raise ValidationException("Invalid input")  # Handler deals with HTTP
```

```python
# Bad - in service layer
from flask import jsonify

def my_service_method():
    if error:
        return jsonify({'error': 'Bad'}), 400  # Don't do this in services
```

### ❌ DON'T: Catch Exceptions You Can't Handle

```python
# Bad
try:
    result = service.process()
except ApplicationNotFoundException:
    pass  # Silently ignoring
```

```python
# Good
try:
    result = service.process()
except ApplicationNotFoundException as e:
    logger.warning(f"Application not found: {e.app_name}")
    return default_value
```

### ✅ DO: Log Before Raising (When Appropriate)

```python
from flask import current_app

def critical_operation():
    try:
        perform_operation()
    except DatabaseError as e:
        current_app.logger.error(f"Critical DB failure: {e}", exc_info=True)
        raise DatabaseException("Failed to perform critical operation")
```

## Error Handler Behavior

### Content Negotiation

The error handlers automatically detect the client's preferred response format:

- **HTML Requests**: Renders error template (`errors/404.html`, `errors/422.html`, `errors/500.html`)
- **JSON Requests** (`Accept: application/json`): Returns JSON response

### JSON Response Format

```json
{
  "error": "ApplicationNotFoundException",
  "message": "Application not found: my-app",
  "resource": "Application",
  "identifier": "my-app"
}
```

### HTML Response

Renders appropriate template with:
- Error message
- Field information (for validation errors)
- Navigation buttons

## Testing Exceptions

```python
import pytest
from infocodest.exceptions import ApplicationNotFoundException

def test_application_not_found():
    with pytest.raises(ApplicationNotFoundException) as exc_info:
        service.get_application("non-existent")

    assert exc_info.value.app_name == "non-existent"
    assert exc_info.value.status_code == 404
```

## Integration with Services (Future - Phase 2)

When implementing services in Phase 2, use exceptions like this:

```python
# infocodest/services/metrica_service.py
from infocodest.exceptions import (
    ApplicationNotFoundException,
    InvalidDateRangeException
)

class MetricaService:
    def get_metrics_by_app(self, app_name: str):
        # Validate
        if not self.metrica_repo.app_exists(app_name):
            raise ApplicationNotFoundException(app_name)

        # Business logic
        return self.metrica_repo.get_by_aplicacion(app_name)

    def get_metrics_in_range(self, start_date, end_date):
        # Validate
        if start_date > end_date:
            raise InvalidDateRangeException(start_date, end_date)

        # Query
        return self.metrica_repo.get_in_date_range(start_date, end_date)
```

## Migration from Current Code

### Before (generic exceptions)

```python
# Old code
if not app:
    abort(404)
```

### After (custom exceptions)

```python
# New code
from infocodest.exceptions import ApplicationNotFoundException

if not app:
    raise ApplicationNotFoundException(app_name)
```

## Error Logging

All custom exceptions are automatically logged by the error handlers:

- **NotFoundException**: Logged at WARNING level
- **ValidationException**: Logged at WARNING level
- **BusinessException**: Logged at WARNING level
- **DatabaseException**: Logged at ERROR level with full traceback
- **ApplicationException**: Logged at ERROR level with full traceback

Logs include:
- Exception message
- Payload context
- Stack trace (for ERROR level)

## Summary

✅ **Use specific exception classes** for better error handling
✅ **Include context in payload** for debugging
✅ **Let error handlers manage HTTP responses** - don't return responses from services
✅ **Log appropriately before raising** critical errors
✅ **Don't catch exceptions you can't handle** - let them propagate
✅ **Test exception scenarios** in unit tests

---

**Next Steps**: When implementing Phase 2 (Services), integrate these exceptions throughout the service layer.

---

**References**:
- Phase 5 Plan: `docs/plan/FASE_5_PLAN_DETALLADO.md`
- Exception Classes: `infocodest/exceptions/`
- Error Handlers: `infocodest/errorhandlers.py`
