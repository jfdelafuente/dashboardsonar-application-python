from infocodest.models.users import User
from infocodest import db
from flask.testing import FlaskClient


def test_create_user(test_client: FlaskClient, init_database: None):
    user = User(email='john@example.com', username='john', password='johnjohn', is_admin=False)
    db.session.add(user)
    db.session.commit()
    john = User.query.filter(User.username.contains("john")).one()
    assert user.username == john.username
    assert user.email == john.email
    assert user.password == john.password
    assert not user.is_admin


def test_new_user(init_database: None):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, and role fields are defined correctly
    """
    user = User(username='admin',email='patkennedy79@gmail.com', password='FlaskIsAwesome')
    assert user.email == 'patkennedy79@gmail.com'
    assert user.__repr__() == '<users admin>'
    assert user.is_active
    assert not user.is_anonymous
    assert not user.is_admin


def test_new_user_with_fixture(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email and password fields are defined correctly
    """
    assert new_user.email == 'lolo@gmail.com'
    assert new_user.username == 'lolo'
    assert new_user.password != 'lolololo'
    assert new_user.is_admin
