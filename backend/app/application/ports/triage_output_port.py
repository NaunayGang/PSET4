from abc import ABC, abstractmethod

from backend.app.domain.entities.incident import Incident


class TriageOutputPort(ABC):
    @abstractmethod
    def present_success(self, incident: Incident) -> None:
        pass

    @abstractmethod
    def present_not_found(self, incident_id: int) -> None:
        pass

    @abstractmethod
    def present_failure(self, error_message: str) -> None:
        pass

