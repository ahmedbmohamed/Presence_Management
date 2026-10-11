"""Class roster: one photo per student in the students folder."""

import re
from dataclasses import dataclass
from pathlib import Path

from presence import config, face

NAME_PATTERN = re.compile(r"^[\w .'-]{2,60}$")


@dataclass(frozen=True)
class Student:
    name: str
    photo: Path


def list_students() -> list[Student]:
    config.ensure_dirs()
    photos = sorted(config.STUDENTS_DIR.glob("*.jpg"), key=lambda p: p.stem.lower())
    return [Student(p.stem, p) for p in photos]


def names() -> list[str]:
    return [s.name for s in list_students()]


def add(name: str, data: bytes) -> Student:
    """Save a student photo after checking it contains exactly one face.

    Raises ValueError (or face.FaceError) when the name or photo is invalid.
    """
    name = " ".join(name.split()).title()
    if not NAME_PATTERN.match(name):
        raise ValueError("Enter a name of 2-60 letters, spaces, apostrophes or hyphens.")
    path = config.STUDENTS_DIR / f"{name}.jpg"
    if path.exists():
        raise ValueError(f"A student named '{name}' already exists.")

    image = face.load_image(data)
    face.encode_single_face(image)

    config.ensure_dirs()
    face.Image.fromarray(image).save(path, "JPEG", quality=90)
    return Student(name, path)


def delete(name: str) -> None:
    (config.STUDENTS_DIR / f"{name}.jpg").unlink(missing_ok=True)
