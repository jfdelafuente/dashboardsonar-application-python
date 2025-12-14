# Arquitectura del Sistema - Dashboard Sonar

**Versión**: 2.0.0 (Post-Refactoring)
**Fecha**: 2025-12-14
**Autor**: Equipo de Desarrollo

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Diagrama de Arquitectura](#diagrama-de-arquitectura)
3. [Capas del Sistema](#capas-del-sistema)
4. [Flujo de Datos](#flujo-de-datos)
5. [Patrones de Diseño](#patrones-de-diseño)
6. [Decisiones Arquitectónicas](#decisiones-arquitectónicas)
7. [Componentes Transversales](#componentes-transversales)
8. [Diagrama de Componentes](#diagrama-de-componentes)
9. [Estrategia de Testing](#estrategia-de-testing)
10. [Consideraciones de Performance](#consideraciones-de-performance)
11. [Seguridad](#seguridad)
12. [Escalabilidad](#escalabilidad)
13. [Monitoreo y Observabilidad](#monitoreo-y-observabilidad)
14. [Referencias](#referencias)

---

## 🎯 Visión General

Dashboard Sonar es una aplicación web Flask que implementa una **arquitectura en capas (Layered Architecture)** con el objetivo de lograr:

- **Separación de responsabilidades** clara entre capas
- **Mantenibilidad** mediante código modular y testeable
- **Escalabilidad** horizontal y vertical
- **Testabilidad** con >80% de cobertura

### Principios Arquitectónicos

1. **Separation of Concerns (SoC)**: Cada capa tiene una responsabilidad única y bien definida
2. **Dependency Inversion**: Las capas superiores dependen de abstracciones, no de implementaciones
3. **Single Responsibility Principle (SRP)**: Cada módulo hace una sola cosa y la hace bien
4. **Don't Repeat Yourself (DRY)**: Código reutilizable centralizado en servicios y utilidades
5. **You Aren't Gonna Need It (YAGNI)**: Solo lo necesario, sin sobre-ingeniería

---

## 📊 Diagrama de Arquitectura

### Vista de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│              (Views / Blueprints / Templates)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Responsabilidades:                                 │   │
│  │  • Renderizar respuestas HTTP/HTML/JSON             │   │
│  │  • Validar entrada del usuario                      │   │
│  │  • Manejar routing y sesiones                       │   │
│  │  • Autorización (login_required)                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Inyección de Dependencias
                      │ (@inject_service decorator)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                            │
│                  (Business Logic)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Responsabilidades:                                 │   │
│  │  • Implementar lógica de negocio                    │   │
│  │  • Orquestar operaciones complejas                  │   │
│  │  • Coordinar múltiples repositorios                 │   │
│  │  • Manejar transacciones                            │   │
│  │  • Transformar datos para presentación              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Llamadas a métodos
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  REPOSITORY LAYER                           │
│                  (Data Access)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Responsabilidades:                                 │   │
│  │  • Abstraer acceso a base de datos                  │   │
│  │  • Encapsular queries SQL complejas                 │   │
│  │  • Operaciones CRUD genéricas                       │   │
│  │  • Queries específicas de dominio                   │   │
│  │  • Paginación y filtrado                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Query Builder (SQLAlchemy)
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                              │
│                 (Domain Models / ORM)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Responsabilidades:                                 │   │
│  │  • Definir estructura de entidades                  │   │
│  │  • Mapear tablas a objetos Python                   │   │
│  │  • Definir relaciones entre modelos                 │   │
│  │  • Validaciones básicas de datos                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ ORM (SQLAlchemy)
                      │
                      ▼
              ┌────────────────┐
              │    DATABASE    │
              │  PostgreSQL    │
              │    SQLite      │
              └────────────────┘
```

---

## 🏗️ Capas del Sistema

### 1. Presentation Layer (Capa de Presentación)

**Ubicación**: `infocodest/{home,api,accounts,charts}/views.py`

**Responsabilidad**: Manejar la interacción HTTP con el usuario

#### Componentes

- **Blueprints**: Módulos Flask para organizar rutas
  - `home`: Dashboard principal, métricas
  - `api`: Endpoints REST para datos
  - `accounts`: Autenticación y gestión de usuarios
  - `charts`: Visualizaciones y gráficos

- **Templates**: Plantillas Jinja2 para renderizar HTML
  - `base.html`: Template base con layout común
  - `home/index.html`: Dashboard principal
  - `errors/`: Páginas de error (404, 500, etc.)

#### Principios de las Vistas

```python
# ✅ CORRECTO: Vista delgada que delega a servicio
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

```python
# ❌ INCORRECTO: Vista con lógica de negocio y queries
@home_bp.route('/metricas')
@login_required
def metricas():
    # ❌ Queries SQL directas en vista
    metricas = Metrica.query \
        .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion) \
        .order_by(Metrica.fecha.desc()) \
        .all()

    # ❌ Lógica de negocio en vista
    for m in metricas:
        m.rating_color = 'red' if m.bugs > 10 else 'green'

    return render_template('home/metricas.html', metricas=metricas)
```

**Características**:
- ✅ Vistas <30 líneas de código
- ✅ Sin queries SQL directas
- ✅ Sin lógica de negocio
- ✅ Solo validación de entrada y renderizado

---

### 2. Service Layer (Capa de Servicio)

**Ubicación**: `infocodest/services/`

**Responsabilidad**: Implementar lógica de negocio

#### Archivos

| Servicio | Responsabilidad |
|----------|----------------|
| `dashboard_service.py` | KPIs, estadísticas del dashboard, cálculos de variación |
| `metrica_service.py` | Operaciones con métricas, formateo de datos |
| `auth_service.py` | Lógica de autenticación, registro de usuarios |

#### Ejemplo: DashboardService

```python
from typing import Dict, Any
from datetime import datetime, timedelta
from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.repositories.daily_repository import DailyRepository
from infocodest.repositories.historico_repository import HistoricoRepository

class DashboardService:
    """Servicio para lógica de negocio del dashboard"""

    def __init__(self):
        # Inyectar dependencias de repositorios
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

        Example:
            >>> service = DashboardService()
            >>> kpis = service.get_kpi_overview(days=30)
            >>> print(kpis['aplicaciones'])
            50
            >>> print(kpis['aplicaciones_text'])
            "5.20% Increase in 30 Days"
        """
        fecha_comparacion = (datetime.now() - timedelta(days=days)).date()

        # Datos actuales (orquestando múltiples repositorios)
        current_data = {
            'aplicaciones': self.metrica_repo.count_distinct_aplicaciones(),
            'repositorios': self.metrica_repo.count(),
            'bugs': self.metrica_repo.sum_bugs(),
            'analisis': self.historico_repo.count(),
            'quality_gates_ok': self.historico_repo.count_quality_gates_ok()
        }

        # Datos históricos
        old_data = self.daily_repo.get_metrics_by_date(fecha_comparacion)

        # Aplicar lógica de negocio: calcular variaciones
        return self._calculate_variations(current_data, old_data, days)

    def _calculate_variations(
        self,
        current: Dict[str, int],
        old: Dict[str, int],
        days: int
    ) -> Dict[str, Any]:
        """
        Calcula variaciones porcentuales entre métricas actuales e históricas

        Lógica de negocio:
        - Si ambos son 0: sin cambio (0%)
        - Si antiguo es 0 y nuevo >0: aumento del 100%
        - Caso normal: ((nuevo / antiguo) * 100) - 100
        """
        result = {}
        for key in current.keys():
            current_val = current[key]
            old_val = old.get(key, 0)

            # Calcular porcentaje de variación
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

**Características de los Servicios**:
- ✅ Sin dependencias de Flask (no usan `request`, `session`)
- ✅ Testeables en aislamiento (mock repositories)
- ✅ Orquestan múltiples repositorios
- ✅ Contienen lógica de negocio compleja
- ✅ Retornan datos procesados, no raw data

---

### 3. Repository Layer (Capa de Repositorio)

**Ubicación**: `infocodest/repositories/`

**Responsabilidad**: Abstraer acceso a datos

#### Archivos

| Repositorio | Modelo | Responsabilidad |
|-------------|--------|----------------|
| `base_repository.py` | Generic[T] | CRUD genérico para cualquier modelo |
| `metrica_repository.py` | Metrica | Queries específicas de métricas |
| `historico_repository.py` | Historico | Queries de datos históricos |
| `daily_repository.py` | Daily | Métricas diarias agregadas |
| `user_repository.py` | User | Gestión de usuarios |
| `proveedor_repository.py` | Proveedor | Gestión de proveedores |

#### Ejemplo: BaseRepository (Genérico)

```python
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from infocodest.extensions import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Repositorio base con operaciones CRUD genéricas

    Patrón Repository: Abstrae el acceso a datos y centraliza queries

    Uso:
        class MetricaRepository(BaseRepository[Metrica]):
            def __init__(self):
                super().__init__(Metrica)
    """

    def __init__(self, model_class: type[T]):
        self.model_class = model_class
        self.session: Session = db.session

    def get_by_id(self, id: int) -> Optional[T]:
        """Obtiene entidad por ID"""
        return self.session.query(self.model_class).get(id)

    def get_all(self) -> List[T]:
        """Obtiene todas las entidades"""
        return self.session.query(self.model_class).all()

    def filter_by(self, **kwargs) -> List[T]:
        """Filtra entidades por atributos"""
        return self.session.query(self.model_class).filter_by(**kwargs).all()

    def create(self, instance: T) -> T:
        """Crea nueva entidad"""
        self.session.add(instance)
        self.session.commit()
        return instance

    def update(self, instance: T) -> T:
        """Actualiza entidad existente"""
        self.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        """Elimina entidad"""
        self.session.delete(instance)
        self.session.commit()

    def count(self) -> int:
        """Cuenta total de entidades"""
        return self.session.query(self.model_class).count()
```

#### Ejemplo: MetricaRepository (Específico)

```python
from typing import List, Optional
from datetime import date
from sqlalchemy import func, desc
from infocodest.repositories.base_repository import BaseRepository
from infocodest.models.metricas import Metrica
from infocodest.models.proveedor import Proveedor

class MetricaRepository(BaseRepository[Metrica]):
    """
    Repositorio para operaciones con métricas

    Extiende BaseRepository con queries específicas de dominio
    """

    def __init__(self):
        super().__init__(Metrica)

    def get_distinct_aplicaciones(self) -> List[str]:
        """Obtiene lista de aplicaciones únicas"""
        return [
            app[0] for app in
            self.session.query(Metrica.aplicacion).distinct().all()
        ]

    def get_metricas_with_proveedor(self) -> List[Metrica]:
        """
        Obtiene métricas con join a proveedor, ordenadas por fecha

        Query compleja encapsulada en repositorio
        """
        return (
            self.session.query(Metrica)
            .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion)
            .order_by(desc(Metrica.fecha))
            .all()
        )

    def get_by_aplicacion(
        self,
        aplicacion: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Metrica]:
        """
        Filtra métricas por aplicación y rango de fechas

        Args:
            aplicacion: Nombre de la aplicación
            start_date: Fecha inicio (opcional)
            end_date: Fecha fin (opcional)

        Returns:
            Lista de métricas ordenadas por fecha ascendente
        """
        query = self.session.query(Metrica).filter(
            Metrica.aplicacion == aplicacion
        )

        if start_date:
            query = query.filter(Metrica.fecha >= start_date)
        if end_date:
            query = query.filter(Metrica.fecha <= end_date)

        return query.order_by(Metrica.fecha.asc()).all()

    def count_distinct_aplicaciones(self) -> int:
        """Cuenta aplicaciones únicas"""
        return self.session.query(
            func.count(func.distinct(Metrica.aplicacion))
        ).scalar()

    def sum_bugs(self) -> int:
        """Suma total de bugs de todas las métricas"""
        return self.session.query(func.sum(Metrica.bugs)).scalar() or 0
```

**Características de los Repositorios**:
- ✅ Abstracción sobre SQLAlchemy
- ✅ Un repositorio por modelo principal
- ✅ Queries complejas encapsuladas
- ✅ Métodos descriptivos (no `query()` genérico)
- ✅ Sin lógica de negocio (solo acceso a datos)

---

### 4. Model Layer (Capa de Modelo)

**Ubicación**: `infocodest/models/`

**Responsabilidad**: Definir estructura de entidades y relaciones

#### Archivos

| Modelo | Tabla | Descripción |
|--------|-------|-------------|
| `users.py` | `users` | Usuarios del sistema |
| `metricas.py` | `metricas` | Métricas de calidad de código |
| `historico.py` | `historico` | Histórico de análisis |
| `daily.py` | `daily` | Agregaciones diarias |
| `proveedor.py` | `proveedor` | Proveedores de servicios |
| `registros.py` | `registros` | Registros de eventos |
| `stat.py` | `stat` | Estadísticas generales |

#### Ejemplo: Modelo Metrica

```python
from infocodest.extensions import db
from datetime import date

class Metrica(db.Model):
    """
    Modelo de métricas de calidad de código

    Representa una medición de calidad en un momento específico
    para un repositorio de una aplicación
    """

    __tablename__ = 'metricas'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Identificación
    aplicacion = db.Column(db.String(255), nullable=False, index=True)
    repo = db.Column(db.String(255), nullable=False)
    project = db.Column(db.String(255))
    fecha = db.Column(db.Date, nullable=False, index=True, default=date.today)

    # Métricas de bugs
    bugs = db.Column(db.Integer, default=0)
    reliability_rating = db.Column(db.String(10))
    reliability_label = db.Column(db.String(50))

    # Métricas de seguridad
    vulnerabilities = db.Column(db.Integer, default=0)
    security_rating = db.Column(db.String(10))
    security_label = db.Column(db.String(50))

    # Code smells
    code_smells = db.Column(db.Integer, default=0)
    sqale_rating = db.Column(db.String(10))
    sqale_label = db.Column(db.String(50))

    # Cobertura
    coverage = db.Column(db.Float)
    unit_tests = db.Column(db.Integer)

    # Quality gate
    quality_gate = db.Column(db.String(50))
    alert_status = db.Column(db.String(50))

    # Tamaño
    size = db.Column(db.Integer)

    # Relación con Proveedor
    # lazy='joined' para eager loading (evitar N+1 queries)
    proveedor = db.relationship(
        'Proveedor',
        primaryjoin='foreign(Metrica.aplicacion) == Proveedor.aplicacion',
        lazy='joined',
        uselist=False
    )

    def __repr__(self):
        return f'<Metrica {self.aplicacion}/{self.repo} - {self.fecha}>'

    def to_dict(self):
        """Serializa modelo a diccionario"""
        return {
            'id': self.id,
            'aplicacion': self.aplicacion,
            'repo': self.repo,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'bugs': self.bugs,
            'vulnerabilities': self.vulnerabilities,
            'code_smells': self.code_smells,
            'coverage': self.coverage,
            'quality_gate': self.quality_gate
        }
```

**Características de los Modelos**:
- ✅ Solo definiciones ORM (SQLAlchemy)
- ✅ Relaciones entre modelos definidas
- ✅ Indexes en campos frecuentes (aplicacion, fecha)
- ✅ Método `to_dict()` para serialización
- ✅ Sin lógica de negocio (solo estructura)

---

## 🔄 Flujo de Datos

### Request → Response Flow

```
1. HTTP Request
   │
   ├──> GET /metricas
   │
   ▼
2. Routing (Flask)
   │
   ├──> @home_bp.route('/metricas')
   │
   ▼
3. Authentication
   │
   ├──> @login_required
   │
   ▼
4. Dependency Injection
   │
   ├──> @inject_service(MetricaService)
   │
   ▼
5. View Function (Presentation Layer)
   │
   ├──> def metricas(metrica_service):
   │    │
   │    ├──> Validar parámetros de entrada
   │    │
   │    ▼
6. Service Call (Service Layer)
   │    │
   │    ├──> metrica_service.get_metricas_dashboard()
   │    │    │
   │    │    ├──> Aplicar lógica de negocio
   │    │    │
   │    │    ▼
7. Repository Calls (Repository Layer)
   │    │    │
   │    │    ├──> metrica_repo.get_metricas_with_proveedor()
   │    │    │    │
   │    │    │    ▼
8. Database Query (Model Layer + SQLAlchemy)
   │    │    │    │
   │    │    │    ├──> SELECT * FROM metricas JOIN proveedor ...
   │    │    │    │
   │    │    │    ▼
9. Database (PostgreSQL / SQLite)
   │    │    │    │
   │    │    │    └──> Returns rows
   │    │    │
   │    │    ├──> Maps to Metrica objects
   │    │    │
   │    │    └──> Returns List[Metrica]
   │    │
   │    ├──> Transforms to dict/JSON
   │    │
   │    └──> Returns processed data
   │
   ├──> Render template with data
   │
   ▼
10. HTTP Response
    │
    └──> HTML / JSON returned to client
```

### Ejemplo Completo de Flujo

```python
# 1. Request: GET /metricas

# 2-5. Vista (Presentation Layer)
@home_bp.route('/metricas')
@login_required
@inject_service(MetricaService)
def metricas(metrica_service: MetricaService):
    # 6. Llamada a servicio
    metricas = metrica_service.get_metricas_dashboard()

    # 10. Renderizar respuesta
    return render_template('home/metricas.html', metricas=metricas)

# 6. Servicio (Service Layer)
class MetricaService:
    def get_metricas_dashboard(self) -> List[Dict[str, Any]]:
        # 7. Llamada a repositorio
        metricas = self.metrica_repo.get_metricas_with_proveedor()

        # Lógica de negocio: transformar a dict
        return [self._metrica_to_dict(m) for m in metricas]

# 7-9. Repositorio (Repository Layer)
class MetricaRepository(BaseRepository[Metrica]):
    def get_metricas_with_proveedor(self) -> List[Metrica]:
        # 8-9. Query a base de datos
        return self.session.query(Metrica)\
            .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion)\
            .order_by(desc(Metrica.fecha))\
            .all()
```

---

## 🎨 Patrones de Diseño

### 1. Repository Pattern

**Propósito**: Abstraer el acceso a datos y centralizar queries

**Implementación**:
```python
# Repositorio abstrae SQLAlchemy
metrica_repo = MetricaRepository()
metricas = metrica_repo.get_by_aplicacion('myapp')

# En lugar de queries directas en vistas
metricas = Metrica.query.filter_by(aplicacion='myapp').all()
```

**Beneficios**:
- ✅ Cambio de ORM sin afectar servicios
- ✅ Testing fácil (mock repositorios)
- ✅ Queries centralizadas y reutilizables

---

### 2. Service Layer Pattern

**Propósito**: Centralizar lógica de negocio

**Implementación**:
```python
# Servicio orquesta múltiples repositorios
class DashboardService:
    def get_kpi_overview(self):
        apps = self.metrica_repo.count_distinct_aplicaciones()
        repos = self.metrica_repo.count()
        # Lógica de negocio: calcular KPIs
        return self._calculate_kpis(apps, repos)
```

**Beneficios**:
- ✅ Vistas delgadas (<30 líneas)
- ✅ Lógica reutilizable
- ✅ Testeable en aislamiento

---

### 3. Dependency Injection

**Propósito**: Desacoplar componentes

**Implementación**:
```python
# Decorador inyecta servicio en vista
@inject_service(MetricaService)
def my_view(metrica_service: MetricaService):
    data = metrica_service.get_data()
    return render_template('template.html', data=data)
```

**Beneficios**:
- ✅ No acoplamiento fuerte
- ✅ Testing fácil (inyectar mocks)
- ✅ Configuración centralizada

---

### 4. Factory Pattern

**Propósito**: Crear aplicación Flask con configuración dinámica

**Implementación**:
```python
# run.py
config = DevelopmentConfig if DEBUG else ProductionConfig
app = create_app(config)

# infocodest/__init__.py
def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    # Inicializar extensiones, blueprints, etc.
    return app
```

**Beneficios**:
- ✅ Configuración por entorno
- ✅ Testing con configuración mock
- ✅ Múltiples instancias de app

---

## 🤔 Decisiones Arquitectónicas

### ADR 1: ¿Por qué Layered Architecture?

**Contexto**: Necesitamos refactorizar aplicación monolítica con SQL en vistas

**Decisión**: Implementar arquitectura en capas (Presentation → Service → Repository → Model)

**Razones**:
1. **Separación de responsabilidades**: Cada capa tiene un propósito claro
2. **Mantenibilidad**: Cambios aislados a una capa no afectan otras
3. **Testabilidad**: Cada capa testeable independientemente
4. **Escalabilidad**: Fácil añadir nuevas features sin romper existente
5. **Simplicidad**: Patrón bien conocido, documentación abundante

**Consecuencias**:
- ✅ Código más mantenible y testeable
- ✅ Onboarding de nuevos desarrolladores más fácil
- ⚠️ Más archivos y código boilerplate
- ⚠️ Overhead pequeño en performance (negligible)

**Alternativas Consideradas**:
- Microservicios: Complejidad innecesaria para tamaño actual
- Hexagonal Architecture: Demasiado complejo para el equipo

---

### ADR 2: ¿Por qué Repository Pattern?

**Contexto**: Queries SQL dispersas en vistas y modelos

**Decisión**: Centralizar acceso a datos en repositorios

**Razones**:
1. **Abstracción**: Ocultar detalles de SQLAlchemy
2. **Reutilización**: Queries complejas usadas en múltiples lugares
3. **Testing**: Mock repositorios en tests de servicios
4. **Cambio de ORM**: Posible migración futura sin afectar servicios

**Consecuencias**:
- ✅ Queries centralizadas y reutilizables
- ✅ Testing mucho más fácil
- ⚠️ Capa adicional (boilerplate)

---

### ADR 3: ¿Por qué NO Microservicios?

**Contexto**: ¿Deberíamos dividir la aplicación en microservicios?

**Decisión**: Mantener monolito modular (layered architecture)

**Razones**:
1. **Complejidad innecesaria**: Equipo pequeño, aplicación mediana
2. **Overhead de comunicación**: Latencia de red entre servicios
3. **Deployment más complejo**: Múltiples servicios a desplegar
4. **Transacciones distribuidas**: Difíciles de manejar
5. **Preparado para migración**: Arquitectura permite migrar a microservicios si crece

**Consecuencias**:
- ✅ Simplicidad de deployment y testing
- ✅ Transacciones ACID simples
- ✅ Mejor performance (sin latencia de red)
- ⚠️ Escalado horizontal más limitado (pero suficiente)

---

### ADR 4: Configuración por Entorno

**Contexto**: ¿Cómo manejar configuración development/production?

**Decisión**: Clases de configuración heredando de base

**Razones**:
1. **Type-safe**: Configuración en código Python, no archivos
2. **Herencia**: Compartir configuración común
3. **Environment-specific**: Sobreescribir solo lo necesario
4. **Validación**: Detectar errores de configuración temprano

**Implementación**:
```python
# config/base.py
class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# config/development.py
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

# config/production.py
class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
```

---

## 🔧 Componentes Transversales

### Utils (Utilidades)

**Ubicación**: `infocodest/utils/`

#### logger.py - Sistema de Logging

```python
from infocodest.utils.logger import setup_logging

# Configurar logging en create_app()
setup_logging(app)

# Usar en código
app.logger.info('Application started')
app.logger.error('Error occurred', exc_info=True)
```

**Características**:
- Logging estructurado con contexto de request
- Rotación de archivos (10MB, 10 backups)
- Niveles: DEBUG, INFO, WARNING, ERROR
- Formato: `[timestamp] LEVEL in module: message [file:line] [method url ip]`

#### decorators.py - Decoradores Custom

```python
# Inyección de servicios
@inject_service(MetricaService)
def my_view(metrica_service: MetricaService):
    pass

# Logging de tiempo de ejecución
@log_execution_time
def slow_function():
    pass
```

#### validators.py - Validaciones

```python
from infocodest.utils.validators import (
    validate_date_range,
    validate_application_name,
    validate_email
)

# Validar rango de fechas
if not validate_date_range(start_date, end_date):
    raise InvalidDateRangeException()
```

#### helpers.py - Funciones Auxiliares

```python
from infocodest.utils.helpers import (
    format_number,
    calculate_percentage,
    truncate_text
)

formatted = format_number(1234567)  # "1,234,567"
percentage = calculate_percentage(80, 100)  # 80.0
```

---

### Exceptions (Excepciones)

**Ubicación**: `infocodest/exceptions/`

#### Jerarquía de Excepciones

```
ApplicationException (base)
    │
    ├── BusinessException
    │   ├── ValidationException
    │   │   ├── InvalidApplicationNameException
    │   │   ├── InvalidMetricValueException
    │   │   └── InvalidDateRangeException
    │   │
    │   └── NotFoundException
    │       ├── ApplicationNotFoundException
    │       └── MetricNotFoundException
    │
    └── TechnicalException
        ├── DatabaseException
        └── ExternalServiceException
```

#### Uso

```python
from infocodest.exceptions.business_exceptions import ApplicationNotFoundException

# En servicio
def get_application(name: str):
    app = self.app_repo.get_by_name(name)
    if not app:
        raise ApplicationNotFoundException(name)
    return app

# Error handler automático renderiza template
@app.errorhandler(ApplicationNotFoundException)
def handle_not_found(error):
    return render_template('errors/404.html', error=error.message), 404
```

---

### Configuration (Configuración)

**Ubicación**: `config/`

#### Estructura

```
config/
├── __init__.py
├── base.py          # BaseConfig (común)
├── development.py   # DevelopmentConfig
├── production.py    # ProductionConfig
└── testing.py       # TestingConfig
```

#### Selección de Configuración

```python
# run.py
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
config = DevelopmentConfig if DEBUG else ProductionConfig
app = create_app(config)
```

---

## 📦 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                     Flask Application                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                 Presentation Layer                      │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │    │
│  │  │   Home   │ │   API    │ │ Accounts │ │  Charts  │  │    │
│  │  │Blueprint │ │Blueprint │ │Blueprint │ │Blueprint │  │    │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │    │
│  └───────┼────────────┼────────────┼────────────┼─────────┘    │
│          │            │            │            │               │
│  ┌───────┴────────────┴────────────┴────────────┴─────────┐    │
│  │                  Service Layer                          │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐         │    │
│  │  │ Dashboard  │ │  Metrica   │ │   Auth     │         │    │
│  │  │  Service   │ │  Service   │ │  Service   │         │    │
│  │  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘         │    │
│  └────────┼──────────────┼──────────────┼─────────────────┘    │
│           │              │              │                       │
│  ┌────────┴──────────────┴──────────────┴──────────────────┐   │
│  │               Repository Layer                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Metrica  │ │Historico │ │  Daily   │ │  User    │  │   │
│  │  │   Repo   │ │   Repo   │ │   Repo   │ │   Repo   │  │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │   │
│  └───────┼────────────┼────────────┼────────────┼─────────┘   │
│          │            │            │            │              │
│  ┌───────┴────────────┴────────────┴────────────┴─────────┐   │
│  │                  Model Layer (ORM)                      │   │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐    │   │
│  │  │ Metrica │ │Historico │ │  Daily  │ │  User   │    │   │
│  │  │  Model  │ │  Model   │ │  Model  │ │  Model  │    │   │
│  │  └────┬────┘ └────┬─────┘ └────┬────┘ └────┬────┘    │   │
│  └───────┼───────────┼────────────┼───────────┼──────────┘   │
│          └───────────┴────────────┴───────────┘               │
│                              │                                 │
│  ┌──────────────────────────▼──────────────────────────┐     │
│  │                  Cross-Cutting Concerns              │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │     │
│  │  │  Utils   │ │Exception │ │  Config  │            │     │
│  │  │ (Logger, │ │ Handlers │ │ (Multi-  │            │     │
│  │  │Decorator,│ │          │ │environ.) │            │     │
│  │  │Validator)│ │          │ │          │            │     │
│  │  └──────────┘ └──────────┘ └──────────┘            │     │
│  └───────────────────────────────────────────────────── │     │
│                                                                │
│              ┌───────────────────────┐                        │
│              │   SQLAlchemy (ORM)    │                        │
│              └───────────┬───────────┘                        │
└──────────────────────────┼─────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │   / SQLite  │
                    └─────────────┘
```

---

## 🧪 Estrategia de Testing

### Pirámide de Testing

```
       ┌───────────────┐
       │  E2E Tests    │  (5%) - Tests de navegador completos
       │   (Futuro)    │
       └───────────────┘
      ┌─────────────────┐
      │ Integration Tests│ (15%) - Tests de múltiples capas
      │    (Futuro)     │
      └─────────────────┘
    ┌───────────────────────┐
    │    Unit Tests         │ (80%) - 202 tests actuales
    │ Repositories, Services│
    │  Utils, Exceptions    │
    └───────────────────────┘
```

### Unit Tests por Capa

#### Repository Tests

**Estrategia**: In-memory SQLite database

```python
import pytest
from infocodest.repositories.metrica_repository import MetricaRepository

@pytest.fixture
def metrica_repo(app):
    with app.app_context():
        return MetricaRepository()

def test_count_distinct_aplicaciones(metrica_repo, sample_metricas):
    count = metrica_repo.count_distinct_aplicaciones()
    assert count == 3  # Verificar con datos de prueba
```

**Cobertura objetivo**: >85%

#### Service Tests

**Estrategia**: Mock repositories

```python
from unittest.mock import Mock, patch
from infocodest.services.dashboard_service import DashboardService

@patch('infocodest.services.dashboard_service.MetricaRepository')
def test_get_kpi_overview(mock_repo_class):
    # Arrange
    mock_repo = Mock()
    mock_repo.count_distinct_aplicaciones.return_value = 10
    mock_repo_class.return_value = mock_repo

    service = DashboardService()

    # Act
    result = service.get_kpi_overview()

    # Assert
    assert result['aplicaciones'] == 10
    mock_repo.count_distinct_aplicaciones.assert_called_once()
```

**Cobertura objetivo**: >80%

#### Utils Tests

**Estrategia**: Pure function tests

```python
from infocodest.utils.validators import validate_percentage

def test_validate_percentage():
    assert validate_percentage(0) is True
    assert validate_percentage(50.5) is True
    assert validate_percentage(100) is True
    assert validate_percentage(-1) is False
    assert validate_percentage(101) is False
```

**Cobertura objetivo**: >95%

### Métricas de Testing Actuales

- **Total tests**: 202
- **Cobertura overall**: >80%
- **Tests por capa**:
  - Repository: 46 tests
  - Service: 17 tests
  - Utils: 74 tests
  - Exceptions: 65 tests

---

## ⚡ Consideraciones de Performance

### Query Optimization

#### 1. Eager Loading de Relaciones

```python
# ✅ CORRECTO: Eager loading (1 query)
metricas = session.query(Metrica).options(
    joinedload(Metrica.proveedor)
).all()

# ❌ INCORRECTO: N+1 queries
metricas = session.query(Metrica).all()
for m in metricas:
    print(m.proveedor.tipo)  # Query adicional por cada métrica
```

#### 2. Indexes en Campos Frecuentes

```python
class Metrica(db.Model):
    aplicacion = db.Column(db.String(255), nullable=False, index=True)
    fecha = db.Column(db.Date, nullable=False, index=True)
```

#### 3. Paginación

```python
# Repository
def get_paginated(self, page=1, per_page=20):
    return self.session.query(self.model_class)\
        .paginate(page=page, per_page=per_page)
```

### Caching (Futuro)

**Plan**: Redis para KPIs calculados

```python
# Futuro: @cached(timeout=300)
def get_kpi_overview(self):
    # Cálculo pesado cacheado por 5 minutos
    pass
```

---

## 🔒 Seguridad

### Autenticación

- **Flask-Login**: Gestión de sesiones
- **Bcrypt**: Hashing de passwords
- **Remember Me**: Tokens seguros

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@accounts_bp.route('/login', methods=['POST'])
def login():
    user = auth_service.authenticate(email, password)
    if user:
        login_user(user, remember=remember_me)
```

### Autorización

```python
@home_bp.route('/admin')
@login_required
@requires_role('admin')
def admin_dashboard():
    pass
```

### CSRF Protection

```python
# WTForms automático
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # CSRF token automático
```

### Input Validation

```python
from infocodest.utils.validators import validate_application_name

app_name = request.args.get('app')
if not validate_application_name(app_name):
    raise InvalidApplicationNameException(app_name)
```

### SQL Injection Prevention

```python
# ✅ CORRECTO: SQLAlchemy ORM (parametrized queries)
metricas = session.query(Metrica).filter_by(aplicacion=app_name).all()

# ❌ INCORRECTO: String concatenation
query = f"SELECT * FROM metricas WHERE aplicacion = '{app_name}'"
```

---

## 📈 Escalabilidad

### Horizontal Scaling

**Preparación actual**:
- ✅ Stateless application (sesiones en cookies)
- ✅ Multiple WSGI workers (Gunicorn)
- ✅ Nginx como load balancer

**Futuro**:
- Redis para sesiones compartidas
- Redis para caching distribuido
- CDN para static files

### Vertical Scaling

**Optimizaciones**:
- Connection pooling (SQLAlchemy)
- Query optimization con indexes
- Eager loading de relaciones

**Configuración**:
```python
# config/production.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### Async Tasks (Futuro)

**Plan**: Celery para tareas pesadas

```python
# Futuro
@celery.task
def calculate_statistics():
    # Cálculos pesados en background
    pass
```

---

## 📊 Monitoreo y Observabilidad

### Logging Actual

```python
# Structured logging
app.logger.info('User logged in', extra={'user_id': user.id})
app.logger.error('Database error', exc_info=True)
```

**Archivos de Log**:
- `logs/info.log`: Logs informativos
- `logs/error.log`: Solo errores
- Rotación: 10MB, 10 backups

### Métricas (Futuro)

**Plan**: Prometheus + Grafana

```python
# Futuro: Prometheus metrics
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)
```

**Métricas a trackear**:
- Request rate
- Response time (p50, p95, p99)
- Error rate
- Database query time
- Active sessions

### Health Checks

```python
@api_bp.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': check_database_connection(),
        'version': '2.0.0'
    })
```

---

## 📚 Referencias

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern - Cosmic Python](https://www.cosmicpython.com/book/chapter_02_repository.html)
- [Service Layer Pattern - Cosmic Python](https://www.cosmicpython.com/book/chapter_04_service_layer.html)
- [12 Factor App](https://12factor.net/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

**Última actualización**: 2025-12-14
**Versión del documento**: 1.0.0
