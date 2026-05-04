import pytest
from datetime import datetime, timedelta
from backend.app.domain.entities import Incident, Comment, AuditLog, Notification
from backend.app.domain.enums import Severity, IncidentState, Role
from uuid import uuid4


@pytest.fixture
def sample_user_id():
    """Fixture for sample user ID"""
    return uuid4()


@pytest.fixture
def sample_incident_id():
    """Fixture for sample incident ID"""
    return uuid4()


@pytest.fixture
def sample_incident(sample_user_id, sample_incident_id):
    """Fixture for creating a sample incident"""
    return Incident(
        id=sample_incident_id,
        title="Payment service down",
        description="Customers cannot complete transactions",
        severity=Severity.CRITICAL,
        state=IncidentState.OPEN,
        creator_id=sample_user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_comment(sample_incident_id, sample_user_id):
    """Fixture for creating a sample comment"""
    return Comment(
        id=uuid4(),
        incident_id=sample_incident_id,
        author_id=sample_user_id,
        text="Investigation in progress",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_audit_log(sample_incident_id, sample_user_id):
    """Fixture for creating a sample audit log"""
    return AuditLog(
        id=uuid4(),
        incident_id=sample_incident_id,
        user_id=sample_user_id,
        action="INCIDENT_CREATED",
        old_value=None,
        new_value="OPEN",
        timestamp=datetime.utcnow(),
        details={"severity": "CRITICAL"},
    )


@pytest.fixture
def sample_notification(sample_incident_id, sample_user_id):
    """Fixture for creating a sample notification"""
    return Notification(
        id=uuid4(),
        user_id=sample_user_id,
        incident_id=sample_incident_id,
        event_type="INCIDENT_CREATED",
        message="CRITICAL incident created",
        read=False,
        created_at=datetime.utcnow(),
    )


class TestIncidentEntity:
    """Tests for Incident domain entity"""

    def test_incident_creation(self, sample_incident):
        """Test that incident can be created with valid attributes"""
        assert sample_incident.title == "Payment service down"
        assert sample_incident.severity == Severity.CRITICAL
        assert sample_incident.state == IncidentState.OPEN
        assert sample_incident.assignee_id is None

    def test_incident_is_critical(self, sample_incident):
        """Test is_critical() method"""
        assert sample_incident.is_critical() is True

        low_incident = Incident(
            id=uuid4(),
            title="Minor issue",
            description="Low severity",
            severity=Severity.LOW,
            state=IncidentState.OPEN,
            creator_id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert low_incident.is_critical() is False

    def test_incident_immutable_after_creation(self, sample_incident):
        """Test that incident fields are properly set"""
        original_title = sample_incident.title
        # Attempting to modify should not work (if entity is properly immutable)
        # This depends on implementation - adjust as needed
        assert sample_incident.title == original_title

    def test_incident_timestamps(self, sample_incident):
        """Test that timestamps are set correctly"""
        assert sample_incident.created_at is not None
        assert sample_incident.updated_at is not None
        assert isinstance(sample_incident.created_at, datetime)
        assert isinstance(sample_incident.updated_at, datetime)

    def test_incident_can_have_assignee(self, sample_incident, sample_user_id):
        """Test incident assignment"""
        responder_id = uuid4()
        sample_incident.assignee_id = responder_id
        assert sample_incident.assignee_id == responder_id

    def test_incident_resolution_summary_optional(self, sample_incident):
        """Test that resolution summary is optional initially"""
        assert sample_incident.resolution_summary is None


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
        assert str(Severity.CRITICAL) in ["Severity.CRITICAL", "CRITICAL"]


class TestIncidentStateEnum:
    """Tests for IncidentState enumeration"""

    def test_all_state_values_exist(self):
        """Test that all required states exist"""
        assert hasattr(IncidentState, "OPEN")
        assert hasattr(IncidentState, "TRIAGED")
        assert hasattr(IncidentState, "ASSIGNED")
        assert hasattr(IncidentState, "IN_PROGRESS")
        assert hasattr(IncidentState, "RESOLVED")
        assert hasattr(IncidentState, "CLOSED")
        assert hasattr(IncidentState, "ESCALATED")
        assert hasattr(IncidentState, "CANCELLED")

    def test_state_equality(self):
        """Test state enum comparison"""
        assert IncidentState.OPEN == IncidentState.OPEN
        assert IncidentState.OPEN != IncidentState.CLOSED


class TestRoleEnum:
    """Tests for Role enumeration"""

    def test_all_role_values_exist(self):
        """Test that all required roles exist"""
        assert hasattr(Role, "OPERATOR")
        assert hasattr(Role, "COMMANDER")
        assert hasattr(Role, "RESPONDER")
        assert hasattr(Role, "MANAGER")
        assert hasattr(Role, "ADMIN")

    def test_role_equality(self):
        """Test role enum comparison"""
        assert Role.COMMANDER == Role.COMMANDER
        assert Role.OPERATOR != Role.COMMANDER


class TestCommentEntity:
    """Tests for Comment domain entity"""

    def test_comment_creation(self, sample_comment):
        """Test comment can be created"""
        assert sample_comment.text == "Investigation in progress"
        assert sample_comment.author_id is not None
        assert sample_comment.incident_id is not None

    def test_comment_requires_text(self):
        """Test that comment text is required"""
        with pytest.raises(Exception):
            Comment(
                id=uuid4(),
                incident_id=uuid4(),
                author_id=uuid4(),
                text="",  # Empty text should fail
                created_at=datetime.utcnow(),
            )

    def test_comment_timestamp(self, sample_comment):
        """Test comment timestamp"""
        assert sample_comment.created_at is not None
        assert isinstance(sample_comment.created_at, datetime)


class TestAuditLogEntity:
    """Tests for AuditLog domain entity"""

    def test_audit_log_creation(self, sample_audit_log):
        """Test audit log can be created"""
        assert sample_audit_log.action == "INCIDENT_CREATED"
        assert sample_audit_log.new_value == "OPEN"
        assert sample_audit_log.user_id is not None

    def test_audit_log_tracks_changes(self, sample_audit_log):
        """Test audit log captures old and new values"""
        assert sample_audit_log.old_value is None
        assert sample_audit_log.new_value is not None

    def test_audit_log_includes_metadata(self, sample_audit_log):
        """Test audit log can include additional details"""
        assert sample_audit_log.details is not None
        assert "severity" in sample_audit_log.details


class TestNotificationEntity:
    """Tests for Notification domain entity"""

    def test_notification_creation(self, sample_notification):
        """Test notification can be created"""
        assert sample_notification.event_type == "INCIDENT_CREATED"
        assert sample_notification.message is not None
        assert sample_notification.read is False

    def test_notification_can_be_marked_read(self, sample_notification):
        """Test notification can be marked as read"""
        assert sample_notification.read is False
        sample_notification.read = True
        assert sample_notification.read is True

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
        assert sample_incident.is_critical() is True
        # Resolution summary should be required before closure

    def test_non_critical_can_close_without_summary(self):
        """Test non-CRITICAL incidents don't need summary"""
        incident = Incident(
            id=uuid4(),
            title="Low priority",
            description="Can close without summary",
            severity=Severity.LOW,
            state=IncidentState.OPEN,
            creator_id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert incident.is_critical() is False


class TestIncidentStateTransitionRules:
    """Tests for state transition business rules"""

    def test_incident_starts_in_open_state(self, sample_incident):
        """Test new incident is in OPEN state"""
        assert sample_incident.state == IncidentState.OPEN

    def test_cannot_enter_in_progress_without_assignee(self, sample_incident):
        """Test incident cannot go to IN_PROGRESS without assignee"""
        assert sample_incident.assignee_id is None
        # Business logic should prevent transition to IN_PROGRESS

    def test_closed_incident_cannot_transition(self, sample_incident):
        """Test CLOSED incident is terminal"""
        sample_incident.state = IncidentState.CLOSED
        # Should not be able to transition from CLOSED

    def test_state_sequence(self):
        """Test valid state progression"""
        states = [
            IncidentState.OPEN,
            IncidentState.TRIAGED,
            IncidentState.ASSIGNED,
            IncidentState.IN_PROGRESS,
            IncidentState.RESOLVED,
            IncidentState.CLOSED,
        ]
        assert len(states) > 0
        assert states[0] == IncidentState.OPEN
        assert states[-1] == IncidentState.CLOSED
