# Plan de Carga de Datos - Dashboard Sonar

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis de Tablas](#análisis-de-tablas)
3. [Estrategias de Carga](#estrategias-de-carga)
4. [Plan de Implementación](#plan-de-implementación)
5. [Arquitectura de Solución](#arquitectura-de-solución)
6. [Cronograma de Ejecución](#cronograma-de-ejecución)
7. [Scripts y Automatización](#scripts-y-automatización)

---

## Resumen Ejecutivo

### Objetivo

Diseñar e implementar un sistema de carga de datos robusto, eficiente y automatizado para todas las tablas de la base de datos del Dashboard Sonar, con diferentes estrategias según el tipo de datos y frecuencia de actualización.

### Alcance

**Tablas en Scope**:
- ✅ `metricas` - Carga completa periódica
- ✅ `historico` - Carga incremental (append)
- ✅ `daily` - Carga diaria (1 registro/día)
- ✅ `registro` - Carga diaria (1 registro/día)
- ✅ `proveedor` - Carga completa
- ✅ `stats` - Actualización derivada de metricas

### Principios de Diseño

1. **Idempotencia**: Los procesos deben ser seguros para re-ejecutar
2. **Trazabilidad**: Logging completo de todas las operaciones
3. **Resiliencia**: Manejo de errores y rollback automático
4. **Performance**: Optimización mediante batch processing
5. **Flexibilidad**: Parametrización de periodos y configuraciones

---

## Análisis de Tablas

### 1. Tabla `metricas` 📊

**Propósito**: Métricas actuales de SonarQube por proyecto/aplicación

**Características**:
- **Estrategia**: Carga completa (truncate & load)
- **Frecuencia**: Configurable (diaria, semanal, bajo demanda)
- **Fuente**: API de SonarQube o CSV exportado
- **Volumen estimado**: Alto (~1000-10000 registros)
- **ETL**: Requiere transformación (labels, categorías)

**Campos clave**:
- `aplicacion`, `proyecto`, `repo`
- Métricas: `ncloc`, `coverage`, `bugs`, `vulnerabilities`
- Labels calculados: `reliability_label`, `security_label`, etc.

**Dependencias**:
- ⬇️ **Después** se actualiza: `stats`

### 2. Tabla `historico` 📈

**Propósito**: Histórico de análisis de SonarQube (time-series)

**Características**:
- **Estrategia**: Carga incremental (append only)
- **Frecuencia**: Diaria o cada análisis
- **Fuente**: API de SonarQube (histórico de análisis)
- **Volumen estimado**: Muy alto (crece constantemente)
- **ETL**: Requiere transformación similar a metricas

**Campos clave**:
- `aplicacion`, `proyecto`, `analysis_date`
- Métricas históricas
- Labels calculados

**Consideraciones**:
- ⚠️ **NO eliminar datos antiguos** (histórico completo)
- ✅ Verificar duplicados por `(aplicacion, proyecto, analysis_date)`
- 🔍 Indexar por fecha para queries eficientes

### 3. Tabla `daily` 📅

**Propósito**: Agregación diaria de métricas por aplicación

**Características**:
- **Estrategia**: Carga diaria (1 registro por aplicación por día)
- **Frecuencia**: Una vez al día (cron diario)
- **Fuente**: Derivada de `metricas` o API directa
- **Volumen estimado**: Medio (~N aplicaciones × días)
- **ETL**: Agregación de métricas

**Campos clave**:
- `aplicacion`, `created_on` (fecha del snapshot)
- `repo`, `num_bugs`, `num_vulnerabilities`, `num_code_smells`
- `num_quality`, `num_analisis`

**Consideraciones**:
- ✅ Verificar que no exista registro para `(aplicacion, DATE(created_on))`
- ✅ Usar timestamp completo para tracking
- 🔄 Permite re-proceso del día actual (update en lugar de insert)

### 4. Tabla `registro` 📝

**Propósito**: Registro diario de eventos/actividades del sistema

**Características**:
- **Estrategia**: Carga diaria (1 registro por día)
- **Frecuencia**: Una vez al día
- **Fuente**: Derivada de análisis agregados o eventos del sistema
- **Volumen estimado**: Bajo (1 registro/día = ~365 registros/año)

**Campos clave**:
- `fecha`, `descripcion`, `tipo_evento`
- Métricas agregadas del día

**Consideraciones**:
- ✅ Un solo registro por día (sistema completo)
- ✅ Verificar fecha antes de insertar

### 5. Tabla `proveedor` 🏢

**Propósito**: Catálogo de proveedores/vendors

**Características**:
- **Estrategia**: Carga completa (replace all)
- **Frecuencia**: Esporádica (cuando cambia catálogo)
- **Fuente**: CSV maestro o configuración
- **Volumen estimado**: Muy bajo (~10-100 registros)

**Campos clave**:
- `nombre`, `codigo`, `activo`

**Consideraciones**:
- 🔒 Tabla maestra (poca frecuencia de cambio)
- ✅ Validar integridad referencial antes de borrar

### 6. Tabla `stats` 📊

**Propósito**: Estadísticas agregadas por aplicación

**Características**:
- **Estrategia**: Actualización completa derivada
- **Frecuencia**: Cada vez que se actualiza `metricas`
- **Fuente**: Derivada de `metricas` (agregaciones)
- **Volumen estimado**: Bajo (~N aplicaciones)
- **ETL**: Requiere transformación (labels agregados)

**Campos clave**:
- `aplicacion`, `repos`
- Ratings: `reliability_rating`, `sqale_rating`, etc.
- Labels: `reliability_label`, `security_label`, etc.

**Dependencias**:
- ⬆️ **Depende de**: `metricas` (debe cargarse después)

---

## Estrategias de Carga

### Estrategia 1: Carga Completa (Truncate & Load)

**Aplicable a**: `metricas`, `proveedor`, `stats`

**Proceso**:
```python
1. BEGIN TRANSACTION
2. BACKUP tabla actual (opcional)
3. TRUNCATE tabla
4. BULK INSERT nuevos datos
5. VALIDATE datos insertados
6. COMMIT TRANSACTION
```

**Ventajas**:
- ✅ Simple y directo
- ✅ Garantiza datos frescos
- ✅ No hay problemas de duplicados

**Desventajas**:
- ❌ Pérdida temporal de datos durante proceso
- ❌ No mantiene histórico

**Implementación**:
```python
def load_complete_replace(table_model, data, session):
    """Load data using truncate & load strategy."""
    try:
        session.begin()
        # Truncate
        session.query(table_model).delete()
        # Bulk insert
        session.bulk_insert_mappings(table_model, data)
        session.commit()
        return len(data)
    except Exception as e:
        session.rollback()
        raise
```

### Estrategia 2: Carga Incremental (Append Only)

**Aplicable a**: `historico`

**Proceso**:
```python
1. BEGIN TRANSACTION
2. IDENTIFICAR nuevos registros (no existentes)
3. BULK INSERT solo nuevos registros
4. COMMIT TRANSACTION
```

**Ventajas**:
- ✅ Mantiene histórico completo
- ✅ Solo agrega nuevos datos

**Desventajas**:
- ❌ Requiere identificación de duplicados
- ❌ Tabla crece indefinidamente

**Implementación**:
```python
def load_incremental_append(table_model, data, unique_keys, session):
    """Load data using append-only strategy with duplicate check."""
    existing = get_existing_records(table_model, data, unique_keys, session)
    new_records = [r for r in data if r not in existing]

    if new_records:
        session.bulk_insert_mappings(table_model, new_records)
        session.commit()
        return len(new_records)
    return 0
```

### Estrategia 3: Carga Diaria (Upsert)

**Aplicable a**: `daily`, `registro`

**Proceso**:
```python
1. BEGIN TRANSACTION
2. CHECK si existe registro para HOY
3. IF existe:
     UPDATE registro existente
   ELSE:
     INSERT nuevo registro
4. COMMIT TRANSACTION
```

**Ventajas**:
- ✅ Idempotente (se puede re-ejecutar)
- ✅ Mantiene histórico
- ✅ Permite correcciones

**Desventajas**:
- ❌ Más complejo que insert simple

**Implementación**:
```python
def load_daily_upsert(table_model, data, date_field, session):
    """Load daily data using upsert strategy."""
    from datetime import date
    today = date.today()

    for record in data:
        existing = session.query(table_model).filter(
            getattr(table_model, date_field) == today,
            table_model.aplicacion == record['aplicacion']
        ).first()

        if existing:
            # Update
            for key, value in record.items():
                setattr(existing, key, value)
        else:
            # Insert
            session.add(table_model(**record))

    session.commit()
```

### Estrategia 4: Carga Derivada (Regeneración)

**Aplicable a**: `stats`

**Proceso**:
```python
1. BEGIN TRANSACTION
2. TRUNCATE tabla stats
3. GENERATE stats desde metricas (queries agregadas)
4. TRANSFORM stats (ETL)
5. INSERT stats generadas
6. COMMIT TRANSACTION
```

**Ventajas**:
- ✅ Siempre sincronizado con fuente
- ✅ No requiere fuente externa

**Desventajas**:
- ❌ Depende de otra tabla
- ❌ Requiere tiempo de procesamiento

---

## Plan de Implementación

### Fase 1: Infraestructura Base (Semana 1)

#### 1.1 Crear Framework de Carga de Datos

**Archivo**: `scripts/data/data_loader_framework.py`

**Componentes**:
```python
class DataLoader:
    """Base class for data loading operations."""

    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.logger = setup_logger()

    def load(self):
        """Main load method - to be overridden."""
        raise NotImplementedError

    def validate(self, data):
        """Validate data before loading."""
        pass

    def log_metrics(self, operation, records_affected):
        """Log operation metrics."""
        pass
```

**Estrategias implementadas**:
- `TruncateLoadStrategy`
- `AppendOnlyStrategy`
- `DailyUpsertStrategy`
- `DerivedDataStrategy`

#### 1.2 Sistema de Logging y Auditoría

**Archivo**: `scripts/data/audit_logger.py`

**Características**:
- Log de todas las operaciones de carga
- Métricas: tiempo de ejecución, registros procesados
- Alertas en caso de errores
- Historial de ejecuciones

### Fase 2: Implementación por Tabla (Semana 2-3)

#### 2.1 Loader: Proveedores (Prioridad: Alta)

**Archivo**: `scripts/data/load_proveedores.py`

**Razón**: Tabla maestra, pocas dependencias

**Funcionalidades**:
```bash
# Carga completa desde CSV
python scripts/data/load_proveedores.py --file datos/proveedores.csv

# Con validación
python scripts/data/load_proveedores.py --file datos/proveedores.csv --validate

# Backup antes de cargar
python scripts/data/load_proveedores.py --file datos/proveedores.csv --backup
```

#### 2.2 Loader: Metricas (Prioridad: Alta)

**Archivo**: `scripts/data/load_metricas.py`

**Funcionalidades**:
```bash
# Carga completa desde SonarQube API
python scripts/data/load_metricas.py --source api --period last-week

# Carga desde CSV
python scripts/data/load_metricas.py --source csv --file datos/metricas.csv

# Carga con transformación ETL
python scripts/data/load_metricas.py --source api --transform --period last-month

# Carga y actualiza stats automáticamente
python scripts/data/load_metricas.py --source api --update-stats
```

**Proceso detallado**:
1. Extraer datos de SonarQube API o CSV
2. Transformar con ETL (`scripts/etl/etl.py::transformar_metricas`)
3. Validar datos
4. Truncate tabla `metricas`
5. Bulk insert nuevos datos
6. Trigger actualización de `stats` (si `--update-stats`)

#### 2.3 Loader: Stats (Prioridad: Alta)

**Archivo**: `scripts/data/generate_stats.py` (ya existe, mejorar)

**Mejoras necesarias**:
```python
# Agregar modo de actualización automática
--auto-trigger  # Se ejecuta automáticamente después de load_metricas

# Agregar modo incremental
--incremental   # Solo actualiza aplicaciones modificadas

# Agregar validación
--validate      # Valida consistencia con metricas
```

#### 2.4 Loader: Historico (Prioridad: Media)

**Archivo**: `scripts/data/load_historico.py`

**Funcionalidades**:
```bash
# Carga incremental desde API
python scripts/data/load_historico.py --source api --since 2024-01-01

# Carga desde CSV (append)
python scripts/data/load_historico.py --source csv --file datos/historico.csv

# Carga con verificación de duplicados
python scripts/data/load_historico.py --source api --check-duplicates --since 2024-01-01
```

**Proceso**:
1. Extraer análisis históricos de SonarQube
2. Identificar análisis ya cargados
3. Filtrar solo nuevos análisis
4. Transformar con ETL
5. Append a tabla `historico`

#### 2.5 Loader: Daily (Prioridad: Media)

**Archivo**: `scripts/data/generate_daily.py`

**Funcionalidades**:
```bash
# Generar snapshot diario (modo automático)
python scripts/data/generate_daily.py

# Generar snapshot para fecha específica
python scripts/data/generate_daily.py --date 2024-01-15

# Re-generar snapshot del día actual (overwrite)
python scripts/data/generate_daily.py --overwrite-today

# Generar desde metricas
python scripts/data/generate_daily.py --source metricas
```

**Proceso**:
1. Obtener datos de aplicaciones (desde `metricas` o API)
2. Agregar métricas por aplicación
3. Verificar si existe snapshot para HOY
4. Upsert registro diario

#### 2.6 Loader: Registro (Prioridad: Baja)

**Archivo**: `scripts/data/generate_registro.py` (ya existe, revisar)

**Funcionalidades**:
```bash
# Generar registro diario del sistema
python scripts/data/generate_registro.py

# Generar registro con descripción custom
python scripts/data/generate_registro.py --description "Carga completa mensual"
```

### Fase 3: Orquestación y Automatización (Semana 4)

#### 3.1 Script Maestro de Carga

**Archivo**: `scripts/data/master_data_loader.py`

**Funcionalidad**: Orquestador de todos los loaders

```bash
# Carga completa (todo)
python scripts/data/master_data_loader.py --mode full

# Carga diaria (daily + registro)
python scripts/data/master_data_loader.py --mode daily

# Carga semanal (metricas + stats + historico)
python scripts/data/master_data_loader.py --mode weekly
```

**Flujo de ejecución**:

**Modo FULL** (carga inicial o mensual):
```
1. Proveedores (CSV)
2. Metricas (API, last 30 days)
3. Stats (derivado de metricas)
4. Historico (API, incremental)
5. Daily (generado desde metricas)
6. Registro (evento de carga completa)
```

**Modo DAILY** (ejecución diaria):
```
1. Daily (snapshot del día)
2. Registro (evento diario)
```

**Modo WEEKLY** (ejecución semanal):
```
1. Metricas (API, last 7 days)
2. Stats (actualización completa)
3. Historico (API, last 7 days - incremental)
4. Registro (evento semanal)
```

#### 3.2 Configuración de Cron Jobs

**Archivo**: `scripts/cron/setup_cron_jobs.sh`

```bash
#!/bin/bash
# Setup cron jobs for data loading

# Daily job (2 AM)
0 2 * * * /path/to/venv/bin/python /path/to/scripts/data/master_data_loader.py --mode daily >> /var/log/dashboard-sonar/daily.log 2>&1

# Weekly job (Sunday 3 AM)
0 3 * * 0 /path/to/venv/bin/python /path/to/scripts/data/master_data_loader.py --mode weekly >> /var/log/dashboard-sonar/weekly.log 2>&1

# Monthly job (1st day of month, 4 AM)
0 4 1 * * /path/to/venv/bin/python /path/to/scripts/data/master_data_loader.py --mode full >> /var/log/dashboard-sonar/monthly.log 2>&1
```

#### 3.3 Monitoreo y Alertas

**Archivo**: `scripts/monitoring/data_load_monitor.py`

**Funcionalidades**:
- Health checks post-carga
- Alertas por email/Slack en caso de errores
- Dashboard de métricas de carga
- Detección de anomalías (ej: carga muy pequeña o muy grande)

---

## Arquitectura de Solución

### Diagrama de Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                    FUENTES DE DATOS                          │
├─────────────┬──────────────┬──────────────┬─────────────────┤
│ SonarQube   │  CSV Files   │  Derivadas   │  Eventos        │
│     API     │              │  (Metricas)  │  Sistema        │
└──────┬──────┴──────┬───────┴──────┬───────┴────┬────────────┘
       │             │               │            │
       ▼             ▼               ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE EXTRACCIÓN                         │
├─────────────┬──────────────┬──────────────┬─────────────────┤
│ API Client  │ CSV Reader   │ Aggregator   │ Event Logger    │
└──────┬──────┴──────┬───────┴──────┬───────┴────┬────────────┘
       │             │               │            │
       ▼             ▼               ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE TRANSFORMACIÓN (ETL)                 │
├─────────────┬──────────────┬──────────────┬─────────────────┤
│transformar_ │transformar_  │transformar_  │  Validation     │
│  metricas   │  historico   │   stats      │    Layer        │
└──────┬──────┴──────┬───────┴──────┬───────┴────┬────────────┘
       │             │               │            │
       ▼             ▼               ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                   ESTRATEGIAS DE CARGA                       │
├──────────┬──────────┬──────────┬──────────┬──────────────────┤
│Truncate  │ Append   │  Upsert  │ Derived  │  Transaction     │
│  Load    │   Only   │  Daily   │   Data   │   Management     │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS                             │
├──────────┬──────────┬──────────┬──────────┬──────────────────┤
│ metricas │historico │  daily   │ registro │  proveedor │stats│
└──────────┴──────────┴──────────┴──────────┴──────────────────┘
     │          │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│               AUDITORÍA Y MONITOREO                          │
├─────────────┬──────────────┬──────────────┬─────────────────┤
│  Logs de    │  Métricas de │   Alertas    │   Dashboard     │
│  Operación  │    Carga     │              │   Monitoreo     │
└─────────────┴──────────────┴──────────────┴─────────────────┘
```

### Dependencias entre Tablas

```
Orden de carga recomendado:

1. proveedor  (independiente)
   │
   ├──> 2. metricas (puede referenciar proveedor)
   │         │
   │         ├──> 3. stats (derivada de metricas)
   │         │
   │         └──> 4. daily (derivada de metricas o API)
   │
   └──> 5. historico (independiente, incremental)

6. registro (siempre al final, registra ejecución)
```

---

## Cronograma de Ejecución

### Ejecución Diaria (2 AM)

```yaml
Daily Job:
  Hora: 02:00 AM
  Duración estimada: 5-10 minutos

  Tareas:
    1. Generate Daily Snapshot:
       - Source: metricas actual o API
       - Target: daily (1 registro por aplicación)
       - Strategy: Upsert
       - Estimated time: 3-5 min

    2. Generate Registro:
       - Source: Evento de sistema
       - Target: registro (1 registro)
       - Strategy: Daily insert
       - Estimated time: <1 min

    3. Health Check:
       - Verify daily records created
       - Send alert if failed
       - Estimated time: 1 min
```

### Ejecución Semanal (Domingo 3 AM)

```yaml
Weekly Job:
  Hora: 03:00 AM (Domingo)
  Duración estimada: 15-30 minutos

  Tareas:
    1. Load Metricas:
       - Source: SonarQube API (last 7 days)
       - Target: metricas (truncate & load)
       - Strategy: Complete replace
       - Estimated time: 5-10 min
       - Triggers: stats update

    2. Update Stats:
       - Source: metricas (aggregation)
       - Target: stats (truncate & load)
       - Strategy: Derived data
       - Estimated time: 2-5 min

    3. Load Historico:
       - Source: SonarQube API (last 7 days)
       - Target: historico (append only)
       - Strategy: Incremental
       - Estimated time: 5-10 min

    4. Generate Registro:
       - Event: Weekly data load
       - Estimated time: <1 min

    5. Health Check:
       - Verify all tables updated
       - Generate summary report
       - Send weekly metrics email
       - Estimated time: 2-3 min
```

### Ejecución Mensual (1er día del mes, 4 AM)

```yaml
Monthly Job:
  Hora: 04:00 AM (Día 1 del mes)
  Duración estimada: 30-60 minutos

  Tareas:
    1. Load Proveedores:
       - Source: CSV maestro
       - Target: proveedor (truncate & load)
       - Strategy: Complete replace
       - Estimated time: 1-2 min

    2. Load Metricas:
       - Source: SonarQube API (last 30 days)
       - Target: metricas (truncate & load)
       - Strategy: Complete replace
       - Estimated time: 10-15 min

    3. Update Stats:
       - Source: metricas (aggregation)
       - Target: stats (truncate & load)
       - Strategy: Derived data
       - Estimated time: 3-5 min

    4. Load Historico:
       - Source: SonarQube API (last 30 days)
       - Target: historico (append only)
       - Strategy: Incremental
       - Estimated time: 15-25 min

    5. Generate Daily:
       - Source: metricas
       - Target: daily (current day)
       - Strategy: Upsert
       - Estimated time: 3-5 min

    6. Generate Registro:
       - Event: Monthly full load
       - Estimated time: <1 min

    7. Maintenance:
       - Vacuum database (SQLite)
       - Analyze tables
       - Archive old logs
       - Estimated time: 5-10 min

    8. Monthly Report:
       - Generate data quality report
       - Generate statistics summary
       - Send to stakeholders
       - Estimated time: 3-5 min
```

---

## Scripts y Automatización

### Estructura de Archivos Propuesta

```
scripts/
├── data/
│   ├── __init__.py
│   ├── framework/
│   │   ├── __init__.py
│   │   ├── base_loader.py         # Clase base DataLoader
│   │   ├── strategies.py          # Estrategias de carga
│   │   ├── validators.py          # Validadores de datos
│   │   └── audit_logger.py        # Sistema de auditoría
│   │
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── load_proveedores.py    # Loader de proveedores
│   │   ├── load_metricas.py       # Loader de metricas
│   │   ├── load_historico.py      # Loader de historico
│   │   ├── generate_daily.py      # Generador de daily
│   │   ├── generate_stats.py      # Generador de stats (exists)
│   │   └── generate_registro.py   # Generador de registro (exists)
│   │
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── master_data_loader.py  # Orquestador maestro
│   │   ├── dependency_manager.py  # Gestor de dependencias
│   │   └── scheduler.py           # Programador de tareas
│   │
│   └── config/
│       ├── __init__.py
│       ├── load_config.yaml       # Configuración de cargas
│       └── sources.yaml           # Configuración de fuentes
│
├── monitoring/
│   ├── __init__.py
│   ├── data_load_monitor.py       # Monitor de cargas
│   ├── health_checker.py          # Health checks
│   └── alerting.py                # Sistema de alertas
│
└── cron/
    ├── setup_cron_jobs.sh         # Setup de cron jobs
    ├── daily_job.sh               # Wrapper para job diario
    ├── weekly_job.sh              # Wrapper para job semanal
    └── monthly_job.sh             # Wrapper para job mensual
```

### Configuración YAML de Ejemplo

**Archivo**: `scripts/data/config/load_config.yaml`

```yaml
# Data Loading Configuration

data_sources:
  sonarqube:
    url: "${SONARQUBE_URL}"
    token: "${SONARQUBE_TOKEN}"
    timeout: 30
    retry_attempts: 3

  csv:
    base_path: "${DATA_DIR}"
    encoding: "utf-8"
    delimiter: ";"

tables:
  metricas:
    strategy: "truncate_load"
    source: "sonarqube"
    period_days: 30
    batch_size: 1000
    etl_transform: true
    post_load_triggers:
      - update_stats

  historico:
    strategy: "append_only"
    source: "sonarqube"
    unique_keys: ["aplicacion", "proyecto", "analysis_date"]
    batch_size: 500
    etl_transform: true

  daily:
    strategy: "daily_upsert"
    source: "derived"  # from metricas or api
    unique_keys: ["aplicacion", "created_on"]
    date_field: "created_on"

  registro:
    strategy: "daily_insert"
    source: "generated"
    unique_keys: ["fecha"]

  proveedor:
    strategy: "truncate_load"
    source: "csv"
    csv_file: "proveedores.csv"
    validate_before_load: true

  stats:
    strategy: "derived"
    source: "metricas"
    etl_transform: true

schedules:
  daily:
    time: "02:00"
    enabled: true
    tables: ["daily", "registro"]

  weekly:
    time: "03:00"
    day_of_week: "sunday"
    enabled: true
    tables: ["metricas", "stats", "historico"]

  monthly:
    time: "04:00"
    day_of_month: 1
    enabled: true
    tables: ["proveedor", "metricas", "stats", "historico", "daily"]

monitoring:
  send_alerts: true
  alert_channels:
    - email
    - slack
  email_recipients:
    - "devops@example.com"
  slack_webhook: "${SLACK_WEBHOOK_URL}"

  health_checks:
    enabled: true
    checks:
      - name: "row_count"
        min_expected: 100
      - name: "data_freshness"
        max_age_hours: 26
      - name: "duplicate_check"
        enabled: true
```

---

## Resumen de Decisiones

### Tabla de Estrategias por Tabla

| Tabla | Estrategia | Frecuencia | Fuente | ETL | Dependencias |
|-------|-----------|-----------|---------|-----|--------------|
| `proveedor` | Truncate & Load | Mensual | CSV | No | Ninguna |
| `metricas` | Truncate & Load | Semanal/Mensual | API | Sí | proveedor (opcional) |
| `stats` | Derived (Regenerate) | Post-metricas | metricas | Sí | metricas |
| `historico` | Append Only | Semanal/Mensual | API | Sí | Ninguna |
| `daily` | Daily Upsert | Diario | metricas/API | Sí | metricas (opcional) |
| `registro` | Daily Insert | Diario | Generado | No | Ninguna |

### Orden de Implementación

1. **Fase 1** (Semana 1): Framework + Proveedores
2. **Fase 2** (Semana 2): Metricas + Stats
3. **Fase 3** (Semana 3): Historico + Daily + Registro
4. **Fase 4** (Semana 4): Orquestación + Automatización + Monitoreo

### KPIs de Éxito

- ✅ 100% de ejecuciones programadas completadas sin errores
- ✅ Tiempo de carga < 60 minutos (carga mensual completa)
- ✅ 0 datos duplicados en historico
- ✅ 100% de días con registro en daily (sin gaps)
- ✅ Tiempo de respuesta de health checks < 5 segundos
- ✅ Alertas enviadas en < 5 minutos ante fallo

---

## Próximos Pasos

1. **Revisión y Aprobación** del plan
2. **Asignación de recursos** (desarrollador + tiempo)
3. **Inicio de Fase 1**: Implementación del framework
4. **Testing** de cada componente
5. **Deployment** a producción con monitoreo

---

**Fecha de creación**: 2024-01-15
**Versión**: 1.0.0
**Autor**: Dashboard Sonar Team
**Estado**: Propuesta - Pendiente de aprobación

🤖 Generated with [Claude Code](https://claude.com/claude-code)
