from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from backend.app.application.events import InMemoryEventBus
from backend.app.application.ports.repositories import (
    CommentRepository,
    IncidentRepository,
    LogRepository,
    NotificationRepository,
    UserRepository,
)
from backend.app.application.services.notification_service import (
    InMemoryNotificationDispatcher,
    NotificationService,
)
from backend.app.application.usecases import (
    AddCommentUseCase,
    AssignIncidentUseCase,
    ChangeSeverityUseCase,
    CreateIncidentUseCase,
    TransitionStateUseCase,
    TriageUseCase,
)
from backend.app.domain.entities import User
from backend.app.domain.enums.severity import Severity
from backend.app.domain.enums.state import State
from backend.app.interface.auth.jwt_auth import get_current_user
from backend.app.interface.auth.role_decorator import role_required
from backend.app.interface.dtos.incident_dto import IncidentDTO
from backend.app.interface.presenter import IncidentPresenter

router = APIRouter()

class CreateIncidentRequest(BaseModel):
    title: str
    description: str | None = None
    severity: str

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, value) -> str:
        if value not in ["Low", "Medium", "High", "Critical"]:
            raise ValueError(f"Invalid severity level: {value}")
        return value

class ChangeSeverityRequest(BaseModel):
    new_severity: Severity

    @field_validator('new_severity')
    @classmethod
    def validate_severity(cls, value) -> str:
        if value not in ["Low", "Medium", "High", "Critical"]:
            raise ValueError(f"Invalid severity level: {value}")
        return value

class TransitionStateRequest(BaseModel):
    new_state: str

    @field_validator('new_state')
    @classmethod
    def validate_state(cls, value) -> str:
        valid_states = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED", "CANCELLED", "ESCALATED"]
        if value not in valid_states:
            raise ValueError(f"Invalid state: {value}")
        return value

class AddCommentRequest(BaseModel):
    content: str

class AssignIncidentRequest(BaseModel):
    assigned_user_id: int

def get_incident_repo() -> IncidentRepository: ...
def get_log_repo() -> LogRepository: ...
def get_user_repo() -> UserRepository: ...
def get_comment_repo() -> CommentRepository: ...
def get_notification_repo() -> NotificationRepository: ...


notification_dispatcher = InMemoryNotificationDispatcher()


def build_event_bus(user_repository: UserRepository, notification_repository: NotificationRepository) -> InMemoryEventBus:
    event_bus = InMemoryEventBus()
    notification_service = NotificationService(user_repository, notification_repository, notification_dispatcher)
    notification_service.register(event_bus)
    return event_bus

@router.post("/incidents", response_model=IncidentDTO)
@role_required("Admin", "Operator")
def create_incident(
    request: CreateIncidentRequest,
    current_user: User = Depends(get_current_user),
    incident_repository: IncidentRepository = Depends(get_incident_repo),
    log_repository: LogRepository = Depends(get_log_repo),
    user_repository: UserRepository = Depends(get_user_repo),
    notification_repository: NotificationRepository = Depends(get_notification_repo),
):
    try:
        severity_enum = Severity(request.severity)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid severity level: {request.severity}")

    presenter = IncidentPresenter()
    event_bus = build_event_bus(user_repository, notification_repository)
    use_case = CreateIncidentUseCase(incident_repository, log_repository, user_repository, event_bus)
    use_case.execute(
        user_id=current_user.id,
        title=request.title,
        description=request.description or "",
        severity=severity_enum,
        output_port=presenter
    )

    if presenter.present_failure_flag:
        raise HTTPException(status_code=400, detail=presenter.failure_message)

    return presenter.response_dto

@router.post("/incidents/{incident_id}/triage", response_model=IncidentDTO)
@role_required("Admin", "Incident_commander")
def triage_incident(
    incident_id: int,
    request: ChangeSeverityRequest,
    current_user: User = Depends(get_current_user),
    incident_repository: IncidentRepository = Depends(get_incident_repo),
    log_repository: LogRepository = Depends(get_log_repo),
    user_repository: UserRepository = Depends(get_user_repo),
    notification_repository: NotificationRepository = Depends(get_notification_repo),
):
    try:
        severity_enum = Severity(request.new_severity)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid severity level: {request.new_severity}")

    presenter = IncidentPresenter()
    event_bus = build_event_bus(user_repository, notification_repository)
    use_case = TriageUseCase(incident_repository, log_repository, user_repository, event_bus)
    use_case.execute(
        user_id=current_user.id,
        incident_id=incident_id,
        priority=severity_enum,
        output_port=presenter
    )

    if presenter.present_failure_flag:
        raise HTTPException(status_code=400, detail=presenter.failure_message)
    if presenter.present_not_found_flag:
        raise HTTPException(status_code=404, detail=f"Incident with ID {presenter.not_found_id} not found.")

    return presenter.response_dto

