from enum import Enum

class State(str, Enum):
    OPEN = "open"
    TRIAGED = "triaged"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

    def __str__(self) -> str:
        return self.value