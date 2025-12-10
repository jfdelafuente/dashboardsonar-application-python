# Plan de Reorganización del Proyecto Flask - Dashboard Sonar

**Fecha**: 2025-12-10
**Objetivo**: Transformar la aplicación Flask en un proyecto mantenible, ágil y eficaz mediante arquitectura en capas

---

## 📊 Diagnóstico Inicial

### Estado Actual del Proyecto

```
dashboardsonar-application-python/
├── config.py                    # Configuración en raíz
├── run.py                       # Entry point
├── manage.py                    # CLI commands
├── infocodest/                  # Aplicación principal
│   ├── __init__.py              # Factory pattern ✅
│   ├── extensions.py            # Extensiones centralizadas ✅
│   ├── errorhandlers.py         # Manejadores de errores ✅
│   ├── accounts/                # Blueprint autenticación
│   ├── api/                     # Blueprint API
│   ├── charts/                  # Blueprint gráficos
│   ├── home/                    # Blueprint home
│   ├── models/                  # Modelos ORM
│   │   ├── database.py          # ⚠️ SQL raw + engine
│   │   ├── users.py
│   │   ├── metricas.py
│   │   ├── historico.py
│   │   └── ...
│   ├── static/                  # Assets
│   └── templates/               # Plantillas Jinja2
├── scripts/                     # Scripts ETL/tareas
├── migrations/                  # Migraciones Alembic ✅
└── tests/                       # Tests ✅
```

### 🔴 Problemas Críticos Identificados

1. **Violación de Separación de Responsabilidades**
   - Consultas SQL directas en vistas (views.py)
   - Lógica de negocio mezclada con presentación
   - Ejemplo: `infocodest/home/views.py` líneas 20-50

2. **Doble Sistema de Acceso a Base de Datos**
   - SQLAlchemy ORM en modelos
   - SQL raw con `create_engine` en `models/database.py`
   - Dificulta mantenimiento y testing

3. **Ausencia de Capa de Servicios**
   - No hay lugar claro para lógica de negocio compleja
   - Dificulta reutilización de código
   - Complica testing unitario

4. **Configuración Fragmentada**
   - Variables en `.env`
   - Configuración en `config.py` (raíz)
   - Valores hardcodeados en código
   - Ejemplo: `DAYS` en `models/database.py` línea 9

5. **Sin Sistema de Logging Estructurado**
   - Solo `print()` statements
   - Dificulta debugging en producción
   - No hay trazabilidad de errores

6. **Dependencias Problemáticas**
   - `requirements.txt` con encoding corrupto (UTF-16)
   - Dificulta instalación y mantenimiento

---

## 🎯 Arquitectura Objetivo

### Patrón: Arquitectura en Capas (Layered Architecture)

```
┌─────────────────────────────────────────┐
│         PRESENTATION LAYER              │
│     (Blueprints/Views/Templates)        │
│  - Renderiza respuestas                 │
│  - Valida entrada usuario               │
│  - Maneja HTTP                          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          SERVICE LAYER                  │
│      (Business Logic)                   │
│  - Orquesta operaciones                 │
│  - Lógica de negocio                    │
│  - Transacciones                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       REPOSITORY LAYER                  │
│      (Data Access)                      │
│  - Abstrae acceso a datos               │
│  - Queries complejas                    │
│  - Operaciones CRUD                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          MODEL LAYER                    │
│      (Domain Models/ORM)                │
│  - Definición entidades                 │
│  - Relaciones                           │
│  - Validaciones básicas                 │
└─────────────────────────────────────────┘
```

### Estructura de Directorios Objetivo

