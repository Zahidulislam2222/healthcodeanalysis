"""
Content Swapper — Orchestrates image, text, heading, and SEO meta replacements
for a single page based on a customer config.
"""

from pathlib import Path

from elementor_parser import ElementorParser
from wp_client import WPClient


class ContentSwapper:
    """Swap images, text, headings, and SEO metas for a WordPress page."""

    def __init__(self, client: WPClient, verbose=True):
        self.client = client
        self.verbose = verbose
        self.log_entries = []

    def log(self, msg):
        self.log_entries.append(msg)
        if self.verbose:
            print(f"  {msg}")

    # ── Image Swap ────────────────────────────────────────────────

    def swap_images(self, page_id, image_configs, elementor_data):
        """
        Upload new images and replace URLs in Elementor data.

        Args:
            page_id: WordPress page ID
            image_configs: list of dicts with old_url/new_file/match_mode
            elementor_data: list (parsed Elementor JSON)

        Returns:
            (modified_elementor_data, upload_results)
        """
        parser = ElementorParser(elementor_data)
        upload_results = []

        for img_conf in image_configs:
            old_url = img_conf.get("old_url", "")
            new_file = img_conf.get("new_file", "")
            match_mode = img_conf.get("match_mode", "exact")
            alt_text = img_conf.get("alt_text", "")

            if not new_file:
                self.log(f"[SKIP] No new_file for old_url={old_url}")
                continue

            # Upload new image
            self.log(f"[UPLOAD] {Path(new_file).name}")
            result = self.client.upload_image(
                new_file,
                title=Path(new_file).stem,
                alt_text=alt_text,
            )
            upload_results.append(result)
            new_url = result["url"]
            new_id = result.get("id")

            # Find and replace in Elementor data
            if match_mode == "filename":
                # Match by filename anywhere in the URL
                all_images = parser.get_all_images()
                replaced = 0
                for img in all_images:
                    if old_url in img["url"]:
                        count = parser.replace_image(img["url"], new_url, new_id)
                        replaced += count
                self.log(f"[REPLACE] '{old_url}' -> '{Path(new_url).name}' ({replaced} replacements)")
            else:
                # Exact URL match
                count = parser.replace_image(old_url, new_url, new_id)
                self.log(f"[REPLACE] exact URL ({count} replacements)")

        return parser.to_data(), upload_results

    # ── Heading Swap ──────────────────────────────────────────────

    def swap_headings(self, elementor_data, heading_configs):
        """
        Replace headings in Elementor data.

        Args:
            elementor_data: list (parsed Elementor JSON)
            heading_configs: list of dicts with index/widget_id and new_text

        Returns:
            modified_elementor_data
        """
        parser = ElementorParser(elementor_data)

        for h_conf in heading_configs:
            new_text = h_conf.get("new_text", "")
            widget_id = h_conf.get("widget_id")
            index = h_conf.get("index")

            if widget_id:
                result = parser.replace_text(widget_id, new_text, "title")
                self.log(f"[HEADING] widget_id={widget_id}: {'OK' if result else 'NOT FOUND'}")
            elif index is not None:
                result = parser.replace_heading_by_index(index, new_text)
                self.log(f"[HEADING] index={index}: {'OK' if result else 'OUT OF RANGE'}")
            else:
                self.log("[SKIP] Heading config missing 'widget_id' or 'index'")

        return parser.to_data()

    # ── Text Editor Swap ──────────────────────────────────────────

    def swap_texts(self, elementor_data, text_configs):
        """
        Replace text-editor widget content in Elementor data.

        Args:
            elementor_data: list (parsed Elementor JSON)
            text_configs: list of dicts with index/widget_id and new_html

        Returns:
            modified_elementor_data
        """
        parser = ElementorParser(elementor_data)

        for t_conf in text_configs:
            new_html = t_conf.get("new_html", "")
            widget_id = t_conf.get("widget_id")
            index = t_conf.get("index")

            if widget_id:
                result = parser.replace_text(widget_id, new_html, "editor")
                self.log(f"[TEXT] widget_id={widget_id}: {'OK' if result else 'NOT FOUND'}")
            elif index is not None:
                result = parser.replace_text_editor_by_index(index, new_html)
                self.log(f"[TEXT] index={index}: {'OK' if result else 'OUT OF RANGE'}")
            else:
                self.log("[SKIP] Text config missing 'widget_id' or 'index'")

        return parser.to_data()

    # ── SEO Meta Swap ─────────────────────────────────────────────

    def swap_seo_meta(self, page_id, meta_config):
        """
        Update Rank Math SEO meta fields for a page.

        Args:
            page_id: WordPress page ID
            meta_config: dict with rank_math_title, rank_math_description, etc.

        Returns:
            API response
        """
        if not meta_config:
            self.log("[SEO] No meta config, skipping")
            return None

        self.log(f"[SEO] Updating {len(meta_config)} meta fields for page {page_id}")

        if self.client.dry_run:
            for key, val in meta_config.items():
                self.log(f"  {key} = {val[:60]}...")
            return {"dry_run": True, "post_id": page_id, "meta_keys": list(meta_config.keys())}

        # Use custom endpoint for Rank Math metas
        resp = self.client.session.post(
            f"{self.client.api_base}/healthcode/v1/rank-math-meta/{page_id}",
            json=meta_config,
            timeout=15,
        )
        if resp.status_code in (200, 201):
            result = resp.json()
            self.log(f"[SEO] Updated: {result.get('updated_keys', [])}")
            return result
        else:
            self.log(f"[SEO] Failed ({resp.status_code}): {resp.text[:200]}")
            return None

    # ── Site Settings ─────────────────────────────────────────────

    def swap_site_settings(self, settings_config):
        """
        Update site-wide settings (title, tagline, logo, favicon).

        Args:
            settings_config: dict with title, description, logo_file, favicon_file

        Returns:
            results dict
        """
        results = {}

        # Basic settings via REST API
        rest_settings = {}
        if "title" in settings_config:
            rest_settings["title"] = settings_config["title"]
        if "description" in settings_config:
            rest_settings["description"] = settings_config["description"]

        if rest_settings:
            self.log(f"[SITE] Updating: {list(rest_settings.keys())}")
            result = self.client.update_site_settings(rest_settings)
            results["settings"] = result

        # Logo upload + activate
        if settings_config.get("logo_file"):
            self.log(f"[SITE] Uploading logo: {settings_config['logo_file']}")
            result = self.client.upload_image(settings_config["logo_file"], title="Site Logo")
            results["logo"] = result
            # Set as active site logo
            if result.get("id"):
                self.log(f"[SITE] Activating logo (attachment {result['id']})")
                self.client.update_site_settings({"custom_logo": result["id"]})

        # Favicon upload + activate
        if settings_config.get("favicon_file"):
            self.log(f"[SITE] Uploading favicon: {settings_config['favicon_file']}")
            result = self.client.upload_image(settings_config["favicon_file"], title="Site Favicon")
            results["favicon"] = result
            # Set as active site icon
            if result.get("id"):
                self.log(f"[SITE] Activating favicon (attachment {result['id']})")
                self.client.update_site_settings({"site_icon": result["id"]})

        return results

    # ── Full Page Swap ────────────────────────────────────────────

    def swap_page(self, page_config, elementor_data):
        """
        Perform all swaps for a single page.

        Args:
            page_config: dict from customer config (one page entry)
            elementor_data: list (parsed Elementor JSON for this page)

        Returns:
            (modified_elementor_data, results_dict)
        """
        page_id = page_config["page_id"]
        page_name = page_config.get("page_name", f"Page {page_id}")
        self.log(f"\n{'=' * 50}")
        self.log(f"Processing: {page_name} (ID: {page_id})")
        self.log(f"{'=' * 50}")

        results = {"page_id": page_id, "page_name": page_name}
        data = elementor_data

        # 1. Swap images
        images = page_config.get("images", [])
        if images:
            data, upload_results = self.swap_images(page_id, images, data)
            results["images_uploaded"] = len(upload_results)
        else:
            results["images_uploaded"] = 0

        # 2. Swap headings
        headings = page_config.get("headings", [])
        if headings:
            data = self.swap_headings(data, headings)
            results["headings_swapped"] = len(headings)
        else:
            results["headings_swapped"] = 0

        # 3. Swap text editors
        texts = page_config.get("texts", [])
        if texts:
            data = self.swap_texts(data, texts)
            results["texts_swapped"] = len(texts)
        else:
            results["texts_swapped"] = 0

        # 4. Update SEO metas
        meta = page_config.get("meta", {})
        if meta:
            meta_result = self.swap_seo_meta(page_id, meta)
            results["seo_updated"] = meta_result is not None
        else:
            results["seo_updated"] = False

        return data, results
