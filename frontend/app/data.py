from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

import streamlit as st

SEVERITIES = ["low", "medium", "high", "critical"]
STATES = ["open", "triaged", "assigned", "in_progress", "resolved", "closed"]

STATE_TRANSITIONS = {
    "open": ["triaged"],
    "triaged": ["assigned"],
    "assigned": ["in_progress"],
    "in_progress": ["resolved"],
    "resolved": ["closed", "triaged"],
    "closed": [],
}

USERS = ["Marco", "Nina", "Carlos", "Irene", "Laura", "Felipe", "Sara", "Andre"]


def _timeline_entry(
    entry_type: str,
    message: str,
    timestamp: datetime,
    actor: str | None = None,
) -> dict:
    return {
        "type": entry_type,
        "message": message,
        "timestamp": timestamp,
        "actor": actor,
    }


def _build_timeline(created_at: datetime, creator: str, severity: str, state: str, assignee: str | None) -> list[dict]:
    timeline = [
        _timeline_entry("created", f"Incident created with severity {severity}", created_at, creator),
    ]

    if assignee:
        timeline.append(
            _timeline_entry("assignment", f"Assigned to {assignee}", created_at + timedelta(minutes=15), creator)
        )

    if state not in {"open", "assigned"}:
        timeline.append(
            _timeline_entry("state", f"State changed to {state}", created_at + timedelta(hours=1), creator)
        )

    return timeline


def get_incidents() -> list[dict]:
    base_time = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
    incidents = [
        {
            "id": 101,
            "title": "Database connection spikes",
            "description": "Intermittent connection errors from the API layer.",
            "severity": "high",
            "state": "in_progress",
            "creator": "Laura",
            "assigned_to": "Marco",
            "created_at": base_time - timedelta(hours=3),
        },
        {
            "id": 102,
            "title": "Latency increase on metrics pipeline",
            "description": "Processing latency exceeded SLO for 10 minutes.",
            "severity": "medium",
            "state": "triaged",
            "creator": "Felipe",
            "assigned_to": "Nina",
            "created_at": base_time - timedelta(hours=6),
        },
        {
            "id": 103,
            "title": "Critical payment failures",
            "description": "Payment gateway returning 502 in prod.",
            "severity": "critical",
            "state": "assigned",
            "creator": "Maria",
            "assigned_to": "Carlos",
            "created_at": base_time - timedelta(hours=1, minutes=25),
        },
        {
            "id": 104,
            "title": "Search indexing backlog",
            "description": "Index queue is growing after batch release.",
            "severity": "low",
            "state": "open",
            "creator": "Dario",
            "assigned_to": None,
            "created_at": base_time - timedelta(days=1, hours=2),
        },
        {
            "id": 105,
            "title": "Login errors for EU region",
            "description": "Spike in 401 errors for EU tenants.",
            "severity": "high",
            "state": "in_progress",
            "creator": "Sara",
            "assigned_to": "Nina",
            "created_at": base_time - timedelta(hours=9, minutes=10),
        },
        {
            "id": 106,
            "title": "Webhook delivery delays",
            "description": "Outbound webhooks delayed by 20 minutes.",
            "severity": "medium",
            "state": "open",
            "creator": "Andre",
            "assigned_to": None,
            "created_at": base_time - timedelta(days=2, hours=4),
        },
        {
            "id": 107,
            "title": "Cache eviction storm",
            "description": "Cache evictions causing request spikes.",
            "severity": "high",
            "state": "resolved",
            "creator": "Sofia",
            "assigned_to": "Marco",
            "created_at": base_time - timedelta(days=1, hours=6),
        },
        {
            "id": 108,
            "title": "Notification retries stuck",
            "description": "Retry queue is not draining as expected.",
            "severity": "medium",
            "state": "assigned",
            "creator": "Ken",
            "assigned_to": "Carlos",
            "created_at": base_time - timedelta(hours=4, minutes=45),
        },
        {
            "id": 109,
            "title": "Frontend bundle regression",
            "description": "Main bundle size grew by 20 percent.",
            "severity": "low",
            "state": "closed",
            "creator": "Luis",
            "assigned_to": "Irene",
            "created_at": base_time - timedelta(days=3, hours=1),
        },
        {
            "id": 110,
            "title": "Critical API timeouts",
            "description": "Requests timing out for premium customers.",
            "severity": "critical",
            "state": "in_progress",
            "creator": "Maya",
            "assigned_to": "Irene",
            "created_at": base_time - timedelta(hours=2, minutes=5),
        },
        {
            "id": 111,
            "title": "Audit log missing entries",
            "description": "Some audit entries missing after deployment.",
            "severity": "medium",
            "state": "open",
            "creator": "Camilo",
            "assigned_to": None,
            "created_at": base_time - timedelta(days=1, hours=9),
        },
        {
            "id": 112,
            "title": "On-call handoff incomplete",
            "description": "Handoff notes not synced.",
            "severity": "low",
            "state": "triaged",
            "creator": "Gina",
            "assigned_to": "Nina",
            "created_at": base_time - timedelta(days=2, hours=3),
        },
    ]

    for incident in incidents:
        incident["timeline"] = _build_timeline(
            incident["created_at"],
            incident["creator"],
            incident["severity"],
            incident["state"],
            incident["assigned_to"],
        )
        incident["comments"] = [
            _timeline_entry(
                "comment",
                "Initial report logged.",
                incident["created_at"] + timedelta(minutes=5),
                incident["creator"],
            )
        ]

    return incidents


