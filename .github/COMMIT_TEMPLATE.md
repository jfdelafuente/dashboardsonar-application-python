# Plantilla de Mensaje de Commit

## Formato Estándar

```
<tipo>(<ámbito>): <descripción corta en imperativo>

<descripción larga opcional - párrafos separados por línea en blanco>

<footer opcional: Fase, Referencias, Breaking Changes>
```

## Tipos de Commit

- `feat`: Nueva funcionalidad
- `refactor`: Refactorización (sin cambio de comportamiento)
- `fix`: Corrección de bug
- `test`: Añadir/modificar tests
- `docs`: Cambios en documentación
- `style`: Formateo, linting (sin cambio de lógica)
- `chore`: Tareas de mantenimiento, configuración
- `perf`: Mejoras de performance

## Ámbitos Comunes

- `repositories`: Capa de repositorios
- `services`: Capa de servicios
- `views`: Vistas/Controllers
- `models`: Modelos ORM
- `config`: Configuración
- `utils`: Utilidades
- `tests`: Tests
- `deps`: Dependencias
- `api`: API endpoints
- `auth`: Autenticación

## Ejemplos

### 1. Nueva Funcionalidad (feat)

```
feat(repositories): add base repository pattern

Implements BaseRepository[T] generic class with CRUD operations:
- get_by_id(id: int) -> Optional[T]
- get_all() -> List[T]
- filter_by(**kwargs) -> List[T]
- create(**kwargs) -> T
- update(instance: T) -> T
- delete(instance: T) -> None

All repositories will inherit from this base class to ensure
consistent data access patterns across the application.

Fase: 1
Task: Create base repository
Ref: PLAN_REORGANIZACION.md#fase-1
```

### 2. Refactorización (refactor)

```
refactor(views): extract business logic to services

Moves logic from home/views.py to MetricaService:
- get_metricas() → metrica_service.get_metricas_dashboard()
- get_distinct_apps() → metrica_service.get_distinct_applications()

Reduces view complexity from 150 to 25 lines.
View now only handles HTTP request/response.

Fase: 3
Task: Refactor home views
```

### 3. Corrección de Bug (fix)

```
fix(services): handle division by zero in KPI calculations

Adds safe division in DashboardService._calculate_variations()
when old_data values are 0.

Previously:
- Crashed with ZeroDivisionError
- No handling for edge cases

Now:
- Returns 100% increase when old value is 0
- Returns 0% when both values are 0

Fixes: #123
Fase: 2
```

### 4. Tests (test)

```
test(repositories): add comprehensive tests for MetricaRepository

Coverage: 95% for infocodest/repositories/metrica_repository.py

Tests added:
- test_get_distinct_applications()
- test_get_metricas_with_proveedor()
- test_count_total_apps()
- test_get_by_aplicacion()
- test_sum_total_bugs_empty_db()

Mocks database interactions using pytest fixtures.

Fase: 1
```

### 5. Documentación (docs)

```
docs(architecture): add layer architecture diagram

Adds visual diagram showing:
- 4-layer architecture (Presentation → Service → Repository → Model)
- Data flow between layers
- Dependency direction

Also updates README.md with architecture section.

Fase: 10
```

### 6. Estilo/Formateo (style)

```
style: apply black formatting to all Python files

Runs: black infocodest/ tests/ --line-length=100

No functional changes, only code formatting.
```

### 7. Tareas de Mantenimiento (chore)

```
chore(deps): update requirements.txt to UTF-8 encoding

Previously:
- UTF-16 encoding causing installation issues
- Missing version pinning for some packages

Now:
- UTF-8 encoding
- All versions pinned for reproducibility
- Separated dev dependencies to requirements-dev.txt

Fase: 7
```

### 8. Performance (perf)

```
perf(queries): optimize N+1 queries in metrics endpoint

Replaces:
- Individual queries per metric (N+1 problem)

With:
- Single query with JOIN and eager loading
- SQLAlchemy joinedload() for proveedor relationship

Reduces API response time from ~500ms to ~50ms.

Fase: 1
```

### 9. Breaking Change

```
feat(config)!: move configuration to config/ module

BREAKING CHANGE: Configuration import path changed.

Before:
  from config import DevelopmentConfig

After:
  from config.development import DevelopmentConfig

Migration required for:
- run.py
- manage.py
- All test files

See MIGRATION_GUIDE.md for details.

Fase: 6
```

## Reglas de Escritura

### ✅ Hacer

1. **Usar imperativo**: "add feature" no "added feature"
2. **Primera letra minúscula**: `feat: add` no `feat: Add`
3. **Sin punto final**: `add feature` no `add feature.`
4. **Máximo 50 caracteres** en la línea de descripción corta
5. **Línea en blanco** entre descripción corta y larga
6. **Explicar el "por qué"**, no solo el "qué"
7. **Referenciar** fase, issue, o plan cuando aplique

### ❌ Evitar

1. Mensajes genéricos: `fix stuff`, `changes`, `wip`
2. Commits gigantes con múltiples cambios no relacionados
3. Commits de código comentado
4. Commits con código que no compila/funciona
5. Falta de contexto en el mensaje largo

## Configurar Plantilla Localmente

```bash
# Guardar esta plantilla como archivo
git config commit.template .github/COMMIT_TEMPLATE.md

# Ahora 'git commit' abrirá el editor con la plantilla
```

## Commit Interactivo (Recomendado)

Para commits con muchos cambios, usar staging interactivo:

```bash
# Añadir archivos relacionados por lote
git add infocodest/repositories/base_repository.py
git add infocodest/repositories/__init__.py
git commit -m "feat(repositories): add base repository"

# Para cambios en mismo archivo
git add -p file.py  # Interactivo: seleccionar hunks
```

## Squash de Commits

Si hiciste commits WIP durante desarrollo:

```bash
# Antes de hacer PR, squash commits relacionados
git rebase -i HEAD~5  # Últimos 5 commits

# En el editor, cambiar 'pick' a 'squash' para combinar
# Reescribir mensaje combinado siguiendo esta plantilla
```

## Verificación Pre-Commit

Antes de hacer commit:

```bash
# 1. Tests pasan
pytest

# 2. Linting OK
flake8 <archivos-modificados>

# 3. Formateo aplicado
black <archivos-modificados>

# 4. Mensaje descriptivo preparado
git commit
```

## Referencias

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
