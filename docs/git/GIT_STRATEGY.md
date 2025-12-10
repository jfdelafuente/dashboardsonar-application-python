# Estrategia de Git para Reorganización del Proyecto

**Fecha**: 2025-12-10
**Objetivo**: Control de versiones seguro durante la refactorización

---

## 🎯 Estrategia General

### Modelo de Branching: **GitFlow Simplificado**

```
main (production-ready)
  ├── develop (integration)
  │   ├── feature/refactor-phase-0-preparation
  │   ├── feature/refactor-phase-1-repositories
  │   ├── feature/refactor-phase-2-services
  │   ├── feature/refactor-phase-3-views
  │   ├── feature/refactor-phase-4-utilities
  │   ├── feature/refactor-phase-5-exceptions
  │   ├── feature/refactor-phase-6-config
  │   ├── feature/refactor-phase-7-dependencies
  │   ├── feature/refactor-phase-8-entrypoints
  │   └── feature/refactor-phase-9-tests
```

### Principios Clave

1. **Una rama por fase** - Aislamiento de cambios
2. **Commits atómicos** - Un concepto lógico por commit
3. **Pull Requests obligatorios** - Revisión antes de merge
4. **Tests antes de merge** - CI/CD gates
5. **Backup automático** - Tags antes de cambios mayores

---

## 📋 Inicialización del Repositorio

### Paso 1: Inicializar Git

```bash
cd "c:\My Program Files\workspace-claude\dashboardsonar-application-python"

# Inicializar repositorio
git init

# Configurar usuario (ajustar a tu info)
git config user.name "Tu Nombre"
git config user.email "tu.email@example.com"

# Primera confirmación del estado actual
git add .
git commit -m "chore: initial commit - baseline before refactoring

- Project structure as-is
- All existing functionality working
- Tests passing (baseline coverage)

This commit serves as the baseline for the refactoring project.
Reference: PLAN_REORGANIZACION.md"

# Crear tag de baseline
git tag -a v1.0.0-baseline -m "Baseline before architecture refactoring"
```

### Paso 2: Conectar con Repositorio Remoto

```bash
# Si ya tienes un repositorio remoto
git remote add origin <URL_DEL_REPOSITORIO>

# Verificar conexión
git remote -v

# Subir baseline
git push -u origin main
git push origin v1.0.0-baseline
```

### Paso 3: Crear Rama Develop

```bash
# Crear rama de desarrollo
git checkout -b develop

# Subir a remoto
git push -u origin develop

# Establecer develop como rama por defecto para features
git config branch.develop.description "Integration branch for refactoring"
```

---

## 🌳 Estructura de Ramas

### Nomenclatura

```
feature/refactor-phase-<N>-<nombre-corto>
```

**Ejemplos**:
- `feature/refactor-phase-0-preparation`
- `feature/refactor-phase-1-repositories`
- `feature/refactor-phase-2-services`

### Propósito de Cada Rama

| Rama | Desde | Merge a | Propósito |
|------|-------|---------|-----------|
| `main` | - | - | Código estable en producción |
| `develop` | `main` | `main` | Integración de features |
| `feature/refactor-phase-*` | `develop` | `develop` | Implementación de cada fase |

---

## 🔄 Workflow por Fase

### Template de Workflow

Para **cada fase** del plan de reorganización:

#### 1. Crear Rama de Feature

```bash
# Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# Crear rama para la fase
git checkout -b feature/refactor-phase-<N>-<nombre>

# Ejemplo para Fase 0
git checkout -b feature/refactor-phase-0-preparation
```

#### 2. Trabajar en la Fase

```bash
# Hacer cambios según el plan...

# Commits frecuentes y atómicos (ver guía abajo)
git add <archivos-relacionados>
git commit -m "<tipo>: <mensaje-corto>

<descripción-detallada>

Fase: <N>
Task: <nombre-tarea>
"

# Ejemplo de commit
git add infocodest/repositories/base_repository.py
git commit -m "feat: add base repository pattern

Implements generic CRUD operations for all repositories:
- get_by_id, get_all, filter_by
- create, update, delete
- Type-safe with generics

Fase: 1
Task: Create base repository
"
```

