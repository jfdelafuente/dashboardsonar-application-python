# Glosario de Términos - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Todos los usuarios
**Propósito**: Definiciones de términos técnicos, acrónimos y conceptos

---

## 📋 Tabla de Contenidos

1. [Métricas de SonarQube](#métricas-de-sonarqube)
2. [Conceptos de Calidad de Código](#conceptos-de-calidad-de-código)
3. [Arquitectura y Tecnologías](#arquitectura-y-tecnologías)
4. [DevOps y Operaciones](#devops-y-operaciones)
5. [Base de Datos](#base-de-datos)
6. [Seguridad](#seguridad)

---

## 🎯 Métricas de SonarQube

### A

**API (Application Programming Interface)**
Interfaz de programación que permite la comunicación entre diferentes componentes de software.

**Application**
Proyecto de software individual que se analiza en SonarQube. Dashboard Sonar puede rastrear múltiples aplicaciones.

---

### B

**Blocker Bug**
Error crítico que impide el funcionamiento básico de la aplicación. Debe resolverse inmediatamente antes de cualquier deployment.

**Bugs**
Errores en el código que probablemente causarán comportamiento incorrecto en tiempo de ejecución. SonarQube clasifica bugs en: Blocker, Critical, Major, Minor, Info.

---

### C

**Code Smell**
Problema de calidad en el código que no es un bug pero indica debilidad en el diseño que puede ralentizar el desarrollo. Ejemplos: código duplicado, funciones muy largas, complejidad excesiva.

**Complexity (Complejidad Ciclomática)**
Métrica que mide el número de rutas independientes a través del código. Alta complejidad indica código difícil de entender y mantener.

```
Complexity = (nodos de decisión) + 1

if → +1
else → +1
for/while → +1
case → +1 por cada opción
```

**Coverage (Cobertura de Tests)**
Porcentaje del código que está cubierto por tests automatizados. Se calcula como:

```
Coverage = (Líneas cubiertas / Total líneas) × 100%
```

**CRUD**
Create, Read, Update, Delete - Las cuatro operaciones básicas de persistencia de datos.

---

### D

**Dashboard**
Interfaz visual que muestra métricas clave de calidad de código de forma consolidada.

**DLOC (Duplicated Lines of Code)**
Líneas de código duplicadas. Indica código que se repite en múltiples lugares, lo que dificulta el mantenimiento.

```
Duplicación = (DLOC / Total LOC) × 100%
```

**Density (Densidad)**
Medida de concentración de issues por línea de código. Por ejemplo:

```
Bug Density = (Bugs / 1000 LOC)
```

**Deuda Técnica (Technical Debt)**
Tiempo estimado necesario para resolver todos los code smells y problemas de mantenibilidad.

```
Deuda Técnica = Σ(Tiempo estimado para resolver cada issue)
```

---

### E

**ETL (Extract, Transform, Load)**
Proceso de extraer datos de SonarQube, transformarlos y cargarlos en Dashboard Sonar.

**ER Diagram (Entity-Relationship Diagram)**
Diagrama que muestra la estructura de la base de datos y las relaciones entre tablas.

---

### H

**Hot Spot (Security Hot Spot)**
Código sensible a la seguridad que requiere revisión manual. No es necesariamente una vulnerabilidad, pero debe verificarse.

---

### I

**Issue**
Problema detectado por SonarQube. Puede ser un bug, vulnerabilidad, code smell o security hot spot.

---

### L

**LOC (Lines of Code)**
Total de líneas de código en el proyecto (excluyendo líneas en blanco y comentarios).

---

### M

**Maintainability Rating**
Calificación de A (mejor) a E (peor) basada en la deuda técnica en relación al tamaño del proyecto.

| Rating | Technical Debt Ratio |
|--------|---------------------|
| A | ≤ 5% |
| B | 6% - 10% |
| C | 11% - 20% |
| D | 21% - 50% |
| E | > 50% |

**Métrica**
Medida cuantitativa que evalúa un aspecto específico de la calidad del código.

---

### N

**NCLOC (Non-Commented Lines of Code)**
Líneas de código sin incluir comentarios ni líneas en blanco. Es la métrica estándar para medir el tamaño del proyecto.

---

### Q

**Quality Gate**
Conjunto de condiciones que el código debe cumplir para considerarse listo para producción.

**Ejemplo de Quality Gate**:
- Coverage ≥ 80%
- Duplicación ≤ 3%
- 0 Blocker/Critical bugs
- 0 Vulnerabilidades críticas
- Reliability Rating ≥ A
- Security Rating ≥ A
- Maintainability Rating ≥ A

---

### R

**Rating**
Calificación de A (mejor) a E (peor) en tres dimensiones: Reliability, Security, Maintainability.

**Reliability Rating**
Calificación basada en la cantidad y severidad de bugs:
- A: 0 bugs
- B: Al menos 1 bug minor
- C: Al menos 1 bug major
- D: Al menos 1 bug critical
- E: Al menos 1 bug blocker

**Repo (Repository)**
Repositorio de código fuente, típicamente en Git.

**RPO (Recovery Point Objective)**
Tiempo máximo de pérdida de datos aceptable. En Dashboard Sonar: < 24 horas.

**RTO (Recovery Time Objective)**
Tiempo máximo para restaurar el servicio. En Dashboard Sonar: < 2 horas.

---

### S

**Security Rating**
Calificación basada en la cantidad y severidad de vulnerabilidades de seguridad:
- A: 0 vulnerabilidades
- B: Al menos 1 vulnerabilidad minor
- C: Al menos 1 vulnerabilidad major
- D: Al menos 1 vulnerabilidad critical
- E: Al menos 1 vulnerabilidad blocker

**SLA (Service Level Agreement)**
Acuerdo que define los niveles de servicio esperados. Para Dashboard Sonar:
- Uptime: 99.5%
- RTO: < 2 horas
- RPO: < 24 horas

**SonarQube**
Plataforma de inspección continua de calidad de código. Dashboard Sonar consume datos de SonarQube.

**SQALE (Software Quality Assessment based on Lifecycle Expectations)**
Metodología para evaluar deuda técnica. SonarQube usa SQALE Rating (Maintainability Rating).

```
SQALE Rating = (Technical Debt / Development Cost) × 100%
```

**SQALE Index**
Sinónimo de Technical Debt. Tiempo estimado en minutos para resolver todos los code smells.

---

### T

**Technical Debt Ratio**
Porcentaje de esfuerzo necesario para resolver code smells en relación al costo de desarrollo:

```
TD Ratio = (Remediation Cost / Development Cost) × 100%
```

**Threshold (Umbral)**
Valor límite que define si una métrica es aceptable o no. Ejemplo: Coverage threshold = 80%.

**Trending**
Análisis de cómo evolucionan las métricas a lo largo del tiempo.

---

### V

**Vulnerability (Vulnerabilidad)**
Debilidad de seguridad en el código que puede ser explotada por atacantes. Clasificadas como: Blocker, Critical, Major, Minor, Info.

---

## 💻 Conceptos de Calidad de Código

### Code Duplication (Duplicación de Código)

Porcentaje de código que se repite en múltiples lugares:

```
Duplicación = (Líneas duplicadas / Total líneas) × 100%
```

**Umbrales**:
- ✅ Excelente: < 3%
- 🟡 Aceptable: 3% - 5%
- 🔴 Malo: > 5%

---

### Cyclomatic Complexity (Complejidad Ciclomática)

Métrica que cuenta el número de caminos independientes en el código.

**Cálculo**:
```
CC = (decisiones) + 1

if/else → +1
for/while → +1
case → +1 por opción
&& / || → +1
```

**Interpretación**:
- 1-10: Código simple, fácil de mantener
- 11-20: Código moderadamente complejo
- 21-50: Código complejo, difícil de testear
- 50+: **Muy complejo**, alto riesgo de bugs

---

### Cognitive Complexity (Complejidad Cognitiva)

Mide qué tan difícil es entender el código. Considera anidamiento y flujo de control.

**Diferencia con Cyclomatic Complexity**:
```python
# Misma Cyclomatic (4), diferente Cognitive

# Versión A - Cognitive = 1
if a and b and c and d:
    do_something()

# Versión B - Cognitive = 4
if a:
    if b:
        if c:
            if d:
                do_something()
```

---

## 🏗️ Arquitectura y Tecnologías

### Backend

**Flask**
Microframework web de Python para construir aplicaciones web.

**SQLAlchemy**
ORM (Object-Relational Mapping) que permite interactuar con bases de datos usando objetos Python.

**Gunicorn**
Servidor WSGI para Python usado en producción.

**WSGI (Web Server Gateway Interface)**
Especificación estándar para interfaces entre servidores web y aplicaciones Python.

---

### Frontend

**Bootstrap**
Framework CSS para crear interfaces web responsivas.

**Chart.js**
Librería JavaScript para crear gráficos interactivos.

**Jinja2**
Motor de templates para Python, usado por Flask.

---

### Base de Datos

**PostgreSQL**
Sistema de gestión de base de datos relacional open source, usado en producción.

**SQLite**
Base de datos ligera embebida, usada en desarrollo y testing.

**Migration**
Cambio versionado en el esquema de base de datos. Gestionado con Flask-Migrate (Alembic).

**ORM (Object-Relational Mapping)**
Técnica para mapear objetos de programación a tablas de base de datos.

---

### Deployment

**AWS (Amazon Web Services)**
Plataforma cloud de Amazon. Dashboard Sonar soporta deployment en EC2, RDS, ECS.

**EC2 (Elastic Compute Cloud)**
Servicio de servidores virtuales en AWS.

**RDS (Relational Database Service)**
Base de datos PostgreSQL gestionada en AWS.

**ECS (Elastic Container Service)**
Servicio de orquestación de contenedores Docker en AWS.

**ALB (Application Load Balancer)**
Balanceador de carga de aplicaciones en AWS.

**Docker**
Plataforma de contenedores para empaquetar aplicaciones.

**Container**
Unidad empaquetada de software que incluye código, runtime y dependencias.

---

## 🔧 DevOps y Operaciones

### Monitoring

**Prometheus**
Sistema de monitoring y alertas open source.

**Grafana**
Plataforma de visualización de métricas y dashboards.

**CloudWatch**
Servicio de monitoring de AWS.

**Golden Signals**
Las 4 métricas clave de monitoring:
1. **Latency** - Tiempo de respuesta
2. **Traffic** - Volumen de requests
3. **Errors** - Tasa de errores
4. **Saturation** - Uso de recursos

---

### Reliability

**MTTR (Mean Time To Recovery)**
Tiempo promedio para recuperarse de un incidente. Objetivo: < 30 minutos.

**SLO (Service Level Objective)**
Objetivo interno de nivel de servicio. Ejemplo: 99.5% uptime.

**SLI (Service Level Indicator)**
Métrica medible de nivel de servicio. Ejemplo: % de requests exitosos.

**Runbook**
Documento con procedimientos paso a paso para resolver incidentes comunes.

**Rollback**
Revertir a una versión anterior del código o base de datos.

---

### CI/CD

**CI (Continuous Integration)**
Práctica de integrar código frecuentemente con tests automatizados.

**CD (Continuous Deployment)**
Despliegue automatizado a producción después de pasar tests.

**Pipeline**
Secuencia automatizada de pasos (build, test, deploy).

**GitHub Actions**
Plataforma de CI/CD integrada en GitHub.

---

## 💾 Base de Datos

### Tablas Principales

**metricas**
Almacena el snapshot más reciente de métricas de SonarQube por aplicación.

**historico**
Almacena histórico completo de métricas para trending y análisis temporal.

**users**
Gestión de usuarios con autenticación bcrypt.

**proveedor**
Metadatos de aplicaciones (provider, tipo, configuración).

**stats**
Estadísticas agregadas por aplicación.

**daily**
Snapshots diarios para análisis de tendencias.

**registro**
Log de ejecución de procesos ETL.

---

### Índices

**Index (Índice de Base de Datos)**
Estructura de datos que mejora la velocidad de búsqueda en una tabla.

**Composite Index**
Índice sobre múltiples columnas. Ejemplo:
```sql
CREATE INDEX idx_app_date ON metricas (aplicacion, fecha DESC);
```

**Covering Index**
Índice que incluye todas las columnas necesarias para una query, evitando acceso a la tabla.

---

### Conceptos de Performance

**N+1 Query Problem**
Anti-pattern donde se ejecuta 1 query principal + N queries adicionales, causando baja performance.

**Connection Pool**
Conjunto reutilizable de conexiones a base de datos para mejorar performance.

**Query Optimization**
Proceso de mejorar el rendimiento de queries SQL usando índices y reescritura.

**EXPLAIN ANALYZE**
Comando PostgreSQL para analizar el plan de ejecución de queries.

---

## 🔒 Seguridad

### OWASP Top 10

Las 10 vulnerabilidades de seguridad más críticas:

1. **SQL Injection** - Inserción de código SQL malicioso
2. **XSS (Cross-Site Scripting)** - Inyección de scripts en páginas web
3. **CSRF (Cross-Site Request Forgery)** - Ejecución de acciones no autorizadas
4. **Broken Authentication** - Autenticación débil o rota
5. **Security Misconfiguration** - Configuración insegura
6. **Sensitive Data Exposure** - Exposición de datos sensibles
7. **XXE (XML External Entities)** - Ataque mediante XML malicioso
8. **Broken Access Control** - Control de acceso inadecuado
9. **Using Components with Known Vulnerabilities** - Dependencias vulnerables
10. **Insufficient Logging & Monitoring** - Logging inadecuado

---

### Conceptos de Seguridad

**bcrypt**
Algoritmo de hashing de passwords resistente a ataques de fuerza bruta.

**Salt**
Datos aleatorios añadidos a passwords antes de hashear para prevenir ataques rainbow table.

**HTTPS**
Protocolo HTTP sobre SSL/TLS para comunicación encriptada.

**SSL/TLS**
Protocolos para encriptar comunicaciones en redes.

**Secrets Management**
Gestión segura de credenciales, API keys y certificados. Herramientas: AWS Secrets Manager, Vault.

**CSP (Content Security Policy)**
Header HTTP que previene XSS especificando fuentes permitidas de contenido.

**Fail2Ban**
Herramienta que banea IPs con intentos fallidos de login.

---

## 📊 Terminología Adicional

### Versioning

**SemVer (Semantic Versioning)**
Esquema de versionado: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: Nueva funcionalidad compatible
- PATCH: Bug fixes compatibles

**Breaking Change**
Cambio incompatible que requiere modificación de código cliente.

---

### Testing

**Unit Test**
Test que verifica una unidad individual de código (función, método).

**Integration Test**
Test que verifica interacción entre componentes.

**E2E (End-to-End) Test**
Test que verifica flujo completo desde interfaz de usuario hasta base de datos.

**Test Coverage**
Porcentaje de código ejecutado por tests.

**Assertion**
Verificación de que un resultado esperado es correcto.

---

### Acrónimos Comunes

| Acrónimo | Significado | Uso en Dashboard Sonar |
|----------|-------------|------------------------|
| **API** | Application Programming Interface | APIs REST para integración |
| **CRUD** | Create, Read, Update, Delete | Operaciones de base de datos |
| **DLOC** | Duplicated Lines of Code | Métrica de duplicación |
| **ETL** | Extract, Transform, Load | Pipeline de datos de SonarQube |
| **HA** | High Availability | Configuración de producción |
| **LOC** | Lines of Code | Tamaño del proyecto |
| **MTTR** | Mean Time To Recovery | SLA de recuperación |
| **NCLOC** | Non-Commented Lines of Code | Métrica estándar de tamaño |
| **ORM** | Object-Relational Mapping | SQLAlchemy |
| **REST** | Representational State Transfer | Arquitectura de APIs |
| **RPO** | Recovery Point Objective | Objetivo de pérdida de datos |
| **RTO** | Recovery Time Objective | Objetivo de tiempo de recuperación |
| **SLA** | Service Level Agreement | Acuerdos de nivel de servicio |
| **SQALE** | Software Quality Assessment | Metodología de deuda técnica |
| **WSGI** | Web Server Gateway Interface | Interfaz Python/servidor web |

---

## 🔗 Referencias

### Documentación Relacionada

Para profundizar en conceptos específicos:

**Métricas de SonarQube**:
- [METRICS_EXPLAINED.md](../user-guide/METRICS_EXPLAINED.md) - Explicación detallada de cada métrica
- [WHAT_IS_DASHBOARD_SONAR.md](../getting-started/WHAT_IS_DASHBOARD_SONAR.md) - Conceptos básicos

**Arquitectura y Tecnología**:
- [ARCHITECTURE.md](../../1-technical/architecture/ARCHITECTURE.md) - Arquitectura del sistema
- [DATABASE_SCHEMA.md](../../1-technical/architecture/DATABASE_SCHEMA.md) - Esquema de base de datos

**Performance**:
- [PERFORMANCE_TUNING.md](../../1-technical/advanced/PERFORMANCE_TUNING.md) - Optimización de performance

**Seguridad**:
- [SECURITY_HARDENING.md](../../2-operations/security/SECURITY_HARDENING.md) - Guía de seguridad

**Operaciones**:
- [MONITORING_GUIDE.md](../../2-operations/monitoring/MONITORING_GUIDE.md) - Monitoring y alertas
- [RUNBOOK.md](../../2-operations/runbooks/RUNBOOK.md) - Procedimientos de incidentes

---

## 📚 Fuentes Externas

**SonarQube Documentation**:
- [Metric Definitions](https://docs.sonarqube.org/latest/user-guide/metric-definitions/)
- [Quality Gates](https://docs.sonarqube.org/latest/user-guide/quality-gates/)

**SQALE Methodology**:
- [SQALE Method](http://www.sqale.org/)

**OWASP**:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

**Flask Documentation**:
- [Flask Official Docs](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

**Última actualización**: Diciembre 2025
**Mantenido por**: Equipo de Documentación
**Contribuciones**: Ver [DOCUMENTAR_CAMBIOS.md](../../1-technical/reference/guides/DOCUMENTAR_CAMBIOS.md)
