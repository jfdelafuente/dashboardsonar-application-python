"""Service for dashboard KPI calculations and metrics aggregation.

This module provides business logic for calculating dashboard KPIs with
percentage variations over time periods. It orchestrates repository operations
and implements the calculation algorithms previously in models/database.py.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.repositories.historico_repository import HistoricoRepository
from infocodest.repositories.daily_repository import DailyRepository


class DashboardService:
    """Service for dashboard KPI calculations.

    This service handles business logic for:
    - Global KPI calculations with percentage variations
    - Application-specific KPI calculations
    - Provider-specific KPI calculations
    - Repository-specific KPI calculations
    - Time-based comparisons (current vs N days ago)

    Migrated from: models/database.py (getDatosMetricas, getDatosAplicacion, getDatosProveedor, getDatosRepositorios)
    """

    def __init__(
        self,
        metrica_repo: Optional[MetricaRepository] = None,
        historico_repo: Optional[HistoricoRepository] = None,
        daily_repo: Optional[DailyRepository] = None,
        days: Optional[int] = None
    ):
        """Initialize DashboardService with repository dependencies.

        Args:
            metrica_repo: Repository for metrics data (default: new instance)
            historico_repo: Repository for historical analysis data (default: new instance)
            daily_repo: Repository for daily aggregated data (default: new instance)
            days: Number of days for comparison period (default: from environment DAYS)
        """
        self.metrica_repo = metrica_repo or MetricaRepository()
        self.historico_repo = historico_repo or HistoricoRepository()
        self.daily_repo = daily_repo or DailyRepository()
        self.days = days if days is not None else int(os.environ.get('DAYS', '15'))

    def get_kpi_overview(self) -> Dict[str, Any]:
        """Calculate global KPIs with percentage variations.

        Calculates current global metrics (applications, repositories, bugs, analysis, quality)
        and compares them with values from N days ago to compute percentage variations.

        Returns:
            Dictionary with KPI values and variation data:
            {
                'aplicaciones': 42,
                'aplicaciones_value': '12.50',
                'aplicaciones_text': '12.50% Increase in 15 Days',
                'repositorios': 120,
                'repositorios_value': '-5.30',
                'repositorios_text': '-5.30% Decrease in 15 Days',
                ...
            }

        Migrated from: models/database.py::getDatosMetricas()
        """
        fecha = self._get_date_n_days_ago(self.days)

        # Current global metrics
        current = {
            'aplicaciones': self.metrica_repo.count_distinct_aplicaciones(),
            'repositorios': self.metrica_repo.count(),
            'bugs': self.metrica_repo.sum_bugs(),
            'analisis': self.historico_repo.count(),
            'quality': self.historico_repo.count_by_alert_status('OK'),
        }

        # Metrics from N days ago (from Daily aggregates)
        old = {
            'aplicaciones': self.daily_repo.count_distinct_aplicaciones_by_date(fecha),
            'repositorios': self.daily_repo.count_by_date(fecha),
            'bugs': self.daily_repo.sum_bugs_by_date(fecha),
            'analisis': self.daily_repo.sum_analisis_by_date(fecha),
            'quality': self.daily_repo.sum_quality_by_date(fecha),
        }

        return self._format_kpi_response(current, old, ['aplicaciones', 'repositorios', 'bugs', 'analisis', 'quality'])

    def get_kpi_by_application(self, aplicacion: str) -> Dict[str, Any]:
        """Calculate application-specific KPIs with percentage variations.

        Args:
            aplicacion: Application name to filter by

        Returns:
            Dictionary with application KPI values and variation data

        Migrated from: models/database.py::getDatosAplicacion()
        """
        fecha = self._get_date_n_days_ago(self.days)

        # Current application metrics
        current = {
            'aplicaciones': self.metrica_repo.count_distinct_aplicaciones_by_aplicacion(aplicacion),
            'repositorios': self.metrica_repo.count_distinct_repos_by_aplicacion(aplicacion),
            'bugs': self.metrica_repo.sum_bugs_by_aplicacion(aplicacion),
            'analisis': self.historico_repo.count_by_aplicacion(aplicacion),
            'quality': self.historico_repo.count_by_aplicacion_and_alert_status(aplicacion, 'OK'),
        }

        # Metrics from N days ago
        old = {
            'aplicaciones': self.daily_repo.count_distinct_aplicaciones_by_date_and_aplicacion(fecha, aplicacion),
            'repositorios': self.daily_repo.count_distinct_repos_by_date_and_aplicacion(fecha, aplicacion),
            'bugs': self.daily_repo.sum_bugs_by_date_and_aplicacion(fecha, aplicacion),
            'analisis': self.daily_repo.sum_analisis_by_date_and_aplicacion(fecha, aplicacion),
            'quality': self.daily_repo.sum_quality_by_date_and_aplicacion(fecha, aplicacion),
        }

        return self._format_kpi_response(current, old, ['aplicaciones', 'repositorios', 'bugs', 'analisis', 'quality'])

    def get_kpi_by_proveedor(self, proveedor: str) -> Dict[str, Any]:
        """Calculate provider-specific KPIs with percentage variations.

        Args:
            proveedor: Provider name to filter by

        Returns:
            Dictionary with provider KPI values and variation data

        Migrated from: models/database.py::getDatosProveedor()
        """
        fecha = self._get_date_n_days_ago(self.days)

        # Current provider metrics
        current = {
            'aplicaciones': self.metrica_repo.count_distinct_aplicaciones_by_proveedor(proveedor),
            'repositorios': self.metrica_repo.count_by_proveedor(proveedor),
            'bugs': self.metrica_repo.sum_bugs_by_proveedor(proveedor),
            'analisis': self.historico_repo.count_by_proveedor(proveedor),
            'quality': self.historico_repo.count_by_proveedor_and_alert_status(proveedor, 'OK'),
        }

        # Metrics from N days ago
        old = {
            'aplicaciones': self.daily_repo.count_distinct_aplicaciones_by_date_and_proveedor(fecha, proveedor),
            'repositorios': self.daily_repo.count_by_date_and_proveedor(fecha, proveedor),
            'bugs': self.daily_repo.sum_bugs_by_date_and_proveedor(fecha, proveedor),
            'analisis': self.daily_repo.sum_analisis_by_date_and_proveedor(fecha, proveedor),
            'quality': self.daily_repo.sum_quality_by_date_and_proveedor(fecha, proveedor),
        }

        return self._format_kpi_response(current, old, ['aplicaciones', 'repositorios', 'bugs', 'analisis', 'quality'])

    def get_kpi_by_repository(self, aplicacion: str, repo: str) -> Dict[str, Any]:
        """Calculate repository-specific KPIs with percentage variations.

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            Dictionary with repository KPI values and variation data

        Migrated from: models/database.py::getDatosRepositorios()
        """
        fecha = self._get_date_n_days_ago(self.days)

        # Current repository metrics
        current = {
            'aplicaciones': self.metrica_repo.count_distinct_aplicaciones_by_aplicacion_and_repo(aplicacion, repo),
            'repositorios': self.metrica_repo.count_by_aplicacion_and_repo(aplicacion, repo),
            'bugs': self.metrica_repo.sum_bugs_by_aplicacion_and_repo(aplicacion, repo),
            'analisis': self.historico_repo.count_by_aplicacion_and_repo(aplicacion, repo),
            'quality': self.historico_repo.count_by_aplicacion_repo_and_alert_status(aplicacion, repo, 'OK'),
        }

        # Metrics from N days ago
        old = {
            'aplicaciones': self.daily_repo.count_distinct_aplicaciones_by_date_aplicacion_and_repo(fecha, aplicacion, repo),
            'repositorios': self.daily_repo.count_by_date_aplicacion_and_repo(fecha, aplicacion, repo),
            'bugs': self.daily_repo.sum_bugs_by_date_aplicacion_and_repo(fecha, aplicacion, repo),
            'analisis': self.daily_repo.sum_analisis_by_date_aplicacion_and_repo(fecha, aplicacion, repo),
            'quality': self.daily_repo.get_quality_by_date_aplicacion_and_repo(fecha, aplicacion, repo),
        }

        return self._format_kpi_response(current, old, ['aplicaciones', 'repositorios', 'bugs', 'analisis', 'quality'])

    # Private helper methods

    def _get_date_n_days_ago(self, days: int) -> str:
        """Calculate date N days ago in YYYY-MM-DD format.

        Args:
            days: Number of days to subtract from today

        Returns:
            Date string in format 'YYYY-MM-DD'

        Migrated from: models/database.py::obtener_fecha_hace_dias()
        """
        start_date = datetime.now() - timedelta(days=days)
        return start_date.strftime("%Y-%m-%d")

    def _calculate_variation(self, current: int, old: int) -> tuple[float, str]:
        """Calculate percentage variation between current and old values.

        Args:
            current: Current value
            old: Old value to compare against

        Returns:
            Tuple of (percentage_variation, comparison_text)
            Example: (12.5, 'Increase') or (-5.3, 'Decrease')

        Migrated from: models/database.py::definir_texto()
        """
        if current == 0 and old == 0:
            return 0.0, "Igual"

        try:
            variation = (current / old) * 100 - 100
        except ZeroDivisionError:
            variation = 100.0
        except (TypeError, ValueError):
            variation = 100.0

        comparison = "Decrease" if variation < 0 else "Increase"
        return round(variation, 1), comparison

    def _format_kpi_response(
        self,
        current_data: Dict[str, int],
        old_data: Dict[str, int],
        keys: list[str]
    ) -> Dict[str, Any]:
        """Format KPI data with variations for template rendering.

        Args:
            current_data: Current metric values
            old_data: Old metric values (from N days ago)
            keys: List of metric keys to process

        Returns:
            Dictionary with formatted KPI data including:
            - {key}: raw value
            - {key}_value: variation percentage as string ('12.50')
            - {key}_text: formatted text ('12.50% Increase in 15 Days')

        Migrated from: models/database.py::calcular_datos()
        """
        result = {}

        for key in keys:
            current_val = current_data.get(key, 0)
            old_val = old_data.get(key, 0)

            result[key] = current_val
            variation, comparison = self._calculate_variation(current_val, old_val)
            result[f'{key}_value'] = f'{variation:.2f}'
            result[f'{key}_text'] = f'{variation:.2f}% {comparison} in {self.days} Days'

        return result
