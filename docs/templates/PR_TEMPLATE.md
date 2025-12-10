# Pull Request: Phase [N] - [Nombre de la Fase]

## 📋 Descripción

<!-- Describe brevemente los cambios realizados en esta fase -->

**Fase**: [Número y nombre de la fase]
**Referencia**: [PLAN_REORGANIZACION.md#fase-N]

## 🎯 Objetivos de la Fase

<!-- Lista los objetivos principales de esta fase según el plan -->

- [ ] Objetivo 1
- [ ] Objetivo 2
- [ ] Objetivo 3

## 🔧 Cambios Realizados

### Archivos Nuevos
<!-- Lista de archivos creados -->

- `path/to/new/file.py` - Descripción
- `path/to/another/file.py` - Descripción

### Archivos Modificados
<!-- Lista de archivos modificados significativamente -->

- `path/to/modified/file.py` - Qué se cambió y por qué
- `path/to/another/modified.py` - Qué se cambió y por qué

### Archivos Eliminados
<!-- Lista de archivos eliminados -->

- `path/to/deleted/file.py` - Por qué se eliminó

## 🧪 Testing

### Tests Ejecutados

```bash
# Comando(s) para ejecutar tests
pytest tests/unit/test_repositories/ -v
pytest tests/integration/ -v
```

### Cobertura de Código

- **Cobertura actual**: X%
- **Cobertura anterior**: Y%
- **Delta**: +Z%

### Tests Añadidos

<!-- Lista de nuevos tests añadidos -->

- `tests/unit/test_*.py` - Descripción de qué testea
- `tests/integration/test_*.py` - Descripción de qué testea

## 📊 Métricas

### Antes vs Después

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Líneas de código en vistas | XXX | YYY | -ZZ% |
| Complejidad ciclomática | XX | YY | -Z |
| Queries SQL en vistas | XX | 0 | -100% |
| Cobertura de tests | XX% | YY% | +Z% |

## 🔍 Puntos de Revisión

<!-- Aspectos específicos que necesitan atención en la revisión -->

- [ ] Revisar implementación de [componente específico]
- [ ] Validar que no se rompe funcionalidad existente
- [ ] Verificar que tests son suficientemente robustos
- [ ] Comprobar documentación inline (docstrings)

## ✅ Checklist Pre-Merge

### Funcionalidad
- [ ] Todos los tests pasan localmente
- [ ] Tests de integración pasan
- [ ] No hay regresiones en funcionalidad existente
- [ ] La aplicación arranca correctamente

### Calidad de Código
- [ ] Código formateado con `black`
- [ ] Linting pasado (`flake8`)
- [ ] Type hints añadidos donde corresponde
- [ ] Docstrings completos en funciones públicas

### Documentación
- [ ] README.md actualizado (si aplica)
- [ ] PLAN_REORGANIZACION.md actualizado con progreso
- [ ] Comentarios en código complejo
- [ ] CHANGELOG.md actualizado (si aplica)

### Git
- [ ] Commits con mensajes descriptivos (semánticos)
- [ ] No hay secretos o credenciales en el código
- [ ] `.gitignore` actualizado (si aplica)
- [ ] Sin conflictos con `develop`

## 🚨 Breaking Changes

<!-- ¿Hay cambios que rompen compatibilidad? -->

- [ ] **NO** hay breaking changes
- [ ] **SÍ** hay breaking changes (especificar abajo)

**Detalle de breaking changes**:
<!-- Si aplica, describe qué se rompe y cómo migrar -->

## 📸 Screenshots / Evidencias

<!-- Si aplica, añade capturas de pantalla o logs que demuestren funcionalidad -->

## 🔗 Referencias

- Issue relacionado: #XXX
- Documentación: [Link]
- Referencia externa: [Link]

## 👥 Reviewers Sugeridos

<!-- @menciona a personas específicas si es necesario -->

@username1 - Para revisar [aspecto específico]
@username2 - Para revisar [aspecto específico]

## 💬 Notas Adicionales

<!-- Cualquier información adicional que el revisor deba saber -->

---

**Tipo de Merge Recomendado**:
- [ ] Merge Commit (preservar historia completa)
- [ ] Squash Merge (historia limpia)

**Después del Merge**:
- [ ] Crear tag `v1.X.0-phase-N`
- [ ] Eliminar rama feature
- [ ] Actualizar tablero de proyecto
