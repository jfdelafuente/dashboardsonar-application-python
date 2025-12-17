# Documentación para Usuarios - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Usuarios finales, administradores, gestores

---

## 📋 Bienvenido

Esta documentación está diseñada para **usuarios finales** y **administradores** de Dashboard Sonar. Aquí encontrarás todo lo necesario para usar y administrar la aplicación **sin necesidad de soporte técnico**.

---

## 🎯 ¿Qué encontrarás aquí?

### Para Usuarios Finales

Si eres **gestor de proyecto**, **desarrollador**, **QA** o **management** y necesitas:
- ✅ Entender qué es Dashboard Sonar
- ✅ Aprender a usar el dashboard
- ✅ Interpretar las métricas de calidad
- ✅ Exportar datos y generar reportes

**→ Esta documentación es para ti**

### Para Administradores

Si eres **administrador de sistemas** y necesitas:
- ✅ Gestionar usuarios (crear, editar, eliminar)
- ✅ Cargar datos desde SonarQube
- ✅ Configurar la aplicación
- ✅ Realizar backups y mantenimiento

**→ Revisa la [Guía de Administrador](#-guía-de-administrador)**

---

## 🚀 Inicio Rápido

### Si eres nuevo (5 minutos)

**Sigue estos pasos en orden**:

1. **Lee primero**: [¿Qué es Dashboard Sonar?](getting-started/WHAT_IS_DASHBOARD_SONAR.md) (5 min)
   - Entenderás para qué sirve y quién lo usa
   - Conceptos básicos explicados sin tecnicismos

2. **Luego**: [Guía de Usuario](user-guide/USER_GUIDE.md) (15-30 min)
   - Cómo hacer login
   - Cómo buscar y filtrar proyectos
   - Cómo exportar datos

3. **Si tienes dudas**: [FAQ](faq/FAQ.md) (consulta rápida)
   - 50+ preguntas frecuentes respondidas

---

## 📚 Documentación Completa

### 🌟 Primeros Pasos

#### [¿Qué es Dashboard Sonar?](getting-started/WHAT_IS_DASHBOARD_SONAR.md)

**Duración de lectura**: 10 minutos

**Contenido**:
- ✅ Introducción no técnica a la aplicación
- ✅ Para qué sirve y qué problemas resuelve
- ✅ Quién debe usarlo (por rol: gestores, tech leads, developers, QA, management)
- ✅ Beneficios principales
- ✅ Conceptos básicos (SonarQube, métricas, Quality Gates)
- ✅ Casos de uso comunes

**Lee esto primero si**:
- Es tu primer contacto con Dashboard Sonar
- Eres no técnico y necesitas entender el valor
- Vas a presentar la herramienta a otros

**Próximo paso**: [Guía de Usuario](user-guide/USER_GUIDE.md)

---

### 📖 Guía de Usuario

#### [Guía Completa de Usuario](user-guide/USER_GUIDE.md) ⭐ **DOCUMENTO PRINCIPAL**

**Duración de lectura**: 30 minutos (consulta por secciones según necesidad)

**Contenido**:
- ✅ **Acceso**: Login, logout, troubleshooting de credenciales
- ✅ **Navegación**: Interfaz explicada con diagramas ASCII
- ✅ **Funcionalidades**:
  - Buscar proyectos
  - Filtrar por aplicación/proveedor/tamaño
  - Ver detalles de proyectos
  - Ver histórico y tendencias
  - Comparar proyectos lado a lado
  - Monitorear Quality Gates
- ✅ **Exportación**: CSV, Excel, gráficos
- ✅ **Casos de uso prácticos**:
  - Revisión semanal de calidad (Tech Lead)
  - Reporte mensual para management (Quality Manager)
  - Validación post-refactor (Developer)
  - Benchmarking entre equipos (CTO)
  - Auditoría de seguridad (Security Officer)
- ✅ **Interpretación de datos**: Ratings, umbrales, tamaños
- ✅ **FAQ y troubleshooting**

**Lee esto si**:
- Necesitas aprender a usar todas las funcionalidades
- Quieres saber cómo hacer algo específico
- Tienes problemas usando el dashboard

**Próximo paso**: [Explicación de Métricas](user-guide/METRICS_EXPLAINED.md)

---

#### [Métricas Explicadas](user-guide/METRICS_EXPLAINED.md) ⭐ **REFERENCIA CLAVE**

**Duración de lectura**: 40 minutos (consulta por métrica según necesidad)

**Contenido**:
- ✅ **Reliability Rating (A-E)**: Bugs, severidades, impacto en producción
- ✅ **Security Rating (A-E)**: Vulnerabilidades (SQL injection, XSS, etc.)
- ✅ **Maintainability Rating (A-E)**: Deuda técnica, code smells
- ✅ **Coverage (%)**: Cobertura de tests, por qué importa
- ✅ **Duplicación (%)**: Código duplicado, impacto en mantenimiento
- ✅ **Complejidad Ciclomática**: Testabilidad y legibilidad
- ✅ **Deuda Técnica**: Qué es, cómo se calcula, cómo reducirla
- ✅ **Quality Gates**: Reglas y condiciones de aprobación
- ✅ **Tamaño del Proyecto**: Clasificación XS a XL
- ✅ **Umbrales recomendados**: Qué valores son buenos/malos
- ✅ **Matriz de prioridades**: Qué métricas mejorar primero

**Incluye**:
- Ejemplos de código bueno vs malo
- Casos reales de impacto en producción
- Guías de mejora para cada métrica

**Lee esto si**:
- No entiendes qué significa una métrica
- Quieres saber si un valor es bueno o malo
- Necesitas explicar métricas a otros (no técnicos)
- Quieres mejorar las métricas de tu proyecto

**Úsalo como**: Referencia rápida al ver el dashboard

---

### 🔧 Guía de Administrador

#### [Guía de Administración](admin-guide/ADMIN_GUIDE.md) ⭐⭐ **CRÍTICO PARA ADMINS**

**Duración de lectura**: 60 minutos (consulta por sección según necesidad)

**Audiencia**: Administradores de sistemas, System Owners

**Contenido**:

**1. Gestión de Usuarios** (~15 min)
- Crear usuarios (Flask shell + script automatizado)
- Modificar usuarios (cambiar password, promover/degradar admin)
- Listar usuarios
- Eliminar usuarios
- Verificar usuarios existentes

**2. Carga de Datos** (~20 min)
- ✅ Pipeline de carga (run_data_pipeline.bat/sh)
- ✅ Preparación de datos (CSVs)
- ✅ Ejecución del pipeline
- ✅ Verificación de carga exitosa
- ✅ Opciones avanzadas:
  - Directorio de datos personalizado
  - Fechas específicas para snapshots
  - Tamaño de batch
  - Regeneración de datos
  - Saltar pasos específicos
- ✅ Programación automática:
  - Windows Task Scheduler
  - Linux/macOS cron
- ✅ Troubleshooting de carga

**3. Configuración de la Aplicación** (~10 min)
- ✅ Archivo .env (variables críticas)
- ✅ Base de datos (SQLite ↔ PostgreSQL)
- ✅ Seguridad (SECRET_KEY)
- ✅ Modo debug (desarrollo vs producción)
- ✅ Servidor (HOST, PORT)
- ✅ Logging (niveles)
- ✅ Aplicar cambios de configuración

**4. Monitoreo y Logs** (~10 min)
- ✅ Ubicación de logs
- ✅ Ver logs en tiempo real
- ✅ Interpretar logs (niveles, formato)
- ✅ Buscar errores
- ✅ Rotación de logs
- ✅ Cambiar nivel de logging

**5. Backup y Restauración** (~15 min)
- ✅ Backup de PostgreSQL (manual y automatizado)
- ✅ Backup de SQLite
- ✅ Restauración desde backup
- ✅ Backup de configuración (.env, datos, logs)
- ✅ Estrategia de backup recomendada

**6. Mantenimiento** (~10 min)
- ✅ Tareas mensuales (tamaño BD, limpieza logs, verificación backups)
- ✅ Tareas trimestrales (actualización dependencias, auditoría usuarios)
- ✅ Actualización de la aplicación (nuevas versiones)

**7. Troubleshooting** (~10 min)
- ✅ Aplicación no inicia
- ✅ Usuarios no pueden hacer login
- ✅ Datos no se cargan
- ✅ Dashboard muy lento

**Lee esto si**:
- Eres responsable de mantener la aplicación funcionando
- Necesitas crear/gestionar usuarios
- Debes cargar datos periódicamente
- Tienes que hacer backups
- La aplicación presenta problemas

**Úsalo como**: Manual de operaciones completo

---

### ❓ Preguntas Frecuentes

#### [FAQ - Preguntas Frecuentes](faq/FAQ.md)

**Duración de lectura**: Consulta rápida (1-2 min por pregunta)

**Contenido**: 50+ preguntas frecuentes organizadas en 7 categorías:

**1. General** (5 preguntas)
- ¿Qué es Dashboard Sonar?
- ¿Reemplaza a SonarQube?
- ¿Necesito saber programar?
- ¿Es gratis/open source?

**2. Uso del Dashboard** (6 preguntas)
- ¿Cómo accedo?
- ¿Cómo busco un proyecto?
- ¿Cómo filtro por aplicación?
- ¿Cómo veo histórico?
- ¿Cómo comparo proyectos?
- ¿Cómo exporto a Excel?

**3. Métricas y Quality Gates** (10 preguntas)
- ¿Qué significan las letras A-E?
- ¿Qué es Reliability/Security/Maintainability?
- ¿Qué es Coverage/Duplicación?
- ¿Qué es Quality Gate?
- ¿Por qué tengo Rating A pero Quality Gate ERROR?

**4. Datos y Actualización** (4 preguntas)
- ¿Con qué frecuencia se actualizan los datos?
- ¿Puedo ver datos históricos de hace 1 año?
- ¿Los datos son en tiempo real?
- ¿Puedo agregar mis propios proyectos?

**5. Problemas Técnicos** (4 preguntas)
- No puedo hacer login
- Dashboard está lento
- Gráficos no se cargan
- Excel muestra caracteres raros al exportar CSV

**6. Administración** (4 preguntas)
- ¿Cómo solicito acceso?
- ¿Cómo cambio mi contraseña?
- ¿Cómo solicito agregar un proyecto?
- ¿Puedo personalizar el dashboard?

**7. Seguridad y Permisos** (4 preguntas)
- ¿Quién puede ver mis proyectos?
- ¿Los datos son privados?
- ¿Puedo compartir mi sesión?
- ¿Hay auditoría de acciones?

**Lee esto si**:
- Tienes una duda rápida
- No quieres leer documentación extensa
- Buscas respuesta a problema común

**Úsalo como**: Referencia rápida de troubleshooting

---

## 🗺️ Guía de Navegación por Necesidad

### "Necesito aprender a usar el dashboard"

**Ruta recomendada**:
1. [¿Qué es Dashboard Sonar?](getting-started/WHAT_IS_DASHBOARD_SONAR.md) (10 min)
2. [Guía de Usuario - Sección "Acceso"](user-guide/USER_GUIDE.md#acceso-a-la-aplicación) (5 min)
3. [Guía de Usuario - Sección "Navegación"](user-guide/USER_GUIDE.md#navegación-del-dashboard) (10 min)
4. [Guía de Usuario - Sección "Funcionalidades"](user-guide/USER_GUIDE.md#funcionalidades-principales) (15 min)
5. Practica en el dashboard real

**Tiempo total**: 40 minutos

---

### "No entiendo qué significan las métricas"

**Ruta recomendada**:
1. [Métricas Explicadas - Introducción](user-guide/METRICS_EXPLAINED.md#introducción) (2 min)
2. [Métricas Explicadas - La métrica específica que no entiendes](user-guide/METRICS_EXPLAINED.md) (5-10 min)
3. [FAQ - Sección "Métricas y Quality Gates"](faq/FAQ.md#métricas-y-quality-gates) (5 min)

**Tiempo total**: 15-20 minutos

---

### "Necesito exportar datos para un reporte"

**Ruta recomendada**:
1. [Guía de Usuario - Sección "Exportación"](user-guide/USER_GUIDE.md#exportación-de-datos) (5 min)
2. [Guía de Usuario - Caso de Uso: "Reporte Mensual"](user-guide/USER_GUIDE.md#caso-2-preparar-reporte-mensual) (5 min)
3. Si tienes problemas: [FAQ - "Excel muestra caracteres raros"](faq/FAQ.md#exporté-a-csv-pero-excel-muestra-caracteres-raros) (2 min)

**Tiempo total**: 10-15 minutos

---

### "Soy administrador y necesito crear usuarios"

**Ruta recomendada**:
1. [Guía de Administrador - Sección "Gestión de Usuarios"](admin-guide/ADMIN_GUIDE.md#gestión-de-usuarios) (15 min)
2. Prueba crear un usuario de test
3. Si tienes problemas: [Guía de Administrador - Sección "Troubleshooting"](admin-guide/ADMIN_GUIDE.md#troubleshooting)

**Tiempo total**: 20-30 minutos

---

### "Necesito cargar datos nuevos al dashboard"

**Ruta recomendada**:
1. [Guía de Administrador - Sección "Carga de Datos"](admin-guide/ADMIN_GUIDE.md#carga-de-datos) (20 min)
2. Ejecuta el pipeline en modo `--dry-run` primero
3. Si hay errores: [Guía de Administrador - "Solución de Problemas en Carga"](admin-guide/ADMIN_GUIDE.md#solución-de-problemas-en-carga-de-datos) (10 min)

**Tiempo total**: 30-40 minutos

---

### "Tengo un problema y no sé qué hacer"

**Ruta recomendada**:
1. [FAQ](faq/FAQ.md) - Busca tu problema (5 min)
2. Si no lo encuentras: [Guía de Usuario - Sección "Preguntas Frecuentes"](user-guide/USER_GUIDE.md#preguntas-frecuentes) (5 min)
3. Si eres admin: [Guía de Administrador - "Troubleshooting"](admin-guide/ADMIN_GUIDE.md#troubleshooting) (10 min)
4. Si persiste: Contacta soporte (ver sección "Soporte" abajo)

---

## 🎯 Por Rol/Audiencia

### Gestor de Proyecto / Product Owner

**Documentos clave**:
1. ⭐ [¿Qué es Dashboard Sonar?](getting-started/WHAT_IS_DASHBOARD_SONAR.md) - Entiende el valor
2. ⭐ [Guía de Usuario](user-guide/USER_GUIDE.md) - Aprende a usar
3. ⭐ [Métricas Explicadas](user-guide/METRICS_EXPLAINED.md) - Interpreta datos
4. [FAQ](faq/FAQ.md) - Dudas comunes

**Casos de uso relevantes**:
- [Revisión semanal de calidad](user-guide/USER_GUIDE.md#caso-1-revisión-semanal-de-calidad)
- [Preparar reporte mensual](user-guide/USER_GUIDE.md#caso-2-preparar-reporte-mensual)

**Tiempo de onboarding**: 1 hora

---

### Desarrollador

**Documentos clave**:
1. [Guía de Usuario](user-guide/USER_GUIDE.md) - Funcionalidades
2. ⭐ [Métricas Explicadas](user-guide/METRICS_EXPLAINED.md) - Entender métricas técnicas
3. [FAQ](faq/FAQ.md) - Dudas técnicas

**Casos de uso relevantes**:
- [Validar mejora post-refactor](user-guide/USER_GUIDE.md#caso-3-validar-mejora-post-refactor)

**Tiempo de onboarding**: 45 minutos

---

### Tech Lead / Arquitecto

**Documentos clave**:
1. [Guía de Usuario](user-guide/USER_GUIDE.md) - Todas las funcionalidades
2. ⭐ [Métricas Explicadas](user-guide/METRICS_EXPLAINED.md) - Profundizar en métricas
3. [FAQ](faq/FAQ.md) - Consulta rápida

**Casos de uso relevantes**:
- [Revisión semanal](user-guide/USER_GUIDE.md#caso-1-revisión-semanal-de-calidad)
- [Benchmarking de equipos](user-guide/USER_GUIDE.md#caso-4-benchmarking-de-equipos)

**Tiempo de onboarding**: 1.5 horas

---

### Quality Assurance (QA)

**Documentos clave**:
1. [Guía de Usuario](user-guide/USER_GUIDE.md)
2. ⭐ [Métricas Explicadas - Coverage, Quality Gates](user-guide/METRICS_EXPLAINED.md)
3. [FAQ](faq/FAQ.md)

**Casos de uso relevantes**:
- [Auditoría de seguridad](user-guide/USER_GUIDE.md#caso-5-auditoría-de-seguridad)
- Monitorear Quality Gates

**Tiempo de onboarding**: 1 hora

---

### Management / C-Level

**Documentos clave**:
1. ⭐ [¿Qué es Dashboard Sonar?](getting-started/WHAT_IS_DASHBOARD_SONAR.md) - Valor de negocio
2. [Guía de Usuario - Secciones básicas](user-guide/USER_GUIDE.md) - Ver dashboards
3. [Métricas Explicadas - Visión general](user-guide/METRICS_EXPLAINED.md) - Qué significan los números

**Casos de uso relevantes**:
- [Preparar reporte mensual](user-guide/USER_GUIDE.md#caso-2-preparar-reporte-mensual)
- [Benchmarking de equipos](user-guide/USER_GUIDE.md#caso-4-benchmarking-de-equipos)

**Tiempo de onboarding**: 30 minutos

---

### Administrador de Sistemas

**Documentos clave**:
1. ⭐⭐ [Guía de Administrador](admin-guide/ADMIN_GUIDE.md) - TODO
2. [Guía de Usuario](user-guide/USER_GUIDE.md) - Entender qué verán los usuarios
3. [FAQ](faq/FAQ.md) - Preguntas comunes de usuarios

**Funciones principales**:
- Gestión de usuarios
- Carga de datos
- Configuración
- Backups
- Troubleshooting

**Tiempo de onboarding**: 2 horas

---

## 📞 Soporte y Recursos Adicionales

### Documentación Técnica (para desarrolladores)

Si eres **desarrollador** trabajando en el código de Dashboard Sonar:

- 📖 **Documentación Técnica**: [docs/1-technical/](../../1-technical/) *(Fase 2 - Pendiente)*
- 🏗️ **Arquitectura**: [docs/ARCHITECTURE.md](../../ARCHITECTURE.md)
- 💻 **Guía de Desarrollo**: [docs/DEVELOPMENT_GUIDE.md](../../DEVELOPMENT_GUIDE.md)
- 🔧 **Troubleshooting Técnico**: [docs/TROUBLESHOOTING.md](../../TROUBLESHOOTING.md)

### Documentación de Operaciones (para DevOps)

Si eres **DevOps/SRE** desplegando Dashboard Sonar:

- 🚀 **Documentación de Operaciones**: [docs/2-operations/](../../2-operations/) *(Fase 2 - Pendiente)*
- 🐳 **Deployment**: [docs/deployment/DEPLOYMENT.md](../../deployment/DEPLOYMENT.md)
- 🔄 **CI/CD**: [docs/CICD_USER_MANUAL.md](../../CICD_USER_MANUAL.md)
- 📊 **Pipeline de Datos**: [docs/DATA_PIPELINE.md](../../DATA_PIPELINE.md)

### Contacto y Ayuda

**¿Necesitas ayuda?**

- 📧 **Email Soporte**: soporte-dashboard@empresa.com
- 💬 **Slack**: #dashboard-sonar-help
- 🎫 **Portal de Tickets**: [soporte.empresa.com](https://soporte.empresa.com)
- 🐛 **Reportar Bug**: [GitHub Issues](https://github.com/jfdelafuente/dashboardsonar-application-python/issues)
- 💡 **Sugerencias**: [Feature Requests](https://github.com/jfdelafuente/dashboardsonar-application-python/issues)

**Horario de soporte**:
- Lunes a Viernes: 9:00 - 18:00 (horario local)
- Respuesta típica: < 24 horas

---

## 📊 Información del Documento

**Última actualización**: Diciembre 2025
**Versión de la documentación**: 1.0.0
**Versión de la aplicación**: v1.10.0-phase-10
**Mantenido por**: Equipo de Documentación Dashboard Sonar

**Contribuciones**: Si encuentras errores o tienes sugerencias para mejorar esta documentación, envía un email a documentacion-dashboard@empresa.com

---

## ✅ Checklist de Onboarding

### Para Usuarios Nuevos

- [ ] Leí [¿Qué es Dashboard Sonar?](getting-started/WHAT_IS_DASHBOARD_SONAR.md)
- [ ] Tengo usuario y contraseña (si no, solicitarlo al admin)
- [ ] Hice login exitosamente
- [ ] Leí [Guía de Usuario - Acceso y Navegación](user-guide/USER_GUIDE.md)
- [ ] Busqué mi primer proyecto en el dashboard
- [ ] Exporté datos a CSV/Excel
- [ ] Leí explicación de al menos 3 métricas en [Métricas Explicadas](user-guide/METRICS_EXPLAINED.md)
- [ ] Guardé bookmark de [FAQ](faq/FAQ.md) para consultas rápidas

**Tiempo estimado**: 1-2 horas

---

### Para Administradores Nuevos

- [ ] Leí [Guía de Administrador completa](admin-guide/ADMIN_GUIDE.md)
- [ ] Verifiqué acceso SSH al servidor
- [ ] Activé entorno virtual y accedí a Flask Shell
- [ ] Creé un usuario de prueba
- [ ] Ejecuté pipeline de carga de datos en `--dry-run`
- [ ] Ejecuté pipeline de carga real
- [ ] Verifiqué que datos aparecen en dashboard
- [ ] Revisé logs de aplicación
- [ ] Configuré backup automatizado
- [ ] Programé carga automática de datos (cron/Task Scheduler)

**Tiempo estimado**: 2-4 horas

---

## 🎉 ¡Comienza Ahora!

**Primer paso**: [¿Qué es Dashboard Sonar?](getting-started/WHAT_IS_DASHBOARD_SONAR.md)

**¿Tienes prisa?**: Ve directo a [Guía de Usuario](user-guide/USER_GUIDE.md)

**¿Eres administrador?**: Empieza con [Guía de Administrador](admin-guide/ADMIN_GUIDE.md)

---

**¡Bienvenido a Dashboard Sonar! 🚀**
