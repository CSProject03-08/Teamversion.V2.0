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

# --- LEFT COLUMN: Trip Overview ---
with left:
    st.subheader("Trip Overview")

    user_id = st.session_state.get("user_id", None)
    if user_id is None:
        st.warning("No user logged in. Please log in first.")
        st.stop()

    # Fetch trips from the DB
    trips = get_user_trips(user_id)

    if trips is None or trips.empty:
        st.info("You have no trips recorded yet.")
    else:
        trips["date_start"] = pd.to_datetime(trips["date_start"])
        trips["date_end"] = pd.to_datetime(trips["date_end"])

        # --- Calendar filter ---
        st.markdown("### 📅 Filter trips by date range")
        date_range = st.date_input(
            "Select a date or range",
            value=(date.today(), date.today()),
            help="Pick one day or a range to see matching trips",
        )

        # Handle single vs range selection
        if isinstance(date_range, tuple):
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range

        # Filter trips that overlap with the chosen date(s)
        mask = (trips["date_start"] <= end_date) & (trips["date_end"] >= start_date)
        filtered = trips.loc[mask].sort_values("date_start", ascending=False)

        if filtered.empty:
            st.warning("No trips found for the selected date(s).")
        else:
            st.dataframe(
                filtered[["destination", "date_start", "date_end", "budget", "status"]],
                use_container_width=True,
                hide_index=True
            )
    
    # keep your table setup
    ensure_table()

      # single-button entry point to the expense wizard
    if "show_expense_form" not in st.session_state:
        st.session_state.show_expense_form = False

    if not st.session_state.show_expense_form:
        st.button("➕ Expense (past business trip)", type="primary", use_container_width=True,
                  on_click=lambda: st.session_state.update(show_expense_form=True))
    else:
        # Popup content (inline view switch)
        st.markdown("### Add business trip expense")
        cols_hdr = st.columns([1, 1])
        with cols_hdr[0]:
            st.write("Please fill each category, upload receipts and review everything before saving.")
        with cols_hdr[1]:
            st.button("✖ Close", use_container_width=True,
                      on_click=lambda: st.session_state.update(show_expense_form=False))

        # Wizard state
        if "expense_wizard" not in st.session_state:
            st.session_state.expense_wizard = {
                "step": 1,
                "hotel_cost": 0.0, "hotel_files": [],
                "transport_cost": 0.0, "transport_files": [],
                "meals_cost": 0.0, "meals_files": [],
                "other_cost": 0.0, "other_files": [],
            }
        wiz = st.session_state.expense_wizard

        # Common trip fields (set once)
        date = st.date_input("Trip date")
        dest_city = st.selectbox(
            "Destination city",
            ["Zurich","Geneva","Basel","Bern","Lausanne","Lugano","Lucerne"]
        )
        duration_days = st.number_input("Duration (days)", min_value=0.0, step=0.5)

        step = wiz["step"]
        st.markdown(f"#### Expense {step} of 5")

        def _next(): wiz.update(step=min(5, step + 1))
        def _back(): wiz.update(step=max(1, step - 1))

        # Step 1: Hotel
        if step == 1:
            wiz["hotel_cost"] = st.number_input(
                "Total hotel cost (CHF)", min_value=0.0, step=10.0, value=float(wiz["hotel_cost"])
            )
            wiz["hotel_files"] = st.file_uploader(
                "📎 Upload hotel receipts (PDF or image)",
                type=["pdf","png","jpg","jpeg"], accept_multiple_files=True, key="hotel_files_upl"
            )
            st.button("Next →", type="primary", on_click=_next)

        # ---------- Step 2: Transportation ----------
        elif step == 2:
            wiz["transport_cost"] = st.number_input(
                "Total transportation cost (CHF)", min_value=0.0, step=10.0, value=float(wiz["transport_cost"])
            )
            wiz["transport_files"] = st.file_uploader(
                "📎 Upload transportation receipts (PDF or image)",
                type=["pdf","png","jpg","jpeg"], accept_multiple_files=True, key="transport_files_upl"
            )
            c1, c2 = st.columns(2)
            with c1: st.button("← Back", on_click=_back, use_container_width=True)
            with c2: st.button("Next →", type="primary", on_click=_next, use_container_width=True)

        # ---------- Step 3: Meals ----------
        elif step == 3:
            wiz["meals_cost"] = st.number_input(
                "Total meals cost (CHF)", min_value=0.0, step=5.0, value=float(wiz["meals_cost"])
            )
            wiz["meals_files"] = st.file_uploader(
                "📎 Upload meal receipts (PDF or image)",
                type=["pdf","png","jpg","jpeg"], accept_multiple_files=True, key="meals_files_upl"
            )
            c1, c2 = st.columns(2)
            with c1: st.button("← Back", on_click=_back, use_container_width=True)
            with c2: st.button("Next →", type="primary", on_click=_next, use_container_width=True)

        # ---------- Step 4: Other ----------
        elif step == 4:
            wiz["other_cost"] = st.number_input(
                "Other costs (CHF)", min_value=0.0, step=5.0, value=float(wiz["other_cost"])
            )
            wiz["other_files"] = st.file_uploader(
                "📎 Upload other receipts (PDF or image)",
                type=["pdf","png","jpg","jpeg"], accept_multiple_files=True, key="other_files_upl"
            )
            c1, c2 = st.columns(2)
            with c1: st.button("← Back", on_click=_back, use_container_width=True)
            with c2: st.button("Next →", type="primary", on_click=_next, use_container_width=True)

        # ---------- Step 5: Review & Save ----------
        elif step == 5:
            total_cost = float(
                wiz["hotel_cost"] + wiz["transport_cost"] + wiz["meals_cost"] + wiz["other_cost"]
            )
            st.subheader("Review")
            st.write(
                f"- **Hotel:** CHF {wiz['hotel_cost']:,.2f} ({len(wiz['hotel_files'] or [])} file(s))\n"
                f"- **Transportation:** CHF {wiz['transport_cost']:,.2f} ({len(wiz['transport_files'] or [])} file(s))\n"
                f"- **Meals:** CHF {wiz['meals_cost']:,.2f} ({len(wiz['meals_files'] or [])} file(s))\n"
                f"- **Other:** CHF {wiz['other_cost']:,.2f} ({len(wiz['other_files'] or [])} file(s))\n"
            )
            st.markdown(f"**Calculated total (CHF):** {total_cost:,.2f}")

            c1, c2 = st.columns(2)
            with c1:
                st.button("← Back", on_click=_back, use_container_width=True)
            with c2:
                if st.button("Save & Retrain", type="primary", use_container_width=True):
                    # TODO: Persist to DB and store uploaded files per category
                    # save_expense(date, dest_city, duration_days, wiz, total_cost)
                    # for category, files in [("hotel", wiz["hotel_files"]), ("transport", wiz["transport_files"]),
                    #                         ("meals", wiz["meals_files"]), ("other", wiz["other_files"])]:
                    #     for f in files or []:
                    #         save_file_to_storage(expense_id, category, f.name, f.getbuffer())

                    st.success("Expense saved and model retrained.")
                    # Reset and close the panel
                    st.session_state.expense_wizard = {
                        "step": 1,
                        "hotel_cost": 0.0, "hotel_files": [],
                        "transport_cost": 0.0, "transport_files": [],
                        "meals_cost": 0.0, "meals_files": [],
                        "other_cost": 0.0, "other_files": [],
                    }
                    st.session_state.show_expense_form = False
                    st.rerun()

# --- RIGHT COLUMN: Edit Profile ---
with right:
    edit_own_profile()
