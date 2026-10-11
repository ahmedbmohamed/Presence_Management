import streamlit as st

from presence import config, face, session, students

COLUMNS = 4


def roster_page() -> None:
    user = session.require_user()
    st.title("Students")

    if user.is_admin:
        _add_student_form()

    roster = students.list_students()
    if not roster:
        st.info("No students registered yet.")
        return

    st.caption(f"{len(roster)} student(s)")
    cols = st.columns(COLUMNS)
    for i, student in enumerate(roster):
        with cols[i % COLUMNS].container(border=True):
            st.image(str(student.photo), width="stretch")
            st.markdown(f"**{student.name}**")
            if user.is_admin and st.button(
                "Remove", key=f"remove_{student.name}", icon=":material/delete:", width="stretch"
            ):
                students.delete(student.name)
                st.toast(f"Removed {student.name}")
                st.rerun()


def _add_student_form() -> None:
    with st.expander("Add a student", icon=":material/person_add:"):
        name = st.text_input("Full name")
        upload_tab, camera_tab = st.tabs(["Upload", "Camera"])
        with upload_tab:
            uploaded = st.file_uploader("Photo", type=config.IMAGE_TYPES, key="student_upload")
        with camera_tab:
            captured = st.camera_input("Take a photo", key="student_camera")

        source = captured or uploaded
        if st.button("Add student", type="primary", disabled=source is None or not name):
            try:
                student = students.add(name, source.getvalue())
            except (ValueError, face.FaceError) as e:
                st.error(str(e))
                return
            st.toast(f"Added {student.name}")
            st.rerun()
