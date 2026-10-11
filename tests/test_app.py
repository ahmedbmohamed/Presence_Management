"""End-to-end checks of the Streamlit app using Streamlit's AppTest."""

from pathlib import Path

import pytest

from streamlit.testing.v1 import AppTest

from presence import auth

MAIN = str(Path(__file__).resolve().parent.parent / "main.py")


def run_app() -> AppTest:
    return AppTest.from_file(MAIN, default_timeout=30).run()


def test_first_run_shows_admin_setup_and_creates_admin():
    at = run_app()
    assert not at.exception
    assert at.title[0].value == "Welcome"

    at.text_input[0].input("boss")
    at.text_input[1].input("password123")
    at.text_input[2].input("password123")
    at.button[0].click().run()

    assert not at.exception
    assert auth.authenticate("boss", "password123").is_admin
    assert at.title[0].value == "Hello, boss"


def test_login_with_wrong_password_shows_error():
    auth.create_user("alice", "password123")
    at = run_app()
    at.text_input[0].input("alice")
    at.text_input[1].input("wrong-password")
    at.button[0].click().run()
    assert at.error[0].value == "Incorrect username or password."


def test_user_login_shows_home_without_admin_pages():
    auth.create_user("alice", "password123")
    at = run_app()
    at.text_input[0].input("alice")
    at.text_input[1].input("password123")
    at.button[0].click().run()

    assert not at.exception
    assert at.title[0].value == "Hello, alice"
    assert "reference photo" in at.warning[0].value


PAGES = {
    "home": "home.home_page",
    "check_in": "check_in.check_in_page",
    "my_photo": "my_photo.my_photo_page",
    "history": "history.history_page",
    "roster": "roster.roster_page",
    "photo_review": "admin.photo_review_page",
    "security_log": "admin.security_log_page",
    "users": "admin.users_page",
}


@pytest.mark.parametrize("role", ["admin", "user"])
@pytest.mark.parametrize("page", PAGES.values(), ids=PAGES.keys())
def test_every_page_renders(page, role):
    from conftest import make_image
    from presence import attendance, photos, security, students

    user = auth.create_user("alice", "password123", role)
    students.add("Ada Lovelace", make_image(120))
    photos.submit("alice", make_image(120))
    attendance.mark_present("alice")
    security.log_event("alice", security.FACE_MISMATCH, "test", 0.7)

    module = page.split(".")[0]
    at = AppTest.from_string(
        f"from presence.views import {module}\n{page}()\n", default_timeout=30
    )
    at.session_state["user"] = user
    at.run()
    assert not at.exception, at.exception
