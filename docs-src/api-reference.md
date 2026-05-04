---
title: API Reference - IncidentFlow
---

## Introduction

IncidentFlow exposes a REST API built with FastAPI for all operations. This document provides complete reference for all endpoints, including request/response examples, authentication, and authorization rules.

**Base URL**: `http://localhost:8000` (development)

**Authentication**: Bearer token in `Authorization` header

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/incidents
```

---

## Authentication & Authorization

### Login

**POST** `/api/auth/login`

Authenticate user and get session token.

**Request:**
```json
{
  "email": "operator@company.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "OPERATOR",
  "email": "operator@company.com"
}
```

**Error Response:** `401 Unauthorized`
```json
{
  "detail": "Invalid credentials"
}
```

---

### Logout

**POST** `/api/auth/logout`

End current session.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

---

## Incidents

### Create Incident

**POST** `/api/incidents`

Create a new incident. Only Operator and Commander roles can create.

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
  "severity": "CRITICAL"
}
```

**Severity Options:**
- `LOW` - Minor issues, can wait
- `MEDIUM` - Affects some users, should be resolved today
- `HIGH` - Affects many users, needs immediate attention
- `CRITICAL` - Service down, requires Commander immediate attention

**Response:** `201 Created`
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "title": "Payment service down",
  "description": "Customers cannot complete transactions...",
  "severity": "CRITICAL",
  "state": "OPEN",
  "creator_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-05-03T10:30:00Z",
  "updated_at": "2026-05-03T10:30:00Z",
  "assignee_id": null,
  "resolved_at": null,
  "closed_at": null,
  "resolution_summary": null
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "Title is required and must be between 5 and 200 characters"
}
```

**Error Response:** `403 Forbidden`
```json
{
  "detail": "You don't have permission to create incidents"
}
```

---

### List Incidents

**GET** `/api/incidents`

Get paginated list of incidents with optional filters.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
```
?page=1
&limit=20
&state=IN_PROGRESS
&severity=CRITICAL
&assignee_id=550e8400-e29b-41d4-a716-446655440000
&search=payment
&sort_by=created_at
&sort_order=desc
```

**Parameters:**
- `page` (int, default: 1) - Page number for pagination
- `limit` (int, default: 20, max: 100) - Results per page
- `state` (string) - Filter by state: OPEN, TRIAGED, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED, ESCALATED, CANCELLED
- `severity` (string) - Filter by severity: LOW, MEDIUM, HIGH, CRITICAL
- `assignee_id` (UUID) - Filter by assigned user
- `search` (string) - Search in title and description
- `sort_by` (string) - Sort field: created_at, updated_at, severity
- `sort_order` (string) - Sort order: asc, desc

**Response:** `200 OK`
```json
{
  "total": 15,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "title": "Payment service down",
      "severity": "CRITICAL",
      "state": "IN_PROGRESS",
      "creator_id": "550e8400-e29b-41d4-a716-446655440000",
      "assignee_id": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2026-05-03T10:30:00Z",
      "updated_at": "2026-05-03T10:45:00Z"
    }
  ]
}
```

---

### Get Incident by ID

**GET** `/api/incidents/{incident_id}`

Get full details of a specific incident including timeline.

**Path Parameters:**
- `incident_id` (UUID) - The incident ID

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "title": "Payment service down",
  "description": "Customers cannot complete transactions...",
  "severity": "CRITICAL",
  "state": "IN_PROGRESS",
  "creator_id": "550e8400-e29b-41d4-a716-446655440000",
  "assignee_id": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2026-05-03T10:30:00Z",
  "updated_at": "2026-05-03T10:45:00Z",
  "resolved_at": null,
  "closed_at": null,
  "resolution_summary": null,
  "comments": [
    {
      "id": "comment-id-1",
      "author_id": "550e8400-e29b-41d4-a716-446655440001",
      "text": "Started investigating payment service logs",
      "created_at": "2026-05-03T10:35:00Z"
    }
  ],
  "audit_log": [
    {
      "id": "audit-1",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "action": "INCIDENT_CREATED",
      "old_value": null,
      "new_value": "OPEN",
      "timestamp": "2026-05-03T10:30:00Z"
    },
    {
      "id": "audit-2",
      "user_id": "550e8400-e29b-41d4-a716-446655440002",
      "action": "INCIDENT_ASSIGNED",
      "old_value": null,
      "new_value": "550e8400-e29b-41d4-a716-446655440001",
      "timestamp": "2026-05-03T10:32:00Z"
    }
  ]
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Incident not found"
}
```

