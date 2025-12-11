# 📋 Templates

Este directorio contiene plantillas para documentar el proceso de refactorización.

---

## 📁 Templates Disponibles

### En este directorio

| Template | Archivo | Propósito |
|----------|---------|-----------|
| **Phase Report** | [PHASE_REPORT_TEMPLATE.md](PHASE_REPORT_TEMPLATE.md) | Template detallado para reportes de cada fase |

### En `.github/` (Templates de GitHub)

| Template | Archivo | Propósito | Uso |
|----------|---------|-----------|-----|
| **Pull Request** | [.github/PULL_REQUEST_TEMPLATE.md](../../.github/PULL_REQUEST_TEMPLATE.md) | Template para PRs | Usado automáticamente por GitHub al crear PRs |
| **Commit Message** | [.github/COMMIT_TEMPLATE.md](../../.github/COMMIT_TEMPLATE.md) | Template para mensajes de commit | Referencia para formato de commits |

---

## 📝 Cómo Usar los Templates

### 1. Phase Report Template

Usado al finalizar cada fase del refactoring:

```bash
# Copiar template
cp docs/templates/PHASE_REPORT_TEMPLATE.md docs/reports/phase-X-nombre.md

# Editar con los datos de la fase
vim docs/reports/phase-X-nombre.md
```

**Cuándo usar**: Al completar cualquier fase (0-10) del refactoring.

**Contenido requerido**:
- Resumen ejecutivo
- Objetivos vs resultados
- Cambios técnicos detallados
- Decisiones de diseño
- Métricas antes/después
- Problemas y soluciones
- Lecciones aprendidas

### 2. Pull Request Template

Usado automáticamente por GitHub al crear un PR:

```bash
# GitHub usa automáticamente .github/PULL_REQUEST_TEMPLATE.md
gh pr create --title "Phase X: Nombre"

# O desde la interfaz web de GitHub
# El template se carga automáticamente
```

**Cuándo usar**: Al crear PR para cada fase completada.

**Contenido incluye**:
- Resumen de cambios
- Checklist de revisión
- Tipo de cambio
- Tests realizados
- Screenshots (si aplica)

### 3. Commit Message Template

Usado como referencia para escribir buenos mensajes de commit:

**Formato**:
```
<tipo>(<ámbito>): <descripción corta>

<descripción larga>

<footer con referencias>
```

**Tipos válidos**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `refactor`: Refactorización
- `docs`: Cambios en documentación
- `test`: Añadir o modificar tests
- `chore`: Tareas de mantenimiento
- `perf`: Mejoras de rendimiento

**Ejemplo**:
```bash
git commit -m "refactor(repositories): implement BaseRepository pattern

Extracted common CRUD operations to BaseRepository generic class.
All domain repositories now inherit from BaseRepository[ModelType].

- Created BaseRepository with TypeVar for model type
- Migrated ProjectRepository to use base class
- Added unit tests with 90% coverage

Closes #123
Phase: 1
"
```

---

## 🔄 Workflow Completo

### Al completar una fase:

1. **Crear Phase Report**:
   ```bash
   cp docs/templates/PHASE_REPORT_TEMPLATE.md docs/reports/phase-X-nombre.md
   # Completar con datos de la fase
   ```

2. **Actualizar CHANGELOG.md**:
   ```bash
   # Añadir entrada para v1.X.0-phase-X
   vim CHANGELOG.md
   ```

3. **Commit de documentación** (usando formato de COMMIT_TEMPLATE.md):
   ```bash
   git add docs/reports/phase-X-nombre.md CHANGELOG.md
   git commit -m "docs: add Phase X completion report and changelog"
   ```

4. **Crear Pull Request** (usa automáticamente PULL_REQUEST_TEMPLATE.md):
   ```bash
   git push -u origin feature/refactor-phase-X-nombre
   gh pr create --title "Phase X: Nombre de la Fase"
   ```

5. **Merge y Tag**:
   ```bash
   # Después de aprobación
   git checkout develop
   git merge feature/refactor-phase-X-nombre
   git tag -a v1.X.0-phase-X -m "Phase X: Nombre completada"
   git push --tags
   ```

---

## 📚 Guías Relacionadas

- **Documentar Cambios**: [docs/guides/DOCUMENTAR_CAMBIOS.md](../guides/DOCUMENTAR_CAMBIOS.md)
- **Estrategia Git**: [docs/git/GIT_STRATEGY.md](../git/GIT_STRATEGY.md)
- **Plan de Reorganización**: [docs/plan/PLAN_REORGANIZACION.md](../plan/PLAN_REORGANIZACION.md)

---

## 📊 Referencias Rápidas

### Semantic Commit Types

| Tipo | Cuándo Usar | Ejemplo |
|------|-------------|---------|
| `feat` | Nueva funcionalidad | `feat(auth): add JWT authentication` |
| `fix` | Bug fix | `fix(api): handle null response from SonarQube` |
| `refactor` | Cambio de código sin cambiar funcionalidad | `refactor(views): extract service layer` |
| `docs` | Solo documentación | `docs: update README with new architecture` |
| `test` | Añadir/modificar tests | `test(repositories): add integration tests` |
| `chore` | Mantenimiento | `chore(deps): update Flask to 3.0.0` |
| `perf` | Mejora de rendimiento | `perf(db): add index on project_key` |
| `style` | Formato, linting | `style: apply black formatter` |

### PR Labels Recomendados

| Label | Descripción | Cuándo Usar |
|-------|-------------|-------------|
| `phase-X` | Fase del refactoring | Todos los PRs de fases |
| `documentation` | Cambios en docs | PRs de documentación |
| `refactoring` | Refactorización | PRs de código refactorizado |
| `breaking-change` | Cambio incompatible | Si rompe API existente |
| `needs-review` | Requiere revisión | PRs listos para review |

---

**Última actualización**: 2025-12-11