#### 3. Push Periódico

```bash
# Subir cambios al remoto frecuentemente
git push origin feature/refactor-phase-<N>-<nombre>

# Primera vez (establecer tracking)
git push -u origin feature/refactor-phase-<N>-<nombre>
```

#### 4. Crear Pull Request

**No hacer merge directo**, siempre usar PR:

```bash
# Usar GitHub CLI (si está instalado)
gh pr create \
  --base develop \
  --head feature/refactor-phase-<N>-<nombre> \
  --title "Phase <N>: <Nombre Descriptivo>" \
  --body "$(cat .github/PULL_REQUEST_TEMPLATE.md)"

# O crear manualmente en GitHub/GitLab
```

#### 5. Code Review y Tests

- ✅ Tests automáticos pasan (CI/CD)
- ✅ Cobertura de código mantenida/mejorada
- ✅ Sin conflictos con develop
- ✅ Revisión de código aprobada

#### 6. Merge a Develop

```bash
# Opción A: Merge desde GitHub/GitLab (recomendado)
# Usar la interfaz web con "Squash and Merge" o "Merge Commit"

# Opción B: Merge local
git checkout develop
git pull origin develop
git merge --no-ff feature/refactor-phase-<N>-<nombre>
git push origin develop

# Eliminar rama feature (después del merge)
git branch -d feature/refactor-phase-<N>-<nombre>
git push origin --delete feature/refactor-phase-<N>-<nombre>
```

#### 7. Tag de Milestone

```bash
# Después de completar cada fase importante
git checkout develop
git tag -a v1.1.0-phase-<N> -m "Completed Phase <N>: <Nombre>"
git push origin v1.1.0-phase-<N>
```

---

## 📝 Guía de Commits Semánticos

### Formato

```
<tipo>(<ámbito>): <descripción corta>

<descripción larga opcional>

<footer opcional>
```

### Tipos de Commit

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `feat` | Nueva funcionalidad | `feat(repositories): add MetricaRepository` |
| `refactor` | Refactorización (sin cambio funcional) | `refactor(views): extract business logic to services` |
| `fix` | Corrección de bug | `fix(api): handle null values in metrics endpoint` |
| `test` | Añadir/modificar tests | `test(services): add unit tests for DashboardService` |
| `docs` | Documentación | `docs(architecture): add layer diagram` |
| `style` | Formato, linting | `style: apply black formatting` |
| `chore` | Tareas de mantenimiento | `chore(deps): update requirements.txt` |
| `perf` | Mejora de performance | `perf(queries): optimize N+1 queries` |

### Ámbitos (Scope)

- `repositories` - Capa de repositorios
- `services` - Capa de servicios
- `views` - Vistas/Controllers
- `models` - Modelos ORM
- `config` - Configuración
- `utils` - Utilidades
- `tests` - Tests
- `deps` - Dependencias

### Ejemplos de Buenos Commits

```bash
# 1. Feature commit
git commit -m "feat(repositories): implement base repository pattern

Adds BaseRepository generic class with CRUD operations:
- Type-safe with Python generics
- Reusable across all models
- Encapsulates SQLAlchemy session management

Fase: 1
Ref: PLAN_REORGANIZACION.md#fase-1
"

# 2. Refactor commit
git commit -m "refactor(views): move queries to MetricaRepository

Extracts all database queries from home/views.py to repositories:
- get_metricas() -> MetricaRepository.get_metricas_with_proveedor()
- get_distinct_apps() -> MetricaRepository.get_distinct_applications()

Reduces view complexity from 150 to 30 lines.

Fase: 3
"

# 3. Test commit
git commit -m "test(repositories): add unit tests for MetricaRepository

Coverage: 95% for MetricaRepository
Tests:
- CRUD operations
- Complex queries with joins
- Edge cases (empty results, null values)

Fase: 1
"

# 4. Fix commit
git commit -m "fix(services): handle division by zero in KPI calculations

Adds safe division in DashboardService._calculate_variations()
Previously crashed when old_data values were 0.

Fixes: #123
"
```

