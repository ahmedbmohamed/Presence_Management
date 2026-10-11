import streamlit as st

from presence import auth, session


def _centered():
    return st.columns([1, 2, 1])[1]


def setup_page() -> None:
    """Shown once, when the database has no accounts yet."""
    with _centered():
        st.title("Welcome")
        st.write("No accounts exist yet. Create the administrator account to get started.")
        with st.form("setup"):
            username = st.text_input("Admin username")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Create admin account", type="primary", width="stretch"):
                if password != confirm:
                    st.error("Passwords do not match.")
                    return
                try:
                    user = auth.create_user(username.strip(), password, role="admin")
                except ValueError as e:
                    st.error(str(e))
                    return
                session.log_in(user)
                st.rerun()


def login_page() -> None:
    with _centered():
        st.title("Attendance")
        st.caption("Sign in to continue")
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", type="primary", width="stretch"):
                user = auth.authenticate(username.strip(), password)
                if user is None:
                    st.error("Incorrect username or password.")
                else:
                    session.log_in(user)
                    st.rerun()
