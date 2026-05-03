from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from data import SEVERITIES, get_incidents


st.set_page_config(page_title="Create Incident", layout="wide")

st.title("Create incident")

if "incidents" not in st.session_state:
    st.session_state["incidents"] = get_incidents()

incidents = st.session_state["incidents"]

with st.form("create_incident_form"):
    title = st.text_input("Title")
    description = st.text_area("Description", height=140)
    severity = st.selectbox("Severity", SEVERITIES)
    submitted = st.form_submit_button("Create")

if submitted:
    errors = []
    if not title.strip():
        errors.append("Title is required.")
    if not description.strip():
        errors.append("Description is required.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        new_id = max(incident["id"] for incident in incidents) + 1 if incidents else 1
        creator = st.session_state.get("active_role", "Operator")
        created_at = datetime.now(timezone.utc)
        new_incident = {
            "id": new_id,
            "title": title.strip(),
            "description": description.strip(),
            "severity": severity,
            "state": "open",
            "creator": creator,
            "assigned_to": None,
            "created_at": created_at,
            "timeline": [
                {
                    "type": "created",
                    "message": f"Incident created with severity {severity}",
                    "timestamp": created_at,
                    "actor": creator,
                }
            ],
            "comments": [],
        }
        incidents.insert(0, new_incident)
        st.session_state["incidents"] = incidents
        st.success("Incident created.")
        st.markdown(f"[Open incident](incident_detail?incident_id={new_id})")

st.page_link("main.py", label="Back to list")
