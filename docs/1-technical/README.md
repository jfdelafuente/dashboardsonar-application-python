# Technical Documentation

**Audiencia**: Desarrolladores, Arquitectos de Software, Ingenieros Backend/Frontend

Esta sección contiene toda la documentación técnica necesaria para desarrollar, mantener y extender Dashboard Sonar.

---

## 📋 Índice por Tema

### 🚀 [Getting Started](getting-started/)
Documentación para empezar rápidamente con el proyecto.

- *(Nota: Añadir QUICK_START.md en el futuro)*

---

### 🏗️ [Architecture](architecture/)
Arquitectura del sistema, decisiones de diseño y documentación de APIs.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[ARCHITECTURE.md](architecture/ARCHITECTURE.md)** | Arquitectura general del sistema (capas, componentes, patrones) | 🔴 CRÍTICO |
| **[DATABASE_SCHEMA.md](architecture/DATABASE_SCHEMA.md)** | Esquema completo de BD con ER diagrams, índices, queries | 🟠 ALTA |
| **[api/API_DOCUMENTATION.md](architecture/api/API_DOCUMENTATION.md)** | Documentación completa de todas las APIs REST | 🟠 ALTA |
| **[api/README.md](architecture/api/README.md)** | Índice de documentación de APIs | 🟡 MEDIA |

---

### 💻 [Development](development/)
Guías de desarrollo, flujos de trabajo y mejores prácticas.

| Documento | Descripción |
|-----------|-------------|
| **[DEVELOPMENT_GUIDE.md](development/DEVELOPMENT_GUIDE.md)** | Guía completa de desarrollo (setup, workflow, testing) |
| **[GIT_STRATEGY.md](development/GIT_STRATEGY.md)** | Estrategia de Git (branching, commits, PRs) |

---

### ⚙️ [Configuration](configuration/)
Sistema de configuración y gestión de dependencias.

| Documento | Descripción |
|-----------|-------------|
| **[CONFIGURATION.md](configuration/CONFIGURATION.md)** | Sistema de configuración completo (.env, settings) |
| **[DEPENDENCIES.md](configuration/DEPENDENCIES.md)** | Gestión de dependencias Python y frontend |
| **[MEJORAS_CONFIGURACION.md](configuration/MEJORAS_CONFIGURACION.md)** | Mejoras implementadas en configuración |

---

### 📊 [Data](data/)
Pipeline de datos, ETL y procesamiento de métricas de SonarQube.

| Documento | Descripción |
|-----------|-------------|
| **[DATA_PIPELINE.md](data/DATA_PIPELINE.md)** | Pipeline de carga de datos desde SonarQube |

---

### 🧪 [Testing](testing/)
Estrategias de testing, seguridad y QA.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[TESTING_SECURITY.md](testing/TESTING_SECURITY.md)** | Testing de funciones de seguridad (password hashing) | 🟡 MEDIA |
| **[MANUAL_TESTING.md](testing/MANUAL_TESTING.md)** | Guía de testing manual y casos de prueba | 🟡 MEDIA |

---

### 🎓 [Advanced](advanced/)
Temas avanzados: migraciones, performance tuning, escalabilidad.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[PERFORMANCE_TUNING.md](advanced/PERFORMANCE_TUNING.md)** | Optimización de queries, N+1, pooling, caching, Gunicorn | 🟠 ALTA |
| **[migration/MIGRATION_GUIDE.md](advanced/migration/MIGRATION_GUIDE.md)** | Guía de migración entre versiones | 🟡 MEDIA |
| **[migration/README.md](advanced/migration/README.md)** | Índice de documentación de migraciones | 🟡 MEDIA |

**Documentación futura recomendada**:

- `SCALING_GUIDE.md` - Estrategias de escalabilidad horizontal/vertical
- `CACHING_STRATEGIES.md` - Redis, Memcached, CDN

---

