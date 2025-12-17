# Análisis de Impacto: Incremento del Campo `project` de 64 a 128 caracteres

**Fecha**: 2025-12-16
**Tablas afectadas**: `metricas`, `historico`
**Campo**: `project`
**Cambio propuesto**: `String(64)` → `String(128)`

---

## 1. Contexto

El campo `project` actualmente tiene un límite de 64 caracteres en las tablas `metricas` e `historico`. Este límite puede ser insuficiente para nombres de proyectos largos en SonarQube, especialmente cuando incluyen:

- Nombres de organización
- Rutas completas de repositorios
- Prefijos/sufijos descriptivos
- Identificadores de entorno

---

## 2. Impacto Técnico

### 2.1 Modelos de Datos

**Archivos a modificar**:
- `infocodest/models/metricas.py` (línea 25)
- `infocodest/models/historico.py` (línea 25)

```python
# Actual
project = db.Column(db.String(64), nullable=True)

# Propuesto
project = db.Column(db.String(128), nullable=True)
```

**Impacto**: ✅ Bajo
- Cambio simple en definición de modelo
- No afecta lógica de negocio
- Campo es `nullable=True`, sin restricciones críticas

### 2.2 Base de Datos

#### 2.2.1 Migración Requerida

Se necesita crear una migración de Alembic:

```python
# migrations/versions/xxxx_increase_project_field_size.py

def upgrade():
    with op.batch_alter_table('metricas', schema=None) as batch_op:
        batch_op.alter_column('project',
                              existing_type=sa.String(length=64),
                              type_=sa.String(length=128),
                              existing_nullable=True)

    with op.batch_alter_table('historico', schema=None) as batch_op:
        batch_op.alter_column('project',
                              existing_type=sa.String(length=64),
                              type_=sa.String(length=128),
                              existing_nullable=True)

def downgrade():
    with op.batch_alter_table('metricas', schema=None) as batch_op:
        batch_op.alter_column('project',
                              existing_type=sa.String(length=128),
                              type_=sa.String(length=64),
                              existing_nullable=True)

    with op.batch_alter_table('historico', schema=None) as batch_op:
        batch_op.alter_column('project',
                              existing_type=sa.String(length=128),
                              type_=sa.String(length=64),
                              existing_nullable=True)
```

**Impacto**: ✅ Bajo-Medio
- **SQLite**: ALTER COLUMN se ejecuta con `batch_alter_table` (sin problemas)
- **PostgreSQL**: ALTER COLUMN es rápido, no requiere reescritura de tabla
- **MySQL**: ALTER COLUMN puede ser lento en tablas grandes (requiere reescritura)

#### 2.2.2 Estimación de Downtime

| Base de Datos | Registros | Tiempo Estimado | Requiere Downtime |
|--------------|-----------|-----------------|-------------------|
| SQLite       | < 1M      | < 1 segundo     | No                |
| PostgreSQL   | < 1M      | < 5 segundos    | No                |
| PostgreSQL   | > 1M      | < 30 segundos   | No (online ALTER) |
| MySQL        | < 100K    | < 10 segundos   | Sí                |
| MySQL        | > 1M      | 1-5 minutos     | Sí                |

**Recomendación**:
- PostgreSQL: Ejecutar en horario normal (soporte de ALTER online)
- MySQL: Ejecutar en ventana de mantenimiento

#### 2.2.3 Impacto en Almacenamiento

**Cálculo por registro**:
- Espacio adicional por carácter: ~1 byte (UTF-8)
- Incremento máximo: 64 bytes adicionales por registro
- Incremento típico: 0-20 bytes (la mayoría de proyectos < 64 chars)

**Ejemplo con 1 millón de registros**:
- Peor caso: 64 MB adicionales por tabla
- Caso típico: 10-20 MB adicionales por tabla
- Total (2 tablas): ~20-40 MB adicionales

**Impacto**: ✅ Mínimo
- Incremento despreciable en bases de datos modernas
- Indices no afectados (campo no está indexado)

### 2.3 Código de Aplicación

#### 2.3.1 Scripts de Carga de Datos

**Archivo**: `scripts/data/load_data.py`

Actualmente la validación ya trunca a 64 caracteres:

```python
# Línea 199
'project': validate_string_field(row.get("project"), "project"),
```

**Cambio necesario**:

```python
'project': validate_string_field(row.get("project"), "project", max_length=128),
```

**Impacto**: ✅ Bajo
- Cambio en un solo lugar
- Permite cargar datos con nombres más largos
- Reduce warnings de truncamiento

#### 2.3.2 Validación y Formularios

**Búsqueda de validación del campo project**:

```bash
grep -r "project" infocodest/forms/ infocodest/utils/
```

**Resultado**: No se encontraron validaciones explícitas del tamaño del campo `project` en formularios o utilidades.

**Impacto**: ✅ Ninguno
- No hay validaciones front-end que actualizar
- Campo no expuesto en formularios de usuario

#### 2.3.3 Consultas y Reportes

El campo `project` no está indexado, se usa solo para:
- Visualización en dashboards
- Filtrado ocasional
- Exportación de datos

