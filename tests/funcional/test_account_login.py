from flask.testing import FlaskClient
from flask_login import current_user


def test_correct_login(test_client: FlaskClient, init_database: None):
    # Ensure login behaves correctly with correct credentials
    response = test_client.post(
            "/login",
            data=dict(username="lolo", password="lolololo"),
            follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'INFOCODES - Home Page | Orange' in response.data
    assert current_user.is_authenticated


def test_incorrect_login(test_client: FlaskClient, init_database: None):
    # Ensure login behaves correctly with incorrect credentials
    response = test_client.post(
            "/login",
            data=dict(username="lolo", password="wrong_user"),
            follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Wrong user or password' in response.data


def test_valid_logout(test_client: FlaskClient, init_database: None):
    # Ensure logout behaves correctly
    response = test_client.post(
            "/login",
            data=dict(username="lolo", password="lolololo"),
            follow_redirects=True,
    )
    assert response.status_code == 200
    assert current_user.is_authenticated
    
    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert not current_user.is_authenticated


def test_login_already_logged(test_client: FlaskClient, init_database: None, login_in_user: None):
    # Ensure login behaves correctly with incorrect credentials
    response = test_client.post(
            "/login",
            data=dict(username="lolo", password="lolololo"),
            follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'INFOCODES - Home Page | Orange' in response.data
    assert current_user.is_authenticated


def test_correct_register(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST)
    THEN check the response is valid and the user is logged in
    """
    response = test_client.post("/register",
                                data=dict(username="test_user",
                                email="test_user@gmail.com",
                                password="test_user",
                                is_admin=False),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Register - Account created successfully.' in response.data


def test_user_already_register(test_client: FlaskClient, init_database: None):
    # Ensure login behaves correctly with incorrect credentials
    response = test_client.post("/register",
                                data=dict(username="lolo",
                                email="lolo@gmail",
                                password="lolololo",
                                is_admin=True),
                                follow_redirects=True,
                )
    assert response.status_code == 200
    assert b'Register - Username already registered' in response.data