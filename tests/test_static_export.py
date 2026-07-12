import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from export_static_site import (
    ExportError,
    StaticExporter,
    collect_css_urls,
    disable_wordpress_forms,
    prefer_elementor_login_popup,
    public_path,
    rewrite_text,
    strip_html,
)


class StaticExportTests(unittest.TestCase):
    def test_public_path_uses_home_and_slugs(self):
        self.assertEqual(public_path({"slug": "home", "link": "http://localhost:8889/"}, "pages"), "/")
        self.assertEqual(
            public_path({"slug": "about", "link": "http://localhost:8889/about/"}, "pages"), "/about/"
        )

    def test_rewrite_text_removes_backend_domains(self):
        result = rewrite_text(
            'http://127.0.0.1:8889/a https:\\/\\/admin-demo.healthcodeanalysis.com\\/b',
            {"http://127.0.0.1:8889", "https://admin-demo.healthcodeanalysis.com"},
            "https://healthcodeanalysis.pages.dev",
        )
        self.assertNotIn("127.0.0.1", result)
        self.assertNotIn("admin-demo.healthcodeanalysis.com", result)
        self.assertEqual(result.count("healthcodeanalysis.pages.dev"), 2)

    def test_exporter_rewrites_bare_localhost_media_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            exporter = StaticExporter(
                "http://127.0.0.1:8889", "https://healthcodeanalysis.pages.dev", Path(directory)
            )
            result = rewrite_text(
                "http://localhost/wp-content/uploads/logo.png",
                exporter.origins,
                exporter.public_url,
            )
        self.assertEqual(result, "https://healthcodeanalysis.pages.dev/wp-content/uploads/logo.png")

    def test_rewrite_text_removes_url_encoded_backend_domains(self):
        result = rewrite_text(
            "embed?url=http%3A%2F%2F127.0.0.1%3A8889%2Fcontact%2F",
            {"http://127.0.0.1:8889"},
            "https://healthcodeanalysis.pages.dev",
        )
        self.assertNotIn("127.0.0.1", result)
        self.assertIn("https%3A%2F%2Fhealthcodeanalysis.pages.dev%2Fcontact", result)

    def test_wordpress_forms_are_explicitly_disabled_in_static_export(self):
        document = '<body><div data-action="https://public.test/wp-json/metform/v1/entries/insert/7"></div></body>'
        result = disable_wordpress_forms(document)
        self.assertIn('data-action="#" data-static-form="disabled"', result)
        self.assertIn("healthcode-static-form-guard", result)
        self.assertNotIn("wp-json/metform", result)

    def test_elementor_popup_replaces_duplicate_custom_popup(self):
        document = '''<body>
<div id="hca-custom-popup"><div>Old login</div></div>
<style>.hca-popup-overlay { display: flex; }</style>
<script>function openCustomPopup() {}</script>
<div id="wpr-popup-id-2732" class="wpr-template-popup">Template login</div>
</body>'''
        result = prefer_elementor_login_popup(document)
        self.assertNotIn("hca-custom-popup", result)
        self.assertNotIn("openCustomPopup", result)
        self.assertIn("wpr-popup-id-2732", result)

    def test_custom_popup_is_kept_without_elementor_replacement(self):
        document = '<div id="hca-custom-popup">Only login</div>'
        self.assertEqual(prefer_elementor_login_popup(document), document)

    def test_css_url_collector_finds_assets_but_skips_data_urls(self):
        result = collect_css_urls('a{background:url("/one.png")}b{src:url(data:image/png;base64,abc)}')
        self.assertEqual(result, {"/one.png"})

    def test_bundle_validation_rejects_local_network_references(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "bad.css").write_text("a{background:url(http://127.0.0.1:8889/a.png)}")
            exporter = StaticExporter("http://127.0.0.1:8889", "https://public.test", output)
            with self.assertRaises(ExportError):
                exporter.validate_public_bundle()

    def test_content_index_is_wp_shaped(self):
        with tempfile.TemporaryDirectory() as directory:
            exporter = StaticExporter(
                "http://127.0.0.1:8889", "https://healthcodeanalysis.pages.dev", Path(directory)
            )
            posts = [{
                "id": 7, "slug": "sample", "link": "http://127.0.0.1:8889/sample/",
                "date": "2026-01-01", "modified": "2026-01-02", "title": {"rendered": "Sample"},
                "excerpt": {"rendered": ""}, "content": {"rendered": "<p>Useful text</p>"}, "categories": [3],
            }]
            categories = [{"id": 3, "slug": "news", "name": "News", "count": 1}]
            result = exporter.build_content_index(posts, [], categories)
        self.assertEqual(result["posts"][0]["content"]["text"], "Useful text")
        self.assertEqual(result["posts"][0]["content"]["rendered"], "Useful text")
        self.assertEqual(result["posts"][0]["link"], "https://healthcodeanalysis.pages.dev/sample/")
        self.assertTrue(result["categories"][0]["link"].endswith("/category/news/"))
        self.assertEqual(set(result["categories"][0]), {"id", "name", "slug", "count", "parent", "link"})
        json.dumps(result)

    def test_strip_html_decodes_entities(self):
        self.assertEqual(strip_html("<p>Health &amp; AI</p><script>bad()</script>"), "Health & AI")


if __name__ == "__main__":
    unittest.main()
