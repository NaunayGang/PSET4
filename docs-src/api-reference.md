---
title: Referencia de API - IncidentFlow
---

## Introducción

IncidentFlow expone una API REST construida con FastAPI para todas las operaciones. Este documento proporciona la referencia completa para todos los endpoints, incluyendo ejemplos de solicitud/respuesta, autenticación y reglas de autorización.

**URL Base**: `http://localhost:8000` (desarrollo)

**Autenticación**: Token Bearer en el encabezado `Authorization`

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/incidents
```

## Niveles de Severidad

Valores válidos de severidad (sensible a mayúsculas, tipo título):

-   `Low` - Problemas menores, puede esperar
-   `Medium` - Afecta a algunos usuarios, debe resolverse hoy
-   `High` - Afecta a muchos usuarios, requiere atención inmediata
-   `Critical` - Servicio caído, requiere atención inmediata del Commander

## Estados de Incidente

Estados válidos para transición (sensible a mayúsculas, MAYÚSCULAS):

-   `OPEN` - Estado inicial al crear
-   `TRIAGED` - Evaluado y con severidad asignada
-   `ASSIGNED` - Asignado a un respondedor
-   `IN_PROGRESS` - Trabajo en progreso
-   `RESOLVED` - Solución implementada
-   `CLOSED` - Cerrado formalmente
-   `CANCELLED` - Cancelado/falsa alarma
-   `ESCALATED` - Escalado a un nivel superior

## Roles

Nombres de roles válidos en el sistema (sensibles a mayúsculas):

-   `Admin` - Acceso completo
-   `Operator` - Crear incidentes, agregar comentarios
-   `Incident_commander` - Coordinar incidentes, asignar, cambiar estados
-   `Technical_responder` - Agregar comentarios, hacer trabajo técnico
-   `Incident_manager` - Ver y cambiar severidad

## Incidentes

### Crear Incidente

**POST** `/incidents`

Crear un nuevo incidente. Requiere rol `Admin` u `Operator`.

**Encabezados:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Cuerpo de la Solicitud:**

```json
{
  "title": "Servicio de pagos caído",
  "description": "Los clientes no pueden completar transacciones. Error 500 en la API de pagos.",
  "severity": "Critical"
}
```

**Respuesta:** `200 OK`

```json
{
  "id": 1,
  "title": "Servicio de pagos caído",
  "description": "Los clientes no pueden completar transacciones...",
  "severity": "Critical",
  "state": "OPEN",
  "creator_id": 1,
  "assigned_user_id": null,
  "created_at": "2026-05-03T10:30:00Z",
  "updated_at": "2026-05-03T10:30:00Z"
}
```

**Respuesta de Error:** `400 Bad Request`

```json
{
  "detail": "Nivel de severidad inválido: CRITICAL"
}
```

**Respuesta de Error:** `403 Forbidden`

```json
{
  "detail": "Permisos insuficientes"
}
```

### Triaje de Incidente

**POST** `/incidents/{incident_id}/triage`

Evaluar y triar un incidente (cambiar su severidad). Requiere rol `Admin` o `Incident_commander`.

**Parámetros de Ruta:**

-   `incident_id` (int) - El ID del incidente

**Encabezados:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Cuerpo de la Solicitud:**

```json
{
  "new_severity": "Critical"
}
```

**Respuesta:** `200 OK`

```json
{
  "id": 1,
  "severity": "Critical",
  "state": "OPEN",
  "updated_at": "2026-05-03T10:35:00Z"
}
```

**Respuesta de Error:** `404 Not Found`

```json
{
  "detail": "Incidente con ID 999 no encontrado."
}
```

### Cambiar Estado

**POST** `/incidents/{incident_id}/transition-state`

Cambiar el estado del incidente. Requiere rol `Admin` o `Incident_commander`.

**Parámetros de Ruta:**

-   `incident_id` (int)

**Encabezados:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Cuerpo de la Solicitud:**

```json
{
  "new_state": "IN_PROGRESS"
}
```

**Transiciones de Estado Válidas:**

```
OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
OPEN → CANCELLED
OPEN → ESCALATED
IN_PROGRESS → ESCALATED
RESOLVED → CLOSED
 Cualquier estado → CANCELLED
 Cualquier estado → ESCALATED
