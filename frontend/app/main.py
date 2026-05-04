from __future__ import annotations

from datetime import datetime, timezone
import math

import streamlit as st

from data import (
    SEVERITIES,
    STATES,
    filter_incidents,
    get_assignee_options,
    get_incidents,
    show_toast,
)


st.set_page_config(page_title="IncidentFlow", layout="wide")


SEVERITY_COLORS = {
    "low": "#7FB069",
    "medium": "#F2B705",
    "high": "#E76F51",
    "critical": "#D00000",
}
STATE_COLORS = {
    "open": "#4C78A8",
    "triaged": "#8F63FF",
    "assigned": "#2A9D8F",
    "in_progress": "#F4A261",
    "resolved": "#43AA8B",
    "closed": "#6C757D",
}


st.title("IncidentFlow")

st.page_link("pages/create_incident.py", label="Create incident")

current_role = st.session_state.get("active_role", "Operator")
if current_role in ("Manager", "Admin"):
    st.page_link("pages/manager_dashboard.py", label="Dashboard")

if current_role == "Admin":
    st.page_link("pages/admin_dashboard.py", label="Admin Panel")

try:
    if "incidents" not in st.session_state:
        st.session_state["incidents"] = get_incidents()
    
    incidents = st.session_state["incidents"]
    
    if not incidents:
        st.warning("No incidents found. Create one to get started.")
        st.stop()

except Exception as e:
    st.error(f"Failed to load incidents: {str(e)}")
    show_toast("Connection error. Please refresh.", "error")
    st.stop()

with st.sidebar:
    st.header("Filters")
    role = st.selectbox("Role (testing)", ["Operator", "Commander", "Manager", "Admin"])
    st.session_state["active_role"] = role
    query = st.text_input("Search", placeholder="Title or description")
    selected_severities = st.multiselect("Severity", SEVERITIES, default=SEVERITIES)
    selected_states = st.multiselect("State", STATES, default=STATES)
    
    try:
        assignee_options = get_assignee_options(incidents)
    except Exception as e:
        st.warning("Failed to load assignees")
        assignee_options = ["All", "Unassigned"]
    
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
current_page = st.session_state.get("current_page", 1)
if current_page > total_pages:
    current_page = total_pages

page = st.number_input("Page", min_value=1, max_value=total_pages, value=current_page, step=1)
st.session_state["current_page"] = page
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

display_count = min(end, len(filtered))
st.caption(f"Showing {display_count} of {len(filtered)} incidents")
