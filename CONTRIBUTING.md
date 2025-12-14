# Guía de Contribución

¡Gracias por tu interés en contribuir a Dashboard Sonar! Esta guía te ayudará a hacer contribuciones efectivas.

---

## 📋 Tabla de Contenidos

1. [Código de Conducta](#código-de-conducta)
2. [Cómo Contribuir](#cómo-contribuir)
3. [Estándares de Código](#estándares-de-código)
4. [Proceso de Pull Request](#proceso-de-pull-request)
5. [Reportar Bugs](#reportar-bugs)
6. [Proponer Features](#proponer-features)

---

## 🤝 Código de Conducta

### Nuestro Compromiso

Nos comprometemos a hacer de la participación en este proyecto una experiencia libre de acoso para todos.

### Comportamientos Esperados

- Usar lenguaje acogedor e inclusivo
- Respetar puntos de vista y experiencias diferentes
- Aceptar críticas constructivas con gracia
- Enfocarse en lo que es mejor para la comunidad

### Comportamientos Inaceptables

- Lenguaje o imágenes sexualizadas
- Comentarios insultantes o despectivos
- Acoso público o privado
- Publicar información privada de otros sin permiso

---

## 🚀 Cómo Contribuir

### Prerequisitos

1. **Fork** el repositorio
2. **Clone** tu fork localmente
3. **Configura** el entorno de desarrollo ([ver DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md))
4. **Crea** una rama para tu contribución

### Flujo de Trabajo

```bash
# 1. Fork y clone
git clone https://github.com/YOUR-USERNAME/dashboardsonar-application-python.git
cd dashboardsonar-application-python

# 2. Añadir upstream
git remote add upstream https://github.com/jfdelafuente/dashboardsonar-application-python.git

# 3. Crear rama desde develop
git checkout develop
git pull upstream develop
git checkout -b feature/my-contribution

# 4. Hacer cambios
# ... editar código ...

# 5. Commit con Conventional Commits
git add .
git commit -m "feat: add new feature"

# 6. Push a tu fork
git push origin feature/my-contribution

# 7. Crear Pull Request en GitHub
```

---

## 📐 Estándares de Código

### Python Style Guide

Seguimos **PEP 8** con algunas adaptaciones:

```python
# ✅ Correcto
def calculate_metrics(data: List[Dict]) -> Dict[str, float]:
    """
    Calculate metrics from data

    Args:
        data: List of metric dictionaries

    Returns:
        Aggregated metrics
    """
    result = {}
    for item in data:
        result[item['name']] = item['value']
    return result

# ❌ Incorrecto
def calculateMetrics(data):  # camelCase
    result={}  # sin espacios
    for item in data:
        result[item['name']]=item['value']  # sin espacios
    return result
```

### Naming Conventions

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Clases | PascalCase | `MetricaService` |
| Funciones | snake_case | `get_all_metricas()` |
| Variables | snake_case | `total_bugs` |
| Constantes | UPPER_CASE | `MAX_RETRIES` |
| Privados | _prefijo | `_internal_method()` |

### Type Hints

Siempre incluir type hints:

```python
from typing import List, Dict, Optional

def process_items(
    items: List[str],
    limit: Optional[int] = None
) -> Dict[str, Any]:
    pass
```

### Docstrings

Usar **Google Style**:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When value is invalid

    Example:
        >>> result = my_function('test', 5)
        True
    """
    pass
```

### Tests

**Obligatorio**: Toda nueva funcionalidad debe incluir tests

```python
# tests/unit/test_my_feature.py
import pytest

class TestMyFeature:
    """Test suite for MyFeature"""

    def test_success_case(self):
        """Test successful operation"""
        # Arrange
        input_data = prepare_test_data()

        # Act
        result = my_feature.process(input_data)

        # Assert
        assert result is not None
        assert result.value == expected_value
```

**Requisitos**:
- ✅ Tests unitarios para repositories
- ✅ Tests unitarios para services (con mocks)
- ✅ Cobertura >80% para código nuevo
- ✅ Todos los tests deben pasar: `pytest`

### Code Quality

```bash
# Formatear código
black infocodest/

# Verificar linting
flake8 infocodest/

# Ordenar imports
isort infocodest/

# Verificar type hints
mypy infocodest/
```

---

## 🔄 Proceso de Pull Request

### Antes de Crear el PR

- [ ] Tests pasan: `pytest`
- [ ] Cobertura >80%: `pytest --cov`
- [ ] Código formateado: `black .`
- [ ] Linting correcto: `flake8`
- [ ] Imports ordenados: `isort`
- [ ] Commits siguen Conventional Commits
- [ ] Rama actualizada con develop

### Template de Pull Request

```markdown
## Descripción

Descripción clara de los cambios realizados.

## Tipo de Cambio

- [ ] Bug fix (cambio que arregla un issue)
- [ ] Nueva feature (cambio que añade funcionalidad)
- [ ] Breaking change (cambio que rompe compatibilidad)
- [ ] Documentación

## ¿Cómo se ha testeado?

Describe los tests realizados:
- [ ] Tests unitarios añadidos
- [ ] Tests de integración añadidos
- [ ] Testing manual realizado

## Checklist

- [ ] Mi código sigue los estándares del proyecto
- [ ] He realizado self-review de mi código
- [ ] He comentado código complejo
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan nuevos warnings
- [ ] He añadido tests que prueban mi fix/feature
- [ ] Tests nuevos y existentes pasan localmente
- [ ] Cambios dependientes han sido mergeados

## Screenshots (si aplica)

Añadir screenshots de cambios UI si corresponde.

## Información Adicional

Cualquier información adicional relevante.
```

### Proceso de Review

1. **Automated Checks**: CI/CD ejecuta tests automáticamente
2. **Code Review**: Al menos 1 aprobación requerida
3. **Discussion**: Responder a comentarios del reviewer
4. **Updates**: Realizar cambios solicitados
5. **Merge**: Una vez aprobado, se hace merge a develop

### Conventional Commits

Formato: `<type>(<scope>): <description>`

**Types válidos**:
- `feat`: Nueva feature
- `fix`: Bug fix
- `docs`: Cambios en documentación
- `test`: Añadir/modificar tests
- `refactor`: Refactorización de código
- `style`: Formateo (sin cambio de lógica)
- `chore`: Cambios en build, dependencias

**Ejemplos**:
```bash
feat(services): add MetricaService.get_statistics method
fix(repositories): correct date filtering in get_by_range
docs: update API_DOCUMENTATION with new endpoints
test(services): add tests for DashboardService
refactor(views): simplify home view logic
```

---

## 🐛 Reportar Bugs

### Antes de Reportar

1. **Busca** en issues existentes
2. **Verifica** que estás en la última versión
3. **Reproduce** el bug consistentemente

### Template de Bug Report

```markdown
## Descripción del Bug

Descripción clara y concisa del bug.

## Pasos para Reproducir

1. Ir a '...'
2. Hacer click en '...'
3. Scroll down a '...'
4. Ver error

## Comportamiento Esperado

Descripción de lo que debería ocurrir.

## Comportamiento Actual

Descripción de lo que está ocurriendo.

## Screenshots

Si aplica, añadir screenshots.

## Entorno

- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.10.5]
- Versión: [e.g. v1.9.0-phase-9]
- Browser (si aplica): [e.g. Chrome 120]

## Logs

```
Pegar logs relevantes aquí
```

## Contexto Adicional

Cualquier información adicional sobre el problema.
```

### Severidad

Usa labels apropiadas:
- `critical`: Sistema no funciona
- `high`: Feature importante rota
- `medium`: Bug menor pero visible
- `low`: Cosmético o edge case

---

## 💡 Proponer Features

### Template de Feature Request

```markdown
## Problema a Resolver

Descripción clara del problema que esta feature resolvería.

## Solución Propuesta

Descripción de cómo te gustaría que funcione la feature.

## Alternativas Consideradas

Otras soluciones que has considerado.

## Información Adicional

Contexto adicional, screenshots, mockups, etc.

## Impacto

- [ ] Afecta a usuarios finales
- [ ] Afecta a desarrolladores
- [ ] Breaking change
- [ ] Requiere migración de datos
```

### Proceso de Aprobación

1. **Discusión**: Issue abierto para discutir la propuesta
2. **Aprobación**: Maintainers aprueban la feature
3. **Diseño**: Se define arquitectura/diseño técnico
4. **Implementación**: Se asigna a developer
5. **Review**: Code review del PR
6. **Merge**: Se integra a develop

---

## 🏗️ Arquitectura del Proyecto

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para entender:

- Arquitectura en capas
- Patrones de diseño utilizados
- Flujo de datos
- Decisiones arquitectónicas

**Reglas importantes**:
- ✅ Vistas delgadas (<30 LOC)
- ✅ Lógica de negocio en servicios
- ✅ Queries SQL en repositorios
- ❌ No SQL directo en vistas
- ❌ No lógica de negocio en repositorios

---

## 📚 Recursos

### Documentación

- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Setup y desarrollo
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migrar código legacy
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentación de API
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del sistema

### Herramientas

- **pytest**: Testing framework
- **black**: Code formatter
- **flake8**: Linter
- **isort**: Import sorter
- **mypy**: Type checker

### Comandos Útiles

```bash
# Setup
pip install -r requirements-dev.txt

# Tests
pytest
pytest --cov=infocodest --cov-report=html

# Code Quality
black infocodest/
flake8 infocodest/
isort infocodest/
mypy infocodest/

# Verificaciones
python scripts/verify_dependencies.py
python scripts/verify_config.py
```

---

## ⚖️ Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la misma licencia que el proyecto (MIT License).

---

## 🙏 Reconocimientos

Gracias a todos los contribuidores que ayudan a mejorar Dashboard Sonar.

### Tipos de Contribuciones

No solo código - todas estas contribuciones son valiosas:

- 📝 Mejorar documentación
- 🐛 Reportar bugs
- 💡 Proponer features
- 🧪 Escribir tests
- 🎨 Mejorar UI/UX
- 🔍 Code review
- 📢 Difundir el proyecto

---

## 💬 Contacto

¿Preguntas? Puedes:
- Abrir un issue
- Discutir en Pull Requests
- Contactar a los maintainers

---

**¡Gracias por contribuir! 🎉**

**Última actualización**: 2025-12-14
**Versión**: 1.0.0
