# FASE 9: Tests y Validación - Plan Detallado

**Fecha**: 2025-12-13
**Fase**: 9 de 10
**Duración estimada**: 2-3 horas
**Objetivo**: Aumentar cobertura de tests del 60% al >80% validando todas las capas refactorizadas

---

## 📊 Resumen Ejecutivo

### Contexto

Después de 8 fases de refactorización exitosas (80% del proyecto completado), hemos transformado la aplicación de una arquitectura monolítica a un sistema en capas:

- **Fase 1**: Repository Layer (acceso a datos)
- **Fase 2**: Service Layer (lógica de negocio)
- **Fase 3**: View Layer refactorizado (presentación)
- **Fase 4**: Utilities (logging, decorators, helpers, validators)
- **Fase 5**: Exception Handling (15 excepciones custom)
- **Fase 6**: Configuration System (modular y flexible)
- **Fase 7**: Dependencies Optimization (requirements limpios)
- **Fase 8**: Entry Points (factory pattern documentado)

### Problema Actual

**La cobertura actual de tests es ~60%**, y los tests existentes:
- No cubren las nuevas capas (repositories, services)
- Usan código legacy directamente
- No validan utilidades nuevas (validators, helpers, decorators)
- No prueban excepciones personalizadas
- No verifican la inyección de dependencias

### Objetivo de la Fase 9

**Aumentar cobertura a >80%** mediante:

1. **Tests unitarios de repositories** (Fase 1)
2. **Tests unitarios de services con mocks** (Fase 2)
3. **Tests de integración de vistas refactorizadas** (Fase 3)
4. **Tests de utilities** (Fase 4)
5. **Tests de excepciones** (Fase 5)
6. **Actualizar tests existentes** para usar nuevas capas

---

## 🎯 Objetivos Detallados

### Objetivos Cuantitativos

| Métrica | Actual | Objetivo | Estrategia |
|---------|--------|----------|------------|
| **Cobertura total** | ~60% | >80% | Tests en todas las capas |
| **Cobertura repositories** | 0% | >85% | Unit tests con DB en memoria |
| **Cobertura services** | 0% | >80% | Unit tests con mocks |
| **Cobertura utils** | Parcial | >85% | Tests de validators/helpers |
| **Cobertura exceptions** | 0% | 100% | Tests de todas las excepciones |
| **Tests de integración** | Básico | Completo | Vistas refactorizadas |

### Objetivos Cualitativos

1. **Confiabilidad**: Todos los tests deben pasar sin errores
2. **Rapidez**: Suite de tests debe ejecutarse en <10 segundos
3. **Mantenibilidad**: Tests claros, bien documentados, con fixtures reutilizables
4. **Aislamiento**: Tests unitarios sin dependencias externas (usando mocks)
5. **Cobertura real**: No solo líneas, sino lógica de negocio y edge cases

---

## 📁 Estructura Actual de Tests

### Archivos Existentes

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures existentes (app, test_client, init_database)
├── unit/
│   ├── __init__.py
│   ├── test_config.py             # Tests de configuración
│   ├── test_form.py               # Tests de formularios
│   └── test_user_model.py         # Tests del modelo User
└── funcional/
    ├── __init__.py
    ├── test_account_login.py      # Tests de login
    ├── test_account_page.py       # Tests de páginas de cuenta
    ├── test_api.py                # Tests de API
    ├── test_auth.py               # Tests de autenticación
    └── test_home.py               # Tests de home (legacy)
```

### Análisis de Fixtures Existentes

**Fixtures en `conftest.py`**:
- `new_user`: Crea un usuario de prueba
- `app`: Crea aplicación Flask con TestingConfig
- `test_client`: Cliente de pruebas
- `init_database`: Inicializa y limpia DB
- `login_in_user`: Login automático

**Estado**: Fixtures bien diseñadas, pero necesitan extensión para nuevas capas.

---

## 🛠️ Estructura de Tests a Crear

### Nueva Organización

```
tests/
├── __init__.py
├── conftest.py                          # ⬆️ Actualizar con nuevas fixtures
│
├── unit/                                # Tests unitarios (sin DB real)
│   ├── __init__.py
│   ├── test_config.py                   # ✅ Existente
│   ├── test_form.py                     # ✅ Existente
│   ├── test_user_model.py               # ✅ Existente
│   │
│   ├── test_repositories/               # 🆕 PASO 2
│   │   ├── __init__.py
│   │   ├── test_base_repository.py      # BaseRepository CRUD
│   │   ├── test_dashboard_repository.py # DashboardRepository queries
│   │   └── test_metrica_repository.py   # MetricaRepository
│   │
│   ├── test_services/                   # 🆕 PASO 3
│   │   ├── __init__.py
│   │   └── test_dashboard_service.py    # DashboardService con mocks
│   │
│   ├── test_utils/                      # 🆕 PASO 4
│   │   ├── __init__.py
│   │   ├── test_validators.py           # 7 validators
│   │   ├── test_helpers.py              # 10 helpers
│   │   └── test_decorators.py           # @inject_service, @retry, etc.
│   │
│   └── test_exceptions/                 # 🆕 PASO 4
│       ├── __init__.py
│       └── test_business_exceptions.py  # 15 custom exceptions
│
├── integration/                         # 🆕 Tests de integración
│   ├── __init__.py
│   └── test_home_views.py               # 🆕 PASO 4 - Vistas refactorizadas
│
└── funcional/                           # Tests funcionales existentes
    ├── __init__.py
    ├── test_account_login.py            # ✅ Existente
    ├── test_account_page.py             # ✅ Existente
    ├── test_api.py                      # ✅ Existente
    ├── test_auth.py                     # ✅ Existente
    └── test_home.py                     # ⬆️ Actualizar para usar service layer