@router.post("/incidents/{incident_id}/transition-state", response_model=IncidentDTO)
@role_required("Admin", "Incident_commander")
def transition_state(
    incident_id: int,
    request: TransitionStateRequest,
    current_user: User = Depends(get_current_user),
    incident_repository: IncidentRepository = Depends(get_incident_repo),
    log_repository: LogRepository = Depends(get_log_repo),
    user_repository: UserRepository = Depends(get_user_repo),
    notification_repository: NotificationRepository = Depends(get_notification_repo),
):
    try:
        state_enum = State[request.new_state]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid state: {request.new_state}")

    presenter = IncidentPresenter()
    event_bus = build_event_bus(user_repository, notification_repository)
    use_case = TransitionStateUseCase(incident_repository, log_repository, user_repository, event_bus)
    use_case.execute(
        user_id=current_user.id,
        incident_id=incident_id,
        new_state=state_enum,
        output_port=presenter
    )

    if presenter.present_failure_flag:
        raise HTTPException(status_code=400, detail=presenter.failure_message)
    if presenter.present_not_found_flag:
        raise HTTPException(status_code=404, detail=f"Incident with ID {presenter.not_found_id} not found.")

    return presenter.response_dto

@router.post("/incidents/{incident_id}/comments")
@role_required("Admin", "Operator", "Technical_responder")
def add_comment(
    incident_id: int,
    request: AddCommentRequest,
    current_user: User = Depends(get_current_user),
    incident_repository: IncidentRepository = Depends(get_incident_repo),
    log_repository: LogRepository = Depends(get_log_repo),
    user_repository: UserRepository = Depends(get_user_repo),
    comment_repository: CommentRepository = Depends(get_comment_repo)
):
    presenter = IncidentPresenter()
    use_case = AddCommentUseCase(incident_repository, user_repository, comment_repository, log_repository)
    use_case.execute(
        incident_id=incident_id,
        user_id=current_user.id,
        content=request.content,
        output_port=presenter
    )

    if presenter.present_failure_flag:
        raise HTTPException(status_code=400, detail=presenter.failure_message)
    if presenter.present_not_found_flag:
        raise HTTPException(status_code=404, detail=f"Incident with ID {presenter.not_found_id} not found.")

    return {"comment_id": presenter.comment_dto.id if presenter.comment_dto else None}

@router.post("/incidents/{incident_id}/assign", response_model=IncidentDTO)
@role_required("Admin", "Incident_commander")
def assign_incident(
    incident_id: int,
    request: AssignIncidentRequest,
    current_user: User = Depends(get_current_user),
    incident_repository: IncidentRepository = Depends(get_incident_repo),
    log_repository: LogRepository = Depends(get_log_repo),
    user_repository: UserRepository = Depends(get_user_repo),
    notification_repository: NotificationRepository = Depends(get_notification_repo),
):
    presenter = IncidentPresenter()
    event_bus = build_event_bus(user_repository, notification_repository)
    use_case = AssignIncidentUseCase(incident_repository, user_repository, log_repository, event_bus)
    use_case.execute(
        incident_id=incident_id,
        user_id=request.assigned_user_id,
        output_port=presenter
    )

    if presenter.present_failure_flag:
        raise HTTPException(status_code=400, detail=presenter.failure_message)
    if presenter.present_not_found_flag:
        raise HTTPException(status_code=404, detail=f"Incident with ID {presenter.not_found_id} not found.")

    return presenter.response_dto

@router.post("/incidents/{incident_id}/change_severity", response_model=IncidentDTO)
@role_required("Admin", "Incident_manager")
def change_severity(
    incident_id: int,
    request: ChangeSeverityRequest,
    current_user: User = Depends(get_current_user),
    incident_repository: IncidentRepository = Depends(get_incident_repo),
    log_repository: LogRepository = Depends(get_log_repo),
    user_repository: UserRepository = Depends(get_user_repo),
    notification_repository: NotificationRepository = Depends(get_notification_repo),

):

    try:
        severity_enum = Severity(request.new_severity)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid severity level: {request.new_severity}")

    presenter = IncidentPresenter()
    event_bus = build_event_bus(user_repository, notification_repository)
    use_case = ChangeSeverityUseCase(incident_repository, log_repository, user_repository, event_bus)
    use_case.execute(
        user_id=current_user.id,
        incident_id=incident_id,
        new_severity=severity_enum,
        output_port=presenter
    )

    if presenter.present_failure_flag:
        raise HTTPException(status_code=400, detail=presenter.failure_message)
    if presenter.present_not_found_flag:
        raise HTTPException(status_code=404, detail=f"Incident with ID {presenter.not_found_id} not found.")

    return presenter.response_dto
