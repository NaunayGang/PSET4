from enum import Enum

class Role(str, Enum):
    OPERATOR = "operator"
    INCIDENT_COMMANDER = "incident_commander"
    TECHNICAL_RESPONDER = "technical_responder"
    MANAGER = "manager"
    ADMIN = "admin"

    def __str__(self) -> str:
        return self.value