```

**Respuesta:** `200 OK`

```json
{
  "id": 1,
  "state": "IN_PROGRESS",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

**Respuesta de Error:** `400 Bad Request` (Transición inválida)

```json
{
  "detail": "Transición de estado inválida o estado del incidente inválido"
}
```

**Respuesta de Error:** `403 Forbidden`

```json
{
  "detail": "Permisos insuficientes"
}
```

### Asignar Incidente

**POST** `/incidents/{incident_id}/assign`

Asignar el incidente a un respondedor técnico. Requiere rol `Admin` o `Incident_commander`.

**Parámetros de Ruta:**

-   `incident_id` (int)

**Encabezados:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Cuerpo de la Solicitud:**

```json
{
  "assigned_user_id": 5
}
```

**Respuesta:** `200 OK`

```json
{
  "id": 1,
  "assigned_user_id": 5,
  "state": "ASSIGNED",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

**Respuesta de Error:** `400 Bad Request`

```json
{
  "detail": "Usuario no encontrado o asignación inválida"
}
```

### Cambiar Severidad

**POST** `/incidents/{incident_id}/change_severity`

Cambiar la severidad del incidente. Requiere rol `Admin` o `Incident_manager`.

**Parámetros de Ruta:**

-   `incident_id` (int)

**Encabezados:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Cuerpo de la Solicitud:**

```json
{
  "new_severity": "Critical"
}
```

**Respuesta:** `200 OK`

```json
{
  "id": 1,
  "severity": "Critical",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

## Comentarios

### Agregar Comentario

**POST** `/incidents/{incident_id}/comments`

Agregar un comentario a la línea de tiempo del incidente. Requiere rol `Admin`, `Operator`, o `Technical_responder`.

**Parámetros de Ruta:**

-   `incident_id` (int)

**Encabezados:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Cuerpo de la Solicitud:**

```json
{
  "content": "Investigación en curso. Se encontró el problema en los logs del servicio payment-gateway."
}
```

**Respuesta:** `200 OK`

```json
{
  "comment_id": 42
}
```

**Respuesta de Error:** `400 Bad Request`

```json
{
  "detail": "El contenido del comentario es requerido"
}
```

**Respuesta de Error:** `404 Not Found`

```json
{
  "detail": "Incidente con ID 999 no encontrado."
}
```

## Códigos de Estado

| Código | Significado |
|--------|------------|
| 200 | OK - Solicitud exitosa |
| 400 | Bad Request - Entrada inválida o transición de estado inválida |
| 403 | Forbidden - Permisos insuficientes |
| 404 | Not Found - El recurso no existe |
| 500 | Internal Server Error |

## Formato de Errores

Los errores siguen este formato:

```json
{
  "detail": "Mensaje de error legible por humanos"
}
```

## Matriz de Permisos por Rol

| Acción | Admin | Operator | Incident_commander | Technical_responder | Incident_manager |
|--------|-------|----------|-------------------|-------------------|------------------|
| Crear Incidente | ✓ | ✓ | ✗ | ✗ | ✗ |
| Triar | ✓ | ✗ | ✓ | ✗ | ✗ |
| Cambiar Estado | ✓ | ✗ | ✓ | ✗ | ✗ |
| Asignar | ✓ | ✗ | ✓ | ✗ | ✗ |
| Cambiar Severidad | ✓ | ✗ | ✗ | ✗ | ✓ |
| Agregar Comentario | ✓ | ✓ | ✓ | ✓ | ✗ |

## Ejemplos

### Ejemplo 1: Crear y Procesar un Incidente

```bash
# 1. Crear incidente Crítico
TOKEN="eyJ..."
curl -X POST http://localhost:8000/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pool de conexiones de base de datos agotado",
    "description": "Todas las conexiones de base de datos están en uso, consultas fallando",
    "severity": "Critical"
  }'

# Respuesta: {"id": 1, "state": "OPEN", ...}

# 2. Triar el incidente
INCIDENT_ID=1
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/triage \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_severity": "Critical"}'

# 3. Asignar al respondedor (user_id = 5)
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/assign \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assigned_user_id": 5}'

# 4. Agregar comentario
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Se agregaron 10 servidores más de base de datos"}'

# 5. Transicionar a IN_PROGRESS
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/transition-state \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_state": "IN_PROGRESS"}'

# 6. Transicionar a RESOLVED
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/transition-state \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_state": "RESOLVED"}'

# 7. Cerrar el incidente
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/transition-state \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_state": "CLOSED"}'
```

## Notas de Desarrollo

-   Todos los IDs de incidentes son enteros (no UUIDs)
-   Todos los timestamps están en UTC (formato ISO 8601)
-   Los valores de severidad son tipo título: `Low`, `Medium`, `High`, `Critical`
-   Los valores de estado son MAYÚSCULAS: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`, `CANCELLED`, `ESCALATED`
-   Los nombres de roles usan guiones bajos: `Incident_commander`, `Technical_responder`, `Incident_manager`
-   Los IDs de usuario son enteros
-   Todos los endpoints POST que modifican retornan el incidente u objeto actualizado
