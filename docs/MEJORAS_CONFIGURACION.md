# Mejoras del Sistema de Configuración

Este documento detalla las mejoras propuestas para el sistema de configuración de Dashboard Sonar, organizadas por prioridad.

## Tabla de Contenidos

- [Alta Prioridad](#alta-prioridad)
  - [1. Validación estricta de SECRET_KEY en producción](#1-validación-estricta-de-secret_key-en-producción)
  - [2. Consolidar lógica de enmascaramiento de URIs](#2-consolidar-lógica-de-enmascaramiento-de-uris)
  - [3. Escapar componentes de Database URI](#3-escapar-componentes-de-database-uri)
  - [4. Documentar variables de entorno requeridas](#4-documentar-variables-de-entorno-requeridas)
- [Media Prioridad](#media-prioridad)
  - [5. Función centralizada para construcción de Database URIs](#5-función-centralizada-para-construcción-de-database-uris)
  - [6. Integrar str_to_bool para lectura de booleanos](#6-integrar-str_to_bool-para-lectura-de-booleanos)
  - [7. Hacer configurables los nombres de bases de datos SQLite](#7-hacer-configurables-los-nombres-de-bases-de-datos-sqlite)
  - [8. Implementar validación de ASSETS_ROOT](#8-implementar-validación-de-assets_root)
- [Baja Prioridad](#baja-prioridad)
  - [9. Añadir type hints a clases de configuración](#9-añadir-type-hints-a-clases-de-configuración)
  - [10. Implementar LOG_LEVEL en BaseConfig](#10-implementar-log_level-en-baseconfig)
  - [11. Llamar validate_config automáticamente](#11-llamar-validate_config-automáticamente)

---

## Alta Prioridad

### 1. Validación estricta de SECRET_KEY en producción

**Problema:**
BaseConfig genera un SECRET_KEY aleatorio si no existe, lo cual es peligroso en producción porque:
- La clave cambia en cada reinicio, invalidando todas las sesiones
- En despliegues multi-proceso, cada worker podría tener una clave diferente
- Los usuarios serán deslogueados constantemente

**Archivos afectados:**
- `config/base.py:16-18`
- `config/production.py`

**Implementación:**

#### Opción A: Validación en ProductionConfig (Recomendada)

```python
# config/production.py
import os
from pathlib import Path
from .base import BaseConfig

# Leer variables de entorno
DB_ENGINE = os.getenv('DB_ENGINE', None)
DB_USERNAME = os.getenv('DB_USERNAME', None)
DB_PASSWORD = os.getenv('DB_PASS', None)
DB_HOST = os.getenv('DB_HOST', None)
DB_PORT = os.getenv('DB_PORT', None)
DB_NAME = os.getenv('DB_NAME', None)

basedir = Path(__file__).resolve().parent.parent

class ProductionConfig(BaseConfig):
    """Production configuration - requires strict environment setup."""

    DEBUG = False
    TESTING = False

    # Validar SECRET_KEY requerido
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY environment variable is required in production.\n"
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Validar que no sea el valor por defecto
    if SECRET_KEY == 'your-secret-key-here-change-in-production':
        raise ValueError(
            "SECRET_KEY is still set to the default value.\n"
            "Generate a new one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Validar longitud mínima
    if len(SECRET_KEY) < 32:
        raise ValueError(
            f"SECRET_KEY must be at least 32 characters (current: {len(SECRET_KEY)}).\n"
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # ... resto de configuración
```

#### Opción B: Validación en validate_config()

```python
# config/base.py
@staticmethod
def validate_config(app):
    """Validate critical configuration settings."""

    # Validar SECRET_KEY en producción
    if not app.config.get('DEBUG') and not app.config.get('TESTING'):
        secret_key = app.config.get('SECRET_KEY')

        if not secret_key:
            raise ValueError(
                "SECRET_KEY must be set in production.\n"
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        if len(secret_key) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters (current: {len(secret_key)}).\n"
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        if secret_key == 'your-secret-key-here-change-in-production':
            raise ValueError(
                "SECRET_KEY is still set to the default value.\n"
                "Generate a new one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        app.logger.info("SECRET_KEY validation passed")

    # Resto de validaciones...
```

**Recomendación:** Usar **Opción A** para fail-fast (fallar al inicio) y evitar que la aplicación arranque con configuración insegura.

---

### 2. Consolidar lógica de enmascaramiento de URIs

**Problema:**
Existe lógica duplicada para enmascarar contraseñas en URIs de base de datos:
- `run.py:41-59` - Función `mask_db_uri()`
- `config/base.py:39-42` - Regex inline en `validate_config()`

Esto dificulta el mantenimiento y puede causar inconsistencias.

**Archivos afectados:**
- `run.py`
- `config/base.py`
- Nuevo archivo: `config/utils.py` (a crear)

**Implementación:**

#### Paso 1: Crear módulo de utilidades compartidas

```python
# config/utils.py
"""
Configuration utilities shared across the application.
"""
from typing import Optional


def mask_db_uri(uri: str) -> str:
    """
    Mask password in database URI for secure logging.

    Converts: postgresql://user:password@host/db
    To:       postgresql://user:***@host/db

    Args:
        uri: Database connection URI

    Returns:
        URI with masked password

    Examples:
        >>> mask_db_uri('postgresql://user:pass123@localhost/db')
        'postgresql://user:***@localhost/db'

        >>> mask_db_uri('sqlite:///path/to/db.sqlite3')
        'sqlite:///path/to/db.sqlite3'
    """
    if not uri:
        return uri

    # Format: scheme://user:password@host/path
    if '@' in uri and ':' in uri:
        parts = uri.split('@')
        if ':' in parts[0]:
            protocol_and_user = parts[0].rsplit(':', 1)
            return f"{protocol_and_user[0]}:***@{parts[1]}"

    return uri


def str_to_bool(value: Optional[str], default: bool = False) -> bool:
    """
    Convert string to boolean safely.

    Accepts: 'true', '1', 'yes', 'on' (case-insensitive) for True
    Accepts: 'false', '0', 'no', 'off' (case-insensitive) for False
    Returns default if value is None or empty.

    Args:
        value: String value to convert
        default: Default boolean value if conversion fails

    Returns:
        Boolean value

    Examples:
        >>> str_to_bool('true')
        True
        >>> str_to_bool('FALSE')
        False
        >>> str_to_bool('1')
        True
        >>> str_to_bool(None, default=True)
        True
    """
    if not value:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')
```

#### Paso 2: Actualizar config/base.py

```python
# config/base.py
import os
import secrets
from pathlib import Path
from .utils import mask_db_uri

basedir = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Base configuration shared across all environments."""

    # Secret key for session encryption
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_hex(32)

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    DAYS_COMPARISON = int(os.getenv('DAYS_COMPARISON', '15'))
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    @staticmethod
    def validate_config(app):
        """Validate critical configuration settings."""

        # Mask password in URI for logging
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri:
            masked_uri = mask_db_uri(db_uri)
            app.logger.info(f'Database: {masked_uri}')

        # Validate SECRET_KEY in production
        if not app.config.get('DEBUG') and not app.config.get('TESTING'):
            secret_key = app.config.get('SECRET_KEY')
            if not secret_key or len(secret_key) < 32:
                raise ValueError(
                    "SECRET_KEY must be set and at least 32 characters in production."
                )
```

#### Paso 3: Actualizar run.py

```python
# run.py
"""
Application entry point.
...
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from infocodest import create_app
from config import config_dict
from config.utils import str_to_bool, mask_db_uri


def get_port(default: int = 5000) -> int:
    """
    Get and validate port number from environment.

    Args:
        default: Default port number

    Returns:
        Valid port number (1024-65535)
    """
    try:
        port = int(os.getenv("PORT", str(default)))
        if not (1024 <= port <= 65535):
            print(f"Warning: Invalid PORT {port}, using {default}")
            return default
        return port
    except ValueError:
        print(f"Warning: Invalid PORT value, using {default}")
        return default


# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Determine environment mode using safe boolean parsing
DEBUG = str_to_bool(os.getenv("DEBUG"), default=False)
TESTING = str_to_bool(os.getenv("TESTING"), default=False)

# ... resto del código
```

---

### 3. Escapar componentes de Database URI

**Problema:**
ProductionConfig construye la URI de base de datos manualmente concatenando strings. Si la contraseña contiene caracteres especiales como `@`, `:`, `/`, `#`, la URI será inválida.

**Ejemplo del problema:**
```python
DB_PASSWORD = "my@pass:word"
# URI resultante: postgresql://user:my@pass:word@localhost/db
# ❌ ROTO: El @ en la contraseña rompe el formato
```

**Archivos afectados:**
- `config/production.py:21-26`

**Implementación:**

```python
# config/production.py
import os
from pathlib import Path
from urllib.parse import quote_plus
from .base import BaseConfig

# Leer variables de entorno
DB_ENGINE = os.getenv('DB_ENGINE', None)
DB_USERNAME = os.getenv('DB_USERNAME', None)
DB_PASSWORD = os.getenv('DB_PASS', None)
DB_HOST = os.getenv('DB_HOST', None)
DB_PORT = os.getenv('DB_PORT', None)
DB_NAME = os.getenv('DB_NAME', None)

basedir = Path(__file__).resolve().parent.parent


class ProductionConfig(BaseConfig):
    """Production configuration - requires strict environment setup."""

    DEBUG = False
    TESTING = False

    # Validar SECRET_KEY
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY environment variable is required in production.\n"
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    if SECRET_KEY == 'your-secret-key-here-change-in-production':
        raise ValueError("SECRET_KEY is still set to the default value.")

    if len(SECRET_KEY) < 32:
        raise ValueError(f"SECRET_KEY must be at least 32 characters (current: {len(SECRET_KEY)}).")

    # Build database URI with proper escaping
    if all([DB_ENGINE, DB_USERNAME, DB_NAME]):
        # Escapar componentes que pueden contener caracteres especiales
        username_escaped = quote_plus(DB_USERNAME)
        password_escaped = quote_plus(DB_PASSWORD) if DB_PASSWORD else ''

        if password_escaped:
            SQLALCHEMY_DATABASE_URI = (
                f'{DB_ENGINE}://{username_escaped}:{password_escaped}'
                f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
            )
        else:
            # Sin contraseña
            SQLALCHEMY_DATABASE_URI = (
                f'{DB_ENGINE}://{username_escaped}'
                f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
            )
    else:
        # Fallback a SQLite con warning
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'db.sqlite3'}"
        print(
            "Warning: Missing database environment variables. "
            f"Required: DB_ENGINE, DB_USERNAME, DB_NAME. Falling back to SQLite."
        )

    # Security settings
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
```

**Ejemplo de uso:**
```bash
# En .env - contraseña con caracteres especiales
DB_PASS=my@pass:word#123

# URI resultante (escapada correctamente):
# postgresql://user:my%40pass%3Aword%23123@localhost/db
# ✅ FUNCIONA: Los caracteres especiales están escapados
```

---

### 4. Documentar variables de entorno requeridas

**Problema:**
No existe documentación centralizada de qué variables de entorno requiere cada configuración.

**Archivos a crear/modificar:**
- `config/README.md` (nuevo)
- Actualizar docstrings en cada clase de configuración

**Implementación:**

#### Paso 1: Crear config/README.md

```markdown
# Sistema de Configuración

Este directorio contiene la configuración de la aplicación Dashboard Sonar, organizada por entornos.

## Estructura

```
config/
├── __init__.py          # Exporta config_dict para selección de entorno
├── base.py              # Configuración base compartida
├── development.py       # Configuración para desarrollo
├── production.py        # Configuración para producción
├── testing.py           # Configuración para testing
├── utils.py             # Utilidades compartidas
└── README.md            # Este archivo
```

## Selección de Entorno

El entorno se selecciona en `run.py` basándose en las variables `DEBUG` y `TESTING`:

| DEBUG | TESTING | Configuración  |
|-------|---------|----------------|
| False | False   | Production     |
| True  | False   | Development    |
| False | True    | Testing        |
| True  | True    | Testing        |

## Variables de Entorno por Configuración

### BaseConfig (Todas las configuraciones)

Variables opcionales con valores por defecto:

| Variable          | Tipo    | Default           | Descripción                              |
|-------------------|---------|-------------------|------------------------------------------|
| `SECRET_KEY`      | string  | auto-generado     | Clave secreta para sesiones (⚠️ requerido en producción) |
| `DAYS_COMPARISON` | integer | `15`              | Días para comparación de métricas        |
| `ASSETS_ROOT`     | string  | `/static/assets`  | Ruta raíz para assets estáticos          |
| `LOG_LEVEL`       | string  | `INFO`            | Nivel de logging                         |

### DevelopmentConfig

Hereda de BaseConfig y añade:

| Variable          | Tipo    | Default              | Descripción                           |
|-------------------|---------|----------------------|---------------------------------------|
| `DEBUG`           | boolean | `True`               | Modo debug activado                   |
| `DB_NAME`         | string  | `db.sqlite3`         | Nombre del archivo SQLite             |

**Base de datos:** SQLite en `db.sqlite3`

### ProductionConfig

Hereda de BaseConfig. **TODAS las siguientes variables son REQUERIDAS:**

| Variable       | Tipo   | Requerido | Descripción                                    |
|----------------|--------|-----------|------------------------------------------------|
| `SECRET_KEY`   | string | ✅        | Mínimo 32 caracteres, nunca el valor por defecto |
| `DB_ENGINE`    | string | ✅        | Motor de BD: `postgresql`, `mysql`, `sqlite`   |
| `DB_USERNAME`  | string | ✅        | Usuario de la base de datos                    |
| `DB_PASS`      | string | ⚠️        | Contraseña (opcional pero recomendado)         |
| `DB_HOST`      | string | ✅        | Host de la base de datos                       |
| `DB_PORT`      | string | ✅        | Puerto de la base de datos                     |
| `DB_NAME`      | string | ✅        | Nombre de la base de datos                     |

**Nota:** Si faltan variables de BD, se usa SQLite como fallback con un warning.

### TestingConfig

Hereda de BaseConfig y añade:

| Variable          | Tipo    | Default              | Descripción                           |
|-------------------|---------|----------------------|---------------------------------------|
| `TESTING`         | boolean | `True`               | Modo testing activado                 |
| `DB_NAME`         | string  | `testdb.sqlite3`     | Nombre del archivo SQLite de testing  |

**Base de datos:** SQLite en `testdb.sqlite3`

## Generar SECRET_KEY

Para producción, genera una clave segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado a tu `.env`:

```bash
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

## Validación de Configuración

Todas las configuraciones incluyen un método `validate_config(app)` que:

1. Valida que SECRET_KEY cumpla los requisitos en producción
2. Enmascara contraseñas en los logs
3. Verifica que ASSETS_ROOT exista
4. Configura el nivel de logging

Este método se llama automáticamente al iniciar la aplicación.

## Ejemplo de .env para Producción

```bash
# Security
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# Application
DEBUG=False
TESTING=False
FLASK_DEBUG=0

# Database
DB_ENGINE=postgresql
DB_USERNAME=dashuser
DB_PASS=my@secure:pass#123
DB_HOST=db.example.com
DB_PORT=5432
DB_NAME=dashboardsonar

# Application settings
DAYS_COMPARISON=30
ASSETS_ROOT=/static/assets
LOG_LEVEL=WARNING
```

## Solución de Problemas

### Error: "SECRET_KEY is required in production"

**Causa:** No existe `SECRET_KEY` en el archivo `.env`.

**Solución:** Genera y agrega una clave:

```bash
python -c "import secrets; print(secrets.token_hex(32))" >> .env
```

### Error: "SECRET_KEY is still set to the default value"

**Causa:** Estás usando el valor `your-secret-key-here-change-in-production`.

**Solución:** Cambia a una clave generada aleatoriamente.

### Warning: "Missing database environment variables"

**Causa:** Faltan variables `DB_ENGINE`, `DB_USERNAME` o `DB_NAME`.

**Solución:** Verifica que todas las variables de BD estén definidas en `.env`.

### Sesiones se invalidan al reiniciar

**Causa:** `SECRET_KEY` está siendo auto-generada (no está en `.env`).

**Solución:** Define `SECRET_KEY` permanente en `.env`.
```

#### Paso 2: Actualizar docstrings

```python
# config/development.py
"""
Development configuration.

Environment Variables:
    DEBUG (optional): Set to True for development (default: True)
    DB_NAME (optional): SQLite database filename (default: db.sqlite3)

Uses SQLite database for simplicity.
CSRF protection is disabled for easier testing.
SQL queries are echoed to console.
"""
```

```python
# config/production.py
"""
Production configuration.

REQUIRED Environment Variables:
    SECRET_KEY: Secret key for session encryption (min 32 chars)
    DB_ENGINE: Database engine (postgresql, mysql, sqlite)
    DB_USERNAME: Database username
    DB_HOST: Database host
    DB_PORT: Database port
    DB_NAME: Database name

OPTIONAL Environment Variables:
    DB_PASS: Database password (recommended)

Raises:
    ValueError: If SECRET_KEY is missing, too short, or set to default value

Uses PostgreSQL/MySQL in production.
Falls back to SQLite if database variables are missing (with warning).
"""
```

---

## Media Prioridad

### 5. Función centralizada para construcción de Database URIs

**Problema:**
La lógica de construcción de URIs está dispersa y no es reutilizable.

**Archivos afectados:**
- `config/utils.py` (extender)
- `config/production.py`
- `config/development.py`
- `config/testing.py`

**Implementación:**

```python
# config/utils.py (añadir al archivo existente)
from typing import Optional
from pathlib import Path
from urllib.parse import quote_plus


def build_database_uri(
    engine: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    sqlite_path: Optional[Path] = None
) -> str:
    """
    Build a SQLAlchemy database URI with proper escaping.

    Args:
        engine: Database engine (postgresql, mysql, sqlite)
        username: Database username (not needed for SQLite)
        password: Database password (optional)
        host: Database host (not needed for SQLite)
        port: Database port (not needed for SQLite)
        database: Database name
        sqlite_path: Path to SQLite file (only for SQLite engine)

    Returns:
        Properly formatted database URI

    Raises:
        ValueError: If required parameters are missing

    Examples:
        >>> build_database_uri('sqlite', sqlite_path=Path('db.sqlite3'))
        'sqlite:///db.sqlite3'

        >>> build_database_uri(
        ...     'postgresql',
        ...     username='user',
        ...     password='my@pass',
        ...     host='localhost',
        ...     port=5432,
        ...     database='mydb'
        ... )
        'postgresql://user:my%40pass@localhost:5432/mydb'
    """
    engine = engine.lower()

    if engine == 'sqlite':
        if not sqlite_path:
            raise ValueError("sqlite_path is required for SQLite engine")
        return f"sqlite:///{sqlite_path}"

    # Para otros engines, validar parámetros requeridos
    if not all([username, database]):
        raise ValueError(
            f"username and database are required for {engine} engine"
        )

    # Construir URI con escaping apropiado
    username_escaped = quote_plus(username)

    if password:
        password_escaped = quote_plus(password)
        credentials = f"{username_escaped}:{password_escaped}"
    else:
        credentials = username_escaped

    # Host y puerto con valores por defecto
    host = host or 'localhost'

    if port:
        host_port = f"{host}:{port}"
    else:
        host_port = host

    return f"{engine}://{credentials}@{host_port}/{database}"
```

**Uso en config/production.py:**

```python
# config/production.py
import os
from pathlib import Path
from .base import BaseConfig
from .utils import build_database_uri

# Leer variables de entorno
DB_ENGINE = os.getenv('DB_ENGINE', None)
DB_USERNAME = os.getenv('DB_USERNAME', None)
DB_PASSWORD = os.getenv('DB_PASS', None)
DB_HOST = os.getenv('DB_HOST', None)
DB_PORT = os.getenv('DB_PORT', None)
DB_NAME = os.getenv('DB_NAME', None)

basedir = Path(__file__).resolve().parent.parent


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Validación de SECRET_KEY...

    # Build database URI
    if all([DB_ENGINE, DB_USERNAME, DB_NAME]):
        try:
            SQLALCHEMY_DATABASE_URI = build_database_uri(
                engine=DB_ENGINE,
                username=DB_USERNAME,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=int(DB_PORT) if DB_PORT else None,
                database=DB_NAME
            )
        except ValueError as e:
            raise ValueError(f"Database configuration error: {e}")
    else:
        # Fallback a SQLite
        SQLALCHEMY_DATABASE_URI = build_database_uri(
            engine='sqlite',
            sqlite_path=basedir / 'db.sqlite3'
        )
        print(
            "Warning: Missing database environment variables. "
            f"Required: DB_ENGINE, DB_USERNAME, DB_NAME. Falling back to SQLite."
        )
```

**Uso en config/development.py:**

```python
# config/development.py
import os
from pathlib import Path
from .base import BaseConfig
from .utils import build_database_uri

basedir = Path(__file__).resolve().parent.parent


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    TESTING = False
    DEVELOPMENT = True

    # SQLite con nombre configurable
    db_name = os.getenv('DB_NAME', 'db.sqlite3')
    SQLALCHEMY_DATABASE_URI = build_database_uri(
        engine='sqlite',
        sqlite_path=basedir / db_name
    )

    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = False
```

---

### 6. Integrar str_to_bool para lectura de booleanos

**Problema:**
Las clases de configuración tienen valores booleanos hardcoded en lugar de leerlos de variables de entorno de forma robusta.

**Archivos afectados:**
- `config/base.py`
- `config/development.py`
- `config/production.py`
- `config/testing.py`

**Implementación:**

```python
# config/base.py
import os
import secrets
from pathlib import Path
from .utils import mask_db_uri, str_to_bool

basedir = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Base configuration shared across all environments."""

    # Secret key
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_hex(32)

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = str_to_bool(
        os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS'),
        default=False
    )

    # Application settings
    DAYS_COMPARISON = int(os.getenv('DAYS_COMPARISON', '15'))
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @staticmethod
    def validate_config(app):
        """Validate critical configuration settings."""
        # ... validaciones existentes
```

```python
# config/development.py
import os
from pathlib import Path
from .base import BaseConfig
from .utils import build_database_uri, str_to_bool

basedir = Path(__file__).resolve().parent.parent


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = str_to_bool(os.getenv('DEBUG'), default=True)
    TESTING = str_to_bool(os.getenv('TESTING'), default=False)
    DEVELOPMENT = True

    # SQLite database
    db_name = os.getenv('DB_NAME', 'db.sqlite3')
    SQLALCHEMY_DATABASE_URI = build_database_uri(
        engine='sqlite',
        sqlite_path=basedir / db_name
    )

    SQLALCHEMY_ECHO = str_to_bool(os.getenv('SQLALCHEMY_ECHO'), default=True)
    WTF_CSRF_ENABLED = str_to_bool(os.getenv('WTF_CSRF_ENABLED'), default=False)
```

---

### 7. Hacer configurables los nombres de bases de datos SQLite

**Problema:**
Los nombres de archivos SQLite están hardcoded, dificultando el testing y desarrollo paralelo.

**Archivos afectados:**
- `config/development.py`
- `config/testing.py`
- `.env.example`

**Implementación:**

Ya implementado en la mejora #6. Adicionalmente, actualizar `.env.example`:

```bash
# .env.example (añadir sección)

# ==========================================
# Database (SQLite for Development/Testing)
# ==========================================

# SQLite database filename (only used in Development/Testing modes)
# Development default: db.sqlite3
# Testing default: testdb.sqlite3
DB_NAME=db.sqlite3
```

---

### 8. Implementar validación de ASSETS_ROOT

**Problema:**
ASSETS_ROOT se lee sin validar que el path exista o sea válido, causando errores silenciosos.

**Archivos afectados:**
- `config/base.py`

**Implementación:**

```python
# config/base.py
import os
import secrets
from pathlib import Path
from .utils import mask_db_uri, str_to_bool

basedir = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Base configuration shared across all environments."""

    # Secret key
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_hex(32)

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    DAYS_COMPARISON = int(os.getenv('DAYS_COMPARISON', '15'))
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @staticmethod
    def validate_config(app):
        """Validate critical configuration settings."""

        # Validar SECRET_KEY en producción
        if not app.config.get('DEBUG') and not app.config.get('TESTING'):
            secret_key = app.config.get('SECRET_KEY')
            if not secret_key or len(secret_key) < 32:
                raise ValueError(
                    "SECRET_KEY must be set and at least 32 characters in production."
                )
            if secret_key == 'your-secret-key-here-change-in-production':
                raise ValueError("SECRET_KEY is still set to the default value.")

        # Validar ASSETS_ROOT
        assets_root = app.config.get('ASSETS_ROOT', '')
        if assets_root:
            # Para paths relativos (como /static/assets), verificar en static_folder
            if assets_root.startswith('/'):
                # Es un path de URL, verificar que el directorio físico exista
                # Asumiendo que /static apunta a la carpeta static/
                physical_path = basedir / 'infocodest' / 'static' / assets_root.lstrip('/static/')
            else:
                physical_path = Path(assets_root)

            if not physical_path.exists():
                app.logger.warning(
                    f"ASSETS_ROOT path does not exist: {physical_path}. "
                    "Static assets may not load correctly."
                )
            elif not physical_path.is_dir():
                app.logger.warning(
                    f"ASSETS_ROOT is not a directory: {physical_path}"
                )
            else:
                app.logger.info(f"ASSETS_ROOT validated: {assets_root}")

        # Validar y enmascarar database URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri:
            masked_uri = mask_db_uri(db_uri)
            app.logger.info(f'Database: {masked_uri}')

        # Configurar nivel de logging
        log_level = app.config.get('LOG_LEVEL', 'INFO')
        import logging
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        app.logger.setLevel(numeric_level)
        app.logger.info(f'Log level set to: {log_level}')
```

---

## Baja Prioridad

### 9. Añadir type hints a clases de configuración

**Problema:**
Las clases de configuración no tienen type hints, dificultando el autocompletado y la verificación de tipos.

**Archivos afectados:**
- Todos los archivos en `config/`

**Implementación:**

```python
# config/base.py
from __future__ import annotations
import os
import secrets
from pathlib import Path
from typing import Optional, ClassVar
from flask import Flask
from .utils import mask_db_uri, str_to_bool

basedir: Path = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Base configuration shared across all environments."""

    # Secret key
    SECRET_KEY: str = os.getenv('SECRET_KEY') or secrets.token_hex(32)

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = ''

    # Application settings
    DAYS_COMPARISON: int = int(os.getenv('DAYS_COMPARISON', '15'))
    ASSETS_ROOT: str = os.getenv('ASSETS_ROOT', '/static/assets')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    # Flask settings
    DEBUG: bool = False
    TESTING: bool = False

    @staticmethod
    def validate_config(app: Flask) -> None:
        """
        Validate critical configuration settings.

        Args:
            app: Flask application instance

        Raises:
            ValueError: If critical configuration is invalid
        """
        # ... implementación
```

```python
# config/production.py
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from .base import BaseConfig
from .utils import build_database_uri

# Leer variables de entorno
DB_ENGINE: Optional[str] = os.getenv('DB_ENGINE')
DB_USERNAME: Optional[str] = os.getenv('DB_USERNAME')
DB_PASSWORD: Optional[str] = os.getenv('DB_PASS')
DB_HOST: Optional[str] = os.getenv('DB_HOST')
DB_PORT: Optional[str] = os.getenv('DB_PORT')
DB_NAME: Optional[str] = os.getenv('DB_NAME')

basedir: Path = Path(__file__).resolve().parent.parent


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG: bool = False
    TESTING: bool = False

    # ... resto de configuración
```

---

### 10. Implementar LOG_LEVEL en BaseConfig

**Problema:**
La variable `LOG_LEVEL` existe en `.env` pero no se usa para configurar el logger.

**Archivos afectados:**
- `config/base.py`

**Implementación:**

Ya incluido en la mejora #8 dentro del método `validate_config()`.

---

### 11. Llamar validate_config automáticamente

**Problema:**
El método `validate_config()` debe llamarse manualmente, siendo fácil olvidarlo.

**Archivos afectados:**
- `infocodest/__init__.py` (factory function)

**Implementación:**

```python
# infocodest/__init__.py
from flask import Flask
from config.base import BaseConfig


def create_app(config_class: type[BaseConfig]) -> Flask:
    """
    Application factory pattern.

    Args:
        config_class: Configuration class to use

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Llamar automáticamente a validate_config
    if hasattr(config_class, 'validate_config'):
        config_class.validate_config(app)

    # Inicializar extensiones
    from infocodest.extensions import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)

    # Registrar blueprints
    from infocodest.routes import register_blueprints
    register_blueprints(app)

    return app
```

---

## Plan de Implementación Sugerido

### Fase 1: Fundamentos (Alta Prioridad)
1. Crear `config/utils.py` con funciones compartidas
2. Implementar validación de SECRET_KEY
3. Implementar escapado de URIs
4. Consolidar lógica de enmascaramiento
5. Crear documentación en `config/README.md`

### Fase 2: Mejoras de usabilidad (Media Prioridad)
6. Implementar `build_database_uri()`
7. Integrar `str_to_bool` en todas las configs
8. Hacer configurables los nombres de BD SQLite
9. Implementar validación de ASSETS_ROOT

### Fase 3: Refinamiento (Baja Prioridad)
10. Añadir type hints completos
11. Asegurar que LOG_LEVEL funciona
12. Llamada automática a `validate_config()`

### Testing después de cada fase
```bash
# Verificar que la aplicación arranca en cada modo
python run.py  # Development
DEBUG=False python run.py  # Production
TESTING=True python run.py  # Testing
```

---

## Beneficios Esperados

- ✅ **Seguridad mejorada**: SECRET_KEY validado, contraseñas enmascaradas, URIs escapadas
- ✅ **Mantenibilidad**: Código DRY (Don't Repeat Yourself), utilidades centralizadas
- ✅ **Configuración robusta**: Parsing seguro de booleanos, validación de paths
- ✅ **Documentación clara**: README con ejemplos y troubleshooting
- ✅ **Mejor developer experience**: Type hints, validación automática, mensajes de error claros
- ✅ **Menos errores**: Validación temprana (fail-fast), escapado automático

---

## Notas de Compatibilidad

Todas las mejoras son **backwards compatible** excepto:
- La validación estricta de SECRET_KEY en producción (intencional - security by default)
- El cambio de comportamiento al fallar si SECRET_KEY es inválido (intencional - fail-fast)

Para migración suave:
1. Generar y configurar SECRET_KEY antes de desplegar
2. Verificar que todas las variables de BD estén configuradas
3. Probar en entorno de staging antes de producción
