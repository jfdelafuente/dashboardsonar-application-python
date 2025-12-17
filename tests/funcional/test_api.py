import json


def test_get_historico_by_project(test_client, init_test_data, login_in_user):
    """
    GIVEN a Flask application with test data
    WHEN the API endpoint '/api/aplicacion/{aplicacion}' is requested
    THEN check that the response contains correct historico data
    """
    response = test_client.get('/api/aplicacion/abacusbrmosp')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

    res = json.loads(response.data.decode('utf-8'))
    assert 'project_name' in res
    assert 'aplicacion' in res
    # Verify response lists are not empty and contain expected data
    assert len(res['project_name']) > 0, "project_name list should not be empty"
    assert len(res['aplicacion']) > 0, "aplicacion list should not be empty"
    assert res['project_name'][0] == 'abacus-application-java'
    assert res['aplicacion'][0] == 'abacusbrmosp'


def test_get_historico_by_name(test_client, init_test_data, login_in_user):
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
    assert res['project_name'][0] == 'abacus-application-java'
    assert res['aplicacion'][0] == 'abacusbrmosp'


def test_get_repos(test_client, init_test_data, login_in_user):
    """
    GIVEN a Flask application with test data
    WHEN the API endpoint '/api/charts_data' is requested
    THEN check that the response is valid JSON with chart data
    """
    response = test_client.get('/api/charts_data')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

    res = json.loads(response.data.decode('utf-8'))
    # Verify response has expected structure
    assert isinstance(res, dict)
    # assert 'labels' in res
    # assert 'values' in res