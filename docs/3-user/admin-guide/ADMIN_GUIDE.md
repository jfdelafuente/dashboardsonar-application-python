# Guía de Administración - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Administradores de la aplicación, System Owners

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Gestión de Usuarios](#gestión-de-usuarios)
3. [Carga de Datos](#carga-de-datos)
4. [Configuración de la Aplicación](#configuración-de-la-aplicación)
5. [Monitoreo y Logs](#monitoreo-y-logs)
6. [Backup y Restauración](#backup-y-restauración)
7. [Mantenimiento](#mantenimiento)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

Esta guía está diseñada para **administradores** que necesitan:

- ✅ Gestionar usuarios (crear, editar, eliminar, roles)
- ✅ Cargar datos desde SonarQube
- ✅ Configurar variables de entorno
- ✅ Monitorear logs y diagnosticar problemas
- ✅ Realizar backups de la base de datos
- ✅ Mantener la aplicación funcionando

**Prerequisitos**:
- Acceso de administrador a la aplicación
- Acceso al servidor donde corre la aplicación
- Conocimientos básicos de terminal/línea de comandos
- (Opcional) Conocimientos de PostgreSQL/SQLite

---

## 👥 Gestión de Usuarios

### Tipos de Roles

Dashboard Sonar tiene 2 roles principales:

| Rol | Permisos | Uso Típico |
|-----|----------|-----------|
| **Admin** | Acceso total, gestión de usuarios, configuración | Administradores de sistema |
| **User** | Solo lectura, visualización de dashboards | Desarrolladores, gestores, QA |

### Crear Usuario Nuevo

#### Opción 1: Mediante Flask Shell (Recomendado)

**Paso 1**: Conectar al servidor

```bash
# SSH al servidor (si es remoto)
ssh usuario@servidor-dashboard.com

# Navegar al directorio de la aplicación
cd /ruta/a/dashboardsonar-application-python
```

**Paso 2**: Activar entorno virtual

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Paso 3**: Abrir Flask Shell

```bash
flask shell
```

**Paso 4**: Crear usuario

```python
from infocodest.models.users import User
from infocodest.extensions import db

# Crear usuario normal
nuevo_usuario = User(
    username='jperez',
    email='jperez@empresa.com',
    password='password_temporal_123',  # El usuario debería cambiarlo
    is_admin=False
)

db.session.add(nuevo_usuario)
db.session.commit()

print(f"✅ Usuario {nuevo_usuario.username} creado correctamente")
```

**Paso 5**: Salir de Flask Shell

```python
exit()
```

---

**Crear usuario administrador**:

```python
admin = User(
    username='admin_sistema',
    email='admin@empresa.com',
    password='password_seguro_admin',
    is_admin=True  # ← Importante para dar permisos de admin
)

db.session.add(admin)
db.session.commit()
```

---

#### Opción 2: Script Automatizado de Setup

Si la aplicación acaba de instalarse, usa el script de setup:

**Windows**:
```bash
setup_database.bat
```

**Linux/macOS**:
```bash
./setup_database.sh
```

El script preguntará:
```
Crear usuario administrador? (y/n): y
Username: admin
Email: admin@empresa.com
Password: ******
Confirmar password: ******

✅ Usuario admin creado correctamente
```

---

### Listar Todos los Usuarios

```python
# En Flask Shell
from infocodest.models.users import User

usuarios = User.query.all()

for user in usuarios:
    rol = "Admin" if user.is_admin else "User"
    print(f"{user.username} ({user.email}) - {rol}")
```

**Salida**:
```
admin (admin@empresa.com) - Admin
jperez (jperez@empresa.com) - User
mgarcia (mgarcia@empresa.com) - User
```

---

### Modificar Usuario

#### Cambiar Password

```python
# En Flask Shell
from infocodest.models.users import User
from infocodest.utils.security import hash_pass
from infocodest.extensions import db

# Buscar usuario
usuario = User.query.filter_by(username='jperez').first()

# Cambiar password (se hashea automáticamente)
usuario.password = 'nueva_password_segura'

# Guardar
db.session.commit()

print(f"✅ Password de {usuario.username} actualizado")
```

---

#### Promover a Administrador

```python
# Buscar usuario
usuario = User.query.filter_by(username='jperez').first()

# Promover a admin
usuario.is_admin = True

# Guardar
db.session.commit()

print(f"✅ {usuario.username} ahora es administrador")
```

---

#### Degradar de Administrador

```python
usuario = User.query.filter_by(username='jperez').first()
usuario.is_admin = False
db.session.commit()

print(f"✅ {usuario.username} ya no es administrador")
```

---

### Eliminar Usuario

⚠️ **ADVERTENCIA**: Esta acción es **irreversible**.

```python
# En Flask Shell
from infocodest.models.users import User
from infocodest.extensions import db

# Buscar usuario
usuario = User.query.filter_by(username='jperez').first()

if usuario:
    username_backup = usuario.username
    db.session.delete(usuario)
    db.session.commit()
    print(f"✅ Usuario {username_backup} eliminado")
else:
    print("❌ Usuario no encontrado")
```

**Recomendación**: En lugar de eliminar, considera **desactivar** el usuario (agregar campo `is_active=False` en futuras versiones).

---

### Verificar Usuario Existe

```python
usuario = User.query.filter_by(username='jperez').first()

if usuario:
    print(f"✅ Usuario {usuario.username} existe")
    print(f"   Email: {usuario.email}")
    print(f"   Admin: {'Sí' if usuario.is_admin else 'No'}")
    print(f"   Creado: {usuario.created_on}")
else:
    print("❌ Usuario no existe")
```

---

## 📊 Carga de Datos

### ¿Qué son los Datos?

Dashboard Sonar muestra métricas de calidad de código que provienen de **SonarQube**. Los datos deben **cargarse periódicamente** para mantener el dashboard actualizado.

### Origen de los Datos

Los datos están en archivos **CSV** generados por análisis de SonarQube:

```
datos/
├── metricas.csv        # Métricas actuales de cada proyecto
├── historico.csv       # Histórico de todos los análisis
└── proveedores.csv     # Relación aplicación-proveedor
```

---

### Pipeline de Carga de Datos

El proyecto incluye un **orquestador** que ejecuta todos los scripts de carga en orden:

#### Paso 1: Preparar Datos

Asegúrate de que los archivos CSV estén en el directorio `datos/`:

```bash
ls datos/
# Deberías ver:
# metricas.csv
# historico.csv
# proveedores.csv (opcional)
```

---

#### Paso 2: Ejecutar Pipeline de Datos

**Windows**:
```bash
# Con configuración por defecto (Development - SQLite)
run_data_pipeline.bat

# Para producción (PostgreSQL)
run_data_pipeline.bat Production

# Ver qué haría sin ejecutar (dry-run)
run_data_pipeline.bat --dry-run
```

**Linux/macOS**:
```bash
# Dar permisos (solo primera vez)
chmod +x run_data_pipeline.sh

# Ejecutar
./run_data_pipeline.sh Production

# Dry-run
./run_data_pipeline.sh --dry-run
```

---

#### Paso 3: Verificar Ejecución

**Salida esperada**:
```
═══════════════════════════════════════════
  Dashboard Sonar - Data Pipeline
  Environment: Production
═══════════════════════════════════════════

Loading environment variables from .env...
✅ Environment loaded

Running data pipeline scripts...

[1/4] Running load_data.py...
  ✅ Loaded 45 projects from metricas.csv
  ✅ Loaded 1,234 historical records
  ⏱  Execution time: 12.5s

[2/4] Running generate_daily.py...
  ✅ Generated 45 daily snapshots
  ⏱  Execution time: 5.2s

[3/4] Running generate_stats.py...
  ✅ Generated statistics for 12 applications
  ⏱  Execution time: 3.8s

[4/4] Running generate_registro.py...
  ✅ Created audit registry
  ⏱  Execution time: 1.1s

═══════════════════════════════════════════
  Summary
═══════════════════════════════════════════
  ✅ load_data.py          : SUCCESS (12.5s)
  ✅ generate_daily.py     : SUCCESS (5.2s)
  ✅ generate_stats.py     : SUCCESS (3.8s)
  ✅ generate_registro.py  : SUCCESS (1.1s)

  Total execution time: 22.6s
═══════════════════════════════════════════
✅ All scripts completed successfully!
```

---

#### Paso 4: Verificar en Dashboard

1. Abre Dashboard Sonar en el navegador
2. Deberías ver los proyectos cargados
3. Verifica que las fechas de "Última Actualización" son recientes

---

### Opciones Avanzadas del Pipeline

#### Especificar Directorio de Datos Personalizado

```bash
run_data_pipeline.bat Production --data-dir ./datos_custom
```

---

#### Especificar Fecha para Snapshots

```bash
run_data_pipeline.bat Production --date 2025-12-15
```

---

#### Tamaño de Batch Personalizado

Para bases de datos grandes, ajusta el batch size:

```bash
run_data_pipeline.bat Production --batch-size 1000
```

---

#### Regenerar Datos

Si necesitas regenerar estadísticas:

```bash
# Regenerar snapshots diarios
run_data_pipeline.bat Production --clear-daily

# Regenerar estadísticas
run_data_pipeline.bat Production --clear-stats

# Regenerar ambos
run_data_pipeline.bat Production --clear-daily --clear-stats
```

---

#### Saltar Pasos Específicos

Si solo quieres ejecutar algunos pasos:

```bash
# Saltar carga de datos (solo generar stats)
run_data_pipeline.bat Production --skip-load

# Saltar generación de daily
run_data_pipeline.bat Production --skip-daily
```

---

### Programar Carga Automática

#### En Windows (Task Scheduler)

**Paso 1**: Abrir Task Scheduler
- Win + R → `taskschd.msc` → Enter

**Paso 2**: Crear Nueva Tarea
- Click derecho en "Task Scheduler Library" → "Create Task"

**Paso 3**: Configurar General
- **Name**: "Dashboard Sonar - Carga Diaria"
- **Description**: "Carga automática de datos de SonarQube"
- **Security**: "Run whether user is logged on or not"

**Paso 4**: Configurar Trigger
- Tab "Triggers" → "New"
- **Begin the task**: "On a schedule"
- **Settings**: "Daily" a las 02:00 AM

**Paso 5**: Configurar Action
- Tab "Actions" → "New"
- **Action**: "Start a program"
- **Program/script**: `C:\ruta\a\dashboardsonar\run_data_pipeline.bat`
- **Add arguments**: `Production`
- **Start in**: `C:\ruta\a\dashboardsonar`

**Paso 6**: Guardar
- Click "OK" → Ingresar password de Windows si se solicita

---

#### En Linux/macOS (Cron)

**Paso 1**: Editar crontab

```bash
crontab -e
```

**Paso 2**: Agregar tarea diaria (2:00 AM)

```cron
# Dashboard Sonar - Carga diaria de datos
0 2 * * * cd /ruta/a/dashboardsonar && ./run_data_pipeline.sh Production >> logs/pipeline.log 2>&1
```

**Explicación**:
- `0 2 * * *`: A las 2:00 AM, todos los días
- `cd /ruta/a/dashboardsonar`: Navegar al directorio
- `./run_data_pipeline.sh Production`: Ejecutar pipeline
- `>> logs/pipeline.log 2>&1`: Guardar output en log

**Paso 3**: Guardar y salir
- Vim: `:wq`
- Nano: Ctrl+X → Y → Enter

**Paso 4**: Verificar cron instalado

```bash
crontab -l
# Deberías ver tu nueva tarea
```

---

### Solución de Problemas en Carga de Datos

#### Error: "CSV file not found"

**Causa**: Archivo `metricas.csv` no existe o ruta incorrecta.

**Solución**:
```bash
# Verificar que archivos existen
ls datos/
# Deben estar: metricas.csv, historico.csv

# Si no existen, exportarlos desde SonarQube
```

---

#### Error: "UNIQUE constraint failed"

**Causa**: Intentas insertar un proyecto que ya existe.

**Solución**:
El script debería hacer `UPSERT` (update or insert). Si sigue fallando:

```bash
# Regenerar base de datos (CUIDADO: Borra datos)
python -c "from infocodest import create_app; from infocodest.extensions import db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"

# Luego volver a cargar datos
run_data_pipeline.bat Production
```

---

#### Error: "Database connection failed"

**Causa**: No puede conectar a PostgreSQL.

**Solución**:
1. Verificar que PostgreSQL está corriendo:
   ```bash
   sudo systemctl status postgresql
   ```

2. Verificar credenciales en `.env`:
   ```env
   DB_ENGINE=postgresql
   DB_USERNAME=tu_usuario
   DB_PASS=tu_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=dashboardsonar
   ```

3. Probar conexión manual:
   ```bash
   psql -h localhost -U tu_usuario -d dashboardsonar
   ```

---

## ⚙️ Configuración de la Aplicación

### Archivo de Configuración (.env)

La aplicación se configura mediante variables de entorno en el archivo `.env` (raíz del proyecto).

**Ubicación**: `/ruta/a/dashboardsonar/.env`

### Variables Críticas

#### Base de Datos

```env
# Para PostgreSQL (Producción)
DB_ENGINE=postgresql
DB_USERNAME=dashboarduser
DB_PASS=password_seguro_123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar

# Para SQLite (Desarrollo)
# Comentar las variables DB_* para usar SQLite por defecto
```

**¿Cómo cambiar de SQLite a PostgreSQL?**

1. Crear base de datos en PostgreSQL:
   ```sql
   CREATE DATABASE dashboardsonar;
   CREATE USER dashboarduser WITH PASSWORD 'password123';
   GRANT ALL PRIVILEGES ON DATABASE dashboardsonar TO dashboarduser;
   ```

2. Actualizar `.env` con las credenciales de PostgreSQL

3. Ejecutar migraciones:
   ```bash
   flask db upgrade
   ```

4. Cargar datos:
   ```bash
   run_data_pipeline.bat Production
   ```

---

#### Seguridad

```env
# CRÍTICO: Generar clave única en producción
SECRET_KEY=tu_clave_secreta_generada_aleatoriamente
```

**¿Cómo generar SECRET_KEY segura?**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copiar output y pegarlo en `.env`:
```env
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

---

#### Modo Debug

```env
# DESARROLLO
DEBUG=True
FLASK_DEBUG=1

# PRODUCCIÓN (siempre False)
DEBUG=False
FLASK_DEBUG=0
```

⚠️ **NUNCA** poner `DEBUG=True` en producción (expone información sensible).

---

#### Servidor

```env
# IP y Puerto
HOST=127.0.0.1  # Solo acceso local
PORT=5000

# Para acceso desde red externa
HOST=0.0.0.0
PORT=5000
```

---

#### Días de Comparación

```env
# Días hacia atrás para comparar métricas históricas
DAYS_COMPARISON=15
```

**Uso**: En el dashboard, cuando ves "Tendencia últimos 15 días", usa este valor.

---

#### Logging

```env
# Nivel de detalle de logs
LOG_LEVEL=INFO  # Opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

### Aplicar Cambios de Configuración

Después de modificar `.env`:

1. **Reiniciar la aplicación**:

   **Si corre con Gunicorn (producción)**:
   ```bash
   sudo systemctl restart dashboardsonar
   ```

   **Si corre con `python run.py` (desarrollo)**:
   - Ctrl+C para detener
   - `python run.py` para iniciar nuevamente

2. **Verificar que cambios se aplicaron**:
   ```bash
   flask shell
   >>> from flask import current_app
   >>> print(current_app.config['DEBUG'])
   False  # Debería ser False en producción
   >>> print(current_app.config['SQLALCHEMY_DATABASE_URI'])
   postgresql://dashboarduser:***@localhost:5432/dashboardsonar
   ```

---

## 📋 Monitoreo y Logs

### Ubicación de Logs

Los logs se guardan en el directorio `logs/`:

```
logs/
├── app.log             # Log principal de la aplicación
├── app.log.1           # Rotación (backup 1)
├── app.log.2           # Rotación (backup 2)
└── ...
```

---

### Ver Logs en Tiempo Real

**Linux/macOS**:
```bash
# Ver últimas 100 líneas
tail -100 logs/app.log

# Seguir logs en tiempo real
tail -f logs/app.log
```

**Windows (PowerShell)**:
```powershell
# Ver últimas 100 líneas
Get-Content logs\app.log -Tail 100

# Seguir logs en tiempo real
Get-Content logs\app.log -Wait -Tail 50
```

---

### Interpretar Logs

**Formato de log**:
```
2025-12-17 10:30:45,123 - INFO - [views.home] - User admin logged in from 192.168.1.100
2025-12-17 10:31:12,456 - ERROR - [services.dashboard_service] - Failed to fetch metrics: Database connection lost
```

**Componentes**:
- `2025-12-17 10:30:45,123`: Timestamp
- `INFO`: Nivel (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `[views.home]`: Módulo que generó el log
- `User admin logged in...`: Mensaje

---

### Niveles de Log

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| **DEBUG** | Detalles técnicos para debugging | "Query executed: SELECT * FROM metricas" |
| **INFO** | Eventos normales | "User logged in", "Data loaded successfully" |
| **WARNING** | Situaciones anormales pero no críticas | "Slow query (2.5s)", "Deprecated function used" |
| **ERROR** | Errores que afectan funcionalidad | "Database connection failed", "File not found" |
| **CRITICAL** | Errores graves, aplicación podría crashear | "Out of memory", "Database corrupted" |

---

### Buscar Errores en Logs

**Linux/macOS**:
```bash
# Buscar errores de hoy
grep "ERROR" logs/app.log | grep "2025-12-17"

# Buscar errores críticos
grep "CRITICAL" logs/app.log

# Buscar errores de base de datos
grep -i "database" logs/app.log | grep "ERROR"
```

**Windows (PowerShell)**:
```powershell
# Buscar errores
Select-String -Path logs\app.log -Pattern "ERROR"

# Buscar errores de hoy
Select-String -Path logs\app.log -Pattern "ERROR" | Select-String -Pattern "2025-12-17"
```

---

### Rotación de Logs

Los logs se rotan automáticamente:
- **Tamaño máximo por archivo**: 10 MB
- **Archivos de backup**: 10
- **Total de logs**: ~100 MB máximo

Cuando `app.log` alcanza 10 MB:
```
app.log (10 MB)  →  app.log.1
                 →  app.log (nuevo, vacío)
```

---

### Cambiar Nivel de Logging

Para ver más detalles (troubleshooting):

1. Editar `.env`:
   ```env
   LOG_LEVEL=DEBUG
   ```

2. Reiniciar aplicación

3. Los logs mostrarán mucho más detalle (queries SQL, variables, etc.)

**⚠️ Advertencia**: `LOG_LEVEL=DEBUG` genera **muchos** logs. Volver a `INFO` después de resolver el problema.

---

## 💾 Backup y Restauración

### Backup de Base de Datos

#### PostgreSQL

**Backup Manual**:
```bash
# Backup completo
pg_dump -h localhost -U dashboarduser -d dashboardsonar > backup_dashboard_2025-12-17.sql

# Backup comprimido
pg_dump -h localhost -U dashboarduser -d dashboardsonar | gzip > backup_dashboard_2025-12-17.sql.gz
```

**Restaurar desde Backup**:
```bash
# Restaurar SQL sin comprimir
psql -h localhost -U dashboarduser -d dashboardsonar < backup_dashboard_2025-12-17.sql

# Restaurar SQL comprimido
gunzip -c backup_dashboard_2025-12-17.sql.gz | psql -h localhost -U dashboarduser -d dashboardsonar
```

---

**Backup Automatizado (Cron)**:

```bash
# Editar crontab
crontab -e

# Agregar backup diario a las 3:00 AM
0 3 * * * pg_dump -h localhost -U dashboarduser -d dashboardsonar | gzip > /backups/dashboard_$(date +\%Y\%m\%d).sql.gz

# Agregar limpieza de backups >30 días
0 4 * * * find /backups/ -name "dashboard_*.sql.gz" -mtime +30 -delete
```

---

#### SQLite

**Backup Manual**:
```bash
# Copiar archivo db.sqlite3
cp db.sqlite3 backup_dashboard_2025-12-17.sqlite3

# Backup comprimido
gzip -c db.sqlite3 > backup_dashboard_2025-12-17.sqlite3.gz
```

**Restaurar desde Backup**:
```bash
# Detener aplicación primero
sudo systemctl stop dashboardsonar

# Restaurar
cp backup_dashboard_2025-12-17.sqlite3 db.sqlite3

# O desde comprimido
gunzip -c backup_dashboard_2025-12-17.sqlite3.gz > db.sqlite3

# Iniciar aplicación
sudo systemctl start dashboardsonar
```

---

### Backup de Archivos de Configuración

**Archivos críticos a respaldar**:
```
.env                     # Variables de entorno (NO commitear a Git)
logs/                    # Logs (opcional, para auditoría)
datos/                   # CSVs fuente (si son únicos)
```

**Backup**:
```bash
# Crear tarball
tar -czf backup_config_2025-12-17.tar.gz .env datos/ logs/

# Copiar a servidor de backups
scp backup_config_2025-12-17.tar.gz usuario@servidor-backups:/backups/dashboard/
```

---

### Estrategia de Backup Recomendada

| Tipo | Frecuencia | Retención | Ubicación |
|------|-----------|-----------|-----------|
| **Base de Datos** | Diario | 30 días | Servidor remoto |
| **Configuración** | Semanal | 90 días | Servidor remoto |
| **Logs** | Mensual | 6 meses | Almacenamiento económico |

---

## 🔧 Mantenimiento

### Tareas Mensuales

#### 1. Revisar Tamaño de Base de Datos

**PostgreSQL**:
```sql
SELECT pg_size_pretty(pg_database_size('dashboardsonar'));
```

**SQLite**:
```bash
du -h db.sqlite3
```

**Si supera 1 GB**: Considerar archivar datos históricos >1 año.

---

#### 2. Limpiar Logs Antiguos

```bash
# Borrar logs >90 días
find logs/ -name "app.log.*" -mtime +90 -delete
```

---

#### 3. Verificar Backups

```bash
# Listar backups
ls -lh /backups/dashboard_*.sql.gz

# Verificar que hay backups de últimos 7 días
find /backups/ -name "dashboard_*.sql.gz" -mtime -7
```

---

### Tareas Trimestrales

#### 1. Actualizar Dependencias (Seguridad)

```bash
# Activar entorno virtual
source venv/bin/activate

# Ver paquetes desactualizados
pip list --outdated

# Actualizar paquetes (CUIDADO: hacer en staging primero)
pip install --upgrade Flask SQLAlchemy

# Congelar nuevas versiones
pip freeze > requirements.txt
```

**⚠️ Advertencia**: Probar en entorno de staging antes de aplicar en producción.

---

#### 2. Revisar Usuarios Activos

```python
# En Flask Shell
from infocodest.models.users import User

usuarios = User.query.all()
print(f"Total usuarios: {len(usuarios)}")

# Identificar usuarios que no han hecho login recientemente
# (Requiere agregar campo last_login en futuras versiones)
```

---

### Actualizaciones de la Aplicación

#### Actualizar a Nueva Versión

**Paso 1**: Backup completo (BD + config)

**Paso 2**: Obtener nueva versión
```bash
git fetch --all
git checkout v2.0.0  # Nueva versión
```

**Paso 3**: Actualizar dependencias
```bash
pip install -r requirements.txt --upgrade
```

**Paso 4**: Ejecutar migraciones de BD
```bash
flask db upgrade
```

**Paso 5**: Reiniciar aplicación
```bash
sudo systemctl restart dashboardsonar
```

**Paso 6**: Verificar
- Acceder al dashboard
- Verificar que datos se muestran correctamente
- Revisar logs por errores

---

## 🐛 Troubleshooting

### Problema: Aplicación no inicia

**Síntomas**: Al ejecutar `python run.py` no arranca.

**Diagnóstico**:
```bash
# Ver logs detallados
python run.py --debug
```

**Causas comunes**:
1. **Puerto ocupado**:
   ```bash
   # Linux/macOS
   lsof -i :5000
   # Matar proceso
   kill -9 <PID>
   ```

2. **Falta SECRET_KEY**:
   - Agregar `SECRET_KEY=...` en `.env`

3. **Base de datos inaccesible**:
   - Verificar que PostgreSQL está corriendo
   - Verificar credenciales en `.env`

---

### Problema: Usuarios no pueden hacer login

**Síntomas**: Error "Invalid credentials" con password correcto.

**Causa**: Hash de password incompatible (migraste de SQLite a PostgreSQL).

**Solución**: Recrear password del usuario:
```python
# En Flask Shell
from infocodest.models.users import User
from infocodest.extensions import db

user = User.query.filter_by(username='admin').first()
user.password = 'nueva_password'  # Se hashea automáticamente
db.session.commit()
```

---

### Problema: Datos no se cargan

**Síntomas**: Pipeline ejecuta sin errores pero dashboard está vacío.

**Diagnóstico**:
```python
# En Flask Shell
from infocodest.models.metricas import Metrica

count = Metrica.query.count()
print(f"Total métricas en BD: {count}")
```

**Si count = 0**:
- Verificar que CSVs tienen datos
- Ejecutar pipeline con `--dry-run` para ver si detecta los datos
- Revisar logs/pipeline.log por errores

---

### Problema: Dashboard muy lento

**Síntomas**: Página tarda >10 segundos en cargar.

**Causas**:
1. **Base de datos lenta**: Agregar índices
2. **Muchos proyectos**: Implementar paginación (ya existe)
3. **Consultas N+1**: Optimizar queries con `joinedload`

**Solución temporal**:
- Agregar más RAM al servidor
- Usar PostgreSQL en lugar de SQLite
- Configurar caché (Redis)

---

## 📞 Soporte

### Recursos Adicionales

- 📖 **Guía de Usuario**: [USER_GUIDE.md](../user-guide/USER_GUIDE.md)
- 🔧 **Troubleshooting Técnico**: [TROUBLESHOOTING.md](../../TROUBLESHOOTING.md)
- 🗄️ **Configuración de BD**: [CONFIGURATION.md](../../CONFIGURATION.md)
- 📊 **Pipeline de Datos**: [DATA_PIPELINE.md](../../DATA_PIPELINE.md)

### Contacto

- 📧 **Email Soporte**: admin-dashboard@empresa.com
- 💬 **Slack**: #dashboard-sonar-admin
- 🎫 **Tickets**: [Portal de Soporte](https://soporte.empresa.com)
- 🐛 **Bugs**: [GitHub Issues](https://github.com/jfdelafuente/dashboardsonar-application-python/issues)

---

## 📚 Próximos Pasos

1. **Configura backups automáticos** (crítico para producción)
2. **Programa carga de datos diaria/semanal** según tus necesidades
3. **Crea tus primeros usuarios** para el equipo
4. **Monitorea logs regularmente** para detectar problemas temprano
5. **Lee la guía de usuario** para entender qué verán los usuarios finales

---

**Última actualización**: Diciembre 2025
**Versión del documento**: 1.0.0
**Autor**: Equipo de Sistemas
**Próxima revisión**: Marzo 2026
