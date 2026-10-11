"""Admin-only pages: photo review, security log and account management."""

from pathlib import Path

import pandas as pd
import streamlit as st

from presence import auth, photos, security, session


def photo_review_page() -> None:
    admin = session.require_user()
    st.title("Photo review")

    queue = photos.pending()
    if not queue:
        st.success("Nothing to review.")
        return

    st.caption(f"{len(queue)} photo(s) waiting")
    for photo in queue:
        with st.container(border=True):
            col_img, col_info = st.columns([1, 2])
            if Path(photo["photo_path"]).exists():
                col_img.image(photo["photo_path"], width=200)
            else:
                col_img.error("File missing")
            col_info.markdown(f"### {photo['username']}")
            col_info.caption(f"Submitted {photo['uploaded_at']}")
            approve, reject = col_info.columns(2)
            if approve.button("Approve", key=f"approve_{photo['id']}", type="primary",
                              icon=":material/check:", width="stretch"):
                photos.review(photo["id"], admin.username, approve=True)
                st.rerun()
            if reject.button("Reject", key=f"reject_{photo['id']}",
                             icon=":material/close:", width="stretch"):
                photos.review(photo["id"], admin.username, approve=False)
                st.rerun()


def security_log_page() -> None:
    st.title("Security log")
    st.caption("Check-ins where the live face did not match the user's approved photo.")

    events = security.list_events()
    if not events:
        st.success("No security events.")
        return

    df = pd.DataFrame([dict(e) for e in events]).rename(columns={
        "created_at": "When", "username": "User", "event_type": "Type",
        "detail": "Detail", "distance": "Face distance",
    })
    st.dataframe(
        df[["When", "User", "Type", "Face distance", "Detail"]],
        hide_index=True,
        width="stretch",
        column_config={"Face distance": st.column_config.NumberColumn(format="%.3f")},
    )


def users_page() -> None:
    admin = session.require_user()
    st.title("Users")

    with st.expander("Create an account", icon=":material/person_add:"):
        with st.form("new_user", clear_on_submit=True):
            username = st.text_input("Username")
            password = st.text_input("Temporary password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            if st.form_submit_button("Create", type="primary"):
                try:
                    auth.create_user(username.strip(), password, role)
                    st.toast(f"Created {username}")
                except ValueError as e:
                    st.error(str(e))

    for row in auth.list_users():
        with st.container(border=True):
            name, role, action = st.columns([3, 1, 1], vertical_alignment="center")
            name.markdown(f"**{row['username']}**  \n:gray[since {row['created_at'][:10]}]")
            role.markdown(f":{'orange' if row['role'] == 'admin' else 'blue'}-badge[{row['role']}]")
            if row["username"] != admin.username and action.button(
                "Delete", key=f"del_{row['username']}", icon=":material/delete:"
            ):
                photos.delete_files_for(row["username"])
                auth.delete_user(row["username"])
                st.rerun()
