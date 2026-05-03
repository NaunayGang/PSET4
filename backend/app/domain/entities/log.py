from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from backend.app.domain.enums.log_level import LogLevel


@dataclass
class Log:
    timestamp: datetime | None
    log_level: LogLevel
    message: str
    id: Optional[int] = None