```
dashboardsonar-application-python/
├── config/                          # ⭐ NUEVO
│   ├── __init__.py
│   ├── base.py                      # Configuración base
│   ├── development.py               # Config desarrollo
│   ├── testing.py                   # Config testing
│   └── production.py                # Config producción
│
├── infocodest/
│   ├── __init__.py                  # Factory app
│   ├── extensions.py                # Extensiones Flask
│   │
│   ├── models/                      # CAPA 1: Domain Models
│   │   ├── __init__.py
│   │   ├── base.py                  # Base model
│   │   ├── users.py
│   │   ├── metricas.py
│   │   ├── historico.py
│   │   ├── proveedor.py
│   │   ├── daily.py
│   │   ├── registros.py
│   │   └── stat.py
│   │
│   ├── repositories/                # ⭐ CAPA 2: Data Access
│   │   ├── __init__.py
│   │   ├── base_repository.py       # Repositorio base genérico
│   │   ├── metrica_repository.py
│   │   ├── historico_repository.py
│   │   ├── proveedor_repository.py
│   │   ├── daily_repository.py
│   │   └── user_repository.py
│   │
│   ├── services/                    # ⭐ CAPA 3: Business Logic
│   │   ├── __init__.py
│   │   ├── metrica_service.py       # Lógica de métricas
│   │   ├── dashboard_service.py     # Lógica KPIs/dashboard
│   │   ├── stats_service.py         # Cálculos estadísticos
│   │   ├── auth_service.py          # Lógica autenticación
│   │   └── export_service.py        # Exportaciones
│   │
│   ├── blueprints/                  # CAPA 4: Presentation (renombrado)
│   │   ├── accounts/
│   │   │   ├── __init__.py
│   │   │   ├── views.py             # Solo presentación
│   │   │   └── forms.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── views.py
│   │   ├── charts/
│   │   │   ├── __init__.py
│   │   │   └── views.py
│   │   └── home/
│   │       ├── __init__.py
│   │       └── views.py
│   │
│   ├── utils/                       # ⭐ NUEVO: Utilidades
│   │   ├── __init__.py
│   │   ├── logger.py                # Sistema logging
│   │   ├── decorators.py            # Decoradores custom
│   │   ├── validators.py            # Validaciones
│   │   └── helpers.py               # Funciones auxiliares
│   │
│   ├── exceptions/                  # ⭐ NUEVO: Excepciones custom
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── business_exceptions.py
│   │
│   ├── static/
│   └── templates/
│
├── scripts/                         # Scripts externos
├── migrations/
├── tests/
│   ├── unit/                        # Tests unitarios por capa
│   │   ├── test_repositories/
│   │   ├── test_services/
│   │   └── test_models/
│   └── integration/                 # Tests integración
│
├── logs/                            # ⭐ NUEVO: Logs aplicación
├── run.py
├── manage.py
└── requirements.txt
```

---

## 📋 Fases de Implementación

### **FASE 0: Preparación** (30 min)

**Objetivo**: Preparar el entorno sin romper funcionalidad

#### Tareas:
- [ ] Crear backup del proyecto
- [ ] Verificar que tests actuales pasan
- [ ] Corregir `requirements.txt` (encoding UTF-16 → UTF-8)
- [ ] Crear estructura de directorios vacía
- [ ] Actualizar `.gitignore` para nuevas carpetas

#### Entregables:
- Backup en `backup_YYYY-MM-DD/`
- Reporte de tests baseline
- `requirements.txt` corregido

#### Comandos:
```bash
# Backup
cp -r . ../backup_$(date +%Y%m%d)

# Ejecutar tests baseline
python -m pytest --verbose --tb=short

# Crear estructura
mkdir -p infocodest/{repositories,services,utils,exceptions,blueprints}
mkdir -p config logs
```

---

### **FASE 1: Capa de Repositorios** (2-3 horas)

**Objetivo**: Centralizar todo el acceso a datos

#### 1.1 Crear Repositorio Base
**Archivo**: `infocodest/repositories/base_repository.py`

```python
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from infocodest.extensions import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Repositorio genérico con operaciones CRUD básicas"""

    def __init__(self, model_class: type[T]):
        self.model_class = model_class
        self.session: Session = db.session

    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.query(self.model_class).get(id)

    def get_all(self) -> List[T]:
        return self.session.query(self.model_class).all()

    def filter_by(self, **kwargs) -> List[T]:
        return self.session.query(self.model_class).filter_by(**kwargs).all()

    def create(self, **kwargs) -> T:
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance

    def update(self, instance: T) -> T:
        self.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        self.session.delete(instance)
        self.session.commit()
```

#### 1.2 Crear Repositorios Específicos

**Archivo**: `infocodest/repositories/metrica_repository.py`

