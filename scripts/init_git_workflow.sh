#!/bin/bash
# Script de Inicialización del Workflow de Git
# Ejecutar ANTES de empezar la Fase 0

set -e  # Exit on error

echo "🚀 Inicializando Workflow de Git para Refactorización"
echo "=================================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "📁 Directorio del proyecto: $PROJECT_DIR"

# ============================================
# PASO 1: Verificar si Git ya está inicializado
# ============================================
echo ""
echo "📋 Paso 1: Verificando estado de Git..."

if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git ya está inicializado${NC}"
    echo "   Saltando inicialización de git init"
    GIT_INITIALIZED=true
else
    echo -e "${GREEN}✅ Git no inicializado. Procediendo con init...${NC}"
    GIT_INITIALIZED=false
fi

# ============================================
# PASO 2: Verificar que los tests actuales pasen
# ============================================
echo ""
echo "🧪 Paso 2: Verificando que los tests actuales pasen..."

if command -v pytest &> /dev/null; then
    echo "   Ejecutando pytest..."

    if pytest --tb=short -q; then
        echo -e "${GREEN}✅ Tests pasaron correctamente${NC}"
    else
        echo -e "${RED}❌ Tests fallaron. Corrige los tests antes de continuar.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  pytest no encontrado. Saltando verificación de tests.${NC}"
    read -p "   ¿Continuar sin verificar tests? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ============================================
# PASO 3: Configurar Git (si no está inicializado)
# ============================================
if [ "$GIT_INITIALIZED" = false ]; then
    echo ""
    echo "🔧 Paso 3: Configurando Git..."

    # Verificar configuración global
    if [ -z "$(git config --global user.name)" ]; then
        echo -e "${YELLOW}⚠️  Git user.name no configurado globalmente${NC}"
        read -p "   Ingresa tu nombre: " git_name
        git config --global user.name "$git_name"
    fi

    if [ -z "$(git config --global user.email)" ]; then
        echo -e "${YELLOW}⚠️  Git user.email no configurado globalmente${NC}"
        read -p "   Ingresa tu email: " git_email
        git config --global user.email "$git_email"
    fi

    echo "   Usuario Git: $(git config --global user.name) <$(git config --global user.email)>"

    # Inicializar repositorio
    echo "   Inicializando repositorio Git..."
    git init
    echo -e "${GREEN}✅ Git inicializado${NC}"
fi

# ============================================
# PASO 4: Crear commit baseline (si no existe)
# ============================================
echo ""
echo "📝 Paso 4: Creando commit baseline..."

if [ "$GIT_INITIALIZED" = false ] || [ -z "$(git log -1 2>/dev/null)" ]; then
    echo "   Añadiendo archivos al staging area..."
    git add .

    echo "   Creando commit baseline..."
    git commit -m "chore: initial commit - baseline before refactoring

- Project structure as-is
- All existing functionality working
- Tests passing (baseline coverage)

This commit serves as the baseline for the refactoring project.
Reference: docs/plan/PLAN_REORGANIZACION.md, docs/git/GIT_STRATEGY.md"

    echo -e "${GREEN}✅ Commit baseline creado${NC}"
else
    echo -e "${YELLOW}⚠️  Ya existen commits. Saltando creación de baseline.${NC}"
fi

# ============================================
# PASO 5: Crear tag de baseline
# ============================================
echo ""
echo "🏷️  Paso 5: Creando tag de baseline..."

if git rev-parse v1.0.0-baseline >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Tag v1.0.0-baseline ya existe${NC}"
else
    git tag -a v1.0.0-baseline -m "Baseline before architecture refactoring

This tag marks the state of the project before starting
the architecture refactoring process.

All functionality is working and tests are passing.

Next: Phase 0 - Preparation
"
    echo -e "${GREEN}✅ Tag v1.0.0-baseline creado${NC}"
fi

# ============================================
# PASO 6: Crear rama develop
# ============================================
echo ""
echo "🌳 Paso 6: Creando rama develop..."

current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

if git rev-parse --verify develop >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Rama develop ya existe${NC}"
else
    # Asegurarse de que estamos en main
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        git checkout -b main 2>/dev/null || git checkout main 2>/dev/null || true
    fi

    # Crear develop desde main/master
    git checkout -b develop
    git config branch.develop.description "Integration branch for refactoring"

    echo -e "${GREEN}✅ Rama develop creada${NC}"
fi

# Asegurarse de estar en develop
git checkout develop 2>/dev/null || echo -e "${YELLOW}⚠️  Ya estás en develop${NC}"

# ============================================
# PASO 7: Configurar plantilla de commit
# ============================================
echo ""
echo "📋 Paso 7: Configurando plantilla de commit..."

if [ -f ".github/COMMIT_TEMPLATE.md" ]; then
    git config commit.template .github/COMMIT_TEMPLATE.md
    echo -e "${GREEN}✅ Plantilla de commit configurada${NC}"
    echo "   Usa 'git commit' (sin -m) para abrir el editor con la plantilla"
