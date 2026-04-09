"""
Customer config validator.
Validates customer JSON config files against the expected schema.
"""

import json
import sys
from pathlib import Path

# Required top-level fields
REQUIRED_FIELDS = ["customer_name", "domain", "pages"]

# Required per-page fields
REQUIRED_PAGE_FIELDS = ["page_id"]

# Valid image extensions
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


class ConfigValidationError(Exception):
    """Raised when config validation fails."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"Config validation failed with {len(errors)} error(s)")


def validate_config(config_path):
    """
    Validate a customer config JSON file.
    Returns (True, config_dict) on success.
    Raises ConfigValidationError with list of errors on failure.
    """
    config_path = Path(config_path)
    errors = []

    # File exists
    if not config_path.exists():
        raise ConfigValidationError([f"Config file not found: {config_path}"])

    # Valid JSON
    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigValidationError([f"Invalid JSON: {e}"])

    # Must be a dict
    if not isinstance(config, dict):
        raise ConfigValidationError(["Config must be a JSON object (dict)"])

    # Required top-level fields
    for field in REQUIRED_FIELDS:
        if field not in config:
            errors.append(f"Missing required field: '{field}'")

    # customer_name
    if "customer_name" in config and not isinstance(config["customer_name"], str):
        errors.append("'customer_name' must be a string")

    # domain
    if "domain" in config:
        domain = config["domain"]
        if not isinstance(domain, str):
            errors.append("'domain' must be a string")
        elif not domain or " " in domain:
            errors.append(f"Invalid domain: '{domain}'")

    # pages
    if "pages" in config:
        pages = config["pages"]
        if not isinstance(pages, list):
            errors.append("'pages' must be a list")
        else:
            for i, page in enumerate(pages):
                if not isinstance(page, dict):
                    errors.append(f"pages[{i}]: must be a dict")
                    continue

                # page_id required
                if "page_id" not in page:
                    errors.append(f"pages[{i}]: missing 'page_id'")
                elif not isinstance(page["page_id"], int):
                    errors.append(f"pages[{i}]: 'page_id' must be an integer")

                # images validation
                if "images" in page:
                    if not isinstance(page["images"], list):
                        errors.append(f"pages[{i}]: 'images' must be a list")
                    else:
                        for j, img in enumerate(page["images"]):
                            if not isinstance(img, dict):
                                errors.append(f"pages[{i}].images[{j}]: must be a dict")
                                continue
                            if "old_url" not in img and "element_id" not in img and "setting_key" not in img:
                                errors.append(
                                    f"pages[{i}].images[{j}]: needs 'old_url', 'element_id', or 'setting_key'"
                                )
                            if "new_file" in img:
                                new_file = Path(img["new_file"])
                                ext = new_file.suffix.lower()
                                if ext not in VALID_IMAGE_EXTENSIONS:
                                    errors.append(f"pages[{i}].images[{j}]: invalid image extension '{ext}'")

                # headings validation
                if "headings" in page:
                    if not isinstance(page["headings"], list):
                        errors.append(f"pages[{i}]: 'headings' must be a list")
                    else:
                        for j, heading in enumerate(page["headings"]):
                            if not isinstance(heading, dict):
                                errors.append(f"pages[{i}].headings[{j}]: must be a dict")
                                continue
                            if "new_text" not in heading:
                                errors.append(f"pages[{i}].headings[{j}]: missing 'new_text'")
                            if "index" not in heading and "widget_id" not in heading:
                                errors.append(f"pages[{i}].headings[{j}]: needs 'index' or 'widget_id'")

                # texts validation
                if "texts" in page:
                    if not isinstance(page["texts"], list):
                        errors.append(f"pages[{i}]: 'texts' must be a list")
                    else:
                        for j, text in enumerate(page["texts"]):
                            if not isinstance(text, dict):
                                errors.append(f"pages[{i}].texts[{j}]: must be a dict")
                                continue
                            if "new_html" not in text:
                                errors.append(f"pages[{i}].texts[{j}]: missing 'new_html'")

                # meta validation
                if "meta" in page:
                    meta = page["meta"]
                    if not isinstance(meta, dict):
                        errors.append(f"pages[{i}]: 'meta' must be a dict")

    # site_settings validation
    if "site_settings" in config:
        ss = config["site_settings"]
        if not isinstance(ss, dict):
            errors.append("'site_settings' must be a dict")

    if errors:
        raise ConfigValidationError(errors)

    return True, config


def load_config(config_path):
    """Load and validate a config file. Returns the config dict."""
    _, config = validate_config(config_path)
    return config


def print_config_summary(config):
    """Print a human-readable summary of a customer config."""
    print(f"Customer: {config.get('customer_name', 'N/A')}")
    print(f"Domain:   {config.get('domain', 'N/A')}")

    pages = config.get("pages", [])
    print(f"Pages:    {len(pages)}")
    for page in pages:
        pid = page.get("page_id", "?")
        n_images = len(page.get("images", []))
        n_headings = len(page.get("headings", []))
        n_texts = len(page.get("texts", []))
        has_meta = "meta" in page
        print(
            f"  Page {pid}: {n_images} images, {n_headings} headings, {n_texts} texts, meta={'yes' if has_meta else 'no'}"
        )

    if "site_settings" in config:
        ss = config["site_settings"]
        print(f"Site settings: {', '.join(ss.keys())}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python config_validator.py <config.json>")
        sys.exit(1)

    try:
        config = load_config(sys.argv[1])
        print("Config is VALID.")
        print()
        print_config_summary(config)
    except ConfigValidationError as e:
        print("Config is INVALID:")
        for err in e.errors:
            print(f"  - {err}")
        sys.exit(1)
