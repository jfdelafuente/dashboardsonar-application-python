# Análisis de Dependencias - Fase 7

**Fecha**: 2025-12-12
**Analista**: Dashboard Sonar Team

## 📊 Estado Actual

### Archivos Encontrados

1. **requirements.txt** (717 bytes)
   - ✅ Existe
   - ⚠️ Algunas versiones sin pinar (secure-smtplib, schedule)
   - ⚠️ Mezcla producción + testing (Flask-Testing)
   - ✅ Versiones mayormente pinadas

2. **requirements-dev.txt** (52 bytes)
   - ⚠️ **PROBLEMA CRÍTICO**: Encoding incorrecto (UTF-16 o similar)
   - ❌ Contenido ilegible
   - 📝 Contiene solo: pytest, pytest-coverage (según tamaño)

### Análisis del requirements.txt Actual

#### ✅ Dependencias Correctas de Producción (36 paquetes)

**Flask Core**:
- Flask==3.0.0 ✅
- Werkzeug==3.0.1 ✅
- Jinja2==3.1.2 ✅
- click==8.1.7 ✅
- itsdangerous==2.1.2 ✅
- blinker==1.7.0 ✅

**Database**:
- SQLAlchemy==2.0.23 ✅
- Flask-SQLAlchemy==3.1.1 ✅
- Flask-Migrate==4.0.5 ✅
- alembic==1.12.1 ✅

**Authentication**:
- Flask-Login==0.6.3 ✅
- Flask-Bcrypt==1.0.1 ✅
- bcrypt==4.0.1 ✅

**Forms & Validation**:
- Flask-WTF==1.2.1 ✅
- WTForms==3.1.1 ✅
- email-validator==2.1.0.post1 ✅
- dnspython==2.4.2 ✅ (dependency of email-validator)

**UI**:
- Flask-Bootstrap==3.3.7.1 ✅
- dominate==2.9.0 ✅
- visitor==0.1.3 ✅

**Security**:
- Flask-Cors==4.0.1 ✅

**Performance**:
- Flask-Minify==0.42 ✅
- htmlmin==0.1.12 ✅
- jsmin==3.0.1 ✅
- rcssmin==1.1.2 ✅
- lesscpy==0.15.1 ✅
- xxhash==3.4.1 ✅

**Environment**:
- python-decouple==3.8 ✅
- python-dotenv==1.0.0 ✅

**Email**:
- secure-smtplib ⚠️ (sin versión pinada)

**Scheduling**:
- schedule ⚠️ (sin versión pinada)

**Dependencies of dependencies** (automáticas):
- Mako==1.3.0 (alembic)
- MarkupSafe==2.1.3 (Jinja2)
- ply==3.11 (lesscpy)
- six==1.16.0 (varias)
- typing_extensions==4.8.0 (SQLAlchemy)
- idna==3.4 (email-validator)
- colorama==0.4.6 (click en Windows)

#### ⚠️ Dependencias que NO deberían estar en producción

**Testing**:
- Flask-Testing==0.8.1 ❌ (debería estar solo en requirements-dev.txt)

#### ❓ Dependencias Cuestionables

**bootstraps==1.0.1**:
- ❓ Posible typo o paquete incorrecto
- ℹ️ Ya tenemos Flask-Bootstrap==3.3.7.1
- 🔍 Verificar si es necesario

### Análisis de Dependencias Instaladas (pip list)

Total de paquetes instalados: **~150 paquetes**

#### 🔴 Herramientas de Desarrollo Instaladas (NO deberían estar en requirements.txt)

**Code Quality**:
- black==24.2.0
- flake8==7.0.0
- isort==5.13.2
- mypy==1.8.0
- pylint==2.17.2
- autopep8==2.0.2
- pre-commit==3.6.2

**Testing**:
- pytest==8.0.0
- pytest-cov==4.1.0
- pytest-mock==3.12.0
- pytest-asyncio==0.23.5
- coverage==7.4.1

**Type Checking**:
- types-beautifulsoup4==4.12.0.20240229
- types-html5lib==1.1.11.20251117
- types-requests==2.31.0.20240218
- types-webencodings==0.5.0.20251108

**Build Tools**:
- build==1.0.3
- setuptools==68.1.2
- wheel (implícito)

**Poetry** (gestor de dependencias alternativo):
- poetry==1.7.0
- poetry-core==1.8.1
- poetry-plugin-export==1.6.0

**Git**:
- GitPython==3.1.45

#### 🟡 Librerías Extra (posiblemente para otros proyectos)

**Data Science**:
- pandas==2.0.2
- numpy==1.24.3
- matplotlib-inline==0.1.6
- plotly==6.5.0
- altair==6.0.0
- openpyxl==3.1.2

**Streamlit** (framework web):
- streamlit==1.52.1

