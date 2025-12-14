# Deployment Documentation

Guías y recursos para desplegar Dashboard Sonar en producción.

---

## 📚 Contenido

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guía completa de despliegue
  - Docker deployment (Compose y simple)
  - Gunicorn + Nginx deployment
  - Cloud deployments (AWS, Azure, GCP)
  - Database setup (PostgreSQL, MySQL)
  - Security configuration (SSL, firewall, fail2ban)
  - Monitoring y logging
  - Backup y recuperación
  - Troubleshooting

- **[examples/](examples/)** - Archivos de configuración de ejemplo
  - docker-compose.yml
  - Dockerfile
  - nginx.conf
  - gunicorn.conf.py

---

## 🚀 Inicio Rápido

### Opción 1: Docker Compose (Recomendado)

```bash
# Ver ejemplos en examples/
cp examples/docker-compose.yml .
cp examples/.env.example .env
# Editar .env con tus valores
docker-compose up -d
```

### Opción 2: Gunicorn + Nginx

```bash
# Ver guía completa en DEPLOYMENT.md
# Sección: "Despliegue con Gunicorn + Nginx"
```

### Opción 3: Cloud

Ver secciones específicas en [DEPLOYMENT.md](DEPLOYMENT.md):
- AWS (EC2 + RDS)
- Azure (App Service + PostgreSQL)
- Google Cloud (Cloud Run + Cloud SQL)

---

## 📋 Checklist de Despliegue

Antes de desplegar:

- [ ] Servidor provisionado
- [ ] PostgreSQL instalado y configurado
- [ ] `.env` configurado con valores de producción
- [ ] SECRET_KEY generada y segura
- [ ] Migraciones ejecutadas
- [ ] Usuario admin creado
- [ ] SSL certificate instalado
- [ ] Firewall configurado
- [ ] Backups automatizados configurados

Ver checklist completo en [DEPLOYMENT.md](DEPLOYMENT.md#-checklist-de-despliegue).

---

## 🔗 Enlaces Relacionados

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Arquitectura del sistema
- [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) - Desarrollo local
- [API_DOCUMENTATION.md](../api/API_DOCUMENTATION.md) - Documentación de API

---

**Última actualización**: 2025-12-14
