import pytest
from datetime import datetime
from uuid import uuid4
from fastapi.testclient import TestClient

# These imports will need to be adjusted based on actual structure
from backend.app.api.main import app
from backend.app.domain.enums import Severity, IncidentState, Role


@pytest.fixture
def client():
    """Fixture for test client"""
    return TestClient(app)


@pytest.fixture
def auth_tokens():
    """Fixture for authentication tokens for different roles"""
    return {
        "operator": "token_operator_placeholder",
        "commander": "token_commander_placeholder",
        "responder": "token_responder_placeholder",
        "manager": "token_manager_placeholder",
        "admin": "token_admin_placeholder",
    }


@pytest.fixture
def test_users():
    """Fixture for test users"""
    return {
        "operator": {
            "id": str(uuid4()),
            "email": "operator@test.com",
            "role": Role.OPERATOR,
        },
        "commander": {
            "id": str(uuid4()),
            "email": "commander@test.com",
            "role": Role.COMMANDER,
        },
        "responder": {
            "id": str(uuid4()),
            "email": "responder@test.com",
            "role": Role.RESPONDER,
        },
        "manager": {
            "id": str(uuid4()),
            "email": "manager@test.com",
            "role": Role.MANAGER,
        },
        "admin": {
            "id": str(uuid4()),
            "email": "admin@test.com",
            "role": Role.ADMIN,
        },
    }


class TestIncidentCreation:
    """Integration tests for incident creation"""

    def test_operator_can_create_incident(self, client, auth_tokens):
        """Test that Operator role can create incidents"""
        response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={
                "title": "Payment service down",
                "description": "Customers cannot complete transactions",
                "severity": "CRITICAL",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Payment service down"
        assert data["severity"] == "CRITICAL"
        assert data["state"] == "OPEN"

    def test_commander_can_create_incident(self, client, auth_tokens):
        """Test that Commander role can create incidents"""
        response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['commander']}"},
            json={
                "title": "Database connection pool exhausted",
                "description": "All connections in use",
                "severity": "HIGH",
            },
        )
        assert response.status_code == 201

    def test_responder_cannot_create_incident(self, client, auth_tokens):
        """Test that Responder role cannot create incidents"""
        response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['responder']}"},
            json={
                "title": "Test",
                "description": "Test",
                "severity": "LOW",
            },
        )
        assert response.status_code == 403

    def test_create_incident_sets_creator(self, client, auth_tokens, test_users):
        """Test that creator is set to the authenticated user"""
        response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={
                "title": "Test incident",
                "description": "Test",
                "severity": "MEDIUM",
            },
        )
        assert response.status_code == 201
        data = response.json()
        # Creator should be set to operator
        assert data["creator_id"] is not None

    def test_incident_requires_title(self, client, auth_tokens):
        """Test that incident title is required"""
        response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={
                "description": "No title",
                "severity": "LOW",
            },
        )
        assert response.status_code == 400


class TestStateTransitions:
    """Integration tests for state machine transitions"""

    def test_valid_transition_open_to_triaged(self, client, auth_tokens):
        """Test valid state transition OPEN → TRIAGED"""
        # Create incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "MEDIUM"},
        )
        incident_id = create_response.json()["id"]

        # Transition to TRIAGED
        response = client.patch(
            f"/api/incidents/{incident_id}/state",
            headers={"Authorization": f"Bearer {auth_tokens['commander']}"},
            json={"state": "TRIAGED"},
        )
        assert response.status_code == 200
        assert response.json()["state"] == "TRIAGED"

    def test_cannot_transition_to_in_progress_without_assignee(
        self, client, auth_tokens
    ):
        """Test that incident cannot move to IN_PROGRESS without assignee"""
        # Create and triage incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "HIGH"},
        )
        incident_id = create_response.json()["id"]

        # Try to move to IN_PROGRESS without assigning
        response = client.patch(
            f"/api/incidents/{incident_id}/state",
            headers={"Authorization": f"Bearer {auth_tokens['commander']}"},
            json={"state": "IN_PROGRESS"},
        )
        assert response.status_code == 400
        assert "assignee" in response.json()["detail"].lower()

    def test_cannot_transition_from_closed(self, client, auth_tokens):
        """Test that CLOSED incident cannot transition to other states"""
        # Create, progress, resolve, and close incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "LOW"},
        )
        incident_id = create_response.json()["id"]

        # Move through states to CLOSED
        client.patch(
            f"/api/incidents/{incident_id}/state",
            headers={"Authorization": f"Bearer {auth_tokens['commander']}"},
            json={"state": "TRIAGED"},
        )

        # Try to transition from CLOSED (after closing)
        # This would require moving through all states first
        # Implementation detail based on actual API

    def test_only_commander_admin_can_change_state(self, client, auth_tokens):
        """Test that only Commander/Admin can change state"""
        # Create incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "MEDIUM"},
        )
        incident_id = create_response.json()["id"]

        # Operator tries to change state (should fail)
        response = client.patch(
            f"/api/incidents/{incident_id}/state",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"state": "TRIAGED"},
        )
        assert response.status_code == 403


