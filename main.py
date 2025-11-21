import streamlit as st
import time
from db.db_functions_users_KT import create_tables, add_user, get_user_by_credentials, get_role_sortkey, register_main
from db.db_functions_trips import create_trip_table, create_trip_users_table

### basic page settings ###
st.set_page_config(page_title="Login", layout="centered", initial_sidebar_state="collapsed")
st.title("Login")

### create db and table if non-existent ###
create_tables()
create_trip_table()
create_trip_users_table()
### add dummies to user.db ###
add_user("Admin", "123", "a@gmail.com", "Administrator")
add_user("Manager", "123", "manager@gmail.com", "Manager")
add_user("User", "123", "user@gmail.com", "User")


### Login-inputs, with censored password ###
with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")


if submitted:
    result = get_user_by_credentials(username, password)
    if result:
        user_ID, username, role = result
        st.session_state["user_ID"] = user_ID
        st.session_state["username"] = username
        st.session_state["role"] = role
        role_sortkey = get_role_sortkey(role)
        st.session_state["role_sortkey"] =  role_sortkey
        st.success(f"Welcome {username}! 🎉 Role: {role}")
        time.sleep(1)
        if role == "Administrator":
            st.switch_page("pages/admin_overview.py")
        elif role == "Manager":
            st.switch_page("pages/manager_overview.py")
        else:
            st.switch_page("pages/user_overview.py")
    else:
        st.error("Wrong username or password.")

" "
" "
" "
" "
"""
Not registered yet? You can register as a manager and start planning your business-trips within your company, create a new account and start inviting your employees. Register now:"""
register_main()