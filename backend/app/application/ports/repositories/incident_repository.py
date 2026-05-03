from abc import ABC, abstractmethod
from typing import List, Optional

from backend.app.domain.entities import incident


class IncidentRepository(ABC):
    @abstractmethod
    def create_incident(self, incident: incident.Incident) -> incident.Incident:
        pass

    @abstractmethod
    def get_incident_by_id(self, incident_id: int) -> Optional[incident.Incident]:
        pass

    @abstractmethod
    def update_incident(self, incident: incident.Incident) -> incident.Incident:
        pass

    @abstractmethod
    def delete_incident(self, incident_id: int) -> None:
        pass

    @abstractmethod
    def list_incidents(self) -> List[incident.Incident]:
        pass

    @abstractmethod
    def list_incidents_by_assigned_user(self, user_id: int) -> List[incident.Incident]:
        pass

    @abstractmethod
    def list_incidents_by_severity(self, severity: incident.Severity) -> List[incident.Incident]:
        pass

    @abstractmethod
    def list_incidents_by_state(self, state: incident.State) -> List[incident.Incident]:
        pass
