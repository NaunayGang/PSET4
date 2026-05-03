from datetime import datetime

from backend.app.application.events import IncidentEvent, IncidentEventType
from backend.app.application.ports.create_incident_port import CreateIncidentPort
from backend.app.domain.entities import Incident, Log
from backend.app.domain.enums import LogLevel, Role, Severity, State


class CreateIncidentUseCase:
    def __init__(self, incident_repository, log_repository, user_repository, event_bus=None):
        self.incident_repository = incident_repository
        self.log_repository = log_repository
        self.user_repository = user_repository
        self.event_bus = event_bus

    def execute(self, user_id: int, title: str, description: str, severity: Severity, output_port: CreateIncidentPort) -> None:
        # Create the incident

        user = self.user_repository.get_user_by_id(user_id)
        user_role = user.role if user else "Unknown"

        if not user:
            output_port.present_failure(f"User with ID {user_id} not found.")
            return

        if user_role not in [Role.ADMIN, Role.OPERATOR]:
            output_port.present_failure(f"User with ID {user_id} does not have permission to create incidents.")
            return

        try:
            new_incident = Incident(
                id=0,  # ID will be set by the repository
                title=title,
                description=description,
                severity=Severity(severity),
                state=State.OPEN,
                created_by=user_id,
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

            if self.event_bus:
                self.event_bus.publish(IncidentEvent(
                    event_type=IncidentEventType.INCIDENT_CREATED,
                    incident_id=incident.id,
                    actor_user_id=user_id,
                    payload={"severity": incident.severity.value},
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
