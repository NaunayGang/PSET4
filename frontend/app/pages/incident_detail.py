from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from data import get_incidents


st.set_page_config(page_title="Incident Detail", layout="wide")

st.title("Incident Detail")

incidents = get_incidents()
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

st.page_link("main.py", label="Back to list")
