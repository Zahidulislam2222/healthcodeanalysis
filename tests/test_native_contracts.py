"""Offline safety and editing contracts for the native Elementor migration."""

from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "wordpress-native/scripts"))
scope_stylesheet = importlib.import_module("style_scope").scope_stylesheet
NativeEnvironment = importlib.import_module("native_settings").NativeEnvironment


class NativeContracts(unittest.TestCase):
    def test_body_classes_remain_on_body(self):
        scoped = scope_stylesheet(".home-page main{margin-top:-95px}body{color:white}")
        self.assertIn(".hc-native.hc-native.hc-native.home-page main", scoped)
        self.assertNotIn(".hc-native .home-page", scoped)
        self.assertIn("body.hc-native.hc-native.hc-native", scoped)

    def test_nested_responsive_rules_and_keyframes(self):
        scoped = scope_stylesheet("@media(max-width:600px){.home-page main{margin:0}}@keyframes fade{to{opacity:1}}")
        self.assertIn(".hc-native.hc-native.hc-native.home-page main", scoped)
        self.assertIn("@keyframes fade{to{opacity:1}}", scoped)

    def test_native_hero_calls_to_action_are_buttons(self):
        data = json.loads((ROOT / "wordpress-native/build/import/pages.json").read_text(encoding="utf-8"))
        home = next(page for page in data["pages"] if page["route"] == "/")

        def walk(nodes):
            for node in nodes:
                yield node
                yield from walk(node["elements"])

        widgets = list(walk(home["elements"]))
        actions = next(node for node in widgets if node["settings"].get("css_classes") == "frontier-actions")
        self.assertEqual([child.get("widgetType") for child in actions["elements"]], ["button", "button"])
        self.assertFalse(any(node.get("widgetType") == "html" for node in widgets))

    def test_toolbox_icons_preserve_contextual_color(self):
        builder = importlib.import_module("build_native")
        from bs4 import BeautifulSoup

        with tempfile.TemporaryDirectory() as folder:
            previous = builder.PLUGIN
            try:
                builder.PLUGIN = Path(folder)
                (builder.PLUGIN / "assets").mkdir()
                fragment = BeautifulSoup(
                    '<section class="frontier-workbench"><span class="tool-icon"><svg stroke="currentColor"></svg></span></section>',
                    "html.parser",
                )
                builder.rich(fragment.span)
                generated = list((builder.PLUGIN / "assets").glob("*.svg"))
                self.assertEqual(len(generated), 1)
                self.assertIn('stroke="#244132"', generated[0].read_text(encoding="utf-8"))
            finally:
                builder.PLUGIN = previous

    def test_importer_refuses_nonlocal_targets(self):
        guard = importlib.import_module("import_local").loopback_only
        for origin in ["http://127.0.0.1:8890", "http://[::1]:8890", "http://localhost:8890"]:
            guard(origin)
        for origin in ["https://example.invalid", "http://192.0.2.1", "http://localhost.example.invalid"]:
            with self.assertRaises(ValueError):
                guard(origin)

    def test_future_data_collection_is_disabled(self):
        policy = json.loads((ROOT / "wordpress-native/data/publishing-policy.json").read_text(encoding="utf-8"))
        self.assertTrue(all(value is False for value in policy["features"].values()))
        self.assertFalse(policy["index_demonstration_articles"])

    def test_importer_rejects_remote_docker_before_mutation(self):
        importer = importlib.import_module("import_local")
        with (
            patch.dict(importer.os.environ, {"DOCKER_HOST": "ssh://example.invalid"}, clear=True),
            patch.object(importer.subprocess, "run") as run,
        ):
            with self.assertRaises(ValueError):
                importer.local_docker_command("docker", 10)
            run.assert_not_called()
        remote = SimpleNamespace(
            returncode=0,
            stdout=json.dumps([{"Endpoints": {"docker": {"Host": "tcp://example.invalid:2375"}}}]).encode(),
        )
        with (
            patch.dict(importer.os.environ, {"DOCKER_CONTEXT": "remote"}, clear=True),
            patch.object(importer.subprocess, "run", return_value=remote) as run,
        ):
            with self.assertRaises(ValueError):
                importer.local_docker_command("docker", 10)
            self.assertEqual(run.call_args.args[0], ["docker", "context", "inspect"])
            self.assertEqual(run.call_count, 1)

    def test_importer_pins_local_socket_and_removes_overrides(self):
        importer = importlib.import_module("import_local")
        for endpoint in ["unix:///var/run/docker.sock", "npipe:////./pipe/dockerDesktopLinuxEngine"]:
            local = SimpleNamespace(
                returncode=0, stdout=json.dumps([{"Endpoints": {"docker": {"Host": endpoint}}}]).encode()
            )
            with (
                patch.dict(importer.os.environ, {"DOCKER_CONTEXT": "local", "DOCKER_TLS_VERIFY": "1"}, clear=True),
                patch.object(importer.subprocess, "run", return_value=local),
            ):
                command, environment = importer.local_docker_command("docker", 10)
                self.assertEqual(command, ["docker", "--host", endpoint])
                self.assertNotIn("DOCKER_CONTEXT", environment)
                self.assertNotIn("DOCKER_TLS_VERIFY", environment)
        for endpoint in ["tcp://127.0.0.1:2375", "npipe:////server/pipe/docker", "unix://remote/socket"]:
            with self.assertRaises(ValueError):
                importer.validate_local_endpoint(endpoint)

    def test_environment_contract_is_complete_and_secrets_not_in_repr(self):
        example = (ROOT / "wordpress-native/.env.example").read_text(encoding="utf-8")
        values = dict(line.split("=", 1) for line in example.splitlines() if "=" in line and not line.startswith("#"))
        self.assertEqual({key.lower() for key in values}, set(NativeEnvironment.__dataclass_fields__))
        values.update(
            DB_PASSWORD="test-key",
            DB_ROOT_PASSWORD="test-key",
            ADMIN_PASSWORD="test-key",
            SITE_URL="http://localhost",
            WP_PORT="8890",
            WP_ENVIRONMENT_TYPE="local",
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.env"
            path.write_text("\n".join(f"{key}={value}" for key, value in values.items()), encoding="utf-8")
            settings = NativeEnvironment.load(path)
            self.assertNotIn("test-key", repr(settings))
            values["WP_ENVIRONMENT_TYPE"] = "production"
            path.write_text("\n".join(f"{key}={value}" for key, value in values.items()), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                NativeEnvironment.load(path)


if __name__ == "__main__":
    unittest.main()
