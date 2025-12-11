"""Repository for Daily model operations.

This module provides data access methods for daily aggregated metrics.
"""

from typing import Optional
from datetime import datetime, date
from sqlalchemy import func, and_
from infocodest.models.daily import Daily
from infocodest.repositories.base_repository import BaseRepository


class DailyRepository(BaseRepository[Daily]):
    """Repository for managing daily aggregated metrics.

    This repository provides methods to query daily metric aggregations
    used for comparing current vs historical data.
    """

    def __init__(self):
        """Initialize DailyRepository."""
        super().__init__(Daily)

    def get_by_date(self, fecha: str) -> list[Daily]:
        """Get all daily records for a specific date.

        Args:
            fecha: Date string (format: YYYY-MM-DD)

        Returns:
            List of Daily entities for the date
        """
        return self.filter_by(created_on=fecha)

    def count_distinct_aplicaciones_by_date(self, fecha: str) -> int:
        """Count distinct applications for a specific date.

        Args:
            fecha: Date string (format: YYYY-MM-DD)

        Returns:
            Number of unique applications on that date
        """
        return (
            self.session.query(func.count(func.distinct(Daily.aplicacion)))
            .filter(Daily.created_on == fecha)
            .scalar()
        ) or 0

    def count_repos_by_date(self, fecha: str) -> int:
        """Count repositories for a specific date.

        Args:
            fecha: Date string (format: YYYY-MM-DD)

        Returns:
            Number of repositories on that date
        """
        return (
            self.session.query(func.count(Daily.repo))
            .filter(Daily.created_on == fecha)
            .scalar()
        ) or 0

    def sum_bugs_by_date(self, fecha: str) -> int:
        """Sum bugs for a specific date.

        Args:
            fecha: Date string (format: YYYY-MM-DD)

        Returns:
            Total bugs on that date
        """
        return (
            self.session.query(func.sum(Daily.num_bugs))
            .filter(Daily.created_on == fecha)
            .scalar()
        ) or 0

    def sum_analisis_by_date(self, fecha: str) -> int:
        """Sum analysis count for a specific date.

        Args:
            fecha: Date string (format: YYYY-MM-DD)

        Returns:
            Total analysis count on that date
        """
        return (
            self.session.query(func.sum(Daily.num_analisis))
            .filter(Daily.created_on == fecha)
            .scalar()
        ) or 0

    def sum_quality_by_date(self, fecha: str) -> int:
        """Sum quality gate count for a specific date.

        Args:
            fecha: Date string (format: YYYY-MM-DD)

        Returns:
            Total quality gate count on that date
        """
        return (
            self.session.query(func.sum(Daily.num_quality))
            .filter(Daily.created_on == fecha)
            .scalar()
        ) or 0

    def count_aplicaciones_by_date_and_app(self, fecha: str, aplicacion: str) -> int:
        """Count applications for a specific date and application.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            aplicacion: Application name

        Returns:
            Count (typically 0 or 1)
        """
        return (
            self.session.query(func.count(func.distinct(Daily.aplicacion)))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.aplicacion == aplicacion
                )
            )
            .scalar()
        ) or 0

    def count_repos_by_date_and_app(self, fecha: str, aplicacion: str) -> int:
        """Count repositories for a specific date and application.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            aplicacion: Application name

        Returns:
            Number of repositories
        """
        return (
            self.session.query(func.count(func.distinct(Daily.repo)))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.aplicacion == aplicacion
                )
            )
            .scalar()
        ) or 0

    def sum_bugs_by_date_and_app(self, fecha: str, aplicacion: str) -> int:
        """Sum bugs for a specific date and application.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            aplicacion: Application name

        Returns:
            Total bugs
        """
        return (
            self.session.query(func.sum(Daily.num_bugs))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.aplicacion == aplicacion
                )
            )
            .scalar()
        ) or 0

    def sum_analisis_by_date_and_app(self, fecha: str, aplicacion: str) -> int:
        """Sum analysis count for a specific date and application.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            aplicacion: Application name

        Returns:
            Total analysis count
        """
        return (
            self.session.query(func.sum(Daily.num_analisis))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.aplicacion == aplicacion
                )
            )
            .scalar()
        ) or 0

    def sum_quality_by_date_and_app(self, fecha: str, aplicacion: str) -> int:
        """Sum quality gate count for a specific date and application.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            aplicacion: Application name

        Returns:
            Total quality gate count
        """
        return (
            self.session.query(func.sum(Daily.num_quality))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.aplicacion == aplicacion
                )
            )
            .scalar()
        ) or 0

    def count_aplicaciones_by_date_and_proveedor(self, fecha: str, proveedor: str) -> int:
        """Count applications for a specific date and provider.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            proveedor: Provider name

        Returns:
            Number of applications
        """
        return (
            self.session.query(func.count(func.distinct(Daily.aplicacion)))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.proveedor == proveedor
                )
            )
            .scalar()
        ) or 0

    def count_repos_by_date_and_proveedor(self, fecha: str, proveedor: str) -> int:
        """Count repositories for a specific date and provider.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            proveedor: Provider name

        Returns:
            Number of repositories
        """
        return (
            self.session.query(func.count(Daily.repo))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.proveedor == proveedor
                )
            )
            .scalar()
        ) or 0

    def sum_bugs_by_date_and_proveedor(self, fecha: str, proveedor: str) -> int:
        """Sum bugs for a specific date and provider.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            proveedor: Provider name

        Returns:
            Total bugs
        """
        return (
            self.session.query(func.sum(Daily.num_bugs))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.proveedor == proveedor
                )
            )
            .scalar()
        ) or 0

    def sum_analisis_by_date_and_proveedor(self, fecha: str, proveedor: str) -> int:
        """Sum analysis count for a specific date and provider.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            proveedor: Provider name

        Returns:
            Total analysis count
        """
        return (
            self.session.query(func.sum(Daily.num_analisis))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.proveedor == proveedor
                )
            )
            .scalar()
        ) or 0

    def sum_quality_by_date_and_proveedor(self, fecha: str, proveedor: str) -> int:
        """Sum quality gate count for a specific date and provider.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            proveedor: Provider name

        Returns:
            Total quality gate count
        """
        return (
            self.session.query(func.sum(Daily.num_quality))
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.proveedor == proveedor
                )
            )
            .scalar()
        ) or 0

    def get_quality_by_date_and_repo(self, fecha: str, aplicacion: str, repo: str) -> Optional[int]:
        """Get quality gate value for a specific date, application and repository.

        Args:
            fecha: Date string (format: YYYY-MM-DD)
            aplicacion: Application name
            repo: Repository name

        Returns:
            Quality gate value or None
        """
        result = (
            self.session.query(Daily.num_quality)
            .filter(
                and_(
                    Daily.created_on == fecha,
                    Daily.aplicacion == aplicacion,
                    Daily.repo == repo
                )
            )
            .first()
        )
        return result[0] if result else None
