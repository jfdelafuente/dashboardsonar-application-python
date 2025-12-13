"""
Error Handlers Module
====================

Custom error handlers for the application.

Handles:
    - Custom application exceptions
    - HTTP errors (401, 404, 500)
    - Business logic exceptions
    - Validation errors

Usage:
    Registered automatically in create_app() factory

Updated: Phase 5 - Exception Handling System
"""

from flask import render_template, jsonify, request

from infocodest.exceptions.base import (
    ApplicationException,
    BusinessException,
    ValidationException,
    NotFoundException,
    DatabaseException
)


def wants_json_response() -> bool:
    """
    Determine if client wants JSON response.

    Returns:
        True if Accept header prefers JSON

    Example:
        >>> wants_json_response()
        False
    """
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return (
        best == 'application/json' and
        request.accept_mimetypes[best] > request.accept_mimetypes['text/html']
    )


########################
#### HTTP Error Handlers ####
########################


def error_401(e):
    """
    Handler for 401 Unauthorized errors.

    Args:
        e: HTTP exception

    Returns:
        Rendered template or JSON response
    """
    if wants_json_response():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status_code': 401
        }), 401
    # mc is for the menu highlighting, which in this case should not be set
    return render_template("errors/401.html", mc=""), 401


def error_404(e):
    """
    Handler for 404 Not Found errors.

    Args:
        e: HTTP exception

    Returns:
        Rendered template or JSON response
    """
    if wants_json_response():
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    # mc is for the menu highlighting, which in this case should not be set
    return render_template("errors/404.html", mc=""), 404


def error_500(e):
    """
    Handler for 500 Internal Server Error.

    Args:
        e: HTTP exception

    Returns:
        Rendered template or JSON response
    """
    if wants_json_response():
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    # mc is for the menu highlighting, which in this case should not be set
    return render_template("errors/500.html", mc=""), 500


########################
#### Custom Exception Handlers ####
########################


def handle_not_found_exception(error: NotFoundException):
    """
    Handler for NotFoundException.

    Args:
        error: NotFoundException instance

    Returns:
        JSON response or rendered template with 404 status

    Example:
        Application not found: my-app
    """
    from flask import current_app
    current_app.logger.warning(
        f'Resource not found: {error.message}',
        extra={'payload': error.payload}
    )

    if wants_json_response():
        return jsonify(error.to_dict()), error.status_code

    return render_template(
        'errors/404.html',
        error_message=error.message,
        mc=""
    ), 404


def handle_validation_exception(error: ValidationException):
    """
    Handler for ValidationException.

    Args:
        error: ValidationException instance

    Returns:
        JSON response or rendered template with 422 status

    Example:
        Invalid date range: start_date must be <= end_date
    """
    from flask import current_app
    current_app.logger.warning(
        f'Validation error: {error.message}',
        extra={'payload': error.payload}
    )

    if wants_json_response():
        return jsonify(error.to_dict()), error.status_code

    return render_template(
        'errors/422.html',
        error_message=error.message,
        field=error.payload.get('field'),
        mc=""
    ), 422


def handle_business_exception(error: BusinessException):
    """
    Handler for BusinessException.

    Args:
        error: BusinessException instance

    Returns:
        JSON response or rendered template

    Example:
        Business rule violation detected
    """
    from flask import current_app
    current_app.logger.warning(
        f'Business exception: {error.message}',
        extra={'payload': error.payload}
    )

    if wants_json_response():
        return jsonify(error.to_dict()), error.status_code

    # For non-validation business errors, use 422 template
    return render_template(
        'errors/422.html',
        error_message=error.message,
        mc=""
    ), error.status_code


def handle_database_exception(error: DatabaseException):
    """
    Handler for DatabaseException.

    Args:
        error: DatabaseException instance

    Returns:
        JSON response or rendered template with 500 status

    Example:
        Database connection failed
    """
    from flask import current_app
    current_app.logger.error(
        f'Database error: {error.message}',
        extra={'payload': error.payload},
        exc_info=True
    )

    if wants_json_response():
        # Don't expose internal error details in production
        return jsonify({
            'error': 'DatabaseException',
            'message': 'A database error occurred',
            'status_code': 500
        }), 500

    return render_template('errors/500.html', mc=""), 500


def handle_application_exception(error: ApplicationException):
    """
    Handler for generic ApplicationException.

    Args:
        error: ApplicationException instance

    Returns:
        JSON response or rendered template

    Example:
        Unexpected application error
    """
    from flask import current_app
    current_app.logger.error(
        f'Application exception: {error.message}',
        extra={'payload': error.payload},
        exc_info=True
    )

    if wants_json_response():
        return jsonify(error.to_dict()), error.status_code

    if error.status_code >= 500:
        return render_template('errors/500.html', mc=""), error.status_code
    elif error.status_code == 404:
        return render_template('errors/404.html', mc=""), 404
    else:
        return render_template('errors/422.html', error_message=error.message, mc=""), error.status_code


def register_error_handlers(app):
    """
    Register all error handlers with the Flask app.

    Args:
        app: Flask application instance

    Handlers registered:
        - Custom exception handlers (most specific first)
        - HTTP error handlers
        - Generic exception handler

    Notes:
        - Order matters: most specific exceptions first
        - Custom exceptions are logged appropriately
        - Supports both HTML and JSON responses
    """
    # Custom exceptions (most specific first)
    app.register_error_handler(NotFoundException, handle_not_found_exception)
    app.register_error_handler(ValidationException, handle_validation_exception)
    app.register_error_handler(DatabaseException, handle_database_exception)
    app.register_error_handler(BusinessException, handle_business_exception)
    app.register_error_handler(ApplicationException, handle_application_exception)

    # HTTP errors
    app.register_error_handler(401, error_401)
    app.register_error_handler(404, error_404)
    app.register_error_handler(500, error_500)

