import streamlit as st

from presence import attendance, photos, security, session, students


def home_page() -> None:
    user = session.require_user()
    st.title(f"Hello, {user.username}")

    if user.is_admin:
        today = attendance.for_date(attendance.today())
        present = int((today["Status"] == attendance.PRESENT).sum())
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Students", len(students.names()))
        c2.metric("Present today", present)
        c3.metric("Photos to review", len(photos.pending()))
        c4.metric("Security alerts", security.count())
        st.info("Review new photos under **Photo review** and failed check-ins under **Security log**.")
        return

    latest = photos.latest(user.username)
    if latest is None:
        st.warning("You haven't added a reference photo yet. Open **My photo** to add one.")
    elif latest["status"] == "pending":
        st.info("Your photo is waiting for an administrator to approve it.")
    elif latest["status"] == "rejected" and photos.approved_encoding(user.username) is None:
        st.error("Your photo was rejected. Please submit a clearer one.")
    else:
        st.success("Your photo is approved. You can check in.")
