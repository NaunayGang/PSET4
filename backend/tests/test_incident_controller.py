from datetime import datetime
from unittest.mock import MagicMock

import pytest

from backend.app.application.events import InMemoryEventBus
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
from backend.app.domain.entities.comment import Comment
from backend.app.domain.entities.incident import Incident
from backend.app.domain.entities.log import Log
from backend.app.domain.entities.user import User
from backend.app.domain.enums.role import Role
from backend.app.domain.enums.severity import Severity
from backend.app.domain.enums.state import State
from backend.app.interface.presenter import IncidentPresenter

# ---------- Fixtures ----------


@pytest.fixture
def mock_incident_repository():
    """Create a mock incident repository."""
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_log_repository():
    """Create a mock log repository."""
    repo = MagicMock()
    repo.create_log.return_value = MagicMock(spec=Log)
    return repo


@pytest.fixture
def mock_comment_repository():
    """Create a mock comment repository."""
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_notification_repository():
    repo = MagicMock()

    def _store(notification):
        notification.id = 1
        return notification

    repo.create_notification.side_effect = _store
    return repo


@pytest.fixture
def event_bus(mock_user_repository, mock_notification_repository):
    bus = InMemoryEventBus()
    dispatcher = InMemoryNotificationDispatcher()
    service = NotificationService(mock_user_repository, mock_notification_repository, dispatcher)
    service.register(bus)
    return bus


@pytest.fixture
def sample_incident():
    """Create a sample incident for testing."""
    return Incident(
        id=1,
        title="Test Incident",
        description="A test incident",
        severity=Severity.HIGH,
        state=State.OPEN,
        assigned_to=None,
        created_at=datetime.now(),
        updated_at=None,
        summary_id=None,
    )


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=1,
        username="test_user",
        password_hash="hashed_password",
        role=Role.ADMIN,
        created_at=datetime.now(),
        last_login=None,
    )


@pytest.fixture
def sample_comment():
    """Create a sample comment for testing."""
    return Comment(
        id=1,
        content="Test comment",
        author_id=1,
        timestamp=datetime.now(),
        incident_id=1,
    )


@pytest.fixture
def presenter():
    """Create a presenter for testing."""
    return IncidentPresenter()


# ---------- Create Incident Tests ----------


def test_create_incident_success(
    sample_user, sample_incident, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter, event_bus
):
    """Test CreateIncidentUseCase success path."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.create_incident.return_value = sample_incident

    use_case = CreateIncidentUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository, event_bus
    )
    use_case.execute(
        user_id=sample_user.id,
        title="Test Incident",
        description="A test incident",
        severity=Severity.HIGH,
        output_port=presenter,
    )

    assert presenter.response_dto is not None
    assert presenter.response_dto.title == "Test Incident"
    assert not presenter.present_failure_flag


def test_create_incident_unauthorized_user(
    mock_user_repository, mock_incident_repository, mock_log_repository, presenter
):
    """Test CreateIncidentUseCase with unauthorized user."""
    unauthorized_user = User(
        id=2,
        username="operator",
        password_hash="hashed",
        role=Role.TECHNICAL_RESPONDER,
        created_at=datetime.now(),
        last_login=None,
    )
    mock_user_repository.get_user_by_id.return_value = unauthorized_user

    use_case = CreateIncidentUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository
    )
    use_case.execute(
        user_id=unauthorized_user.id,
        title="Test",
        description="Test",
        severity=Severity.HIGH,
        output_port=presenter,
    )

    assert presenter.present_failure_flag


def test_create_incident_user_not_found(
    mock_user_repository, mock_incident_repository, mock_log_repository, presenter
):
    """Test CreateIncidentUseCase when user not found."""
    mock_user_repository.get_user_by_id.return_value = None

    use_case = CreateIncidentUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository
    )
    use_case.execute(
        user_id=999,
        title="Test",
        description="Test",
        severity=Severity.HIGH,
        output_port=presenter,
    )

    assert presenter.present_failure_flag


# ---------- Triage Incident Tests ----------


def test_triage_incident_success(
    sample_user, sample_incident, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter
):
    """Test TriageUseCase success path."""
    triaged_incident = Incident(
        id=1,
        title="Test Incident",
        description="A test incident",
        severity=Severity.CRITICAL,
        state=State.TRIAGED,
        assigned_to=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        summary_id=None,
    )

    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = sample_incident
    mock_incident_repository.update_incident.return_value = triaged_incident

    use_case = TriageUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository
    )
    use_case.execute(
        user_id=sample_user.id,
        incident_id=1,
        priority=Severity.CRITICAL,
        output_port=presenter,
    )

    assert presenter.response_dto is not None
    assert not presenter.present_failure_flag


def test_triage_nonexistent_incident(
    sample_user, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter
):
    """Test triaging a non-existent incident."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = None

    use_case = TriageUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository
    )

    with pytest.raises(ValueError):
        use_case.execute(
            user_id=sample_user.id,
            incident_id=999,
            priority=Severity.CRITICAL,
            output_port=presenter,
        )


