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