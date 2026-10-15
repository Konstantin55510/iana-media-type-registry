# iana-media-type-registry

Looks up and validates media types against the IANA registry, with file-extension mappings bundled as static data.

```python
from iana_media_type_registry import lookup_by_extension, is_valid_media_type

print(lookup_by_extension(".json"))   # ['application/json']
print(is_valid_media_type("text/html")) # True
print(is_valid_media_type("application/vnd.example.thing"))  # False
```

## Why this exists

The IANA media type registry is large, periodically updated, and not available as a tidy offline package. This library ships a static snapshot of common, widely-used media types with their extension mappings, so dependency-free validation and lookup work in environments with no network access.

The trade-off: the snapshot is not exhaustive. Niche vendor types (``application/vnd.*``) and rarely-used subtypes are deliberately omitted to keep the data auditable and the package small. ``is_valid_media_type`` checks membership in this snapshot, not free-form RFC 6838 grammar — a type that is syntactically valid but unregistered here will return ``False``.

## Awkward edge

Some extensions map to more than one registered media type. ``.xml`` is the common case: both ``application/xml`` and ``text/xml`` are registered (both marked deprecated). ``lookup_by_extension`` always returns a list to handle this uniformly — never a string, even when there is exactly one match.

## API

All names below are importable from the package root (`iana_media_type_registry`).

- `lookup_by_extension(extension: str) -> list[str]` — returns media types for the given extension (with or without leading dot, case-insensitive). Empty list if unknown.
- `lookup_media_type(media_type: str) -> dict | None` — returns the registry record (keys: `name`, `extensions`, `deprecated`, `template`) or `None`.
- `is_valid_media_type(media_type: str) -> bool` — `True` iff the type is in the bundled snapshot. Case-insensitive.
- `MEDIA_TYPES` — the full registry dict, keyed by lowercase `type/subtype`.
- `EXTENSION_TO_MEDIA_TYPES` — reverse index, extension (lowercase, no dot) to list of media types.
- `DATA_SOURCE` — provenance string documenting the snapshot.
