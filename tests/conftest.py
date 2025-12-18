import pytest
from infocodest import create_app
from infocodest.extensions import db
from config import TestingConfig  # New config system from config/ module (Phase 6)
from infocodest.models.users import User


@pytest.fixture
def new_user():
    user = User(username='lolo',
                email='lolo@gmail.com',
                password='lolololo',
                is_admin=True)
    return user


@pytest.fixture
def app():
    flask_app = create_app(TestingConfig)
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def test_client(app):
    with app.test_client() as testing_client:
        yield testing_client

@pytest.fixture()
def init_database(test_client):
    
    # Create the database and the database table
    db.create_all()
    # Insert user data
    default_user = User(
        username="lolo", email="lolo@gmail.com", password="lolololo", is_admin=True
    )
    db.session.add(default_user)
    db.session.commit()

    yield  # this is where the testing happens!
    
    # Close the database session and drop all tables after the session
    db.session.remove()
    db.drop_all()


@pytest.fixture
def login_in_user(test_client):
    response = test_client.post(
            "/login",
            data=dict(username="lolo", password="lolololo"),
            follow_redirects=True,
    )
    yield
    test_client.get("/logout")


@pytest.fixture()
def init_test_data(init_database):
    """
    Initialize test data for API tests
    Creates sample metrica, historico, proveedor, daily, and registro records

    Note: API endpoints use different tables:
    - /api/aplicacion/{aplicacion} -> Metrica table
    - /api/aplicacion/{aplicacion}/{project} -> Historico table
    - /api/daily/{aplicacion} -> Daily table
    - /api/registro -> Registro table
    """
    from infocodest.models.metricas import Metrica
    from infocodest.models.historico import Historico
    from infocodest.models.proveedor import Proveedor
    from infocodest.models.daily import Daily
    from infocodest.models.registros import Registro
    from datetime import date, timedelta

    # Create sample metrica data (for /api/aplicacion/{aplicacion})
    metrica1 = Metrica(
        repo="abacus-application-java",
        aplicacion="abacusbrmosp",
        fecha="2025-01-01",
        bugs=5,
        reliability_rating=3,
        reliability_label="C",
        vulnerabilities=2,
        security_rating=4,
        security_label="D",
        code_smells=10,
        sqale_rating=2,
        sqale_label="B",
        alert_status="OK",
        project="abacus-application-java",
        complexity=100,
        coverage=75,
        unit_tests="50",
        ncloc=1000,
        duplicated_line_density=5,
        sqale_index=120,
        sqale_debt_ratio=10,
        size="M",
        dloc_label="A",
        coverage_label="B",
        quality_gate="PASSED"
    )

    # Create sample historico data (for /api/aplicacion/{aplicacion}/{project})
    historico1 = Historico(
        repo="abacus-application-java",
        aplicacion="abacusbrmosp",
        fecha="2025-01-01",
        bugs=5,
        reliability_rating=3,
        reliability_label="C",
        vulnerabilities=2,
        security_rating=4,
        security_label="D",
        code_smells=10,
        sqale_rating=2,
        sqale_label="B",
        alert_status="OK",
        project="abacus-application-java",
        complexity=100,
        coverage=75,
        unit_tests="50",
        ncloc=1000,
        duplicated_line_density=5,
        sqale_index=120,
        sqale_debt_ratio=10,
        size="M",
        dloc_label="A",
        coverage_label="B",
        quality_gate="PASSED"
    )

    # Create sample proveedor data
    proveedor1 = Proveedor(
        aplicacion="abacusbrmosp",
        proveedor="Test Provider",
        tipo="Internal"
    )

    # Create sample daily data (for /api/daily/{aplicacion})
    daily1 = Daily(
        repo="abacus-application-java",
        aplicacion="abacusbrmosp",
        proveedor="Test Provider",
        created_on=date.today() - timedelta(days=1),
        num_bugs=5,
        num_vulnerabilities=2,
        num_code_smells=10,
        num_quality=8,
        num_analisis=1
    )

    # Create sample registro data (for /api/registro)
    # No need for unique values - constraints removed from model
    registro1 = Registro(
        proceso="test_import_001",
        created_on=date.today(),
        num_app=10,
        num_repo=15,
        num_bugs=25,
        num_quality=8,
        num_analisis=5
    )

    db.session.add(metrica1)
    db.session.add(historico1)
    db.session.add(proveedor1)
    db.session.add(daily1)
    db.session.add(registro1)
    db.session.commit()

    yield  # Tests run here

    # Cleanup is handled by init_database fixture