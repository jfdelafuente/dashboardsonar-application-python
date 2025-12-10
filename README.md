# Dashboard Sonar - Flask Application

> Aplicación web para visualización y análisis de métricas de calidad de código desde SonarQube

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Proyecto de Refactorización

> **Estado Actual**: 📋 En preparación para refactorización arquitectónica
>
> **Objetivo**: Transformar la aplicación a una arquitectura en capas mantenible, ágil y eficaz

### 📚 Documentación Completa

Toda la documentación del proyecto de refactorización está organizada en el directorio [`docs/`](docs/):

```
docs/
├── README.md                    → Índice principal
├── plan/                        → Plan de refactorización
├── git/                         → Estrategia de versionado
├── guides/                      → Guías de usuario
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
- 🔀 **[Estrategia Git](docs/git/GIT_STRATEGY.md)** - Control de versiones detallado
- 📖 **[Resumen](docs/guides/RESUMEN.md)** - Navegación entre documentos

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
│   ├── plan/                   # Plan de reorganización
│   ├── git/                    # Estrategia Git
│   ├── guides/                 # Guías de usuario
│   └── templates/              # Plantillas
│
├── infocodest/                 # Aplicación principal
│   ├── __init__.py             # Factory pattern
│   ├── extensions.py           # Extensiones Flask
│   ├── accounts/               # Blueprint autenticación
│   ├── api/                    # Blueprint API
│   ├── charts/                 # Blueprint gráficos
│   ├── home/                   # Blueprint home
│   ├── models/                 # Modelos ORM
│   ├── static/                 # Assets estáticos
│   └── templates/              # Plantillas Jinja2
│
├── scripts/                    # Scripts de utilidad
│   ├── init_git_workflow.sh   # Inicialización Git
│   └── init_db.py             # Inicializar BD
│
├── tests/                      # Tests unitarios y funcionales
├── migrations/                 # Migraciones Alembic
├── config.py                   # Configuración
├── run.py                      # Entry point
└── requirements.txt            # Dependencias
```

---

## 🚀 Roadmap de Refactorización

### Fases Planificadas

| Fase | Descripción | Duración | Estado |
|------|-------------|----------|--------|
| 0 | Preparación | 30 min | ⏸️ Pendiente |
| 1 | Capa de Repositorios | 2-3h | ⏸️ Pendiente |
| 2 | Capa de Servicios | 3-4h | ⏸️ Pendiente |
| 3 | Refactorizar Vistas | 2-3h | ⏸️ Pendiente |
| 4-10 | ... | ... | ⏸️ Pendiente |

**Total**: 14-20 horas estimadas

Ver detalles completos en **[docs/plan/PLAN_REORGANIZACION.md](docs/plan/PLAN_REORGANIZACION.md)**

### Objetivos de Calidad

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| Cobertura Tests | ~60% | >80% |
| Líneas por Vista | ~100 | <30 |
| Complejidad | >10 | <5 |

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

- **Índice completo**: [docs/README.md](docs/README.md)
- **Quick start**: [docs/guides/INICIO_RAPIDO.md](docs/guides/INICIO_RAPIDO.md)
- **Estrategia Git**: [docs/git/GIT_STRATEGY.md](docs/git/GIT_STRATEGY.md)
- **Plan completo**: [docs/plan/PLAN_REORGANIZACION.md](docs/plan/PLAN_REORGANIZACION.md)

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
