---
title: UML Diagrams - IncidentFlow System Design
---

## Overview

This document contains the PlantUML diagrams that visualize the IncidentFlow system architecture, domain model, workflows, and use cases. These diagrams are essential for understanding the system design and serve as a reference for implementation.

## State Machine Diagram

The state machine diagram shows the lifecycle of an incident and all valid transitions between states.

![State Machine Diagram](../resources/images/IncidentFlowStateMachine.svg)

### State Descriptions

- **OPEN**: Initial state when an incident is reported
- **TRIAGED**: Incident has been evaluated for severity and impact
- **ASSIGNED**: Incident has been assigned to a technical responder
- **IN_PROGRESS**: The assigned responder is actively working on the solution
- **RESOLVED**: The solution has been implemented but not yet formally closed
- **CLOSED**: Incident is formally closed with summary and audit trail complete
- **ESCALATED**: Can be triggered from any state; incident escalated to higher level
- **CANCELLED**: Incident was a false alarm or no longer relevant

### Valid Transitions

From **OPEN**:
- → TRIAGED (after evaluation)
- → CANCELLED (if false alarm)
- → ESCALATED (if needs immediate escalation)

From **TRIAGED**:
- → ASSIGNED (when responder assigned)
- → CANCELLED (if determined not urgent)
- → ESCALATED (if escalation needed)

From **ASSIGNED**:
- → IN_PROGRESS (when work starts)
- → CANCELLED (if not needed)
- → ESCALATED (for escalation)

From **IN_PROGRESS**:
- → RESOLVED (when solution implemented)
- → ESCALATED (for escalation)

From **RESOLVED**:
- → CLOSED (only Commander/Admin can close; CRITICAL requires summary)
- → IN_PROGRESS (if issue resurfaces)

From **ESCALATED**:
- → ASSIGNED (reassign and continue)
- → IN_PROGRESS (continue from escalation)

From **CANCELLED** or **CLOSED**:
- → [End] (Terminal states)

## Class Diagram

The class diagram shows the domain entities, their attributes, relationships, and key interfaces for the repository pattern.

![Class Diagram](../resources/images/IncidentFlowClassDiagram.svg)

### Core Entities

**User**
- id: UUID
- email: str
- name: str
- role: Role (Operator, Commander, Responder, Manager, Admin)
- active: bool
- created_at: DateTime

**Incident** (Aggregate Root)
- id: UUID
- title: str
- description: str
- severity: Severity (LOW, MEDIUM, HIGH, CRITICAL)
- state: IncidentState
- creator_id: UUID (references User)
- assignee_id: UUID (references User, nullable)
- created_at: DateTime
- updated_at: DateTime
- resolved_at: DateTime (nullable)
- closed_at: DateTime (nullable)
- resolution_summary: str (nullable)

Key methods:
- `transition_state(new_state, user)`: Changes incident state with validation
- `assign(user, commander)`: Assigns incident to a user
- `add_comment(text, user)`: Adds a comment to incident timeline
- `change_severity(new_severity, user)`: Changes severity with audit trail
- `can_close()`: Validates if incident can be closed (CRITICAL requires summary)
- `is_critical()`: Returns true if severity is CRITICAL

**Comment**
- id: UUID
- incident_id: UUID (references Incident)
- author_id: UUID (references User)
- text: str
- created_at: DateTime

**AuditLog** (for compliance and debugging)
- id: UUID
- incident_id: UUID (references Incident)
- user_id: UUID (references User)
- action: str (what changed: state, severity, assignment, etc)
- old_value: str (nullable)
- new_value: str (nullable)
- timestamp: DateTime
- details: JSON (additional context)

**Notification**
- id: UUID
- user_id: UUID (references User)
- incident_id: UUID (references Incident)
- event_type: str (INCIDENT_CREATED, SEVERITY_CHANGED, etc)
- message: str
- read: bool
- created_at: DateTime

### Enumerations

**Severity**
- LOW
- MEDIUM
- HIGH
- CRITICAL

**IncidentState**
- OPEN
- TRIAGED
- ASSIGNED
- IN_PROGRESS
- RESOLVED
- CLOSED
- ESCALATED
- CANCELLED

**Role**
- OPERATOR
- COMMANDER
- RESPONDER
- MANAGER
- ADMIN

### Repository Interfaces (Dependency Inversion)

All infrastructure layer implementations depend on these domain interfaces:

- **IIncidentRepository**: CRUD operations on incidents, filtering by state/severity/assignee
- **ICommentRepository**: Create and retrieve comments for incidents
- **IAuditLogRepository**: Create and retrieve audit logs
- **IUserRepository**: Retrieve user information by ID or email
- **IEventBus**: Publish events, subscribe to event handlers

