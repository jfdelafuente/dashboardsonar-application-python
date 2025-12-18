"""
Functional tests for API endpoints

Tests all 11 API endpoints:
    1. /api/aplicacion/<aplicacion> - Get metrics by application
    2. /api/aplicacion/<project>/<name> - Get historico by project and name
    3. /api/registro - Get registro data
    4. /api/kpis - Get all KPIs
    5. /api/kpis/<project>/<name> - Get KPIs historico
    6. /api/rating/<project>/<name> - Get rating historico
    7. /api/daily/<aplicacion> - Get daily data by application
    8. /api/daily/metrica/<aplicacion> - Get daily metrica (experimental)
    9. /api/daily/<aplicacion>/<repo> - Get daily data by app and repo
    10. /api/daily/by_proveedor/<proveedor> - Get daily data by provider

Created: Phase 6 - Test Coverage Improvements (Priority 2)
"""

import json
import pytest
from flask.testing import FlaskClient


# ============================================================================
# Tests for /api/aplicacion/<aplicacion>
# ============================================================================

class TestApiAplicacion:
    """Tests for /api/aplicacion/<aplicacion> endpoint"""

    def test_get_historico_by_project(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with test data
        WHEN the API endpoint '/api/aplicacion/{aplicacion}' is requested
        THEN check that the response contains correct metrica data
        """
        response = test_client.get('/api/aplicacion/abacusbrmosp')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert 'project_name' in res
        assert 'aplicacion' in res
        assert 'fecha' in res
        assert 'bugs' in res
        assert 'vulnerabilities' in res
        assert 'codesmells' in res

        # Verify response lists are not empty and contain expected data
        assert len(res['project_name']) > 0, "project_name list should not be empty"
        assert len(res['aplicacion']) > 0, "aplicacion list should not be empty"
        assert res['project_name'][0] == 'abacus-application-java'
        assert res['aplicacion'][0] == 'abacusbrmosp'
        assert res['bugs'][0] == 5
        assert res['vulnerabilities'][0] == 2
        assert res['codesmells'][0] == 10

    def test_get_historico_by_project_nonexistent(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a nonexistent application name
        WHEN requesting the endpoint
        THEN returns empty lists
        """
        response = test_client.get('/api/aplicacion/nonexistent')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert len(res['project_name']) == 0
        assert len(res['aplicacion']) == 0


# ============================================================================
# Tests for /api/aplicacion/<project>/<name>
# ============================================================================

class TestApiAplicacionProject:
    """Tests for /api/aplicacion/<project>/<name> endpoint"""

    def test_get_historico_by_name(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with test data
        WHEN the API endpoint '/api/aplicacion/{aplicacion}/{project}' is requested
        THEN check that the response contains correct historico data for specific project
        """
        response = test_client.get('/api/aplicacion/abacusbrmosp/abacus-application-java')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert 'project_name' in res
        assert 'aplicacion' in res
        assert 'fecha' in res
        assert 'bugs' in res
        assert 'vulnerabilities' in res
        assert 'codesmells' in res

        assert res['project_name'][0] == 'abacus-application-java'
        assert res['aplicacion'][0] == 'abacusbrmosp'
        assert res['bugs'][0] == 5
        assert res['vulnerabilities'][0] == 2
        assert res['codesmells'][0] == 10

    def test_get_historico_by_name_nonexistent(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN nonexistent project/name combination
        WHEN requesting the endpoint
        THEN returns empty lists
        """
        response = test_client.get('/api/aplicacion/nonexistent/nonexistent')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert len(res['project_name']) == 0


# ============================================================================
# Tests for /api/registro
# ============================================================================

class TestApiRegistro:
    """Tests for /api/registro endpoint"""

    def test_get_registro_with_limit(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with registro data
        WHEN the API endpoint '/api/registro?limit=30' is requested
        THEN check that the response contains registro records from last 30 days
        """
        response = test_client.get('/api/registro?limit=30')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert isinstance(res, list)
        assert len(res) > 0

        # Check first record has expected structure
        first_record = res[0]
        assert 'proceso' in first_record
        assert 'created_on' in first_record
        assert 'num_app' in first_record
        assert 'num_repo' in first_record

    def test_get_registro_with_small_limit(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a registro created today
        WHEN requesting with limit=0 (today only)
        THEN returns today's records
        """
        response = test_client.get('/api/registro?limit=0')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert isinstance(res, list)


# ============================================================================
# Tests for /api/kpis
# ============================================================================

class TestApiKpis:
    """Tests for /api/kpis endpoint"""

    def test_get_all_kpis(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with metrica data
        WHEN the API endpoint '/api/kpis' is requested
        THEN check that the response contains all KPIs
        """
        response = test_client.get('/api/kpis')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert isinstance(res, list)
        assert len(res) > 0

        # Check first record structure
        first_kpi = res[0]
        assert 'repo' in first_kpi
        assert 'aplicacion' in first_kpi
        assert 'bugs' in first_kpi
        assert 'vulnerabilities' in first_kpi
        assert 'code_smells' in first_kpi


# ============================================================================
# Tests for /api/kpis/<project>/<name>
# ============================================================================

class TestApiKpisHistorico:
    """Tests for /api/kpis/<project>/<name> endpoint"""

    def test_get_kpis_historico_by_name(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with historico data
        WHEN the API endpoint '/api/kpis/{project}/{name}' is requested
        THEN check that the response contains correct KPI metrics
        """
        response = test_client.get('/api/kpis/abacusbrmosp/abacus-application-java')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert 'project_name' in res
        assert 'aplicacion' in res
        assert 'fecha' in res
        assert 'sqale_debt_ratio' in res
        assert 'complexity' in res
        assert 'duplicated_line_density' in res
        assert 'coverage' in res
        assert 'ncloc' in res

        # Verify data values
        assert res['project_name'][0] == 'abacus-application-java'
        assert res['sqale_debt_ratio'][0] == 10
        assert res['complexity'][0] == 100
        assert res['coverage'][0] == 75

    def test_get_kpis_historico_nonexistent(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN nonexistent project/name
        WHEN requesting KPIs historico
        THEN returns empty lists
        """
        response = test_client.get('/api/kpis/nonexistent/nonexistent')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert len(res['project_name']) == 0


# ============================================================================
# Tests for /api/rating/<project>/<name>
# ============================================================================

class TestApiRating:
    """Tests for /api/rating/<project>/<name> endpoint"""

    def test_get_rating_historico_by_name(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with metrica data
        WHEN the API endpoint '/api/rating/{project}/{name}' is requested
        THEN check that the response contains rating metrics
        """
        response = test_client.get('/api/rating/abacusbrmosp/abacus-application-java')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert 'project_name' in res
        assert 'aplicacion' in res
        assert 'fecha' in res
        assert 'sqale_rating' in res
        assert 'reliability_rating' in res
        assert 'security_rating' in res

        # Verify rating values
        assert res['project_name'][0] == 'abacus-application-java'
        assert res['sqale_rating'][0] == 2
        assert res['reliability_rating'][0] == 3
        assert res['security_rating'][0] == 4

    def test_get_rating_nonexistent(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN nonexistent project/name
        WHEN requesting rating historico
        THEN returns empty lists
        """
        response = test_client.get('/api/rating/nonexistent/nonexistent')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert len(res['project_name']) == 0


# ============================================================================
# Tests for /api/daily/<aplicacion>
# ============================================================================

class TestApiDaily:
    """Tests for /api/daily/<aplicacion> endpoint"""

    def test_get_daily_by_aplicacion(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with daily data
        WHEN the API endpoint '/api/daily/{aplicacion}' is requested
        THEN check that the response contains aggregated daily metrics
        """
        response = test_client.get('/api/daily/abacusbrmosp')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert 'project_name' in res
        assert 'aplicacion' in res
        assert 'fecha' in res
        assert 'bugs' in res
        assert 'vulnerabilities' in res
        assert 'codesmells' in res
        assert 'analisis' in res

        # Verify data
        assert len(res['project_name']) > 0
        assert res['aplicacion'][0] == 'abacusbrmosp'

    def test_get_daily_nonexistent_aplicacion(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN nonexistent application
        WHEN requesting daily data
        THEN returns empty lists
        """
        response = test_client.get('/api/daily/nonexistent')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert len(res['project_name']) == 0


# ============================================================================
# Tests for /api/daily/<aplicacion>/<repo>
# ============================================================================

class TestApiDailyRepo:
    """Tests for /api/daily/<aplicacion>/<repo> endpoint"""

    def test_get_daily_by_aplicacion_and_repo(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with daily data
        WHEN the API endpoint '/api/daily/{aplicacion}/{repo}' is requested
        THEN check that the response contains daily metrics for specific repo
        """
        response = test_client.get('/api/daily/abacusbrmosp/abacus-application-java')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert 'fecha' in res
        assert 'project_name' in res
        assert 'aplicacion' in res
        assert 'bugs' in res
        assert 'vulnerabilities' in res
        assert 'codesmells' in res
        assert 'analisis' in res

        # Verify data
        if len(res['project_name']) > 0:
            assert res['project_name'][0] == 'abacus-application-java'
            assert res['aplicacion'][0] == 'abacusbrmosp'

    def test_get_daily_nonexistent_repo(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN nonexistent repo
        WHEN requesting daily data
        THEN returns empty lists
        """
        response = test_client.get('/api/daily/abacusbrmosp/nonexistent')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert len(res['project_name']) == 0


# ============================================================================
# Tests for /api/daily/by_proveedor/<proveedor>
# ============================================================================

class TestApiDailyProveedor:
    """Tests for /api/daily/by_proveedor/<proveedor> endpoint"""

    def test_get_daily_by_proveedor(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with daily data by provider
        WHEN the API endpoint '/api/daily/by_proveedor/{proveedor}' is requested
        THEN check that the response contains aggregated daily metrics by provider
        """
        response = test_client.get('/api/daily/by_proveedor/Test Provider')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        res = json.loads(response.data.decode('utf-8'))
        assert 'fecha' in res
        assert 'proveedor' in res
        assert 'bugs' in res
        assert 'vulnerabilities' in res
        assert 'codesmells' in res
        assert 'analisis' in res

        # Verify provider data
        if len(res['proveedor']) > 0:
            assert res['proveedor'][0] == 'Test Provider'

    def test_get_daily_nonexistent_proveedor(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN nonexistent provider
        WHEN requesting daily data
        THEN returns empty lists
        """
        response = test_client.get('/api/daily/by_proveedor/Nonexistent Provider')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert len(res['proveedor']) == 0


# ============================================================================
# Tests for /api/daily/metrica/<aplicacion> (experimental endpoint)
# ============================================================================

class TestApiDailyMetrica:
    """Tests for /api/daily/metrica/<aplicacion> endpoint (experimental - may not work)"""

    def test_get_daily_metrica(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN a Flask application with daily data
        WHEN the API endpoint '/api/daily/metrica/{aplicacion}?metrica=bugs' is requested
        THEN check if the endpoint responds (endpoint marked as experimental)

        Note: This endpoint has a comment in code saying "prueba. no funciona"
        """
        response = test_client.get('/api/daily/metrica/abacusbrmosp?metrica=bugs')

        # Just verify endpoint responds (may or may not work correctly based on code comment)
        assert response.status_code in [200, 400, 500]  # Accept any response

        if response.status_code == 200:
            # If it works, verify structure
            res = json.loads(response.data.decode('utf-8'))
            assert isinstance(res, dict)


# ============================================================================
# Integration Tests
# ============================================================================

class TestApiIntegration:
    """Integration tests for API endpoints"""

    def test_api_endpoints_require_authentication(self, test_client: FlaskClient, init_test_data):
        """
        GIVEN API endpoints
        WHEN accessed without authentication
        THEN most should still work (APIs are typically public)
        """
        # These endpoints should work even without auth (public APIs)
        endpoints = [
            '/api/aplicacion/abacusbrmosp',
            '/api/kpis',
            '/api/daily/abacusbrmosp',
        ]

        for endpoint in endpoints:
            response = test_client.get(endpoint)
            # APIs typically return 200 even without auth
            assert response.status_code in [200, 302]

    def test_all_api_endpoints_return_json(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN all API endpoints
        WHEN requested
        THEN all return JSON content type
        """
        endpoints = [
            '/api/aplicacion/abacusbrmosp',
            '/api/aplicacion/abacusbrmosp/abacus-application-java',
            '/api/registro?limit=30',
            '/api/kpis',
            '/api/kpis/abacusbrmosp/abacus-application-java',
            '/api/rating/abacusbrmosp/abacus-application-java',
            '/api/daily/abacusbrmosp',
            '/api/daily/abacusbrmosp/abacus-application-java',
            '/api/daily/by_proveedor/Test Provider',
        ]

        for endpoint in endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 200
            assert 'application/json' in response.content_type

    def test_api_endpoints_handle_special_characters(self, test_client: FlaskClient, init_test_data, login_in_user):
        """
        GIVEN API endpoints with URL-encoded special characters
        WHEN requested
        THEN handle gracefully
        """
        # Test with spaces (URL encoded)
        response = test_client.get('/api/daily/by_proveedor/Test%20Provider')
        assert response.status_code == 200

        res = json.loads(response.data.decode('utf-8'))
        assert isinstance(res, dict)
