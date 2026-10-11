"""Logged-in user stored in Streamlit's session state."""

import streamlit as st

from presence.auth import User

_KEY = "user"


def current_user() -> User | None:
    return st.session_state.get(_KEY)


def require_user() -> User:
    user = current_user()
    if user is None:
        st.stop()
    return user


def log_in(user: User) -> None:
    st.session_state[_KEY] = user


def log_out() -> None:
    st.session_state.clear()
