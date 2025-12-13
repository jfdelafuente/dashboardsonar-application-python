"""Repository layer for data access operations.

This package implements the Repository Pattern, providing a clean abstraction
over SQLAlchemy database operations. Each repository encapsulates data access
logic for a specific domain model.

Example usage:
    >>> from infocodest.repositories import MetricaRepository
    >>> repo = MetricaRepository()
    >>> metricas = repo.get_by_aplicacion('my-app')
"""

from .base_repository import BaseRepository
from .metrica_repository import MetricaRepository
from .historico_repository import HistoricoRepository
from .daily_repository import DailyRepository
from .proveedor_repository import ProveedorRepository
from .user_repository import UserRepository

__all__ = [
    'BaseRepository',
    'MetricaRepository',
    'HistoricoRepository',
    'DailyRepository',
    'ProveedorRepository',
    'UserRepository',
]
