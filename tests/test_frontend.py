"""Offline regression checks for the locally generated publication."""

from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
build = importlib.import_module("build_frontend").build
FrontendSettings = importlib.import_module("frontend_settings").FrontendSettings
project_path = importlib.import_module("frontend_settings").project_path
route_from_link = importlib.import_module("import_frontend_content").route_from_link


class FrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.settings = replace(FrontendSettings.load(), output=Path(cls.temporary.name) / "preview")
        cls.count = build(cls.settings)
        cls.library = json.loads(cls.settings.content.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_every_source_route_exists(self):
        self.assertEqual(self.count, len(self.library["source_routes"]))
        for route in self.library["source_routes"]:
            self.assertTrue((self.settings.output / route.strip("/") / "index.html").is_file(), route)

    def test_every_local_link_and_asset_exists(self):
        for file in self.settings.output.rglob("*.html"):
            soup = BeautifulSoup(file.read_text(encoding="utf-8"), "html.parser")
            self.assertEqual(len(soup.select("h1")), 1, str(file))
            for element in soup.select("[href], [src]"):
                value = element.get("href") or element.get("src")
                if value.startswith("/"):
                    target = self.settings.output / unquote(urlparse(value).path).lstrip("/")
                    self.assertTrue(target.exists(), value)

    def test_imported_content_is_escaped(self):
        data = json.loads(self.settings.content.read_text(encoding="utf-8"))
        data["posts"][0]["title"] = '<img src=x onerror="alert(1)">'
        source = Path(self.temporary.name) / "malicious-content.json"
        source.write_text(json.dumps(data), encoding="utf-8")
        output = Path(self.temporary.name) / "escaped"
        build(replace(self.settings, content=source, output=output))
        page = (output / data["posts"][0]["route"].strip("/") / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<img src=x", page)
        self.assertIn("&lt;img", page)

    def test_paths_cannot_escape(self):
        for path in ("../outside", "nested/../../outside"):
            with self.assertRaises(ValueError):
                project_path(ROOT, path)
        for route in (
            "https://example.test/../secret",
            "https://example.test/%2e%2e/secret",
            "https://example.test/a\\b",
        ):
            with self.assertRaises(ValueError):
                route_from_link(route)

    def test_unicode_route_is_normalized(self):
        self.assertEqual(route_from_link("https://example.test/chads%E2%82%82/"), "/chads₂/")

    def test_rebuild_removes_only_manifest_owned_obsolete_files(self):
        output = Path(self.temporary.name) / "rebuild"
        settings = replace(self.settings, output=output)
        build(settings)
        obsolete = output / "retired" / "index.html"
        obsolete.parent.mkdir()
        obsolete.write_text("Retired page", encoding="utf-8")
        preserved = output / "unmanaged.txt"
        preserved.write_text("Local note", encoding="utf-8")
        manifest = output / "build-manifest.json"
        entries = json.loads(manifest.read_text(encoding="utf-8"))
        entries.append("retired/index.html")
        manifest.write_text(json.dumps(entries), encoding="utf-8")
        build(settings)
        self.assertFalse(obsolete.exists())
        self.assertTrue(preserved.exists())

    def test_client_has_no_remote_services(self):
        config = self.settings.client
        self.assertTrue(config["search_index"].startswith("/"))
        code = (ROOT / "frontend/scripts/app.mjs").read_text(encoding="utf-8")
        for forbidden in ("api.openai.com", "openrouter.ai", "sk-proj-", "-----BEGIN PRIVATE KEY-----", "innerHTML"):
            self.assertNotIn(forbidden, code)
        self.assertNotIn("https://", code)


if __name__ == "__main__":
    unittest.main()
