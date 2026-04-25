from dataclasses import dataclass
from datetime import datetime
from enums import LogLevel

@dataclass
class Log:
    id: int
    timestamp: datetime
    log_level: LogLevel
    message: str


