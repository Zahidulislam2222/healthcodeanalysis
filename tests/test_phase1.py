"""
Phase 1 Tests: Project structure, core utilities, config validation.
Tests run without network access (dry-run / mock mode).
"""

import json
import os
import sys
import tempfile

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from config_validator import ConfigValidationError, validate_config
from elementor_parser import ElementorParser
from wp_client import WPClient

# ── Sample Elementor data (based on real extracted data) ──────────

SAMPLE_ELEMENTOR = [
    {
        "id": "6fc0b7dd",
        "elType": "container",
        "settings": {
            "flex_direction": "column",
            "background_image": {
                "url": "https://healthcodeanalysis.com/wp-content/uploads/2025/12/hero-bg.jpg",
                "id": 100,
            },
        },
        "elements": [
            {
                "id": "abc123",
                "elType": "widget",
                "widgetType": "heading",
                "settings": {"title": "Where AI Meets Medicine", "size": "h1"},
                "elements": [],
            },
            {
                "id": "def456",
                "elType": "widget",
                "widgetType": "text-editor",
                "settings": {"editor": "<p>Bridging the gap between clinical excellence.</p>"},
                "elements": [],
            },
            {
                "id": "ghi789",
                "elType": "widget",
                "widgetType": "image",
                "settings": {
                    "image": {
                        "url": "https://healthcodeanalysis.com/wp-content/uploads/2025/12/Doctor2-pose.png",
                        "id": 200,
                    }
                },
                "elements": [],
            },
            {
                "id": "jkl012",
                "elType": "widget",
                "widgetType": "heading",
                "settings": {"title": "Choose Your Path", "size": "h2"},
                "elements": [],
            },
            {
                "id": "counter1",
                "elType": "widget",
                "widgetType": "counter",
                "settings": {"title": "ARTICLES PUBLISHED", "ending_number": "150"},
                "elements": [],
            },
            {
                "id": "btn1",
                "elType": "widget",
                "widgetType": "button",
                "settings": {"text": "Explore Now", "link": {"url": "https://healthcodeanalysis.com/repository"}},
                "elements": [],
            },
            {
                "id": "testimonials1",
                "elType": "widget",
                "widgetType": "jkit_testimonials",
                "settings": {
                    "sg_testimonials_list": [
                        {
                            "sg_testimonials_list_client_avatar": {
                                "url": "https://healthcodeanalysis.com/wp-content/uploads/2025/12/Testimonial-3.png",
                                "id": 300,
                            },
                            "sg_testimonials_list_client_name": "Dr. Smith",
                        },
                        {
                            "sg_testimonials_list_client_avatar": {
                                "url": "https://healthcodeanalysis.com/wp-content/uploads/2025/12/Testimonial.png",
                                "id": 301,
                            },
                            "sg_testimonials_list_client_name": "Dr. Jones",
                        },
                    ]
                },
                "elements": [],
            },
        ],
    }
]

PASSED = 0
FAILED = 0


def test(name, condition, detail=""):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS: {name}")
    else:
        FAILED += 1
        print(f"  FAIL: {name} {detail}")


def test_project_structure():
    """Test that all required directories and files exist."""
    print("\n=== Test: Project Structure ===")
    base = os.path.join(os.path.dirname(__file__), "..")

    dirs = ["scripts", "configs", "templates", "assets", "tests"]
    for d in dirs:
        path = os.path.join(base, d)
        test(f"Directory '{d}' exists", os.path.isdir(path))

    files = [
        "CLAUDE.md",
        "BUILD_PLAN.md",
        ".env.sample",
        ".gitignore",
        "scripts/wp_client.py",
        "scripts/elementor_parser.py",
        "scripts/config_validator.py",
        "scripts/healthcode-api-bridge.php",
        "configs/customer-template.json",
    ]
    for f in files:
        path = os.path.join(base, f)
        test(f"File '{f}' exists", os.path.isfile(path))


