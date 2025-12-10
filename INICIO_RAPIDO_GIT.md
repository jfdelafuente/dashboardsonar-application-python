# 🚀 Inicio Rápido - Control de Versiones

**Para**: Equipo de desarrollo
**Propósito**: Guía rápida para empezar con el workflow de Git

---

## ⚡ Quick Start (5 minutos)

### Opción 1: Script Automático (Recomendado)

```bash
# En Git Bash o terminal
cd "c:\My Program Files\workspace-claude\dashboardsonar-application-python"

# Dar permisos de ejecución (si es necesario)
chmod +x scripts/init_git_workflow.sh

# Ejecutar script de inicialización
./scripts/init_git_workflow.sh
```

El script hará automáticamente:
- ✅ Inicializar Git (si no está)
- ✅ Crear commit baseline
- ✅ Crear tag `v1.0.0-baseline`
- ✅ Crear rama `develop`
- ✅ Configurar estructura de directorios
- ✅ Actualizar `.gitignore`

### Opción 2: Manual (10 minutos)

```bash
# 1. Inicializar Git
git init

# 2. Configurar usuario
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"

# 3. Crear baseline
git add .
git commit -m "chore: initial commit - baseline before refactoring"

# 4. Crear tag
git tag -a v1.0.0-baseline -m "Baseline before refactoring"

# 5. Crear develop
git checkout -b develop

# 6. Configurar plantilla de commits
git config commit.template .github/COMMIT_TEMPLATE.md
```

---

## 📋 Workflow Diario - Resumen

### Empezar una Nueva Fase

```bash
# Actualizar develop
git checkout develop
git pull origin develop

# Crear rama de feature
git checkout -b feature/refactor-phase-N-nombre

# Ejemplo: Fase 1
git checkout -b feature/refactor-phase-1-repositories
```

### Durante el Desarrollo

```bash
# Hacer cambios en archivos...

# Ver qué cambió
git status
git diff

# Añadir cambios relacionados
git add archivo1.py archivo2.py

# Commit con mensaje descriptivo
git commit -m "feat(repositories): add base repository pattern"

# Push frecuente
git push origin feature/refactor-phase-1-repositories
```

### Finalizar la Fase

```bash
# Asegurarse de que tests pasan
pytest

# Formatear código
black infocodest/

# Push final
git push origin feature/refactor-phase-1-repositories

# Crear Pull Request en GitHub
# (Usar plantilla en .github/PULL_REQUEST_TEMPLATE.md)
```

### Después del Merge

```bash
# Volver a develop
git checkout develop
git pull origin develop

# Crear tag de milestone
git tag -a v1.1.0-phase-1 -m "Phase 1 completed"
git push origin v1.1.0-phase-1

# Limpiar rama local
git branch -d feature/refactor-phase-1-repositories
```

---

## 🎯 Comandos Más Usados

### Información

```bash
# Estado actual
git status

# Ver commits
git log --oneline --graph --all

# Ver tags
git tag -l

# Ver ramas
git branch -a
```

### Trabajo Diario

```bash
# Crear rama
git checkout -b feature/nueva-rama

# Cambiar de rama
git checkout develop

# Ver cambios
git diff
git diff --staged

# Añadir archivos
git add archivo.py
git add .  # Todo

# Commit
git commit -m "mensaje"
git commit  # Abre editor con plantilla

# Push
git push origin nombre-rama
```

### Correcciones

```bash
# Deshacer cambios no commiteados
git restore archivo.py
git restore .  # Todo

# Deshacer último commit (mantiene cambios)
git reset --soft HEAD~1

# Deshacer último commit (descarta cambios)
git reset --hard HEAD~1

# Descartar todos los cambios locales
git reset --hard HEAD
```

---

## 📝 Formato de Mensajes de Commit

### Template Básico

```
<tipo>(<ámbito>): <descripción>

<detalles opcionales>

Fase: N
```

### Tipos Comunes

