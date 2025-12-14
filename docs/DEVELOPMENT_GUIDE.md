# Guía de Desarrollo - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: 2025-12-14
**Para**: Desarrolladores trabajando en el proyecto

---

## 📋 Tabla de Contenidos

1. [Setup del Entorno](#setup-del-entorno)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Creando un Nuevo Repository](#creando-un-nuevo-repository)
4. [Creando un Nuevo Service](#creando-un-nuevo-service)
5. [Creando una Nueva Vista](#creando-una-nueva-vista)
6. [Testing](#testing)
7. [Convenciones de Código](#convenciones-de-código)
8. [Git Workflow](#git-workflow)

---

## 🚀 Setup del Entorno

### Requisitos

- Python 3.10+
- Git
- PostgreSQL 13+ (producción) o SQLite (desarrollo)

### Instalación Paso a Paso

#### 1. Clonar Repositorio

```bash
git clone https://github.com/jfdelafuente/dashboardsonar-application-python.git
cd dashboardsonar-application-python
```

#### 2. Crear Entorno Virtual

**Linux/Mac**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Instalar Dependencias

**Producción**:
```bash
pip install -r requirements.txt
```

**Desarrollo** (incluye testing, linting):
```bash
pip install -r requirements-dev.txt
```

#### 4. Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar .env con tus valores
vim .env
```

**Variables importantes**:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_ENGINE=sqlite
DB_NAME=db.sqlite3
DAYS_COMPARISON=15
LOG_LEVEL=DEBUG
```

#### 5. Inicializar Base de Datos

```bash
# Crear directorio de datos
mkdir -p datos

# Ejecutar migraciones
flask db upgrade
```

#### 6. Ejecutar Aplicación

```bash
python run.py
```

Aplicación disponible en: `http://127.0.0.1:5000/`

### Verificar Instalación

```bash
# Verificar dependencias
python scripts/verify_dependencies.py

# Verificar configuración
python scripts/verify_config.py

# Ejecutar tests
pytest
```

---

## 📁 Estructura del Proyecto

### Organización por Capas

```
infocodest/
├── models/         # CAPA 1: Domain Models (ORM)
├── repositories/   # CAPA 2: Data Access
├── services/       # CAPA 3: Business Logic
├── home/           # CAPA 4: Presentation (Views)
├── api/            # CAPA 4: Presentation (API)
├── utils/          # Cross-cutting: Utilidades
└── exceptions/     # Cross-cutting: Excepciones
```

### Flujo de Dependencias

```
Views → Services → Repositories → Models → Database
```

**Reglas**:
- ✅ Vistas pueden usar servicios
- ✅ Servicios pueden usar repositorios
- ✅ Repositorios pueden usar modelos
- ❌ Repositorios NO usan servicios
- ❌ Modelos NO tienen lógica de negocio

---

## 🗄️ Creando un Nuevo Repository

### Paso 1: Crear Modelo (si no existe)

```python
# infocodest/models/my_model.py
from infocodest.extensions import db

class MyModel(db.Model):
    """Descripción del modelo"""

    __tablename__ = 'my_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<MyModel {self.name}>'

    def to_dict(self):
        """Serializa a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
```

### Paso 2: Crear Repositorio

```python
# infocodest/repositories/my_repository.py
from typing import List, Optional
from infocodest.repositories.base_repository import BaseRepository
from infocodest.models.my_model import MyModel

class MyRepository(BaseRepository[MyModel]):
    """
    Repositorio para operaciones con MyModel

    Responsabilidades:
    - Acceso a datos de MyModel
    - Queries específicas del dominio
    - Abstracción sobre SQLAlchemy
    """

    def __init__(self):
        super().__init__(MyModel)

    def get_by_name(self, name: str) -> Optional[MyModel]:
        """
        Obtiene instancia por nombre

        Args:
            name: Nombre a buscar

        Returns:
            MyModel o None si no existe

        Example:
            >>> repo = MyRepository()
            >>> item = repo.get_by_name('example')
            >>> print(item.name)
            'example'
        """
        return self.session.query(self.model_class)\
            .filter(self.model_class.name == name)\
            .first()

    def get_recent(self, limit: int = 10) -> List[MyModel]:
        """
        Obtiene registros más recientes

        Args:
            limit: Número máximo de resultados

        Returns:
            Lista de MyModel ordenados por fecha descendente
        """
        return self.session.query(self.model_class)\
            .order_by(self.model_class.created_at.desc())\
            .limit(limit)\
            .all()

    def search_by_name(self, query: str) -> List[MyModel]:
        """
        Búsqueda parcial por nombre

        Args:
            query: Texto a buscar

        Returns:
            Lista de MyModel que coinciden
        """
        return self.session.query(self.model_class)\
            .filter(self.model_class.name.ilike(f'%{query}%'))\
            .all()
```

### Paso 3: Registrar en `__init__.py`

```python
# infocodest/repositories/__init__.py
from infocodest.repositories.base_repository import BaseRepository
from infocodest.repositories.metrica_repository import MetricaRepository
from infocodest.repositories.my_repository import MyRepository  # ← Añadir

__all__ = [
    'BaseRepository',
    'MetricaRepository',
    'MyRepository',  # ← Añadir
]
```

### Paso 4: Escribir Tests

```python
# tests/unit/test_repositories/test_my_repository.py
import pytest
from infocodest.repositories.my_repository import MyRepository
from infocodest.models.my_model import MyModel

class TestMyRepository:
    """Test suite for MyRepository"""

    @pytest.fixture
    def repo(self, app):
        """Fixture: repositorio con contexto de app"""
        with app.app_context():
            return MyRepository()

    @pytest.fixture
    def sample_data(self, app):
        """Fixture: datos de prueba"""
        with app.app_context():
            item1 = MyModel(name='test1')
            item2 = MyModel(name='test2')
            db.session.add_all([item1, item2])
            db.session.commit()
            yield
            # Cleanup
            db.session.query(MyModel).delete()
            db.session.commit()

    def test_get_by_name_existing(self, repo, sample_data):
        """Test obtener por nombre existente"""
        # Act
        result = repo.get_by_name('test1')

        # Assert
        assert result is not None
        assert result.name == 'test1'

    def test_get_by_name_non_existing(self, repo, sample_data):
        """Test obtener por nombre inexistente"""
        # Act
        result = repo.get_by_name('nonexistent')

        # Assert
        assert result is None

    def test_get_recent(self, repo, sample_data):
        """Test obtener registros recientes"""
        # Act
        results = repo.get_recent(limit=5)

        # Assert
        assert len(results) <= 5
        assert results[0].created_at >= results[-1].created_at
```

---

## 💼 Creando un Nuevo Service

### Paso 1: Crear Servicio

```python
# infocodest/services/my_service.py
from typing import List, Dict, Any, Optional
from infocodest.repositories.my_repository import MyRepository
from infocodest.exceptions.business_exceptions import (
    NotFoundException,
    ValidationException
)

class MyService:
    """
    Servicio para lógica de negocio de MyModel

    Responsabilidades:
    - Implementar reglas de negocio
    - Orquestar múltiples repositorios
    - Transformar datos para presentación
    - Manejar excepciones de negocio
    """

    def __init__(self):
        self.my_repo = MyRepository()

    def get_all_items(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los items con formato para presentación

        Returns:
            Lista de diccionarios con datos de items

        Example:
            >>> service = MyService()
            >>> items = service.get_all_items()
            >>> print(items[0]['name'])
            'example'
        """
        items = self.my_repo.get_all()
        return [item.to_dict() for item in items]

    def get_item_by_name(self, name: str) -> Dict[str, Any]:
        """
        Obtiene item por nombre

        Args:
            name: Nombre del item

        Returns:
            Diccionario con datos del item

        Raises:
            ValidationException: Si nombre es inválido
            NotFoundException: Si item no existe

        Example:
            >>> service = MyService()
            >>> item = service.get_item_by_name('example')
        """
        # Validación de entrada
        if not name or len(name) < 2:
            raise ValidationException(
                "Name must be at least 2 characters",
                field='name'
            )

        # Buscar item
        item = self.my_repo.get_by_name(name)

        if not item:
            raise NotFoundException(
                resource='MyModel',
                identifier=name
            )

        # Transformar a dict
        return item.to_dict()

    def create_item(self, name: str) -> Dict[str, Any]:
        """
        Crea nuevo item

        Args:
            name: Nombre del item

        Returns:
            Diccionario con item creado

        Raises:
            ValidationException: Si datos son inválidos
        """
        # Validación
        if not name:
            raise ValidationException("Name is required", field='name')

        # Verificar que no exista
        existing = self.my_repo.get_by_name(name)
        if existing:
            raise ValidationException(
                f"Item with name '{name}' already exists",
                field='name'
            )

        # Crear
        from infocodest.models.my_model import MyModel
        item = MyModel(name=name)
        created = self.my_repo.create(item)

        return created.to_dict()

    def search_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca items por nombre

        Args:
            query: Texto de búsqueda
            limit: Máximo de resultados

        Returns:
            Lista de items que coinciden
        """
        # Validación
        if not query or len(query) < 2:
            return []

        # Buscar
        items = self.my_repo.search_by_name(query)

        # Limitar y transformar
        return [item.to_dict() for item in items[:limit]]
```

### Paso 2: Escribir Tests con Mocks

```python
# tests/unit/test_services/test_my_service.py
import pytest
from unittest.mock import Mock, patch
from infocodest.services.my_service import MyService
from infocodest.exceptions.business_exceptions import (
    NotFoundException,
    ValidationException
)

class TestMyService:
    """Test suite for MyService"""

    @pytest.fixture
    def service(self):
        """Fixture: servicio"""
        return MyService()

    @pytest.fixture
    def mock_repo(self, service):
        """Fixture: mock del repositorio"""
        service.my_repo = Mock()
        return service.my_repo

    def test_get_all_items_success(self, service, mock_repo):
        """Test obtener todos los items"""
        # Arrange
        mock_item = Mock()
        mock_item.to_dict.return_value = {'id': 1, 'name': 'test'}
        mock_repo.get_all.return_value = [mock_item]

        # Act
        result = service.get_all_items()

        # Assert
        assert len(result) == 1
        assert result[0]['name'] == 'test'
        mock_repo.get_all.assert_called_once()

    def test_get_item_by_name_success(self, service, mock_repo):
        """Test obtener item existente"""
        # Arrange
        mock_item = Mock()
        mock_item.to_dict.return_value = {'id': 1, 'name': 'test'}
        mock_repo.get_by_name.return_value = mock_item

        # Act
        result = service.get_item_by_name('test')

        # Assert
        assert result['name'] == 'test'
        mock_repo.get_by_name.assert_called_once_with('test')

    def test_get_item_by_name_not_found(self, service, mock_repo):
        """Test obtener item inexistente lanza excepción"""
        # Arrange
        mock_repo.get_by_name.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException):
            service.get_item_by_name('nonexistent')

    def test_get_item_by_name_invalid_name(self, service, mock_repo):
        """Test validación de nombre inválido"""
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.get_item_by_name('a')  # Muy corto

        assert 'at least 2 characters' in str(exc_info.value)

    def test_create_item_success(self, service, mock_repo):
        """Test crear item correctamente"""
        # Arrange
        mock_repo.get_by_name.return_value = None  # No existe
        mock_created = Mock()
        mock_created.to_dict.return_value = {'id': 1, 'name': 'new'}
        mock_repo.create.return_value = mock_created

        # Act
        result = service.create_item('new')

        # Assert
        assert result['name'] == 'new'
        mock_repo.create.assert_called_once()

    def test_create_item_duplicate(self, service, mock_repo):
        """Test crear item duplicado lanza excepción"""
        # Arrange
        mock_repo.get_by_name.return_value = Mock()  # Ya existe

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.create_item('existing')

        assert 'already exists' in str(exc_info.value)
```

---

## 🎨 Creando una Nueva Vista

### Paso 1: Definir Ruta en Blueprint

```python
# infocodest/home/views.py
from flask import render_template, request, jsonify
from flask_login import login_required
from infocodest.home import home_bp
from infocodest.services.my_service import MyService
from infocodest.utils.decorators import inject_service
from infocodest.exceptions.business_exceptions import (
    NotFoundException,
    ValidationException
)

@home_bp.route('/items')
@login_required
@inject_service(MyService)
def list_items(my_service: MyService):
    """
    Lista todos los items

    Vista delgada: solo llama a servicio y renderiza
    """
    items = my_service.get_all_items()
    return render_template('home/items.html', items=items)

@home_bp.route('/items/<name>')
@login_required
@inject_service(MyService)
def item_detail(name: str, my_service: MyService):
    """
    Detalle de un item

    Args:
        name: Nombre del item

    Returns:
        Template renderizado o error 404
    """
    try:
        item = my_service.get_item_by_name(name)
        return render_template('home/item_detail.html', item=item)
    except NotFoundException:
        # Error handler automático renderiza 404.html
        raise

@home_bp.route('/items/search')
@login_required
@inject_service(MyService)
def search_items(my_service: MyService):
    """
    Búsqueda de items

    Query params:
        q: Texto de búsqueda
        limit: Máximo de resultados (default: 10)

    Returns:
        JSON con resultados
    """
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))

    results = my_service.search_items(query, limit)

    return jsonify({
        'query': query,
        'count': len(results),
        'results': results
    })
```

### Paso 2: Crear Template

```html
<!-- infocodest/templates/home/items.html -->
{% extends "base.html" %}

{% block title %}Items{% endblock %}

{% block content %}
<div class="container">
    <h1>Items</h1>

    <div class="row">
        {% for item in items %}
        <div class="col-md-4">
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">{{ item.name }}</h5>
                    <p class="card-text">
                        Created: {{ item.created_at }}
                    </p>
                    <a href="{{ url_for('home.item_detail', name=item.name) }}"
                       class="btn btn-primary">
                        Ver Detalle
                    </a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

### Paso 3: Vista de API REST

```python
# infocodest/api/views.py
from flask import jsonify, request
from infocodest.api import api_bp
from infocodest.services.my_service import MyService
from infocodest.utils.decorators import inject_service
from infocodest.exceptions.business_exceptions import ValidationException

@api_bp.route('/api/items', methods=['GET'])
@inject_service(MyService)
def api_list_items(my_service: MyService):
    """
    GET /api/items - Lista todos los items

    Returns:
        JSON con lista de items
    """
    items = my_service.get_all_items()
    return jsonify({
        'count': len(items),
        'items': items
    })

@api_bp.route('/api/items', methods=['POST'])
@inject_service(MyService)
def api_create_item(my_service: MyService):
    """
    POST /api/items - Crea nuevo item

    Request Body:
        {
            "name": "item name"
        }

    Returns:
        201: Item creado
        400: Validación fallida
    """
    data = request.get_json()

    if not data or 'name' not in data:
        raise ValidationException("Name is required", field='name')

    item = my_service.create_item(data['name'])

    return jsonify(item), 201

@api_bp.route('/api/items/<name>', methods=['GET'])
@inject_service(MyService)
def api_get_item(name: str, my_service: MyService):
    """
    GET /api/items/<name> - Obtiene item por nombre

    Returns:
        200: Item encontrado
        404: Item no existe
    """
    item = my_service.get_item_by_name(name)
    return jsonify(item)
```

---

## 🧪 Testing

### Tipos de Tests

1. **Unit Tests**: Repositories, Services, Utils (202 tests actuales)
2. **Integration Tests**: Tests end-to-end (futuro)

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=infocodest --cov-report=html

# Tests específicos
pytest tests/unit/test_repositories/
pytest tests/unit/test_services/test_my_service.py

# Test individual
pytest tests/unit/test_services/test_my_service.py::TestMyService::test_get_all_items_success

# Ver output detallado
pytest -v -s
```

### Estructura de Tests

```python
import pytest

class TestMyFeature:
    """Test suite for MyFeature"""

    @pytest.fixture
    def my_fixture(self):
        """Descripción del fixture"""
        # Setup
        obj = create_object()
        yield obj
        # Teardown (opcional)
        cleanup(obj)

    def test_success_case(self, my_fixture):
        """Test caso exitoso"""
        # Arrange
        input_data = prepare_data()

        # Act
        result = my_fixture.method(input_data)

        # Assert
        assert result is not None
        assert result.value == expected_value

    def test_error_case(self, my_fixture):
        """Test caso de error"""
        # Arrange
        invalid_input = None

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            my_fixture.method(invalid_input)

        assert 'required' in str(exc_info.value)
```

### Fixtures Comunes

```python
# tests/conftest.py
import pytest
from infocodest import create_app
from infocodest.extensions import db
from config.testing import TestingConfig

@pytest.fixture
def app():
    """Fixture: Flask app para testing"""
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture: Test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture: CLI runner"""
    return app.test_cli_runner()
```

---

## 📐 Convenciones de Código

### Naming Conventions

```python
# Clases: PascalCase
class MyService:
    pass

# Funciones/métodos: snake_case
def get_all_items():
    pass

# Constantes: UPPER_CASE
MAX_ITEMS = 100

# Privados: prefijo _
def _internal_method():
    pass

# Variables: snake_case
my_variable = "value"
```

### Docstrings (Google Style)

```python
def my_function(param1: str, param2: int) -> List[str]:
    """
    Breve descripción de una línea

    Descripción más detallada si es necesario.
    Puede tener múltiples párrafos.

    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2

    Returns:
        Descripción del valor de retorno

    Raises:
        ValueError: Cuándo se lanza
        TypeError: Cuándo se lanza

    Example:
        >>> result = my_function('test', 5)
        >>> print(result)
        ['test1', 'test2']
    """
    pass
```

### Type Hints

```python
from typing import List, Dict, Optional, Any

# Siempre usar type hints
def process_data(
    items: List[str],
    config: Dict[str, Any],
    limit: Optional[int] = None
) -> Dict[str, List[str]]:
    pass
```

### Import Order (isort)

```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party
from flask import Flask, request
from sqlalchemy import func

# 3. Local application
from infocodest.repositories.my_repository import MyRepository
from infocodest.services.my_service import MyService
```

### Code Formatting (black)

```bash
# Formatear código
black infocodest/

# Verificar sin cambiar
black --check infocodest/
```

### Linting (flake8)

```bash
# Ejecutar linter
flake8 infocodest/

# Con configuración custom
flake8 --max-line-length=100 infocodest/
```

---

## 🔀 Git Workflow

### Conventional Commits

Formato: `<type>(<scope>): <description>`

**Types**:
- `feat`: Nueva feature
- `fix`: Bug fix
- `docs`: Cambios en documentación
- `test`: Añadir/modificar tests
- `refactor`: Refactorización
- `chore`: Cambios en build, dependencias

**Examples**:
```bash
git commit -m "feat(services): add MyService for item management"
git commit -m "fix(repositories): correct query in get_by_name"
git commit -m "docs: update DEVELOPMENT_GUIDE with examples"
git commit -m "test(services): add tests for MyService.create_item"
```

### Feature Branch Workflow

```bash
# 1. Crear rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature

# 2. Hacer cambios y commits
git add .
git commit -m "feat: add new feature"

# 3. Push a remoto
git push -u origin feature/my-new-feature

# 4. Crear Pull Request en GitHub

# 5. Después de merge, limpiar
git checkout develop
git pull origin develop
git branch -d feature/my-new-feature
```

### Commit Message Template

```bash
# Añadir a .git/config
[commit]
    template = .gitmessage

# Crear .gitmessage
cat > .gitmessage << 'EOF'
# <type>(<scope>): <subject>
# |<----  Using a Maximum Of 50 Characters  ---->|

# Explain why this change is being made
# |<----   Try To Limit Each Line to a Maximum Of 72 Characters   ---->|

# Provide links or keys to any relevant tickets, articles or other resources
# Example: Github issue #23

# --- COMMIT END ---
# Type can be
#    feat     (new feature)
#    fix      (bug fix)
#    refactor (refactoring code)
#    style    (formatting, missing semicolons, etc; no code change)
#    docs     (changes to documentation)
#    test     (adding or refactoring tests; no production code change)
#    chore    (updating grunt tasks etc; no production code change)
# --------------------
EOF
```

---

## 🎯 Checklist para Nueva Feature

- [ ] Crear rama feature/nombre-descriptivo
- [ ] Crear/actualizar modelo si necesario
- [ ] Crear repositorio con queries necesarias
- [ ] Escribir tests del repositorio
- [ ] Crear servicio con lógica de negocio
- [ ] Escribir tests del servicio (con mocks)
- [ ] Crear vista(s) usando @inject_service
- [ ] Crear template(s) si es HTML
- [ ] Actualizar documentación si necesario
- [ ] Verificar que todos los tests pasan
- [ ] Verificar cobertura >80%
- [ ] Commit con Conventional Commits
- [ ] Push y crear Pull Request
- [ ] Code review
- [ ] Merge a develop

---

## 📚 Recursos Adicionales

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura del sistema
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migrar código legacy
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentación de API
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Cómo contribuir

---

**Última actualización**: 2025-12-14
**Versión**: 1.0.0