def test_elementor_parser_find_widgets():
    """Test finding widgets by type."""
    print("\n=== Test: ElementorParser.find_widgets ===")
    parser = ElementorParser(SAMPLE_ELEMENTOR)

    headings = parser.find_widgets(widget_type="heading")
    test("Finds 2 heading widgets", len(headings) == 2)
    test("First heading is 'Where AI Meets Medicine'", headings[0][1]["settings"]["title"] == "Where AI Meets Medicine")

    images = parser.find_widgets(widget_type="image")
    test("Finds 1 image widget", len(images) == 1)

    buttons = parser.find_widgets(widget_type="button")
    test("Finds 1 button widget", len(buttons) == 1)

    counters = parser.find_widgets(widget_type="counter")
    test("Finds 1 counter widget", len(counters) == 1)

    by_id = parser.find_widgets(widget_id="abc123")
    test("Finds widget by ID 'abc123'", len(by_id) == 1)
    test("Widget abc123 is a heading", by_id[0][1]["widgetType"] == "heading")


def test_elementor_parser_get_all_widgets():
    """Test getting all widgets summary."""
    print("\n=== Test: ElementorParser.get_all_widgets ===")
    parser = ElementorParser(SAMPLE_ELEMENTOR)
    widgets = parser.get_all_widgets()
    test("Gets 7 widgets total", len(widgets) == 7, f"got {len(widgets)}")
    types = [w["type"] for w in widgets]
    test("Contains heading", "heading" in types)
    test("Contains text-editor", "text-editor" in types)
    test("Contains image", "image" in types)
    test("Contains counter", "counter" in types)
    test("Contains button", "button" in types)
    test("Contains jkit_testimonials", "jkit_testimonials" in types)


def test_elementor_parser_get_all_images():
    """Test finding all images."""
    print("\n=== Test: ElementorParser.get_all_images ===")
    parser = ElementorParser(SAMPLE_ELEMENTOR)
    images = parser.get_all_images()

    test("Finds 4 images total", len(images) == 4, f"got {len(images)}")
    urls = [img["url"] for img in images]
    test("Finds hero-bg.jpg", any("hero-bg.jpg" in u for u in urls))
    test("Finds Doctor2-pose.png", any("Doctor2-pose.png" in u for u in urls))
    test("Finds Testimonial-3.png", any("Testimonial-3.png" in u for u in urls))
    test("Finds Testimonial.png", any("Testimonial.png" in u for u in urls))


def test_elementor_parser_replace_image():
    """Test replacing an image URL."""
    print("\n=== Test: ElementorParser.replace_image ===")
    parser = ElementorParser(SAMPLE_ELEMENTOR)

    old_url = "https://healthcodeanalysis.com/wp-content/uploads/2025/12/Doctor2-pose.png"
    new_url = "https://customer.com/wp-content/uploads/2026/04/new-photo.png"

    count = parser.replace_image(old_url, new_url, new_attachment_id=999)
    test("Replaces 1 image", count == 1)

    images = parser.get_all_images()
    urls = [img["url"] for img in images]
    test("Old URL gone", old_url not in urls)
    test("New URL present", new_url in urls)


def test_elementor_parser_replace_text():
    """Test replacing text by widget ID."""
    print("\n=== Test: ElementorParser.replace_text ===")
    parser = ElementorParser(SAMPLE_ELEMENTOR)

    result = parser.replace_text("abc123", "New Heading Text")
    test("Replace returns True", result is True)

    headings = parser.find_widgets(widget_type="heading")
    test("Heading text updated", headings[0][1]["settings"]["title"] == "New Heading Text")

    result2 = parser.replace_text("nonexistent_id", "Nothing")
    test("Nonexistent ID returns False", result2 is False)


