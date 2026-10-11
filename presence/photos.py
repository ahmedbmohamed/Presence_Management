"""Reference photos that users submit and admins approve."""

import sqlite3
from datetime import datetime
from pathlib import Path

import numpy as np

from presence import config, face
from presence.database import connect


def submit(username: str, data: bytes) -> None:
    """Validate that the image holds exactly one face, save it and queue it for review.

    Raises face.FaceError if the image is unusable.
    """
    image = face.load_image(data)
    encoding, _ = face.encode_single_face(image)

    config.ensure_dirs()
    path = config.USER_PHOTOS_DIR / f"{username}_{datetime.now():%Y%m%d_%H%M%S_%f}.jpg"
    face.Image.fromarray(image).save(path, "JPEG", quality=90)

    with connect() as conn:
        # A new submission replaces any photo still waiting for review.
        replaced = conn.execute(
            "DELETE FROM user_photos WHERE username = ? AND status = 'pending' "
            "RETURNING photo_path",
            (username,),
        ).fetchall()
        for row in replaced:
            Path(row["photo_path"]).unlink(missing_ok=True)
        conn.execute(
            "INSERT INTO user_photos (username, photo_path, face_encoding) VALUES (?, ?, ?)",
            (username, str(path), face.to_bytes(encoding)),
        )


def latest(username: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM user_photos WHERE username = ? ORDER BY id DESC LIMIT 1",
            (username,),
        ).fetchone()


def approved_encoding(username: str) -> np.ndarray | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT face_encoding FROM user_photos WHERE username = ? AND status = 'approved' "
            "ORDER BY reviewed_at DESC, id DESC LIMIT 1",
            (username,),
        ).fetchone()
    return face.from_bytes(row["face_encoding"]) if row else None


def pending() -> list[sqlite3.Row]:
    with connect() as conn:
        return conn.execute(
            "SELECT id, username, photo_path, uploaded_at FROM user_photos "
            "WHERE status = 'pending' ORDER BY uploaded_at"
        ).fetchall()


def review(photo_id: int, reviewer: str, approve: bool) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE user_photos SET status = ?, reviewed_at = CURRENT_TIMESTAMP, reviewed_by = ? "
            "WHERE id = ?",
            ("approved" if approve else "rejected", reviewer, photo_id),
        )


def approved_user_count() -> int:
    with connect() as conn:
        return conn.execute(
            "SELECT COUNT(DISTINCT username) FROM user_photos WHERE status = 'approved'"
        ).fetchone()[0]


def delete_files_for(username: str) -> None:
    with connect() as conn:
        rows = conn.execute(
            "SELECT photo_path FROM user_photos WHERE username = ?", (username,)
        ).fetchall()
    for row in rows:
        Path(row["photo_path"]).unlink(missing_ok=True)
