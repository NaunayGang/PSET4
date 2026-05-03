from dataclasses import dataclass
from datetime import datetime

from backend.app.domain.enums.role import Role


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: Role
    created_at: datetime
    last_login: datetime | None

