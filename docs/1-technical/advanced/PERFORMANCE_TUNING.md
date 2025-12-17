# Performance Tuning Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Desarrolladores, DBAs, DevOps, SREs
**Objetivo**: Optimizar performance para >1000 repositorios y >100 usuarios concurrentes

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Database Optimization](#database-optimization)
3. [Application Optimization](#application-optimization)
4. [Caching Strategies](#caching-strategies)
5. [Gunicorn Tuning](#gunicorn-tuning)
6. [Frontend Optimization](#frontend-optimization)
7. [Monitoring Performance](#monitoring-performance)

---

## 🎯 Introducción

### Performance Goals

| Métrica | Objetivo | Crítico Si |
|---------|----------|------------|
| **Page Load Time** | < 1s (p95) | > 3s |
| **API Response Time** | < 500ms (p95) | > 2s |
| **Database Query Time** | < 100ms (p95) | > 1s |
| **Concurrent Users** | 100+ sin degradación | Saturación en <50 |
| **Memory Usage** | < 2GB (Gunicorn) | > 4GB |
| **CPU Usage** | < 60% promedio | > 80% sostenido |

### Metodología de Optimización

1. **Measure First** - Profiling antes de optimizar
2. **Identify Bottlenecks** - 80/20 rule (80% impacto en 20% código)
3. **Optimize** - Una cosa a la vez
4. **Measure Again** - Verificar mejora
5. **Repeat** - Hasta alcanzar objetivos

---

## 🗄️ Database Optimization

### 1. Query Optimization

#### Problema: N+1 Queries

**❌ LENTO** (N+1 problema):
```python
# Esto genera 1 query para metricas + N queries para proveedores
metricas = Metrica.query.all()
for metrica in metricas:
    proveedor = Proveedor.query.filter_by(aplicacion=metrica.aplicacion).first()
    print(f"{metrica.repo}: {proveedor.proveedor}")
```

**✅ RÁPIDO** (1 query con JOIN):
```python
from infocodest.models.metricas import Metrica
from infocodest.models.proveedor import Proveedor

# 1 query con JOIN
results = db.session.query(Metrica, Proveedor).join(
    Proveedor,
    Metrica.aplicacion == Proveedor.aplicacion
).all()

for metrica, proveedor in results:
    print(f"{metrica.repo}: {proveedor.proveedor}")
```

**Mejora**: De ~500ms a ~50ms (10x más rápido)

---

#### Problema: SELECT * en Queries Grandes

**❌ LENTO** (fetch todas las columnas):
```python
# Trae 37 columnas por cada fila
metricas = Metrica.query.all()
```

**✅ RÁPIDO** (fetch solo lo necesario):
```python
# Solo las columnas que necesitas
metricas = db.session.query(
    Metrica.id,
    Metrica.repo,
    Metrica.aplicacion,
    Metrica.bugs,
    Metrica.coverage
).all()
```

**Mejora**: De ~200KB a ~50KB de datos transferidos (4x menos)

---

#### Problema: Queries sin Límite

**❌ LENTO** (fetch miles de registros):
```python
# En producción, puede retornar 15,000 registros
historico = Historico.query.all()
```

**✅ RÁPIDO** (paginación):
```python
# Solo 100 registros por página
page = 1
per_page = 100
historico = Historico.query.paginate(page=page, per_page=per_page)

# O con limit/offset
historico = Historico.query.limit(100).offset((page-1) * 100).all()
```

**Mejora**: De ~2s a ~100ms (20x más rápido)

---

### 2. Índices Críticos

#### Verificar Uso de Índices

```sql
-- PostgreSQL: Ver plan de ejecución
EXPLAIN ANALYZE
SELECT * FROM metricas
WHERE aplicacion = 'my-app' AND bugs > 10;

-- Si ves "Seq Scan" en lugar de "Index Scan", necesitas un índice
```

#### Crear Índices Compuestos

**Problema**: Queries frecuentes con múltiples condiciones.

```python
# Query común en dashboard
metricas = Metrica.query.filter(
    Metrica.aplicacion == 'my-app',
    Metrica.bugs > 10
).order_by(Metrica.bugs.desc()).all()
```

**Solución**: Índice compuesto

```sql
-- Crear índice compuesto para este patrón
CREATE INDEX idx_metricas_app_bugs ON metricas (aplicacion, bugs DESC);

-- Verificar uso
EXPLAIN ANALYZE
SELECT * FROM metricas
WHERE aplicacion = 'my-app' AND bugs > 10
ORDER BY bugs DESC;

-- Debe mostrar: "Index Scan using idx_metricas_app_bugs"
```

**Mejora**: De ~500ms a ~20ms (25x más rápido)

---

#### Índices Recomendados

```sql
-- Para filtros en dashboard
CREATE INDEX idx_metricas_app_bugs ON metricas (aplicacion, bugs);
CREATE INDEX idx_metricas_app_coverage ON metricas (aplicacion, coverage);
CREATE INDEX idx_metricas_app_security ON metricas (aplicacion, security_rating);

-- Para trending (histórico por fecha)
CREATE INDEX idx_historico_repo_fecha ON historico (repo, fecha DESC);
CREATE INDEX idx_historico_app_fecha ON historico (aplicacion, fecha DESC);

-- Para agregaciones
CREATE INDEX idx_metricas_app_fecha ON metricas (aplicacion, fecha);

-- Para búsquedas por proveedor
CREATE INDEX idx_proveedor_proveedor ON proveedor (proveedor, aplicacion);
```

---

### 3. Connection Pooling

#### Configuración Óptima

```python
# infocodest/config.py
class ProductionConfig:
    # PostgreSQL Connection Pool
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,           # Conexiones normales
        'max_overflow': 10,        # Conexiones extra si se satura
        'pool_recycle': 3600,      # Reciclar conexiones cada 1h
        'pool_pre_ping': True,     # Verificar conexión antes de usar
        'pool_timeout': 30,        # Timeout si no hay conexiones
        'echo': False,             # Disable SQL echo (performance)
    }

    # Disable modification tracking (performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

**Dimensionamiento del Pool**:
```
pool_size = (num_gunicorn_workers * 2) + 5
          = (4 workers * 2) + 5
          = 13 → redondear a 20 para headroom
```

---

### 4. Database Statistics

#### Actualizar Estadísticas (PostgreSQL)

```sql
-- Actualizar estadísticas para query planner
ANALYZE metricas;
ANALYZE historico;

-- O todas las tablas
ANALYZE;

-- Programar en cron (diario a las 2 AM)
0 2 * * * psql -U postgres -d dashboardsonar -c "ANALYZE;"
```

#### Verificar Fragmentación de Índices

```sql
-- Ver índices fragmentados
SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Rebuild si es necesario
REINDEX INDEX idx_metricas_app_bugs;

-- O toda la tabla
REINDEX TABLE metricas;
```

---

### 5. Query Caching (Redis)

**Implementación con Flask-Caching**:

```python
# requirements.txt
flask-caching==2.1.0
redis==5.0.0

# infocodest/__init__.py
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 0,
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutos
})
cache.init_app(app)

# infocodest/routes/dashboard.py
from infocodest import cache

@app.route('/dashboard')
@cache.cached(timeout=300, key_prefix='dashboard_home')
def dashboard():
    # Esta query solo se ejecuta cada 5 minutos
    metricas = Metrica.query.all()
    return render_template('dashboard.html', metricas=metricas)

# Invalidar cache cuando se actualizan datos
@app.route('/update_metrics', methods=['POST'])
def update_metrics():
    # Actualizar datos
    load_sonarqube_data()

    # Invalidar cache
    cache.delete('dashboard_home')

    return jsonify({'success': True})
```

**Mejora**: De ~500ms a ~10ms (50x más rápido para requests cacheadas)

---

## 🚀 Application Optimization

### 1. Lazy Loading vs Eager Loading

#### Problema: N+1 Queries con Relaciones

**❌ LENTO** (lazy loading):
```python
# Genera N queries (1 por cada aplicacion)
metricas = Metrica.query.all()
for metrica in metricas:
    # Lazy load - query adicional
    stats = Stat.query.filter_by(aplicacion=metrica.aplicacion).first()
```

**✅ RÁPIDO** (eager loading):
```python
from sqlalchemy.orm import joinedload

# Eager load - 1 query con JOIN
metricas = Metrica.query.options(
    joinedload(Metrica.stats)  # Si tuvieras relationship definida
).all()

# O hacer query compuesta
results = db.session.query(Metrica, Stat).join(
    Stat, Metrica.aplicacion == Stat.aplicacion
).all()
```

---

### 2. Bulk Operations

#### Problema: Insertar 1000 Registros Uno por Uno

**❌ LENTO** (1000 INSERT statements):
```python
for metric_data in metrics_list:  # 1000 items
    metrica = Metrica(**metric_data)
    db.session.add(metrica)
    db.session.commit()  # ❌ Commit en cada iteración
```
**Tiempo**: ~30 segundos

**✅ RÁPIDO** (bulk insert):
```python
# Opción 1: Add all + 1 commit
for metric_data in metrics_list:
    metrica = Metrica(**metric_data)
    db.session.add(metrica)

db.session.commit()  # 1 solo commit
```
**Tiempo**: ~2 segundos (15x más rápido)

**✅ MÁS RÁPIDO** (bulk_insert_mappings):
```python
# Opción 2: Bulk insert mappings (sin ORM overhead)
db.session.bulk_insert_mappings(Metrica, metrics_list)
db.session.commit()
```
**Tiempo**: ~500ms (60x más rápido)

---

### 3. Generator Patterns

#### Problema: Procesar 50,000 Registros en Memoria

**❌ LENTO** (carga todo en memoria - 500MB RAM):
```python
# Carga todos los 50,000 registros
historico = Historico.query.all()

for h in historico:
    process(h)
```

**✅ RÁPIDO** (generator - 50MB RAM):
```python
# Yield batch de 1000 registros
def yield_in_chunks(query, chunk_size=1000):
    offset = 0
    while True:
        chunk = query.limit(chunk_size).offset(offset).all()
        if not chunk:
            break
        yield chunk
        offset += chunk_size

# Procesar en batches
query = Historico.query
for chunk in yield_in_chunks(query):
    for h in chunk:
        process(h)
    db.session.commit()  # Commit por batch
```

**Mejora**: De 500MB RAM a 50MB RAM (10x menos memoria)

---

### 4. Response Compression

**Implementar Gzip en Flask**:

```python
# requirements.txt
flask-compress==1.14

# infocodest/__init__.py
from flask_compress import Compress

compress = Compress()
compress.init_app(app)

# Auto-compress respuestas > 500 bytes
app.config['COMPRESS_MIN_SIZE'] = 500
app.config['COMPRESS_LEVEL'] = 6  # Balance entre CPU y compresión
```

**Mejora**: De ~200KB a ~30KB (JSON responses - 6x más pequeño)

---

## 💾 Caching Strategies

### 1. Application-Level Caching

#### Caché de Dashboard Home

```python
from flask_caching import Cache
from functools import wraps

cache = Cache()

def cache_with_user_context(timeout=300):
    """Cache con contexto de usuario"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f'view_{f.__name__}_{current_user.id}'
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

@app.route('/dashboard')
@login_required
@cache_with_user_context(timeout=300)
def dashboard():
    metricas = Metrica.query.all()
    return render_template('dashboard.html', metricas=metricas)
```

---

#### Caché de Cálculos Costosos

```python
@cache.memoize(timeout=600)  # 10 minutos
def calculate_app_statistics(aplicacion):
    """Cálculo costoso de estadísticas"""
    metricas = Metrica.query.filter_by(aplicacion=aplicacion).all()

    return {
        'total_repos': len(metricas),
        'avg_bugs': sum(m.bugs for m in metricas) / len(metricas),
        'avg_coverage': sum(m.coverage for m in metricas) / len(metricas),
        # ... más cálculos complejos
    }

# Usar en route
@app.route('/app/<aplicacion>')
def app_detail(aplicacion):
    stats = calculate_app_statistics(aplicacion)  # Cacheado
    return render_template('app.html', stats=stats)
```

---

### 2. Browser Caching

**Configurar headers de caché**:

```python
from flask import make_response
from datetime import datetime, timedelta

@app.after_request
def add_cache_headers(response):
    # Cache estático por 1 año
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 31536000  # 1 año
        response.cache_control.public = True

    # Cache API por 5 minutos
    elif request.path.startswith('/api/'):
        response.cache_control.max_age = 300  # 5 min
        response.cache_control.private = True

    # No cache para páginas HTML
    else:
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True

    return response
```

---

### 3. CDN para Assets Estáticos

**Offload assets a CDN** (CloudFront, Cloudflare):

```python
# infocodest/config.py
class ProductionConfig:
    # Usar CDN para static files
    STATIC_URL = 'https://cdn.dashboard-sonar.com/static/'

# En templates
<link rel="stylesheet" href="{{ config.STATIC_URL }}css/style.css">
<script src="{{ config.STATIC_URL }}js/app.js"></script>
```

**Mejora**: De ~500ms TTFB a ~50ms TTFB (10x más rápido)

---

## ⚙️ Gunicorn Tuning

### 1. Worker Configuration

**Calcular workers óptimos**:

```bash
# Fórmula: (2 x NUM_CORES) + 1
# Ejemplo: servidor con 4 cores
workers = (2 x 4) + 1 = 9

# En gunicorn.conf.py o systemd service
gunicorn \
  --workers 9 \
  --worker-class sync \
  --worker-connections 1000 \
  --bind 0.0.0.0:5000 \
  "infocodest:create_app()"
```

**Worker types**:

| Type | Cuándo Usar | Concurrency |
|------|-------------|-------------|
| **sync** | CPU-bound tasks (default) | 1 request/worker |
| **gevent** | I/O-bound (DB, APIs) | 1000+ requests/worker |
| **eventlet** | Similar a gevent | 1000+ requests/worker |

**Para Dashboard Sonar** (I/O-bound por DB queries):

```bash
# Instalar gevent
pip install gevent

# Usar gevent workers
gunicorn \
  --workers 4 \
  --worker-class gevent \
  --worker-connections 1000 \
  --bind 0.0.0.0:5000 \
  "infocodest:create_app()"
```

**Mejora**: De ~50 usuarios concurrentes a ~200 usuarios (4x más)

---

### 2. Timeout Configuration

```bash
gunicorn \
  --timeout 30 \          # Request timeout (default 30s)
  --graceful-timeout 30 \ # Tiempo para finalizar gracefully
  --keep-alive 5 \        # Keep-alive connections
  "infocodest:create_app()"
```

---

### 3. Preloading Application

```bash
# Preload app antes de fork workers (ahorra memoria)
gunicorn \
  --preload \
  --workers 4 \
  "infocodest:create_app()"
```

**Trade-off**:
- ✅ Menos memoria (app cargada 1 vez)
- ❌ Reload más lento (debe reiniciar todos los workers)

---

### 4. Complete Gunicorn Config

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 30
keepalive = 5

# Restart workers after N requests (prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '/var/log/dashboardsonar/access.log'
errorlog = '/var/log/dashboardsonar/error.log'
loglevel = 'info'

# Process naming
proc_name = 'dashboardsonar'

# Preload app
preload_app = True
```

**Ejecutar**:
```bash
gunicorn -c gunicorn.conf.py "infocodest:create_app()"
```

---

## 🎨 Frontend Optimization

### 1. Minify & Bundle Assets

**Instalar herramientas**:

```bash
npm install --save-dev webpack webpack-cli terser-webpack-plugin
```

**webpack.config.js**:

```javascript
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
  mode: 'production',
  entry: './static/js/app.js',
  output: {
    filename: 'app.min.js',
    path: __dirname + '/static/dist'
  },
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin()]
  }
};
```

**Mejora**: De ~300KB JS a ~80KB (4x más pequeño)

---

### 2. Lazy Load Images

```html
<!-- Lazy load imágenes off-screen -->
<img src="placeholder.jpg"
     data-src="large-image.jpg"
     loading="lazy"
     alt="Dashboard">

<script>
document.addEventListener("DOMContentLoaded", function() {
  let lazyImages = [].slice.call(document.querySelectorAll("img[data-src]"));

  if ("IntersectionObserver" in window) {
    let lazyImageObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          let lazyImage = entry.target;
          lazyImage.src = lazyImage.dataset.src;
          lazyImageObserver.unobserve(lazyImage);
        }
      });
    });

    lazyImages.forEach(function(lazyImage) {
      lazyImageObserver.observe(lazyImage);
    });
  }
});
</script>
```

---

### 3. Debounce Search Input

```javascript
// Evitar queries en cada keystroke
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Aplicar a search
const searchInput = document.getElementById('search');
const debouncedSearch = debounce(function(query) {
  fetch(`/api/search?q=${query}`)
    .then(r => r.json())
    .then(data => updateResults(data));
}, 300);  // Esperar 300ms después del último keystroke

searchInput.addEventListener('input', (e) => {
  debouncedSearch(e.target.value);
});
```

**Mejora**: De ~50 requests/segundo a ~3 requests/segundo (17x menos)

---

## 📈 Monitoring Performance

### 1. Application Profiling

**Flask-Profiler**:

```python
# requirements.txt
flask-profiler==1.8.1

# infocodest/__init__.py
from flask_profiler import Profiler

app.config['flask_profiler'] = {
    'enabled': True,
    'storage': {
        'engine': 'sqlite',
        'FILE': '/tmp/flask_profiler.sql'
    },
    'basicAuth': {
        'enabled': True,
        'username': 'admin',
        'password': 'admin'
    },
    'ignore': ['^/static/.*']
}
profiler = Profiler()
profiler.init_app(app)

# Acceder a: http://localhost:5000/flask-profiler/
```

---

### 2. Database Query Profiling

**SQLAlchemy Profiling**:

```python
# infocodest/config.py
class DevelopmentConfig:
    SQLALCHEMY_ECHO = True  # Log all SQL queries

# O con profiler
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging
import time

logging.basicConfig()
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.1:  # Log slow queries (>100ms)
        logger.warning(f"SLOW QUERY ({total:.2f}s): {statement}")
```

---

### 3. Load Testing

**Usando Locust**:

```python
# locustfile.py
from locust import HttpUser, task, between

class DashboardUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_dashboard(self):
        self.client.get("/dashboard")

    @task(2)
    def view_app(self):
        self.client.get("/app/my-application")

    @task(1)
    def search(self):
        self.client.get("/search?q=bugs")

# Ejecutar
# locust -f locustfile.py --host=http://localhost:5000
```

**Objetivo**: Simular 100 usuarios concurrentes, verificar que p95 latency < 1s.

---

## 📚 Referencias

### Documentación Relacionada

- **[DATABASE_SCHEMA.md](../architecture/DATABASE_SCHEMA.md)** - Esquema de BD
- **[ARCHITECTURE.md](../architecture/ARCHITECTURE.md)** - Arquitectura general
- **[MONITORING_GUIDE.md](../../2-operations/monitoring/MONITORING_GUIDE.md)** - Monitoring

### Recursos Externos

- [PostgreSQL Performance Tips](https://www.postgresql.org/docs/current/performance-tips.html)
- [SQLAlchemy Performance](https://docs.sqlalchemy.org/en/20/faq/performance.html)
- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/settings.html)
- [Flask Caching](https://flask-caching.readthedocs.io/)

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
**Mantenido por**: Equipo de Desarrollo
