"""Face detection, encoding and matching."""

import io
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

from presence import config

Location = tuple[int, int, int, int]  # top, right, bottom, left


class FaceError(ValueError):
    """Raised when an image does not contain exactly one usable face."""


@dataclass(frozen=True)
class MatchResult:
    matched: bool
    distance: float
    location: Location


def _fr():
    # Imported lazily: dlib is slow to load and not needed by the rest of the app.
    import face_recognition

    return face_recognition


def load_image(data: bytes) -> np.ndarray:
    """Decode image bytes into an RGB array."""
    return np.array(Image.open(io.BytesIO(data)).convert("RGB"))


def encode_single_face(image: np.ndarray) -> tuple[np.ndarray, Location]:
    fr = _fr()
    locations = fr.face_locations(image)
    if not locations:
        raise FaceError("No face detected. Use a well-lit, front-facing photo.")
    if len(locations) > 1:
        raise FaceError("More than one face detected. Only you should be in the photo.")
    encodings = fr.face_encodings(image, locations)
    if not encodings:
        raise FaceError("The face could not be encoded. Try another photo.")
    return encodings[0], locations[0]


def match(known: np.ndarray, image: np.ndarray) -> MatchResult:
    encoding, location = encode_single_face(image)
    distance = float(_fr().face_distance([known], encoding)[0])
    return MatchResult(distance <= config.FACE_MATCH_TOLERANCE, distance, location)


def to_bytes(encoding: np.ndarray) -> bytes:
    return encoding.astype(np.float64).tobytes()


def from_bytes(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float64)


def annotate(image: np.ndarray, location: Location, label: str, ok: bool) -> Image.Image:
    """Draw a labelled box around the face."""
    top, right, bottom, left = location
    color = (34, 197, 94) if ok else (239, 68, 68)
    picture = Image.fromarray(image)
    draw = ImageDraw.Draw(picture)
    draw.rectangle((left, top, right, bottom), outline=color, width=3)
    draw.rectangle((left, bottom, right, bottom + 24), fill=color)
    draw.text((left + 6, bottom + 5), label, fill=(255, 255, 255))
    return picture