```

---

## 📝 PASO 2: Tests de Repositories

### Objetivo

Crear tests unitarios para la capa de repositorios (Fase 1) con **cobertura >85%**.

### Archivos a Crear

#### 1. `tests/unit/test_repositories/__init__.py`

```python
"""
Unit tests for repository layer.

Tests CRUD operations and query methods using in-memory SQLite database.
"""
```

#### 2. `tests/unit/test_repositories/test_base_repository.py`

**Objetivo**: Probar operaciones CRUD genéricas de `BaseRepository`

**Tests a implementar** (~15 tests):

```python
import pytest
from infocodest.repositories.base_repository import BaseRepository
from infocodest.models.users import User
from infocodest.extensions import db


class TestBaseRepository:
    """Test suite for BaseRepository CRUD operations."""

    @pytest.fixture
    def user_repo(self, app):
        """Create repository for User model."""
        with app.app_context():
            db.create_all()
            yield BaseRepository(User)
            db.session.remove()
            db.drop_all()

    def test_create_user(self, user_repo):
        """Test creating a new user."""
        user = User(username='test', email='test@example.com', password='password')
        created = user_repo.create(user)

        assert created.id is not None
        assert created.username == 'test'
        assert created.email == 'test@example.com'

    def test_get_by_id_existing(self, user_repo):
        """Test retrieving user by ID."""
        user = User(username='test', email='test@example.com', password='password')
        created = user_repo.create(user)

        retrieved = user_repo.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.username == 'test'

    def test_get_by_id_nonexistent(self, user_repo):
        """Test retrieving non-existent user returns None."""
        result = user_repo.get_by_id(99999)
        assert result is None

    def test_get_all_empty(self, user_repo):
        """Test get_all with no records."""
        users = user_repo.get_all()
        assert users == []

    def test_get_all_multiple(self, user_repo):
        """Test get_all with multiple records."""
        user1 = User(username='user1', email='user1@example.com', password='pass1')
        user2 = User(username='user2', email='user2@example.com', password='pass2')
        user_repo.create(user1)
        user_repo.create(user2)

        users = user_repo.get_all()
        assert len(users) == 2

    def test_update_user(self, user_repo):
        """Test updating user."""
        user = User(username='test', email='test@example.com', password='password')
        created = user_repo.create(user)

        created.username = 'updated'
        updated = user_repo.update(created)

        assert updated.username == 'updated'

    def test_delete_user(self, user_repo):
        """Test deleting user."""
        user = User(username='test', email='test@example.com', password='password')
        created = user_repo.create(user)
        user_id = created.id

        user_repo.delete(created)

        retrieved = user_repo.get_by_id(user_id)
        assert retrieved is None

    def test_count_zero(self, user_repo):
        """Test count with no records."""
        count = user_repo.count()
        assert count == 0

    def test_count_multiple(self, user_repo):
        """Test count with multiple records."""
        user1 = User(username='user1', email='user1@example.com', password='pass1')
        user2 = User(username='user2', email='user2@example.com', password='pass2')
        user_repo.create(user1)
        user_repo.create(user2)

        count = user_repo.count()
        assert count == 2

    def test_filter_by_single_condition(self, user_repo):
        """Test filter_by with single condition."""
        user1 = User(username='alice', email='alice@example.com', password='pass1')
        user2 = User(username='bob', email='bob@example.com', password='pass2')
        user_repo.create(user1)
        user_repo.create(user2)

        results = user_repo.filter_by(username='alice')
        assert len(results) == 1
        assert results[0].username == 'alice'

    def test_filter_by_multiple_conditions(self, user_repo):
        """Test filter_by with multiple conditions."""
        user1 = User(username='alice', email='alice@example.com', password='pass1', is_admin=True)
        user2 = User(username='bob', email='bob@example.com', password='pass2', is_admin=False)
        user_repo.create(user1)
        user_repo.create(user2)

        results = user_repo.filter_by(username='alice', is_admin=True)
        assert len(results) == 1
        assert results[0].username == 'alice'

    def test_filter_by_no_results(self, user_repo):
        """Test filter_by with no matching results."""
        results = user_repo.filter_by(username='nonexistent')
        assert results == []

    def test_first_or_none_found(self, user_repo):
        """Test first_or_none when record exists."""
        user = User(username='test', email='test@example.com', password='password')
        user_repo.create(user)

        result = user_repo.first_or_none(username='test')
        assert result is not None
        assert result.username == 'test'

    def test_first_or_none_not_found(self, user_repo):
        """Test first_or_none when record doesn't exist."""
        result = user_repo.first_or_none(username='nonexistent')
        assert result is None

    def test_exists_true(self, user_repo):
        """Test exists returns True when record exists."""
        user = User(username='test', email='test@example.com', password='password')
        user_repo.create(user)

        exists = user_repo.exists(username='test')
        assert exists is True

    def test_exists_false(self, user_repo):
        """Test exists returns False when record doesn't exist."""
        exists = user_repo.exists(username='nonexistent')
        assert exists is False
