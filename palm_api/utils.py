"""Small standalone helpers used across the package."""
from __future__ import annotations

import hashlib

# Phrases the vision model uses when the image is not a readable palm.
# If any of these appears in the analysis output we treat it as "no palm"
# and short-circuit the endpoint with a 400.
_NO_PALM_MARKERS = (
    "have not provided", "haven't provided", "has not provided",
    "did not provide", "didn't provide", "not provided an",
    "cannot see", "can't see", "unable to see",
    "cannot perform", "can't perform",
    "actual palm image", "actual photograph of a palm",
    "actual image of a human palm", "image of a palm",
    "please upload", "please provide",
    "no palm", "not a palm", "isn't a palm",
)


def get_image_hash(image_bytes: bytes) -> str:
    """Stable per-image identifier used for record IDs and fallback seeding."""
    return hashlib.md5(image_bytes).hexdigest()


def no_palm_detected(reading: str) -> bool:
    """True if `reading` looks like a refusal rather than an actual palm reading."""
    low = reading.lower()
    return any(marker in low for marker in _NO_PALM_MARKERS)
