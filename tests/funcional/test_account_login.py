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


def test_correct_register(test_client: FlaskClient, init_database: None):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST)
    THEN check the response is valid and the user is logged in
    """
    import time
    # Use timestamp to ensure unique username on each test run
    unique_username = f"test_user_{int(time.time() * 1000)}"
    unique_email = f"{unique_username}@gmail.com"

    response = test_client.post("/register",
                                data=dict(username=unique_username,
                                email=unique_email,
                                password="test_user_password",
                                confirm_password="test_user_password",
                                is_admin=False),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Account created successfully.' in response.data


def test_user_already_register(test_client: FlaskClient, init_database: None):
    """
    GIVEN a Flask application with an existing user 'lolo'
    WHEN trying to register with the same username
    THEN check that the appropriate error message is shown
    """
    response = test_client.post("/register",
                                data=dict(username="lolo",
                                email="lolo_new@gmail.com",  # Different email but same username
                                password="lolololo",
                                confirm_password="lolololo",
                                is_admin=True),
                                follow_redirects=True,
                )
    assert response.status_code == 200
    assert b'Username already registered.' in response.data