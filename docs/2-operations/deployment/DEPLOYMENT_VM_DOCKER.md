# VM + Docker Deployment Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, System Administrators
**Plataformas**: DigitalOcean, Linode, Vultr, Hetzner, cualquier VPS

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Comparación de Proveedores VPS](#comparación-de-proveedores-vps)
3. [Prerequisitos](#prerequisitos)
4. [Setup Inicial del Servidor](#setup-inicial-del-servidor)
5. [Instalación de Docker](#instalación-de-docker)
6. [Deployment con Docker Compose](#deployment-con-docker-compose)
7. [Configuración de NGINX Reverse Proxy](#configuración-de-nginx-reverse-proxy)
8. [SSL con Let's Encrypt](#ssl-con-lets-encrypt)
9. [Firewall y Seguridad](#firewall-y-seguridad)
10. [Backups Automatizados](#backups-automatizados)
11. [Monitoring con Prometheus](#monitoring-con-prometheus)
12. [CI/CD con GitHub Actions](#cicd-con-github-actions)
13. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

### ¿Por qué VM + Docker?

**Ventajas**:
- ✅ **Control total**: Acceso root SSH, configuración completa
- ✅ **Costo bajo**: $5-20/mes (vs $100+ en PaaS/Cloud)
- ✅ **Portabilidad**: Docker funciona en cualquier VM
- ✅ **Flexibilidad**: Instalar cualquier software
- ✅ **Aprendizaje**: Entender DevOps desde cero

**Desventajas**:
- ❌ **Gestión manual**: OS updates, security patches
- ❌ **Responsabilidad**: Tú gestionas backups, monitoring, SSL
- ❌ **Escalabilidad limitada**: Vertical scaling solamente
- ❌ **Tiempo de setup**: 1-2 horas vs 10 minutos en PaaS

---

### ¿Cuándo usar VM + Docker?

**Usa VM + Docker si**:
- Presupuesto limitado ($5-20/mes)
- Quieres aprender DevOps
- Necesitas control total
- Tráfico predecible (<10k users/mes)

**NO uses VM + Docker si**:
- No tienes experiencia con Linux
- Necesitas auto-scaling
- Presupuesto permite PaaS ($50+/mes)
- Producción crítica (usa managed services)

---

## 📊 Comparación de Proveedores VPS

| Proveedor | Precio/mes | RAM | CPU | Storage | Bandwidth | Regiones | Soporte |
|-----------|------------|-----|-----|---------|-----------|----------|---------|
| **DigitalOcean** | $6 | 1 GB | 1 vCPU | 25 GB SSD | 1 TB | 14 | Excelente |
| **Linode (Akamai)** | $5 | 1 GB | 1 vCPU | 25 GB SSD | 1 TB | 11 | Excelente |
| **Vultr** | $6 | 1 GB | 1 vCPU | 25 GB SSD | 1 TB | 32 | Bueno |
| **Hetzner** | €4.5 | 2 GB | 2 vCPU | 40 GB SSD | 20 TB | 3 (EU) | Medio |
| **AWS Lightsail** | $5 | 1 GB | 1 vCPU | 40 GB SSD | 2 TB | 16 | AWS Support |

**Recomendación para Dashboard Sonar**:

| Escenario | Proveedor | Plan | Precio/mes |
|-----------|-----------|------|------------|
| **Desarrollo/Staging** | Hetzner | CX11 (2 GB RAM) | €4.5 (~$5) |
| **Producción pequeña** | DigitalOcean | Basic (2 GB RAM) | $12 |
| **Producción media** | Linode | Dedicated 4 GB | $24 |
| **Alta disponibilidad** | DigitalOcean + Load Balancer | 3x 2 GB + LB | ~$50 |

---

## 📦 Prerequisitos

### Crear VPS

**DigitalOcean**:
1. Registrarse en https://www.digitalocean.com/
2. Create → Droplets
3. Configurar:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic Shared CPU → $12/mes (2 GB RAM, 1 vCPU)
   - **Datacenter**: Closest to users (Frankfurt, London, New York)
   - **Authentication**: SSH keys (recomendado) o Password
   - **Hostname**: `dashboardsonar-prod`
4. Create Droplet

**Linode**:
1. https://www.linode.com/ → Create Linode
2. Configurar:
   - **Image**: Ubuntu 22.04 LTS
   - **Region**: EU-Central (Frankfurt) o US-East (Newark)
   - **Plan**: Shared CPU → Linode 2 GB ($12/mes)
   - **Root Password**: Strong password
   - **SSH Keys**: Añadir tu clave pública
3. Create Linode

---

### Generar SSH Key (si no tienes)

```bash
# Linux/macOS/WSL
ssh-keygen -t ed25519 -C "tu-email@empresa.com"
# Guardar en: /home/usuario/.ssh/id_ed25519

# Ver clave pública (copiar al proveedor VPS)
cat ~/.ssh/id_ed25519.pub
```

---

## 🖥️ Setup Inicial del Servidor

### Paso 1: Conectar via SSH

```bash
# Reemplazar con tu IP
ssh root@157.245.123.456

# Si usas SSH key específica:
ssh -i ~/.ssh/id_ed25519 root@157.245.123.456
```

---

### Paso 2: Actualizar sistema

```bash
apt update && apt upgrade -y
apt install -y curl git vim ufw fail2ban
```

---

### Paso 3: Crear usuario no-root

```bash
# Crear usuario
adduser deploy
# Ingresar password y detalles

# Agregar a sudo
usermod -aG sudo deploy

# Copiar SSH keys de root a deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

**Probar conexión**:
```bash
# Desde tu máquina local
ssh deploy@157.245.123.456
```

---

### Paso 4: Configurar firewall

```bash
# Permitir SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar firewall
sudo ufw enable

# Verificar
sudo ufw status
```

---

### Paso 5: Configurar Fail2Ban (protección brute-force)

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Verificar
sudo fail2ban-client status
```

---

## 🐳 Instalación de Docker

### Instalar Docker Engine

```bash
# Remover versiones antiguas
sudo apt remove docker docker-engine docker.io containerd runc

# Instalar dependencias
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Agregar Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Agregar repositorio Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verificar instalación
sudo docker --version
sudo docker compose version
```

---

### Configurar usuario para usar Docker sin sudo

```bash
# Agregar usuario actual a grupo docker
sudo usermod -aG docker $USER

# Aplicar cambio (logout/login)
newgrp docker

# Verificar
docker ps
```

---

## 🚀 Deployment con Docker Compose

### Paso 1: Clonar repositorio

```bash
cd /home/deploy
git clone https://github.com/jfdelafuente/dashboardsonar-application-python.git
cd dashboardsonar-application-python
```

---

### Paso 2: Crear `.env` con producción

**`.env.production`**:
```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=tu-secret-key-super-fuerte-generado

# Database
DATABASE_URL=postgresql://dashboard_user:strong_password_here@postgres:5432/dashboardsonar

# PostgreSQL
POSTGRES_USER=dashboard_user
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DB=dashboardsonar

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_WORKER_CLASS=gevent
GUNICORN_TIMEOUT=120

# Logging
LOG_LEVEL=INFO

# Application
HOST=0.0.0.0
PORT=5000
```

**Generar SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

### Paso 3: Crear `Dockerfile`

**`Dockerfile`**:
```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Comando por defecto
CMD ["gunicorn", "infocodest:create_app()", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "gevent", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

---

### Paso 4: Crear `docker-compose.yml`

**`docker-compose.yml`**:
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: dashboardsonar-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"  # Solo localhost puede acceder
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - dashboardsonar-network

  # Dashboard Sonar Application
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dashboardsonar-app
    restart: unless-stopped
    env_file:
      - .env.production
    ports:
      - "127.0.0.1:5000:5000"  # Solo localhost (NGINX hará proxy)
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - dashboardsonar-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # NGINX Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: dashboardsonar-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /var/log/nginx:/var/log/nginx
    depends_on:
      - app
    networks:
      - dashboardsonar-network

volumes:
  postgres_data:
    driver: local

networks:
  dashboardsonar-network:
    driver: bridge
```

---

### Paso 5: Build y ejecutar

```bash
# Build imagen
docker compose build

# Ejecutar migraciones (primera vez)
docker compose run --rm app flask db upgrade

# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Verificar estado
docker compose ps
```

---

## 🔧 Configuración de NGINX Reverse Proxy

### Crear configuración NGINX

```bash
mkdir -p nginx/conf.d
```

**`nginx/nginx.conf`**:
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_disable "msie6";
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    include /etc/nginx/conf.d/*.conf;
}
```

**`nginx/conf.d/dashboardsonar.conf`**:
```nginx
upstream dashboardsonar_app {
    server app:5000 fail_timeout=30s max_fails=3;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name dashboard.tudominio.com;  # Cambiar

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dashboard.tudominio.com;  # Cambiar

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logging
    access_log /var/log/nginx/dashboardsonar_access.log;
    error_log /var/log/nginx/dashboardsonar_error.log;

    # Static files (if any)
    location /static/ {
        alias /app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Flask app
    location / {
        proxy_pass http://dashboardsonar_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Health check endpoint (sin logs)
    location /health {
        proxy_pass http://dashboardsonar_app;
        access_log off;
    }
}
```

---

## 🔒 SSL con Let's Encrypt

### Instalar Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

### Obtener certificado SSL

```bash
# Obtener certificado (standalone mode, detiene NGINX temporalmente)
sudo certbot certonly --nginx -d dashboard.tudominio.com --email admin@tudominio.com --agree-tos --non-interactive

# Los certificados se guardan en:
# /etc/letsencrypt/live/dashboard.tudominio.com/fullchain.pem
# /etc/letsencrypt/live/dashboard.tudominio.com/privkey.pem
```

---

### Copiar certificados a carpeta nginx

```bash
sudo mkdir -p /home/deploy/dashboardsonar-application-python/nginx/ssl

sudo cp /etc/letsencrypt/live/dashboard.tudominio.com/fullchain.pem \
        /home/deploy/dashboardsonar-application-python/nginx/ssl/

sudo cp /etc/letsencrypt/live/dashboard.tudominio.com/privkey.pem \
        /home/deploy/dashboardsonar-application-python/nginx/ssl/

sudo chown -R deploy:deploy /home/deploy/dashboardsonar-application-python/nginx/ssl
```

---

### Renovación automática

```bash
# Test de renovación
sudo certbot renew --dry-run

# Crear cron job para renovación automática
sudo crontab -e

# Agregar línea (renovar cada día a las 2 AM):
0 2 * * * certbot renew --quiet && cp /etc/letsencrypt/live/dashboard.tudominio.com/*.pem /home/deploy/dashboardsonar-application-python/nginx/ssl/ && docker compose -f /home/deploy/dashboardsonar-application-python/docker-compose.yml restart nginx
```

---

## 💾 Backups Automatizados

### Script de backup PostgreSQL

**`scripts/backup.sh`**:
```bash
#!/bin/bash

# Configuración
BACKUP_DIR="/home/deploy/backups"
DB_CONTAINER="dashboardsonar-postgres"
DB_NAME="dashboardsonar"
DB_USER="dashboard_user"
RETENTION_DAYS=7

# Crear directorio de backups
mkdir -p $BACKUP_DIR

# Timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/dashboard_backup_$TIMESTAMP.sql.gz"

# Backup
docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Verificar éxito
if [ $? -eq 0 ]; then
    echo "✅ Backup exitoso: $BACKUP_FILE"
    # Eliminar backups antiguos
    find $BACKUP_DIR -name "dashboard_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
else
    echo "❌ Backup falló"
    exit 1
fi
```

**Hacer ejecutable**:
```bash
chmod +x scripts/backup.sh
```

---

### Programar backups con cron

```bash
crontab -e

# Backup diario a las 3 AM
0 3 * * * /home/deploy/dashboardsonar-application-python/scripts/backup.sh >> /home/deploy/backups/backup.log 2>&1
```

---

### Restore desde backup

```bash
# Restore desde archivo .sql.gz
gunzip -c /home/deploy/backups/dashboard_backup_20251217_030000.sql.gz | \
docker exec -i dashboardsonar-postgres psql -U dashboard_user dashboardsonar
```

---

## 📊 Monitoring con Prometheus

**`docker-compose.monitoring.yml`**:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "127.0.0.1:9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - dashboardsonar-network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=changeme
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - dashboardsonar-network

volumes:
  prometheus_data:
  grafana_data:

networks:
  dashboardsonar-network:
    external: true
```

**Iniciar monitoring**:
```bash
docker compose -f docker-compose.monitoring.yml up -d
```

**Acceder a Grafana**: `http://IP_SERVIDOR:3000` (admin/changeme)

---

## 🔄 CI/CD con GitHub Actions

**`.github/workflows/deploy-vm.yml`**:
```yaml
name: Deploy to VM

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy via SSH
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SSH_HOST }}
        username: ${{ secrets.SSH_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /home/deploy/dashboardsonar-application-python
          git pull origin main
          docker compose build
          docker compose up -d
          docker compose logs --tail=50
```

**Secrets en GitHub**:
- `SSH_HOST`: IP del servidor
- `SSH_USER`: `deploy`
- `SSH_PRIVATE_KEY`: Tu SSH private key

---

## 🔧 Troubleshooting

### Ver logs de contenedores

```bash
# Logs de todos los servicios
docker compose logs -f

# Logs de servicio específico
docker compose logs -f app

# Últimas 100 líneas
docker compose logs --tail=100 app
```

---

### Reiniciar servicios

```bash
# Reiniciar todo
docker compose restart

# Reiniciar solo app
docker compose restart app
```

---

### App no accesible

```bash
# Verificar contenedores corriendo
docker compose ps

# Verificar NGINX
curl http://localhost

# Verificar app directamente
curl http://localhost:5000/health

# Verificar firewall
sudo ufw status
```

---

**Última actualización**: Diciembre 2025
**Mantenido por**: Equipo DevOps
**Soporte**: devops@empresa.com
