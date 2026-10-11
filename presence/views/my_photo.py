import streamlit as st

from presence import config, face, photos, session


def my_photo_page() -> None:
    user = session.require_user()
    st.title("My photo")

    latest = photos.latest(user.username)
    if latest is None:
        st.info("No photo yet. Add one below, then an administrator will review it.")
    else:
        col_img, col_info = st.columns([1, 2])
        col_img.image(latest["photo_path"], width=220)
        status = latest["status"]
        if status == "pending":
            col_info.warning(f"Waiting for review (submitted {latest['uploaded_at']}).")
        elif status == "approved":
            col_info.success(f"Approved by {latest['reviewed_by']} on {latest['reviewed_at']}.")
        else:
            col_info.error(f"Rejected by {latest['reviewed_by']}. Please submit a new photo.")

    st.divider()
    st.subheader("Submit a new photo")
    st.caption("Use a clear, front-facing photo with only your face in it.")

    upload_tab, camera_tab = st.tabs(["Upload", "Camera"])
    with upload_tab:
        uploaded = st.file_uploader("Photo", type=config.IMAGE_TYPES)
    with camera_tab:
        captured = st.camera_input("Take a photo")

    source = captured or uploaded
    if source is not None and st.button("Submit for review", type="primary"):
        try:
            photos.submit(user.username, source.getvalue())
        except face.FaceError as e:
            st.error(str(e))
            return
        st.success("Photo submitted. An administrator will review it.")
        st.rerun()
