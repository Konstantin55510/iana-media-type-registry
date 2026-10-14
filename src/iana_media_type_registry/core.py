"""
Core lookup and validation logic.

Design decisions
----------------
- ``MEDIA_TYPES`` keys use the canonical IANA form (lowercase ``type/subtype``).
  Media types are case-insensitive per RFC 2045 §2, so callers may pass any case;
  we normalise with ``str.lower`` before lookup. Keeping the stored keys lowercase
  avoids repeated normalisation and makes the data easy to audit.
- ``EXTENSION_TO_MEDIA_TYPES`` maps each extension to a *list* of media types,
  because some extensions are ambiguous (``.xml`` → ``text/xml`` *and*
  ``application/xml``). A list, even when it has one element, keeps the return
  shape uniform so callers never have to special-case single vs. multiple.
- ``is_valid_media_type`` does a structural check against the *bundled* registry,
  not a free-form RFC 2045 grammar check. The brief says "validates against the
  IANA registry"; a full grammar parser would accept types the registry does
  not contain, which is the opposite of what the function promises.
- Extensions are stored without the leading dot and in lowercase. Lookup
  normalises input the same way, so both ``"html"`` and ``".HTML"`` resolve.
"""

from typing import Dict, List, Optional, Tuple

#: Human-readable provenance string so users can audit which snapshot this is.
DATA_SOURCE: str = "static snapshot of common IANA-registered media types (2024-Q4 subset)"

#: Canonical media type records. Keys are lowercase ``type/subtype``.
#: The ``extensions`` list may be empty — some registered types (notably
#: ``application/octet-stream``) have no standard extension mapping.
MEDIA_TYPES: Dict[str, Dict[str, object]] = {
    "application/javascript": {
        "name": "JavaScript",
        "extensions": ["js", "mjs"],
        "deprecated": False,
        "template": None,
    },
    "application/json": {
        "name": "JSON",
        "extensions": ["json"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/application/json",
    },
    "application/octet-stream": {
        "name": "Octet-stream",
        "extensions": [],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/application/octet-stream",
    },
    "application/pdf": {
        "name": "PDF",
        "extensions": ["pdf"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/application/pdf",
    },
    "application/xml": {
        "name": "XML (application)",
        "extensions": ["xml"],
        "deprecated": True,
        "template": "https://www.iana.org/assignments/media-types/application/xml",
    },
    "application/zip": {
        "name": "Zip archive",
        "extensions": ["zip"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/application/zip",
    },
    "audio/mpeg": {
        "name": "MP3 audio",
        "extensions": ["mp3"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/audio/mpeg",
    },
    "audio/ogg": {
        "name": "Ogg audio",
        "extensions": ["ogg", "oga"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/audio/ogg",
    },
    "image/gif": {
        "name": "GIF image",
        "extensions": ["gif"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/image/gif",
    },
    "image/jpeg": {
        "name": "JPEG image",
        "extensions": ["jpg", "jpeg"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/image/jpeg",
    },
    "image/png": {
        "name": "PNG image",
        "extensions": ["png"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/image/png",
    },
    "image/svg+xml": {
        "name": "SVG image",
        "extensions": ["svg"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/image/svg+xml",
    },
    "image/webp": {
        "name": "WebP image",
        "extensions": ["webp"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/image/webp",
    },
    "text/css": {
        "name": "CSS stylesheet",
        "extensions": ["css"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/text/css",
    },
    "text/csv": {
        "name": "CSV (comma-separated values)",
        "extensions": ["csv"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/text/csv",
    },
    "text/html": {
        "name": "HTML",
        "extensions": ["html", "htm"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/text/html",
    },
    "text/plain": {
        "name": "Plain text",
        "extensions": ["txt", "text"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/text/plain",
    },
    "text/xml": {
        "name": "XML (text)",
        "extensions": ["xml"],
        "deprecated": True,
        "template": "https://www.iana.org/assignments/media-types/text/xml",
    },
    "video/mp4": {
        "name": "MP4 video",
        "extensions": ["mp4"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/video/mp4",
    },
    "video/webm": {
        "name": "WebM video",
        "extensions": ["webm"],
        "deprecated": False,
        "template": "https://www.iana.org/assignments/media-types/video/webm",
    },
}


def _build_extension_index() -> Dict[str, List[str]]:
    """Build a reverse index from extension (lowercase, no dot) to media types.

    The index is built once at import time and treated as read-only thereafter.
    Because extensions can map to more than one registered type, each value is
    a list; duplicates are avoided by checking membership before append.
    """
    index: Dict[str, List[str]] = {}
    for media_type, record in MEDIA_TYPES.items():
        for ext in record["extensions"]:  # type: ignore[union-attr]
            key = ext.lower()
            bucket = index.setdefault(key, [])
            if media_type not in bucket:
                bucket.append(media_type)
    return index


#: Reverse lookup table, built once at import. Read-only by convention.
EXTENSION_TO_MEDIA_TYPES: Dict[str, List[str]] = _build_extension_index()


def lookup_media_type(media_type: str) -> Optional[Dict[str, object]]:
    """Return the registry record for *media_type*, or ``None`` if not found.

    ``media_type`` is matched case-insensitively, matching RFC 2045 §2.
    The returned dict is the live record from :data:`MEDIA_TYPES`; mutating it
    will affect future lookups. Callers who need isolation should copy it.
    """
    if not isinstance(media_type, str) or not media_type:
        return None
    return MEDIA_TYPES.get(media_type.lower())


def lookup_by_extension(extension: str) -> List[str]:
    """Return the list of media types registered for *extension*.

    *extension* may be supplied with or without a leading dot and in any case
    (``"html"``, ``"HTML"``, ``".html"`` all resolve identically).

    Returns an empty list — never ``None`` — when the extension is unknown
    or the input is not a non-empty string. A consistent empty-list return
    keeps callers free of null checks.
    """
    if not isinstance(extension, str) or not extension:
        return []
    normalised = extension.lower()
    if normalised.startswith("."):
        normalised = normalised[1:]
    return list(EXTENSION_TO_MEDIA_TYPES.get(normalised, []))


def is_valid_media_type(media_type: str) -> bool:
    """Return ``True`` iff *media_type* is present in the bundled registry.

    This is a registry-membership check, not a free-form grammar check:
    ``application/vnd.example.thing`` is syntactically valid per RFC 6838 but
    will return ``False`` here unless it is in the bundled snapshot.
    Case-insensitive, per RFC 2045 §2.
    """
    return lookup_media_type(media_type) is not None
