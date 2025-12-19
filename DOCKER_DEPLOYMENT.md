# Docker Deployment Guide

Este documento describe cómo desplegar la aplicación Dashboard SonarQube utilizando Docker y Docker Compose.

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Arquitectura](#arquitectura)
3. [Configuración Rápida](#configuración-rápida)
4. [Configuración Detallada](#configuración-detallada)
5. [Comandos Docker](#comandos-docker)
6. [Configuración con Nginx](#configuración-con-nginx)
7. [Troubleshooting](#troubleshooting)
8. [Seguridad](#seguridad)

---

## Requisitos Previos

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB de RAM mínimo
- 5GB de espacio en disco

**Verificar instalación:**

```bash
docker --version
docker-compose --version
```

---

## Arquitectura

El despliegue Docker incluye:

```
┌─────────────────────────────────────────────┐
│  Nginx (Reverse Proxy - Opcional)          │
│  Puerto: 80, 443                            │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│  Flask Application (Gunicorn)               │
│  Puerto: 5000                               │
│  Workers: 4                                 │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│  PostgreSQL Database                        │
│  Puerto: 5432 (interno)                     │
│  Volume: postgres_data                      │
└─────────────────────────────────────────────┘
```

### Componentes:

1. **Web (Flask + Gunicorn)**
   - Aplicación Flask con servidor WSGI Gunicorn
   - 4 workers por defecto
   - Health check cada 30s
   - Volúmenes para datos y logs

2. **Database (PostgreSQL 16)**
   - Base de datos PostgreSQL
   - Datos persistentes en volumen Docker
   - Health check automático

3. **Nginx (Opcional)**
   - Reverse proxy
   - Servir archivos estáticos
   - Compresión Gzip
   - Headers de seguridad

---

## Configuración Rápida

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd dashboardsonar-application-python
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.docker .env

# Editar y actualizar valores (especialmente SECRET_KEY)
nano .env
```

**CRÍTICO:** Generar SECRET_KEY segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Actualizar `SECRET_KEY` en `.env` con el valor generado.

### 3. Iniciar Servicios

```bash
# Sin Nginx (solo app + database)
docker-compose up -d

# Con Nginx (app + database + nginx)
docker-compose --profile with-nginx up -d
```

### 4. Inicializar Base de Datos

```bash
# Ejecutar migraciones
docker-compose exec web flask db upgrade

# Crear usuario admin (opcional)
docker-compose exec web python manage.py create_admin
```

### 5. Cargar Datos Iniciales (Opcional)

```bash
# Copiar archivos CSV al contenedor
docker cp datos/metricas.csv dashboardsonar-web:/app/datos/
docker cp datos/historico.csv dashboardsonar-web:/app/datos/
docker cp datos/proveedores.csv dashboardsonar-web:/app/datos/

# Ejecutar pipeline de carga
docker-compose exec web python scripts/data_pipeline.py
```

### 6. Acceder a la Aplicación

- **Sin Nginx:** http://localhost:5000
- **Con Nginx:** http://localhost
- **Health Check:** http://localhost:5000/health

---

## Configuración Detallada

### Variables de Entorno (.env)

```env
# Flask
DEBUG=False
TESTING=False
PORT=5000

# Security
SECRET_KEY=<genera-una-clave-segura-aqui>

# Database
DB_ENGINE=postgresql
DB_HOST=db
DB_PORT=5432
DB_NAME=dashboardsonar
DB_USERNAME=postgres
DB_PASS=<password-seguro>

# Application
ASSETS_ROOT=/static/assets
DAYS_COMPARISON=15

# Data Files
DATA_DIR=./datos
METRICAS_FILENAME=metricas.csv
HISTORICO_FILENAME=historico.csv
PROVEEDORES_FILENAME=proveedores.csv

# Logging
LOG_LEVEL=INFO
```

### Personalizar Configuración

#### Cambiar Puerto de la Aplicación

Editar `.env`:

```env
PORT=8080
```

Actualizar `docker-compose.yml`:

```yaml
services:
  web:
    ports:
      - "8080:5000"  # host:container
```

#### Ajustar Workers de Gunicorn

Editar `Dockerfile`, modificar CMD:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", ...]
```

#### Configurar Memoria y CPU

Editar `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

---

## Comandos Docker

### Gestión de Servicios

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Borra datos)
docker-compose down -v

# Ver logs
docker-compose logs -f

# Ver logs de servicio específico
docker-compose logs -f web

# Reiniciar servicio
docker-compose restart web

# Ver estado
docker-compose ps
```

### Build y Rebuild

```bash
# Build inicial
docker-compose build

# Rebuild sin caché (fuerza rebuild completo)
docker-compose build --no-cache

# Rebuild y reiniciar
docker-compose up -d --build
```

### Ejecutar Comandos en Contenedor

```bash
# Shell interactivo
docker-compose exec web bash

# Comandos Flask
docker-compose exec web flask db upgrade
docker-compose exec web flask db migrate -m "descripción"

# Python scripts
docker-compose exec web python manage.py create_admin
docker-compose exec web python scripts/data_pipeline.py

# Ver variables de entorno
docker-compose exec web env
```

### Gestión de Base de Datos

```bash
# Backup
docker-compose exec db pg_dump -U postgres dashboardsonar > backup.sql

# Restore
docker-compose exec -T db psql -U postgres dashboardsonar < backup.sql

# Conectar a PostgreSQL
docker-compose exec db psql -U postgres -d dashboardsonar
```

### Monitorización

```bash
# Ver recursos
docker stats

# Ver logs en tiempo real
docker-compose logs -f --tail=100

# Inspeccionar contenedor
docker-compose exec web ps aux
docker-compose exec web df -h
```

---

## Configuración con Nginx

### Activar Nginx

```bash
docker-compose --profile with-nginx up -d
```

### Configuración SSL (HTTPS)

1. **Obtener Certificados SSL**

```bash
# Usando Let's Encrypt (ejemplo)
certbot certonly --standalone -d tu-dominio.com
```

2. **Copiar Certificados al Proyecto**

```bash
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem nginx/ssl/key.pem
```

3. **Descomentar Configuración HTTPS**

Editar `nginx/conf.d/app.conf` y descomentar sección HTTPS.

4. **Actualizar docker-compose.yml**

```yaml
services:
  nginx:
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
```

5. **Reiniciar Nginx**

```bash
docker-compose restart nginx
```

### Servir Archivos Estáticos

Nginx está configurado para servir archivos estáticos desde `/static/`:

```nginx
location /static/ {
    alias /usr/share/nginx/html/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Troubleshooting

### Problema: Contenedor web no inicia

**Síntoma:**

```bash
docker-compose ps
# web    Exit 1
```

**Solución:**

```bash
# Ver logs completos
docker-compose logs web

# Problemas comunes:
# 1. SECRET_KEY no configurada
# 2. Database no disponible
# 3. Puerto 5000 ocupado
```

### Problema: Database connection refused

**Síntoma:**

```
psycopg2.OperationalError: could not connect to server
```

**Solución:**

```bash
# Verificar que DB está running
docker-compose ps db

# Reiniciar DB
docker-compose restart db

# Verificar health check
docker-compose exec db pg_isready -U postgres
```

### Problema: Health check failing

**Síntoma:**

```bash
docker-compose ps
# web    unhealthy
```

**Solución:**

```bash
# Test manual del health check
curl http://localhost:5000/health

# Ver logs específicos
docker-compose logs --tail=50 web

# Verificar conectividad a DB
docker-compose exec web python -c "from infocodest.extensions import db; db.session.execute(db.text('SELECT 1'))"
```

### Problema: Puerto ya en uso

**Síntoma:**

```
Error: Bind for 0.0.0.0:5000 failed: port is already allocated
```

**Solución:**

```bash
# Cambiar puerto en .env
PORT=8080

# Actualizar docker-compose.yml
ports:
  - "8080:5000"
```

### Problema: Volúmenes no persisten datos

**Solución:**

```bash
# Ver volúmenes
docker volume ls

# Inspeccionar volumen
docker volume inspect dashboardsonar-application-python_postgres_data

# Backup manual
docker run --rm -v dashboardsonar-application-python_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

---

## Seguridad

### Checklist de Seguridad

- [ ] **SECRET_KEY generada y única** (no usar valor por defecto)
- [ ] **Contraseñas de DB seguras** (min. 16 caracteres)
- [ ] **DEBUG=False en producción**
- [ ] **SSL/TLS configurado** (HTTPS)
- [ ] **Firewall configurado** (solo puertos necesarios)
- [ ] **Volúmenes con backups regulares**
- [ ] **Logs monitorizados** (errores y accesos)
- [ ] **Contenedores actualizados** (imágenes base)

### Generar Contraseñas Seguras

```bash
# SECRET_KEY (64 caracteres hex)
python -c "import secrets; print(secrets.token_hex(32))"

# Password (32 caracteres alfanuméricos)
python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))"
```

### Actualizar Imágenes Base

```bash
# Pull latest images
docker-compose pull

# Rebuild y reiniciar
docker-compose up -d --build
```

### Restringir Acceso a Red

```bash
# En docker-compose.yml, limitar puertos expuestos
services:
  db:
    # NO exponer puerto 5432 externamente
    # ports:  # Comentar esta sección
```

### Backups Automáticos

Crear script `backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres dashboardsonar > backup_${DATE}.sql
gzip backup_${DATE}.sql
find . -name "backup_*.sql.gz" -mtime +7 -delete  # Mantener 7 días
```

Configurar cron:

```bash
# Backup diario a las 2 AM
0 2 * * * /path/to/backup.sh
```

---

## Despliegue en Producción

### Pre-requisitos Adicionales

1. **Dominio configurado** con DNS apuntando al servidor
2. **Certificado SSL** (Let's Encrypt recomendado)
3. **Firewall** configurado (solo 80, 443, 22)
4. **Backups** configurados y probados
5. **Monitoring** (opcional: Prometheus, Grafana)

### Pasos Recomendados

1. Configurar `.env` con valores de producción
2. Generar SECRET_KEY único
3. Configurar SSL en Nginx
4. Iniciar con `--profile with-nginx`
5. Probar health checks
6. Configurar backups automáticos
7. Configurar logs externos (opcional)
8. Monitorizar recursos

### Variables de Producción Recomendadas

```env
DEBUG=False
TESTING=False
LOG_LEVEL=WARNING
DB_PASS=<password-muy-seguro>
SECRET_KEY=<clave-unica-64-chars>
```

---

## Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)

---

Generated with [Claude Code](https://claude.com/claude-code)
