from datetime import datetime

from backend.app.application.ports.change_severity_port import ChangeSeverityPort
from backend.app.domain.entities import Log
from backend.app.domain.enums import LogLevel, Role, Severity


class ChangeSeverityUseCase:
    def __init__(self, incident_repository, log_repository, user_repository):
        self.incident_repository = incident_repository
        self.log_repository = log_repository
        self.user_repository = user_repository

    def execute(self, user_id: int, incident_id: int, new_severity: Severity, output_port: ChangeSeverityPort) -> None:
        # Fetch the incident from the repository
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
            output_port.present_failure(f"User with ID {user_id} does not have permission to change incident severity.")
            return

        try:
            # Change the severity of the incident
            incident.change_severity(new_severity)

            self.incident_repository.update_incident(incident)

            # Log the severity change
            if new_severity == Severity.CRITICAL:
                log_message = f"Severity of incident {incident.id} changed to CRITICAL. Immediate attention required!"
                log_level = LogLevel.CRITICAL
            else:
                log_message = f"Severity of incident {incident.id} changed to {new_severity.value}"
                log_level = LogLevel.INFO

            self.log_repository.create_log(Log(
                message=log_message,
                log_level=log_level,
                timestamp=datetime.now()
            ))

            output_port.present_success(incident)
        except Exception as e:
            output_port.present_failure(str(e))
