# Plan Detallado - Fase 7: Optimización de Dependencias

**Fecha de Creación**: 2025-12-12
**Estado**: 📋 Planificado
**Duración Estimada**: 30 minutos

## 🎯 Objetivo

Limpiar, organizar y optimizar las dependencias del proyecto, separando dependencias de producción de las de desarrollo, actualizando versiones a releases seguros, y asegurando compatibilidad.

## 📋 Tabla de Contenidos

- [Resumen Ejecutivo](#resumen-ejecutivo)
- [Pasos de Implementación](#pasos-de-implementación)
- [Estructura de Archivos](#estructura-de-archivos)
- [Checklist de Completitud](#checklist-de-completitud)

---

## 📊 Resumen Ejecutivo

### Situación Actual
- `requirements.txt` puede contener dependencias mezcladas (prod + dev)
- Posibles problemas de encoding (no UTF-8)
- Versiones no pinadas o desactualizadas
- Sin separación clara entre dependencias de producción y desarrollo

### Situación Objetivo
- ✅ `requirements.txt` en UTF-8 con versiones pinadas
- ✅ `requirements-dev.txt` separado para herramientas de desarrollo
- ✅ Versiones actualizadas y seguras
- ✅ Instalación limpia verificada
- ✅ Documentación de dependencias actualizada

### Beneficios
1. **Reproducibilidad**: Builds consistentes con versiones pinadas
2. **Seguridad**: Versiones actualizadas sin vulnerabilidades conocidas
3. **Claridad**: Separación prod/dev facilita deployments
4. **Performance**: Instalaciones más rápidas en producción

---

## 🔧 Pasos de Implementación

### PASO 0: Preparar Estrategia Git

**Objetivo**: Crear rama de trabajo siguiendo la estrategia Git del proyecto

**Comandos**:
```bash
# Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# Crear rama para Fase 7
git checkout -b feature/refactor-phase-7-dependencies

# Verificar rama creada
git branch --show-current

# Push inicial de la rama
git push -u origin feature/refactor-phase-7-dependencies
```

**Verificación**:
- [ ] Rama `feature/refactor-phase-7-dependencies` creada
- [ ] Branch basado en `develop` actualizado
- [ ] Push inicial completado

**Commit inicial**:
```bash
git commit --allow-empty -m "chore: init Phase 7 - Dependencies Optimization

Initialize Phase 7 branch for dependencies cleanup and optimization

Fase: 7
Task: Initialize branch
"
```

---

### PASO 1: Analizar Dependencias Actuales

**Objetivo**: Entender el estado actual de las dependencias

**Comandos**:
```bash
# Ver dependencias instaladas actualmente
pip list --format=freeze > temp_current_deps.txt

# Ver dependencias en requirements.txt actual
cat requirements.txt
```

**Acciones**:
1. Revisar `requirements.txt` actual
2. Identificar dependencias de producción vs desarrollo
3. Identificar versiones obsoletas o con vulnerabilidades
4. Verificar encoding del archivo actual

**Notas a capturar**:
- Dependencias no utilizadas que se pueden remover
- Dependencias faltantes que deberían estar
- Conflictos de versiones potenciales

---

### PASO 2: Crear Nuevo requirements.txt

**Objetivo**: Crear archivo de dependencias de producción limpio y organizado

**Archivo**: `requirements.txt`

**Contenido** (basado en el plan):
```txt
# Flask Core
Flask==3.0.0
Werkzeug==3.0.1

# Database
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
alembic==1.12.1

# Authentication
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
bcrypt==4.0.1

# Forms & Validation
Flask-WTF==1.2.1
WTForms==3.1.1
email-validator==2.1.0

# UI
Flask-Bootstrap==3.3.7.1
dominate==2.9.0

# Security
Flask-CORS==4.0.1

# Performance
Flask-Minify==0.42

# Email
secure-smtplib==0.1.1

# Scheduling
schedule==1.2.0

# Environment
python-decouple==3.8
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
Flask-Testing==0.8.1
```

**Consideraciones**:
- Archivo en UTF-8 (sin BOM)
- Una dependencia por línea
- Versiones exactas pinadas (==)
- Agrupado por categoría funcional
- Comentarios descriptivos para cada sección

**Commit**:
```bash
git add requirements.txt
git commit -m "feat(deps): create clean production requirements

- UTF-8 encoding
- Pinned versions for reproducibility
- Organized by functional category
- Production dependencies only

Fase: 7
Task: Create production requirements
"
```

---

### PASO 3: Crear requirements-dev.txt

**Objetivo**: Separar dependencias de desarrollo en archivo dedicado

**Archivo**: `requirements-dev.txt`

**Contenido**:
```txt
-r requirements.txt

# Development tools
black==23.12.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.0

# Testing
pytest-mock==3.12.0
pytest-flask==1.3.0
coverage==7.3.3

# Documentation
sphinx==7.2.6
```

**Consideraciones**:
- Primera línea: `-r requirements.txt` (incluye deps de prod)
- Solo herramientas de desarrollo/testing/docs
- Versiones pinadas
- Agrupado por propósito

**Commit**:
```bash
git add requirements-dev.txt
git commit -m "feat(deps): add development requirements

Separate development dependencies from production:
- Code quality tools (black, flake8, mypy, isort)
- Testing tools (pytest-mock, pytest-flask, coverage)
- Documentation tools (sphinx)

Includes production requirements via -r requirements.txt

Fase: 7
Task: Create development requirements
"
```

---

### PASO 4: Verificar Instalación Limpia

**Objetivo**: Asegurar que las dependencias se instalan correctamente

**Comandos para testing** (en entorno virtual limpio):

```bash
# Crear entorno virtual de prueba
python -m venv venv_test

# Activar (Windows)
.\venv_test\Scripts\activate

# Activar (Linux/Mac)
# source venv_test/bin/activate

# Instalar requirements de producción
pip install -r requirements.txt

# Verificar instalación
pip list

# Probar que la app arranca
python -c "from infocodest import create_app; from config import config_dict; app = create_app(config_dict['Development']); print('✓ App imports successfully')"

# Limpiar
deactivate
rm -rf venv_test  # o rmdir /s venv_test en Windows
```

**Verificaciones**:
- [ ] Instalación completa sin errores
- [ ] No hay conflictos de versiones
- [ ] La aplicación importa correctamente
- [ ] Tests básicos pasan

**Si hay problemas**:
1. Ajustar versiones en requirements.txt
2. Resolver conflictos
3. Actualizar y re-verificar
4. Commit de ajustes

---

### PASO 5: Actualizar .gitignore

**Objetivo**: Asegurar que entornos virtuales y archivos temporales no se commitean

**Archivo**: `.gitignore`

**Verificar que incluye**:
```
# Entornos virtuales
env/
venv/
venv_*/
.venv/
ENV/
env.bak/
venv.bak/

# Pip
pip-log.txt
pip-delete-this-directory.txt

# Dependencias temporales
temp_current_deps.txt
```

**Acción**:
- Si ya existe: verificar que está completo
- Si falta algo: añadirlo

**Commit** (solo si se modificó):
```bash
git add .gitignore
git commit -m "chore(deps): update .gitignore for dependency files

Ensure virtual environments and temp dependency files are ignored

Fase: 7
Task: Update .gitignore
"
```

---

### PASO 6: Actualizar Documentación

**Objetivo**: Documentar las dependencias y proceso de instalación

#### 6.1 Crear DEPENDENCIES.md

**Archivo**: `docs/DEPENDENCIES.md`

**Contenido**:
```markdown
# Dependencies Guide

**Version**: v1.7.0
**Last Updated**: 2025-12-12

## Overview

This project uses separate dependency files for production and development environments:

- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development tools (includes production deps)

## Installation

### Production Environment

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Development Environment

\`\`\`bash
pip install -r requirements-dev.txt
\`\`\`

## Dependency Categories

### Flask Core
- **Flask 3.0.0** - Web framework
- **Werkzeug 3.0.1** - WSGI utility library

### Database
- **SQLAlchemy 2.0.23** - ORM
- **Flask-SQLAlchemy 3.1.1** - Flask SQLAlchemy integration
- **Flask-Migrate 4.0.5** - Database migrations
- **alembic 1.12.1** - Migration tool

### Authentication
- **Flask-Login 0.6.3** - User session management
- **Flask-Bcrypt 1.0.1** - Password hashing
- **bcrypt 4.0.1** - Bcrypt implementation

### Forms & Validation
- **Flask-WTF 1.2.1** - WTForms integration
- **WTForms 3.1.1** - Form handling
- **email-validator 2.1.0** - Email validation

### UI
- **Flask-Bootstrap 3.3.7.1** - Bootstrap integration
- **dominate 2.9.0** - HTML generation

### Security
- **Flask-CORS 4.0.1** - CORS handling

### Performance
- **Flask-Minify 0.42** - HTML/CSS/JS minification

### Email
- **secure-smtplib 0.1.1** - Secure SMTP

### Scheduling
- **schedule 1.2.0** - Task scheduling

### Environment
- **python-decouple 3.8** - Config from environment
- **python-dotenv 1.0.0** - .env file support

### Testing
- **pytest 7.4.3** - Testing framework
- **pytest-cov 4.1.0** - Coverage plugin
- **Flask-Testing 0.8.1** - Flask testing utilities

## Development Tools

### Code Quality
- **black 23.12.0** - Code formatter
- **flake8 6.1.0** - Linter
- **mypy 1.7.1** - Type checker
- **isort 5.13.0** - Import sorter

### Testing
- **pytest-mock 3.12.0** - Mocking for pytest
- **pytest-flask 1.3.0** - Pytest Flask fixtures
- **coverage 7.3.3** - Code coverage

### Documentation
- **sphinx 7.2.6** - Documentation generator

## Updating Dependencies

### Check for Updates

\`\`\`bash
pip list --outdated
\`\`\`

### Update a Specific Package

\`\`\`bash
pip install --upgrade package-name==new-version
pip freeze > requirements.txt  # Update requirements
\`\`\`

### Security Audits

\`\`\`bash
pip install safety
safety check -r requirements.txt
\`\`\`

## Troubleshooting

### Dependency Conflicts

If you encounter version conflicts:

1. Create a fresh virtual environment
2. Install requirements one category at a time
3. Identify the conflicting packages
4. Adjust versions in requirements.txt

### Installation Errors

Common issues:

- **Compiler errors**: Ensure you have build tools installed
  - Windows: Visual Studio Build Tools
  - Linux: `build-essential`, `python3-dev`
  - Mac: Xcode Command Line Tools

- **Permission errors**: Use virtual environment (never sudo pip)

### Virtual Environment Issues

\`\`\`bash
# Recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
\`\`\`

## Best Practices

1. **Always use virtual environments** - Never install in global Python
2. **Pin versions** - Use exact versions (==) for reproducibility
3. **Separate prod/dev** - Keep development tools out of production
4. **Regular updates** - Check for security updates monthly
5. **Test before updating** - Always test after updating dependencies

## Related Documentation

- [Configuration Guide](guides/CONFIGURATION_GUIDE.md) - Environment configuration
- [Development Setup](guides/INICIO_RAPIDO.md) - Quick start guide

---

**Maintained by**: Dashboard Sonar Team
```

**Commit**:
```bash
git add docs/DEPENDENCIES.md
git commit -m "docs(deps): add comprehensive dependencies guide

Complete documentation covering:
- Installation instructions (prod vs dev)
- Dependency categories and purposes
- Update procedures
- Troubleshooting
- Best practices

Fase: 7
Task: Document dependencies
"
```

#### 6.2 Actualizar README.md

**Archivo**: `README.md`

**Sección a añadir/actualizar** (después de "Requisitos Previos"):

```markdown
### Instalación de Dependencias

#### Producción
\`\`\`bash
pip install -r requirements.txt
\`\`\`

#### Desarrollo
\`\`\`bash
pip install -r requirements-dev.txt
\`\`\`

Ver [DEPENDENCIES.md](docs/DEPENDENCIES.md) para información detallada.
```

**Commit**:
```bash
git add README.md
git commit -m "docs: update README with dependency installation

Add clear instructions for installing production vs development dependencies

Fase: 7
Task: Update README
"
```

---

### PASO 7: Crear Script de Verificación

**Objetivo**: Script automatizado para verificar dependencias

**Archivo**: `scripts/verify_dependencies.py`

**Contenido**:
```python
"""
Dependency Verification Script
===============================

Verifies that all required dependencies are installed and compatible.

Usage:
    python scripts/verify_dependencies.py

Exit codes:
    0: All dependencies verified successfully
    1: Missing or incompatible dependencies

Created: Phase 7 - Dependencies Optimization
"""

import sys
import importlib
import pkg_resources
from typing import List, Tuple

# Required packages with minimum versions
REQUIRED_PACKAGES = {
    'flask': '3.0.0',
    'sqlalchemy': '2.0.0',
    'flask_login': '0.6.0',
    'flask_wtf': '1.2.0',
    'pytest': '7.4.0',
}

def check_package(package_name: str, min_version: str) -> Tuple[bool, str]:
    """
    Check if package is installed and meets minimum version.

    Returns:
        (success, message)
    """
    try:
        # Try to import
        importlib.import_module(package_name.replace('-', '_'))

        # Check version
        installed_version = pkg_resources.get_distribution(
            package_name.replace('_', '-')
        ).version

        if pkg_resources.parse_version(installed_version) >= pkg_resources.parse_version(min_version):
            return True, f"✓ {package_name} {installed_version} (>= {min_version})"
        else:
            return False, f"✗ {package_name} {installed_version} (< {min_version} required)"

    except ImportError:
        return False, f"✗ {package_name} not installed"
    except Exception as e:
        return False, f"✗ {package_name} error: {str(e)}"

def main():
    print("=" * 60)
    print("Dependency Verification")
    print("=" * 60)
    print()

    failures = []

    for package, min_version in REQUIRED_PACKAGES.items():
        success, message = check_package(package, min_version)
        print(message)

        if not success:
            failures.append(package)

    print()
    print("=" * 60)

    if failures:
        print(f"[FAIL] {len(failures)} package(s) missing or incompatible:")
        for package in failures:
            print(f"  - {package}")
        print()
        print("Run: pip install -r requirements-dev.txt")
        sys.exit(1)
    else:
        print("[SUCCESS] All dependencies verified!")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

**Commit**:
```bash
git add scripts/verify_dependencies.py
git commit -m "feat(deps): add dependency verification script

Automated script to verify:
- All required packages are installed
- Versions meet minimum requirements
- Packages can be imported

Fase: 7
Task: Create verification script
"
```

---

### PASO 8: Testing Final

**Objetivo**: Verificar que todo funciona correctamente

**Comandos**:
```bash
# Ejecutar script de verificación
python scripts/verify_dependencies.py

# Verificar que la configuración funciona
python scripts/verify_config.py

# Ejecutar tests (si existen)
pytest

# Verificar que la app arranca
python run.py --help  # o similar
```

**Verificaciones**:
- [ ] Script de verificación pasa (0 errores)
- [ ] Configuración verificada correctamente
- [ ] Tests pasan (si aplica)
- [ ] Aplicación arranca sin errores

**Si hay problemas**: Ajustar y corregir antes de continuar

---

### PASO 9: Push y Verificación Final

**Objetivo**: Subir todos los cambios al repositorio remoto

**Comandos**:
```bash
# Ver estado final
git status

# Ver log de commits
git log --oneline -10

# Push todos los commits
git push origin feature/refactor-phase-7-dependencies
```

**Verificación**:
- [ ] Working tree clean
- [ ] Todos los commits pushed
- [ ] Branch visible en GitHub

---

### PASO 10: Crear Reporte de Fase

**Objetivo**: Documentar lo completado en esta fase

**Archivo**: `docs/reports/phase-7-dependencies.md`

**Contenido mínimo**:
- Resumen ejecutivo
- Objetivos vs Resultados
- Cambios técnicos detallados
- Archivos creados/modificados
- Métricas
- Commits realizados
- Lecciones aprendidas

**Plantilla**: Usar `docs/templates/PHASE_REPORT_TEMPLATE.md` o seguir formato de `docs/reports/phase-6-configuration.md`

**Commit**:
```bash
git add docs/reports/phase-7-dependencies.md
git commit -m "docs(deps): add Phase 7 completion report

Comprehensive report documenting dependencies optimization:
- Requirements reorganization
- Dependencies documentation
- Verification tooling

Fase: 7
Task: Create completion report
"
```

---

### PASO 11: Actualizar CHANGELOG

**Objetivo**: Registrar cambios en el CHANGELOG del proyecto

**Archivo**: `CHANGELOG.md`

**Añadir entrada**:
```markdown
## [1.7.0-phase-7] - 2025-12-12

### Added

- **Dependencies Documentation**: Complete guide for managing dependencies
  - `docs/DEPENDENCIES.md` (XXX LOC) - Comprehensive dependency guide
  - Installation instructions for prod vs dev
  - Update procedures and troubleshooting
  - Security audit guidelines

- **Dependency Verification**: Automated verification script
  - `scripts/verify_dependencies.py` (XXX LOC) - Verify installed packages
  - Version compatibility checking
  - Exit codes for CI/CD integration

### Changed

- **Production Requirements** (`requirements.txt`):
  - Reorganized by functional category
  - All versions pinned for reproducibility
  - UTF-8 encoding (previously may have had issues)
  - Comments added for clarity

- **Development Requirements** (`requirements-dev.txt`):
  - Separated from production dependencies
  - Development tools (black, flake8, mypy, isort)
  - Testing tools (pytest-mock, pytest-flask, coverage)
  - Documentation tools (sphinx)

### Technical Debt

None. This phase focuses on cleanup and organization.

### Metrics

- X files created/modified
- X commits
- Dependencies organized: X production, Y development
- 100% dependency documentation coverage
```

**Commit**:
```bash
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for Phase 7 release

Add v1.7.0-phase-7 entry with dependencies optimization changes

Fase: 7
Task: Update CHANGELOG
"
```

---

### PASO 12: Actualizar Documentación del Proyecto

**Objetivo**: Actualizar README y índices de documentación

**Archivos a actualizar**:

1. **README.md**:
   - Actualizar badges (versión a v1.7.0-phase-7, progreso a 70%)
   - Actualizar estado (Fase 7 Completada)

2. **docs/README.md**:
   - Actualizar progreso (7/10 fases)
   - Añadir Phase 7 a completadas

3. **docs/reports/README.md**:
   - Añadir entrada para phase-7-dependencies.md

**Commit**:
```bash
git add README.md docs/README.md docs/reports/README.md
git commit -m "docs: update project documentation for Phase 7

- Update version badges to v1.7.0-phase-7
- Update progress indicators to 70% (7/10 phases)
- Add Phase 7 to completed phases index

Fase: 7
Task: Update project documentation
"
```

---

### PASO 13: Crear Pull Request y Merge

**Objetivo**: Integrar cambios a develop

**Comandos**:
```bash
# Asegurar que todo está pushed
git push origin feature/refactor-phase-7-dependencies

# Cambiar a develop
git checkout develop

# Merge con --no-ff para preservar historial
git merge --no-ff feature/refactor-phase-7-dependencies -m "Merge Phase 7: Dependencies Optimization

Complete reorganization and optimization of project dependencies.

Key changes:
- Reorganized requirements.txt by category
- Separated dev dependencies to requirements-dev.txt
- Added comprehensive dependency documentation
- Created verification script
- All versions pinned for reproducibility

Files: X changed, XXX+ insertions
Commits: XX semantic commits
"

# Push develop
git push origin develop

# Crear tag
git tag -a v1.7.0-phase-7 -m "Release v1.7.0 - Phase 7: Dependencies Optimization

Optimized and organized project dependencies.

Features:
- Production requirements reorganized
- Development requirements separated
- Dependency verification script
- Comprehensive documentation

Phase: 7/10 (70% complete)
"

# Push tag
git push origin v1.7.0-phase-7

# Eliminar rama local y remota
git branch -d feature/refactor-phase-7-dependencies
git push origin --delete feature/refactor-phase-7-dependencies
```

---

## 📁 Estructura de Archivos

### Archivos Creados

```
requirements-dev.txt           # Dependencias de desarrollo
docs/DEPENDENCIES.md           # Guía de dependencias
docs/reports/phase-7-dependencies.md  # Reporte de fase
scripts/verify_dependencies.py # Script de verificación
docs/plan/FASE_7_PLAN_DETALLADO.md   # Este documento
```

### Archivos Modificados

```
requirements.txt               # Reorganizado y limpiado
CHANGELOG.md                   # Entrada de Phase 7
README.md                      # Versión y progreso actualizado
docs/README.md                 # Progreso actualizado
docs/reports/README.md         # Índice actualizado
.gitignore                     # Potencialmente (si falta algo)
```

---

## ✅ Checklist de Completitud

### Implementación
- [ ] requirements.txt recreado en UTF-8
- [ ] requirements-dev.txt creado
- [ ] Dependencias organizadas por categoría
- [ ] Versiones pinadas (==)
- [ ] Instalación limpia verificada
- [ ] Script de verificación creado y funcional

### Documentación
- [ ] DEPENDENCIES.md creado
- [ ] README.md actualizado
- [ ] Phase report creado
- [ ] CHANGELOG.md actualizado
- [ ] docs/README.md actualizado
- [ ] docs/reports/README.md actualizado

### Testing
- [ ] Script de verificación pasa (0 errores)
- [ ] Instalación limpia sin conflictos
- [ ] Aplicación arranca correctamente
- [ ] Tests pasan (si aplica)

### Git & CI
- [ ] Feature branch creado
- [ ] XX commits semánticos realizados
- [ ] Branch pushed a remote
- [ ] Pull request creado (o merge directo)
- [ ] Merge a develop completado
- [ ] Tag v1.7.0-phase-7 creado
- [ ] Tag pushed a remote
- [ ] Feature branch eliminado

**Completitud Esperada**: 100% (todos los items marcados)

---

## 📊 Métricas Esperadas

- **Archivos creados**: ~5 archivos
- **Archivos modificados**: ~6 archivos
- **Líneas de código/docs**: ~500-700 LOC
- **Commits**: 10-15 commits semánticos
- **Duración real**: 30-45 minutos
- **Breaking changes**: 0 (100% compatible)

---

## 🎓 Notas Importantes

### Consideraciones de Versiones

- **Verificar compatibilidad**: Antes de actualizar versiones, verificar que no hay breaking changes
- **Consultar CHANGELOG**: De cada paquete para entender cambios entre versiones
- **Testing**: Siempre probar en entorno de desarrollo antes de actualizar producción

### Seguridad

- **Safety**: Considerar usar `pip install safety && safety check` para auditorías de seguridad
- **Dependabot**: GitHub puede notificar sobre vulnerabilidades automáticamente
- **Regular updates**: Actualizar dependencias al menos mensualmente

### Mejores Prácticas

1. **Virtual environments**: SIEMPRE usar entornos virtuales
2. **Pin everything**: Versiones exactas en producción
3. **Separate concerns**: Prod vs dev dependencies separadas
4. **Document**: Explicar por qué se usa cada dependencia
5. **Test**: Verificar después de cada cambio de dependencias

---

**Documento creado**: 2025-12-12
**Versión del plan**: 1.0
**Autor**: Dashboard Sonar Team
**Fase**: 7/10 (Optimización de Dependencias)
