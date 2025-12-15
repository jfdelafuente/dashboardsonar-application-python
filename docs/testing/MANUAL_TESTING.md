# Manual de Usuario - Testing Dashboard Sonar

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos Previos](#requisitos-previos)
3. [Configuración del Entorno de Testing](#configuración-del-entorno-de-testing)
4. [Ejecución de Tests](#ejecución-de-tests)
5. [Validación del Entorno y Configuración](#validación-del-entorno-y-configuración)
6. [Evaluación de Tests Existentes](#evaluación-de-tests-existentes)
7. [Plan de Elaboración de Nuevos Tests](#plan-de-elaboración-de-nuevos-tests)
8. [Mejores Prácticas](#mejores-prácticas)
9. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

Este manual proporciona una guía completa para ejecutar, validar y desarrollar tests en el proyecto Dashboard Sonar. El sistema de testing utiliza **pytest** con fixtures personalizadas y está organizado en dos categorías principales:

- **Tests Unitarios** (`tests/unit/`): Prueban componentes individuales de forma aislada
- **Tests Funcionales** (`tests/funcional/`): Prueban flujos completos de la aplicación

---

## Requisitos Previos

### Software Necesario

```bash
Python 3.11+
pip (gestor de paquetes)
virtualenv (recomendado)
Git
```

### Dependencias de Testing

Las dependencias se encuentran en `requirements-dev.txt`:

```
pytest==7.4.3           # Framework de testing
pytest-cov==4.1.0       # Cobertura de código
pytest-mock==3.12.0     # Mocks y patches
pytest-flask==1.3.0     # Integración con Flask
Flask-Testing==0.8.1    # Herramientas de testing para Flask
```

### Instalación de Dependencias

```bash
# Activar entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar dependencias de desarrollo (incluye testing)
pip install -r requirements-dev.txt
```

---

## Configuración del Entorno de Testing

### 1. Configuración de Base de Datos de Testing

El proyecto utiliza una base de datos SQLite separada para testing:

```python
# config/testing.py
class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testdb.sqlite3'
    WTF_CSRF_ENABLED = False
    BCRYPT_LOG_ROUNDS = 1  # Acelera hashing de contraseñas en tests
```

**Características:**
- Base de datos independiente (`testdb.sqlite3`)
- CSRF deshabilitado para facilitar tests
- Bcrypt optimizado (1 round en lugar de 12)
- Se crea y destruye automáticamente en cada test

### 2. Fixtures Disponibles

El archivo `tests/conftest.py` proporciona fixtures reutilizables:

```python
# Fixtures principales
@pytest.fixture
def app():
    """Aplicación Flask configurada para testing"""

@pytest.fixture
def test_client(app):
    """Cliente de testing HTTP"""

@pytest.fixture
def init_database(test_client):
    """Base de datos inicializada con datos de prueba"""

@pytest.fixture
def new_user():
    """Usuario de prueba (modelo User)"""

@pytest.fixture
def login_in_user(test_client):
    """Sesión de usuario autenticado"""
```

**Uso de fixtures:**

```python
def test_example(test_client, init_database):
    """
    test_client: proporciona cliente HTTP
    init_database: crea BD y datos de prueba
    """
    response = test_client.get('/metricas')
    assert response.status_code == 200
```

### 3. Variables de Entorno para Testing

Crear archivo `.env.test` (opcional):

```bash
# .env.test
FLASK_ENV=testing
SECRET_KEY=test-secret-key-change-in-production
DAYS=15
```

---

## Ejecución de Tests

### Comandos Básicos

#### Ejecutar todos los tests

```bash
pytest
```

#### Ejecutar tests con salida detallada

```bash
pytest -v
```

#### Ejecutar tests de una categoría específica

```bash
# Solo tests unitarios
pytest tests/unit/

# Solo tests funcionales
pytest tests/funcional/

# Tests de un módulo específico
pytest tests/unit/test_services/
```

#### Ejecutar un archivo de test específico

```bash
pytest tests/unit/test_config.py
```

#### Ejecutar un test específico

```bash
pytest tests/unit/test_config.py::test_development_config
```

### Ejecución con Cobertura de Código

#### Generar reporte de cobertura básico

```bash
pytest --cov=infocodest tests/
```

#### Generar reporte de cobertura detallado

```bash
pytest --cov=infocodest --cov-report=html tests/
```

Esto genera un reporte HTML en `htmlcov/index.html` que puedes abrir en el navegador.

#### Generar reporte de cobertura con porcentajes

```bash
pytest --cov=infocodest --cov-report=term-missing tests/
```

Muestra líneas específicas que no están cubiertas.

### Opciones Útiles de pytest

```bash
# Detener en el primer fallo
pytest -x

# Mostrar solo resumen
pytest -q

# Mostrar print statements durante tests
pytest -s

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n auto

# Ejecutar solo tests que fallaron la última vez
pytest --lf

# Ejecutar tests que fallaron + todos los que no se ejecutaron
pytest --ff

# Marcar tests lentos y ejecutar solo los rápidos
pytest -m "not slow"
```

### Estructura de Salida

```bash
$ pytest -v tests/

tests/unit/test_config.py::test_development_config PASSED      [ 10%]
tests/unit/test_config.py::test_testing_config PASSED          [ 20%]
tests/unit/test_config.py::test_production_config PASSED       [ 30%]
tests/unit/test_user_model.py::test_create_user PASSED         [ 40%]
tests/unit/test_user_model.py::test_new_user PASSED            [ 50%]
tests/funcional/test_home.py::test_metricas_page PASSED        [ 60%]
...

========================= 20 passed in 2.45s =========================
```

---

## Validación del Entorno y Configuración

### 1. Script de Verificación de Dependencias

Ejecutar antes de los tests para asegurar que todas las dependencias están instaladas:

```bash
python scripts/verification/verify_dependencies.py
```

**Salida esperada:**

```
============================================================
Dependency Verification - Dashboard Sonar
============================================================

Production Dependencies:
------------------------------------------------------------
[OK] alembic 1.12.1 (>= 1.12.0)
[OK] bcrypt 4.1.2 (>= 4.0.0)
[OK] email-validator 2.1.0 (>= 2.1.0)
[OK] flask 3.0.0 (>= 3.0.0)
[OK] flask-bcrypt 1.0.1 (>= 1.0.0)
[OK] flask-login 0.6.3 (>= 0.6.0)
[OK] flask-migrate 4.0.5 (>= 4.0.0)
[OK] flask-sqlalchemy 3.1.1 (>= 3.1.0)
[OK] flask-wtf 1.2.1 (>= 1.2.0)
[OK] python-decouple 3.8 (>= 3.8)
[OK] schedule 1.2.0 (>= 1.2.0)
[OK] sqlalchemy 2.0.23 (>= 2.0.0)
[OK] wtforms 3.1.1 (>= 3.1.0)

Development Dependencies (optional):
------------------------------------------------------------
[OK] black 23.12.0 (>= 23.12.0)
[OK] flake8 6.1.0 (>= 6.1.0)
[OK] mypy 1.7.1 (>= 1.7.0)
[OK] pytest 7.4.3 (>= 7.4.0)
[OK] pytest-cov 4.1.0 (>= 4.1.0)

============================================================
[SUCCESS] All dependencies verified!
  Production dependencies: OK
  Development dependencies: OK
============================================================
```

**Si hay errores:**

```bash
[FAIL] pytest not installed
Run: pip install -r requirements-dev.txt
```

### 2. Script de Verificación de Configuración

Verifica que todas las configuraciones cargan correctamente:

```bash
python scripts/verification/verify_config.py
```

**Salida esperada:**

```
============================================================
Configuration Verification
============================================================

[TEST 1] Importing config classes...
[OK] All config classes imported successfully

[TEST 2] Verifying config_dict structure...
[OK] config_dict has all expected keys: {'Production', 'Testing', 'Development', 'base'}

[TEST 3] Verifying required attributes...
  Testing base...
  [OK] base: All required attributes present
  Testing Development...
  [OK] Development: All required attributes present
  Testing Testing...
  [OK] Testing: All required attributes present
  Testing Production...
  [OK] Production: All required attributes present

[TEST 4] Verifying inheritance...
  [OK] DevelopmentConfig inherits from BaseConfig
  [OK] TestingConfig inherits from BaseConfig
  [OK] ProductionConfig inherits from BaseConfig

[TEST 5] Verifying environment-specific settings...
  [OK] DevelopmentConfig has DEBUG=True
  [OK] ProductionConfig has DEBUG=False
  [OK] TestingConfig has TESTING=True

============================================================
[SUCCESS] All configurations verified!
[INFO] 4 configuration classes validated
============================================================
```

### 3. Verificación Manual de Fixtures

Ejecutar test que verifica fixtures:

```bash
pytest tests/conftest.py -v
```

O crear un test rápido:

```python
# tests/test_fixtures_validation.py
def test_app_fixture(app):
    """Verifica que la aplicación se crea correctamente"""
    assert app is not None
    assert app.config['TESTING'] is True

def test_test_client_fixture(test_client):
    """Verifica que el cliente de prueba funciona"""
    response = test_client.get('/metricas')
    assert response is not None

def test_init_database_fixture(init_database, test_client):
    """Verifica que la BD se inicializa con datos"""
    from infocodest.models.users import User
    from infocodest.extensions import db

    users = db.session.query(User).all()
    assert len(users) >= 1
```

### 4. Checklist de Validación Pre-Testing

Antes de ejecutar tests, verificar:

- [ ] Entorno virtual activado
- [ ] Dependencias instaladas (`verify_dependencies.py` pasa)
- [ ] Configuraciones válidas (`verify_config.py` pasa)
- [ ] Base de datos de testing no existe o está limpia
- [ ] Variables de entorno configuradas (si es necesario)
- [ ] Puerto 5000 disponible (para tests funcionales)

---

## Evaluación de Tests Existentes

### Inventario de Tests Actuales

#### Tests Unitarios (17 archivos)

**1. Configuración (`tests/unit/test_config.py`)**
- `test_development_config()`: Verifica configuración Development
- `test_testing_config()`: Verifica configuración Testing
- `test_production_config()`: Verifica configuración Production
- **Estado**: ✅ Completo
- **Cobertura**: 100% de configuraciones

**2. Modelo de Usuario (`tests/unit/test_user_model.py`)**
- `test_create_user()`: Creación de usuario en BD
- `test_new_user()`: Instanciación de modelo User
- `test_new_user_with_fixture()`: Uso de fixture new_user
- **Estado**: ✅ Completo
- **Cobertura**: Básica (crea, no actualiza ni elimina)

**3. Formularios (`tests/unit/test_form.py`)**
- **Estado**: ⚠️ No revisado en detalle
- **Prioridad**: Media

**4. Excepciones (`tests/unit/test_exceptions/test_business_exceptions.py`)**
- **Estado**: ✅ Implementado
- **Cobertura**: Excepciones de negocio personalizadas

**5. Repositorios**

- **BaseRepository** (`tests/unit/test_repositories/test_base_repository.py`)
  - **Estado**: ✅ Implementado
  - **Cobertura**: CRUD completo, paginación, filtros

- **MetricaRepository** (`tests/unit/test_repositories/test_metrica_repository.py`)
  - 15+ tests de métodos específicos
  - **Cobertura**: Queries específicas, agregaciones, filtros
  - **Estado**: ✅ Excelente cobertura

**6. Servicios (`tests/unit/test_services/test_dashboard_service.py`)**
- 15+ tests de DashboardService
- Tests de KPIs (overview, por aplicación, por proveedor, por repositorio)
- Tests de cálculo de variaciones porcentuales
- Tests de manejo de división por cero
- **Estado**: ✅ Excelente cobertura con mocks
- **Cobertura**: Lógica de negocio aislada

**7. Utilidades (`tests/unit/test_utils/test_validators.py`)**
- **Estado**: ✅ Implementado
- **Cobertura**: Validadores personalizados

#### Tests Funcionales (5 archivos)

**1. Home (`tests/funcional/test_home.py`)**
- `test_metricas_page()`: GET /metricas
- `test_metricas_page_login()`: GET /metricas con auth
- `test_proveedores_metricas_page()`: GET /proveedores
- `test_historico_metricas_page()`: GET /historico
- **Estado**: ⚠️ Parcial (algunos tests comentados)
- **Cobertura**: Rutas principales sin autenticación

**2. Account Login (`tests/funcional/test_account_login.py`)**
- **Estado**: ⚠️ No revisado
- **Prioridad**: Alta (seguridad)

**3. Account Page (`tests/funcional/test_account_page.py`)**
- **Estado**: ⚠️ No revisado
- **Prioridad**: Media

**4. Auth (`tests/funcional/test_auth.py`)**
- **Estado**: ⚠️ No revisado
- **Prioridad**: Alta (seguridad)

**5. API (`tests/funcional/test_api.py`)**
- **Estado**: ⚠️ No revisado
- **Prioridad**: Alta (endpoints API)

### Métricas de Cobertura Actual

Para generar métricas actuales:

```bash
pytest --cov=infocodest --cov-report=term-missing tests/
```

**Interpretación de resultados:**

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
infocodest/__init__.py                     15      2    87%   23-24
infocodest/models/users.py                 25      0   100%
infocodest/repositories/base.py            45      5    89%   67-71
infocodest/services/dashboard_service.py   120     15    88%   145-160
---------------------------------------------------------------------
TOTAL                                     850    125    85%
```

- **Stmts**: Líneas de código ejecutables
- **Miss**: Líneas no cubiertas
- **Cover**: Porcentaje de cobertura
- **Missing**: Rangos de líneas sin cobertura

**Objetivos de cobertura recomendados:**
- Modelos: 90-100%
- Repositorios: 85-95%
- Servicios: 80-90%
- Vistas/Controllers: 70-85%
- Utilidades: 90-100%

### Análisis de Calidad de Tests

**Fortalezas:**
1. ✅ Uso consistente de fixtures
2. ✅ Tests unitarios bien aislados con mocks
3. ✅ Nombres descriptivos de tests
4. ✅ Docstrings en tests importantes
5. ✅ Separación clara unit/funcional
6. ✅ Tests de servicios con buena cobertura de casos edge

**Debilidades identificadas:**
1. ⚠️ Tests funcionales incompletos (muchos comentados)
2. ⚠️ Falta cobertura de API endpoints
3. ⚠️ No hay tests de integración con base de datos real
4. ⚠️ Tests de autenticación/seguridad insuficientes
5. ⚠️ No hay tests de rendimiento
6. ⚠️ Falta cobertura de casos de error en vistas

---

## Plan de Elaboración de Nuevos Tests

### Metodología de Priorización

Cada test nuevo se evalúa con 3 criterios:

1. **Necesidad** (1-5): ¿Qué tan crítico es?
   - 5: Crítico (seguridad, pérdida de datos)
   - 4: Muy importante (funcionalidad core)
   - 3: Importante (features principales)
   - 2: Deseable (features secundarias)
   - 1: Nice-to-have (mejoras)

2. **Prioridad** (Alta/Media/Baja): ¿Cuándo implementar?
   - Alta: Sprint actual
   - Media: Próximos 2 sprints
   - Baja: Backlog

3. **Dificultad** (1-5): ¿Qué tan complejo?
   - 1: Muy fácil (< 1 hora)
   - 2: Fácil (1-2 horas)
   - 3: Media (2-4 horas)
   - 4: Difícil (4-8 horas)
   - 5: Muy difícil (> 8 horas)

### Fase 1: Tests Críticos (Sprint 1-2)

#### 1.1 Autenticación y Seguridad
**Necesidad: 5 | Prioridad: Alta | Dificultad: 3**

```python
# tests/funcional/test_auth_complete.py

def test_login_success(test_client, init_database):
    """Usuario puede hacer login con credenciales válidas"""

def test_login_invalid_credentials(test_client, init_database):
    """Login falla con credenciales inválidas"""

def test_login_sql_injection_protection(test_client, init_database):
    """Sistema protege contra SQL injection en login"""

def test_logout_clears_session(test_client, init_database, login_in_user):
    """Logout limpia la sesión correctamente"""

def test_protected_route_requires_auth(test_client):
    """Rutas protegidas redirigen a login si no autenticado"""

def test_session_timeout(test_client, init_database):
    """Sesión expira después del tiempo configurado"""

def test_csrf_protection(test_client, init_database):
    """Formularios validan token CSRF"""
```

**Estimación:** 6-8 horas

#### 1.2 API Endpoints Críticos
**Necesidad: 5 | Prioridad: Alta | Dificultad: 3**

```python
# tests/funcional/test_api_endpoints.py

def test_api_authentication_required(test_client):
    """API requiere autenticación"""

def test_api_get_metricas(test_client, init_database, login_in_user):
    """GET /api/metricas retorna datos correctos"""

def test_api_get_metricas_pagination(test_client, init_database, login_in_user):
    """API soporta paginación"""

def test_api_filter_by_aplicacion(test_client, init_database, login_in_user):
    """API filtra por aplicación correctamente"""

def test_api_invalid_params_return_400(test_client, init_database, login_in_user):
    """API retorna 400 con parámetros inválidos"""

def test_api_rate_limiting(test_client, init_database, login_in_user):
    """API tiene rate limiting configurado"""
```

**Estimación:** 6-8 horas

#### 1.3 Modelos de Datos Core
**Necesidad: 4 | Prioridad: Alta | Dificultad: 2**

```python
# tests/unit/test_metrica_model.py

def test_create_metrica(init_database):
    """Crear métrica con todos los campos"""

def test_metrica_unique_constraint(init_database):
    """Constraint único en repo se valida"""

def test_metrica_relationships(init_database):
    """Relaciones con otras tablas funcionan"""

# tests/unit/test_daily_model.py

def test_create_daily_snapshot(init_database):
    """Crear snapshot diario"""

def test_daily_allows_multiple_per_app(init_database):
    """Permite múltiples registros por aplicación (diferentes fechas)"""

def test_daily_composite_index(init_database):
    """Índice compuesto (aplicacion, created_on) funciona"""

# tests/unit/test_historico_model.py

def test_create_historico(init_database):
    """Crear registro histórico"""

def test_historico_append_only(init_database):
    """Histórico es append-only (no se actualiza)"""
```

**Estimación:** 4-6 horas

### Fase 2: Tests Importantes (Sprint 3-4)

#### 2.1 Servicios de Datos
**Necesidad: 4 | Prioridad: Media | Dificultad: 3**

```python
# tests/unit/test_services/test_metrica_service.py

def test_load_metricas_from_sonarqube(mock_requests):
    """Cargar métricas desde SonarQube API"""

def test_transform_metricas_data(mock_raw_data):
    """Transformar datos crudos a modelo Metrica"""

def test_handle_api_errors_gracefully(mock_requests_error):
    """Manejo de errores de API externa"""

# tests/unit/test_services/test_daily_snapshot_service.py

def test_create_daily_snapshot():
    """Crear snapshot diario de todas las aplicaciones"""

def test_prevent_duplicate_daily_snapshot():
    """No crear snapshot duplicado para mismo día"""

def test_calculate_daily_aggregations():
    """Calcular agregaciones diarias correctamente"""
```

**Estimación:** 6-8 horas

#### 2.2 ETL y Carga de Datos
**Necesidad: 4 | Prioridad: Media | Dificultad: 4**

```python
# tests/integration/test_etl_metricas.py

def test_extract_from_csv():
    """Extraer datos de CSV correctamente"""

def test_transform_metricas():
    """Transformar métricas según reglas de negocio"""

def test_load_to_database():
    """Cargar datos transformados a BD"""

def test_etl_full_pipeline():
    """Pipeline ETL completo funciona end-to-end"""

# tests/integration/test_data_loaders.py

def test_truncate_and_load_proveedores():
    """Carga completa de proveedores (truncate & load)"""

def test_append_only_historico():
    """Carga incremental de histórico (append only)"""

def test_daily_upsert():
    """Upsert diario (insert o update)"""

def test_derived_stats_regeneration():
    """Regeneración de stats derivadas"""
```

**Estimación:** 8-12 horas

#### 2.3 Vistas y Templates
**Necesidad: 3 | Prioridad: Media | Dificultad: 2**

```python
# tests/funcional/test_dashboard_views.py

def test_home_page_displays_kpis(test_client, init_database):
    """Home muestra KPIs principales"""

def test_metricas_page_table(test_client, init_database):
    """Página métricas muestra tabla de datos"""

def test_metricas_pagination(test_client, init_database):
    """Paginación funciona correctamente"""

def test_filter_by_aplicacion(test_client, init_database):
    """Filtro por aplicación funciona"""

def test_filter_by_proveedor(test_client, init_database):
    """Filtro por proveedor funciona"""

def test_error_page_404(test_client):
    """Página 404 se muestra correctamente"""

def test_error_page_500(test_client):
    """Página 500 se muestra en errores de servidor"""
```

**Estimación:** 4-6 horas

### Fase 3: Tests Complementarios (Sprint 5-6)

#### 3.1 Validaciones y Formularios
**Necesidad: 3 | Prioridad: Media | Dificultad: 2**

```python
# tests/unit/test_forms_validation.py

def test_login_form_validates_email():
    """Formulario login valida formato email"""

def test_login_form_requires_password():
    """Formulario login requiere contraseña"""

def test_filter_form_validates_dates():
    """Formulario filtros valida rangos de fechas"""

def test_user_form_validates_username_unique():
    """Formulario usuario valida username único"""
```

**Estimación:** 3-4 horas

#### 3.2 Utilidades y Helpers
**Necesidad: 3 | Prioridad: Baja | Dificultad: 2**

```python
# tests/unit/test_utils/test_date_helpers.py

def test_calculate_date_range():
    """Calcular rango de fechas correctamente"""

def test_format_date_for_display():
    """Formatear fechas para visualización"""

def test_parse_date_from_sonarqube():
    """Parsear fechas de SonarQube API"""

# tests/unit/test_utils/test_security_helpers.py

def test_sanitize_input():
    """Sanitizar input de usuario"""

def test_validate_permissions():
    """Validar permisos de usuario"""
```

**Estimación:** 3-4 horas

#### 3.3 Migraciones de Base de Datos
**Necesidad: 3 | Prioridad: Baja | Dificultad: 3**

```python
# tests/integration/test_migrations.py

def test_migration_stats_repos_constraint():
    """Migración fix_stats_repos_constraint funciona"""

def test_migration_daily_repo_constraint():
    """Migración fix_daily_repo_constraint funciona"""

def test_migration_daily_aplicacion_constraint():
    """Migración fix_daily_aplicacion_constraint funciona"""

def test_migrations_are_idempotent():
    """Migraciones pueden ejecutarse múltiples veces sin errores"""
```

**Estimación:** 6-8 horas

### Fase 4: Tests Avanzados (Backlog)

#### 4.1 Tests de Rendimiento
**Necesidad: 2 | Prioridad: Baja | Dificultad: 4**

```python
# tests/performance/test_dashboard_performance.py

def test_kpi_calculation_performance():
    """Cálculo de KPIs completa en < 2 segundos"""

def test_metricas_query_with_1000_records():
    """Query de métricas con 1000 registros < 1 segundo"""

def test_concurrent_users_load(locust_test):
    """Sistema soporta 50 usuarios simultáneos"""
```

**Estimación:** 12-16 horas

#### 4.2 Tests End-to-End
**Necesidad: 2 | Prioridad: Baja | Dificultad: 5**

```python
# tests/e2e/test_user_workflows.py (usando Selenium/Playwright)

def test_user_login_and_view_dashboard():
    """Usuario puede hacer login y ver dashboard"""

def test_user_filters_metricas_by_date():
    """Usuario filtra métricas por rango de fechas"""

def test_user_exports_data_to_csv():
    """Usuario exporta datos a CSV"""
```

**Estimación:** 16-20 horas

### Resumen de Prioridades

| Fase | Categoría | Necesidad | Prioridad | Dificultad | Estimación |
|------|-----------|-----------|-----------|------------|------------|
| 1 | Autenticación y Seguridad | 5 | Alta | 3 | 6-8h |
| 1 | API Endpoints Críticos | 5 | Alta | 3 | 6-8h |
| 1 | Modelos de Datos Core | 4 | Alta | 2 | 4-6h |
| 2 | Servicios de Datos | 4 | Media | 3 | 6-8h |
| 2 | ETL y Carga de Datos | 4 | Media | 4 | 8-12h |
| 2 | Vistas y Templates | 3 | Media | 2 | 4-6h |
| 3 | Validaciones y Formularios | 3 | Media | 2 | 3-4h |
| 3 | Utilidades y Helpers | 3 | Baja | 2 | 3-4h |
| 3 | Migraciones BD | 3 | Baja | 3 | 6-8h |
| 4 | Tests de Rendimiento | 2 | Baja | 4 | 12-16h |
| 4 | Tests End-to-End | 2 | Baja | 5 | 16-20h |

**Total estimado:** 75-100 horas de desarrollo de tests

### Roadmap de Implementación

**Sprint 1-2 (3-4 semanas): Fase 1 - Tests Críticos**
- Semana 1: Autenticación y Seguridad
- Semana 2: API Endpoints
- Semana 3-4: Modelos de Datos Core

**Sprint 3-4 (4-6 semanas): Fase 2 - Tests Importantes**
- Semana 5-6: Servicios de Datos
- Semana 7-8: ETL y Carga de Datos
- Semana 9-10: Vistas y Templates

**Sprint 5-6 (4-6 semanas): Fase 3 - Tests Complementarios**
- Semana 11-12: Validaciones y Formularios
- Semana 13: Utilidades y Helpers
- Semana 14-15: Migraciones BD

**Backlog (cuando sea necesario): Fase 4 - Tests Avanzados**
- Performance testing
- End-to-end testing

---

## Mejores Prácticas

### 1. Nomenclatura de Tests

**Convención de nombres:**

```python
def test_<what>_<condition>_<expected_result>():
    """Docstring explicando el test"""
    pass

# Ejemplos:
def test_login_valid_credentials_redirects_to_home():
    """Usuario con credenciales válidas es redirigido a home"""

def test_create_user_duplicate_email_raises_error():
    """Crear usuario con email duplicado lanza IntegrityError"""
```

### 2. Estructura de Tests (Arrange-Act-Assert)

```python
def test_example():
    # ARRANGE: Preparar datos y mocks
    user = User(username='test', email='test@example.com')
    db.session.add(user)
    db.session.commit()

    # ACT: Ejecutar la acción a probar
    result = user_service.get_user_by_username('test')

    # ASSERT: Verificar el resultado
    assert result is not None
    assert result.username == 'test'
    assert result.email == 'test@example.com'
```

### 3. Uso de Mocks

**Cuándo usar mocks:**
- APIs externas (SonarQube)
- Servicios de email
- Sistema de archivos
- Dependencias lentas

**Ejemplo:**

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_fetch_from_sonarqube(mock_get):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'test'}
    mock_get.return_value = mock_response

    # Act
    result = sonarqube_service.fetch_metrics()

    # Assert
    assert result == {'data': 'test'}
    mock_get.assert_called_once()
```

### 4. Limpieza de Datos de Test

```python
@pytest.fixture
def clean_database(test_client):
    """Fixture que limpia la BD después del test"""
    db.create_all()

    yield

    # Cleanup
    db.session.remove()
    db.drop_all()
```

### 5. Tests Parametrizados

Para probar múltiples casos similares:

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("admin", True),
    ("user", False),
    ("guest", False),
])
def test_is_admin(input, expected):
    user = User(username=input, is_admin=expected)
    assert user.is_admin == expected
```

### 6. Markers para Organizar Tests

```python
# Marcar tests lentos
@pytest.mark.slow
def test_complex_calculation():
    pass

# Marcar tests de integración
@pytest.mark.integration
def test_database_connection():
    pass

# Ejecutar solo tests rápidos:
# pytest -m "not slow"
```

### 7. Documentación de Tests

```python
def test_user_login_flow(test_client, init_database):
    """
    Test del flujo completo de login de usuario.

    Given: Un usuario registrado en la base de datos
    When: El usuario envía credenciales válidas
    Then: Es redirigido a la página de inicio
    And: La sesión contiene el user_id
    """
    # Test implementation...
```

---

## Solución de Problemas

### Problema 1: Tests fallan con "Database is locked"

**Causa:** SQLite tiene limitaciones de concurrencia

**Solución:**

```python
# config/testing.py
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Usar BD en memoria
```

O ejecutar tests secuencialmente:

```bash
pytest -n 0  # Deshabilitar ejecución paralela
```

### Problema 2: Fixture 'app' not found

**Causa:** `conftest.py` no se está cargando

**Solución:**

1. Verificar que `tests/__init__.py` existe
2. Ejecutar pytest desde el directorio raíz del proyecto
3. Verificar PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Problema 3: Import errors en tests

**Causa:** Módulos no se encuentran

**Solución:**

```python
# Agregar al inicio de conftest.py
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### Problema 4: Tests pasan localmente pero fallan en CI

**Causa:** Diferencias de entorno

**Solución:**

1. Verificar versiones de dependencias:

```bash
pip freeze > requirements-lock.txt
```

2. Usar misma versión de Python en CI
3. Configurar variables de entorno en CI

### Problema 5: Cobertura reporta números incorrectos

**Causa:** Archivos no incluidos en medición

**Solución:**

Crear archivo `.coveragerc`:

```ini
[run]
source = infocodest
omit =
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

### Problema 6: Tests muy lentos

**Solución:**

1. Usar BD en memoria:

```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

2. Reducir BCRYPT_LOG_ROUNDS en testing:

```python
BCRYPT_LOG_ROUNDS = 1
```

3. Usar mocks para operaciones lentas
4. Ejecutar tests en paralelo:

```bash
pip install pytest-xdist
pytest -n auto
```

---

## Recursos Adicionales

### Documentación Oficial

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/3.0.x/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

### Tutoriales Recomendados

- [Real Python - Testing Flask Applications](https://realpython.com/flask-testing/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

### Herramientas Complementarias

- **pytest-watch**: Auto-ejecuta tests cuando cambian archivos
- **pytest-xdist**: Ejecución paralela de tests
- **pytest-benchmark**: Tests de rendimiento
- **Hypothesis**: Property-based testing
- **Faker**: Generación de datos de prueba

---

## Conclusión

Este manual proporciona una guía completa para:

1. ✅ **Ejecutar tests** en diferentes modalidades
2. ✅ **Validar el entorno** antes de testing
3. ✅ **Evaluar tests existentes** con métricas detalladas
4. ✅ **Planificar nuevos tests** con prioridades y estimaciones

### Próximos Pasos Recomendados

1. Ejecutar verificación de entorno: `python scripts/verification/verify_dependencies.py`
2. Generar reporte de cobertura actual: `pytest --cov=infocodest --cov-report=html tests/`
3. Revisar tests de Fase 1 (Críticos) y comenzar implementación
4. Establecer objetivo de cobertura mínima (recomendado: 80%)
5. Integrar tests en pipeline CI/CD

---

**Versión:** 1.0
**Fecha:** 2025-12-15
**Autor:** Dashboard Sonar Team
**Revisión:** Pendiente
