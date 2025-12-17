# Preguntas Frecuentes (FAQ) - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Todos los usuarios

---

## 📋 Tabla de Contenidos

1. [General](#general)
2. [Uso del Dashboard](#uso-del-dashboard)
3. [Métricas y Quality Gates](#métricas-y-quality-gates)
4. [Datos y Actualización](#datos-y-actualización)
5. [Problemas Técnicos](#problemas-técnicos)
6. [Administración](#administración)
7. [Seguridad y Permisos](#seguridad-y-permisos)

---

## 🎯 General

### ¿Qué es Dashboard Sonar?

**R**: Dashboard Sonar es una aplicación web que centraliza y visualiza las métricas de calidad de código de todos los proyectos de tu organización. Los datos provienen de análisis de SonarQube.

**Para qué sirve**:
- Ver estado de calidad de todos los proyectos en un solo lugar
- Comparar proyectos entre sí
- Monitorear tendencias históricas
- Identificar problemas de seguridad y bugs
- Generar reportes para management

**Lee más**: [¿Qué es Dashboard Sonar?](../getting-started/WHAT_IS_DASHBOARD_SONAR.md)

---

### ¿Dashboard Sonar reemplaza a SonarQube?

**R**: **No**. Dashboard Sonar **complementa** a SonarQube.

**Diferencias**:
- **SonarQube**: Analiza el código y detecta problemas (bugs, vulnerabilidades, etc.)
- **Dashboard Sonar**: Visualiza los resultados de SonarQube de forma consolidada

**Flujo**:
```
Código → SonarQube (análisis) → Dashboard Sonar (visualización)
```

**Cuándo usar cada uno**:
- **SonarQube**: Ver detalles técnicos de un proyecto específico (qué línea de código tiene el bug)
- **Dashboard Sonar**: Ver estado general de todos los proyectos, comparar, generar reportes

---

### ¿Es necesario saber programación para usar Dashboard Sonar?

**R**: **No**. Dashboard Sonar está diseñado para usuarios no técnicos.

**Usuarios típicos**:
- Gestores de proyecto (no técnicos)
- Management / C-level (no técnicos)
- Quality Assurance
- Desarrolladores (también lo usan)

**Lee**: [Guía de Usuario](../user-guide/USER_GUIDE.md) (sin conocimientos técnicos requeridos)

---

### ¿Dashboard Sonar es gratis / open source?

**R**: Dashboard Sonar es un proyecto interno desarrollado específicamente para tu organización. El código fuente está disponible en GitHub (privado o público según configuración).

---

## 🖥️ Uso del Dashboard

### ¿Cómo accedo a Dashboard Sonar?

**R**:
1. Abre tu navegador (Chrome, Firefox, Edge, Safari)
2. Ve a la URL proporcionada por tu organización:
   ```
   https://dashboard-sonar.tuempresa.com
   ```
3. Ingresa tu usuario y contraseña
4. Click en "Login"

**Si no tienes usuario**: Contacta al administrador de sistemas.

**Lee**: [Acceso a la Aplicación](../user-guide/USER_GUIDE.md#acceso-a-la-aplicación)

---

### ¿Cómo busco un proyecto específico?

**R**:
1. En el dashboard principal, busca el **campo de búsqueda** (parte superior de la tabla)
2. Escribe el nombre del proyecto (ej: `backend`)
3. La tabla se filtra automáticamente

**Tip**: La búsqueda es parcial y no distingue mayúsculas:
- Buscar `back` encuentra `backend-api`, `backend-service`

**Lee**: [Buscar Proyectos](../user-guide/USER_GUIDE.md#1-buscar-proyectos)

---

### ¿Cómo filtro proyectos por aplicación/equipo?

**R**:
1. Usa los **filtros** en la parte superior del dashboard
2. Click en dropdown **"Aplicación"**
3. Selecciona la aplicación (ej: "Core Backend")
4. La tabla se actualizará automáticamente

**Filtros disponibles**:
- Aplicación
- Proveedor/Equipo
- Tamaño (XS, S, M, L, XL)
- Quality Gate (OK, ERROR)
- Rating (A, B, C, D, E)

**Lee**: [Filtrar por Aplicación](../user-guide/USER_GUIDE.md#2-filtrar-por-aplicación)

---

### ¿Cómo veo el histórico de un proyecto?

**R**:
1. Click en el **nombre del proyecto** en la tabla
2. Se abre la vista detallada
3. Busca la sección **"Histórico"** o **"Tendencias"**
4. Selecciona rango de fechas (últimos 7, 30, 90 días)
5. El gráfico mostrará la evolución de las métricas

**Qué puedes ver**:
- Evolución de coverage
- Evolución de bugs
- Cambios en ratings (A → B → C)

**Lee**: [Ver Histórico](../user-guide/USER_GUIDE.md#4-ver-histórico-de-un-proyecto)

---

### ¿Cómo comparo 2 o más proyectos?

**R**:
1. Selecciona **checkbox** de los proyectos que quieres comparar
2. Click en botón **"Comparar Seleccionados"**
3. Se mostrará una tabla comparativa lado a lado

**Uso típico**: Comparar proyectos similares para identificar best practices.

**Lee**: [Comparar Proyectos](../user-guide/USER_GUIDE.md#5-comparar-proyectos)

---

### ¿Cómo exporto los datos a Excel?

**R**:
1. Aplica los filtros deseados (para exportar solo lo que necesitas)
2. Click en botón **"Exportar"** (icono 📥)
3. Selecciona formato:
   - **CSV**: Para importar en otras herramientas
   - **Excel (.xlsx)**: Para análisis en Excel
4. El archivo se descargará automáticamente

**Contenido del archivo**: Todas las columnas visibles y solo los proyectos filtrados.

**Lee**: [Exportación de Datos](../user-guide/USER_GUIDE.md#exportación-de-datos)

---

## 📊 Métricas y Quality Gates

### ¿Qué significan las letras A, B, C, D, E?

**R**: Son **calificaciones** que indican la calidad del código:

| Rating | Significado | Color |
|--------|-------------|-------|
| **A** | Excelente | 🟢 Verde |
| **B** | Bueno | 🟢 Verde claro |
| **C** | Medio | 🟡 Amarillo |
| **D** | Malo | 🟠 Naranja |
| **E** | Muy malo / Crítico | 🔴 Rojo |

**Ejemplo**:
- Reliability **A** = 0 bugs (excelente)
- Security **E** = Vulnerabilidades críticas (muy malo, **no desplegar**)

**Lee**: [Calificaciones Explicadas](../user-guide/METRICS_EXPLAINED.md#calificaciones-ratings-a-e)

---

### ¿Qué es Reliability?

**R**: Mide la **confiabilidad** del código (probabilidad de que funcione sin bugs).

**Rating basado en**:
- **A**: 0 bugs
- **B**: Solo bugs menores
- **C**: Bugs mayores
- **D**: Bugs críticos
- **E**: Bugs bloqueantes (aplicación crashea)

**En producción**:
- Rating **A/B**: Aplicación estable
- Rating **D/E**: Alto riesgo de crashes y errores

**Lee**: [Reliability Rating Detallado](../user-guide/METRICS_EXPLAINED.md#reliability-rating)

---

### ¿Qué es Security?

**R**: Mide la **seguridad** del código (vulnerabilidades que podrían ser explotadas).

**Rating basado en**:
- **A**: 0 vulnerabilidades (muy seguro)
- **B**: Vulnerabilidades menores
- **C**: Vulnerabilidades mayores
- **D**: Vulnerabilidades críticas
- **E**: Vulnerabilidades bloqueantes (hackeable)

**Tipos de vulnerabilidades**:
- SQL Injection
- Cross-Site Scripting (XSS)
- Hardcoded passwords
- Weak cryptography

**Lee**: [Security Rating Detallado](../user-guide/METRICS_EXPLAINED.md#security-rating)

---

### ¿Qué es Maintainability?

**R**: Mide qué tan **fácil es mantener y modificar** el código en el futuro.

**Basado en Deuda Técnica**:
- **A**: ≤ 5% deuda (muy mantenible)
- **B**: 6-10% deuda (mantenible)
- **C**: 11-20% deuda (algo difícil)
- **D**: 21-50% deuda (difícil)
- **E**: > 50% deuda (código legacy, muy difícil)

**Impacto práctico**:
- Rating **A**: Agregar feature toma 2 días
- Rating **D**: La misma feature toma 4 días (código complejo)

**Lee**: [Maintainability Rating Detallado](../user-guide/METRICS_EXPLAINED.md#maintainability-rating)

---

### ¿Qué es Coverage?

**R**: Porcentaje del código cubierto por tests automáticos.

**Ejemplo**:
- **85% coverage** = 85% del código tiene tests
- Si cambias código, los tests detectarán el 85% de los bugs

**Umbrales**:
- **> 80%**: 🟢 Excelente
- **60-80%**: 🟢 Bueno
- **40-60%**: 🟡 Medio
- **< 40%**: 🔴 Insuficiente

**Por qué importa**: Más coverage = menos bugs en producción.

**Lee**: [Coverage Detallado](../user-guide/METRICS_EXPLAINED.md#coverage-cobertura-de-tests)

---

### ¿Qué es Duplicación?

**R**: Porcentaje de código copiado/pegado.

**Ejemplo**:
- **2% duplicación** = 2 de cada 100 líneas están duplicadas
- **20% duplicación** = 1 de cada 5 líneas está duplicada

**Por qué es malo**:
- Si cambias lógica, tienes que cambiarla en N lugares
- Aumenta bugs por cambios inconsistentes
- Mantenimiento 3x más caro

**Umbrales**:
- **< 3%**: 🟢 Excelente
- **3-5%**: 🟢 Aceptable
- **> 10%**: 🔴 Muy alto

**Lee**: [Duplicación Detallada](../user-guide/METRICS_EXPLAINED.md#duplicación-de-código)

---

### ¿Qué es Quality Gate?

**R**: Un conjunto de **reglas** que el código debe cumplir para considerarse "aprobado para producción".

**Ejemplo de reglas**:
```
✅ Bugs críticos = 0
✅ Vulnerabilidades mayores = 0
✅ Coverage > 80%
✅ Duplicación < 3%
```

**Estados**:
- ✅ **OK**: Todas las reglas se cumplen (puede ir a producción)
- ❌ **ERROR**: Al menos una regla falla (NO desplegar)

**Analogía**: Como la inspección técnica de un auto. Si falla, no puedes circular.

**Lee**: [Quality Gates Detallado](../user-guide/METRICS_EXPLAINED.md#quality-gates)

---

### Mi proyecto tiene Rating A pero Quality Gate ERROR. ¿Por qué?

**R**: Quality Gate evalúa **múltiples condiciones**, no solo un rating.

**Ejemplo**:
- Reliability: **A** (0 bugs) ✅
- Security: **A** (0 vulnerabilidades) ✅
- Coverage: **65%** ❌ (requerido > 80%)
- **Quality Gate: ERROR** (porque coverage falla)

**Solución**: Ver en la vista detallada qué condición específica está fallando y mejorarla.

---

## 🔄 Datos y Actualización

### ¿Con qué frecuencia se actualizan los datos?

**R**: Depende de la configuración de tu organización. Típicamente:

- **Proyectos activos**: Diariamente (cada commit a main/develop)
- **Proyectos en mantenimiento**: Semanalmente
- **Proyectos legacy**: Mensualmente o bajo demanda

**Cómo verificar cuándo se actualizó**:
- En la tabla, columna **"Última Actualización"** muestra la fecha del último análisis

**Si necesitas actualización inmediata**: Contacta al administrador para ejecutar análisis de SonarQube y carga de datos.

---

### ¿Puedo ver datos de hace 6 meses o 1 año?

**R**: **Sí**, siempre que esos análisis históricos hayan sido cargados en la base de datos.

**Cómo ver histórico**:
1. Ir a vista detallada del proyecto
2. Sección "Histórico"
3. Seleccionar rango de fechas personalizado
4. Especificar fecha inicio y fin

**Limitación**: Solo puedes ver análisis que existen en la base de datos. Si el proyecto se creó hace 3 meses, no hay datos de hace 1 año.

---

### ¿Los datos que veo son en tiempo real?

**R**: **No**. Los datos son un **snapshot** del último análisis de SonarQube que se cargó.

**Flujo típico**:
```
1. Developer hace commit → GitHub
2. CI/CD ejecuta SonarQube → Análisis del código
3. Resultados exportados a CSV
4. Script carga CSV a Dashboard Sonar
5. Dashboard muestra los datos (30 min - 24h después del commit)
```

**Para datos en tiempo real**: Consulta directamente SonarQube (no Dashboard Sonar).

---

### ¿Puedo agregar mis propios proyectos al dashboard?

**R**: **No directamente**. Los proyectos provienen de análisis de SonarQube.

**Proceso**:
1. Configurar SonarQube para analizar tu proyecto
2. Ejecutar análisis de SonarQube
3. Los resultados se exportan a CSV
4. El administrador ejecuta script de carga de datos
5. Tu proyecto aparecerá en Dashboard Sonar

**Contacta**: Al administrador de SonarQube para agregar tu proyecto.

---

## 🐛 Problemas Técnicos

### No puedo hacer login. ¿Qué hago?

**R**: Verifica lo siguiente:

**1. Credenciales correctas**:
- Usuario y contraseña distinguen mayúsculas/minúsculas
- No hay espacios extra antes/después del usuario

**2. Usuario existe**:
- Contacta al administrador para verificar que tu usuario está creado

**3. Cuenta no bloqueada**:
- Después de 5 intentos fallidos, cuenta se bloquea por 15 minutos
- Espera o contacta al administrador para desbloquear

**4. Navegador**:
- Limpia cookies/caché
- Prueba en modo incógnito
- Prueba otro navegador

**Si persiste**: Contacta al administrador para resetear tu password.

**Lee**: [Problemas de Login](../user-guide/USER_GUIDE.md#problemas-de-login)

---

### El dashboard está muy lento. ¿Es normal?

**R**: **No**. El dashboard debería cargar en menos de 5 segundos.

**Causas posibles**:
1. **Muchos proyectos** (> 100): Usa filtros para reducir cantidad
2. **Conexión a internet lenta**: Verifica tu velocidad
3. **Servidor sobrecargado**: Contacta al administrador
4. **Navegador con muchas pestañas**: Cierra pestañas innecesarias

**Soluciones temporales**:
- Filtrar por aplicación específica
- Usar paginación (ir a página 2, 3 en lugar de ver todos)
- Cerrar y volver a abrir navegador

**Si persiste**: Reporta al administrador (puede necesitar optimización de BD).

---

### Los gráficos no se cargan. ¿Qué hago?

**R**:
1. **Refresca la página**: Ctrl+F5 (Windows) o Cmd+Shift+R (Mac)
2. **Limpia caché del navegador**
3. **Verifica JavaScript habilitado**: Dashboard requiere JS activo
4. **Prueba otro navegador**: Chrome, Firefox, Edge

**Si solo afecta a un proyecto**:
- Puede que ese proyecto no tenga datos históricos
- Contacta al administrador

---

### Exporté a CSV pero Excel muestra caracteres raros

**R**: Problema de **encoding**. Dashboard exporta en UTF-8, pero Excel a veces usa otro encoding.

**Solución**:
1. Abre Excel
2. **Datos** → **Desde texto/CSV**
3. Selecciona el archivo CSV descargado
4. En **Origen del archivo**, selecciona **UTF-8**
5. Click **Cargar**

**Alternativa**: Exporta a Excel (.xlsx) en lugar de CSV (no tiene problema de encoding).

---

## 👨‍💼 Administración

### ¿Cómo solicito acceso a Dashboard Sonar?

**R**:
1. Contacta al administrador de sistemas de tu organización
2. Indica:
   - Tu nombre completo
   - Email corporativo
   - Rol/equipo
   - Justificación (ej: "Necesito monitorear calidad del proyecto Backend")
3. El administrador creará tu usuario y te enviará credenciales

**Tiempo típico**: 1-2 días hábiles.

---

### ¿Cómo cambio mi contraseña?

**R**: Actualmente Dashboard Sonar **no tiene** funcionalidad de cambio de password por UI.

**Proceso**:
1. Contacta al administrador
2. Solicita reset de password
3. El administrador cambiará tu password y te enviará la nueva

**En futuras versiones**: Se agregará funcionalidad de "Cambiar Password" en perfil de usuario.

---

### ¿Cómo solicito que se agregue un proyecto al dashboard?

**R**:
1. Contacta al **administrador de SonarQube** (no Dashboard Sonar)
2. Solicita que tu proyecto sea agregado a SonarQube
3. Una vez que SonarQube esté analizando tu proyecto
4. Contacta al **administrador de Dashboard** para cargar los datos

**Tiempo típico**:
- Configurar SonarQube: 1-2 días
- Aparecer en Dashboard: 1 día después del primer análisis

---

### ¿Puedo personalizar el dashboard (agregar/quitar columnas)?

**R**: **No en la versión actual**. El dashboard muestra un conjunto fijo de columnas:
- Nombre, Aplicación, Quality Gate, Reliability, Security, Maintainability, Coverage, Duplicación, Tamaño

**En futuras versiones**: Se considerará agregar:
- Preferencias de usuario (qué columnas mostrar)
- Dashboards personalizados por rol
- Widgets configurables

**Sugerencia**: Si necesitas columnas específicas, exporta a CSV y personaliza en Excel.

---

## 🔒 Seguridad y Permisos

### ¿Quién puede ver mis proyectos?

**R**: Depende de la configuración:

**Configuración típica**:
- **Usuarios normales**: Ven solo proyectos de su equipo/aplicación
- **Administradores**: Ven todos los proyectos de la organización

**Si tienes dudas**: Contacta al administrador para confirmar qué proyectos puedes ver.

---

### ¿Los datos son privados o se comparten externamente?

**R**: Los datos son **100% privados** dentro de tu organización.

**Seguridad**:
- Dashboard Sonar corre en servidores internos (no cloud público, a menos que tu org use cloud privado)
- Solo usuarios autenticados pueden acceder
- Datos no se comparten con terceros
- No hay tracking o analytics externo

---

### ¿Puedo compartir mi sesión con un compañero?

**R**: **No recomendado por seguridad**.

**Riesgos**:
- Tu compañero podría hacer acciones bajo tu usuario (no hay auditoría clara)
- Si compartes password, es difícil revocarlo después

**Mejor práctica**:
- Solicita al administrador que cree usuario para tu compañero
- Comparte **pantallas** o **exporta datos** a Excel para compartir

---

### ¿Dashboard Sonar tiene auditoría de acciones?

**R**: **Parcialmente**. Los logs registran:
- ✅ Logins exitosos y fallidos
- ✅ IP desde donde se conecta el usuario
- ✅ Timestamp de acceso

**No se registra actualmente**:
- ❌ Qué proyectos vio cada usuario
- ❌ Qué exportó cada usuario
- ❌ Qué filtros usó

**En futuras versiones**: Se agregará auditoría completa de acciones.

---

## 📞 ¿No encontraste tu pregunta?

### Recursos Adicionales

- 📖 **Guía Completa de Usuario**: [USER_GUIDE.md](../user-guide/USER_GUIDE.md)
- 📊 **Explicación de Métricas**: [METRICS_EXPLAINED.md](../user-guide/METRICS_EXPLAINED.md)
- 🔧 **Guía de Administrador**: [ADMIN_GUIDE.md](../admin-guide/ADMIN_GUIDE.md)
- 🐛 **Troubleshooting Técnico**: [TROUBLESHOOTING.md](../../TROUBLESHOOTING.md)

### Contacto

- 📧 **Email**: soporte-dashboard@empresa.com
- 💬 **Slack**: #dashboard-sonar-help
- 🎫 **Portal de Tickets**: [soporte.empresa.com](https://soporte.empresa.com)
- 🐛 **Reportar Bug**: [GitHub Issues](https://github.com/jfdelafuente/dashboardsonar-application-python/issues)

---

**Última actualización**: Diciembre 2025
**Versión del documento**: 1.0.0
**Contribuciones**: Si tienes una pregunta frecuente que no está aquí, envíala a soporte-dashboard@empresa.com
