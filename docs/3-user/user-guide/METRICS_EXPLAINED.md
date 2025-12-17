# Métricas Explicadas - Dashboard Sonar

**Versión**: 1.0.0
**Fecha**: Diciembre 2025
**Audiencia**: Usuarios finales, gestores, desarrolladores

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Reliability Rating](#reliability-rating)
3. [Security Rating](#security-rating)
4. [Maintainability Rating](#maintainability-rating)
5. [Coverage (Cobertura de Tests)](#coverage-cobertura-de-tests)
6. [Duplicación de Código](#duplicación-de-código)
7. [Complejidad Ciclomática](#complejidad-ciclomática)
8. [Deuda Técnica](#deuda-técnica)
9. [Quality Gates](#quality-gates)
10. [Tamaño del Proyecto](#tamaño-del-proyecto)
11. [Interpretación Conjunta](#interpretación-conjunta)
12. [Umbrales Recomendados](#umbrales-recomendados)

---

## 🎯 Introducción

Esta guía explica en detalle **cada métrica** que verás en Dashboard Sonar, incluyendo:

- ✅ **Qué mide** cada métrica
- ✅ **Cómo se calcula**
- ✅ **Qué valores son buenos o malos**
- ✅ **Por qué importa** para tu proyecto
- ✅ **Cómo mejorar** cada métrica
- ✅ **Ejemplos prácticos**

**Prerequisito**: Lee primero [WHAT_IS_DASHBOARD_SONAR.md](../getting-started/WHAT_IS_DASHBOARD_SONAR.md) para conceptos básicos.

---

## 🐛 Reliability Rating

### ¿Qué mide?

La **confiabilidad** del código, es decir, la probabilidad de que funcione correctamente sin errores (bugs).

### Escala de Calificación

| Rating | Condición | Significado | Impacto en Producción |
|--------|-----------|-------------|----------------------|
| **A** | 0 bugs | Excelente - Sin bugs detectados | 🟢 Muy bajo riesgo de fallos |
| **B** | Al menos 1 bug menor | Bueno - Bugs de bajo impacto | 🟢 Bajo riesgo |
| **C** | Al menos 1 bug mayor | Medio - Bugs que afectan funcionalidad | 🟡 Riesgo moderado |
| **D** | Al menos 1 bug crítico | Malo - Bugs que causan fallos importantes | 🟠 Alto riesgo |
| **E** | Al menos 1 bug bloqueante | Muy malo - Bugs que impiden uso | 🔴 **Crítico** - No desplegar |

### Tipos de Bugs

#### 1. Bug Bloqueante (Blocker)
**Severidad**: 🔴 Crítica

**Ejemplos**:
- NullPointerException que crashea la aplicación
- División por cero sin validación
- Infinite loop que congela el sistema
- Memory leak crítico

**Impacto**: La aplicación **no puede funcionar**.

---

#### 2. Bug Crítico (Critical)
**Severidad**: 🟠 Alta

**Ejemplos**:
- Pérdida de datos del usuario
- Fallo en proceso de pago
- Brecha de seguridad grave
- Error que afecta flujo principal

**Impacto**: Funcionalidad principal **no funciona correctamente**.

---

#### 3. Bug Mayor (Major)
**Severidad**: 🟡 Media

**Ejemplos**:
- Cálculo incorrecto en reportes
- Validación de formulario faltante
- Error en feature secundario
- Performance degradado

**Impacto**: Funcionalidad **parcialmente afectada**.

---

#### 4. Bug Menor (Minor)
**Severidad**: 🟢 Baja

**Ejemplos**:
- Typo en mensaje de error
- UI elemento mal alineado
- Log message incorrecto
- Código difícil de leer

**Impacto**: **Estético** o de mantenibilidad, no afecta funcionalidad.

---

### ¿Cómo se calcula?

SonarQube detecta bugs analizando el código en busca de **patrones problemáticos**:

**Ejemplo de bug detectado**:
```python
# Bug: Posible división por cero
def calcular_promedio(total, cantidad):
    return total / cantidad  # ❌ Si cantidad=0, crashea
```

**Código correcto**:
```python
def calcular_promedio(total, cantidad):
    if cantidad == 0:
        return 0
    return total / cantidad  # ✅ Validación agregada
```

El rating se asigna según el **bug de mayor severidad**:
- Si hay 1 bug bloqueante → Rating E (sin importar cuántos bugs menores haya)
- Si hay solo bugs menores → Rating B

### ¿Por qué importa?

| Rating | Consecuencias en Producción |
|--------|----------------------------|
| **E** o **D** | 🔴 Crashs frecuentes, usuarios frustrados, pérdida de confianza |
| **C** | 🟡 Comportamiento inconsistente, reportes incorrectos |
| **B** o **A** | 🟢 Aplicación estable y confiable |

**Ejemplo real**: Un proyecto con Rating E tuvo 15 incidentes críticos en producción en 1 mes. Después de arreglar bugs → Rating A → 0 incidentes en 6 meses.

### ¿Cómo mejorar?

1. **Priorizar por severidad**: Arregla bloqueantes/críticos primero
2. **Code review**: Revisar código antes de merge
3. **Testing**: Escribir tests que cubran casos edge
4. **Linting**: Usar herramientas como Pylint, ESLint para detectar bugs temprano
5. **Análisis estático**: Ejecutar SonarQube en CI/CD

**Meta recomendada**: Rating A o B antes de cada release.

---

## 🔒 Security Rating

### ¿Qué mide?

La **seguridad** del código, detectando vulnerabilidades que podrían ser explotadas por atacantes.

### Escala de Calificación

| Rating | Condición | Significado | Riesgo de Hackeo |
|--------|-----------|-------------|------------------|
| **A** | 0 vulnerabilidades | Muy seguro | 🟢 Muy bajo |
| **B** | Al menos 1 vulnerabilidad menor | Seguro | 🟢 Bajo |
| **C** | Al menos 1 vulnerabilidad mayor | Vulnerable | 🟡 Medio - Requiere acción |
| **D** | Al menos 1 vulnerabilidad crítica | Muy vulnerable | 🟠 Alto - **Urgente** |
| **E** | Al menos 1 vulnerabilidad bloqueante | Extremadamente vulnerable | 🔴 **Crítico** - No desplegar |

### Tipos de Vulnerabilidades

#### 1. SQL Injection
**Severidad**: Crítica

**Qué es**: Atacante puede ejecutar comandos SQL arbitrarios.

**Ejemplo vulnerable**:
```python
# ❌ VULNERABLE
query = f"SELECT * FROM users WHERE username = '{username}'"
db.execute(query)
# Si username = "admin' OR '1'='1", retorna todos los usuarios
```

**Código seguro**:
```python
# ✅ SEGURO - Prepared statement
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (username,))
```

**Impacto**: Robo de datos, modificación/eliminación de base de datos.

---

#### 2. Cross-Site Scripting (XSS)
**Severidad**: Mayor/Crítica

**Qué es**: Atacante inyecta JavaScript malicioso en la página.

**Ejemplo vulnerable**:
```javascript
// ❌ VULNERABLE
document.getElementById('output').innerHTML = userInput;
// Si userInput = "<script>alert('hacked')</script>", ejecuta código
```

**Código seguro**:
```javascript
// ✅ SEGURO - Escape HTML
document.getElementById('output').textContent = userInput;
```

**Impacto**: Robo de cookies/sesiones, redirección a sitios maliciosos.

---

#### 3. Hardcoded Credentials
**Severidad**: Crítica

**Qué es**: Contraseñas/API keys en el código fuente.

**Ejemplo vulnerable**:
```python
# ❌ VULNERABLE
DB_PASSWORD = "admin123"
API_KEY = "sk_live_abc123xyz"
```

**Código seguro**:
```python
# ✅ SEGURO - Variables de entorno
import os
DB_PASSWORD = os.getenv("DB_PASSWORD")
API_KEY = os.getenv("API_KEY")
```

**Impacto**: Si el código es público (GitHub), credenciales expuestas.

---

#### 4. Weak Cryptography
**Severidad**: Mayor

**Qué es**: Uso de algoritmos de encriptación débiles.

**Ejemplo vulnerable**:
```python
# ❌ VULNERABLE - MD5 es inseguro
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
```

**Código seguro**:
```python
# ✅ SEGURO - bcrypt con salt
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

**Impacto**: Contraseñas pueden ser crackeadas fácilmente.

---

### ¿Cómo se calcula?

SonarQube detecta vulnerabilidades mediante:
- **Análisis de patrones** de código inseguro (OWASP Top 10)
- **Reglas de seguridad** específicas por lenguaje
- **Dependency check** (librerías con vulnerabilidades conocidas)

Rating se asigna según vulnerabilidad de mayor severidad.

### ¿Por qué importa?

| Rating | Consecuencias Reales |
|--------|---------------------|
| **E** o **D** | 🔴 Hackeo probable, robo de datos, multas GDPR, reputación dañada |
| **C** | 🟡 Vulnerable a ataques dirigidos |
| **B** o **A** | 🟢 Conforme con estándares de seguridad (ISO 27001, SOC 2) |

**Caso real**: Una empresa con Rating E fue hackeada, perdió 10M de registros de usuarios. Multa GDPR: €20 millones. Costo de remediación: €50 millones.

### ¿Cómo mejorar?

1. **Auditoría de seguridad**: Revisar todas las vulnerabilidades detectadas
2. **Actualizar dependencias**: Usar versiones sin CVEs conocidos
3. **Usar secrets managers**: Vault, AWS Secrets Manager, no hardcodear
4. **Input validation**: Validar/escapar toda entrada de usuario
5. **Security training**: Capacitar equipo en OWASP Top 10
6. **Penetration testing**: Contratar ethical hackers para pruebas

**Meta recomendada**: Rating A (0 vulnerabilidades) antes de producción.

---

## 🔧 Maintainability Rating

### ¿Qué mide?

Qué tan **fácil es mantener y modificar** el código en el futuro.

Basado en el concepto de **Deuda Técnica** (SQALE - Software Quality Assessment based on Lifecycle Expectations).

### Escala de Calificación

| Rating | Deuda Técnica | Significado | Esfuerzo de Mantenimiento |
|--------|---------------|-------------|--------------------------|
| **A** | ≤ 5% | Excelente - Muy mantenible | 🟢 Bajo (1x tiempo normal) |
| **B** | 6-10% | Bueno - Mantenible | 🟢 Normal (1.2x) |
| **C** | 11-20% | Medio - Algo difícil | 🟡 Alto (1.5x) |
| **D** | 21-50% | Malo - Difícil de mantener | 🟠 Muy alto (2x) |
| **E** | > 50% | Muy malo - Código legacy | 🔴 Extremo (3x+ tiempo) |

### ¿Qué es Deuda Técnica?

**Analogía bancaria**: Si tomas un préstamo (escribes código rápido pero sucio), pagas "intereses" (tiempo extra en cada modificación futura).

**Ejemplo**:
- Código limpio (Rating A): Agregar feature toma **2 días**
- Código con deuda técnica (Rating D): La misma feature toma **4 días** (por entender/navegar código complejo)

### ¿Cómo se calcula?

**Fórmula**:
```
Deuda Técnica (%) = (Tiempo de remediar code smells / Tiempo de desarrollo) × 100
```

**Ejemplo**:
- Proyecto de 100 días de desarrollo
- Code smells tomarían 15 días arreglar
- Deuda Técnica = 15 / 100 = **15%** → Rating C

### Code Smells (Problemas de Mantenibilidad)

#### 1. Funciones Muy Largas
**Problema**: Difícil de entender y testear.

```python
# ❌ Code smell: Función de 200 líneas
def procesar_pedido(pedido):
    # Validación: 50 líneas
    # Cálculo de precio: 60 líneas
    # Actualización de inventario: 40 líneas
    # Envío de email: 30 líneas
    # Logging: 20 líneas
```

**Mejor**:
```python
# ✅ Dividir en funciones pequeñas
def procesar_pedido(pedido):
    validar_pedido(pedido)
    precio = calcular_precio(pedido)
    actualizar_inventario(pedido)
    enviar_confirmacion(pedido)
    log_pedido(pedido)
```

---

#### 2. Complejidad Excesiva
**Problema**: Demasiados if/else/loops anidados.

```python
# ❌ Complejidad ciclomática: 15 (muy alta)
def calcular_descuento(cliente, producto, cantidad):
    if cliente.es_premium:
        if producto.categoria == "electronica":
            if cantidad > 10:
                if cliente.antiguedad > 5:
                    # ...8 niveles más de if
```

**Mejor**:
```python
# ✅ Dividir lógica, usar early returns
def calcular_descuento(cliente, producto, cantidad):
    if not cliente.es_premium:
        return 0

    descuento_base = obtener_descuento_categoria(producto)
    descuento_volumen = obtener_descuento_volumen(cantidad)
    descuento_fidelidad = obtener_descuento_fidelidad(cliente)

    return max(descuento_base, descuento_volumen, descuento_fidelidad)
```

---

#### 3. Código Duplicado
**Problema**: Cambio en un lugar requiere cambios en N lugares.

```python
# ❌ Duplicación
def enviar_email_bienvenida(usuario):
    smtp = SMTP("smtp.gmail.com", 587)
    smtp.login("user", "pass")
    smtp.send(...)

def enviar_email_recuperacion(usuario):
    smtp = SMTP("smtp.gmail.com", 587)  # Duplicado
    smtp.login("user", "pass")          # Duplicado
    smtp.send(...)
```

**Mejor**:
```python
# ✅ Extraer lógica común
class EmailService:
    def __init__(self):
        self.smtp = SMTP("smtp.gmail.com", 587)
        self.smtp.login("user", "pass")

    def enviar(self, destinatario, asunto, cuerpo):
        self.smtp.send(...)

# Usar en ambos casos
email_service.enviar(usuario.email, "Bienvenida", mensaje)
```

---

#### 4. Comentarios Excesivos (Code Smell)
**Problema**: Código necesita comentarios para entenderse = código mal escrito.

```python
# ❌ Comentarios innecesarios
# Calcula el total del carrito sumando precio * cantidad de cada item
def calc(c):  # c es el carrito
    t = 0     # t es el total
    for i in c.items:  # i es cada item
        t += i.p * i.q  # p es precio, q es cantidad
    return t
```

**Mejor**:
```python
# ✅ Código auto-explicativo (no necesita comentarios)
def calcular_total_carrito(carrito):
    total = 0
    for item in carrito.items:
        total += item.precio * item.cantidad
    return total
```

---

### ¿Por qué importa?

| Rating | Impacto en Desarrollo |
|--------|----------------------|
| **E** o **D** | 🔴 Desarrollo lento, bugs frecuentes al modificar, rotación alta de devs (nadie quiere mantenerlo) |
| **C** | 🟡 Desarrollo más lento de lo esperado |
| **B** o **A** | 🟢 Desarrollo ágil, onboarding rápido, bajo costo de mantenimiento |

**Caso real**: Proyecto con Rating E → cada feature tomaba 3 semanas. Después de refactorización → Rating B → mismas features toman 1 semana.

### ¿Cómo mejorar?

1. **Refactorizar progresivamente**: No todo a la vez, cada sprint mejorar 5-10%
2. **Code reviews**: Rechazar PRs con code smells nuevos
3. **Límites estrictos**: Función máx 50 líneas, complejidad máx 10
4. **Principios SOLID**: Single Responsibility, Open/Closed, etc.
5. **DRY (Don't Repeat Yourself)**: Extraer código duplicado
6. **Testing**: Código testeable es código limpio

**Meta recomendada**: Rating A o B (<10% deuda técnica).

---

## 📊 Coverage (Cobertura de Tests)

### ¿Qué mide?

Porcentaje del código que está **cubierto por tests automáticos** (unit tests, integration tests).

### Cálculo

```
Coverage (%) = (Líneas ejecutadas por tests / Total líneas de código) × 100
```

**Ejemplo**:
- Total de líneas: 1,000
- Líneas ejecutadas durante tests: 800
- **Coverage = 80%**

### Escala de Interpretación

| Coverage | Calificación | Significado | Riesgo |
|----------|--------------|-------------|--------|
| **> 80%** | 🟢 Excelente | Muy bien testeado | Muy bajo |
| **60-80%** | 🟢 Bueno | Bien testeado | Bajo |
| **40-60%** | 🟡 Medio | Parcialmente testeado | Medio |
| **20-40%** | 🟠 Bajo | Mal testeado | Alto |
| **< 20%** | 🔴 Muy bajo | Casi sin tests | **Crítico** |

### ¿Por qué importa?

**Con alto coverage (>80%)**:
- ✅ Tests detectan **80% de los bugs** antes de producción
- ✅ Refactorización segura (tests fallan si rompes algo)
- ✅ Documentación viva (tests muestran cómo usar el código)
- ✅ Confianza en cambios

**Con bajo coverage (<40%)**:
- ❌ **60-80% de bugs** pasan desapercibidos hasta producción
- ❌ Miedo a refactorizar (no sabes si rompiste algo)
- ❌ Regresiones frecuentes
- ❌ Debugging largo (sin tests que aíslen el problema)

**Caso real**: Proyecto con 95% coverage → 0.5 bugs por release. Proyecto con 20% coverage → 15 bugs por release.

### Tipos de Coverage

#### 1. Line Coverage
**Qué mide**: % de líneas ejecutadas.

**Ejemplo**:
```python
def dividir(a, b):
    if b == 0:           # Línea 1
        return None      # Línea 2
    return a / b         # Línea 3

# Test
def test_dividir():
    assert dividir(10, 2) == 5  # Ejecuta líneas 1 y 3

# Line coverage: 66% (2/3 líneas)
# Línea 2 nunca se ejecutó
```

---

#### 2. Branch Coverage
**Qué mide**: % de ramas (if/else) ejecutadas.

**Ejemplo**:
```python
def calcular_descuento(precio, es_vip):
    if es_vip:         # Rama 1: True
        return precio * 0.8
    else:              # Rama 2: False
        return precio

# Test
def test_vip():
    assert calcular_descuento(100, True) == 80

# Branch coverage: 50% (solo rama True testeada)
```

**Test completo**:
```python
def test_vip():
    assert calcular_descuento(100, True) == 80

def test_no_vip():
    assert calcular_descuento(100, False) == 100

# Branch coverage: 100%
```

---

### ¿Cómo mejorar?

1. **Identificar gaps**: Ver qué módulos tienen <80% coverage
2. **Escribir tests para código nuevo**: 100% coverage en PRs
3. **Aumentar progresivamente**: +5% cada sprint
4. **TDD (Test-Driven Development)**: Escribir test antes del código
5. **Herramientas**: pytest-cov, coverage.py, Istanbul (JS)

**Meta recomendada**:
- **Código nuevo**: 100% coverage
- **Código legacy**: Mínimo 60%, objetivo 80%

---

## 📋 Duplicación de Código

### ¿Qué mide?

Porcentaje de líneas de código **duplicadas** (copiadas/pegadas en múltiples lugares).

### Cálculo

```
Duplicación (%) = (Líneas duplicadas / Total líneas) × 100
```

### Escala de Interpretación

| Duplicación | Calificación | Significado |
|-------------|--------------|-------------|
| **< 3%** | 🟢 Excelente | Muy poco duplicado |
| **3-5%** | 🟢 Aceptable | Ligeramente duplicado |
| **5-10%** | 🟡 Alto | Bastante duplicado |
| **10-20%** | 🟠 Muy alto | Muy duplicado |
| **> 20%** | 🔴 Crítico | Extremadamente duplicado |

### ¿Por qué es malo?

**Ejemplo de problema**:
```python
# Archivo A
def enviar_email_bienvenida(usuario):
    smtp = SMTP("smtp.gmail.com", 587)
    smtp.login("soporte@empresa.com", "password123")
    smtp.send(usuario.email, "Bienvenido", mensaje)

# Archivo B (código duplicado)
def enviar_email_recuperacion(usuario):
    smtp = SMTP("smtp.gmail.com", 587)           # ← Duplicado
    smtp.login("soporte@empresa.com", "password123")  # ← Duplicado
    smtp.send(usuario.email, "Recuperar password", mensaje)
```

**Problema**: Si cambia el password del email, hay que cambiarlo en **2 lugares**. Si hay 10 archivos con duplicación → **10 lugares**.

**Consecuencias**:
- ❌ Bugs por cambios inconsistentes
- ❌ Mantenimiento 3x más caro
- ❌ Refactorización difícil

### ¿Cómo mejorar?

**Solución: Extraer a función/clase común**
```python
# email_service.py
class EmailService:
    def __init__(self):
        self.smtp = SMTP("smtp.gmail.com", 587)
        self.smtp.login("soporte@empresa.com", "password123")

    def enviar(self, destinatario, asunto, mensaje):
        self.smtp.send(destinatario, asunto, mensaje)

# Archivo A
email_service.enviar(usuario.email, "Bienvenido", mensaje)

# Archivo B
email_service.enviar(usuario.email, "Recuperar password", mensaje)
```

**Resultado**: 1 solo lugar para cambiar configuración de email.

**Meta recomendada**: < 3% duplicación.

---

## 🔢 Complejidad Ciclomática

### ¿Qué mide?

Número de **caminos independientes** a través del código (if, loops, switch).

### Cálculo

Cuenta los puntos de decisión:
```
Complejidad = 1 + (cantidad de if + for + while + case + ||  + &&)
```

**Ejemplo**:
```python
def calcular_precio(producto, cantidad, es_vip):  # +1 (inicio)
    precio = producto.precio * cantidad

    if es_vip:                                     # +1 (if)
        precio *= 0.9

    if cantidad > 10:                              # +1 (if)
        precio *= 0.95

    return precio

# Complejidad = 1 + 2 = 3 (baja, fácil de testear)
```

### Escala de Interpretación

| Complejidad | Calificación | Significado | Testabilidad |
|-------------|--------------|-------------|--------------|
| **1-10** | 🟢 Baja | Simple y claro | Fácil (2-5 tests) |
| **11-20** | 🟡 Media | Moderadamente complejo | Media (10-15 tests) |
| **21-50** | 🟠 Alta | Complejo | Difícil (50+ tests) |
| **> 50** | 🔴 Muy alta | Extremadamente complejo | Casi imposible |

### ¿Por qué importa?

**Función con complejidad 3**: 2^3 = 8 tests para cubrir todos los caminos.

**Función con complejidad 15**: 2^15 = **32,768 tests** para cobertura completa → **imposible**.

**Consecuencias de alta complejidad**:
- ❌ Imposible de testear completamente
- ❌ Difícil de entender
- ❌ Alto riesgo de bugs
- ❌ Modificaciones son arriesgadas

### ¿Cómo mejorar?

**Refactorizar dividiendo en funciones más pequeñas**:

```python
# ❌ Complejidad: 15 (muy alta)
def procesar_pedido(pedido):
    if pedido.es_valido:
        if pedido.cliente.es_vip:
            if pedido.total > 1000:
                if pedido.pais == "ES":
                    # ... 10 niveles más de if
```

**✅ Dividir en funciones pequeñas**:
```python
def procesar_pedido(pedido):
    if not es_pedido_valido(pedido):
        return False

    descuento = calcular_descuento(pedido)
    impuestos = calcular_impuestos(pedido)
    total = calcular_total(pedido, descuento, impuestos)

    return finalizar_pedido(pedido, total)

# Cada función tiene complejidad < 5
```

**Meta recomendada**: Complejidad < 10 por función.

---

## 💳 Deuda Técnica

### ¿Qué es?

Estimación del **tiempo necesario** para arreglar todos los code smells.

### Cálculo

SonarQube estima cuánto tiempo tomaría cada code smell:
- Función muy larga: 20 minutos
- Variable mal nombrada: 2 minutos
- Código duplicado: 30 minutos

**Ejemplo**:
- 50 code smells que tomarían **15 días** arreglar
- **Deuda Técnica = 15 días**

Si el proyecto tardó 100 días en desarrollarse:
- **Ratio de Deuda = 15 / 100 = 15%** → Rating C

### Interpretación

| Deuda Técnica | Significado |
|---------------|-------------|
| **3 días** | Bajo - Se puede refactorizar en 1 sprint |
| **20 días** | Medio - Requiere 1-2 meses de refactor |
| **100 días** | Alto - Proyecto legacy, considerar reescritura |
| **> 200 días** | Crítico - Código prácticamente inmante.md) para entender qué es el dashboard
2. Revisa cada métrica en tu proyecto y compara con umbrales
3. Prioriza mejoras usando la tabla de prioridades
4. Lee [USER_GUIDE.md](USER_GUIDE.md) para aprender a navegar el dashboard

---

**Última actualización**: Diciembre 2025
**Versión del documento**: 1.0.0
**Próxima revisión**: Marzo 2026