```python
from typing import List, Optional
from datetime import date
from infocodest.repositories.base_repository import BaseRepository
from infocodest.models.metricas import Metrica
from infocodest.models.proveedor import Proveedor
from sqlalchemy import func, desc

class MetricaRepository(BaseRepository[Metrica]):

    def __init__(self):
        super().__init__(Metrica)

    def get_distinct_applications(self) -> List[str]:
        """Obtiene aplicaciones únicas"""
        return [app[0] for app in
                self.session.query(Metrica.aplicacion).distinct().all()]

    def get_metricas_with_proveedor(self) -> List[Metrica]:
        """Métricas con join a proveedor, ordenadas por fecha"""
        return (self.session.query(Metrica)
                .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion)
                .order_by(desc(Metrica.fecha))
                .all())

    def get_by_aplicacion(self, aplicacion: str) -> List[Metrica]:
        """Filtra métricas por aplicación"""
        return (self.session.query(Metrica)
                .filter(Metrica.aplicacion == aplicacion)
                .order_by(Metrica.fecha.asc())
                .all())

    def count_total_apps(self) -> int:
        """Cuenta aplicaciones únicas"""
        return self.session.query(func.count(func.distinct(Metrica.aplicacion))).scalar()

    def count_total_repos(self) -> int:
        """Cuenta repositorios totales"""
        return self.session.query(func.count(Metrica.repo)).scalar()

    def sum_total_bugs(self) -> int:
        """Suma total de bugs"""
        return self.session.query(func.sum(Metrica.bugs)).scalar() or 0
```

#### 1.3 Migrar Queries de `models/database.py`

**Mapeo de funciones**:
- `getDatosMetricas()` → `DashboardRepository.get_kpi_metrics()`
- `getDatosAplicacion()` → `DashboardRepository.get_kpi_by_app()`
- `getDatosProveedor()` → `DashboardRepository.get_kpi_by_provider()`

#### Tareas:
- [ ] Crear `base_repository.py`
- [ ] Crear `metrica_repository.py`
- [ ] Crear `historico_repository.py`
- [ ] Crear `proveedor_repository.py`
- [ ] Crear `daily_repository.py`
- [ ] Crear `user_repository.py`
- [ ] Migrar todas las queries SQL de `models/database.py`
- [ ] Escribir tests unitarios para cada repositorio

#### Criterio de Éxito:
- Todas las queries SQL están en repositorios
- `models/database.py` marcado para eliminación
- 100% cobertura de tests en repositorios

---

### **FASE 2: Capa de Servicios** (3-4 horas)

**Objetivo**: Extraer lógica de negocio de las vistas

#### 2.1 Crear Servicio de Dashboard

**Archivo**: `infocodest/services/dashboard_service.py`

```python
from typing import Dict, Any
from datetime import datetime, timedelta
from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.repositories.daily_repository import DailyRepository
from infocodest.repositories.historico_repository import HistoricoRepository

class DashboardService:
    """Servicio para lógica de negocio del dashboard"""

    def __init__(self):
        self.metrica_repo = MetricaRepository()
        self.daily_repo = DailyRepository()
        self.historico_repo = HistoricoRepository()

    def get_kpi_overview(self, days: int = 15) -> Dict[str, Any]:
        """
        Calcula KPIs generales del dashboard

        Args:
            days: Número de días para comparación

        Returns:
            Dict con KPIs y variaciones porcentuales
        """
        fecha_comparacion = (datetime.now() - timedelta(days=days)).date()

        # Datos actuales
        current_data = {
            'aplicaciones': self.metrica_repo.count_total_apps(),
            'repositorios': self.metrica_repo.count_total_repos(),
            'bugs': self.metrica_repo.sum_total_bugs(),
            'analisis': self.historico_repo.count_total_analysis(),
            'quality': self.historico_repo.count_ok_quality_gates()
        }

        # Datos históricos
        old_data = self.daily_repo.get_metrics_by_date(fecha_comparacion)

        # Calcular variaciones
        return self._calculate_variations(current_data, old_data, days)

    def get_kpi_by_application(self, app_name: str, days: int = 15) -> Dict[str, Any]:
        """KPIs filtrados por aplicación"""
        # Implementación similar
        pass

    def _calculate_variations(
        self,
        current: Dict[str, int],
        old: Dict[str, int],
        days: int
    ) -> Dict[str, Any]:
        """
        Calcula variaciones porcentuales

        Migrado de: models/database.py::calcular_datos()
        """
        result = {}
        for key in current.keys():
            current_val = current[key]
            old_val = old.get(key, 0)

            # Calcular porcentaje
            if old_val == 0 and current_val == 0:
                variation = 0.0
                trend = "Igual"
            elif old_val == 0:
                variation = 100.0
                trend = "Increase"
            else:
                variation = ((current_val / old_val) * 100) - 100
                trend = "Decrease" if variation < 0 else "Increase"

            result[key] = current_val
            result[f'{key}_value'] = round(variation, 2)
            result[f'{key}_text'] = f'{variation:.2f}% {trend} in {days} Days'

        return result
```

