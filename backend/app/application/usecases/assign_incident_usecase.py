from backend.app.application.ports.assign_incident_port import AssignIncidentPort
from backend.app.domain.entities import Log, Incident, User
from datetime import datetime

from backend.app.domain.enums.log_level import LogLevel

class AssignIncidentUseCase:
    def __init__(self, incident_repository, user_repository, log_repository):
        self.incident_repository = incident_repository
        self.user_repository = user_repository
        self.log_repository = log_repository

    def execute(self, incident_id: int, user_id: int, output_port: AssignIncidentPort) -> None:
        # Fetch the incident and user from the repositories
        incident = self.incident_repository.get_incident_by_id(incident_id)

        if not incident:
            output_port.present_not_found(incident_id)
            return

        if not self.user_repository.get_user_by_id(user_id):
            output_port.present_failure(f"User with ID {user_id} not found.")
            return

        try:
            # Assign the incident to the user
            incident.assignIncident(user_id)

            self.incident_repository.update_incident(incident)

            # Log the assignment of the incident
            log_message = f"Incident {incident.id} assigned to user {user_id} (ID: {user_id})"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.INFO,
                timestamp=datetime.now()
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