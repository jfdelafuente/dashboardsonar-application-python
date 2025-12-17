# Security Hardening Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, Security Engineers
**Criticidad**: 🔴 CRÍTICO - Protección de sistemas

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Application Security](#application-security)
3. [Database Security](#database-security)
4. [Infrastructure Security](#infrastructure-security)
5. [Network Security](#network-security)
6. [Authentication & Authorization](#authentication--authorization)
7. [Secrets Management](#secrets-management)
8. [Security Monitoring](#security-monitoring)
9. [Compliance & Auditing](#compliance--auditing)
10. [Security Checklist](#security-checklist)

---

## 🎯 Introducción

### ¿Por qué Security Hardening?

**Amenazas comunes**:
- 🦠 **SQL Injection**: Atacante ejecuta SQL malicioso
- 🔓 **XSS** (Cross-Site Scripting): Inyección de JavaScript
- 🔑 **Credential Stuffing**: Uso de credenciales robadas
- 🌐 **CSRF** (Cross-Site Request Forgery): Peticiones maliciosas
- 💉 **Command Injection**: Ejecución de comandos del sistema
- 🔐 **Weak Authentication**: Passwords débiles, sin 2FA
- 📂 **Directory Traversal**: Acceso a archivos no autorizados

**Objetivo**: Reducir superficie de ataque y proteger datos sensibles.

---

### Security Framework: Defense in Depth

**Capas de seguridad**:
```
┌─────────────────────────────────────────┐
│ Layer 7: Monitoring & Alerting         │ ← SIEM, IDS/IPS
├─────────────────────────────────────────┤
│ Layer 6: Application Security          │ ← Input validation, CSRF tokens
├─────────────────────────────────────────┤
│ Layer 5: Authentication & Authorization │ ← 2FA, RBAC, JWT
├─────────────────────────────────────────┤
│ Layer 4: Data Security                 │ ← Encryption at rest/transit
├─────────────────────────────────────────┤
│ Layer 3: Network Security              │ ← Firewall, WAF, VPC
├─────────────────────────────────────────┤
│ Layer 2: Infrastructure Security       │ ← OS hardening, patching
├─────────────────────────────────────────┤
│ Layer 1: Physical Security             │ ← Datacenter security
└─────────────────────────────────────────┘
```

---

## 🛡️ Application Security

### 1. Input Validation & Sanitization

**Problema**: Input no validado puede causar SQL injection, XSS, command injection.

---

#### SQL Injection Prevention

**❌ VULNERABLE**:
```python
# NUNCA hacer esto
user_id = request.args.get('user_id')
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)
```

**✅ SEGURO** (usar parametrized queries):
```python
# Flask-SQLAlchemy con ORM (automáticamente seguro)
user = User.query.filter_by(id=user_id).first()

# O con SQL raw (usar parámetros)
query = "SELECT * FROM users WHERE id = :user_id"
db.session.execute(text(query), {"user_id": user_id})
```

---

#### XSS Prevention

**❌ VULNERABLE**:
```html
<!-- Si user_input = "<script>alert('XSS')</script>" -->
<div>{{ user_input | safe }}</div>
```

**✅ SEGURO** (auto-escape en Jinja2):
```html
<!-- Jinja2 auto-escapa por defecto -->
<div>{{ user_input }}</div>
<!-- Output: &lt;script&gt;alert('XSS')&lt;/script&gt; -->
```

**Configuración en Flask**:
```python
# infocodest/__init__.py
from flask import Flask
from markupsafe import escape

app = Flask(__name__)

# Auto-escape habilitado por defecto en Jinja2
# Si necesitas deshabilitar (NUNCA hacerlo sin sanitizar):
# app.jinja_env.autoescape = False  # ❌ INSEGURO
```

---

#### Command Injection Prevention

**❌ VULNERABLE**:
```python
import os

# NUNCA hacer esto
filename = request.args.get('filename')
os.system(f"cat {filename}")  # Vulnerable a: filename = "file.txt; rm -rf /"
```

**✅ SEGURO**:
```python
import subprocess

# Usar subprocess con lista (no shell=True)
filename = request.args.get('filename')

# Validar input primero
allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")
if not all(c in allowed_chars for c in filename):
    abort(400, "Invalid filename")

# Usar subprocess de forma segura
result = subprocess.run(['cat', filename], capture_output=True, text=True)
```

---

### 2. CSRF Protection

**Implementar en Flask**:
```python
# requirements.txt
flask-wtf==1.2.1

# infocodest/__init__.py
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # CRÍTICO: debe ser secreto
csrf = CSRFProtect(app)

# Todas las POST requests requerirán token CSRF
```

**En formularios**:
```html
<!-- forms/login.html -->
<form method="POST">
    {{ form.hidden_tag() }}  <!-- Incluye CSRF token automáticamente -->
    {{ form.username.label }} {{ form.username }}
    {{ form.password.label }} {{ form.password }}
    <button type="submit">Login</button>
</form>
```

**En AJAX requests**:
```javascript
// Agregar CSRF token a headers
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'X-CSRFToken': document.querySelector('meta[name=csrf-token]').content,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
```

---

### 3. Content Security Policy (CSP)

**Prevenir XSS** definiendo fuentes permitidas de contenido.

```python
# infocodest/security/headers.py
from flask import Flask

def set_security_headers(app: Flask):
    @app.after_request
    def add_security_headers(response):
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'"
        )

        # X-Frame-Options (prevent clickjacking)
        response.headers['X-Frame-Options'] = 'DENY'

        # X-Content-Type-Options (prevent MIME sniffing)
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # X-XSS-Protection (legacy browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Referrer-Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions-Policy (disable unnecessary features)
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response

# En __init__.py
from infocodest.security.headers import set_security_headers
set_security_headers(app)
```

---

### 4. Rate Limiting

**Prevenir brute force** y DoS attacks.

```python
# requirements.txt
flask-limiter==3.5.0

# infocodest/__init__.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"  # O memory:// para desarrollo
)

# En routes
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Máximo 5 intentos por minuto
def login():
    # ...
```

---

### 5. Secure Session Management

```python
# infocodest/config.py
class ProductionConfig:
    # Secret key (NUNCA commitear en git)
    SECRET_KEY = os.getenv('SECRET_KEY')  # Debe ser 32+ bytes random

    # Session config
    SESSION_COOKIE_SECURE = True       # Solo HTTPS
    SESSION_COOKIE_HTTPONLY = True     # No accesible desde JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'    # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora

    # Remember me cookie
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 2592000  # 30 días
```

---

### 6. File Upload Security

**Si la aplicación permite subir archivos**:

```python
# infocodest/utils/file_upload.py
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        abort(400, "No file provided")

    file = request.files['file']

    # Validar filename
    if not allowed_file(file.filename):
        abort(400, "File type not allowed")

    # Sanitizar filename (prevenir directory traversal)
    filename = secure_filename(file.filename)

    # Validar tamaño
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > MAX_FILE_SIZE:
        abort(400, "File too large")
    file.seek(0)

    # Guardar en directorio seguro (fuera de webroot)
    upload_folder = '/var/uploads/dashboardsonar'
    file.save(os.path.join(upload_folder, filename))

    return jsonify({'success': True})
```

---

## 🗄️ Database Security

### 1. PostgreSQL Hardening

#### Configuración de Autenticación

```bash
# /etc/postgresql/13/main/pg_hba.conf

# ❌ INSEGURO (permite cualquier usuario sin password)
# host    all    all    0.0.0.0/0    trust

# ✅ SEGURO (requiere password y SSL)
hostssl    dashboardsonar    dashboard_user    10.0.0.0/16    md5
hostssl    dashboardsonar    dashboard_user    ::1/128        md5

# Rechazar todo lo demás
host    all    all    0.0.0.0/0    reject
```

---

#### SSL/TLS Encryption

```bash
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/postgresql.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
ssl_ca_file = '/etc/ssl/certs/ca-certificate.crt'

# Forzar SSL
ssl_min_protocol_version = 'TLSv1.2'
```

**Generar certificados**:
```bash
# Self-signed (desarrollo)
openssl req -new -x509 -days 365 -nodes -text \
  -out /etc/ssl/certs/postgresql.crt \
  -keyout /etc/ssl/private/postgresql.key \
  -subj "/CN=dashboardsonar-db"

chmod 600 /etc/ssl/private/postgresql.key
chown postgres:postgres /etc/ssl/private/postgresql.key
```

---

#### Database Permissions (Least Privilege)

```sql
-- Crear usuario de aplicación con permisos mínimos
CREATE USER dashboard_app WITH PASSWORD 'secure_password_here';

-- Conceder solo permisos necesarios
GRANT CONNECT ON DATABASE dashboardsonar TO dashboard_app;
GRANT USAGE ON SCHEMA public TO dashboard_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO dashboard_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dashboard_app;

-- NO conceder SUPERUSER, CREATEDB, CREATEROLE
```

**Usuario separado para backups** (solo lectura):
```sql
CREATE USER dashboard_backup WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE dashboardsonar TO dashboard_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dashboard_backup;
```

---

#### Row-Level Security (RLS)

**Si hay multi-tenancy**:
```sql
-- Habilitar RLS en tabla
ALTER TABLE proyectos ENABLE ROW LEVEL SECURITY;

-- Crear política: usuarios solo ven sus propios proyectos
CREATE POLICY proyectos_isolation ON proyectos
    USING (owner_id = current_setting('app.current_user_id')::integer);

-- En la aplicación, set user context:
db.session.execute(text("SET app.current_user_id = :user_id"), {"user_id": current_user.id})
```

---

### 2. Database Encryption

#### Encryption at Rest (AWS RDS)

```bash
# Al crear RDS, habilitar encryption
aws rds create-db-instance \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:region:account:key/key-id \
  ...
```

#### Transparent Data Encryption (TDE)

**Para PostgreSQL on-premise**:
```bash
# Usar pgcrypto extension
psql -U postgres -d dashboardsonar

CREATE EXTENSION pgcrypto;

-- Encriptar columna sensible
ALTER TABLE users ADD COLUMN ssn_encrypted bytea;

UPDATE users SET ssn_encrypted = pgp_sym_encrypt(ssn, 'encryption_key');

-- Consultar
SELECT pgp_sym_decrypt(ssn_encrypted, 'encryption_key') FROM users;
```

---

## 🖥️ Infrastructure Security

### 1. Operating System Hardening (Ubuntu)

#### Actualizaciones Automáticas

```bash
# Instalar unattended-upgrades
sudo apt install unattended-upgrades

# Configurar
sudo dpkg-reconfigure -plow unattended-upgrades

# Editar /etc/apt/apt.conf.d/50unattended-upgrades
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "03:00";
```

---

#### Firewall (UFW)

```bash
# Habilitar UFW
sudo ufw enable

# Denegar todo por defecto
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH (solo desde IPs específicas)
sudo ufw allow from YOUR_IP to any port 22

# Permitir HTTPS desde ALB
sudo ufw allow from 10.0.0.0/16 to any port 5000

# Ver reglas
sudo ufw status numbered
```

---

#### Disable Unnecessary Services

```bash
# Listar servicios corriendo
systemctl list-units --type=service --state=running

# Deshabilitar servicios no necesarios
sudo systemctl disable bluetooth.service
sudo systemctl disable cups.service
sudo systemctl disable avahi-daemon.service
```

---

#### SSH Hardening

```bash
# Editar /etc/ssh/sshd_config
sudo nano /etc/ssh/sshd_config

# Cambios recomendados:
PermitRootLogin no                      # ❌ No permitir login como root
PasswordAuthentication no               # ❌ Solo SSH keys
PubkeyAuthentication yes                # ✅ Usar SSH keys
PermitEmptyPasswords no                 # ❌ No passwords vacíos
X11Forwarding no                        # ❌ Deshabilitar X11
MaxAuthTries 3                          # Máximo 3 intentos
ClientAliveInterval 300                 # Timeout después de 5 min inactividad
ClientAliveCountMax 2
AllowUsers ubuntu dashboard_user        # Solo permitir usuarios específicos
Protocol 2                              # Usar SSHv2 (no v1)

# Reiniciar SSH
sudo systemctl restart sshd
```

---

#### Fail2Ban (Prevenir Brute Force)

```bash
# Instalar Fail2Ban
sudo apt install fail2ban

# Crear configuración
sudo tee /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 600
EOF

# Reiniciar
sudo systemctl restart fail2ban

# Ver bans activos
sudo fail2ban-client status sshd
```

---

### 2. Docker Security (si se usa)

```dockerfile
# Dockerfile - Best practices

# Usar imagen oficial y específica (no 'latest')
FROM python:3.12.1-slim

# No correr como root
RUN useradd -m -u 1000 appuser
USER appuser

# Copiar solo lo necesario (no copiar .git, tests, etc.)
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser infocodest/ ./infocodest/

# Remover cache y archivos innecesarios
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache

# Usar HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD curl -f http://localhost:5000/health || exit 1

# No exponer puertos innecesarios
EXPOSE 5000
```

**Docker Compose Security**:
```yaml
version: '3.8'
services:
  app:
    image: dashboardsonar:latest
    read_only: true  # Filesystem read-only
    tmpfs:
      - /tmp
    cap_drop:
      - ALL  # Drop todas las capabilities
    cap_add:
      - NET_BIND_SERVICE  # Solo lo necesario
    security_opt:
      - no-new-privileges:true
    ulimits:
      nproc: 65535
      nofile:
        soft: 20000
        hard: 40000
```

---

## 🌐 Network Security

### 1. HTTPS/TLS Configuration

**Nginx con SSL**:
```nginx
# /etc/nginx/sites-available/dashboardsonar
server {
    listen 80;
    server_name dashboard-sonar.empresa.com;

    # Redirigir HTTP → HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dashboard-sonar.empresa.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/dashboard-sonar.empresa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard-sonar.empresa.com/privkey.pem;

    # SSL protocols (solo TLS 1.2+)
    ssl_protocols TLSv1.2 TLSv1.3;

    # Ciphers fuertes
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;

    # HSTS (force HTTPS for 1 year)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Obtener certificado Let's Encrypt**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d dashboard-sonar.empresa.com

# Auto-renovación
sudo certbot renew --dry-run
```

---

### 2. Web Application Firewall (WAF)

**AWS WAF** (si estás en AWS):
```bash
# Crear Web ACL
aws wafv2 create-web-acl \
  --name dashboardsonar-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json

# waf-rules.json - Reglas OWASP Top 10
[
  {
    "Name": "BlockSQLi",
    "Priority": 1,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesSQLiRuleSet"
      }
    },
    "Action": {"Block": {}},
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "BlockSQLi"
    }
  },
  {
    "Name": "RateLimitRule",
    "Priority": 2,
    "Statement": {
      "RateBasedStatement": {
        "Limit": 2000,
        "AggregateKeyType": "IP"
      }
    },
    "Action": {"Block": {}},
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "RateLimit"
    }
  }
]
```

---

## 🔐 Authentication & Authorization

### 1. Password Security

**Hashing con Bcrypt**:
```python
# infocodest/models/user.py
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        # Bcrypt automáticamente usa salt único
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
```

**Password Policy**:
```python
# infocodest/utils/password_policy.py
import re

def validate_password(password):
    """
    Política de password:
    - Mínimo 12 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 símbolo especial
    """
    if len(password) < 12:
        return False, "Password debe tener al menos 12 caracteres"

    if not re.search(r'[A-Z]', password):
        return False, "Password debe tener al menos 1 mayúscula"

    if not re.search(r'[a-z]', password):
        return False, "Password debe tener al menos 1 minúscula"

    if not re.search(r'\d', password):
        return False, "Password debe tener al menos 1 número"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password debe tener al menos 1 símbolo especial"

    # Check against common passwords
    common_passwords = ['password123', 'admin123', 'welcome123']
    if password.lower() in common_passwords:
        return False, "Password demasiado común"

    return True, "Password válido"
```

---

### 2. Two-Factor Authentication (2FA)

```python
# requirements.txt
pyotp==2.9.0

# infocodest/models/user.py
import pyotp

class User(db.Model):
    # ...
    totp_secret = db.Column(db.String(32), nullable=True)
    totp_enabled = db.Column(db.Boolean, default=False)

    def enable_2fa(self):
        """Generate TOTP secret"""
        self.totp_secret = pyotp.random_base32()
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.username,
            issuer_name='Dashboard Sonar'
        )

    def verify_totp(self, token):
        """Verify TOTP token"""
        if not self.totp_enabled:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)

# En login route
@app.route('/login/verify', methods=['POST'])
def login_verify_2fa():
    user = User.query.get(session['pending_user_id'])
    token = request.form.get('token')

    if user.verify_totp(token):
        login_user(user)
        return redirect('/dashboard')
    else:
        flash('Invalid 2FA token')
        return redirect('/login')
```

---

### 3. Role-Based Access Control (RBAC)

```python
# infocodest/models/user.py
from enum import Enum

class UserRole(Enum):
    VIEWER = 'viewer'
    ANALYST = 'analyst'
    ADMIN = 'admin'

class User(db.Model):
    # ...
    role = db.Column(db.Enum(UserRole), default=UserRole.VIEWER)

    def has_permission(self, permission):
        permissions = {
            UserRole.VIEWER: ['read_projects', 'read_metrics'],
            UserRole.ANALYST: ['read_projects', 'read_metrics', 'export_data'],
            UserRole.ADMIN: ['read_projects', 'read_metrics', 'export_data',
                           'manage_users', 'manage_settings']
        }
        return permission in permissions.get(self.role, [])

# Decorator para proteger rutas
from functools import wraps
from flask import abort

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Uso
@app.route('/admin/users')
@login_required
@permission_required('manage_users')
def manage_users():
    # Solo accesible para ADMIN
    pass
```

---

## 🔑 Secrets Management

### 1. Environment Variables (Development)

```bash
# .env (NUNCA commitear en git)
SECRET_KEY=muy_secreto_cambiar_en_produccion
DATABASE_URL=postgresql://user:password@localhost/dashboardsonar
SONARQUBE_TOKEN=squ_123abc...

# .gitignore (CRÍTICO)
.env
*.env
.env.*
!.env.example  # Solo el template
```

---

### 2. AWS Secrets Manager (Production)

**Guardar secretos**:
```bash
# Crear secret
aws secretsmanager create-secret \
  --name dashboardsonar/prod/db \
  --secret-string '{
    "username": "dbadmin",
    "password": "super_secure_password_here",
    "host": "dashboardsonar-db.xxx.eu-west-1.rds.amazonaws.com",
    "port": 5432,
    "database": "dashboardsonar"
  }'

# Guardar SECRET_KEY
aws secretsmanager create-secret \
  --name dashboardsonar/prod/secret-key \
  --secret-string "$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

---

**Recuperar en aplicación**:
```python
# infocodest/config.py
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='eu-west-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

class ProductionConfig:
    # Cargar desde Secrets Manager
    db_secrets = get_secret('dashboardsonar/prod/db')
    DATABASE_URL = f"postgresql://{db_secrets['username']}:{db_secrets['password']}@{db_secrets['host']}/{db_secrets['database']}"

    secret_key = get_secret('dashboardsonar/prod/secret-key')
    SECRET_KEY = secret_key
```

---

### 3. Vault (HashiCorp)

**Alternativa más robusta**:
```bash
# Instalar Vault
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
unzip vault_*.zip
sudo mv vault /usr/local/bin/

# Iniciar Vault
vault server -dev

# Guardar secret
vault kv put secret/dashboardsonar/db \
  username=dbadmin \
  password=secure_password

# Leer secret
vault kv get -field=password secret/dashboardsonar/db
```

---

## 📊 Security Monitoring

### 1. Security Audit Logs

```python
# infocodest/utils/audit_log.py
import logging

audit_logger = logging.getLogger('audit')
audit_handler = logging.FileHandler('/var/log/dashboardsonar/audit.log')
audit_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

def log_security_event(event_type, user, details):
    """Log security-related events"""
    audit_logger.info(
        f"EVENT={event_type} USER={user} IP={request.remote_addr} DETAILS={details}"
    )

# Uso
@app.route('/login', methods=['POST'])
def login():
    if user.check_password(password):
        log_security_event('LOGIN_SUCCESS', user.username, 'User logged in')
    else:
        log_security_event('LOGIN_FAILED', username, 'Invalid password')
```

---

### 2. Intrusion Detection (AIDE)

```bash
# Instalar AIDE
sudo apt install aide

# Inicializar database
sudo aideinit

# Crear baseline
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Check de integridad (diario)
sudo aide --check

# Cron job
echo "0 2 * * * root /usr/bin/aide --check | mail -s 'AIDE Report' security@empresa.com" | sudo tee -a /etc/crontab
```

---

## 📋 Security Checklist

### Pre-Production Security Checklist

**Application**:
- [ ] CSRF protection habilitado
- [ ] Input validation en todos los endpoints
- [ ] SQL queries parametrizadas (no string concatenation)
- [ ] XSS protection (auto-escape en templates)
- [ ] Rate limiting configurado
- [ ] Security headers configurados (CSP, HSTS, X-Frame-Options)
- [ ] File upload validation (si aplica)
- [ ] Error messages no revelan información sensible

**Authentication**:
- [ ] Passwords hasheadas con bcrypt
- [ ] Password policy implementada (12+ caracteres, complejidad)
- [ ] 2FA habilitado para admins
- [ ] Session timeout configurado (<1 hora)
- [ ] Cookies con Secure, HttpOnly, SameSite flags

**Database**:
- [ ] SSL/TLS habilitado para conexiones
- [ ] Usuario de app con permisos mínimos (no SUPERUSER)
- [ ] Encryption at rest habilitado
- [ ] Backups encriptados
- [ ] pg_hba.conf configurado (no 'trust')

**Infrastructure**:
- [ ] OS actualizado (unattended-upgrades configurado)
- [ ] SSH hardening (no root login, solo keys)
- [ ] Firewall configurado (UFW)
- [ ] Fail2Ban instalado
- [ ] Servicios innecesarios deshabilitados

**Network**:
- [ ] HTTPS/TLS configurado (solo TLS 1.2+)
- [ ] Certificados válidos (no self-signed en prod)
- [ ] HSTS habilitado
- [ ] WAF configurado (AWS WAF o similar)

**Secrets**:
- [ ] .env NO commiteado en git
- [ ] Secrets en AWS Secrets Manager (o Vault)
- [ ] SECRET_KEY rotado regularmente
- [ ] Database passwords fuertes (20+ caracteres random)

**Monitoring**:
- [ ] Security audit logs habilitados
- [ ] CloudWatch/SIEM configurado
- [ ] Alertas para eventos críticos (login failures, access denied)
- [ ] Log rotation configurado

**Compliance**:
- [ ] GDPR compliance verificado (si aplica)
- [ ] Política de retención de datos definida
- [ ] Incident response plan documentado

---

## 📚 Referencias

### Documentación Relacionada

- 🚨 **Runbook**: [RUNBOOK.md](../runbooks/RUNBOOK.md)
- 📊 **Monitoring**: [MONITORING_GUIDE.md](../monitoring/MONITORING_GUIDE.md)
- 💾 **Backups**: [BACKUP_RESTORE.md](../backup-recovery/BACKUP_RESTORE.md)
- 🚀 **Deployment**: [DEPLOYMENT_AWS.md](../deployment/DEPLOYMENT_AWS.md)

### Recursos Externos

- 📖 [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- 📖 [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- 📖 [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- 📖 [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- 📖 [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
**Mantenido por**: Equipo Security & DevOps
**Próxima revisión**: Después de cada pentest o incidente de seguridad
