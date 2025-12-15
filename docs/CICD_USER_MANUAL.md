# Manual de Usuario - CI/CD Pipeline

## 📖 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos Previos](#requisitos-previos)
3. [Configuración Inicial](#configuración-inicial)
4. [Flujos de Trabajo](#flujos-de-trabajo)
5. [Guía de Uso Diario](#guía-de-uso-diario)
6. [Despliegues](#despliegues)
7. [Resolución de Problemas](#resolución-de-problemas)
8. [Mejores Prácticas](#mejores-prácticas)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción

### ¿Qué es CI/CD?

**CI/CD** (Continuous Integration/Continuous Deployment) es un sistema automatizado que:

- **Valida automáticamente** cada cambio de código
- **Ejecuta pruebas** para garantizar calidad
- **Detecta vulnerabilidades** de seguridad
- **Despliega automáticamente** a staging y producción

### Beneficios para el Equipo

✅ **Calidad garantizada**: Todo código pasa por pruebas automáticas
✅ **Detección temprana**: Errores encontrados antes de llegar a producción
✅ **Despliegues rápidos**: De minutos en lugar de horas
✅ **Rollback automático**: Reversión instantánea si algo falla
✅ **Seguridad mejorada**: Escaneo automático de vulnerabilidades

---

## Requisitos Previos

### Para Desarrolladores

- **Git** instalado y configurado
- **Python 3.10+** instalado
- Acceso al repositorio de GitHub
- Entorno de desarrollo local configurado

### Para Administradores de Sistema

- Acceso de administrador a GitHub (para configurar Environments)
- Acceso SSH a servidores de staging y producción
- Permisos para crear y gestionar GitHub Secrets

---

## Configuración Inicial

### 1. Configuración de GitHub Environments

Los administradores deben configurar tres entornos en GitHub:

#### a) Entorno Staging

1. Ve a **Settings** → **Environments** → **New environment**
2. Nombre: `staging`
3. **Deployment branches**: Solo `develop`
4. Agrega los siguientes **Secrets**:
   - `STAGING_HOST`: Hostname del servidor (ej: `staging.example.com`)
   - `STAGING_USER`: Usuario SSH (ej: `deployer`)
   - `STAGING_PATH`: Ruta de despliegue (ej: `/var/www/dashboardsonar`)
   - `STAGING_SSH_KEY`: Clave privada SSH (contenido completo del archivo)

#### b) Entorno Production

1. Ve a **Settings** → **Environments** → **New environment**
2. Nombre: `production`
3. **Deployment branches**: Solo `main`
4. ✅ Activa **Required reviewers**: Selecciona 1-2 personas que deben aprobar
5. ✅ Activa **Wait timer**: 5 minutos (opcional)
6. Agrega los siguientes **Secrets**:
   - `PRODUCTION_HOST`: Hostname del servidor
   - `PRODUCTION_USER`: Usuario SSH
   - `PRODUCTION_PATH`: Ruta de despliegue
   - `PRODUCTION_SSH_KEY`: Clave privada SSH

#### c) Entorno Production Approval

1. Nombre: `production-approval`
2. ✅ **Required reviewers**: Mismo equipo que production
3. No requiere secrets adicionales

### 2. Configuración de Secrets Repositorio (Opcional)

Para notificaciones y servicios externos:

1. Ve a **Settings** → **Secrets and variables** → **Actions**
2. Agrega:
   - `CODECOV_TOKEN`: Token de Codecov (para reportes de cobertura)
   - `SLACK_WEBHOOK_URL`: Webhook de Slack (para notificaciones)

### 3. Generación de Claves SSH

En el servidor de despliegue:

```bash
# En tu máquina local o servidor de CI/CD
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key

# Copia la clave pública al servidor
ssh-copy-id -i ~/.ssh/deploy_key.pub deployer@staging.example.com

# Copia la clave PRIVADA a GitHub Secrets
cat ~/.ssh/deploy_key
# Copia todo el contenido y pégalo en STAGING_SSH_KEY o PRODUCTION_SSH_KEY
```

### 4. Configuración del Servidor

En cada servidor (staging/production):

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3.11 python3-pip python3-venv git

# Crear usuario de despliegue
sudo useradd -m -s /bin/bash deployer
sudo usermod -aG sudo deployer

# Crear directorio de la aplicación
sudo mkdir -p /var/www/dashboardsonar
sudo chown deployer:deployer /var/www/dashboardsonar

# Clonar repositorio
cd /var/www/dashboardsonar
git clone https://github.com/TU_USUARIO/dashboardsonar-application-python.git .

# Configurar systemd (servicio)
sudo nano /etc/systemd/system/dashboardsonar.service
```

**Contenido del archivo de servicio**:

```ini
[Unit]
Description=Dashboard Sonar Application
After=network.target

[Service]
Type=simple
User=deployer
WorkingDirectory=/var/www/dashboardsonar
Environment="PATH=/var/www/dashboardsonar/venv/bin"
ExecStart=/var/www/dashboardsonar/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar e iniciar el servicio
sudo systemctl daemon-reload
sudo systemctl enable dashboardsonar
sudo systemctl start dashboardsonar
```

---

## Flujos de Trabajo

### 1. Workflow de Pull Request (CI)

**Trigger**: Cuando se crea o actualiza un Pull Request a `develop` o `main`

**Qué hace**:

1. **Code Quality** - Verifica estilo de código (Black, Flake8, Pylint)
2. **Security Scan** - Escanea vulnerabilidades (Safety, Bandit)
3. **Unit Tests** - Ejecuta pruebas en Python 3.10, 3.11, 3.12
4. **Integration Tests** - Pruebas de integración completas
5. **Build Validation** - Verifica que la aplicación se construye correctamente
6. **PR Summary** - Genera resumen de resultados

**Tiempo estimado**: 5-8 minutos

**Indicador de éxito**: ✅ Todos los checks en verde

### 2. Workflow de Staging Deployment (CD)

**Trigger**: Cuando se hace merge a la rama `develop`

**Qué hace**:

1. **Pre-deployment Validation** - Ejecuta todas las pruebas
2. **Deploy** - Despliega automáticamente a staging
   - Crea backup automático
   - Actualiza código (git pull)
   - Instala dependencias
   - Ejecuta migraciones de BD
   - Reinicia aplicación
3. **Smoke Tests** - Verifica que la aplicación funciona
4. **Notification** - Notifica resultado (Slack/GitHub)

**Tiempo estimado**: 3-5 minutos

**URL de verificación**: `http://staging.example.com`

### 3. Workflow de Production Deployment (CD)

**Trigger**: Cuando se crea un tag de versión (ej: `v1.2.3`)

**Qué hace**:

1. **Validate** - Valida tag, ejecuta pruebas completas, escaneo de seguridad
2. **Approve** - **REQUIERE APROBACIÓN MANUAL** ⚠️
3. **Deploy** - Despliega con estrategia blue-green
   - Crea backup completo
   - Prepara nueva versión en paralelo
   - Prueba nueva versión en puerto temporal
   - Cambia a nueva versión (zero-downtime)
   - Reinicia aplicación
4. **Validate Deployment** - Ejecuta smoke tests en producción
5. **Rollback** - Si falla, revierte automáticamente
6. **Notification** - Notifica resultado final

**Tiempo estimado**: 8-12 minutos (más tiempo de aprobación)

**Requiere**: Aprobación manual de reviewers configurados

### 4. Workflow de Nightly Tests

**Trigger**: Automático todos los días a las 2:00 AM UTC

**Qué hace**:

1. **Extended Unit Tests** - Pruebas extendidas en múltiples versiones de Python
2. **Integration Tests** - Pruebas de integración completas
3. **Performance Tests** - Benchmarks de rendimiento
4. **Security Audit** - Auditoría de seguridad completa con reportes
5. **Code Quality** - Análisis de complejidad y duplicación
6. **Dependency Check** - Verifica dependencias obsoletas y licencias
7. **Summary** - Genera reporte consolidado y notifica

**Tiempo estimado**: 15-20 minutos

**Reportes generados**: Disponibles en GitHub Actions Artifacts

---

## Guía de Uso Diario

### Para Desarrolladores

#### 1. Trabajando en una Nueva Funcionalidad

```bash
# 1. Crea una rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/nueva-funcionalidad

# 2. Desarrolla tu código
# ... haz tus cambios ...

# 3. Ejecuta checks locales ANTES de hacer commit
pip install -r requirements-dev.txt
./scripts/ci/lint.sh              # Verifica calidad de código
./scripts/ci/security.sh          # Verifica seguridad
./scripts/ci/test.sh --html       # Ejecuta pruebas con cobertura

# 4. Si todo pasa, haz commit
git add .
git commit -m "feat: descripción de la funcionalidad"

# 5. Push a GitHub
git push origin feature/nueva-funcionalidad
```

#### 2. Creando un Pull Request

1. Ve a GitHub → **Pull requests** → **New pull request**
2. **Base**: `develop` ← **Compare**: `feature/nueva-funcionalidad`
3. Completa la descripción:
   - ¿Qué hace este cambio?
   - ¿Por qué es necesario?
   - ¿Cómo se puede probar?
4. Clic en **Create pull request**

**El CI se ejecutará automáticamente**:

- ⏳ Espera 5-8 minutos
- ✅ Si todo pasa → Solicita revisión de código
- ❌ Si algo falla → Revisa los logs, corrige y haz push de nuevo

#### 3. Revisando el Estado del CI

En tu Pull Request, verás checks como:

```
✅ Code Quality / Lint and Format
✅ Security Scan / Safety and Bandit
✅ Unit Tests (Python 3.11) / Run Tests
✅ Integration Tests / Test Application
✅ Build / Validate Build
✅ PR Summary / Generate Summary
```

**Haz clic en "Details"** para ver logs detallados si algo falla.

#### 4. Corrigiendo Errores del CI

##### Error de Formato de Código

```bash
# El CI falló con "Black formatting failed"
./scripts/ci/lint.sh --fix    # Auto-formatea el código
git add .
git commit -m "style: fix code formatting"
git push
```

##### Error de Pruebas

```bash
# El CI falló con "2 tests failed"
pytest tests/ -v              # Ejecuta pruebas localmente
# ... corrige los errores ...
git add .
git commit -m "fix: corregir pruebas fallidas"
git push
```

##### Error de Seguridad

```bash
# El CI falló con "Security vulnerabilities found"
./scripts/ci/security.sh      # Ve los detalles
pip install --upgrade paquete-vulnerable
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: actualizar dependencias vulnerables"
git push
```

---

## Despliegues

### Despliegue a Staging (Automático)

**Cuándo**: Automáticamente al hacer merge a `develop`

**Pasos**:

1. Tu PR ha sido aprobado y todos los checks pasan ✅
2. Haz clic en **Merge pull request** en GitHub
3. **Automáticamente** se dispara el despliegue a staging
4. Monitorea en: **Actions** → **CD - Staging Deployment**

**Verificación**:

```bash
# Opción 1: Smoke tests automáticos (ya incluidos)
# Revisa el workflow para ver si pasaron

# Opción 2: Verificación manual
curl http://staging.example.com/
# Debe devolver la página principal

# Opción 3: Prueba en navegador
# Abre: http://staging.example.com
# Verifica la funcionalidad manualmente
```

**Si falla el despliegue**:

- Revisa los logs en GitHub Actions
- Conéctate al servidor para investigar:

```bash
ssh deployer@staging.example.com
cd /var/www/dashboardsonar
tail -f logs/app.log              # Ver logs de la aplicación
sudo systemctl status dashboardsonar  # Ver estado del servicio
```

### Despliegue a Producción (Manual con Aprobación)

**Cuándo**: Cuando estás listo para liberar una nueva versión

**Requisitos**:

- Todo debe funcionar correctamente en staging
- Equipo ha validado las funcionalidades
- Has decidido el número de versión (semver: `v1.2.3`)

**Pasos detallados**:

#### 1. Merge develop a main

```bash
# Desde tu máquina local
git checkout main
git pull origin main
git merge develop
git push origin main
```

#### 2. Crear Tag de Versión

```bash
# Formato: v[MAJOR].[MINOR].[PATCH]
# Ejemplos:
# - v1.0.0 - Primera versión de producción
# - v1.1.0 - Nueva funcionalidad
# - v1.1.1 - Corrección de bugs

git tag -a v1.2.3 -m "Release version 1.2.3

Cambios principales:
- Nueva funcionalidad de reportes
- Corrección de bug en autenticación
- Mejoras de rendimiento
"

# Push del tag
git push origin v1.2.3
```

#### 3. El Workflow se Dispara Automáticamente

Ve a **Actions** → **CD - Production Deployment**

**Fase 1: Validate** (2-3 min)
- ✅ Valida que el tag existe
- ✅ Verifica que está en main branch
- ✅ Ejecuta suite completa de pruebas
- ✅ Escaneo de seguridad

**Fase 2: Approve Deployment** ⚠️ **REQUIERE ACCIÓN MANUAL**

1.Recibirás una notificación (email/GitHub)
2. Ve a la página del workflow en GitHub Actions
3. Verás un botón amarillo: **"Review pending deployments"**
4. Haz clic → Revisa la información
5. Marca ✅ **production-approval**
6. Escribe un comentario (opcional): "Aprobado para producción"
7. Haz clic en **Approve and deploy**

**Fase 3: Deploy** (3-5 min)
- 📦 Crea backup de producción actual
- 🔵 Prepara nueva versión (blue-green deployment)
- 🧪 Prueba nueva versión en puerto temporal
- 🔄 Cambia a nueva versión (zero-downtime)
- ♻️ Reinicia aplicación

**Fase 4: Validate Deployment** (1-2 min)
- Espera 30s para estabilización
- ✅ Ejecuta smoke tests en producción
- ✅ Verifica endpoints críticos

**Fase 5: Rollback** (solo si falla)
- Si algo falla en validación
- ⚠️ Rollback automático a versión anterior
- 📧 Notificación de fallo

**Fase 6: Notification**
- ✅ Notificación de éxito (Slack/GitHub)
- ❌ Notificación de fallo (si aplica)

#### 4. Verificación Post-Despliegue

```bash
# Verifica que la aplicación responde
curl https://production.example.com/

# Verifica versión desplegada (si tienes endpoint)
curl https://production.example.com/api/version

# Monitorea logs en tiempo real
ssh deployer@production.example.com
tail -f /var/www/dashboardsonar/logs/app.log
```

**Checklist de verificación**:

- [ ] Página principal carga correctamente
- [ ] Login funciona
- [ ] Funcionalidades críticas operativas
- [ ] No hay errores en logs
- [ ] Tiempos de respuesta normales
- [ ] Base de datos responde correctamente

### Rollback Manual (Si es Necesario)

Si detectas un problema después del despliegue:

```bash
# Opción 1: Desde tu máquina local (recomendado)
# Ejecutar script de rollback
export PRODUCTION_HOST=production.example.com
export PRODUCTION_USER=deployer
export PRODUCTION_PATH=/var/www/dashboardsonar
export PRODUCTION_SSH_KEY=~/.ssh/production_key

# Ver backups disponibles
./scripts/ci/rollback.sh --list-backups

# Hacer rollback al backup más reciente
./scripts/ci/rollback.sh --timestamp 20231215_143022

# Opción 2: Rollback manual en el servidor
ssh deployer@production.example.com
cd /var/www/dashboardsonar

# Ver backups disponibles
ls -lht ../backups/

# Hacer rollback manual
sudo systemctl stop dashboardsonar
mv /var/www/dashboardsonar /var/www/dashboardsonar-failed
cd /var/www
tar -xzf backups/production-backup-20231215_143022.tar.gz -C dashboardsonar
sudo systemctl start dashboardsonar

# Verificar
curl http://localhost:5000/
```

---

## Resolución de Problemas

### Problema 1: CI Falla por Timeout

**Síntoma**: El workflow se detiene con "Job cancelled due to timeout"

**Causa**: Las pruebas tardan más de lo esperado

**Solución**:

```yaml
# Edita .github/workflows/ci-pull-request.yml
jobs:
  unit-tests:
    timeout-minutes: 30  # Aumenta de 15 a 30
```

### Problema 2: Despliegue Falla por Conexión SSH

**Síntoma**: Error "Permission denied (publickey)"

**Causa**: Clave SSH incorrecta o no autorizada

**Solución**:

```bash
# 1. Verifica que la clave pública está en el servidor
ssh deployer@staging.example.com 'cat ~/.ssh/authorized_keys'

# 2. Regenera y vuelve a copiar la clave
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key_new
ssh-copy-id -i ~/.ssh/deploy_key_new.pub deployer@staging.example.com

# 3. Actualiza el secret en GitHub
cat ~/.ssh/deploy_key_new
# Copia el contenido y actualiza STAGING_SSH_KEY en GitHub
```

### Problema 3: Smoke Tests Fallan Después del Despliegue

**Síntoma**: Deployment exitoso pero smoke tests fallan

**Causa**: Aplicación no se inició correctamente

**Solución**:

```bash
# Conéctate al servidor
ssh deployer@staging.example.com

# Verifica el servicio
sudo systemctl status dashboardsonar

# Si está failed, revisa logs
sudo journalctl -u dashboardsonar -n 50

# Revisa logs de la aplicación
tail -100 /var/www/dashboardsonar/logs/app.log

# Posibles problemas:
# - Falta variable de entorno
# - Error en migraciones de BD
# - Dependencia faltante
# - Puerto ocupado
```

### Problema 4: Merge a Develop No Dispara Staging Deployment

**Síntoma**: Hiciste merge pero no se despliega a staging

**Causa**: Branch protection rules o workflow deshabilitado

**Solución**:

```bash
# 1. Verifica que el workflow está habilitado
# GitHub → Actions → CD - Staging Deployment → Enable workflow

# 2. Verifica los filtros del workflow
# El workflow debe tener:
on:
  push:
    branches: [develop]

# 3. Dispara manualmente
# GitHub → Actions → CD - Staging Deployment → Run workflow
```

### Problema 5: Codecov No Muestra Cobertura

**Síntoma**: Badge muestra "unknown" o no se actualiza

**Causa**: Token no configurado o inválido

**Solución**:

```bash
# 1. Genera nuevo token en codecov.io
# https://codecov.io/gh/TU_USUARIO/TU_REPO/settings

# 2. Actualiza el secret en GitHub
# Settings → Secrets → CODECOV_TOKEN

# 3. Re-ejecuta el workflow
# Actions → CI - Pull Request → Re-run jobs
```

### Problema 6: Production Deployment Se Queda en "Waiting for Approval"

**Síntoma**: No recibes notificación de aprobación

**Causa**: Reviewers no configurados correctamente

**Solución**:

```bash
# 1. Verifica reviewers del environment
# Settings → Environments → production-approval → Required reviewers

# 2. Asegúrate de que los reviewers:
#    - Tienen acceso al repositorio
#    - Están en la lista de required reviewers
#    - Tienen notificaciones habilitadas

# 3. Aprueba manualmente:
# Actions → Workflow → Review pending deployments → Approve
```

---

## Mejores Prácticas

### 1. Antes de Crear un Pull Request

✅ **Ejecuta checks localmente**:

```bash
# Siempre ejecuta estos comandos ANTES de push
./scripts/ci/lint.sh --fix      # Auto-corrige formato
./scripts/ci/security.sh         # Verifica seguridad
./scripts/ci/test.sh             # Ejecuta pruebas
```

✅ **Escribe mensajes de commit claros**:

```bash
# ✅ BIEN
git commit -m "feat: agregar exportación de reportes a PDF"
git commit -m "fix: corregir error de autenticación en login"
git commit -m "docs: actualizar documentación de API"

# ❌ MAL
git commit -m "cambios"
git commit -m "fix"
git commit -m "asdf"
```

### 2. Durante el Desarrollo

✅ **Commits pequeños y frecuentes**: Es mejor hacer 5 commits pequeños que 1 gigante

✅ **Una funcionalidad por PR**: No mezcles múltiples funcionalidades en un PR

✅ **Actualiza tu rama frecuentemente**:

```bash
# Mantén tu rama actualizada con develop
git checkout feature/mi-feature
git fetch origin
git rebase origin/develop
```

### 3. Code Review

✅ **Revisa los checks del CI antes de aprobar**

✅ **Verifica que la cobertura de código no bajó**

✅ **Prueba localmente si el cambio es crítico**

### 4. Despliegues a Staging

✅ **Verifica staging después de cada merge**

✅ **Reporta problemas inmediatamente**

✅ **No hagas merge a develop si staging está roto**

### 5. Despliegues a Producción

✅ **Despliega en horarios de baja actividad** (ej: 2AM - 6AM)

✅ **Notifica al equipo antes de desplegar**

✅ **Ten el comando de rollback listo**

✅ **Monitorea por al menos 30 minutos después del deploy**

✅ **Documenta los cambios en CHANGELOG.md**

### 6. Versionado Semántico

Usa **Semantic Versioning** (`vMAJOR.MINOR.PATCH`):

- **MAJOR** (v2.0.0): Cambios incompatibles con versiones anteriores
- **MINOR** (v1.3.0): Nueva funcionalidad compatible con versiones anteriores
- **PATCH** (v1.2.1): Correcciones de bugs

```bash
# Ejemplos:
v1.0.0  # Primera versión de producción
v1.1.0  # Agregaste nueva funcionalidad
v1.1.1  # Corregiste un bug
v2.0.0  # Cambio que rompe compatibilidad (breaking change)
```

---

## Preguntas Frecuentes

### ¿Cuánto tarda el CI en ejecutarse?

- **Pull Request CI**: 5-8 minutos
- **Staging Deployment**: 3-5 minutos
- **Production Deployment**: 8-12 minutos (+ tiempo de aprobación)
- **Nightly Tests**: 15-20 minutos

### ¿Puedo saltarme los checks del CI?

**No se recomienda**. Los checks están ahí para proteger la calidad del código. Sin embargo, si es absolutamente necesario:

```bash
# Los administradores pueden forzar merge (no recomendado)
# Requiere permisos de admin y puede violar políticas de equipo
```

### ¿Qué hago si el CI está fallando por un servicio externo?

```bash
# Opción 1: Re-ejecuta el workflow
# Actions → Workflow fallido → Re-run failed jobs

# Opción 2: Si el problema persiste, crea un issue
# Documenta el error y notifica al equipo DevOps
```

### ¿Puedo desplegar a staging manualmente?

**Sí**:

```bash
# Opción 1: Via GitHub Actions UI
# Actions → CD - Staging Deployment → Run workflow → Select branch

# Opción 2: Desde línea de comandos
./scripts/ci/deploy-staging.sh --branch feature/mi-feature
```

### ¿Cómo deshago un despliegue a producción?

```bash
# Usa el script de rollback
./scripts/ci/rollback.sh --list-backups
./scripts/ci/rollback.sh --timestamp TIMESTAMP_DEL_BACKUP
```

### ¿Puedo ver los reportes de seguridad?

**Sí**:

1. Ve a **Actions** → Workflow completado
2. Baja hasta **Artifacts**
3. Descarga: `security-audit-reports.zip`
4. Descomprime y revisa los reportes JSON

### ¿Qué pasa si borro accidentalmente un tag de versión?

```bash
# NO se puede desplegar a producción sin tag
# Si borraste un tag:

# 1. Recréalo en el mismo commit
git tag -a v1.2.3 COMMIT_SHA -m "Release v1.2.3"
git push origin v1.2.3

# 2. El workflow se disparará automáticamente
```

### ¿Cómo agrego más pruebas al CI?

```bash
# 1. Agrega tus pruebas en el directorio tests/
tests/
  unit/
    test_mi_modulo.py
  integration/
    test_mi_api.py

# 2. El CI las detectará automáticamente
# No necesitas modificar los workflows
```

### ¿Puedo recibir notificaciones por email?

**Sí**, GitHub envía notificaciones automáticas:

1. Ve a **Settings** (tu perfil) → **Notifications**
2. Activa: **Actions** → Email notifications
3. Recibirás emails cuando:
   - Un workflow falla
   - Se requiere aprobación
   - Un deployment se completa

### ¿Cómo configuro notificaciones de Slack?

```bash
# 1. Crea un Incoming Webhook en Slack
# https://api.slack.com/messaging/webhooks

# 2. Agrega el webhook como secret en GitHub
# Settings → Secrets → SLACK_WEBHOOK_URL

# 3. Los workflows enviarán notificaciones automáticamente
```

---

## Recursos Adicionales

### Documentación Relacionada

- [Workflows Documentation](.github/README.md) - Detalles técnicos de workflows
- [Scripts Documentation](scripts/ci/README.md) - Documentación de scripts
- [Implementation Plan](docs/plan/PLAN_CICD_AUTOMATION.md) - Plan de implementación

### Scripts Útiles

```bash
# Ejecutar todos los checks localmente
./scripts/ci/lint.sh && ./scripts/ci/security.sh && ./scripts/ci/test.sh

# Desplegar a staging (manual)
./scripts/ci/deploy-staging.sh --dry-run  # Ver qué haría
./scripts/ci/deploy-staging.sh             # Ejecutar

# Verificar salud de staging/production
./scripts/ci/smoke-tests.sh --url http://staging.example.com --verbose
```

### Contacto y Soporte

- **Problemas con CI/CD**: Crea un issue en GitHub con label `ci/cd`
- **Emergencias de producción**: Contacta al equipo DevOps
- **Preguntas generales**: Canal de Slack #devops

---

## Changelog del Manual

- **v1.0.0** (2024-01-15): Versión inicial del manual
  - Documentación completa de workflows
  - Guías de despliegue
  - Resolución de problemas
  - FAQ

---

**Última actualización**: 2024-01-15
**Versión**: 1.0.0
**Mantenido por**: Equipo DevOps
