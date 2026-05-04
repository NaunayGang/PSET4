from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from data import (
    SEVERITIES,
    STATES,
    USERS,
    get_assignee_options,
    get_audit_logs,
    get_counts_by_severity,
    get_counts_by_state,
    get_critical_recent,
    get_incidents_by_day,
    get_incidents,
    get_unassigned,
    transition_incident,
)


st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("Admin Dashboard")

if "incidents" not in st.session_state:
    st.session_state["incidents"] = get_incidents()

incidents = st.session_state["incidents"]

current_role = st.session_state.get("active_role", "Operator")
is_admin = current_role == "Admin"
is_manager = current_role in ("Manager", "Admin")

if not is_manager:
    st.error("Access denied. Manager or Admin role required.")
    st.page_link("main.py", label="Back to list")
    st.stop()

auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)

if auto_refresh:
    import time
    time.sleep(30)

st.header("Overview")

severity_counts = get_counts_by_severity(incidents)
state_counts = get_counts_by_state(incidents)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Critical", severity_counts.get("critical", 0))
with col2:
    st.metric("High", severity_counts.get("high", 0))
with col3:
    st.metric("Medium", severity_counts.get("medium", 0))
with col4:
    st.metric("Low", severity_counts.get("low", 0))

st.header("State Distribution")
for state, count in state_counts.items():
    st.caption(f"{state}: {count}")

st.header("Critical Recent (24h)")
critical_recent = get_critical_recent(incidents, 24)
if critical_recent:
    for inc in critical_recent:
        st.write(f"- {inc['id']}: {inc['title']} ({inc['state']})")
else:
    st.info("No critical incidents in last 24 hours")

st.header("Unassigned Incidents")
unassigned = get_unassigned(incidents)
st.write(f"Total unassigned: {len(unassigned)}")

for inc in unassigned[:5]:
    st.write(f"- {inc['id']}: {inc['title']}")

if is_admin:
    st.divider()
    st.header("Admin Panel")

    tab1, tab2, tab3 = st.tabs(["Reassign", "Manage Users", "Audit Log"])

    with tab1:
        st.subheader("Reassign Incidents")
        unassign = get_unassigned(incidents)
        if unassign:
            assign_incident_id = st.selectbox(
                "Select incident",
                [i["id"] for i in unassign],
            )
            incident_map = {i["id"]: i for i in incidents}
            selected_incident = incident_map.get(assign_incident_id)
            if selected_incident:
                new_assignee = st.selectbox("Assign to", USERS)
                if st.button("Assign", key="reassign_btn"):
                    success, msg = transition_incident(
                        selected_incident,
                        None,
                        "Admin",
                        None,
                        None,
                        new_assignee,
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.info("No unassigned incidents")

    with tab2:
        st.subheader("Manage Users")
        st.write("Available users:", ", ".join(USERS))
        st.info("User management Coming Soon")

    with tab3:
        st.subheader("Audit Log")
        log_actor = st.selectbox("Filter by actor", [""] + USERS)
        log_type = st.selectbox("Filter by type", ["", "state", "severity", "assignment"])

        logs = get_audit_logs(
            incidents,
            actor_filter=log_actor if log_actor else None,
            type_filter=log_type if log_type else None,
        )

        st.write(f"Total entries: {len(logs)}")
        for log in logs[:20]:
            ts = log.get("timestamp")
            ts_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "N/A"
            st.write(f"- [{ts_str}] {log.get('type')}: {log.get('message')} (by {log.get('actor')})")

st.page_link("main.py", label="Back to list")