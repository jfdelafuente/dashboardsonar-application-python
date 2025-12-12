"""
Helper Functions Module
========================

Provides common utility functions for the application.

Features:
    - Percentage formatting
    - Variation calculation
    - Safe division with zero handling
    - Flexible date parsing
    - Trend classification

Usage:
    from infocodest.utils.helpers import format_percentage, calculate_variation

    percentage = calculate_variation(current=120, old=100)
    formatted = format_percentage(percentage)  # "+20.00%"

Created: Phase 4 - Utilities System
"""

from datetime import date, datetime
from typing import Optional, List


def format_percentage(
    value: float,
    decimals: int = 2,
    include_sign: bool = True
) -> str:
    """
    Formatea un número como porcentaje.

    Args:
        value: Valor a formatear (ej: 0.1234 o 12.34)
        decimals: Número de decimales (default: 2)
        include_sign: Incluir signo + para positivos (default: True)

    Returns:
        String formateado (ej: "+12.34%", "-5.67%", "0.00%")

    Example:
        >>> format_percentage(12.34)
        '+12.34%'
        >>> format_percentage(-5.67)
        '-5.67%'
        >>> format_percentage(0)
        '0.00%'
        >>> format_percentage(12.345, decimals=1)
        '+12.3%'
        >>> format_percentage(12.34, include_sign=False)
        '12.34%'

    Notes:
        - Valores positivos incluyen signo + si include_sign=True
        - Valores negativos siempre incluyen signo -
        - Cero nunca incluye signo
    """
    # Format with specified decimals
    formatted_value = f"{value:.{decimals}f}"

    # Add sign if needed
    if value > 0 and include_sign:
        return f"+{formatted_value}%"
    elif value == 0:
        return f"{formatted_value}%"
    else:
        return f"{formatted_value}%"


def calculate_variation(
    current_value: float,
    old_value: float,
    as_percentage: bool = True
) -> float:
    """
    Calcula variación entre dos valores.

    Args:
        current_value: Valor actual
        old_value: Valor anterior
        as_percentage: Retornar como porcentaje (default: True)

    Returns:
        Variación calculada (porcentaje o decimal)

    Example:
        >>> calculate_variation(120, 100)
        20.0
        >>> calculate_variation(80, 100)
        -20.0
        >>> calculate_variation(100, 100)
        0.0
        >>> calculate_variation(50, 0)
        100.0
        >>> calculate_variation(0, 0)
        0.0
        >>> calculate_variation(120, 100, as_percentage=False)
        0.2

    Formula:
        - Si old_value == 0 y current_value == 0: retorna 0.0
        - Si old_value == 0 y current_value > 0: retorna 100.0 (o 1.0)
        - Caso normal: ((current_value / old_value) * 100) - 100

    Notes:
        - Maneja división por cero de forma segura
        - Retorna porcentaje por defecto (20.0 = +20%)
        - as_percentage=False retorna decimal (0.2 = +20%)
    """
    # Handle zero old_value
    if old_value == 0:
        if current_value == 0:
            return 0.0
        else:
            # 100% increase if old was zero and current is not
            return 100.0 if as_percentage else 1.0

    # Normal case
    if as_percentage:
        return ((current_value / old_value) * 100) - 100
    else:
        return (current_value / old_value) - 1


def safe_division(
    numerator: float,
    denominator: float,
    default: float = 0.0
) -> float:
    """
    División segura que maneja división por cero.

    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor por defecto si denominator es 0 (default: 0.0)

    Returns:
        Resultado de la división o valor por defecto

    Example:
        >>> safe_division(10, 2)
        5.0
        >>> safe_division(10, 0)
        0.0
        >>> safe_division(10, 0, default=None)
        >>> safe_division(100, 0, default=-1)
        -1

    Notes:
        - Evita ZeroDivisionError
        - Permite especificar valor por defecto personalizado
        - Útil para cálculos de métricas que pueden tener cero
    """
    if denominator == 0:
        return default

    return numerator / denominator


