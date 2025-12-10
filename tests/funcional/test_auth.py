from flask.testing import FlaskClient
from flask_login import current_user

def test_main_route_requires_login(test_client: FlaskClient):
    # Ensure main route requres logged in user.
    response = test_client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"INFOCODE - Login | Orange" in response.data
    assert b'Login' in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data
    
def test_logout_route_requires_login(test_client):
    # Ensure logout route requres logged in user.
    response = test_client.get("/logout", follow_redirects=True)
    assert b"INFOCODE - Login | Orange" in response.data
    assert b'Login' in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data


def test_correct_login(test_client, init_database):
    # Ensure login behaves correctly with correct credentials
    response = test_client.post(
            "/login",
            data=dict(username="lolo", password="lolololo"),
            follow_redirects=True,
    )
    assert (current_user.email == "lolo@gmail.com")  # noqa: F821
    assert current_user.is_authenticated
    assert response.status_code == 200


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


def test_logout_behaves_correctly(test_client: FlaskClient, init_database: None):
    # Ensure logout behaves correctly, regarding the session
    response = test_client.post(
            "/login",
            data=dict(username="lolo", password="lolololo"),
            follow_redirects=True,
    )
    assert (current_user.email == "lolo@gmail.com")  # noqa: F821
    assert current_user.is_authenticated
    assert response.status_code == 200

    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert not current_user.is_authenticated


def test_login_page(test_client):
    response = test_client.get("/login")
    assert response.status_code == 200
    assert b"INFOCODE - Login | Orange" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data


def test_register_page(test_client):
    response = test_client.get("/register")
    assert response.status_code == 200
    assert b"INFOCODE - Register | Orange" in response.data
    assert b"Username" in response.data
    assert b"Email" in response.data
    assert b"Password" in response.data


def test_valid_registration(test_client: FlaskClient, init_database: None):
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


def test_password_page(test_client):
    response = test_client.get("/password")
    assert response.status_code == 200
    assert b"INFOCODE - Password Recovery | Orange" in response.data


# def test_logout_redirect(test_client):
#     response = test_client.get("/logout")
#     # Check that there was one redirect response.
#     # assert len(response.history) == 1
#     # Check that the second request was to the index page.
#     # assert response.request.path == "/login"
#     assert b"INFOCODE - Login | Orange" in response.data
