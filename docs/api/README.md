# API Documentation

Documentación completa de todas las rutas y endpoints de Dashboard Sonar.

---

## 📚 Contenido

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentación completa de API
  - 40+ web routes (HTML endpoints)
  - 10+ API endpoints (JSON responses)
  - Autenticación y seguridad
  - Request/Response examples
  - Ejemplos de integración (curl, Python, bash)
  - Scripts de automatización y CI/CD

---

## 🚀 Inicio Rápido

### Endpoints Principales

#### Autenticación
- `POST /accounts/login` - Iniciar sesión
- `POST /accounts/register` - Registrar usuario
- `GET /accounts/logout` - Cerrar sesión

#### Dashboard
- `GET /` - Dashboard principal
- `GET /metricas` - Métricas generales
- `GET /stats` - Estadísticas

#### API (JSON)
- `GET /api/aplicacion/<name>` - Métricas de aplicación
- `GET /api/kpis` - Todos los KPIs
- `GET /api/daily/<aplicacion>` - Análisis diarios

Ver [API_DOCUMENTATION.md](API_DOCUMENTATION.md) para documentación completa.

---

## 🔗 Enlaces Relacionados

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Arquitectura del sistema
- [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) - Guía de desarrollo
- [DEPLOYMENT.md](../deployment/DEPLOYMENT.md) - Despliegue en producción

---

**Última actualización**: 2025-12-14
