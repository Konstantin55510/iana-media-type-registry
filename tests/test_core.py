"""Tests for the core lookup and validation functions.

These tests exercise the behaviour the implementation actually claims to
support: case-insensitive lookup, extension ambiguity, registry-membership
validation, and defensive handling of bad input types. No test relies on
network access, wall-clock time, or floating-point comparison.
"""

import unittest

from iana_media_type_registry import (
    DATA_SOURCE,
    EXTENSION_TO_MEDIA_TYPES,
    MEDIA_TYPES,
    is_valid_media_type,
    lookup_by_extension,
    lookup_media_type,
)


class TestLookupMediaType(unittest.TestCase):
    def test_returns_record_for_known_type(self):
        record = lookup_media_type("application/json")
        self.assertIsNotNone(record)
        self.assertEqual(record["name"], "JSON")
        self.assertEqual(record["extensions"], ["json"])
        self.assertFalse(record["deprecated"])

    def test_case_insensitive(self):
        self.assertIsNotNone(lookup_media_type("Application/JSON"))
        self.assertIsNotNone(lookup_media_type("APPLICATION/json"))
        self.assertEqual(
            lookup_media_type("Application/JSON")["name"],
            lookup_media_type("application/json")["name"],
        )

    def test_unknown_returns_none(self):
        self.assertIsNone(lookup_media_type("application/vnd.example.thing"))

    def test_empty_string_returns_none(self):
        self.assertIsNone(lookup_media_type(""))

    def test_non_string_returns_none(self):
        self.assertIsNone(lookup_media_type(None))
        self.assertIsNone(lookup_media_type(123))
        self.assertIsNone(lookup_media_type(["application/json"]))


class TestLookupByExtension(unittest.TestCase):
    def test_single_match(self):
        result = lookup_by_extension("png")
        self.assertEqual(result, ["image/png"])

    def test_leading_dot_stripped(self):
        self.assertEqual(lookup_by_extension(".png"), lookup_by_extension("png"))

    def test_case_insensitive(self):
        self.assertEqual(lookup_by_extension("PNG"), lookup_by_extension("png"))
        self.assertEqual(lookup_by_extension(".PNG"), lookup_by_extension(".png"))

    def test_ambiguous_extension(self):
        result = lookup_by_extension("xml")
        self.assertIn("application/xml", result)
        self.assertIn("text/xml", result)
        self.assertEqual(len(result), 2)

    def test_unknown_extension_returns_empty_list(self):
        self.assertEqual(lookup_by_extension("xyz"), [])

    def test_empty_returns_empty_list(self):
        self.assertEqual(lookup_by_extension(""), [])

    def test_non_string_returns_empty_list(self):
        self.assertEqual(lookup_by_extension(None), [])
        self.assertEqual(lookup_by_extension(42), [])

    def test_returns_copy_not_internal_list(self):
        first = lookup_by_extension("json")
        first.append("application/bogus")
        second = lookup_by_extension("json")
        self.assertEqual(second, ["application/json"])


class TestIsValidMediaType(unittest.TestCase):
    def test_known_type_is_valid(self):
        self.assertTrue(is_valid_media_type("text/plain"))

    def test_case_insensitive(self):
        self.assertTrue(is_valid_media_type("TEXT/PLAIN"))
        self.assertTrue(is_valid_media_type("Text/Plain"))

    def test_unknown_type_is_invalid(self):
        self.assertFalse(is_valid_media_type("application/vnd.example.thing"))

    def test_empty_is_invalid(self):
        self.assertFalse(is_valid_media_type(""))

    def test_non_string_is_invalid(self):
        self.assertFalse(is_valid_media_type(None))
        self.assertFalse(is_valid_media_type(123))


class TestRegistryData(unittest.TestCase):
    def test_extension_index_consistent_with_media_types(self):
        """Every extension in a record must appear in the reverse index."""
        for media_type, record in MEDIA_TYPES.items():
            for ext in record["extensions"]:
                self.assertIn(media_type, EXTENSION_TO_MEDIA_TYPES[ext.lower()])

    def test_media_types_are_lowercase_keys(self):
        for key in MEDIA_TYPES:
            self.assertEqual(key, key.lower(), f"key {key!r} is not lowercase")

    def test_each_record_has_required_fields(self):
        for media_type, record in MEDIA_TYPES.items():
            self.assertIn("name", record)
            self.assertIn("extensions", record)
            self.assertIn("deprecated", record)
            self.assertIsInstance(record["extensions"], list)
            self.assertIsInstance(record["deprecated"], bool)

    def test_data_source_is_documented(self):
        self.assertIsInstance(DATA_SOURCE, str)
        self.assertTrue(len(DATA_SOURCE) > 0)


if __name__ == "__main__":
    unittest.main()