---

## 🔀 Estrategia de Merge

### Opción 1: Merge Commit (Recomendado para este proyecto)

**Ventajas**:
- Preserva historia completa
- Fácil revertir fases completas
- Claro en auditorías

```bash
git merge --no-ff feature/refactor-phase-1-repositories
```

**Resultado**:
```
* Merge branch 'feature/refactor-phase-1-repositories' into develop
|\
| * test(repositories): add unit tests
| * feat(repositories): add MetricaRepository
| * feat(repositories): add base repository
|/
```

### Opción 2: Squash Merge

**Ventajas**:
- Historia limpia en develop
- Un commit por fase

**Cuándo usar**: Fases con muchos commits experimentales

```bash
git merge --squash feature/refactor-phase-4-utilities
git commit -m "feat: complete Phase 4 - Utilities layer"
```

### Opción 3: Rebase (No recomendado para este proyecto)

**Por qué no**: Fases son paralelas y colaborativas, rebase complica.

---

## 🏷️ Estrategia de Tagging

### Tags Semánticos

```
v<major>.<minor>.<patch>-<label>
```

### Tags Durante la Refactorización

| Tag | Cuándo | Propósito |
|-----|--------|-----------|
| `v1.0.0-baseline` | Commit inicial | Punto de restauración |
| `v1.1.0-phase-1` | Después Fase 1 | Repositorios completados |
| `v1.2.0-phase-2` | Después Fase 2 | Servicios completados |
| `v1.3.0-phase-3` | Después Fase 3 | Vistas refactorizadas |
| `v1.4.0-phase-4-7` | Después Fases 4-7 | Utilities + Config |
| `v1.5.0-phase-8-9` | Después Fases 8-9 | Entry points + Tests |
| `v2.0.0` | Merge a main | Refactorización completa |

### Comandos

```bash
# Crear tag anotado
git tag -a v1.1.0-phase-1 -m "Phase 1 completed: Repository layer

✅ BaseRepository implemented
✅ All domain repositories created
✅ SQL queries migrated from models/database.py
✅ Tests coverage: 85%
"

# Subir tags
git push origin v1.1.0-phase-1

# Listar tags
git tag -l

# Ver detalles de tag
git show v1.1.0-phase-1
```

---

## 🚨 Rollback y Recuperación

### Escenario 1: Descartar Cambios en Fase Actual

```bash
# Descartar todos los cambios no commiteados
git reset --hard HEAD

# Descartar commits de la rama feature (volver a develop)
git reset --hard develop
```

### Escenario 2: Revertir Fase Ya Mergeada

```bash
# Opción A: Revert (seguro, crea nuevo commit)
git checkout develop
git revert -m 1 <commit-hash-del-merge>
git push origin develop

# Opción B: Volver a tag anterior (destructivo)
git reset --hard v1.0.0-baseline
git push --force origin develop  # ¡Peligroso!
```

### Escenario 3: Restaurar desde Tag

```bash
# Ver código en un tag específico
git checkout v1.0.0-baseline

# Crear rama desde tag
git checkout -b recover/from-baseline v1.0.0-baseline
```

---

## 🔍 Inspección y Auditoría

### Ver Cambios Entre Fases

```bash
# Diferencias entre tags
git diff v1.0.0-baseline..v1.1.0-phase-1

# Archivos cambiados
git diff --name-only v1.0.0-baseline..v1.1.0-phase-1

# Estadísticas
git diff --stat v1.0.0-baseline..v1.1.0-phase-1
```

### Ver Historia de Archivo Específico