# ---------- Transition State Tests ----------


def test_transition_state_success(
    sample_user, sample_incident, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter
):
    """Test TransitionStateUseCase success path."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = sample_incident

    use_case = TransitionStateUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository
    )
    use_case.execute(
        user_id=sample_user.id,
        incident_id=1,
        new_state=State.CANCELLED,
        output_port=presenter,
    )

    assert presenter.response_dto is not None
    assert not presenter.present_failure_flag


def test_transition_state_nonexistent_incident(
    sample_user, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter
):
    """Test transitioning state of non-existent incident."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = None

    use_case = TransitionStateUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository
    )
    use_case.execute(
        user_id=sample_user.id,
        incident_id=999,
        new_state=State.CANCELLED,
        output_port=presenter,
    )

    assert presenter.present_not_found_flag


# ---------- Add Comment Tests ----------


def test_add_comment_success(
    sample_user, sample_incident, sample_comment, mock_user_repository,
    mock_incident_repository, mock_comment_repository, mock_log_repository, presenter
):
    """Test AddCommentUseCase success path."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = sample_incident
    mock_comment_repository.create_comment.return_value = sample_comment

    use_case = AddCommentUseCase(
        mock_incident_repository,
        mock_user_repository,
        mock_comment_repository,
        mock_log_repository,
    )
    use_case.execute(
        incident_id=1,
        user_id=sample_user.id,
        content="Test comment",
        output_port=presenter,
    )

    assert presenter.comment_dto is not None
    assert not presenter.present_failure_flag


def test_add_comment_nonexistent_incident(
    sample_user, mock_user_repository, mock_incident_repository,
    mock_comment_repository, mock_log_repository, presenter
):
    """Test adding comment to non-existent incident."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = None

    use_case = AddCommentUseCase(
        mock_incident_repository,
        mock_user_repository,
        mock_comment_repository,
        mock_log_repository,
    )
    use_case.execute(
        incident_id=999,
        user_id=sample_user.id,
        content="Test",
        output_port=presenter,
    )

    assert presenter.present_not_found_flag


# ---------- Assign Incident Tests ----------


def test_assign_incident_success(
    sample_user, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter, event_bus
):
    """Test AssignIncidentUseCase success path."""
    triaged_incident = Incident(
        id=1,
        title="Test Incident",
        description="A test incident",
        severity=Severity.HIGH,
        state=State.TRIAGED,
        assigned_to=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        summary_id=None,
    )

    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = triaged_incident

    use_case = AssignIncidentUseCase(
        mock_incident_repository, mock_user_repository, mock_log_repository, event_bus
    )
    use_case.execute(
        incident_id=1,
        user_id=sample_user.id,
        output_port=presenter,
    )

    assert presenter.response_dto is not None
    assert not presenter.present_failure_flag


def test_assign_nonexistent_incident(
    sample_user, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter
):
    """Test assigning a non-existent incident."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = None

    use_case = AssignIncidentUseCase(
        mock_incident_repository, mock_user_repository, mock_log_repository
    )
    use_case.execute(
        incident_id=999,
        user_id=sample_user.id,
        output_port=presenter,
    )

    assert presenter.present_not_found_flag


# ---------- Change Severity Tests ----------


def test_change_severity_success(
    sample_user, sample_incident, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter, event_bus
):
    """Test ChangeSeverityUseCase success path."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = sample_incident

    use_case = ChangeSeverityUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository, event_bus
    )
    use_case.execute(
        user_id=sample_user.id,
        incident_id=1,
        new_severity=Severity.CRITICAL,
        output_port=presenter,
    )

    assert presenter.response_dto is not None
    assert not presenter.present_failure_flag


