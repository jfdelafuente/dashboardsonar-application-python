# Dashboard Sonar - Flask Application

> Aplicación web para visualización y análisis de métricas de calidad de código desde SonarQube

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-automated-brightgreen.svg)](.github/workflows/)
[![Refactoring](https://img.shields.io/badge/refactoring-100%25%20complete-brightgreen.svg)](docs/plan/PLAN_REORGANIZACION.md)
[![Version](https://img.shields.io/badge/version-v1.10.0--phase--10-blue.svg)](CHANGELOG.md)
[![Phases](https://img.shields.io/badge/phases-10%2F10%20done-brightgreen.svg)](docs/reports/)
[![Tests](https://img.shields.io/badge/tests-378%20passing%20(100%25)-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-78%25-success.svg)](tests/)
[![Architecture](https://img.shields.io/badge/architecture-layered-blue.svg)](docs/ARCHITECTURE.md)

---

## 🎯 Proyecto de Refactorización

> **Estado**: 🎉 **PROYECTO COMPLETADO** - 100% refactorizado
>
> **Versión**: v1.10.0-phase-10
>
> **Arquitectura**: Layered Architecture (Presentation → Service → Repository → Model)
>
> **Calidad**: 378 tests (100% passing), 78% coverage, SOLID principles

### 📚 Documentación Completa

#### Documentación Técnica Principal

- 🏗️ **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitectura completa del sistema
- 🚀 **[DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md)** - Guía de desarrollo
- 🔄 **[MIGRATION_GUIDE.md](docs/migration/MIGRATION_GUIDE.md)** - Migración de código legacy
- 📡 **[API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)** - Documentación de API
- 🚢 **[DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md)** - Guía de despliegue
- 🤝 **[CONTRIBUTING.md](CONTRIBUTING.md)** - Cómo contribuir

#### Documentación del Proyecto

```text
docs/
├── README.md                    → Índice principal
├── ARCHITECTURE.md              → Arquitectura del sistema
├── DEVELOPMENT_GUIDE.md         → Guía de desarrollo
│
├── api/                         → Documentación de API
│   ├── README.md
│   └── API_DOCUMENTATION.md
│
├── deployment/                  → Guías de despliegue
│   ├── README.md
│   ├── DEPLOYMENT.md
│   └── examples/                → Configs de ejemplo
│
├── migration/                   → Migración de código legacy
│   ├── README.md
│   └── MIGRATION_GUIDE.md
│
├── plan/                        → Plan de reorganización (10 fases)
├── reports/                     → Reportes completos (Phases 0-10)
├── guides/                      → Guías especializadas
├── git/                         → Estrategia Git
└── templates/                   → Plantillas
```

### 🚀 Inicio Rápido

#### 🐳 Opción 1: Docker (Recomendado)

La forma más rápida de ejecutar la aplicación:

```bash
# 1. Configurar variables de entorno
cp .env.docker .env
# Editar .env y generar SECRET_KEY: python -c "import secrets; print(secrets.token_hex(32))"

# 2. Iniciar servicios (app + PostgreSQL)
docker-compose up -d

# 3. Inicializar base de datos
docker-compose exec web flask db upgrade

# 4. Acceder a la aplicación
# http://localhost:5000
```

📖 **Ver guía completa**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

#### 💻 Opción 2: Instalación Local

**Para nuevos desarrolladores**:

1. Lee **[docs/guides/INICIO_RAPIDO.md](docs/guides/INICIO_RAPIDO.md)** (5-10 min)
2. Ejecuta el script de inicialización:

   ```bash
   ./scripts/init_git_workflow.sh
   ```

3. Revisa el **[índice de documentación](docs/README.md)**

**Para entender el proyecto completo**:

- 📋 **[Plan de Reorganización](docs/plan/PLAN_REORGANIZACION.md)** - Plan maestro de 10 fases
- 📊 **[Reportes de Fases](docs/reports/)** - Reportes completos de fases 0-7
- 🔀 **[Estrategia Git](docs/git/GIT_STRATEGY.md)** - Control de versiones detallado
- 📖 **[Resumen](docs/guides/RESUMEN.md)** - Navegación entre documentos
- ⚙️ **[Configuration Guide](docs/guides/CONFIGURATION_GUIDE.md)** - Sistema modular de configuración
- 🚨 **[Exception Handling Guide](docs/guides/EXCEPTION_HANDLING_GUIDE.md)** - Sistema de excepciones custom
- 📦 **[Dependencies Guide](docs/DEPENDENCIES.md)** - Guía completa de gestión de dependencias

---

## 📖 Documentación Original del Proyecto

> Ver **[README_ORIGINAL.md](README_ORIGINAL.md)** para las instrucciones originales completas

### Requisitos Previos

- Python 3.8+
- SQLite3
- Virtualenv

### Instalación de Dependencias

Para información completa sobre las dependencias del proyecto, consulta **[docs/DEPENDENCIES.md](docs/DEPENDENCIES.md)**

#### Producción

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar instalación
python scripts/verify_requirements.py
```

#### Desarrollo

```bash
# Instalar dependencias de desarrollo (incluye las de producción)
pip install -r requirements-dev.txt
```

### Instalación Rápida

#### Unix/Linux/Mac

```bash
python3.8 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
export FLASK_APP=run.py
export FLASK_DEBUG=true
flask run
```

#### Windows

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
$env:FLASK_APP = ".\run.py"
$env:FLASK_DEBUG = "true"
flask run
```

Aplicación disponible en: `http://127.0.0.1:5000/`

### Docker

```bash
echo "DEBUG=True" > .env
docker-compose up --build
```

Visita `http://localhost:5085`

---

## 📁 Estructura del Proyecto

### Arquitectura en Capas

El proyecto sigue una **arquitectura en capas (Layered Architecture)** con separación clara de responsabilidades:

```text
┌────────────────────────────────────────────┐
│        PRESENTATION LAYER                  │  ← Blueprints (home, api, accounts, charts)
│        (Views / Templates)                 │    Maneja HTTP, renderiza respuestas
└──────────────┬─────────────────────────────┘
               │ @inject_service
               ▼
┌────────────────────────────────────────────┐
│         SERVICE LAYER                      │  ← DashboardService, MetricaService
│         (Business Logic)                   │    Lógica de negocio, orquestación
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│        REPOSITORY LAYER                    │  ← MetricaRepository, HistoricoRepository
│        (Data Access)                       │    Queries SQL, CRUD operations
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│         MODEL LAYER                        │  ← Metrica, Historico, User (ORM)
│         (Domain Models)                    │    Definición de entidades
└──────────────┬─────────────────────────────┘
               │
               ▼
         [PostgreSQL/SQLite]
```

### Estructura de Directorios

```text
dashboardsonar-application-python/
├── 📋 Documentación
│   ├── ARCHITECTURE.md         # ⭐ Arquitectura completa del sistema
│   ├── DEVELOPMENT_GUIDE.md    # ⭐ Guía de desarrollo
│   ├── MIGRATION_GUIDE.md      # ⭐ Migración de código legacy
│   ├── API_DOCUMENTATION.md    # ⭐ Documentación de API
│   ├── DEPLOYMENT.md           # ⭐ Guía de despliegue
│   ├── CONTRIBUTING.md         # ⭐ Cómo contribuir
│   ├── CHANGELOG.md            # Registro de cambios (v1.0 → v1.10)
│   └── docs/                   # Documentación adicional
│       ├── plan/               # Planes detallados (Phases 0-10)
│       ├── reports/            # Reportes de fases (Phases 0-10)
│       ├── guides/             # Guías especializadas
│       └── templates/          # Plantillas
│
├── ⚙️ Configuración
│   ├── config/                 # ⭐ FASE 6: Configuración por entorno
│   │   ├── base.py             # Configuración base
│   │   ├── development.py      # Config desarrollo
│   │   ├── production.py       # Config producción
│   │   └── testing.py          # Config testing
│   ├── .env.example            # Template de variables de entorno
│   └── .gitignore              # Archivos ignorados
│
├── 🏗️ Aplicación Principal
│   └── infocodest/
│       ├── __init__.py         # Factory pattern (create_app)
│       ├── extensions.py       # Extensiones Flask (db, login_manager, etc.)
│       ├── errorhandlers.py    # Error handlers custom
│       │
│       ├── 📊 CAPA 4: PRESENTATION (Views/Blueprints)
│       ├── home/               # Blueprint: Dashboard principal
│       │   ├── __init__.py
│       │   └── views.py        # Vistas delgadas (<30 LOC)
│       ├── api/                # Blueprint: API REST
│       ├── accounts/           # Blueprint: Autenticación
│       ├── charts/             # Blueprint: Gráficos
│       ├── static/             # Assets (CSS, JS, imágenes)
│       └── templates/          # Plantillas Jinja2
│       │
│       ├── 💼 CAPA 3: SERVICE (Business Logic)
│       ├── services/           # ⭐ FASE 2
│       │   ├── __init__.py
│       │   ├── dashboard_service.py    # KPIs y métricas dashboard
│       │   ├── metrica_service.py      # Operaciones con métricas
│       │   └── auth_service.py         # Lógica de autenticación
│       │
│       ├── 🗄️ CAPA 2: REPOSITORY (Data Access)
│       ├── repositories/       # ⭐ FASE 1
│       │   ├── __init__.py
│       │   ├── base_repository.py      # CRUD genérico <T>
│       │   ├── metrica_repository.py   # Queries específicas
│       │   ├── historico_repository.py
│       │   ├── daily_repository.py
│       │   ├── user_repository.py
│       │   └── proveedor_repository.py
│       │
│       ├── 📦 CAPA 1: MODEL (Domain Models)
│       ├── models/             # Modelos ORM (SQLAlchemy)
│       │   ├── __init__.py
│       │   ├── users.py        # Modelo User
│       │   ├── metricas.py     # Modelo Metrica
│       │   ├── historico.py    # Modelo Historico
│       │   ├── daily.py        # Modelo Daily
│       │   └── proveedor.py    # Modelo Proveedor
│       │
│       ├── 🔧 CAPAS TRANSVERSALES (Cross-Cutting)
│       ├── utils/              # ⭐ FASE 4: Utilidades
│       │   ├── logger.py       # Logging estructurado
│       │   ├── decorators.py   # @inject_service, @log_execution_time
│       │   ├── validators.py   # 7 validators
│       │   └── helpers.py      # 10 funciones auxiliares
│       │
│       └── exceptions/         # ⭐ FASE 5: Excepciones custom
│           ├── base.py         # ApplicationException, BusinessException
│           └── business_exceptions.py  # 15 excepciones específicas
│
├── 🧪 Testing
│   └── tests/                  # ⭐ 378 tests (100% passing, 78% coverage)
│       ├── unit/               # 333 tests unitarios
│       │   ├── test_repositories/      # Repository tests
│       │   ├── test_services/          # Service tests
│       │   ├── test_utils/             # 199 utils tests (96-100% coverage)
│       │   ├── test_models/            # Model tests
│       │   └── test_exceptions/        # Exception tests
│       └── funcional/          # 45 tests funcionales
│           ├── test_api.py            # 21 API endpoint tests
│           ├── test_auth.py           # Authentication tests
│           └── test_home.py           # Main routes tests
│
├── 🔨 Scripts y Utilidades
│   ├── scripts/                # Scripts de verificación
│   │   ├── verify_dependencies.py
│   │   ├── verify_requirements.py
│   │   └── verify_config.py
│   ├── logs/                   # Logs con rotación automática
│   └── migrations/             # Migraciones Alembic
│
├── 🚀 Entry Points
│   ├── run.py                  # ⭐ FASE 8: Entry point actualizado
│   ├── requirements.txt        # Dependencias producción (20 packages)
│   └── requirements-dev.txt    # Dependencias desarrollo
```

**Leyenda**: ⭐ = Añadido durante refactorización

---

## 🚀 Roadmap de Refactorización

### 🎉 Progreso: 100% COMPLETADO (10/10 fases)

| Fase | Descripción | Duración | Estado | Reporte |
|------|-------------|----------|--------|---------|
| 0 | Preparación | 30 min | ✅ Completado | [Ver reporte](docs/reports/phase-0-preparation.md) |
| 1 | Capa de Repositorios | 2h | ✅ Completado | [Ver reporte](docs/reports/phase-1-repositories.md) |
| 2 | Capa de Servicios | 3h | ✅ Completado | [Ver reporte](docs/reports/phase-2-services.md) |
| 3 | Refactorizar Vistas | 2h | ✅ Completado | [Ver reporte](docs/reports/phase-3-views.md) |
| 4 | Sistema de Utilidades | 1.5h | ✅ Completado | [Ver reporte](docs/reports/phase-4-utilities.md) |
| 5 | Manejo de Excepciones | 1h | ✅ Completado | [Ver reporte](docs/reports/phase-5-exceptions.md) |
| 6 | Configuración Mejorada | 1h | ✅ Completado | [Ver reporte](docs/reports/phase-6-configuration.md) |
| 7 | Optimización Dependencias | 45 min | ✅ Completado | [Ver reporte](docs/reports/phase-7-dependencies.md) |
| 8 | Actualizar Entry Points | 45 min | ✅ Completado | [Ver reporte](docs/reports/phase-8-entrypoints.md) |
| 9 | Tests y Validación | 2.5h | ✅ Completado | [Ver reporte](docs/reports/phase-9-tests.md) |
| 10 | Documentación y Limpieza | 3h | ✅ **Completado** | [Ver reporte](docs/reports/phase-10-documentation.md) |

**Duración total**: 18 horas (dentro de estimación de 16-21h)

**Plan completo**: [docs/plan/PLAN_REORGANIZACION.md](docs/plan/PLAN_REORGANIZACION.md)

### Logros de Calidad

| Métrica | Antes | Actual | Objetivo | Estado |
|---------|-------|--------|----------|--------|
| **Arquitectura** | Monolítica | Capas (Repo/Service/View) | Separación clara | ✅ Logrado |
| **Líneas por Vista** | ~100 | <30 | <30 | ✅ Logrado |
| **Logging** | print() | Structured logging | Sistema robusto | ✅ Logrado |
| **Excepciones** | abort() | 15 custom exceptions | Sistema completo | ✅ Logrado |
| **Type Hints** | Parcial | 100% (nuevas capas) | 100% | ✅ Logrado |
| **Docstrings** | Básico | 100% (nuevas capas) | 100% | ✅ Logrado |
| **Cobertura Tests** | 63% | 78% (378 tests, 100% passing) | >70% | ✅ Logrado |
| **Complejidad** | >10 | <5 (nuevas capas) | <5 | ✅ Logrado |

### Nuevas Capacidades Añadidas

#### Arquitectura y Patrones

- ✅ **Repository Pattern** - Capa de acceso a datos con `BaseRepository<T>` genérico
- ✅ **Service Layer** - Lógica de negocio separada (DashboardService, etc.)
- ✅ **Dependency Injection** - Decorador `@inject_service` para DI limpio
- ✅ **Factory Pattern** - Application factory con `create_app(config)`

#### Utilidades y Cross-Cutting

- ✅ **Structured Logging** - Sistema con rotación automática (10MB, 10 backups)
- ✅ **Custom Exceptions** - 15 clases específicas del dominio con HTTP codes
- ✅ **Error Handlers** - Soporte automático JSON/HTML (content negotiation)
- ✅ **Validators** - 7 validators para input validation
- ✅ **Helpers** - 10 funciones auxiliares reutilizables
- ✅ **Decorators** - `@inject_service`, `@log_execution_time`, `@retry`, `@deprecated`

#### Calidad de Código

- ✅ **Type Hints** - 100% coverage en nuevas capas
- ✅ **Docstrings** - Google-style en todas las funciones
- ✅ **Semantic Commits** - Conventional Commits en todo el proyecto
- ✅ **Code Reviews** - Pull Requests documentados para cada fase

#### Gestión de Dependencias (Fase 7)

- ✅ **Dependencies Optimization** - 47% reducción en requirements.txt (38→20 paquetes)
- ✅ **100% Version Pinning** - Todas las dependencias con versiones exactas
- ✅ **Production/Dev Separation** - requirements.txt vs requirements-dev.txt
- ✅ **Dependency Verification** - Scripts automáticos de verificación (2)
- ✅ **UTF-8 Encoding** - requirements-dev.txt recreado correctamente
- ✅ **Comprehensive Documentation** - docs/DEPENDENCIES.md (350+ LOC)
- ✅ **Organized by Category** - 10 categorías en producción, 3 en desarrollo

---

## 🧪 Tests

**Estado actual**: ✅ **378 tests passing (100%)** | 78% coverage

### Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=infocodest --cov-report=html

# Run by category (pytest markers - Priority 3)
pytest -m api              # API tests (21 tests, ~30s)
pytest -m unit             # Unit tests (333 tests)
pytest -m functional       # Functional tests (45 tests)
pytest -m security         # Security tests
pytest -m "not slow"       # Exclude slow tests
```

### Test Organization

- **Unit Tests** (333): Isolated component tests with mocks
- **Functional Tests** (45): Integration with Flask application
- **100% Categorized**: All tests marked with pytest markers for selective execution

### Documentation

- 📖 **[Testing Manual](docs/1-technical/testing/MANUAL_TESTING.md)** - Complete testing guide
- 📊 **[Test Reports](docs/1-technical/testing/)** - Priority 1-4 completion reports
- 🎯 **[Coverage Report](htmlcov/index.html)** - Generated after running tests with --cov

---

## 🔄 CI/CD Automation

The project includes a complete automated Continuous Integration and Continuous Deployment pipeline using GitHub Actions.

### 📚 Documentation

- **[CI/CD User Manual](docs/CICD_USER_MANUAL.md)** - Complete guide for developers and DevOps
- **[Workflows Documentation](.github/README.md)** - Technical details of all workflows
- **[Scripts Documentation](scripts/ci/README.md)** - CI/CD scripts reference

### CI Pipeline

Every Pull Request to `develop` or `main` branches automatically runs:

- **Code Quality & Linting** - Black, isort, Flake8, Pylint, mypy
- **Security Scanning** - Safety (dependencies) and Bandit (code)
- **Unit Tests** - Matrix testing on Python 3.10, 3.11, and 3.12
- **Integration Tests** - Full application integration testing
- **Build Validation** - Verify imports and configuration
- **Coverage Reports** - Uploaded to Codecov

### CD Pipeline

- **Staging Deployment** - Automatic deployment to staging on merge to `develop`
- **Production Deployment** - Manual deployment with approval on version tags
- **Blue-Green Strategy** - Zero-downtime deployments
- **Automatic Rollback** - Reverts automatically if deployment fails
- **Smoke Tests** - Post-deployment health checks

### Running CI Checks Locally

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all checks (recommended before pushing)
./scripts/ci/lint.sh              # Code quality checks
./scripts/ci/security.sh          # Security scanning
./scripts/ci/test.sh --html       # Tests with coverage

# Or run individual tools
flake8 infocodest/
black --check infocodest/
pytest tests/ -v --cov=infocodest --cov-report=html
```

### Quick Start for Developers

**For your first time**:

1. Read the [CI/CD User Manual](docs/CICD_USER_MANUAL.md) (15 min)
2. Install dev dependencies: `pip install -r requirements-dev.txt`
3. Run local checks before each commit: `./scripts/ci/lint.sh && ./scripts/ci/test.sh`

**For deployments**:

- Staging: Automatic on merge to `develop`
- Production: Create version tag (e.g., `v1.2.3`) and approve deployment

See the [User Manual](docs/CICD_USER_MANUAL.md) for complete workflows and troubleshooting.

---

## 🗄️ Base de Datos

### Configurar

```bash
mkdir datos
```

Archivo `.env`:

```env
DEBUG=True
FLASK_APP=run.py
FLASK_DEBUG=False
ASSETS_ROOT=/static/assets
DATABASE=db.sqlite3
```

### Migraciones

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 🤝 Contribuir

### Workflow

1. Lee **[docs/guides/INICIO_RAPIDO.md](docs/guides/INICIO_RAPIDO.md)**
2. Crea rama: `git checkout -b feature/nombre`
3. Sigue **[plantillas de commits](docs/templates/COMMIT_TEMPLATE.md)**
4. Crea **[Pull Request](docs/templates/PR_TEMPLATE.md)**

### Standards

- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/)
- **Código**: PEP 8
- **Tests**: Cobertura >70% (actual: 78%, 378 tests passing)

---

## 📞 Documentación y Soporte

### Documentación General

- **Índice completo**: [docs/README.md](docs/README.md)
- **Quick start**: [docs/guides/INICIO_RAPIDO.md](docs/guides/INICIO_RAPIDO.md)
- **Estrategia Git**: [docs/git/GIT_STRATEGY.md](docs/git/GIT_STRATEGY.md)
- **Plan completo**: [docs/plan/PLAN_REORGANIZACION.md](docs/plan/PLAN_REORGANIZACION.md)
- **CHANGELOG**: [CHANGELOG.md](CHANGELOG.md) - Registro detallado de cambios

### Guías Técnicas

- **Configuration System**: [docs/guides/CONFIGURATION_GUIDE.md](docs/guides/CONFIGURATION_GUIDE.md)
- **Exception Handling**: [docs/guides/EXCEPTION_HANDLING_GUIDE.md](docs/guides/EXCEPTION_HANDLING_GUIDE.md)
- **Dependencies Management**: [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md)
- **Documentar Cambios**: [docs/guides/DOCUMENTAR_CAMBIOS.md](docs/guides/DOCUMENTAR_CAMBIOS.md)

### Reportes de Fases

- **Phase 0**: [Preparación](docs/reports/phase-0-preparation.md)
- **Phase 1**: [Repositorios](docs/reports/phase-1-repositories.md)
- **Phase 2**: [Servicios](docs/reports/phase-2-services.md)
- **Phase 3**: [Vistas](docs/reports/phase-3-views.md)
- **Phase 4**: [Utilidades](docs/reports/phase-4-utilities.md)
- **Phase 5**: [Excepciones](docs/reports/phase-5-exceptions.md)
- **Phase 6**: [Configuración](docs/reports/phase-6-configuration.md)
- **Phase 7**: [Dependencias](docs/reports/phase-7-dependencies.md)

---

## 🎉 Comenzar

```bash
# 1. Leer documentación
cat docs/README.md

# 2. Inicializar Git workflow
./scripts/init_git_workflow.sh

# 3. Seguir guía de inicio
cat docs/guides/INICIO_RAPIDO.md
```

---

## 🎉 Proyecto Completado

El proyecto de refactorización ha sido completado exitosamente. La aplicación ahora cuenta con:

- ✅ Arquitectura en capas bien definida
- ✅ 378 tests (100% passing) con 78% de cobertura
- ✅ Documentación técnica completa y actualizada
- ✅ Código mantenible y escalable con SOLID principles

Ver **[README_ORIGINAL.md](README_ORIGINAL.md)** para documentación técnica detallada.