#### 2.2 Crear Servicio de Métricas

**Archivo**: `infocodest/services/metrica_service.py`

```python
from typing import List, Dict, Any
from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.repositories.proveedor_repository import ProveedorRepository

class MetricaService:
    """Servicio para operaciones con métricas"""

    def __init__(self):
        self.metrica_repo = MetricaRepository()
        self.proveedor_repo = ProveedorRepository()

    def get_metricas_dashboard(self) -> List[Dict[str, Any]]:
        """
        Obtiene métricas formateadas para el dashboard

        Migrado de: home/views.py::get_metricas()
        """
        metricas = self.metrica_repo.get_metricas_with_proveedor()

        return [
            {
                'aplicacion': m.aplicacion,
                'repo': m.repo,
                'size': m.size,
                'fecha': m.fecha,
                'reliability_label': m.reliability_label,
                'reliability_rating': m.reliability_rating,
                'bugs': m.bugs,
                'security_label': m.security_label,
                'security_rating': m.security_rating,
                'vulnerabilities': m.vulnerabilities,
                'sqale_label': m.sqale_label,
                'sqale_rating': m.sqale_rating,
                'code_smells': m.code_smells,
                'alert_status': m.alert_status,
                'quality_gate': m.quality_gate,
                'project': m.project,
                'coverage': m.coverage,
                'unit_tests': m.unit_tests,
                'tipo': m.proveedor.tipo if m.proveedor else None
            }
            for m in metricas
        ]

    def get_distinct_applications(self) -> List[str]:
        """Lista de aplicaciones únicas"""
        return self.metrica_repo.get_distinct_applications()

    def get_metrics_by_application(self, app_name: str) -> List[Dict[str, Any]]:
        """Métricas de una aplicación específica"""
        return self.metrica_repo.get_by_aplicacion(app_name)
```

#### Tareas:
- [ ] Crear `dashboard_service.py`
- [ ] Crear `metrica_service.py`
- [ ] Crear `stats_service.py`
- [ ] Crear `auth_service.py`
- [ ] Migrar lógica de `models/database.py` a servicios
- [ ] Migrar funciones helper de vistas a servicios
- [ ] Escribir tests unitarios con mocks

#### Criterio de Éxito:
- Servicios no tienen dependencias de Flask (request, session)
- Servicios son testeables en aislamiento
- Lógica de negocio extraída de vistas

---

### **FASE 3: Refactorizar Vistas** (2-3 horas)

**Objetivo**: Vistas delgadas que solo manejan HTTP

#### 3.1 Refactorizar Home Views

**Antes** (`home/views.py`):
```python
@home_bp.route('/metricas')
@login_required
def metricas():
    metricas = Metrica.query \
        .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion) \
        .order_by(Metrica.fecha.desc()) \
        .with_entities(...) \
        .all()

    # ... más lógica ...

    return render_template('home/metricas.html', metricas=metricas)
```

**Después**:
```python
from infocodest.services.metrica_service import MetricaService
from infocodest.utils.decorators import inject_service

@home_bp.route('/metricas')
@login_required
@inject_service(MetricaService)
def metricas(metrica_service: MetricaService):
    """Vista de métricas - solo presentación"""
    metricas = metrica_service.get_metricas_dashboard()
    return render_template('home/metricas.html', metricas=metricas)
```

#### 3.2 Refactorizar API Views

**Antes** (`api/views.py`):
```python
@api_bp.route("/api/aplicacion/<aplicacion>")
def historico_project(aplicacion):
    data = {}
    metricas = Metrica.query.filter(Metrica.aplicacion == aplicacion).order_by(Metrica.fecha.asc()).all()
    data["project_name"] = [row.repo for row in metricas]
    # ... más transformaciones ...
    return jsonify(data)
```