---

### Update Incident State

**PATCH** `/api/incidents/{incident_id}/state`

Change incident state. Only Incident Commander and Admin can do this.

**Path Parameters:**
- `incident_id` (UUID)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "state": "IN_PROGRESS"
}
```

**Valid State Transitions:**
```
OPEN → TRIAGED
TRIAGED → ASSIGNED
ASSIGNED → IN_PROGRESS
IN_PROGRESS → RESOLVED
RESOLVED → CLOSED
Any → ESCALATED
Any → CANCELLED
```

**Response:** `200 OK`
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "state": "IN_PROGRESS",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

**Error Response:** `400 Bad Request` (Invalid transition)
```json
{
  "detail": "Cannot transition from IN_PROGRESS to TRIAGED"
}
```

**Error Response:** `400 Bad Request` (Missing assignee for IN_PROGRESS)
```json
{
  "detail": "Cannot move to IN_PROGRESS without an assignee"
}
```

**Error Response:** `403 Forbidden`
```json
{
  "detail": "Only Incident Commander can change state"
}
```

---

### Assign Incident

**PATCH** `/api/incidents/{incident_id}/assignee`

Assign incident to a technical responder. Only Incident Commander and Admin.

**Path Parameters:**
- `incident_id` (UUID)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "assignee_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Response:** `200 OK`
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "assignee_id": "550e8400-e29b-41d4-a716-446655440001",
  "state": "ASSIGNED",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "User not found or not active"
}
```

---

### Change Severity

**PATCH** `/api/incidents/{incident_id}/severity`

Change incident severity. Only Incident Commander and Admin. If CRITICAL, notifies Commander and Manager.

**Path Parameters:**
- `incident_id` (UUID)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "severity": "CRITICAL"
}
```

**Response:** `200 OK`
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "severity": "CRITICAL",
  "updated_at": "2026-05-03T10:40:00Z"
}
```

---

## Comments

### Add Comment

**POST** `/api/incidents/{incident_id}/comments`

Add a comment to incident timeline. All authenticated users can comment.

**Path Parameters:**
- `incident_id` (UUID)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Investigation underway. Found issue in payment-gateway service logs."
}
```

**Response:** `201 Created`
```json
{
  "id": "comment-id-1",
  "incident_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "author_id": "550e8400-e29b-41d4-a716-446655440001",
  "text": "Investigation underway. Found issue in payment-gateway service logs.",
  "created_at": "2026-05-03T10:40:00Z"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "Comment text cannot be empty"
}
```

---

### List Comments

**GET** `/api/incidents/{incident_id}/comments`

Get all comments for an incident.

**Path Parameters:**
- `incident_id` (UUID)

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
```
?page=1
&limit=50
```

**Response:** `200 OK`
```json
{
  "total": 5,
  "page": 1,
  "results": [
    {
      "id": "comment-id-1",
      "author_id": "550e8400-e29b-41d4-a716-446655440001",
      "text": "Investigation underway...",
      "created_at": "2026-05-03T10:40:00Z"
    }
  ]
}
```

---

## Audit Log

### Get Audit Log

**GET** `/api/incidents/{incident_id}/audit`

Get audit log for an incident. Only Manager and Admin can view.

**Path Parameters:**
- `incident_id` (UUID)

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
```
?page=1
&limit=50
&action=SEVERITY_CHANGED
&user_id=550e8400-e29b-41d4-a716-446655440000
```

**Response:** `200 OK`
```json
{
  "total": 8,
  "page": 1,
  "results": [
    {
      "id": "audit-1",
      "incident_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "action": "INCIDENT_CREATED",
      "old_value": null,
      "new_value": "OPEN",
      "timestamp": "2026-05-03T10:30:00Z",
      "details": {
        "severity": "CRITICAL",
        "creator": "operator@company.com"
      }
    },
    {
      "id": "audit-2",
      "incident_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "user_id": "550e8400-e29b-41d4-a716-446655440002",
      "action": "SEVERITY_CHANGED",
      "old_value": "HIGH",
      "new_value": "CRITICAL",
      "timestamp": "2026-05-03T10:35:00Z",
      "details": {
        "reason": "More users affected than initially thought"
      }
    }
  ]
}
```

**Error Response:** `403 Forbidden`
```json
{
  "detail": "Only Manager and Admin can view audit logs"
}
```

---

## Notifications

### Get Notifications

**GET** `/api/notifications`

Get user's notifications.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
```
?page=1
&limit=20
&read=false
```

**Response:** `200 OK`
```json
{
  "total": 3,
  "unread": 2,
  "results": [
    {
      "id": "notif-1",
      "incident_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "event_type": "INCIDENT_ASSIGNED",
      "message": "You have been assigned to incident: Payment service down",
      "read": false,
      "created_at": "2026-05-03T10:32:00Z"
    }
  ]
}
```

---

### Mark Notification as Read

**PATCH** `/api/notifications/{notification_id}/read`

Mark a notification as read.

**Path Parameters:**
- `notification_id` (UUID)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "notif-1",
  "read": true
}
```

