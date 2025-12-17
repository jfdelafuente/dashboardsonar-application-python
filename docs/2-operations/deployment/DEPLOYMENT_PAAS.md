# PaaS Deployment Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Desarrolladores, DevOps
**Plataformas**: Heroku, Railway, Render, Fly.io

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Comparación de Plataformas](#comparación-de-plataformas)
3. [Deployment en Heroku](#deployment-en-heroku)
4. [Deployment en Railway](#deployment-en-railway)
5. [Deployment en Render](#deployment-en-render)
6. [Deployment en Fly.io](#deployment-en-flyio)
7. [Configuración de PostgreSQL](#configuración-de-postgresql)
8. [Variables de Entorno](#variables-de-entorno)
9. [CI/CD Automático](#cicd-automático)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

### ¿Qué es PaaS?

**Platform as a Service (PaaS)** es una plataforma cloud que simplifica deployment eliminando la gestión de servidores.

**Ventajas**:
- ✅ **Simplicidad**: Deploy en minutos con `git push`
- ✅ **Sin gestión de servidores**: No preocuparse por OS, Docker, networking
- ✅ **Auto-scaling**: Escala automáticamente con tráfico
- ✅ **SSL gratis**: HTTPS incluido
- ✅ **CI/CD integrado**: Deploy automático desde Git
- ✅ **Backups automáticos**: PostgreSQL managed con backups

**Desventajas**:
- ❌ **Costo mayor**: $20-50/mes vs $5/mes en VPS
- ❌ **Vendor lock-in**: Difícil migrar entre plataformas
- ❌ **Menos control**: No acceso SSH, configuración limitada

---

### ¿Cuándo usar PaaS?

**Usa PaaS si**:
- Quieres deployment en < 10 minutos
- No tienes experiencia con DevOps/servidores
- Presupuesto permite ($20-100/mes)
- Equipo pequeño (1-5 personas)
- Prototipo o MVP

**NO uses PaaS si**:
- Necesitas control total del servidor
- Presupuesto muy limitado (<$10/mes)
- Aplicación con requisitos muy específicos

---

## 📊 Comparación de Plataformas

| Plataforma | Precio/mes | Free Tier | PostgreSQL | Deploy | SSL | Regions | Dificultad |
|-----------|------------|-----------|------------|--------|-----|---------|------------|
| **Heroku** | $25+ | ❌ (removido 2022) | ✅ $9+/mes | Git push | ✅ Gratis | USA, EU | Baja |
| **Railway** | $20+ | ✅ $5 crédito | ✅ Incluido | Git push | ✅ Gratis | USA, EU | Muy baja |
| **Render** | $25+ | ✅ Limitado | ✅ $7+/mes | Git push | ✅ Gratis | USA, EU, Asia | Baja |
| **Fly.io** | $15+ | ✅ Limitado | ✅ Incluido | Fly CLI | ✅ Gratis | Global (30+) | Media |

**Recomendación para Dashboard Sonar**:
- **MVP/Prototipo**: Railway (free tier + fácil)
- **Producción pequeña**: Render (buen balance precio/features)
- **Producción enterprise**: Heroku (mature, soporte)

---

## 🚀 Deployment en Heroku

### Prerequisitos

```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Verificar
heroku --version
```

---

### Paso 1: Crear aplicación

```bash
cd /ruta/dashboardsonar-application-python

# Crear app
heroku create dashboardsonar-prod

# O con región específica:
heroku create dashboardsonar-prod --region eu
```

---

### Paso 2: Agregar PostgreSQL

```bash
# Agregar addon PostgreSQL (plan Mini: $5/mes)
heroku addons:create heroku-postgresql:mini --app dashboardsonar-prod

# Verificar DATABASE_URL se configuró automáticamente
heroku config --app dashboardsonar-prod
```

**Planes PostgreSQL**:
- **Mini**: $5/mes, 1M rows, 1 GB RAM
- **Basic**: $9/mes, 10M rows, 1 GB RAM (recomendado)
- **Standard**: $50+/mes, 64M rows, 4 GB RAM

---

### Paso 3: Configurar variables de entorno

```bash
# SECRET_KEY (generar uno fuerte)
heroku config:set SECRET_KEY="$(openssl rand -hex 32)" --app dashboardsonar-prod

# Configuración Flask
heroku config:set FLASK_ENV=production --app dashboardsonar-prod
heroku config:set FLASK_DEBUG=0 --app dashboardsonar-prod

# Logging
heroku config:set LOG_LEVEL=INFO --app dashboardsonar-prod

# Gunicorn (workers dinámicos basados en dynos)
heroku config:set GUNICORN_WORKERS=4 --app dashboardsonar-prod
heroku config:set GUNICORN_WORKER_CLASS=gevent --app dashboardsonar-prod
heroku config:set GUNICORN_TIMEOUT=120 --app dashboardsonar-prod

# Verificar
heroku config --app dashboardsonar-prod
```

---

### Paso 4: Crear archivos de configuración

**`Procfile`** (en root del proyecto):
```
web: gunicorn "infocodest:create_app()" --workers=${GUNICORN_WORKERS:-4} --worker-class=${GUNICORN_WORKER_CLASS:-gevent} --timeout=${GUNICORN_TIMEOUT:-120} --bind 0.0.0.0:$PORT
release: flask db upgrade
```

**Explicación**:
- `web`: Proceso principal (Gunicorn)
- `release`: Comando que se ejecuta antes de deploy (migraciones DB)

**`runtime.txt`** (especificar versión Python):
```
python-3.11.9
```

**`requirements.txt`** (debe estar actualizado):
```bash
pip freeze > requirements.txt
```

---

### Paso 5: Deploy

```bash
# Agregar remote de Heroku (si no se hizo antes)
heroku git:remote --app dashboardsonar-prod

# Deploy
git push heroku main

# O si tu branch principal es develop:
git push heroku develop:main
```

**Monitorear deploy**:
```bash
heroku logs --tail --app dashboardsonar-prod
```

---

### Paso 6: Escalar dynos

**Heroku usa "dynos" (contenedores)**:

```bash
# Ver dynos actuales
heroku ps --app dashboardsonar-prod

# Escalar web dyno (Basic: $7/mes, Standard-1X: $25/mes)
heroku ps:scale web=1:Standard-1X --app dashboardsonar-prod

# Para alta carga, escalar horizontal:
heroku ps:scale web=3:Standard-2X --app dashboardsonar-prod
```

**Tipos de dynos**:
- **Basic**: $7/mes, 512 MB RAM, no duerme
- **Standard-1X**: $25/mes, 512 MB RAM
- **Standard-2X**: $50/mes, 1 GB RAM (recomendado)

---

### Paso 7: Configurar dominio custom + SSL

```bash
# Agregar dominio
heroku domains:add dashboard.tudominio.com --app dashboardsonar-prod

# Heroku te dará un DNS target (ej: fierce-mountain-123.herokudns.com)
# Crear registro CNAME en tu DNS:
# dashboard.tudominio.com -> fierce-mountain-123.herokudns.com

# SSL es automático (Let's Encrypt)
heroku certs:auto:enable --app dashboardsonar-prod
```

---

### Monitoreo y Logs

```bash
# Ver logs en tiempo real
heroku logs --tail --app dashboardsonar-prod

# Ver logs de últimas 1500 líneas
heroku logs -n 1500 --app dashboardsonar-prod

# Agregar addon de logs (Papertrail: gratis hasta 50MB/mes)
heroku addons:create papertrail --app dashboardsonar-prod

# Acceder a Papertrail
heroku addons:open papertrail --app dashboardsonar-prod
```

---

## 🚄 Deployment en Railway

**Railway** es más moderno y tiene free tier generoso.

### Paso 1: Crear cuenta y proyecto

1. Ve a https://railway.app/
2. Sign up con GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Selecciona `dashboardsonar-application-python`

---

### Paso 2: Agregar PostgreSQL

1. En el proyecto, click "+ New"
2. Selecciona "Database" → "PostgreSQL"
3. Railway creará automáticamente `DATABASE_URL` como variable

---

### Paso 3: Configurar variables de entorno

En Railway dashboard → "Variables" tab:

```env
SECRET_KEY=tu-secret-key-generado
FLASK_ENV=production
FLASK_DEBUG=0
LOG_LEVEL=INFO
GUNICORN_WORKERS=4
GUNICORN_WORKER_CLASS=gevent
GUNICORN_TIMEOUT=120
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Railway lo inyecta automáticamente
```

**Generar SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

### Paso 4: Configurar build

Railway detecta automáticamente Python, pero puedes personalizar:

**`railway.toml`** (opcional, en root):
```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "gunicorn 'infocodest:create_app()' --workers=4 --worker-class=gevent --timeout=120 --bind 0.0.0.0:$PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 5
```

**Alternativa con `Procfile`**:
```
web: gunicorn "infocodest:create_app()" --workers=4 --worker-class=gevent --timeout=120 --bind 0.0.0.0:$PORT
release: flask db upgrade
```

---

### Paso 5: Deploy

**Railway hace deploy automático** con cada `git push` a GitHub.

1. Commit cambios a GitHub
2. Railway detecta y despliega automáticamente
3. Ver logs en Railway dashboard

**Verificar deployment**:
```bash
# Railway genera URL automático:
# https://dashboardsonar-production.up.railway.app
```

---

### Paso 6: Dominio custom

1. Railway dashboard → "Settings" → "Domains"
2. Click "Custom Domain"
3. Ingresa `dashboard.tudominio.com`
4. Configura CNAME en tu DNS apuntando a Railway
5. SSL es automático

---

### Pricing Railway

**Free tier**:
- $5 crédito gratis/mes
- Suficiente para apps pequeñas

**Pro plan** ($20/mes):
- $20 crédito incluido
- Luego usage-based (~$0.000231/GB-hr)

**Estimación Dashboard Sonar**:
- App (512 MB): ~$8/mes
- PostgreSQL (1 GB): ~$16/mes
- **Total**: ~$24/mes

---

## 🎨 Deployment en Render

### Paso 1: Crear cuenta

1. https://render.com/
2. Sign up con GitHub

---

### Paso 2: Crear PostgreSQL

1. Dashboard → "New +" → "PostgreSQL"
2. Configurar:
   - Name: `dashboardsonar-db`
   - Database: `dashboardsonar`
   - User: `dashboard_user`
   - Region: Oregon (USA) o Frankfurt (EU)
   - Plan: **Starter** ($7/mes) o **Standard** ($20/mes)
3. Click "Create Database"
4. Copiar **Internal Database URL** (para conectar desde app en Render)

---

### Paso 3: Crear Web Service

1. Dashboard → "New +" → "Web Service"
2. Conectar GitHub repo: `dashboardsonar-application-python`
3. Configurar:
   - **Name**: `dashboardsonar-app`
   - **Region**: Mismo que PostgreSQL
   - **Branch**: `main`
   - **Root Directory**: `.` (vacío)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "infocodest:create_app()" --workers=4 --worker-class=gevent --timeout=120 --bind=0.0.0.0:$PORT`
   - **Plan**: **Starter** ($7/mes) o **Standard** ($25/mes)

---

### Paso 4: Variables de entorno

En "Environment" tab:

```env
DATABASE_URL=<copiar Internal Database URL de PostgreSQL>
SECRET_KEY=<generar con: openssl rand -hex 32>
FLASK_ENV=production
FLASK_DEBUG=0
LOG_LEVEL=INFO
GUNICORN_WORKERS=4
GUNICORN_WORKER_CLASS=gevent
GUNICORN_TIMEOUT=120
PYTHON_VERSION=3.11.9
```

---

### Paso 5: Deploy

Render hace **auto-deploy** en cada push a GitHub.

**Monitorear**:
- Logs: Render dashboard → "Logs" tab
- Eventos: "Events" tab

**URL generado**:
```
https://dashboardsonar-app.onrender.com
```

---

### Paso 6: Dominio custom + SSL

1. Render dashboard → "Settings" → "Custom Domain"
2. Agregar `dashboard.tudominio.com`
3. Configurar CNAME en DNS → apuntar a Render
4. SSL automático con Let's Encrypt

---

### Render Pricing

| Plan | Precio/mes | CPU | RAM | Auto-scale |
|------|------------|-----|-----|------------|
| **Starter** | $7 | 0.5 CPU | 512 MB | ❌ |
| **Standard** | $25 | 1 CPU | 2 GB | ✅ |
| **Pro** | $85 | 2 CPU | 4 GB | ✅ |

**Estimación Dashboard Sonar**:
- App: $25/mes (Standard)
- PostgreSQL: $7/mes (Starter)
- **Total**: $32/mes

---

## ✈️ Deployment en Fly.io

Fly.io es moderno, con cobertura global (30+ regiones).

### Paso 1: Instalar Fly CLI

```bash
# Linux/macOS
curl -L https://fly.io/install.sh | sh

# Agregar al PATH
echo 'export PATH="$HOME/.fly/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verificar
fly version
```

---

### Paso 2: Login y crear app

```bash
fly auth login

cd /ruta/dashboardsonar-application-python

# Crear app (interactivo)
fly launch

# Responde:
# - App name: dashboardsonar-prod
# - Region: lhr (London) o fra (Frankfurt)
# - PostgreSQL: Yes
# - Plan: Development (gratis) o Dedicated CPU ($1.94/mes)
```

Esto creará `fly.toml`.

---

### Paso 3: Configurar `fly.toml`

**`fly.toml`**:
```toml
app = "dashboardsonar-prod"
primary_region = "lhr"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  FLASK_ENV = "production"
  FLASK_DEBUG = "0"
  LOG_LEVEL = "INFO"
  GUNICORN_WORKERS = "4"
  GUNICORN_WORKER_CLASS = "gevent"
  GUNICORN_TIMEOUT = "120"
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[services]]
  internal_port = 8080
  protocol = "tcp"
  auto_stop_machines = true
  auto_start_machines = true

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [services.concurrency]
    type = "connections"
    hard_limit = 1000
    soft_limit = 500

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

---

### Paso 4: PostgreSQL

```bash
# Crear PostgreSQL cluster
fly postgres create --name dashboardsonar-db --region lhr

# Conectar app a PostgreSQL
fly postgres attach dashboardsonar-db --app dashboardsonar-prod
```

Esto agrega automáticamente `DATABASE_URL`.

---

### Paso 5: Secrets (variables sensibles)

```bash
# SECRET_KEY
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" --app dashboardsonar-prod

# Verificar secrets
fly secrets list --app dashboardsonar-prod
```

---

### Paso 6: Deploy

```bash
fly deploy --app dashboardsonar-prod

# Monitorear logs
fly logs --app dashboardsonar-prod

# Ver status
fly status --app dashboardsonar-prod
```

**URL**:
```
https://dashboardsonar-prod.fly.dev
```

---

### Paso 7: Dominio custom

```bash
# Agregar certificado SSL
fly certs create dashboard.tudominio.com --app dashboardsonar-prod

# Fly te dirá qué registros DNS crear (A y AAAA)
# Ejemplo:
# A     dashboard.tudominio.com -> 66.241.124.100
# AAAA  dashboard.tudominio.com -> 2a09:8280:1::1
```

---

### Fly.io Pricing

**Free tier** (Hobby):
- 3 shared-cpu-1x VMs (256 MB RAM)
- 3 GB persistent storage
- 160 GB outbound transfer

**Paid** (Pay as you go):
- Shared CPU: $1.94/mes por VM (256 MB)
- Dedicated CPU: $23/mes por VM (2 GB)
- PostgreSQL: $0.02/GB-hour (~$15/mes por 1 GB)

---

## ⚙️ Configuración de PostgreSQL

### Backups automáticos

**Heroku**:
```bash
heroku pg:backups:schedule DATABASE_URL --at '02:00 America/New_York' --app dashboardsonar-prod
```

**Railway**: Backups automáticos incluidos (retención 7 días)

**Render**: Backups automáticos incluidos (retención 7 días en Starter, 30 en Standard)

**Fly.io**:
```bash
fly volumes snapshot create <volume-id> --app dashboardsonar-db
```

---

### Conexión local a PostgreSQL

**Heroku**:
```bash
heroku pg:psql --app dashboardsonar-prod
```

**Railway**:
```bash
# Copiar DATABASE_URL de dashboard
psql "postgresql://user:pass@host:port/db"
```

**Render**:
```bash
# Usar External Database URL (dashboard)
psql "postgresql://user:pass@host:port/db"
```

---

## 🔄 CI/CD Automático

Todas las plataformas PaaS soportan **auto-deploy** desde GitHub.

### GitHub Actions + Heroku

**`.github/workflows/deploy-heroku.yml`**:
```yaml
name: Deploy to Heroku

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.14
      with:
        heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
        heroku_app_name: "dashboardsonar-prod"
        heroku_email: "tu-email@empresa.com"
```

**Secrets en GitHub**:
- `HEROKU_API_KEY`: Obtener de https://dashboard.heroku.com/account

---

## 🔧 Troubleshooting

### App no arranca (H10 error en Heroku)

```bash
# Ver logs
heroku logs --tail --app dashboardsonar-prod

# Verificar Procfile existe y es correcto
cat Procfile

# Verificar workers
heroku ps --app dashboardsonar-prod
```

**Causas comunes**:
- `Procfile` con typos
- `PORT` no configurado (Heroku/Railway usan $PORT variable)
- Dependencias faltantes en `requirements.txt`

---

### DATABASE_URL no funciona

```bash
# Verificar DATABASE_URL está configurado
heroku config:get DATABASE_URL --app dashboardsonar-prod

# Probar conexión manual
heroku pg:psql --app dashboardsonar-prod
```

---

### Build falla

**Solución**:
```bash
# Verificar requirements.txt actualizado
pip freeze > requirements.txt

# Especificar versión Python en runtime.txt
echo "python-3.11.9" > runtime.txt

# Commit y redeploy
git add requirements.txt runtime.txt
git commit -m "fix: update dependencies"
git push heroku main
```

---

## 📚 Recursos Adicionales

**Documentación oficial**:
- [Heroku Python Docs](https://devcenter.heroku.com/categories/python-support)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs/)

**Comparadores de precios**:
- [PaaS Comparison](https://www.paasify.it/)

---

**Última actualización**: Diciembre 2025
**Mantenido por**: Equipo DevOps
**Soporte**: devops@empresa.com
