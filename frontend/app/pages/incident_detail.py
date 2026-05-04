from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from data import (
    SEVERITIES,
    USERS,
    get_available_transitions,
    get_incidents,
    transition_incident,
)


st.set_page_config(page_title="Incident Detail", layout="wide")

st.title("Incident Detail")

if "incidents" not in st.session_state:
    st.session_state["incidents"] = get_incidents()

incidents = st.session_state["incidents"]
incident_map = {incident["id"]: incident for incident in incidents}

query_params = st.query_params
selected_id = query_params.get("incident_id")

selected_incident = None
if selected_id is not None:
    try:
        selected_incident = incident_map.get(int(selected_id))
    except ValueError:
        selected_incident = None

if selected_incident is None:
    incident_id = st.selectbox("Select an incident", [incident["id"] for incident in incidents])
    selected_incident = incident_map[incident_id]

current_role = st.session_state.get("active_role", "Operator")
can_edit = current_role in ("Commander", "Admin")

st.subheader(selected_incident["title"])

st.write(selected_incident["description"])

col1, col2 = st.columns(2)
with col1:
    st.write(
        {
            "Severity": selected_incident["severity"],
            "State": selected_incident["state"],
            "Creator": selected_incident["creator"],
        }
    )
with col2:
    st.write(
        {
            "Assignee": selected_incident["assigned_to"] or "Unassigned",
        }
    )

created_at = selected_incident["created_at"].astimezone(timezone.utc)
created_at_text = created_at.strftime("%Y-%m-%d %H:%M UTC")

st.caption(f"Created at {created_at_text}")

link_value = f"incident_detail?incident_id={selected_incident['id']}"
st.text_input("Shareable link", value=link_value, disabled=True)
if st.button("Copy link", key="copy_link"):
    st.info("Copy the link from the field above.")

if can_edit:
    st.divider()
    st.subheader("Control Panel")

    available_transitions = get_available_transitions(selected_incident["state"])

    trans_col1, trans_col2, trans_col3 = st.columns([2, 2, 1])

    with trans_col1:
        if available_transitions:
            new_state = st.selectbox(
                "Transition to",
                [""] + available_transitions,
                index=0,
            )
        else:
            new_state = ""
            st.caption("No transitions available")

    with trans_col2:
        user_options = [""] + USERS
        new_assignee = st.selectbox(
            "Assign to",
            user_options,
            index=0,
        )

    with trans_col3:
        severity_options = [""] + SEVERITIES
        current_severity_idx = SEVERITIES.index(selected_incident["severity"]) + 1
        new_severity = st.selectbox(
            "Severity",
            severity_options,
            index=current_severity_idx,
        )

    resolution_summary = ""
    if new_state == "closed" and selected_incident["severity"] == "critical":
        resolution_summary = st.text_input("Resolution summary (required for CRITICAL)")

    apply_transition = st.button("Apply Changes")

    if apply_transition:
        target_state = new_state if new_state else None
        assignee_value = new_assignee if new_assignee else None
        severity_value = new_severity if new_severity else None

        if target_state or assignee_value or (severity_value and severity_value != selected_incident["severity"]):
            success, message = transition_incident(
                selected_incident,
                target_state,
                current_role,
                resolution_summary if target_state == "closed" else None,
                severity_value if severity_value and severity_value != selected_incident["severity"] else None,
                assignee_value if assignee_value else None,
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("No changes to apply.")

st.divider()

st.subheader("Timeline")

timeline = list(selected_incident.get("timeline", [])) + list(selected_incident.get("comments", []))
timeline.sort(key=lambda entry: entry["timestamp"])

if not timeline:
    st.info("No timeline events yet.")
else:
    for entry in timeline:
        ts = entry["timestamp"].astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
        actor = entry.get("actor") or "System"
        st.markdown(f"- [{entry['type'].upper()}] {entry['message']} ({actor}, {ts} UTC)")

st.subheader("Add comment")

is_closed = selected_incident["state"] == "closed"
if is_closed:
    st.warning("This incident is closed. Comments are disabled.")

with st.form("comment_form", clear_on_submit=True):
    comment = st.text_area("Comment", height=120, disabled=is_closed)
    submitted = st.form_submit_button("Post comment", disabled=is_closed)

if submitted:
    if not comment.strip():
        st.error("Comment is required.")
    else:
        author = st.session_state.get("active_role", "Operator")
        entry = {
            "type": "comment",
            "message": comment.strip(),
            "timestamp": datetime.now(timezone.utc),
            "actor": author,
        }
        selected_incident.setdefault("comments", []).append(entry)
        st.success("Comment added.")

st.page_link("main.py", label="Back to list")