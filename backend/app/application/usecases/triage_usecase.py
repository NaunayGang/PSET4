from datetime import datetime

from backend.app.application.ports.triage_output_port import TriageOutputPort
from backend.app.domain.entities import log
from backend.app.domain.enums.severity import Severity


class TriageUseCase:
    def __init__(self, incident_repository, log_repository):
        self.incident_repository = incident_repository
        self.log_repository = log_repository

    def execute(self, incident_id: int, priority: Severity, output_port: TriageOutputPort) -> None:
        incident = self.incident_repository.get_incident_by_id(incident_id)
        if not incident:
            self.log_repository.create_log(log.Log(
                message=f"Attempted to triage non-existent incident with ID {incident_id}",
                log_level=log.LogLevel.WARNING,
                timestamp=datetime.now()
            ))
            output_port.present_not_found(incident_id)
            raise ValueError(f"Incident with ID {incident_id} not found.")

        try:
            incident.triage_incident(priority)
            updated_incident = self.incident_repository.update_incident(incident)
            output_port.present_success(updated_incident)
        except ValueError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to triage incident with ID {incident_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            output_port.present_failure(str(e))
            raise ValueError(f"Failed to triage incident: {str(e)}")
