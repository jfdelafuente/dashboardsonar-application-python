# Data Pipeline - User Manual

## Overview

The **Data Pipeline** is an orchestrated system that processes SonarQube data through multiple stages: data loading, daily snapshots, statistics generation, and audit registry creation.

The pipeline consists of:
- **Wrapper Scripts**: `run_data_pipeline.sh` (Linux/Mac) and `run_data_pipeline.bat` (Windows)
- **Orchestrator**: `run_all_data_scripts.py` - Coordinates execution of all data scripts
- **Data Scripts**: Individual Python scripts for each processing stage

## Table of Contents

1. [Quick Start](#quick-start)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Wrapper Scripts](#wrapper-scripts)
4. [Orchestrator](#orchestrator)
5. [Data Scripts](#data-scripts)
6. [Configuration](#configuration)
7. [Common Workflows](#common-workflows)
8. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
9. [Best Practices](#best-practices)

---

## Quick Start

### Basic Execution

**Linux/Mac:**
```bash
./run_data_pipeline.sh
```

**Windows:**
```cmd
run_data_pipeline.bat
```

This runs the complete pipeline with default settings (Development configuration).

### Production Execution

**Linux/Mac:**
```bash
./run_data_pipeline.sh Production
```

**Windows:**
```cmd
run_data_pipeline.bat Production
```

### Check What Would Run (Dry Run)

**Linux/Mac:**
```bash
./run_data_pipeline.sh Development --dry-run
```

**Windows:**
```cmd
run_data_pipeline.bat Development --dry-run
```

---

## Pipeline Architecture

### Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE FLOW                       │
└─────────────────────────────────────────────────────────────┘

1. LOAD DATA (load_data.py)
   ├─ Read CSV files from ./datos directory
   ├─ Load into: metricas, historico, proveedor tables
   └─ Validate and transform data
           │
           ↓
2. GENERATE DAILY (generate_daily.py)
   ├─ Aggregate metrics per application + repo
   ├─ Create daily snapshots
   └─ Load into: daily table
           │
           ↓
3. GENERATE STATS (generate_stats.py)
   ├─ Calculate aggregated statistics per application
   ├─ Count ratings and quality gates
   └─ Load into: stats table
           │
           ↓
4. GENERATE REGISTRY (generate_registro.py)
   ├─ Calculate global statistics
   ├─ Create audit record
   └─ Load into: registros table
```

### Pipeline Components

| Component | Type | Purpose |
|-----------|------|---------|
| `run_data_pipeline.sh` | Bash Script | Linux/Mac wrapper |
| `run_data_pipeline.bat` | Batch Script | Windows wrapper |
| `run_all_data_scripts.py` | Python Orchestrator | Coordinates script execution |
| `load_data.py` | Data Script | Load CSV data into database |
| `generate_daily.py` | Data Script | Generate daily snapshots |
| `generate_stats.py` | Data Script | Generate aggregated statistics |
| `generate_registro.py` | Data Script | Create audit registry |

---

## Wrapper Scripts

### Linux/Mac: `run_data_pipeline.sh`

**Location:** [run_data_pipeline.sh](../../../run_data_pipeline.sh)

**Purpose:**
- Loads environment variables from `.env` file
- Validates virtual environment activation
- Parses configuration and arguments
- Executes the Python orchestrator

**Syntax:**
```bash
./run_data_pipeline.sh [CONFIG] [EXTRA_ARGS...]
```

**Parameters:**
- `CONFIG` - Optional configuration: `Development`, `Testing`, or `Production`
- `EXTRA_ARGS` - Additional arguments passed to orchestrator

**Examples:**
```bash
# Default (Development)
./run_data_pipeline.sh

# Production environment
./run_data_pipeline.sh Production

# Development with stats regeneration
./run_data_pipeline.sh Development --clear-stats

# Custom data directory
./run_data_pipeline.sh --data-dir ./custom_datos

# Production with all options
./run_data_pipeline.sh Production --clear-daily --clear-stats
```

**What It Does:**
1. Checks if virtual environment is activated
2. Loads `.env` file if present
3. Parses configuration argument
4. Constructs Python command
5. Executes `scripts/data/run_all_data_scripts.py`
6. Returns exit code (0 = success, non-zero = failure)

**Environment Variables Loaded:**
- `SQLALCHEMY_DATABASE_URI`
- `SECRET_KEY`
- Any other variables in `.env`

---

### Windows: `run_data_pipeline.bat`

**Location:** [run_data_pipeline.bat](../../../run_data_pipeline.bat)

**Purpose:**
- Windows equivalent of the bash script
- Same functionality, Windows-compatible syntax

**Syntax:**
```cmd
run_data_pipeline.bat [CONFIG] [EXTRA_ARGS...]
```

**Parameters:**
- `CONFIG` - Optional: `Development`, `Testing`, or `Production`
- `EXTRA_ARGS` - Additional arguments passed to orchestrator

**Examples:**
```cmd
REM Default (Development)
run_data_pipeline.bat

REM Production environment
run_data_pipeline.bat Production

REM Development with custom options
run_data_pipeline.bat Development --clear-stats --batch-size 200

REM Custom data directory
run_data_pipeline.bat --data-dir .\custom_datos
```

**Error Handling:**
- Checks virtual environment activation
- Validates `.env` file presence (warning if missing)
- Returns exit code for automation compatibility

---

## Orchestrator

### `run_all_data_scripts.py`

**Location:** [scripts/data/run_all_data_scripts.py](../../../scripts/data/run_all_data_scripts.py)

**Purpose:**
- Orchestrates execution of all data processing scripts
- Manages dependencies between scripts
- Provides comprehensive error handling
- Generates execution summary

### Command-Line Options

```bash
python scripts/data/run_all_data_scripts.py [OPTIONS]
```

#### Configuration Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--config` | Development, Testing, Production | Development | Environment configuration |

#### Data Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--data-dir` | Path | `./datos` | Directory containing CSV files |
| `--date` | YYYY-MM-DD | Today | Date for daily snapshot |
| `--batch-size` | Integer | 100 | Batch size for bulk operations |

#### Control Flags

| Flag | Description |
|------|-------------|
| `--clear-daily` | Clear existing daily records for the date before generating |
| `--clear-stats` | Clear existing stats before regenerating |
| `--skip-load` | Skip data loading step (only run generators) |
| `--skip-daily` | Skip daily generation step |
| `--skip-stats` | Skip stats generation step |
| `--skip-registry` | Skip registry creation step |
| `--dry-run` | Show execution plan without running |

### Usage Examples

#### Full Pipeline with Defaults

```bash
python scripts/data/run_all_data_scripts.py
```

**What Runs:**
1. Load data from `./datos`
2. Generate daily snapshots for today
3. Generate statistics
4. Create registry record

---

#### Production Environment with Regeneration

```bash
python scripts/data/run_all_data_scripts.py \
  --config Production \
  --clear-daily \
  --clear-stats
```

**What Runs:**
1. Clears existing daily records for today
2. Loads data from `./datos`
3. Regenerates daily snapshots
4. Clears all stats
5. Regenerates statistics
6. Creates new registry record

---

#### Skip Data Load (Only Generate)

```bash
python scripts/data/run_all_data_scripts.py --skip-load
```

**Use Case:** Data already loaded, only need to regenerate aggregations

**What Runs:**
1. ~~Load data~~ (skipped)
2. Generate daily snapshots
3. Generate statistics
4. Create registry record

---

#### Custom Data Directory and Date

```bash
python scripts/data/run_all_data_scripts.py \
  --data-dir ./custom_data \
  --date 2025-12-15
```

**What Runs:**
1. Load data from `./custom_data`
2. Generate daily snapshots for 2025-12-15
3. Generate statistics
4. Create registry record for 2025-12-15

---

#### Dry Run (Show Execution Plan)

```bash
python scripts/data/run_all_data_scripts.py --dry-run
```

**Output:**
- Shows what commands would be executed
- Displays configuration
- No actual execution
- Useful for verification

---

### Execution Output

**Example Output:**
```
============================================================================
DATA PIPELINE ORCHESTRATOR
============================================================================

Configuration: Development (default)
Data Directory: ./datos (default)
Date: 2025-12-19 (default)
Batch Size: 100 (default)

[+] Loading environment variables from c:\workspace\dashboardsonar\.env
[+] Environment variables loaded successfully

================================================================================
[*] Step: 1. Load Data from CSV Files
[*] Command: python scripts\data\load_data.py --config Development
================================================================================

Loading data from CSV files...
[OK] Loaded 150 metricas records
[OK] Loaded 89 historico records
[OK] Loaded 25 proveedor records

[✓] 1. Load Data from CSV Files completed successfully (12.34s)

================================================================================
[*] Step: 2. Generate Daily Snapshots
[*] Command: python scripts\data\generate_daily.py --config Development
================================================================================

Extracting daily metrics for 2025-12-19...
Found 25 applications
[OK] Extracted metrics for 150 repositories
[OK] Loaded 150 daily records

[✓] 2. Generate Daily Snapshots completed successfully (8.56s)

================================================================================
[*] Step: 3. Generate Aggregated Statistics
[*] Command: python scripts\data\generate_stats.py --config Development
================================================================================

Extracting statistics from metricas table...
Found 25 applications
[OK] Extracted statistics for 25 applications
[OK] Loaded 25 statistics records

[✓] 3. Generate Aggregated Statistics completed successfully (5.23s)

================================================================================
[*] Step: 4. Create Audit Registry Record
[*] Command: python scripts\data\generate_registro.py --config Development
================================================================================

Calculating global statistics...
  Applications: 25
  Repositories: 150
  Total bugs: 543
  Quality gates OK: 89
  Total analyses: 89
[OK] Registry record created (ID: 15)

[✓] 4. Create Audit Registry Record completed successfully (2.11s)

================================================================================
EXECUTION SUMMARY
================================================================================

Total Duration: 28.24s
Steps Executed: 4

Results:
  ✓ Successful: 4

Details:
  [✓] 1. Load Data from CSV Files                  (12.34s)
  [✓] 2. Generate Daily Snapshots                  (8.56s)
  [✓] 3. Generate Aggregated Statistics            (5.23s)
  [✓] 4. Create Audit Registry Record              (2.11s)

================================================================================

[✓] Pipeline completed successfully
```

---

### Error Handling

**Dependency Management:**
- Scripts execute in sequence
- If a script fails, subsequent steps are skipped
- Exit code reflects success/failure

**Example with Error:**
```
================================================================================
[*] Step: 1. Load Data from CSV Files
================================================================================

[✗] Error: CSV file not found: ./datos/metricas.csv

[✗] 1. Load Data from CSV Files failed with exit code 1

[SKIP] 2. Generate Daily Snapshots skipped (previous step failed)
[SKIP] 3. Generate Aggregated Statistics skipped (previous step failed)
[SKIP] 4. Create Audit Registry Record skipped (previous step failed)

Results:
  ✗ Failed:     1
  - Skipped:    3

[✗] Pipeline completed with errors
```

---

## Data Scripts

### 1. `load_data.py` - Data Loader

**Location:** [scripts/data/load_data.py](../../../scripts/data/load_data.py)

**Purpose:**
- Loads CSV files into database tables
- Handles: metricas, historico, proveedor

**Usage:**
```bash
python scripts/data/load_data.py [OPTIONS]
```

**Options:**
- `--config CONFIG` - Environment: Development, Testing, Production
- `--data-dir PATH` - CSV directory (default: `./datos`)
- `--batch-size N` - Batch size for inserts (default: 100)

**CSV Files Expected:**
- `metricas.csv` - Application metrics
- `historico.csv` - Historical quality gate data
- `proveedor.csv` - Provider/vendor information

**Example:**
```bash
# Load from default directory
python scripts/data/load_data.py

# Load from custom directory
python scripts/data/load_data.py --data-dir ./imports/2025-12-15

# Production with larger batches
python scripts/data/load_data.py --config Production --batch-size 500
```

**Output:**
```
============================================================
Data Loading Script
============================================================
Configuration: Development
Data directory: ./datos
Batch size: 100
============================================================

Loading metricas from ./datos/metricas.csv...
[OK] Loaded 150 metricas records

Loading historico from ./datos/historico.csv...
[OK] Loaded 89 historico records

Loading proveedor from ./datos/proveedor.csv...
[OK] Loaded 25 proveedor records

============================================================
Data Loading Summary
============================================================
Metricas:    150 records
Historico:   89 records
Proveedor:   25 records
Total:       264 records
Duration:    12.34 seconds
============================================================

[OK] Data loading completed successfully!
```

---

### 2. `generate_daily.py` - Daily Snapshots

**Location:** [scripts/data/generate_daily.py](../../../scripts/data/generate_daily.py)

**Purpose:**
- Generates daily snapshots of aggregated metrics
- Creates time-series data for trend analysis

**Usage:**
```bash
python scripts/data/generate_daily.py [OPTIONS]
```

**Options:**
- `--config CONFIG` - Environment configuration
- `--date YYYY-MM-DD` - Snapshot date (default: today)
- `--clear-date` - Clear existing records for the date before generating
- `--batch-size N` - Batch size (default: 100)

**What It Does:**
1. Aggregates metrics per application + repository
2. Calculates: bugs, vulnerabilities, code smells, quality gates, analyses
3. Loads into `daily` table

**Example:**
```bash
# Generate for today
python scripts/data/generate_daily.py

# Generate for specific date
python scripts/data/generate_daily.py --date 2025-12-15

# Regenerate today's snapshot
python scripts/data/generate_daily.py --clear-date

# Production environment
python scripts/data/generate_daily.py --config Production
```

**Output:**
```
============================================================
Daily Metrics Generation Script
============================================================
Configuration: Development
Snapshot date: 2025-12-19
Clear existing: False
Batch size: 100
============================================================

Extracting daily metrics for 2025-12-19...
Found 25 applications
  Processing application 1/25: abacusbrmosp
  Processing application 2/25: adminpanelbi
  ...
[OK] Extracted metrics for 150 repositories across 25 applications

Loading 150 daily records...
  Progress: 100/150 (66.7%)
  Progress: 150/150 (100.0%)
[OK] Loaded 150 daily records

============================================================
Daily Metrics Generation Summary
============================================================
Snapshot date: 2025-12-19
Records generated: 150
Duration: 8.56 seconds
============================================================

[OK] Daily metrics generation completed successfully!
```

**Database Impact:**
- **Table:** `daily`
- **Records Created:** One per application + repository combination
- **Storage:** Accumulates over time (one snapshot per day)

---

### 3. `generate_stats.py` - Statistics Generator

**Location:** [scripts/data/generate_stats.py](../../../scripts/data/generate_stats.py)

**Purpose:**
- Generates aggregated statistics per application
- Counts ratings and quality gates

**Usage:**
```bash
python scripts/data/generate_stats.py [OPTIONS]
```

**Options:**
- `--config CONFIG` - Environment configuration
- `--clear` - Clear existing stats before regenerating
- `--batch-size N` - Batch size (default: 100)

**What It Calculates:**
- Number of repositories per application
- Count of "A" ratings for:
  - Reliability
  - Maintainability (SQALE)
  - Security
  - Documentation (DLOC)
  - Coverage
- Count of "OK" quality gates

**Example:**
```bash
# Generate stats (append)
python scripts/data/generate_stats.py

# Regenerate all stats
python scripts/data/generate_stats.py --clear

# Production environment
python scripts/data/generate_stats.py --config Production --clear
```

**Output:**
```
============================================================
Statistics Generation Script
============================================================
Configuration: Development
Clear existing: True
Batch size: 100
============================================================

Clearing existing statistics...
[OK] Deleted 25 existing records

Extracting statistics from metricas table...
Found 25 applications
  Processing 1/25: abacusbrmosp
  Processing 2/25: adminpanelbi
  ...
[OK] Extracted statistics for 25 applications

Transforming statistics...
[OK] Statistics transformed

Loading 25 statistics records...
  Progress: 25/25 (100.0%)
[OK] Loaded 25 statistics records

============================================================
Statistics Generation Summary
============================================================
Records generated: 25
Duration: 5.23 seconds
============================================================

[OK] Statistics generation completed successfully!
```

**Database Impact:**
- **Table:** `stats`
- **Records Created:** One per application
- **Clear Flag:** `--clear` deletes all existing stats before regenerating

---

### 4. `generate_registro.py` - Audit Registry

**Location:** [scripts/data/generate_registro.py](../../../scripts/data/generate_registro.py)

**Purpose:**
- Creates audit log of pipeline execution
- Records global statistics for monitoring

**Usage:**
```bash
python scripts/data/generate_registro.py [OPTIONS]
```

**Options:**
- `--config CONFIG` - Environment configuration
- `--process-name NAME` - Custom process name (default: "Registro informe Sonar")
- `--date YYYY-MM-DD` - Registry date (default: today)

**What It Records:**
- Process name and timestamp
- Number of applications
- Number of repositories
- Total bugs
- Quality gates OK
- Total analyses

**Example:**
```bash
# Default registry
python scripts/data/generate_registro.py

# Custom process name
python scripts/data/generate_registro.py --process-name "Daily Load 2025-12-19"

# Production with custom date
python scripts/data/generate_registro.py --config Production --date 2025-12-15

# Pipeline orchestrator uses custom name with timestamp
python scripts/data/generate_registro.py \
  --process-name "Data Pipeline - 2025-12-19 10:30:00"
```

**Output:**
```
============================================================
Process Registry Generation Script
============================================================
Configuration: Development
Process: Data Pipeline - 2025-12-19 10:35:22
Date: 2025-12-19
============================================================

Calculating global statistics...
  Applications: 25
  Repositories: 150
  Total bugs: 543
  Quality gates OK: 89
  Total analyses: 89
[OK] Global statistics calculated

Creating registry record for 'Data Pipeline - 2025-12-19 10:35:22'...
[OK] Registry record created (ID: 15)

============================================================
Registry Record Summary
============================================================
Process: Data Pipeline - 2025-12-19 10:35:22
Date: 2025-12-19
------------------------------------------------------------
Applications:         25
Repositories:        150
Total Bugs:          543
Quality OK:           89
Total Analyses:       89
============================================================

Duration: 2.11 seconds

[OK] Registry record created successfully!
```

**Database Impact:**
- **Table:** `registros`
- **Records Created:** One per execution
- **Use Case:** Track pipeline runs, monitor system health over time

---

## Configuration

### Environment Selection

The pipeline supports three environments:

| Environment | Purpose | Database |
|-------------|---------|----------|
| **Development** | Local development | SQLite or local PostgreSQL |
| **Testing** | Automated tests | In-memory or test database |
| **Production** | Production deployment | Production PostgreSQL/MySQL |

**Configuration Files:**
- `config.py` - Configuration classes
- `.env` - Environment variables

### Configuration via `.env` File

**Example `.env`:**
```env
# Database Configuration
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost:5432/dashboardsonar

# Application Settings
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Data Pipeline Settings
DEFAULT_BATCH_SIZE=100
DEFAULT_DATA_DIR=./datos
```

### Override Configuration

**Via Command Line:**
```bash
# Use Production configuration
./run_data_pipeline.sh Production

# Use custom data directory (overrides .env)
./run_data_pipeline.sh --data-dir ./custom_data

# Use custom batch size (overrides .env)
./run_data_pipeline.sh --batch-size 500
```

**Via Environment Variables:**
```bash
# Set environment variable
export SQLALCHEMY_DATABASE_URI="postgresql://prod_user:pass@prod-server/db"

# Run pipeline (uses environment variable)
./run_data_pipeline.sh Production
```

**Priority Order** (highest to lowest):
1. Command-line arguments
2. Environment variables
3. `.env` file
4. Default values in code

---

## Common Workflows

### Workflow 1: Daily Automated Execution

**Use Case:** Scheduled daily data processing

**Cron Job (Linux/Mac):**
```bash
# Edit crontab
crontab -e

# Add daily execution at 2 AM
0 2 * * * cd /path/to/dashboard && ./run_data_pipeline.sh Production >> /var/log/dashboard-pipeline.log 2>&1
```

**Windows Task Scheduler:**
```cmd
REM Create scheduled task
schtasks /create /tn "Dashboard Pipeline" /tr "C:\dashboard\run_data_pipeline.bat Production" /sc daily /st 02:00
```

**Script:**
```bash
#!/bin/bash
# daily_pipeline.sh

cd /path/to/dashboard
source venv/bin/activate
./run_data_pipeline.sh Production --clear-daily --clear-stats

# Email on failure
if [ $? -ne 0 ]; then
    echo "Pipeline failed on $(date)" | mail -s "Pipeline Error" admin@example.com
fi
```

---

### Workflow 2: Manual Data Load with Custom Date

**Use Case:** Load historical data for a specific date

**Steps:**
```bash
# 1. Prepare CSV files in custom directory
mkdir -p ./imports/2025-12-15
# Copy CSV files to ./imports/2025-12-15

# 2. Run pipeline with custom date and directory
python scripts/data/run_all_data_scripts.py \
  --data-dir ./imports/2025-12-15 \
  --date 2025-12-15 \
  --config Production

# 3. Verify data loaded correctly
python manage.py db-status
```

---

### Workflow 3: Regenerate Statistics Only

**Use Case:** Recalculate stats without reloading data

**Steps:**
```bash
# Skip data load, only regenerate aggregations
python scripts/data/run_all_data_scripts.py \
  --skip-load \
  --clear-daily \
  --clear-stats
```

**What Happens:**
1. ~~Load data~~ (skipped)
2. Regenerate daily snapshots (clears + generates)
3. Regenerate statistics (clears + generates)
4. Create new registry record

---

### Workflow 4: Development Testing

**Use Case:** Test pipeline changes during development

**Steps:**
```bash
# 1. Create test data directory
mkdir -p ./test_data
# Add small CSV samples

# 2. Dry run to check execution plan
python scripts/data/run_all_data_scripts.py \
  --data-dir ./test_data \
  --dry-run

# 3. Execute with test data
python scripts/data/run_all_data_scripts.py \
  --data-dir ./test_data \
  --config Development

# 4. Verify results
python manage.py shell
>>> from infocodest.models.daily import Daily
>>> Daily.query.count()
150
```

---

### Workflow 5: Production Deployment

**Use Case:** First-time production data load

**Steps:**
```bash
# 1. Backup existing database
pg_dump -h localhost -U user dashboardsonar > backup_$(date +%Y%m%d).sql

# 2. Prepare production CSV files
ls -lh ./datos/
# Verify all CSV files present

# 3. Test with dry run
./run_data_pipeline.sh Production --dry-run

# 4. Execute production load
./run_data_pipeline.sh Production --clear-daily --clear-stats

# 5. Verify success
if [ $? -eq 0 ]; then
    echo "Production load successful"
else
    echo "Production load failed - check logs"
    # Restore backup if needed
fi

# 6. Monitor registry records
python manage.py shell
>>> from infocodest.models.registros import Registro
>>> Registro.query.order_by(Registro.created_on.desc()).first()
```

---

## Monitoring and Troubleshooting

### Monitoring Pipeline Execution

#### 1. Check Registry Records

**Via Python Shell:**
```python
python manage.py shell

>>> from infocodest.models.registros import Registro
>>> latest = Registro.query.order_by(Registro.created_on.desc()).first()
>>> print(f"Last run: {latest.proceso} on {latest.created_on}")
>>> print(f"Apps: {latest.num_app}, Repos: {latest.num_repo}")
>>> print(f"Bugs: {latest.num_bugs}, Quality OK: {latest.num_quality}")
```

#### 2. Review Execution Logs

**Redirect output to log file:**
```bash
./run_data_pipeline.sh Production 2>&1 | tee pipeline_$(date +%Y%m%d).log
```

**Check log for errors:**
```bash
grep -i "error\|failed\|✗" pipeline_20251219.log
```

#### 3. Monitor Database Growth

**Check table sizes:**
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

### Common Issues and Solutions

#### Issue 1: CSV File Not Found

**Error:**
```
[ERROR] CSV file not found: ./datos/metricas.csv
```

**Solutions:**
1. Check file exists:
   ```bash
   ls -lh ./datos/
   ```

2. Verify file name (case-sensitive on Linux):
   ```bash
   # Should be exactly: metricas.csv, historico.csv, proveedor.csv
   ```

3. Use absolute path:
   ```bash
   python scripts/data/load_data.py --data-dir /full/path/to/datos
   ```

---

#### Issue 2: Virtual Environment Not Activated

**Error:**
```
[!] Error: Virtual environment is not activated
[!] Please activate it first:
[!]   venv\Scripts\activate
```

**Solution:**
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Then run pipeline
./run_data_pipeline.sh
```

---

#### Issue 3: Database Connection Failed

**Error:**
```
[ERROR] Database connection failed
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. **Check database server:**
   ```bash
   # PostgreSQL
   sudo systemctl status postgresql

   # MySQL
   sudo systemctl status mysql
   ```

2. **Verify connection string in `.env`:**
   ```env
   SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost:5432/dbname
   ```

3. **Test connection manually:**
   ```bash
   psql -h localhost -U user -d dbname
   ```

4. **Check database exists:**
   ```sql
   -- PostgreSQL
   \l

   -- MySQL
   SHOW DATABASES;
   ```

---

#### Issue 4: Duplicate Key Error

**Error:**
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint
```

**Cause:** Trying to insert data that already exists (unique constraint violation)

**Solutions:**

1. **Clear existing data for the date:**
   ```bash
   python scripts/data/generate_daily.py --clear-date
   ```

2. **Regenerate stats (clears first):**
   ```bash
   python scripts/data/generate_stats.py --clear
   ```

3. **Manual cleanup via SQL:**
   ```sql
   -- Delete daily records for specific date
   DELETE FROM daily WHERE created_on = '2025-12-19';

   -- Delete all stats
   DELETE FROM stats;
   ```

---

#### Issue 5: Out of Memory

**Error:**
```
MemoryError: Unable to allocate array
```

**Cause:** Processing very large CSV files with default batch size

**Solution:**
```bash
# Reduce batch size
python scripts/data/load_data.py --batch-size 50

# Or use orchestrator with smaller batches
./run_data_pipeline.sh --batch-size 50
```

---

#### Issue 6: Pipeline Stops After First Failure

**Behavior:** If step 1 fails, steps 2-4 are skipped

**Explanation:** This is **by design** - scripts have dependencies

**Solutions:**

1. **Fix the failing step first:**
   ```bash
   # Run individual script to see detailed error
   python scripts/data/load_data.py
   ```

2. **Skip failing step if data already loaded:**
   ```bash
   # Skip data load, run generators only
   ./run_data_pipeline.sh --skip-load
   ```

3. **Run individual scripts:**
   ```bash
   # Run each script manually for troubleshooting
   python scripts/data/generate_daily.py
   python scripts/data/generate_stats.py
   python scripts/data/generate_registro.py
   ```

---

#### Issue 7: Permission Denied on Script Execution

**Error (Linux/Mac):**
```
bash: ./run_data_pipeline.sh: Permission denied
```

**Solution:**
```bash
# Make script executable
chmod +x run_data_pipeline.sh

# Then run
./run_data_pipeline.sh
```

---

### Debugging Individual Scripts

**Run with Python directly to see full traceback:**
```bash
python scripts/data/load_data.py
python scripts/data/generate_daily.py
python scripts/data/generate_stats.py
python scripts/data/generate_registro.py
```

**Check script help:**
```bash
python scripts/data/load_data.py --help
python scripts/data/generate_daily.py --help
python scripts/data/generate_stats.py --help
python scripts/data/generate_registro.py --help
```

**Interactive debugging:**
```bash
# Add breakpoint in script
import pdb; pdb.set_trace()

# Run script
python scripts/data/load_data.py
```

---

## Best Practices

### 1. Scheduled Execution

**Use cron/Task Scheduler for automated daily runs:**
```bash
# Good: Automated daily at consistent time
0 2 * * * cd /path/to/dashboard && ./run_data_pipeline.sh Production

# Bad: Manual execution (easy to forget)
```

---

### 2. Clear Flags for Regeneration

**Use `--clear-*` flags when regenerating:**
```bash
# Good: Clear before regenerating to avoid duplicates
./run_data_pipeline.sh Production --clear-daily --clear-stats

# Bad: Append mode might create duplicates for daily snapshots
./run_data_pipeline.sh Production
```

---

### 3. Backup Before Production Runs

**Always backup production database:**
```bash
#!/bin/bash
# Pre-pipeline backup script

# Backup database
pg_dump -h localhost -U user dashboardsonar > backup_$(date +%Y%m%d_%H%M%S).sql

# Run pipeline
./run_data_pipeline.sh Production --clear-daily --clear-stats

# On success, clean old backups (keep last 7 days)
if [ $? -eq 0 ]; then
    find . -name "backup_*.sql" -mtime +7 -delete
fi
```

---

### 4. Log All Production Executions

**Redirect output to timestamped log files:**
```bash
# Good: Logs for debugging
./run_data_pipeline.sh Production 2>&1 | tee logs/pipeline_$(date +%Y%m%d_%H%M%S).log

# Bad: No logs (can't debug failures)
./run_data_pipeline.sh Production
```

---

### 5. Monitor Registry Records

**Regularly check pipeline execution history:**
```python
# Check last 7 days of pipeline runs
from infocodest.models.registros import Registro
from datetime import datetime, timedelta

seven_days_ago = datetime.now() - timedelta(days=7)
recent_runs = Registro.query.filter(
    Registro.created_on >= seven_days_ago
).order_by(Registro.created_on.desc()).all()

for run in recent_runs:
    print(f"{run.created_on}: {run.num_app} apps, {run.num_bugs} bugs")
```

---

### 6. Dry Run Before Production

**Always test with `--dry-run` first:**
```bash
# Step 1: Dry run to verify command
./run_data_pipeline.sh Production --clear-daily --dry-run

# Step 2: Execute after verification
./run_data_pipeline.sh Production --clear-daily
```

---

### 7. Use Appropriate Batch Sizes

**Tune batch size based on data volume and memory:**

| Data Volume | Recommended Batch Size |
|-------------|------------------------|
| < 1,000 records | 100 (default) |
| 1,000 - 10,000 | 200-500 |
| 10,000 - 100,000 | 500-1,000 |
| > 100,000 | 1,000-5,000 |

**Example:**
```bash
# Small dataset (default)
./run_data_pipeline.sh --batch-size 100

# Large dataset
./run_data_pipeline.sh --batch-size 1000
```

---

### 8. Environment-Specific Execution

**Never use Development config in Production:**
```bash
# Good: Explicit Production config
./run_data_pipeline.sh Production

# Bad: Default config in production server
./run_data_pipeline.sh  # Uses Development by default!
```

---

### 9. Data Validation

**Validate CSV files before loading:**
```bash
# Check CSV structure
head -5 datos/metricas.csv
head -5 datos/historico.csv
head -5 datos/proveedor.csv

# Check for special characters
file datos/*.csv

# Verify encoding (should be UTF-8)
file -i datos/*.csv
```

---

### 10. Exit Code Checking in Automation

**Check exit codes for automation scripts:**
```bash
#!/bin/bash
# automation_script.sh

./run_data_pipeline.sh Production

if [ $? -eq 0 ]; then
    echo "Pipeline SUCCESS - $(date)" >> /var/log/pipeline_success.log
    # Send success notification
else
    echo "Pipeline FAILED - $(date)" >> /var/log/pipeline_error.log
    # Send alert email
    echo "Pipeline failed on $(date)" | mail -s "ALERT: Pipeline Failed" admin@example.com
fi
```

---

## Performance Optimization

### Batch Size Tuning

**Increase batch size for faster execution:**
```bash
# Default (100 records per batch)
./run_data_pipeline.sh

# Optimized (500 records per batch)
./run_data_pipeline.sh --batch-size 500
```

**Benchmark:**
```bash
# Test different batch sizes
time ./run_data_pipeline.sh --batch-size 100
time ./run_data_pipeline.sh --batch-size 500
time ./run_data_pipeline.sh --batch-size 1000
```

---

### Skip Unnecessary Steps

**Skip steps that aren't needed:**
```bash
# Data already loaded, only regenerate aggregations
./run_data_pipeline.sh --skip-load --clear-daily --clear-stats
```

---

### Parallel Execution (Advanced)

**Run independent scripts in parallel:**
```bash
# NOT RECOMMENDED without dependency management
# Stats depend on daily, which depends on data load

# Only safe for independent regenerations
python scripts/data/generate_daily.py --clear-date &
python scripts/data/generate_stats.py --clear &
wait
```

---

## Integration with CI/CD

### GitLab CI Example

```yaml
# .gitlab-ci.yml

stages:
  - test
  - deploy

test_pipeline:
  stage: test
  script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install -r requirements.txt
    - python scripts/data/run_all_data_scripts.py --config Testing --dry-run
  only:
    - merge_requests

deploy_production:
  stage: deploy
  script:
    - source venv/bin/activate
    - ./run_data_pipeline.sh Production --clear-daily --clear-stats
  only:
    - main
  when: manual
```

---

### GitHub Actions Example

```yaml
# .github/workflows/pipeline.yml

name: Data Pipeline

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt

      - name: Run Pipeline
        env:
          SQLALCHEMY_DATABASE_URI: ${{ secrets.DATABASE_URI }}
        run: |
          source venv/bin/activate
          ./run_data_pipeline.sh Production --clear-daily --clear-stats

      - name: Notify on failure
        if: failure()
        run: echo "Pipeline failed" | mail -s "Pipeline Error" admin@example.com
```

---

## Additional Resources

### Related Documentation

- **manage.py Manual**: [MANAGE_PY_MANUAL.md](MANAGE_PY_MANUAL.md)
- **Database Schema**: [DATABASE_SCHEMA.md](../architecture/DATABASE_SCHEMA.md)
- **Daily Model**: [infocodest/models/daily.py](../../../infocodest/models/daily.py)
- **Stats Model**: [infocodest/models/stat.py](../../../infocodest/models/stat.py)

### Source Code Reference

- **Orchestrator**: [scripts/data/run_all_data_scripts.py](../../../scripts/data/run_all_data_scripts.py)
- **Bash Wrapper**: [run_data_pipeline.sh](../../../run_data_pipeline.sh)
- **Windows Wrapper**: [run_data_pipeline.bat](../../../run_data_pipeline.bat)
- **Data Scripts**: [scripts/data/](../../../scripts/data/)

### Database Tables

| Table | Purpose | Created By |
|-------|---------|------------|
| `metricas` | Application metrics | load_data.py |
| `historico` | Historical quality data | load_data.py |
| `proveedor` | Provider information | load_data.py |
| `daily` | Daily aggregated snapshots | generate_daily.py |
| `stats` | Application statistics | generate_stats.py |
| `registros` | Audit registry | generate_registro.py |

---

## Summary

The Data Pipeline is a robust system for processing SonarQube data through multiple stages:

**Key Features:**
- Automated orchestration with error handling
- Configurable execution (skip steps, clear data, custom dates)
- Cross-platform support (Linux/Mac/Windows)
- Comprehensive logging and monitoring
- Batch processing for large datasets

**Execution Methods:**
1. **Wrapper Scripts**: `./run_data_pipeline.sh` or `run_data_pipeline.bat`
2. **Orchestrator**: `python scripts/data/run_all_data_scripts.py`
3. **Individual Scripts**: Run data scripts separately

**Best Practices:**
- Use `--dry-run` before production runs
- Always backup database before production execution
- Log all executions for debugging
- Monitor registry records for pipeline health
- Use appropriate batch sizes for performance

For quick help:
```bash
# Wrapper help
./run_data_pipeline.sh --help

# Orchestrator help
python scripts/data/run_all_data_scripts.py --help

# Individual script help
python scripts/data/load_data.py --help
```

---

**Last Updated**: 2025-12-19
**Version**: 1.11.0
**Author**: Dashboard Sonar Team
