from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    user_id: int
    incident_id: int
    event_type: str
    message: str
    created_at: datetime
    id: int | None = None
    read_at: datetime | None = None
