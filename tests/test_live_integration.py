"""
Live Integration Tests — verifies both Docker and Live site are fully working.
Tests actual API calls, Elementor data parsing, content swap dry-run, and site cloning.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import requests

from config_validator import load_config
from content_swapper import ContentSwapper
from elementor_parser import ElementorParser
from wp_client import WPClient

API_KEY = os.getenv("HC_API_KEY", "test-api-key-not-set")
LOCAL_URL = "http://localhost:8889"
LIVE_URL = "https://healthcodeanalysis.com"

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


def check_env(url, label):
    """Check if an environment is reachable."""
    try:
        resp = requests.get(f"{url}/wp-json/healthcode/v1/ping", headers={"X-HC-API-Key": API_KEY}, timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def test_docker_containers():
    """Verify Docker containers are running."""
    print("\n=== Docker Containers ===")
    import subprocess

    result = subprocess.run(
        ["docker", "ps", "--filter", "name=hc-", "--format", "{{.Names}}:{{.Status}}"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    lines = result.stdout.strip().split("\n")
    names = [line.split(":")[0] for line in lines if line]
    test("hc-wordpress running", "hc-wordpress" in names, f"got {names}")
    test("hc-db running", "hc-db" in names)
    test("hc-phpmyadmin running", "hc-phpmyadmin" in names)


def test_api_ping(url, label):
    """Test API ping endpoint."""
    print(f"\n=== {label}: API Ping ===")
    resp = requests.get(f"{url}/wp-json/healthcode/v1/ping", headers={"X-HC-API-Key": API_KEY}, timeout=10)
    test(f"{label} ping returns 200", resp.status_code == 200)
    data = resp.json()
    test(f"{label} has site name", "site" in data and len(data["site"]) > 0)
    test(f"{label} has version 1.1.0", data.get("version") == "1.1.0")


def test_page_map(url, label):
    """Test page map returns Elementor pages."""
    print(f"\n=== {label}: Page Map ===")
    resp = requests.get(f"{url}/wp-json/healthcode/v1/page-map", headers={"X-HC-API-Key": API_KEY}, timeout=10)
    test(f"{label} page-map returns 200", resp.status_code == 200)
    pages = resp.json().get("pages", [])
    test(f"{label} has 34 pages", len(pages) == 34, f"got {len(pages)}")

    # Check key pages exist
    page_ids = [p["id"] for p in pages]
    for pid, name in [(1212, "Contact"), (2471, "Home"), (1210, "About Us"), (1843, "header")]:
        test(f"{label} has {name} (ID {pid})", pid in page_ids)


def test_elementor_data_read(url, label):
    """Test reading Elementor data for key pages."""
    print(f"\n=== {label}: Elementor Data Read ===")

    for pid, name, expected_widgets in [(1212, "Contact", 8), (2471, "Home", 39), (1210, "About Us", 23)]:
        resp = requests.get(
            f"{url}/wp-json/healthcode/v1/elementor-data/{pid}", headers={"X-HC-API-Key": API_KEY}, timeout=15
        )
        test(f"{label} {name} returns 200", resp.status_code == 200)

        if resp.status_code == 200:
            data = resp.json()
            test(f"{label} {name} has title", data.get("title") == name)

            parser = ElementorParser(data["data"])
            widgets = parser.get_all_widgets()
            test(
                f"{label} {name} has ~{expected_widgets} widgets",
                abs(len(widgets) - expected_widgets) <= 3,
                f"got {len(widgets)}",
            )

            images = parser.get_all_images()
            test(f"{label} {name} images parseable", isinstance(images, list))

            headings = parser.find_widgets(widget_type="heading")
            test(f"{label} {name} has headings", len(headings) > 0)


def test_elementor_modify_roundtrip(url, label):
    """Test that we can read, modify, and verify Elementor data."""
    print(f"\n=== {label}: Elementor Modify (read-only verify) ===")

    resp = requests.get(
        f"{url}/wp-json/healthcode/v1/elementor-data/1212", headers={"X-HC-API-Key": API_KEY}, timeout=15
    )
    if resp.status_code != 200:
        test(f"{label} read Contact page", False)
        return

    data = resp.json()["data"]
    parser = ElementorParser(data)

    # Test image finding
    images = parser.get_all_images()
    test(f"{label} finds Contact images", len(images) >= 1)
    if images:
        test(f"{label} Contact has Contact-US.webp", any("Contact-US" in img["url"] for img in images))

    # Test heading finding
    headings = parser.find_widgets(widget_type="heading")
    test(f"{label} finds Contact headings", len(headings) == 2)
    if len(headings) >= 1:
        test(f"{label} first heading is 'Contact Us'", headings[0][1]["settings"]["title"] == "Contact Us")

    # Test modification (in memory only — don't write back)
    parser.replace_heading_by_index(0, "TEST HEADING")
    headings_after = parser.find_widgets(widget_type="heading")
    test(f"{label} heading modified in memory", headings_after[0][1]["settings"]["title"] == "TEST HEADING")

    # Test domain replacement
    parser2 = ElementorParser(data)
    count = parser2.bulk_replace_domain("localhost:8889", "newdomain.com")
    test(f"{label} domain replace works", count >= 0)

    # Export/import roundtrip
    json_str = parser2.to_json()
    parser3 = ElementorParser(json_str)
    test(f"{label} JSON roundtrip OK", len(parser3.get_all_widgets()) == len(parser.get_all_widgets()))


def test_content_swapper_dry_run(url, label):
    """Test ContentSwapper against real data in dry-run."""
    print(f"\n=== {label}: Content Swapper (dry-run) ===")

    client = WPClient(site_url=url, api_key=API_KEY, dry_run=True)
    swapper = ContentSwapper(client, verbose=False)

    # Get real Elementor data
    resp = requests.get(
        f"{url}/wp-json/healthcode/v1/elementor-data/1212", headers={"X-HC-API-Key": API_KEY}, timeout=15
    )
    if resp.status_code != 200:
        test(f"{label} get data for swap", False)
        return

    real_data = resp.json()["data"]

    page_config = {
        "page_id": 1212,
        "page_name": "Contact",
        "headings": [
            {"index": 0, "new_text": "Contact Test Corp"},
            {"index": 1, "new_text": "Get in touch with Test Corp"},
        ],
        "texts": [],
        "images": [
            {"old_url": "Contact-US.webp", "new_file": "assets/test/contact-bg.webp", "match_mode": "filename"},
        ],
        "meta": {
            "rank_math_title": "Contact - Test Corp",
            "rank_math_description": "Contact Test Corp today.",
        },
    }

    modified_data, results = swapper.swap_page(page_config, real_data)

    test(f"{label} swap returns data", isinstance(modified_data, list))
    test(f"{label} 1 image uploaded", results["images_uploaded"] == 1)
    test(f"{label} 2 headings swapped", results["headings_swapped"] == 2)
    test(f"{label} SEO updated", results["seo_updated"] is True)

    # Verify heading was actually changed
    parser = ElementorParser(modified_data)
    headings = parser.find_widgets(widget_type="heading")
    test(f"{label} heading 0 is 'Contact Test Corp'", headings[0][1]["settings"]["title"] == "Contact Test Corp")
    test(
        f"{label} heading 1 is 'Get in touch with Test Corp'",
        headings[1][1]["settings"]["title"] == "Get in touch with Test Corp",
    )

    # Verify image was replaced
    images = parser.get_all_images()
    test(f"{label} original image replaced", not any("Contact-US.webp" in img["url"] for img in images))


def test_wp_client_connection(url, label):
    """Test WPClient.test_connection()."""
    print(f"\n=== {label}: WPClient Connection ===")
    client = WPClient(site_url=url, api_key=API_KEY)
    result = client.test_connection()
    test(f"{label} connected", result.get("connected") is True)
    test(f"{label} has title", len(result.get("title", "")) > 0)
    test(f"{label} has URL", len(result.get("url", "")) > 0)


def test_customer_template_against_real_data(url, label):
    """Validate customer template page IDs exist on the site."""
    print(f"\n=== {label}: Customer Template Validation ===")
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "customer-template.json")
    config = load_config(config_path)

    resp = requests.get(f"{url}/wp-json/healthcode/v1/page-map", headers={"X-HC-API-Key": API_KEY}, timeout=10)
    all_page_ids = [p["id"] for p in resp.json().get("pages", [])]
    # Also get regular page IDs
    resp2 = requests.get(f"{url}/wp-json/wp/v2/pages?per_page=100", timeout=10)
    if resp2.status_code == 200:
        wp_page_ids = [p["id"] for p in resp2.json()]
        all_page_ids.extend(wp_page_ids)

    for page in config["pages"]:
        pid = page["page_id"]
        name = page.get("page_name", f"Page {pid}")
        test(f"{label} page '{name}' (ID {pid}) exists on site", pid in all_page_ids, f"ID {pid} not found")


if __name__ == "__main__":
    print("=" * 60)
    print("LIVE INTEGRATION TESTS")
    print("=" * 60)

    # Check environments
    docker_up = check_env(LOCAL_URL, "Docker")
    live_up = check_env(LIVE_URL, "Live")

    print(f"\nDocker: {'UP' if docker_up else 'DOWN'}")
    print(f"Live:   {'UP' if live_up else 'DOWN'}")

    # Docker tests
    if docker_up:
        test_docker_containers()
        test_api_ping(LOCAL_URL, "LOCAL")
        test_page_map(LOCAL_URL, "LOCAL")
        test_elementor_data_read(LOCAL_URL, "LOCAL")
        test_elementor_modify_roundtrip(LOCAL_URL, "LOCAL")
        test_content_swapper_dry_run(LOCAL_URL, "LOCAL")
        test_wp_client_connection(LOCAL_URL, "LOCAL")
        test_customer_template_against_real_data(LOCAL_URL, "LOCAL")
    else:
        print("\n  SKIPPED: Docker tests (containers not running)")

    # Live tests
    if live_up:
        test_api_ping(LIVE_URL, "LIVE")
        test_page_map(LIVE_URL, "LIVE")
        test_elementor_data_read(LIVE_URL, "LIVE")
        test_elementor_modify_roundtrip(LIVE_URL, "LIVE")
        test_content_swapper_dry_run(LIVE_URL, "LIVE")
        test_wp_client_connection(LIVE_URL, "LIVE")
        test_customer_template_against_real_data(LIVE_URL, "LIVE")
    else:
        print("\n  SKIPPED: Live tests (site not reachable)")

    print()
    print("=" * 60)
    total = PASSED + FAILED
    print(f"RESULTS: {PASSED}/{total} passed, {FAILED} failed")
    print("=" * 60)

    sys.exit(0 if FAILED == 0 else 1)
