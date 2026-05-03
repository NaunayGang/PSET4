from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from data import get_incidents


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

st.subheader(selected_incident["title"])

st.write(selected_incident["description"])

st.write(
    {
        "Severity": selected_incident["severity"],
        "State": selected_incident["state"],
        "Creator": selected_incident["creator"],
        "Assignee": selected_incident["assigned_to"] or "Unassigned",
    }
)

created_at = selected_incident["created_at"].astimezone(timezone.utc)
created_at_text = created_at.strftime("%Y-%m-%d %H:%M UTC")

st.caption(f"Created at {created_at_text}")

link_value = f"incident_detail?incident_id={selected_incident['id']}"
st.text_input("Shareable link", value=link_value, disabled=True)
if st.button("Copy link"):
    st.info("Copy the link from the field above.")

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