```bash
# Commits que modificaron un archivo
git log --follow -- infocodest/repositories/base_repository.py

# Ver cambios en cada commit
git log -p -- infocodest/models/database.py
```

### Encontrar Cuándo se Introdujo un Bug

```bash
# Git bisect
git bisect start
git bisect bad                    # Commit actual tiene bug
git bisect good v1.0.0-baseline   # Baseline funcionaba
# ... git bisect detecta automáticamente el commit culpable
```

---

## 📊 Workflow Completo por Fase

### Checklist de Inicio de Fase

```bash
# 1. Actualizar develop
git checkout develop
git pull origin develop

# 2. Crear rama de feature
git checkout -b feature/refactor-phase-<N>-<nombre>

# 3. Verificar estado limpio
git status

# 4. Crear tag de checkpoint (opcional)
git tag checkpoint-before-phase-<N>
```

### Checklist Durante la Fase

- [ ] Commits atómicos frecuentes (cada subtarea)
- [ ] Mensajes de commit descriptivos (semánticos)
- [ ] Push al remoto al final del día
- [ ] Tests unitarios para cada componente nuevo
- [ ] Actualizar documentación inline (docstrings)

### Checklist de Fin de Fase

```bash
# 1. Verificar que todos los tests pasan
python -m pytest

# 2. Verificar cobertura
python -m pytest --cov=infocodest --cov-report=term

# 3. Linting y formateo
black infocodest/
flake8 infocodest/

# 4. Commit final de limpieza
git add .
git commit -m "chore(phase-<N>): final cleanup and documentation"

# 5. Push final
git push origin feature/refactor-phase-<N>-<nombre>

# 6. Crear Pull Request
gh pr create --base develop --title "Phase <N>: <Nombre>"

# 7. Después del merge, tag de milestone
git checkout develop
git pull origin develop
git tag -a v1.<N>.0-phase-<N> -m "Phase <N> completed"
git push origin v1.<N>.0-phase-<N>

# 8. Eliminar rama local y remota
git branch -d feature/refactor-phase-<N>-<nombre>
git push origin --delete feature/refactor-phase-<N>-<nombre>
```

---

## 🛡️ Protección de Ramas

### Configuración Recomendada en GitHub/GitLab

#### Rama `main`

- ✅ Require pull request reviews (mínimo 1)
- ✅ Require status checks to pass (CI/CD)
- ✅ Require branches to be up to date
- ✅ Include administrators (no bypass)
- ✅ Restrict force push
- ✅ Restrict deletion

#### Rama `develop`

- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ⚠️ Allow force push (solo para maintainers)
- ✅ Restrict deletion

---

## 📐 Ejemplo Completo: Fase 1