**Después**:
```python
from infocodest.services.metrica_service import MetricaService

@api_bp.route("/api/aplicacion/<aplicacion>")
@inject_service(MetricaService)
def historico_project(aplicacion: str, metrica_service: MetricaService):
    """API endpoint - solo serialización"""
    data = metrica_service.get_historico_serialized(aplicacion)
    return jsonify(data)
```

#### Tareas:
- [ ] Mover blueprints a `infocodest/blueprints/`
- [ ] Refactorizar `home/views.py`
- [ ] Refactorizar `api/views.py`
- [ ] Refactorizar `charts/views.py`
- [ ] Refactorizar `accounts/views.py`
- [ ] Implementar decorador `@inject_service`
- [ ] Actualizar imports en `__init__.py`

#### Criterio de Éxito:
- Vistas tienen máximo 20 líneas
- Sin queries SQL en vistas
- Sin lógica de negocio en vistas

---

### **FASE 4: Sistema de Utilidades** (1-2 horas)

**Objetivo**: Centralizar funcionalidades transversales

#### 4.1 Logger Estructurado

**Archivo**: `infocodest/utils/logger.py`

```python
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from flask import Flask, has_request_context, request

class RequestFormatter(logging.Formatter):
    """Formateador que incluye contexto de request"""

    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None

        return super().format(record)

def setup_logging(app: Flask):
    """
    Configura logging estructurado para la aplicación

    Niveles:
    - DEBUG: logs/debug.log (rotación 10MB)
    - INFO: logs/info.log (rotación 10MB)
    - ERROR: logs/error.log (rotación 10MB)
    - Console: INFO en desarrollo, WARNING en producción
    """
    logs_dir = Path(app.root_path).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)

    # Formato
    file_formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s '
        '[%(pathname)s:%(lineno)d] [%(method)s %(url)s %(remote_addr)s]'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler de archivo con rotación
    info_handler = RotatingFileHandler(
        logs_dir / 'info.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(file_formatter)

    error_handler = RotatingFileHandler(
        logs_dir / 'error.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(
        logging.DEBUG if app.config['DEBUG'] else logging.WARNING
    )
    console_handler.setFormatter(console_formatter)

    # Configurar logger de la app
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(info_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)

    # Remover handlers por defecto
    app.logger.handlers = [h for h in app.logger.handlers
                           if not isinstance(h, logging.StreamHandler)]
```

#### 4.2 Decoradores Útiles

**Archivo**: `infocodest/utils/decorators.py`

```python
from functools import wraps
from typing import Type, Callable
from flask import current_app

def inject_service(service_class: Type):
    """
    Decorador para inyectar servicios en vistas

    Uso:
        @inject_service(MetricaService)
        def my_view(metrica_service: MetricaService):
            ...
    """
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            service = service_class()
            return f(*args, **kwargs, **{
                f'{service_class.__name__.lower().replace("service", "_service")}': service
            })
        return decorated_function
    return decorator

def log_execution_time(f: Callable):
    """Loguea tiempo de ejecución de función"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import time
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        current_app.logger.info(
            f'{f.__name__} executed in {end - start:.2f}s'
        )
        return result
    return decorated_function
```

#### 4.3 Validadores

**Archivo**: `infocodest/utils/validators.py`

```python
from typing import Optional
from datetime import date, datetime

def validate_date_range(
    start_date: Optional[date],
    end_date: Optional[date]
) -> bool:
    """Valida que rango de fechas sea coherente"""
    if start_date and end_date:
        return start_date <= end_date
    return True

def validate_application_name(app_name: str) -> bool:
    """Valida formato de nombre de aplicación"""
    return bool(app_name and len(app_name) <= 255)
```

#### Tareas:
- [ ] Crear `utils/logger.py`
- [ ] Crear `utils/decorators.py`
- [ ] Crear `utils/validators.py`
- [ ] Crear `utils/helpers.py`
- [ ] Integrar logger en `__init__.py`
- [ ] Reemplazar `print()` por `logger`

#### Criterio de Éxito:
- No hay `print()` en el código
- Logs estructurados en archivos rotativos
- Sistema de inyección de dependencias funcional

---

### **FASE 5: Manejo de Excepciones** (1 hora)

**Objetivo**: Excepciones custom para mejor control de errores

