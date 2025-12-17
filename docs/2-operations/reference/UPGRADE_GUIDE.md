# Upgrade Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, System Administrators
**Propósito**: Guía para actualizar Dashboard Sonar entre versiones

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Pre-Upgrade Checklist](#pre-upgrade-checklist)
3. [Upgrade Procedures](#upgrade-procedures)
4. [Post-Upgrade Verification](#post-upgrade-verification)
5. [Rollback Procedures](#rollback-procedures)
6. [Version-Specific Notes](#version-specific-notes)
7. [Breaking Changes](#breaking-changes)

---

## 🎯 Introducción

### Versioning Strategy

Dashboard Sonar sigue **Semantic Versioning** (SemVer):

```
MAJOR.MINOR.PATCH (ejemplo: 1.10.2)

MAJOR: Cambios incompatibles (breaking changes)
MINOR: Nueva funcionalidad backward-compatible
PATCH: Bug fixes backward-compatible
```

### Frecuencia de Releases

| Tipo | Frecuencia | Ejemplo |
|------|------------|---------|
| **Patch** | Cada 2-4 semanas | 1.10.0 → 1.10.1 |
| **Minor** | Cada 2-3 meses | 1.10.0 → 1.11.0 |
| **Major** | Cada 1-2 años | 1.10.0 → 2.0.0 |

### Canales de Release

| Canal | Descripción | Para |
|-------|-------------|------|
| **Stable** | Producción | Todos los usuarios |
| **Beta** | Testing pre-release | Early adopters |
| **Dev** | Desarrollo activo | Contribuidores |

---

## ✅ Pre-Upgrade Checklist

### 1. Planning

**30 días antes del upgrade**:

- [ ] Leer [CHANGELOG.md](../../../CHANGELOG.md) para la nueva versión
- [ ] Revisar [Breaking Changes](#breaking-changes) si es MAJOR update
- [ ] Verificar compatibilidad de dependencias (Python, PostgreSQL)
- [ ] Planificar ventana de mantenimiento (2-4 horas recomendado)
- [ ] Notificar a stakeholders

**1 semana antes**:

- [ ] Realizar upgrade en entorno de staging
- [ ] Ejecutar tests de integración en staging
- [ ] Documentar cualquier issue encontrado
- [ ] Preparar plan de rollback

**1 día antes**:

- [ ] Verificar backups recientes (< 24 horas)
- [ ] Confirmar que backup es restaurable
- [ ] Verificar espacio en disco (>20% libre)
- [ ] Notificación final a usuarios

---

### 2. Backup Critical Data

```bash
#!/bin/bash
# pre_upgrade_backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/pre_upgrade_$DATE"

mkdir -p $BACKUP_DIR

echo "=== Pre-Upgrade Backup ==="

# 1. Database backup
echo "[1/4] Backing up database..."
pg_dump -h localhost -U dashboard_user -d dashboardsonar \
  -F c -f $BACKUP_DIR/database.backup

# 2. Application code
echo "[2/4] Backing up application..."
tar -czf $BACKUP_DIR/application.tar.gz /opt/dashboardsonar

# 3. Configuration files
echo "[3/4] Backing up configuration..."
cp /opt/dashboardsonar/.env $BACKUP_DIR/.env.backup
cp /etc/systemd/system/dashboardsonar.service $BACKUP_DIR/dashboardsonar.service.backup

# 4. Nginx config
echo "[4/4] Backing up nginx config..."
cp /etc/nginx/sites-available/dashboardsonar $BACKUP_DIR/nginx-dashboardsonar.backup

echo ""
echo "✅ Backup completado en: $BACKUP_DIR"
echo "Tamaño total:"
du -sh $BACKUP_DIR
```

---

### 3. Environment Verification

```bash
#!/bin/bash
# verify_environment.sh

echo "=== Environment Verification ==="

# Python version
echo "Python version:"
python3 --version
# Requerido: Python 3.12+

# PostgreSQL version
echo "PostgreSQL version:"
psql --version
# Requerido: PostgreSQL 13+

# Disk space
echo "Disk space:"
df -h / | awk 'NR==2 {print "Used: "$5" - Available: "$4}'
# Requerido: >20% free

# Memory
echo "Memory:"
free -h | awk 'NR==2 {print "Available: "$7}'
# Requerido: >2GB free

# Check services
echo "Services status:"
systemctl is-active dashboardsonar
systemctl is-active postgresql
systemctl is-active nginx
```

---

## 🔄 Upgrade Procedures

### Patch Update (1.10.0 → 1.10.1)

**Duración**: ~10 minutos
**Downtime**: ~2 minutos
**Riesgo**: Bajo

```bash
#!/bin/bash
# upgrade_patch.sh

echo "=== Patch Upgrade: v1.10.0 → v1.10.1 ==="

# 1. Detener aplicación
echo "[1/6] Stopping application..."
sudo systemctl stop dashboardsonar

# 2. Backup (ya hecho en pre-upgrade)
echo "[2/6] Backup already completed in pre-upgrade"

# 3. Pull latest code
echo "[3/6] Pulling latest code..."
cd /opt/dashboardsonar
git fetch --tags
git checkout v1.10.1

# 4. Update dependencies
echo "[4/6] Updating dependencies..."
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 5. Run migrations (si las hay)
echo "[5/6] Running migrations..."
flask db upgrade

# 6. Restart application
echo "[6/6] Restarting application..."
sudo systemctl start dashboardsonar

# Verify
sleep 5
curl -f http://localhost:5000/health || echo "❌ Health check failed!"

echo "✅ Patch upgrade complete"
```

---

### Minor Update (1.10.0 → 1.11.0)

**Duración**: ~30 minutos
**Downtime**: ~10 minutos
**Riesgo**: Medio

```bash
#!/bin/bash
# upgrade_minor.sh

echo "=== Minor Upgrade: v1.10.0 → v1.11.0 ==="

# 1. Enable maintenance mode
echo "[1/8] Enabling maintenance mode..."
# Opcional: mostrar página de mantenimiento en Nginx
sudo cp /opt/dashboardsonar/maintenance.html /var/www/html/
sudo systemctl reload nginx

# 2. Detener aplicación
echo "[2/8] Stopping application..."
sudo systemctl stop dashboardsonar

# 3. Pull latest code
echo "[3/8] Pulling latest code..."
cd /opt/dashboardsonar
git fetch --tags
git checkout v1.11.0

# 4. Update dependencies
echo "[4/8] Updating dependencies..."
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 5. Check for breaking changes in .env
echo "[5/8] Checking configuration..."
# Revisar CHANGELOG para nuevas variables de entorno
# Ejemplo: si v1.11.0 requiere FEATURE_FLAGS=true
if ! grep -q "FEATURE_FLAGS" .env; then
    echo "⚠️  Adding new env var: FEATURE_FLAGS"
    echo "FEATURE_FLAGS=true" >> .env
fi

# 6. Run database migrations
echo "[6/8] Running database migrations..."
flask db upgrade

# 7. Restart application
echo "[7/8] Restarting application..."
sudo systemctl start dashboardsonar

# 8. Verify and disable maintenance
echo "[8/8] Verifying..."
sleep 10
if curl -f http://localhost:5000/health; then
    echo "✅ Health check passed"
    sudo rm /var/www/html/maintenance.html
    sudo systemctl reload nginx
    echo "✅ Minor upgrade complete"
else
    echo "❌ Health check failed - See rollback procedure"
    exit 1
fi
```

---

### Major Update (1.x.x → 2.0.0)

**Duración**: 1-2 horas
**Downtime**: ~30 minutos
**Riesgo**: Alto

```bash
#!/bin/bash
# upgrade_major.sh

echo "=== MAJOR Upgrade: v1.10.0 → v2.0.0 ==="
echo "⚠️  WARNING: This is a MAJOR update with breaking changes"
read -p "Have you read the upgrade notes for v2.0.0? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Please read upgrade notes before proceeding"
    exit 1
fi

# 1. Full backup (critical for major upgrades)
echo "[1/10] Creating full backup..."
/opt/scripts/pre_upgrade_backup.sh

# 2. Enable maintenance mode
echo "[2/10] Enabling maintenance mode..."
sudo systemctl stop dashboardsonar

# 3. Backup current version (for fast rollback)
echo "[3/10] Backing up current version..."
cd /opt
sudo mv dashboardsonar dashboardsonar.v1.backup

# 4. Clone fresh install
echo "[4/10] Cloning v2.0.0..."
sudo git clone https://github.com/jfdelafuente/dashboardsonar-application-python.git dashboardsonar
cd dashboardsonar
git checkout v2.0.0

# 5. Setup virtualenv
echo "[5/10] Setting up virtualenv..."
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Migrate configuration
echo "[6/10] Migrating configuration..."
# Copiar .env antiguo y agregar nuevas variables
cp /opt/dashboardsonar.v1.backup/.env .env

# Agregar nuevas variables según upgrade notes v2.0.0
echo "NEW_FEATURE_ENABLED=true" >> .env

# 7. Database migration (CRITICAL)
echo "[7/10] Running database migrations..."
# Para MAJOR upgrades, puede haber migraciones largas
flask db upgrade

# Verificar migración exitosa
if [ $? -ne 0 ]; then
    echo "❌ Migration failed - Rolling back"
    # Rollback database
    flask db downgrade
    exit 1
fi

# 8. Data migration (si es necesario)
echo "[8/10] Running data migration..."
# Ejemplo: si v2.0.0 requiere migrar datos
python scripts/migrate_data_v1_to_v2.py

# 9. Restart services
echo "[9/10] Restarting services..."
sudo systemctl daemon-reload
sudo systemctl start dashboardsonar

# 10. Extended verification
echo "[10/10] Verifying upgrade..."
sleep 15

# Health check
if ! curl -f http://localhost:5000/health; then
    echo "❌ Health check failed"
    exit 1
fi

# Smoke tests
python -m pytest tests/smoke_tests/

if [ $? -eq 0 ]; then
    echo "✅ MAJOR upgrade complete"
    echo "⚠️  Keep v1 backup for 7 days before deleting"
else
    echo "❌ Smoke tests failed - See logs"
    exit 1
fi
```

---

## ✔️ Post-Upgrade Verification

### 1. Automated Tests

```bash
#!/bin/bash
# post_upgrade_verification.sh

echo "=== Post-Upgrade Verification ==="

# 1. Health check
echo "[1/5] Health check..."
curl -f http://localhost:5000/health || exit 1

# 2. Database connectivity
echo "[2/5] Database connectivity..."
psql -h localhost -U dashboard_user -d dashboardsonar -c "SELECT 1;" || exit 1

# 3. Sample queries
echo "[3/5] Sample queries..."
psql -h localhost -U dashboard_user -d dashboardsonar -c "SELECT COUNT(*) FROM metricas;" || exit 1

# 4. Login test
echo "[4/5] Login test..."
# Usar curl con credenciales de test
curl -X POST http://localhost:5000/login \
  -d "username=testuser&password=testpass" \
  -c cookies.txt || exit 1

# 5. Dashboard rendering
echo "[5/5] Dashboard rendering..."
curl -b cookies.txt http://localhost:5000/dashboard | grep -q "Dashboard" || exit 1

echo "✅ All verifications passed"
```

---

### 2. Manual Verification

- [ ] Login con usuario administrador
- [ ] Verificar dashboard carga correctamente
- [ ] Verificar métricas se muestran
- [ ] Probar búsqueda de proyectos
- [ ] Verificar histórico/trending
- [ ] Probar exportación de datos
- [ ] Verificar logs (no hay ERRORs)

```bash
# Check logs for errors
sudo journalctl -u dashboardsonar -n 100 --no-pager | grep -i error

# Check application logs
tail -100 /var/log/dashboardsonar/app.log | grep -i error
```

---

### 3. Performance Verification

```bash
# Check response times
time curl -o /dev/null -s -w "%{time_total}\n" http://localhost:5000/dashboard

# Expected: <1 segundo
```

---

## ⏪ Rollback Procedures

### Rollback from Patch/Minor Update

```bash
#!/bin/bash
# rollback_minor.sh

echo "=== Rolling back to previous version ==="

# 1. Stop current version
echo "[1/5] Stopping current version..."
sudo systemctl stop dashboardsonar

# 2. Checkout previous version
echo "[2/5] Checking out previous version..."
cd /opt/dashboardsonar
git checkout v1.10.0  # Previous version

# 3. Reinstall dependencies
echo "[3/5] Reinstalling dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 4. Rollback database migration
echo "[4/5] Rolling back database..."
flask db downgrade  # Baja 1 migración
# O específica: flask db downgrade <revision>

# 5. Restart
echo "[5/5] Restarting..."
sudo systemctl start dashboardsonar

# Verify
sleep 5
curl -f http://localhost:5000/health && echo "✅ Rollback complete"
```

---

### Rollback from Major Update

```bash
#!/bin/bash
# rollback_major.sh

echo "=== Rolling back MAJOR upgrade ==="

# 1. Stop v2.0.0
echo "[1/6] Stopping v2.0.0..."
sudo systemctl stop dashboardsonar

# 2. Restore v1 codebase
echo "[2/6] Restoring v1 codebase..."
cd /opt
sudo rm -rf dashboardsonar
sudo mv dashboardsonar.v1.backup dashboardsonar

# 3. Restore database from backup
echo "[3/6] Restoring database..."
BACKUP_FILE="/backups/pre_upgrade_*/database.backup"
pg_restore -h localhost -U dashboard_user \
  -d dashboardsonar --clean --if-exists \
  $(ls -t $BACKUP_FILE | head -1)

# 4. Restore .env
echo "[4/6] Restoring configuration..."
# Ya está en el directorio restaurado

# 5. Restart services
echo "[5/6] Restarting services..."
sudo systemctl start dashboardsonar

# 6. Verify
echo "[6/6] Verifying rollback..."
sleep 10
curl -f http://localhost:5000/health && echo "✅ Rollback complete"
```

---

## 📝 Version-Specific Notes

### v1.11.0 (Próximo Release)

**Fecha estimada**: Enero 2026

**New Features**:
- Nueva API de exportación de datos
- Dashboard de trending mejorado
- Soporte para Quality Gates personalizados

**Breaking Changes**: Ninguno

**Migration Notes**:
```bash
# Nuevas variables de entorno requeridas
ENABLE_CUSTOM_QUALITY_GATES=true
MAX_EXPORT_ROWS=10000
```

**Database Migrations**: 1 migración automática (agregar tabla `custom_quality_gates`)

**Estimated Upgrade Time**: 15 minutos

---

### v2.0.0 (Future Major Release)

**Fecha estimada**: 2026 Q3

**Breaking Changes** (preliminar):
- Python 3.12+ required (drop support for 3.11)
- PostgreSQL 14+ required
- Cambios en API REST (v2 endpoints)
- Nueva estructura de configuración (.env → config.yaml)

**Migration Notes**:
- Requiere migración de datos de configuración
- Script de migración provisto: `scripts/migrate_config_v1_to_v2.py`

**Estimated Upgrade Time**: 1-2 horas

---

## ⚠️ Breaking Changes

### Como Identificar Breaking Changes

**En CHANGELOG.md**:
```markdown
## [2.0.0] - 2026-09-01

### BREAKING CHANGES
- Removed support for Python 3.11
- Changed API endpoint structure from /api/v1/* to /api/v2/*
- Replaced .env configuration with config.yaml
```

**En código**:
```python
# Old (v1.x)
from infocodest.config import get_config
config = get_config()

# New (v2.0)
from infocodest.config import ConfigManager
config = ConfigManager.load_from_yaml('config.yaml')
```

---

### Migration Strategies for Breaking Changes

#### 1. Feature Flags (Gradual Migration)

```python
# Soportar ambos métodos durante transición
from infocodest.config import settings

if settings.USE_LEGACY_CONFIG:
    # Old way
    config = get_config()
else:
    # New way
    config = ConfigManager.load_from_yaml()
```

#### 2. Adapter Pattern

```python
# Crear adapter para mantener compatibilidad
class LegacyConfigAdapter:
    def __init__(self, new_config):
        self.config = new_config

    def get(self, key):
        # Mapear old keys a new keys
        key_mapping = {
            'DB_HOST': 'database.host',
            'DB_PORT': 'database.port'
        }
        new_key = key_mapping.get(key, key)
        return self.config.get(new_key)
```

---

## 📚 Referencias

### Documentación Relacionada

- **[CHANGELOG.md](../../../CHANGELOG.md)** - Registro de cambios
- **[DEPLOYMENT_AWS.md](../deployment/DEPLOYMENT_AWS.md)** - Deployment procedures
- **[BACKUP_RESTORE.md](../backup-recovery/BACKUP_RESTORE.md)** - Backup & restore
- **[RUNBOOK.md](../runbooks/RUNBOOK.md)** - Incident response

### Contacto y Soporte

**Pre-upgrade Planning**:
- Email: devops@empresa.com
- Slack: #dashboard-sonar-ops

**During Upgrade (Emergency)**:
- On-call: Ver [RUNBOOK.md](../runbooks/RUNBOOK.md)
- Phone: +34 XXX XXX XXX

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
**Próxima revisión**: Antes de cada major release
**Mantenido por**: Equipo DevOps
