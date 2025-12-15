# Dashboard Sonar - Guía de Instalación y Configuración

Esta guía proporciona instrucciones completas para configurar y poner en marcha la aplicación Dashboard Sonar desde cero.

---

## Descripción de la Aplicación

**Dashboard Sonar** es una aplicación web desarrollada con Flask que proporciona análisis, visualización y seguimiento de métricas de calidad de código provenientes de SonarQube.

### Funcionalidad Principal

La aplicación permite a los equipos de desarrollo:

#### 1. **Visualización de Métricas de Calidad**

- **Dashboard Principal**: Vista consolidada de métricas de calidad de código de todos los repositorios
- **Análisis por Aplicación**: Métricas agrupadas por aplicación/proyecto
- **Tendencias Temporales**: Evolución histórica de las métricas a lo largo del tiempo
- **Indicadores de Calidad**: Bugs, vulnerabilidades, code smells, cobertura de tests, duplicación de código

#### 2. **Gestión de Repositorios**

- Seguimiento de múltiples repositorios y proyectos
- Clasificación por tipo de aplicación y proveedor
- Etiquetado de tamaño de repositorio (XS, S, M, L, XL)
- Estado de Quality Gates (OK/ERROR)

#### 3. **Análisis de Métricas**

- **Reliability Rating**: Evaluación de confiabilidad del código (A-E)
- **Security Rating**: Calificación de seguridad (A-E)
- **Maintainability (SQALE)**: Índice de mantenibilidad técnica
- **Coverage**: Porcentaje de cobertura de pruebas unitarias
- **Duplicación**: Densidad de líneas duplicadas (DLOC)
- **Complejidad Ciclomática**: Medición de complejidad del código

#### 4. **Seguimiento Histórico**

- Almacenamiento de análisis históricos de SonarQube
- Comparación de métricas entre diferentes fechas
- Identificación de tendencias de mejora o deterioro
- Snapshots diarios para análisis temporal

#### 5. **Gestión de Proveedores**

- Asociación de aplicaciones con proveedores externos
- Clasificación por tipo de proveedor
- Trazabilidad de responsabilidades

#### 6. **Estadísticas Agregadas**

- Contadores de repositorios por aplicación
- Cantidad de repositorios con calificación "A"
- Conteo de Quality Gates aprobados (OK)
- Estadísticas globales del ecosistema

#### 7. **Auditoría y Registros**

- Registro de procesos de carga de datos
- Auditoría de análisis realizados
- Estadísticas globales por fecha
- Trazabilidad de cambios

### Arquitectura de Datos

La aplicación gestiona 7 tablas principales:

1. **metricas**: Métricas actuales de cada repositorio
2. **historico**: Histórico completo de todos los análisis
3. **daily**: Snapshots diarios agregados por repositorio
4. **stats**: Estadísticas agregadas por aplicación
5. **proveedor**: Relación aplicación-proveedor
6. **registros**: Auditoría de procesos y estadísticas globales
7. **users**: Usuarios del sistema (autenticación)

### Casos de Uso

- **Gestores de Proyecto**: Monitoreo del estado general de calidad
- **Tech Leads**: Análisis de tendencias y áreas de mejora
- **Desarrolladores**: Revisión de métricas de sus repositorios
- **Quality Assurance**: Seguimiento de compliance y quality gates
- **Management**: Reportes de estadísticas globales