```

**Cobertura esperada**: >90% de BaseRepository

#### 3. `tests/unit/test_repositories/test_dashboard_repository.py`

**Objetivo**: Probar métodos específicos de `DashboardRepository`

**Tests a implementar** (~20 tests):

```python
import pytest
from datetime import datetime
from infocodest.repositories.dashboard_repository import DashboardRepository
from infocodest.models.metricas import Metrica
from infocodest.extensions import db


@pytest.fixture
def dashboard_repo(app):
    """Create DashboardRepository with test data."""
    with app.app_context():
        db.create_all()

        # Sample test data
        metricas = [
            Metrica(
                metrica='App1',
                estado='OK',
                cobertura=85.5,
                bugs=10,
                vulnerabilidades=2,
                code_smells=50,
                duplicaciones=5.0,
                lineas=10000,
                fecha_actualizacion=datetime(2025, 12, 1)
            ),
            Metrica(
                metrica='App2',
                estado='ERROR',
                cobertura=60.0,
                bugs=25,
                vulnerabilidades=8,
                code_smells=120,
                duplicaciones=12.0,
                lineas=15000,
                fecha_actualizacion=datetime(2025, 12, 5)
            ),
            Metrica(
                metrica='App3',
                estado='OK',
                cobertura=90.0,
                bugs=5,
                vulnerabilidades=0,
                code_smells=30,
                duplicaciones=2.0,
                lineas=8000,
                fecha_actualizacion=datetime(2025, 12, 10)
            ),
        ]

        for metrica in metricas:
            db.session.add(metrica)
        db.session.commit()

        yield DashboardRepository()

        db.session.remove()
        db.drop_all()


class TestDashboardRepository:
    """Test suite for DashboardRepository query methods."""

    def test_get_distinct_applications(self, dashboard_repo):
        """Test retrieving distinct application names."""
        apps = dashboard_repo.get_distinct_applications()
        assert len(apps) == 3
        assert 'App1' in apps
        assert 'App2' in apps
        assert 'App3' in apps

    def test_count_total_apps(self, dashboard_repo):
        """Test counting total applications."""
        count = dashboard_repo.count_total_apps()
        assert count == 3

    def test_get_apps_by_estado_ok(self, dashboard_repo):
        """Test filtering apps by estado OK."""
        apps_ok = dashboard_repo.get_apps_by_estado('OK')
        assert len(apps_ok) == 2
        assert all(app.estado == 'OK' for app in apps_ok)

    def test_get_apps_by_estado_error(self, dashboard_repo):
        """Test filtering apps by estado ERROR."""
        apps_error = dashboard_repo.get_apps_by_estado('ERROR')
        assert len(apps_error) == 1
        assert apps_error[0].metrica == 'App2'

    def test_get_average_cobertura(self, dashboard_repo):
        """Test calculating average coverage."""
        avg = dashboard_repo.get_average_cobertura()
        expected = (85.5 + 60.0 + 90.0) / 3
        assert abs(avg - expected) < 0.01

    def test_get_total_bugs(self, dashboard_repo):
        """Test summing total bugs."""
        total = dashboard_repo.get_total_bugs()
        assert total == 40  # 10 + 25 + 5

    def test_get_total_vulnerabilidades(self, dashboard_repo):
        """Test summing total vulnerabilities."""
        total = dashboard_repo.get_total_vulnerabilidades()
        assert total == 10  # 2 + 8 + 0

    def test_get_apps_with_high_cobertura(self, dashboard_repo):
        """Test filtering apps with coverage > 80%."""
        high_coverage = dashboard_repo.get_apps_with_cobertura_above(80.0)
        assert len(high_coverage) == 2  # App1 (85.5) and App3 (90.0)

    def test_get_apps_with_vulnerabilidades(self, dashboard_repo):
        """Test filtering apps with vulnerabilities."""
        apps_with_vulns = dashboard_repo.get_apps_with_vulnerabilidades()
        assert len(apps_with_vulns) == 2  # App1 and App2

    def test_get_latest_metricas(self, dashboard_repo):
        """Test retrieving latest metrics ordered by date."""
        latest = dashboard_repo.get_latest_metricas(limit=2)
        assert len(latest) == 2
        assert latest[0].metrica == 'App3'  # Most recent (2025-12-10)
        assert latest[1].metrica == 'App2'  # Second (2025-12-05)

    # Add 10 more tests for other DashboardRepository methods...
```

**Cobertura esperada**: >85% de DashboardRepository

#### 4. `tests/unit/test_repositories/test_metrica_repository.py`

Similar structure for `MetricaRepository`.

### Actualización de `conftest.py`

Añadir fixture para datos de prueba:

```python
@pytest.fixture
def sample_metricas(app):
    """Create sample metrics for testing."""
    with app.app_context():
        db.create_all()

        metricas = [
            Metrica(
                metrica='TestApp1',
                estado='OK',
                cobertura=85.0,
                bugs=10,
                vulnerabilidades=2,
                code_smells=50,
                duplicaciones=5.0,
                lineas=10000
            ),
            # Add more sample data...
        ]

        for metrica in metricas:
            db.session.add(metrica)
        db.session.commit()

        yield

        db.session.remove()
        db.drop_all()
