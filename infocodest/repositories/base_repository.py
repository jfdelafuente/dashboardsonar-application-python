"""Base repository for generic CRUD operations.

This module provides a generic repository pattern implementation that can be
used as a base class for domain-specific repositories.
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from infocodest.extensions import db

# Type variable for the model class
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Generic repository providing basic CRUD operations.

    This class implements the Repository pattern for data access, providing
    a clean abstraction over SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class for this repository
        session: The database session (defaults to Flask-SQLAlchemy db.session)

    Example:
        >>> from infocodest.models.metricas import Metrica
        >>> from infocodest.repositories.base_repository import BaseRepository
        >>>
        >>> class MetricaRepository(BaseRepository[Metrica]):
        >>>     def __init__(self):
        >>>         super().__init__(Metrica)
        >>>
        >>> repo = MetricaRepository()
        >>> metrica = repo.get_by_id(1)
    """

    def __init__(self, model: type[T], session: Optional[Session] = None):
        """Initialize repository with a model class.

        Args:
            model: The SQLAlchemy model class for this repository
            session: Optional database session. If None, uses Flask-SQLAlchemy's db.session
        """
        self.model = model
        self.session = session or db.session

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The primary key of the entity

        Returns:
            The entity if found, None otherwise
        """
        return self.session.query(self.model).get(entity_id)

    def get_all(self) -> List[T]:
        """Retrieve all entities.

        Returns:
            List of all entities
        """
        return self.session.query(self.model).all()

    def filter_by(self, **kwargs: Any) -> List[T]:
        """Filter entities by column values.

        Args:
            **kwargs: Column name and value pairs to filter by

        Returns:
            List of matching entities

        Example:
            >>> repo.filter_by(aplicacion='myapp', bugs=0)
        """
        return self.session.query(self.model).filter_by(**kwargs).all()

    def find_one(self, **kwargs: Any) -> Optional[T]:
        """Find a single entity by column values.

        Args:
            **kwargs: Column name and value pairs to filter by

        Returns:
            The first matching entity or None

        Example:
            >>> repo.find_one(repo='my-repo', aplicacion='myapp')
        """
        return self.session.query(self.model).filter_by(**kwargs).first()

    def create(self, entity: T) -> T:
        """Create a new entity.

        Args:
            entity: The entity to create

        Returns:
            The created entity with any generated fields populated

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        try:
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            return entity
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def create_many(self, entities: List[T]) -> List[T]:
        """Create multiple entities in a single transaction.

        Args:
            entities: List of entities to create

        Returns:
            List of created entities

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        try:
            self.session.add_all(entities)
            self.session.commit()
            for entity in entities:
                self.session.refresh(entity)
            return entities
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def update(self, entity: T) -> T:
        """Update an existing entity.

        Args:
            entity: The entity to update

        Returns:
            The updated entity

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        try:
            self.session.merge(entity)
            self.session.commit()
            return entity
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def delete(self, entity: T) -> None:
        """Delete an entity.

        Args:
            entity: The entity to delete

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        try:
            self.session.delete(entity)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def delete_by_id(self, entity_id: int) -> bool:
        """Delete an entity by its ID.

        Args:
            entity_id: The primary key of the entity to delete

        Returns:
            True if entity was deleted, False if not found

        Raises:
            SQLAlchemyError: If the database operation fails
        """
        entity = self.get_by_id(entity_id)
        if entity:
            self.delete(entity)
            return True
        return False

    def count(self, **kwargs: Any) -> int:
        """Count entities matching the given criteria.

        Args:
            **kwargs: Column name and value pairs to filter by

        Returns:
            Number of matching entities

        Example:
            >>> total = repo.count()
            >>> active_count = repo.count(alert_status='OK')
        """
        query = self.session.query(self.model)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query.count()

    def exists(self, **kwargs: Any) -> bool:
        """Check if any entity matches the given criteria.

        Args:
            **kwargs: Column name and value pairs to filter by

        Returns:
            True if at least one matching entity exists, False otherwise

        Example:
            >>> if repo.exists(repo='my-repo'):
            >>>     print("Repository exists")
        """
        return self.count(**kwargs) > 0

    def paginate(self, page: int = 1, per_page: int = 20, **kwargs: Any) -> Dict[str, Any]:
        """Paginate entities with optional filtering.

        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            **kwargs: Column name and value pairs to filter by

        Returns:
            Dictionary with pagination info:
                - items: List of entities for the current page
                - total: Total number of matching entities
                - page: Current page number
                - per_page: Items per page
                - pages: Total number of pages

        Example:
            >>> result = repo.paginate(page=2, per_page=10, aplicacion='myapp')
            >>> print(f"Page {result['page']} of {result['pages']}")
            >>> for item in result['items']:
            >>>     print(item)
        """
        query = self.session.query(self.model)
        if kwargs:
            query = query.filter_by(**kwargs)

        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page  # Ceiling division
        }