---

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Base de Datos](#base-de-datos)
5. [Ejecución](#ejecución)
6. [Entornos de Configuración](#entornos-de-configuración)
7. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

### Software Necesario

- **Python 3.12+** (64-bit recomendado)
- **pip** (gestor de paquetes de Python)
- **Git** (para control de versiones)
- **Base de datos** (opcional):
  - SQLite (incluida por defecto)
  - PostgreSQL (recomendado para producción)
  - MySQL/MariaDB (alternativa)

### Verificar Instalación

```bash
# Verificar Python
python --version
# o
py -3.12 --version

# Verificar pip
pip --version
```

---

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/jfdelafuente/dashboardsonar-application-python.git
cd dashboardsonar-application-python
```

### 2. Crear Entorno Virtual

**En Windows:**
```bash
# Crear entorno virtual
py -3.12 -m venv venv

# Activar entorno virtual
venv\Scripts\activate
```

**En Linux/macOS:**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar Instalación

```bash
pip list | findstr "Flask"
```

Deberías ver:
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Migrate
- etc.

---

## Configuración

### Sistema de Configuración Modular

La aplicación utiliza un sistema de configuración modular ubicado en el directorio `config/`:

```
config/
├── __init__.py          # Exporta config_dict
├── base.py              # Configuración base compartida
├── development.py       # Configuración para desarrollo
├── testing.py           # Configuración para tests
└── production.py        # Configuración para producción
```

### Variables de Entorno

#### 1. Crear Archivo .env

Copia el archivo de ejemplo y edítalo:

```bash
copy .env.example .env
```

#### 2. Configurar Variables Obligatorias

Edita `.env` con tus valores:

```bash
# ==========================================
# Database Configuration
# ==========================================

# Para SQLite (desarrollo local):
# No requiere configuración adicional, usa db.sqlite3 por defecto

# Para PostgreSQL (producción):
DB_ENGINE=postgresql
DB_USERNAME=tu_usuario_db
DB_PASS=tu_contraseña_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar

# Para MySQL:
DB_ENGINE=mysql+pymysql
DB_USERNAME=tu_usuario_db
DB_PASS=tu_contraseña_db
DB_HOST=localhost
DB_PORT=3306
DB_NAME=dashboardsonar

# ==========================================
# Security
# ==========================================

# IMPORTANTE: Generar una clave secreta única
# Ejecuta: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=genera_tu_clave_secreta_aqui

# ==========================================
# Application Settings
# ==========================================

# Flask application entry point
FLASK_APP=run.py

# Debug mode (valores aceptados: true/1/yes/on o false/0/no/off, case-insensitive)
# IMPORTANTE: FLASK_DEBUG y DEBUG deben estar sincronizados
# Para desarrollo: FLASK_DEBUG=1 y DEBUG=True
# Para producción: FLASK_DEBUG=0 y DEBUG=False
FLASK_DEBUG=0
DEBUG=False
TESTING=False

# Configuración del servidor
HOST=127.0.0.1
PORT=5000

# Días de comparación para métricas históricas (default: 15)
DAYS_COMPARISON=15

# ==========================================
# Assets
# ==========================================

ASSETS_ROOT=/static/assets

# ==========================================
# Logging
# ==========================================

# Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

### 3. Generar SECRET_KEY

**Es CRÍTICO generar una clave secreta única para producción:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado en `.env`:
```
SECRET_KEY=tu_clave_generada_aqui
```

---

## Base de Datos

### Opción 1: SQLite (Desarrollo)

**Configuración automática** - No requiere pasos adicionales.

La aplicación creará `db.sqlite3` automáticamente en el directorio raíz.

### Opción 2: PostgreSQL (Producción)

#### 1. Instalar PostgreSQL

**Windows:**
- Descargar de https://www.postgresql.org/download/
- Instalar siguiendo el asistente

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### 2. Crear Base de Datos

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear usuario
CREATE USER dashboarduser WITH PASSWORD 'tu_contraseña';

# Crear base de datos
CREATE DATABASE dashboardsonar OWNER dashboarduser;

# Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE dashboardsonar TO dashboarduser;

# Salir
\q
```

#### 3. Configurar .env

```bash
DB_ENGINE=postgresql
DB_USERNAME=dashboarduser
DB_PASS=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar
```

#### 4. Instalar Driver PostgreSQL

```bash
pip install psycopg2-binary
```

### Opción 3: MySQL/MariaDB

#### 1. Instalar MySQL

**Windows:**
- Descargar de https://dev.mysql.com/downloads/installer/

**Linux:**
```bash
sudo apt update
sudo apt install mysql-server
```

#### 2. Crear Base de Datos

```bash
mysql -u root -p

CREATE DATABASE dashboardsonar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dashboarduser'@'localhost' IDENTIFIED BY 'tu_contraseña';
GRANT ALL PRIVILEGES ON dashboardsonar.* TO 'dashboarduser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Configurar .env

```bash
DB_ENGINE=mysql+pymysql
DB_USERNAME=dashboarduser
DB_PASS=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
DB_NAME=dashboardsonar
```

#### 4. Instalar Driver MySQL

```bash
pip install pymysql
```

### Inicializar Base de Datos y Crear Usuario Admin

#### Opción 1: Script Automatizado (RECOMENDADO)

La forma más sencilla de inicializar la base de datos y crear el usuario administrador es usando el script automatizado:

**Windows:**
```bash
# Asegúrate de activar el entorno virtual primero
venv\Scripts\activate

# Ejecutar script de setup (modo interactivo)
setup_database.bat

# O especificar el entorno
setup_database.bat Development
setup_database.bat Production
```

**Linux/macOS:**
```bash
# Asegúrate de activar el entorno virtual primero
source venv/bin/activate

# Dar permisos de ejecución (solo primera vez)
chmod +x setup_database.sh

# Ejecutar script de setup (modo interactivo)
./setup_database.sh

# O especificar el entorno
./setup_database.sh Development
./setup_database.sh Production
```

**Modo No Interactivo (para scripts/CI/CD):**

```bash
# Con credenciales por defecto
python scripts/setup/setup_database.py --config Development --non-interactive

# Con credenciales personalizadas
python scripts/setup/setup_database.py --config Production --non-interactive \
  --username myadmin \
  --email admin@miempresa.com \
  --password mi_contraseña_segura
```

El script automatizado:

- ✅ Crea todas las tablas de la base de datos
- ✅ Crea el usuario administrador
- ✅ Valida que no haya errores
- ✅ Permite personalizar credenciales
- ✅ Muestra información clara del proceso

#### Opción 2: Usar Flask-Migrate

```bash
# Inicializar migraciones (solo primera vez)
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migraciones
flask db upgrade
```

Luego crear el usuario admin manualmente (ver Opción 4).

#### Opción 3: Crear Tablas Directamente

Si `flask db` no funciona, usa el shell de Python:

```python
python

>>> from infocodest import create_app
>>> from infocodest.extensions import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

Luego crear el usuario admin manualmente (ver Opción 4).

#### Opción 4: Crear Usuario Administrador Manualmente

Si necesitas crear un usuario admin manualmente:

```python
python

>>> from infocodest import create_app
>>> from infocodest.extensions import db
>>> from infocodest.models.users import User

>>> app = create_app()
>>> with app.app_context():
...     admin = User(
...         username='admin',
...         email='admin@example.com',
...         password='admin123'
...     )
...     db.session.add(admin)
...     db.session.commit()
...     print("Usuario admin creado")
>>> exit()
```

**Nota:** El modelo `User` hashea automáticamente la contraseña en su constructor, no es necesario usar `hash_pass()` directamente.

---

## Ejecución

### Modo Desarrollo

```bash
# Asegúrate de estar en el entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Ejecutar aplicación
python run.py
```

La aplicación estará disponible en: http://127.0.0.1:5000

### Variables de Entorno Soportadas

La aplicación soporta las siguientes variables de entorno que pueden configurarse en `.env`:

#### Variables de Debug Mode

| Variable | Valores Aceptados | Default | Descripción |
|----------|-------------------|---------|-------------|
| `DEBUG` | `true`, `1`, `yes`, `on` (case-insensitive) o `false`, `0`, `no`, `off` | `False` | Activa modo debug de la aplicación |
| `FLASK_DEBUG` | `1` o `0` | `0` | Activa modo debug de Flask |
| `TESTING` | `true`, `1`, `yes`, `on` o `false`, `0`, `no`, `off` | `False` | Activa modo testing |

**IMPORTANTE:** `FLASK_DEBUG` y `DEBUG` deben estar sincronizados:
- **Desarrollo:** `FLASK_DEBUG=1` y `DEBUG=True`
- **Producción:** `FLASK_DEBUG=0` y `DEBUG=False`

#### Variables de Servidor

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `HOST` | IP | `127.0.0.1` | IP del servidor (usar `0.0.0.0` para acceso externo) |
| `PORT` | Número (1024-65535) | `5000` | Puerto del servidor |

**Ejemplos de configuración:**

```bash
# Desarrollo local
DEBUG=True
FLASK_DEBUG=1
HOST=127.0.0.1
PORT=5000

# Desarrollo accesible desde red local
DEBUG=True
FLASK_DEBUG=1
HOST=0.0.0.0
PORT=8000

# Producción
DEBUG=False
FLASK_DEBUG=0
HOST=0.0.0.0
PORT=5000
```

### Modo Producción

**Usando Gunicorn (Linux/Mac):**

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar
gunicorn --bind 0.0.0.0:5000 run:app
```

**Usando Waitress (Windows/multiplataforma):**

```bash
# Instalar waitress
pip install waitress

# Ejecutar
waitress-serve --host 0.0.0.0 --port 5000 run:app
```

### Configurar como Servicio (Producción)

**Linux con systemd:**

Crear `/etc/systemd/system/dashboardsonar.service`:

```ini
[Unit]
Description=Dashboard Sonar Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/ruta/a/dashboardsonar-application-python
Environment="PATH=/ruta/a/dashboardsonar-application-python/venv/bin"
ExecStart=/ruta/a/dashboardsonar-application-python/venv/bin/gunicorn --bind 0.0.0.0:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Iniciar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboardsonar
sudo systemctl start dashboardsonar
```

---

## Entornos de Configuración

### ¿Cómo Funciona el Sistema de Configuración?

El sistema de configuración utiliza **herencia de clases** para diferentes entornos:

```
BaseConfig (config/base.py)
    ├── DevelopmentConfig (config/development.py)
    ├── TestingConfig (config/testing.py)
    └── ProductionConfig (config/production.py)
```

### BaseConfig (config/base.py)

**Configuración compartida por todos los entornos:**

- **Seguridad:**
  - `SECRET_KEY`: Clave secreta para sesiones (lee de .env o genera automáticamente)
  - `CSRF_ENABLED`: Protección CSRF habilitada
  - `WTF_CSRF_ENABLED`: Protección CSRF para formularios

- **Base de Datos:**
  - `SQLALCHEMY_TRACK_MODIFICATIONS`: False (desactiva warnings)
  - `SQLALCHEMY_ECHO`: False por defecto (muestra queries SQL)
  - `BCRYPT_LOG_ROUNDS`: 13 (rounds para hash de contraseñas)

- **Aplicación:**
  - `FLASK_APP`: Punto de entrada (default: run.py)
  - `DAYS_COMPARISON`: Días para comparación de métricas (default: 15)
  - `ASSETS_ROOT`: Ruta de assets estáticos

- **Logging:**
  - `LOG_LEVEL`: Nivel de logging (default: INFO)
  - `LOG_DIR`: Directorio de logs (basedir/logs)

- **Sesiones/Cookies:**
  - `SESSION_COOKIE_HTTPONLY`: True (seguridad)
  - `REMEMBER_COOKIE_HTTPONLY`: True
  - `REMEMBER_COOKIE_DURATION`: 3600 segundos

### DevelopmentConfig (config/development.py)

**Optimizado para desarrollo local:**

```python
DEBUG = True
TESTING = False
DEVELOPMENT = True

# Base de datos SQLite local
SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"
SQLALCHEMY_ECHO = True  # Muestra queries SQL en consola

# CSRF deshabilitado para testing manual
WTF_CSRF_ENABLED = False

# Logging verboso
LOG_LEVEL = 'DEBUG'

# Debug toolbar habilitada
DEBUG_TB_ENABLED = True
```

**Uso:**
```python
from config import config_dict
app = create_app(config_dict['Development'])
```

### TestingConfig (config/testing.py)

**Para ejecutar tests automatizados:**

```python
DEBUG = True
TESTING = True

# Base de datos de test separada
SQLALCHEMY_DATABASE_URI = "sqlite:///testdb.sqlite3"

# CSRF deshabilitado para test clients
WTF_CSRF_ENABLED = False

# Bcrypt más rápido (menos rounds)
BCRYPT_LOG_ROUNDS = 1
```

**Uso en tests:**
```python
from config import TestingConfig

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    return app
```

### ProductionConfig (config/production.py)

**Optimizado para producción:**

```python
DEBUG = False
TESTING = False

# Base de datos desde variables de entorno
DB_ENGINE = os.getenv('DB_ENGINE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

SQLALCHEMY_DATABASE_URI = f'{DB_ENGINE}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Seguridad reforzada
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # Solo HTTPS
REMEMBER_COOKIE_SECURE = True

# Logging reducido
LOG_LEVEL = 'WARNING'

# Debug toolbar deshabilitada
DEBUG_TB_ENABLED = False
```

**Uso:**
```python
from config import config_dict
app = create_app(config_dict['Production'])
```

### Seleccionar Configuración en run.py

El archivo `run.py` selecciona automáticamente la configuración:

```python
from config import config_dict
import os

# Determinar entorno
config_mode = os.getenv('FLASK_ENV', 'Production')

# Cargar configuración
if config_mode == 'development':
    config_class = config_dict['Development']
elif config_mode == 'testing':
    config_class = config_dict['Testing']
else:
    config_class = config_dict['Production']

# Crear app
app = create_app(config_class)
```

**Cambiar entorno:**

```bash
# Desarrollo
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows

# Producción (default)
export FLASK_ENV=production
```

---

## Estructura del Proyecto

```
dashboardsonar-application-python/
│
├── config/                      # Sistema de configuración modular
│   ├── __init__.py             # Exporta config_dict
│   ├── base.py                 # Configuración base
│   ├── development.py          # Config desarrollo
│   ├── testing.py              # Config testing
│   └── production.py           # Config producción
│
├── infocodest/                  # Paquete principal de la aplicación
│   ├── __init__.py             # Factory pattern (create_app)
│   ├── extensions.py           # Extensiones Flask (db, login_manager, etc)
│   │
│   ├── models/                 # Modelos de datos (ORM)
│   │   ├── users.py
│   │   ├── metricas.py
│   │   ├── historico.py
│   │   ├── daily.py
│   │   └── proveedor.py
│   │
│   ├── repositories/           # Capa de acceso a datos
│   │   ├── base_repository.py
│   │   ├── user_repository.py
│   │   ├── metrica_repository.py
│   │   ├── historico_repository.py
│   │   ├── daily_repository.py
│   │   └── proveedor_repository.py
│   │
│   ├── services/               # Lógica de negocio
│   │   ├── auth_service.py
│   │   ├── dashboard_service.py
│   │   └── metrica_service.py
│   │
│   ├── views/                  # Rutas y controladores
│   │   ├── authentication.py
│   │   ├── dashboard.py
│   │   └── home.py
│   │
│   ├── utils/                  # Utilidades
│   │   ├── decorators.py       # Decoradores (@inject_service)
│   │   └── security.py         # Funciones de seguridad (hash_pass)
│   │
│   └── static/                 # Archivos estáticos (CSS, JS, imágenes)
│       └── assets/
│
├── migrations/                  # Migraciones de base de datos (Flask-Migrate)
│   └── versions/
│
├── logs/                        # Archivos de log (creado automáticamente)
│
├── .env                         # Variables de entorno (NO COMMITEAR)
├── .env.example                # Ejemplo de variables de entorno
├── .gitignore                  # Archivos ignorados por Git
├── requirements.txt            # Dependencias Python
├── run.py                      # Punto de entrada de la aplicación
├── manage.py                   # Script de gestión CLI
├── README.md                   # Documentación principal
└── SETUP.md                    # Esta guía
```

---

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'flask'"

**Solución:**
```bash
# Verifica que el entorno virtual esté activado
venv\Scripts\activate  # Windows

# Reinstala dependencias
pip install -r requirements.txt
```

### Error: "greenlet compilation failed" en Windows

**Causa:** Python 32-bit intentando compilar greenlet.

**Solución:**
```bash
# Instalar Python 64-bit
# Crear nuevo entorno virtual
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "SQLALCHEMY_DATABASE_URI not configured"

**Solución:**

1. Verifica que `.env` existe y tiene las variables correctas
2. Para desarrollo, no es necesario configurar DB_* (usa SQLite)
3. Para producción, asegúrate de definir todas las variables:

```bash
DB_ENGINE=postgresql
DB_USERNAME=tu_usuario
DB_PASS=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar
```

### Error: "SECRET_KEY not set"

**Solución:**

Genera una clave secreta:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Añádela a `.env`:
```
SECRET_KEY=tu_clave_generada
```

### Error: "Table does not exist"

**Solución:**

Inicializa la base de datos:
```bash
flask db upgrade
```

O crea las tablas manualmente:
```python
python
>>> from infocodest import create_app
>>> from infocodest.extensions import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

### La aplicación no carga assets estáticos

**Solución:**

1. Verifica que `ASSETS_ROOT` en `.env` es correcto:
```
ASSETS_ROOT=/static/assets
```

2. Asegúrate de que la carpeta existe:
```
infocodest/static/assets/
```

### Puerto 5000 ya en uso

**Solución:**

Cambia el puerto en `run.py`:
```python
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)
```

### Logs no se están generando

**Solución:**

1. Verifica que el directorio `logs/` existe:
```bash
mkdir logs
```

2. Verifica permisos de escritura

3. Cambia `LOG_LEVEL` en `.env`:
```
LOG_LEVEL=DEBUG
```

---

## Seguridad en Producción

### Checklist de Seguridad

- [ ] **SECRET_KEY único y generado aleatoriamente**
- [ ] **Archivo .env NO commiteado a Git** (verificar .gitignore)
- [ ] **DEBUG=False en producción**
- [ ] **HTTPS configurado** (SESSION_COOKIE_SECURE=True)
- [ ] **Base de datos con usuario no-root**
- [ ] **Contraseñas de BD seguras**
- [ ] **Firewall configurado** (solo puertos necesarios)
- [ ] **Actualizaciones de seguridad aplicadas**
- [ ] **Backups de base de datos configurados**
- [ ] **Logs monitoreados**

### Generar Contraseñas Seguras

```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Contraseña de BD
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Comandos Útiles

### Gestión de Entorno Virtual

```bash
# Crear entorno
py -3.12 -m venv venv

# Activar
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

# Desactivar
deactivate

# Listar paquetes instalados
pip list

# Congelar dependencias
pip freeze > requirements.txt
```

### Base de Datos

```bash
# Crear migración
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir migración
flask db downgrade

# Ver historial
flask db history

# Crear todas las tablas
python -c "from infocodest import create_app; from infocodest.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Git

```bash
# Ver estado
git status

# Ver ramas
git branch -a

# Cambiar rama
git checkout develop

# Actualizar
git pull origin develop

# Ver logs
git log --oneline -10
```

---

## Recursos Adicionales

- **Documentación Flask:** https://flask.palletsprojects.com/
- **SQLAlchemy:** https://www.sqlalchemy.org/
- **Flask-Migrate:** https://flask-migrate.readthedocs.io/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Gunicorn:** https://gunicorn.org/

---

## Soporte

Para reportar problemas o solicitar ayuda:

1. Revisa esta guía completa
2. Consulta la sección de Solución de Problemas
3. Revisa los logs en `logs/`
4. Crea un issue en el repositorio: https://github.com/jfdelafuente/dashboardsonar-application-python/issues

---

**Última actualización:** Diciembre 2025
**Versión de la guía:** 1.0
