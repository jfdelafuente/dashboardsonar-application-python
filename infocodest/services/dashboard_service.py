"""Service for dashboard KPI calculations and metrics aggregation.

This module provides business logic for calculating dashboard KPIs with
percentage variations over time periods. It orchestrates repository operations
and implements the calculation algorithms previously in models/database.py.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta, date
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
            'quality': self.historico_repo.count_quality_ok(),
        }

        # Metrics from N days ago (from Daily aggregates)
        old = {
            'aplicaciones': self.daily_repo.count_distinct_aplicaciones_by_date(fecha),
            'repositorios': self.daily_repo.count_repos_by_date(fecha),
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
            'aplicaciones': self.metrica_repo.count_aplicaciones_by_aplicacion(aplicacion),
            'repositorios': self.metrica_repo.count_by_aplicacion(aplicacion),
            'bugs': self.metrica_repo.sum_bugs_by_aplicacion(aplicacion),
            'analisis': self.historico_repo.count_by_aplicacion(aplicacion),
            'quality': self.historico_repo.count_quality_ok_by_aplicacion(aplicacion),
        }

        # Metrics from N days ago
        old = {
            'aplicaciones': self.daily_repo.count_aplicaciones_by_date_and_app(fecha, aplicacion),
            'repositorios': self.daily_repo.count_repos_by_date_and_app(fecha, aplicacion),
            'bugs': self.daily_repo.sum_bugs_by_date_and_app(fecha, aplicacion),
            'analisis': self.daily_repo.sum_analisis_by_date_and_app(fecha, aplicacion),
            'quality': self.daily_repo.sum_quality_by_date_and_app(fecha, aplicacion),
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
            'quality': self.historico_repo.count_quality_ok_by_proveedor(proveedor),
        }

        # Metrics from N days ago
        old = {
            'aplicaciones': self.daily_repo.count_aplicaciones_by_date_and_proveedor(fecha, proveedor),
            'repositorios': self.daily_repo.count_repos_by_date_and_proveedor(fecha, proveedor),
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
            'aplicaciones': self.metrica_repo.count_aplicaciones_by_aplicacion_and_repo(aplicacion, repo),
            'repositorios': self.metrica_repo.count_by_aplicacion_and_repo(aplicacion, repo),
            'bugs': self.metrica_repo.sum_bugs_by_aplicacion_and_repo(aplicacion, repo),
            'analisis': self.historico_repo.count_by_aplicacion_and_repo(aplicacion, repo),
            'quality': self.historico_repo.count_quality_ok_by_repo(aplicacion, repo),
        }

        # Metrics from N days ago
        old = {
            'aplicaciones': self.daily_repo.count_aplicaciones_by_date_and_repo(fecha, aplicacion, repo),
            'repositorios': self.daily_repo.count_repos_by_date_and_repo(fecha, aplicacion, repo),
            'bugs': self.daily_repo.sum_bugs_by_date_and_repo(fecha, aplicacion, repo),
            'analisis': self.daily_repo.sum_analisis_by_date_and_repo(fecha, aplicacion, repo),
            'quality': self.daily_repo.get_quality_by_date_and_repo(fecha, aplicacion, repo),
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

    # Public query methods for views

    def get_distinct_applications(self) -> List[Tuple[str]]:
        """Get list of distinct application names.

        Returns:
            List of tuples containing application names
            Example: [('app1',), ('app2',), ('app3',)]

        Migrated from: home/views.py::get_distinct_apps()
        """
        from infocodest.models.metricas import Metrica

        results = Metrica.query.with_entities(
            Metrica.aplicacion
        ).distinct().all()

        return results

    def get_distinct_providers(self) -> List[Tuple[str]]:
        """Get list of distinct provider names.

        Returns:
            List of tuples containing provider names
            Example: [('provider1',), ('provider2',)]

        Migrated from: home/views.py::get_distinct_providers()
        """
        from infocodest.models.metricas import Metrica
        from infocodest.models.proveedor import Proveedor

        results = Proveedor.query \
            .join(Metrica, Proveedor.aplicacion == Metrica.aplicacion) \
            .with_entities(Proveedor.proveedor) \
            .distinct() \
            .all()

        return results

    def get_all_metricas_with_proveedor(self) -> List[Any]:
        """Get all metricas with provider info, ordered by date desc.

        Returns:
            List of metric records with provider type and all metric fields

        Migrated from: home/views.py::get_metricas()
        """
        from infocodest.models.metricas import Metrica
        from infocodest.models.proveedor import Proveedor

        metricas = Metrica.query \
            .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion) \
            .order_by(Metrica.fecha.desc()) \
            .with_entities(
                Metrica.aplicacion,
                Metrica.repo,
                Metrica.size,
                Metrica.fecha,
                Metrica.reliability_label,
                Metrica.reliability_rating,
                Metrica.bugs,
                Metrica.security_label,
                Metrica.security_rating,
                Metrica.vulnerabilities,
                Metrica.sqale_label,
                Metrica.sqale_rating,
                Metrica.code_smells,
                Metrica.alert_status,
                Metrica.quality_gate,
                Metrica.project,
                Metrica.coverage,
                Metrica.unit_tests,
                Proveedor.tipo
            ) \
            .all()

        return metricas

    def get_all_stats_with_proveedor(self) -> List[Any]:
        """Get all stats with provider info.

        Returns:
            List of stat records with provider type

        Migrated from: home/views.py::get_stats()
        """
        from infocodest.models.stat import Stat
        from infocodest.models.proveedor import Proveedor

        stats = Stat.query \
            .join(Proveedor, Proveedor.aplicacion == Stat.aplicacion) \
            .with_entities(
                Stat.aplicacion,
                Stat.repos,
                Stat.reliability_label,
                Stat.reliability_rating,
                Stat.security_label,
                Stat.security_rating,
                Stat.sqale_label,
                Stat.sqale_rating,
                Stat.alert_status_label,
                Stat.alert_status_ok,
                Stat.dloc_label,
                Stat.dloc_rating,
                Stat.coverage_label,
                Stat.coverage_rating,
                Proveedor.tipo
            ) \
            .all()

        return stats

    def get_metricas_by_aplicacion(self, aplicacion: str) -> List[Any]:
        """Get metricas for specific application with provider info.

        Args:
            aplicacion: Application name to filter by

        Returns:
            List of metric records for the application

        Migrated from: home/views.py::get_metricas_aplicacion()
        """
        from infocodest.models.metricas import Metrica
        from infocodest.models.proveedor import Proveedor

        return Metrica.query \
            .join(Proveedor, Metrica.aplicacion == Proveedor.aplicacion) \
            .filter(Metrica.aplicacion == aplicacion) \
            .order_by(Metrica.fecha.desc()) \
            .with_entities(
                Metrica.aplicacion,
                Metrica.repo,
                Metrica.size,
                Metrica.fecha,
                Metrica.reliability_label,
                Metrica.reliability_rating,
                Metrica.bugs,
                Metrica.security_label,
                Metrica.security_rating,
                Metrica.vulnerabilities,
                Metrica.sqale_label,
                Metrica.sqale_rating,
                Metrica.code_smells,
                Metrica.alert_status,
                Metrica.quality_gate,
                Metrica.project,
                Metrica.coverage,
                Metrica.unit_tests,
                Proveedor.tipo
            ) \
            .all()

    def get_stats_by_aplicacion(self, aplicacion: str) -> List[Any]:
        """Get stats for specific application.

        Args:
            aplicacion: Application name to filter by

        Returns:
            List of stat records for the application

        Migrated from: home/views.py::get_stats_aplicacion()
        """
        from infocodest.models.stat import Stat
        from infocodest.models.proveedor import Proveedor

        return Stat.query \
            .join(Proveedor, Stat.aplicacion == Proveedor.aplicacion) \
            .filter(Stat.aplicacion == aplicacion) \
            .with_entities(
                Stat.aplicacion,
                Stat.repos,
                Stat.reliability_label,
                Stat.reliability_rating,
                Stat.security_label,
                Stat.security_rating,
                Stat.sqale_label,
                Stat.sqale_rating,
                Stat.alert_status_label,
                Stat.alert_status_ok,
                Stat.dloc_label,
                Stat.dloc_rating,
                Stat.coverage_label,
                Stat.coverage_rating,
                Proveedor.tipo
            ) \
            .all()

    def get_metricas_by_proveedor(self, proveedor: str) -> List[Any]:
        """Get metricas for specific provider.

        Args:
            proveedor: Provider name to filter by

        Returns:
            List of metric records for the provider

        Migrated from: home/views.py::get_metricas_proveedor()
        """
        from infocodest.models.metricas import Metrica
        from infocodest.models.proveedor import Proveedor

        return Metrica.query \
            .join(Proveedor, Metrica.aplicacion == Proveedor.aplicacion) \
            .filter(Proveedor.proveedor == proveedor) \
            .order_by(Metrica.aplicacion.asc(), Metrica.fecha.desc()) \
            .with_entities(
                Metrica.aplicacion,
                Metrica.repo,
                Metrica.size,
                Metrica.fecha,
                Metrica.reliability_label,
                Metrica.reliability_rating,
                Metrica.bugs,
                Metrica.security_label,
                Metrica.security_rating,
                Metrica.vulnerabilities,
                Metrica.sqale_label,
                Metrica.sqale_rating,
                Metrica.code_smells,
                Metrica.alert_status,
                Metrica.quality_gate,
                Metrica.project,
                Metrica.coverage,
                Metrica.unit_tests,
                Proveedor.tipo
            )

    def get_stats_by_proveedor(self, proveedor: str) -> List[Any]:
        """Get stats for specific provider.

        Args:
            proveedor: Provider name to filter by

        Returns:
            List of stat records for the provider

        Migrated from: home/views.py::get_stats_proveedor()
        """
        from infocodest.models.stat import Stat
        from infocodest.models.proveedor import Proveedor

        return Stat.query \
            .join(Proveedor, Stat.aplicacion == Proveedor.aplicacion) \
            .filter(Proveedor.proveedor == proveedor) \
            .with_entities(
                Stat.aplicacion,
                Stat.repos,
                Stat.reliability_label,
                Stat.reliability_rating,
                Stat.security_label,
                Stat.security_rating,
                Stat.sqale_label,
                Stat.sqale_rating,
                Stat.alert_status_label,
                Stat.alert_status_ok,
                Stat.dloc_label,
                Stat.dloc_rating,
                Stat.coverage_label,
                Stat.coverage_rating,
                Proveedor.tipo
            ) \
            .all()

    def get_daily_summary(self) -> List[Any]:
        """Get daily summary for yesterday, grouped by application.

        Returns:
            List of daily aggregated records for yesterday

        Migrated from: home/views.py::get_dailys()
        """
        from infocodest.models.daily import Daily
        from sqlalchemy.sql import func

        return Daily.query \
            .filter(Daily.created_on == date.today() - timedelta(days=1)) \
            .group_by(Daily.aplicacion) \
            .with_entities(
                Daily.aplicacion,
                func.count('*').label('repo'),
                Daily.proveedor,
                Daily.created_on,
                func.sum(Daily.num_bugs).label('num_bugs'),
                func.sum(Daily.num_vulnerabilities).label('num_vulnerabilities'),
                func.sum(Daily.num_code_smells).label('num_code_smells'),
                func.sum(Daily.num_quality).label('num_quality'),
                func.sum(Daily.num_analisis).label('num_analisis')
            ) \
            .all()

    def get_daily_by_proveedor(self, proveedor: str) -> List[Any]:
        """Get daily summary for specific provider.

        Args:
            proveedor: Provider name to filter by

        Returns:
            List of daily aggregated records for the provider

        Migrated from: home/views.py::get_dailys_proveedor()
        """
        from infocodest.models.daily import Daily
        from sqlalchemy.sql import func

        return Daily.query \
            .filter(Daily.created_on == date.today() - timedelta(days=1)) \
            .group_by(Daily.aplicacion) \
            .filter(Daily.proveedor == proveedor) \
            .with_entities(
                Daily.aplicacion,
                func.count('*').label('repo'),
                Daily.proveedor,
                Daily.created_on,
                func.sum(Daily.num_bugs).label('num_bugs'),
                func.sum(Daily.num_vulnerabilities).label('num_vulnerabilities'),
                func.sum(Daily.num_code_smells).label('num_code_smells'),
                func.sum(Daily.num_quality).label('num_quality'),
                func.sum(Daily.num_analisis).label('num_analisis')
            ) \
            .all()

    def get_daily_details_by_aplicacion(self, aplicacion: str) -> List[Any]:
        """Get daily details for specific application.

        Args:
            aplicacion: Application name to filter by

        Returns:
            List of daily detail records for the application

        Migrated from: home/views.py::get_dailys_details_aplicacion()
        """
        from infocodest.models.daily import Daily

        return Daily.query \
            .filter(Daily.created_on == date.today() - timedelta(days=1)) \
            .filter(Daily.aplicacion == aplicacion) \
            .with_entities(
                Daily.aplicacion,
                Daily.repo,
                Daily.proveedor,
                Daily.created_on,
                Daily.num_bugs,
                Daily.num_vulnerabilities,
                Daily.num_code_smells,
                Daily.num_quality,
                Daily.num_analisis
            ) \
            .all()

    def get_daily_details_by_repo(self, aplicacion: str, repo: str) -> List[Any]:
        """Get daily details for specific repository.

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            List of daily detail records for the repository

        Migrated from: home/views.py::get_dailys_details_repo()
        """
        from infocodest.models.daily import Daily
        from sqlalchemy import and_

        return Daily.query \
            .filter(Daily.created_on == date.today() - timedelta(days=1)) \
            .filter(and_(Daily.repo == repo, Daily.aplicacion == aplicacion)) \
            .with_entities(
                Daily.aplicacion,
                Daily.repo,
                Daily.proveedor,
                Daily.created_on,
                Daily.num_bugs,
                Daily.num_vulnerabilities,
                Daily.num_code_smells,
                Daily.num_quality,
                Daily.num_analisis
            ) \
            .all()

    def get_historico_by_aplicacion_and_repo(
        self,
        aplicacion: str,
        repo: str
    ) -> List[Any]:
        """Get historical data for specific repository.

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            List of historical records for the repository

        Migrated from: home/views.py::get_historico_name()
        """
        from infocodest.models.historico import Historico
        from infocodest.models.proveedor import Proveedor
        from sqlalchemy import and_

        return Historico.query \
            .join(Proveedor, Historico.aplicacion == Proveedor.aplicacion) \
            .filter(and_(Historico.repo == repo, Historico.aplicacion == aplicacion)) \
            .order_by(Historico.fecha.desc()) \
            .with_entities(
                Historico.aplicacion,
                Historico.repo,
                Historico.size,
                Historico.fecha,
                Historico.reliability_label,
                Historico.reliability_rating,
                Historico.bugs,
                Historico.security_label,
                Historico.security_rating,
                Historico.vulnerabilities,
                Historico.sqale_label,
                Historico.sqale_rating,
                Historico.code_smells,
                Historico.alert_status,
                Historico.quality_gate,
                Historico.project,
                Historico.coverage,
                Historico.unit_tests,
                Proveedor.tipo
            ) \
            .all()
