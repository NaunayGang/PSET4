from dataclasses import dataclass
from datetime import datetime

@dataclass
class Comment:
    id: int
    incident_id: int
    author_id: int
    timestamp: datetime
    content: str