```

---

## 📝 PASO 3: Tests de Services

### Objetivo

Crear tests unitarios para la capa de servicios (Fase 2) **usando mocks** para aislar la lógica de negocio. Cobertura >80%.

### Archivos a Crear

#### 1. `tests/unit/test_services/__init__.py`

```python
"""
Unit tests for service layer.

Tests business logic using mocked repositories for isolation.
"""
```

#### 2. `tests/unit/test_services/test_dashboard_service.py`

**Objetivo**: Probar lógica de negocio de `DashboardService` sin tocar DB

**Tests a implementar** (~20 tests):

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from infocodest.services.dashboard_service import DashboardService
from infocodest.models.metricas import Metrica
from infocodest.exceptions.business_exceptions import (
    NoDataFoundException,
    InvalidParameterException
)


class TestDashboardService:
    """Test suite for DashboardService business logic."""

    @pytest.fixture
    def mock_dashboard_repo(self):
        """Create mocked DashboardRepository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_dashboard_repo):
        """Create DashboardService with mocked repository."""
        with patch('infocodest.services.dashboard_service.DashboardRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_dashboard_repo
            return DashboardService()

    def test_get_kpi_overview_success(self, service, mock_dashboard_repo):
        """Test KPI overview calculation with valid data."""
        # Arrange
        mock_dashboard_repo.count_total_apps.return_value = 10
        mock_dashboard_repo.get_total_bugs.return_value = 50
        mock_dashboard_repo.get_total_vulnerabilidades.return_value = 15
        mock_dashboard_repo.get_average_cobertura.return_value = 75.5

        # Act
        result = service.get_kpi_overview()

        # Assert
        assert result['aplicaciones'] == 10
        assert result['bugs'] == 50
        assert result['vulnerabilidades'] == 15
        assert result['cobertura_promedio'] == 75.5
        mock_dashboard_repo.count_total_apps.assert_called_once()

    def test_get_kpi_overview_no_data(self, service, mock_dashboard_repo):
        """Test KPI overview when no data exists."""
        # Arrange
        mock_dashboard_repo.count_total_apps.return_value = 0

        # Act & Assert
        with pytest.raises(NoDataFoundException) as exc_info:
            service.get_kpi_overview()

        assert "No metrics found" in str(exc_info.value)

    def test_get_apps_by_quality_gate_ok(self, service, mock_dashboard_repo):
        """Test filtering apps by quality gate OK."""
        # Arrange
        mock_apps = [
            Mock(metrica='App1', estado='OK'),
            Mock(metrica='App2', estado='OK'),
        ]
        mock_dashboard_repo.get_apps_by_estado.return_value = mock_apps

        # Act
        result = service.get_apps_by_quality_gate('OK')

        # Assert
        assert len(result) == 2
        mock_dashboard_repo.get_apps_by_estado.assert_called_once_with('OK')

    def test_get_apps_by_quality_gate_invalid_status(self, service, mock_dashboard_repo):
        """Test invalid quality gate status raises exception."""
        # Act & Assert
        with pytest.raises(InvalidParameterException) as exc_info:
            service.get_apps_by_quality_gate('INVALID_STATUS')

        assert "Invalid quality gate status" in str(exc_info.value)

    def test_calculate_health_score_perfect(self, service, mock_dashboard_repo):
        """Test health score calculation for perfect metrics."""
        # Arrange
        mock_metrica = Mock(
            cobertura=100.0,
            bugs=0,
            vulnerabilidades=0,
            code_smells=0,
            duplicaciones=0.0
        )

        # Act
        score = service.calculate_health_score(mock_metrica)

        # Assert
        assert score == 100.0

    def test_calculate_health_score_poor(self, service, mock_dashboard_repo):
        """Test health score calculation for poor metrics."""
        # Arrange
        mock_metrica = Mock(
            cobertura=30.0,
            bugs=100,
            vulnerabilidades=50,
            code_smells=500,
            duplicaciones=25.0
        )

        # Act
        score = service.calculate_health_score(mock_metrica)

        # Assert
        assert score < 40.0

    def test_get_trending_data_last_30_days(self, service, mock_dashboard_repo):
        """Test trending data for last 30 days."""
        # Arrange
        from datetime import datetime, timedelta
        today = datetime.now()
        mock_metricas = [
            Mock(fecha_actualizacion=today - timedelta(days=i), bugs=10 + i)
            for i in range(30)
        ]
        mock_dashboard_repo.get_metricas_by_date_range.return_value = mock_metricas

        # Act
        result = service.get_trending_data(days=30)

        # Assert
        assert len(result['dates']) == 30
        assert len(result['bugs']) == 30
        mock_dashboard_repo.get_metricas_by_date_range.assert_called_once()

    def test_get_top_vulnerable_apps(self, service, mock_dashboard_repo):
        """Test retrieving top vulnerable applications."""
        # Arrange
        mock_apps = [
            Mock(metrica='App1', vulnerabilidades=10),
            Mock(metrica='App2', vulnerabilidades=8),
            Mock(metrica='App3', vulnerabilidades=5),
        ]
        mock_dashboard_repo.get_apps_ordered_by_vulnerabilidades.return_value = mock_apps

        # Act
        result = service.get_top_vulnerable_apps(limit=3)

        # Assert
        assert len(result) == 3
        assert result[0].metrica == 'App1'
        assert result[0].vulnerabilidades == 10

    def test_get_coverage_distribution(self, service, mock_dashboard_repo):
        """Test coverage distribution calculation."""
        # Arrange
        mock_apps = [
            Mock(cobertura=95.0),  # Excellent (>90)
            Mock(cobertura=85.0),  # Good (80-90)
            Mock(cobertura=75.0),  # Fair (70-80)
            Mock(cobertura=85.0),  # Good (80-90)
            Mock(cobertura=50.0),  # Poor (<70)
        ]
        mock_dashboard_repo.get_all.return_value = mock_apps

        # Act
        result = service.get_coverage_distribution()

        # Assert
        assert result['excellent'] == 1  # >90
        assert result['good'] == 2       # 80-90
        assert result['fair'] == 1       # 70-80
        assert result['poor'] == 1       # <70

    # Add 10 more tests for other service methods...
```

