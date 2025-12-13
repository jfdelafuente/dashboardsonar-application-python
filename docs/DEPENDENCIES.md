# Dependencies Guide

**Dashboard Sonar Application - Python Flask**

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Dependencias de Producción](#dependencias-de-producción)
3. [Dependencias de Desarrollo](#dependencias-de-desarrollo)
4. [Instalación](#instalación)
5. [Actualización de Dependencias](#actualización-de-dependencias)
6. [Verificación](#verificación)
7. [Troubleshooting](#troubleshooting)

## Descripción General

Este proyecto utiliza **pip** para la gestión de dependencias. Las dependencias están organizadas en dos archivos:

- **`requirements.txt`**: Dependencias necesarias para ejecutar la aplicación en producción
- **`requirements-dev.txt`**: Dependencias adicionales para desarrollo, testing y documentación

Todas las dependencias tienen **versiones pinadas** (usando `==`) para garantizar reproducibilidad y estabilidad.

## Dependencias de Producción

### Flask Core (3.0.0)

El framework web principal y sus componentes esenciales:

- **Flask==3.0.0**: Framework web principal
- **Werkzeug==3.0.1**: Librería WSGI utilities

**Uso**: Base de toda la aplicación web.

### Database (SQLAlchemy 2.0.23)

ORM y gestión de migraciones:

- **SQLAlchemy==2.0.23**: ORM para manejo de base de datos
- **Flask-SQLAlchemy==3.1.1**: Integración de SQLAlchemy con Flask
- **Flask-Migrate==4.0.5**: Gestión de migraciones de base de datos
- **alembic==1.12.1**: Motor de migraciones (dependencia de Flask-Migrate)

**Uso**:
- Modelos de datos en `infocodest/models/`
- Migraciones en `migrations/`
- Configuración en `infocodest/config.py`

### Authentication

Sistema de autenticación y seguridad de contraseñas:

- **Flask-Login==0.6.3**: Gestión de sesiones de usuario
- **Flask-Bcrypt==1.0.1**: Hashing de contraseñas
- **bcrypt==4.0.1**: Implementación de bcrypt

**Uso**:
- Sistema de login en `infocodest/auth/`
- Modelos de usuario en `infocodest/models/user.py`

### Forms & Validation

Manejo de formularios y validación:

- **Flask-WTF==1.2.1**: Integración de WTForms con Flask
- **WTForms==3.1.1**: Librería de formularios
- **email-validator==2.1.0.post1**: Validación de emails

**Uso**:
- Formularios en `infocodest/forms/`
- Validación automática en vistas

### UI (User Interface)

Componentes de interfaz de usuario:

- **Flask-Bootstrap==3.3.7.1**: Integración de Bootstrap 3
- **dominate==2.9.0**: Generación de HTML (dependencia de Flask-Bootstrap)

**Uso**:
- Templates en `infocodest/templates/`
- Estilos Bootstrap en toda la interfaz

### Security

Seguridad y CORS:

- **Flask-CORS==4.0.1**: Cross-Origin Resource Sharing

**Uso**:
- Configuración en `infocodest/__init__.py`
- Permite peticiones desde dominios externos (APIs)

### Performance

Optimización de rendimiento:

- **Flask-Minify==0.42**: Minificación automática de HTML, CSS y JS

**Uso**:
- Configuración en `infocodest/__init__.py`
- Reduce tamaño de respuestas HTTP

### Email

Envío de correos electrónicos:

- **secure-smtplib==0.1.1**: SMTP seguro para envío de emails

**Uso**:
- Envío de notificaciones y reportes
- Configuración via variables de entorno

### Scheduling

Programación de tareas:

- **schedule==1.2.0**: Ejecución de tareas programadas

**Uso**:
- Tareas periódicas y cron jobs
- Scripts en `scripts/`

### Environment

Configuración de entorno:

- **python-decouple==3.8**: Gestión de configuración desde archivos .env
- **python-dotenv==1.0.0**: Carga de variables de entorno

**Uso**:
- Archivo `.env` (ver `.env.example`)
- Configuración en `infocodest/config.py`

## Dependencias de Desarrollo

Las siguientes dependencias **NO** se instalan en producción, solo en entornos de desarrollo.

### Development Tools

Herramientas para calidad de código:

- **black==23.12.0**: Formateador de código Python
- **flake8==6.1.0**: Linter (detección de errores de estilo)
- **mypy==1.7.1**: Type checker estático
- **isort==5.13.0**: Ordenador de imports

**Uso**:
```bash
# Formatear código
black infocodest/

# Verificar estilo
flake8 infocodest/

# Type checking
mypy infocodest/

# Ordenar imports
isort infocodest/
```

### Testing

Framework de testing y coverage:

- **pytest==7.4.3**: Framework de testing
- **pytest-cov==4.1.0**: Cobertura de tests
- **pytest-mock==3.12.0**: Mocking para tests
- **pytest-flask==1.3.0**: Helpers para testing de Flask
- **Flask-Testing==0.8.1**: Utilidades adicionales para testing Flask

**Uso**:
```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=infocodest

# Tests específicos
pytest tests/test_models.py
```

### Documentation

Generación de documentación:

- **sphinx==7.2.6**: Generador de documentación

**Uso**:
```bash
# Generar documentación HTML
cd docs
make html
```

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip actualizado: `python -m pip install --upgrade pip`

### Instalación en Producción

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias de producción
pip install -r requirements.txt

# 4. Verificar instalación
python scripts/verify_requirements.py
```

### Instalación en Desarrollo

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias de desarrollo (incluye las de producción)
pip install -r requirements-dev.txt

# 4. Verificar instalación
python scripts/verify_requirements.py
```

## Actualización de Dependencias

### Política de Actualización

- **Versiones pinadas**: Todas las dependencias tienen versiones exactas (`==`)
- **Actualizaciones**: Solo actualizar tras testing exhaustivo
- **Security patches**: Prioridad alta para actualizaciones de seguridad

### Proceso de Actualización

```bash
# 1. Verificar versiones actuales
pip list --outdated

# 2. Actualizar una dependencia específica
pip install --upgrade Flask==3.1.0

# 3. Actualizar requirements.txt
pip freeze | grep Flask==

# 4. Ejecutar tests completos
pytest

# 5. Verificar la aplicación
flask run

# 6. Commit de cambios
git add requirements.txt
git commit -m "chore(deps): update Flask to 3.1.0"
```

### Actualizaciones de Seguridad

```bash
# Verificar vulnerabilidades conocidas
pip install safety
safety check

# Actualizar dependencia con vulnerabilidad
pip install --upgrade paquete-vulnerable==version-segura
```

## Verificación

### Script de Verificación Automática

El proyecto incluye un script de verificación:

```bash
python scripts/verify_requirements.py
```

**Verifica**:
- Archivos requirements tienen codificación UTF-8
- Todas las dependencias tienen versiones pinadas
- No hay paquetes duplicados
- Cuenta total de paquetes

**Salida esperada**:
```
Verificando requirements.txt
[OK] File is readable (UTF-8)
[OK] Total lines: 39
[OK] Packages listed: 20
[OK] All packages have pinned versions
[OK] No duplicate packages

Verificando requirements-dev.txt
[OK] File is readable (UTF-8)
...
```

### Verificación Manual

```bash
# Ver paquetes instalados
pip list

# Verificar versiones específicas
pip show Flask
pip show SQLAlchemy

# Verificar integridad
pip check
```

## Troubleshooting

### Error: "No module named X"

```bash
# Solución: Reinstalar dependencias
pip install -r requirements.txt
# o para desarrollo:
pip install -r requirements-dev.txt
```

### Error: Versiones incompatibles

```bash
# Solución: Limpiar entorno e instalar desde cero
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Error: Encoding issues en Windows

```bash
# Solución: Asegurar UTF-8 en Windows
set PYTHONIOENCODING=utf-8
pip install -r requirements.txt
```

### Error: pip outdated

```bash
# Solución: Actualizar pip
python -m pip install --upgrade pip
```

### Problemas con compilación de paquetes (bcrypt, etc.)

```bash
# En Windows: Instalar Visual C++ Build Tools
# Descargar de: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# En Linux: Instalar dependencias de desarrollo
sudo apt-get install python3-dev build-essential
```

### Error: "Could not find a version that satisfies the requirement"

```bash
# Verificar versión de Python
python --version

# Debe ser Python 3.8+
# Si no, actualizar Python y recrear venv
```

## Notas Adicionales

### ¿Por qué versiones pinadas?

- **Reproducibilidad**: Mismo comportamiento en todos los entornos
- **Estabilidad**: Evita actualizaciones inesperadas que rompen la aplicación
- **Testing**: Garantiza que los tests validan la versión exacta en producción

### ¿Qué hacer si necesito añadir una dependencia?

1. Instalar en entorno de desarrollo: `pip install nueva-dependencia`
2. Obtener versión exacta: `pip freeze | grep nueva-dependencia`
3. Añadir a `requirements.txt` (producción) o `requirements-dev.txt` (desarrollo)
4. Organizar por categoría con comentario explicativo
5. Ejecutar tests: `pytest`
6. Verificar script: `python scripts/verify_requirements.py`
7. Commit: `git commit -m "feat(deps): add nueva-dependencia==X.Y.Z"`

### Dependencias transitivas

No listamos dependencias transitivas (dependencias de nuestras dependencias) en los archivos requirements. pip las instala automáticamente. Ejemplos:

- `Jinja2` (instalado automáticamente por Flask)
- `MarkupSafe` (instalado por Jinja2)
- `dnspython` (instalado por email-validator)

Solo listamos dependencias **directamente usadas** en nuestro código.

---

**Última actualización**: 2025-12-13
**Fase**: 7 - Dependencies Optimization
