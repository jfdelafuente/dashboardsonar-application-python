"""
Input Validators Module
========================

Provides validation functions for business logic inputs.

Features:
    - Date range validation
    - Application name format validation
    - Metric value bounds checking
    - Email format validation

Usage:
    from infocodest.utils.validators import validate_date_range, validate_email

    if not validate_date_range(start, end):
        raise ValueError("Invalid date range")

    if validate_email(user_email):
        send_notification(user_email)

Created: Phase 4 - Utilities System
"""

import re
from datetime import date
from typing import Optional, Any


def validate_date_range(
    start_date: Optional[date],
    end_date: Optional[date]
) -> bool:
    """
    Valida que rango de fechas sea coherente.

    Args:
        start_date: Fecha inicial (puede ser None)
        end_date: Fecha final (puede ser None)

    Returns:
        True si el rango es válido, False en caso contrario

    Example:
        >>> from datetime import date
        >>> validate_date_range(date(2025, 1, 1), date(2025, 12, 31))
        True
        >>> validate_date_range(date(2025, 12, 31), date(2025, 1, 1))
        False
        >>> validate_date_range(None, date(2025, 12, 31))
        True

    Notes:
        - Si ambas fechas son None, retorna True
        - Si solo una fecha es None, retorna True
        - Si ambas existen, verifica start_date <= end_date
    """
    if start_date is None or end_date is None:
        return True

    return start_date <= end_date


def validate_application_name(app_name: str) -> bool:
    """
    Valida formato de nombre de aplicación.

    Args:
        app_name: Nombre de la aplicación

    Returns:
        True si el nombre es válido, False en caso contrario

    Example:
        >>> validate_application_name("my-app")
        True
        >>> validate_application_name("my_app_123")
        True
        >>> validate_application_name("")
        False
        >>> validate_application_name("a" * 300)
        False

    Rules:
        - No puede estar vacío
        - Longitud máxima: 255 caracteres
        - Solo caracteres alfanuméricos, guiones (-), guiones bajos (_)
    """
    if not app_name:
        return False

    if len(app_name) > 255:
        return False

    # Pattern: alphanumeric, hyphens, underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, app_name))


def validate_metric_value(
    value: Any,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> bool:
    """
    Valida que un valor de métrica esté en rango válido.

    Args:
        value: Valor a validar
        min_value: Valor mínimo permitido (opcional)
        max_value: Valor máximo permitido (opcional)

    Returns:
        True si el valor es válido, False en caso contrario

    Example:
        >>> validate_metric_value(50, min_value=0, max_value=100)
        True
        >>> validate_metric_value(150, min_value=0, max_value=100)
        False
        >>> validate_metric_value(-10, min_value=0)
        False
        >>> validate_metric_value("invalid")
        False

    Notes:
        - El valor debe ser numérico (int o float)
        - Si min_value es None, no hay límite inferior
        - Si max_value es None, no hay límite superior
    """
    # Check if value is numeric
    if not isinstance(value, (int, float)):
        return False

    # Check minimum bound
    if min_value is not None and value < min_value:
        return False

    # Check maximum bound
    if max_value is not None and value > max_value:
        return False

    return True


def validate_email(email: str) -> bool:
    """
    Valida formato de email.

    Args:
        email: Dirección de email

    Returns:
        True si el formato es válido, False en caso contrario

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
        >>> validate_email("@example.com")
        False
        >>> validate_email("user@")
        False

    Rules:
        - Debe contener exactamente un '@'
        - Debe tener texto antes del '@' (local part)
        - Debe tener texto después del '@' (domain)
        - El dominio debe contener al menos un punto
        - Formato básico: local@domain.tld

    Notes:
        Esta es una validación básica. Para validación completa
        según RFC 5322, usar una librería especializada como
        email-validator.
    """
    if not email or not isinstance(email, str):
        return False

    # Basic pattern: local@domain.tld
    # - At least one character before @
    # - Exactly one @
    # - At least one character after @
    # - At least one dot in domain part
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    return bool(re.match(pattern, email))


def validate_repository_name(repo_name: str) -> bool:
    """
    Valida formato de nombre de repositorio.

    Args:
        repo_name: Nombre del repositorio

    Returns:
        True si el nombre es válido, False en caso contrario

    Example:
        >>> validate_repository_name("my-repo")
        True
        >>> validate_repository_name("org/repo")
        True
        >>> validate_repository_name("")
        False

    Rules:
        - No puede estar vacío
        - Longitud máxima: 255 caracteres
        - Puede contener: alfanuméricos, guiones, guiones bajos, puntos, slash
    """
    if not repo_name:
        return False

    if len(repo_name) > 255:
        return False

    # Pattern: alphanumeric, hyphens, underscores, dots, slash
    pattern = r'^[a-zA-Z0-9_.\-/]+$'
    return bool(re.match(pattern, repo_name))


def validate_percentage(value: Any) -> bool:
    """
    Valida que un valor sea un porcentaje válido (0-100).

    Args:
        value: Valor a validar

    Returns:
        True si es un porcentaje válido, False en caso contrario

    Example:
        >>> validate_percentage(50)
        True
        >>> validate_percentage(100.0)
        True
        >>> validate_percentage(150)
        False
        >>> validate_percentage(-10)
        False

    Notes:
        - Acepta int y float
        - Rango válido: 0 <= value <= 100
    """
    return validate_metric_value(value, min_value=0.0, max_value=100.0)


def validate_rating(rating: Any) -> bool:
    """
    Valida que un rating sea válido (A-E o 1-5).

    Args:
        rating: Rating a validar (puede ser str o int)

    Returns:
        True si el rating es válido, False en caso contrario

    Example:
        >>> validate_rating("A")
        True
        >>> validate_rating("E")
        True
        >>> validate_rating(1)
        True
        >>> validate_rating(5)
        True
        >>> validate_rating("F")
        False
        >>> validate_rating(0)
        False

    Notes:
        - Acepta letras: A, B, C, D, E (mayúsculas)
        - Acepta números: 1, 2, 3, 4, 5
    """
    if isinstance(rating, str):
        return rating.upper() in ['A', 'B', 'C', 'D', 'E']
    elif isinstance(rating, int):
        return 1 <= rating <= 5
    else:
        return False
