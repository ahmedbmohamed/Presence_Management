"""Entry point: `streamlit run main.py`."""

import streamlit as st

from presence import attendance, auth, database, session
from presence.views import admin, check_in, history, home, login, my_photo, roster

st.set_page_config(page_title="Attendance", page_icon=":material/how_to_reg:", layout="wide")
database.init_db()


def _page(func, title, icon, default=False):
    return st.Page(func, title=title, icon=f":material/{icon}:", url_path=func.__name__,
                   default=default)


def _navigation(user: auth.User | None):
    if user is None:
        entry = login.login_page if auth.has_any_user() else login.setup_page
        return st.navigation([_page(entry, "Sign in", "login", default=True)], position="hidden")

    pages = {
        "": [
            _page(home.home_page, "Home", "home", default=True),
            _page(check_in.check_in_page, "Check in", "how_to_reg"),
            _page(my_photo.my_photo_page, "My photo", "account_box"),
            _page(history.history_page, "Attendance history", "calendar_month"),
            _page(roster.roster_page, "Students", "groups"),
        ]
    }
    if user.is_admin:
        pages["Admin"] = [
            _page(admin.photo_review_page, "Photo review", "fact_check"),
            _page(admin.security_log_page, "Security log", "shield"),
            _page(admin.users_page, "Users", "manage_accounts"),
        ]
    return st.navigation(pages)


def _sidebar(user: auth.User) -> None:
    with st.sidebar:
        st.markdown(f"Signed in as **{user.username}**")
        if user.is_admin:
            st.badge("admin", color="orange")
        if st.button("Sign out", icon=":material/logout:", width="stretch"):
            session.log_out()
            st.rerun()


user = session.current_user()
if user is not None:
    attendance.open_today()
    _sidebar(user)
_navigation(user).run()
