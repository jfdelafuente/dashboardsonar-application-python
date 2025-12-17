# Monitoring Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, Tech Leads
**Objetivo**: Configurar monitoreo proactivo para prevenir incidentes

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Métricas Clave](#métricas-clave)
3. [Configuración de Alertas](#configuración-de-alertas)
4. [Dashboards](#dashboards)
5. [Logs y Análisis](#logs-y-análisis)
6. [Health Checks](#health-checks)
7. [Herramientas Recomendadas](#herramientas-recomendadas)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

### ¿Por qué Monitorear?

El monitoreo proactivo permite:

✅ **Detectar problemas antes que afecten usuarios** (alertas tempranas)
✅ **Reducir MTTR** (Mean Time To Recovery) - de 30 min → 5 min
✅ **Cumplir SLA** de 99.5% uptime
✅ **Optimizar recursos** (CPU, memoria, costos)
✅ **Auditar actividad** (seguridad, compliance)

---

### Filosofía de Monitoreo

Seguimos el modelo **Golden Signals** de SRE:

| Signal | Qué Mide | Objetivo |
|--------|----------|----------|
| **Latency** | Tiempo de respuesta | < 1s (p95) |
| **Traffic** | Requests por minuto | Detectar spikes |
| **Errors** | Tasa de errores | < 0.1% |
| **Saturation** | Uso de recursos | < 80% CPU/Memory |

---

## 📊 Métricas Clave

### 1. Application Metrics (Flask)

#### 1.1 Request Latency (Latencia)

**Qué medir**:
- P50 (mediana): Tiempo de respuesta típico
- P95: 95% de requests más rápidos que este valor
- P99: 99% de requests más rápidos que este valor

**Thresholds**:
```yaml
Latency:
  p50: < 500ms   # ✅ Good
  p95: < 1s      # ⚠️ Warning si > 1s
  p99: < 2s      # 🔴 Critical si > 2s
```

**Cómo medir** (con Prometheus):

```python
# infocodest/monitoring/metrics.py
from prometheus_client import Histogram
import time
from functools import wraps

# Definir métrica
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint', 'status']
)

# Decorator para medir latencia
def measure_latency(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = f(*args, **kwargs)
            status = 200
            return result
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.endpoint,
                status=status
            ).observe(duration)
    return wrapper

# Aplicar a rutas
@app.route('/dashboard')
@measure_latency
def dashboard():
    # ...
```

---

#### 1.2 Request Rate (Tráfico)

**Qué medir**:
- Requests por minuto (RPM)
- Requests por segundo (RPS)

**Thresholds**:
```yaml
Traffic:
  normal: 10-50 RPM
  high: 50-100 RPM    # ⚠️ Warning
  critical: > 100 RPM # 🔴 Alerta - posible ataque
```

**Cómo medir**:

```python
from prometheus_client import Counter

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

@app.before_request
def count_request():
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status='pending'
    ).inc()
```

---

#### 1.3 Error Rate (Errores)

**Qué medir**:
- HTTP 4xx (errores de cliente)
- HTTP 5xx (errores de servidor)
- Tasa de error (%)

**Thresholds**:
```yaml
Errors:
  4xx_rate: < 5%     # Errores de usuario (OK)
  5xx_rate: < 0.1%   # ⚠️ Warning si > 0.1%
  5xx_rate: > 1%     # 🔴 Critical
```

**Cómo medir**:

```python
from prometheus_client import Counter

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status_code']
)

@app.errorhandler(Exception)
def handle_error(error):
    status = getattr(error, 'code', 500)
    ERROR_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status_code=status
    ).inc()
    return jsonify({'error': str(error)}), status
```

---

### 2. Infrastructure Metrics (Sistema)

#### 2.1 CPU Usage

**Qué medir**:
- CPU total (%)
- CPU por proceso (Gunicorn, PostgreSQL)

**Thresholds**:
```yaml
CPU:
  normal: < 60%
  warning: 60-80%   # ⚠️
  critical: > 80%   # 🔴 Alerta
```

**Cómo medir** (con node_exporter de Prometheus):

```bash
# Instalar node_exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvfz node_exporter-*.tar.gz
sudo cp node_exporter-*/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter

# Crear service
sudo tee /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

**Query Prometheus**:
```promql
# CPU promedio últimos 5 minutos
rate(node_cpu_seconds_total{mode!="idle"}[5m]) * 100
```

---

#### 2.2 Memory Usage

**Qué medir**:
- Memoria total usada (%)
- Memoria por proceso

**Thresholds**:
```yaml
Memory:
  normal: < 70%
  warning: 70-85%   # ⚠️
  critical: > 85%   # 🔴 Alerta - riesgo de OOM
```

**Query Prometheus**:
```promql
# Memoria usada (%)
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**Alerta CloudWatch** (AWS):
```json
{
  "AlarmName": "DashboardSonar-HighMemory",
  "MetricName": "MemoryUtilization",
  "Namespace": "AWS/EC2",
  "Statistic": "Average",
  "Period": 300,
  "EvaluationPeriods": 2,
  "Threshold": 85.0,
  "ComparisonOperator": "GreaterThanThreshold",
  "AlarmActions": ["arn:aws:sns:region:account:topic"]
}
```

---

#### 2.3 Disk Space

**Qué medir**:
- Disco usado (%)
- Crecimiento diario

**Thresholds**:
```yaml
Disk:
  normal: < 70%
  warning: 70-85%   # ⚠️
  critical: > 85%   # 🔴 Limpiar logs/backups
```

**Script de monitoreo**:
```bash
#!/bin/bash
# check_disk.sh

THRESHOLD=85
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ $USAGE -gt $THRESHOLD ]; then
    echo "🔴 CRITICAL: Disk usage ${USAGE}% > ${THRESHOLD}%"
    # Enviar alerta
    curl -X POST https://slack.webhook.url -d "{\"text\":\"Disk ${USAGE}%\"}"
else
    echo "✅ Disk usage: ${USAGE}%"
fi
```

**Cron job** (ejecutar cada hora):
```bash
0 * * * * /path/to/check_disk.sh >> /var/log/disk_check.log 2>&1
```

---

### 3. Database Metrics (PostgreSQL)

#### 3.1 Active Connections

**Qué medir**:
- Conexiones activas
- Conexiones idle
- Max connections

**Thresholds**:
```yaml
Connections:
  max: 100
  warning: > 80      # ⚠️ 80% capacity
  critical: > 95     # 🔴 Riesgo de "no more connections"
```

**Query para monitorear**:
```sql
-- Ver conexiones activas
SELECT
    count(*) FILTER (WHERE state = 'active') AS active,
    count(*) FILTER (WHERE state = 'idle') AS idle,
    count(*) AS total
FROM pg_stat_activity;
```

**Alerta Prometheus** (con postgres_exporter):
```promql
# Alerta si conexiones > 80
pg_stat_database_numbackends > 80
```

---

#### 3.2 Query Performance

**Qué medir**:
- Queries lentas (>1s)
- Queries más ejecutadas
- Cache hit ratio

**Thresholds**:
```yaml
Queries:
  slow_threshold: 1000ms   # ⚠️ Log si > 1s
  cache_hit_ratio: > 95%   # ✅ Good
  cache_hit_ratio: < 90%   # 🔴 Problema - agregar índices
```

**Habilitar slow query log** (PostgreSQL):
```bash
# Editar postgresql.conf
sudo nano /etc/postgresql/13/main/postgresql.conf

# Agregar:
log_min_duration_statement = 1000  # Log queries > 1s
log_line_prefix = '%t [%p]: user=%u,db=%d,app=%a,client=%h '
```

**Query para analizar**:
```sql
-- Top 10 queries lentas
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

#### 3.3 Cache Hit Ratio

**Qué medir**:
- Porcentaje de queries servidas desde cache (RAM) vs disco

**Query**:
```sql
SELECT
    sum(heap_blks_read) AS heap_read,
    sum(heap_blks_hit) AS heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio
FROM pg_statio_user_tables;

-- ✅ Ratio > 0.95 (95%) = Good
-- 🔴 Ratio < 0.90 (90%) = Aumentar shared_buffers
```

---

### 4. Business Metrics (Aplicación)

#### 4.1 User Activity

**Qué medir**:
- Usuarios activos (sesiones)
- Logins por día
- Dashboards más visitados

**Implementación**:
```python
# infocodest/monitoring/analytics.py
from prometheus_client import Gauge

ACTIVE_USERS = Gauge('active_users_total', 'Active logged-in users')

@app.before_request
def track_user():
    if current_user.is_authenticated:
        # Actualizar timestamp de último acceso
        cache.set(f'user_active_{current_user.id}', True, timeout=300)

        # Contar usuarios activos (últimos 5 min)
        active_count = len(cache.keys('user_active_*'))
        ACTIVE_USERS.set(active_count)
```

---

#### 4.2 Data Pipeline Metrics

**Qué medir**:
- Última ejecución del pipeline
- Filas cargadas
- Errores en carga

**Implementación**:
```python
# infocodest/pipeline/monitoring.py
from prometheus_client import Gauge, Counter

PIPELINE_LAST_RUN = Gauge('pipeline_last_run_timestamp', 'Last pipeline execution')
PIPELINE_ROWS_LOADED = Counter('pipeline_rows_loaded_total', 'Rows loaded')
PIPELINE_ERRORS = Counter('pipeline_errors_total', 'Pipeline errors')

def run_pipeline():
    try:
        rows = load_sonarqube_data()
        PIPELINE_ROWS_LOADED.inc(rows)
        PIPELINE_LAST_RUN.set(time.time())
    except Exception as e:
        PIPELINE_ERRORS.inc()
        raise
```

**Alerta**: Si no se ejecutó pipeline en 25 horas (debe correr diariamente):
```promql
# Alerta si última ejecución > 25 horas
(time() - pipeline_last_run_timestamp) > 90000
```

---

## 🚨 Configuración de Alertas

### Estrategia de Alertas

**Regla de Oro**: Alertar solo sobre síntomas que requieren acción humana.

**NO alertar sobre**:
- ❌ Métricas informativas (logins/día)
- ❌ Problemas que se auto-resuelven (spike temporal)
- ❌ False positives (flaps)

**SÍ alertar sobre**:
- ✅ Downtime (health check failed)
- ✅ Degradación de performance (latency >2s)
- ✅ Recursos críticos (memory >90%, disk >90%)
- ✅ Errores críticos (error rate >1%)

---

### Niveles de Severidad

| Nivel | Descripción | Respuesta | Ejemplo |
|-------|-------------|-----------|---------|
| 🔴 **CRITICAL** | Downtime o pérdida de datos | Inmediata (5 min) | App down, DB caída |
| 🟠 **HIGH** | Performance degradado | 15 minutos | Latency >2s |
| 🟡 **MEDIUM** | Tendencia preocupante | 1 hora | Disk 80% |
| 🔵 **LOW** | Informacional | No requiere acción | Cache hit <95% |

---

### Alertas Recomendadas

#### Alerta #1: Application Down

**Severidad**: 🔴 CRITICAL

**Condición**:
```promql
# Prometheus
up{job="dashboardsonar"} == 0
```

**Acción**: Página on-call inmediatamente → Ver [RUNBOOK.md](../runbooks/RUNBOOK.md#incident-1-aplicación-caída)

**Configuración AlertManager**:
```yaml
# /etc/prometheus/alertmanager.yml
groups:
  - name: dashboardsonar
    interval: 30s
    rules:
      - alert: ApplicationDown
        expr: up{job="dashboardsonar"} == 0
        for: 1m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "Dashboard Sonar is DOWN"
          description: "Application has been down for 1 minute"
          runbook: "https://docs.empresa.com/runbook#app-down"
```

---

#### Alerta #2: High Error Rate

**Severidad**: 🔴 CRITICAL

**Condición**:
```promql
# Tasa de errores 5xx > 1% (últimos 5 min)
(
  rate(http_errors_total{status_code=~"5.."}[5m])
  /
  rate(http_requests_total[5m])
) * 100 > 1
```

**Acción**: Investigar logs → Ver [RUNBOOK.md](../runbooks/RUNBOOK.md#troubleshooting-por-logs)

---

#### Alerta #3: High Latency

**Severidad**: 🟠 HIGH

**Condición**:
```promql
# P95 latency > 2 segundos
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
```

**Acción**: Investigar queries lentas → Ver [RUNBOOK.md](../runbooks/RUNBOOK.md#incident-2-aplicación-lenta)

---

#### Alerta #4: High CPU Usage

**Severidad**: 🟠 HIGH

**Condición**:
```promql
# CPU > 80% por 10 minutos
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
```

**Acción**: Identificar proceso problemático

```bash
# Ver proceso usando más CPU
top -b -n 1 | head -20
```

---

#### Alerta #5: High Memory Usage

**Severidad**: 🟠 HIGH

**Condición**:
```promql
# Memory > 85%
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
```

**Acción**: Reiniciar aplicación si es leak

```bash
sudo systemctl restart dashboardsonar
```

---

#### Alerta #6: Disk Space Critical

**Severidad**: 🔴 CRITICAL

**Condición**:
```promql
# Disk > 90%
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90
```

**Acción**: Limpiar logs y backups antiguos

```bash
# Limpiar logs >30 días
find /var/log/dashboardsonar -name "*.log" -mtime +30 -delete

# Limpiar backups >7 días
find /backups/dashboardsonar -name "*.sql" -mtime +7 -delete
```

---

#### Alerta #7: Database Connections High

**Severidad**: 🟡 MEDIUM

**Condición**:
```promql
# Conexiones > 80 (de max 100)
pg_stat_database_numbackends > 80
```

**Acción**: Investigar leak de conexiones

```sql
-- Ver conexiones idle
SELECT pid, usename, application_name, state, state_change
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < NOW() - INTERVAL '10 minutes';
```

---

#### Alerta #8: Data Pipeline Not Running

**Severidad**: 🟡 MEDIUM

**Condición**:
```promql
# Pipeline no ejecutado en 25 horas
(time() - pipeline_last_run_timestamp) > 90000
```

**Acción**: Ejecutar pipeline manualmente

```bash
cd /path/to/dashboardsonar
./run_data_pipeline.sh Production
```

---

### Configuración de Notificaciones

#### Slack Integration

```yaml
# /etc/prometheus/alertmanager.yml
receivers:
  - name: 'slack-critical'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#incidents-dashboard-sonar'
        title: '🔴 {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

  - name: 'slack-warnings'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#ops-dashboard'
        title: '🟠 {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

route:
  receiver: 'slack-warnings'
  routes:
    - match:
        severity: critical
      receiver: 'slack-critical'
```

---

#### PagerDuty Integration (para on-call)

```yaml
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
        description: '{{ .GroupLabels.alertname }}'
        severity: '{{ .GroupLabels.severity }}'

route:
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true  # También enviar a Slack
```

---

## 📈 Dashboards

### Herramientas

| Herramienta | Uso | Costo |
|-------------|-----|-------|
| **Grafana** | Dashboards personalizados | Gratis (self-hosted) |
| **AWS CloudWatch** | Si estás en AWS | Pay-per-use |
| **Datadog** | All-in-one monitoring | $15/host/mes |
| **New Relic** | APM completo | $99/mes |

**Recomendación**: Empezar con **Grafana + Prometheus** (gratis, open-source).

---

### Dashboard #1: Application Overview

**Propósito**: Vista general del health de la aplicación.

**Panels**:

1. **Request Rate (QPM)**
   - Query: `rate(http_requests_total[5m]) * 60`
   - Visualización: Time series line chart
   - Threshold: Línea roja en 100 QPM

2. **Error Rate (%)**
   - Query: `(rate(http_errors_total[5m]) / rate(http_requests_total[5m])) * 100`
   - Visualización: Gauge (0-5%)
   - Color: Verde <0.1%, Amarillo 0.1-1%, Rojo >1%

3. **P95 Latency**
   - Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
   - Visualización: Time series
   - Threshold: Línea roja en 2s

4. **Active Users**
   - Query: `active_users_total`
   - Visualización: Stat (número grande)

5. **Uptime**
   - Query: `avg_over_time(up{job="dashboardsonar"}[24h]) * 100`
   - Visualización: Gauge (99.5% SLA)

**JSON de Grafana**:
```json
{
  "dashboard": {
    "title": "Dashboard Sonar - Application Overview",
    "panels": [
      {
        "title": "Request Rate (QPM)",
        "targets": [{
          "expr": "rate(http_requests_total[5m]) * 60"
        }],
        "type": "graph"
      }
    ]
  }
}
```

---

### Dashboard #2: Infrastructure

**Propósito**: Monitorear recursos de sistema.

**Panels**:

1. **CPU Usage (%)**
   - Query: `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
   - Threshold: 80%

2. **Memory Usage (%)**
   - Query: `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100`
   - Threshold: 85%

3. **Disk Usage (%)**
   - Query: `(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100`
   - Threshold: 90%

4. **Network I/O**
   - Query: `rate(node_network_receive_bytes_total[5m])`, `rate(node_network_transmit_bytes_total[5m])`

---

### Dashboard #3: Database Performance

**Propósito**: Monitorear PostgreSQL.

**Panels**:

1. **Active Connections**
   - Query: `pg_stat_database_numbackends`
   - Threshold: 80 (de max 100)

2. **Queries per Second**
   - Query: `rate(pg_stat_database_xact_commit[5m])`

3. **Cache Hit Ratio**
   - Query: `pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)`
   - Threshold: <90% = Problema

4. **Slow Queries**
   - Requiere integración con logs
   - Panel con tabla de últimas slow queries

---

### Dashboard #4: Business Metrics

**Propósito**: Métricas de negocio para stakeholders.

**Panels**:

1. **Daily Active Users**
   - Query basada en logs de login

2. **Projects Monitored**
   - Query: `SELECT COUNT(*) FROM proyectos`

3. **Data Freshness** (última carga)
   - Query: `time() - pipeline_last_run_timestamp`
   - Mostrar como "hace X horas"

4. **Top 10 Most Viewed Dashboards**
   - Basado en logs de acceso

---

## 📝 Logs y Análisis

### Estructura de Logs

**Ubicación**:
```
/var/log/dashboardsonar/
├── app.log              # Application logs
├── access.log           # Nginx access logs
├── error.log            # Nginx error logs
└── pipeline.log         # Data pipeline logs
```

---

### Niveles de Log

**Configuración en .env**:
```bash
# Development
LOG_LEVEL=DEBUG

# Production
LOG_LEVEL=INFO
```

**Niveles**:
| Nivel | Cuándo Usar | Ejemplo |
|-------|-------------|---------|
| **DEBUG** | Development | `logger.debug(f"User {user_id} accessed {endpoint}")` |
| **INFO** | Eventos normales | `logger.info("Data pipeline completed: 150 rows")` |
| **WARNING** | Problema menor | `logger.warning("Slow query detected: 1.2s")` |
| **ERROR** | Error recuperable | `logger.error("Failed to load project", exc_info=True)` |
| **CRITICAL** | Error fatal | `logger.critical("Database connection lost")` |

---

### Formato de Logs

**Configuración**:
```python
# infocodest/config/logging.py
import logging

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/dashboardsonar/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'default'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
}
```

---

### Log Rotation

**Configuración con logrotate**:
```bash
# /etc/logrotate.d/dashboardsonar
/var/log/dashboardsonar/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 dashboarduser dashboarduser
    sharedscripts
    postrotate
        systemctl reload dashboardsonar
    endscript
}
```

**Verificar**:
```bash
sudo logrotate -d /etc/logrotate.d/dashboardsonar
```

---

### Análisis de Logs

#### Buscar Errores Recientes

```bash
# Últimos 50 errores
tail -1000 /var/log/dashboardsonar/app.log | grep -E "ERROR|CRITICAL"

# Errores en las últimas 24 horas
grep -E "ERROR|CRITICAL" /var/log/dashboardsonar/app.log | grep "$(date '+%Y-%m-%d')"

# Top 10 errores más comunes
grep "ERROR" /var/log/dashboardsonar/app.log | awk '{print $6}' | sort | uniq -c | sort -rn | head -10
```

---

#### Analizar Latency

```bash
# Queries lentas (>1s)
grep "took [0-9]\{4,\}ms" /var/log/dashboardsonar/app.log

# Estadísticas de latency
awk '/took [0-9]+ms/ {gsub(/took |ms/, ""); print $NF}' /var/log/dashboardsonar/app.log | \
  awk '{sum+=$1; count++; if($1>max) max=$1} END {print "Avg:", sum/count, "Max:", max}'
```

---

#### Analizar Tráfico (Nginx)

```bash
# Requests por minuto
awk '{print $4}' /var/log/nginx/access.log | cut -d: -f1-3 | uniq -c

# Top 10 IPs
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Top 10 endpoints
awk '{print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Response codes
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn
```

---

### Agregación de Logs (Opcional)

Para análisis avanzado, usar herramientas como:

**ELK Stack** (Elasticsearch, Logstash, Kibana):
```yaml
# docker-compose.yml para ELK
version: '3'
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - 9200:9200

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.11.0
    ports:
      - 5601:5601
    depends_on:
      - elasticsearch
```

**Loki + Grafana** (alternativa más ligera):
```bash
# Instalar Loki
wget https://github.com/grafana/loki/releases/download/v2.9.0/loki-linux-amd64.zip
unzip loki-linux-amd64.zip
sudo mv loki-linux-amd64 /usr/local/bin/loki

# Configurar Promtail (agente de logs)
wget https://github.com/grafana/loki/releases/download/v2.9.0/promtail-linux-amd64.zip
unzip promtail-linux-amd64.zip
sudo mv promtail-linux-amd64 /usr/local/bin/promtail
```

---

## 🏥 Health Checks

### Application Health Endpoint

**Implementación**:
```python
# infocodest/routes/health.py
from flask import Blueprint, jsonify
from infocodest.extensions import db
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint para monitoring.
    Retorna 200 si todo está OK, 500 si hay problemas.
    """
    start = time.time()
    health = {
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'checks': {}
    }

    # Check 1: Database connectivity
    try:
        db.session.execute('SELECT 1')
        health['checks']['database'] = 'ok'
    except Exception as e:
        health['status'] = 'unhealthy'
        health['checks']['database'] = f'error: {str(e)}'

    # Check 2: Disk space
    import shutil
    disk = shutil.disk_usage('/')
    disk_percent = (disk.used / disk.total) * 100
    if disk_percent > 90:
        health['status'] = 'degraded'
        health['checks']['disk'] = f'warning: {disk_percent:.1f}% used'
    else:
        health['checks']['disk'] = f'ok: {disk_percent:.1f}% used'

    # Response time
    health['response_time_ms'] = round((time.time() - start) * 1000, 2)

    status_code = 200 if health['status'] == 'healthy' else 500
    return jsonify(health), status_code
```

**Ejemplo de respuesta**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-17T10:30:00Z",
  "checks": {
    "database": "ok",
    "disk": "ok: 45.2% used"
  },
  "response_time_ms": 12.5
}
```

---

### Synthetic Monitoring

**Objetivo**: Simular usuario real para detectar problemas antes que usuarios reales.

**Herramienta**: Uptime Robot (gratis para 50 monitors)

**Configuración**:
```yaml
Monitor Type: HTTP(s)
URL: https://dashboard-sonar.empresa.com/health
Interval: 5 minutes
Alert Contacts: ops-dashboard@empresa.com, Slack webhook
```

**Alternativa self-hosted** (Blackbox Exporter):
```yaml
# /etc/prometheus/blackbox.yml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200]
      method: GET
      fail_if_not_ssl: true
```

```promql
# Prometheus scrape config
scrape_configs:
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://dashboard-sonar.empresa.com/health
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - target_label: __address__
        replacement: localhost:9115
```

---

## 🔧 Herramientas Recomendadas

### Stack Básico (Gratis)

| Componente | Herramienta | Por qué |
|------------|-------------|---------|
| **Metrics** | Prometheus | Industry standard, open-source |
| **Dashboards** | Grafana | Visualizaciones hermosas, gratis |
| **Logs** | Loki | Integra con Grafana, lightweight |
| **Alerting** | AlertManager | Parte de Prometheus, flexible |
| **Uptime** | Uptime Robot | Gratis para 50 monitors |

**Costo total**: $0/mes (self-hosted)

---

### Stack Avanzado (Paid)

| Componente | Herramienta | Costo | Por qué |
|------------|-------------|-------|---------|
| **All-in-one** | Datadog | $15/host/mes | Todo integrado, excelente UX |
| **APM** | New Relic | $99/mes | Tracing, perfilado de código |
| **Logs** | Splunk | $150/GB/mes | Análisis avanzado |
| **Uptime** | Pingdom | $10/mes | Desde múltiples regiones |

**Costo total**: ~$100-300/mes

---

### Stack Cloud Native (AWS)

| Componente | Herramienta | Costo |
|------------|-------------|-------|
| **Metrics** | CloudWatch | $0.30/métrica/mes |
| **Logs** | CloudWatch Logs | $0.50/GB |
| **Dashboards** | CloudWatch Dashboards | $3/dashboard/mes |
| **Alerting** | CloudWatch Alarms | $0.10/alarm/mes |
| **APM** | X-Ray | $5/millón traces |

**Costo estimado**: $20-50/mes para app pequeña

---

## 🔍 Troubleshooting

### Problema: Alertas Falsas (Flapping)

**Síntoma**: Alerta se activa y desactiva constantemente.

**Solución**:
```yaml
# AlertManager - Agregar `for` para esperar antes de alertar
- alert: HighCPU
  expr: cpu_usage > 80
  for: 5m  # Esperar 5 minutos antes de alertar
```

---

### Problema: Demasiadas Alertas

**Síntoma**: On-call recibe 50+ alertas por día.

**Solución**:
1. Subir thresholds (ej: CPU >80% → >90%)
2. Agrupar alertas relacionadas
3. Usar `inhibit_rules` para suprimir alertas secundarias

```yaml
# AlertManager
inhibit_rules:
  - source_match:
      alertname: 'ApplicationDown'
    target_match_re:
      alertname: 'High.*'
    equal: ['instance']
```

---

### Problema: Métricas No Aparecen en Grafana

**Diagnóstico**:
```bash
# 1. Verificar que Prometheus está scrapeando
curl http://localhost:9090/metrics | grep http_requests_total

# 2. Ver targets en Prometheus
curl http://localhost:9090/api/v1/targets

# 3. Verificar que la app expone métricas
curl http://localhost:5000/metrics
```

---

## 📚 Referencias

### Documentación Relacionada

- 🚨 **Runbook**: [RUNBOOK.md](../runbooks/RUNBOOK.md)
- 💾 **Backups**: [BACKUP_RESTORE.md](../backup-recovery/BACKUP_RESTORE.md)
- 🚀 **Deployment**: [DEPLOYMENT_AWS.md](../deployment/DEPLOYMENT_AWS.md)
- 🔒 **Security**: [SECURITY_HARDENING.md](../security/SECURITY_HARDENING.md)

### Recursos Externos

- 📖 [Prometheus Documentation](https://prometheus.io/docs/)
- 📖 [Grafana Tutorials](https://grafana.com/tutorials/)
- 📖 [Google SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- 📖 [AWS CloudWatch Best Practices](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Best_Practice_Recommended_Alarms_AWS_Services.html)

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
**Mantenido por**: Equipo SRE
**Próxima revisión**: Trimestral
