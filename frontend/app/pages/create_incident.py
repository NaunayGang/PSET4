from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from data import (
    SEVERITIES,
    get_incidents,
    show_toast,
    validate_required,
    validate_selection,
)


st.set_page_config(page_title="Create Incident", layout="wide")

st.title("Create incident")

if "incidents" not in st.session_state:
    st.session_state["incidents"] = get_incidents()

incidents = st.session_state["incidents"]

with st.form("create_incident_form", clear_on_submit=True):
    title = st.text_input("Title", placeholder="Enter incident title")
    title_error = st.empty()
    
    description = st.text_area("Description", height=140, placeholder="Describe the incident")
    description_error = st.empty()
    
    severity = st.selectbox("Severity", SEVERITIES, index=None, placeholder="Select severity")
    severity_error = st.empty()
    
    st.caption("* All fields are required")
    submitted = st.form_submit_button("Create", type="primary")

if submitted:
    errors = []
    
    valid, msg = validate_required(title, "Title")
    if not valid:
        errors.append(msg)
        title_error.error(msg)
    
    valid, msg = validate_required(description, "Description")
    if not valid:
        errors.append(msg)
        description_error.error(msg)
    
    valid, msg = validate_selection(severity, "Severity")
    if not valid:
        errors.append(msg)
        severity_error.error(msg)

    if errors:
        show_toast("Please fix the errors above", "error")
    else:
        with st.spinner("Creating incident..."):
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
        
        show_toast(f"Incident {new_id} created successfully!", "success")
        st.success(f"Incident created with ID: {new_id}")
        st.markdown(f"[Open incident](incident_detail?incident_id={new_id})")

st.page_link("main.py", label="Back to list")