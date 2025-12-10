import os
from flask.testing import FlaskClient


basedir = os.path.abspath(os.path.dirname(__file__))

def test_development_config(test_client: FlaskClient):
    test_client.config.from_object('config.DevelopmentConfig')
    assert test_client.config['DEBUG']
    assert not test_client.config['TESTING']
    # assert app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite:///" + os.path.join(basedir, "db.sqlite3")


def test_testing_config(test_client):
    test_client.config.from_object('config.TestingConfig')
    assert test_client.config['DEBUG']
    assert test_client.config['TESTING']
    # assert app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite:///" + os.path.join(basedir, "testdb.sqlite3")


def test_production_config(test_client):
    test_client.config.from_object('config.ProductionConfig')
    assert not test_client.config['DEBUG']
    assert not test_client.config['TESTING']
    # assert app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite:///" + os.path.join(basedir, "db.sqlite3")