def test_change_severity_nonexistent_incident(
    sample_user, mock_user_repository, mock_incident_repository,
    mock_log_repository, presenter
):
    """Test changing severity of non-existent incident."""
    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_incident_repository.get_incident_by_id.return_value = None

    use_case = ChangeSeverityUseCase(
        mock_incident_repository, mock_log_repository, mock_user_repository
    )
    use_case.execute(
        user_id=sample_user.id,
        incident_id=999,
        new_severity=Severity.CRITICAL,
        output_port=presenter,
    )

    assert presenter.present_not_found_flag


# ---------- Presenter Tests ----------


def test_presenter_create_dto(sample_incident):
    """Test IncidentPresenter DTO creation."""
    presenter = IncidentPresenter()
    presenter.present_success(sample_incident)

    assert presenter.response_dto is not None
    assert presenter.response_dto.id == 1
    assert presenter.response_dto.title == "Test Incident"
    assert presenter.response_dto.severity == "high"
    assert presenter.response_dto.state == "open"


def test_presenter_not_found(presenter):
    """Test IncidentPresenter not found handling."""
    presenter.present_not_found(999)

    assert presenter.present_not_found_flag
    assert presenter.not_found_id == 999
    assert "not found" in presenter.error_message


def test_presenter_failure(presenter):
    """Test IncidentPresenter failure handling."""
    error_msg = "Test error message"
    presenter.present_failure(error_msg)

    assert presenter.present_failure_flag
    assert presenter.failure_message == error_msg
    assert presenter.error_message == error_msg


def test_presenter_comment(sample_comment, presenter):
    """Test IncidentPresenter comment handling."""
    presenter.present_comment(sample_comment)

    assert presenter.comment_dto is not None
    assert presenter.comment_dto.id == 1
    assert presenter.comment_dto.content == "Test comment"


def test_notifications_for_critical_incident_created(
    mock_incident_repository,
    mock_user_repository,
    mock_log_repository,
    mock_notification_repository,
    presenter,
):
    creator = User(
        id=1,
        username="creator",
        password_hash="hash",
        role=Role.OPERATOR,
        created_at=datetime.now(),
        last_login=None,
    )
    commander = User(
        id=2,
        username="commander",
        password_hash="hash",
        role=Role.INCIDENT_COMMANDER,
        created_at=datetime.now(),
        last_login=None,
    )
    manager = User(
        id=3,
        username="manager",
        password_hash="hash",
        role=Role.MANAGER,
        created_at=datetime.now(),
        last_login=None,
    )

    incident = Incident(
        id=11,
        title="Critical",
        description="Critical incident",
        severity=Severity.CRITICAL,
        state=State.OPEN,
        assigned_to=None,
        created_at=datetime.now(),
        updated_at=None,
        summary_id=None,
        created_by=creator.id,
    )

    mock_user_repository.get_user_by_id.return_value = creator
    mock_user_repository.list_users.return_value = [creator, commander, manager]
    mock_incident_repository.create_incident.return_value = incident

    bus = InMemoryEventBus()
    dispatcher = InMemoryNotificationDispatcher()
    NotificationService(mock_user_repository, mock_notification_repository, dispatcher).register(bus)

    use_case = CreateIncidentUseCase(
        mock_incident_repository,
        mock_log_repository,
        mock_user_repository,
        bus,
    )
    use_case.execute(
        user_id=creator.id,
        title="Critical",
        description="Critical incident",
        severity=Severity.CRITICAL,
        output_port=presenter,
    )

    called_user_ids = {call.args[0].user_id for call in mock_notification_repository.create_notification.call_args_list}
    assert called_user_ids == {commander.id, manager.id}


