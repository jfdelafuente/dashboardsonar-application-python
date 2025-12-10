from flask.testing import FlaskClient


def test_home_page_requires_login(test_client: FlaskClient):
    response = test_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data
    assert b"INFOCODE - Login | Orange" in response.data

def test_login_page(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Username' in response.data
    assert b'Password' in response.data
    assert b"INFOCODE - Login | Orange" in response.data

def test_register_page(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/register')
    assert response.status_code == 200
    assert b'Username' in response.data
    assert b'Password' in response.data
    assert b'Email' in response.data
    
def test_password_page(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/password' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/password')
    assert response.status_code == 200
    assert b'Password' in response.data

def test_logout_page_requires_login(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data
    assert b"INFOCODE - Login | Orange" in response.data