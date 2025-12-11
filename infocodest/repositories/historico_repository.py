"""Repository for Historico model operations.

This module provides data access methods for historical SonarQube analysis data.
"""

from typing import List
from sqlalchemy import func, and_
from infocodest.models.historico import Historico
from infocodest.models.proveedor import Proveedor
from infocodest.repositories.base_repository import BaseRepository


class HistoricoRepository(BaseRepository[Historico]):
    """Repository for managing historical analysis data.

    This repository provides methods to query historical SonarQube analysis records.
    """

    def __init__(self):
        """Initialize HistoricoRepository."""
        super().__init__(Historico)

    def get_by_aplicacion(self, aplicacion: str) -> List[Historico]:
        """Get all historical records for a specific application.

        Args:
            aplicacion: Application name

        Returns:
            List of Historico entities for the application
        """
        return self.filter_by(aplicacion=aplicacion)

    def get_by_repo(self, repo: str) -> List[Historico]:
        """Get all historical records for a specific repository.

        Args:
            repo: Repository name

        Returns:
            List of Historico entities for the repository
        """
        return self.filter_by(repo=repo)

    def count_all(self) -> int:
        """Count total number of historical analysis records.

        Returns:
            Total count of Historico records
        """
        return self.count()

    def count_by_aplicacion(self, aplicacion: str) -> int:
        """Count historical records for a specific application.

        Args:
            aplicacion: Application name

        Returns:
            Count of records for the application
        """
        return self.count(aplicacion=aplicacion)

    def count_by_aplicacion_and_repo(self, aplicacion: str, repo: str) -> int:
        """Count historical records for a specific repository in an application.

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            Count of records for the repository
        """
        return (
            self.session.query(func.count(Historico.id))
            .filter(
                and_(
                    Historico.aplicacion == aplicacion,
                    Historico.repo == repo
                )
            )
            .scalar()
        ) or 0

    def count_quality_ok(self) -> int:
        """Count records with quality gate status OK.

        Returns:
            Number of records with alert_status='OK'
        """
        return self.count(alert_status='OK')

    def count_quality_ok_by_aplicacion(self, aplicacion: str) -> int:
        """Count records with quality gate OK for a specific application.

        Args:
            aplicacion: Application name

        Returns:
            Number of OK quality gates for the application
        """
        return (
            self.session.query(func.count(Historico.alert_status))
            .filter(
                and_(
                    Historico.alert_status == 'OK',
                    Historico.aplicacion == aplicacion
                )
            )
            .scalar()
        ) or 0

    def count_quality_ok_by_repo(self, aplicacion: str, repo: str) -> int:
        """Count records with quality gate OK for a specific repository.

        Args:
            aplicacion: Application name
            repo: Repository name

        Returns:
            Number of OK quality gates for the repository
        """
        return (
            self.session.query(func.count(Historico.alert_status))
            .filter(
                and_(
                    Historico.alert_status == 'OK',
                    Historico.aplicacion == aplicacion,
                    Historico.repo == repo
                )
            )
            .scalar()
        ) or 0

    def count_by_proveedor(self, proveedor: str) -> int:
        """Count historical records for a provider.

        Args:
            proveedor: Provider name

        Returns:
            Count of records for the provider
        """
        return (
            self.session.query(func.count(Historico.id))
            .join(Proveedor, Proveedor.aplicacion == Historico.aplicacion)
            .filter(Proveedor.proveedor == proveedor)
            .scalar()
        ) or 0

    def count_quality_ok_by_proveedor(self, proveedor: str) -> int:
        """Count records with quality gate OK for a provider.

        Args:
            proveedor: Provider name

        Returns:
            Number of OK quality gates for the provider
        """
        return (
            self.session.query(func.count(Historico.alert_status))
            .join(Proveedor, Proveedor.aplicacion == Historico.aplicacion)
            .filter(
                and_(
                    Historico.alert_status == 'OK',
                    Proveedor.proveedor == proveedor
                )
            )
            .scalar()
        ) or 0