def test_notifications_for_assigned_incident(
    mock_incident_repository,
    mock_user_repository,
    mock_log_repository,
    mock_notification_repository,
    presenter,
):
    assignee = User(
        id=22,
        username="assignee",
        password_hash="hash",
        role=Role.INCIDENT_COMMANDER,
        created_at=datetime.now(),
        last_login=None,
    )
    incident = Incident(
        id=12,
        title="Triaged",
        description="T",
        severity=Severity.HIGH,
        state=State.TRIAGED,
        assigned_to=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        summary_id=None,
        created_by=1,
    )

    mock_user_repository.get_user_by_id.return_value = assignee
    mock_incident_repository.get_incident_by_id.return_value = incident

    bus = InMemoryEventBus()
    dispatcher = InMemoryNotificationDispatcher()
    NotificationService(mock_user_repository, mock_notification_repository, dispatcher).register(bus)

    use_case = AssignIncidentUseCase(
        mock_incident_repository,
        mock_user_repository,
        mock_log_repository,
        bus,
    )
    use_case.execute(
        incident_id=incident.id,
        user_id=assignee.id,
        output_port=presenter,
    )

    assert mock_notification_repository.create_notification.call_count == 1
    assert mock_notification_repository.create_notification.call_args[0][0].user_id == assignee.id


def test_notifications_for_severity_change(
    sample_user,
    sample_incident,
    mock_incident_repository,
    mock_user_repository,
    mock_log_repository,
    mock_notification_repository,
    presenter,
):
    commander = User(
        id=2,
        username="commander",
        password_hash="hash",
        role=Role.INCIDENT_COMMANDER,
        created_at=datetime.now(),
        last_login=None,
    )
    manager = User(
        id=3,
        username="manager",
        password_hash="hash",
        role=Role.MANAGER,
        created_at=datetime.now(),
        last_login=None,
    )

    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_user_repository.list_users.return_value = [sample_user, commander, manager]
    mock_incident_repository.get_incident_by_id.return_value = sample_incident

    bus = InMemoryEventBus()
    dispatcher = InMemoryNotificationDispatcher()
    NotificationService(mock_user_repository, mock_notification_repository, dispatcher).register(bus)

    use_case = ChangeSeverityUseCase(
        mock_incident_repository,
        mock_log_repository,
        mock_user_repository,
        bus,
    )
    use_case.execute(
        user_id=sample_user.id,
        incident_id=sample_incident.id,
        new_severity=Severity.CRITICAL,
        output_port=presenter,
    )

    called_user_ids = {call.args[0].user_id for call in mock_notification_repository.create_notification.call_args_list}
    assert called_user_ids == {commander.id, manager.id}


def test_notifications_for_resolved_incident(
    sample_user,
    mock_incident_repository,
    mock_user_repository,
    mock_log_repository,
    mock_notification_repository,
    presenter,
):
    manager = User(
        id=3,
        username="manager",
        password_hash="hash",
        role=Role.MANAGER,
        created_at=datetime.now(),
        last_login=None,
    )
    creator = User(
        id=4,
        username="creator",
        password_hash="hash",
        role=Role.OPERATOR,
        created_at=datetime.now(),
        last_login=None,
    )
    incident = Incident(
        id=99,
        title="In progress",
        description="incident",
        severity=Severity.HIGH,
        state=State.IN_PROGRESS,
        assigned_to=sample_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        summary_id=None,
        created_by=creator.id,
    )

    mock_user_repository.get_user_by_id.return_value = sample_user
    mock_user_repository.list_users.return_value = [sample_user, manager, creator]
    mock_incident_repository.get_incident_by_id.return_value = incident

    bus = InMemoryEventBus()
    dispatcher = InMemoryNotificationDispatcher()
    NotificationService(mock_user_repository, mock_notification_repository, dispatcher).register(bus)

    use_case = TransitionStateUseCase(
        mock_incident_repository,
        mock_log_repository,
        mock_user_repository,
        bus,
    )
    use_case.execute(
        user_id=sample_user.id,
        incident_id=incident.id,
        new_state=State.RESOLVED,
        output_port=presenter,
    )

    called_user_ids = {call.args[0].user_id for call in mock_notification_repository.create_notification.call_args_list}
    assert called_user_ids == {manager.id, creator.id}