### 📚 [Reference](reference/)
Material de referencia, guías rápidas y troubleshooting para desarrolladores.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[TROUBLESHOOTING.md](reference/TROUBLESHOOTING.md)** | Resolución de problemas técnicos comunes | 🟠 ALTA |
| **[guides/CONFIGURATION_GUIDE.md](reference/guides/CONFIGURATION_GUIDE.md)** | Guía de configuración | 🟡 MEDIA |
| **[guides/DOCUMENTAR_CAMBIOS.md](reference/guides/DOCUMENTAR_CAMBIOS.md)** | Cómo documentar cambios | 🟡 MEDIA |
| **[guides/ETL_IMPORT_FIX.md](reference/guides/ETL_IMPORT_FIX.md)** | Fix de importación ETL | 🟢 BAJA |
| **[guides/EXCEPTION_HANDLING_GUIDE.md](reference/guides/EXCEPTION_HANDLING_GUIDE.md)** | Guía de manejo de excepciones | 🟡 MEDIA |
| **[guides/INICIO_RAPIDO.md](reference/guides/INICIO_RAPIDO.md)** | Inicio rápido | 🟡 MEDIA |
| **[guides/RESUMEN.md](reference/guides/RESUMEN.md)** | Resumen general | 🟢 BAJA |

---

## 🎯 Rutas de Aprendizaje

### Para Nuevos Desarrolladores

**Día 1: Setup y Comprensión**
1. [DEVELOPMENT_GUIDE.md](development/DEVELOPMENT_GUIDE.md) - Setup del entorno
2. [ARCHITECTURE.md](architecture/ARCHITECTURE.md) - Entender la arquitectura
3. [reference/guides/INICIO_RAPIDO.md](reference/guides/INICIO_RAPIDO.md) - Primer contacto

**Semana 1: Profundización**
4. [CONFIGURATION.md](configuration/CONFIGURATION.md) - Sistema de configuración
5. [DATA_PIPELINE.md](data/DATA_PIPELINE.md) - Pipeline de datos
6. [api/API_DOCUMENTATION.md](architecture/api/API_DOCUMENTATION.md) - APIs disponibles

**Mes 1: Expertise**
7. [GIT_STRATEGY.md](development/GIT_STRATEGY.md) - Flujo de trabajo
8. [advanced/migration/](advanced/migration/) - Migraciones avanzadas
9. [reference/guides/](reference/guides/) - Guías de referencia

---

### Para Arquitectos

**Core Reading**:
1. [ARCHITECTURE.md](architecture/ARCHITECTURE.md) - Arquitectura completa
2. [CONFIGURATION.md](configuration/CONFIGURATION.md) - Configuración y settings
3. [DATA_PIPELINE.md](data/DATA_PIPELINE.md) - Pipeline de datos

**Advanced Topics**:
4. [advanced/migration/MIGRATION_GUIDE.md](advanced/migration/MIGRATION_GUIDE.md) - Estrategias de migración
5. Ver [../2-operations/](../2-operations/) para deployment y escalabilidad

---

## 🔗 Documentación Relacionada

### Otros Sectores

- **[2-operations/](../2-operations/)** - Para DevOps/SRE (deployment, monitoring, runbooks)
- **[3-user/](../3-user/)** - Para usuarios finales y administradores

### Documentación Archivada

- **[archive/](../archive/)** - Documentación histórica del proceso de refactorización

---

## 📖 Contribuir a la Documentación

¿Encontraste un error o quieres mejorar la documentación?

1. Lee [reference/guides/DOCUMENTAR_CAMBIOS.md](reference/guides/DOCUMENTAR_CAMBIOS.md)
2. Sigue [GIT_STRATEGY.md](development/GIT_STRATEGY.md) para el flujo de Git
3. Crea un PR con tus cambios

---

**Última actualización**: Diciembre 2025
**Mantenido por**: Equipo de Desarrollo
