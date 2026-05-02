from datetime import datetime

from backend.app.application.ports.transition_state_port import TransitionStatePort
from backend.app.domain.entities import Log, User
from backend.app.domain.enums import LogLevel, State, Role


class TransitionStateUseCase:
    def __init__(self, incident_repository, log_repository, user_repository):
        self.incident_repository = incident_repository
        self.log_repository = log_repository
        self.user_repository = user_repository

    def execute(self, user_id: int, incident_id: int, new_state: State, output_port: TransitionStatePort) -> None:
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
            output_port.present_failure(f"User with ID {user_id} does not have permission to transition incident state.")
            return

        try:
            # Transition the state of the incident
            old_state = incident.state
            match new_state:
                case State.CANCELLED:
                    incident.cancel_incident()
                case State.ESCALATED:
                    incident.escalate_incident()
                case State.IN_PROGRESS:
                    incident.inprogress_incident()
                case State.RESOLVED:
                    incident.resolve_incident()
                case State.CLOSED:
                    incident.close_incident()
                case _:
                    raise ValueError(f"Invalid state: {new_state}")
            self.incident_repository.update_incident(incident)

            # Log the state transition of the incident
            log_message = f"Incident {incident.id} transitioned from {old_state} to {new_state}"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.INFO,
                timestamp=datetime.now()
            ))

            output_port.present_incident(incident)
        except Exception as e:
            log_message = f"Failed to transition state of incident {incident_id} to {new_state}: {str(e)}"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            output_port.present_failure(str(e))
            raise ValueError(f"Failed to transition state: {str(e)}")
