from dataclasses import dataclass
from datetime import datetime

from ..enums.severity import Severity
from ..enums.state import State


@dataclass
class Incident:
    id: int
    title: str
    description: str | None
    severity: Severity
    state: State
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime | None
    summary_id: int | None
    created_by: int | None = None

    def cancel_incident(self) -> None:

        if self.state in [State.CLOSED, State.CANCELLED]:
            raise ValueError("Cannot cancel an incident that is already closed or cancelled.")

        self.state = State.CANCELLED
        self.updated_at = datetime.now()

    def escalate_incident(self) -> None:

        if self.state not in [State.OPEN, State.TRIAGED, State.ASSIGNED]:
            raise ValueError("Only incidents in OPEN, TRIAGED, or ASSIGNED state can be escalated.")

        self.state = State.ESCALATED
        self.updated_at = datetime.now()


    def triage_incident(self, priority: Severity) -> None:

        if self.state != State.OPEN:
            raise ValueError("Only incidents in OPEN state can be triaged.")

        self.severity = priority
        self.state = State.TRIAGED
        self.updated_at = datetime.now()

    def assign_incident(self, user_id: int) -> None:

        if self.state != State.TRIAGED:
            raise ValueError("Only incidents in TRIAGED state can be assigned.")

        self.assigned_to = user_id
        self.state = State.ASSIGNED
        self.updated_at = datetime.now()

    def inprogress_incident(self) -> None:

        if self.state != State.ASSIGNED:
            raise ValueError("Only incidents in ASSIGNED state can be marked as in progress.")
        self.state = State.IN_PROGRESS
        self.updated_at = datetime.now()

    def resolve_incident(self) -> None:

        if self.state != State.IN_PROGRESS:
            raise ValueError("Only incidents in IN_PROGRESS state can be resolved.")

        self.state = State.RESOLVED
        self.updated_at = datetime.now()

    def close_incident(self) -> None:

        if self.state != State.RESOLVED:
            raise ValueError("Only incidents in RESOLVED state can be closed.")

        if self.severity == Severity.CRITICAL and self.summary_id is None:
            raise ValueError("Critical incidents cannot be closed without further review.")

        self.state = State.CLOSED
        self.updated_at = datetime.now()

    def change_severity(self, new_severity: Severity) -> None:
        if self.state in [State.CLOSED, State.CANCELLED]:
            raise ValueError("Cannot change severity of an incident that is already closed or cancelled.")

        self.severity = new_severity
        self.updated_at = datetime.now()

