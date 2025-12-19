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

# Verificar estado de la base de datos
docker-compose exec web python manage.py db-status

# Crear usuario admin (interactivo con validación)
docker-compose exec web python manage.py create-admin
```

### 5. Cargar Datos Iniciales (Opcional)

**Opción A: Datos de prueba (Desarrollo)**

```bash
# Cargar usuarios de prueba (rápido)
docker-compose exec web python manage.py seed-data --users 5

# Credenciales generadas:
# - admin@test.com / Admin123! (admin)
# - user1@test.com / User123!
# - user2@test.com / User123!
# ...
```

**Opción B: Datos reales desde CSV**

```bash
# Los archivos CSV ya están montados en ./datos (bind mount)
# No necesitas copiarlos, están disponibles automáticamente

# Ejecutar pipeline completo de carga de datos
docker-compose exec web python scripts/data/run_all_data_scripts.py

# O solo cargar datos sin generar snapshots/stats
docker-compose exec web python scripts/data/run_all_data_scripts.py --skip-daily --skip-stats --skip-registry

# O solo cargar datos CSV (sin procesamiento adicional)
docker-compose exec web python scripts/data/load_data.py
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

#### Iniciar Servicios

```bash
# Iniciar todos los servicios en background
docker-compose up -d

# Iniciar con logs visibles (foreground)
docker-compose up

# Iniciar solo servicios específicos
docker-compose up -d web db

# Iniciar con Nginx
docker-compose --profile with-nginx up -d
```

#### Parar Servicios

**Opción 1: Parar y mantener contenedores (pausa temporal)**

```bash
docker-compose stop
```
- ✅ Detiene los contenedores
- ❌ NO elimina contenedores
- ✅ Mantiene todos los datos
- 💡 Uso: Pausa temporal, reinicio rápido con `docker-compose start`

**Opción 2: Parar y eliminar contenedores (parada normal)** ⭐ **RECOMENDADO**

```bash
docker-compose down
```
- ✅ Detiene los contenedores
- ✅ Elimina los contenedores
- ✅ **Mantiene los volúmenes** (datos persistentes)
- ✅ Libera recursos de red
- 💡 Uso: Parada normal del día a día

**Opción 3: Parar y eliminar TODO** ⚠️ **CUIDADO - BORRA DATOS**

```bash
docker-compose down -v
```
- ✅ Detiene los contenedores
- ✅ Elimina los contenedores
- ❌ **ELIMINA VOLÚMENES** (¡pierdes base de datos!)
- 💡 Uso: Solo para limpieza completa o reset total

**Opción 4: Parar servicios específicos**

```bash
# Parar solo el servicio web
docker-compose stop web

# Parar solo la base de datos
docker-compose stop db

# Parar solo nginx
docker-compose stop nginx
```

#### Tabla Comparativa - Opciones de Parada

| Comando | Detiene | Elimina Contenedores | Elimina Volúmenes | Datos DB | Uso Recomendado |
|---------|---------|---------------------|-------------------|----------|-----------------|
| `stop` | ✅ | ❌ | ❌ | ✅ Persisten | Pausa temporal |
| `down` | ✅ | ✅ | ❌ | ✅ Persisten | **Parada normal** |
| `down -v` | ✅ | ✅ | ✅ | ❌ Se borran | Limpieza total |

#### Reiniciar Servicios

```bash
# Reiniciar todos los servicios
docker-compose restart

# Reiniciar servicio específico
docker-compose restart web
docker-compose restart db

# Parar, rebuild y reiniciar
docker-compose down
docker-compose up -d --build
```

#### Ver Estado y Logs

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de servicio específico
docker-compose logs -f web
docker-compose logs -f db

# Ver últimas 100 líneas de logs
docker-compose logs --tail=100 web
```

#### Flujo de Trabajo Típico

```bash
# 1. Iniciar servicios por primera vez
docker-compose up -d

# 2. Trabajar con la aplicación...

# 3. Ver logs si hay problemas
docker-compose logs -f web

# 4. Al finalizar el día, parar servicios
docker-compose down

# 5. Al día siguiente, volver a iniciar
docker-compose up -d
# ✅ Los datos persisten porque los volúmenes se mantienen
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
docker-compose exec web python manage.py create-admin
docker-compose exec web python scripts/data_pipeline.py

# Ver variables de entorno
docker-compose exec web env
```

### Comandos de Gestión (manage.py)

El nuevo `manage.py` incluye comandos mejorados para gestión de usuarios y base de datos:

#### Gestión de Usuarios

```bash
# Crear admin (con validación de email y contraseña)
docker-compose exec web python manage.py create-admin

# Listar todos los usuarios
docker-compose exec web python manage.py list-users

# Eliminar usuario
docker-compose exec web python manage.py delete-user --email user@example.com

# Promover usuario a admin
docker-compose exec web python manage.py make-admin --email user@example.com

# Resetear contraseña
docker-compose exec web python manage.py reset-password --email user@example.com

# Cargar usuarios de prueba (solo desarrollo)
docker-compose exec web python manage.py seed-data --users 10
```

#### Utilidades de Base de Datos

```bash
# Ver estado de la base de datos
docker-compose exec web python manage.py db-status
# Muestra: conexión, total usuarios, admins, versión SQLAlchemy

# Listar comandos disponibles
docker-compose exec web python manage.py commands
```

#### Validaciones Incluidas

El comando `create-admin` incluye validaciones:

**Email:**
- Formato válido (RFC compliant)
- Verifica duplicados

**Contraseña:**
- Mínimo 8 caracteres
- Al menos 1 mayúscula
- Al menos 1 minúscula
- Al menos 1 dígito

**Manejo de Errores:**
- Rollback automático si falla
- Mensajes claros de error
- Colores en terminal para mejor UX

### Gestión de Logs

Los logs se almacenan en un volumen Docker (`app_logs`) para evitar problemas de permisos.

```bash
# Ver logs de la aplicación en tiempo real
docker-compose exec web tail -f /app/logs/info.log

# Ver todos los archivos de log
docker-compose exec web ls -la /app/logs

# Leer log completo
docker-compose exec web cat /app/logs/info.log

# Copiar logs al host (backup)
docker cp dashboardsonar-web:/app/logs ./logs-backup

# Ver ubicación del volumen en el host
docker volume inspect dashboardsonar-application-python_app_logs

# Limpiar logs antiguos (dentro del contenedor)
docker-compose exec web sh -c "find /app/logs -name '*.log' -mtime +7 -delete"
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
