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
| `SQLITE_DB_FILE`  | string  | `db.sqlite3`         | Nombre del archivo SQLite para desarrollo |

**Base de datos:** SQLite en `db.sqlite3`

**Nota:** `SQLITE_DB_FILE` es diferente de `DB_NAME` (usado en Production para PostgreSQL/MySQL)

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

**Mejoras de seguridad (Phase 1):**
- Validación estricta de `SECRET_KEY` (mínimo 32 caracteres, no puede ser el valor por defecto)
- Escapado automático de caracteres especiales en credenciales de BD usando `urllib.parse.quote_plus`
- La aplicación falla al inicio si `SECRET_KEY` no cumple los requisitos

### TestingConfig

Hereda de BaseConfig y añade:

| Variable          | Tipo    | Default              | Descripción                           |
|-------------------|---------|----------------------|---------------------------------------|
| `TESTING`         | boolean | `True`               | Modo testing activado                 |
| `SQLITE_DB_FILE`  | string  | `testdb.sqlite3`     | Nombre del archivo SQLite para testing |

**Base de datos:** SQLite en `testdb.sqlite3`

**Nota:** `SQLITE_DB_FILE` es diferente de `DB_NAME` (usado en Production para PostgreSQL/MySQL)

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
3. Verifica configuración crítica
4. Configura el nivel de logging

Este método se llama automáticamente al iniciar la aplicación.

## Utilidades Compartidas (config/utils.py)

### mask_db_uri(uri: str) -> str

Enmascara contraseñas en URIs de base de datos para logging seguro.

```python
from config.utils import mask_db_uri

uri = "postgresql://user:password123@localhost/db"
print(mask_db_uri(uri))
# Output: postgresql://user:***@localhost/db
```

### str_to_bool(value: Optional[str], default: bool = False) -> bool

Convierte strings de variables de entorno a booleanos de forma segura.

```python
from config.utils import str_to_bool

debug = str_to_bool(os.getenv('DEBUG'))  # Acepta: true, 1, yes, on
testing = str_to_bool(os.getenv('TESTING'), default=False)
```

## Ejemplos de .env

### Para Desarrollo (Development)

```bash
# ==========================================
# Security
# ==========================================
SECRET_KEY=dev-secret-key-not-for-production

# ==========================================
# Application Settings
# ==========================================
DEBUG=True
TESTING=False
FLASK_DEBUG=1

# ==========================================
# Database Configuration (SQLite)
# ==========================================
# Para Development/Testing: usar SQLITE_DB_FILE
SQLITE_DB_FILE=db.sqlite3

# ==========================================
# Application Settings
# ==========================================
DAYS_COMPARISON=15
ASSETS_ROOT=/static/assets
LOG_LEVEL=DEBUG
```

### Para Testing

```bash
# ==========================================
# Application Settings
# ==========================================
DEBUG=True
TESTING=True
FLASK_DEBUG=1

# ==========================================
# Database Configuration (SQLite)
# ==========================================
SQLITE_DB_FILE=testdb.sqlite3

# ==========================================
# Application Settings
# ==========================================
LOG_LEVEL=DEBUG
```

### Para Producción (Production)

```bash
# ==========================================
# Security
# ==========================================
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# ==========================================
# Application Settings
# ==========================================
DEBUG=False
TESTING=False
FLASK_DEBUG=0

# ==========================================
# Database Configuration (PostgreSQL/MySQL)
# ==========================================
# Para Production: usar DB_ENGINE, DB_USERNAME, DB_NAME, etc.
DB_ENGINE=postgresql
DB_USERNAME=dashuser
DB_PASS=my@secure:pass#123
DB_HOST=db.example.com
DB_PORT=5432
DB_NAME=dashboardsonar

# ==========================================
# Application Settings
# ==========================================
DAYS_COMPARISON=30
ASSETS_ROOT=/static/assets
LOG_LEVEL=WARNING
```

**Nota:** Las contraseñas con caracteres especiales (@, :, /, #) se escapan automáticamente usando `urllib.parse.quote_plus`.

**Importante:**

- `SQLITE_DB_FILE`: Nombre de archivo SQLite (solo Development/Testing)
- `DB_NAME`: Nombre de base de datos PostgreSQL/MySQL (solo Production)
- Son variables diferentes para propósitos diferentes

## Solución de Problemas

### Error: "SECRET_KEY is required in production"

**Causa:** No existe `SECRET_KEY` en el archivo `.env`.

**Solución:** Genera y agrega una clave:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Copia el resultado al .env como SECRET_KEY=...
```

### Error: "SECRET_KEY is still set to the default value"

**Causa:** Estás usando el valor `your-secret-key-here-change-in-production`.

**Solución:** Cambia a una clave generada aleatoriamente.

### Error: "SECRET_KEY must be at least 32 characters"

**Causa:** La clave actual es demasiado corta.

**Solución:** Genera una nueva clave con el comando anterior.

### Warning: "Missing database environment variables"

**Causa:** Faltan variables `DB_ENGINE`, `DB_USERNAME` o `DB_NAME`.

**Solución:** Verifica que todas las variables de BD estén definidas en `.env`.

### Sesiones se invalidan al reiniciar

**Causa:** `SECRET_KEY` está siendo auto-generada (no está en `.env`).

**Solución:** Define `SECRET_KEY` permanente en `.env`.

### Error de conexión a base de datos con caracteres especiales en contraseña

**Causa:** La contraseña contiene caracteres especiales que no están escapados.

**Solución:** A partir de Phase 1, el escapado es automático. Verifica que estás usando ProductionConfig actualizado.

## Mejoras Implementadas

### Phase 1 (Alta Prioridad) ✅

1. **Validación estricta de SECRET_KEY en producción**
   - Falla si SECRET_KEY no existe
   - Falla si es el valor por defecto
   - Falla si tiene menos de 32 caracteres

2. **Escapado automático de URIs de base de datos**
   - Usa `urllib.parse.quote_plus` para username y password
   - Soporta contraseñas con caracteres especiales

3. **Utilidades compartidas en config/utils.py**
   - `mask_db_uri()`: Enmascara contraseñas en logs
   - `str_to_bool()`: Conversión robusta de strings a booleanos

4. **Código DRY**
   - `run.py` usa utilidades de `config/utils.py`
   - `config/base.py` usa `mask_db_uri` compartido
   - Sin duplicación de lógica

## Referencias

- Documento completo de mejoras: `docs/MEJORAS_CONFIGURACION.md`
- Tests de configuración: `tests/unit/test_config.py`
- Ejemplo de configuración: `.env.example`