#### 5.1 Excepciones Base

**Archivo**: `infocodest/exceptions/base.py`

```python
class ApplicationException(Exception):
    """Excepción base de la aplicación"""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class BusinessException(ApplicationException):
    """Excepción de lógica de negocio"""

    def __init__(self, message: str):
        super().__init__(message, status_code=422)
```

**Archivo**: `infocodest/exceptions/business_exceptions.py`

```python
from infocodest.exceptions.base import BusinessException

class ApplicationNotFoundException(BusinessException):
    def __init__(self, app_name: str):
        super().__init__(f'Application not found: {app_name}')

class InvalidDateRangeException(BusinessException):
    def __init__(self):
        super().__init__('Invalid date range provided')

class MetricNotFoundException(BusinessException):
    def __init__(self, metric_id: int):
        super().__init__(f'Metric not found: {metric_id}')
```

#### 5.2 Error Handlers

**Actualizar**: `infocodest/errorhandlers.py`

```python
from flask import jsonify, render_template
from infocodest.exceptions.base import ApplicationException, BusinessException

def register_error_handlers(app):
    """Registra manejadores de errores personalizados"""

    @app.errorhandler(BusinessException)
    def handle_business_exception(error):
        app.logger.warning(f'Business exception: {error.message}')

        if error.status_code >= 500:
            return render_template('errors/500.html'), error.status_code
        return render_template('errors/422.html', error=error.message), 422

    @app.errorhandler(ApplicationException)
    def handle_app_exception(error):
        app.logger.error(f'Application exception: {error.message}')
        return render_template('errors/500.html'), error.status_code

    # Mantener handlers existentes
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
```

#### Tareas:
- [ ] Crear estructura `exceptions/`
- [ ] Implementar excepciones custom
- [ ] Actualizar error handlers
- [ ] Usar excepciones en servicios

---

### **FASE 6: Configuración Mejorada** (1 hora)

**Objetivo**: Configuración centralizada y tipo-segura

#### 6.1 Configuración Base

**Archivo**: `config/base.py`

```python
import os
from pathlib import Path
from typing import Optional

basedir = Path(__file__).parent.parent.absolute()

class BaseConfig:
    """Configuración base compartida"""

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_hex(32)

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # CSRF
    WTF_CSRF_ENABLED = True
    CSRF_ENABLED = True

    # Assets
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    # Application
    DAYS_COMPARISON = int(os.getenv('DAYS_COMPARISON', '15'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = basedir / 'logs'

    @staticmethod
    def init_app(app):
        """Hook para inicialización custom"""
        pass
```

**Archivo**: `config/development.py`

```python
from config.base import BaseConfig, basedir

class DevelopmentConfig(BaseConfig):
    """Configuración de desarrollo"""

    DEBUG = True
    TESTING = False

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'db.sqlite3'}"
    SQLALCHEMY_ECHO = True  # SQL queries en consola

    WTF_CSRF_ENABLED = False  # Facilitar testing manual

    LOG_LEVEL = 'DEBUG'
```

**Archivo**: `config/production.py`

```python
import os
from config.base import BaseConfig, basedir

class ProductionConfig(BaseConfig):
    """Configuración de producción"""

    DEBUG = False
    TESTING = False

    # Base de datos desde env vars
    DB_ENGINE = os.getenv('DB_ENGINE')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

    if all([DB_ENGINE, DB_USERNAME, DB_NAME]):
        SQLALCHEMY_DATABASE_URI = (
            f'{DB_ENGINE}://{DB_USERNAME}:{DB_PASSWORD}'
            f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'db.sqlite3'}"

    # Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # Solo HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = 3600

    LOG_LEVEL = 'WARNING'

    @staticmethod
    def init_app(app):
        # Configuración específica de producción
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)
```

#### Tareas:
- [ ] Crear estructura `config/`
- [ ] Migrar configuración de `config.py` raíz
- [ ] Actualizar referencias en código
- [ ] Añadir validación de config requerida

---

### **FASE 7: Optimización de Dependencias** (30 min)

**Objetivo**: Limpiar y organizar dependencias

#### 7.1 Corregir Requirements

**Nuevo**: `requirements.txt` (UTF-8, con versiones pinadas)

