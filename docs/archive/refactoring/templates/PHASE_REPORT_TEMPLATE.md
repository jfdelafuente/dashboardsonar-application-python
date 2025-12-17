# Phase [N]: [Nombre de la Fase] - Report

**Fecha**: YYYY-MM-DD
**Duración Real**: X horas (estimado: Y horas)
**Estado**: [✅ Completado | ⚠️ Parcial | ❌ Bloqueado]

---

## 📊 Resumen Ejecutivo

<!-- 3-5 líneas que resuman los logros principales de la fase -->

[Descripción breve del trabajo realizado, resultados clave y estado general]

---

## 🎯 Objetivos vs Resultados

| Objetivo | Planificado | Real | Estado | Notas |
|----------|-------------|------|--------|-------|
| [Objetivo 1] | ✅ | ✅ | Completo | - |
| [Objetivo 2] | ✅ | ⚠️ | Parcial | [Razón] |
| [Objetivo 3] | ✅ | ✅ | Completo | - |
| [Extra no planificado] | ❌ | ✅ | Añadido | [Justificación] |

**Cumplimiento**: X de Y objetivos (XX%)

---

## 🔧 Cambios Técnicos Detallados

### Archivos Creados

| Archivo | LOC | Propósito | Tests |
|---------|-----|-----------|-------|
| `path/to/file.py` | 150 | [Descripción breve] | ✅ 90% |
| `path/to/another.py` | 200 | [Descripción breve] | ✅ 85% |

**Total**: X archivos, Y líneas de código

#### Detalles Importantes

- **`archivo1.py`**:
  - Función principal: `nombre_funcion()`
  - Patrón usado: [Repository/Service/etc.]
  - Dependencias: [lista]

### Archivos Modificados

| Archivo | LOC Antes | LOC Después | Δ | Cambio Principal |
|---------|-----------|-------------|---|------------------|
| `path/to/modified.py` | 150 | 75 | -75 | Refactorizado lógica a servicio |

### Archivos Eliminados

| Archivo | Razón de Eliminación | Migrado a |
|---------|---------------------|-----------|
| `path/to/deleted.py` | [Razón] | `nuevo/path.py` |

### Estructura de Directorios Creada

```
infocodest/
├── new_directory/
│   ├── __init__.py
│   ├── component1.py
│   └── component2.py
```

---

## 🎨 Decisiones de Diseño

### Decisión 1: [Título de la Decisión]

**Contexto**: [Por qué se necesitaba tomar esta decisión]

**Decisión**: [Qué se decidió hacer]

**Alternativas Consideradas**:
1. **Opción A**: [Descripción] - Rechazada porque [razón]
2. **Opción B**: [Descripción] - Rechazada porque [razón]
3. **Opción C (Elegida)**: [Descripción] - Elegida porque [razón]

**Justificación**:
- Razón 1
- Razón 2
- Razón 3

**Trade-offs**:
- ✅ Pro: [Beneficio]
- ❌ Con: [Desventaja aceptada]

**Referencias**:
- [Documentación relevante]
- [Artículo/Blog post]

**Impacto**:
- Archivos afectados: [lista]
- Fases futuras afectadas: [lista]

---

### Decisión 2: [Otra Decisión Importante]

[Mismo formato que Decisión 1]

---

## 📊 Métricas

### Tabla Comparativa

| Métrica | Antes | Después | Δ | Objetivo | Estado |
|---------|-------|---------|---|----------|--------|
| LOC en vistas | 150 | 30 | -120 (-80%) | <50 | ✅ Superado |
| Cobertura tests | 60% | 85% | +25% | >80% | ✅ Superado |
| Queries por request | 10 | 2 | -8 (-80%) | <5 | ✅ Logrado |
| Tiempo respuesta API | 500ms | 50ms | -450ms (-90%) | <100ms | ✅ Superado |
| Complejidad ciclomática | 15 | 4 | -11 (-73%) | <5 | ✅ Logrado |

### Gráficos

<!-- Si tienes screenshots o gráficos, incluirlos aquí -->

**Tiempo de Respuesta - Antes vs Después**:
```
Antes:  ████████████████████████████ 500ms
Después: ██ 50ms
```

### Tests

```bash
# Comando ejecutado
$ pytest tests/unit/test_[componente]/ -v --cov

# Resultados
===================== 42 passed in 2.3s ======================

# Coverage
----------- coverage: 85% of infocodest/[componente] -----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
component1.py                   45      3    93%
component2.py                   38      8    79%
-------------------------------------------------
TOTAL                           83     11    85%
```