---

## Users & Roles

### Get Current User

**GET** `/api/users/me`

Get current authenticated user info.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "email": "commander@company.com",
  "name": "Sarah Johnson",
  "role": "COMMANDER",
  "active": true,
  "created_at": "2026-04-15T08:00:00Z"
}
```

---

### List Users (Admin Only)

**GET** `/api/users`

Get all users. Admin only.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "total": 12,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "email": "commander@company.com",
      "name": "Sarah Johnson",
      "role": "COMMANDER",
      "active": true
    }
  ]
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Don't have permission |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Invalid state transition |
| 500 | Internal Server Error |

---

## Error Format

All errors follow this format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-05-03T10:40:00Z"
}
```

---

## Rate Limiting

API has rate limiting:
- 100 requests per minute per user
- Returns `429 Too Many Requests` when exceeded

---

## Pagination

List endpoints return paginated results:

```json
{
  "total": 100,
  "page": 1,
  "limit": 20,
  "results": [...]
}
```

Navigate pages with `page` and `limit` query parameters.

---

## Postman Collection

A Postman collection with all endpoints is available at: `/docs/postman-collection.json`

Import it into Postman to test all endpoints with example requests.

---

## Examples

### Example 1: Create and Resolve a CRITICAL Incident

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"operator@company.com","password":"pass123"}'

# Response: {"token": "eyJ..."}

# 2. Create CRITICAL incident
TOKEN="eyJ..."
curl -X POST http://localhost:8000/api/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database connection pool exhausted",
    "description": "All database connections are in use, queries failing",
    "severity": "CRITICAL"
  }'

# Response: {"id": "incident-uuid", "state": "OPEN", ...}

# 3. View incident (notifications should be sent to Commander/Manager)
INCIDENT_ID="incident-uuid"
curl http://localhost:8000/api/incidents/$INCIDENT_ID \
  -H "Authorization: Bearer $TOKEN"

# 4. Assign to technical responder (as Commander)
COMMANDER_TOKEN="eyJ..."
RESPONDER_ID="responder-uuid"
curl -X PATCH http://localhost:8000/api/incidents/$INCIDENT_ID/assignee \
  -H "Authorization: Bearer $COMMANDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"assignee_id\": \"$RESPONDER_ID\"}"

# 5. Add comment
curl -X POST http://localhost:8000/api/incidents/$INCIDENT_ID/comments \
  -H "Authorization: Bearer $COMMANDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Added more database servers to connection pool"}'

# 6. Resolve
curl -X PATCH http://localhost:8000/api/incidents/$INCIDENT_ID/state \
  -H "Authorization: Bearer $COMMANDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state": "RESOLVED"}'

# 7. Close with summary
curl -X PATCH http://localhost:8000/api/incidents/$INCIDENT_ID/state \
  -H "Authorization: Bearer $COMMANDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "CLOSED",
    "resolution_summary": "Added 10 more database servers. Connections now handling peak load."
  }'
```

---

## Development Notes

- All timestamps are in UTC (ISO 8601 format)
- All IDs are UUIDs (v4)
- Severity is case-sensitive: use CRITICAL not Critical
- States are case-sensitive: use IN_PROGRESS not In_Progress
- Empty string for search means no filtering
