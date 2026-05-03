from datetime import datetime

from backend.app.application.events import IncidentEvent, IncidentEventType
from backend.app.application.ports.assign_incident_port import AssignIncidentPort
from backend.app.domain.entities import Log
from backend.app.domain.enums import LogLevel, Role


class AssignIncidentUseCase:
    def __init__(self, incident_repository, user_repository, log_repository, event_bus=None):
        self.incident_repository = incident_repository
        self.user_repository = user_repository
        self.log_repository = log_repository
        self.event_bus = event_bus

    def execute(self, incident_id: int, user_id: int, output_port: AssignIncidentPort) -> None:
        # Fetch the incident and user from the repositories
        incident = self.incident_repository.get_incident_by_id(incident_id)
        user = self.user_repository.get_user_by_id(user_id)
        user_role = user.role if user else "Unknown"

        if not incident:
            output_port.present_not_found(incident_id)
            return

        if not user:
            output_port.present_failure(f"User with ID {user_id} not found.")
            return

        if user_role not in [Role.ADMIN, Role.INCIDENT_COMMANDER]:
            output_port.present_failure(f"User with ID {user_id} does not have permission to be assigned to incidents.")
            return

        try:
            # Assign the incident to the user
            incident.assign_incident(user_id)

            self.incident_repository.update_incident(incident)

            # Log the assignment of the incident
            log_message = f"Incident {incident.id} assigned to user {user_id} (ID: {user_id})"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.INFO,
                timestamp=datetime.now()
            ))

            if self.event_bus:
                self.event_bus.publish(IncidentEvent(
                    event_type=IncidentEventType.INCIDENT_ASSIGNED,
                    incident_id=incident.id,
                    actor_user_id=user_id,
                    payload={"assignee_id": user_id},
                ))

            output_port.present_success(incident)
        except Exception as e:
            log_message = f"Failed to assign incident {incident_id} to user {user_id}: {str(e)}"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            output_port.present_failure(str(e))
            raise ValueError(f"Failed to assign incident: {str(e)}")