---

## 🐛 Problemas Encontrados y Soluciones

### Problema 1: [Título del Problema]

**Descripción**: [Explicación detallada del problema]

**Síntoma**:
```python
# Código que causaba el error
# O mensaje de error
```

**Causa Raíz**: [Explicación de por qué ocurrió]

**Solución**:
```python
# Código de la solución
# O pasos seguidos
```

**Prevención**: [Cómo evitar este problema en el futuro]

**Commit**: `a1b2c3d` - [mensaje del commit]

**Tiempo Perdido**: X horas

---

### Problema 2: [Otro Problema]

[Mismo formato]

---

## 💡 Lecciones Aprendidas

### 1. [Lección Técnica]

**Aprendizaje**: [Qué aprendimos]

**Contexto**: [En qué situación]

**Aplicación Futura**:
- En qué fases aplicar este conocimiento
- Qué hacer diferente

**Ejemplo**:
```python
# Código de ejemplo que ilustra el aprendizaje
```

---

### 2. [Lección de Proceso]

**Aprendizaje**: [Qué aprendimos sobre el proceso]

**Impacto**: [Cómo afecta a futuras fases]

**Recomendación**: [Qué cambiar en el workflow]

---

## 🔴 Deuda Técnica Identificada

### 1. [Título de Deuda Técnica]

**Descripción**: [Qué se dejó pendiente o se hizo de forma subóptima]

**Razón**: [Por qué se decidió dejar para después]

**Impacto**:
- **Performance**: [Alto/Medio/Bajo]
- **Mantenibilidad**: [Alto/Medio/Bajo]
- **Seguridad**: [Alto/Medio/Bajo]

**Prioridad**: [Alta/Media/Baja]

**Plan de Resolución**:
- **Cuándo**: [En qué fase abordar]
- **Cómo**: [Solución propuesta]
- **Esfuerzo Estimado**: X horas

**Issue Tracking**: #123

---

### 2. [Otra Deuda Técnica]

[Mismo formato]

---

## 🔜 Próximos Pasos

### Para la Siguiente Fase

1. [Acción específica 1]
   - Por qué es necesario
   - Qué archivos afecta

2. [Acción específica 2]
   - Dependencia de esta fase
   - Qué preparar

### Bloqueadores Resueltos

- ✅ [Bloqueador 1 que se resolvió]
- ✅ [Bloqueador 2 que se resolvió]

### Bloqueadores Pendientes

- ⚠️ [Bloqueador que afecta siguiente fase]
  - Impacto: [descripción]
  - Plan: [cómo resolver]

### Recomendaciones para el Equipo

1. **Técnicas**:
   - [Recomendación 1]
   - [Recomendación 2]

2. **De Proceso**:
   - [Recomendación 1]
   - [Recomendación 2]

---

## 📸 Screenshots / Evidencias

<!-- Incluir capturas de pantalla relevantes -->

### Antes
![Before](./images/phase-N-before.png)

### Después
![After](./images/phase-N-after.png)

### Tests Pasando
```
[Paste de output de tests]
```

---

## 📎 Referencias

- **Commits de la fase**: [Compare v1.X-1.0...v1.X.0-phase-X](https://github.com/user/repo/compare/...)
- **Pull Request**: [#XX](https://github.com/user/repo/pull/XX)
- **Issues relacionados**: [#YY](https://github.com/user/repo/issues/YY), [#ZZ](https://github.com/user/repo/issues/ZZ)
- **Documentación**: [PLAN_REORGANIZACION.md Fase X](../plan/PLAN_REORGANIZACION.md#fase-x)
- **Artículos/Referencias Externas**:
  - [Link 1]
  - [Link 2]

---

## 👥 Contribuidores

**Autor Principal**: [Nombre]
**Revisores**: [Nombre 1], [Nombre 2]
**Consultados**: [Nombre experto en X]

---

## ✅ Checklist de Completitud

- [ ] Todos los objetivos cumplidos o justificados
- [ ] Métricas medidas y documentadas
- [ ] Tests con >80% coverage
- [ ] Sin warnings de linter
- [ ] Documentación inline (docstrings) añadida
- [ ] CHANGELOG.md actualizado
- [ ] Pull Request creado y aprobado
- [ ] Tag creado y pusheado
- [ ] Deuda técnica documentada
- [ ] Lecciones aprendidas capturadas

---

**Fecha de Finalización**: YYYY-MM-DD
**Tag**: v1.X.0-phase-X
**Aprobado por**: [Tech Lead]