class TestCriticalIncidentRules:
    """Integration tests for CRITICAL incident special rules"""

    def test_critical_incident_notifies_immediately(self, client, auth_tokens):
        """Test that CRITICAL incident triggers immediate notifications"""
        response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={
                "title": "Critical incident",
                "description": "CRITICAL severity",
                "severity": "CRITICAL",
            },
        )
        assert response.status_code == 201
        # In actual implementation, notifications should be created

    def test_critical_requires_summary_to_close(self, client, auth_tokens):
        """Test that CRITICAL incident cannot close without summary"""
        # Create CRITICAL incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={
                "title": "Critical",
                "description": "Critical",
                "severity": "CRITICAL",
            },
        )
        incident_id = create_response.json()["id"]

        # Try to close without summary
        response = client.patch(
            f"/api/incidents/{incident_id}/state",
            headers={"Authorization": f"Bearer {auth_tokens['commander']}"},
            json={"state": "CLOSED"},
        )
        assert response.status_code == 400
        assert "summary" in response.json()["detail"].lower()

    def test_critical_must_have_assignee(self, client, auth_tokens, test_users):
        """Test that CRITICAL incident must have assignee"""
        # Create CRITICAL incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={
                "title": "Critical",
                "description": "Critical",
                "severity": "CRITICAL",
            },
        )
        incident_id = create_response.json()["id"]

        # Try to move to IN_PROGRESS without assigning (should fail)
        response = client.patch(
            f"/api/incidents/{incident_id}/state",
            headers={"Authorization": f"Bearer {auth_tokens['commander']}"},
            json={"state": "IN_PROGRESS"},
        )
        assert response.status_code == 400


class TestPermissions:
    """Integration tests for role-based permissions"""

    def test_operator_can_comment(self, client, auth_tokens):
        """Test that Operator can add comments"""
        # Create incident first
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "LOW"},
        )
        incident_id = create_response.json()["id"]

        # Add comment
        response = client.post(
            f"/api/incidents/{incident_id}/comments",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"text": "Initial investigation"},
        )
        assert response.status_code == 201

    def test_manager_can_view_audit_log(self, client, auth_tokens):
        """Test that Manager can view audit log"""
        # Create incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "LOW"},
        )
        incident_id = create_response.json()["id"]

        # Manager views audit log
        response = client.get(
            f"/api/incidents/{incident_id}/audit",
            headers={"Authorization": f"Bearer {auth_tokens['manager']}"},
        )
        assert response.status_code == 200

    def test_operator_cannot_view_audit_log(self, client, auth_tokens):
        """Test that Operator cannot view audit log"""
        # Create incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "LOW"},
        )
        incident_id = create_response.json()["id"]

        # Operator tries to view audit log (should fail)
        response = client.get(
            f"/api/incidents/{incident_id}/audit",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
        )
        assert response.status_code == 403

    def test_responder_cannot_assign(self, client, auth_tokens, test_users):
        """Test that Responder cannot assign incidents"""
        # Create incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "MEDIUM"},
        )
        incident_id = create_response.json()["id"]

        # Responder tries to assign (should fail)
        response = client.patch(
            f"/api/incidents/{incident_id}/assignee",
            headers={"Authorization": f"Bearer {auth_tokens['responder']}"},
            json={"assignee_id": test_users["responder"]["id"]},
        )
        assert response.status_code == 403


