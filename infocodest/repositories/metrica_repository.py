"""Repository for Metrica model operations.

This module provides data access methods for SonarQube metrics.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Query
from infocodest.models.metricas import Metrica
from infocodest.models.proveedor import Proveedor
from infocodest.repositories.base_repository import BaseRepository


class MetricaRepository(BaseRepository[Metrica]):
    """Repository for managing SonarQube metrics data.

    This repository provides methods to query and manipulate metrics data,
    including complex queries with joins and aggregations.
    """

    def __init__(self):
        """Initialize MetricaRepository."""
        super().__init__(Metrica)

    def get_by_repo(self, repo: str) -> Optional[Metrica]:
        """Get metrics for a specific repository.

        Args:
            repo: Repository name

        Returns:
            Metrica entity if found, None otherwise
        """
        return self.find_one(repo=repo)

    def get_by_aplicacion(self, aplicacion: str) -> List[Metrica]:
        """Get all metrics for a specific application.

        Args:
            aplicacion: Application name

        Returns:
            List of Metrica entities for the application
        """
        return self.filter_by(aplicacion=aplicacion)

    def get_distinct_aplicaciones(self) -> List[str]:
        """Get list of distinct application names.

        Returns:
            List of unique application names
        """
        result = (
            self.session.query(Metrica.aplicacion)
            .distinct()
            .all()
        )
        return [row[0] for row in result if row[0]]

    def get_metricas_with_provider(self) -> List[Tuple]:
        """Get all metrics with provider information joined.

        Returns:
            List of tuples containing metric and provider data
        """
        return (
            self.session.query(
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
            .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion)
            .order_by(desc(Metrica.fecha))
            .all()
        )

    def get_metricas_by_aplicacion_with_provider(self, aplicacion: str) -> List[Tuple]:
        """Get metrics for an application with provider information.

        Args:
            aplicacion: Application name

        Returns:
            List of tuples containing metric and provider data for the application
        """
        return (
            self.session.query(
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
            .join(Proveedor, Metrica.aplicacion == Proveedor.aplicacion)
            .filter(Metrica.aplicacion == aplicacion)
            .order_by(desc(Metrica.fecha))
            .all()
        )

    def get_metricas_by_repo_with_provider(self, aplicacion: str, repo: str) -> List[Tuple]:
        """Get metrics for a specific repository with provider information.

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            List of tuples containing metric and provider data for the repository
        """
        return (
            self.session.query(
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
            .join(Proveedor, Metrica.aplicacion == Proveedor.aplicacion)
            .filter(
                and_(
                    Metrica.aplicacion == aplicacion,
                    Metrica.repo == repo
                )
            )
            .order_by(desc(Metrica.fecha))
            .all()
        )

    def count_distinct_aplicaciones(self) -> int:
        """Count distinct applications.

        Returns:
            Number of unique applications
        """
        return (
            self.session.query(func.count(func.distinct(Metrica.aplicacion)))
            .scalar()
        ) or 0

    def count_repositorios(self) -> int:
        """Count total repositories.

        Returns:
            Total number of repositories
        """
        return self.session.query(func.count(Metrica.repo)).scalar() or 0

    def sum_bugs(self) -> int:
        """Sum all bugs across all metrics.

        Returns:
            Total number of bugs
        """
        return self.session.query(func.sum(Metrica.bugs)).scalar() or 0

    def count_by_aplicacion(self, aplicacion: str) -> int:
        """Count repositories for a specific application.

        Args:
            aplicacion: Application name

        Returns:
            Number of repositories for the application
        """
        return (
            self.session.query(func.count(func.distinct(Metrica.repo)))
            .filter(Metrica.aplicacion == aplicacion)
            .scalar()
        ) or 0

    def sum_bugs_by_aplicacion(self, aplicacion: str) -> int:
        """Sum bugs for a specific application.

        Args:
            aplicacion: Application name

        Returns:
            Total bugs for the application
        """
        return (
            self.session.query(func.sum(Metrica.bugs))
            .filter(Metrica.aplicacion == aplicacion)
            .scalar()
        ) or 0

    def count_aplicaciones_by_aplicacion(self, aplicacion: str) -> int:
        """Count applications for a specific application (returns 0 or 1).

        Args:
            aplicacion: Application name

        Returns:
            1 if application exists, 0 otherwise
        """
        return (
            self.session.query(func.count(func.distinct(Metrica.aplicacion)))
            .filter(Metrica.aplicacion == aplicacion)
            .scalar()
        ) or 0

    def count_aplicaciones_by_aplicacion_and_repo(self, aplicacion: str, repo: str) -> int:
        """Count applications for a specific application and repository (returns 0 or 1).

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            1 if application exists for the repository, 0 otherwise
        """
        return (
            self.session.query(func.count(func.distinct(Metrica.aplicacion)))
            .filter(
                and_(
                    Metrica.aplicacion == aplicacion,
                    Metrica.repo == repo
                )
            )
            .scalar()
        ) or 0

    def count_by_aplicacion_and_repo(self, aplicacion: str, repo: str) -> int:
        """Count repositories for a specific application and repository (returns 0 or 1).

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            1 if repository exists, 0 otherwise
        """
        return (
            self.session.query(func.count(Metrica.repo))
            .filter(
                and_(
                    Metrica.aplicacion == aplicacion,
                    Metrica.repo == repo
                )
            )
            .scalar()
        ) or 0

    def sum_bugs_by_aplicacion_and_repo(self, aplicacion: str, repo: str) -> int:
        """Sum bugs for a specific application and repository.

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            Total bugs for the repository
        """
        return (
            self.session.query(func.sum(Metrica.bugs))
            .filter(
                and_(
                    Metrica.aplicacion == aplicacion,
                    Metrica.repo == repo
                )
            )
            .scalar()
        ) or 0

    def get_repositorios_count_by_aplicacion(self) -> List[Tuple[str, int]]:
        """Get repository count grouped by application.

        Returns:
            List of tuples (aplicacion, num_repos) ordered by count descending,
            only including applications with more than 2 repositories
        """
        return (
            self.session.query(
                Metrica.aplicacion,
                func.count().label('NUM_REPO')
            )
            .group_by(Metrica.aplicacion)
            .having(func.count() > 2)
            .order_by(desc(func.count()))
            .all()
        )

    def count_by_proveedor(self, proveedor: str) -> int:
        """Count distinct applications for a provider.

        Args:
            proveedor: Provider name

        Returns:
            Number of applications for the provider
        """
        return (
            self.session.query(func.count(func.distinct(Metrica.aplicacion)))
            .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion)
            .filter(Proveedor.proveedor == proveedor)
            .scalar()
        ) or 0

    def count_repos_by_proveedor(self, proveedor: str) -> int:
        """Count repositories for a provider.

        Args:
            proveedor: Provider name

        Returns:
            Number of repositories for the provider
        """
        return (
            self.session.query(func.count(Metrica.repo))
            .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion)
            .filter(Proveedor.proveedor == proveedor)
            .scalar()
        ) or 0

    def sum_bugs_by_proveedor(self, proveedor: str) -> int:
        """Sum bugs for a provider.

        Args:
            proveedor: Provider name

        Returns:
            Total bugs for the provider
        """
        return (
            self.session.query(func.sum(Metrica.bugs))
            .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion)
            .filter(Proveedor.proveedor == proveedor)
            .scalar()
        ) or 0
