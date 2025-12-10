import json


def test_get_historico_by_project(test_client):
    response = test_client.get('/api/aplicacion/abacusbrmosp')
    res = json.loads(response.data.decode('utf-8'))
    print(res)
    assert res['project_name'][0] == 'abacus-application-java'
    assert res['aplicacion'][0] == 'abacusbrmosp'
    assert response.status_code == 200


def test_get_historico_by_name(test_client):
    response = test_client.get('/api/aplicacion/abacusbrmosp/abacus-application-java')
    res = json.loads(response.data.decode('utf-8'))
    print(res)
    assert res['project_name'][0] == 'abacus-application-java'
    assert res['aplicacion'][0] == 'abacusbrmosp'
    assert response.status_code == 200
    
    
def test_get_repos(test_client):
    response = test_client.get('/api/charts_data')
    res = json.loads(response.data.decode('utf-8'))
    print(res)
    # assert res['labels'] == 1
    # assert res['values'] == 'Havard'
    assert response.status_code == 200