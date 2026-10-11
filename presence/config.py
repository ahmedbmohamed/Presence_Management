"""Paths and settings. Override the data location with the PRESENCE_DATA_DIR env var."""

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("PRESENCE_DATA_DIR", ROOT_DIR / "data"))

DB_PATH = DATA_DIR / "presence.db"
ATTENDANCE_CSV = DATA_DIR / "attendance.csv"
STUDENTS_DIR = DATA_DIR / "students"
USER_PHOTOS_DIR = DATA_DIR / "user_photos"

# Max face distance accepted as a match (lower = stricter). 0.6 is the library default.
FACE_MATCH_TOLERANCE = 0.5

PASSWORD_ITERATIONS = 310_000
MIN_PASSWORD_LENGTH = 8

IMAGE_TYPES = ["jpg", "jpeg", "png"]


def ensure_dirs() -> None:
    for directory in (DATA_DIR, STUDENTS_DIR, USER_PHOTOS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
