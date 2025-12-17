# Runbook - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, On-call Engineers
**Criticidad**: 🔴 CRÍTICO - Para uso en producción

---

## 📋 Tabla de Contenidos

1. [Información General](#información-general)
2. [Contactos de Emergencia](#contactos-de-emergencia)
3. [Health Checks](#health-checks)
4. [Incidentes Comunes](#incidentes-comunes)
5. [Procedimientos de Emergencia](#procedimientos-de-emergencia)
6. [Rollback](#rollback)
7. [Escalamiento](#escalamiento)
8. [Post-Incident](#post-incident)

---

## 🎯 Información General

### ¿Qué es este Runbook?

Este documento contiene **procedimientos operativos** para responder a incidentes en Dashboard Sonar en producción.

**Úsalo cuando**:
- 🔴 La aplicación está caída (downtime)
- 🟠 Hay errores críticos afectando usuarios
- 🟡 Performance degradado significativamente
- 🔵 Alertas críticas activadas

**Objetivo**: Restaurar el servicio lo más rápido posible (MTTR < 30 minutos).

---

### Información del Servicio

| Elemento | Valor | Notas |
|----------|-------|-------|
| **Nombre** | Dashboard Sonar | |
| **URL Producción** | https://dashboard-sonar.empresa.com | |
| **URL Staging** | https://staging-dashboard.empresa.com | Para testing |
| **Repositorio** | github.com/jfdelafuente/dashboardsonar-application-python | |
| **SLA** | 99.5% uptime | ~3.6 horas downtime/mes permitido |
| **RTO** | 30 minutos | Recovery Time Objective |
| **RPO** | 24 horas | Recovery Point Objective (pérdida de datos aceptable) |

---

### Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Runtime** | Python | 3.12+ |
| **Framework** | Flask | 3.0.0 |
| **WSGI Server** | Gunicorn | 20.1+ |
| **Base de Datos** | PostgreSQL | 13+ |
| **Web Server** | Nginx | 1.18+ |
| **OS** | Ubuntu Linux | 22.04 LTS |

---

## 📞 Contactos de Emergencia

### Equipo On-Call

| Rol | Nombre | Email | Teléfono | Horario | Escalamiento |
|-----|--------|-------|----------|---------|--------------|
| **On-call Primary** | [Nombre] | oncall-primary@empresa.com | +34 XXX XXX XXX | 24/7 | Inmediato |
| **On-call Backup** | [Nombre] | oncall-backup@empresa.com | +34 XXX XXX XXX | 24/7 | +15 minutos |
| **Tech Lead** | [Nombre] | techlead@empresa.com | +34 XXX XXX XXX | Lun-Vie 9-18h | +30 minutos |
| **SRE Manager** | [Nombre] | sre-manager@empresa.com | +34 XXX XXX XXX | Lun-Vie 9-18h | +1 hora |
| **CTO** | [Nombre] | cto@empresa.com | +34 XXX XXX XXX | Emergencias | Critical only |

### Proveedores Externos

| Proveedor | Servicio | Contacto | SLA |
|-----------|----------|----------|-----|
| **AWS Support** | Infraestructura | support.aws.com | < 1 hora (Enterprise) |
| **PostgreSQL DBA** | Base de Datos | dba@empresa.com | < 2 horas |

### Canales de Comunicación

- 🚨 **Slack - Incidentes**: #incidents-dashboard-sonar
- 💬 **Slack - Operaciones**: #ops-dashboard
- 📧 **Email Grupo**: ops-dashboard@empresa.com
- 📱 **PagerDuty**: dashboard-sonar-oncall

---

## 🏥 Health Checks

### Health Check Rápido (30 segundos)

Ejecuta estos checks para evaluar el estado del servicio:

#### 1. Application Health Endpoint

```bash
curl -I https://dashboard-sonar.empresa.com/health

# ✅ Respuesta esperada (200 OK):
HTTP/2 200
content-type: application/json
{"status": "healthy", "timestamp": "2025-12-17T10:30:00Z"}

# ❌ Problema (5xx, timeout, connection refused)
```

**Si falla**: La aplicación no responde → Ver [Incident: Aplicación Caída](#incident-1-aplicación-caída-http-502503)

---

#### 2. Database Connectivity

```bash
# Desde el servidor de aplicación
psql -h db-host -U dashboard_user -d dashboardsonar -c "SELECT 1;"

# ✅ Respuesta esperada:
 ?column?
----------
        1
(1 row)

# ❌ Problema: connection refused, timeout, authentication failed
```

**Si falla**: Database no accesible → Ver [Incident: Database Connection Error](#incident-3-database-connection-error)

---

#### 3. Web Server (Nginx) Status

```bash
sudo systemctl status nginx

# ✅ Respuesta esperada:
● nginx.service - A high performance web server
   Active: active (running) since Mon 2025-12-17 10:00:00 UTC

# ❌ Problema: inactive (dead), failed
```

**Si falla**: Nginx caído → Ver [Procedimiento: Reiniciar Nginx](#reiniciar-nginx)

---

#### 4. Application Server (Gunicorn) Status

```bash
sudo systemctl status dashboardsonar

# ✅ Respuesta esperada:
● dashboardsonar.service - Dashboard Sonar Flask Application
   Active: active (running) since Mon 2025-12-17 10:00:00 UTC

# ❌ Problema: inactive (dead), failed
```

**Si falla**: Gunicorn caído → Ver [Incident: Aplicación Caída](#incident-1-aplicación-caída-http-502503)

---

#### 5. Application Logs - Errores Recientes

```bash
# Ver últimos 50 errores
tail -50 /var/log/dashboardsonar/app.log | grep -E "ERROR|CRITICAL"

# ✅ Sin errores recientes (output vacío)
# ❌ Múltiples ERRORs o CRITICAL
```

**Si hay errores**: Diagnosticar según el mensaje → Ver [Troubleshooting por Logs](#troubleshooting-por-logs)

---

### Health Check Completo (5 minutos)

Para análisis más profundo:

```bash
#!/bin/bash
# health_check_full.sh

echo "=== Dashboard Sonar - Health Check Completo ==="
echo ""

# 1. HTTP Health
echo "[1/7] HTTP Health Endpoint..."
curl -f https://dashboard-sonar.empresa.com/health || echo "❌ FAILED"

# 2. Database
echo "[2/7] Database Connectivity..."
psql -h localhost -U dashboard_user -d dashboardsonar -c "SELECT COUNT(*) FROM metricas;" || echo "❌ FAILED"

# 3. Nginx
echo "[3/7] Nginx Status..."
sudo systemctl is-active nginx || echo "❌ FAILED"

# 4. Gunicorn
echo "[4/7] Gunicorn Status..."
sudo systemctl is-active dashboardsonar || echo "❌ FAILED"

# 5. Disk Space
echo "[5/7] Disk Space..."
df -h / | awk 'NR==2 {if ($5+0 > 85) print "❌ Disk > 85%: "$5; else print "✅ Disk OK: "$5}'

# 6. Memory
echo "[6/7] Memory Usage..."
free -h | awk 'NR==2 {print "Memory: "$3"/"$2}'

# 7. Recent Errors
echo "[7/7] Recent Critical Errors..."
tail -100 /var/log/dashboardsonar/app.log | grep -c "CRITICAL" | awk '{if ($1 > 0) print "❌ "$1" CRITICAL errors"; else print "✅ No critical errors"}'

echo ""
echo "=== Health Check Completado ==="
```

---

## 🔥 Incidentes Comunes

### Incident #1: Aplicación Caída (HTTP 502/503)

**Síntomas**:
- Dashboard no carga (502 Bad Gateway o 503 Service Unavailable)
- Health endpoint no responde
- Usuarios reportan "página no disponible"

**Severidad**: 🔴 **CRÍTICA** - Downtime total

**Tiempo de respuesta**: < 5 minutos

---

#### Causa Raíz Probable

| Probabilidad | Causa | Cómo Verificar |
|--------------|-------|----------------|
| **70%** | Gunicorn workers crashed | `systemctl status dashboardsonar` |
| **15%** | Database connection pool exhausted | Logs: "FATAL: remaining connection slots" |
| **10%** | Out of memory (OOM) | `dmesg | grep -i oom` |
| **5%** | Nginx misconfigured | `sudo nginx -t` |

---

#### Resolución - Paso a Paso

**PASO 1**: Verificar estado de Gunicorn

```bash
sudo systemctl status dashboardsonar

# Si muestra "inactive (dead)" o "failed":
```

**PASO 2**: Ver últimas líneas del log para entender por qué crasheó

```bash
tail -50 /var/log/dashboardsonar/app.log
# Buscar: CRITICAL, Out of memory, Traceback
```

**PASO 3**: Reiniciar Gunicorn

```bash
sudo systemctl restart dashboardsonar

# Verificar que inició correctamente
sudo systemctl status dashboardsonar
# Debe mostrar: "active (running)"
```

**PASO 4**: Verificar que la aplicación responde

```bash
curl https://dashboard-sonar.empresa.com/health
# Debe retornar: {"status": "healthy"}
```

**PASO 5**: Monitorear logs en tiempo real por 2-3 minutos

```bash
tail -f /var/log/dashboardsonar/app.log
# Asegurar que no hay nuevos ERRORs
```

**Tiempo estimado**: 3-5 minutos

---

#### Si el Reinicio No Funciona

**Escenario A**: Gunicorn no inicia (falla inmediatamente)

```bash
# Ver error específico
journalctl -u dashboardsonar -n 50

# Causas comunes:
# 1. Puerto 5000 ocupado
sudo lsof -i :5000
# Si hay proceso, matar: sudo kill -9 <PID>

# 2. Syntax error en código Python
python /path/to/dashboardsonar/run.py
# Arreglar el error de sintaxis

# 3. Archivo .env corrupto o SECRET_KEY faltante
cat /path/to/dashboardsonar/.env | grep SECRET_KEY
# Regenerar si falta: python -c "import secrets; print(secrets.token_hex(32))"
```

**Escenario B**: Gunicorn inicia pero crashea en loop

```bash
# Aumentar log level a DEBUG temporalmente
# Editar .env:
LOG_LEVEL=DEBUG

# Reiniciar
sudo systemctl restart dashboardsonar

# Ver logs detallados
tail -f /var/log/dashboardsonar/app.log
# Identificar el error específico

# RESTAURAR LOG_LEVEL=INFO después de resolver
```

---

#### Escalamiento

Si después de **15 minutos** no resuelves:

1. **Notificar en Slack #incidents-dashboard-sonar**:
   ```
   🔴 CRITICAL: Dashboard Sonar DOWN
   Inicio: 10:30 UTC
   Intentado: Restart gunicorn (failed)
   Logs: [pegar últimas 10 líneas]
   Escalando a Tech Lead
   ```

2. **Llamar a Tech Lead** (ver [Contactos](#contactos-de-emergencia))

3. **Considerar rollback** si el problema empezó después de un deploy → Ver [Rollback](#rollback-de-aplicación)

---

### Incident #2: Aplicación Lenta (>5s Response Time)

**Síntomas**:
- Dashboard tarda >5 segundos en cargar
- Usuarios reportan "aplicación muy lenta"
- Timeouts esporádicos

**Severidad**: 🟠 **ALTA** - Servicio degradado

**Tiempo de respuesta**: < 10 minutos

---

#### Causa Raíz Probable

| Probabilidad | Causa | Cómo Verificar |
|--------------|-------|----------------|
| **50%** | Queries SQL lentas | `SELECT * FROM pg_stat_activity WHERE state = 'active'` |
| **25%** | Alto volumen de tráfico | Nginx access logs: `tail /var/log/nginx/access.log | wc -l` |
| **15%** | CPU/Memory saturados | `top`, `free -h` |
| **10%** | Base de datos no optimizada | Falta de índices |

---

#### Resolución - Paso a Paso

**PASO 1**: Verificar queries activas en PostgreSQL

```bash
psql -h localhost -U dashboard_user -d dashboardsonar

# Ver queries activas
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC
LIMIT 10;
```

**Si hay queries >30 segundos**:

```sql
-- Identificar el PID de la query lenta
-- Luego terminarla:
SELECT pg_terminate_backend(12345);  -- Reemplazar 12345 con el PID real
```

---

**PASO 2**: Verificar uso de CPU y Memoria

```bash
# CPU
top -b -n 1 | head -20

# Memory
free -h

# Si CPU >90% o Memory >90%:
# Identificar proceso problemático
ps aux --sort=-%mem | head -10
ps aux --sort=-%cpu | head -10
```

**Si Gunicorn está usando >80% Memory**:

```bash
# Reiniciar para liberar memoria
sudo systemctl restart dashboardsonar
```

---

**PASO 3**: Verificar conexiones activas a la base de datos

```sql
SELECT count(*) FROM pg_stat_activity;

-- Si hay >80 conexiones (de max 100):
-- Hay leak de conexiones
```

**Solución temporal**:

```bash
# Reiniciar aplicación para liberar conexiones
sudo systemctl restart dashboardsonar
```

**Solución permanente**: Reportar a Tech Lead para investigar leak en código.

---

**PASO 4**: Verificar logs de queries lentas

```bash
# Ver queries que tardaron >1 segundo
tail -100 /var/log/dashboardsonar/app.log | grep -E "took [0-9]{4,}ms"

# Ejemplo output:
# 2025-12-17 10:30:00 - WARNING - Query took 2500ms: SELECT * FROM metricas WHERE...
```

**Si hay queries lentas recurrentes**: Reportar a Tech Lead para agregar índices.

---

#### Mitigación Temporal

Si el problema persiste y no puedes resolverlo:

```bash
# Opción 1: Reiniciar Nginx (libera cache)
sudo systemctl restart nginx

# Opción 2: Aumentar workers de Gunicorn (si hay CPU disponible)
# Editar /etc/systemd/system/dashboardsonar.service
# ExecStart: --workers 4 → --workers 6
sudo systemctl daemon-reload
sudo systemctl restart dashboardsonar

# Opción 3: Reiniciar PostgreSQL (CUIDADO: breve downtime)
sudo systemctl restart postgresql
```

---

### Incident #3: Database Connection Error

**Síntomas**:
- Error: `OperationalError: could not connect to server`
- Error: `FATAL: remaining connection slots are reserved`
- Error: `FATAL: database "dashboardsonar" does not exist`

**Severidad**: 🔴 **CRÍTICA** - Downtime total

---

#### Resolución - Por Tipo de Error

**Error A**: "could not connect to server"

```bash
# PASO 1: Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Si está "inactive":
sudo systemctl start postgresql

# PASO 2: Verificar conectividad de red
ping db-host

# PASO 3: Verificar firewall
sudo ufw status | grep 5432
# Debe mostrar: 5432 ALLOW

# PASO 4: Probar conexión manual
psql -h localhost -U dashboard_user -d dashboardsonar

# Si falla con "authentication failed":
# Verificar credenciales en .env
cat /path/to/.env | grep DB_PASS
```

---

**Error B**: "remaining connection slots are reserved"

**Causa**: Connection pool exhausted (>100 conexiones activas).

```bash
# PASO 1: Ver conexiones activas
psql -h localhost -U dashboard_user -d dashboardsonar

SELECT count(*) FROM pg_stat_activity;
# Si retorna >90: Problema

# PASO 2: Terminar conexiones idle
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND query_start < NOW() - INTERVAL '10 minutes';

# PASO 3: Reiniciar aplicación (para liberar leak)
sudo systemctl restart dashboardsonar
```

---

**Error C**: "database 'dashboardsonar' does not exist"

**Causa**: Database fue eliminada o nombre incorrecto en .env.

```bash
# PASO 1: Listar bases de datos
psql -h localhost -U postgres -c "\l"

# PASO 2: Si no existe dashboardsonar:
# Restaurar desde backup (ver BACKUP_RESTORE.md)

# O crear nueva (solo si no hay datos importantes):
createdb -h localhost -U postgres dashboardsonar
flask db upgrade
```

---

### Incident #4: Deployment Failed

**Síntomas**:
- Nuevo deployment no funciona
- Aplicación muestra código antiguo después de deploy
- CI/CD pipeline falló

**Severidad**: 🟡 **MEDIA** - No afecta producción si no se deployó

---

#### Resolución

**PASO 1**: Verificar estado del último deployment

```bash
# Ver commit actual en producción
cd /path/to/dashboardsonar
git log -1 --oneline

# Ver si hay cambios sin commitear
git status
```

---

**PASO 2**: Si el deployment falló a mitad de camino

```bash
# Restaurar a versión anterior estable
git checkout <commit-hash-anterior>

# Reiniciar aplicación
sudo systemctl restart dashboardsonar
```

---

**PASO 3**: Si la aplicación muestra código antiguo (cache)

```bash
# Limpiar cache de Python
find /path/to/dashboardsonar -type d -name __pycache__ -exec rm -rf {} +

# Reiniciar
sudo systemctl restart dashboardsonar

# Limpiar cache de Nginx
sudo rm -rf /var/cache/nginx/*
sudo systemctl restart nginx
```

---

## 🚨 Procedimientos de Emergencia

### Reiniciar Nginx

```bash
# Verificar configuración antes de reiniciar
sudo nginx -t

# Si OK:
sudo systemctl restart nginx

# Verificar que inició
sudo systemctl status nginx

# Ver logs si hay error
sudo tail -50 /var/log/nginx/error.log
```

---

### Reiniciar Gunicorn (Aplicación)

```bash
sudo systemctl restart dashboardsonar

# Verificar status
sudo systemctl status dashboardsonar

# Si falló, ver logs
journalctl -u dashboardsonar -n 50
```

---

### Reiniciar PostgreSQL

⚠️ **ADVERTENCIA**: Esto causa ~10-30 segundos de downtime.

**Solo hacer si**:
- Hay queries hung que no se pueden terminar
- Database en estado corrupto
- Leak de memoria en PostgreSQL

```bash
# Notificar downtime primero
# Slack: "⚠️ Reiniciando PostgreSQL - 30s downtime"

sudo systemctl restart postgresql

# Verificar que inició
sudo systemctl status postgresql

# Verificar conectividad
psql -h localhost -U postgres -c "SELECT 1;"

# Reiniciar aplicación
sudo systemctl restart dashboardsonar
```

---

### Emergency Shutdown (Mantenimiento)

Si necesitas apagar todo para mantenimiento:

```bash
#!/bin/bash
# emergency_shutdown.sh

echo "🚨 EMERGENCY SHUTDOWN - Dashboard Sonar"

# 1. Detener aplicación
echo "Deteniendo aplicación..."
sudo systemctl stop dashboardsonar

# 2. Detener Nginx
echo "Deteniendo Nginx..."
sudo systemctl stop nginx

# 3. Detener PostgreSQL (opcional, solo si es mantenimiento de BD)
# echo "Deteniendo PostgreSQL..."
# sudo systemctl stop postgresql

echo "✅ Todos los servicios detenidos"
echo "Para reiniciar: ./emergency_startup.sh"
```

---

### Emergency Startup (Después de Mantenimiento)

```bash
#!/bin/bash
# emergency_startup.sh

echo "🚀 EMERGENCY STARTUP - Dashboard Sonar"

# 1. Iniciar PostgreSQL (si fue detenido)
# echo "Iniciando PostgreSQL..."
# sudo systemctl start postgresql
# sleep 5

# 2. Iniciar aplicación
echo "Iniciando aplicación..."
sudo systemctl start dashboardsonar
sleep 3

# 3. Iniciar Nginx
echo "Iniciando Nginx..."
sudo systemctl start nginx

echo ""
echo "✅ Verificando servicios..."
sudo systemctl status postgresql | grep "Active:"
sudo systemctl status dashboardsonar | grep "Active:"
sudo systemctl status nginx | grep "Active:"

echo ""
echo "🏥 Health Check..."
curl -I https://dashboard-sonar.empresa.com/health

echo ""
echo "✅ Startup completado"
```

---

## ⏪ Rollback

### Rollback de Aplicación

**Cuándo usar**: Después de un deployment que introdujo bugs.

**Prerequisitos**: Conocer el commit hash de la versión estable anterior.

---

#### Procedimiento

**PASO 1**: Identificar versión anterior estable

```bash
cd /path/to/dashboardsonar

# Ver últimos 10 commits
git log --oneline -10

# Output ejemplo:
# a1b2c3d (HEAD) fix: corregir bug en dashboard
# e4f5g6h feat: agregar nueva funcionalidad  ← Aquí empezó el problema
# h7i8j9k fix: mejorar performance           ← Última versión estable
```

---

**PASO 2**: Hacer rollback al commit estable

```bash
# Checkout al commit anterior
git checkout h7i8j9k

# Verificar que estamos en la versión correcta
git log -1
```

---

**PASO 3**: Reiniciar aplicación

```bash
sudo systemctl restart dashboardsonar

# Verificar status
sudo systemctl status dashboardsonar
```

---

**PASO 4**: Verificar que funciona

```bash
# Health check
curl https://dashboard-sonar.empresa.com/health

# Ver logs
tail -f /var/log/dashboardsonar/app.log
# Asegurar que no hay ERRORs
```

---

**PASO 5**: Notificar rollback

```
Slack #incidents-dashboard-sonar:
✅ ROLLBACK COMPLETADO
Versión actual: h7i8j9k (última versión estable)
Tiempo de recuperación: 5 minutos
Próximos pasos: Tech Lead investigará el bug en commit e4f5g6h
```

---

### Rollback de Base de Datos

⚠️ **CRÍTICO**: Solo hacer si sabes lo que estás haciendo.

**Cuándo usar**: Migración de BD falló y dejó BD en estado inconsistente.

```bash
# PASO 1: Ver migraciones aplicadas
flask db current

# PASO 2: Revertir última migración
flask db downgrade -1

# PASO 3: Verificar que BD funciona
psql -h localhost -U dashboard_user -d dashboardsonar -c "SELECT COUNT(*) FROM metricas;"

# PASO 4: Reiniciar aplicación
sudo systemctl restart dashboardsonar
```

**Si la migración corrupted la BD**: Restaurar desde backup → Ver [BACKUP_RESTORE.md](../backup-recovery/BACKUP_RESTORE.md)

---

## 📈 Escalamiento

### Matriz de Escalamiento

| Tiempo Transcurrido | Acción | A Quién Escalar |
|---------------------|--------|-----------------|
| **0-15 min** | On-call primario intenta resolver | - |
| **15 min** | Si no resuelve, escalar | On-call backup |
| **30 min** | Si sigue sin resolverse, escalar | Tech Lead |
| **1 hora** | Si es crítico y no resuelto, escalar | SRE Manager |
| **2 horas** | Si afecta negocio, escalar | CTO |

---

### Cuándo Escalar Inmediatamente

**Escalar a Tech Lead SIN esperar** si:
- 🔴 Downtime total >30 minutos
- 🔴 Pérdida de datos detectada
- 🔴 Brecha de seguridad sospechada
- 🔴 Rollback falló
- 🔴 Backup corrupto

---

## 📋 Post-Incident

### Post-Incident Report (PIR)

Después de resolver un incidente, **completar este reporte en 24 horas**:

```markdown
# Post-Incident Report - Dashboard Sonar

**Incident ID**: INC-2025-001
**Fecha**: 2025-12-17
**Duración**: 10:30 - 11:00 UTC (30 minutos)
**Severidad**: 🔴 CRÍTICA

---

## Resumen Ejecutivo
[2-3 oraciones explicando qué pasó y el impacto]

## Línea de Tiempo
- 10:30 - Alerta recibida: Dashboard no responde
- 10:32 - On-call empieza investigación
- 10:35 - Identificado: Gunicorn crashed por OOM
- 10:40 - Reinicio de Gunicorn
- 10:45 - Servicio restaurado
- 11:00 - Incident cerrado

## Causa Raíz
[Explicación técnica de la causa]

## Impacto
- **Usuarios afectados**: 150 usuarios activos
- **Downtime**: 30 minutos
- **Pérdida de datos**: Ninguna
- **Revenue impact**: Ninguno (app interna)

## Resolución
[Pasos tomados para resolver]

## Prevención Futura
- [ ] Acción 1: Aumentar memory limit de Gunicorn
- [ ] Acción 2: Agregar alerta de memory >80%
- [ ] Acción 3: Investigar memory leak en código

## Lessons Learned
[Qué aprendimos, qué mejorar en procesos]

---

**Preparado por**: [Nombre On-call]
**Revisado por**: [Tech Lead]
**Fecha**: 2025-12-17
```

**Enviar a**: ops-dashboard@empresa.com, #post-mortems (Slack)

---

## 📚 Referencias

### Documentación Relacionada

- 📊 **Monitoring**: [MONITORING_GUIDE.md](../monitoring/MONITORING_GUIDE.md)
- 💾 **Backups**: [BACKUP_RESTORE.md](../backup-recovery/BACKUP_RESTORE.md)
- 🔒 **Security**: [SECURITY_HARDENING.md](../security/SECURITY_HARDENING.md)
- 🚀 **Deployment**: [DEPLOYMENT_AWS.md](../deployment/DEPLOYMENT_AWS.md)
- 🔧 **Admin Guide**: [../../3-user/admin-guide/ADMIN_GUIDE.md](../../3-user/admin-guide/ADMIN_GUIDE.md)

---

**Última actualización**: Diciembre 2025
**Versión del runbook**: 1.0.0
**Próxima revisión**: Después de cada incidente crítico
**Mantenido por**: Equipo SRE
