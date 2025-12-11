"""Service for metrics and repository aggregation queries.

This module provides business logic for querying and aggregating SonarQube
metrics data, including repository counts by application.
"""

from typing import List, Tuple, Optional

from infocodest.repositories.metrica_repository import MetricaRepository


class MetricaService:
    """Service for metrics queries and repository aggregations.

    This service handles business logic for:
    - Repository counts by application
    - Applications with multiple repositories
    - Metrics aggregation and filtering

    Migrated from: models/database.py::getRepositorios()
    """

    def __init__(self, metrica_repo: Optional[MetricaRepository] = None):
        """Initialize MetricaService with repository dependencies.

        Args:
            metrica_repo: Repository for metrics data (default: new instance)
        """
        self.metrica_repo = metrica_repo or MetricaRepository()

    def get_applications_with_multiple_repos(
        self,
        min_repos: int = 2,
        order_by_count: bool = True
    ) -> List[Tuple[str, int]]:
        """Get applications that have more than a minimum number of repositories.

        This method is useful for identifying applications with multiple repositories
        for aggregated reporting and charts.

        Args:
            min_repos: Minimum number of repositories required (default: 2)
            order_by_count: Order results by repository count descending (default: True)

        Returns:
            List of tuples (aplicacion, repo_count) sorted by count descending
            Example: [('my-app', 15), ('other-app', 8), ('third-app', 3)]

        Migrated from: models/database.py::getRepositorios()
        """
        results = self.metrica_repo.get_repo_count_by_aplicacion(
            min_count=min_repos,
            order_by_count=order_by_count
        )

        # Convert Row objects to tuples for backwards compatibility
        return [(row.aplicacion, row.num_repo) for row in results]

    def get_all_applications_with_repo_counts(self) -> List[Tuple[str, int]]:
        """Get all applications with their repository counts.

        Returns:
            List of tuples (aplicacion, repo_count) for all applications

        Example:
            >>> service = MetricaService()
            >>> service.get_all_applications_with_repo_counts()
            [('app1', 5), ('app2', 1), ('app3', 12)]
        """
        results = self.metrica_repo.get_repo_count_by_aplicacion(
            min_count=1,
            order_by_count=True
        )

        return [(row.aplicacion, row.num_repo) for row in results]

    def get_applications_with_min_repos(self, min_repos: int) -> List[str]:
        """Get list of application names that have at least min_repos repositories.

        Args:
            min_repos: Minimum number of repositories required

        Returns:
            List of application names

        Example:
            >>> service = MetricaService()
            >>> service.get_applications_with_min_repos(5)
            ['my-app', 'other-app']
        """
        results = self.metrica_repo.get_repo_count_by_aplicacion(
            min_count=min_repos,
            order_by_count=False
        )

        return [row.aplicacion for row in results]