| Tipo | Cuándo Usar | Ejemplo |
|------|-------------|---------|
| `feat` | Nueva funcionalidad | `feat(repositories): add MetricaRepository` |
| `refactor` | Cambio sin alterar comportamiento | `refactor(views): extract logic to services` |
| `fix` | Corrección de bug | `fix(api): handle null values` |
| `test` | Añadir/modificar tests | `test(services): add unit tests` |
| `docs` | Solo documentación | `docs: update architecture diagram` |
| `chore` | Tareas de mantenimiento | `chore(deps): update requirements.txt` |

### Ejemplo Completo

```
feat(repositories): add base repository pattern

Implements BaseRepository[T] with generic CRUD operations:
- get_by_id, get_all, filter_by
- create, update, delete

All repositories will inherit from this class.

Fase: 1
Task: Create base repository
Ref: PLAN_REORGANIZACION.md#fase-1
```

---

## 🌳 Estructura de Ramas

```
main (production)
  └── develop (integration)
      ├── feature/refactor-phase-0-preparation
      ├── feature/refactor-phase-1-repositories
      ├── feature/refactor-phase-2-services
      └── feature/refactor-phase-3-views
```

### Reglas

1. **main**: Solo código estable, listo para producción
2. **develop**: Integración de features, siempre funcional
3. **feature/***: Trabajo en progreso, una por fase

---

## 🚨 Solución de Problemas Comunes

### "No tengo permisos para ejecutar el script"

```bash
# Windows (Git Bash)
chmod +x scripts/init_git_workflow.sh

# Windows (PowerShell) - ejecutar como:
bash scripts/init_git_workflow.sh
```

### "Conflictos al hacer merge"

```bash
# Ver archivos en conflicto
git status

# Editar archivos manualmente, resolver conflictos
# Buscar marcadores: <<<<<<< HEAD, =======, >>>>>>>

# Después de resolver
git add archivo-resuelto.py
git commit -m "merge: resolve conflicts"
```

### "Cometí en la rama equivocada"

```bash
# Guardar cambios
git stash

# Cambiar a la rama correcta
git checkout rama-correcta

# Aplicar cambios
git stash pop
```

### "Quiero deshacer mi último commit"

```bash
# Mantener cambios en archivos
git reset --soft HEAD~1

# Descartar cambios también
git reset --hard HEAD~1
```

### "Olvidé añadir archivos al último commit"

```bash
# Añadir archivos
git add archivos-olvidados.py

# Amendear último commit
git commit --amend --no-edit
```

---

## ✅ Checklist Pre-Push

Antes de hacer `git push`:

- [ ] Tests pasan: `pytest`
- [ ] Código formateado: `black infocodest/`
- [ ] Sin errores de linting: `flake8 infocodest/`
- [ ] Commit message descriptivo
- [ ] No hay secretos o credenciales en el código

---

## 📚 Recursos

### Documentación Completa

- **Plan completo**: [PLAN_REORGANIZACION.md](PLAN_REORGANIZACION.md)
- **Estrategia Git detallada**: [GIT_STRATEGY.md](GIT_STRATEGY.md)
- **Template PR**: [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- **Template Commit**: [.github/COMMIT_TEMPLATE.md](.github/COMMIT_TEMPLATE.md)

### Tutoriales Git

- [Git Basics - Official](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [Git Branching](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 🆘 Ayuda

### Si tienes dudas:

1. Revisa [GIT_STRATEGY.md](GIT_STRATEGY.md) para detalles
2. Consulta con el equipo
3. Usa `git help <comando>` para documentación

### Comandos de Ayuda

```bash
git help commit
git help branch
git help merge
```

---

## 🎯 Próximo Paso

```bash
# Después de la inicialización, comenzar Fase 0
git checkout -b feature/refactor-phase-0-preparation
```

Luego seguir [PLAN_REORGANIZACION.md](PLAN_REORGANIZACION.md) Fase 0.

---

**¡Listo para empezar! 🚀**
