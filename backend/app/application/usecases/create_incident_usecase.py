from datetime import datetime

from backend.app.application.ports.create_incident_port import CreateIncidentPort
from backend.app.domain.entities import Incident, Log
from backend.app.domain.enums import LogLevel, Severity, State


class CreateIncidentUseCase:
    def __init__(self, incident_repository, log_repository):
        self.incident_repository = incident_repository
        self.log_repository = log_repository

    def execute(self, title, description, severity, output_port: CreateIncidentPort) -> None:
        # Create the incident
        try:
            new_incident = Incident(
                id=0,  # ID will be set by the repository
                title=title,
                description=description,
                severity=Severity(severity),
                state=State.OPEN,
                assigned_to=None,
                created_at=datetime.now(),
                updated_at=None,
                summary_id=None
            )
            incident = self.incident_repository.create_incident(new_incident)

            # Log the creation of the incident
            log_message = f"Incident created with ID: {incident.id}"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.INFO,
                timestamp=datetime.now()
            ))

            output_port.present_incident(incident)

        except Exception as e:
            log_message = f"Failed to create incident: {str(e)}"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            output_port.present_failure(str(e))
            raise ValueError(f"Failed to create incident: {str(e)}")