**Machine Learning/AI**:
- openai==1.19.0

**Web Scraping**:
- beautifulsoup4==4.12.0
- duckduckgo_search==4.4.3
- lxml==5.1.0

**APIs Externas**:
- python-gitlab==3.14.0
- py-strava==2.2.0
- pyTelegramBotAPI==4.11.0

**Jupyter**:
- ipykernel==6.23.1
- ipython==8.13.2
- jupyter_client==8.2.0
- jupyter_core==5.3.0

#### ✅ Dependencias Correctas ya instaladas

Todas las del requirements.txt están instaladas (Flask, SQLAlchemy, etc.)

## 🎯 Hallazgos Clave

### ❌ Problemas Críticos

1. **requirements-dev.txt corrupto**:
   - Encoding incorrecto (parece UTF-16)
   - Contenido ilegible
   - Necesita recrearse desde cero

2. **Versiones sin pinar**:
   - `secure-smtplib` (sin versión)
   - `schedule` (sin versión)

3. **Dependencia de testing en producción**:
   - `Flask-Testing==0.8.1` debería estar solo en dev

### ⚠️ Problemas Menores

1. **bootstraps==1.0.1**:
   - Posible dependencia incorrecta o typo
   - Verificar si es necesario

2. **Mezcla de entornos**:
   - Muchas herramientas de desarrollo instaladas globalmente
   - Sugiere que el proyecto se desarrolla sin venv limpio

### ✅ Puntos Positivos

1. **Versiones mayormente pinadas**: 36 de 38 dependencias tienen versiones exactas
2. **Dependencias organizadas**: Aunque no por categorías, están todas listadas
3. **Versiones actualizadas**: Flask 3.0.0, SQLAlchemy 2.0.23, etc.

## 📋 Plan de Acción

### Paso 1: Limpiar requirements.txt

**Acciones**:
1. ✅ Mantener todas las dependencias de producción
2. ❌ Remover `Flask-Testing==0.8.1` (mover a dev)
3. ⚠️ Verificar `bootstraps==1.0.1` (posible remoción)
4. ✅ Pinar versiones de `secure-smtplib` y `schedule`
5. ✅ Organizar por categorías con comentarios

**Dependencias a añadir versión**:
- secure-smtplib → secure-smtplib==0.1.1
- schedule → schedule==1.2.0

**Dependencias a remover**:
- Flask-Testing==0.8.1 (mover a dev)
- bootstraps==1.0.1 (verificar primero si es necesario)

### Paso 2: Recrear requirements-dev.txt

**Incluir**:
```
-r requirements.txt

# Code Quality
black==23.12.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
Flask-Testing==0.8.1

# Documentation
sphinx==7.2.6
```

**Notas**:
- Usar versiones del plan original (pueden ser más recientes que las instaladas)
- Incluir Flask-Testing que se remueve de requirements.txt

### Paso 3: Crear .env.example actualizado

Ya existe de la Fase 6, verificar que está completo.

### Paso 4: Verificación

1. Crear script de verificación (`scripts/verify_dependencies.py`)
2. Probar instalación limpia en venv temporal
3. Verificar que la app arranca
4. Ejecutar tests (si existen)

## 📊 Métricas

### Antes de la Fase 7

- **requirements.txt**: 38 dependencias (36 pinadas, 2 sin pinar)
- **requirements-dev.txt**: ❌ Corrupto (2 dependencias ilegibles)
- **Mezcla prod/dev**: ✅ Testing en producción
- **Encoding**: ⚠️ requirements-dev.txt con encoding incorrecto
- **Organización**: ❌ Sin categorías, sin comentarios

### Después de la Fase 7 (esperado)

- **requirements.txt**: ~36 dependencias (100% pinadas, organizadas por categoría)
- **requirements-dev.txt**: ~11 dependencias (100% pinadas, organizadas)
- **Mezcla prod/dev**: ✅ Separación clara
- **Encoding**: ✅ UTF-8 en todos los archivos
- **Organización**: ✅ Categorías claras con comentarios

## 🔍 Dependencias a Investigar

1. **bootstraps==1.0.1**:
   - Buscar en código si se usa
   - Si no se usa, remover
   - Si es typo de `Bootstrap-Flask`, corregir

2. **secure-smtplib vs smtplib**:
   - Verificar que se usa secure-smtplib
   - Confirmar versión 0.1.1

3. **schedule**:
   - Verificar si se usa para tareas programadas
   - Confirmar versión 1.2.0

---

**Conclusión**: El sistema actual tiene buenas bases (versiones mayormente pinadas), pero necesita:
1. Recrear requirements-dev.txt desde cero (UTF-8)
2. Separar testing de producción
3. Pinar 2 versiones faltantes
4. Organizar por categorías
5. Verificar/remover bootstraps
