"""Service layer for business logic operations.

This package implements the Service Layer Pattern, providing business logic
that orchestrates repository operations and implements domain workflows.
Each service encapsulates business rules for a specific domain area.

Example usage:
    >>> from infocodest.services import DashboardService
    >>> service = DashboardService()
    >>> kpis = service.get_kpi_overview()
"""

from .dashboard_service import DashboardService
from .metrica_service import MetricaService
from .auth_service import AuthService

__all__ = [
    'DashboardService',
    'MetricaService',
    'AuthService',
]