def test_elementor_parser_replace_heading_by_index():
    """Test replacing heading by index."""
    print("\n=== Test: ElementorParser.replace_heading_by_index ===")
    parser = ElementorParser(SAMPLE_ELEMENTOR)

    result = parser.replace_heading_by_index(0, "First Heading Changed")
    test("Index 0 replace succeeds", result is True)

    result = parser.replace_heading_by_index(1, "Second Heading Changed")
    test("Index 1 replace succeeds", result is True)

    result = parser.replace_heading_by_index(99, "Won't work")
    test("Out of range index returns False", result is False)

    headings = parser.find_widgets(widget_type="heading")
    test("First heading text correct", headings[0][1]["settings"]["title"] == "First Heading Changed")
    test("Second heading text correct", headings[1][1]["settings"]["title"] == "Second Heading Changed")


def test_elementor_parser_bulk_replace_domain():
    """Test domain replacement."""
    print("\n=== Test: ElementorParser.bulk_replace_domain ===")
    parser = ElementorParser(SAMPLE_ELEMENTOR)

    count = parser.bulk_replace_domain("healthcodeanalysis.com", "newcustomer.com")
    test("Replaces multiple domain occurrences", count > 0, f"replaced {count}")

    json_str = parser.to_json()
    test("Old domain gone", "healthcodeanalysis.com" not in json_str)
    test("New domain present", "newcustomer.com" in json_str)


def test_elementor_parser_json_roundtrip():
    """Test JSON export/import roundtrip."""
    print("\n=== Test: ElementorParser JSON roundtrip ===")
    parser = ElementorParser(SAMPLE_ELEMENTOR)
    json_str = parser.to_json()
    parser2 = ElementorParser(json_str)
    test("Roundtrip produces same data", parser.to_data() == parser2.to_data())

    # File roundtrip
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write(json_str)
        tmp_path = f.name
    try:
        parser3 = ElementorParser.load_from_file(tmp_path)
        test("File roundtrip works", parser.to_data() == parser3.to_data())
    finally:
        os.unlink(tmp_path)


def test_config_validator_valid():
    """Test valid config passes validation."""
    print("\n=== Test: Config Validator (valid config) ===")
    config = {
        "customer_name": "Test Customer",
        "domain": "test.com",
        "pages": [
            {
                "page_id": 2471,
                "headings": [{"index": 0, "new_text": "Hello"}],
                "texts": [{"index": 0, "new_html": "<p>Hi</p>"}],
                "images": [{"old_url": "test.jpg", "new_file": "assets/test/photo.jpg"}],
                "meta": {"rank_math_title": "Test Page"},
            }
        ],
        "site_settings": {"title": "Test Site"},
    }
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(config, f)
        tmp_path = f.name
    try:
        valid, result = validate_config(tmp_path)
        test("Valid config passes", valid is True)
        test("Returns config dict", result["customer_name"] == "Test Customer")
    except ConfigValidationError as e:
        test("Valid config passes", False, f"errors: {e.errors}")
    finally:
        os.unlink(tmp_path)


def test_config_validator_invalid():
    """Test invalid configs are caught."""
    print("\n=== Test: Config Validator (invalid configs) ===")

    # Missing required fields
    config = {"customer_name": "Test"}
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(config, f)
        tmp_path = f.name
    try:
        validate_config(tmp_path)
        test("Catches missing fields", False)
    except ConfigValidationError as e:
        test("Catches missing 'domain'", any("domain" in err for err in e.errors))
        test("Catches missing 'pages'", any("pages" in err for err in e.errors))
    finally:
        os.unlink(tmp_path)

    # Invalid page_id type
    config = {"customer_name": "Test", "domain": "test.com", "pages": [{"page_id": "not_a_number"}]}
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(config, f)
        tmp_path = f.name
    try:
        validate_config(tmp_path)
        test("Catches invalid page_id type", False)
    except ConfigValidationError as e:
        test("Catches invalid page_id type", any("page_id" in err for err in e.errors))
    finally:
        os.unlink(tmp_path)

    # Invalid domain
    config = {"customer_name": "Test", "domain": "has spaces", "pages": []}
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(config, f)
        tmp_path = f.name
    try:
        validate_config(tmp_path)
        test("Catches invalid domain", False)
    except ConfigValidationError as e:
        test("Catches invalid domain", any("domain" in err.lower() for err in e.errors))
    finally:
        os.unlink(tmp_path)

    # Nonexistent file
    try:
        validate_config("/nonexistent/path.json")
        test("Catches missing file", False)
    except ConfigValidationError as e:
        test("Catches missing file", any("not found" in err for err in e.errors))

    # Invalid JSON
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("{invalid json")
        tmp_path = f.name
    try:
        validate_config(tmp_path)
        test("Catches invalid JSON", False)
    except ConfigValidationError as e:
        test("Catches invalid JSON", any("json" in err.lower() for err in e.errors))
    finally:
        os.unlink(tmp_path)

    # Missing heading new_text
    config = {"customer_name": "T", "domain": "t.com", "pages": [{"page_id": 1, "headings": [{"index": 0}]}]}
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(config, f)
        tmp_path = f.name
    try:
        validate_config(tmp_path)
        test("Catches missing new_text in heading", False)
    except ConfigValidationError as e:
        test("Catches missing new_text in heading", any("new_text" in err for err in e.errors))
    finally:
        os.unlink(tmp_path)


