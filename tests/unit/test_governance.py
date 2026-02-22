#!/usr/bin/env python3
"""
QA Suite 1: Governance & Security Unit Tests
Tests validate_request() exhaustively — the single input firewall for all pipeline entry points.
Run: PYTHONPATH=. python3 tests/unit/test_governance.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from scriptpulse.governance import validate_request, MAX_CHARS

class TestGovernanceValidation(unittest.TestCase):

    # ── Happy path ────────────────────────────────────────────────────
    def test_valid_normal_script(self):
        """Normal screenplay text passes."""
        result = validate_request("INT. OFFICE - DAY\n\nJOHN\nHello world.")
        self.assertTrue(result)

    def test_valid_single_word(self):
        """Single word passes."""
        self.assertTrue(validate_request("hello"))

    def test_valid_unicode_text(self):
        """Valid unicode (accented characters) passes."""
        self.assertTrue(validate_request("Ça va? Très bien, merci."))

    def test_valid_exactly_at_limit(self):
        """Payload exactly at MAX_CHARS passes."""
        payload = "A" * MAX_CHARS
        self.assertTrue(validate_request(payload))

    # ── Type enforcement ──────────────────────────────────────────────
    def test_rejects_integer(self):
        """Integer input raises ValueError."""
        with self.assertRaises(ValueError):
            validate_request(42)

    def test_rejects_none(self):
        """None input raises ValueError."""
        with self.assertRaises(ValueError):
            validate_request(None)

    def test_rejects_list(self):
        """List input raises ValueError."""
        with self.assertRaises(ValueError):
            validate_request(["INT. OFFICE - DAY"])

    def test_rejects_bytes(self):
        """Bytes input raises ValueError (not a str)."""
        with self.assertRaises(ValueError):
            validate_request(b"INT. OFFICE - DAY")

    # ── Size enforcement ──────────────────────────────────────────────
    def test_rejects_oversized_payload(self):
        """Payload exceeding MAX_CHARS raises ValueError."""
        payload = "X" * (MAX_CHARS + 1)
        with self.assertRaises(ValueError) as ctx:
            validate_request(payload)
        self.assertIn("exceeds maximum", str(ctx.exception))

    def test_rejects_5mb_plus_blob(self):
        """5MB + 1 byte payload is rejected."""
        payload = "A" * (5 * 1024 * 1024 + 1)
        with self.assertRaises(ValueError):
            validate_request(payload)

    # ── Null-byte injection ───────────────────────────────────────────
    def test_rejects_null_byte(self):
        """Null byte in payload raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            validate_request("INT. OFFICE\x00INJECTED - DAY")
        self.assertIn("null", str(ctx.exception).lower())

    def test_rejects_null_byte_at_start(self):
        """Leading null byte raises ValueError."""
        with self.assertRaises(ValueError):
            validate_request("\x00payload")

    def test_rejects_null_byte_at_end(self):
        """Trailing null byte raises ValueError."""
        with self.assertRaises(ValueError):
            validate_request("normal text\x00")

    def test_rejects_multiple_null_bytes(self):
        """Multiple null bytes raises ValueError."""
        with self.assertRaises(ValueError):
            validate_request("a\x00b\x00c")

    # ── Empty string (edge case) ───────────────────────────────────────
    def test_empty_string_passes(self):
        """Empty string passes governance (pipeline handles empty gracefully)."""
        result = validate_request("")
        self.assertTrue(result)


if __name__ == '__main__':
    print("═" * 55)
    print("QA SUITE 1: Governance & Security Unit Tests")
    print("═" * 55)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGovernanceValidation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