else
    echo -e "${YELLOW}⚠️  Plantilla de commit no encontrada${NC}"
fi

# ============================================
# PASO 8: Verificar/Crear estructura de directorios para las fases
# ============================================
echo ""
echo "📂 Paso 8: Creando estructura de directorios..."

directories=(
    "infocodest/repositories"
    "infocodest/services"
    "infocodest/utils"
    "infocodest/exceptions"
    "config"
    "logs"
    "tests/unit/test_repositories"
    "tests/unit/test_services"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        touch "$dir/__init__.py" 2>/dev/null || true
        echo "   ✅ Creado: $dir"
    else
        echo "   ⏭️  Ya existe: $dir"
    fi
done

echo -e "${GREEN}✅ Estructura de directorios lista${NC}"

# ============================================
# PASO 9: Crear .gitkeep para directorios vacíos
# ============================================
echo ""
echo "📌 Paso 9: Creando .gitkeep en directorios vacíos..."

for dir in "${directories[@]}"; do
    if [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
        touch "$dir/.gitkeep"
        echo "   ✅ .gitkeep en $dir"
    fi
done

# ============================================
# PASO 10: Verificar .gitignore
# ============================================
echo ""
echo "🚫 Paso 10: Verificando .gitignore..."

if [ -f ".gitignore" ]; then
    echo -e "${GREEN}✅ .gitignore existe${NC}"

    # Añadir entradas si no existen
    gitignore_entries=(
        "logs/"
        "*.log"
        ".pytest_cache/"
        ".coverage"
        "htmlcov/"
        "__pycache__/"
        "*.pyc"
        "db.sqlite3"
        "testdb.sqlite3"
        ".env"
        "venv/"
        ".venv/"
    )

    for entry in "${gitignore_entries[@]}"; do
        if ! grep -q "^${entry}$" .gitignore; then
            echo "$entry" >> .gitignore
            echo "   ✅ Añadido a .gitignore: $entry"
        fi
    done
else
    echo -e "${YELLOW}⚠️  .gitignore no encontrado. Creando uno nuevo...${NC}"
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual Environment
venv/
.venv/
ENV/
env/

# Flask
instance/
.webassets-cache

# Database
*.sqlite3
*.db

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
EOF
    echo -e "${GREEN}✅ .gitignore creado${NC}"
fi

# ============================================
# PASO 11: Commit de preparación (si hay cambios)
# ============================================
echo ""
echo "💾 Paso 11: Guardando configuración inicial..."

if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "chore: setup git workflow for refactoring

- Created directory structure for new layers
- Updated .gitignore
- Configured commit template
- Ready for Phase 0

Ref: docs/git/GIT_STRATEGY.md
" || echo -e "${YELLOW}⚠️  No hay cambios para commitear${NC}"

    echo -e "${GREEN}✅ Configuración commiteada${NC}"
else
    echo "   No hay cambios para commitear"
fi

# ============================================
# PASO 12: Resumen y próximos pasos
# ============================================
echo ""
echo "=========================================="
echo -e "${GREEN}✅ ¡Inicialización Completada!${NC}"
echo "=========================================="
echo ""
echo "📊 Estado Actual:"
echo "   - Rama actual: $(git rev-parse --abbrev-ref HEAD)"
echo "   - Último commit: $(git log -1 --oneline)"
echo "   - Tags: $(git tag -l | tr '\n' ', ' | sed 's/,$//')"
echo ""
echo "📚 Documentación:"
echo "   - Índice principal: docs/README.md"
echo "   - Plan completo: docs/plan/PLAN_REORGANIZACION.md"
echo "   - Estrategia Git: docs/git/GIT_STRATEGY.md"
echo "   - Guía rápida: docs/guides/INICIO_RAPIDO.md"
echo "   - Template PR: .github/PULL_REQUEST_TEMPLATE.md"
echo "   - Template Commit: .github/COMMIT_TEMPLATE.md"
echo ""
echo "🚀 Próximos Pasos:"
echo ""
echo "   1. Revisar docs/README.md (índice completo)"
echo "   2. Leer docs/guides/INICIO_RAPIDO.md"
echo "   3. Ejecutar Fase 0: Preparación"
echo "      $ git checkout -b feature/refactor-phase-0-preparation"
echo ""
echo "   4. Seguir el workflow de docs/git/GIT_STRATEGY.md para cada fase"
echo ""
echo "💡 Comandos Útiles:"
echo "   - Ver estado: git status"
echo "   - Ver historial: git log --oneline --graph --all"
echo "   - Ver tags: git tag -l"
echo "   - Crear rama fase: git checkout -b feature/refactor-phase-N-nombre"
echo ""
echo "=================================================="
echo -e "${GREEN}¡Listo para empezar la refactorización! 🎉${NC}"
echo "=================================================="