def test_config_template_is_valid_json():
    """Test that the customer template file is valid JSON."""
    print("\n=== Test: Customer Template JSON ===")
    template_path = os.path.join(os.path.dirname(__file__), "..", "configs", "customer-template.json")
    test("Template file exists", os.path.isfile(template_path))
    try:
        with open(template_path) as f:
            data = json.load(f)
        test("Template is valid JSON", True)
        test("Template has customer_name", "customer_name" in data)
        test("Template has domain", "domain" in data)
        test("Template has pages", "pages" in data)
        test("Template has 6 pages", len(data["pages"]) == 6, f"got {len(data['pages'])}")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        test("Template is valid JSON", False, str(e))


def test_wp_client_dry_run():
    """Test WPClient in dry-run mode."""
    print("\n=== Test: WPClient (dry-run) ===")
    client = WPClient(site_url="https://example.com", username="test", app_password="test", dry_run=True)

    test("Client has correct site_url", client.site_url == "https://example.com")
    test("Client has correct api_base", client.api_base == "https://example.com/wp-json")
    test("Client is in dry_run mode", client.dry_run is True)

    # Test dry-run upload
    result = client.upload_image("/fake/path/photo.jpg")
    test("Dry-run upload returns mock data", result["dry_run"] is True)
    test("Dry-run upload has URL", "photo.jpg" in result["url"])
    test("Dry-run upload has ID", result["id"] == 99999)

    # Test dry-run meta update
    result = client.update_post_meta(1, {"rank_math_title": "Test"})
    test("Dry-run meta update works", result["dry_run"] is True)

    # Test dry-run site settings
    result = client.update_site_settings({"title": "Test"})
    test("Dry-run settings update works", result["dry_run"] is True)

    # Test dry-run elementor update
    result = client.update_elementor_data(1, SAMPLE_ELEMENTOR)
    test("Dry-run elementor update works", result["dry_run"] is True)
    test("Dry-run elementor reports widget count", result["widgets"] == 7, f"got {result['widgets']}")

    # Test dry-run cache flush
    result = client.flush_cache()
    test("Dry-run cache flush works", result["dry_run"] is True)


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1 TESTS")
    print("=" * 60)

    test_project_structure()
    test_elementor_parser_find_widgets()
    test_elementor_parser_get_all_widgets()
    test_elementor_parser_get_all_images()
    test_elementor_parser_replace_image()
    test_elementor_parser_replace_text()
    test_elementor_parser_replace_heading_by_index()
    test_elementor_parser_bulk_replace_domain()
    test_elementor_parser_json_roundtrip()
    test_config_validator_valid()
    test_config_validator_invalid()
    test_config_template_is_valid_json()
    test_wp_client_dry_run()

    print()
    print("=" * 60)
    total = PASSED + FAILED
    print(f"RESULTS: {PASSED}/{total} passed, {FAILED} failed")
    print("=" * 60)

    sys.exit(0 if FAILED == 0 else 1)
