from backend.app.application.ports.transition_state_port import TransitionStatePort
from backend.app.domain.entities import Log, Incident
from backend.app.domain.enums import Severity, State, LogLevel
from datetime import datetime

class TransitionStateUseCase:
    def __init__(self, incident_repository, log_repository):
        self.incident_repository = incident_repository
        self.log_repository = log_repository

    def execute(self, incident_id: int, new_state: State, output_port: TransitionStatePort) -> None:
        # Fetch the incident from the repository
        incident = self.incident_repository.get_incident_by_id(incident_id)

        if not incident:
            output_port.present_not_found(incident_id)
            return

        try:
            # Transition the state of the incident
            old_state = incident.state
            match new_state:
                case State.CANCELLED:
                    incident.cancelIncident()
                case State.ESCALATED:
                    incident.escalateIncident()
                case State.IN_PROGRESS:
                    incident.inProgressIncident()
                case State.RESOLVED:
                    incident.resolveIncident()
                case State.CLOSED:
                    incident.closeIncident()
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
    