# AWS Deployment Guide - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: DevOps, SRE, Cloud Engineers
**Cloud Provider**: Amazon Web Services (AWS)

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitecturas de Deployment](#arquitecturas-de-deployment)
3. [Opción 1: EC2 + RDS (Recomendado)](#opción-1-ec2--rds-recomendado)
4. [Opción 2: ECS Fargate (Serverless)](#opción-2-ecs-fargate-serverless)
5. [Opción 3: Elastic Beanstalk (Managed)](#opción-3-elastic-beanstalk-managed)
6. [Networking & Security](#networking--security)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Scaling & Performance](#scaling--performance)
9. [Cost Optimization](#cost-optimization)

---

## 🎯 Introducción

### ¿Por qué AWS?

**Ventajas**:
- ✅ **Escalabilidad**: De 10 a 10,000 usuarios sin reescribir código
- ✅ **Alta disponibilidad**: 99.99% SLA con Multi-AZ
- ✅ **Managed services**: RDS, ELB, CloudWatch automatizan operaciones
- ✅ **Seguridad**: VPC, Security Groups, IAM roles
- ✅ **Backups automáticos**: RDS automated backups

**Desventajas**:
- ❌ **Costo**: $100-500/mes (vs $20/mes en VPS básico)
- ❌ **Complejidad**: Curva de aprendizaje para AWS
- ❌ **Vendor lock-in**: Difícil migrar a otra cloud

---

### Prerequisitos

**Cuenta AWS**:
- [ ] Cuenta AWS creada
- [ ] Billing configurado
- [ ] IAM user con permisos AdministratorAccess (o permisos específicos: EC2, RDS, VPC, IAM)

**Herramientas locales**:
```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar
aws --version

# Configurar credenciales
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: eu-west-1 (o us-east-1)
# Default output format: json
```

---

## 🏗️ Arquitecturas de Deployment

### Comparación de Opciones

| Arquitectura | Complejidad | Costo/mes | Escalabilidad | Gestión | Uso Recomendado |
|--------------|-------------|-----------|---------------|---------|-----------------|
| **EC2 + RDS** | Media | $150-300 | Alta (manual) | Manual | Producción estándar |
| **ECS Fargate** | Alta | $200-400 | Automática | Semi-managed | Microservicios |
| **Elastic Beanstalk** | Baja | $100-200 | Automática | Fully-managed | Prototipo rápido |
| **Lambda + API Gateway** | Muy alta | $50-100 | Infinita | Serverless | Tráfico muy variable |

**Recomendación para Dashboard Sonar**: **EC2 + RDS** (balance entre costo, control y simplicidad).

---

### Arquitectura Objetivo: EC2 + RDS

```
                                   ┌──────────────────────────────────┐
                                   │         AWS Region               │
                                   │       (eu-west-1)                │
┌──────────────┐                   │                                  │
│              │                   │  ┌────────────────────────────┐  │
│   Internet   │──────────────────────▶│   Application Load          │  │
│              │                   │  │   Balancer (ALB)            │  │
└──────────────┘                   │  │   (HTTPS/SSL)               │  │
                                   │  └────────┬───────────────────┘  │
                                   │           │                      │
                                   │  ┌────────▼──────────┐           │
                                   │  │  Target Group     │           │
                                   │  └────────┬──────────┘           │
                                   │           │                      │
                    ┌──────────────┼───────────┴─────────┐            │
                    │              │                     │            │
       ┌────────────▼──────────┐   │   ┌────────────────▼──────────┐ │
       │ Availability Zone 1    │   │   │ Availability Zone 2      │ │
       │                        │   │   │                          │ │
       │  ┌──────────────────┐  │   │   │  ┌──────────────────┐   │ │
       │  │ EC2 Instance     │  │   │   │  │ EC2 Instance     │   │ │
       │  │ (t3.medium)      │  │   │   │  │ (t3.medium)      │   │ │
       │  │ - Gunicorn       │  │   │   │  │ - Gunicorn       │   │ │
       │  │ - Flask App      │  │   │   │  │ - Flask App      │   │ │
       │  └────────┬─────────┘  │   │   │  └────────┬─────────┘   │ │
       │           │             │   │   │           │             │ │
       └───────────┼─────────────┘   │   └───────────┼─────────────┘ │
                   │                 │               │               │
                   └─────────────────┼───────────────┘               │
                                     │                               │
                                     │  ┌──────────────────────────┐ │
                                     │  │   RDS PostgreSQL         │ │
                                     │  │   (Multi-AZ)             │ │
                                     │  │   db.t3.medium           │ │
                                     │  └──────────────────────────┘ │
                                     │                               │
                                     │  ┌──────────────────────────┐ │
                                     │  │   S3 Bucket              │ │
                                     │  │   (Backups, Logs)        │ │
                                     │  └──────────────────────────┘ │
                                     │                               │
                                     └───────────────────────────────┘
```

**Componentes**:
- **ALB**: Application Load Balancer (HTTPS, SSL termination)
- **EC2**: 2x t3.medium (para alta disponibilidad)
- **RDS**: PostgreSQL 13 Multi-AZ (automatic failover)
- **S3**: Backups, logs, static files
- **CloudWatch**: Monitoring, logs, alertas

---

## 🚀 Opción 1: EC2 + RDS (Recomendado)

### Paso 1: Crear VPC y Subnets

**¿Qué es VPC?**: Virtual Private Cloud - red privada aislada en AWS.

```bash
# Crear VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' \
  --output text)

aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=dashboardsonar-vpc

# Habilitar DNS
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

echo "VPC ID: $VPC_ID"
```

---

**Crear Subnets** (2 públicas + 2 privadas en diferentes AZs):

```bash
# Subnet Pública 1 (AZ1) - Para ALB y NAT
SUBNET_PUBLIC_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone eu-west-1a \
  --query 'Subnet.SubnetId' \
  --output text)

aws ec2 create-tags --resources $SUBNET_PUBLIC_1 --tags Key=Name,Value=Public-1a

# Subnet Pública 2 (AZ2)
SUBNET_PUBLIC_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone eu-west-1b \
  --query 'Subnet.SubnetId' \
  --output text)

aws ec2 create-tags --resources $SUBNET_PUBLIC_2 --tags Key=Name,Value=Public-1b

# Subnet Privada 1 (AZ1) - Para EC2
SUBNET_PRIVATE_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone eu-west-1a \
  --query 'Subnet.SubnetId' \
  --output text)

aws ec2 create-tags --resources $SUBNET_PRIVATE_1 --tags Key=Name,Value=Private-1a

# Subnet Privada 2 (AZ2) - Para RDS
SUBNET_PRIVATE_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.12.0/24 \
  --availability-zone eu-west-1b \
  --query 'Subnet.SubnetId' \
  --output text)

aws ec2 create-tags --resources $SUBNET_PRIVATE_2 --tags Key=Name,Value=Private-1b
```

---

**Internet Gateway** (para acceso a internet):

```bash
# Crear Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)

aws ec2 create-tags --resources $IGW_ID --tags Key=Name,Value=dashboardsonar-igw

# Attachar a VPC
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# Crear Route Table para subnets públicas
RTB_PUBLIC=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' \
  --output text)

aws ec2 create-tags --resources $RTB_PUBLIC --tags Key=Name,Value=Public-RT

# Agregar ruta a Internet Gateway
aws ec2 create-route --route-table-id $RTB_PUBLIC --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID

# Asociar subnets públicas
aws ec2 associate-route-table --subnet-id $SUBNET_PUBLIC_1 --route-table-id $RTB_PUBLIC
aws ec2 associate-route-table --subnet-id $SUBNET_PUBLIC_2 --route-table-id $RTB_PUBLIC
```

---

### Paso 2: Crear Security Groups

**Security Group para ALB**:

```bash
SG_ALB=$(aws ec2 create-security-group \
  --group-name dashboardsonar-alb-sg \
  --description "Security group for ALB" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Permitir HTTP (80) desde internet
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ALB \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Permitir HTTPS (443) desde internet
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ALB \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

echo "ALB Security Group: $SG_ALB"
```

---

**Security Group para EC2**:

```bash
SG_EC2=$(aws ec2 create-security-group \
  --group-name dashboardsonar-ec2-sg \
  --description "Security group for EC2 instances" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Permitir tráfico desde ALB (puerto 5000 - Gunicorn)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2 \
  --protocol tcp \
  --port 5000 \
  --source-group $SG_ALB

# Permitir SSH desde tu IP (para management)
# Reemplazar YOUR_IP con tu IP pública
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2 \
  --protocol tcp \
  --port 22 \
  --cidr YOUR_IP/32

echo "EC2 Security Group: $SG_EC2"
```

---

**Security Group para RDS**:

```bash
SG_RDS=$(aws ec2 create-security-group \
  --group-name dashboardsonar-rds-sg \
  --description "Security group for RDS PostgreSQL" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Permitir PostgreSQL (5432) desde EC2
aws ec2 authorize-security-group-ingress \
  --group-id $SG_RDS \
  --protocol tcp \
  --port 5432 \
  --source-group $SG_EC2

echo "RDS Security Group: $SG_RDS"
```

---

### Paso 3: Crear RDS PostgreSQL

**DB Subnet Group** (para Multi-AZ):

```bash
aws rds create-db-subnet-group \
  --db-subnet-group-name dashboardsonar-db-subnet \
  --db-subnet-group-description "Subnet group for Dashboard Sonar RDS" \
  --subnet-ids $SUBNET_PRIVATE_1 $SUBNET_PRIVATE_2
```

---

**Crear RDS Instance**:

```bash
aws rds create-db-instance \
  --db-instance-identifier dashboardsonar-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 13.11 \
  --master-username dbadmin \
  --master-user-password 'YourSecurePassword123!' \
  --allocated-storage 20 \
  --storage-type gp3 \
  --storage-encrypted \
  --db-name dashboardsonar \
  --vpc-security-group-ids $SG_RDS \
  --db-subnet-group-name dashboardsonar-db-subnet \
  --multi-az \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "sun:04:00-sun:05:00" \
  --enable-cloudwatch-logs-exports '["postgresql","upgrade"]' \
  --deletion-protection

echo "⏳ RDS creándose... (tarda ~10 minutos)"
echo "Verificar status:"
echo "aws rds describe-db-instances --db-instance-identifier dashboardsonar-db"
```

**Esperar a que esté disponible**:

```bash
aws rds wait db-instance-available --db-instance-identifier dashboardsonar-db
echo "✅ RDS disponible"

# Obtener endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier dashboardsonar-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"
```

---

### Paso 4: Crear EC2 Instances

**Key Pair** (para SSH):

```bash
aws ec2 create-key-pair \
  --key-name dashboardsonar-key \
  --query 'KeyMaterial' \
  --output text > dashboardsonar-key.pem

chmod 400 dashboardsonar-key.pem
```

---

**Launch EC2 Instance** (Ubuntu 22.04):

```bash
# Buscar AMI de Ubuntu 22.04
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)

echo "AMI: $AMI_ID"

# User data script (instalación automática)
cat > user-data.sh <<'EOF'
#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y \
  python3.12 \
  python3.12-venv \
  python3-pip \
  git \
  postgresql-client \
  nginx

# Create app directory
mkdir -p /opt/dashboardsonar
cd /opt/dashboardsonar

# Clone repository
git clone https://github.com/jfdelafuente/dashboardsonar-application-python.git .

# Create virtualenv
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env file (will be updated with actual values)
cat > .env <<'ENVEOF'
SECRET_KEY=temp_secret_key
DATABASE_URL=postgresql://dbadmin:password@RDS_ENDPOINT/dashboardsonar
FLASK_ENV=production
LOG_LEVEL=INFO
ENVEOF

# Create systemd service
cat > /etc/systemd/system/dashboardsonar.service <<'SERVICEEOF'
[Unit]
Description=Dashboard Sonar Flask Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/dashboardsonar
Environment="PATH=/opt/dashboardsonar/venv/bin"
ExecStart=/opt/dashboardsonar/venv/bin/gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --access-logfile /var/log/dashboardsonar/access.log \
  --error-logfile /var/log/dashboardsonar/error.log \
  "infocodest:create_app()"

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Create log directory
mkdir -p /var/log/dashboardsonar
chown -R ubuntu:ubuntu /var/log/dashboardsonar

# Set permissions
chown -R ubuntu:ubuntu /opt/dashboardsonar

# Enable and start service
systemctl daemon-reload
systemctl enable dashboardsonar
systemctl start dashboardsonar

echo "✅ Dashboard Sonar instalado"
EOF

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.medium \
  --key-name dashboardsonar-key \
  --security-group-ids $SG_EC2 \
  --subnet-id $SUBNET_PRIVATE_1 \
  --user-data file://user-data.sh \
  --iam-instance-profile Name=DashboardSonarEC2Role \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=dashboardsonar-app-1}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"
echo "⏳ Esperando que la instancia esté corriendo..."

aws ec2 wait instance-running --instance-ids $INSTANCE_ID
echo "✅ Instancia corriendo"
```

---

**Configurar .env con valores reales**:

```bash
# SSH a la instancia (via bastion host o Session Manager)
ssh -i dashboardsonar-key.pem ubuntu@INSTANCE_PRIVATE_IP

# Actualizar .env
sudo nano /opt/dashboardsonar/.env

# Actualizar:
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=postgresql://dbadmin:YourSecurePassword123!@$RDS_ENDPOINT/dashboardsonar

# Reiniciar servicio
sudo systemctl restart dashboardsonar

# Verificar logs
sudo journalctl -u dashboardsonar -f
```

---

### Paso 5: Crear Application Load Balancer

**Target Group**:

```bash
TG_ARN=$(aws elbv2 create-target-group \
  --name dashboardsonar-tg \
  --protocol HTTP \
  --port 5000 \
  --vpc-id $VPC_ID \
  --health-check-enabled \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

echo "Target Group ARN: $TG_ARN"
```

---

**Registrar EC2 instance en Target Group**:

```bash
aws elbv2 register-targets \
  --target-group-arn $TG_ARN \
  --targets Id=$INSTANCE_ID
```

---

**Crear ALB**:

```bash
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name dashboardsonar-alb \
  --subnets $SUBNET_PUBLIC_1 $SUBNET_PUBLIC_2 \
  --security-groups $SG_ALB \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

echo "ALB ARN: $ALB_ARN"

# Obtener DNS del ALB
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns $ALB_ARN \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "✅ ALB DNS: $ALB_DNS"
echo "Acceder en: http://$ALB_DNS"
```

---

**Crear Listener (HTTP)**:

```bash
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

---

**Configurar HTTPS con ACM** (opcional pero recomendado):

```bash
# 1. Request SSL certificate
CERT_ARN=$(aws acm request-certificate \
  --domain-name dashboard-sonar.empresa.com \
  --validation-method DNS \
  --query 'CertificateArn' \
  --output text)

# 2. Validar DNS (agregar CNAME en Route53 o tu DNS provider)
aws acm describe-certificate --certificate-arn $CERT_ARN

# 3. Una vez validado, crear listener HTTPS
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN

# 4. Redirigir HTTP → HTTPS
aws elbv2 modify-listener \
  --listener-arn $(aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --query 'Listeners[?Protocol==`HTTP`].ListenerArn' --output text) \
  --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'
```

---

### Paso 6: Configurar CloudWatch Monitoring

**Instalar CloudWatch Agent en EC2**:

```bash
# SSH a la instancia
ssh -i dashboardsonar-key.pem ubuntu@INSTANCE_IP

# Descargar e instalar CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Crear configuración
sudo tee /opt/aws/amazon-cloudwatch-agent/etc/config.json <<'EOF'
{
  "metrics": {
    "namespace": "DashboardSonar",
    "metrics_collected": {
      "cpu": {
        "measurement": [{"name": "cpu_usage_idle", "rename": "CPU_IDLE", "unit": "Percent"}],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": [{"name": "used_percent", "rename": "DISK_USED", "unit": "Percent"}],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "mem": {
        "measurement": [{"name": "mem_used_percent", "rename": "MEM_USED", "unit": "Percent"}],
        "metrics_collection_interval": 60
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/dashboardsonar/app.log",
            "log_group_name": "/dashboardsonar/application",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

# Iniciar CloudWatch Agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

---

**Crear CloudWatch Alarms**:

```bash
# Alarm: CPU > 80%
aws cloudwatch put-metric-alarm \
  --alarm-name dashboardsonar-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --alarm-actions arn:aws:sns:eu-west-1:ACCOUNT_ID:ops-alerts

# Alarm: Memory > 85%
aws cloudwatch put-metric-alarm \
  --alarm-name dashboardsonar-high-memory \
  --alarm-description "Alert when memory exceeds 85%" \
  --metric-name MEM_USED \
  --namespace DashboardSonar \
  --statistic Average \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --alarm-actions arn:aws:sns:eu-west-1:ACCOUNT_ID:ops-alerts
```

---

## 🐳 Opción 2: ECS Fargate (Serverless)

### ¿Cuándo usar ECS Fargate?

**Ventajas**:
- ✅ No gestionar servidores (serverless)
- ✅ Auto-scaling automático
- ✅ Pago por uso (no pagas cuando no hay tráfico)

**Desventajas**:
- ❌ Más complejo que EC2
- ❌ Más caro para tráfico constante
- ❌ Requiere containerización (Docker)

---

### Paso 1: Crear Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run Gunicorn
CMD ["gunicorn", \
     "--workers", "4", \
     "--bind", "0.0.0.0:5000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "infocodest:create_app()"]
```

---

### Paso 2: Build & Push a ECR

```bash
# Crear ECR repository
aws ecr create-repository --repository-name dashboardsonar

# Login a ECR
aws ecr get-login-password --region eu-west-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com

# Build image
docker build -t dashboardsonar .

# Tag image
docker tag dashboardsonar:latest ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/dashboardsonar:latest

# Push image
docker push ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/dashboardsonar:latest
```

---

### Paso 3: Crear ECS Cluster

```bash
aws ecs create-cluster --cluster-name dashboardsonar-cluster
```

---

### Paso 4: Task Definition

```json
{
  "family": "dashboardsonar-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "dashboardsonar",
      "image": "ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/dashboardsonar:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "FLASK_ENV", "value": "production"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {"name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dashboardsonar",
          "awslogs-region": "eu-west-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

---

### Paso 5: Create ECS Service

```bash
aws ecs create-service \
  --cluster dashboardsonar-cluster \
  --service-name dashboardsonar-service \
  --task-definition dashboardsonar-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_PRIVATE_1,$SUBNET_PRIVATE_2],securityGroups=[$SG_ECS],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$TG_ARN,containerName=dashboardsonar,containerPort=5000"
```

---

## 🎈 Opción 3: Elastic Beanstalk (Managed)

**Más simple** para empezar rápido.

### Deployment con EB CLI

```bash
# Instalar EB CLI
pip install awsebcli

# Inicializar
eb init -p python-3.12 dashboardsonar --region eu-west-1

# Crear .ebextensions/python.config
mkdir -p .ebextensions
cat > .ebextensions/python.config <<EOF
option_settings:
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
  aws:elasticbeanstalk:container:python:
    WSGIPath: "infocodest:create_app()"
EOF

# Crear environment
eb create dashboardsonar-prod \
  --database.engine postgres \
  --database.username dbadmin \
  --envvars SECRET_KEY=xxx,DATABASE_URL=xxx

# Deploy
eb deploy

# Acceder
eb open
```

---

## 🔒 Networking & Security

### VPC Best Practices

**Arquitectura 3-tier**:
```
┌─────────────────────────────────────────┐
│ Public Subnets (DMZ)                    │
│ - ALB                                   │
│ - NAT Gateway                           │
│ - Bastion Host                          │
└─────────────────────────────────────────┘
           ↓ (Security Group rules)
┌─────────────────────────────────────────┐
│ Private Subnets (Application)           │
│ - EC2 Instances                         │
│ - ECS Tasks                             │
└─────────────────────────────────────────┘
           ↓ (Security Group rules)
┌─────────────────────────────────────────┐
│ Private Subnets (Database)              │
│ - RDS                                   │
│ - ElastiCache (si se usa)               │
└─────────────────────────────────────────┘
```

---

### IAM Roles

**EC2 Instance Role**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::dashboardsonar-backups/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:dashboardsonar/*"
    }
  ]
}
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions + AWS

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/dashboardsonar:$IMAGE_TAG .
          docker push $ECR_REGISTRY/dashboardsonar:$IMAGE_TAG

      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster dashboardsonar-cluster \
            --service dashboardsonar-service \
            --force-new-deployment
```

---

## 📈 Scaling & Performance

### Auto Scaling Group (EC2)

```bash
# Create Launch Template
aws ec2 create-launch-template \
  --launch-template-name dashboardsonar-lt \
  --version-description "v1" \
  --launch-template-data '{
    "ImageId": "'$AMI_ID'",
    "InstanceType": "t3.medium",
    "KeyName": "dashboardsonar-key",
    "SecurityGroupIds": ["'$SG_EC2'"],
    "UserData": "..."
  }'

# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name dashboardsonar-asg \
  --launch-template LaunchTemplateName=dashboardsonar-lt,Version=1 \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2 \
  --vpc-zone-identifier "$SUBNET_PRIVATE_1,$SUBNET_PRIVATE_2" \
  --target-group-arns $TG_ARN \
  --health-check-type ELB \
  --health-check-grace-period 300

# Scaling Policy (CPU > 70%)
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name dashboardsonar-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 70.0
  }'
```

---

## 💰 Cost Optimization

### Estimación de Costos Mensual

**Opción 1: EC2 + RDS**:
```
- EC2 (2x t3.medium):        $60/mes
- RDS (db.t3.medium Multi-AZ): $120/mes
- ALB:                        $20/mes
- Data Transfer:              $10/mes
- CloudWatch:                 $5/mes
- S3 (backups):               $5/mes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:                        ~$220/mes
```

**Optimizaciones**:
1. **Reserved Instances**: Ahorrar 40% (compromiso 1-3 años)
2. **Savings Plans**: Ahorrar 30-50%
3. **Spot Instances**: Ahorrar 70% (para entornos dev/test)
4. **RDS Single-AZ** (dev): Ahorrar 50% en RDS

---

## 📚 Referencias

### Documentación AWS

- [EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [RDS User Guide](https://docs.aws.amazon.com/rds/)
- [ECS Developer Guide](https://docs.aws.amazon.com/ecs/)
- [ALB User Guide](https://docs.aws.amazon.com/elasticloadbalancing/)

### Documentación Relacionada

- 🚨 **Runbook**: [RUNBOOK.md](../runbooks/RUNBOOK.md)
- 📊 **Monitoring**: [MONITORING_GUIDE.md](../monitoring/MONITORING_GUIDE.md)
- 💾 **Backups**: [BACKUP_RESTORE.md](../backup-recovery/BACKUP_RESTORE.md)
- 🔒 **Security**: [SECURITY_HARDENING.md](../security/SECURITY_HARDENING.md)

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
**Mantenido por**: Equipo DevOps
