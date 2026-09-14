"""Keep provider configuration and obvious secret material out of native runtime code."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = [
    *sorted((ROOT / "wordpress-native/scripts").glob("*.py")),
    *sorted((ROOT / "wordpress-native/plugin").glob("*.php")),
]


class NativeConfigurationContracts(unittest.TestCase):
    def test_urls_are_only_fixed_protocol_identifiers(self):
        allowed = {
            "build_native.py": {"http://www.w3.org/2000/svg"},
            "publishing.php": {"https://schema.org"},
        }
        for path in SOURCE:
            with self.subTest(file=path.name):
                urls = set(re.findall(r"https?://[^\s\"'<>]+", path.read_text(encoding="utf-8")))
                self.assertEqual(urls - allowed.get(path.name, set()), set())

    def test_no_obvious_secret_material_or_model_ids(self):
        signatures = [
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
            r"\bAKIA[A-Z0-9]{16}\b",
            r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
            r"\bsk-[A-Za-z0-9_-]{20,}\b",
            r"\b(?:gpt|claude|gemini|seedance)-[0-9][A-Za-z0-9_.-]*\b",
        ]
        for path in SOURCE:
            content = path.read_text(encoding="utf-8")
            for signature in signatures:
                with self.subTest(file=path.name, signature=signature):
                    self.assertIsNone(re.search(signature, content))


if __name__ == "__main__":
    unittest.main()
