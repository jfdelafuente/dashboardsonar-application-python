"""
Unit tests for form validation.

Updated: Priority 3 - Added pytest markers
"""

import pytest
from flask.testing import FlaskClient
from infocodest.accounts.forms import RegisterForm, LoginForm, PasswordForm

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit

def test_validate_success_register_form(test_client: FlaskClient, init_database: None):
    """Ensure correct data validates."""
    form = RegisterForm(username="new_user",
                        email="new_user@gmail.com",
                        password="useruseruser",
                        confirm_password="useruseruser")
    assert form.validate() is True


def test_validate_fail_long_username_register_form(test_client: FlaskClient):
    """Ensure incorrect username does not validate."""
    form = RegisterForm(username="new",
                        email="new_user@gmail.com",
                        password="useruseruser",
                        confirm_password="useruseruser")
    assert form.validate() is False
    assert "Field must be between 4 and 25 characters long." in form.username.errors


def test_validate_fail_username_register_form(test_client: FlaskClient):
    """Ensure incorrect username does not validate."""
    form = RegisterForm(email="new_user@gmail.com",
                        password="useruseruser",
                        confirm_password="useruseruser")
    assert form.validate() is False
    assert "This field is required." in form.username.errors


def test_validate_fail_email_register_form(test_client: FlaskClient):
    """Ensure user can't register when a duplicate username is used."""
    form = RegisterForm(username="new_user",
                        email="new_user",
                        password="useruseruser",
                        confirm_password="useruseruser")
    assert form.validate() is False
    assert "Invalid email address." in form.email.errors


def test_validate_fail_password_register_form(test_client: FlaskClient):
    """Ensure user can't register when a duplicate email is used."""
    form = RegisterForm(username="new_user",
                        email="new_user@gmail.com",
                        password="user",
                        confirm_password="user")
    assert form.validate() is False
    assert "Field must be between 8 and 72 characters long." in form.password.errors


def test_validate_fail_confirm_password_register_form(test_client: FlaskClient):
    """Ensure user can't register when a duplicate email is used."""
    form = RegisterForm(username="new_user",
                        email="new_user@gmail.com",
                        password="useruseruser",
                        confirm_password="useruseruserrrr")
    assert form.validate() is False
    assert "Passwords must match." in form.confirm_password.errors


def test_user_already_register_form(test_client: FlaskClient, init_database: None):
    """Ensure correct data validates."""
    form = RegisterForm(username="lolo",
                        email="lolo@gmail.com",
                        password="lolololo",
                        confirm_password="lolololo")
    assert not form.validate()
    assert "Username already registered." in form.username.errors
    
def test_email_already_register_form(test_client: FlaskClient, init_database: None):
    """Ensure correct data validates."""
    form = RegisterForm(username="lololito",
                        email="lolo@gmail.com",
                        password="lolololo",
                        confirm_password="lolololo")
    assert not form.validate()
    assert "Please use a different email address." in form.email.errors


def test_validate_success_login_form(test_client: FlaskClient):
    """Ensure incorrect data does not validate."""
    form = LoginForm(username="neww", password="newnewnew")
    assert form.validate() is True

def test_validate_fail_username_login_form(test_client: FlaskClient):
    """Ensure incorrect data does not validate."""
    form = LoginForm(password="newnewnew")
    assert not form.validate()
    assert "This field is required." in form.username.errors
    
def test_validate_fail_password_login_form(test_client: FlaskClient):
    """Ensure incorrect data does not validate."""
    form = LoginForm(username="new_user")
    assert not form.validate()
    assert "This field is required." in form.password.errors
    
def test_validate_success_password_form(test_client: FlaskClient):
    """Ensure incorrect data does not validate."""
    form = PasswordForm(email="new_user@gmail.com")
    assert form.validate()


def test_validate_fail_password_form(test_client: FlaskClient):
    """Ensure incorrect data does not validate."""
    form = PasswordForm(email="new_user")
    assert not form.validate()
    assert "Invalid email address." in form.email.errors