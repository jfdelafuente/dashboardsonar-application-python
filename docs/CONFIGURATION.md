# Configuration Guide

**Dashboard Sonar Application - Configuration System**

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Configuraciones Disponibles](#configuraciones-disponibles)
3. [Database Configuration](#database-configuration)
4. [Cómo Cambiar entre SQLite y PostgreSQL](#cómo-cambiar-entre-sqlite-y-postgresql)
5. [Variables de Entorno](#variables-de-entorno)
6. [Ejemplos de Uso](#ejemplos-de-uso)

## Descripción General

El sistema de configuración utiliza **archivos de configuración por entorno** ubicados en el directorio `config/`:

- **base.py**: Configuración compartida por todos los entornos
- **development.py**: Configuración para desarrollo
- **testing.py**: Configuración para testing
- **production.py**: Configuración para producción

Las configuraciones se cargan automáticamente desde variables de entorno definidas en el archivo `.env`.

## Configuraciones Disponibles

### Development (Desarrollo)

**Archivo**: `config/development.py`

**Características**:
- Debug mode: **ACTIVADO**
- Database: **Auto-detecta** PostgreSQL/MySQL o SQLite
- SQLALCHEMY_ECHO: **True** (muestra queries SQL en consola)
- CSRF: **Desactivado** (para facilitar testing manual)
- Log Level: **DEBUG**

**Auto-detección de base de datos**:
- Si `DB_ENGINE` y `DB_USERNAME` están configurados → usa PostgreSQL/MySQL
- Si no están configurados → usa SQLite (por defecto)

### Testing (Pruebas)

**Archivo**: `config/testing.py`

**Características**:
- Testing mode: **ACTIVADO**
- Database: **SQLite en memoria** (`:memory:`)
- CSRF: **Desactivado**
- Log Level: **INFO**

### Production (Producción)

**Archivo**: `config/production.py`

**Características**:
- Debug mode: **DESACTIVADO**
- Database: **PostgreSQL/MySQL** (obligatorio)
- SECRET_KEY: **Validación estricta** (debe estar configurado)
- CSRF: **Activado**
- Session cookies: **Secure** (solo HTTPS)
- Log Level: **WARNING**

## Database Configuration

### Opción 1: Development con SQLite (Default)

**No requiere configuración** - simplemente omite las variables de PostgreSQL en `.env`:

```env
# .env - Development con SQLite
FLASK_DEBUG=1
DEBUG=True
SECRET_KEY=your-secret-key-for-development

# NO configurar DB_ENGINE ni DB_USERNAME
# La aplicación usará SQLite automáticamente
```

**Resultado**: `sqlite:///db.sqlite3`

---

### Opción 2: Development con PostgreSQL

**Auto-detecta PostgreSQL** cuando configuras `DB_ENGINE` y `DB_USERNAME` en `.env`:

```env
# .env - Development con PostgreSQL
FLASK_DEBUG=1
DEBUG=True
SECRET_KEY=your-secret-key-for-development

# Configuración de PostgreSQL para Development
DB_ENGINE=postgresql
DB_USERNAME=postgres
DB_PASS=mypassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar_dev
```

**Resultado**: `postgresql://postgres:mypassword@localhost:5432/dashboardsonar_dev`

**Valores por defecto** si no se especifican:
- `DB_HOST`: `localhost`
- `DB_PORT`: Se usa el puerto por defecto del motor (5432 para PostgreSQL)
- `DB_NAME`: `dashboardsonar_dev`

---

### Opción 3: Development con MySQL

```env
# .env - Development con MySQL
FLASK_DEBUG=1
DEBUG=True
SECRET_KEY=your-secret-key-for-development

# Configuración de MySQL para Development
DB_ENGINE=mysql
DB_USERNAME=root
DB_PASS=mypassword
DB_HOST=localhost
DB_PORT=3306
DB_NAME=dashboardsonar_dev
```

**Resultado**: `mysql://root:mypassword@localhost:3306/dashboardsonar_dev`

---

### Opción 4: Production con PostgreSQL

**Requiere todas las variables** configuradas:

```env
# .env - Production
FLASK_DEBUG=0
DEBUG=False
SECRET_KEY=generated-secret-key-minimum-32-chars

# Configuración de PostgreSQL para Production
DB_ENGINE=postgresql
DB_USERNAME=dbuser
DB_PASS=securepassword
DB_HOST=db.example.com
DB_PORT=5432
DB_NAME=dashboardsonar
```

**Validación estricta**:
- `SECRET_KEY` debe tener al menos 32 caracteres
- `SECRET_KEY` no puede ser el valor por defecto
- `DB_ENGINE`, `DB_USERNAME` y `DB_NAME` son obligatorios

---

## Cómo Cambiar entre SQLite y PostgreSQL

### Escenario 1: De SQLite a PostgreSQL en Development

**Paso 1**: Asegúrate de tener PostgreSQL instalado y corriendo

**Paso 2**: Crea la base de datos:
```bash
# En PostgreSQL
createdb dashboardsonar_dev
```

**Paso 3**: Edita tu `.env` y añade las variables de PostgreSQL:
```env
# Añadir estas líneas al .env
DB_ENGINE=postgresql
DB_USERNAME=postgres
DB_PASS=tu_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar_dev
```

**Paso 4**: Ejecuta la configuración de base de datos:
```bash
# Windows
setup_database.bat

# Linux/macOS
./setup_database.sh
```

**Paso 5**: Verifica que está usando PostgreSQL:
```bash
flask shell
>>> from flask import current_app
>>> print(current_app.config['SQLALCHEMY_DATABASE_URI'])
# Debería mostrar: postgresql://postgres:***@localhost:5432/dashboardsonar_dev
```

---

### Escenario 2: De PostgreSQL a SQLite en Development

**Paso 1**: Edita tu `.env` y comenta/elimina las variables de PostgreSQL:
```env
# Comentar o eliminar estas líneas
# DB_ENGINE=postgresql
# DB_USERNAME=postgres
# DB_PASS=tu_password
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=dashboardsonar_dev
```

**Paso 2**: Opcionalmente, especifica el archivo SQLite:
```env
# Opcional - usa un archivo SQLite específico
SQLITE_DB_FILE=db.sqlite3
```

**Paso 3**: Ejecuta la configuración de base de datos:
```bash
# Windows
setup_database.bat

# Linux/macOS
./setup_database.sh
```

**Paso 4**: Verifica que está usando SQLite:
```bash
flask shell
>>> from flask import current_app
>>> print(current_app.config['SQLALCHEMY_DATABASE_URI'])
# Debería mostrar: sqlite:///C:\path\to\db.sqlite3
```

---

## Variables de Entorno

### Variables de Base de Datos

| Variable | Requerido | Valores | Descripción |
|----------|-----------|---------|-------------|
| `DB_ENGINE` | Condicional | `postgresql`, `mysql`, `sqlite` | Motor de base de datos |
| `DB_USERNAME` | Condicional | String | Usuario de base de datos |
| `DB_PASS` | Opcional | String | Contraseña de base de datos |
| `DB_HOST` | Opcional | String | Host (default: `localhost`) |
| `DB_PORT` | Opcional | Integer | Puerto (default: según motor) |
| `DB_NAME` | Opcional | String | Nombre de BD (default: `dashboardsonar_dev` en Development) |
| `SQLITE_DB_FILE` | Opcional | String | Archivo SQLite (default: `db.sqlite3`) |

**Lógica de detección en Development**:
- Si `DB_ENGINE` está configurado **Y** `DB_USERNAME` está configurado **Y** `DB_ENGINE` no es `sqlite`:
  - → Usa PostgreSQL/MySQL
- Si no:
  - → Usa SQLite

### Variables de Aplicación

| Variable | Requerido | Valores | Descripción |
|----------|-----------|---------|-------------|
| `SECRET_KEY` | Sí (Production) | String (min 32 chars) | Clave secreta para sesiones |
| `FLASK_APP` | No | String | Punto de entrada (default: `run.py`) |
| `FLASK_DEBUG` | No | `0`, `1` | Debug mode |
| `DEBUG` | No | `True`, `False` | Debug mode (debe coincidir con FLASK_DEBUG) |
| `TESTING` | No | `True`, `False` | Testing mode |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Nivel de logging |
| `DAYS_COMPARISON` | No | Integer | Días para comparación de métricas (default: 15) |

### Variables de Datos

| Variable | Requerido | Valores | Descripción |
|----------|-----------|---------|-------------|
| `DATA_DIR` | No | String | Directorio de archivos CSV (default: `./datos`) |
| `METRICAS_FILENAME` | No | String | Archivo CSV de métricas (default: `metricas.csv`) |
| `HISTORICO_FILENAME` | No | String | Archivo CSV de histórico (default: `historico.csv`) |
| `PROVEEDORES_FILENAME` | No | String | Archivo CSV de proveedores (default: `proveedores.csv`) |

---

## Ejemplos de Uso

### Ejemplo 1: Desarrollo rápido con SQLite

```env
# .env
FLASK_APP=run.py
FLASK_DEBUG=1
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production

# No configurar variables de PostgreSQL
# La aplicación usará SQLite automáticamente
```

**Ejecutar**:
```bash
setup_database.bat
flask run
```

---

### Ejemplo 2: Desarrollo con PostgreSQL local

```env
# .env
FLASK_APP=run.py
FLASK_DEBUG=1
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production

# PostgreSQL Development
DB_ENGINE=postgresql
DB_USERNAME=postgres
DB_PASS=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar_dev
```

**Preparación**:
```bash
# Crear base de datos
createdb dashboardsonar_dev

# Setup
setup_database.bat

# Verificar
flask shell
>>> from flask import current_app
>>> print(current_app.config['SQLALCHEMY_DATABASE_URI'])
```

---

### Ejemplo 3: PostgreSQL con Docker

```env
# .env
FLASK_APP=run.py
FLASK_DEBUG=1
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production

# PostgreSQL en Docker
DB_ENGINE=postgresql
DB_USERNAME=dashuser
DB_PASS=dashpass
DB_HOST=localhost
DB_PORT=5433
DB_NAME=dashboardsonar_dev
```

**Docker Compose**:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: dashuser
      POSTGRES_PASSWORD: dashpass
      POSTGRES_DB: dashboardsonar_dev
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Ejecutar**:
```bash
# Iniciar PostgreSQL en Docker
docker-compose up -d

# Setup base de datos
setup_database.bat

# Ejecutar aplicación
flask run
```

---

### Ejemplo 4: Testing con SQLite en memoria

```env
# .env
FLASK_APP=run.py
TESTING=True
SECRET_KEY=test-secret-key

# Testing usa SQLite en memoria automáticamente
# No necesita configuración adicional
```

**Ejecutar tests**:
```bash
pytest
pytest --cov=infocodest
```

---

### Ejemplo 5: Production con PostgreSQL

```env
# .env
FLASK_APP=run.py
FLASK_DEBUG=0
DEBUG=False
SECRET_KEY=generatedwithpythonsecretstokenhex32chars

# PostgreSQL Production
DB_ENGINE=postgresql
DB_USERNAME=produser
DB_PASS=securepasswordhere
DB_HOST=db.production.com
DB_PORT=5432
DB_NAME=dashboardsonar

# Logging
LOG_LEVEL=WARNING
```

**Ejecutar**:
```bash
# Setup (solo primera vez o en migraciones)
setup_database.bat Production

# Ejecutar aplicación
set FLASK_CONFIG=Production
flask run
```

---

## Troubleshooting

### Error: "DB_ENGINE not set"

**Causa**: Intentas usar Development con PostgreSQL pero falta `DB_ENGINE`.

**Solución**:
```env
# Añadir a .env
DB_ENGINE=postgresql
```

---

### Error: "DB_USERNAME not set"

**Causa**: Intentas usar Development con PostgreSQL pero falta `DB_USERNAME`.

**Solución**:
```env
# Añadir a .env
DB_USERNAME=postgres
```

---

### Error: "SECRET_KEY environment variable is required in production"

**Causa**: Production requiere `SECRET_KEY` configurado explícitamente.

**Solución**:
```bash
# Generar SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Añadir a .env
SECRET_KEY=output-del-comando-anterior
```

---

### Problema: No sé qué base de datos está usando

**Solución**: Verificar desde Flask shell
```bash
flask shell
>>> from flask import current_app
>>> print(current_app.config['SQLALCHEMY_DATABASE_URI'])
```

---

### Problema: La aplicación usa SQLite cuando debería usar PostgreSQL

**Causa**: Las variables `DB_ENGINE` o `DB_USERNAME` no están configuradas correctamente en `.env`.

**Solución**:
1. Verificar que `.env` existe en la raíz del proyecto
2. Verificar que las variables están **sin comentar** en `.env`:
   ```env
   DB_ENGINE=postgresql  # No debe tener # al inicio
   DB_USERNAME=postgres  # No debe tener # al inicio
   ```
3. Reiniciar la aplicación

---

**Última actualización**: Diciembre 2025
**Versión de la guía**: 1.0
