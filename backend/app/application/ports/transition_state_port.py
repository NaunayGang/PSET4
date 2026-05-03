from abc import ABC, abstractmethod

from backend.app.domain.entities import Incident


class TransitionStatePort(ABC):
    @abstractmethod
    def present_incident(self, incident: Incident) -> None:
        pass

    @abstractmethod
    def present_failure(self, error_message: str) -> None:
        pass

    @abstractmethod
    def present_not_found(self, incident_id: int) -> None:
        pass
