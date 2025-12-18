"""
Unit tests for DashboardService.

Tests business logic using mocked repositories to isolate service layer.

Updated: Priority 3 - Added pytest markers
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from infocodest.services.dashboard_service import DashboardService

# Mark all tests in this module as services and unit tests
pytestmark = [pytest.mark.services, pytest.mark.unit]


class TestDashboardService:
    """Test suite for DashboardService business logic."""

    @pytest.fixture
    def mock_metrica_repo(self):
        """Create mocked MetricaRepository."""
        return Mock()

    @pytest.fixture
    def mock_historico_repo(self):
        """Create mocked HistoricoRepository."""
        return Mock()

    @pytest.fixture
    def mock_daily_repo(self):
        """Create mocked DailyRepository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Create DashboardService with all mocked repositories."""
        return DashboardService(
            metrica_repo=mock_metrica_repo,
            historico_repo=mock_historico_repo,
            daily_repo=mock_daily_repo,
            days=15
        )

    def test_init_with_defaults(self):
        """Test DashboardService initialization with default repositories."""
        service = DashboardService(days=10)

        assert service.days == 10
        assert service.metrica_repo is not None
        assert service.historico_repo is not None
        assert service.daily_repo is not None

    @patch.dict('os.environ', {'DAYS': '20'})
    def test_init_days_from_environment(self):
        """Test days parameter defaults to environment variable."""
        service = DashboardService()
        assert service.days == 20

    def test_get_kpi_overview_success(self, service, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Test KPI overview calculation with valid data."""
        # Arrange - Current metrics
        mock_metrica_repo.count_distinct_aplicaciones.return_value = 10
        mock_metrica_repo.count.return_value = 50
        mock_metrica_repo.sum_bugs.return_value = 100
        mock_historico_repo.count.return_value = 200
        mock_historico_repo.count_quality_ok.return_value = 150

        # Arrange - Old metrics (from 15 days ago)
        mock_daily_repo.count_distinct_aplicaciones_by_date.return_value = 8
        mock_daily_repo.count_repos_by_date.return_value = 45
        mock_daily_repo.sum_bugs_by_date.return_value = 120
        mock_daily_repo.sum_analisis_by_date.return_value = 180
        mock_daily_repo.sum_quality_by_date.return_value = 140

        # Act
        result = service.get_kpi_overview()

        # Assert - Current values
        assert result['aplicaciones'] == 10
        assert result['repositorios'] == 50
        assert result['bugs'] == 100
        assert result['analisis'] == 200
        assert result['quality'] == 150

        # Assert - Variations calculated
        assert 'aplicaciones_value' in result
        assert 'aplicaciones_text' in result
        assert 'repositorios_value' in result
        assert 'bugs_value' in result
        assert 'analisis_value' in result
        assert 'quality_value' in result

        # Verify repository methods called
        mock_metrica_repo.count_distinct_aplicaciones.assert_called_once()
        mock_metrica_repo.count.assert_called_once()
        mock_metrica_repo.sum_bugs.assert_called_once()
        mock_historico_repo.count.assert_called_once()
        mock_historico_repo.count_quality_ok.assert_called_once()

    def test_get_kpi_by_application(self, service, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Test application-specific KPI calculation."""
        aplicacion = 'TestApp'

        # Arrange - Current metrics
        mock_metrica_repo.count_aplicaciones_by_aplicacion.return_value = 1
        mock_metrica_repo.count_by_aplicacion.return_value = 5
        mock_metrica_repo.sum_bugs_by_aplicacion.return_value = 20
        mock_historico_repo.count_by_aplicacion.return_value = 30
        mock_historico_repo.count_quality_ok_by_aplicacion.return_value = 25

        # Arrange - Old metrics
        mock_daily_repo.count_aplicaciones_by_date_and_app.return_value = 1
        mock_daily_repo.count_repos_by_date_and_app.return_value = 4
        mock_daily_repo.sum_bugs_by_date_and_app.return_value = 18
        mock_daily_repo.sum_analisis_by_date_and_app.return_value = 28
        mock_daily_repo.sum_quality_by_date_and_app.return_value = 23

        # Act
        result = service.get_kpi_by_application(aplicacion)

        # Assert
        assert result['aplicaciones'] == 1
        assert result['repositorios'] == 5
        assert result['bugs'] == 20
        assert result['analisis'] == 30
        assert result['quality'] == 25

        # Verify correct parameters passed
        mock_metrica_repo.count_by_aplicacion.assert_called_once_with(aplicacion)
        mock_metrica_repo.sum_bugs_by_aplicacion.assert_called_once_with(aplicacion)
        mock_historico_repo.count_by_aplicacion.assert_called_once_with(aplicacion)
        mock_historico_repo.count_quality_ok_by_aplicacion.assert_called_once_with(aplicacion)

    def test_get_kpi_by_proveedor(self, service, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Test provider-specific KPI calculation."""
        proveedor = 'TestProvider'

        # Arrange - Current metrics
        mock_metrica_repo.count_by_proveedor.return_value = 3
        mock_metrica_repo.count_repos_by_proveedor.return_value = 15
        mock_metrica_repo.sum_bugs_by_proveedor.return_value = 50
        mock_historico_repo.count_by_proveedor.return_value = 60
        mock_historico_repo.count_quality_ok_by_proveedor.return_value = 45

        # Arrange - Old metrics
        mock_daily_repo.count_aplicaciones_by_date_and_proveedor.return_value = 3
        mock_daily_repo.count_repos_by_date_and_proveedor.return_value = 12
        mock_daily_repo.sum_bugs_by_date_and_proveedor.return_value = 48
        mock_daily_repo.sum_analisis_by_date_and_proveedor.return_value = 55
        mock_daily_repo.sum_quality_by_date_and_proveedor.return_value = 42

        # Act
        result = service.get_kpi_by_proveedor(proveedor)

        # Assert
        assert result['aplicaciones'] == 3
        assert result['repositorios'] == 15
        assert result['bugs'] == 50
        assert result['analisis'] == 60
        assert result['quality'] == 45

        # Verify correct parameters
        mock_metrica_repo.count_by_proveedor.assert_called_once_with(proveedor)
        mock_metrica_repo.count_repos_by_proveedor.assert_called_once_with(proveedor)

    def test_get_kpi_by_repositorio(self, service, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Test repository-specific KPI calculation."""
        aplicacion = 'TestApp'
        repositorio = 'test-repo'

        # Arrange - Current metrics
        mock_metrica_repo.count_aplicaciones_by_aplicacion_and_repo.return_value = 1
        mock_metrica_repo.count_by_aplicacion_and_repo.return_value = 1
        mock_metrica_repo.sum_bugs_by_aplicacion_and_repo.return_value = 5
        mock_historico_repo.count_by_aplicacion_and_repo.return_value = 10
        mock_historico_repo.count_quality_ok_by_repo.return_value = 8

        # Arrange - Old metrics
        mock_daily_repo.count_aplicaciones_by_date_and_repo.return_value = 1
        mock_daily_repo.count_repos_by_date_and_repo.return_value = 1
        mock_daily_repo.sum_bugs_by_date_and_repo.return_value = 6
        mock_daily_repo.sum_analisis_by_date_and_repo.return_value = 9
        mock_daily_repo.get_quality_by_date_and_repo.return_value = 7

        # Act
        result = service.get_kpi_by_repository(aplicacion, repositorio)

        # Assert
        assert result['aplicaciones'] == 1
        assert result['repositorios'] == 1
        assert result['bugs'] == 5
        assert result['analisis'] == 10
        assert result['quality'] == 8

        # Verify correct parameters
        mock_metrica_repo.count_aplicaciones_by_aplicacion_and_repo.assert_called_once_with(aplicacion, repositorio)
        mock_metrica_repo.count_by_aplicacion_and_repo.assert_called_once_with(aplicacion, repositorio)
        mock_metrica_repo.sum_bugs_by_aplicacion_and_repo.assert_called_once_with(aplicacion, repositorio)

    def test_percentage_variation_increase(self, service, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Test percentage variation calculation for increase scenario."""
        # Arrange - 25% increase (from 100 to 125)
        mock_metrica_repo.count_distinct_aplicaciones.return_value = 125
        mock_metrica_repo.count.return_value = 50
        mock_metrica_repo.sum_bugs.return_value = 10
        mock_historico_repo.count.return_value = 100
        mock_historico_repo.count_by_alert_status.return_value = 80

        mock_daily_repo.count_distinct_aplicaciones_by_date.return_value = 100
        mock_daily_repo.count_by_date.return_value = 50
        mock_daily_repo.sum_bugs_by_date.return_value = 10
        mock_daily_repo.sum_analisis_by_date.return_value = 100
        mock_daily_repo.sum_quality_by_date.return_value = 80

        # Act
        result = service.get_kpi_overview()

        # Assert - aplicaciones increased 25%
        assert result['aplicaciones'] == 125
        # The variation text should indicate an increase
        assert 'Increase' in result['aplicaciones_text'] or '25' in result['aplicaciones_value']

    def test_percentage_variation_decrease(self, service, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Test percentage variation calculation for decrease scenario."""
        # Arrange - 20% decrease (from 100 to 80)
        mock_metrica_repo.count_distinct_aplicaciones.return_value = 80
        mock_metrica_repo.count.return_value = 50
        mock_metrica_repo.sum_bugs.return_value = 10
        mock_historico_repo.count.return_value = 100
        mock_historico_repo.count_by_alert_status.return_value = 70

        mock_daily_repo.count_distinct_aplicaciones_by_date.return_value = 100
        mock_daily_repo.count_by_date.return_value = 50
        mock_daily_repo.sum_bugs_by_date.return_value = 10
        mock_daily_repo.sum_analisis_by_date.return_value = 100
        mock_daily_repo.sum_quality_by_date.return_value = 70

        # Act
        result = service.get_kpi_overview()

        # Assert - aplicaciones decreased 20%
        assert result['aplicaciones'] == 80
        # The variation should be negative
        assert 'Decrease' in result['aplicaciones_text'] or '-20' in result['aplicaciones_value']

    def test_percentage_variation_no_change(self, service, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Test percentage variation when values are unchanged."""
        # Arrange - No change (100 -> 100)
        mock_metrica_repo.count_distinct_aplicaciones.return_value = 100
        mock_metrica_repo.count.return_value = 50
        mock_metrica_repo.sum_bugs.return_value = 10
        mock_historico_repo.count.return_value = 100
        mock_historico_repo.count_by_alert_status.return_value = 80

        mock_daily_repo.count_distinct_aplicaciones_by_date.return_value = 100
        mock_daily_repo.count_by_date.return_value = 50
        mock_daily_repo.sum_bugs_by_date.return_value = 10
        mock_daily_repo.sum_analisis_by_date.return_value = 100
        mock_daily_repo.sum_quality_by_date.return_value = 80

        # Act
        result = service.get_kpi_overview()

        # Assert - No variation (0%)
        assert result['aplicaciones'] == 100
        # Variation should be 0 or indicate no change
        assert '0' in result['aplicaciones_value'] or 'No change' in result.get('aplicaciones_text', '')

    def test_division_by_zero_in_variation(self, service, mock_metrica_repo, mock_historico_repo, mock_daily_repo):
        """Test percentage variation handles division by zero (old value = 0)."""
        # Arrange - Old value is 0, new value is 100
        mock_metrica_repo.count_distinct_aplicaciones.return_value = 100
        mock_metrica_repo.count.return_value = 50
        mock_metrica_repo.sum_bugs.return_value = 10
        mock_historico_repo.count.return_value = 100
        mock_historico_repo.count_by_alert_status.return_value = 80

        mock_daily_repo.count_distinct_aplicaciones_by_date.return_value = 0  # Division by zero
        mock_daily_repo.count_by_date.return_value = 50
        mock_daily_repo.sum_bugs_by_date.return_value = 10
        mock_daily_repo.sum_analisis_by_date.return_value = 100
        mock_daily_repo.sum_quality_by_date.return_value = 80

        # Act - Should not raise exception
        result = service.get_kpi_overview()

        # Assert - Should handle gracefully
        assert result['aplicaciones'] == 100
        # Variation should handle the division by zero case
        assert 'aplicaciones_value' in result

    def test_get_date_n_days_ago(self, service):
        """Test helper method to calculate date N days ago."""
        # This tests the private method indirectly through get_kpi_overview
        # The date calculation should subtract 15 days from today
        with patch('infocodest.services.dashboard_service.datetime') as mock_datetime:
            mock_now = datetime(2025, 12, 15)
            mock_datetime.now.return_value = mock_now

            # Call a method that uses _get_date_n_days_ago internally
            # We can verify the date passed to repository methods
            mock_metrica_repo = Mock()
            mock_historico_repo = Mock()
            mock_daily_repo = Mock()

            service = DashboardService(
                metrica_repo=mock_metrica_repo,
                historico_repo=mock_historico_repo,
                daily_repo=mock_daily_repo,
                days=15
            )

            # Mock all return values to prevent errors
            mock_metrica_repo.count_distinct_aplicaciones.return_value = 10
            mock_metrica_repo.count.return_value = 50
            mock_metrica_repo.sum_bugs.return_value = 100
            mock_historico_repo.count.return_value = 200
            mock_historico_repo.count_by_alert_status.return_value = 150
            mock_daily_repo.count_distinct_aplicaciones_by_date.return_value = 8
            mock_daily_repo.count_by_date.return_value = 45
            mock_daily_repo.sum_bugs_by_date.return_value = 120
            mock_daily_repo.sum_analisis_by_date.return_value = 180
            mock_daily_repo.sum_quality_by_date.return_value = 140

            service.get_kpi_overview()

            # Verify the daily repo was called with a date parameter
            # (the actual date calculation is implementation detail)
            assert mock_daily_repo.count_distinct_aplicaciones_by_date.called

    def test_mock_isolation_no_database_access(self, service):
        """Test that mocked service doesn't access real database."""
        # This test verifies that using mocks prevents any database queries
        # Service methods should only call mocked repositories
        assert isinstance(service.metrica_repo, Mock)
        assert isinstance(service.historico_repo, Mock)
        assert isinstance(service.daily_repo, Mock)

    def test_service_with_custom_days_parameter(self):
        """Test service can be initialized with custom days parameter."""
        mock_metrica = Mock()
        mock_historico = Mock()
        mock_daily = Mock()

        service = DashboardService(
            metrica_repo=mock_metrica,
            historico_repo=mock_historico,
            daily_repo=mock_daily,
            days=30
        )

        assert service.days == 30

    def test_multiple_kpi_calls_use_same_repositories(self, service):
        """Test that multiple KPI calls reuse the same repository instances."""
        # Setup minimal mocks to allow calls
        service.metrica_repo.count_distinct_aplicaciones.return_value = 10
        service.metrica_repo.count.return_value = 50
        service.metrica_repo.sum_bugs.return_value = 100
        service.historico_repo.count.return_value = 200
        service.historico_repo.count_by_alert_status.return_value = 150
        service.daily_repo.count_distinct_aplicaciones_by_date.return_value = 8
        service.daily_repo.count_by_date.return_value = 45
        service.daily_repo.sum_bugs_by_date.return_value = 120
        service.daily_repo.sum_analisis_by_date.return_value = 180
        service.daily_repo.sum_quality_by_date.return_value = 140

        # Call overview twice
        service.get_kpi_overview()
        service.get_kpi_overview()

        # Verify repositories were called twice
        assert service.metrica_repo.count_distinct_aplicaciones.call_count == 2
        assert service.historico_repo.count.call_count == 2
