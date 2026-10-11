import pytest
from conftest import make_image

from presence import auth, face, photos, students


@pytest.fixture
def alice():
    return auth.create_user("alice", "password123")


def test_photo_without_face_is_rejected(alice):
    with pytest.raises(face.FaceError):
        photos.submit("alice", make_image(0))
    assert photos.latest("alice") is None


def test_approval_flow_and_matching(alice):
    photos.submit("alice", make_image(120))
    assert photos.approved_encoding("alice") is None

    (pending,) = photos.pending()
    photos.review(pending["id"], "admin", approve=True)

    known = photos.approved_encoding("alice")
    assert face.match(known, face.load_image(make_image(121))).matched
    assert not face.match(known, face.load_image(make_image(250))).matched


def test_resubmitting_replaces_pending_photo(alice, data_dir):
    photos.submit("alice", make_image(100))
    photos.submit("alice", make_image(110))
    assert len(photos.pending()) == 1
    assert len(list((data_dir / "user_photos").iterdir())) == 1


def test_student_needs_a_face_and_unique_name():
    with pytest.raises(face.FaceError):
        students.add("Ada", make_image(0))
    students.add("Ada", make_image(120))
    with pytest.raises(ValueError, match="already exists"):
        students.add("ada", make_image(120))
