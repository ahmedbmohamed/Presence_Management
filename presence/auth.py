"""User accounts and password hashing (PBKDF2-SHA256 with a per-user salt)."""

import hashlib
import hmac
import re
import secrets
import sqlite3
from dataclasses import dataclass

from presence import config
from presence.database import connect

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")


@dataclass(frozen=True)
class User:
    username: str
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), config.PASSWORD_ITERATIONS
    )
    return f"pbkdf2_sha256${config.PASSWORD_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), int(iterations)
    )
    return hmac.compare_digest(digest.hex(), expected)


def validate_new_account(username: str, password: str) -> str | None:
    """Return an error message, or None if the credentials are acceptable."""
    if not USERNAME_PATTERN.match(username):
        return "Username must be 3-32 characters: letters, digits, '.', '_' or '-'."
    if len(password) < config.MIN_PASSWORD_LENGTH:
        return f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters."
    return None


def create_user(username: str, password: str, role: str = "user") -> User:
    error = validate_new_account(username, password)
    if error:
        raise ValueError(error)
    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hash_password(password), role),
            )
    except sqlite3.IntegrityError:
        raise ValueError(f"User '{username}' already exists.") from None
    return User(username, role)


def authenticate(username: str, password: str) -> User | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row and verify_password(password, row["password_hash"]):
        return User(row["username"], row["role"])
    return None


def has_any_user() -> bool:
    with connect() as conn:
        return conn.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None


def list_users() -> list[sqlite3.Row]:
    with connect() as conn:
        return conn.execute(
            "SELECT username, role, created_at FROM users ORDER BY username"
        ).fetchall()


def delete_user(username: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
