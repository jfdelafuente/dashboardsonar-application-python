# Guía de Usuario - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Usuarios finales (gestores, developers, QA, tech leads)

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Acceso a la Aplicación](#acceso-a-la-aplicación)
3. [Navegación del Dashboard](#navegación-del-dashboard)
4. [Funcionalidades Principales](#funcionalidades-principales)
5. [Interpretación de Datos](#interpretación-de-datos)
6. [Exportación de Datos](#exportación-de-datos)
7. [Casos de Uso Prácticos](#casos-de-uso-prácticos)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🎯 Introducción

Esta guía te enseñará cómo usar **Dashboard Sonar** para:

- ✅ Visualizar métricas de calidad de código
- ✅ Filtrar y buscar proyectos/repositorios
- ✅ Analizar tendencias históricas
- ✅ Comparar calidad entre proyectos
- ✅ Exportar datos para reportes
- ✅ Monitorear Quality Gates

**Prerequisitos**:
- Tener un usuario activo (proporcionado por el administrador)
- Acceso a la URL de Dashboard Sonar
- Navegador moderno (Chrome, Firefox, Edge, Safari)

---

## 🔐 Acceso a la Aplicación

### Paso 1: Abrir la aplicación

Abre tu navegador y ve a la URL proporcionada por tu organización:

```
https://dashboard-sonar.tuempresa.com
```

O si es entorno local:
```
http://localhost:5000
```

### Paso 2: Pantalla de Login

Verás la pantalla de inicio de sesión con:

```
┌──────────────────────────────────┐
│   Dashboard Sonar                │
│   ═══════════════════            │
│                                  │
│   Usuario:  [______________]    │
│   Password: [______________]    │
│                                  │
│           [  Login  ]            │
│                                  │
│   ¿Olvidaste tu contraseña?     │
└──────────────────────────────────┘
```

**Campos**:
- **Usuario**: Tu nombre de usuario (ejemplo: `jperez`)
- **Password**: Tu contraseña

### Paso 3: Iniciar Sesión

1. Ingresa tu **usuario**
2. Ingresa tu **contraseña**
3. Click en el botón **"Login"**

Si las credenciales son correctas, serás redirigido al **Dashboard Principal**.

### Problemas de Login

❌ **Error: "Invalid credentials"**
- **Causa**: Usuario o contraseña incorrectos
- **Solución**: Verifica que estás escribiendo correctamente (mayúsculas/minúsculas importan)

❌ **Error: "Account disabled"**
- **Causa**: Tu cuenta ha sido desactivada
- **Solución**: Contacta al administrador

❌ **Error: "Too many failed attempts"**
- **Causa**: Demasiados intentos fallidos de login
- **Solución**: Espera 15 minutos o contacta al administrador

### Cerrar Sesión

Para salir de la aplicación de forma segura:

1. Click en tu **nombre de usuario** (esquina superior derecha)
2. Selecciona **"Logout"**
3. Serás redirigido a la pantalla de login

**Importante**: Siempre cierra sesión cuando uses computadoras compartidas.

---

## 🏠 Navegación del Dashboard

### Dashboard Principal

Después del login, verás el **Dashboard Principal** con varias secciones:

```
┌─────────────────────────────────────────────────────────────────────┐
│ [Logo] Dashboard Sonar              Usuario: Juan Pérez    [Logout] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [🏠 Dashboard] [📊 Métricas] [📈 Histórico] [⚙️ Configuración]     │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Filtros:                                                           │
│  Aplicación: [Todas ▼]  Proveedor: [Todos ▼]  Tamaño: [Todos ▼]    │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📊 Resumen General                                                 │
│  ┌───────┬───────┬───────┬───────┬───────────┐                     │
│  │ Total │ QG OK │ Rating│ Bugs  │ Coverage  │                     │
│  │  45   │  38   │  A    │  12   │   82%     │                     │
│  └───────┴───────┴───────┴───────┴───────────┘                     │
│                                                                      │
│  📋 Proyectos                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Nombre        │ App     │ QG    │ Reliability │ Security │... │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ backend-api   │ Core    │ ✅ OK │     A       │    A     │... │  │
│  │ frontend-web  │ Core    │ ✅ OK │     B       │    A     │... │  │
│  │ mobile-app    │ Mobile  │ ❌ ERR│     C       │    B     │... │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  [  Anterior  ]  Página 1 de 3  [  Siguiente  ]                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Elementos de la Interfaz

#### 1. Barra de Navegación Superior

**Elementos**:
- **Logo**: Click para volver al dashboard principal
- **Usuario**: Muestra tu nombre, click para ver perfil/logout
- **Menú de navegación**:
  - 🏠 **Dashboard**: Vista principal
  - 📊 **Métricas**: Vista detallada de métricas
  - 📈 **Histórico**: Tendencias temporales
  - ⚙️ **Configuración**: Preferencias (solo admins)

#### 2. Filtros

Permiten reducir los datos mostrados:

- **Aplicación**: Filtra por aplicación/producto (Backend, Frontend, Mobile, etc.)
- **Proveedor**: Filtra por equipo/proveedor externo
- **Tamaño**: Filtra por tamaño del repositorio (XS, S, M, L, XL)
- **Quality Gate**: Filtra por estado (OK, ERROR)
- **Rating**: Filtra por calificación (A, B, C, D, E)

**Uso de Filtros**:
1. Click en el dropdown del filtro
2. Selecciona el valor deseado
3. La tabla se actualizará automáticamente

**Limpiar Filtros**:
- Click en **"Limpiar Filtros"** para volver a ver todos los datos

#### 3. Resumen General (KPIs)

Tarjetas con indicadores clave:

- **Total Proyectos**: Cantidad total de repositorios
- **QG OK**: Cantidad con Quality Gate aprobado
- **Rating Promedio**: Calificación promedio (A-E)
- **Bugs Totales**: Suma de bugs en todos los proyectos
- **Coverage Promedio**: % promedio de cobertura de tests

#### 4. Tabla de Proyectos

Muestra todos los repositorios con sus métricas:

**Columnas principales**:
- **Nombre**: Nombre del repositorio
- **Aplicación**: A qué aplicación/producto pertenece
- **Quality Gate**: ✅ OK o ❌ ERROR
- **Reliability**: Calificación A-E
- **Security**: Calificación A-E
- **Maintainability**: Calificación A-E
- **Coverage**: % de cobertura de tests
- **Duplicación**: % de código duplicado
- **Tamaño**: XS, S, M, L, XL
- **Última Actualización**: Fecha del último análisis

**Ordenamiento**:
- Click en el **encabezado de columna** para ordenar
- Click nuevamente para invertir el orden (ascendente/descendente)

**Paginación**:
- Usa **"Anterior"** / **"Siguiente"** para navegar entre páginas
- Por defecto muestra 20 proyectos por página

---

## 🔧 Funcionalidades Principales

### 1. Buscar Proyectos

**Ubicación**: Campo de búsqueda en la parte superior de la tabla

**Uso**:
1. Escribe el nombre del proyecto (ej: `backend`)
2. La tabla se filtra automáticamente mostrando solo coincidencias
3. Borra el texto para ver todos los proyectos nuevamente

**Búsqueda soportada**:
- ✅ Búsqueda parcial: `back` encuentra `backend-api`, `backend-service`
- ✅ No distingue mayúsculas/minúsculas: `BACKEND` = `backend`
- ✅ Busca en nombre del proyecto y aplicación

**Ejemplo**:
```
Buscar: "payment"
Resultado:
  - payment-service
  - payment-gateway
  - payment-processor
```

---

### 2. Filtrar por Aplicación

**Uso**:
1. Click en dropdown **"Aplicación"**
2. Selecciona una aplicación de la lista (ej: "Core Backend")
3. Solo se mostrarán proyectos de esa aplicación

**Aplicaciones típicas**:
- Core Backend
- Frontend Web
- Mobile Apps
- Microservicios
- Legacy Systems
- APIs Externas

**Combinar con otros filtros**:
```
Aplicación: "Core Backend"
+ Quality Gate: "ERROR"
= Solo proyectos backend con problemas
```

---

### 3. Ver Detalles de un Proyecto

**Uso**:
1. Busca el proyecto en la tabla
2. Click en el **nombre del proyecto** (es un link)
3. Se abrirá una vista detallada

**Vista Detallada contiene**:

```
┌────────────────────────────────────────────┐
│  Proyecto: backend-api                     │
│  Aplicación: Core Backend                  │
│  Proveedor: Equipo Interno                 │
│  Tamaño: L (50,000 líneas)                 │
├────────────────────────────────────────────┤
│                                            │
│  Quality Gate: ✅ OK                       │
│                                            │
│  📊 Métricas Actuales                      │
│  ├─ Reliability:      A (0 bugs)          │
│  ├─ Security:         A (0 vulnerab.)     │
│  ├─ Maintainability:  B (8% deuda)        │
│  ├─ Coverage:         85%                  │
│  ├─ Duplicación:      2.3%                 │
│  └─ Complejidad:      45                   │
│                                            │
│  📈 Tendencia (últimos 30 días)            │
│  [Gráfico de líneas mostrando evolución]  │
│                                            │
│  📋 Detalles Adicionales                   │
│  - Bugs: 0 (0 críticos, 0 mayores)        │
│  - Vulnerabilidades: 0                     │
│  - Code Smells: 45 (5 mayores, 40 menores)│
│  - Deuda Técnica: 4 días                   │
│                                            │
│  🔗 Enlaces                                │
│  - [Ver en SonarQube]                      │
│  - [Ver Código en Git]                     │
│                                            │
│  [← Volver al Dashboard]                   │
└────────────────────────────────────────────┘
```

---

### 4. Ver Histórico de un Proyecto

**Uso**:
1. En la vista detallada del proyecto, busca sección **"Histórico"**
2. Selecciona rango de fechas (últimos 7, 30, 90 días, o personalizado)
3. El gráfico se actualizará mostrando tendencias

**Gráficos disponibles**:

**A. Evolución de Calificaciones**
```
Rating
  A  ████████████████████
  B  ████
  C
  D
  E
     └────────────────────> Tiempo
     Ene  Feb  Mar  Abr
```

**B. Evolución de Coverage**
```
Coverage (%)
 100% ┤
  80% ┤    ╭─╮
  60% ┤───╯  ╰───
  40% ┤
   0% └────────────────────> Tiempo
```

**C. Evolución de Bugs**
```
Bugs
  50 ┤
  25 ┤  ●
  10 ┤    ╲
   0 ┤     ╲●───●───●
     └────────────────────> Tiempo
```

**Interpretación**:
- ✅ **Línea ascendente** en coverage = Mejorando
- ✅ **Línea descendente** en bugs = Mejorando
- ❌ **Línea descendente** en coverage = Empeorando
- ❌ **Línea ascendente** en bugs = Empeorando

---

### 5. Comparar Proyectos

**Uso**:
1. Selecciona checkbox de 2 o más proyectos en la tabla
2. Click en botón **"Comparar Seleccionados"**
3. Se mostrará una tabla comparativa

**Vista Comparativa**:

| Métrica | Proyecto A | Proyecto B | Proyecto C |
|---------|-----------|-----------|-----------|
| **Reliability** | A | B | C |
| **Security** | A | A | B |
| **Coverage** | 85% | 72% | 45% |
| **Duplicación** | 2% | 8% | 15% |
| **Bugs** | 0 | 5 | 23 |

**Indicadores**:
- 🟢 **Verde**: Mejor valor
- 🟡 **Amarillo**: Valor intermedio
- 🔴 **Rojo**: Peor valor

**Uso práctico**:
- Comparar proyectos similares
- Identificar best practices (proyecto con mejores métricas)
- Detectar outliers (proyecto muy por debajo del promedio)

---

### 6. Monitorear Quality Gates

**¿Qué es un Quality Gate?**

Un conjunto de reglas que el código debe cumplir para ser "aprobado".

**Ejemplo de Quality Gate**:
```
Condiciones:
✅ Bugs críticos = 0
✅ Vulnerabilidades mayores = 0
✅ Coverage > 80%
✅ Duplicación < 3%
✅ Deuda técnica < 5%
```

**Estados posibles**:
- ✅ **OK**: Todas las condiciones se cumplen
- ❌ **ERROR**: Al menos una condición falla

**Cómo ver qué falló**:
1. Click en proyecto con Quality Gate **ERROR**
2. En vista detallada, busca sección **"Quality Gate"**
3. Verás lista de condiciones:

```
Quality Gate: ❌ ERROR

Condiciones que fallan:
❌ Coverage: 65% (requerido: > 80%)
❌ Duplicación: 5.2% (requerido: < 3%)

Condiciones que pasan:
✅ Bugs críticos: 0
✅ Vulnerabilidades: 0
✅ Deuda técnica: 3%
```

**Acción recomendada**:
- Si eres **desarrollador**: Agrega tests y reduce duplicación
- Si eres **gestor**: Asigna tareas de mejora al equipo
- Si es **bloqueante**: No permitir despliegue a producción hasta resolver

---

## 📊 Interpretación de Datos

### Calificaciones (Ratings) A-E

| Rating | Significado | Color | Acción Recomendada |
|--------|-------------|-------|-------------------|
| **A** | Excelente | 🟢 Verde | Mantener |
| **B** | Bueno | 🟢 Verde claro | Mantener o mejorar |
| **C** | Medio | 🟡 Amarillo | Planificar mejoras |
| **D** | Malo | 🟠 Naranja | Mejorar urgentemente |
| **E** | Muy malo | 🔴 Rojo | **CRÍTICO** - Acción inmediata |

### Umbrales Recomendados

| Métrica | Excelente | Bueno | Aceptable | Malo | Crítico |
|---------|-----------|-------|-----------|------|---------|
| **Coverage** | >80% | 60-80% | 40-60% | 20-40% | <20% |
| **Duplicación** | <3% | 3-5% | 5-10% | 10-15% | >15% |
| **Complejidad** | <10 | 10-20 | 20-30 | 30-50 | >50 |
| **Deuda Técnica** | <5% | 5-10% | 10-20% | 20-30% | >30% |

### Tamaño de Repositorios

| Tamaño | Líneas de Código | Ejemplo |
|--------|------------------|---------|
| **XS** | < 1,000 | Librerías pequeñas |
| **S** | 1,000 - 10,000 | Microservicios |
| **M** | 10,000 - 50,000 | APIs, servicios medianos |
| **L** | 50,000 - 100,000 | Aplicaciones completas |
| **XL** | > 100,000 | Monolitos, sistemas legacy |

**Nota**: Proyectos más grandes (XL) suelen tener mayor complejidad y deuda técnica.

---

## 📥 Exportación de Datos

### Exportar Tabla a CSV/Excel

**Uso**:
1. Aplica los filtros deseados
2. Click en botón **"Exportar"** (icono 📥)
3. Selecciona formato:
   - **CSV**: Para importar en otras herramientas
   - **Excel (.xlsx)**: Para análisis en Excel

**Contenido del archivo**:
- Todas las columnas visibles en la tabla
- Solo los proyectos filtrados actualmente
- Incluye headers (encabezados)

**Ejemplo de CSV**:
```csv
Nombre,Aplicación,Quality Gate,Reliability,Security,Maintainability,Coverage,Duplicación
backend-api,Core,OK,A,A,B,85%,2.3%
frontend-web,Core,OK,B,A,B,72%,3.1%
mobile-app,Mobile,ERROR,C,B,C,45%,8.2%
```

**Usos comunes**:
- Crear reportes personalizados en Excel
- Importar a Power BI / Tableau
- Análisis estadístico avanzado
- Compartir con stakeholders sin acceso al dashboard

---

### Exportar Gráfico

**Uso**:
1. En vista de gráfico (histórico, tendencias)
2. Click derecho en el gráfico
3. Selecciona **"Guardar imagen como..."**
4. Guarda como PNG/JPG

**Uso común**:
- Incluir en presentaciones
- Reportes de progreso
- Documentación de mejoras

---

## 🎯 Casos de Uso Prácticos

### Caso 1: Revisión Semanal de Calidad

**Rol**: Tech Lead

**Objetivo**: Revisar estado de calidad de mis 10 proyectos cada lunes.

**Pasos**:
1. Login en Dashboard Sonar
2. Filtrar por **Aplicación** = "Mi App"
3. Ordenar por **Quality Gate** (ERROR primero)
4. Identificar proyectos con ❌
5. Click en cada proyecto para ver qué falló
6. Crear tareas en Jira/Asana para resolver problemas
7. Exportar tabla a CSV para archivo

**Tiempo**: 15 minutos

**Resultado**: Lista priorizada de tareas de mejora técnica.

---

### Caso 2: Preparar Reporte Mensual

**Rol**: Quality Manager

**Objetivo**: Presentar estado de calidad a dirección.

**Pasos**:
1. Login en Dashboard Sonar
2. Seleccionar **"Todas las aplicaciones"**
3. Anotar KPIs del Resumen General:
   - Total proyectos: 45
   - QG OK: 38 (84%)
   - Bugs totales: 67
   - Coverage promedio: 78%
4. Filtrar por **Quality Gate** = "ERROR"
5. Exportar lista de proyectos con problemas
6. Ir a sección **Histórico**
7. Exportar gráficos de tendencia (últimos 3 meses)
8. Crear presentación PowerPoint con:
   - KPIs actuales
   - Tendencias (¿mejorando o empeorando?)
   - Top 5 proyectos con peor calidad
   - Plan de acción

**Tiempo**: 45 minutos

**Resultado**: Presentación ejecutiva lista.

---

### Caso 3: Validar Mejora Post-Refactor

**Rol**: Desarrollador

**Objetivo**: Confirmar que el refactor mejoró las métricas.

**Pasos**:
1. Anotar métricas **antes del refactor**:
   - Maintainability: C
   - Complejidad: 78
   - Duplicación: 12%
2. Realizar refactorización
3. Ejecutar análisis de SonarQube
4. Esperar ~30 minutos a que Dashboard actualice
5. Volver a Dashboard Sonar
6. Buscar el proyecto
7. Comparar métricas **después del refactor**:
   - Maintainability: B
   - Complejidad: 32
   - Duplicación: 4%
8. Ver gráfico histórico para confirmar tendencia

**Tiempo**: 5 minutos (después del análisis)

**Resultado**: Validación objetiva de que el refactor funcionó.

---

### Caso 4: Benchmarking de Equipos

**Rol**: CTO

**Objetivo**: Comparar calidad de código entre 3 equipos.

**Pasos**:
1. Filtrar por **Proveedor** = "Equipo A"
2. Anotar promedio de Coverage, Bugs, Duplicación
3. Repetir para Equipo B y Equipo C
4. Crear tabla comparativa:

| Equipo | Coverage | Bugs | Duplicación | Rating Prom. |
|--------|----------|------|-------------|--------------|
| A | 88% | 12 | 2.1% | A |
| B | 75% | 34 | 5.8% | B |
| C | 62% | 67 | 9.2% | C |

5. Identificar equipo con mejores prácticas (Equipo A)
6. Organizar sesión de knowledge sharing

**Tiempo**: 20 minutos

**Resultado**: Insights para mejorar procesos de desarrollo.

---

### Caso 5: Auditoría de Seguridad

**Rol**: Security Officer

**Objetivo**: Encontrar proyectos con vulnerabilidades.

**Pasos**:
1. Login en Dashboard Sonar
2. Ordenar tabla por **Security** (peor primero)
3. Filtrar por **Security Rating** = "D" o "E"
4. Para cada proyecto:
   - Click en nombre
   - Ver cantidad de vulnerabilidades
   - Ver severidad (crítica, mayor, menor)
   - Anotar tipo de vulnerabilidad
5. Exportar lista completa a CSV
6. Crear plan de remediación con deadlines:
   - Críticas: 7 días
   - Mayores: 30 días
   - Menores: 90 días

**Tiempo**: 30 minutos

**Resultado**: Plan de acción con prioridades claras.

---

## ❓ Preguntas Frecuentes

### General

**P: ¿Con qué frecuencia se actualizan los datos?**

R: Los datos se actualizan cada vez que se ejecuta un análisis de SonarQube. Típicamente:
- Proyectos activos: Diariamente (cada commit a main)
- Proyectos en mantenimiento: Semanalmente
- Consulta al administrador para frecuencia específica

---

**P: ¿Puedo ver datos históricos de hace 1 año?**

R: Sí, todos los análisis históricos están disponibles. En la vista de proyecto, selecciona rango de fechas personalizado.

---

**P: ¿Por qué mi proyecto no aparece en el dashboard?**

R: Posibles causas:
1. No se ha ejecutado análisis de SonarQube aún
2. No tienes permisos para ver ese proyecto
3. El proyecto fue eliminado
4. Contacta al administrador

---

**P: ¿Puedo editar datos en el dashboard?**

R: No. Dashboard Sonar es una herramienta de **solo lectura**. Los datos provienen de SonarQube y no pueden modificarse aquí.

---

### Métricas

**P: ¿Qué significa "Deuda Técnica"?**

R: Es una estimación del tiempo necesario para arreglar todos los code smells. Por ejemplo:
- Deuda técnica: 15 días = Se necesitarían 15 días de trabajo para arreglar todos los problemas de mantenibilidad.

---

**P: ¿Por qué Coverage bajó del 85% al 83%?**

R: Posibles causas:
1. Se agregó código nuevo sin tests
2. Se eliminaron tests
3. Se cambiaron configuraciones de análisis
4. Revisa commits recientes para identificar causa

---

**P: Mi proyecto tiene Rating A pero Quality Gate ERROR. ¿Por qué?**

R: Quality Gate evalúa múltiples condiciones, no solo el rating. Puede tener Rating A en Reliability pero fallar en Coverage (< 80%).

---

### Exportación

**P: ¿El CSV incluye todos los proyectos?**

R: Solo incluye proyectos visibles actualmente (después de aplicar filtros). Para exportar todos, limpia los filtros primero.

---

**P: ¿Puedo programar exportación automática mensual?**

R: No directamente desde la UI. Contacta al administrador para configurar exportaciones automáticas por email.

---

### Permisos

**P: ¿Puedo ver proyectos de otros equipos?**

R: Depende de tus permisos. Usuarios normales ven solo sus proyectos. Administradores ven todos.

---

**P: ¿Cómo solicito acceso a más proyectos?**

R: Contacta al administrador de Dashboard Sonar con justificación de negocio.

---

## 📞 Soporte

### ¿Necesitas ayuda?

**Documentación adicional**:
- 📖 [Explicación de Métricas](METRICS_EXPLAINED.md)
- 🔧 [Guía de Administrador](../admin-guide/ADMIN_GUIDE.md)
- ❓ [FAQ Completo](../faq/FAQ.md)
- 🐛 [Troubleshooting](../../TROUBLESHOOTING.md)

**Contacto**:
- 📧 **Email**: soporte-dashboard@tuempresa.com
- 💬 **Slack**: #dashboard-sonar-help
- 🎫 **Tickets**: [Portal de Soporte](https://soporte.tuempresa.com)

**Reportar problemas**:
- 🐛 **Bugs**: [GitHub Issues](https://github.com/jfdelafuente/dashboardsonar-application-python/issues)
- 💡 **Sugerencias**: [Feature Requests](https://github.com/jfdelafuente/dashboardsonar-application-python/issues)

---

## 📚 Próximos Pasos

1. **Practica**: Explora el dashboard con los filtros y búsquedas
2. **Profundiza**: Lee [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md) para entender cada métrica
3. **Personaliza**: Pide al administrador configurar alertas personalizadas
4. **Comparte**: Enseña a tu equipo a usar el dashboard

---

**Última actualización**: Diciembre 2025
**Versión del documento**: 1.0.0
**Autor**: Equipo de Calidad
**Próxima revisión**: Marzo 2026