**Cobertura esperada**: >80% de DashboardService

### Ventajas de usar Mocks

1. **Aislamiento**: Tests no dependen de DB, son más rápidos
2. **Control**: Podemos simular cualquier escenario (errores, edge cases)
3. **Repetibilidad**: Siempre producen los mismos resultados
4. **Claridad**: Verificamos solo la lógica de negocio

---

## 📝 PASO 4: Tests de Integración y Utilidades

### A. Tests de Integración de Vistas

#### `tests/integration/__init__.py`

```python
"""
Integration tests for refactored views.

Tests view layer with service layer integration (no mocks).
"""
```

#### `tests/integration/test_home_views.py`

**Objetivo**: Probar vistas refactorizadas (Fase 3) con service layer real

**Tests a implementar** (~15 tests):

```python
import pytest
from infocodest.extensions import db
from infocodest.models.metricas import Metrica


@pytest.fixture
def client_with_data(test_client, init_database):
    """Test client with sample metrics data."""
    # Add sample metrics
    metrica1 = Metrica(
        metrica='TestApp1',
        estado='OK',
        cobertura=85.0,
        bugs=10,
        vulnerabilidades=2,
        code_smells=50,
        duplicaciones=5.0,
        lineas=10000
    )
    db.session.add(metrica1)
    db.session.commit()

    yield test_client


class TestHomeViews:
    """Integration tests for refactored home views."""

    def test_index_page_loads(self, client_with_data, login_in_user):
        """Test index page loads successfully."""
        response = client_with_data.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data

    def test_index_displays_kpi_data(self, client_with_data, login_in_user):
        """Test index page displays KPI data from service."""
        response = client_with_data.get('/')
        assert response.status_code == 200
        # Verify KPIs are displayed (injected via service)
        assert b'TestApp1' in response.data or b'1' in response.data

    def test_quality_gate_view_ok(self, client_with_data, login_in_user):
        """Test quality gate view with OK status."""
        response = client_with_data.get('/quality-gate/OK')
        assert response.status_code == 200

    def test_quality_gate_view_error(self, client_with_data, login_in_user):
        """Test quality gate view with ERROR status."""
        response = client_with_data.get('/quality-gate/ERROR')
        assert response.status_code == 200

    def test_service_injection_in_views(self, client_with_data, login_in_user):
        """Test that views use service layer (not direct DB queries)."""
        # This test verifies that refactored views use @inject_service
        response = client_with_data.get('/')
        assert response.status_code == 200
        # Service layer should be injected, no direct ORM calls in views

    # Add 10 more integration tests...
```

### B. Tests de Utilidades

#### 1. `tests/unit/test_utils/test_validators.py`

**Objetivo**: Probar los 7 validadores (Fase 4)

```python
import pytest
from infocodest.utils.validators import (
    validate_email,
    validate_username,
    validate_date_range,
    validate_pagination,
    validate_quality_gate_status,
    validate_percentage,
    validate_positive_integer
)
from infocodest.exceptions.business_exceptions import ValidationException


class TestValidators:
    """Test suite for input validators."""

    # validate_email tests
    def test_validate_email_valid(self):
        """Test valid email addresses."""
        assert validate_email('user@example.com') is True
        assert validate_email('test.user@domain.co.uk') is True

    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        with pytest.raises(ValidationException):
            validate_email('invalid-email')
        with pytest.raises(ValidationException):
            validate_email('user@')
        with pytest.raises(ValidationException):
            validate_email('@example.com')

    # validate_username tests
    def test_validate_username_valid(self):
        """Test valid usernames."""
        assert validate_username('john_doe') is True
        assert validate_username('user123') is True

    def test_validate_username_too_short(self):
        """Test username too short."""
        with pytest.raises(ValidationException):
            validate_username('ab')  # Less than 3 chars

    def test_validate_username_too_long(self):
        """Test username too long."""
        with pytest.raises(ValidationException):
            validate_username('a' * 51)  # More than 50 chars

    # validate_percentage tests
    def test_validate_percentage_valid(self):
        """Test valid percentages."""
        assert validate_percentage(0.0) is True
        assert validate_percentage(50.5) is True
        assert validate_percentage(100.0) is True

    def test_validate_percentage_invalid(self):
        """Test invalid percentages."""
        with pytest.raises(ValidationException):
            validate_percentage(-1.0)
        with pytest.raises(ValidationException):
            validate_percentage(101.0)

    # validate_quality_gate_status tests
    def test_validate_quality_gate_status_valid(self):
        """Test valid quality gate statuses."""
        assert validate_quality_gate_status('OK') is True
        assert validate_quality_gate_status('ERROR') is True
        assert validate_quality_gate_status('WARN') is True

    def test_validate_quality_gate_status_invalid(self):
        """Test invalid quality gate status."""
        with pytest.raises(ValidationException):
            validate_quality_gate_status('INVALID')

    # Add tests for remaining validators...
```

