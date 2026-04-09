"""
Elementor JSON Parser and Modifier.
Parses _elementor_data JSON, finds widgets by type/ID, and replaces content.
"""

import copy
import json
import re


class ElementorParser:
    """Parse and modify Elementor page data."""

    def __init__(self, elementor_data):
        """
        Args:
            elementor_data: list of Elementor elements (parsed JSON)
                            or a JSON string to parse.
        """
        if isinstance(elementor_data, str):
            self.data = json.loads(elementor_data)
        else:
            self.data = copy.deepcopy(elementor_data)

    # ── Query ─────────────────────────────────────────────────────

    def find_widgets(self, widget_type=None, widget_id=None):
        """Find widgets by type and/or ID. Returns list of (path, widget) tuples."""
        results = []
        self._walk(self.data, [], widget_type, widget_id, results)
        return results

    def _walk(self, elements, path, widget_type, widget_id, results):
        for i, el in enumerate(elements):
            current_path = [*path, i]
            wtype = el.get("widgetType")
            wid = el.get("id")

            match = True
            if widget_type and wtype != widget_type:
                match = False
            if widget_id and wid != widget_id:
                match = False
            if widget_type is None and widget_id is None:
                match = False

            if match:
                results.append((current_path, el))

            if "elements" in el:
                self._walk(el["elements"], [*current_path, "elements"], widget_type, widget_id, results)

    def get_all_widgets(self):
        """Get all widgets with their types, IDs, and key settings."""
        widgets = []
        self._collect_all(self.data, widgets)
        return widgets

    def _collect_all(self, elements, widgets, depth=0):
        for el in elements:
            wtype = el.get("widgetType")
            if wtype:
                settings = el.get("settings", {})
                info = {
                    "id": el.get("id"),
                    "type": wtype,
                    "depth": depth,
                }
                # Extract key content based on widget type
                if wtype == "heading":
                    info["title"] = settings.get("title", "")
                elif wtype == "text-editor":
                    info["editor"] = settings.get("editor", "")[:200]
                elif wtype == "image":
                    img = settings.get("image", {})
                    info["image_url"] = img.get("url", "")
                    info["image_id"] = img.get("id", "")
                elif wtype == "button":
                    info["text"] = settings.get("text", "")
                    info["link"] = settings.get("link", {}).get("url", "")
                elif wtype == "counter":
                    info["title"] = settings.get("title", "")
                    info["ending_number"] = settings.get("ending_number", "")

                widgets.append(info)

            if "elements" in el:
                self._collect_all(el["elements"], widgets, depth + 1)

    def get_all_images(self):
        """Get all image references in the Elementor data."""
        images = []
        self._find_images(self.data, images)
        return images

    def _find_images(self, elements, images, parent_type="root"):
        for el in elements:
            wtype = el.get("widgetType") or el.get("elType", "unknown")
            settings = el.get("settings", {})

            for key, val in settings.items():
                # Direct image fields
                if isinstance(val, dict) and "url" in val:
                    url = val.get("url", "")
                    if url and self._is_image_url(url):
                        images.append(
                            {
                                "element_id": el.get("id"),
                                "element_type": wtype,
                                "setting_key": key,
                                "url": url,
                                "attachment_id": val.get("id", ""),
                            }
                        )

                # Images inside repeater lists
                if isinstance(val, list):
                    for idx, item in enumerate(val):
                        if isinstance(item, dict):
                            for k2, v2 in item.items():
                                if isinstance(v2, dict) and "url" in v2:
                                    url = v2.get("url", "")
                                    if url and self._is_image_url(url):
                                        images.append(
                                            {
                                                "element_id": el.get("id"),
                                                "element_type": wtype,
                                                "setting_key": f"{key}[{idx}].{k2}",
                                                "url": url,
                                                "attachment_id": v2.get("id", ""),
                                            }
                                        )

                # Background images in string CSS
                if isinstance(val, str) and "wp-content/uploads" in val:
                    urls = re.findall(r'https?://[^\s"\']+\.(?:jpg|png|webp|jpeg|gif|svg)', val)
                    for url in urls:
                        images.append(
                            {
                                "element_id": el.get("id"),
                                "element_type": wtype,
                                "setting_key": f"{key}(css)",
                                "url": url,
                            }
                        )

            if "elements" in el:
                self._find_images(el["elements"], images, wtype)

    @staticmethod
    def _is_image_url(url):
        return any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"])

    # ── Modify ────────────────────────────────────────────────────

    def replace_image(self, old_url, new_url, new_attachment_id=None):
        """Replace an image URL throughout the Elementor data. Returns count of replacements."""
        count = self._replace_image_recursive(self.data, old_url, new_url, new_attachment_id)
        return count

    def _replace_image_recursive(self, elements, old_url, new_url, new_id):
        count = 0
        for el in elements:
            settings = el.get("settings", {})
            for key, val in settings.items():
                if isinstance(val, dict) and val.get("url") == old_url:
                    val["url"] = new_url
                    if new_id is not None:
                        val["id"] = new_id
                    count += 1
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            for _k2, v2 in item.items():
                                if isinstance(v2, dict) and v2.get("url") == old_url:
                                    v2["url"] = new_url
                                    if new_id is not None:
                                        v2["id"] = new_id
                                    count += 1
                elif isinstance(val, str) and old_url in val:
                    settings[key] = val.replace(old_url, new_url)
                    count += 1

            if "elements" in el:
                count += self._replace_image_recursive(el["elements"], old_url, new_url, new_id)
        return count

    def replace_text(self, widget_id, new_text, setting_key="title"):
        """Replace text in a specific widget by its Elementor ID."""
        return self._replace_text_recursive(self.data, widget_id, new_text, setting_key)

    def _replace_text_recursive(self, elements, widget_id, new_text, setting_key):
        for el in elements:
            if el.get("id") == widget_id:
                if "settings" not in el:
                    el["settings"] = {}
                el["settings"][setting_key] = new_text
                return True
            if "elements" in el and self._replace_text_recursive(el["elements"], widget_id, new_text, setting_key):
                return True
        return False

    def replace_heading_by_index(self, index, new_text):
        """Replace the Nth heading widget's title (0-indexed)."""
        headings = self.find_widgets(widget_type="heading")
        if index < len(headings):
            _path, widget = headings[index]
            if "settings" not in widget:
                widget["settings"] = {}
            widget["settings"]["title"] = new_text
            return True
        return False

    def replace_text_editor_by_index(self, index, new_html):
        """Replace the Nth text-editor widget's content (0-indexed)."""
        editors = self.find_widgets(widget_type="text-editor")
        if index < len(editors):
            _path, widget = editors[index]
            if "settings" not in widget:
                widget["settings"] = {}
            widget["settings"]["editor"] = new_html
            return True
        return False

    def bulk_replace_domain(self, old_domain, new_domain):
        """Replace all occurrences of a domain in the entire Elementor data."""
        json_str = json.dumps(self.data)
        count = json_str.count(old_domain)
        json_str = json_str.replace(old_domain, new_domain)
        self.data = json.loads(json_str)
        return count

    # ── Export ─────────────────────────────────────────────────────

    def to_json(self, indent=None):
        """Export modified data as JSON string."""
        return json.dumps(self.data, ensure_ascii=False, indent=indent)

    def to_data(self):
        """Export modified data as Python list."""
        return self.data

    # ── Static helpers ────────────────────────────────────────────

    @staticmethod
    def load_from_file(file_path):
        """Load Elementor JSON from a file."""
        with open(file_path, encoding="utf-8") as f:
            return ElementorParser(json.load(f))

    def save_to_file(self, file_path, indent=2):
        """Save Elementor JSON to a file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=indent)
