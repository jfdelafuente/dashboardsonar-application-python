# Backup & Restore Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, Database Administrators
**Criticidad**: 🔴 CRÍTICO - Protección de datos

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Estrategia de Backup](#estrategia-de-backup)
3. [Backup de PostgreSQL](#backup-de-postgresql)
4. [Backup de SQLite](#backup-de-sqlite)
5. [Backup de Archivos](#backup-de-archivos)
6. [Restore Procedures](#restore-procedures)
7. [Disaster Recovery](#disaster-recovery)
8. [Testing](#testing)
9. [Automatización](#automatización)

---

## 🎯 Introducción

### ¿Por qué Backups?

Los backups son **críticos** para proteger contra:

- 🔥 **Corrupción de datos**: Bug en código que modifica/elimina datos
- 💣 **Errores humanos**: `DROP TABLE` accidental, `DELETE` sin `WHERE`
- 🌪️ **Desastres**: Fallo de hardware, incendio en datacenter
- 🦠 **Ataques**: Ransomware, SQL injection maliciosa
- 🔄 **Migraciones fallidas**: Rollback de schema changes

**Objetivo**: Poder restaurar datos a cualquier punto en el tiempo (PITR - Point-In-Time Recovery).

---

### Objetivos de Backup

| Métrica | Definición | Objetivo Dashboard Sonar |
|---------|------------|--------------------------|
| **RPO** | Recovery Point Objective - Datos que puedes perder | 24 horas |
| **RTO** | Recovery Time Objective - Tiempo para recuperar | 2 horas |
| **Retention** | Tiempo que guardas backups | 30 días |

**Ejemplo**: Si el backup es a las 2 AM y la BD se corrompe a las 5 PM:
- **RPO 24h**: Pierdes datos del día actual (volver a backup de 2 AM)
- **RTO 2h**: Sistema restaurado a las 7 PM

---

## 📦 Estrategia de Backup

### Tipos de Backup

| Tipo | Descripción | Frecuencia | Tamaño | Velocidad Restore |
|------|-------------|------------|--------|-------------------|
| **Full Backup** | Backup completo de toda la BD | Diario (2 AM) | Grande (~500MB) | Rápido (5 min) |
| **Incremental** | Solo cambios desde último backup | Cada 6 horas | Pequeño (~50MB) | Medio (15 min) |
| **Transaction Logs** | WAL logs para PITR | Continuo | Muy pequeño | Lento (30 min) |

**Estrategia recomendada**:
```
┌─────────────────────────────────────────────┐
│ Full Backup Diario (2 AM)                   │
│   +                                         │
│   └─> Incremental cada 6 horas (8 AM, 2 PM, 8 PM) │
│   +                                         │
│   └─> WAL archiving continuo (cada commit) │
└─────────────────────────────────────────────┘
```

---

### Ubicaciones de Backup

**Regla 3-2-1**:
- **3** copias de datos (1 producción + 2 backups)
- **2** tipos de media diferentes (disco local + cloud)
- **1** copia off-site (S3, Azure Blob)

**Implementación**:
```
┌────────────────┐
│  PostgreSQL    │
│  (Producción)  │
└────────┬───────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
    ┌─────────┐       ┌─────────┐
    │ Disco   │       │  AWS S3 │
    │ Local   │ sync  │ (Off-site)
    │ /backups│──────>│ Encrypted│
    └─────────┘       └─────────┘

    Retention:        Retention:
    7 días           30 días
```

---

## 🐘 Backup de PostgreSQL

### Método 1: pg_dump (Logical Backup)

**Características**:
- ✅ Portátil (funciona en cualquier versión PostgreSQL)
- ✅ Backup selectivo (tables, schemas)
- ❌ Requiere parar/slow down la app durante backup grande
- ❌ No soporta PITR

---

#### Full Backup con pg_dump

**Script básico**:
```bash
#!/bin/bash
# backup_postgresql.sh

# Variables
DB_NAME="dashboardsonar"
DB_USER="dashboard_user"
DB_HOST="localhost"
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dashboardsonar_$DATE.sql"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Ejecutar pg_dump
echo "Iniciando backup de PostgreSQL..."
pg_dump -h $DB_HOST \
        -U $DB_USER \
        -d $DB_NAME \
        -F c \
        -b \
        -v \
        -f $BACKUP_FILE

# Verificar que el backup fue exitoso
if [ $? -eq 0 ]; then
    echo "✅ Backup completado: $BACKUP_FILE"

    # Comprimir
    gzip $BACKUP_FILE
    echo "✅ Comprimido: $BACKUP_FILE.gz"

    # Calcular tamaño
    SIZE=$(du -h $BACKUP_FILE.gz | cut -f1)
    echo "📦 Tamaño: $SIZE"
else
    echo "❌ ERROR: Backup falló"
    exit 1
fi

# Limpiar backups antiguos (>7 días)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
echo "🧹 Backups antiguos eliminados"
```

**Parámetros importantes**:
- `-F c`: Formato custom (comprimido, optimizado para pg_restore)
- `-b`: Incluir large objects (BLOBs)
- `-v`: Verbose (mostrar progreso)
- `--exclude-table-data=logs`: Excluir datos de tabla logs (solo schema)

---

#### Backup Solo Schema (para testing)

```bash
pg_dump -h localhost \
        -U dashboard_user \
        -d dashboardsonar \
        --schema-only \
        -f schema_only.sql
```

---

#### Backup Solo Datos (sin schema)

```bash
pg_dump -h localhost \
        -U dashboard_user \
        -d dashboardsonar \
        --data-only \
        -F c \
        -f data_only.backup
```

---

### Método 2: pg_basebackup (Physical Backup)

**Características**:
- ✅ Muy rápido (copia archivos binarios)
- ✅ Soporta PITR con WAL archiving
- ✅ No requiere downtime
- ❌ Requiere más espacio (copia todo el cluster)
- ❌ Dependiente de versión PostgreSQL

---

#### Configuración para pg_basebackup

**PASO 1**: Configurar PostgreSQL para replicación

```bash
# Editar postgresql.conf
sudo nano /etc/postgresql/13/main/postgresql.conf

# Agregar:
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backups/wal_archive/%f && cp %p /backups/wal_archive/%f'
max_wal_senders = 3
```

**PASO 2**: Configurar autenticación

```bash
# Editar pg_hba.conf
sudo nano /etc/postgresql/13/main/pg_hba.conf

# Agregar:
host    replication     dashboard_user    127.0.0.1/32    md5
```

**PASO 3**: Reiniciar PostgreSQL

```bash
sudo systemctl restart postgresql
```

---

#### Ejecutar pg_basebackup

```bash
#!/bin/bash
# basebackup_postgresql.sh

BACKUP_DIR="/backups/postgresql_base"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/base_$DATE"

# Crear directorio WAL archive si no existe
mkdir -p /backups/wal_archive

# Ejecutar pg_basebackup
pg_basebackup -h localhost \
              -U dashboard_user \
              -D $BACKUP_PATH \
              -Ft \
              -z \
              -P \
              -X stream

if [ $? -eq 0 ]; then
    echo "✅ Base backup completado: $BACKUP_PATH"
else
    echo "❌ ERROR: Base backup falló"
    exit 1
fi
```

**Parámetros**:
- `-D`: Directorio destino
- `-Ft`: Formato tar
- `-z`: Comprimir con gzip
- `-P`: Mostrar progreso
- `-X stream`: Incluir WAL logs necesarios para consistencia

---

### Método 3: WAL Archiving (Continuous Backup)

**Objetivo**: Permitir PITR (restaurar a cualquier momento).

**Configuración**:
```bash
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backups/wal_archive/%f && cp %p /backups/wal_archive/%f'
archive_timeout = 300  # Forzar WAL switch cada 5 min
```

**Verificar WAL archiving**:
```sql
-- Ver última transacción archivada
SELECT pg_current_wal_lsn();

-- Ver archivos WAL en archive
SELECT * FROM pg_stat_archiver;
```

---

### Backup Encriptado (Para Datos Sensibles)

```bash
#!/bin/bash
# backup_postgresql_encrypted.sh

DB_NAME="dashboardsonar"
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dashboardsonar_$DATE.sql.gz.gpg"
GPG_KEY="backups@empresa.com"

# Backup + Comprimir + Encriptar en un solo pipeline
pg_dump -h localhost -U dashboard_user -d $DB_NAME -F c | \
  gzip | \
  gpg --encrypt --recipient $GPG_KEY --output $BACKUP_FILE

echo "✅ Backup encriptado: $BACKUP_FILE"
```

**Restore encriptado**:
```bash
gpg --decrypt dashboardsonar_20251217.sql.gz.gpg | \
  gunzip | \
  pg_restore -h localhost -U dashboard_user -d dashboardsonar
```

---

## 💾 Backup de SQLite

**Cuándo usar**: Entorno de desarrollo o testing.

### Método 1: Copia de Archivo

```bash
#!/bin/bash
# backup_sqlite.sh

DB_FILE="/path/to/dashboardsonar.db"
BACKUP_DIR="/backups/sqlite"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dashboardsonar_$DATE.db"

mkdir -p $BACKUP_DIR

# Copia con verificación de integridad
sqlite3 $DB_FILE ".backup '$BACKUP_FILE'"

if [ $? -eq 0 ]; then
    echo "✅ Backup SQLite completado: $BACKUP_FILE"
    gzip $BACKUP_FILE
else
    echo "❌ ERROR: Backup falló"
    exit 1
fi
```

---

### Método 2: Dump SQL

```bash
#!/bin/bash
# dump_sqlite.sh

DB_FILE="/path/to/dashboardsonar.db"
BACKUP_DIR="/backups/sqlite"
DATE=$(date +%Y%m%d_%H%M%S)
DUMP_FILE="$BACKUP_DIR/dashboardsonar_$DATE.sql"

# Dump a SQL text
sqlite3 $DB_FILE .dump > $DUMP_FILE

gzip $DUMP_FILE
echo "✅ SQLite dump completado: $DUMP_FILE.gz"
```

---

## 📁 Backup de Archivos

### Archivos a Incluir en Backup

```
/path/to/dashboardsonar/
├── .env                     # ⚠️ CRÍTICO - Configuración
├── instance/                # Archivos de instancia (si existen)
├── logs/                    # Logs (opcional, para auditoría)
└── uploads/                 # Archivos subidos por usuarios (si existen)
```

---

### Script de Backup de Archivos

```bash
#!/bin/bash
# backup_files.sh

APP_DIR="/path/to/dashboardsonar"
BACKUP_DIR="/backups/files"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/files_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# Crear tar con archivos críticos
tar -czf $BACKUP_FILE \
    -C $APP_DIR \
    .env \
    instance \
    uploads 2>/dev/null  # Ignorar errores si no existen

if [ $? -eq 0 ] || [ $? -eq 1 ]; then  # tar retorna 1 si algunos archivos no existen
    echo "✅ Backup de archivos completado: $BACKUP_FILE"
    SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "📦 Tamaño: $SIZE"
else
    echo "❌ ERROR: Backup falló"
    exit 1
fi

# Limpiar backups antiguos
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

---

## ⏪ Restore Procedures

### Restore PostgreSQL desde pg_dump

#### Escenario 1: Restore Completo (Drop & Recreate)

```bash
#!/bin/bash
# restore_postgresql_full.sh

BACKUP_FILE="/backups/postgresql/dashboardsonar_20251217.sql.gz"
DB_NAME="dashboardsonar"
DB_USER="dashboard_user"

# ⚠️ ADVERTENCIA: Esto ELIMINARÁ la base de datos actual
read -p "⚠️ Esto BORRARÁ la BD actual. Continuar? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Restore cancelado"
    exit 1
fi

# Paso 1: Detener aplicación
echo "🛑 Deteniendo aplicación..."
sudo systemctl stop dashboardsonar

# Paso 2: Drop base de datos existente
echo "🗑️ Eliminando BD actual..."
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"

# Paso 3: Crear BD nueva
echo "🆕 Creando BD nueva..."
psql -h localhost -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Paso 4: Restore desde backup
echo "📥 Restaurando desde backup..."
gunzip -c $BACKUP_FILE | pg_restore -h localhost -U $DB_USER -d $DB_NAME -v

if [ $? -eq 0 ]; then
    echo "✅ Restore completado exitosamente"
else
    echo "❌ ERROR: Restore falló"
    exit 1
fi

# Paso 5: Verificar datos
echo "🔍 Verificando datos..."
psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM metricas;"

# Paso 6: Reiniciar aplicación
echo "🚀 Reiniciando aplicación..."
sudo systemctl start dashboardsonar

echo "✅ Proceso completado"
```

**Tiempo estimado**: 5-10 minutos (dependiendo del tamaño)

---

#### Escenario 2: Restore Selectivo (Solo Tablas Específicas)

```bash
# Listar tablas en el backup
pg_restore -l dashboardsonar_20251217.backup | grep TABLE

# Restaurar solo tabla 'proyectos'
pg_restore -h localhost \
           -U dashboard_user \
           -d dashboardsonar \
           -t proyectos \
           -c \
           dashboardsonar_20251217.backup
```

**Parámetros**:
- `-t`: Tabla específica
- `-c`: Drop antes de crear (clean)

---

#### Escenario 3: Restore a Nueva Base de Datos (Testing)

```bash
# Crear BD de testing
psql -h localhost -U postgres -c "CREATE DATABASE dashboardsonar_test OWNER dashboard_user;"

# Restore a BD de testing
gunzip -c dashboardsonar_20251217.sql.gz | \
  pg_restore -h localhost -U dashboard_user -d dashboardsonar_test -v

# Probar con la app apuntando a dashboardsonar_test
```

---

### Restore PostgreSQL desde Base Backup (PITR)

**Escenario**: Restaurar a un punto específico en el tiempo (ej: antes de un `DELETE` accidental).

**PASO 1**: Detener PostgreSQL

```bash
sudo systemctl stop postgresql
```

---

**PASO 2**: Mover datos actuales (por si acaso)

```bash
sudo mv /var/lib/postgresql/13/main /var/lib/postgresql/13/main.old
```

---

**PASO 3**: Restaurar base backup

```bash
# Extraer base backup
sudo tar -xzf /backups/postgresql_base/base_20251217.tar.gz -C /var/lib/postgresql/13/main

# Ajustar permisos
sudo chown -R postgres:postgres /var/lib/postgresql/13/main
```

---

**PASO 4**: Configurar recovery

```bash
# Crear recovery.conf (PostgreSQL <12) o recovery.signal (PostgreSQL 12+)
sudo tee /var/lib/postgresql/13/main/recovery.signal <<EOF
# Recovery mode enabled
EOF

sudo tee -a /var/lib/postgresql/13/main/postgresql.conf <<EOF
restore_command = 'cp /backups/wal_archive/%f %p'
recovery_target_time = '2025-12-17 14:30:00'  # Punto exacto de recuperación
recovery_target_action = 'promote'
EOF
```

---

**PASO 5**: Iniciar PostgreSQL en recovery mode

```bash
sudo systemctl start postgresql

# Monitorear logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log

# Verás algo como:
# starting point-in-time recovery to 2025-12-17 14:30:00
# restored log file "000000010000000000000001"
# recovery stopping before commit of transaction 1234, time 2025-12-17 14:29:58
# recovery has finished
# database system is ready to accept connections
```

---

**PASO 6**: Verificar datos

```bash
psql -h localhost -U dashboard_user -d dashboardsonar -c "SELECT NOW();"
psql -h localhost -U dashboard_user -d dashboardsonar -c "SELECT COUNT(*) FROM proyectos;"
```

**Tiempo estimado**: 30-60 minutos (dependiendo de cantidad de WAL logs)

---

### Restore SQLite

```bash
#!/bin/bash
# restore_sqlite.sh

BACKUP_FILE="/backups/sqlite/dashboardsonar_20251217.db.gz"
DB_FILE="/path/to/dashboardsonar.db"

# Backup de BD actual (por si acaso)
cp $DB_FILE ${DB_FILE}.before_restore

# Restaurar
gunzip -c $BACKUP_FILE > $DB_FILE

# Verificar integridad
sqlite3 $DB_FILE "PRAGMA integrity_check;"

# Si retorna "ok", el restore fue exitoso
if [ $? -eq 0 ]; then
    echo "✅ Restore SQLite completado"
else
    echo "❌ ERROR: BD corrupta"
    # Restaurar backup de BD actual
    mv ${DB_FILE}.before_restore $DB_FILE
fi
```

---

### Restore de Archivos

```bash
#!/bin/bash
# restore_files.sh

BACKUP_FILE="/backups/files/files_20251217.tar.gz"
APP_DIR="/path/to/dashboardsonar"

# Detener aplicación
sudo systemctl stop dashboardsonar

# Restaurar archivos
tar -xzf $BACKUP_FILE -C $APP_DIR

# Ajustar permisos
sudo chown -R dashboarduser:dashboarduser $APP_DIR

# Reiniciar aplicación
sudo systemctl start dashboardsonar

echo "✅ Archivos restaurados"
```

---

## 🌪️ Disaster Recovery

### Plan de Disaster Recovery (DR)

**Escenarios críticos**:

1. 🔥 **Servidor completo caído** (hardware failure, incendio)
2. 💣 **Base de datos corrupta** (irrecuperable)
3. 🦠 **Ransomware attack**
4. 🌊 **Datacenter completo down**

---

### DR Procedure: Servidor Nuevo

**Objetivo**: Levantar Dashboard Sonar en servidor completamente nuevo.

**Tiempo estimado**: 2-4 horas

---

#### PASO 1: Provisionar Servidor Nuevo

```bash
# AWS EC2
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name dashboardsonar-key \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx

# O manualmente en consola AWS
```

---

#### PASO 2: Instalar Dependencias

```bash
# Conectar al servidor
ssh -i dashboardsonar-key.pem ubuntu@new-server-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.12
sudo apt install python3.12 python3.12-venv python3-pip -y

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Instalar Nginx
sudo apt install nginx -y

# Instalar Git
sudo apt install git -y
```

---

#### PASO 3: Clonar Aplicación

```bash
cd /opt
sudo git clone https://github.com/jfdelafuente/dashboardsonar-application-python.git
cd dashboardsonar-application-python
sudo chown -R ubuntu:ubuntu .

# Crear virtualenv
python3.12 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

#### PASO 4: Restaurar .env desde Backup

```bash
# Descargar backup desde S3
aws s3 cp s3://backups-dashboardsonar/files/files_latest.tar.gz /tmp/

# Extraer .env
tar -xzf /tmp/files_latest.tar.gz -C /opt/dashboardsonar-application-python .env

# Verificar
cat .env
```

---

#### PASO 5: Configurar PostgreSQL

```bash
# Crear usuario
sudo -u postgres psql -c "CREATE USER dashboard_user WITH PASSWORD 'secure_password';"

# Crear base de datos
sudo -u postgres psql -c "CREATE DATABASE dashboardsonar OWNER dashboard_user;"
```

---

#### PASO 6: Restaurar Base de Datos desde S3

```bash
# Descargar último backup desde S3
aws s3 cp s3://backups-dashboardsonar/postgresql/dashboardsonar_latest.sql.gz /tmp/

# Restaurar
gunzip -c /tmp/dashboardsonar_latest.sql.gz | \
  pg_restore -h localhost -U dashboard_user -d dashboardsonar -v

# Verificar
psql -h localhost -U dashboard_user -d dashboardsonar -c "SELECT COUNT(*) FROM proyectos;"
```

---

#### PASO 7: Configurar Servicios

```bash
# Copiar service files desde repo
sudo cp /opt/dashboardsonar-application-python/deployment/dashboardsonar.service /etc/systemd/system/
sudo cp /opt/dashboardsonar-application-python/deployment/nginx-dashboardsonar.conf /etc/nginx/sites-available/dashboardsonar

# Habilitar
sudo ln -s /etc/nginx/sites-available/dashboardsonar /etc/nginx/sites-enabled/
sudo systemctl enable dashboardsonar
sudo systemctl enable nginx

# Iniciar
sudo systemctl start dashboardsonar
sudo systemctl start nginx
```

---

#### PASO 8: Verificar

```bash
# Health check
curl http://localhost/health

# Acceder desde navegador
# http://new-server-ip/
```

---

#### PASO 9: Actualizar DNS

```bash
# Actualizar DNS para apuntar a nuevo servidor
# dashboard-sonar.empresa.com -> new-server-ip

# O en Route53 (AWS):
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456 \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "dashboard-sonar.empresa.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "new-server-ip"}]
      }
    }]
  }'
```

---

## 🧪 Testing de Backups

### ¿Por qué Testar Backups?

**Regla de Oro**: Un backup no testeado es un backup que NO funciona.

**Estadística**: 34% de empresas descubren que sus backups están corruptos cuando intentan restaurar.

---

### Test Mensual de Restore

**Procedimiento** (ejecutar 1er día de cada mes):

```bash
#!/bin/bash
# test_backup_restore.sh

echo "=== TEST DE RESTORE - Dashboard Sonar ==="
date

# Paso 1: Crear BD de testing
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS dashboardsonar_test;"
psql -h localhost -U postgres -c "CREATE DATABASE dashboardsonar_test OWNER dashboard_user;"

# Paso 2: Restaurar último backup
LATEST_BACKUP=$(ls -t /backups/postgresql/*.sql.gz | head -1)
echo "Restaurando: $LATEST_BACKUP"

gunzip -c $LATEST_BACKUP | pg_restore -h localhost -U dashboard_user -d dashboardsonar_test 2>&1 | tee /tmp/restore_test.log

# Paso 3: Verificar integridad
echo "Verificando datos..."
PROYECTOS_COUNT=$(psql -h localhost -U dashboard_user -d dashboardsonar_test -t -c "SELECT COUNT(*) FROM proyectos;")
METRICAS_COUNT=$(psql -h localhost -U dashboard_user -d dashboardsonar_test -t -c "SELECT COUNT(*) FROM metricas;")

echo "Proyectos: $PROYECTOS_COUNT"
echo "Métricas: $METRICAS_COUNT"

# Paso 4: Cleanup
psql -h localhost -U postgres -c "DROP DATABASE dashboardsonar_test;"

# Paso 5: Reportar resultado
if grep -q "ERROR" /tmp/restore_test.log; then
    echo "❌ TEST FALLIDO - Revisar logs"
    # Enviar alerta
    curl -X POST https://slack.webhook.url -d '{"text":"🔴 Backup test FAILED"}'
    exit 1
else
    echo "✅ TEST EXITOSO"
    curl -X POST https://slack.webhook.url -d '{"text":"✅ Backup test passed"}'
fi
```

**Agregar a crontab**:
```bash
# Ejecutar el 1er día de cada mes a las 3 AM
0 3 1 * * /path/to/test_backup_restore.sh >> /var/log/backup_test.log 2>&1
```

---

### Checklist de Testing

- [ ] Restore completo funciona sin errores
- [ ] Datos verificados (counts coinciden con producción)
- [ ] Schema intacto (todas las tablas existen)
- [ ] Índices creados correctamente
- [ ] Foreign keys funcionan
- [ ] Aplicación puede conectarse a BD restaurada
- [ ] Tiempo de restore < RTO (2 horas)

---

## 🤖 Automatización

### Cron Jobs para Backups Automáticos

```bash
# Editar crontab
crontab -e

# Agregar:

# Full backup diario a las 2 AM
0 2 * * * /path/to/backup_postgresql.sh >> /var/log/backup.log 2>&1

# Backup incremental cada 6 horas
0 */6 * * * /path/to/backup_incremental.sh >> /var/log/backup.log 2>&1

# Backup de archivos diario a las 3 AM
0 3 * * * /path/to/backup_files.sh >> /var/log/backup.log 2>&1

# Sync a S3 cada hora
0 * * * * aws s3 sync /backups/ s3://backups-dashboardsonar/ --delete >> /var/log/s3sync.log 2>&1

# Test de restore mensual (1er día del mes a las 4 AM)
0 4 1 * * /path/to/test_backup_restore.sh >> /var/log/backup_test.log 2>&1

# Limpiar backups locales >7 días (diario a las 5 AM)
0 5 * * * find /backups/postgresql -name "*.sql.gz" -mtime +7 -delete
```

---

### Script Maestro de Backup

```bash
#!/bin/bash
# master_backup.sh - Ejecuta todos los backups

set -e  # Exit on error

LOG_FILE="/var/log/master_backup.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] === INICIO BACKUP MAESTRO ===" >> $LOG_FILE

# 1. PostgreSQL
echo "[$DATE] Backup PostgreSQL..." >> $LOG_FILE
/path/to/backup_postgresql.sh >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "[$DATE] ✅ PostgreSQL OK" >> $LOG_FILE
else
    echo "[$DATE] ❌ PostgreSQL FAILED" >> $LOG_FILE
    curl -X POST https://slack.webhook.url -d '{"text":"🔴 PostgreSQL backup failed"}'
fi

# 2. Archivos
echo "[$DATE] Backup archivos..." >> $LOG_FILE
/path/to/backup_files.sh >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "[$DATE] ✅ Archivos OK" >> $LOG_FILE
else
    echo "[$DATE] ❌ Archivos FAILED" >> $LOG_FILE
fi

# 3. Sync a S3
echo "[$DATE] Sync a S3..." >> $LOG_FILE
aws s3 sync /backups/ s3://backups-dashboardsonar/ --delete >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "[$DATE] ✅ S3 Sync OK" >> $LOG_FILE
else
    echo "[$DATE] ❌ S3 Sync FAILED" >> $LOG_FILE
    curl -X POST https://slack.webhook.url -d '{"text":"🔴 S3 sync failed"}'
fi

# 4. Verificar espacio en disco
DISK_USAGE=$(df /backups | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "[$DATE] ⚠️ Disk usage: $DISK_USAGE%" >> $LOG_FILE
    curl -X POST https://slack.webhook.url -d "{\"text\":\"⚠️ Backup disk $DISK_USAGE% full\"}"
fi

echo "[$DATE] === FIN BACKUP MAESTRO ===" >> $LOG_FILE
```

---

### Monitoreo de Backups

```bash
#!/bin/bash
# check_backup_freshness.sh

# Verificar que haya backup reciente (<26 horas)
LATEST_BACKUP=$(find /backups/postgresql -name "*.sql.gz" -mtime -1 | wc -l)

if [ $LATEST_BACKUP -eq 0 ]; then
    echo "❌ No hay backup reciente (>24 horas)"
    curl -X POST https://slack.webhook.url -d '{"text":"🔴 No recent backups found!"}'
    exit 1
else
    echo "✅ Backup reciente encontrado"
fi
```

**Cron**:
```bash
# Ejecutar cada 6 horas
0 */6 * * * /path/to/check_backup_freshness.sh
```

---

## 📚 Referencias

### Documentación Relacionada

- 🚨 **Runbook**: [RUNBOOK.md](../runbooks/RUNBOOK.md)
- 📊 **Monitoring**: [MONITORING_GUIDE.md](../monitoring/MONITORING_GUIDE.md)
- 🚀 **Deployment**: [DEPLOYMENT_AWS.md](../deployment/DEPLOYMENT_AWS.md)
- 🔧 **Admin Guide**: [../../3-user/admin-guide/ADMIN_GUIDE.md](../../3-user/admin-guide/ADMIN_GUIDE.md)

### Recursos Externos

- 📖 [PostgreSQL Backup & Restore](https://www.postgresql.org/docs/current/backup.html)
- 📖 [AWS RDS Automated Backups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
- 📖 [Disaster Recovery Best Practices](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
**Mantenido por**: Equipo SRE/DBA
**Próxima revisión**: Después de cada DR drill (trimestral)
