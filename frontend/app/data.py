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


def get_counts_by_severity(incidents: list[dict]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for incident in incidents:
        severity = incident.get("severity", "low")
        if severity in counts:
            counts[severity] += 1
    return counts


def get_counts_by_state(incidents: list[dict]) -> dict[str, int]:
    counts = {}
    for state in STATES:
        counts[state] = 0
    for incident in incidents:
        state = incident.get("state")
        if state in counts:
            counts[state] += 1
    return counts


def get_critical_recent(incidents: list[dict], hours: int = 24) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    for incident in incidents:
        if incident.get("severity") == "critical":
            created = incident.get("created_at")
            if created and created > cutoff:
                recent.append(incident)
    return recent


def get_unassigned(incidents: list[dict]) -> list[dict]:
    return [i for i in incidents if not i.get("assigned_to")]


def get_incidents_by_day(incidents: list[dict], days: int = 7) -> dict[str, int]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    by_day = {}
    for i in range(days):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        by_day[day] = 0
    for incident in incidents:
        created = incident.get("created_at")
        if created and created > cutoff:
            day = created.strftime("%Y-%m-%d")
            if day in by_day:
                by_day[day] += 1
    return by_day


def get_audit_logs(incidents: list[dict], actor_filter: str = None, type_filter: str = None) -> list[dict]:
    logs = []
    for incident in incidents:
        timeline = incident.get("timeline", [])
        for entry in timeline:
            if entry.get("type") in ("state", "severity", "assignment"):
                if actor_filter and entry.get("actor") != actor_filter:
                    continue
                if type_filter and entry.get("type") != type_filter:
                    continue
                logs.append({
                    "incident_id": incident["id"],
                    "incident_title": incident["title"],
                    "type": entry.get("type"),
                    "message": entry.get("message"),
                    "actor": entry.get("actor"),
                    "timestamp": entry.get("timestamp"),
                })
    logs.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
    return logs