## Sequence Diagram: CRITICAL Incident Flow

This sequence diagram illustrates the entire lifecycle of a CRITICAL severity incident from creation through resolution and closure.

![Sequence Diagram](../resources/images/IncidentFlowSequenceCritical.svg)

### Flow Steps

1. **Operator creates CRITICAL incident** via Streamlit UI
2. **Frontend sends POST /incidents** request to API
3. **API layer validates** and routes to Application layer
4. **Application layer:**
   - Validates incident data
   - Saves to database
   - Publishes INCIDENT_CREATED event
   - Because severity=CRITICAL, publishes notification events
5. **Event Bus notifies** Commander and Manager immediately (in-memory notifications)
6. **Commander receives notification** and views incident details
7. **Commander assigns** incident to a Technical Responder and changes state to ASSIGNED
8. **System audits** the assignment and publishes INCIDENT_ASSIGNED event
9. **Responder is notified** of assignment
10. **Responder starts work**, transitions to IN_PROGRESS
11. **Responder adds comment** with investigation details
12. **Responder resolves** the incident and transitions to RESOLVED
13. **System notifies** Manager of resolution
14. **Commander closes** the incident (only Commander/Admin can do this for CRITICAL)
15. **System validates** that CRITICAL incident has a summary before allowing closure
16. **System audits** the closure and publishes INCIDENT_CLOSED event
17. **Final state**: Incident is CLOSED with complete timeline and audit trail

## Use Case Diagram

The use case diagram shows what actions each role can perform in the IncidentFlow system.

![Use Case Diagram](../resources/images/IncidentFlowUseCaseDiagram.svg)

### Role Capabilities

**Operator**
- Create Incident
- Add Comment
- View Incident
- View Dashboard (basic list)

**Incident Commander** (Most Actions)
- Create Incident
- Triage Incident
- Assign Incident
- Add Comment
- Change State (with restrictions)
- Change Severity
- View Incident
- View Dashboard (with assignments and timeline focus)
- Escalate Incident
- Close Incident (restricted: CRITICAL needs summary)

**Technical Responder**
- Add Comment
- Change State (limited: can move to IN_PROGRESS, RESOLVED)
- View Incident
- View Dashboard (their assigned incidents)

**Manager** (Read-Only + Audit)
- View Incident (read-only)
- View Dashboard (metrics, incident distribution, unassigned count)
- View Audit Log (full visibility for compliance)

**Admin** (Full Access)
- All actions from all roles
- Create/Manage Users
- Reassign Incidents
- Full Audit Log Access

## Hexagonal Architecture Diagram

This diagram shows how the system is organized in a hexagonal (clean) architecture with clear separation of concerns.

![Hexagonal Architecture](../resources/images/IncidentFlowArchitecture.svg)

### Layers Explained

#### Frontend Layer
- **Streamlit UI**: Multi-page interface for different user roles
- Handles presentation logic and user interaction
- Calls Backend API endpoints

#### API Layer
- **FastAPI REST Endpoints**: All external communication
- Request validation and response serialization
- Permission decorators for authorization

#### Application Layer
- **Use Cases**: Business operations (CreateIncident, TriageIncident, etc)
- Orchestrates domain entities and infrastructure services
- No direct database calls; depends on repository interfaces
- DTOs validate input and shape output

#### Domain Layer (Core - No External Dependencies)
- **Entities**: Business objects with identity (Incident, User, Comment)
- **Value Objects**: Enumerations (Severity, IncidentState, Role)
- **Business Rules**: State machine, CRITICAL restrictions, permissions
- **Abstractions (Interfaces)**: IIncidentRepository, IEventBus, etc
- This layer is **testable in isolation** without mocks

#### Infrastructure Layer
- **Repositories**: Concrete implementations of domain interfaces
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Event Bus**: In-memory publish/subscribe for events and notifications
- Depends on domain abstractions (dependency inversion principle)

### Key Architectural Principles

1. **Dependency Inversion**: High-level modules don't depend on low-level modules; both depend on abstractions
2. **Single Responsibility**: Each layer has one reason to change
3. **Testability**: Domain layer is testable without test doubles
4. **Flexibility**: Easy to swap implementations (e.g., different database, event bus)

## Diagram Generation

All diagrams are generated from PlantUML source files (.puml) and compiled to PNG using:

```bash
nix shell nixpkgs#plantuml --command plantuml -o docs-src/resources/images docs-src/uml/*.puml
```

Or via the documented compilation method:

```bash
nix develop path:. --command tern-core
```

## Next Steps

These diagrams should guide:
- Backend implementation of the domain layer and repositories
- Frontend UI design and workflow implementation
- API endpoint design and validation
- Test case design and test fixtures
- Team discussions and code reviews