def filter_incidents(
    incidents: Iterable[dict],
    severities: set[str],
    states: set[str],
    assignee: str | None,
    query: str,
) -> list[dict]:
    results = []
    needle = query.strip().lower()

    for incident in incidents:
        if severities and incident["severity"] not in severities:
            continue
        if states and incident["state"] not in states:
            continue
        if assignee and assignee != "All":
            if assignee == "Unassigned" and incident["assigned_to"] is not None:
                continue
            if assignee not in ("Unassigned", "All") and incident["assigned_to"] != assignee:
                continue
        if needle:
            title = incident["title"].lower()
            description = incident["description"].lower()
            if needle not in title and needle not in description:
                continue
        results.append(incident)

    return results


def _get_assignee_options(incidents: Iterable[dict]) -> list[str]:
    assignees = sorted({incident["assigned_to"] for incident in incidents if incident["assigned_to"]})
    return ["All", "Unassigned"] + assignees


@st.cache_data
def get_assignee_options(_incidents: list[dict]) -> list[str]:
    return _get_assignee_options(_incidents)


def get_available_transitions(current_state: str) -> list[str]:
    return STATE_TRANSITIONS.get(current_state, [])


def can_transition(current_state: str, target_state: str) -> bool:
    return target_state in STATE_TRANSITIONS.get(current_state, [])


def validate_transition(incident: dict, target_state: str, resolution_summary: str = None) -> tuple[bool, str]:
    current_state = incident["state"]
    severity = incident["severity"]
    assignee = incident.get("assigned_to")

    if target_state == "closed" and severity == "critical" and not resolution_summary:
        return False, "Cannot close CRITICAL incident without resolution summary."

    if target_state == "in_progress" and not assignee:
        return False, "Cannot move to IN_PROGRESS without assignee."

    valid_transitions = STATE_TRANSITIONS.get(current_state, [])
    if target_state not in valid_transitions:
        return False, f"Invalid transition from {current_state} to {target_state}."

    return True, ""


def transition_incident(
    incident: dict,
    target_state: str,
    actor: str,
    resolution_summary: str = None,
    new_severity: str = None,
    new_assignee: str = None,
) -> tuple[bool, str]:
    valid, error = validate_transition(incident, target_state, resolution_summary)
    if not valid:
        return False, error

    timestamp = datetime.now(timezone.utc)
    current_state = incident["state"]

    if target_state != current_state:
        incident["state"] = target_state
        incident.setdefault("timeline", []).append({
            "type": "state",
            "message": f"State changed from {current_state} to {target_state}",
            "timestamp": timestamp,
            "actor": actor,
        })
        if resolution_summary:
            incident.setdefault("timeline", []).append({
                "type": "resolution",
                "message": f"Resolution: {resolution_summary}",
                "timestamp": timestamp,
                "actor": actor,
            })

    if new_severity and new_severity != incident.get("severity"):
        old_severity = incident.get("severity")
        incident["severity"] = new_severity
        incident.setdefault("timeline", []).append({
            "type": "severity",
            "message": f"Severity changed from {old_severity} to {new_severity}",
            "timestamp": timestamp,
            "actor": actor,
        })

    if new_assignee is not None and new_assignee != incident.get("assigned_to"):
        old_assignee = incident.get("assigned_to") or "Unassigned"
        new_assignee_display = new_assignee if new_assignee else "Unassigned"
        incident["assigned_to"] = new_assignee
        incident.setdefault("timeline", []).append({
            "type": "assignment",
            "message": f"Assigned from {old_assignee} to {new_assignee_display}",
            "timestamp": timestamp,
            "actor": actor,
        })

    return True, "Transition applied successfully."
