# Dashboard Sonar - Flask Application

> Aplicación web para visualización y análisis de métricas de calidad de código desde SonarQube

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Refactoring](https://img.shields.io/badge/refactoring-50%25%20complete-yellow.svg)](docs/plan/PLAN_REORGANIZACION.md)
[![Version](https://img.shields.io/badge/version-v1.5.0--phase--5-blue.svg)](CHANGELOG.md)
[![Phases](https://img.shields.io/badge/phases-5%2F10%20done-success.svg)](docs/reports/)

---

## 🎯 Proyecto de Refactorización

> **Estado Actual**: 🚀 **Fase 5 Completada** - 50% del proyecto completado
>
> **Versión**: v1.5.0-phase-5
>
> **Objetivo**: Transformar la aplicación a una arquitectura en capas mantenible, ágil y eficaz

### 📚 Documentación Completa

Toda la documentación del proyecto de refactorización está organizada en el directorio [`docs/`](docs/):

```
docs/
├── README.md                    → Índice principal
├── plan/                        → Plan de refactorización y planes detallados
├── reports/                     → Reportes de fases completadas (0-5)
├── guides/                      → Guías de usuario (Exception Handling, Inicio Rápido, etc.)
├── git/                         → Estrategia de versionado
└── templates/                   → Plantillas de commits y PRs
```

### 🚀 Inicio Rápido

**Para nuevos desarrolladores**:
1. Lee **[docs/guides/INICIO_RAPIDO.md](docs/guides/INICIO_RAPIDO.md)** (5-10 min)
2. Ejecuta el script de inicialización:
   ```bash
   ./scripts/init_git_workflow.sh
   ```
3. Revisa el **[índice de documentación](docs/README.md)**

**Para entender el proyecto completo**:
- 📋 **[Plan de Reorganización](docs/plan/PLAN_REORGANIZACION.md)** - Plan maestro de 10 fases
- 📊 **[Reportes de Fases](docs/reports/)** - Reportes completos de fases 0-5
- 🔀 **[Estrategia Git](docs/git/GIT_STRATEGY.md)** - Control de versiones detallado
- 📖 **[Resumen](docs/guides/RESUMEN.md)** - Navegación entre documentos
- 🚨 **[Exception Handling Guide](docs/guides/EXCEPTION_HANDLING_GUIDE.md)** - Sistema de excepciones custom

---

## 📖 Documentación Original del Proyecto

> Ver **[README_ORIGINAL.md](README_ORIGINAL.md)** para las instrucciones originales completas

### Requisitos Previos

- Python 3.8+
- SQLite3
- Virtualenv

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

```
dashboardsonar-application-python/
├── docs/                        # 📚 Documentación de refactorización
│   ├── README.md               # Índice principal
│   ├── plan/                   # Plan de reorganización y planes detallados
│   ├── reports/                # ⭐ Reportes de fases completadas (0-5)
│   ├── guides/                 # Guías de usuario y best practices
│   ├── git/                    # Estrategia Git
│   └── templates/              # Plantillas
│
├── infocodest/                 # Aplicación principal
│   ├── __init__.py             # Factory pattern
│   ├── extensions.py           # Extensiones Flask
│   ├── errorhandlers.py        # ⭐ Error handlers (actualizado Fase 5)
│   │
│   ├── repositories/           # ⭐ FASE 1: Capa de acceso a datos
│   │   ├── base_repository.py
│   │   ├── dashboard_repository.py
│   │   └── ...
│   │
│   ├── services/               # ⭐ FASE 2: Capa de lógica de negocio
│   │   ├── dashboard_service.py
│   │   └── ...
│   │
│   ├── utils/                  # ⭐ FASE 4: Utilidades transversales
│   │   ├── logger.py           # Sistema de logging estructurado
│   │   ├── decorators.py       # @inject_service, @retry, etc.
│   │   ├── validators.py       # Validadores de entrada
│   │   └── helpers.py          # Funciones auxiliares
│   │
│   ├── exceptions/             # ⭐ FASE 5: Sistema de excepciones
│   │   ├── base.py             # Excepciones base
│   │   └── business_exceptions.py  # Excepciones específicas (15)
│   │
│   ├── accounts/               # Blueprint autenticación
│   ├── api/                    # Blueprint API
│   ├── charts/                 # Blueprint gráficos
│   ├── home/                   # Blueprint home (refactorizado Fase 3)
│   ├── models/                 # Modelos ORM
│   ├── static/                 # Assets estáticos
│   └── templates/              # Plantillas Jinja2
│
├── scripts/                    # Scripts de utilidad
├── tests/                      # Tests unitarios y funcionales
├── migrations/                 # Migraciones Alembic
├── logs/                       # ⭐ Logs de aplicación (rotación automática)
├── config.py                   # Configuración
├── run.py                      # Entry point
├── CHANGELOG.md                # ⭐ Registro de cambios detallado
└── requirements.txt            # Dependencias
```

**Leyenda**: ⭐ = Nuevos elementos añadidos durante la refactorización

---

## 🚀 Roadmap de Refactorización

### Progreso Actual: 50% Completado (5/10 fases)

| Fase | Descripción | Duración | Estado | Reporte |
|------|-------------|----------|--------|---------|
| 0 | Preparación | 30 min | ✅ **Completado** | [Ver reporte](docs/reports/phase-0-preparation.md) |
| 1 | Capa de Repositorios | 2h | ✅ **Completado** | [Ver reporte](docs/reports/phase-1-repositories.md) |
| 2 | Capa de Servicios | 3h | ✅ **Completado** | [Ver reporte](docs/reports/phase-2-services.md) |
| 3 | Refactorizar Vistas | 2h | ✅ **Completado** | [Ver reporte](docs/reports/phase-3-views.md) |
| 4 | Sistema de Utilidades | 1.5h | ✅ **Completado** | [Ver reporte](docs/reports/phase-4-utilities.md) |
| 5 | Manejo de Excepciones | 1h | ✅ **Completado** | [Ver reporte](docs/reports/phase-5-exceptions.md) |
| 6 | Configuración Mejorada | 1h | ⏭️ **Siguiente** | - |
| 7 | Optimización Dependencias | 30 min | ⏸️ Pendiente | - |
| 8 | Actualizar Entry Points | 30 min | ⏸️ Pendiente | - |
| 9 | Tests y Validación | 2-3h | ⏸️ Pendiente | - |
| 10 | Documentación y Limpieza | 1h | ⏸️ Pendiente | - |

**Progreso**: 10 horas completadas de 14-20 horas estimadas

Ver detalles completos en **[docs/plan/PLAN_REORGANIZACION.md](docs/plan/PLAN_REORGANIZACION.md)**

### Logros de Calidad

| Métrica | Antes | Actual | Objetivo | Estado |
|---------|-------|--------|----------|--------|
| **Arquitectura** | Monolítica | Capas (Repo/Service/View) | Separación clara | ✅ Logrado |
| **Líneas por Vista** | ~100 | <30 | <30 | ✅ Logrado |
| **Logging** | print() | Structured logging | Sistema robusto | ✅ Logrado |
| **Excepciones** | abort() | 15 custom exceptions | Sistema completo | ✅ Logrado |
| **Type Hints** | Parcial | 100% (nuevas capas) | 100% | ✅ Logrado |
| **Docstrings** | Básico | 100% (nuevas capas) | 100% | ✅ Logrado |
| **Cobertura Tests** | ~60% | ~60% | >80% | ⏭️ Fase 9 |
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

---

## 🧪 Tests

```bash
# Tests básicos
python -m pytest --setup-show

# Tests con cobertura
python -m pytest --cov=infocodest --cov-report=html
```

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
- **Tests**: Cobertura >80%

---

## 📞 Documentación y Soporte

### Documentación General

- **Índice completo**: [docs/README.md](docs/README.md)
- **Quick start**: [docs/guides/INICIO_RAPIDO.md](docs/guides/INICIO_RAPIDO.md)
- **Estrategia Git**: [docs/git/GIT_STRATEGY.md](docs/git/GIT_STRATEGY.md)
- **Plan completo**: [docs/plan/PLAN_REORGANIZACION.md](docs/plan/PLAN_REORGANIZACION.md)
- **CHANGELOG**: [CHANGELOG.md](CHANGELOG.md) - Registro detallado de cambios

### Guías Técnicas

- **Exception Handling**: [docs/guides/EXCEPTION_HANDLING_GUIDE.md](docs/guides/EXCEPTION_HANDLING_GUIDE.md)
- **Documentar Cambios**: [docs/guides/DOCUMENTAR_CAMBIOS.md](docs/guides/DOCUMENTAR_CAMBIOS.md)

### Reportes de Fases

- **Phase 0**: [Preparación](docs/reports/phase-0-preparation.md)
- **Phase 1**: [Repositorios](docs/reports/phase-1-repositories.md)
- **Phase 2**: [Servicios](docs/reports/phase-2-services.md)
- **Phase 3**: [Vistas](docs/reports/phase-3-views.md)
- **Phase 4**: [Utilidades](docs/reports/phase-4-utilities.md)
- **Phase 5**: [Excepciones](docs/reports/phase-5-exceptions.md)

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

**¡Listo para transformar la aplicación! 🚀**

Ver **[README_ORIGINAL.md](README_ORIGINAL.md)** para documentación técnica detallada.
