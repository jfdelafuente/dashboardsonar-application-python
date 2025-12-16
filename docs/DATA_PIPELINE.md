# Data Pipeline Documentation

**Dashboard Sonar - Comprehensive Data Processing Pipeline**

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Pipeline](#arquitectura-del-pipeline)
3. [Scripts Individuales](#scripts-individuales)
4. [Orquestador de Pipeline](#orquestador-de-pipeline)
5. [Uso](#uso)
6. [Ejemplos](#ejemplos)
7. [Troubleshooting](#troubleshooting)

---

## Descripción General

El Data Pipeline de Dashboard Sonar es un sistema coordinado de scripts que procesan datos de calidad de código desde SonarQube a través de múltiples etapas:

1. **Carga de Datos** (ETL) - Importa datos desde archivos CSV
2. **Generación Diaria** - Crea snapshots agregados por día
3. **Generación de Estadísticas** - Calcula métricas agregadas por aplicación
4. **Registro de Auditoría** - Crea registros del proceso para trazabilidad

### Beneficios del Pipeline Orquestado

- ✅ **Ejecución Ordenada**: Scripts se ejecutan en la secuencia correcta
- ✅ **Manejo de Errores**: Si un paso falla, el pipeline se detiene
- ✅ **Variables de Entorno**: Carga automática desde `.env`
- ✅ **Configuración Flexible**: Soporta Development, Testing y Production
- ✅ **Logging Completo**: Salida en tiempo real de cada paso
- ✅ **Resumen de Ejecución**: Reporte final con duración y estado de cada paso

---

## Arquitectura del Pipeline

### Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Pipeline Orchestrator                    │
│                  (run_all_data_scripts.py)                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
        Load .env Variables           Check Virtual Environment
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 1: Load Data from CSV                                        │
│ Script: load_data.py                                               │
│ Input:  CSV files (metricas.csv, historico.csv, proveedores.csv)  │
│ Output: Database tables (metricas, historico, proveedor)          │
└───────────────────────────────────────────────────────────────────┘
                │
                ▼ (if success)
┌───────────────────────────────────────────────────────────────────┐
│ STEP 2: Generate Daily Snapshots                                  │
│ Script: generate_daily.py                                          │
│ Input:  metricas table                                             │
│ Output: daily table (aggregated by aplicacion + repo + date)      │
└───────────────────────────────────────────────────────────────────┘
                │
                ▼ (if success)
┌───────────────────────────────────────────────────────────────────┐
│ STEP 3: Generate Statistics                                       │
│ Script: generate_stats.py                                          │
│ Input:  metricas table                                             │
│ Output: stats table (aggregated by aplicacion)                    │
└───────────────────────────────────────────────────────────────────┘
                │
                ▼ (if success)
┌───────────────────────────────────────────────────────────────────┐
│ STEP 4: Create Audit Registry                                     │
│ Script: generate_registro.py                                       │
│ Input:  All tables                                                 │
│ Output: registros table (audit log with global stats)             │
└───────────────────────────────────────────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ Summary Report │
        └───────────────┘
```

### Dependencias entre Scripts

```
load_data.py
    │
    ├──> generate_daily.py (requires metricas)
    │
    ├──> generate_stats.py (requires metricas)
    │
    └──> generate_registro.py (requires all tables)
```

---

## Scripts Individuales

### 1. `load_data.py` - Carga de Datos

**Propósito**: Cargar datos desde archivos CSV a la base de datos.

**Tablas Afectadas**:
- `metricas` - Métricas actuales de repositorios
- `historico` - Histórico completo de análisis
- `proveedor` - Relación aplicación-proveedor

**Características**:
- ✅ Validación de campos (tamaño, tipo, rango)
- ✅ Manejo de errores (descarta registros inválidos)
- ✅ Inserción en batch para performance
- ✅ Fallback individual si batch falla
- ✅ Transformaciones ETL automáticas

**Opciones**:
```bash
--config CONFIG        # Development, Testing, Production
--data-dir PATH        # Directorio con CSVs (default: ./datos)
--batch-size N         # Tamaño de lote (default: 100)
```

---

### 2. `generate_daily.py` - Snapshots Diarios

**Propósito**: Generar agregaciones diarias por repositorio.

**Tabla Afectada**: `daily`

**Datos Generados**:
- Aplicación + Repositorio + Fecha
- Bugs, Vulnerabilidades, Code Smells agregados
- Quality Gates (OK/ERROR)
- Conteo de análisis

**Características**:
- ✅ Agregación temporal automática
- ✅ Soporta fechas personalizadas
- ✅ Puede limpiar y regenerar
- ✅ Detección de duplicados

**Opciones**:
```bash
--config CONFIG        # Development, Testing, Production
--date YYYY-MM-DD      # Fecha específica (default: hoy)
--clear-date           # Limpiar registros de la fecha antes de generar
--batch-size N         # Tamaño de lote (default: 100)
```

---

### 3. `generate_stats.py` - Estadísticas Agregadas

**Propósito**: Calcular estadísticas por aplicación.

**Tabla Afectada**: `stats`

**Datos Generados**:
- Número de repositorios por aplicación
- Conteo de ratings "A" (reliability, security, maintainability)
- Conteo de Quality Gates "OK"
- Labels de calidad

**Características**:
- ✅ Agregación multi-nivel
- ✅ Cálculos de ratings basados en distribución
- ✅ Puede limpiar y regenerar
- ✅ Performance optimizada con queries SQL

**Opciones**:
```bash
--config CONFIG        # Development, Testing, Production
--clear                # Limpiar stats existentes antes de generar
--batch-size N         # Tamaño de lote (default: 100)
```

---

### 4. `generate_registro.py` - Registro de Auditoría

**Propósito**: Crear registro del proceso con estadísticas globales.

**Tabla Afectada**: `registros`

**Datos Generados**:
- Nombre del proceso
- Timestamp de ejecución
- Estadísticas globales:
  - Total de aplicaciones
  - Total de repositorios
  - Total de bugs
  - Quality Gates OK
  - Análisis totales

**Características**:
- ✅ Auditoría completa del pipeline
- ✅ Trazabilidad de ejecuciones
- ✅ Estadísticas de health check
- ✅ Nombres de proceso personalizables

**Opciones**:
```bash
--config CONFIG           # Development, Testing, Production
--process-name NAME       # Nombre del proceso (default: "Registro informe Sonar")
--date YYYY-MM-DD         # Fecha del registro (default: hoy)
```

---

## Orquestador de Pipeline

### Script Principal: `run_all_data_scripts.py`

El orquestador ejecuta todos los scripts en orden, con manejo de errores y logging.

**Características**:
- ✅ Ejecución secuencial con validación de éxito
- ✅ Carga automática de variables de entorno desde `.env`
- ✅ Salida en tiempo real de cada script
- ✅ Resumen final con duración y estado
- ✅ Soporte para dry-run
- ✅ Skip de pasos individuales
- ✅ Configuración unificada

**Opciones**:

```bash
--config CONFIG        # Development, Testing, Production
--data-dir PATH        # Directorio con CSVs
--date YYYY-MM-DD      # Fecha para daily snapshot
--batch-size N         # Tamaño de lote para todos los scripts

# Regeneración
--clear-daily          # Limpiar daily antes de generar
--clear-stats          # Limpiar stats antes de generar

# Control de ejecución
--skip-load            # Saltar carga de datos
--skip-daily           # Saltar generación daily
--skip-stats           # Saltar generación stats
--skip-registry        # Saltar creación de registro

# Utilidades
--dry-run              # Mostrar plan sin ejecutar
```

---

## Uso

### Wrappers Disponibles

#### Windows: `run_data_pipeline.bat`

```bash
# Ejecución básica (Development con SQLite)
run_data_pipeline.bat

# Production con PostgreSQL
run_data_pipeline.bat Production

# Con opciones adicionales
run_data_pipeline.bat Development --clear-stats

# Custom data directory
run_data_pipeline.bat Production --data-dir C:\datos_sonar
```

#### Linux/macOS: `run_data_pipeline.sh`

```bash
# Dar permisos de ejecución (solo primera vez)
chmod +x run_data_pipeline.sh

# Ejecución básica (Development con SQLite)
./run_data_pipeline.sh

# Production con PostgreSQL
./run_data_pipeline.sh Production

# Con opciones adicionales
./run_data_pipeline.sh Development --clear-stats

# Custom data directory
./run_data_pipeline.sh Production --data-dir /var/datos_sonar
```

### Ejecución Directa del Script Python

```bash
python scripts/data/run_all_data_scripts.py [OPTIONS]
```

---

## Ejemplos

### Ejemplo 1: Carga Completa Inicial

**Escenario**: Primera vez cargando datos en un entorno nuevo.

```bash
# Development con SQLite
run_data_pipeline.bat

# Production con PostgreSQL
run_data_pipeline.bat Production
```

**Resultado**:
1. Carga datos desde `./datos/*.csv`
2. Genera daily snapshots para hoy
3. Genera estadísticas agregadas
4. Crea registro de auditoría

---

### Ejemplo 2: Regenerar Solo Estadísticas

**Escenario**: Los datos están cargados, solo quieres recalcular stats.

```bash
run_data_pipeline.bat --skip-load --skip-daily --clear-stats
```

**Resultado**:
1. ~~Carga de datos~~ (skipped)
2. ~~Daily snapshots~~ (skipped)
3. Regenera estadísticas (limpia y recalcula)
4. Crea registro de auditoría

---

### Ejemplo 3: Carga con Fecha Específica

**Escenario**: Cargar datos para un día específico del pasado.

```bash
run_data_pipeline.bat Production --date 2025-12-01 --data-dir ./datos_diciembre
```

**Resultado**:
1. Carga datos desde `./datos_diciembre/*.csv`
2. Genera daily snapshot para 2025-12-01
3. Genera estadísticas
4. Crea registro con fecha 2025-12-01

---

### Ejemplo 4: Dry Run (Ver Plan)

**Escenario**: Ver qué se ejecutaría sin hacer cambios.

```bash
run_data_pipeline.bat Production --dry-run
```

**Resultado**:
- Muestra los comandos que se ejecutarían
- No modifica la base de datos
- Útil para validar configuración

---

### Ejemplo 5: Regenerar Daily del Día Anterior

**Escenario**: Los datos de ayer están mal, quieres regenerarlos.

```bash
run_data_pipeline.bat --skip-load --date 2025-12-15 --clear-daily
```

**Resultado**:
1. ~~Carga de datos~~ (skipped)
2. Regenera daily para 2025-12-15 (limpia primero)
3. Regenera stats
4. Crea registro

---

### Ejemplo 6: Pipeline Completo con Todas las Opciones

```bash
run_data_pipeline.bat Production \
    --data-dir C:\sonar_data \
    --date 2025-12-15 \
    --batch-size 500 \
    --clear-daily \
    --clear-stats
```

**Resultado**:
- Carga desde `C:\sonar_data`
- Daily para 2025-12-15 (limpiado primero)
- Stats regeneradas (limpiadas primero)
- Batch size de 500 para mejor performance
- Production config (PostgreSQL)

---

## Salida del Pipeline

### Formato de Output

```
================================================================================
DATA PIPELINE ORCHESTRATOR
================================================================================

Configuration: Production
Data Directory: ./datos
Date: 2025-12-16
Batch Size: 100

[+] Loading environment variables from .env file...
[+] Environment variables loaded successfully

================================================================================
[*] Step: 1. Load Data from CSV Files
[*] Command: python scripts\data\load_data.py --config Production
================================================================================

[Processing metricas.csv...]
[+] Loaded 150 metricas records (3 skipped)
[Processing historico.csv...]
[+] Loaded 500 historico records (5 skipped)
[Processing proveedores.csv...]
[+] Loaded 20 proveedor records (0 skipped)

[✓] 1. Load Data from CSV Files completed successfully (12.34s)

================================================================================
[*] Step: 2. Generate Daily Snapshots
[*] Command: python scripts\data\generate_daily.py --config Production
================================================================================

[+] Generated 45 daily records for 2025-12-16
[✓] 2. Generate Daily Snapshots completed successfully (3.21s)

================================================================================
[*] Step: 3. Generate Aggregated Statistics
[*] Command: python scripts\data\generate_stats.py --config Production
================================================================================

[+] Generated 12 stats records
[✓] 3. Generate Aggregated Statistics completed successfully (1.56s)

================================================================================
[*] Step: 4. Create Audit Registry Record
[*] Command: python scripts\data\generate_registro.py --config Production
================================================================================

[+] Created registry record: Data Pipeline - 2025-12-16 10:30:45
[✓] 4. Create Audit Registry Record completed successfully (0.89s)

================================================================================
EXECUTION SUMMARY
================================================================================

Total Duration: 18.00s
Steps Executed: 4

Results:
  ✓ Successful: 4

Details:
  [✓] 1. Load Data from CSV Files                (12.34s)
  [✓] 2. Generate Daily Snapshots                (3.21s)
  [✓] 3. Generate Aggregated Statistics          (1.56s)
  [✓] 4. Create Audit Registry Record            (0.89s)

================================================================================

[✓] Pipeline completed successfully
```

---

## Troubleshooting

### Error: Virtual environment not activated

**Síntoma**:
```
[!] Error: Virtual environment is not activated
```

**Solución**:
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

---

### Error: .env file not found

**Síntoma**:
```
[!] Warning: .env file not found
```

**Solución**:
```bash
# Copiar desde el ejemplo
cp .env.example .env

# Editar con tus valores
nano .env  # o notepad .env en Windows
```

---

### Error: Database connection failed

**Síntoma**:
```
psycopg2.OperationalError: could not connect to server
```

**Solución**:

1. Verificar que PostgreSQL está corriendo
2. Verificar credenciales en `.env`:
   ```env
   DB_ENGINE=postgresql
   DB_USERNAME=postgres
   DB_PASS=tu_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=dashboardsonar
   ```
3. Probar conexión: `psql -h localhost -U postgres`

---

### Error: CSV file not found

**Síntoma**:
```
FileNotFoundError: [Errno 2] No such file or directory: './datos/metricas.csv'
```

**Solución**:
```bash
# Verificar que los archivos existen
ls datos/

# O especificar directorio correcto
run_data_pipeline.bat --data-dir C:\ruta\correcta
```

---

### Error: Pipeline stops at Step 1

**Síntoma**:
```
[✗] 1. Load Data from CSV Files failed with exit code 1
```

**Solución**:

1. Ver el error específico en la salida de `load_data.py`
2. Revisar validación de campos (puede estar descartando registros)
3. Verificar formato de CSVs
4. Ejecutar solo load_data.py para debug:
   ```bash
   python scripts/data/load_data.py --config Development
   ```

---

### Problema: Pipeline muy lento

**Síntoma**: Pipeline tarda mucho tiempo en ejecutarse.

**Solución**:

1. Aumentar batch size:
   ```bash
   run_data_pipeline.bat --batch-size 500
   ```

2. Usar PostgreSQL en lugar de SQLite (mucho más rápido para grandes volúmenes)

3. Verificar que no hay índices faltantes en la BD

---

### Problema: Stats o Daily vacíos

**Síntoma**: `generate_stats` o `generate_daily` generan 0 registros.

**Causa**: No hay datos en `metricas` table.

**Solución**:

1. Verificar que load_data.py cargó datos:
   ```bash
   flask shell
   >>> from infocodest.models.metricas import Metrica
   >>> print(Metrica.query.count())
   ```

2. Si está vacío, revisar los CSVs y volver a cargar

---

## Integración con Cron/Task Scheduler

### Linux Cron

```bash
# Editar crontab
crontab -e

# Ejecutar pipeline diariamente a las 2 AM
0 2 * * * cd /path/to/project && source venv/bin/activate && ./run_data_pipeline.sh Production >> /var/log/data_pipeline.log 2>&1
```

### Windows Task Scheduler

1. Abrir Task Scheduler
2. Create Task
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
   - Program: `C:\path\to\project\venv\Scripts\python.exe`
   - Arguments: `scripts\data\run_all_data_scripts.py --config Production`
   - Start in: `C:\path\to\project`

---

## Mejores Prácticas

1. **Siempre usar el orquestador** (`run_data_pipeline`) en lugar de scripts individuales
2. **Hacer dry-run primero** en Production antes de ejecutar
3. **Monitorear logs** para detectar validaciones que descartan datos
4. **Usar batch-size adecuado** (100-500 dependiendo del volumen)
5. **Programar ejecuciones** diarias vía cron/scheduler
6. **Verificar registros** después de cada ejecución para auditoría
7. **Backup antes** de ejecutar con `--clear-stats` o `--clear-daily`

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0
