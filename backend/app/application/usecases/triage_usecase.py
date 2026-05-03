from datetime import datetime

from backend.app.application.events import IncidentEvent, IncidentEventType
from backend.app.application.ports.triage_output_port import TriageOutputPort
from backend.app.domain.entities import log
from backend.app.domain.enums import Role, Severity


class TriageUseCase:
    def __init__(self, incident_repository, log_repository, user_repository, event_bus=None):
        self.incident_repository = incident_repository
        self.user_repository = user_repository
        self.log_repository = log_repository
        self.event_bus = event_bus

    def execute(self, user_id: int, incident_id: int, priority: Severity, output_port: TriageOutputPort) -> None:
        user = self.user_repository.get_user_by_id(user_id)
        incident = self.incident_repository.get_incident_by_id(incident_id)
        user_role = user.role if user else "Unknown"

        if not user:
            output_port.present_failure(f"User with ID {user_id} not found.")
            return

        if user_role not in [Role.ADMIN, Role.INCIDENT_COMMANDER]:
            output_port.present_failure(f"User with ID {user_id} does not have permission to triage incidents.")
            return

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

            if self.event_bus:
                self.event_bus.publish(IncidentEvent(
                    event_type=IncidentEventType.SEVERITY_CHANGED,
                    incident_id=updated_incident.id,
                    actor_user_id=user_id,
                    payload={"new_severity": updated_incident.severity.value},
                ))

            output_port.present_success(updated_incident)
        except ValueError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to triage incident with ID {incident_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            output_port.present_failure(str(e))
            raise ValueError(f"Failed to triage incident: {str(e)}")
