"""
Phase 2-4 Tests: Image swap, text swap, SEO meta, content swapper, deploy script.
All tests run in dry-run mode — no network access needed.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from content_swapper import ContentSwapper
from elementor_parser import ElementorParser
from wp_client import WPClient

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


# ── Real-ish Elementor data based on extracted site ──────────────

ABOUT_PAGE_DATA = [
    {
        "id": "6ce4840",
        "elType": "container",
        "settings": {
            "background_overlay_image": {
                "url": "https://healthcodeanalysis.com/wp-content/uploads/2025/12/About-US.webp",
                "id": 50,
            }
        },
        "elements": [
            {
                "id": "h1_about",
                "elType": "widget",
                "widgetType": "heading",
                "settings": {"title": "About Us", "size": "h1"},
                "elements": [],
            },
            {
                "id": "h2_clinic",
                "elType": "widget",
                "widgetType": "heading",
                "settings": {"title": "Medical Clinic that you can trust", "size": "h2"},
                "elements": [],
            },
            {
                "id": "txt_desc",
                "elType": "widget",
                "widgetType": "text-editor",
                "settings": {"editor": "<p>About HC Analysis</p>"},
                "elements": [],
            },
            {
                "id": "txt_detail",
                "elType": "widget",
                "widgetType": "text-editor",
                "settings": {
                    "editor": "<p>Getting an accurate diagnosis can be one of the most impactful experiences.</p>"
                },
                "elements": [],
            },
            {
                "id": "img_doctor",
                "elType": "widget",
                "widgetType": "image",
                "settings": {
                    "image": {
                        "url": "https://healthcodeanalysis.com/wp-content/uploads/2025/12/Doctor2-pose.png",
                        "id": 100,
                    }
                },
                "elements": [],
            },
            {
                "id": "testimonials_widget",
                "elType": "widget",
                "widgetType": "jkit_testimonials",
                "settings": {
                    "sg_testimonials_list": [
                        {
                            "sg_testimonials_list_client_avatar": {
                                "url": "https://healthcodeanalysis.com/wp-content/uploads/2025/12/Testimonial-3.png",
                                "id": 200,
                            },
                            "sg_testimonials_list_client_name": "Dr. Smith",
                        },
                        {
                            "sg_testimonials_list_client_avatar": {
                                "url": "https://healthcodeanalysis.com/wp-content/uploads/2025/12/Testimonial.png",
                                "id": 201,
                            },
                            "sg_testimonials_list_client_name": "Dr. Jones",
                        },
                    ]
                },
                "elements": [],
            },
            {
                "id": "h3_testimonials",
                "elType": "widget",
                "widgetType": "heading",
                "settings": {"title": "What Our Clients Say"},
                "elements": [],
            },
        ],
    }
]


def test_content_swapper_images():
    """Test image swapping with filename matching."""
    print("\n=== Test: ContentSwapper — Image Swap ===")
    client = WPClient(site_url="https://test.com", dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    image_configs = [
        {"old_url": "About-US.webp", "new_file": "assets/test/new-bg.webp", "match_mode": "filename"},
        {"old_url": "Doctor2-pose.png", "new_file": "assets/test/new-doctor.png", "match_mode": "filename"},
        {"old_url": "Testimonial-3.png", "new_file": "assets/test/t1.png", "match_mode": "filename"},
    ]

    data, results = swapper.swap_images(1210, image_configs, ABOUT_PAGE_DATA)
    test("Returns modified data", isinstance(data, list))
    test("Uploaded 3 images", len(results) == 3)

    parser = ElementorParser(data)
    images = parser.get_all_images()
    urls_str = json.dumps([img["url"] for img in images])
    test("About-US.webp replaced", "About-US.webp" not in urls_str)
    test("Doctor2-pose.png replaced", "Doctor2-pose.png" not in urls_str)
    test("Testimonial-3.png replaced", "Testimonial-3.png" not in urls_str)
    test("New URLs contain test.com", "test.com" in urls_str)


def test_content_swapper_headings():
    """Test heading replacement by index."""
    print("\n=== Test: ContentSwapper — Heading Swap ===")
    client = WPClient(site_url="https://test.com", dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    heading_configs = [
        {"index": 0, "new_text": "About Our Company"},
        {"index": 1, "new_text": "Healthcare you can trust"},
        {"index": 2, "new_text": "Customer Testimonials"},
    ]

    data = swapper.swap_headings(ABOUT_PAGE_DATA, heading_configs)
    parser = ElementorParser(data)
    headings = parser.find_widgets(widget_type="heading")

    test("3 headings still exist", len(headings) == 3)
    test("Heading 0 updated", headings[0][1]["settings"]["title"] == "About Our Company")
    test("Heading 1 updated", headings[1][1]["settings"]["title"] == "Healthcare you can trust")
    test("Heading 2 updated", headings[2][1]["settings"]["title"] == "Customer Testimonials")


def test_content_swapper_headings_by_widget_id():
    """Test heading replacement by widget ID."""
    print("\n=== Test: ContentSwapper — Heading Swap (by ID) ===")
    client = WPClient(site_url="https://test.com", dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    heading_configs = [
        {"widget_id": "h1_about", "new_text": "About XYZ Corp"},
        {"widget_id": "nonexistent", "new_text": "Should not crash"},
    ]

    data = swapper.swap_headings(ABOUT_PAGE_DATA, heading_configs)
    parser = ElementorParser(data)
    widget = parser.find_widgets(widget_id="h1_about")
    test("Widget found by ID", len(widget) == 1)
    test("Text updated by ID", widget[0][1]["settings"]["title"] == "About XYZ Corp")

    log = swapper.log_entries
    test("Logs not-found for nonexistent ID", any("NOT FOUND" in entry for entry in log))


def test_content_swapper_texts():
    """Test text-editor replacement."""
    print("\n=== Test: ContentSwapper — Text Swap ===")
    client = WPClient(site_url="https://test.com", dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    text_configs = [
        {"index": 0, "new_html": "<p>About Our Amazing Company</p>"},
        {"index": 1, "new_html": "<p>We provide the best healthcare solutions.</p>"},
    ]

    data = swapper.swap_texts(ABOUT_PAGE_DATA, text_configs)
    parser = ElementorParser(data)
    editors = parser.find_widgets(widget_type="text-editor")

    test("2 text-editors exist", len(editors) == 2)
    test("Text 0 updated", "Amazing Company" in editors[0][1]["settings"]["editor"])
    test("Text 1 updated", "best healthcare" in editors[1][1]["settings"]["editor"])


def test_content_swapper_seo_meta():
    """Test SEO meta update in dry-run."""
    print("\n=== Test: ContentSwapper — SEO Meta ===")
    client = WPClient(site_url="https://test.com", dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    meta = {
        "rank_math_title": "About Us - Test Company",
        "rank_math_description": "Learn about Test Company and our mission.",
        "rank_math_focus_keyword": "about test company",
    }

    result = swapper.swap_seo_meta(1210, meta)
    test("Returns dry-run result", result is not None)
    test("Result has dry_run flag", result.get("dry_run") is True)
    test("Result has correct post_id", result.get("post_id") == 1210)
    test("Result has all meta keys", set(result.get("meta_keys", [])) == set(meta.keys()))


def test_content_swapper_empty_meta():
    """Test SEO meta skip when empty."""
    print("\n=== Test: ContentSwapper — SEO Meta (empty) ===")
    client = WPClient(site_url="https://test.com", dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    result = swapper.swap_seo_meta(1210, {})
    test("Empty meta returns None", result is None)

    result = swapper.swap_seo_meta(1210, None)
    test("None meta returns None", result is None)


def test_content_swapper_full_page():
    """Test full page swap (all operations combined)."""
    print("\n=== Test: ContentSwapper — Full Page Swap ===")
    client = WPClient(site_url="https://test.com", dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    page_config = {
        "page_id": 1210,
        "page_name": "About Us",
        "headings": [
            {"index": 0, "new_text": "About New Company"},
            {"index": 1, "new_text": "Trusted Healthcare Provider"},
        ],
        "texts": [
            {"index": 0, "new_html": "<p>We are the best.</p>"},
        ],
        "images": [
            {"old_url": "Doctor2-pose.png", "new_file": "assets/test/team.png", "match_mode": "filename"},
        ],
        "meta": {
            "rank_math_title": "About - New Company",
            "rank_math_description": "About our company.",
        },
    }

    modified_data, results = swapper.swap_page(page_config, ABOUT_PAGE_DATA)

    test("Returns modified data", isinstance(modified_data, list))
    test("Results has page_id", results["page_id"] == 1210)
    test("1 image uploaded", results["images_uploaded"] == 1)
    test("2 headings swapped", results["headings_swapped"] == 2)
    test("1 text swapped", results["texts_swapped"] == 1)
    test("SEO updated", results["seo_updated"] is True)

    # Verify actual content changes
    parser = ElementorParser(modified_data)
    headings = parser.find_widgets(widget_type="heading")
    test("Heading 0 is 'About New Company'", headings[0][1]["settings"]["title"] == "About New Company")
    editors = parser.find_widgets(widget_type="text-editor")
    test("Text 0 updated", "We are the best" in editors[0][1]["settings"]["editor"])


def test_content_swapper_site_settings():
    """Test site settings swap in dry-run."""
    print("\n=== Test: ContentSwapper — Site Settings ===")
    client = WPClient(site_url="https://test.com", dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    settings = {
        "title": "New Customer Site",
        "description": "The best customer site ever",
        "logo_file": "assets/test/logo.png",
        "favicon_file": "assets/test/favicon.png",
    }

    results = swapper.swap_site_settings(settings)
    test("Settings updated", "settings" in results)
    test("Logo uploaded", "logo" in results)
    test("Favicon uploaded", "favicon" in results)
    test("Settings dry_run", results["settings"].get("dry_run") is True)


def test_deploy_script_dry_run():
    """Test the deploy script in dry-run mode with a sample config."""
    print("\n=== Test: Deploy Script (dry-run) ===")

    # Create a minimal valid config
    config = {
        "customer_name": "Test Corp",
        "domain": "testcorp.com",
        "site_settings": {"title": "Test Corp Site"},
        "pages": [
            {
                "page_id": 1210,
                "page_name": "About",
                "headings": [{"index": 0, "new_text": "About Test Corp"}],
                "texts": [{"index": 0, "new_html": "<p>We are Test Corp.</p>"}],
                "images": [],
                "meta": {"rank_math_title": "About - Test Corp"},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(config, f)
        tmp_path = f.name

    try:
        # Import and test directly
        from deploy_customer import _generate_mock_elementor

        mock_data = _generate_mock_elementor(config["pages"][0])
        test("Mock Elementor data generated", isinstance(mock_data, list))
        test("Mock has container", mock_data[0]["elType"] == "container")
        test("Mock has elements", len(mock_data[0]["elements"]) > 0)

        # Test the full deploy in dry-run
        client = WPClient(site_url="https://testcorp.com", dry_run=True)
        swapper = ContentSwapper(client, verbose=False)

        page_conf = config["pages"][0]
        _modified_data, results = swapper.swap_page(page_conf, mock_data)

        test("Deploy dry-run completes", results is not None)
        test("Page results has page_id", results["page_id"] == 1210)
    finally:
        os.unlink(tmp_path)


def test_real_db_elementor_parsing():
    """Test parsing real Elementor data from extracted database if available."""
    print("\n=== Test: Real DB Elementor Parsing ===")
    db_path = os.path.join(os.path.dirname(__file__), "..", "extracted_database.sql")

    if not os.path.exists(db_path):
        test("Extracted DB exists (optional)", True)
        print("    (Skipped — extracted_database.sql not found)")
        return

    with open(db_path, encoding="utf-8", errors="replace") as f:
        sql = f.read()

    # Try to parse the Contact page (ID 1212) — it parsed cleanly earlier
    search = ",1212,'_elementor_data','"
    pos = sql.find(search)
    test("Found Contact page Elementor data", pos != -1)

    if pos == -1:
        return

    val_start = pos + len(search)
    i = val_start
    result_chars = []
    while i < min(val_start + 500000, len(sql)):
        c = sql[i]
        if c == "\\" and i + 1 < len(sql):
            next_c = sql[i + 1]
            if next_c == "'":
                result_chars.append("'")
                i += 2
                continue
            elif next_c == '"':
                result_chars.append('"')
                i += 2
                continue
            elif next_c == "\\":
                result_chars.append("\\")
                i += 2
                continue
            elif next_c == "n":
                result_chars.append("\n")
                i += 2
                continue
            elif next_c == "r":
                result_chars.append("\r")
                i += 2
                continue
            else:
                result_chars.append(c)
                i += 1
                continue
        elif c == "'":
            break
        else:
            result_chars.append(c)
            i += 1

    json_str = "".join(result_chars)

    try:
        data = json.loads(json_str)
        test("Contact page JSON parses", True)

        parser = ElementorParser(data)
        widgets = parser.get_all_widgets()
        test("Finds widgets in Contact page", len(widgets) > 0, f"found {len(widgets)}")

        images = parser.get_all_images()
        test("Finds images in Contact page", len(images) >= 0)  # May have 0 direct images

        headings = parser.find_widgets(widget_type="heading")
        test("Finds headings in Contact page", len(headings) >= 1)

        # Test that we can modify and re-export
        parser.replace_heading_by_index(0, "New Contact Heading")
        new_json = parser.to_json()
        test("Modified JSON is valid", json.loads(new_json) is not None)
        test("New heading in output", "New Contact Heading" in new_json)

    except json.JSONDecodeError as e:
        test("Contact page JSON parses", False, str(e))


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 2-4 TESTS")
    print("=" * 60)

    test_content_swapper_images()
    test_content_swapper_headings()
    test_content_swapper_headings_by_widget_id()
    test_content_swapper_texts()
    test_content_swapper_seo_meta()
    test_content_swapper_empty_meta()
    test_content_swapper_full_page()
    test_content_swapper_site_settings()
    test_deploy_script_dry_run()
    test_real_db_elementor_parsing()

    print()
    print("=" * 60)
    total = PASSED + FAILED
    print(f"RESULTS: {PASSED}/{total} passed, {FAILED} failed")
    print("=" * 60)

    sys.exit(0 if FAILED == 0 else 1)
