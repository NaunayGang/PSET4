from backend.app.application.ports.add_comment_port import AddCommentPort
from backend.app.application.ports.assign_incident_port import AssignIncidentPort
from backend.app.application.ports.change_severity_port import ChangeSeverityPort
from backend.app.application.ports.create_incident_port import CreateIncidentPort
from backend.app.application.ports.transition_state_port import TransitionStatePort
from backend.app.application.ports.triage_output_port import TriageOutputPort
from backend.app.domain.entities.comment import Comment
from backend.app.domain.entities.incident import Incident
from backend.app.interface.dtos import IncidentDTO


class IncidentPresenter(
    TriageOutputPort,
    CreateIncidentPort,
    AddCommentPort,
    AssignIncidentPort,
    TransitionStatePort,
    ChangeSeverityPort
):
    def __init__(self) -> None:
        self.response_dto = None
        self.comment_dto = None
        self.error_message = None
        self.not_found = False
        self.not_found_id = None
        self._failure_flag = False
        self._not_found_flag = False
        self.failure_message = None

    def _create_incident_dto(self, incident: Incident) -> IncidentDTO:
        return IncidentDTO(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            severity=incident.severity.value,
            state=incident.state.value,
            assigned_to=incident.assigned_to,
            created_at=incident.created_at.isoformat() if incident.created_at else "",
            updated_at=incident.updated_at.isoformat() if incident.updated_at else None,
            summary_id=incident.summary_id if incident.summary_id else None
        )

    # TriageOutputPort methods
    def present_success(self, incident: Incident) -> None:
        self.response_dto = self._create_incident_dto(incident)

    # CreateIncidentPort and TransitionStatePort methods
    def present_incident(self, incident: Incident) -> None:
        self.response_dto = self._create_incident_dto(incident)

    # AddCommentPort methods
    def present_comment(self, comment: Comment) -> None:
        self.comment_dto = comment

    # Port methods for handling not found and failure states
    def present_not_found(self, incident_id: int) -> None:
        self._not_found_flag = True
        self.not_found_id = incident_id
        self.not_found = True
        self.error_message = f"Incident with ID {incident_id} not found."

    def present_failure(self, error_message: str) -> None:
        self._failure_flag = True
        self.failure_message = error_message
        self.error_message = error_message

    # Helper properties for controller compatibility
    @property
    def present_not_found_flag(self) -> bool:
        return self._not_found_flag

    @property
    def present_failure_flag(self) -> bool:
        return self._failure_flag
