import io
import sys
import types

import numpy as np
import pytest
from PIL import Image

from presence import config, database


def _fake_face_recognition() -> types.ModuleType:
    """Stand-in for face_recognition so tests run without dlib.

    A black image has no face; any other image has one face whose encoding
    is derived from its mean brightness, so similar images match.
    """
    fr = types.ModuleType("face_recognition")

    def face_locations(image):
        return [] if image.max() == 0 else [(10, 60, 60, 10)]

    def face_encodings(image, locations=None):
        return [np.full(128, image.mean() / 255.0)]

    def face_distance(known, encoding):
        return np.linalg.norm(np.asarray(known) - encoding, axis=1)

    fr.face_locations = face_locations
    fr.face_encodings = face_encodings
    fr.face_distance = face_distance
    return fr


sys.modules["face_recognition"] = _fake_face_recognition()


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "presence.db")
    monkeypatch.setattr(config, "ATTENDANCE_CSV", tmp_path / "attendance.csv")
    monkeypatch.setattr(config, "STUDENTS_DIR", tmp_path / "students")
    monkeypatch.setattr(config, "USER_PHOTOS_DIR", tmp_path / "user_photos")
    monkeypatch.setattr(config, "PASSWORD_ITERATIONS", 1_000)  # keep tests fast
    database.init_db()
    return tmp_path


def make_image(brightness: int) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (80, 80), (brightness,) * 3).save(buffer, "JPEG")
    return buffer.getvalue()
