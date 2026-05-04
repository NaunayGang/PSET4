from __future__ import annotations

import streamlit as st

from data import (
    get_counts_by_severity,
    get_counts_by_state,
    get_critical_recent,
    get_incidents_by_day,
    get_incidents,
    get_unassigned,
)


st.set_page_config(page_title="Manager Dashboard", layout="wide")

st.title("Manager Dashboard")

if "incidents" not in st.session_state:
    st.session_state["incidents"] = get_incidents()

incidents = st.session_state["incidents"]

current_role = st.session_state.get("active_role", "Operator")
is_manager = current_role in ("Manager", "Admin")

if not is_manager:
    st.error("Access denied. Manager or Admin role required.")
    st.page_link("main.py", label="Back to list")
    st.stop()


def render_auto_refresh(interval_seconds: int = 30):
    st.markdown(
        f"""
        <meta http-equiv="refresh" content="{interval_seconds}">
        <script>
            setTimeout(function(){{
                window.location.reload();
            }}, {interval_seconds * 1000});
        </script>
        """,
        unsafe_allow_html=True,
    )


auto_refresh = st.checkbox("Auto-refresh (30s)", value=False, key="mgr_refresh")

if auto_refresh:
    render_auto_refresh(30)


st.header("Metrics")

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
state_cols = st.columns(len(st.session_state.get("states", ["open", "triaged", "assigned", "in_progress", "resolved", "closed"])))
state_list = ["open", "triaged", "assigned", "in_progress", "resolved", "closed"]
for idx, state in enumerate(state_list):
    with state_cols[idx]:
        st.metric(state.title().replace("_", " "), state_counts.get(state, 0))

st.header("Critical Recent (24h)")
critical_recent = get_critical_recent(incidents, 24)
if critical_recent:
    for inc in critical_recent:
        with st.container(border=True):
            st.write(f"**{inc['id']}**: {inc['title']}")
            st.caption(f"State: {inc['state']} | Severity: {inc['severity']}")
else:
    st.info("No critical incidents in last 24 hours")

st.header("Unassigned")
unassigned = get_unassigned(incidents)
st.write(f"Total: {len(unassigned)}")

if unassigned:
    for inc in unassigned:
        with st.container(border=True):
            st.write(f"**{inc['id']}**: {inc['title']}")
            st.caption(f"Severity: {inc['severity']}")

st.header("Incidents by Day (Last 7 days)")
by_day = get_incidents_by_day(incidents, 7)
for day, count in sorted(by_day.items()):
    st.write(f"{day}: {count} incidents")

st.caption("*Manager view is read-only*")

st.page_link("main.py", label="Back to list")