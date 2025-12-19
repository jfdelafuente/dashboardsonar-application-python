# Database Schema - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Desarrolladores, Database Administrators, Arquitectos
**Database**: PostgreSQL 13+ / SQLite 3+ (compatible)

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Diagrama ER](#diagrama-er)
3. [Tablas Principales](#tablas-principales)
4. [Índices y Performance](#índices-y-performance)
5. [Relaciones](#relaciones)
6. [Queries Comunes](#queries-comunes)
7. [Migraciones](#migraciones)

---

## 🎯 Introducción

### Propósito de la Base de Datos

Dashboard Sonar utiliza una base de datos relacional para almacenar:
- **Métricas de calidad de código** desde SonarQube
- **Histórico** de métricas para análisis de tendencias
- **Usuarios** y autenticación
- **Estadísticas agregadas** por aplicación
- **Proveedores** y metadatos de aplicaciones

### Tecnologías Soportadas

| Base de Datos | Versión | Uso Recomendado |
|---------------|---------|-----------------|
| **PostgreSQL** | 13+ | Producción (recomendado) |
| **SQLite** | 3+ | Desarrollo y testing |

**ORM**: SQLAlchemy 2.0+

---

## 📊 Diagrama ER

### Diagrama Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DASHBOARD SONAR - DATABASE SCHEMA               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│     USERS       │
├─────────────────┤
│ PK id           │
│ UQ username     │
│ UQ email        │
│    password     │
│    created_on   │
│    is_admin     │
└─────────────────┘


┌─────────────────┐        1:N        ┌──────────────────┐
│   PROVEEDOR     │◄───────────────────│   METRICAS       │
├─────────────────┤                    ├──────────────────┤
│ PK id           │                    │ PK id            │
│ UQ aplicacion   │                    │ IX repo          │
│    proveedor    │                    │ IX aplicacion    │◄──────┐
│    tipo         │                    │    fecha         │       │
└─────────────────┘                    │ IX bugs          │       │
                                       │ IX reliability...│       │
                                       │ IX vulnerabil... │       │
                                       │ IX security_...  │       │
                                       │ IX code_smells   │       │
                                       │ IX sqale_rating  │       │
                                       │    alert_status  │       │
        ┌───────────────────────────  │    project       │       │
        │                              │ IX complexity    │       │
        │                              │ IX coverage      │       │
        │                              │    unit_tests    │       │
        │                              │ IX ncloc         │       │
        │                              │ IX duplicated... │       │
        │                              │ IX sqale_index   │       │
        │                              │ IX sqale_debt... │       │
        │                              │    size          │       │
        │                              │    quality_gate  │       │
        │                              └──────────────────┘       │
        │                                                          │
        │                              ┌──────────────────┐       │
        │  Mismo schema ───────────────│   HISTORICO      │       │
        │  (historical data)           ├──────────────────┤       │
        │                              │ PK id            │       │
        │                              │ IX repo          │       │
        │                              │ IX aplicacion    │       │
        │                              │    fecha         │       │
        │                              │ IX ... (same as  │       │
        │                              │        metricas) │       │
        │                              └──────────────────┘       │
        │                                                          │
        │                                                          │
        │                              ┌──────────────────┐       │
        └──────────────────────────────│     STATS        │       │
          Aggregated by aplicacion    ├──────────────────┤       │
                                      │ PK id            │       │
                                      │ UQ aplicacion    │───────┘
                                      │ IX repos         │
                                      │    reliability...│
                                      │    sqale_rating  │
                                      │    security_...  │
                                      │    alert_status..│
                                      │    dloc_rating   │
                                      │    coverage_...  │
                                      └──────────────────┘


┌─────────────────┐        1:N        ┌──────────────────┐
│   PROVEEDOR     │◄───────────────────│     DAILY        │
│  (referenced)   │                    ├──────────────────┤
└─────────────────┘                    │ PK id            │
                                       │ IX aplicacion    │
                                       │ IX repo (V128)   │ ⚠️ FIXED v1.11.0
                                       │    proveedor     │
                                       │ IX created_on    │
                                       │    num_bugs      │
                                       │    num_vulnera...│
                                       │    num_code_sm...│
                                       │    num_quality   │
                                       │    num_analisis  │
                                       │                  │
                                       │ INDEX: (aplicac..│
                                       │        created_on│
                                       └──────────────────┘


┌─────────────────┐
│   REGISTRO      │         (Process execution log)
├─────────────────┤
│ PK id           │
│ UQ proceso      │
│    created_on   │
│ UQ num_app      │
│ UQ num_repo     │
│ UQ num_bugs     │
│ UQ num_quality  │
│ UQ num_analisis │
└─────────────────┘


Legend:
  PK = Primary Key
  UQ = Unique Constraint
  IX = Indexed Column
  FK = Foreign Key (implicit via aplicacion)
  ◄──  = One-to-Many relationship
```

---

## 📁 Tablas Principales

### 1. METRICAS

**Propósito**: Almacena las métricas actuales de calidad de código para cada repositorio.

**Modelo**: `infocodest.models.metricas.Metrica`

#### Esquema

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK | Primary key |
| `repo` | VARCHAR(64) | NOT NULL, INDEX | Nombre del repositorio |
| `aplicacion` | VARCHAR(64) | INDEX | Nombre de la aplicación |
| `fecha` | VARCHAR(64) | | Fecha de la medición |
| `bugs` | INTEGER | NOT NULL, INDEX | Número de bugs |
| `reliability_rating` | INTEGER | NOT NULL, INDEX | Rating de fiabilidad (1-5) |
| `reliability_label` | VARCHAR(64) | | Label (A-E) |
| `vulnerabilities` | INTEGER | NOT NULL, INDEX | Número de vulnerabilidades |
| `security_rating` | INTEGER | NOT NULL, INDEX | Rating de seguridad (1-5) |
| `security_label` | VARCHAR(64) | | Label (A-E) |
| `code_smells` | INTEGER | NOT NULL, INDEX | Número de code smells |
| `sqale_rating` | INTEGER | NOT NULL, INDEX | Rating de mantenibilidad (1-5) |
| `sqale_label` | VARCHAR(64) | | Label (A-E) |
| `alert_status` | VARCHAR(64) | | Status del Quality Gate (OK/ERROR) |
| `project` | VARCHAR(128) | | Key del proyecto en SonarQube |
| `complexity` | INTEGER | NOT NULL, INDEX | Complejidad ciclomática |
| `coverage` | INTEGER | NOT NULL, INDEX | Cobertura de tests (%) |
| `unit_tests` | VARCHAR(64) | | Número de tests unitarios |
| `ncloc` | INTEGER | NOT NULL, INDEX | Líneas de código (no comentadas) |
| `duplicated_line_density` | INTEGER | NOT NULL, INDEX | Densidad de líneas duplicadas (%) |
| `sqale_index` | INTEGER | NOT NULL, INDEX | Índice SQALE (minutos) |
| `sqale_debt_ratio` | INTEGER | NOT NULL, INDEX | Ratio de deuda técnica (%) |
| `size` | VARCHAR(64) | | Tamaño del proyecto (S/M/L/XL) |
| `dloc_label` | VARCHAR(64) | | Label de duplicación (A-E) |
| `coverage_label` | VARCHAR(64) | | Label de cobertura (A-E) |
| `quality_gate` | VARCHAR(64) | | Estado del Quality Gate |

#### Índices

```sql
CREATE INDEX ix_metricas_repo ON metricas (repo);
CREATE INDEX ix_metricas_aplicacion ON metricas (aplicacion);
CREATE INDEX ix_metricas_bugs ON metricas (bugs);
CREATE INDEX ix_metricas_reliability_rating ON metricas (reliability_rating);
CREATE INDEX ix_metricas_vulnerabilities ON metricas (vulnerabilities);
CREATE INDEX ix_metricas_security_rating ON metricas (security_rating);
CREATE INDEX ix_metricas_code_smells ON metricas (code_smells);
CREATE INDEX ix_metricas_sqale_rating ON metricas (sqale_rating);
CREATE INDEX ix_metricas_complexity ON metricas (complexity);
CREATE INDEX ix_metricas_coverage ON metricas (coverage);
CREATE INDEX ix_metricas_ncloc ON metricas (ncloc);
CREATE INDEX ix_metricas_duplicated_line_density ON metricas (duplicated_line_density);
CREATE INDEX ix_metricas_sqale_index ON metricas (sqale_index);
CREATE INDEX ix_metricas_sqale_debt_ratio ON metricas (sqale_debt_ratio);
```

**Justificación de índices**: Todos los campos numéricos de métricas están indexados para permitir filtrado rápido en el dashboard (ej: filtrar por bugs > 10, coverage < 80%, etc.).

---

### 2. HISTORICO

**Propósito**: Almacena el histórico de métricas para análisis de tendencias.

**Modelo**: `infocodest.models.historico.Historico`

#### Esquema

**Idéntico a METRICAS** (todas las columnas y tipos son los mismos).

**Diferencia conceptual**:
- **METRICAS**: Estado actual (última medición)
- **HISTORICO**: Todas las mediciones históricas para trending

#### Ejemplo de Uso

```python
from infocodest.models.historico import Historico

# Obtener histórico de un repo
historico = Historico.query.filter_by(repo='my-repo').order_by(Historico.fecha.desc()).all()

# Analizar tendencia de bugs
trend = db.session.query(
    Historico.fecha,
    Historico.bugs
).filter(
    Historico.repo == 'my-repo'
).order_by(Historico.fecha).all()
```

---

### 3. USERS

**Propósito**: Gestión de usuarios y autenticación.

**Modelo**: `infocodest.models.users.User`

#### Esquema

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK | Primary key |
| `username` | VARCHAR(64) | UNIQUE | Nombre de usuario |
| `email` | VARCHAR | NOT NULL, UNIQUE | Email del usuario |
| `password` | VARCHAR(256) | NOT NULL | Password hasheado (bcrypt) |
| `created_on` | DATETIME | INDEX | Fecha de creación |
| `is_admin` | BOOLEAN | NOT NULL, DEFAULT FALSE | Si es administrador |

#### Características de Seguridad

**Password Hashing**:
```python
from infocodest.utils.security import hash_pass

# Al crear usuario, el password se hashea automáticamente
user = User(username='john', email='john@example.com', password='plaintextpass')
# password se convierte a bcrypt hash internamente
```

**Verificación**:
```python
from infocodest.utils.security import verify_pass

if verify_pass(user.password, input_password):
    # Login exitoso
```

#### Índices

```sql
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_created_on ON users (created_on);
```

---

### 4. PROVEEDOR

**Propósito**: Metadata de aplicaciones (proveedor, tipo).

**Modelo**: `infocodest.models.proveedor.Proveedor`

#### Esquema

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK | Primary key |
| `aplicacion` | VARCHAR(64) | NOT NULL, UNIQUE | Nombre de aplicación |
| `proveedor` | TEXT | | Nombre del proveedor/vendor |
| `tipo` | TEXT | | Tipo de aplicación (Frontend, Backend, etc.) |

#### Ejemplo de Uso

```python
from infocodest.models.proveedor import Proveedor

# Filtrar proyectos por proveedor
apps = Proveedor.query.filter_by(proveedor='Accenture').all()

# Contar aplicaciones por tipo
from sqlalchemy import func
stats = db.session.query(
    Proveedor.tipo,
    func.count(Proveedor.id)
).group_by(Proveedor.tipo).all()
```

---

### 5. STATS

**Propósito**: Estadísticas agregadas por aplicación (calculadas desde METRICAS).

**Modelo**: `infocodest.models.stat.Stat`

#### Esquema

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK | Primary key |
| `aplicacion` | VARCHAR(64) | NOT NULL, UNIQUE | Nombre de aplicación |
| `repos` | INTEGER | NOT NULL, INDEX | Número de repositorios |
| `reliability_rating` | INTEGER | NOT NULL | Count de repos con reliability A |
| `reliability_label` | TEXT | | Label agregado (ej: "5/10 repos A") |
| `sqale_rating` | INTEGER | NOT NULL | Count de repos con maintainability A |
| `sqale_label` | TEXT | | Label agregado |
| `security_rating` | INTEGER | NOT NULL | Count de repos con security A |
| `security_label` | TEXT | | Label agregado |
| `alert_status_ok` | INTEGER | NOT NULL | Count de repos con Quality Gate OK |
| `alert_status_label` | TEXT | | Label agregado |
| `dloc_rating` | INTEGER | NOT NULL | Count de repos con duplicación A |
| `dloc_label` | TEXT | | Label agregado |
| `coverage_rating` | INTEGER | NOT NULL | Count de repos con cobertura A |
| `coverage_label` | TEXT | | Label agregado |

#### Cálculo de Estadísticas

```python
# Ejemplo: Calcular stats para una aplicación
from infocodest.models.metricas import Metrica
from infocodest.models.stat import Stat

app_name = 'my-application'
metricas = Metrica.query.filter_by(aplicacion=app_name).all()

stat = Stat(
    aplicacion=app_name,
    repos=len(metricas),
    reliability_rating=len([m for m in metricas if m.reliability_label == 'A']),
    reliability_label=f"{reliability_rating}/{len(metricas)} repos A",
    # ... similar para otros ratings
)
db.session.add(stat)
db.session.commit()
```

---

### 6. DAILY

**Propósito**: Métricas agregadas diarias por repositorio (snapshots diarios).

**Modelo**: `infocodest.models.daily.Daily`

#### Esquema

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK | Primary key |
| `aplicacion` | VARCHAR(64) | NOT NULL, INDEX | Nombre de aplicación |
| `repo` | VARCHAR(128) | NOT NULL, INDEX | **Nombre del repositorio** ⚠️ **FIXED: v1.11.0** |
| `proveedor` | TEXT | | Proveedor |
| `created_on` | DATETIME | INDEX | Fecha del snapshot |
| `num_bugs` | INTEGER | NOT NULL | Total bugs |
| `num_vulnerabilities` | INTEGER | NOT NULL | Total vulnerabilidades |
| `num_code_smells` | INTEGER | NOT NULL | Total code smells |
| `num_quality` | INTEGER | NOT NULL | Métrica de calidad |
| `num_analisis` | INTEGER | NOT NULL | Número de análisis |

#### Índice Compuesto

```sql
CREATE INDEX idx_daily_aplicacion_date ON daily (aplicacion, created_on);
```

**Justificación**: Permite queries rápidas de trending por aplicación en un rango de fechas.

**Nota**: Una aplicación puede tener múltiples registros (uno por día con diferentes repos), por lo que `aplicacion` NO es unique.

#### Cambio de Esquema (v1.11.0)

⚠️ **BREAKING CHANGE - Migración Requerida**

**Fecha**: 2025-12-19
**Issue**: [#26](https://github.com/jfdelafuente/dashboardsonar-application-python/issues/26)

**Cambio**: La columna `repo` cambió de `INTEGER` a `VARCHAR(128)`.

**Antes** (❌ Incorrecto):

```sql
repo INTEGER NOT NULL
```

- Almacenaba un número (count de repositorios)
- Causaba error al intentar insertar nombres de repos

**Después** (✅ Correcto):

```sql
repo VARCHAR(128) NOT NULL
```

- Almacena el **nombre del repositorio** (ej: `'abacus-application-java'`)
- Consistente con las columnas `repo` en METRICAS e HISTORICO

**Migración**:

```bash
# Ejecutar migración automática
python scripts/migrations/fix_daily_repo_datatype.py --config Development

# Verificar migración
python scripts/migrations/fix_daily_repo_datatype.py --config Development --verify-only
```

**Documentación**: Ver [DAILY_REPO_DATATYPE_FIX.md](../bugfixes/DAILY_REPO_DATATYPE_FIX.md) para detalles completos.

---

### 7. REGISTRO

**Propósito**: Log de ejecuciones del pipeline de datos.

**Modelo**: `infocodest.models.registros.Registro`

#### Esquema

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK | Primary key |
| `proceso` | VARCHAR(64) | NOT NULL, UNIQUE | ID del proceso |
| `created_on` | DATETIME | | Fecha de ejecución |
| `num_app` | INTEGER | NOT NULL, UNIQUE, INDEX | Apps procesadas |
| `num_repo` | INTEGER | NOT NULL, UNIQUE, INDEX | Repos procesados |
| `num_bugs` | INTEGER | NOT NULL, UNIQUE, INDEX | Bugs encontrados |
| `num_quality` | INTEGER | NOT NULL, UNIQUE, INDEX | Quality gates |
| `num_analisis` | INTEGER | UNIQUE, INDEX | Análisis ejecutados |

**Nota**: Las columnas num_* tienen UNIQUE constraint, lo cual parece ser un error de diseño (debería ser solo INDEX). **RECOMENDACIÓN**: Remover UNIQUE en próxima migración.

---

## 🔍 Índices y Performance

### Estrategia de Indexación

**Principio**: Indexar columnas utilizadas frecuentemente en:
1. **WHERE clauses** (filtros)
2. **ORDER BY** (ordenamiento)
3. **JOIN conditions** (aunque no tenemos FKs explícitas)
4. **GROUP BY** (agregaciones)

### Índices Críticos para Performance

#### METRICAS / HISTORICO

```sql
-- Para filtros en dashboard
CREATE INDEX idx_metricas_app_bugs ON metricas (aplicacion, bugs);
CREATE INDEX idx_metricas_app_coverage ON metricas (aplicacion, coverage);

-- Para queries de trending (histórico por fecha)
CREATE INDEX idx_historico_repo_fecha ON historico (repo, fecha);
CREATE INDEX idx_historico_app_fecha ON historico (aplicacion, fecha);
```

#### DAILY

```sql
-- Para trending diario
CREATE INDEX idx_daily_app_date ON daily (aplicacion, created_on DESC);
```

#### USERS

```sql
-- Para login rápido
CREATE UNIQUE INDEX idx_users_username ON users (username);
CREATE UNIQUE INDEX idx_users_email ON users (email);
```

### Análisis de Query Performance

```sql
-- PostgreSQL: Analizar plan de ejecución
EXPLAIN ANALYZE
SELECT * FROM metricas
WHERE aplicacion = 'my-app' AND bugs > 10
ORDER BY bugs DESC;

-- Verificar uso de índices
\d+ metricas

-- Ver índices sin usar (candidates para eliminación)
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY schemaname, tablename;
```

---

## 🔗 Relaciones

### Relaciones Lógicas (No Enforced por FK)

Dashboard Sonar **no utiliza Foreign Keys explícitas**, pero tiene relaciones lógicas via columna `aplicacion`:

```
PROVEEDOR (aplicacion) ◄──── 1:N ───── METRICAS (aplicacion)
                        ◄──── 1:N ───── HISTORICO (aplicacion)
                        ◄──── 1:1 ───── STATS (aplicacion)
                        ◄──── 1:N ───── DAILY (aplicacion)
```

### Ejemplo de Join Lógico

```python
from infocodest.models.metricas import Metrica
from infocodest.models.proveedor import Proveedor

# Join con SQLAlchemy
results = db.session.query(Metrica, Proveedor).join(
    Proveedor,
    Metrica.aplicacion == Proveedor.aplicacion
).filter(
    Proveedor.proveedor == 'Accenture'
).all()

# O con SQL raw
query = """
SELECT m.*, p.proveedor, p.tipo
FROM metricas m
LEFT JOIN proveedor p ON m.aplicacion = p.aplicacion
WHERE p.proveedor = :proveedor
"""
results = db.session.execute(query, {'proveedor': 'Accenture'})
```

**¿Por qué no FKs?**:
- Flexibilidad para importar datos desde SonarQube sin validación estricta
- Evitar problemas de integridad referencial durante cargas masivas
- Simplicidad en migraciones

**Trade-off**: Responsabilidad de mantener integridad en capa de aplicación.

---

## 📝 Queries Comunes

### 1. Obtener Métricas Actuales de una Aplicación

```python
from infocodest.models.metricas import Metrica

metricas = Metrica.query.filter_by(aplicacion='my-app').all()

# Con filtros adicionales
metricas_criticas = Metrica.query.filter(
    Metrica.aplicacion == 'my-app',
    Metrica.bugs > 10,
    Metrica.coverage < 80
).all()
```

### 2. Trending de Bugs (Histórico)

```python
from infocodest.models.historico import Historico
from sqlalchemy import func

# Últimos 30 días
trending = db.session.query(
    Historico.fecha,
    func.sum(Historico.bugs).label('total_bugs')
).filter(
    Historico.aplicacion == 'my-app'
).group_by(Historico.fecha).order_by(Historico.fecha.desc()).limit(30).all()
```

### 3. Top 10 Aplicaciones con Más Bugs

```python
from infocodest.models.metricas import Metrica
from sqlalchemy import func

top_bugs = db.session.query(
    Metrica.aplicacion,
    func.sum(Metrica.bugs).label('total_bugs')
).group_by(Metrica.aplicacion).order_by(func.sum(Metrica.bugs).desc()).limit(10).all()
```

### 4. Aplicaciones por Proveedor con Estadísticas

```python
from infocodest.models.proveedor import Proveedor
from infocodest.models.stat import Stat

apps = db.session.query(Proveedor, Stat).join(
    Stat,
    Proveedor.aplicacion == Stat.aplicacion
).filter(
    Proveedor.proveedor == 'Accenture'
).all()
```

### 5. Buscar Proyectos con Quality Gate Failed

```python
from infocodest.models.metricas import Metrica

failed_projects = Metrica.query.filter(
    Metrica.alert_status == 'ERROR'
).all()

# O con quality_gate
failed_qg = Metrica.query.filter(
    Metrica.quality_gate != 'OK'
).all()
```

### 6. Cobertura Promedio por Aplicación

```python
from infocodest.models.metricas import Metrica
from sqlalchemy import func

coverage_stats = db.session.query(
    Metrica.aplicacion,
    func.avg(Metrica.coverage).label('avg_coverage'),
    func.min(Metrica.coverage).label('min_coverage'),
    func.max(Metrica.coverage).label('max_coverage')
).group_by(Metrica.aplicacion).all()
```

---

## 🔄 Migraciones

### Herramienta: Flask-Migrate (Alembic)

**Ubicación de migraciones**: `migrations/versions/`

### Comandos Comunes

```bash
# Inicializar migraciones (ya hecho)
flask db init

# Crear nueva migración automática
flask db migrate -m "descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade

# Ver historial
flask db history

# Ver estado actual
flask db current
```

### Ejemplo de Migración

**Agregar columna `tags` a METRICAS**:

```bash
flask db migrate -m "add tags column to metricas"
```

Genera archivo en `migrations/versions/`:

```python
def upgrade():
    op.add_column('metricas', sa.Column('tags', sa.String(255), nullable=True))
    op.create_index('ix_metricas_tags', 'metricas', ['tags'])

def downgrade():
    op.drop_index('ix_metricas_tags', table_name='metricas')
    op.drop_column('metricas', 'tags')
```

Aplicar:
```bash
flask db upgrade
```

### Migración: Fix Daily.repo Data Type (v1.11.0) ✅ COMPLETADA

**Fecha**: 2025-12-19
**Issue**: [#26](https://github.com/jfdelafuente/dashboardsonar-application-python/issues/26)
**Script**: `scripts/migrations/fix_daily_repo_datatype.py`

**Problema**: La columna `daily.repo` estaba definida como `INTEGER` pero el código insertaba strings (nombres de repositorios).

**Error**:

```text
psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type integer: "abacus-application-java"
```

**Solución Implementada**:

```bash
# Ejecutar migración
python scripts/migrations/fix_daily_repo_datatype.py --config Development
```

**Cambios aplicados**:

- ✅ Cambió `repo` de `INTEGER` a `VARCHAR(128)`
- ✅ Preservó datos existentes (si los hubiera)
- ✅ Recreó índices correctamente
- ✅ Soporta SQLite, PostgreSQL y MySQL
- ✅ Incluye tests de verificación

**Documentación completa**: [DAILY_REPO_DATATYPE_FIX.md](../bugfixes/DAILY_REPO_DATATYPE_FIX.md)

---

### Migración: Remover UNIQUE de REGISTRO (Pendiente)

**Problema identificado**: Las columnas num_* en REGISTRO tienen UNIQUE constraint innecesario.

**Solución**:

```python
# migrations/versions/YYYYMMDD_remove_unique_registro.py
from alembic import op

def upgrade():
    # PostgreSQL
    op.drop_constraint('registro_num_app_key', 'registro', type_='unique')
    op.drop_constraint('registro_num_repo_key', 'registro', type_='unique')
    op.drop_constraint('registro_num_bugs_key', 'registro', type_='unique')
    op.drop_constraint('registro_num_quality_key', 'registro', type_='unique')
    op.drop_constraint('registro_num_analisis_key', 'registro', type_='unique')

def downgrade():
    # Revertir si es necesario
    op.create_unique_constraint('registro_num_app_key', 'registro', ['num_app'])
    # ... etc
```

---

## 📊 Tamaño y Estadísticas

### Estimación de Tamaño

**Asumiendo**:
- 100 aplicaciones
- 500 repositorios totales
- 30 días de histórico
- 1 snapshot diario por aplicación

| Tabla | Registros | Tamaño Estimado (PostgreSQL) |
|-------|-----------|------------------------------|
| METRICAS | 500 | ~200 KB |
| HISTORICO | 15,000 (500 repos * 30 días) | ~6 MB |
| USERS | 20 | ~5 KB |
| PROVEEDOR | 100 | ~10 KB |
| STATS | 100 | ~15 KB |
| DAILY | 3,000 (100 apps * 30 días) | ~500 KB |
| REGISTRO | 30 (1 ejecución/día) | ~5 KB |

**Total estimado**: ~7 MB de datos + índices (~14 MB total)

**Crecimiento**:
- HISTORICO: +6 MB/mes
- DAILY: +500 KB/mes

---

## 🔧 Mantenimiento

### Vacuum (PostgreSQL)

```sql
-- Liberar espacio
VACUUM ANALYZE metricas;
VACUUM ANALYZE historico;

-- Vacuum completo (requiere EXCLUSIVE lock)
VACUUM FULL metricas;
```

### Rebuild Índices

```sql
-- Si los índices están fragmentados
REINDEX TABLE metricas;
REINDEX TABLE historico;
```

### Limpieza de Datos Antiguos

```sql
-- Eliminar histórico >1 año
DELETE FROM historico
WHERE fecha < (CURRENT_DATE - INTERVAL '1 year');

-- Eliminar daily >3 meses
DELETE FROM daily
WHERE created_on < (CURRENT_DATE - INTERVAL '3 months');
```

---

## 📚 Referencias

### Documentación Relacionada

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura general
- **[DATA_PIPELINE.md](../data/DATA_PIPELINE.md)** - Cómo se cargan los datos
- **[PERFORMANCE_TUNING.md](../advanced/PERFORMANCE_TUNING.md)** - Optimización de queries
- **[BACKUP_RESTORE.md](../../2-operations/backup-recovery/BACKUP_RESTORE.md)** - Backup de BD

### Recursos Externos

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- [Flask-Migrate](https://flask-migrate.readthedocs.io/)
- [Alembic](https://alembic.sqlalchemy.org/)

---

**Última actualización**: 2025-12-19
**Versión del schema**: 1.11.0 (Daily.repo: INTEGER → VARCHAR(128))
**Mantenido por**: Equipo de Desarrollo
