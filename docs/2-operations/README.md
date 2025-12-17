# Operations Documentation

**Audiencia**: DevOps Engineers, SRE, System Administrators, Cloud Engineers

Esta sección contiene toda la documentación operativa necesaria para deployar, monitorear, mantener y escalar Dashboard Sonar en producción.

---

## 📋 Índice por Tema

### 🚨 [Runbooks](runbooks/)
Procedimientos de respuesta a incidentes y troubleshooting operativo.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[RUNBOOK.md](runbooks/RUNBOOK.md)** | Runbook completo con procedimientos de incidentes, health checks y rollback | 🔴 CRÍTICO |

**Contenido clave**:
- Health checks (30s rápido, 5min completo)
- 4 incidentes comunes con resolución paso a paso
- Procedimientos de emergencia y rollback
- Matriz de escalamiento
- Post-incident report templates

---

### 📊 [Monitoring](monitoring/)
Métricas, alertas, dashboards y observabilidad.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[MONITORING_GUIDE.md](monitoring/MONITORING_GUIDE.md)** | Guía completa de monitoring con Prometheus, Grafana, CloudWatch | 🔴 CRÍTICO |

**Contenido clave**:
- Golden Signals (Latency, Traffic, Errors, Saturation)
- Configuración de Prometheus y Grafana
- 8 alertas críticas con thresholds
- Dashboards recomendados
- Log aggregation y análisis

---

### 💾 [Backup & Recovery](backup-recovery/)
Estrategia de backups, disaster recovery y restauración.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[BACKUP_RESTORE.md](backup-recovery/BACKUP_RESTORE.md)** | Estrategia completa de backups y disaster recovery | 🔴 CRÍTICO |

**Contenido clave**:
- Estrategia 3-2-1 de backups (RPO 24h, RTO 2h)
- Métodos de backup PostgreSQL (pg_dump, pg_basebackup, WAL archiving)
- Procedimientos de restore completo y selectivo
- Point-in-time recovery (PITR)
- Plan de disaster recovery completo

---

### 🚀 [Deployment](deployment/)
Guías de deployment en diferentes plataformas cloud.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[DEPLOYMENT_AWS.md](deployment/DEPLOYMENT_AWS.md)** | Deployment completo en AWS (EC2, RDS, ECS, Beanstalk) | 🟠 ALTA |
| **[infrastructure/deployment/DEPLOYMENT.md](infrastructure/deployment/DEPLOYMENT.md)** | Guía general de deployment | 🟡 MEDIA |

**DEPLOYMENT_AWS.md - Contenido clave**:
- 3 arquitecturas de deployment (EC2+RDS, ECS Fargate, Elastic Beanstalk)
- Setup completo paso a paso (VPC, Security Groups, RDS Multi-AZ, ALB)
- Auto-scaling y HA configuration
- CI/CD pipeline con GitHub Actions
- Cost optimization (~$220/mes baseline)

**Documentación futura recomendada**:
- `DEPLOYMENT_GCP.md` - Google Cloud Platform
- `DEPLOYMENT_AZURE.md` - Microsoft Azure
- `DEPLOYMENT_KUBERNETES.md` - Kubernetes/Helm

---

### 🔒 [Security](security/)
Hardening de seguridad, compliance y mejores prácticas.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[SECURITY_HARDENING.md](security/SECURITY_HARDENING.md)** | Guía completa de security hardening | 🔴 CRÍTICO |

**Contenido clave**:
- Protección OWASP Top 10 (SQL injection, XSS, CSRF)
- Application security (input validation, CSRF tokens, CSP)
- Database security (SSL, RLS, encryption at rest/transit)
- Infrastructure hardening (OS, SSH, firewall, Fail2Ban)
- Secrets management (AWS Secrets Manager, Vault)
- Security checklist pre-producción

---

### 🔄 [CI/CD](cicd/)
Pipelines de integración y deployment continuo.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[CICD_USER_MANUAL.md](cicd/CICD_USER_MANUAL.md)** | Manual de usuario de CI/CD | 🟡 MEDIA |

**Documentación futura recomendada**:
- `CICD_GITHUB_ACTIONS.md` - GitHub Actions workflows
- `CICD_JENKINS.md` - Jenkins pipelines
- `CICD_GITLAB.md` - GitLab CI/CD

---

### 🏗️ [Infrastructure](infrastructure/)
Infraestructura as code, configuración de servidores.

| Documento | Descripción | Prioridad |
|-----------|-------------|-----------|
| **[deployment/DEPLOYMENT.md](infrastructure/deployment/DEPLOYMENT.md)** | Deployment general | 🟡 MEDIA |
| **[deployment/README.md](infrastructure/deployment/README.md)** | Índice de deployment docs | 🟡 MEDIA |

**Documentación futura recomendada**:
- `TERRAFORM.md` - Infrastructure as Code con Terraform
- `ANSIBLE.md` - Configuration management con Ansible
- `DOCKER_COMPOSE.md` - Deployment con Docker Compose

---

### 📚 [Reference](reference/)
Material de referencia rápida para operaciones.

- *(Sección reservada para troubleshooting operativo y quick reference guides)*

**Documentación futura recomendada**:
- `TROUBLESHOOTING_OPS.md` - Troubleshooting operativo
- `COMMAND_REFERENCE.md` - Comandos útiles
- `UPGRADE_GUIDE.md` - Guía de actualización entre versiones

---

