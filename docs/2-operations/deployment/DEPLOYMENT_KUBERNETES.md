# Kubernetes Deployment Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, Platform Engineers
**Plataforma**: Kubernetes (cualquier distribución)

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Prerequisitos](#prerequisitos)
3. [Arquitectura en Kubernetes](#arquitectura-en-kubernetes)
4. [Setup con Manifests (YAML)](#setup-con-manifests-yaml)
5. [Setup con Helm Chart](#setup-con-helm-chart)
6. [Configuración de PostgreSQL](#configuración-de-postgresql)
7. [Ingress y SSL/TLS](#ingress-y-ssltls)
8. [Secrets Management](#secrets-management)
9. [Persistent Volumes](#persistent-volumes)
10. [Horizontal Pod Autoscaling](#horizontal-pod-autoscaling)
11. [Monitoring y Logging](#monitoring-y-logging)
12. [CI/CD con Kubernetes](#cicd-con-kubernetes)
13. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

### ¿Por qué Kubernetes?

**Ventajas**:
- ✅ **Portabilidad**: Funciona en cualquier cloud (AWS EKS, GCP GKE, Azure AKS) o on-premise
- ✅ **Auto-scaling**: HPA (Horizontal Pod Autoscaler) escala automáticamente
- ✅ **Auto-healing**: Pods que fallan se reinician automáticamente
- ✅ **Rolling updates**: Zero-downtime deployments
- ✅ **Declarative**: Infraestructura como código (GitOps)
- ✅ **Ecosistema**: Helm charts, Prometheus, Grafana, Istio

**Desventajas**:
- ❌ **Complejidad**: Curva de aprendizaje pronunciada
- ❌ **Overhead**: Requiere cluster management (managed Kubernetes recomendado)
- ❌ **Costo**: Cluster + nodos + load balancer (~$150-400/mes)

---

### ¿Cuándo usar Kubernetes?

**Usa Kubernetes si**:
- Necesitas alta disponibilidad (99.99%+)
- Tu aplicación debe escalar automáticamente
- Tienes múltiples microservicios
- Quieres portabilidad multi-cloud
- Tu equipo tiene experiencia con K8s

**NO uses Kubernetes si**:
- Es una aplicación simple (usa VM + Docker o PaaS)
- No tienes experiencia con K8s (curva de aprendizaje)
- Presupuesto limitado (<$100/mes)

---

## 📦 Prerequisitos

### Cluster Kubernetes

**Opciones recomendadas**:

| Proveedor | Servicio | Costo/mes | Dificultad |
|-----------|----------|-----------|------------|
| **AWS** | EKS (Elastic Kubernetes Service) | $220+ | Media |
| **GCP** | GKE (Google Kubernetes Engine) | $200+ | Baja |
| **Azure** | AKS (Azure Kubernetes Service) | $200+ | Media |
| **DigitalOcean** | DOKS (managed K8s) | $120+ | Baja |
| **Linode** | LKE (Linode Kubernetes Engine) | $110+ | Baja |
| **Local** | Minikube / Kind | Gratis | Alta |

**Configuración mínima recomendada**:
- **Nodos**: 2-3 nodos worker (high availability)
- **CPU**: 2 vCPU por nodo
- **RAM**: 4 GB por nodo
- **Versión K8s**: 1.27+ (stable)

---

### Herramientas Locales

```bash
# kubectl (CLI de Kubernetes)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verificar
kubectl version --client

# Helm (package manager)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verificar
helm version

# (Opcional) kubectx/kubens - Cambiar contextos fácilmente
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens
```

---

### Configurar acceso al cluster

**AWS EKS**:
```bash
aws eks update-kubeconfig --region eu-west-1 --name dashboard-sonar-cluster
```

**GCP GKE**:
```bash
gcloud container clusters get-credentials dashboard-sonar-cluster --region europe-west1
```

**DigitalOcean DOKS**:
```bash
doctl kubernetes cluster kubeconfig save dashboard-sonar-cluster
```

**Verificar conexión**:
```bash
kubectl cluster-info
kubectl get nodes
```

---

## 🏗️ Arquitectura en Kubernetes

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Ingress Controller                      │   │
│  │          (NGINX / Traefik / ALB)                     │   │
│  │              HTTPS/SSL (Cert-Manager)                │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │            Service (dashboard-sonar)                 │   │
│  │              Type: ClusterIP                         │   │
│  │              Port: 5000                              │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │         Deployment (dashboard-sonar)                 │   │
│  │                                                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │   Pod 1    │  │   Pod 2    │  │   Pod 3    │    │   │
│  │  │ (Gunicorn) │  │ (Gunicorn) │  │ (Gunicorn) │    │   │
│  │  │  replicas=3│  │            │  │            │    │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │   │
│  └────────┼───────────────┼───────────────┼───────────┘   │
│           │               │               │                │
│           │               │               │                │
│  ┌────────▼───────────────▼───────────────▼───────────┐   │
│  │         Service (postgresql)                        │   │
│  │              Type: ClusterIP                        │   │
│  │              Port: 5432                             │   │
│  └──────────────────┬──────────────────────────────────┘   │
│                     │                                       │
│  ┌──────────────────▼──────────────────────────────────┐   │
│  │    StatefulSet (postgresql)                         │   │
│  │         or External RDS/CloudSQL                    │   │
│  │                                                      │   │
│  │  ┌────────────┐                                     │   │
│  │  │ PostgreSQL │◄─── PersistentVolumeClaim (PVC)    │   │
│  │  │  Pod       │◄─── PersistentVolume (PV)          │   │
│  │  └────────────┘                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           ConfigMap & Secrets                       │   │
│  │   - Database credentials                            │   │
│  │   - SECRET_KEY, .env vars                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Setup con Manifests (YAML)

### Paso 1: Crear Namespace

```bash
kubectl create namespace dashboardsonar
kubens dashboardsonar  # Switch to namespace
```

O con YAML:

**`namespace.yaml`**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dashboardsonar
```

```bash
kubectl apply -f namespace.yaml
```

---

### Paso 2: Secrets (Credenciales)

**`secrets.yaml`**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: dashboardsonar-secrets
  namespace: dashboardsonar
type: Opaque
stringData:
  SECRET_KEY: "your-super-secret-key-change-this-in-production"
  DATABASE_URL: "postgresql://dbuser:dbpassword@postgresql:5432/dashboardsonar"
  POSTGRES_PASSWORD: "strong-db-password-here"
  POSTGRES_USER: "dashboard_user"
  POSTGRES_DB: "dashboardsonar"
```

**IMPORTANTE**: En producción, usa **Sealed Secrets** o **External Secrets Operator** en lugar de guardar secrets en Git.

```bash
kubectl apply -f secrets.yaml
```

---

### Paso 3: ConfigMap (Configuración)

**`configmap.yaml`**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dashboardsonar-config
  namespace: dashboardsonar
data:
  FLASK_ENV: "production"
  FLASK_DEBUG: "0"
  LOG_LEVEL: "INFO"
  GUNICORN_WORKERS: "4"
  GUNICORN_WORKER_CLASS: "gevent"
  GUNICORN_TIMEOUT: "120"
  DATABASE_POOL_SIZE: "20"
  DATABASE_MAX_OVERFLOW: "10"
```

```bash
kubectl apply -f configmap.yaml
```

---

### Paso 4: PostgreSQL StatefulSet + Service

**Opción A: PostgreSQL en Kubernetes (desarrollo/staging)**

**`postgresql-pvc.yaml`**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgresql-pvc
  namespace: dashboardsonar
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard  # o gp2 (AWS), pd-standard (GCP)
```

**`postgresql-statefulset.yaml`**:
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: dashboardsonar
spec:
  serviceName: postgresql
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: dashboardsonar-secrets
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: dashboardsonar-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: dashboardsonar-secrets
              key: POSTGRES_PASSWORD
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgresql-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U $POSTGRES_USER
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U $POSTGRES_USER
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgresql-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: standard
      resources:
        requests:
          storage: 10Gi
```

**`postgresql-service.yaml`**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgresql
  namespace: dashboardsonar
spec:
  type: ClusterIP
  ports:
  - port: 5432
    targetPort: 5432
  selector:
    app: postgresql
```

```bash
kubectl apply -f postgresql-pvc.yaml
kubectl apply -f postgresql-statefulset.yaml
kubectl apply -f postgresql-service.yaml
```

**Opción B: PostgreSQL externo (producción)**

Usa RDS (AWS), CloudSQL (GCP), o Azure Database for PostgreSQL, y actualiza `DATABASE_URL` en secrets.yaml.

---

### Paso 5: Dashboard Sonar Deployment

**`deployment.yaml`**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dashboardsonar
  namespace: dashboardsonar
  labels:
    app: dashboardsonar
spec:
  replicas: 3  # High availability
  selector:
    matchLabels:
      app: dashboardsonar
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero-downtime deployment
  template:
    metadata:
      labels:
        app: dashboardsonar
        version: v1.10.0
    spec:
      containers:
      - name: dashboardsonar
        image: dashboardsonar/app:v1.10.0  # Reemplazar con tu imagen
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
          name: http
        env:
        # Desde ConfigMap
        - name: FLASK_ENV
          valueFrom:
            configMapKeyRef:
              name: dashboardsonar-config
              key: FLASK_ENV
        - name: FLASK_DEBUG
          valueFrom:
            configMapKeyRef:
              name: dashboardsonar-config
              key: FLASK_DEBUG
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: dashboardsonar-config
              key: LOG_LEVEL
        - name: GUNICORN_WORKERS
          valueFrom:
            configMapKeyRef:
              name: dashboardsonar-config
              key: GUNICORN_WORKERS
        - name: GUNICORN_WORKER_CLASS
          valueFrom:
            configMapKeyRef:
              name: dashboardsonar-config
              key: GUNICORN_WORKER_CLASS
        - name: GUNICORN_TIMEOUT
          valueFrom:
            configMapKeyRef:
              name: dashboardsonar-config
              key: GUNICORN_TIMEOUT
        # Desde Secrets
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: dashboardsonar-secrets
              key: SECRET_KEY
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: dashboardsonar-secrets
              key: DATABASE_URL
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health  # Asume endpoint /health en tu app
            port: 5000
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        # (Opcional) Persistent volume para logs
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

```bash
kubectl apply -f deployment.yaml
```

**Verificar deployment**:
```bash
kubectl get pods -n dashboardsonar
kubectl logs -f deployment/dashboardsonar -n dashboardsonar
```

---

### Paso 6: Service (ClusterIP)

**`service.yaml`**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: dashboardsonar
  namespace: dashboardsonar
  labels:
    app: dashboardsonar
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 5000
    protocol: TCP
    name: http
  selector:
    app: dashboardsonar
```

```bash
kubectl apply -f service.yaml
```

---

### Paso 7: Ingress (Exposición externa + SSL)

**Instalar NGINX Ingress Controller** (si no está instalado):
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

**Instalar Cert-Manager** (para SSL automático con Let's Encrypt):
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

**Crear ClusterIssuer para Let's Encrypt**:

**`letsencrypt-issuer.yaml`**:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@tudominio.com  # Cambiar
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

```bash
kubectl apply -f letsencrypt-issuer.yaml
```

**Crear Ingress**:

**`ingress.yaml`**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dashboardsonar-ingress
  namespace: dashboardsonar
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - dashboard.tudominio.com  # Cambiar
    secretName: dashboardsonar-tls
  rules:
  - host: dashboard.tudominio.com  # Cambiar
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dashboardsonar
            port:
              number: 80
```

```bash
kubectl apply -f ingress.yaml
```

**Configurar DNS**:
```bash
# Obtener IP del Load Balancer
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Crear registro A en tu DNS apuntando a esta IP:
# dashboard.tudominio.com -> 34.56.78.90
```

**Verificar SSL**:
```bash
curl https://dashboard.tudominio.com
```

---

## 🎁 Setup con Helm Chart

Helm simplifica deployment con templates reutilizables.

### Estructura de Helm Chart

```bash
mkdir -p dashboardsonar-chart
cd dashboardsonar-chart

dashboardsonar/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── postgresql-statefulset.yaml
│   └── hpa.yaml
└── .helmignore
```

**`Chart.yaml`**:
```yaml
apiVersion: v2
name: dashboardsonar
description: Dashboard Sonar - SonarQube Metrics Dashboard
type: application
version: 1.10.0
appVersion: "1.10.0"
keywords:
  - dashboard
  - sonarqube
  - metrics
  - quality
maintainers:
  - name: DevOps Team
    email: devops@empresa.com
```

**`values.yaml`** (configuración personalizable):
```yaml
replicaCount: 3

image:
  repository: dashboardsonar/app
  tag: v1.10.0
  pullPolicy: Always

service:
  type: ClusterIP
  port: 80
  targetPort: 5000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: dashboard.tudominio.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: dashboardsonar-tls
      hosts:
        - dashboard.tudominio.com

resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

postgresql:
  enabled: true  # false si usas RDS externo
  auth:
    username: dashboard_user
    password: changeme
    database: dashboardsonar
  persistence:
    enabled: true
    size: 10Gi
  resources:
    requests:
      memory: 512Mi
      cpu: 250m

env:
  FLASK_ENV: production
  FLASK_DEBUG: "0"
  LOG_LEVEL: INFO
  GUNICORN_WORKERS: "4"
  GUNICORN_WORKER_CLASS: gevent
  GUNICORN_TIMEOUT: "120"

secrets:
  secretKey: "your-super-secret-key-change-in-production"
  databaseUrl: "postgresql://dashboard_user:changeme@dashboardsonar-postgresql:5432/dashboardsonar"
```

**Instalar chart**:
```bash
helm install dashboardsonar ./dashboardsonar-chart \
  --namespace dashboardsonar \
  --create-namespace \
  --values values.yaml
```

**Actualizar deployment**:
```bash
# Modificar values.yaml (ej: cambiar replicaCount)
helm upgrade dashboardsonar ./dashboardsonar-chart \
  --namespace dashboardsonar \
  --values values.yaml
```

**Rollback**:
```bash
helm rollback dashboardsonar 1 --namespace dashboardsonar
```

---

## ⚙️ Horizontal Pod Autoscaling (HPA)

**`hpa.yaml`**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dashboardsonar-hpa
  namespace: dashboardsonar
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dashboardsonar
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 min antes de scale down
    scaleUp:
      stabilizationWindowSeconds: 60   # 1 min antes de scale up
```

```bash
kubectl apply -f hpa.yaml
kubectl get hpa -n dashboardsonar --watch
```

---

## 📊 Monitoring y Logging

### Prometheus + Grafana (via Helm)

```bash
# Agregar repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Instalar kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Acceder a Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Usuario: admin
# Password: (obtener con):
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

**Dashboards recomendados**:
- Kubernetes Cluster Monitoring (ID: 7249)
- Pod Monitoring (ID: 6417)
- Ingress NGINX (ID: 9614)

---

### Logging con EFK Stack

**Elasticsearch + Fluentd + Kibana**:

```bash
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch --namespace logging --create-namespace
helm install kibana elastic/kibana --namespace logging
helm install fluentd fluent/fluentd --namespace logging
```

---

## 🔄 CI/CD con Kubernetes

### GitHub Actions Pipeline

**`.github/workflows/k8s-deploy.yml`**:
```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: |
        docker build -t dashboardsonar/app:${{ github.sha }} .
        docker tag dashboardsonar/app:${{ github.sha }} dashboardsonar/app:latest

    - name: Push to Docker Hub
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker push dashboardsonar/app:${{ github.sha }}
        docker push dashboardsonar/app:latest

    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'

    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/dashboardsonar \
          dashboardsonar=dashboardsonar/app:${{ github.sha }} \
          -n dashboardsonar
        kubectl rollout status deployment/dashboardsonar -n dashboardsonar
```

---

## 🔧 Troubleshooting

### Pods no arrancan

```bash
# Ver estado de pods
kubectl get pods -n dashboardsonar

# Logs del pod
kubectl logs -f <pod-name> -n dashboardsonar

# Describir pod (ver eventos)
kubectl describe pod <pod-name> -n dashboardsonar

# Entrar al pod
kubectl exec -it <pod-name> -n dashboardsonar -- /bin/bash
```

### Problemas comunes

**1. ImagePullBackOff**:
```bash
# Verificar que la imagen existe en Docker Hub
docker pull dashboardsonar/app:v1.10.0

# Si es imagen privada, crear secret:
kubectl create secret docker-registry regcred \
  --docker-server=docker.io \
  --docker-username=<usuario> \
  --docker-password=<password> \
  --docker-email=<email> \
  -n dashboardsonar

# Agregar en deployment.yaml:
spec:
  imagePullSecrets:
  - name: regcred
```

**2. CrashLoopBackOff**:
```bash
# Ver logs del container que crashea
kubectl logs <pod-name> -n dashboardsonar --previous

# Problemas típicos:
# - DATABASE_URL incorrecto
# - SECRET_KEY no configurado
# - Migraciones de BD pendientes
```

**3. Ingress no funciona**:
```bash
# Verificar ingress
kubectl get ingress -n dashboardsonar
kubectl describe ingress dashboardsonar-ingress -n dashboardsonar

# Verificar NGINX controller
kubectl get pods -n ingress-nginx

# Ver logs de NGINX
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

---

## 📚 Recursos Adicionales

**Documentación oficial**:
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Helm Docs](https://helm.sh/docs/)
- [NGINX Ingress](https://kubernetes.github.io/ingress-nginx/)
- [Cert-Manager](https://cert-manager.io/docs/)

**Herramientas útiles**:
- [k9s](https://k9scli.io/) - Terminal UI para K8s
- [Lens](https://k8slens.dev/) - GUI para K8s
- [kubectx/kubens](https://github.com/ahmetb/kubectx) - Cambiar contextos rápido

**Cursos recomendados**:
- [Kubernetes for Beginners (KodeKloud)](https://kodekloud.com/)
- [Certified Kubernetes Administrator (CKA)](https://www.cncf.io/certification/cka/)

---

**Última actualización**: Diciembre 2025
**Mantenido por**: Equipo DevOps
**Soporte**: devops@empresa.com
