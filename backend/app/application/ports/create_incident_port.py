from abc import ABC, abstractmethod

from app.domain.entities.incident import Incident


class CreateIncidentPort(ABC):
    @abstractmethod
    def present_incident(self, incident: Incident) -> None:
        pass

    @abstractmethod
    def present_failure(self, error_message: str) -> None:
        pass