## 🎯 Rutas de Aprendizaje

### Para Nuevos DevOps/SRE

**Día 1: Setup Inicial**
1. [deployment/DEPLOYMENT_AWS.md](deployment/DEPLOYMENT_AWS.md) - Deployar en AWS
2. [security/SECURITY_HARDENING.md](security/SECURITY_HARDENING.md) - Securizar el sistema
3. [backup-recovery/BACKUP_RESTORE.md](backup-recovery/BACKUP_RESTORE.md) - Configurar backups

**Semana 1: Operación Diaria**
4. [monitoring/MONITORING_GUIDE.md](monitoring/MONITORING_GUIDE.md) - Setup monitoring
5. [runbooks/RUNBOOK.md](runbooks/RUNBOOK.md) - Procedimientos de incidentes
6. [cicd/CICD_USER_MANUAL.md](cicd/CICD_USER_MANUAL.md) - CI/CD pipelines

**On-call Preparation**
7. Memorizar [runbooks/RUNBOOK.md](runbooks/RUNBOOK.md) - Incidentes comunes
8. Configurar alertas desde [monitoring/MONITORING_GUIDE.md](monitoring/MONITORING_GUIDE.md)
9. Practicar restore desde [backup-recovery/BACKUP_RESTORE.md](backup-recovery/BACKUP_RESTORE.md)

---

### Para SREs

**Core Reading** (en orden):
1. [monitoring/MONITORING_GUIDE.md](monitoring/MONITORING_GUIDE.md) - Observability
2. [runbooks/RUNBOOK.md](runbooks/RUNBOOK.md) - Incident response
3. [backup-recovery/BACKUP_RESTORE.md](backup-recovery/BACKUP_RESTORE.md) - DR planning
4. [security/SECURITY_HARDENING.md](security/SECURITY_HARDENING.md) - Security posture

**Advanced Topics**:
5. [deployment/DEPLOYMENT_AWS.md](deployment/DEPLOYMENT_AWS.md) - Infrastructure
6. Ver [../1-technical/](../1-technical/) para entender la arquitectura

---

### Para System Administrators

**Essential Reading**:
1. [../3-user/admin-guide/ADMIN_GUIDE.md](../3-user/admin-guide/ADMIN_GUIDE.md) - Administración diaria
2. [backup-recovery/BACKUP_RESTORE.md](backup-recovery/BACKUP_RESTORE.md) - Backups
3. [security/SECURITY_HARDENING.md](security/SECURITY_HARDENING.md) - Security
4. [runbooks/RUNBOOK.md](runbooks/RUNBOOK.md) - Troubleshooting

---

## 🚨 Documentos Críticos para On-Call

Si estás on-call, estos son los documentos que **DEBES** tener a mano:

### 🔴 P0 - CRÍTICO (leer antes de on-call)
1. **[runbooks/RUNBOOK.md](runbooks/RUNBOOK.md)** - Procedimientos de incidentes
2. **[monitoring/MONITORING_GUIDE.md](monitoring/MONITORING_GUIDE.md)** - Alertas y métricas

### 🟠 P1 - ALTA (conocer ubicación)
3. **[backup-recovery/BACKUP_RESTORE.md](backup-recovery/BACKUP_RESTORE.md)** - Restore procedures
4. **[deployment/DEPLOYMENT_AWS.md](deployment/DEPLOYMENT_AWS.md)** - Infrastructure details

### 🟡 P2 - MEDIA (nice to know)
5. **[security/SECURITY_HARDENING.md](security/SECURITY_HARDENING.md)** - Security procedures
6. **[../3-user/admin-guide/ADMIN_GUIDE.md](../3-user/admin-guide/ADMIN_GUIDE.md)** - Admin operations

---

## 📊 SLAs y Objetivos

| Métrica | Objetivo | Documentación |
|---------|----------|---------------|
| **Uptime** | 99.5% | [monitoring/MONITORING_GUIDE.md](monitoring/MONITORING_GUIDE.md) |
| **RTO** | < 2 horas | [backup-recovery/BACKUP_RESTORE.md](backup-recovery/BACKUP_RESTORE.md) |
| **RPO** | < 24 horas | [backup-recovery/BACKUP_RESTORE.md](backup-recovery/BACKUP_RESTORE.md) |
| **MTTR** | < 30 minutos | [runbooks/RUNBOOK.md](runbooks/RUNBOOK.md) |
| **P95 Latency** | < 1s | [monitoring/MONITORING_GUIDE.md](monitoring/MONITORING_GUIDE.md) |

---

## 🔗 Documentación Relacionada

### Otros Sectores

- **[1-technical/](../1-technical/)** - Para desarrolladores (arquitectura, APIs, desarrollo)
- **[3-user/](../3-user/)** - Para usuarios finales y administradores

### Documentación Externa

- [AWS Documentation](https://docs.aws.amazon.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## 📖 Contribuir a la Documentación

¿Encontraste un incidente no documentado o quieres agregar un runbook?

1. Actualiza el documento relevante (preferiblemente RUNBOOK.md)
2. Sigue [../1-technical/development/GIT_STRATEGY.md](../1-technical/development/GIT_STRATEGY.md)
3. Crea un PR con tus cambios
4. Notifica al equipo SRE para review

---

**Última actualización**: Diciembre 2025
**Mantenido por**: Equipo DevOps/SRE
**SLA Documentación**: Actualizar dentro de 24h después de cada incidente P0/P1