#### 2. `tests/unit/test_utils/test_helpers.py`

**Objetivo**: Probar las 10 funciones helper (Fase 4)

```python
import pytest
from datetime import datetime
from infocodest.utils.helpers import (
    format_percentage,
    format_number,
    calculate_days_ago,
    truncate_string,
    safe_divide,
    parse_date,
    get_severity_class,
    calculate_trend,
    group_by_key,
    flatten_list
)


class TestHelpers:
    """Test suite for helper functions."""

    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(85.5432) == '85.54%'
        assert format_percentage(100.0) == '100.00%'
        assert format_percentage(0.0) == '0.00%'

    def test_format_number(self):
        """Test number formatting with thousands separator."""
        assert format_number(1000) == '1,000'
        assert format_number(1234567) == '1,234,567'
        assert format_number(42) == '42'

    def test_safe_divide_normal(self):
        """Test safe division with valid divisor."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(7, 2) == 3.5

    def test_safe_divide_by_zero(self):
        """Test safe division by zero returns default."""
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=None) is None

    def test_truncate_string(self):
        """Test string truncation."""
        assert truncate_string('Hello World', 5) == 'Hello...'
        assert truncate_string('Short', 10) == 'Short'

    def test_get_severity_class_high(self):
        """Test severity class for high values."""
        assert get_severity_class(100, threshold_high=50) == 'danger'

    def test_get_severity_class_medium(self):
        """Test severity class for medium values."""
        assert get_severity_class(30, threshold_high=50, threshold_medium=20) == 'warning'

    def test_get_severity_class_low(self):
        """Test severity class for low values."""
        assert get_severity_class(10, threshold_high=50, threshold_medium=20) == 'success'

    # Add tests for remaining helpers...
```

#### 3. `tests/unit/test_utils/test_decorators.py`

**Objetivo**: Probar decoradores (Fase 4)

```python
import pytest
import time
from unittest.mock import Mock, patch
from infocodest.utils.decorators import (
    inject_service,
    log_execution_time,
    retry,
    deprecated
)


class TestDecorators:
    """Test suite for utility decorators."""

    def test_inject_service_decorator(self):
        """Test @inject_service decorator injects service."""
        from infocodest.services.dashboard_service import DashboardService

        @inject_service(DashboardService, 'dashboard_service')
        def view_function(dashboard_service=None):
            return dashboard_service

        result = view_function()
        assert result is not None
        assert isinstance(result, DashboardService)

    def test_log_execution_time_decorator(self, caplog):
        """Test @log_execution_time logs execution duration."""
        @log_execution_time
        def slow_function():
            time.sleep(0.1)
            return 'done'

        result = slow_function()
        assert result == 'done'
        # Check that execution time was logged
        assert any('execution time' in record.message.lower() for record in caplog.records)

    def test_retry_decorator_succeeds_first_try(self):
        """Test @retry when function succeeds on first try."""
        mock_func = Mock(return_value='success')

        @retry(max_attempts=3, delay=0.01)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == 'success'
        assert mock_func.call_count == 1

    def test_retry_decorator_succeeds_after_retries(self):
        """Test @retry when function succeeds after retries."""
        mock_func = Mock(side_effect=[Exception('fail'), Exception('fail'), 'success'])

        @retry(max_attempts=3, delay=0.01)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == 'success'
        assert mock_func.call_count == 3

    def test_retry_decorator_fails_after_max_attempts(self):
        """Test @retry raises exception after max attempts."""
        mock_func = Mock(side_effect=Exception('persistent failure'))

        @retry(max_attempts=3, delay=0.01)
        def test_func():
            return mock_func()

        with pytest.raises(Exception) as exc_info:
            test_func()

        assert 'persistent failure' in str(exc_info.value)
        assert mock_func.call_count == 3

    def test_deprecated_decorator_warns(self):
        """Test @deprecated decorator issues warning."""
        @deprecated(reason='Use new_function instead')
        def old_function():
            return 'old'

        with pytest.warns(DeprecationWarning):
            result = old_function()

        assert result == 'old'
```

### C. Tests de Excepciones

#### `tests/unit/test_exceptions/test_business_exceptions.py`

**Objetivo**: Probar las 15 excepciones personalizadas (Fase 5)