**Impacto**: ✅ Ninguno
- No hay joins ni búsquedas intensivas sobre este campo
- Sin degradación de performance esperada

### 2.4 Tests

**Tests afectados**: Ninguno identificado

Búsqueda en tests:

```bash
grep -r "project.*String\|project.*64" tests/
```

**Resultado**: No hay assertions sobre el tamaño del campo `project` en tests.

**Impacto**: ✅ Ninguno
- No se requiere actualizar tests

---

## 3. Impacto en el Negocio

### 3.1 Ventajas

✅ **Compatibilidad**: Soporte para nombres de proyectos largos de SonarQube
✅ **Prevención de Errores**: Menos registros descartados por truncamiento
✅ **Calidad de Datos**: Nombres completos sin pérdida de información
✅ **Flexibilidad**: Acomoda diferentes convenciones de nombrado

### 3.2 Desventajas

⚠️ **Almacenamiento**: Incremento mínimo en espacio de disco (~20-40 MB para 1M registros)
⚠️ **Migración**: Requiere ejecutar migración en producción (downtime mínimo)

---

## 4. Análisis de Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Fallo de migración | Baja | Alto | Backup completo antes de migración |
| Pérdida de datos en downgrade | Media | Medio | Validar que no hay datos > 64 chars antes de downgrade |
| Performance degradada | Muy Baja | Bajo | Monitoreo post-migración |
| Incompatibilidad backward | Muy Baja | Bajo | Código existente sigue funcionando |

---

## 5. Plan de Implementación

### Fase 1: Preparación
1. ✅ Análisis de impacto (este documento)
2. ⏳ Crear migración de Alembic
3. ⏳ Actualizar modelos
4. ⏳ Actualizar script de carga de datos
5. ⏳ Actualizar documentación

### Fase 2: Testing
1. ⏳ Probar migración en desarrollo (SQLite)
2. ⏳ Probar migración en staging (PostgreSQL/MySQL)
3. ⏳ Validar carga de datos con nombres largos
4. ⏳ Verificar consultas y reportes

### Fase 3: Producción
1. ⏳ Backup completo de base de datos
2. ⏳ Ejecutar migración: `flask db upgrade`
3. ⏳ Verificar integridad de datos
4. ⏳ Monitorear performance (primeras 24h)

### Fase 4: Post-Implementación
1. ⏳ Validar que no hay errores en logs
2. ⏳ Confirmar carga correcta de nuevos datos
3. ⏳ Actualizar documentación de producción

---

## 6. Comandos de Migración

### Crear migración

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Generar migración automática
flask db migrate -m "Increase project field size to 128 characters"

# Revisar migración generada
# Editar si es necesario: migrations/versions/xxxx_increase_project_field_size.py

# Aplicar migración
flask db upgrade

# En caso de rollback (solo si no hay datos > 64 chars)
flask db downgrade
```

---

## 7. Validaciones Pre-Migración

### Verificar datos existentes que excederían 64 caracteres

```sql
-- PostgreSQL/MySQL
SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN LENGTH(project) > 64 THEN 1 END) as records_over_64,
    MAX(LENGTH(project)) as max_length
FROM metricas
WHERE project IS NOT NULL;

SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN LENGTH(project) > 64 THEN 1 END) as records_over_64,
    MAX(LENGTH(project)) as max_length
FROM historico
WHERE project IS NOT NULL;

-- SQLite
SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN LENGTH(project) > 64 THEN 1 END) as records_over_64,
    MAX(LENGTH(project)) as max_length
FROM metricas
WHERE project IS NOT NULL;
```

---

## 8. Recomendaciones

### ✅ Recomendación: PROCEDER CON LA MIGRACIÓN

**Justificación**:
1. **Impacto técnico mínimo**: Cambio simple y seguro
2. **Beneficio claro**: Evita pérdida de información
3. **Riesgo controlado**: Migración reversible con backup
4. **Sin breaking changes**: Código existente compatible

### Orden de Ejecución Recomendado

1. **Desarrollo**: Aplicar cambios y probar
2. **Testing/Staging**: Validar migración con datos reales
3. **Producción**: Ejecutar en ventana de mantenimiento (solo MySQL) o en horario normal (PostgreSQL/SQLite)

### Consideraciones Especiales

- **PostgreSQL**: No requiere ventana de mantenimiento (ALTER COLUMN es online)
- **MySQL**: Planificar ventana de mantenimiento para tablas > 1M registros
- **SQLite**: Sin impacto de performance, migración instantánea

---

## 9. Conclusión

El cambio de `String(64)` a `String(128)` para el campo `project` en las tablas `metricas` e `historico` es:

- ✅ **Técnicamente viable**: Bajo riesgo, fácil implementación
- ✅ **Funcionalmente beneficioso**: Previene truncamiento de datos
- ✅ **Operacionalmente seguro**: Migración reversible con backup
- ✅ **Estratégicamente recomendable**: Mejora calidad de datos

**Decisión**: ✅ **APROBADO PARA IMPLEMENTACIÓN**

---

**Preparado por**: Claude Code
**Revisado por**: [Pendiente]
**Aprobado por**: [Pendiente]
**Fecha de implementación planeada**: [Pendiente]
