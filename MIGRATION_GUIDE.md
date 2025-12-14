# Guía de Migración de Código Legacy

**Versión**: 1.0.0
**Fecha**: 2025-12-14
**Para**: Desarrolladores migrando código antiguo a la nueva arquitectura

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Cambios Principales](#cambios-principales)
3. [Migración de Queries SQL](#migración-de-queries-sql)
4. [Migración de Lógica de Negocio](#migración-de-lógica-de-negocio)
5. [Migración de Vistas](#migración-de-vistas)
6. [Checklist de Migración](#checklist-de-migración)
7. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🎯 Introducción

Esta guía te ayudará a migrar código legacy (anterior a v2.0.0) a la nueva arquitectura en capas.

### ¿Por qué Migrar?

La nueva arquitectura ofrece:

- ✅ **Separación de responsabilidades**: Código más mantenible
- ✅ **Testabilidad**: >80% cobertura con tests aislados
- ✅ **Reutilización**: Lógica centralizada en servicios
- ✅ **Escalabilidad**: Fácil añadir nuevas features

### Antes vs Después

**Antes (Legacy)**:
```python
# home/views.py - Todo mezclado
@home_bp.route('/metricas')
def metricas():
    # ❌ Query SQL directa en vista
    metricas = Metrica.query.join(...).filter(...).all()

    # ❌ Lógica de negocio en vista
    for m in metricas:
        m.status_color = 'red' if m.bugs > 10 else 'green'

    return render_template('metricas.html', metricas=metricas)
```

**Después (Refactorizado)**:
```python
# home/views.py - Solo presentación
@home_bp.route('/metricas')
@login_required
@inject_service(MetricaService)
def metricas(metrica_service: MetricaService):
    # ✅ Delega a servicio
    metricas = metrica_service.get_metricas_dashboard()
    return render_template('metricas.html', metricas=metricas)

# services/metrica_service.py - Lógica de negocio
class MetricaService:
    def get_metricas_dashboard(self):
        # ✅ Usa repositorio para datos
        metricas = self.metrica_repo.get_metricas_with_proveedor()
        # ✅ Aplica lógica de negocio
        return [self._enrich_metrica(m) for m in metricas]

# repositories/metrica_repository.py - Acceso a datos
class MetricaRepository(BaseRepository[Metrica]):
    def get_metricas_with_proveedor(self):
        # ✅ Query encapsulada
        return self.session.query(Metrica)\
            .join(Proveedor)\
            .order_by(desc(Metrica.fecha))\
            .all()
```

---

## 🔄 Cambios Principales

### 1. Eliminación de `models/database.py`

**Antes**:
```python
# models/database.py (DEPRECATED)
def getDatosMetricas():
    engine = create_engine(...)
    query = "SELECT * FROM metricas..."
    return pd.read_sql(query, engine)
```

**Después**:
```python
# repositories/metrica_repository.py
class MetricaRepository(BaseRepository[Metrica]):
    def get_all_metricas(self) -> List[Metrica]:
        return self.session.query(Metrica).all()
```

### 2. Inyección de Dependencias

**Antes**:
```python
# Vista instancia directamente
def my_view():
    repo = MetricaRepository()  # ❌ Acoplamiento fuerte
    data = repo.get_all()
```

**Después**:
```python
# Vista recibe servicio inyectado
@inject_service(MetricaService)
def my_view(metrica_service: MetricaService):
    data = metrica_service.get_data()  # ✅ Desacoplado
```

### 3. Configuración por Entorno

**Antes**:
```python
# config.py en raíz
class Config:
    DEBUG = True
    DATABASE_URI = 'sqlite:///db.sqlite3'
```

**Después**:
```python
# config/development.py
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

# config/production.py
class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
```

### 4. Manejo de Errores

**Antes**:
```python
# Vista maneja errores manualmente
def my_view():
    try:
        data = get_data()
    except Exception:
        return "Error", 500  # ❌ Genérico
```

**Después**:
```python
# Servicio lanza excepción específica
def get_application(name: str):
    app = self.app_repo.get_by_name(name)
    if not app:
        raise ApplicationNotFoundException(name)  # ✅ Específico
    return app

# Error handler automático en errorhandlers.py
@app.errorhandler(ApplicationNotFoundException)
def handle_not_found(error):
    return render_template('errors/404.html', error=error), 404
```

---

## 🗄️ Migración de Queries SQL

### Paso 1: Identificar Queries en Vistas

Busca patrones como:

```python
# Buscar en vistas
Metrica.query.filter(...)
db.session.query(...)
engine.execute(...)
```

### Paso 2: Crear Repositorio

```python
# repositories/metrica_repository.py
from infocodest.repositories.base_repository import BaseRepository
from infocodest.models.metricas import Metrica

class MetricaRepository(BaseRepository[Metrica]):
    def __init__(self):
        super().__init__(Metrica)

    # Migrar query específica
    def get_by_aplicacion(self, app_name: str) -> List[Metrica]:
        return self.session.query(Metrica)\
            .filter(Metrica.aplicacion == app_name)\
            .order_by(Metrica.fecha.asc())\
            .all()
```

### Paso 3: Usar en Servicio

```python
# services/metrica_service.py
class MetricaService:
    def __init__(self):
        self.metrica_repo = MetricaRepository()

    def get_metricas_by_app(self, app_name: str) -> List[Dict]:
        metricas = self.metrica_repo.get_by_aplicacion(app_name)
        return [m.to_dict() for m in metricas]
```

### Ejemplo Completo

**Antes**:
```python
# home/views.py
@home_bp.route('/app/<name>')
def app_detail(name):
    # ❌ Query SQL directa
    metricas = Metrica.query\
        .filter(Metrica.aplicacion == name)\
        .join(Proveedor)\
        .order_by(Metrica.fecha.desc())\
        .all()

    # ❌ Cálculo de estadísticas en vista
    total_bugs = sum(m.bugs for m in metricas)
    avg_coverage = sum(m.coverage for m in metricas) / len(metricas)

    return render_template('app_detail.html',
                         metricas=metricas,
                         total_bugs=total_bugs,
                         avg_coverage=avg_coverage)
```

**Después**:
```python
# home/views.py - Solo presentación
@home_bp.route('/app/<name>')
@login_required
@inject_service(DashboardService)
def app_detail(name: str, dashboard_service: DashboardService):
    # ✅ Delega a servicio
    stats = dashboard_service.get_app_statistics(name)
    return render_template('app_detail.html', **stats)

# services/dashboard_service.py - Lógica de negocio
class DashboardService:
    def __init__(self):
        self.metrica_repo = MetricaRepository()

    def get_app_statistics(self, app_name: str) -> Dict[str, Any]:
        # ✅ Usa repositorio
        metricas = self.metrica_repo.get_by_aplicacion_with_proveedor(app_name)

        if not metricas:
            raise ApplicationNotFoundException(app_name)

        # ✅ Lógica de negocio centralizada
        return {
            'metricas': [m.to_dict() for m in metricas],
            'total_bugs': sum(m.bugs for m in metricas),
            'avg_coverage': self._calculate_avg_coverage(metricas),
            'trend': self._calculate_trend(metricas)
        }

# repositories/metrica_repository.py - Acceso a datos
class MetricaRepository(BaseRepository[Metrica]):
    def get_by_aplicacion_with_proveedor(self, app_name: str) -> List[Metrica]:
        # ✅ Query encapsulada con eager loading
        return self.session.query(Metrica)\
            .filter(Metrica.aplicacion == app_name)\
            .join(Proveedor)\
            .options(joinedload(Metrica.proveedor))\
            .order_by(desc(Metrica.fecha))\
            .all()
```

---

## 💼 Migración de Lógica de Negocio

### Identificar Lógica de Negocio

Busca código que:

- Calcula valores (KPIs, estadísticas, porcentajes)
- Transforma datos (formateo, agregación)
- Aplica reglas de negocio (validaciones complejas)
- Orquesta múltiples operaciones

### Ejemplo: Cálculo de KPIs

**Antes**:
```python
# home/views.py
@home_bp.route('/dashboard')
def dashboard():
    # ❌ Lógica de negocio en vista
    total_apps = Metrica.query.distinct(Metrica.aplicacion).count()
    total_repos = Metrica.query.count()
    total_bugs = db.session.query(func.sum(Metrica.bugs)).scalar()

    # ❌ Cálculo de variación en vista
    old_data = get_old_data(days=15)
    variation = ((total_bugs / old_data['bugs']) * 100) - 100

    return render_template('dashboard.html',
                         apps=total_apps,
                         repos=total_repos,
                         bugs=total_bugs,
                         variation=variation)
```

**Después**:
```python
# home/views.py - Solo presentación
@home_bp.route('/dashboard')
@login_required
@inject_service(DashboardService)
def dashboard(dashboard_service: DashboardService):
    # ✅ Delega a servicio
    kpis = dashboard_service.get_kpi_overview(days=15)
    return render_template('dashboard.html', **kpis)

# services/dashboard_service.py - Lógica centralizada
class DashboardService:
    def __init__(self):
        self.metrica_repo = MetricaRepository()
        self.daily_repo = DailyRepository()

    def get_kpi_overview(self, days: int = 15) -> Dict[str, Any]:
        """
        Calcula KPIs del dashboard con variaciones

        Args:
            days: Días para comparación

        Returns:
            Dict con KPIs y textos de variación
        """
        # ✅ Orquesta múltiples repositorios
        current = {
            'aplicaciones': self.metrica_repo.count_distinct_aplicaciones(),
            'repositorios': self.metrica_repo.count(),
            'bugs': self.metrica_repo.sum_bugs()
        }

        # ✅ Obtiene datos históricos
        fecha_comp = (datetime.now() - timedelta(days=days)).date()
        old = self.daily_repo.get_metrics_by_date(fecha_comp)

        # ✅ Aplica lógica de negocio
        return self._calculate_variations(current, old, days)

    def _calculate_variations(self, current, old, days):
        """Lógica de cálculo de variaciones (privado)"""
        result = {}
        for key in current.keys():
            curr_val = current[key]
            old_val = old.get(key, 0)

            if old_val == 0 and curr_val == 0:
                var = 0.0
                trend = "Igual"
            elif old_val == 0:
                var = 100.0
                trend = "Increase"
            else:
                var = ((curr_val / old_val) * 100) - 100
                trend = "Decrease" if var < 0 else "Increase"

            result[key] = curr_val
            result[f'{key}_value'] = round(var, 2)
            result[f'{key}_text'] = f'{var:.2f}% {trend} in {days} Days'

        return result
```

---

## 🎨 Migración de Vistas

### Principio: Vistas Delgadas

Objetivo: **<30 líneas** por vista

**Responsabilidades de una Vista**:
- ✅ Validar parámetros de entrada
- ✅ Llamar a servicio
- ✅ Renderizar template o JSON
- ❌ NO queries SQL
- ❌ NO lógica de negocio

### Patrón de Migración

```python
# ANTES: Vista gruesa
@bp.route('/endpoint')
def old_view():
    # Queries SQL
    data = Model.query.filter(...).all()

    # Procesamiento
    processed = process_data(data)

    # Más queries
    related = Related.query.filter(...).all()

    # Cálculos
    stats = calculate_stats(data, related)

    return render_template('template.html',
                         data=processed,
                         stats=stats)

# DESPUÉS: Vista delgada
@bp.route('/endpoint')
@login_required
@inject_service(MyService)
def new_view(my_service: MyService):
    # Solo llama a servicio y renderiza
    result = my_service.get_data_with_stats()
    return render_template('template.html', **result)
```

### Ejemplo: Vista de API

**Antes**:
```python
# api/views.py
@api_bp.route('/api/metricas/<app>')
def get_metricas(app):
    # ❌ Query y transformación en vista
    metricas = Metrica.query.filter_by(aplicacion=app).all()

    data = {
        'repos': [m.repo for m in metricas],
        'bugs': [m.bugs for m in metricas],
        'coverage': [m.coverage for m in metricas]
    }

    return jsonify(data)
```

**Después**:
```python
# api/views.py
@api_bp.route('/api/metricas/<app>')
@inject_service(MetricaService)
def get_metricas(app: str, metrica_service: MetricaService):
    # ✅ Validación simple
    if not app:
        raise InvalidApplicationNameException(app)

    # ✅ Delega a servicio
    data = metrica_service.get_metricas_serialized(app)
    return jsonify(data)

# services/metrica_service.py
class MetricaService:
    def get_metricas_serialized(self, app_name: str) -> Dict[str, List]:
        """Retorna métricas en formato para API"""
        metricas = self.metrica_repo.get_by_aplicacion(app_name)

        if not metricas:
            raise ApplicationNotFoundException(app_name)

        return {
            'repos': [m.repo for m in metricas],
            'bugs': [m.bugs for m in metricas],
            'coverage': [m.coverage for m in metricas],
            'dates': [m.fecha.isoformat() for m in metricas]
        }
```

---

## ✅ Checklist de Migración

### Paso 1: Análisis

- [ ] Identificar archivo a migrar (vista, helper, etc.)
- [ ] Listar queries SQL en el archivo
- [ ] Listar lógica de negocio
- [ ] Identificar dependencias

### Paso 2: Crear Repositorio (si no existe)

- [ ] Crear `MyRepository` extendiendo `BaseRepository`
- [ ] Migrar queries SQL a métodos del repositorio
- [ ] Añadir docstrings (Google style)
- [ ] Escribir tests unitarios del repositorio

### Paso 3: Crear Servicio (si no existe)

- [ ] Crear `MyService` con inyección de repositorios
- [ ] Migrar lógica de negocio a métodos del servicio
- [ ] Añadir docstrings
- [ ] Escribir tests unitarios con mocks

### Paso 4: Refactorizar Vista

- [ ] Aplicar decorador `@inject_service(MyService)`
- [ ] Reemplazar queries SQL con llamadas a servicio
- [ ] Eliminar lógica de negocio
- [ ] Reducir a <30 líneas
- [ ] Verificar funcionalidad

### Paso 5: Limpieza

- [ ] Eliminar código comentado
- [ ] Eliminar imports no usados
- [ ] Actualizar tests de integración
- [ ] Verificar que no hay regresiones

### Paso 6: Documentación

- [ ] Actualizar docstrings
- [ ] Añadir entry a CHANGELOG si es feature significativa
- [ ] Commit con Conventional Commits

---

## ❓ Preguntas Frecuentes

### 1. ¿Debo migrar todo el código de una vez?

**No**. Migra incrementalmente por features:

```
Sprint 1: Migrar endpoint /metricas
Sprint 2: Migrar endpoint /dashboard
Sprint 3: Migrar endpoints de API
```

### 2. ¿Qué hago con código que usa `models/database.py`?

**Eliminar y migrar a repositorios**:

```python
# Antes
from infocodest.models.database import getDatosMetricas
data = getDatosMetricas()  # ❌ DEPRECATED

# Después
metrica_repo = MetricaRepository()
data = metrica_repo.get_all()  # ✅
```

### 3. ¿Cómo testeo código migrado?

**Usa mocks para servicios**:

```python
from unittest.mock import Mock
from infocodest.services.metrica_service import MetricaService

def test_my_view():
    # Arrange
    mock_service = Mock(spec=MetricaService)
    mock_service.get_data.return_value = {'key': 'value'}

    # Act
    with app.test_client() as client:
        response = client.get('/endpoint')

    # Assert
    assert response.status_code == 200
```

### 4. ¿Qué hacer con helpers dispersos?

**Migrar a `utils/helpers.py`**:

```python
# Antes: helpers en múltiples archivos
def format_number(n):
    ...

# Después: centralizado en utils
from infocodest.utils.helpers import format_number
```

### 5. ¿Cómo manejar errores ahora?

**Lanzar excepciones específicas**:

```python
# Antes
if not user:
    abort(404)  # ❌ Genérico

# Después
if not user:
    raise UserNotFoundException(user_id)  # ✅ Específico
```

### 6. ¿Puedo seguir usando `db.session` directamente?

**Sí, pero solo en repositorios**:

```python
# ✅ Correcto: en repositorio
class MyRepository(BaseRepository[MyModel]):
    def custom_query(self):
        return self.session.query(...).all()

# ❌ Incorrecto: en vista o servicio
def my_view():
    data = db.session.query(Model).all()  # NO!
```

### 7. ¿Cómo migro código con transacciones?

**Usa servicios para coordinar**:

```python
# Servicio maneja transacción
class MyService:
    def complex_operation(self):
        try:
            # Múltiples operaciones
            self.repo1.create(...)
            self.repo2.update(...)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise BusinessException(str(e))
```

---

## 📚 Recursos Adicionales

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura completa
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Crear nuevos componentes
- **[docs/reports/](docs/reports/)** - Reportes de cada fase de migración

---

## 🎯 Resumen

| Capa | Antes | Después |
|------|-------|---------|
| **Vista** | Queries SQL + Lógica | Solo presentación (<30 LOC) |
| **Servicio** | No existía | Lógica de negocio centralizada |
| **Repositorio** | No existía | Queries SQL encapsuladas |
| **Modelo** | ORM + SQL raw | Solo definiciones ORM |

**Regla de oro**: Si dudas dónde poner código, pregúntate:

- ¿Es acceso a datos? → **Repository**
- ¿Es lógica de negocio? → **Service**
- ¿Es presentación HTTP? → **View**

---

**Última actualización**: 2025-12-14
**Versión**: 1.0.0
