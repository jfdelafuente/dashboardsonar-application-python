# GCP Deployment Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, Cloud Engineers
**Cloud Provider**: Google Cloud Platform (GCP)

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Prerequisitos](#prerequisitos)
3. [Arquitecturas de Deployment](#arquitecturas-de-deployment)
4. [Opción 1: Compute Engine + Cloud SQL](#opción-1-compute-engine--cloud-sql-recomendado)
5. [Opción 2: Cloud Run (Serverless)](#opción-2-cloud-run-serverless)
6. [Opción 3: Google Kubernetes Engine (GKE)](#opción-3-google-kubernetes-engine-gke)
7. [Cloud SQL Configuration](#cloud-sql-configuration)
8. [Load Balancer Setup](#load-balancer-setup)
9. [Cloud CDN y SSL](#cloud-cdn-y-ssl)
10. [Secret Manager](#secret-manager)
11. [Monitoring con Cloud Operations](#monitoring-con-cloud-operations)
12. [CI/CD con Cloud Build](#cicd-con-cloud-build)
13. [Cost Optimization](#cost-optimization)

---

## 🎯 Introducción

### ¿Por qué Google Cloud Platform?

**Ventajas**:
- ✅ **Performance**: Red global de Google con latencia ultra-baja
- ✅ **Serverless options**: Cloud Run para auto-scaling sin gestión de VMs
- ✅ **Managed services**: Cloud SQL, GKE totalmente gestionados
- ✅ **Free tier generoso**: $300 crédito inicial + Always Free tier
- ✅ **BigQuery integration**: Analytics avanzados de métricas
- ✅ **Precios competitivos**: Descuentos por uso sostenido automáticos

**Desventajas**:
- ❌ **Curva de aprendizaje**: Interface puede ser compleja
- ❌ **Menos maduro que AWS**: Menor ecosistema de terceros
- ❌ **Vendor lock-in**: Servicios propietarios de Google

---

### Prerequisitos

**Cuenta GCP**:
- [ ] Cuenta Google Cloud creada
- [ ] Billing habilitado (requiere tarjeta de crédito)
- [ ] Proyecto GCP creado
- [ ] Free tier activo ($300 crédito por 90 días)

**Herramientas locales**:

```bash
# Instalar Google Cloud SDK (gcloud CLI)
# Linux/macOS
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verificar instalación
gcloud --version

# Login
gcloud auth login

# Configurar proyecto
gcloud config set project YOUR_PROJECT_ID

# Configurar región por defecto
gcloud config set compute/region europe-west1
gcloud config set compute/zone europe-west1-b
```

**Habilitar APIs necesarias**:

```bash
gcloud services enable \
  compute.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  run.googleapis.com \
  container.googleapis.com \
  cloudresourcemanager.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com
```

---

## 🏗️ Arquitecturas de Deployment

### Comparación de Opciones

| Arquitectura | Complejidad | Costo/mes | Escalabilidad | Gestión | Uso Recomendado |
|--------------|-------------|-----------|---------------|---------|-----------------|
| **Compute Engine + Cloud SQL** | Media | $80-200 | Manual (Instance Groups) | Semi-managed | Producción estándar |
| **Cloud Run + Cloud SQL** | Baja | $30-100 | Automática (0-1000 instancias) | Serverless | Apps modernas, tráfico variable |
| **GKE + Cloud SQL** | Alta | $150-400 | Automática (K8s HPA) | Managed K8s | Microservicios, alta carga |

**Recomendación para Dashboard Sonar**:
- **Prototipo/Startup**: Cloud Run ($30-50/mes)
- **Producción pequeña-media**: Compute Engine + Cloud SQL ($80-120/mes)
- **Producción enterprise**: GKE + Cloud SQL ($200+/mes)

---

## 🖥️ Opción 1: Compute Engine + Cloud SQL (Recomendado)

### Arquitectura Objetivo

```
┌────────────────────────────────────────────────────────────────┐
│                      Google Cloud Platform                      │
│                         (europe-west1)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Cloud Load Balancer (HTTPS)                 │  │
│  │             SSL Certificate (Google-managed)              │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │         Managed Instance Group (Auto-scaling)            │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Compute VM 1 │  │ Compute VM 2 │  │ Compute VM 3 │  │  │
│  │  │  (e2-small)  │  │  (e2-small)  │  │  (e2-small)  │  │  │
│  │  │  Dashboard   │  │  Dashboard   │  │  Dashboard   │  │  │
│  │  │  Sonar App   │  │  Sonar App   │  │  Sonar App   │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │  │
│  └─────────┼──────────────────┼──────────────────┼──────────┘  │
│            │                  │                  │              │
│            └──────────────────┼──────────────────┘              │
│                               │                                 │
│  ┌────────────────────────────▼────────────────────────────┐   │
│  │              Cloud SQL (PostgreSQL)                     │   │
│  │              High Availability (HA)                     │   │
│  │              Automatic backups                          │   │
│  │              Private IP (VPC)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Secret Manager                              │   │
│  │              (DATABASE_URL, SECRET_KEY)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

### Paso 1: Crear Cloud SQL Instance

```bash
# Crear instancia PostgreSQL
gcloud sql instances create dashboardsonar-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=europe-west1 \
  --network=default \
  --enable-bin-log \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04 \
  --database-flags=max_connections=100

# Crear base de datos
gcloud sql databases create dashboardsonar \
  --instance=dashboardsonar-db

# Crear usuario
gcloud sql users create dashboard_user \
  --instance=dashboardsonar-db \
  --password=STRONG_PASSWORD_HERE

# Obtener Connection Name (para conectar desde Compute Engine)
gcloud sql instances describe dashboardsonar-db \
  --format="value(connectionName)"
# Output: project-id:europe-west1:dashboardsonar-db
```

**Tiers recomendados**:
- **db-f1-micro**: Gratis (0.6 GB RAM) - Desarrollo
- **db-g1-small**: $25/mes (1.7 GB RAM) - Producción pequeña
- **db-n1-standard-1**: $70/mes (3.75 GB RAM) - Producción media

---

### Paso 2: Crear Instance Template

**Startup script** (`startup.sh`):

```bash
#!/bin/bash

# Update system
apt-get update
apt-get install -y python3 python3-pip python3-venv git

# Clone repository
cd /opt
git clone https://github.com/jfdelafuente/dashboardsonar-application-python.git
cd dashboardsonar-application-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Get secrets from Secret Manager
PROJECT_ID=$(gcloud config get-value project)
export SECRET_KEY=$(gcloud secrets versions access latest --secret="dashboardsonar-secret-key")
export DATABASE_URL=$(gcloud secrets versions access latest --secret="dashboardsonar-db-url")

# Run migrations
flask db upgrade

# Create systemd service
cat <<EOF > /etc/systemd/system/dashboardsonar.service
[Unit]
Description=Dashboard Sonar Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/dashboardsonar-application-python
Environment="PATH=/opt/dashboardsonar-application-python/venv/bin"
Environment="SECRET_KEY=$SECRET_KEY"
Environment="DATABASE_URL=$DATABASE_URL"
Environment="FLASK_ENV=production"
ExecStart=/opt/dashboardsonar-application-python/venv/bin/gunicorn \
  "infocodest:create_app()" \
  --bind 0.0.0.0:8080 \
  --workers 4 \
  --worker-class gevent \
  --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
systemctl daemon-reload
systemctl enable dashboardsonar
systemctl start dashboardsonar
```

**Crear secrets en Secret Manager**:

```bash
# SECRET_KEY
echo -n "your-super-secret-key-here" | \
gcloud secrets create dashboardsonar-secret-key \
  --replication-policy="automatic" \
  --data-file=-

# DATABASE_URL
echo -n "postgresql://dashboard_user:STRONG_PASSWORD@/dashboardsonar?host=/cloudsql/PROJECT_ID:europe-west1:dashboardsonar-db" | \
gcloud secrets create dashboardsonar-db-url \
  --replication-policy="automatic" \
  --data-file=-
```

**Crear Instance Template**:

```bash
gcloud compute instance-templates create dashboardsonar-template \
  --machine-type=e2-small \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server \
  --metadata-from-file startup-script=startup.sh \
  --scopes=https://www.googleapis.com/auth/sqlservice.admin,https://www.googleapis.com/auth/cloud-platform \
  --service-account=YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com
```

---

### Paso 3: Crear Managed Instance Group

```bash
# Crear Instance Group
gcloud compute instance-groups managed create dashboardsonar-ig \
  --base-instance-name=dashboardsonar \
  --template=dashboardsonar-template \
  --size=2 \
  --zone=europe-west1-b

# Configurar Auto-scaling
gcloud compute instance-groups managed set-autoscaling dashboardsonar-ig \
  --max-num-replicas=10 \
  --min-num-replicas=2 \
  --target-cpu-utilization=0.70 \
  --cool-down-period=60 \
  --zone=europe-west1-b

# Configurar Named Port (para Load Balancer)
gcloud compute instance-groups managed set-named-ports dashboardsonar-ig \
  --named-ports=http:8080 \
  --zone=europe-west1-b
```

---

### Paso 4: Crear Load Balancer

```bash
# 1. Create Health Check
gcloud compute health-checks create http dashboardsonar-health-check \
  --port=8080 \
  --request-path=/health \
  --check-interval=10s \
  --timeout=5s \
  --unhealthy-threshold=3 \
  --healthy-threshold=2

# 2. Create Backend Service
gcloud compute backend-services create dashboardsonar-backend \
  --protocol=HTTP \
  --health-checks=dashboardsonar-health-check \
  --global \
  --enable-cdn \
  --session-affinity=CLIENT_IP \
  --timeout=120s

# 3. Add Instance Group to Backend
gcloud compute backend-services add-backend dashboardsonar-backend \
  --instance-group=dashboardsonar-ig \
  --instance-group-zone=europe-west1-b \
  --balancing-mode=UTILIZATION \
  --max-utilization=0.8 \
  --global

# 4. Create URL Map
gcloud compute url-maps create dashboardsonar-lb \
  --default-service=dashboardsonar-backend

# 5. Reserve Static IP
gcloud compute addresses create dashboardsonar-ip \
  --global

# Ver IP asignado
gcloud compute addresses describe dashboardsonar-ip \
  --global \
  --format="value(address)"

# 6. Create SSL Certificate (Google-managed)
gcloud compute ssl-certificates create dashboardsonar-ssl \
  --domains=dashboard.tudominio.com \
  --global

# 7. Create HTTPS Proxy
gcloud compute target-https-proxies create dashboardsonar-https-proxy \
  --url-map=dashboardsonar-lb \
  --ssl-certificates=dashboardsonar-ssl

# 8. Create Forwarding Rule (HTTPS)
gcloud compute forwarding-rules create dashboardsonar-https-rule \
  --address=dashboardsonar-ip \
  --target-https-proxy=dashboardsonar-https-proxy \
  --global \
  --ports=443

# 9. Create HTTP to HTTPS Redirect
gcloud compute url-maps import dashboardsonar-lb \
  --global \
  --source /dev/stdin <<EOF
name: dashboardsonar-lb
defaultService: https://www.googleapis.com/compute/v1/projects/$(gcloud config get-value project)/global/backendServices/dashboardsonar-backend
hostRules:
- hosts:
  - dashboard.tudominio.com
  pathMatcher: path-matcher-1
pathMatchers:
- name: path-matcher-1
  defaultService: https://www.googleapis.com/compute/v1/projects/$(gcloud config get-value project)/global/backendServices/dashboardsonar-backend
EOF
```

**Configurar DNS**:
```bash
# Apunta tu dominio a la IP del Load Balancer
# Crear registro A:
# dashboard.tudominio.com -> [IP_DEL_LOAD_BALANCER]
```

---

## ☁️ Opción 2: Cloud Run (Serverless)

**Cloud Run** es serverless, escala automáticamente de 0 a 1000+ instancias.

### Arquitectura Cloud Run

```
┌─────────────────────────────────────────────────────────┐
│              Cloud Run Service                          │
│         (Auto-scaling 0-1000 instances)                 │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Container 1  │  │ Container 2  │  │ Container N  │  │
│  │ (Dashboard)  │  │ (Dashboard)  │  │ (Dashboard)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼──────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │     Cloud SQL (PostgreSQL)          │
          │     Private IP connection           │
          └─────────────────────────────────────┘
```

---

### Paso 1: Crear Dockerfile optimizado para Cloud Run

**`Dockerfile.cloudrun`**:

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar código
COPY . .

# Cambiar a usuario no-root
RUN chown -R appuser:appuser /app
USER appuser

# Cloud Run usa PORT environment variable
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')" || exit 1

# Entrypoint
CMD exec gunicorn "infocodest:create_app()" \
    --bind :$PORT \
    --workers 1 \
    --threads 8 \
    --worker-class gthread \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -
```

---

### Paso 2: Build y Push a Container Registry

```bash
# Configurar Docker para GCP
gcloud auth configure-docker

# Build imagen
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/dashboardsonar:v1.0.0

# O con docker local:
docker build -f Dockerfile.cloudrun -t gcr.io/YOUR_PROJECT_ID/dashboardsonar:v1.0.0 .
docker push gcr.io/YOUR_PROJECT_ID/dashboardsonar:v1.0.0
```

---

### Paso 3: Deploy a Cloud Run

```bash
# Deploy con Cloud SQL connection
gcloud run deploy dashboardsonar \
  --image gcr.io/YOUR_PROJECT_ID/dashboardsonar:v1.0.0 \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 80 \
  --set-cloudsql-instances=PROJECT_ID:europe-west1:dashboardsonar-db \
  --set-secrets=SECRET_KEY=dashboardsonar-secret-key:latest,DATABASE_URL=dashboardsonar-db-url:latest \
  --set-env-vars="FLASK_ENV=production,LOG_LEVEL=INFO"

# Obtener URL del servicio
gcloud run services describe dashboardsonar \
  --region europe-west1 \
  --format="value(status.url)"
```

---

### Paso 4: Configurar Dominio Custom

```bash
# Mapear dominio custom
gcloud run domain-mappings create \
  --service dashboardsonar \
  --domain dashboard.tudominio.com \
  --region europe-west1

# Cloud Run te dará registros DNS para configurar (CNAME)
# Ejemplo:
# dashboard.tudominio.com -> ghs.googlehosted.com
```

**SSL es automático** con Cloud Run (Let's Encrypt).

---

### Pricing Cloud Run

**Modelo de pricing**:
- **CPU**: $0.00002400 / vCPU-second
- **Memory**: $0.00000250 / GB-second
- **Requests**: $0.40 / million requests
- **Free tier**: 2M requests/mes, 360,000 GB-seconds

**Estimación Dashboard Sonar**:
- 100k requests/mes
- 512 MB RAM, 1 vCPU
- Avg request duration: 200ms
- **Costo**: ~$15-30/mes

---

## 🎯 Opción 3: Google Kubernetes Engine (GKE)

Ver [DEPLOYMENT_KUBERNETES.md](DEPLOYMENT_KUBERNETES.md) para guía completa de Kubernetes.

### Crear cluster GKE

```bash
# Crear cluster GKE Autopilot (managed, más económico)
gcloud container clusters create-auto dashboardsonar-cluster \
  --region=europe-west1 \
  --release-channel=regular

# O cluster Standard (más control)
gcloud container clusters create dashboardsonar-cluster \
  --zone=europe-west1-b \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10 \
  --enable-autorepair \
  --enable-autoupgrade

# Obtener credenciales
gcloud container clusters get-credentials dashboardsonar-cluster \
  --region=europe-west1
```

**Deployment en GKE**: Seguir pasos de [DEPLOYMENT_KUBERNETES.md](DEPLOYMENT_KUBERNETES.md).

---

## 💾 Cloud SQL Configuration

### High Availability (HA)

```bash
# Habilitar HA (replica en zona diferente)
gcloud sql instances patch dashboardsonar-db \
  --availability-type=REGIONAL

# Configurar backups automáticos
gcloud sql instances patch dashboardsonar-db \
  --backup-start-time=03:00 \
  --retained-backups-count=7 \
  --retained-transaction-log-days=7
```

---

### Point-in-Time Recovery

```bash
# Restaurar a timestamp específico
gcloud sql backups restore BACKUP_ID \
  --backup-instance=dashboardsonar-db \
  --backup-id=BACKUP_ID

# O crear instancia nueva desde backup
gcloud sql instances clone dashboardsonar-db dashboardsonar-db-restored \
  --point-in-time '2025-12-17T10:00:00.000Z'
```

---

### Monitoring y Performance Insights

```bash
# Habilitar Query Insights
gcloud sql instances patch dashboardsonar-db \
  --insights-config-query-insights-enabled \
  --insights-config-query-string-length=1024 \
  --insights-config-record-application-tags \
  --insights-config-record-client-address
```

Ver insights en: Cloud Console → SQL → dashboardsonar-db → Query Insights

---

## 🔐 Secret Manager

### Crear y gestionar secrets

```bash
# Crear secret
echo -n "mi-secreto" | gcloud secrets create mi-secret --data-file=-

# Añadir nueva versión
echo -n "nuevo-valor" | gcloud secrets versions add mi-secret --data-file=-

# Acceder a secret desde aplicación
gcloud secrets versions access latest --secret="mi-secret"

# Dar permisos a Service Account
gcloud secrets add-iam-policy-binding mi-secret \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 📊 Monitoring con Cloud Operations

### Cloud Monitoring (Stackdriver)

**Métricas automáticas** (sin configuración):
- CPU usage
- Memory usage
- Disk I/O
- Network traffic
- HTTP requests (Cloud Run)

**Dashboard personalizado**:

```bash
# Instalar Ops Agent en Compute Engine
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
```

**Ver métricas**: Cloud Console → Monitoring → Dashboards

---

### Cloud Logging

```bash
# Ver logs en tiempo real
gcloud logging read "resource.type=gce_instance" \
  --limit 50 \
  --format json

# Logs de Cloud Run
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50

# Crear alertas
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High CPU Alert" \
  --condition-display-name="CPU > 80%" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s
```

---

## 🔄 CI/CD con Cloud Build

**`cloudbuild.yaml`**:

```yaml
steps:
  # Run tests
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        pip install pytest
        pytest tests/

  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/dashboardsonar:$COMMIT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/dashboardsonar:latest'
      - '-f'
      - 'Dockerfile.cloudrun'
      - '.'

  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/dashboardsonar:$COMMIT_SHA'

  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'dashboardsonar'
      - '--image'
      - 'gcr.io/$PROJECT_ID/dashboardsonar:$COMMIT_SHA'
      - '--region'
      - 'europe-west1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/dashboardsonar:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/dashboardsonar:latest'

timeout: '1200s'
```

**Crear trigger automático**:

```bash
gcloud builds triggers create github \
  --repo-name=dashboardsonar-application-python \
  --repo-owner=jfdelafuente \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

---

## 💰 Cost Optimization

### Compute Engine

```bash
# Usar Committed Use Discounts (37% descuento)
gcloud compute commitments create dashboardsonar-commitment \
  --resources=vcpu=4,memory=16 \
  --plan=12-month \
  --region=europe-west1

# Usar Spot VMs (60-91% descuento) para workloads tolerantes a interrupciones
gcloud compute instance-templates create dashboardsonar-spot-template \
  --machine-type=e2-small \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP
```

---

### Cloud SQL

```bash
# Usar auto-scaling de storage (pagar solo lo que usas)
gcloud sql instances patch dashboardsonar-db \
  --storage-auto-increase \
  --storage-auto-increase-limit=100

# Programar stop/start para staging
gcloud sql instances patch dashboardsonar-db \
  --activation-policy=NEVER  # Stop

gcloud sql instances patch dashboardsonar-db \
  --activation-policy=ALWAYS # Start
```

---

### Estimación de Costos

| Componente | Tier/Type | Costo/mes |
|------------|-----------|-----------|
| **Compute Engine** (2x e2-small) | Sustained Use Discount | $25 |
| **Cloud SQL** (db-g1-small) | HA enabled | $50 |
| **Load Balancer** | Forwarding rules + traffic | $18 |
| **Cloud Storage** (backups) | 50 GB standard | $1 |
| **Networking** | 500 GB egress | $40 |
| **Cloud Monitoring** | Standard (free tier) | $0 |
| **Total (Compute Engine)** | | **~$134/mes** |
|  |  |  |
| **Cloud Run** (100k req/mes) | 512 MB, 1 vCPU | $20 |
| **Cloud SQL** (db-g1-small) | | $50 |
| **Total (Cloud Run)** | | **~$70/mes** |

**Cálculo exacto**: https://cloud.google.com/products/calculator

---

## 🔧 Troubleshooting

### Compute Engine no puede conectar a Cloud SQL

```bash
# Verificar que la VM tiene scope correcto
gcloud compute instances describe INSTANCE_NAME \
  --format="value(serviceAccounts[].scopes)"

# Debe incluir: https://www.googleapis.com/auth/sqlservice.admin

# Reinstanciar con scopes correctos
gcloud compute instances set-service-account INSTANCE_NAME \
  --service-account=SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/sqlservice.admin,https://www.googleapis.com/auth/cloud-platform
```

---

### Cloud Run timeout

```bash
# Aumentar timeout (max 3600s)
gcloud run services update dashboardsonar \
  --timeout=3600 \
  --region=europe-west1

# Aumentar memoria
gcloud run services update dashboardsonar \
  --memory=1Gi \
  --region=europe-west1
```

---

### Load Balancer 502 Bad Gateway

```bash
# Verificar Health Check
gcloud compute health-checks describe dashboardsonar-health-check

# Ver logs de backend instances
gcloud compute instance-groups managed list-instances dashboardsonar-ig \
  --zone=europe-west1-b

# Ver logs del balanceador
gcloud logging read "resource.type=http_load_balancer" --limit 50
```

---

## 📚 Recursos Adicionales

**Documentación oficial**:
- [Compute Engine Docs](https://cloud.google.com/compute/docs)
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Cloud SQL Docs](https://cloud.google.com/sql/docs)
- [GKE Docs](https://cloud.google.com/kubernetes-engine/docs)

**Herramientas**:
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)
- [Cloud Console](https://console.cloud.google.com/)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)

**Certificaciones**:
- [Associate Cloud Engineer](https://cloud.google.com/certification/cloud-engineer)
- [Professional Cloud Architect](https://cloud.google.com/certification/cloud-architect)

---

**Última actualización**: Diciembre 2025
**Mantenido por**: Equipo DevOps
**Soporte**: devops@empresa.com
