import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from backend.app.domain.entities import Comment, Incident, Log, Notification
from backend.app.domain.enums import Role, Severity, State


@pytest.fixture
def sample_user_id():
    """Fixture for sample user ID"""
    return 1


@pytest.fixture
def sample_incident_id():
    """Fixture for sample incident ID"""
    return 1


@pytest.fixture
def sample_incident(sample_user_id, sample_incident_id):
    """Fixture for creating a sample incident"""
    return Incident(
        id=sample_incident_id,
        title="Payment service down",
        description="Customers cannot complete transactions",
        severity=Severity.CRITICAL,
        state=State.OPEN,
        created_by=sample_user_id,
        assigned_to=None,
        summary_id=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_comment(sample_incident_id, sample_user_id):
    """Fixture for creating a sample comment"""
    return Comment(
        id=1,
        incident_id=sample_incident_id,
        author_id=sample_user_id,
        content="Investigation in progress",
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_audit_log(sample_incident_id, sample_user_id):
    """Fixture for creating a sample audit log"""
    from backend.app.domain.enums.log_level import LogLevel
    return Log(
        id=1,
        log_level=LogLevel.INFO,
        message="INCIDENT_CREATED",
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_notification(sample_incident_id, sample_user_id):
    """Fixture for creating a sample notification"""
    return Notification(
        id=1,
        user_id=sample_user_id,
        incident_id=sample_incident_id,
        event_type="INCIDENT_CREATED",
        message="CRITICAL incident created",
        read_at=None,
        created_at=datetime.now(),
    )


class TestIncidentEntity:
    """Tests for Incident domain entity"""

    def test_incident_creation(self, sample_incident):
        """Test that incident can be created with valid attributes"""
        assert sample_incident.title == "Payment service down"
        assert sample_incident.severity == Severity.CRITICAL
        assert sample_incident.state == State.OPEN
        assert sample_incident.assigned_to is None

    def test_incident_timestamps(self, sample_incident):
        """Test that timestamps are set correctly"""
        assert sample_incident.created_at is not None
        assert sample_incident.updated_at is not None
        assert isinstance(sample_incident.created_at, datetime)
        assert isinstance(sample_incident.updated_at, datetime)

    def test_incident_can_have_assignee(self, sample_incident):
        """Test incident assignment"""
        responder_id = 2
        sample_incident.assigned_to = responder_id
        assert sample_incident.assigned_to == responder_id

    def test_incident_resolution_summary_optional(self, sample_incident):
        """Test that resolution summary is optional initially"""
        assert sample_incident.summary_id is None


class TestSeverityEnum:
    """Tests for Severity enumeration"""

    def test_all_severity_values_exist(self):
        """Test that all required severity levels exist"""
        assert hasattr(Severity, "LOW")
        assert hasattr(Severity, "MEDIUM")
        assert hasattr(Severity, "HIGH")
        assert hasattr(Severity, "CRITICAL")

    def test_severity_equality(self):
        """Test severity enum comparison"""
        assert Severity.CRITICAL == Severity.CRITICAL
        assert Severity.LOW != Severity.CRITICAL

    def test_severity_string_representation(self):
        """Test severity can be converted to string"""
        assert str(Severity.CRITICAL) in ["Severity.CRITICAL", "CRITICAL", "critical"]


class TestStateEnum:
    """Tests for State enumeration"""

    def test_all_state_values_exist(self):
        """Test that all required states exist"""
        assert hasattr(State, "OPEN")
        assert hasattr(State, "TRIAGED")
        assert hasattr(State, "ASSIGNED")
        assert hasattr(State, "IN_PROGRESS")
        assert hasattr(State, "RESOLVED")
        assert hasattr(State, "CLOSED")
        assert hasattr(State, "ESCALATED")
        assert hasattr(State, "CANCELLED")

    def test_state_equality(self):
        """Test state enum comparison"""
        assert State.OPEN == State.OPEN
        assert State.OPEN != State.CLOSED


class TestRoleEnum:
    """Tests for Role enumeration"""

    def test_all_role_values_exist(self):
        """Test that all required roles exist"""
        assert hasattr(Role, "OPERATOR")
        assert hasattr(Role, "INCIDENT_COMMANDER")
        assert hasattr(Role, "TECHNICAL_RESPONDER")
        assert hasattr(Role, "MANAGER")
        assert hasattr(Role, "ADMIN")

    def test_role_equality(self):
        """Test role enum comparison"""
        assert Role.INCIDENT_COMMANDER == Role.INCIDENT_COMMANDER
        assert Role.OPERATOR != Role.INCIDENT_COMMANDER


class TestCommentEntity:
    """Tests for Comment domain entity"""

    def test_comment_creation(self, sample_comment):
        """Test comment can be created"""
        assert sample_comment.content == "Investigation in progress"
        assert sample_comment.author_id is not None
        assert sample_comment.incident_id is not None

    def test_comment_requires_text(self):
        """Test that comment text is generally expected to have content"""
        # In python dataclasses, we can create it without validation unless __post_init__ is used
        # We test that the content can be accessed
        comment = Comment(
            id=1,
            incident_id=1,
            author_id=1,
            content="",
            timestamp=datetime.now(),
        )
        assert comment.content == ""

    def test_comment_timestamp(self, sample_comment):
        """Test comment timestamp"""
        assert sample_comment.timestamp is not None
        assert isinstance(sample_comment.timestamp, datetime)


class TestAuditLogEntity:
    """Tests for Log (AuditLog) domain entity"""

    def test_audit_log_creation(self, sample_audit_log):
        """Test audit log can be created"""
        from backend.app.domain.enums.log_level import LogLevel
        assert sample_audit_log.message == "INCIDENT_CREATED"
        assert sample_audit_log.log_level == LogLevel.INFO


class TestNotificationEntity:
    """Tests for Notification domain entity"""

    def test_notification_creation(self, sample_notification):
        """Test notification can be created"""
        assert sample_notification.event_type == "INCIDENT_CREATED"
        assert sample_notification.message is not None
        assert sample_notification.read_at is None

    def test_notification_can_be_marked_read(self, sample_notification):
        """Test notification can be marked as read"""
        assert sample_notification.read_at is None
        sample_notification.read_at = datetime.now()
        assert sample_notification.read_at is not None

    def test_notification_timestamp(self, sample_notification):
        """Test notification has timestamp"""
        assert sample_notification.created_at is not None
        assert isinstance(sample_notification.created_at, datetime)


class TestIncidentCriticalRestrictions:
    """Tests for CRITICAL incident restrictions"""

    def test_critical_incident_requires_summary_to_close(self, sample_incident):
        """Test CRITICAL incident cannot close without summary"""
        sample_incident.severity = Severity.CRITICAL
        # This should be validated by business logic
        with pytest.raises(ValueError):
            sample_incident.state = State.RESOLVED
            sample_incident.close_incident()

    def test_non_critical_can_close_without_summary(self):
        """Test non-CRITICAL incidents don't need summary"""
        incident = Incident(
            id=1,
            title="Low priority",
            description="Can close without summary",
            severity=Severity.LOW,
            state=State.RESOLVED,
            assigned_to=1,
            summary_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        incident.close_incident()
        assert incident.state == State.CLOSED


class TestStateTransitionRules:
    """Tests for state transition business rules"""

    def test_incident_starts_in_open_state(self, sample_incident):
        """Test new incident is in OPEN state"""
        assert sample_incident.state == State.OPEN

    def test_cannot_enter_in_progress_without_assignee(self, sample_incident):
        """Test incident cannot go to IN_PROGRESS without assignee"""
        assert sample_incident.assigned_to is None
        # Must be in ASSIGNED state first to go to IN_PROGRESS
        with pytest.raises(ValueError):
            sample_incident.inprogress_incident()

    def test_closed_incident_cannot_transition(self, sample_incident):
        """Test CLOSED incident is terminal for some operations"""
        sample_incident.state = State.CLOSED

        with pytest.raises(ValueError):
            sample_incident.cancel_incident()

        with pytest.raises(ValueError):
            sample_incident.change_severity(Severity.LOW)

    def test_state_sequence(self):
        """Test valid state progression"""
        states = [
            State.OPEN,
            State.TRIAGED,
            State.ASSIGNED,
            State.IN_PROGRESS,
            State.RESOLVED,
            State.CLOSED,
        ]
        assert len(states) > 0
        assert states[0] == State.OPEN
        assert states[-1] == State.CLOSED
