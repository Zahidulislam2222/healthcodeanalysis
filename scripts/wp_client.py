"""
WordPress REST API Client for Elementor site automation.
Handles authentication, media uploads, post/meta updates, and cache flushing.
"""

import base64
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests")
    sys.exit(1)


class WPClient:
    """WordPress REST API client with API key + Application Password auth."""

    def __init__(self, site_url=None, username=None, app_password=None, api_key=None, dry_run=False):
        self.site_url = (site_url or os.getenv("WP_SITE_URL", "")).rstrip("/")
        self.username = username or os.getenv("WP_USERNAME", "")
        self.app_password = app_password or os.getenv("WP_APP_PASSWORD", "")
        self.api_key = api_key or os.getenv("HC_API_KEY", "")
        self.dry_run = dry_run
        self.api_base = f"{self.site_url}/wp-json"
        self.session = requests.Session()

        headers = {"User-Agent": "HealthCode-Automation/1.0"}

        # Prefer API key auth (works through Cloudflare/LiteSpeed)
        if self.api_key:
            headers["X-HC-API-Key"] = self.api_key

        # Also set Basic auth as fallback
        if self.username and self.app_password:
            credentials = f"{self.username}:{self.app_password}"
            token = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {token}"

        self.session.headers.update(headers)

    def test_connection(self):
        """Test connection to WordPress REST API. Returns site info or raises."""
        try:
            # Try our custom ping endpoint first (works with API key auth)
            resp = self.session.get(f"{self.api_base}/healthcode/v1/ping", timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "connected": True,
                    "title": data.get("site", ""),
                    "url": data.get("url", ""),
                    "version": data.get("version", ""),
                }

            # Fallback to standard WP settings endpoint
            resp = self.session.get(f"{self.api_base}/wp/v2/settings", timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "connected": True,
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "url": data.get("url", ""),
                }
            elif resp.status_code == 401:
                return {"connected": False, "error": "Authentication failed. Check API key or app password."}
            else:
                return {"connected": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
        except requests.exceptions.ConnectionError:
            return {"connected": False, "error": f"Cannot reach {self.site_url}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    # ── Media ──────────────────────────────────────────────────────

    def upload_image(self, file_path, title=None, alt_text=None):
        """Upload an image to WordPress media library. Returns attachment dict."""
        file_path = Path(file_path)

        if self.dry_run:
            return {
                "id": 99999,
                "url": f"{self.site_url}/wp-content/uploads/2026/04/{file_path.name}",
                "title": title or file_path.stem,
                "dry_run": True,
            }

        if not file_path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
        }
        mime = mime_types.get(file_path.suffix.lower(), "image/jpeg")

        # Try custom endpoint first (works with API key auth through Cloudflare)
        with open(file_path, "rb") as f:
            resp = self.session.post(
                f"{self.api_base}/healthcode/v1/upload-media",
                files={"file": (file_path.name, f, mime)},
                data={"alt_text": alt_text or ""},
                timeout=60,
            )

        if resp.status_code in (200, 201):
            data = resp.json()
            return {
                "id": data.get("id", 0),
                "url": data.get("url", ""),
                "title": data.get("title", ""),
            }

        # Fallback to standard WP endpoint
        with open(file_path, "rb") as f:
            resp = self.session.post(
                f"{self.api_base}/wp/v2/media",
                headers={
                    "Content-Disposition": f'attachment; filename="{file_path.name}"',
                    "Content-Type": mime,
                },
                data=f.read(),
                timeout=60,
            )

        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Upload failed ({resp.status_code}): {resp.text[:300]}")

        data = resp.json()
        result = {
            "id": data["id"],
            "url": data.get("source_url", data.get("guid", {}).get("rendered", "")),
            "title": data.get("title", {}).get("rendered", ""),
        }

        if alt_text:
            self.session.post(
                f"{self.api_base}/wp/v2/media/{data['id']}",
                json={"alt_text": alt_text},
                timeout=15,
            )

        return result

    # ── Posts & Pages ──────────────────────────────────────────────

    def get_pages(self, per_page=100):
        """Get all published pages."""
        pages = []
        page_num = 1
        while True:
            resp = self.session.get(
                f"{self.api_base}/wp/v2/pages",
                params={"per_page": per_page, "page": page_num, "status": "publish"},
                timeout=15,
            )
            if resp.status_code != 200:
                break
            batch = resp.json()
            if not batch:
                break
            pages.extend(batch)
            if len(batch) < per_page:
                break
            page_num += 1
        return pages

    def get_page(self, page_id):
        """Get a single page by ID."""
        resp = self.session.get(f"{self.api_base}/wp/v2/pages/{page_id}", timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"Page {page_id} not found ({resp.status_code})")
        return resp.json()

    def get_posts(self, per_page=100):
        """Get all published posts."""
        posts = []
        page_num = 1
        while True:
            resp = self.session.get(
                f"{self.api_base}/wp/v2/posts",
                params={"per_page": per_page, "page": page_num, "status": "publish"},
                timeout=15,
            )
            if resp.status_code != 200:
                break
            batch = resp.json()
            if not batch:
                break
            posts.extend(batch)
            if len(batch) < per_page:
                break
            page_num += 1
        return posts

    # ── Post Meta (Elementor data & Rank Math) ────────────────────

    def get_post_meta(self, post_id, meta_key):
        """Get a specific meta value for a post. Requires custom REST endpoint or direct DB."""
        resp = self.session.get(
            f"{self.api_base}/wp/v2/pages/{post_id}",
            params={"_fields": "id,meta"},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("meta", {}).get(meta_key)
        return None

    def update_post_meta(self, post_id, meta_dict, post_type="pages"):
        """Update meta fields on a post/page."""
        if self.dry_run:
            return {"dry_run": True, "post_id": post_id, "meta_keys": list(meta_dict.keys())}

        resp = self.session.post(
            f"{self.api_base}/wp/v2/{post_type}/{post_id}",
            json={"meta": meta_dict},
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Meta update failed ({resp.status_code}): {resp.text[:300]}")
        return resp.json()

    # ── Elementor Data ────────────────────────────────────────────

    def get_elementor_data(self, post_id):
        """
        Get Elementor JSON data for a post.
        Note: _elementor_data is not exposed via standard REST API.
        This requires the custom endpoint we'll register, or direct DB access.
        Falls back to parsing from raw post content.
        """
        # Try custom endpoint first
        resp = self.session.get(
            f"{self.api_base}/healthcode/v1/elementor-data/{post_id}",
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()

        # Fallback: try standard meta (if registered)
        meta = self.get_post_meta(post_id, "_elementor_data")
        if meta:
            if isinstance(meta, str):
                return json.loads(meta)
            return meta

        return None

    def update_elementor_data(self, post_id, elementor_json):
        """Update Elementor data for a post."""
        if self.dry_run:
            widget_count = 0

            def count_widgets(elements):
                nonlocal widget_count
                for el in elements:
                    if el.get("widgetType"):
                        widget_count += 1
                    if "elements" in el:
                        count_widgets(el["elements"])

            count_widgets(elementor_json)
            return {"dry_run": True, "post_id": post_id, "widgets": widget_count}

        # Use custom endpoint
        resp = self.session.post(
            f"{self.api_base}/healthcode/v1/elementor-data/{post_id}",
            json={"data": elementor_json},
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Elementor update failed ({resp.status_code}): {resp.text[:300]}")
        return resp.json()

    # ── Site Settings ─────────────────────────────────────────────

    def get_site_settings(self):
        """Get site title, description, etc."""
        resp = self.session.get(f"{self.api_base}/wp/v2/settings", timeout=15)
        if resp.status_code == 200:
            return resp.json()
        return {}

    def update_site_settings(self, settings_dict):
        """Update site settings (title, description, etc.)."""
        if self.dry_run:
            return {"dry_run": True, "settings": list(settings_dict.keys())}

        # Try custom endpoint first (works with API key auth)
        resp = self.session.post(
            f"{self.api_base}/healthcode/v1/site-settings",
            json=settings_dict,
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()

        # Fallback to standard WP endpoint
        resp = self.session.post(
            f"{self.api_base}/wp/v2/settings",
            json=settings_dict,
            timeout=15,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Settings update failed ({resp.status_code}): {resp.text[:300]}")
        return resp.json()

    # ── Cache ─────────────────────────────────────────────────────

    def flush_cache(self):
        """Attempt to flush LiteSpeed / Elementor cache."""
        if self.dry_run:
            return {"dry_run": True, "action": "flush_cache"}

        results = {}
        # Try LiteSpeed purge
        resp = self.session.get(f"{self.site_url}/?litespeed_purge=all", timeout=15)
        results["litespeed"] = resp.status_code

        # Try Elementor CSS regeneration via custom endpoint
        resp = self.session.post(
            f"{self.api_base}/healthcode/v1/flush-elementor-cache",
            timeout=15,
        )
        results["elementor"] = resp.status_code

        return results
