"""
Custom Decorators Module
=========================

Provides utility decorators for Flask views and services.

Features:
    - Service injection for dependency injection pattern
    - Execution time logging for performance monitoring
    - Function deprecation warnings
    - Retry mechanism for transient failures

Usage:
    from infocodest.utils.decorators import inject_service, log_execution_time

    @app.route("/metrics")
    @inject_service(MetricaService)
    @log_execution_time
    def metrics_view(metrica_service: MetricaService):
        return metrica_service.get_all()

Created: Phase 4 - Utilities System
"""

import functools
import time
import warnings
from typing import Type, Callable, Any, TypeVar, Optional

try:
    from flask import current_app
except ImportError:
    current_app = None


T = TypeVar('T')


def inject_service(service_class: Type[T]) -> Callable:
    """
    Decorator to inject service instances into Flask view functions.

    Enables dependency injection pattern by automatically instantiating
    service classes and passing them as keyword arguments to views.

    Args:
        service_class: Service class to instantiate and inject

    Returns:
        Decorator function

    Example:
        >>> from infocodest.services import MetricaService
        >>> from infocodest.utils.decorators import inject_service
        >>>
        >>> @app.route("/metrics")
        >>> @inject_service(MetricaService)
        >>> def metrics_view(metrica_service: MetricaService):
        ...     data = metrica_service.get_all()
        ...     return render_template("metrics.html", data=data)

    Notes:
        - Service instance is created fresh for each request
        - Service is passed as keyword argument with pattern: service_class_name
        - Example: MetricaService → metrica_service parameter
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Instantiate service
            service = service_class()

            # Generate parameter name from class name
            # MetricaService → metrica_service
            param_name = _service_class_to_param_name(service_class.__name__)

            # Inject service as keyword argument
            kwargs[param_name] = service

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def log_execution_time(f: Callable) -> Callable:
    """
    Decorator to log function execution time.

    Logs the execution duration of the decorated function to the
    Flask application logger (if available) or to stdout.

    Args:
        f: Function to decorate

    Returns:
        Decorated function that logs execution time

    Example:
        >>> @log_execution_time
        >>> def expensive_query():
        ...     return db.session.query(Metrica).all()
        >>> # Logs: "expensive_query executed in 0.45s"

    Notes:
        - Uses current_app.logger if running in Flask context
        - Falls back to print() if Flask context unavailable
        - Time precision: 2 decimal places
    """
    @functools.wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()

        try:
            result = f(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            duration = end_time - start_time

            log_message = f'{f.__name__} executed in {duration:.2f}s'

            if current_app:
                current_app.logger.info(log_message)
            else:
                print(log_message)

    return decorated_function


def deprecated(reason: str, version: Optional[str] = None) -> Callable:
    """
    Decorator to mark functions as deprecated.

    Emits a DeprecationWarning when the decorated function is called,
    with a message indicating the reason and migration path.

    Args:
        reason: Explanation of why deprecated and migration instructions
        version: Version when deprecation was introduced (optional)

    Returns:
        Decorator function

    Example:
        >>> @deprecated(
        ...     reason="Use DashboardService.get_kpi_overview() instead",
        ...     version="1.4.0"
        ... )
        >>> def getDatosMetricas():
        ...     return {"apps": 10}
        >>>
        >>> getDatosMetricas()  # Emits DeprecationWarning

    Notes:
        - Warning category: DeprecationWarning
        - Warning appears once per call location (default Python behavior)
        - To see all warnings: python -W default::DeprecationWarning
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Build warning message
            msg = f"Call to deprecated function {f.__name__}. {reason}"
            if version:
                msg = f"[v{version}] {msg}"

            # Emit warning
            warnings.warn(
                msg,
                category=DeprecationWarning,
                stacklevel=2
            )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def retry(max_attempts: int = 3, delay: float = 1.0,
          exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator to retry function on exception.

    Retries the decorated function up to max_attempts times if it
    raises one of the specified exceptions.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Delay in seconds between retries (default: 1.0)
        exceptions: Tuple of exception types to catch (default: Exception)

    Returns:
        Decorator function

    Example:
        >>> from sqlalchemy.exc import OperationalError
        >>>
        >>> @retry(max_attempts=3, delay=0.5, exceptions=(OperationalError,))
        >>> def save_to_db(data):
        ...     db.session.add(data)
        ...     db.session.commit()

    Notes:
        - Logs retry attempts to current_app.logger if available
        - Re-raises exception if all attempts fail
        - Useful for transient database errors, network timeouts
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts:
                        msg = (f"Attempt {attempt}/{max_attempts} failed for {f.__name__}: {e}. "
                               f"Retrying in {delay}s...")

                        if current_app:
                            current_app.logger.warning(msg)
                        else:
                            print(f"WARNING: {msg}")

                        time.sleep(delay)
                    else:
                        msg = f"All {max_attempts} attempts failed for {f.__name__}"

                        if current_app:
                            current_app.logger.error(msg)
                        else:
                            print(f"ERROR: {msg}")

            # Re-raise the last exception after all attempts
            raise last_exception

        return decorated_function

    return decorator


def _service_class_to_param_name(class_name: str) -> str:
    """
    Convert service class name to parameter name.

    Args:
        class_name: Name of the service class (e.g., "MetricaService")

    Returns:
        Parameter name in snake_case (e.g., "metrica_service")

    Example:
        >>> _service_class_to_param_name("DashboardService")
        'dashboard_service'
        >>> _service_class_to_param_name("MetricaService")
        'metrica_service'
        >>> _service_class_to_param_name("AuthService")
        'auth_service'
    """
    # Remove "Service" suffix if present
    if class_name.endswith('Service'):
        base_name = class_name[:-7]  # Remove last 7 chars ("Service")
    else:
        base_name = class_name

    # Convert PascalCase to snake_case
    result = []
    for i, char in enumerate(base_name):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())

    return ''.join(result) + '_service'
