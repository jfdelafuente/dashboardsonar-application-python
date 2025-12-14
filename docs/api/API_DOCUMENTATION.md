# API Documentation - Dashboard Sonar

Documentación completa de todas las rutas, endpoints y APIs del sistema Dashboard Sonar.

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Autenticación](#autenticación)
3. [Web Routes (HTML)](#web-routes-html)
4. [API Endpoints (JSON)](#api-endpoints-json)
5. [Códigos de Estado](#códigos-de-estado)
6. [Ejemplos de Uso](#ejemplos-de-uso)

---

## 🔍 Introducción

Dashboard Sonar expone dos tipos de endpoints:

- **Web Routes**: Devuelven páginas HTML renderizadas (para navegadores)
- **API Endpoints**: Devuelven datos JSON (para consumo programático)

### Base URL

```text
http://localhost:5000
```

### Formato de Respuesta

Las API responses siguen el formato JSON estándar:

```json
{
  "project_name": ["repo1", "repo2"],
  "aplicacion": ["app1", "app2"],
  "fecha": ["2024-01-01", "2024-01-02"],
  "bugs": [10, 5],
  "vulnerabilities": [3, 1]
}
```

---

## 🔐 Autenticación

### Métodos de Autenticación

El sistema utiliza **session-based authentication** con Flask-Login.

#### POST /accounts/register

Registrar un nuevo usuario.

**Request**:
```http
POST /accounts/register
Content-Type: application/x-www-form-urlencoded

username=johndoe&email=john@example.com&password=SecurePass123&confirm=SecurePass123
```

**Response** (HTML):
```html
<!-- Success: Redirect to registration page with success message -->
<!-- Error: Show validation error message -->
```

**Validaciones**:
- Username: requerido, único
- Email: requerido, formato válido, único
- Password: mínimo 6 caracteres
- Confirm: debe coincidir con password

#### POST /accounts/login

Iniciar sesión.

**Request**:
```http
POST /accounts/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=SecurePass123&remember=on
```

**Response** (Redirect):
```text
302 Redirect to /
Set-Cookie: session=...
```

**Errores**:
- 401: Invalid username and/or password

#### GET /accounts/logout

Cerrar sesión (requiere autenticación).

**Request**:
```http
GET /accounts/logout
Cookie: session=...
```

**Response**:
```text
302 Redirect to /accounts/login
```

#### GET /accounts/user/<username>

Ver perfil de usuario.

**Request**:
```http
GET /accounts/user/johndoe
```

**Response** (HTML):
```html
<!-- User profile page -->
```

**Errores**:
- 404: Usuario no encontrado

#### POST /accounts/password

Recuperar contraseña (simulado).

**Request**:
```http
POST /accounts/password
Content-Type: application/x-www-form-urlencoded

email=john@example.com
```

**Response** (HTML):
```html
<!-- Confirmation message -->
```

---

## 🌐 Web Routes (HTML)

Todas las rutas web requieren autenticación (`@login_required`) excepto las de accounts.

### Dashboard Principal

#### GET /

Dashboard principal con KPIs generales.

**Request**:
```http
GET /
Cookie: session=...
```

**Response** (HTML):
- Vista: `home/index.html`
- Datos: KPI overview, fecha actual

**Servicio**: `DashboardService.get_kpi_overview()`

---

### Métricas

#### GET /metricas

Listado de todas las métricas con información del proveedor.

**Request**:
```http
GET /metricas
Cookie: session=...
```

**Response** (HTML):
- Vista: `home/metricas/metricas.html`
- Datos: Todas las métricas con proveedor, KPI overview

**Servicio**: `DashboardService.get_all_metricas_with_proveedor()`

#### GET/POST /metricas/aplicacion

Histórico de métricas por aplicación.

**Request GET**:
```http
GET /metricas/aplicacion
Cookie: session=...
```

**Request POST**:
```http
POST /metricas/aplicacion
Content-Type: application/x-www-form-urlencoded
Cookie: session=...

project_name=MyApp
```

**Response** (HTML):
- Vista: `home/metricas/historico.html`
- Datos GET: Lista de aplicaciones disponibles
- Datos POST: Métricas filtradas por aplicación, KPIs de aplicación

**Servicios**:
- `DashboardService.get_distinct_applications()`
- `DashboardService.get_metricas_by_aplicacion(project)`
- `DashboardService.get_kpi_by_application(project)`

#### GET /metricas/aplicacion/<project>

Histórico de métricas de una aplicación específica.

**Request**:
```http
GET /metricas/aplicacion/MyApp
```

**Response** (HTML):
- Vista: `home/metricas/historico.html`
- Datos: Métricas de la aplicación, KPIs, lista de aplicaciones

#### GET /metricas/aplicacion/<project>/<name>

Histórico detallado de un repositorio específico con gráficos.

**Request**:
```http
GET /metricas/aplicacion/MyApp/my-repo
```

**Response** (HTML):
- Vista: `home/metricas/charts_historico.html`
- Datos: Histórico completo del repositorio

**Servicio**: `DashboardService.get_historico_by_aplicacion_and_repo(project, name)`

#### GET/POST /metricas/proveedores

Métricas agrupadas por proveedor.

**Request POST**:
```http
POST /metricas/proveedores
Content-Type: application/x-www-form-urlencoded
Cookie: session=...

project_name=ProveedorX
```

**Response** (HTML):
- Vista: `home/metricas/proveedores.html`
- Datos: Métricas del proveedor, KPIs del proveedor

**Servicios**:
- `DashboardService.get_distinct_providers()`
- `DashboardService.get_metricas_by_proveedor(project)`
- `DashboardService.get_kpi_by_proveedor(project)`

---

### KPIs

#### GET /kpis

Listado de todos los KPIs.

**Request**:
```http
GET /kpis
Cookie: session=...
```

**Response** (HTML):
- Vista: `home/kpis/kpis.html`
- Datos: Todos los KPIs, overview

**Nota**: Esta ruta usa query directa (legacy): `Metrica.query.all()`

#### GET/POST /kpis/aplicacion

KPIs filtrados por aplicación.

**Request POST**:
```http
POST /kpis/aplicacion
Content-Type: application/x-www-form-urlencoded

project_name=MyApp
```

**Response** (HTML):
- Vista: `home/kpis/kpis_historico.html`
- Datos: KPIs de la aplicación

#### GET /kpis/aplicacion/<project>

KPIs de una aplicación específica.

**Request**:
```http
GET /kpis/aplicacion/MyApp
```

**Response** (HTML):
- Vista: `home/kpis/kpis_historico.html`

#### GET /kpis/aplicacion/<project>/<name>

KPIs con gráficos de un repositorio específico.

**Request**:
```http
GET /kpis/aplicacion/MyApp/my-repo
```

**Response** (HTML):
- Vista: `home/kpis/kpis_charts_historico.html`
- Datos: Histórico del repositorio con gráficos

#### GET/POST /kpis/proveedores

KPIs agrupados por proveedor.

**Request POST**:
```http
POST /kpis/proveedores
Content-Type: application/x-www-form-urlencoded

project_name=ProveedorX
```

**Response** (HTML):
- Vista: `home/kpis/kpis_proveedores.html`
- Datos: KPIs del proveedor

**Nota**: Esta ruta usa query directa con join (legacy)

---

### Estadísticas

#### GET /stats

Estadísticas generales con información del proveedor.

**Request**:
```http
GET /stats
Cookie: session=...
```

**Response** (HTML):
- Vista: `home/stats/stats.html`
- Datos: Todas las estadísticas con proveedor

**Servicio**: `DashboardService.get_all_stats_with_proveedor()`

#### GET/POST /stats/aplicacion

Estadísticas por aplicación.

**Request POST**:
```http
POST /stats/aplicacion
Content-Type: application/x-www-form-urlencoded

project_name=MyApp
```

**Response** (HTML):
- Vista: `home/stats/stats_historico.html`

**Servicio**: `DashboardService.get_stats_by_aplicacion(project)`

#### GET /stats/aplicacion/<project>

Estadísticas de una aplicación específica.

**Request**:
```http
GET /stats/aplicacion/MyApp
```

**Response** (HTML):
- Vista: `home/stats/stats_historico.html`

#### GET/POST /stats/proveedores

Estadísticas por proveedor.

**Request POST**:
```http
POST /stats/proveedores
Content-Type: application/x-www-form-urlencoded

project_name=ProveedorX
```

**Response** (HTML):
- Vista: `home/stats/stats_proveedores.html`

**Servicio**: `DashboardService.get_stats_by_proveedor(project)`

---

### Dailys (Análisis Diarios)

#### GET /dailys

Resumen diario de análisis.

**Request**:
```http
GET /dailys
```

**Response** (HTML):
- Vista: `home/dailys/dailys.html`
- Datos: Resumen diario

**Servicio**: `DashboardService.get_daily_summary()`

#### GET/POST /dailys/aplicacion

Análisis diarios por aplicación.

**Request POST**:
```http
POST /dailys/aplicacion
Content-Type: application/x-www-form-urlencoded

project_name=MyApp
```

**Response** (HTML):
- Vista: `home/dailys/dailys_historico_chart.html`
- Datos: Detalles diarios de la aplicación con gráficos

**Servicio**: `DashboardService.get_daily_details_by_aplicacion(project)`

#### GET /dailys/aplicacion/<project>

Análisis diarios de una aplicación específica.

**Request**:
```http
GET /dailys/aplicacion/MyApp
```

**Response** (HTML):
- Vista: `home/dailys/dailys_historico_chart.html`

#### GET /dailys/aplicacion/<project>/<repo>

Análisis diarios de un repositorio específico.

**Request**:
```http
GET /dailys/aplicacion/MyApp/my-repo
```

**Response** (HTML):
- Vista: `home/dailys/dailys_historico_repo_chart.html`
- Datos: Detalles diarios del repositorio, KPIs del repo

**Servicios**:
- `DashboardService.get_daily_details_by_repo(project, repo)`
- `DashboardService.get_kpi_by_repository(project, repo)`

#### GET/POST /dailys/proveedores

Análisis diarios por proveedor.

**Request POST**:
```http
POST /dailys/proveedores
Content-Type: application/x-www-form-urlencoded

project_name=ProveedorX
```

**Response** (HTML):
- Vista: `home/dailys/dailys_proveedores_chart.html`
- Datos: Análisis diarios del proveedor con gráficos

**Servicio**: `DashboardService.get_daily_by_proveedor(project)`

---

### Charts (Gráficos)

#### GET /charts/

Página principal de gráficos.

**Request**:
```http
GET /charts/
```

**Response** (HTML):
- Vista: `charts/index.html`

#### GET /charts/charts_test

Gráfico de prueba: aplicaciones con múltiples repositorios.

**Request**:
```http
GET /charts/charts_test
```

**Response** (HTML):
- Vista: `charts/charts_test.html`
- Datos: Labels y valores para gráfico

**Servicio**: `MetricaService.get_applications_with_multiple_repos()`

#### GET/POST /charts/charts_historico

Selector de gráficos históricos.

**Request POST**:
```http
POST /charts/charts_historico
Content-Type: application/x-www-form-urlencoded

project_name=MyApp
```

**Response** (HTML):
- Vista: `charts/charts_historico.html`
- Datos: Aplicaciones disponibles, proyecto seleccionado

#### GET /charts/charts_ejemplo

Página de ejemplos de gráficos.

**Request**:
```http
GET /charts/charts_ejemplo
```

**Response** (HTML):
- Vista: `charts/charts_ejemplo.html`

#### GET /charts/charts_radar/<project>/<name>

Gráfico radar de métricas para un repositorio.

**Request**:
```http
GET /charts/charts_radar/MyApp/my-repo
```

**Response** (HTML):
- Vista: `charts/charts_radar.html`
- Parámetros: project, name

---

## 📡 API Endpoints (JSON)

Todos los endpoints bajo `/api/` devuelven datos en formato JSON.

### Métricas API

#### GET /api/aplicacion/<aplicacion>

Obtener métricas de una aplicación.

**Request**:
```http
GET /api/aplicacion/MyApp
```

**Response**:
```json
{
  "project_name": ["repo1", "repo2", "repo3"],
  "aplicacion": ["MyApp", "MyApp", "MyApp"],
  "fecha": ["2024-01-01", "2024-01-15", "2024-02-01"],
  "bugs": [15, 10, 8],
  "vulnerabilities": [5, 3, 2],
  "codesmells": [120, 100, 95]
}
```

**Descripción**: Devuelve todas las métricas de todos los repositorios de una aplicación, ordenadas por fecha ascendente.

**Modelo**: `Metrica`

#### GET /api/aplicacion/<project>/<name>

Obtener histórico de un repositorio específico.

**Request**:
```http
GET /api/aplicacion/MyApp/my-repo
```

**Response**:
```json
{
  "project_name": ["my-repo", "my-repo", "my-repo"],
  "aplicacion": ["MyApp", "MyApp", "MyApp"],
  "fecha": ["2024-01-01", "2024-01-15", "2024-02-01"],
  "bugs": [5, 4, 3],
  "vulnerabilities": [2, 1, 1],
  "codesmells": [45, 40, 38]
}
```

**Descripción**: Devuelve el histórico completo de métricas de un repositorio específico.

**Modelo**: `Historico`

---

### Registros API

#### GET /api/registro?limit=<days>

Obtener registros recientes.

**Request**:
```http
GET /api/registro?limit=30
```

**Query Parameters**:
- `limit`: Número de días hacia atrás (requerido)

**Response**:
```json
[
  {
    "id": 1,
    "aplicacion": "MyApp",
    "repo": "my-repo",
    "created_on": "2024-01-15",
    "status": "success",
    "message": "Analysis completed"
  },
  {
    "id": 2,
    "aplicacion": "MyApp",
    "repo": "other-repo",
    "created_on": "2024-01-16",
    "status": "success",
    "message": "Analysis completed"
  }
]
```

**Descripción**: Devuelve todos los registros de los últimos N días.

**Modelo**: `Registro`

---

### KPIs API

#### GET /api/kpis

Obtener todos los KPIs.

**Request**:
```http
GET /api/kpis
```

**Response**:
```json
[
  {
    "id": 1,
    "aplicacion": "MyApp",
    "repo": "my-repo",
    "fecha": "2024-01-15",
    "bugs": 10,
    "vulnerabilities": 3,
    "code_smells": 50,
    "sqale_rating": "A",
    "reliability_rating": "B",
    "security_rating": "A"
  }
]
```

**Descripción**: Devuelve todas las métricas (KPIs) del sistema.

**Modelo**: `Metrica`

#### GET /api/kpis/<project>/<name>

Obtener histórico de KPIs de un repositorio.

**Request**:
```http
GET /api/kpis/MyApp/my-repo
```

**Response**:
```json
{
  "project_name": ["my-repo", "my-repo"],
  "aplicacion": ["MyApp", "MyApp"],
  "fecha": ["2024-01-01", "2024-01-15"],
  "sqale_debt_ratio": [2.5, 2.3],
  "complexity": [150, 145],
  "duplicated_line_density": [3.2, 3.0],
  "coverage": [85.5, 87.2],
  "ncloc": [15000, 15200]
}
```

**Descripción**: Devuelve métricas técnicas detalladas (deuda técnica, complejidad, cobertura, etc.).

**Modelo**: `Historico`

#### GET /api/rating/<project>/<name>

Obtener histórico de ratings de un repositorio.

**Request**:
```http
GET /api/rating/MyApp/my-repo
```

**Response**:
```json
{
  "project_name": ["my-repo", "my-repo"],
  "aplicacion": ["MyApp", "MyApp"],
  "fecha": ["2024-01-01", "2024-01-15"],
  "sqale_rating": ["A", "A"],
  "reliability_rating": ["B", "A"],
  "security_rating": ["A", "A"]
}
```

**Descripción**: Devuelve el histórico de ratings (A-E) de un repositorio.

**Modelo**: `Metrica`

---

### Daily API

#### GET /api/daily/<aplicacion>

Obtener análisis diarios agregados de una aplicación.

**Request**:
```http
GET /api/daily/MyApp
```

**Response**:
```json
{
  "project_name": ["my-repo", "my-repo"],
  "aplicacion": ["MyApp", "MyApp"],
  "fecha": ["2024-01-15", "2024-01-16"],
  "bugs": [25, 22],
  "vulnerabilities": [8, 7],
  "codesmells": [150, 145],
  "analisis": [5, 5]
}
```

**Descripción**: Devuelve análisis diarios agrupados por fecha, con sumas agregadas de todos los repositorios.

**Modelo**: `Daily`

**Agregación**: `GROUP BY created_on`, `SUM(num_bugs, num_vulnerabilities, num_code_smells, num_analisis)`

#### GET /api/daily/<aplicacion>/<repo>

Obtener análisis diarios de un repositorio específico.

**Request**:
```http
GET /api/daily/MyApp/my-repo
```

**Response**:
```json
{
  "fecha": ["2024-01-15", "2024-01-16"],
  "project_name": ["my-repo", "my-repo"],
  "aplicacion": ["MyApp", "MyApp"],
  "bugs": [10, 8],
  "vulnerabilities": [3, 2],
  "codesmells": [60, 58],
  "analisis": [2, 2]
}
```

**Descripción**: Devuelve análisis diarios de un repositorio específico, agrupados por fecha.

**Modelo**: `Daily`

#### GET /api/daily/by_proveedor/<proveedor>

Obtener análisis diarios agregados por proveedor.

**Request**:
```http
GET /api/daily/by_proveedor/ProveedorX
```

**Response**:
```json
{
  "fecha": ["2024-01-15", "2024-01-16"],
  "proveedor": ["ProveedorX", "ProveedorX"],
  "bugs": [50, 45],
  "vulnerabilities": [15, 12],
  "codesmells": [300, 280],
  "analisis": [10, 10]
}
```

**Descripción**: Devuelve análisis diarios de todos los proyectos de un proveedor, agrupados por fecha.

**Modelo**: `Daily`

**Agregación**: `GROUP BY created_on`, `SUM(num_bugs, num_vulnerabilities, num_code_smells, num_analisis)`

#### GET /api/daily/metrica/<aplicacion>?metrica=<metric_name>

**NOTA**: Endpoint experimental, actualmente no funcional.

**Request**:
```http
GET /api/daily/metrica/MyApp?metrica=bugs
```

**Estado**: ⚠️ No funciona correctamente (query SQL inválida)

---

## 📊 Códigos de Estado

### Códigos HTTP

| Código | Descripción | Uso |
|--------|-------------|-----|
| 200 | OK | Request exitoso |
| 302 | Redirect | Después de login/logout/acciones |
| 401 | Unauthorized | Credenciales inválidas |
| 404 | Not Found | Usuario o recurso no encontrado |
| 500 | Server Error | Error interno del servidor |

### Flash Messages

Las web routes utilizan Flask flash messages:

| Categoría | Uso |
|-----------|-----|
| `info` | Mensajes informativos |
| `success` | Operación exitosa |
| `danger` | Errores, credenciales inválidas |

---

## 💻 Ejemplos de Uso

### Ejemplo 1: Login y Acceso al Dashboard

```bash
# 1. Login
curl -X POST http://localhost:5000/accounts/login \
  -d "username=admin&password=secret123" \
  -c cookies.txt

# 2. Acceder al dashboard
curl http://localhost:5000/ \
  -b cookies.txt

# 3. Obtener métricas de una aplicación
curl http://localhost:5000/api/aplicacion/MyApp \
  -H "Accept: application/json"
```

### Ejemplo 2: Obtener Análisis Diarios con Python

```python
import requests

# Obtener análisis diarios de una aplicación
response = requests.get('http://localhost:5000/api/daily/MyApp')
data = response.json()

# Procesar datos
for i in range(len(data['fecha'])):
    fecha = data['fecha'][i]
    bugs = data['bugs'][i]
    vulnerabilities = data['vulnerabilities'][i]
    print(f"{fecha}: {bugs} bugs, {vulnerabilities} vulnerabilities")
```

### Ejemplo 3: Obtener Histórico de un Repositorio

```python
import requests
import matplotlib.pyplot as plt

# Obtener datos históricos
response = requests.get('http://localhost:5000/api/aplicacion/MyApp/my-repo')
data = response.json()

# Crear gráfico
plt.figure(figsize=(10, 6))
plt.plot(data['fecha'], data['bugs'], label='Bugs', marker='o')
plt.plot(data['fecha'], data['vulnerabilities'], label='Vulnerabilities', marker='s')
plt.plot(data['fecha'], data['codesmells'], label='Code Smells', marker='^')
plt.xlabel('Fecha')
plt.ylabel('Count')
plt.title(f'Métricas - {data["aplicacion"][0]}/{data["project_name"][0]}')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### Ejemplo 4: Obtener KPIs Técnicos

```bash
# Obtener métricas técnicas detalladas
curl http://localhost:5000/api/kpis/MyApp/my-repo | jq .

# Output:
# {
#   "project_name": ["my-repo", "my-repo"],
#   "aplicacion": ["MyApp", "MyApp"],
#   "fecha": ["2024-01-01", "2024-01-15"],
#   "sqale_debt_ratio": [2.5, 2.3],
#   "complexity": [150, 145],
#   "coverage": [85.5, 87.2]
# }
```

### Ejemplo 5: Dashboard Automation Script

```python
#!/usr/bin/env python3
"""
Script para obtener resumen diario de todas las aplicaciones
"""
import requests
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def get_daily_summary():
    """Obtiene resumen diario de todas las aplicaciones"""
    # Login
    session = requests.Session()
    session.post(f'{BASE_URL}/accounts/login', data={
        'username': 'admin',
        'password': 'secret123'
    })

    # Obtener todas las aplicaciones
    # (necesitarías un endpoint para esto, o hardcodearlo)
    applications = ['MyApp', 'OtherApp', 'ThirdApp']

    print(f"Dashboard Summary - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)

    for app in applications:
        response = requests.get(f'{BASE_URL}/api/daily/{app}')
        data = response.json()

        if data['fecha']:
            last_date = data['fecha'][-1]
            bugs = data['bugs'][-1]
            vulnerabilities = data['vulnerabilities'][-1]
            codesmells = data['codesmells'][-1]

            print(f"\n{app}:")
            print(f"  Last Analysis: {last_date}")
            print(f"  Bugs: {bugs}")
            print(f"  Vulnerabilities: {vulnerabilities}")
            print(f"  Code Smells: {codesmells}")

if __name__ == '__main__':
    get_daily_summary()
```

### Ejemplo 6: Integración con CI/CD

```bash
#!/bin/bash
# Script para verificar calidad después de deploy

APP_NAME="MyApp"
REPO_NAME="my-repo"
API_URL="http://dashboard.example.com"

# Obtener últimas métricas
response=$(curl -s "${API_URL}/api/aplicacion/${APP_NAME}/${REPO_NAME}")

# Extraer bugs del último análisis
bugs=$(echo $response | jq '.bugs[-1]')
vulnerabilities=$(echo $response | jq '.vulnerabilities[-1]')

# Verificar umbrales
if [ $bugs -gt 10 ] || [ $vulnerabilities -gt 5 ]; then
    echo "❌ Quality gate failed!"
    echo "Bugs: $bugs (max: 10)"
    echo "Vulnerabilities: $vulnerabilities (max: 5)"
    exit 1
else
    echo "✅ Quality gate passed!"
    exit 0
fi
```

---

## 🔧 Notas Técnicas

### Arquitectura de Servicios

Las web routes utilizan la capa de servicios refactorizada:

- `DashboardService`: Lógica de negocio principal
- `MetricaService`: Operaciones sobre métricas
- `AuthService`: Autenticación y gestión de usuarios

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para más detalles.

### Queries Legacy

Algunos endpoints aún contienen queries SQL directas (marcados como legacy):

- `/kpis`: `Metrica.query.all()`
- `/kpis/proveedores` (POST): Query con JOIN directo

**TODO**: Migrar a repositorios en futuras fases.

### Paginación

⚠️ **Limitación actual**: Los endpoints de API no implementan paginación.

Para grandes volúmenes de datos, considerar:
- Implementar paginación en repositorios
- Añadir parámetros `?page=1&per_page=50`
- Devolver metadata de paginación en responses

### Rate Limiting

⚠️ **Limitación actual**: No hay rate limiting implementado.

Para producción, considerar:
- Implementar Flask-Limiter
- Definir límites por endpoint
- Proteger endpoints públicos

### CORS

⚠️ **Limitación actual**: CORS no está configurado.

Para consumo desde frontend separado:
```python
from flask_cors import CORS

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "https://frontend.example.com"}})
```

---

## 📈 Métricas Disponibles

### Métricas de Calidad

| Métrica | Descripción | Fuente |
|---------|-------------|--------|
| `bugs` | Número de bugs detectados | SonarQube |
| `vulnerabilities` | Número de vulnerabilidades | SonarQube |
| `code_smells` | Número de code smells | SonarQube |
| `sqale_rating` | Rating de mantenibilidad (A-E) | SonarQube |
| `reliability_rating` | Rating de confiabilidad (A-E) | SonarQube |
| `security_rating` | Rating de seguridad (A-E) | SonarQube |

### Métricas Técnicas

| Métrica | Descripción | Fuente |
|---------|-------------|--------|
| `sqale_debt_ratio` | Ratio de deuda técnica (%) | SonarQube |
| `complexity` | Complejidad ciclomática | SonarQube |
| `duplicated_line_density` | Densidad de líneas duplicadas (%) | SonarQube |
| `coverage` | Cobertura de tests (%) | SonarQube |
| `ncloc` | Número de líneas de código | SonarQube |

### Métricas Diarias

| Métrica | Descripción | Cálculo |
|---------|-------------|---------|
| `num_bugs` | Bugs encontrados en el día | Daily |
| `num_vulnerabilities` | Vulnerabilidades del día | Daily |
| `num_code_smells` | Code smells del día | Daily |
| `num_analisis` | Número de análisis ejecutados | Daily |

---

## 🚀 Próximos Pasos

### Mejoras Planificadas

1. **API REST Completa**:
   - Implementar CRUD completo para métricas
   - Añadir endpoints de configuración
   - Versionar API (`/api/v1/...`)

2. **Autenticación API**:
   - Implementar JWT tokens
   - API keys para servicios externos
   - OAuth2 para integraciones

3. **Documentación OpenAPI**:
   - Generar spec OpenAPI 3.0
   - Integrar Swagger UI
   - Ejemplos interactivos

4. **Webhooks**:
   - Notificaciones de nuevos análisis
   - Alertas de umbrales superados
   - Integraciones con Slack/Teams

5. **GraphQL**:
   - Endpoint GraphQL para queries flexibles
   - Reducir over-fetching de datos

---

## 📚 Referencias

- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del sistema
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Guía de desarrollo
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migración de código legacy
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)

---

**Última actualización**: 2025-12-14
**Versión**: v1.10.0-phase-10
**Mantenedor**: Dashboard Sonar Team
