import unittest
from pathlib import Path


class AdminSecurityHeaderTests(unittest.TestCase):
    def test_csp_allows_wordpress_same_origin_admin_iframes(self):
        plugin = Path(__file__).resolve().parents[1] / "scripts" / "hc-auto-activate.php"
        source = plugin.read_text(encoding="utf-8")
        self.assertIn("frame-src 'self' https://www.google.com", source)


if __name__ == "__main__":
    unittest.main()