```txt
# Flask Core
Flask==3.0.0
Werkzeug==3.0.1

# Database
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
alembic==1.12.1

# Authentication
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
bcrypt==4.0.1

# Forms & Validation
Flask-WTF==1.2.1
WTForms==3.1.1
email-validator==2.1.0

# UI
Flask-Bootstrap==3.3.7.1
dominate==2.9.0

# Security
Flask-CORS==4.0.1

# Performance
Flask-Minify==0.42

# Email
secure-smtplib==0.1.1

# Scheduling
schedule==1.2.0

# Environment
python-decouple==3.8
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
Flask-Testing==0.8.1
```

**Nuevo**: `requirements-dev.txt`

```txt
-r requirements.txt

# Development tools
black==23.12.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.0

# Testing
pytest-mock==3.12.0
pytest-flask==1.3.0
coverage==7.3.3

# Documentation
sphinx==7.2.6
```

#### Tareas:
- [ ] Recrear `requirements.txt` en UTF-8
- [ ] Separar dependencias dev
- [ ] Actualizar versiones seguras
- [ ] Verificar instalación limpia

---

### **FASE 8: Actualizar Entry Points** (30 min)

**Objetivo**: Actualizar run.py y __init__.py

#### 8.1 Factory App Mejorado

**Actualizar**: `infocodest/__init__.py`

```python
from flask import Flask
from flask_cors import CORS

from infocodest.extensions import db, login_manager, migrate, bootstrap, csrf
from infocodest.utils.logger import setup_logging
from infocodest.errorhandlers import register_error_handlers

def register_blueprints(app: Flask):
    """Registra blueprints de la aplicación"""
    from infocodest.blueprints.accounts.views import accounts_bp
    from infocodest.blueprints.home.views import home_bp
    from infocodest.blueprints.charts.views import charts_bp
    from infocodest.blueprints.api.views import api_bp

    app.register_blueprint(accounts_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(charts_bp, url_prefix='/charts')
    app.register_blueprint(api_bp)

def initialize_extensions(app: Flask):
    """Inicializa extensiones Flask"""
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    csrf.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

def create_app(config_object):
    """
    Factory pattern para crear aplicación Flask

    Args:
        config_object: Clase de configuración (DevelopmentConfig, etc.)
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Inicializar config custom
    config_object.init_app(app)

    with app.app_context():
        # Setup logging
        setup_logging(app)

        # Initialize extensions
        initialize_extensions(app)

        # Register blueprints
        register_blueprints(app)

        # Register error handlers
        register_error_handlers(app)

        app.logger.info(f'Application started - Environment: {config_object.__name__}')

    return app
```

#### 8.2 Run Script Mejorado

**Actualizar**: `run.py`

```python
import os
from dotenv import load_dotenv, find_dotenv
from flask_minify import Minify

from infocodest import create_app
from config.development import DevelopmentConfig
from config.production import ProductionConfig
from config.testing import TestingConfig

# Cargar variables de entorno
load_dotenv(find_dotenv())

# Determinar configuración
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
TESTING = os.getenv("TESTING", "False").lower() == "true"

if TESTING:
    config = TestingConfig
elif DEBUG:
    config = DevelopmentConfig
else:
    config = ProductionConfig

# Crear aplicación
app = create_app(config)

# Minificación en producción
if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=DEBUG
    )
```

---

### **FASE 9: Tests y Validación** (2-3 horas)

**Objetivo**: Asegurar que todo funciona

#### 9.1 Tests Unitarios por Capa

**Tests de Repositorios**: `tests/unit/test_repositories/test_metrica_repository.py`

```python
import pytest
from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.models.metricas import Metrica

class TestMetricaRepository:

    @pytest.fixture
    def repo(self, app):
        with app.app_context():
            return MetricaRepository()

    def test_get_distinct_applications(self, repo, sample_metricas):
        apps = repo.get_distinct_applications()
        assert len(apps) > 0
        assert isinstance(apps[0], str)

    def test_count_total_apps(self, repo, sample_metricas):
        count = repo.count_total_apps()
        assert isinstance(count, int)
        assert count >= 0
```

**Tests de Servicios**: `tests/unit/test_services/test_dashboard_service.py`