def parse_date_string(
    date_str: str,
    formats: Optional[List[str]] = None
) -> Optional[date]:
    """
    Parsea string de fecha intentando múltiples formatos.

    Args:
        date_str: String con fecha
        formats: Lista de formatos a intentar (opcional)

    Returns:
        Objeto date si se parsea exitosamente, None en caso contrario

    Example:
        >>> parse_date_string("2025-12-12")
        datetime.date(2025, 12, 12)
        >>> parse_date_string("12/12/2025")
        datetime.date(2025, 12, 12)
        >>> parse_date_string("invalid")
        None

    Default Formats:
        - %Y-%m-%d (ISO: 2025-12-12)
        - %d/%m/%Y (Español: 12/12/2025)
        - %d-%m-%Y (Español con guión: 12-12-2025)
        - %Y/%m/%d (ISO con slash: 2025/12/12)

    Notes:
        - Intenta cada formato en orden
        - Retorna None si ningún formato funciona
        - Retorna objeto date (no datetime)
    """
    if formats is None:
        formats = [
            '%Y-%m-%d',      # ISO: 2025-12-12
            '%d/%m/%Y',      # Español: 12/12/2025
            '%d-%m-%Y',      # Español con guión: 12-12-2025
            '%Y/%m/%d',      # ISO con slash: 2025/12/12
            '%Y%m%d',        # Compacto: 20251212
        ]

    for fmt in formats:
        try:
            parsed_datetime = datetime.strptime(date_str, fmt)
            return parsed_datetime.date()
        except (ValueError, TypeError):
            continue

    return None


def get_variation_trend(variation: float, threshold: float = 0.1) -> str:
    """
    Determina la tendencia de una variación.

    Args:
        variation: Valor de variación (porcentaje)
        threshold: Umbral para considerar cambio significativo (default: 0.1)

    Returns:
        "Increase", "Decrease", o "Stable"

    Example:
        >>> get_variation_trend(5.0)
        'Increase'
        >>> get_variation_trend(-3.0)
        'Decrease'
        >>> get_variation_trend(0.05)
        'Stable'
        >>> get_variation_trend(0.5, threshold=1.0)
        'Stable'

    Notes:
        - variation > threshold: "Increase"
        - variation < -threshold: "Decrease"
        - -threshold <= variation <= threshold: "Stable"
        - Threshold por defecto: 0.1% (muy sensible)
    """
    if variation > threshold:
        return "Increase"
    elif variation < -threshold:
        return "Decrease"
    else:
        return "Stable"


def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Trunca un string a longitud máxima con sufijo.

    Args:
        text: Texto a truncar
        max_length: Longitud máxima (incluyendo sufijo)
        suffix: Sufijo a añadir si se trunca (default: '...')

    Returns:
        Texto truncado

    Example:
        >>> truncate_string("Hello World", 8)
        'Hello...'
        >>> truncate_string("Hello", 10)
        'Hello'
        >>> truncate_string("Long text here", 10, suffix='»')
        'Long text»'

    Notes:
        - Si text.length <= max_length, retorna text sin cambios
        - Sufijo cuenta para la longitud total
        - max_length debe ser >= len(suffix)
    """
    if len(text) <= max_length:
        return text

    if max_length < len(suffix):
        raise ValueError(f"max_length must be >= len(suffix) ({len(suffix)})")

    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix


def get_quality_gate_color(status: str) -> str:
    """
    Retorna color para status de quality gate.

    Args:
        status: Status del quality gate ("OK", "ERROR", "WARN", etc.)

    Returns:
        Color correspondiente ("green", "red", "yellow", "gray")

    Example:
        >>> get_quality_gate_color("OK")
        'green'
        >>> get_quality_gate_color("ERROR")
        'red'
        >>> get_quality_gate_color("WARN")
        'yellow'
        >>> get_quality_gate_color("UNKNOWN")
        'gray'

    Notes:
        - Case-insensitive
        - Status no reconocidos retornan 'gray'
    """
    status_upper = status.upper() if status else ""

    color_map = {
        'OK': 'green',
        'PASSED': 'green',
        'SUCCESS': 'green',
        'ERROR': 'red',
        'FAILED': 'red',
        'FAILURE': 'red',
        'WARN': 'yellow',
        'WARNING': 'yellow',
        'PENDING': 'yellow',
    }

    return color_map.get(status_upper, 'gray')


def get_rating_color(rating: str) -> str:
    """
    Retorna color para rating (A-E).

    Args:
        rating: Rating (A, B, C, D, E)

    Returns:
        Color correspondiente

    Example:
        >>> get_rating_color("A")
        'green'
        >>> get_rating_color("C")
        'yellow'
        >>> get_rating_color("E")
        'red'

    Notes:
        - A: green (excelente)
        - B: lightgreen (bueno)
        - C: yellow (aceptable)
        - D: orange (pobre)
        - E: red (malo)
    """
    rating_upper = rating.upper() if rating else ""

    color_map = {
        'A': 'green',
        'B': 'lightgreen',
        'C': 'yellow',
        'D': 'orange',
        'E': 'red',
    }

    return color_map.get(rating_upper, 'gray')
