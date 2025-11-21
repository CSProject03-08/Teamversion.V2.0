import streamlit as st
import pandas as pd
from datetime import date

from db.db_functions_users import edit_own_profile
from db.db_functions_usertrips import get_user_trips

# --- Page setup ---
st.set_page_config(page_title="Employee Dashboard", layout="wide")
st.title("Employee Dashboard")

# --- Access control ---
if "role" not in st.session_state or st.session_state["role"] != "User":
    st.error("Access denied. Please log in as User.")
    st.stop()

# --- Layout ---
left, right = st.columns([4, 2], gap="large")

# -----------------------------
# LEFT: TRIP OVERVIEW
# -----------------------------
with left:
    st.subheader("Your Trips")

    user_id = st.session_state.get("user_ID", None)
    if user_id is None:
        st.warning("No user logged in. Please log in again.")
        st.stop()

    trips = get_user_trips(user_id)

    if trips is None or trips.empty:
        st.info("You have no trips assigned yet.")
    else:
        # normalise date columns
        trips["start_date"] = pd.to_datetime(trips["start_date"])
        trips["end_date"] = pd.to_datetime(trips["end_date"])

        st.markdown("### 📅 Filter by date range")
        date_range = st.date_input(
            "Select a date or range",
            value=(date.today(), date.today()),
            help="Pick one day or a range to filter your trips",
        )

        if isinstance(date_range, tuple):
            start, end = date_range
        else:
            start = end = date_range

        mask = (trips["start_date"] <= end) & (trips["end_date"] >= start)
        filtered = trips.loc[mask].sort_values("start_date", ascending=True)

        if filtered.empty:
            st.warning("No trips found for the selected date range.")
        else:
            st.dataframe(
                filtered[["trip_ID", "destination", "start_date", "end_date", "occasion"]],
                use_container_width=True,
                hide_index=True
            )

# -----------------------------
# RIGHT: PROFILE
# -----------------------------
with right:
    st.subheader("My Profile")
    edit_own_profile()
