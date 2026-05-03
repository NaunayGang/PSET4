from dataclasses import dataclass
from enum import Enum
from typing import Any


class IncidentEventType(str, Enum):
    INCIDENT_CREATED = "INCIDENT_CREATED"
    INCIDENT_ASSIGNED = "INCIDENT_ASSIGNED"
    SEVERITY_CHANGED = "SEVERITY_CHANGED"
    INCIDENT_RESOLVED = "INCIDENT_RESOLVED"


@dataclass(frozen=True)
class IncidentEvent:
    event_type: IncidentEventType
    incident_id: int
    actor_user_id: int | None = None
    payload: dict[str, Any] | None = None
