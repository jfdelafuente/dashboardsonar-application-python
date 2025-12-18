"""
Functional tests for home view and main pages.

Updated: Priority 3 - Added pytest markers
"""

import pytest
from flask.testing import FlaskClient
from flask_login import current_user

# Mark all tests in this module as functional tests
pytestmark = pytest.mark.functional

# def test_home_page(test_client):
#     """
#     GIVEN a Flask application configured for testing
#     WHEN the '/' page is requested (GET)
#     THEN check that the response is valid
#     """
#     # response = test_client.get('/')
#     response = test_client.get("/", follow_redirects=True)
#     assert response.status_code == 200
#     assert b"Sonar CFM - Home Page | Orange" in response.data


# def test_home_page_post(test_client):
#     """
#     GIVEN a Flask application configured for testing
#     WHEN the '/' page is posted to (POST)
#     THEN check that a '405' (Method Not Allowed) status code is returned
#     """
#     response = test_client.post('/')
#     assert response.status_code == 405


def test_metricas_page(test_client: FlaskClient, init_database: None, login_in_user: None):
    """
    GIVEN a Flask application with authenticated user
    WHEN the '/metricas' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/metricas')
    assert response.status_code == 200
    # assert b"Sonar CFM - Metricas | Orange" in response.data

def test_metricas_page_login(test_client: FlaskClient, init_database: None, login_in_user: None):
    """
    GIVEN a Flask application with authenticated user
    WHEN the '/metricas' page is requested (GET) with login
    THEN check that the response is valid
    """
    response = test_client.get('/metricas')
    assert response.status_code == 200
    # assert b"Sonar CFM - Metricas | Orange" in response.data


def test_proveedores_metricas_page(test_client: FlaskClient, init_database: None, login_in_user: None):
    """
    GIVEN a Flask application with authenticated user
    WHEN the '/metricas/proveedores' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/metricas/proveedores')
    assert response.status_code == 200
    # assert b"Sonar CFM - Proveedores Metricas | Orange" in response.data


def test_historico_metricas_page(test_client: FlaskClient, init_database: None, login_in_user: None, init_test_data: None):
    """
    GIVEN a Flask application with authenticated user and test data
    WHEN the '/metricas/aplicacion' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/metricas/aplicacion')
    assert response.status_code == 200
    # assert b"Sonar CFM - Historico Metricas | Orange" in response.data