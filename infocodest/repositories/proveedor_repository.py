"""Repository for Proveedor model operations.

This module provides data access methods for provider (proveedor) data.
"""

from typing import List
from sqlalchemy import func
from infocodest.models.proveedor import Proveedor
from infocodest.models.metricas import Metrica
from infocodest.repositories.base_repository import BaseRepository


class ProveedorRepository(BaseRepository[Proveedor]):
    """Repository for managing provider data.

    This repository provides methods to query provider/supplier information
    associated with applications.
    """

    def __init__(self):
        """Initialize ProveedorRepository."""
        super().__init__(Proveedor)

    def get_by_aplicacion(self, aplicacion: str) -> Proveedor:
        """Get provider for a specific application.

        Args:
            aplicacion: Application name

        Returns:
            Proveedor entity if found, None otherwise
        """
        return self.find_one(aplicacion=aplicacion)

    def get_by_proveedor_name(self, proveedor: str) -> List[Proveedor]:
        """Get all applications for a specific provider.

        Args:
            proveedor: Provider name

        Returns:
            List of Proveedor entities for that provider
        """
        return self.filter_by(proveedor=proveedor)

    def get_distinct_proveedores(self) -> List[str]:
        """Get list of distinct provider names.

        Only returns providers that have associated metrics.

        Returns:
            List of unique provider names
        """
        result = (
            self.session.query(Proveedor.proveedor)
            .join(Metrica, Proveedor.aplicacion == Metrica.aplicacion)
            .with_entities(Proveedor.proveedor)
            .distinct()
            .all()
        )
        return [row[0] for row in result if row[0]]

    def get_all_with_tipo(self) -> List[Proveedor]:
        """Get all providers with their tipo (type) information.

        Returns:
            List of all Proveedor entities
        """
        return self.get_all()

    def count_aplicaciones_by_proveedor(self, proveedor: str) -> int:
        """Count applications for a specific provider.

        Args:
            proveedor: Provider name

        Returns:
            Number of applications for that provider
        """
        return self.count(proveedor=proveedor)