```python
import pytest
from infocodest.exceptions.business_exceptions import (
    NoDataFoundException,
    InvalidParameterException,
    ValidationException,
    DatabaseException,
    ServiceException,
    RepositoryException,
    ConfigurationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    DuplicateResourceException,
    ExternalServiceException,
    DataIntegrityException,
    BusinessRuleException,
    RateLimitException
)


class TestBusinessExceptions:
    """Test suite for custom business exceptions."""

    def test_no_data_found_exception(self):
        """Test NoDataFoundException."""
        with pytest.raises(NoDataFoundException) as exc_info:
            raise NoDataFoundException("No data available")

        assert "No data available" in str(exc_info.value)
        assert exc_info.value.http_code == 404

    def test_invalid_parameter_exception(self):
        """Test InvalidParameterException."""
        with pytest.raises(InvalidParameterException) as exc_info:
            raise InvalidParameterException("Invalid status parameter")

        assert "Invalid status parameter" in str(exc_info.value)
        assert exc_info.value.http_code == 400

    def test_validation_exception(self):
        """Test ValidationException."""
        with pytest.raises(ValidationException) as exc_info:
            raise ValidationException("Email format invalid")

        assert "Email format invalid" in str(exc_info.value)
        assert exc_info.value.http_code == 400

    def test_database_exception(self):
        """Test DatabaseException."""
        with pytest.raises(DatabaseException) as exc_info:
            raise DatabaseException("Connection failed")

        assert "Connection failed" in str(exc_info.value)
        assert exc_info.value.http_code == 500

    def test_authentication_exception(self):
        """Test AuthenticationException."""
        with pytest.raises(AuthenticationException) as exc_info:
            raise AuthenticationException("Invalid credentials")

        assert "Invalid credentials" in str(exc_info.value)
        assert exc_info.value.http_code == 401

    def test_authorization_exception(self):
        """Test AuthorizationException."""
        with pytest.raises(AuthorizationException) as exc_info:
            raise AuthorizationException("Access denied")

        assert "Access denied" in str(exc_info.value)
        assert exc_info.value.http_code == 403

    def test_resource_not_found_exception(self):
        """Test ResourceNotFoundException."""
        with pytest.raises(ResourceNotFoundException) as exc_info:
            raise ResourceNotFoundException("User not found")

        assert "User not found" in str(exc_info.value)
        assert exc_info.value.http_code == 404

    def test_duplicate_resource_exception(self):
        """Test DuplicateResourceException."""
        with pytest.raises(DuplicateResourceException) as exc_info:
            raise DuplicateResourceException("User already exists")

        assert "User already exists" in str(exc_info.value)
        assert exc_info.value.http_code == 409

    def test_rate_limit_exception(self):
        """Test RateLimitException."""
        with pytest.raises(RateLimitException) as exc_info:
            raise RateLimitException("Too many requests")

        assert "Too many requests" in str(exc_info.value)
        assert exc_info.value.http_code == 429

    # Test all 15 exceptions...
```

---

## 📝 PASO 5: Verificar Cobertura y Crear Reporte

### Comandos de Verificación

```bash
# 1. Ejecutar todos los tests
python -m pytest -v

# 2. Ejecutar con cobertura
python -m pytest --cov=infocodest --cov-report=html --cov-report=term

# 3. Verificar cobertura mínima
python -m pytest --cov=infocodest --cov-report=term --cov-fail-under=80

# 4. Ver reporte HTML
# Abrir: htmlcov/index.html
```

### Métricas de Cobertura Esperadas

| Módulo | Cobertura Objetivo | Tests |
|--------|-------------------|-------|
| `repositories/` | >85% | 30+ tests |
| `services/` | >80% | 20+ tests |
| `utils/validators.py` | >90% | 20+ tests |
| `utils/helpers.py` | >85% | 20+ tests |
| `utils/decorators.py` | >80% | 10+ tests |
| `exceptions/` | 100% | 15+ tests |
| `home/views.py` (refactored) | >75% | 15+ tests |
| **TOTAL** | **>80%** | **130+ tests** |

### Reporte de Cobertura

El comando generará un reporte detallado mostrando:
- Líneas cubiertas vs totales por módulo
- Porcentaje de cobertura
- Líneas sin cubrir (para identificar gaps)

---

## 📝 PASO 6: Actualizar Tests Existentes

### Objetivo

Actualizar tests funcionales existentes para usar service layer en lugar de acceso directo a DB.

### Archivos a Modificar

#### `tests/funcional/test_home.py`

**Antes** (acceso directo a DB):
```python
def test_index(test_client, login_in_user, init_database):
    response = test_client.get('/')
    # Direct DB query in test
    metricas = Metrica.query.all()
    assert len(metricas) > 0
```

**Después** (verifica uso de service layer):
```python
def test_index_uses_service_layer(test_client, login_in_user, init_database):
    """Test that index view uses service layer."""
    response = test_client.get('/')
    assert response.status_code == 200
    # Verify that view injected service (no direct ORM calls)
    # Service layer handles all data access
```

### Tests a Actualizar

1. `test_home.py` - Verificar uso de `DashboardService`
2. `test_api.py` - Actualizar para usar service layer
3. Cualquier test que haga queries directas a ORM

---

## 🎯 Criterios de Éxito

### Tests Deben Pasar

- [x] Todos los tests unitarios pasan (repositories, services, utils, exceptions)
- [x] Todos los tests de integración pasan
- [x] Tests existentes actualizados y pasan
- [x] No hay tests con warnings

### Cobertura

- [x] Cobertura total >80%
- [x] Cobertura repositories >85%
- [x] Cobertura services >80%
- [x] Cobertura utils >85%
- [x] Cobertura exceptions 100%

