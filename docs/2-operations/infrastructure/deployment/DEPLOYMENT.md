# Guía de Despliegue - Dashboard Sonar

Guía completa para desplegar Dashboard Sonar en entornos de producción.

---

## 📋 Tabla de Contenidos

1. [Prerequisitos](#prerequisitos)
2. [Configuración de Entornos](#configuración-de-entornos)
3. [Despliegue con Docker](#despliegue-con-docker)
4. [Despliegue con Gunicorn + Nginx](#despliegue-con-gunicorn--nginx)
5. [Despliegue en Cloud](#despliegue-en-cloud)
6. [Base de Datos](#base-de-datos)
7. [Seguridad](#seguridad)
8. [Monitoreo](#monitoreo)
9. [Backup y Recuperación](#backup-y-recuperación)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisitos

### Requisitos del Sistema

#### Mínimo (Desarrollo/Testing)
```text
- CPU: 2 cores
- RAM: 2 GB
- Disco: 10 GB
- OS: Ubuntu 20.04+, CentOS 7+, o equivalente
```

#### Recomendado (Producción)
```text
- CPU: 4+ cores
- RAM: 4+ GB
- Disco: 20+ GB SSD
- OS: Ubuntu 22.04 LTS, RHEL 8+
```

### Software Requerido

```bash
# Python
python3.10 o superior

# Base de datos
PostgreSQL 13+ (recomendado para producción)
MySQL 8.0+ (alternativa)
SQLite 3 (solo desarrollo)

# Servidor Web
Nginx 1.18+
Gunicorn 20.1+

# Otros
Git 2.30+
pip 21.0+
```

---

## ⚙️ Configuración de Entornos

### 1. Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```bash
# .env.production
# =================

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-min-32-chars-please-change-this

# Database (PostgreSQL)
DATABASE_URL=postgresql://dbuser:dbpassword@localhost:5432/dashboardsonar
SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_ECHO=False

# Server
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/dashboardsonar/app.log

# CORS (si aplica)
CORS_ORIGINS=https://dashboard.example.com

# Workers (Gunicorn)
WORKERS=4
WORKER_CLASS=sync
WORKER_CONNECTIONS=1000
TIMEOUT=30
KEEPALIVE=5
```

### 2. Generar SECRET_KEY Segura

```python
# generate_secret.py
import secrets
print(secrets.token_urlsafe(32))
```

```bash
python3 generate_secret.py
# Output: WkB3Yr5d9QJ8F2xN7Km4Lp1Sq6Ht8Vz3Jn0Mg5Rc2Wf
```

### 3. Configuración por Entorno

```python
# config.py (ejemplo mejorado)
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///dev.db'
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ECHO = False

    # Validar que SECRET_KEY esté configurada
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## 🐳 Despliegue con Docker

### Opción 1: Docker Compose (Recomendado)

#### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: dashboardsonar-web
    restart: always
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://dbuser:dbpassword@db:5432/dashboardsonar
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    volumes:
      - ./logs:/var/log/dashboardsonar
    networks:
      - dashboardsonar-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    container_name: dashboardsonar-db
    restart: always
    environment:
      - POSTGRES_USER=dbuser
      - POSTGRES_PASSWORD=dbpassword
      - POSTGRES_DB=dashboardsonar
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - dashboardsonar-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dbuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: dashboardsonar-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    networks:
      - dashboardsonar-network

volumes:
  postgres-data:

networks:
  dashboardsonar-network:
    driver: bridge
```

#### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create log directory
RUN mkdir -p /var/log/dashboardsonar

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /var/log/dashboardsonar
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "30", "run:app"]
```

#### .dockerignore

```text
# .dockerignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv
.env
.env.local
.git/
.gitignore
*.md
!README.md
.pytest_cache/
.coverage
htmlcov/
*.log
*.db
*.sqlite
.DS_Store
```

#### Comandos de Despliegue

```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f web

# 5. Run migrations
docker-compose exec web flask db upgrade

# 6. Create admin user
docker-compose exec web python create_admin.py

# 7. Stop services
docker-compose down

# 8. Stop and remove volumes
docker-compose down -v
```

### Opción 2: Docker Simple

```bash
# Build
docker build -t dashboardsonar:latest .

# Run
docker run -d \
  --name dashboardsonar \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e SECRET_KEY=your-secret-key \
  dashboardsonar:latest

# Check logs
docker logs -f dashboardsonar

# Stop
docker stop dashboardsonar
docker rm dashboardsonar
```

---

## 🚀 Despliegue con Gunicorn + Nginx

### 1. Instalación en Servidor Ubuntu

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3.10 python3-pip python3-venv \
  postgresql postgresql-contrib nginx git

# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash dashboardsonar
sudo su - dashboardsonar
```

### 2. Clonar y Configurar Aplicación

```bash
# Como usuario dashboardsonar
cd /home/dashboardsonar

# Clonar repositorio
git clone https://github.com/jfdelafuente/dashboardsonar-application-python.git app
cd app

# Crear virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Configurar environment
cp .env.example .env
nano .env  # Editar con valores de producción

# Ejecutar migraciones
flask db upgrade

# Crear usuario admin
python create_admin.py
```

### 3. Configurar Gunicorn

#### gunicorn.conf.py

```python
# /home/dashboardsonar/app/gunicorn.conf.py
import multiprocessing

# Server socket
bind = '127.0.0.1:5000'
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/dashboardsonar/access.log'
errorlog = '/var/log/dashboardsonar/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'dashboardsonar'

# Server mechanics
daemon = False
pidfile = '/var/run/dashboardsonar/dashboardsonar.pid'
user = 'dashboardsonar'
group = 'dashboardsonar'

# SSL (si aplica)
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'
```

### 4. Systemd Service

#### /etc/systemd/system/dashboardsonar.service

```ini
[Unit]
Description=Dashboard Sonar Gunicorn Application
After=network.target postgresql.service

[Service]
Type=notify
User=dashboardsonar
Group=dashboardsonar
WorkingDirectory=/home/dashboardsonar/app
Environment="PATH=/home/dashboardsonar/app/venv/bin"
EnvironmentFile=/home/dashboardsonar/app/.env
ExecStart=/home/dashboardsonar/app/venv/bin/gunicorn \
    --config /home/dashboardsonar/app/gunicorn.conf.py \
    run:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Comandos Systemd

```bash
# Crear directorios de logs
sudo mkdir -p /var/log/dashboardsonar /var/run/dashboardsonar
sudo chown dashboardsonar:dashboardsonar /var/log/dashboardsonar /var/run/dashboardsonar

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable dashboardsonar

# Start service
sudo systemctl start dashboardsonar

# Check status
sudo systemctl status dashboardsonar

# View logs
sudo journalctl -u dashboardsonar -f

# Restart
sudo systemctl restart dashboardsonar

# Stop
sudo systemctl stop dashboardsonar
```

### 5. Configurar Nginx

#### /etc/nginx/sites-available/dashboardsonar

```nginx
# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name dashboard.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dashboard.example.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/dashboard.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard.example.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/dashboard.example.com/chain.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logging
    access_log /var/log/nginx/dashboardsonar_access.log;
    error_log /var/log/nginx/dashboardsonar_error.log;

    # Max upload size
    client_max_body_size 10M;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 256;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Static files
    location /static {
        alias /home/dashboardsonar/app/infocodest/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
```

#### Activar Sitio

```bash
# Link configuration
sudo ln -s /etc/nginx/sites-available/dashboardsonar /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Enable Nginx
sudo systemctl enable nginx
```

### 6. SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d dashboard.example.com

# Renovación automática (ya configurada)
sudo certbot renew --dry-run

# Ver estado de renovación
sudo systemctl status certbot.timer
```

---

## ☁️ Despliegue en Cloud

### AWS (EC2 + RDS)

#### 1. Crear EC2 Instance

```bash
# Instance type: t3.medium (2 vCPU, 4GB RAM)
# AMI: Ubuntu 22.04 LTS
# Storage: 20GB gp3
# Security Group:
#   - SSH (22) from your IP
#   - HTTP (80) from 0.0.0.0/0
#   - HTTPS (443) from 0.0.0.0/0
```

#### 2. Crear RDS PostgreSQL

```bash
# Engine: PostgreSQL 15
# Instance class: db.t3.micro (dev) / db.t3.small (prod)
# Storage: 20GB gp3
# VPC: Same as EC2
# Security Group: PostgreSQL (5432) from EC2 security group
```

#### 3. Configurar Aplicación

```bash
# SSH to EC2
ssh -i key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# Set DATABASE_URL
export DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/dashboardsonar

# Follow Gunicorn + Nginx steps above
```

#### 4. Configurar Auto Scaling (Opcional)

- Create AMI from configured EC2
- Create Launch Template
- Create Auto Scaling Group (min: 2, max: 4)
- Create Application Load Balancer
- Configure health checks

### Azure (App Service + PostgreSQL)

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name dashboardsonar-rg --location eastus

# Create PostgreSQL
az postgres flexible-server create \
  --resource-group dashboardsonar-rg \
  --name dashboardsonar-db \
  --location eastus \
  --admin-user dbadmin \
  --admin-password <password> \
  --sku-name Standard_B1ms \
  --version 15

# Create App Service
az webapp up \
  --resource-group dashboardsonar-rg \
  --name dashboardsonar \
  --runtime "PYTHON:3.10" \
  --sku B1

# Configure environment variables
az webapp config appsettings set \
  --resource-group dashboardsonar-rg \
  --name dashboardsonar \
  --settings FLASK_ENV=production \
    DATABASE_URL=<connection-string> \
    SECRET_KEY=<secret-key>

# Deploy
git push azure main
```

### Google Cloud (Cloud Run + Cloud SQL)

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Login
gcloud auth login

# Create Cloud SQL instance
gcloud sql instances create dashboardsonar-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Build and deploy
gcloud run deploy dashboardsonar \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_ENV=production,DATABASE_URL=<connection-string>
```

---

## 🗄️ Base de Datos

### PostgreSQL (Recomendado)

#### Instalación

```bash
# Ubuntu
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Configuración

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE dashboardsonar;
CREATE USER dbuser WITH ENCRYPTED PASSWORD 'dbpassword';
GRANT ALL PRIVILEGES ON DATABASE dashboardsonar TO dbuser;

# Exit
\q
```

#### Connection String

```text
postgresql://dbuser:dbpassword@localhost:5432/dashboardsonar
```

#### Backup

```bash
# Backup
pg_dump -U dbuser -h localhost dashboardsonar > backup_$(date +%Y%m%d).sql

# Restore
psql -U dbuser -h localhost dashboardsonar < backup_20240115.sql

# Automated daily backup (cron)
0 2 * * * pg_dump -U dbuser dashboardsonar | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
```

### MySQL (Alternativa)

```bash
# Install
sudo apt install mysql-server

# Secure installation
sudo mysql_secure_installation

# Create database
sudo mysql
CREATE DATABASE dashboardsonar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dbuser'@'localhost' IDENTIFIED BY 'dbpassword';
GRANT ALL PRIVILEGES ON dashboardsonar.* TO 'dbuser'@'localhost';
FLUSH PRIVILEGES;
```

#### Connection String

```text
mysql://dbuser:dbpassword@localhost:3306/dashboardsonar
```

---

## 🔒 Seguridad

### 1. Firewall (UFW)

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow PostgreSQL (only from app server)
sudo ufw allow from <app-server-ip> to any port 5432

# Check status
sudo ufw status
```

### 2. Fail2Ban

```bash
# Install
sudo apt install fail2ban

# Configure
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
```

```bash
# Start
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

### 3. Security Headers (ya en Nginx)

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

### 4. Rate Limiting (Nginx)

```nginx
# En http block
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# En location block
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    # ... proxy pass ...
}
```

### 5. Database Security

```bash
# PostgreSQL - Restrict connections
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

```text
# Only allow local connections
host    dashboardsonar    dbuser    127.0.0.1/32    md5
```

---

## 📊 Monitoreo

### 1. Logs

```bash
# Application logs
tail -f /var/log/dashboardsonar/app.log

# Nginx logs
tail -f /var/log/nginx/dashboardsonar_access.log
tail -f /var/log/nginx/dashboardsonar_error.log

# Gunicorn logs
sudo journalctl -u dashboardsonar -f

# System logs
sudo tail -f /var/log/syslog
```

### 2. Monitoring con Prometheus + Grafana (Opcional)

#### Exponer métricas Flask

```python
# requirements.txt
prometheus-flask-exporter==0.22.3

# app.py
from prometheus_flask_exporter import PrometheusMetrics

app = create_app()
metrics = PrometheusMetrics(app)
```

#### docker-compose.monitoring.yml

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  grafana-data:
```

### 3. Uptime Monitoring

- UptimeRobot (gratuito)
- Pingdom
- StatusCake

---

## 💾 Backup y Recuperación

### Script de Backup Automatizado

```bash
#!/bin/bash
# /home/dashboardsonar/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/dashboardsonar"
APP_DIR="/home/dashboardsonar/app"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U dbuser dashboardsonar | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Application backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C /home/dashboardsonar app

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
chmod +x /home/dashboardsonar/backup.sh

# Cron (daily at 2 AM)
crontab -e
0 2 * * * /home/dashboardsonar/backup.sh >> /var/log/dashboardsonar/backup.log 2>&1
```

### Recuperación

```bash
# Restore database
gunzip -c /backups/dashboardsonar/db_20240115.sql.gz | psql -U dbuser dashboardsonar

# Restore application
tar -xzf /backups/dashboardsonar/app_20240115.tar.gz -C /home/dashboardsonar
sudo systemctl restart dashboardsonar
```

---

## 🔧 Troubleshooting

### Problema: Aplicación no inicia

```bash
# Check service status
sudo systemctl status dashboardsonar

# Check logs
sudo journalctl -u dashboardsonar -n 50

# Check Gunicorn manually
cd /home/dashboardsonar/app
source venv/bin/activate
gunicorn --bind 127.0.0.1:5000 run:app

# Common issues:
# - Wrong DATABASE_URL
# - Missing SECRET_KEY
# - Port already in use
# - Permission issues
```

### Problema: 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status dashboardsonar

# Check Nginx upstream
sudo nginx -t

# Check logs
tail -f /var/log/nginx/dashboardsonar_error.log

# Test upstream manually
curl http://127.0.0.1:5000/
```

### Problema: Database Connection Error

```bash
# Test connection
psql -U dbuser -h localhost -d dashboardsonar

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Problema: High Memory Usage

```bash
# Check memory
free -h

# Check processes
top
htop

# Reduce Gunicorn workers
# Edit gunicorn.conf.py: workers = 2

# Restart
sudo systemctl restart dashboardsonar
```

### Problema: SSL Certificate Issues

```bash
# Renew certificate manually
sudo certbot renew

# Check certificate expiry
sudo certbot certificates

# Test SSL configuration
sudo nginx -t
```

---

## 📋 Checklist de Despliegue

### Pre-Deployment

- [ ] Revisar código en develop
- [ ] Ejecutar todos los tests: `pytest`
- [ ] Verificar cobertura: `pytest --cov`
- [ ] Ejecutar linters: `black`, `flake8`, `isort`
- [ ] Actualizar `requirements.txt`
- [ ] Revisar CHANGELOG
- [ ] Tag de versión en git

### Deployment

- [ ] Servidor provisionado
- [ ] PostgreSQL instalado y configurado
- [ ] `.env` configurado con valores de producción
- [ ] SECRET_KEY generada y segura
- [ ] Database migraciones ejecutadas
- [ ] Usuario admin creado
- [ ] Gunicorn configurado
- [ ] Systemd service configurado
- [ ] Nginx configurado
- [ ] SSL certificate instalado
- [ ] Firewall configurado
- [ ] Fail2Ban configurado
- [ ] Backups automatizados configurados

### Post-Deployment

- [ ] Verificar aplicación funciona
- [ ] Verificar HTTPS funciona
- [ ] Verificar login funciona
- [ ] Verificar base de datos conecta
- [ ] Verificar logs se escriben correctamente
- [ ] Configurar monitoreo de uptime
- [ ] Configurar alertas
- [ ] Documentar credenciales en vault
- [ ] Notificar a equipo de deploy exitoso

---

## 📚 Referencias

- [Flask Deployment Options](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Última actualización**: 2025-12-14
**Versión**: v1.10.0-phase-10
**Mantenedor**: Dashboard Sonar Team
