---
title: API Reference - IncidentFlow
---

## Introduction

IncidentFlow exposes a REST API built with FastAPI for all operations. This document provides complete reference for all endpoints, including request/response examples, authentication, and authorization rules.

**Base URL**: `http://localhost:8000` (development)

**Authentication**: Bearer token in `Authorization` header (JWT)

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/incidents
```

---

## Severity Levels

Valid severity values (case-sensitive, title-case):
- `Low` - Minor issues, can wait
- `Medium` - Affects some users, should be resolved today
- `High` - Affects many users, needs immediate attention
- `Critical` - Service down, requires Commander immediate attention

---

## Incident States

Valid states for transition (case-sensitive, UPPERCASE):
- `OPEN` - Initial state when created
- `IN_PROGRESS` - Work in progress
- `RESOLVED` - Solution implemented
- `CLOSED` - Formally closed
- `CANCELLED` - Cancelled/false alarm
- `ESCALATED` - Escalated to higher level

---

## Roles

Valid role names in the system (case-sensitive):
- `Admin` - Full access
- `Operator` - Create incidents, add comments
- `Incident_commander` - Coordinate incidents, assign, change states
- `Technical_responder` - Add comments, do technical work
- `Incident_manager` - View and change severity

---

## Incidents

### Create Incident

**POST** `/incidents`

Create a new incident. Requires `Admin` or `Operator` role.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Payment service down",
  "description": "Customers cannot complete transactions. Error 500 in payment API.",
  "severity": "Critical"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Payment service down",
  "description": "Customers cannot complete transactions...",
  "severity": "Critical",
  "state": "OPEN",
  "creator_id": 1,
  "assigned_user_id": null,
  "created_at": "2026-05-03T10:30:00Z",
  "updated_at": "2026-05-03T10:30:00Z"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "Invalid severity level: CRITICAL"
}
```

**Error Response:** `403 Forbidden`
```json
{
  "detail": "Not enough permissions"
}
```

---

### Triage Incident

**POST** `/incidents/{incident_id}/triage`

Evaluate and triage an incident (change its severity). Requires `Admin` or `Incident_commander` role.

**Path Parameters:**
- `incident_id` (int) - The incident ID

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "new_severity": "Critical"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "severity": "Critical",
  "state": "OPEN",
  "updated_at": "2026-05-03T10:35:00Z"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Incident with ID 999 not found."
}
```

---

### Transition State

**POST** `/incidents/{incident_id}/transition-state`

Change incident state. Requires `Admin` or `Incident_commander` role.

**Path Parameters:**
- `incident_id` (int)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "new_state": "IN_PROGRESS"
}
```

**Valid State Transitions:**
```
OPEN → IN_PROGRESS
OPEN → CANCELLED
OPEN → ESCALATED
IN_PROGRESS → RESOLVED
IN_PROGRESS → ESCALATED
RESOLVED → CLOSED
Any state → CANCELLED
Any state → ESCALATED
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "state": "IN_PROGRESS",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

**Error Response:** `400 Bad Request` (Invalid transition)
```json
{
  "detail": "Invalid state transition or incident state"
}
```

**Error Response:** `403 Forbidden`
```json
{
  "detail": "Not enough permissions"
}
```

---

### Assign Incident

**POST** `/incidents/{incident_id}/assign`

Assign incident to a technical responder. Requires `Admin` or `Incident_commander` role.

**Path Parameters:**
- `incident_id` (int)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "assigned_user_id": 5
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "assigned_user_id": 5,
  "state": "IN_PROGRESS",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "User not found or invalid assignment"
}
```

---

### Change Severity

**POST** `/incidents/{incident_id}/change_severity`

Change incident severity. Requires `Admin` or `Incident_manager` role.

**Path Parameters:**
- `incident_id` (int)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "new_severity": "Critical"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "severity": "Critical",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

---

## Comments

### Add Comment

**POST** `/incidents/{incident_id}/comments`

Add a comment to incident timeline. Requires `Admin`, `Operator`, or `Technical_responder` role.

**Path Parameters:**
- `incident_id` (int)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "Investigation underway. Found issue in payment-gateway service logs."
}
```

**Response:** `200 OK`
```json
{
  "comment_id": 42
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "Comment content is required"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Incident with ID 999 not found."
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 400 | Bad Request - Invalid input or invalid state transition |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

---

## Error Format

Errors follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

---

## Role Permission Matrix

| Action | Admin | Operator | Incident_commander | Technical_responder | Incident_manager |
|--------|-------|----------|-------------------|-------------------|------------------|
| Create Incident | ✓ | ✓ | ✗ | ✗ | ✗ |
| Triage | ✓ | ✗ | ✓ | ✗ | ✗ |
| Transition State | ✓ | ✗ | ✓ | ✗ | ✗ |
| Assign | ✓ | ✗ | ✓ | ✗ | ✗ |
| Change Severity | ✓ | ✗ | ✗ | ✗ | ✓ |
| Add Comment | ✓ | ✓ | ✓ | ✓ | ✗ |

---

## Examples

### Example 1: Create and Process an Incident

```bash
# 1. Create Critical incident
TOKEN="eyJ..."
curl -X POST http://localhost:8000/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database connection pool exhausted",
    "description": "All database connections are in use, queries failing",
    "severity": "Critical"
  }'

# Response: {"id": 1, "state": "OPEN", ...}

# 2. Triage the incident
INCIDENT_ID=1
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/triage \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_severity": "Critical"}'

# 3. Assign to responder (user_id = 5)
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/assign \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assigned_user_id": 5}'

# 4. Add comment
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Added 10 more database servers"}'

# 5. Transition to IN_PROGRESS
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/transition-state \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_state": "IN_PROGRESS"}'

# 6. Transition to RESOLVED
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/transition-state \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_state": "RESOLVED"}'

# 7. Close the incident
curl -X POST http://localhost:8000/incidents/$INCIDENT_ID/transition-state \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_state": "CLOSED"}'
```

---

## Development Notes

- All incident IDs are integers (not UUIDs)
- All timestamps are in UTC (ISO 8601 format)
- Severity values are title-case: `Low`, `Medium`, `High`, `Critical`
- State values are UPPERCASE: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`, `CANCELLED`, `ESCALATED`
- Role names use underscores: `Incident_commander`, `Technical_responder`, `Incident_manager`
- User IDs are integers
- All POST endpoints that modify return the updated incident or object
