"""Log of failed face verifications."""

import sqlite3

from presence.database import connect

FACE_MISMATCH = "face_mismatch"


def log_event(username: str, event_type: str, detail: str, distance: float | None = None) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO security_events (username, event_type, detail, distance) "
            "VALUES (?, ?, ?, ?)",
            (username, event_type, detail, distance),
        )


def list_events() -> list[sqlite3.Row]:
    with connect() as conn:
        return conn.execute(
            "SELECT id, username, event_type, detail, distance, created_at "
            "FROM security_events ORDER BY id DESC"
        ).fetchall()


def count() -> int:
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM security_events").fetchone()[0]
