from __future__ import annotations

from datetime import datetime, timezone
import math

import streamlit as st

from data import SEVERITIES, STATES, filter_incidents, get_assignee_options, get_incidents


st.set_page_config(page_title="IncidentFlow", layout="wide")


SEVERITY_COLORS = {
    "LOW": "#7FB069",
    "MEDIUM": "#F2B705",
    "HIGH": "#E76F51",
    "CRITICAL": "#D00000",
}
STATE_COLORS = {
    "OPEN": "#4C78A8",
    "TRIAGED": "#8F63FF",
    "ASSIGNED": "#2A9D8F",
    "IN_PROGRESS": "#F4A261",
    "RESOLVED": "#43AA8B",
    "CLOSED": "#6C757D",
}


st.title("IncidentFlow")

incidents = get_incidents()

with st.sidebar:
    st.header("Filters")
    role = st.selectbox("Role (testing)", ["Operator", "Commander", "Manager", "Admin"])
    query = st.text_input("Search", placeholder="Title or description")
    selected_severities = st.multiselect("Severity", SEVERITIES, default=SEVERITIES)
    selected_states = st.multiselect("State", STATES, default=STATES)
    assignee_options = get_assignee_options(incidents)
    selected_assignee = st.selectbox("Assignee", assignee_options)
    page_size = st.selectbox("Page size", [5, 10, 20], index=1)

st.caption(f"Active role: {role}")

filtered = filter_incidents(
    incidents,
    set(selected_severities),
    set(selected_states),
    selected_assignee,
    query,
)

if not filtered:
    st.info("No incidents match your filters.")
    st.stop()

total_pages = max(1, math.ceil(len(filtered) / page_size))
page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
start = (page - 1) * page_size
end = start + page_size


def badge(label: str, color: str) -> str:
    return (
        f"<span style='background:{color};color:#fff;"
        "padding:2px 8px;border-radius:999px;font-size:12px;"
        "margin-left:6px'>"
        f"{label}</span>"
    )


def time_ago(timestamp: datetime) -> str:
    now = datetime.now(timezone.utc)
    delta = now - timestamp
    minutes = int(delta.total_seconds() // 60)
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


for incident in filtered[start:end]:
    with st.container(border=True):
        header_col, badge_col = st.columns([4, 2])
        with header_col:
            st.subheader(incident["title"])
        with badge_col:
            severity_badge = badge(incident["severity"], SEVERITY_COLORS[incident["severity"]])
            state_badge = badge(incident["state"], STATE_COLORS[incident["state"]])
            st.markdown(severity_badge + state_badge, unsafe_allow_html=True)

        st.write(incident["description"])
        created_by = incident["creator"]
        assignee = incident["assigned_to"] or "Unassigned"
        created_at = time_ago(incident["created_at"])
        st.caption(f"Created by {created_by} | Assigned to {assignee} | {created_at}")
        st.markdown(f"[Open details](incident_detail?incident_id={incident['id']})")

st.caption(f"Showing {min(end, len(filtered))} of {len(filtered)} incidents")
