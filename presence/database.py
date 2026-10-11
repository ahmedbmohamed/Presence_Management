"""SQLite connection and schema."""

import sqlite3
from contextlib import contextmanager

from presence import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_photos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL REFERENCES users (username) ON DELETE CASCADE,
    photo_path    TEXT NOT NULL,
    face_encoding BLOB NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'approved', 'rejected')),
    uploaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at   TIMESTAMP,
    reviewed_by   TEXT
);

CREATE TABLE IF NOT EXISTS security_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    detail      TEXT,
    distance    REAL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def connect():
    """Yield a connection that commits on success and always closes."""
    config.ensure_dirs()
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