### Calidad

- [x] Tests bien documentados (docstrings)
- [x] Tests independientes (no dependen del orden)
- [x] Fixtures reutilizables en `conftest.py`
- [x] Uso correcto de mocks en tests unitarios
- [x] Tiempo de ejecución <10 segundos

---

## 📊 Resumen de Archivos a Crear/Modificar

### Nuevos Archivos (13)

```
tests/
├── unit/
│   ├── test_repositories/
│   │   ├── __init__.py                    # Nuevo
│   │   ├── test_base_repository.py        # Nuevo - 15 tests
│   │   ├── test_dashboard_repository.py   # Nuevo - 20 tests
│   │   └── test_metrica_repository.py     # Nuevo - 10 tests
│   │
│   ├── test_services/
│   │   ├── __init__.py                    # Nuevo
│   │   └── test_dashboard_service.py      # Nuevo - 20 tests
│   │
│   ├── test_utils/
│   │   ├── __init__.py                    # Nuevo
│   │   ├── test_validators.py             # Nuevo - 20 tests
│   │   ├── test_helpers.py                # Nuevo - 20 tests
│   │   └── test_decorators.py             # Nuevo - 10 tests
│   │
│   └── test_exceptions/
│       ├── __init__.py                    # Nuevo
│       └── test_business_exceptions.py    # Nuevo - 15 tests
│
└── integration/
    ├── __init__.py                        # Nuevo
    └── test_home_views.py                 # Nuevo - 15 tests
```

### Archivos a Modificar (3)

```
tests/
├── conftest.py                            # Modificar - Añadir fixtures
├── funcional/test_home.py                 # Modificar - Actualizar tests
└── funcional/test_api.py                  # Modificar - Actualizar tests
```

**Total**: 13 archivos nuevos + 3 modificados = **16 archivos**

---

## ⏱️ Estimación de Tiempo

| Paso | Actividad | Duración |
|------|-----------|----------|
| 2 | Tests de repositories (3 archivos, 45 tests) | 45 min |
| 3 | Tests de services (1 archivo, 20 tests) | 30 min |
| 4a | Tests de integración (1 archivo, 15 tests) | 30 min |
| 4b | Tests de utils (3 archivos, 50 tests) | 45 min |
| 4c | Tests de excepciones (1 archivo, 15 tests) | 20 min |
| 5 | Verificar cobertura y ajustes | 20 min |
| 6 | Actualizar tests existentes | 20 min |
| 7 | Crear reporte de fase | 20 min |

**Total estimado**: ~3 horas y 10 minutos

---

## 📚 Recursos y Referencias

### Documentación de Testing

- **pytest**: https://docs.pytest.org/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **Flask testing**: https://flask.palletsprojects.com/en/2.3.x/testing/

### Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **FIRST Principles**: Fast, Independent, Repeatable, Self-validating, Timely
3. **One assertion per test** (cuando sea posible)
4. **Clear test names**: `test_<function>_<scenario>_<expected_result>`
5. **Use fixtures** para setup/teardown
6. **Mock external dependencies**

### Comandos Útiles

```bash
# Ejecutar solo tests unitarios
pytest tests/unit -v

# Ejecutar solo tests de integración
pytest tests/integration -v

# Ejecutar tests con pattern
pytest -k "test_repository" -v

# Ver coverage de módulo específico
pytest --cov=infocodest.repositories --cov-report=term

# Generar reporte HTML
pytest --cov=infocodest --cov-report=html
open htmlcov/index.html  # Ver en navegador
```

---

## ✅ Checklist de Completación

### Tests Implementados

- [ ] Tests de BaseRepository (15 tests)
- [ ] Tests de DashboardRepository (20 tests)
- [ ] Tests de MetricaRepository (10 tests)
- [ ] Tests de DashboardService (20 tests)
- [ ] Tests de validators (20 tests)
- [ ] Tests de helpers (20 tests)
- [ ] Tests de decorators (10 tests)
- [ ] Tests de excepciones (15 tests)
- [ ] Tests de integración home views (15 tests)

### Calidad

- [ ] Todos los tests pasan sin errores
- [ ] Cobertura total >80%
- [ ] Tiempo de ejecución <10s
- [ ] No hay warnings en pytest
- [ ] Tests bien documentados

### Documentación

- [ ] Plan detallado creado
- [ ] Reporte de fase creado
- [ ] CHANGELOG actualizado
- [ ] README actualizado con métricas

### Git

- [ ] Commits siguen Conventional Commits
- [ ] Branch pusheado a remoto
- [ ] PR creado
- [ ] Tag creado

---

## 🎯 Resultado Esperado

Al finalizar la Fase 9, tendremos:

✅ **130+ tests nuevos** cubriendo todas las capas refactorizadas
✅ **Cobertura >80%** validada con pytest-cov
✅ **Suite de tests rápida** (<10s) y confiable
✅ **Tests mantenibles** con fixtures y mocks
✅ **Documentación completa** de estrategia de testing

Esto nos prepara para la **Fase 10 (final)**: Documentación y Limpieza.

---

**Versión del Plan**: 1.0
**Última actualización**: 2025-12-13
**Autor**: Claude Code (AI Assistant)
**Próximo paso**: PASO 2 - Implementar tests de repositories
