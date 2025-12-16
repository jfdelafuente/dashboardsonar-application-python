# Troubleshooting Guide

**Dashboard Sonar Application - Resolución de Problemas**

## Tabla de Contenidos

1. [Problemas de Autenticación](#problemas-de-autenticación)
2. [Problemas de Base de Datos](#problemas-de-base-de-datos)
3. [Problemas de Migración](#problemas-de-migración)
4. [Problemas de Configuración](#problemas-de-configuración)
5. [Problemas de Dependencias](#problemas-de-dependencias)

---

## Problemas de Autenticación

### Error: `AttributeError: 'str' object has no attribute 'decode'`

**Descripción del Error:**
```python
File "infocodest/services/auth_service.py", line 56, in authenticate_user
  if user and verify_pass(password, user.password):
AttributeError: 'str' object has no attribute 'decode'
```

**Causa:**
Este error ocurre cuando cambias de SQLite a PostgreSQL (o viceversa) y la forma en que se almacenan las contraseñas hasheadas es diferente:
- **SQLite**: Almacena el hash como `String` (texto)
- **PostgreSQL**: Puede almacenar el hash como `bytes` o `String` dependiendo de la configuración

**Solución:**

Este problema ya está resuelto en la versión actual del código. La función `verify_pass()` ahora maneja automáticamente ambos tipos:

```python
# En infocodest/utils/security.py
def verify_pass(provided_password, stored_password):
    # Handle both bytes (PostgreSQL) and str (SQLite) stored passwords
    if isinstance(stored_password, bytes):
        stored_password = stored_password.decode("ascii")
    # ... resto del código
```

**Si sigues viendo este error:**

1. Asegúrate de tener la última versión del código:
   ```bash
   git pull origin develop
   ```

2. Si tienes usuarios existentes en la base de datos, puede que necesites recrear las contraseñas:
   ```python
   # En flask shell
   from infocodest.models.users import User
   from infocodest.utils.security import hash_pass
   from infocodest.extensions import db

   user = User.query.filter_by(username='admin').first()
   user.password = hash_pass('nueva_contraseña')
   db.session.commit()
   ```

---

### Error: `psycopg2.errors.StringDataRightTruncation: value too long for type character varying(256)`

**Descripción del Error:**

```python
psycopg2.errors.StringDataRightTruncation: value too long for type character varying(256)
[SQL: INSERT INTO users (username, email, password, ...) VALUES (...)]
[parameters: {'password': b'6a37d6ade0465814...', ...}]
```

**Causa:**
Este error ocurre cuando se intenta crear un usuario en PostgreSQL y el hash de la contraseña se pasa como `bytes` en lugar de `string`. Los bytes ocupan más espacio cuando se convierten y exceden el límite VARCHAR(256).

**Solución:**

Este problema ya está resuelto en la versión actual del código. El modelo `User` ahora decodifica automáticamente el hash a string:

```python
# En infocodest/models/users.py
if property == "password":
    value = hash_pass(value)  # Returns bytes
    # Decode to string for database storage
    if isinstance(value, bytes):
        value = value.decode("ascii")
```

**Si sigues viendo este error:**

1. Asegúrate de tener la última versión del código:
   ```bash
   git pull origin develop
   ```

2. Si usas `setup_database.sh` o `setup_database.bat`, el script debería funcionar correctamente ahora.

3. Si creas usuarios manualmente, asegúrate de usar el modelo User:

   ```python
   # CORRECTO (automáticamente decodifica)
   user = User(username='admin', email='admin@example.com', password='password')

   # INCORRECTO (no uses hash_pass directamente)
   # user.password = hash_pass('password')  # Esto dará bytes
   ```

---

### Error: Login falla después de migrar de SQLite a PostgreSQL

**Causa:**
Las contraseñas hasheadas pueden tener un formato ligeramente diferente entre bases de datos.

**Solución:**

Opción 1: Recrear usuarios en PostgreSQL:
```bash
# Conectar a flask shell
flask shell

# Importar modelos
from infocodest.models.users import User
from infocodest.extensions import db

# Crear nuevo usuario admin
admin = User(
    username='admin',
    email='admin@example.com',
    password='tu_password_segura',  # Se hasheará automáticamente
    is_admin=True
)
db.session.add(admin)
db.session.commit()
```

Opción 2: Exportar/importar usuarios:
```bash
# En SQLite (antes de migrar)
python scripts/export_users.py > users.json

# En PostgreSQL (después de migrar)
python scripts/import_users.py < users.json
```

---

## Problemas de Base de Datos

### Error: `ModuleNotFoundError: No module named 'psycopg2'`

**Causa:**
Falta el driver de PostgreSQL para Python.

**Solución:**
```bash
pip install psycopg2-binary==2.9.11
```

O reinstalar todas las dependencias:
```bash
pip install -r requirements.txt
```

---

### Error: `connection to server at "X.X.X.X", port 5432 failed: Connection timed out`

**Causa:**
No se puede conectar al servidor PostgreSQL.

**Soluciones:**

1. **Verificar que PostgreSQL está corriendo:**
   ```bash
   # En Linux
   sudo systemctl status postgresql

   # En Windows (PowerShell como admin)
   Get-Service -Name postgresql*
   ```

2. **Verificar credenciales en `.env`:**
   ```env
   DB_ENGINE=postgresql
   DB_USERNAME=postgres
   DB_PASS=tu_password
   DB_HOST=localhost  # Cambiar si es remoto
   DB_PORT=5432
   DB_NAME=dashboardsonar_dev
   ```

3. **Verificar conectividad de red:**
   ```bash
   # Probar conexión
   telnet 192.168.1.14 5432

   # O con psql
   psql -h 192.168.1.14 -U postgres -d dashboardsonar_dev
   ```

4. **Verificar firewall:**
   - En servidor PostgreSQL, asegurarse de que el puerto 5432 está abierto
   - Verificar `pg_hba.conf` para permitir conexiones remotas

5. **Volver a SQLite temporalmente:**
   ```env
   # Comentar en .env:
   # DB_ENGINE=postgresql
   # DB_USERNAME=postgres
   # ...

   # La aplicación usará SQLite automáticamente
   ```

---

### Error: `FATAL: database "dashboardsonar_dev" does not exist`

**Causa:**
La base de datos no ha sido creada en PostgreSQL.

**Solución:**
```bash
# Crear la base de datos
createdb dashboardsonar_dev

# O con psql
psql -U postgres
CREATE DATABASE dashboardsonar_dev;
\q

# Luego ejecutar setup
setup_database.bat
```

---

### Error: `FATAL: role "dbuser" does not exist`

**Causa:**
El usuario de PostgreSQL no existe.

**Solución:**
```bash
# Crear usuario en PostgreSQL
psql -U postgres
CREATE USER dbuser WITH PASSWORD 'dbpassword';
GRANT ALL PRIVILEGES ON DATABASE dashboardsonar_dev TO dbuser;
\q
```

---

## Problemas de Migración

### Error: `Target database is not up to date`

**Causa:**
Alembic no tiene registro de las tablas existentes.

**Solución:**
```bash
# Marcar la base de datos como actualizada
flask db stamp head

# Luego puedes crear nuevas migraciones
flask db migrate -m "descripcion"
```

---

### Error: Migración falla con `table already exists`

**Causa:**
Las tablas ya existen en la base de datos pero Alembic no lo sabe.

**Solución:**

Opción 1: Stamp current:
```bash
# Si las tablas ya están correctas
flask db stamp head
```

Opción 2: Drop y recrear (CUIDADO: perderás datos):
```bash
# Solo en desarrollo
python -c "from infocodest import create_app; from infocodest.extensions import db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"

# Luego stamp
flask db stamp head
```

Opción 3: Migración manual:
```bash
# Editar el archivo de migración generado
# Comentar las líneas que crean tablas existentes
flask db upgrade
```

---

### Error: No se puede generar migración porque no conecta a PostgreSQL

**Causa:**
PostgreSQL está configurado en `.env` pero no está accesible.

**Solución Temporal:**

Generar migración con SQLite:
```bash
# Opción 1: Comentar temporalmente en .env
# DB_ENGINE=postgresql
# DB_USERNAME=...

# Generar migración
flask db migrate -m "descripcion"

# Descomentar variables de PostgreSQL

# Aplicar migración en PostgreSQL cuando esté accesible
flask db upgrade
```

---

## Problemas de Configuración

### Error: `SECRET_KEY environment variable is required in production`

**Causa:**
Falta configurar `SECRET_KEY` en Production.

**Solución:**
```bash
# Generar SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Añadir a .env
SECRET_KEY=output_del_comando_anterior
```

---

### Problema: La aplicación usa SQLite cuando debería usar PostgreSQL

**Causa:**
Las variables de entorno no están correctamente configuradas.

**Solución:**

1. Verificar que `.env` existe en la raíz del proyecto

2. Verificar que las variables NO están comentadas:
   ```env
   # INCORRECTO (comentadas):
   # DB_ENGINE=postgresql
   # DB_USERNAME=postgres

   # CORRECTO (sin #):
   DB_ENGINE=postgresql
   DB_USERNAME=postgres
   DB_PASS=password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=dashboardsonar_dev
   ```

3. Verificar desde Flask Shell:
   ```bash
   flask shell
   >>> from flask import current_app
   >>> print(current_app.config['SQLALCHEMY_DATABASE_URI'])
   # Debería mostrar postgresql://... y no sqlite:///...
   ```

4. Reiniciar la aplicación después de cambiar `.env`

---

### Error: `FileNotFoundError: [Errno 2] No such file or directory: '.env'`

**Causa:**
El archivo `.env` no existe.

**Solución:**
```bash
# Copiar desde el ejemplo
cp .env.example .env

# Editar con tus valores
# En Windows:
notepad .env

# En Linux/macOS:
nano .env
```

---

## Problemas de Dependencias

### Error: `No module named 'pandas'`

**Causa:**
Faltan dependencias del proyecto.

**Solución:**
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# O solo pandas
pip install pandas==2.1.4 numpy==1.26.2
```

---

### Error: Conflictos de versiones al instalar requirements

**Causa:**
Versiones incompatibles o entorno virtual corrupto.

**Solución:**
```bash
# Recrear entorno virtual
deactivate
rm -rf venv  # o rmdir /s venv en Windows
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Error: `ImportError: cannot import name 'X' from 'Y'`

**Causa:**
Versión incorrecta de paquete instalada.

**Solución:**
```bash
# Ver versiones instaladas
pip list

# Comparar con requirements.txt
# Si hay diferencias, reinstalar:
pip uninstall paquete-problematico
pip install paquete-problematico==version-correcta

# O reinstalar todo
pip install -r requirements.txt --force-reinstall
```

---

## Problemas de Windows

### Error: `'flask' is not recognized as an internal or external command`

**Causa:**
El entorno virtual no está activado o Flask no está instalado.

**Solución:**
```bash
# Activar entorno virtual
venv\Scripts\activate

# Verificar que muestra (venv) al inicio del prompt
# Luego instalar Flask si es necesario
pip install -r requirements.txt
```

---

### Error: Encoding issues con caracteres especiales

**Causa:**
Problemas de codificación en Windows.

**Solución:**
```bash
# Configurar encoding UTF-8
set PYTHONIOENCODING=utf-8

# En PowerShell
$env:PYTHONIOENCODING="utf-8"

# Ejecutar aplicación
flask run
```

---

## Problemas de Linux/macOS

### Error: `Permission denied` al ejecutar scripts `.sh`

**Causa:**
Falta permiso de ejecución.

**Solución:**
```bash
# Dar permisos de ejecución
chmod +x setup_database.sh
chmod +x load_data.sh

# Ejecutar
./setup_database.sh
```

---

### Error: `python: command not found`

**Causa:**
En algunos sistemas, Python 3 se llama `python3`.

**Solución:**
```bash
# Usar python3
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

# O crear alias
alias python=python3
```

---

## Verificación del Sistema

### Script de verificación rápida

Crear archivo `verify_system.py`:

```python
#!/usr/bin/env python
"""Verify system configuration and dependencies."""

import sys
import os

def verify_system():
    print("=== System Verification ===\n")

    # Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK\n")

    # .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("❌ .env file missing")
        print("   Run: cp .env.example .env\n")
        return False

    # Virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment active\n")
    else:
        print("⚠️  Virtual environment not detected")
        print("   Run: python -m venv venv && venv\\Scripts\\activate\n")

    # Dependencies
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        print("❌ Flask not installed")
        return False

    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        return False

    # Database drivers
    try:
        import psycopg2
        print(f"✅ psycopg2 installed (PostgreSQL support)")
    except ImportError:
        print("⚠️  psycopg2 not installed (no PostgreSQL support)")

    print("\n✅ System verification completed")
    return True

if __name__ == '__main__':
    verify_system()
```

Ejecutar:
```bash
python verify_system.py
```

---

## Soporte Adicional

Si el problema persiste después de intentar estas soluciones:

1. **Revisar logs**: Consulta `logs/` para mensajes de error detallados

2. **Modo DEBUG**: Activa debug en `.env`:
   ```env
   FLASK_DEBUG=1
   DEBUG=True
   LOG_LEVEL=DEBUG
   ```

3. **Crear Issue**: https://github.com/jfdelafuente/dashboardsonar-application-python/issues

4. **Documentación**:
   - [SETUP.md](../SETUP.md) - Guía de instalación
   - [CONFIGURATION.md](CONFIGURATION.md) - Guía de configuración
   - [DEPENDENCIES.md](DEPENDENCIES.md) - Guía de dependencias

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0
