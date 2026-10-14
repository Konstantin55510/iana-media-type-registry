"""
Public API for iana-media-type-registry.

We re-export the lookup and validation functions from :mod:`core` so callers
can import directly from the package root::

    from iana_media_type_registry import lookup_by_extension, is_valid_media_type

The bundled data is static — a snapshot of common IANA-registered media types
with their file-extension mappings. ``DATA_SOURCE`` documents the registry version.
"""

from .core import (
    DATA_SOURCE,
    EXTENSION_TO_MEDIA_TYPES,
    MEDIA_TYPES,
    is_valid_media_type,
    lookup_by_extension,
    lookup_media_type,
)

__all__ = [
    "DATA_SOURCE",
    "EXTENSION_TO_MEDIA_TYPES",
    "MEDIA_TYPES",
    "is_valid_media_type",
    "lookup_by_extension",
    "lookup_media_type",
]