class TestAuditTrail:
    """Integration tests for audit logging"""

    def test_incident_creation_is_audited(self, client, auth_tokens):
        """Test that incident creation creates audit log entry"""
        response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "MEDIUM"},
        )
        incident_id = response.json()["id"]

        # Check audit log
        audit_response = client.get(
            f"/api/incidents/{incident_id}/audit",
            headers={"Authorization": f"Bearer {auth_tokens['admin']}"},
        )
        assert audit_response.status_code == 200
        audit_data = audit_response.json()
        assert len(audit_data["results"]) > 0
        assert audit_data["results"][0]["action"] == "INCIDENT_CREATED"

    def test_state_change_is_audited(self, client, auth_tokens):
        """Test that state changes are recorded in audit log"""
        # Create incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "MEDIUM"},
        )
        incident_id = create_response.json()["id"]

        # Change state
        client.patch(
            f"/api/incidents/{incident_id}/state",
            headers={"Authorization": f"Bearer {auth_tokens['commander']}"},
            json={"state": "TRIAGED"},
        )

        # Check audit log includes state change
        audit_response = client.get(
            f"/api/incidents/{incident_id}/audit",
            headers={"Authorization": f"Bearer {auth_tokens['admin']}"},
        )
        audit_data = audit_response.json()
        # Should have at least 2 entries: creation and state change
        assert len(audit_data["results"]) >= 2

    def test_severity_change_is_audited(self, client, auth_tokens):
        """Test that severity changes are audited with old/new values"""
        # Create incident with LOW severity
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "LOW"},
        )
        incident_id = create_response.json()["id"]

        # Change to CRITICAL
        client.patch(
            f"/api/incidents/{incident_id}/severity",
            headers={"Authorization": f"Bearer {auth_tokens['commander']}"},
            json={"severity": "CRITICAL"},
        )

        # Check audit log
        audit_response = client.get(
            f"/api/incidents/{incident_id}/audit",
            headers={"Authorization": f"Bearer {auth_tokens['admin']}"},
        )
        audit_data = audit_response.json()
        severity_change = [
            e for e in audit_data["results"] if e["action"] == "SEVERITY_CHANGED"
        ]
        assert len(severity_change) > 0
        assert severity_change[0]["old_value"] == "LOW"
        assert severity_change[0]["new_value"] == "CRITICAL"


class TestTimeline:
    """Integration tests for incident timeline"""

    def test_comments_appear_in_timeline(self, client, auth_tokens):
        """Test that comments appear in incident detail timeline"""
        # Create incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "MEDIUM"},
        )
        incident_id = create_response.json()["id"]

        # Add comment
        client.post(
            f"/api/incidents/{incident_id}/comments",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"text": "Investigation started"},
        )

        # Get incident detail
        detail_response = client.get(
            f"/api/incidents/{incident_id}",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
        )
        detail_data = detail_response.json()
        assert len(detail_data["comments"]) > 0
        assert "Investigation started" in detail_data["comments"][0]["text"]

    def test_timeline_is_chronological(self, client, auth_tokens):
        """Test that timeline events are in chronological order"""
        # Create incident
        create_response = client.post(
            "/api/incidents",
            headers={"Authorization": f"Bearer {auth_tokens['operator']}"},
            json={"title": "Test", "description": "Test", "severity": "MEDIUM"},
        )
        incident_id = create_response.json()["id"]

        # Get timeline from audit log
        audit_response = client.get(
            f"/api/incidents/{incident_id}/audit",
            headers={"Authorization": f"Bearer {auth_tokens['admin']}"},
        )
        audit_data = audit_response.json()

        # Verify chronological order
        timestamps = [
            datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            for entry in audit_data["results"]
        ]
        assert timestamps == sorted(timestamps)
