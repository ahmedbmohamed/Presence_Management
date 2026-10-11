import streamlit as st

from presence import attendance, face, photos, security, session


def check_in_page() -> None:
    user = session.require_user()
    st.title("Check in")

    known = photos.approved_encoding(user.username)
    if known is None:
        st.warning("You need an approved reference photo before you can check in.")
        return

    st.write("Look at the camera and take a picture. Your face is compared to your approved photo.")
    shot = st.camera_input("Camera", label_visibility="collapsed")
    if shot is None:
        return

    image = face.load_image(shot.getvalue())
    with st.spinner("Verifying..."):
        try:
            result = face.match(known, image)
        except face.FaceError as e:
            st.error(str(e))
            return

    if not result.matched:
        security.log_event(
            user.username,
            security.FACE_MISMATCH,
            "Live face did not match the approved photo.",
            result.distance,
        )
        st.image(face.annotate(image, result.location, "NOT VERIFIED", ok=False))
        st.error("Your face did not match your approved photo. This attempt has been logged.")
        return

    st.image(face.annotate(image, result.location, user.username, ok=True))
    time, newly = attendance.mark_present(user.username)
    if newly:
        st.success(f"Checked in at {time}.")
        st.balloons()
    else:
        st.info(f"You already checked in today at {time}.")