```python
import pytest
from unittest.mock import Mock, patch
from infocodest.services.dashboard_service import DashboardService

class TestDashboardService:

    @pytest.fixture
    def service(self):
        return DashboardService()

    @patch('infocodest.services.dashboard_service.MetricaRepository')
    def test_get_kpi_overview(self, mock_repo, service):
        # Mock repositorio
        mock_repo.return_value.count_total_apps.return_value = 10

        result = service.get_kpi_overview()

        assert 'aplicaciones' in result
        assert result['aplicaciones'] == 10
```

#### Tareas:
- [ ] Tests unitarios de repositorios
- [ ] Tests unitarios de servicios (con mocks)
- [ ] Tests integración de vistas
- [ ] Verificar cobertura >80%
- [ ] Actualizar tests existentes

---

### **FASE 10: Documentación y Limpieza** (1 hora)

**Objetivo**: Documentar cambios y limpiar código legacy

#### Tareas:
- [ ] Actualizar README.md con nueva estructura
- [ ] Documentar arquitectura en ARCHITECTURE.md
- [ ] Añadir docstrings a todos los módulos
- [ ] Eliminar archivos deprecated:
  - `models/database.py`
  - Funciones duplicadas
- [ ] Actualizar .gitignore

#### Entregables:
- `ARCHITECTURE.md` con diagramas
- `README.md` actualizado
- `MIGRATION_GUIDE.md` para el equipo

---

## 📊 Métricas de Éxito

### Antes vs Después

| Métrica | Antes | Objetivo |
|---------|-------|----------|
| Líneas por vista | ~100 | <30 |
| Cobertura tests | ~60% | >80% |
| Complejidad ciclomática | >10 | <5 |
| Tiempo respuesta API | ~200ms | <100ms |
| Queries por request | ~10 | <5 |
| Archivos con SQL raw | 5 | 0 |

### KPIs de Calidad

- ✅ Separación de responsabilidades (SoC)
- ✅ Principio de única responsabilidad (SRP)
- ✅ Inyección de dependencias
- ✅ Testabilidad (>80% cobertura)
- ✅ Logging estructurado
- ✅ Manejo de errores robusto

---

## 🚨 Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Romper funcionalidad existente | Media | Alto | Tests completos antes/después cada fase |
| Regresión en performance | Baja | Medio | Benchmarks antes/después |
| Conflictos en merge | Media | Bajo | Feature branch + revisión código |
| Tiempo estimado insuficiente | Alta | Medio | Fases independientes, priorizar 1-3 |

---

## 📅 Timeline Estimado

| Fase | Duración | Dependencias |
|------|----------|--------------|
| 0. Preparación | 30 min | - |
| 1. Repositorios | 2-3h | Fase 0 |
| 2. Servicios | 3-4h | Fase 1 |
| 3. Vistas | 2-3h | Fase 2 |
| 4. Utilidades | 1-2h | - |
| 5. Excepciones | 1h | Fase 4 |
| 6. Configuración | 1h | - |
| 7. Dependencias | 30 min | - |
| 8. Entry points | 30 min | Fases 1-7 |
| 9. Tests | 2-3h | Fases 1-8 |
| 10. Documentación | 1h | Fase 9 |

**Total estimado**: 14-20 horas
**Recomendación**: Ejecutar en sprints de 2-3 fases por semana

---

## 🎯 Orden de Ejecución Recomendado

### Sprint 1 (Core Architecture)
1. Fase 0: Preparación
2. Fase 1: Repositorios
3. Fase 2: Servicios

### Sprint 2 (Presentation & Utils)
4. Fase 3: Vistas
5. Fase 4: Utilidades
6. Fase 5: Excepciones

### Sprint 3 (Polish & Validate)
7. Fase 6: Configuración
8. Fase 7: Dependencias
9. Fase 8: Entry points
10. Fase 9: Tests
11. Fase 10: Documentación

---

## 📚 Referencias y Recursos

- [Flask Best Practices](https://flask.palletsprojects.com/patterns/)
- [Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [12 Factor App](https://12factor.net/)

---

## ✅ Checklist de Pre-Implementación

Antes de ejecutar el plan:

- [ ] Backup completo del proyecto
- [ ] Tests actuales pasando
- [ ] Rama feature creada (`feature/refactor-architecture`)
- [ ] Equipo informado del alcance
- [ ] Entorno de desarrollo limpio
- [ ] Dependencias actualizadas

---

**Siguiente paso**: Ejecutar Fase 0 - Preparación
