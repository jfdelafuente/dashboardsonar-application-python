# Análisis Completo de Documentación del Proyecto
# Dashboard Sonar Application - Python

**Fecha de Análisis**: 2025-12-17
**Versión del Proyecto**: v1.10.0-phase-10
**Analista**: Equipo de Arquitectura
**Propósito**: Reestructuración de documentación para independencia del cliente

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Inventario Completo de Documentación](#inventario-completo-de-documentación)
3. [Análisis de Brechas (Gap Analysis)](#análisis-de-brechas-gap-analysis)
4. [Clasificación por Audiencia](#clasificación-por-audiencia)
5. [Nueva Estructura Propuesta](#nueva-estructura-propuesta)
6. [Roadmap de Reorganización](#roadmap-de-reorganización)
7. [Recomendaciones](#recomendaciones)

---

## 📊 Resumen Ejecutivo

### Situación Actual

El proyecto **Dashboard Sonar** cuenta con documentación extensa (50+ archivos markdown, >15,000 LOC) generada durante un proceso de refactorización de 10 fases. La documentación actual está orientada principalmente al **desarrollo técnico** y al **proceso de refactorización**, pero presenta las siguientes **limitaciones críticas**:

#### Problemas Identificados

1. **Falta de documentación para usuarios finales** (administradores, clientes)
2. **Documentación de despliegue incompleta** (sin guías específicas de cloud, CI/CD production-ready)
3. **Documentación dispersa** (50+ archivos sin índice claro por audiencia)
4. **Enfoque en el proceso de refactorización** (útil para el equipo de desarrollo, pero no para mantenimiento)
5. **Sin manual de operaciones** para administradores de sistemas
6. **Ausencia de runbooks** para incidentes comunes
7. **Falta de guías de migración** para actualizaciones futuras

#### Fortalezas Identificadas

1. ✅ **Excelente documentación técnica** para desarrolladores (ARCHITECTURE.md, DEVELOPMENT_GUIDE.md)
2. ✅ **Documentación de API** bien estructurada
3. ✅ **Guías de configuración** detalladas (CONFIGURATION.md, DEPENDENCIES.md)
4. ✅ **Guía de troubleshooting** completa (TROUBLESHOOTING.md)
5. ✅ **Documentación de seguridad** (TESTING_SECURITY.md)
6. ✅ **Pipeline de datos** documentado (DATA_PIPELINE.md)

### Propuesta de Reorganización

Estructurar la documentación en **3 categorías principales** según audiencia:

```
docs/
├── 1-technical/          → Para desarrolladores (Backend, Frontend, Testing)
├── 2-operations/         → Para DevOps/SRE (Deployment, Monitoring, Runbooks)
└── 3-user/               → Para clientes/administradores (User Guide, Admin Guide)
```

**Objetivo**: Garantizar que cualquier persona (cliente, nuevo desarrollador, DevOps) pueda **mantener, escalar y operar** la aplicación **sin depender del equipo original**.

---

## 📦 Inventario Completo de Documentación

### Documentación Raíz (6 archivos)

| Archivo | Tamaño | Propósito | Audiencia | Estado |
|---------|--------|-----------|-----------|--------|
| `README.md` | 552 LOC | Índice principal del proyecto | Todos | ✅ Completo |
| `SETUP.md` | 1,133 LOC | Guía de instalación y configuración | Desarrolladores/DevOps | ✅ Completo |
| `CONTRIBUTING.md` | ~200 LOC | Guía de contribución | Desarrolladores | ✅ Completo |
| `CHANGELOG.md` | ~500 LOC | Registro de cambios | Todos | ✅ Completo |
| `PROYECTO_COMPLETADO.md` | ~100 LOC | Resumen del proyecto completado | Gestión | ✅ Completo |

**Total**: 2,485 LOC aprox.

---

### Documentación Principal (`docs/`)

#### Documentos Técnicos Core (10 archivos)

| Archivo | LOC | Propósito | Audiencia | Gap Analysis |
|---------|-----|-----------|-----------|--------------|
| `ARCHITECTURE.md` | ~800 | Arquitectura del sistema | Desarrolladores/Arquitectos | ✅ Excelente |
| `DEVELOPMENT_GUIDE.md` | ~600 | Guía de desarrollo | Desarrolladores | ✅ Excelente |
| `CONFIGURATION.md` | ~400 | Sistema de configuración | Desarrolladores/DevOps | ✅ Completo |
| `DEPENDENCIES.md` | ~350 | Gestión de dependencias | Desarrolladores | ✅ Completo |
| `TROUBLESHOOTING.md` | ~637 | Solución de problemas | Todos | ✅ Completo |
| `TESTING_SECURITY.md` | ~400 | Testing de seguridad | Desarrolladores | ✅ Completo |
| `DATA_PIPELINE.md` | ~450 | Pipeline de datos | Desarrolladores/Data Engineers | ✅ Completo |
| `CICD_USER_MANUAL.md` | ~300 | Manual de CI/CD | DevOps | ⚠️ Necesita ampliación |
| `MEJORAS_CONFIGURACION.md` | ~200 | Mejoras de configuración | Desarrolladores | ✅ Completo |

**Subtotal**: ~4,137 LOC

#### API Documentation (`docs/api/`)

| Archivo | LOC | Propósito | Gap |
|---------|-----|-----------|-----|
| `API_DOCUMENTATION.md` | ~500 | Documentación de API | ✅ Completo |
| `README.md` | ~50 | Índice de API | ✅ Completo |

**Subtotal**: ~550 LOC

#### Deployment (`docs/deployment/`)

| Archivo | LOC | Propósito | Gap |
|---------|-----|-----------|-----|
| `DEPLOYMENT.md` | ~600 | Guía de despliegue | ⚠️ Falta cloud específico |
| `README.md` | ~50 | Índice de deployment | ✅ OK |

**Subtotal**: ~650 LOC

**GAPS IDENTIFICADOS**:
- ❌ Falta: Guía de despliegue en AWS/GCP/Azure
- ❌ Falta: Guía de configuración de load balancers
- ❌ Falta: Guía de auto-scaling
- ❌ Falta: Guía de blue-green deployment

#### Migration (`docs/migration/`)

| Archivo | LOC | Propósito | Gap |
|---------|-----|-----------|-----|
| `MIGRATION_GUIDE.md` | ~400 | Migración de código legacy | ✅ Completo (histórico) |
| `README.md` | ~50 | Índice de migración | ✅ OK |

**Subtotal**: ~450 LOC

**GAPS IDENTIFICADOS**:
- ⚠️ Solo documenta migración del código legacy (histórico)
- ❌ Falta: Guía de migración de versiones futuras (v1.x → v2.x)
- ❌ Falta: Guía de migración de base de datos en producción

#### Testing (`docs/testing/`)

| Archivo | LOC | Propósito | Gap |
|---------|-----|-----------|-----|
| `MANUAL_TESTING.md` | ~200 | Testing manual | ✅ Completo |

**Subtotal**: ~200 LOC

#### Guides (`docs/guides/`)

| Archivo | LOC | Propósito | Gap |
|---------|-----|-----------|-----|
| `INICIO_RAPIDO.md` | ~300 | Quick start | ✅ Excelente |
| `CONFIGURATION_GUIDE.md` | ~400 | Guía de configuración | ✅ Excelente |
| `EXCEPTION_HANDLING_GUIDE.md` | ~300 | Manejo de excepciones | ✅ Completo |
| `RESUMEN.md` | ~250 | Navegación de docs | ✅ Útil |
| `DOCUMENTAR_CAMBIOS.md` | ~150 | Cómo documentar cambios | ✅ Completo |
| `ETL_IMPORT_FIX.md` | ~200 | Fix de importación ETL | ✅ Completo |

**Subtotal**: ~1,600 LOC

#### Plans & Reports (Históricos)

**docs/plan/** (10 archivos):
- PLAN_REORGANIZACION.md (~1,200 LOC)
- FASE_5_PLAN_DETALLADO.md - FASE_10_PLAN_DETALLADO.md (~3,000 LOC)
- PLAN_CICD_AUTOMATION.md (~400 LOC)
- PLAN_DATA_LOADING.md (~300 LOC)

**Subtotal**: ~4,900 LOC

**docs/reports/** (11 archivos):
- phase-0-preparation.md → phase-10-documentation.md (~5,000 LOC)
- README.md (~100 LOC)

**Subtotal**: ~5,100 LOC

**OBSERVACIÓN**: Estos documentos son **históricos** (proceso de refactorización). Útiles para entender el proyecto, pero no son documentación operativa.

#### Analysis (`docs/analysis/`)

| Archivo | LOC | Propósito | Gap |
|---------|-----|-----------|-----|
| `dependencies-analysis.md` | ~200 | Análisis de dependencias | ✅ Histórico |
| `project_field_size_impact.md` | ~150 | Análisis de impacto | ✅ Histórico |

**Subtotal**: ~350 LOC

#### Git Strategy (`docs/git/`)

| Archivo | LOC | Propósito | Gap |
|---------|-----|-----------|-----|
| `GIT_STRATEGY.md` | ~800 | Estrategia Git completa | ✅ Excelente |

**Subtotal**: ~800 LOC

---

### Resumen de Inventario

| Categoría | Archivos | LOC Aprox. | Estado |
|-----------|----------|-----------|--------|
| **Raíz** | 6 | 2,485 | ✅ Completo |
| **Docs Core** | 10 | 4,137 | ✅ Muy bueno |
| **API** | 2 | 550 | ✅ Completo |
| **Deployment** | 2 | 650 | ⚠️ Mejorable |
| **Migration** | 2 | 450 | ⚠️ Solo histórico |
| **Testing** | 1 | 200 | ✅ OK |
| **Guides** | 6 | 1,600 | ✅ Excelente |
| **Plans (históricos)** | 10 | 4,900 | ℹ️ Históricos |
| **Reports (históricos)** | 11 | 5,100 | ℹ️ Históricos |
| **Analysis** | 2 | 350 | ℹ️ Históricos |
| **Git Strategy** | 1 | 800 | ✅ Excelente |
| **Templates** | 3 | 300 | ✅ OK |
| **.github** | 5 | 400 | ✅ OK |

**TOTAL GENERAL**: ~50 archivos, ~22,000 LOC de documentación

---

## 🔍 Análisis de Brechas (Gap Analysis)

### ❌ CRÍTICO: Documentación Faltante

#### 1. Documentación de Usuario Final

| Documento Faltante | Audiencia | Importancia | Impacto |
|-------------------|-----------|-------------|---------|
| **USER_GUIDE.md** | Usuarios finales | 🔴 CRÍTICA | Sin esto, el cliente no puede usar la app |
| **ADMIN_GUIDE.md** | Administradores | 🔴 CRÍTICA | No pueden gestionar usuarios/datos |
| **FAQ.md** | Todos | 🟡 Media | Reduce soporte repetitivo |

**Contenido necesario para USER_GUIDE.md**:
- ✅ Cómo acceder a la aplicación
- ✅ Login y gestión de sesiones
- ✅ Navegación del dashboard
- ✅ Interpretación de métricas (Reliability, Security, Maintainability)
- ✅ Filtros y búsquedas
- ✅ Exportación de datos/reportes
- ✅ Casos de uso comunes

**Contenido necesario para ADMIN_GUIDE.md**:
- ✅ Gestión de usuarios (crear, editar, eliminar)
- ✅ Configuración de la aplicación (variables de entorno)
- ✅ Carga de datos (ejecución de pipelines)
- ✅ Monitoreo de logs
- ✅ Backups y restauración
- ✅ Gestión de proveedores y aplicaciones
- ✅ Troubleshooting básico

#### 2. Documentación de Operaciones (DevOps/SRE)

| Documento Faltante | Audiencia | Importancia | Impacto |
|-------------------|-----------|-------------|---------|
| **RUNBOOK.md** | DevOps/SRE | 🔴 CRÍTICA | No saben cómo responder a incidentes |
| **MONITORING_GUIDE.md** | DevOps/SRE | 🔴 CRÍTICA | No pueden detectar problemas |
| **BACKUP_RESTORE.md** | DevOps/Admins | 🔴 CRÍTICA | Riesgo de pérdida de datos |
| **SCALING_GUIDE.md** | DevOps | 🟡 Alta | No pueden escalar la app |
| **CLOUD_DEPLOYMENT_AWS.md** | DevOps | 🟡 Alta | No pueden desplegar en cloud |
| **CLOUD_DEPLOYMENT_GCP.md** | DevOps | 🟡 Media | Alternativa cloud |
| **CLOUD_DEPLOYMENT_AZURE.md** | DevOps | 🟡 Media | Alternativa cloud |
| **DISASTER_RECOVERY.md** | DevOps/SRE | 🟡 Alta | No hay plan de recuperación |

**Contenido necesario para RUNBOOK.md**:
- ✅ Incidentes comunes y cómo resolverlos
- ✅ Procedimientos de emergency shutdown
- ✅ Cómo hacer rollback de una versión
- ✅ Cómo reiniciar servicios
- ✅ Logs a consultar para cada tipo de error
- ✅ Contactos de escalamiento
- ✅ Checklist de health checks

**Contenido necesario para MONITORING_GUIDE.md**:
- ✅ Métricas clave a monitorear (CPU, memoria, DB connections)
- ✅ Configuración de alertas (Prometheus, CloudWatch, etc.)
- ✅ Dashboards recomendados (Grafana, DataDog)
- ✅ Logs estructurados y cómo consultarlos
- ✅ Thresholds de alarma
- ✅ Integración con PagerDuty/Opsgenie

**Contenido necesario para BACKUP_RESTORE.md**:
- ✅ Estrategia de backup (frecuencia, retención)
- ✅ Cómo hacer backup manual de la base de datos
- ✅ Cómo automatizar backups (cron, cloud snapshots)
- ✅ Procedimiento de restauración paso a paso
- ✅ Testing de restauración
- ✅ Backup de archivos estáticos y logs

#### 3. Documentación Técnica Avanzada

| Documento Faltante | Audiencia | Importancia | Impacto |
|-------------------|-----------|-------------|---------|
| **PERFORMANCE_TUNING.md** | Desarrolladores/DevOps | 🟡 Alta | No pueden optimizar |
| **DATABASE_SCHEMA.md** | Desarrolladores/DBAs | 🟡 Alta | Dificulta cambios de BD |
| **SECURITY_HARDENING.md** | DevOps/Security | 🟡 Alta | Vulnerabilidades potenciales |
| **UPGRADE_GUIDE.md** | Todos | 🟡 Alta | Miedo a actualizar |

**Contenido necesario para PERFORMANCE_TUNING.md**:
- ✅ Optimización de queries SQL
- ✅ Índices de base de datos recomendados
- ✅ Configuración de caché (Redis, Memcached)
- ✅ Tuning de Gunicorn/uWSGI (workers, threads)
- ✅ Profiling de código Python
- ✅ CDN para assets estáticos

**Contenido necesario para DATABASE_SCHEMA.md**:
- ✅ Diagrama ER completo
- ✅ Descripción de cada tabla y sus campos
- ✅ Relaciones entre tablas
- ✅ Índices existentes
- ✅ Constraints y validaciones
- ✅ Queries complejas explicadas

**Contenido necesario para SECURITY_HARDENING.md**:
- ✅ Checklist de seguridad
- ✅ Configuración de HTTPS/TLS
- ✅ Hardening de PostgreSQL
- ✅ Rate limiting y anti-DDoS
- ✅ Gestión de secretos (Vault, AWS Secrets Manager)
- ✅ Auditoría de seguridad
- ✅ OWASP Top 10 compliance

**Contenido necesario para UPGRADE_GUIDE.md**:
- ✅ Cómo actualizar de v1.x a v2.x
- ✅ Migraciones de base de datos
- ✅ Breaking changes por versión
- ✅ Testing de upgrade en staging
- ✅ Rollback plan

---

### ⚠️ ALTA PRIORIDAD: Documentación Incompleta

#### Documentación Actual que Necesita Ampliación

| Documento Existente | Gap Identificado | Prioridad |
|--------------------|------------------|-----------|
| `DEPLOYMENT.md` | Falta deployment en cloud (AWS/GCP/Azure) | 🔴 Alta |
| `DEPLOYMENT.md` | Falta configuración de load balancers | 🔴 Alta |
| `DEPLOYMENT.md` | Falta estrategia de blue-green deployment | 🟡 Media |
| `CICD_USER_MANUAL.md` | Falta guía de producción (solo habla de staging) | 🔴 Alta |
| `MIGRATION_GUIDE.md` | Solo documenta migración histórica, falta guía de upgrades futuros | 🟡 Media |
| `TROUBLESHOOTING.md` | Podría incluir más casos de producción | 🟡 Baja |

---

### 🟢 BAJA PRIORIDAD: Mejoras Opcionales

| Documento Propuesto | Audiencia | Importancia | Justificación |
|--------------------|-----------|-------------|---------------|
| **GLOSSARY.md** | Todos | 🟢 Baja | Útil para nuevos miembros |
| **ARCHITECTURE_DECISIONS.md** (ADRs) | Arquitectos | 🟢 Baja | Buena práctica, no crítico |
| **CONTRIBUTING_ADVANCED.md** | Desarrolladores | 🟢 Baja | Ya existe CONTRIBUTING.md básico |
| **CODE_OF_CONDUCT.md** | Todos | 🟢 Muy baja | Open source nice-to-have |

---

## 👥 Clasificación por Audiencia

### Audiencia 1: Desarrolladores (Backend/Frontend)

**Necesitan**:
- ✅ Entender la arquitectura del sistema
- ✅ Saber cómo crear nuevos endpoints/servicios/repositorios
- ✅ Conocer las convenciones de código
- ✅ Ejecutar tests
- ✅ Configurar entorno de desarrollo

**Documentación Actual (Excelente)**:
- ✅ ARCHITECTURE.md
- ✅ DEVELOPMENT_GUIDE.md
- ✅ CONFIGURATION.md
- ✅ TESTING_SECURITY.md
- ✅ API_DOCUMENTATION.md
- ✅ DEPENDENCIES.md

**Gaps**:
- ⚠️ DATABASE_SCHEMA.md (sería útil)
- ⚠️ PERFORMANCE_TUNING.md (sería útil)

---

### Audiencia 2: DevOps/SRE (Operaciones)

**Necesitan**:
- ❌ Desplegar la aplicación en producción (cloud, on-premise)
- ❌ Monitorear métricas y logs
- ❌ Responder a incidentes (runbooks)
- ❌ Hacer backups y restauraciones
- ❌ Escalar la aplicación
- ❌ Asegurar alta disponibilidad

**Documentación Actual (Incompleta)**:
- ⚠️ DEPLOYMENT.md (básico, falta cloud)
- ⚠️ CICD_USER_MANUAL.md (falta producción)
- ✅ TROUBLESHOOTING.md (bueno, pero enfocado a desarrollo)

**Gaps Críticos**:
- ❌ RUNBOOK.md (CRÍTICO)
- ❌ MONITORING_GUIDE.md (CRÍTICO)
- ❌ BACKUP_RESTORE.md (CRÍTICO)
- ❌ CLOUD_DEPLOYMENT_*.md (Alta prioridad)
- ❌ SCALING_GUIDE.md (Alta prioridad)
- ❌ DISASTER_RECOVERY.md (Alta prioridad)
- ❌ SECURITY_HARDENING.md (Alta prioridad)

---

### Audiencia 3: Usuarios Finales / Clientes

**Necesitan**:
- ❌ Entender cómo usar la aplicación (UI/UX)
- ❌ Interpretar las métricas del dashboard
- ❌ Exportar datos y generar reportes
- ❌ Resolver problemas comunes (FAQ)

**Documentación Actual**:
- ❌ **NINGUNA** documentación de usuario final

**Gaps Críticos**:
- ❌ USER_GUIDE.md (CRÍTICO)
- ❌ FAQ.md (Alta prioridad)

---

### Audiencia 4: Administradores de la Aplicación

**Necesitan**:
- ❌ Gestionar usuarios (crear, editar, eliminar)
- ❌ Configurar la aplicación
- ❌ Cargar datos (ejecutar pipelines)
- ❌ Ver logs y diagnosticar problemas
- ❌ Hacer backups básicos

**Documentación Actual**:
- ✅ DATA_PIPELINE.md (cómo ejecutar pipelines)
- ⚠️ SETUP.md (cubre instalación, pero no administración)

**Gaps Críticos**:
- ❌ ADMIN_GUIDE.md (CRÍTICO)

---

## 🗂️ Nueva Estructura Propuesta

### Estructura de 3 Niveles por Audiencia

```
docs/
│
├── README.md                          # Índice principal (mejorado)
│
├── 1-technical/                       # PARA DESARROLLADORES
│   ├── README.md                      # Índice técnico
│   │
│   ├── getting-started/               # Inicio rápido
│   │   ├── QUICK_START.md             # 5 minutos para empezar
│   │   ├── SETUP_DEVELOPMENT.md       # Setup completo desarrollo
│   │   └── SETUP_TESTING.md           # Setup para tests
│   │
│   ├── architecture/                  # Arquitectura
│   │   ├── ARCHITECTURE.md            # ✅ (ya existe, mover)
│   │   ├── DATABASE_SCHEMA.md         # ❌ NUEVO
│   │   ├── API_DOCUMENTATION.md       # ✅ (mover de docs/api/)
│   │   └── DESIGN_PATTERNS.md         # ✅ (extraer de ARCHITECTURE)
│   │
│   ├── development/                   # Guías de desarrollo
│   │   ├── DEVELOPMENT_GUIDE.md       # ✅ (ya existe, mover)
│   │   ├── CODING_STANDARDS.md        # ✅ (extraer de DEVELOPMENT_GUIDE)
│   │   ├── GIT_WORKFLOW.md            # ✅ (ya existe en docs/git/, mover)
│   │   ├── CREATING_REPOSITORIES.md   # ✅ (extraer de DEVELOPMENT_GUIDE)
│   │   ├── CREATING_SERVICES.md       # ✅ (extraer de DEVELOPMENT_GUIDE)
│   │   └── CREATING_VIEWS.md          # ✅ (extraer de DEVELOPMENT_GUIDE)
│   │
│   ├── testing/                       # Testing
│   │   ├── TESTING_GUIDE.md           # ✅ (consolidar)
│   │   ├── TESTING_SECURITY.md        # ✅ (ya existe, mover)
│   │   ├── MANUAL_TESTING.md          # ✅ (ya existe, mover)
│   │   └── E2E_TESTING.md             # ⚠️ (opcional)
│   │
│   ├── configuration/                 # Configuración
│   │   ├── CONFIGURATION.md           # ✅ (ya existe, mover)
│   │   ├── DEPENDENCIES.md            # ✅ (ya existe, mover)
│   │   └── ENVIRONMENT_VARIABLES.md   # ✅ (extraer de CONFIGURATION)
│   │
│   ├── data/                          # Data Engineering
│   │   ├── DATA_PIPELINE.md           # ✅ (ya existe, mover)
│   │   ├── ETL_PROCESSES.md           # ✅ (extraer de DATA_PIPELINE)
│   │   └── DATA_MODELS.md             # ❌ NUEVO (modelos de negocio)
│   │
│   ├── advanced/                      # Temas avanzados
│   │   ├── PERFORMANCE_TUNING.md      # ❌ NUEVO
│   │   └── MIGRATION_GUIDE.md         # ✅ (ya existe, mover)
│   │
│   └── reference/                     # Referencia rápida
│       ├── TROUBLESHOOTING_DEV.md     # ✅ (filtrar TROUBLESHOOTING.md)
│       ├── CHANGELOG.md               # ✅ (ya existe en raíz, link)
│       └── CONTRIBUTING.md            # ✅ (ya existe en raíz, link)
│
├── 2-operations/                      # PARA DEVOPS/SRE
│   ├── README.md                      # Índice operaciones
│   │
│   ├── deployment/                    # Despliegue
│   │   ├── DEPLOYMENT_OVERVIEW.md     # ✅ Visión general
│   │   ├── DEPLOYMENT_DOCKER.md       # ✅ (extraer de DEPLOYMENT.md)
│   │   ├── DEPLOYMENT_KUBERNETES.md   # ⚠️ (opcional futuro)
│   │   ├── DEPLOYMENT_AWS.md          # ❌ NUEVO (EC2, RDS, ECS, Lambda)
│   │   ├── DEPLOYMENT_GCP.md          # ❌ NUEVO (Compute Engine, Cloud SQL, Cloud Run)
│   │   ├── DEPLOYMENT_AZURE.md        # ❌ NUEVO (App Service, Azure SQL)
│   │   └── DEPLOYMENT_ONPREMISE.md    # ✅ (basado en DEPLOYMENT.md actual)
│   │
│   ├── infrastructure/                # Infraestructura
│   │   ├── LOAD_BALANCING.md          # ❌ NUEVO
│   │   ├── SCALING_GUIDE.md           # ❌ NUEVO (horizontal/vertical)
│   │   ├── HIGH_AVAILABILITY.md       # ❌ NUEVO
│   │   └── CDN_CONFIGURATION.md       # ⚠️ (opcional)
│   │
│   ├── cicd/                          # CI/CD
│   │   ├── CICD_OVERVIEW.md           # ✅ (basado en CICD_USER_MANUAL)
│   │   ├── GITHUB_ACTIONS.md          # ✅ (extraer de CICD_USER_MANUAL)
│   │   ├── DEPLOYMENT_PIPELINE.md     # ❌ NUEVO (staging → production)
│   │   └── ROLLBACK_PROCEDURES.md     # ❌ NUEVO
│   │
│   ├── monitoring/                    # Monitoreo
│   │   ├── MONITORING_GUIDE.md        # ❌ NUEVO (CRÍTICO)
│   │   ├── LOGGING.md                 # ❌ NUEVO (ELK, CloudWatch, Datadog)
│   │   ├── ALERTING.md                # ❌ NUEVO (PagerDuty, Opsgenie)
│   │   └── DASHBOARDS.md              # ❌ NUEVO (Grafana, CloudWatch)
│   │
│   ├── security/                      # Seguridad
│   │   ├── SECURITY_OVERVIEW.md       # ✅ (consolidar)
│   │   ├── SECURITY_HARDENING.md      # ❌ NUEVO (CRÍTICO)
│   │   ├── SECRETS_MANAGEMENT.md      # ❌ NUEVO (Vault, AWS Secrets)
│   │   └── SSL_TLS_CONFIGURATION.md   # ❌ NUEVO
│   │
│   ├── backup-recovery/               # Backup y DR
│   │   ├── BACKUP_RESTORE.md          # ❌ NUEVO (CRÍTICO)
│   │   ├── DISASTER_RECOVERY.md       # ❌ NUEVO
│   │   └── RTO_RPO.md                 # ❌ NUEVO (objetivos de recuperación)
│   │
│   ├── runbooks/                      # Runbooks
│   │   ├── RUNBOOK_OVERVIEW.md        # ❌ NUEVO (CRÍTICO)
│   │   ├── INCIDENT_RESPONSE.md       # ❌ NUEVO
│   │   ├── COMMON_ISSUES.md           # ✅ (basado en TROUBLESHOOTING)
│   │   └── HEALTH_CHECKS.md           # ❌ NUEVO
│   │
│   └── reference/                     # Referencia operativa
│       ├── TROUBLESHOOTING_OPS.md     # ✅ (filtrar TROUBLESHOOTING.md)
│       └── UPGRADE_GUIDE.md           # ❌ NUEVO
│
└── 3-user/                            # PARA CLIENTES/USUARIOS
    ├── README.md                      # Índice usuario
    │
    ├── getting-started/               # Primeros pasos
    │   ├── WHAT_IS_DASHBOARD_SONAR.md # ❌ NUEVO (intro no técnica)
    │   ├── FIRST_LOGIN.md             # ❌ NUEVO
    │   └── QUICK_TOUR.md              # ❌ NUEVO (tour visual)
    │
    ├── user-guide/                    # Guía de usuario
    │   ├── USER_GUIDE.md              # ❌ NUEVO (CRÍTICO)
    │   ├── DASHBOARD_OVERVIEW.md      # ❌ NUEVO
    │   ├── METRICS_EXPLAINED.md       # ❌ NUEVO (qué significan las métricas)
    │   ├── FILTERS_SEARCH.md          # ❌ NUEVO
    │   ├── EXPORT_REPORTS.md          # ❌ NUEVO
    │   └── USE_CASES.md               # ❌ NUEVO (casos prácticos)
    │
    ├── admin-guide/                   # Guía de administrador
    │   ├── ADMIN_GUIDE.md             # ❌ NUEVO (CRÍTICO)
    │   ├── USER_MANAGEMENT.md         # ❌ NUEVO
    │   ├── DATA_LOADING.md            # ✅ (basado en DATA_PIPELINE, simplificado)
    │   ├── CONFIGURATION.md           # ❌ NUEVO (config desde UI o .env)
    │   └── LOGS_DIAGNOSTICS.md        # ❌ NUEVO (para admins, no DevOps)
    │
    ├── faq/                           # Preguntas frecuentes
    │   ├── FAQ.md                     # ❌ NUEVO
    │   └── COMMON_PROBLEMS.md         # ✅ (filtrar TROUBLESHOOTING)
    │
    └── reference/                     # Referencia
        ├── GLOSSARY.md                # ❌ NUEVO (términos técnicos)
        └── SUPPORT.md                 # ❌ NUEVO (cómo obtener ayuda)
```

---

### Resumen de Cambios Propuestos

| Categoría | Archivos a Mover | Archivos Nuevos | Archivos a Dividir |
|-----------|------------------|-----------------|-------------------|
| **1-technical/** | 15 | 5 | 8 |
| **2-operations/** | 3 | 25 | 2 |
| **3-user/** | 1 | 15 | 1 |
| **TOTAL** | 19 | 45 | 11 |

**Esfuerzo estimado**:
- Mover/reorganizar: 2-3 días
- Crear documentación nueva: 10-15 días
- Revisar y consolidar: 2-3 días

**TOTAL**: 14-21 días de esfuerzo

---

## 🛤️ Roadmap de Reorganización

### Fase 1: Crítica - Documentación de Usuario (3-5 días)

**Objetivo**: Permitir que el cliente pueda usar y administrar la aplicación sin soporte técnico.

**Entregables**:
1. ✅ `docs/3-user/getting-started/WHAT_IS_DASHBOARD_SONAR.md`
   - Descripción no técnica de la aplicación
   - Casos de uso principales
   - Audiencia: Gestión, usuarios finales

2. ✅ `docs/3-user/user-guide/USER_GUIDE.md` (CRÍTICO)
   - Cómo hacer login
   - Navegación del dashboard
   - Interpretación de métricas
   - Filtros y búsquedas
   - Exportación de datos

3. ✅ `docs/3-user/admin-guide/ADMIN_GUIDE.md` (CRÍTICO)
   - Gestión de usuarios
   - Carga de datos (cómo ejecutar pipelines)
   - Configuración básica
   - Ver logs
   - Troubleshooting para admins

4. ✅ `docs/3-user/user-guide/METRICS_EXPLAINED.md`
   - Qué significa cada métrica (Reliability, Security, Maintainability, etc.)
   - Cómo interpretar los valores A-E
   - Quality Gates explicados

5. ✅ `docs/3-user/faq/FAQ.md`
   - Preguntas frecuentes de usuarios
   - Problemas comunes y soluciones

**Prioridad**: 🔴 CRÍTICA

---

### Fase 2: Crítica - Documentación de Operaciones (5-7 días)

**Objetivo**: Permitir que DevOps/SRE puedan operar la aplicación en producción sin soporte del equipo de desarrollo.

**Entregables**:
1. ✅ `docs/2-operations/runbooks/RUNBOOK_OVERVIEW.md` (CRÍTICO)
   - Incidentes comunes y resolución
   - Procedimientos de emergency
   - Rollback procedures
   - Health checks

2. ✅ `docs/2-operations/monitoring/MONITORING_GUIDE.md` (CRÍTICO)
   - Métricas a monitorear (CPU, RAM, DB connections, request latency)
   - Configuración de alertas
   - Dashboards recomendados
   - Logs estructurados

3. ✅ `docs/2-operations/backup-recovery/BACKUP_RESTORE.md` (CRÍTICO)
   - Estrategia de backup
   - Cómo hacer backup manual
   - Automatización de backups
   - Procedimiento de restauración
   - Testing de restauración

4. ✅ `docs/2-operations/deployment/DEPLOYMENT_AWS.md` (Alta prioridad)
   - Deployment en AWS EC2 + RDS
   - Deployment en AWS ECS (Docker)
   - Deployment en AWS Lambda (serverless)
   - Configuración de ALB, Auto Scaling Groups

5. ✅ `docs/2-operations/security/SECURITY_HARDENING.md` (Alta prioridad)
   - Checklist de seguridad
   - HTTPS/TLS configuration
   - PostgreSQL hardening
   - Rate limiting
   - Gestión de secretos (AWS Secrets Manager, Vault)

6. ✅ `docs/2-operations/infrastructure/SCALING_GUIDE.md`
   - Horizontal scaling (múltiples instancias)
   - Vertical scaling (más recursos)
   - Load balancing
   - Auto-scaling configuration

**Prioridad**: 🔴 CRÍTICA

---

### Fase 3: Alta Prioridad - Reorganización de Docs Existentes (2-3 días)

**Objetivo**: Reorganizar documentación existente en la nueva estructura de 3 niveles.

**Tareas**:
1. ✅ Crear estructura de carpetas `docs/1-technical/`, `docs/2-operations/`, `docs/3-user/`
2. ✅ Mover documentos existentes a sus categorías
3. ✅ Actualizar índices (README.md en cada carpeta)
4. ✅ Actualizar links internos entre documentos
5. ✅ Archivar documentación histórica (plans, reports) en `docs/archive/`

**Mapa de Movimientos**:

| Documento Actual | Nueva Ubicación |
|-----------------|------------------|
| `docs/ARCHITECTURE.md` | `docs/1-technical/architecture/ARCHITECTURE.md` |
| `docs/DEVELOPMENT_GUIDE.md` | `docs/1-technical/development/DEVELOPMENT_GUIDE.md` |
| `docs/api/API_DOCUMENTATION.md` | `docs/1-technical/architecture/API_DOCUMENTATION.md` |
| `docs/CONFIGURATION.md` | `docs/1-technical/configuration/CONFIGURATION.md` |
| `docs/DEPENDENCIES.md` | `docs/1-technical/configuration/DEPENDENCIES.md` |
| `docs/TESTING_SECURITY.md` | `docs/1-technical/testing/TESTING_SECURITY.md` |
| `docs/DATA_PIPELINE.md` | `docs/1-technical/data/DATA_PIPELINE.md` |
| `docs/deployment/DEPLOYMENT.md` | `docs/2-operations/deployment/DEPLOYMENT_OVERVIEW.md` |
| `docs/CICD_USER_MANUAL.md` | `docs/2-operations/cicd/CICD_OVERVIEW.md` |
| `docs/TROUBLESHOOTING.md` | Dividir en `1-technical/reference/TROUBLESHOOTING_DEV.md` y `2-operations/reference/TROUBLESHOOTING_OPS.md` |
| `docs/git/GIT_STRATEGY.md` | `docs/1-technical/development/GIT_WORKFLOW.md` |
| `docs/migration/MIGRATION_GUIDE.md` | `docs/1-technical/advanced/MIGRATION_GUIDE.md` |
| `docs/plan/*` | `docs/archive/refactoring/plan/*` |
| `docs/reports/*` | `docs/archive/refactoring/reports/*` |

**Prioridad**: 🟡 ALTA

---

### Fase 4: Media Prioridad - Documentación Técnica Avanzada (3-4 días)

**Objetivo**: Facilitar desarrollo y mantenimiento técnico avanzado.

**Entregables**:
1. ✅ `docs/1-technical/architecture/DATABASE_SCHEMA.md`
   - Diagrama ER completo
   - Descripción de tablas y campos
   - Relaciones y constraints
   - Índices

2. ✅ `docs/1-technical/advanced/PERFORMANCE_TUNING.md`
   - Optimización de queries SQL
   - Índices recomendados
   - Configuración de caché
   - Tuning de Gunicorn
   - Profiling

3. ✅ `docs/2-operations/deployment/DEPLOYMENT_GCP.md`
   - Deployment en Google Cloud
   - Compute Engine + Cloud SQL
   - Cloud Run (serverless)
   - Load Balancer configuration

4. ✅ `docs/2-operations/reference/UPGRADE_GUIDE.md`
   - Cómo actualizar versiones
   - Migraciones de BD
   - Breaking changes
   - Testing de upgrades
   - Rollback plan

**Prioridad**: 🟡 MEDIA

---

### Fase 5: Baja Prioridad - Mejoras Opcionales (2-3 días)

**Objetivo**: Pulir la documentación y añadir extras útiles.

**Entregables**:
1. ✅ `docs/3-user/reference/GLOSSARY.md`
   - Términos técnicos explicados
   - Acrónimos (SQALE, DLOC, etc.)

2. ✅ `docs/2-operations/deployment/DEPLOYMENT_AZURE.md`
   - Deployment en Azure
   - App Service + Azure SQL
   - Container Instances

3. ✅ `docs/2-operations/deployment/DEPLOYMENT_KUBERNETES.md`
   - Deployment en Kubernetes
   - Helm charts
   - Scaling y HA

4. ✅ Actualizar README.md principal con nueva estructura

**Prioridad**: 🟢 BAJA

---

### Cronograma Propuesto

| Fase | Duración | Esfuerzo (días) | Inicio | Fin |
|------|----------|----------------|--------|-----|
| **Fase 1: Docs de Usuario** | 1 semana | 3-5 | Semana 1 | Semana 1 |
| **Fase 2: Docs de Operaciones** | 1.5 semanas | 5-7 | Semana 1 | Semana 2 |
| **Fase 3: Reorganización** | 3 días | 2-3 | Semana 2 | Semana 2 |
| **Fase 4: Docs Técnicas Avanzadas** | 1 semana | 3-4 | Semana 3 | Semana 3 |
| **Fase 5: Mejoras Opcionales** | 3 días | 2-3 | Semana 4 | Semana 4 |

**Duración Total**: 3-4 semanas (15-22 días de esfuerzo)

**Nota**: Las Fases 1, 2 y 3 se pueden ejecutar en paralelo si hay múltiples personas trabajando.

---

## 💡 Recomendaciones

### 1. Priorización de Esfuerzo

**Enfoque Sugerido**:
1. **Semana 1**: Documentación de usuario (Fase 1) - **CRÍTICO** para independencia del cliente
2. **Semana 1-2**: Documentación de operaciones (Fase 2) - **CRÍTICO** para operación en producción
3. **Semana 2**: Reorganización (Fase 3) - **ALTA** para facilitar navegación
4. **Semana 3**: Docs técnicas avanzadas (Fase 4) - **MEDIA** para escalabilidad
5. **Semana 4**: Mejoras opcionales (Fase 5) - **BAJA** nice-to-have

### 2. Herramientas Recomendadas

**Para Diagramas**:
- **Mermaid** (markdown nativo en GitHub)
- **Draw.io** / **Lucidchart** para diagramas de arquitectura
- **dbdiagram.io** para esquemas de BD

**Para Screenshots** (User Guide):
- **Snagit** / **Greenshot** / **LightShot**
- Anotar capturas con flechas y texto explicativo

**Para Validación**:
- **markdownlint** (linting de markdown)
- **vale** (prose linting, consistencia de estilo)

### 3. Estándares de Documentación

**Estructura de cada documento**:
```markdown
# Título del Documento

**Versión**: X.Y.Z
**Fecha**: YYYY-MM-DD
**Audiencia**: Desarrolladores / DevOps / Usuarios

---

## Tabla de Contenidos
1. [Sección 1](#sección-1)
2. [Sección 2](#sección-2)

---

## Sección 1
Contenido...

## Sección 2
Contenido...
```

**Convenciones**:
- ✅ Usar bullet points y listas numeradas
- ✅ Incluir ejemplos de código con syntax highlighting
- ✅ Añadir screenshots cuando sea relevante (especialmente en User Guide)
- ✅ Usar tablas para comparaciones
- ✅ Incluir alerts: ⚠️ Warning, ❌ Error, ✅ Success, ℹ️ Info
- ✅ Links relativos entre documentos (no absolutos)

### 4. Mantenimiento de Documentación

**Proceso Propuesto**:
1. ✅ Incluir actualización de docs en **Definition of Done** de cada feature
2. ✅ Code review debe incluir revisión de cambios en docs
3. ✅ Cada release debe actualizar `CHANGELOG.md` y `UPGRADE_GUIDE.md`
4. ✅ Revisar docs cada trimestre para detectar obsolescencia

**Responsabilidades**:
- **Desarrolladores**: Docs técnicas (1-technical)
- **DevOps**: Docs de operaciones (2-operations)
- **Product Owner / UX**: Docs de usuario (3-user)

### 5. Métricas de Éxito

**KPIs para medir el impacto**:
- ✅ Reducción de tickets de soporte relacionados con "cómo hacer X"
- ✅ Tiempo de onboarding de nuevos desarrolladores (objetivo: <2 días)
- ✅ Tiempo de deployment de un nuevo DevOps (objetivo: <1 día con las guías)
- ✅ Feedback positivo del cliente sobre la documentación de usuario

### 6. Documentación como Código

**Propuesta**:
- ✅ Almacenar docs en el mismo repo (ya lo hacen)
- ✅ Usar **MkDocs** o **Docusaurus** para generar site estático navegable
  - Ventajas: búsqueda, navegación por categorías, versioning
  - Deploy en GitHub Pages / Netlify
- ✅ Configurar CI/CD para validar links rotos en PRs
- ✅ Automatizar generación de tabla de contenidos

**Ejemplo con MkDocs**:
```yaml
# mkdocs.yml
site_name: Dashboard Sonar Documentation
theme:
  name: material
nav:
  - Home: index.md
  - For Developers:
      - Getting Started: 1-technical/getting-started/QUICK_START.md
      - Architecture: 1-technical/architecture/ARCHITECTURE.md
  - For DevOps:
      - Deployment: 2-operations/deployment/DEPLOYMENT_OVERVIEW.md
      - Monitoring: 2-operations/monitoring/MONITORING_GUIDE.md
  - For Users:
      - User Guide: 3-user/user-guide/USER_GUIDE.md
      - Admin Guide: 3-user/admin-guide/ADMIN_GUIDE.md
```

---

## 📎 Anexos

### Anexo A: Checklist de Documentación Mínima Viable (MVP)

Para garantizar independencia del cliente, la siguiente documentación es **MÍNIMA OBLIGATORIA**:

- [ ] `docs/3-user/user-guide/USER_GUIDE.md` (CRÍTICO)
- [ ] `docs/3-user/admin-guide/ADMIN_GUIDE.md` (CRÍTICO)
- [ ] `docs/2-operations/runbooks/RUNBOOK_OVERVIEW.md` (CRÍTICO)
- [ ] `docs/2-operations/monitoring/MONITORING_GUIDE.md` (CRÍTICO)
- [ ] `docs/2-operations/backup-recovery/BACKUP_RESTORE.md` (CRÍTICO)
- [ ] `docs/2-operations/deployment/DEPLOYMENT_AWS.md` (si usan AWS) O `DEPLOYMENT_GCP.md` O `DEPLOYMENT_ONPREMISE.md`
- [ ] `docs/2-operations/security/SECURITY_HARDENING.md` (CRÍTICO)
- [ ] `docs/1-technical/architecture/DATABASE_SCHEMA.md` (Alta prioridad)
- [ ] `docs/README.md` actualizado con nueva estructura

**Esfuerzo Mínimo**: 7-10 días

---

### Anexo B: Plantilla de USER_GUIDE.md

```markdown
# Guía de Usuario - Dashboard Sonar

**Versión**: 1.0.0
**Audiencia**: Usuarios finales (gestores de proyecto, developers, QA)

---

## 1. Introducción

### ¿Qué es Dashboard Sonar?
[Explicación no técnica de la aplicación]

### Casos de Uso Principales
- Monitorear calidad de código de repositorios
- Detectar tendencias de mejora/deterioro
- Generar reportes de métricas

---

## 2. Primeros Pasos

### 2.1 Acceso a la Aplicación
URL: https://dashboard.example.com
[Screenshot de login]

### 2.2 Login
Usuario: su_usuario
Contraseña: su_contraseña
[Screenshot]

### 2.3 Dashboard Principal
[Screenshot anotado del dashboard]
- (1) Menú principal
- (2) Filtros
- (3) Métricas principales
- (4) Gráficos

---

## 3. Entendiendo las Métricas

### 3.1 Reliability Rating (A-E)
- **A**: Excelente (0 bugs)
- **B**: Bueno (1-3 bugs menores)
- ...

### 3.2 Security Rating (A-E)
...

### 3.3 Maintainability (SQALE)
...

[Tabla con todas las métricas explicadas]

---

## 4. Funcionalidades

### 4.1 Filtrar por Aplicación
[Screenshot + pasos]

### 4.2 Buscar Repositorios
[Screenshot + pasos]

### 4.3 Ver Histórico
[Screenshot + pasos]

### 4.4 Exportar Datos
[Screenshot + pasos]

---

## 5. Preguntas Frecuentes

**¿Cómo interpretar Quality Gates?**
...

**¿Con qué frecuencia se actualizan los datos?**
...
```

---

### Anexo C: Plantilla de ADMIN_GUIDE.md

```markdown
# Guía de Administración - Dashboard Sonar

**Versión**: 1.0.0
**Audiencia**: Administradores de la aplicación

---

## 1. Gestión de Usuarios

### 1.1 Crear Usuario
[Pasos + screenshots o código]

### 1.2 Editar Usuario
[Pasos]

### 1.3 Eliminar Usuario
[Pasos]

### 1.4 Roles y Permisos
[Explicación de roles: admin, user, viewer]

---

## 2. Carga de Datos

### 2.1 Ejecutar Pipeline de Datos

**Windows**:
```bash
run_data_pipeline.bat Development
```

**Linux/macOS**:
```bash
./run_data_pipeline.sh Production
```

### 2.2 Verificar Carga Exitosa
[Cómo ver logs, qué buscar]

### 2.3 Solución de Problemas en Carga
[Errores comunes]

---

## 3. Configuración

### 3.1 Variables de Entorno (.env)
[Cuáles son críticas, cómo cambiarlas]

### 3.2 Configuración de Base de Datos
[Cómo cambiar de SQLite a PostgreSQL]

---

## 4. Monitoreo y Logs

### 4.1 Ver Logs de Aplicación
Ubicación: `/var/log/dashboardsonar/app.log`
[Cómo interpretar logs]

### 4.2 Ver Logs de Carga de Datos
[Ubicación, qué buscar]

---

## 5. Backup y Restauración

### 5.1 Backup Manual de Base de Datos
[Pasos específicos para PostgreSQL/SQLite]

### 5.2 Restaurar desde Backup
[Pasos]

---

## 6. Troubleshooting

### Error: "Database connection failed"
Solución: ...

### Error: "User not found"
Solución: ...
```

---

### Anexo D: Plantilla de RUNBOOK.md

```markdown
# Runbook - Dashboard Sonar

**Versión**: 1.0.0
**Audiencia**: DevOps, SRE, On-call engineers

---

## 1. Emergency Contacts

| Rol | Nombre | Email | Teléfono | Escalamiento |
|-----|--------|-------|----------|--------------|
| On-call primary | ... | ... | ... | Inmediato |
| On-call backup | ... | ... | ... | +15 min |
| Tech Lead | ... | ... | ... | +30 min |

---

## 2. Health Checks

### 2.1 Application Health
```bash
curl https://dashboard.example.com/health
# Expected: {"status": "ok"}
```

### 2.2 Database Health
```bash
psql -h localhost -U dbuser -d dashboardsonar -c "SELECT 1;"
```

### 2.3 Logs Health
```bash
tail -f /var/log/dashboardsonar/app.log
# Should NOT see ERROR lines
```

---

## 3. Common Incidents

### 3.1 Application Down (HTTP 502/503)

**Síntomas**:
- Dashboard no carga
- HTTP 502 Bad Gateway
- HTTP 503 Service Unavailable

**Causa Raíz Probable**:
1. Gunicorn workers crashed
2. Database connection pool exhausted
3. Out of memory

**Resolución**:

**Paso 1**: Verificar logs
```bash
tail -100 /var/log/dashboardsonar/app.log
```
Buscar: `CRITICAL`, `ERROR`, `Out of memory`

**Paso 2**: Reiniciar Gunicorn
```bash
sudo systemctl restart dashboardsonar
sudo systemctl status dashboardsonar
```

**Paso 3**: Verificar que vuelve
```bash
curl https://dashboard.example.com/health
```

**Si no resuelve**: Escalar a Tech Lead

---

### 3.2 Slow Response (>5s)

**Síntomas**:
- Dashboard carga lento
- Timeouts en requests

**Causa Raíz Probable**:
1. Database queries lentas
2. Alto volumen de tráfico
3. Falta de índices

**Resolución**:

**Paso 1**: Ver active queries en DB
```sql
SELECT pid, query, state, query_start
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;
```

**Paso 2**: Terminar queries lentas (>5 min)
```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE query_start < NOW() - INTERVAL '5 minutes';
```

**Paso 3**: Revisar logs de aplicación
```bash
grep "took [0-9]\{4,\}ms" /var/log/dashboardsonar/app.log
```

---

### 3.3 Database Connection Error

**Síntomas**:
- `OperationalError: could not connect to server`
- `FATAL: remaining connection slots are reserved`

**Causa Raíz Probable**:
1. PostgreSQL down
2. Connection pool exhausted
3. Firewall bloqueando

**Resolución**:

**Paso 1**: Verificar PostgreSQL está up
```bash
sudo systemctl status postgresql
```

**Paso 2**: Si está down, iniciar
```bash
sudo systemctl start postgresql
```

**Paso 3**: Verificar connections activas
```sql
SELECT count(*) FROM pg_stat_activity;
```

Si > 90 (de max 100), hay leak de connections:
```bash
sudo systemctl restart dashboardsonar
```

---

## 4. Rollback Procedures

### 4.1 Rollback Application Code

**Paso 1**: Identificar versión anterior estable
```bash
git tag -l
# Ejemplo: v1.9.0
```

**Paso 2**: Checkout y deploy
```bash
git checkout v1.9.0
sudo systemctl restart dashboardsonar
```

**Paso 3**: Verificar
```bash
curl https://dashboard.example.com/health
```

---

### 4.2 Rollback Database Migration

**Paso 1**: Ver migraciones aplicadas
```bash
flask db current
```

**Paso 2**: Revertir última migración
```bash
flask db downgrade -1
```

**Paso 3**: Reiniciar app
```bash
sudo systemctl restart dashboardsonar
```

---

## 5. Monitoring Checklist

Revisar estos paneles cada hora durante incident:

- [ ] Grafana Dashboard: CPU, RAM, Disk
- [ ] CloudWatch Logs: Errores en últimos 5 min
- [ ] Database Metrics: Connections, Query time
- [ ] Application Logs: HTTP 5xx rate

---

## 6. Post-Incident Report

Después de resolver incident, llenar:
- **Tiempo de inicio**: [timestamp]
- **Tiempo de resolución**: [timestamp]
- **Causa raíz**: [descripción]
- **Impacto**: [usuarios afectados, downtime]
- **Acciones tomadas**: [pasos]
- **Follow-up**: [preventive measures]

Enviar a: devops-team@example.com
```

---

## 🎯 Conclusión

La documentación actual del proyecto **Dashboard Sonar** es **excelente para desarrolladores** pero presenta **gaps críticos** en:

1. ❌ Documentación de usuario final (USER_GUIDE, ADMIN_GUIDE)
2. ❌ Documentación operativa (RUNBOOK, MONITORING, BACKUP)
3. ❌ Despliegue en cloud (AWS, GCP, Azure)

**Propuesta**: Reorganizar en **3 categorías por audiencia** (Technical, Operations, User) y crear **~45 nuevos documentos** en **3-4 semanas**.

**Prioridad Inmediata** (Semanas 1-2):
- USER_GUIDE.md
- ADMIN_GUIDE.md
- RUNBOOK.md
- MONITORING_GUIDE.md
- BACKUP_RESTORE.md

Con esto, el cliente podrá **operar y mantener** la aplicación **sin dependencia del equipo de desarrollo**.

---

**Documento preparado por**: Equipo de Arquitectura
**Fecha**: 2025-12-17
**Próxima revisión**: Después de implementar Fase 1