```bash
# === DÍA 1: INICIO FASE 1 ===

# Preparar entorno
git checkout develop
git pull origin develop
git checkout -b feature/refactor-phase-1-repositories

# Trabajo: Crear BaseRepository
# ... editar infocodest/repositories/base_repository.py ...

git add infocodest/repositories/base_repository.py
git add infocodest/repositories/__init__.py
git commit -m "feat(repositories): add base repository pattern

Implements BaseRepository[T] with generic CRUD:
- get_by_id, get_all, filter_by
- create, update, delete
- Type-safe with TypeVar

Fase: 1
Task: 1.1 - Base repository
"

git push -u origin feature/refactor-phase-1-repositories

# === DÍA 2: CONTINUAR FASE 1 ===

# Trabajo: Crear MetricaRepository
# ... editar infocodest/repositories/metrica_repository.py ...

git add infocodest/repositories/metrica_repository.py
git commit -m "feat(repositories): add MetricaRepository

Migrates queries from models/database.py:
- get_distinct_applications()
- get_metricas_with_proveedor()
- count_total_apps(), count_total_repos()
- sum_total_bugs()

Fase: 1
Task: 1.2 - Metrica repository
"

# Trabajo: Tests
# ... editar tests/unit/test_repositories/test_metrica_repository.py ...

git add tests/unit/test_repositories/
git commit -m "test(repositories): add MetricaRepository tests

Coverage: 92%
Tests complex queries, joins, aggregations

Fase: 1
"

git push origin feature/refactor-phase-1-repositories

# === DÍA 3: FINALIZAR FASE 1 ===

# Crear resto de repositorios...
# ... commits similares ...

# Cleanup final
git add .
git commit -m "docs(repositories): add docstrings and type hints

Fase: 1
"

# Verificar tests
python -m pytest --cov=infocodest/repositories

# Push final
git push origin feature/refactor-phase-1-repositories

# Crear PR
gh pr create \
  --base develop \
  --title "Phase 1: Repository Layer Implementation" \
  --body "## Summary
Implements repository pattern for data access layer.

## Changes
- BaseRepository with generic CRUD
- Domain repositories: Metrica, Historico, Proveedor, Daily, User
- Migrated all SQL queries from models/database.py
- Unit tests with 85% coverage

## Testing
\`\`\`bash
pytest tests/unit/test_repositories/ -v
\`\`\`

## Checklist
- [x] Tests pass
- [x] Coverage >80%
- [x] Docstrings added
- [x] Type hints complete

Closes #<issue-number>
"

# Después de merge en GitHub
git checkout develop
git pull origin develop
git tag -a v1.1.0-phase-1 -m "Phase 1 completed: Repository layer"
git push origin v1.1.0-phase-1

# Limpiar
git branch -d feature/refactor-phase-1-repositories
```

---

## 🔄 Integración Continua (CI/CD)

### GitHub Actions Recomendado

**Archivo**: `.github/workflows/test.yml`

```yaml
name: Tests

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop, main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest --cov=infocodest --cov-report=xml --cov-report=term

    - name: Check coverage
      run: |
        coverage report --fail-under=80

    - name: Lint with flake8
      run: |
        flake8 infocodest/ --max-line-length=100
```

---

## 📚 Comandos de Referencia Rápida

```bash
# === SETUP INICIAL ===
git init
git add .
git commit -m "chore: initial commit"
git tag v1.0.0-baseline
git branch develop
git checkout develop

# === NUEVA FASE ===
git checkout develop && git pull
git checkout -b feature/refactor-phase-<N>-<nombre>

# === DURANTE DESARROLLO ===
git add <files>
git commit -m "<tipo>(<ámbito>): <mensaje>"
git push origin feature/refactor-phase-<N>-<nombre>

# === FIN DE FASE ===
pytest && black . && flake8 .
git push origin feature/refactor-phase-<N>-<nombre>
gh pr create --base develop

# === DESPUÉS DEL MERGE ===
git checkout develop && git pull
git tag -a v1.<N>.0-phase-<N> -m "Phase <N> completed"
git push origin v1.<N>.0-phase-<N>

# === INSPECCIÓN ===
git log --oneline --graph --all
git diff v1.0.0-baseline..HEAD
git show v1.1.0-phase-1

# === EMERGENCIA ===
git reset --hard HEAD      # Descartar cambios
git checkout v1.0.0-baseline  # Volver a baseline
```

---

## ✅ Checklist Pre-Implementación

Antes de empezar la Fase 0:

- [ ] Git instalado y configurado
- [ ] Usuario y email configurados globalmente
- [ ] Acceso al repositorio remoto (si existe)
- [ ] `.gitignore` actualizado
- [ ] README.md con instrucciones básicas
- [ ] Tests actuales ejecutándose correctamente
- [ ] Equipo informado del proceso

---

## 🎯 Próximos Pasos

1. **Inicializar Git** (si aún no está)
2. **Crear commit baseline**
3. **Crear rama develop**
4. **Configurar protección de ramas**
5. **Ejecutar Fase 0** siguiendo este workflow

**Siguiente**: Inicialización del repositorio Git
