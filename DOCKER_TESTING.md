# Testing Local con Docker - Guía Completa

Guía paso a paso para probar el despliegue Docker de la aplicación Dashboard SonarQube en tu máquina local.

## 📋 Tabla de Contenidos

1. [Pre-requisitos](#pre-requisitos)
2. [Plan de Testing](#plan-de-testing)
3. [Fase 1: Build y Startup](#fase-1-build-y-startup)
4. [Fase 2: Verificación de Servicios](#fase-2-verificación-de-servicios)
5. [Fase 3: Testing de Base de Datos](#fase-3-testing-de-base-de-datos)
6. [Fase 4: Testing de Aplicación Web](#fase-4-testing-de-aplicación-web)
7. [Fase 5: Testing de Datos](#fase-5-testing-de-datos-opcional)
8. [Fase 6: Testing de Comandos manage.py](#fase-6-testing-de-comandos-managepy)
9. [Fase 7: Testing de Logs y Volúmenes](#fase-7-testing-de-logs-y-volúmenes)
10. [Fase 8: Testing de Parada/Reinicio](#fase-8-testing-de-paradareinicio)
11. [Checklist de Testing](#checklist-de-testing)
12. [Troubleshooting](#troubleshooting)
13. [Tiempo Estimado](#tiempo-estimado)

---

## Pre-requisitos

### Software Requerido

- **Docker Engine**: 20.10+ o superior
- **Docker Compose**: 2.0+ o superior
- **Git**: Para clonar el repositorio
- **Editor de texto**: VS Code, Notepad++, etc.

### Verificar Instalación

```bash
# Verificar versión de Docker
docker --version
# Output esperado: Docker version 20.10.x o superior

# Verificar versión de Docker Compose
docker-compose --version
# Output esperado: Docker Compose version 2.x.x o superior

# Verificar que Docker está corriendo
docker ps
# Si funciona sin errores, Docker está activo
```

### Recursos del Sistema

- **RAM**: Mínimo 4GB disponible (recomendado 8GB)
- **Disco**: Mínimo 5GB libres
- **CPU**: 2 cores mínimo
- **Puertos**: 5000 y 5432 deben estar disponibles

```bash
# Windows: Verificar puertos en uso
netstat -ano | findstr ":5000"
netstat -ano | findstr ":5432"

# Linux/Mac: Verificar puertos en uso
lsof -i :5000
lsof -i :5432
```

---

## Plan de Testing

### Resumen de Fases

| Fase | Descripción | Tiempo | Crítica |
|------|-------------|--------|---------|
| 1 | Build y Startup | ~5 min | ✅ Sí |
| 2 | Verificación de Servicios | ~2 min | ✅ Sí |
| 3 | Testing de Base de Datos | ~3 min | ✅ Sí |
| 4 | Testing de Aplicación Web | ~5 min | ✅ Sí |
| 5 | Testing de Datos | ~5 min | ⚠️ Opcional |
| 6 | Testing de manage.py | ~3 min | ⚠️ Opcional |
| 7 | Testing de Logs | ~2 min | ⚠️ Opcional |
| 8 | Testing de Parada/Reinicio | ~2 min | ✅ Sí |

**Total Testing Básico**: ~15 minutos
**Total Testing Completo**: ~30 minutos

---

## Fase 1: Build y Startup

⏱️ **Tiempo estimado**: 5 minutos

### 1.1 Preparar el Entorno

```bash
# Ir al directorio del proyecto
cd "c:\My Program Files\workspace-claude\dashboardsonar-application-python"

# Verificar que estás en la rama correcta
git branch
# Debe mostrar: * feature/docker-deployment

# Verificar que los archivos Docker existen
ls -la | grep -i docker
# Debe mostrar: Dockerfile, docker-compose.yml, .dockerignore
```

### 1.2 Configurar Variables de Entorno

```bash
# Copiar template de variables de entorno
cp .env.docker .env

# Editar el archivo .env
code .env
# O usar tu editor preferido: notepad .env
```

**Contenido mínimo requerido para `.env`:**

```env
# Flask Configuration
DEBUG=True
TESTING=False
PORT=5000

# Security - IMPORTANTE: Generar nueva clave
SECRET_KEY=CAMBIA_ESTO_POR_UNA_CLAVE_SEGURA

# Database Configuration
DB_NAME=dashboardsonar
DB_USERNAME=postgres
DB_PASS=testpass123

# Application Settings
DAYS_COMPARISON=15
```

**CRÍTICO - Generar SECRET_KEY segura:**

```bash
# Ejecutar este comando para generar una clave
python -c "import secrets; print(secrets.token_hex(32))"

# Copiar el output y pegarlo en .env como SECRET_KEY
# Ejemplo de output:
# a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Archivo `.env` completo (ejemplo):**

```env
# Flask Configuration
DEBUG=True
TESTING=False
PORT=5000

# Security
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# Database Configuration
DB_NAME=dashboardsonar
DB_USERNAME=postgres
DB_PASS=testpass123

# Application Settings
ASSETS_ROOT=/static/assets
DAYS_COMPARISON=15

# Data Files
DATA_DIR=./datos
METRICAS_FILENAME=metricas.csv
HISTORICO_FILENAME=historico.csv
PROVEEDORES_FILENAME=proveedores.csv

# Logging
LOG_LEVEL=INFO
```

### 1.3 Build de las Imágenes Docker

```bash
# Build de las imágenes (primera vez toma ~3-5 minutos)
docker-compose build
```

**Output esperado:**

```
[+] Building 180.5s (18/18) FINISHED
 => [internal] load build definition from Dockerfile
 => [builder 1/6] FROM docker.io/library/python:3.11-slim
 => [builder 2/6] RUN apt-get update && apt-get install...
 => [builder 3/6] COPY requirements.txt .
 => [builder 4/6] RUN python -m venv /opt/venv
 => [builder 5/6] RUN pip install --no-cache-dir...
 => [stage-1 1/8] FROM docker.io/library/python:3.11-slim
 => [stage-1 2/8] RUN apt-get update && apt-get install...
 => [stage-1 3/8] RUN useradd -m -u 1000 appuser...
 => [stage-1 4/8] WORKDIR /app
 => [stage-1 5/8] COPY --from=builder /opt/venv /opt/venv
 => [stage-1 6/8] COPY --chown=appuser:appuser . .
 => [stage-1 7/8] USER appuser
 => [stage-1 8/8] RUN mkdir -p /app/logs /app/datos
 => exporting to image
 => => writing image sha256:abc123...
 => => naming to docker.io/library/dashboardsonar-application-python_web
```

**✅ Verificar éxito:**

- No debe haber errores rojos
- Debe terminar con `Successfully built` y `Successfully tagged`

**❌ Errores comunes:**

- `ERROR: failed to solve` → Revisar Dockerfile
- `pip install failed` → Revisar requirements.txt
- `COPY failed` → Verificar que los archivos existan

### 1.4 Iniciar los Servicios

```bash
# Iniciar en modo detached (background)
docker-compose up -d
```

**Output esperado:**

```
[+] Running 3/3
 ✔ Network dashboardsonar-application-python_app-network  Created
 ✔ Container dashboardsonar-db                            Started
 ✔ Container dashboardsonar-web                           Started
```

**Ver logs en tiempo real (opcional):**

```bash
# Seguir logs de todos los servicios
docker-compose logs -f

# Salir con Ctrl+C (los contenedores siguen corriendo)
```

**Output esperado en logs:**

```
dashboardsonar-db   | database system is ready to accept connections
dashboardsonar-web  | Using configuration: Development
dashboardsonar-web  | INFO: Application started - Config: DevelopmentConfig
dashboardsonar-web  | [INFO] Listening at: http://0.0.0.0:5000
```

---

## Fase 2: Verificación de Servicios

⏱️ **Tiempo estimado**: 2 minutos

### 2.1 Verificar Estado de Contenedores

```bash
# Ver estado de todos los contenedores
docker-compose ps
```

**Output esperado:**

```
NAME                   IMAGE                                      COMMAND                  SERVICE   CREATED         STATUS                   PORTS
dashboardsonar-db      postgres:16-alpine                        "docker-entrypoint.s…"   db        2 minutes ago   Up 2 minutes (healthy)   5432/tcp
dashboardsonar-web     dashboardsonar-application-python_web     "gunicorn --bind 0.0…"   web       2 minutes ago   Up 2 minutes (healthy)   0.0.0.0:5000->5000/tcp
```

**✅ Verificar:**

- STATUS debe ser `Up X minutes (healthy)` para ambos
- web debe mostrar puerto `0.0.0.0:5000->5000/tcp`

**❌ Si ves:**

- `Exited (1)` → Contenedor falló al iniciar (ver logs)
- `Up X minutes (unhealthy)` → Health check fallando

### 2.2 Verificar Health Checks

```bash
# Test health check del endpoint
curl http://localhost:5000/health
```

**Output esperado:**

```json
{"status":"healthy","database":"connected"}
```

**En Windows PowerShell:**

```powershell
Invoke-WebRequest -Uri http://localhost:5000/health | Select-Object -Expand Content
```

**❌ Si falla:**

```bash
# Ver logs del contenedor web
docker-compose logs web

# Ver si la base de datos está lista
docker-compose logs db | grep "ready to accept connections"
```

### 2.3 Verificar Conectividad de Base de Datos

```bash
# Probar conexión a PostgreSQL desde el host
docker-compose exec db pg_isready -U postgres
```

**Output esperado:**

```
/var/run/postgresql:5432 - accepting connections
```

**Probar desde el contenedor web:**

```bash
# Ejecutar comando db-status de manage.py
docker-compose exec web python manage.py db-status
```

**Output esperado:**

```
Using configuration: Development

=== Database Status ===

Database URI: postgresql://***:***@db:5432/dashboardsonar
✅ Database connection: OK

Users:
  Total: 0
  Admins: 0
  Regular: 0

Database Engine: postgresql
SQLAlchemy Version: 2.0.23
```

---

## Fase 3: Testing de Base de Datos

⏱️ **Tiempo estimado**: 3 minutos

### 3.1 Ejecutar Migraciones

```bash
# Aplicar migraciones de base de datos
docker-compose exec web flask db upgrade
```

**Output esperado:**

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial migration
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, Add users table
...
```

**✅ Verificar:**

- Debe terminar sin errores
- Debe mostrar "Running upgrade" para cada migración

**❌ Si falla:**

```bash
# Ver error completo
docker-compose logs web | grep -i error

# Reiniciar base de datos
docker-compose restart db

# Esperar 10 segundos y reintentar
sleep 10
docker-compose exec web flask db upgrade
```

### 3.2 Verificar Tablas Creadas

```bash
# Conectar a PostgreSQL
docker-compose exec db psql -U postgres -d dashboardsonar
```

**Dentro de psql:**

```sql
-- Listar todas las tablas
\dt

-- Output esperado:
--              List of relations
--  Schema |        Name        | Type  |  Owner
-- --------+--------------------+-------+----------
--  public | alembic_version    | table | postgres
--  public | historico_daily    | table | postgres
--  public | kpis               | table | postgres
--  public | proveedor          | table | postgres
--  public | registro           | table | postgres
--  public | users              | table | postgres

-- Verificar estructura de tabla users
\d users

-- Salir de psql
\q
```

### 3.3 Crear Usuarios de Prueba

**Opción A: Seed data automático (Rápido)**

```bash
# Crear 5 usuarios de prueba
docker-compose exec web python manage.py seed-data --users 5
```

**Output esperado:**

```
Using configuration: Development

=== Seed Sample Data ===

⚠️  This will create 5 test users. Continue? [y/N]: y
✅ Created admin: admin@test.com (password: Admin123!)

✅ Seed completed! Created 5 users.

⚠️  WARNING: These are TEST credentials. Do NOT use in production!
```

**Credenciales generadas:**

- **Admin**: `admin@test.com` / `Admin123!`
- **Users**: `user1@test.com`, `user2@test.com`, etc. / `User123!`

**Opción B: Crear admin manualmente (Interactivo)**

```bash
# Crear admin con validaciones
docker-compose exec web python manage.py create-admin
```

**Flujo interactivo:**

```
Using configuration: Development

=== Create Admin User ===

Email address: admin@example.com
Username (optional, press Enter to skip):
Password: ********
Confirm password: ********

✅ Admin user created successfully!
   Email: admin@example.com
   Admin: Yes
```

### 3.4 Verificar Usuarios Creados

```bash
# Listar todos los usuarios
docker-compose exec web python manage.py list-users
```

**Output esperado:**

```
Using configuration: Development

=== User List ===

Total users: 5

ID    Email                          Username             Admin    Created
-------------------------------------------------------------------------------------
5     admin@test.com                 admin                ✓ Yes    2025-12-19 16:30
4     user4@test.com                 user4                No       2025-12-19 16:30
3     user3@test.com                 user3                No       2025-12-19 16:30
2     user2@test.com                 user2                No       2025-12-19 16:30
1     user1@test.com                 user1                No       2025-12-19 16:30
```

---

## Fase 4: Testing de Aplicación Web

⏱️ **Tiempo estimado**: 5 minutos

### 4.1 Acceder a la Aplicación

**Abrir navegador en:**

```
http://localhost:5000
```

**✅ Verificar:**

- Página de login carga correctamente
- CSS se carga (página tiene estilos)
- No hay errores en la consola del navegador (F12)
- Logo y elementos visuales se ven correctamente

**❌ Si no carga:**

```bash
# Ver logs
docker-compose logs web

# Verificar que el puerto está abierto
docker-compose ps
# Debe mostrar: 0.0.0.0:5000->5000/tcp

# Probar desde consola
curl http://localhost:5000
```

### 4.2 Login con Usuario de Prueba

**Credenciales:**

```
Email: admin@test.com
Password: Admin123!
```

**✅ Verificar:**

- Login exitoso
- Redirige al dashboard/home
- Menú de navegación visible
- Usuario logueado aparece en la interfaz

**❌ Si falla el login:**

```bash
# Verificar que el usuario existe
docker-compose exec web python manage.py list-users

# Ver logs durante el intento de login
docker-compose logs -f web
# Intentar login de nuevo y ver errores
```

### 4.3 Navegar por la Aplicación

**Rutas a probar:**

1. **Home/Dashboard**: `/`
   - ✅ Carga sin errores
   - ✅ Widgets/cards visibles

2. **Métricas**: `/metricas/aplicacion`
   - ✅ Página carga
   - ✅ Tablas/gráficos (si hay datos)

3. **Charts**: `/charts/...`
   - ✅ Gráficos renderizan
   - ✅ No hay errores JS

4. **Logout**: `/accounts/logout`
   - ✅ Cierra sesión
   - ✅ Redirige a login

### 4.4 Verificar Logs de la Aplicación

```bash
# Ver logs en tiempo real
docker-compose exec web tail -f /app/logs/info.log

# Buscar errores
docker-compose exec web grep -i error /app/logs/info.log

# Ver últimas 50 líneas
docker-compose exec web tail -50 /app/logs/info.log
```

**✅ No deben aparecer:**

- `ERROR` en los logs durante navegación normal
- Stack traces de Python
- Errores de base de datos

---

## Fase 5: Testing de Datos (Opcional)

⏱️ **Tiempo estimado**: 5 minutos

### 5.1 Verificar Montaje de Datos

```bash
# Ver archivos CSV montados
docker-compose exec web ls -la /app/datos
```

**Output esperado:**

```
total 124
drwxr-xr-x 2 appuser appuser   4096 Dec 19 16:00 .
drwxr-xr-x 1 appuser appuser   4096 Dec 19 16:00 ..
-rw-r--r-- 1 appuser appuser  45678 Dec 15 12:00 historico.csv
-rw-r--r-- 1 appuser appuser  23456 Dec 15 12:00 metricas.csv
-rw-r--r-- 1 appuser appuser   1234 Dec 15 12:00 proveedores.csv
```

### 5.2 Cargar Datos CSV

**Opción A: Pipeline completo**

```bash
# Cargar datos + generar daily snapshots + stats + registro
docker-compose exec web python scripts/data/run_all_data_scripts.py
```

**Opción B: Solo cargar CSV**

```bash
# Cargar solo los datos CSV sin procesamiento
docker-compose exec web python scripts/data/load_data.py
```

**Output esperado:**

```
Loading data from CSV files...
✓ Loaded 1234 records from metricas.csv
✓ Loaded 5678 records from historico.csv
✓ Loaded 12 records from proveedores.csv
Data loading completed successfully!
```

### 5.3 Verificar Datos Cargados

```bash
# Conectar a PostgreSQL
docker-compose exec db psql -U postgres -d dashboardsonar
```

**En psql:**

```sql
-- Contar registros en cada tabla
SELECT COUNT(*) FROM registro;
SELECT COUNT(*) FROM historico_daily;
SELECT COUNT(*) FROM kpis;
SELECT COUNT(*) FROM proveedor;

-- Ver primeros registros
SELECT * FROM registro LIMIT 5;

-- Salir
\q
```

---

## Fase 6: Testing de Comandos manage.py

⏱️ **Tiempo estimado**: 3 minutos

### 6.1 Listar Comandos Disponibles

```bash
docker-compose exec web python manage.py commands
```

**Output esperado:**

```
Using configuration: Development

=== Available Management Commands ===

create-admin         Create an admin user with validation
list-users           List all users in the system
delete-user          Delete a user by email
make-admin           Promote a user to admin status
reset-password       Reset a user's password
db-status            Show database connection status
seed-data            Load sample data for development
commands             Show this help message

Flask built-in commands:
db init              Initialize migrations
db migrate           Create migration
db upgrade           Apply migrations
db downgrade         Revert migrations
routes               Show all routes
shell                Start interactive shell

Usage:
  python manage.py <command> [options]

Examples:
  python manage.py create-admin
  python manage.py list-users
  python manage.py delete-user --email user@example.com
```

### 6.2 Test: Promover Usuario a Admin

```bash
# Promover user1 a admin
docker-compose exec web python manage.py make-admin --email user1@test.com
```

**Output esperado:**

```
Using configuration: Development

=== Promote User to Admin: user1@test.com ===

✅ User user1@test.com promoted to admin successfully.
```

**Verificar:**

```bash
docker-compose exec web python manage.py list-users
# user1 debe aparecer con "✓ Yes" en columna Admin
```

### 6.3 Test: Reset Password

```bash
# Resetear contraseña de user2
docker-compose exec web python manage.py reset-password --email user2@test.com
```

**Flujo:**

```
Using configuration: Development

=== Reset Password: user2@test.com ===

New password: ********
Confirm new password: ********

✅ Password for user2@test.com reset successfully.
```

**Probar validación (ingresar password débil):**

```
New password: 123
Confirm new password: 123

❌ Password must be at least 8 characters long
Try another password? [y/N]: n
```

### 6.4 Test: Eliminar Usuario

```bash
# Eliminar user3
docker-compose exec web python manage.py delete-user --email user3@test.com
```

**Flujo:**

```
Using configuration: Development

=== Delete User: user3@test.com ===

User ID: 3
Email: user3@test.com
Username: user3
Admin: No

⚠️  Are you sure you want to delete this user? [y/N]: y

✅ User user3@test.com deleted successfully.
```

**Verificar:**

```bash
docker-compose exec web python manage.py list-users
# user3 NO debe aparecer
```

### 6.5 Resumen Final de Usuarios

```bash
docker-compose exec web python manage.py list-users
```

**Debe mostrar:**

- admin@test.com (Admin)
- user1@test.com (Admin) ← Promovido
- user2@test.com (Normal) ← Password reseteado
- user4@test.com (Normal)
- ~~user3@test.com~~ ← Eliminado

---

## Fase 7: Testing de Logs y Volúmenes

⏱️ **Tiempo estimado**: 2 minutos

### 7.1 Verificar Volúmenes Creados

```bash
# Listar volúmenes del proyecto
docker volume ls | grep dashboardsonar
```

**Output esperado:**

```
local     dashboardsonar-application-python_app_logs
local     dashboardsonar-application-python_postgres_data
```

### 7.2 Inspeccionar Volumen de Logs

```bash
# Ver detalles del volumen
docker volume inspect dashboardsonar-application-python_app_logs
```

**Output esperado (ejemplo):**

```json
[
    {
        "CreatedAt": "2025-12-19T16:30:00Z",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "dashboardsonar-application-python",
            "com.docker.compose.volume": "app_logs"
        },
        "Mountpoint": "/var/lib/docker/volumes/dashboardsonar-application-python_app_logs/_data",
        "Name": "dashboardsonar-application-python_app_logs",
        "Options": null,
        "Scope": "local"
    }
]
```

### 7.3 Acceder a Logs

```bash
# Ver logs en tiempo real
docker-compose exec web tail -f /app/logs/info.log

# Ver todos los archivos de log
docker-compose exec web ls -la /app/logs

# Leer log completo
docker-compose exec web cat /app/logs/info.log
```

### 7.4 Backup de Logs

```bash
# Copiar logs al host
docker cp dashboardsonar-web:/app/logs ./logs-backup

# Verificar archivos copiados
ls -la ./logs-backup
```

**Output esperado:**

```
total 48
drwxr-xr-x 2 user user  4096 Dec 19 16:45 .
drwxr-xr-x 8 user user  4096 Dec 19 16:45 ..
-rw-r--r-- 1 user user 12345 Dec 19 16:45 info.log
-rw-r--r-- 1 user user   456 Dec 19 16:45 error.log
```

### 7.5 Limpiar Logs Antiguos

```bash
# Eliminar logs de más de 7 días (ejemplo)
docker-compose exec web sh -c "find /app/logs -name '*.log' -mtime +7 -delete"

# Listar logs restantes
docker-compose exec web ls -la /app/logs
```

---

## Fase 8: Testing de Parada/Reinicio

⏱️ **Tiempo estimado**: 2 minutos

### 8.1 Parar Servicios

```bash
# Parar y eliminar contenedores (mantiene volúmenes)
docker-compose down
```

**Output esperado:**

```
[+] Running 3/3
 ✔ Container dashboardsonar-web     Removed
 ✔ Container dashboardsonar-db      Removed
 ✔ Network dashboardsonar-application-python_app-network  Removed
```

### 8.2 Verificar Contenedores Eliminados

```bash
# Listar contenedores (debe estar vacío)
docker-compose ps
```

**Output esperado:**

```
NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
```

### 8.3 Verificar Volúmenes Persisten

```bash
# Los volúmenes deben seguir existiendo
docker volume ls | grep dashboardsonar
```

**Output esperado:**

```
local     dashboardsonar-application-python_app_logs
local     dashboardsonar-application-python_postgres_data
```

✅ Los volúmenes NO se eliminaron (datos persisten)

### 8.4 Reiniciar Servicios

```bash
# Reiniciar servicios
docker-compose up -d
```

**Output esperado:**

```
[+] Running 3/3
 ✔ Network dashboardsonar-application-python_app-network  Created
 ✔ Container dashboardsonar-db                            Started
 ✔ Container dashboardsonar-web                           Started
```

### 8.5 Verificar Persistencia de Datos

```bash
# Listar usuarios (deben seguir existiendo)
docker-compose exec web python manage.py list-users
```

**✅ Debe mostrar:**

- Todos los usuarios que existían antes del `docker-compose down`
- user3 NO debe aparecer (fue eliminado antes)
- user1 sigue siendo admin

**✅ Verificar DB:**

```bash
docker-compose exec web python manage.py db-status
```

**Debe mostrar:**

- Total de usuarios igual que antes
- Base de datos conectada
- Datos intactos

---

## Checklist de Testing

Marca cada item conforme lo completes:

### Build & Startup

- [ ] `docker --version` muestra versión 20.10+
- [ ] `docker-compose --version` muestra versión 2.0+
- [ ] Archivo `.env` creado con SECRET_KEY única
- [ ] `docker-compose build` exitoso sin errores
- [ ] `docker-compose up -d` inicia ambos contenedores
- [ ] Contenedores en estado `healthy`

### Health Checks

- [ ] `curl http://localhost:5000/health` retorna `{"status":"healthy"}`
- [ ] `docker-compose ps` muestra STATUS `Up (healthy)`
- [ ] `pg_isready` confirma PostgreSQL activo

### Base de Datos

- [ ] `flask db upgrade` ejecuta sin errores
- [ ] Tablas creadas en PostgreSQL (`\dt` muestra tablas)
- [ ] `seed-data` crea usuarios correctamente
- [ ] `db-status` muestra conexión OK
- [ ] `list-users` muestra 5 usuarios

### Aplicación Web

- [ ] Página login carga en http://localhost:5000
- [ ] CSS/JS cargan correctamente (no errores 404)
- [ ] Login con `admin@test.com` / `Admin123!` funciona
- [ ] Dashboard carga sin errores
- [ ] Navegación entre páginas funciona
- [ ] Logout funciona correctamente

### Comandos manage.py

- [ ] `commands` lista todos los comandos
- [ ] `list-users` muestra tabla formateada
- [ ] `make-admin` promueve usuario correctamente
- [ ] `reset-password` valida contraseña fuerte
- [ ] `delete-user` elimina y pide confirmación
- [ ] Validaciones funcionan (email, password)

### Datos (Opcional)

- [ ] Archivos CSV visibles en `/app/datos`
- [ ] `load_data.py` carga datos sin errores
- [ ] Datos visibles en PostgreSQL

### Logs y Volúmenes

- [ ] Logs se escriben en `/app/logs/info.log`
- [ ] `docker volume ls` muestra volúmenes creados
- [ ] `docker cp` funciona para backup de logs
- [ ] Volúmenes persisten datos

### Parada/Reinicio

- [ ] `docker-compose down` limpia contenedores
- [ ] Volúmenes NO se eliminan con `down`
- [ ] `docker-compose up -d` restaura servicios
- [ ] Datos persisten después de reinicio
- [ ] Usuarios siguen existiendo post-restart

---

## Troubleshooting

### Problema: Build Falla

**Síntoma:**

```
ERROR: failed to solve: process "/bin/sh -c pip install..." did not complete successfully
```

**Solución:**

```bash
# Limpiar caché de Docker
docker system prune -a

# Rebuild sin caché
docker-compose build --no-cache

# Verificar requirements.txt
cat requirements.txt
```

### Problema: Puerto 5000 Ocupado

**Síntoma:**

```
Error: Bind for 0.0.0.0:5000 failed: port is already allocated
```

**Solución:**

```bash
# Windows: Encontrar proceso usando puerto 5000
netstat -ano | findstr :5000

# Matar proceso (reemplaza PID)
taskkill /PID 1234 /F

# O cambiar puerto en .env
PORT=8080
```

Actualizar `docker-compose.yml`:

```yaml
ports:
  - "8080:5000"
```

### Problema: Base de Datos No Conecta

**Síntoma:**

```
psycopg2.OperationalError: could not connect to server
```

**Solución:**

```bash
# Ver logs de DB
docker-compose logs db

# Verificar health check
docker-compose ps

# Reiniciar DB
docker-compose restart db

# Esperar 10 segundos
sleep 10

# Verificar conexión
docker-compose exec db pg_isready -U postgres
```

### Problema: Health Check Falla

**Síntoma:**

```
STATUS: Up X minutes (unhealthy)
```

**Solución:**

```bash
# Ver logs completos
docker-compose logs web

# Test manual del health check
docker-compose exec web curl http://localhost:5000/health

# Verificar que DB está lista
docker-compose exec db pg_isready -U postgres

# Si DB no está lista, esperar más tiempo
docker-compose restart web
```

### Problema: Permission Denied en Logs

**Síntoma:**

```
PermissionError: [Errno 13] Permission denied: '/app/logs/info.log'
```

**Solución:**

✅ **Ya está solucionado** con `app_logs` volume en la configuración actual.

Si persiste:

```bash
# Rebuild completo
docker-compose down
docker-compose up -d --build

# Verificar permisos
docker-compose exec web ls -la /app/logs
# Debe mostrar owner: appuser
```

### Problema: Contenedor Web Falla al Iniciar

**Síntoma:**

```
dashboardsonar-web    Exited (1)
```

**Solución:**

```bash
# Ver logs completos
docker-compose logs web

# Errores comunes:
# 1. SECRET_KEY no configurada
grep SECRET_KEY .env

# 2. Dependencias faltantes
docker-compose exec web pip list

# 3. Error de sintaxis en código
docker-compose exec web python -c "from infocodest import create_app"
```

### Problema: Volúmenes Llenos

**Síntoma:**

```
Error: No space left on device
```

**Solución:**

```bash
# Ver espacio usado por Docker
docker system df

# Limpiar volúmenes no usados
docker volume prune

# Limpiar todo (¡CUIDADO!)
docker system prune -a --volumes
```

### Problema: Migraciones Fallan

**Síntoma:**

```
ERROR [alembic.util.messaging] Target database is not up to date
```

**Solución:**

```bash
# Ver historial de migraciones
docker-compose exec web flask db history

# Ver estado actual
docker-compose exec web flask db current

# Forzar a última versión
docker-compose exec web flask db stamp head

# Reintentar upgrade
docker-compose exec web flask db upgrade
```

---

## Tiempo Estimado

### Testing Básico (Mínimo)

| Fase | Tiempo |
|------|--------|
| Build y Startup | 5 min |
| Verificación de Servicios | 2 min |
| Testing de Base de Datos | 3 min |
| Testing de Aplicación Web | 5 min |
| Parada/Reinicio | 2 min |
| **TOTAL** | **~17 min** |

### Testing Completo

| Fase | Tiempo |
|------|--------|
| Build y Startup | 5 min |
| Verificación de Servicios | 2 min |
| Testing de Base de Datos | 3 min |
| Testing de Aplicación Web | 5 min |
| Testing de Datos | 5 min |
| Testing de manage.py | 3 min |
| Testing de Logs | 2 min |
| Parada/Reinicio | 2 min |
| **TOTAL** | **~27 min** |

### Con Troubleshooting

| Escenario | Tiempo |
|-----------|--------|
| Sin problemas | 15-30 min |
| Problemas menores | 30-45 min |
| Problemas mayores | 45-60 min |

---

## Próximos Pasos

Una vez completado el testing local exitosamente:

1. **Code Review** - Revisar código con el equipo
2. **Merge** - Integrar a rama `develop` o `main`
3. **Tag de Versión** - Crear tag (ej: `v1.1.0-docker`)
4. **Despliegue Staging** - Probar en ambiente de staging
5. **Despliegue Producción** - Deploy final a producción

---

## Referencias

- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Guía completa de despliegue
- [README.md](README.md) - Documentación principal del proyecto
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

📖 Generated with [Claude Code](https://claude.com/claude-code)
