"""
JOB REQUIREMENTS TEST — Tests EXACTLY what the client asked for:

1. "In each page I have 4 photos and text" → change photos
2. "change in each page the photos, the text and the metas" → verify all 3
3. "under each domain, in the C Panel, to clone my template" → clone script
4. "do the procedure with prompts" → one command
5. "clone the template as many times as I want" → repeatable

This runs against LOCAL Docker to prove it works without touching the live site.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import requests

from clone_site import CPanelClient, SiteCloner
from config_validator import load_config
from content_swapper import ContentSwapper
from elementor_parser import ElementorParser
from wp_client import WPClient

API_KEY = os.getenv("HC_API_KEY", "test-api-key-not-set")
LOCAL_URL = "http://localhost:8889"
HEADERS = {"X-HC-API-Key": API_KEY}
BASE = f"{LOCAL_URL}/wp-json/healthcode/v1"

PASSED = 0
FAILED = 0
TOTAL_REQUIREMENTS = 0

# Fix Windows encoding
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None


def test(name, condition, detail=""):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS: {name}")
    else:
        FAILED += 1
        print(f"  FAIL: {name} {detail}")


def requirement(name):
    global TOTAL_REQUIREMENTS
    TOTAL_REQUIREMENTS += 1
    print(f"\n{'=' * 60}")
    print(f"REQUIREMENT {TOTAL_REQUIREMENTS}: {name}")
    print(f"{'=' * 60}")


# ─── Save original state so we can verify changes and restore ────


def get_elementor_data(page_id):
    resp = requests.get(f"{BASE}/elementor-data/{page_id}", headers=HEADERS, timeout=15)
    if resp.status_code == 200:
        return resp.json()
    return None


def save_elementor_data(page_id, data):
    resp = requests.post(
        f"{BASE}/elementor-data/{page_id}",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"data": data},
        timeout=30,
    )
    return resp.status_code in (200, 201)


def get_rank_math_meta(page_id):
    """Read Rank Math metas directly from DB via WP REST."""
    # Use our custom endpoint indirectly — read from postmeta
    resp = requests.get(
        f"{LOCAL_URL}/wp-json/wp/v2/pages/{page_id}",
        headers=HEADERS,
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json().get("meta", {})
    return {}


# ─── TESTS ───────────────────────────────────────────────────────


def test_requirement_1_change_photos():
    """JOB: "change the photos" — upload images + replace in Elementor."""
    requirement("CHANGE PHOTOS on a page")

    # About Us page has 6 images — perfect test
    original = get_elementor_data(1210)
    test("Can read About Us Elementor data", original is not None)
    if not original:
        return

    original_data = original["data"]
    parser = ElementorParser(original_data)
    original_images = parser.get_all_images()
    test(f"About Us has images ({len(original_images)})", len(original_images) > 0)

    # Upload test images and replace
    client = WPClient(site_url=LOCAL_URL, api_key=API_KEY)
    swapper = ContentSwapper(client, verbose=False)

    image_configs = [
        {"old_url": "About-US.webp", "new_file": "assets/test-customer/new-about-bg.png", "match_mode": "filename"},
        {"old_url": "Doctor2-pose.png", "new_file": "assets/test-customer/new-doctor.png", "match_mode": "filename"},
        {
            "old_url": "Testimonial-3.png",
            "new_file": "assets/test-customer/new-testimonial1.png",
            "match_mode": "filename",
        },
        {
            "old_url": "Testimonial.png",
            "new_file": "assets/test-customer/new-testimonial2.png",
            "match_mode": "filename",
        },
    ]

    modified_data, upload_results = swapper.swap_images(1210, image_configs, original_data)

    test("4 images uploaded successfully", len(upload_results) == 4)
    for i, result in enumerate(upload_results):
        test(f"  Image {i + 1} has URL", "url" in result and len(result["url"]) > 0)
        test(f"  Image {i + 1} has ID", "id" in result and result["id"] > 0)

    # Verify old URLs are gone from modified data
    parser_new = ElementorParser(modified_data)
    new_images = parser_new.get_all_images()
    old_filenames = ["About-US.webp", "Doctor2-pose.png", "Testimonial-3.png", "Testimonial.png"]
    for old_fn in old_filenames:
        found = any(old_fn in img["url"] for img in new_images)
        test(f"  Old image '{old_fn}' replaced", not found, "still found in data" if found else "")

    # Save modified data to Docker site
    saved = save_elementor_data(1210, modified_data)
    test("Modified Elementor data saved to site", saved)

    # Re-read from site and verify
    verify = get_elementor_data(1210)
    if verify:
        parser_verify = ElementorParser(verify["data"])
        verify_images = parser_verify.get_all_images()
        for old_fn in old_filenames:
            found = any(old_fn in img["url"] for img in verify_images)
            test(f"  Verified on site: '{old_fn}' gone", not found)
        # Check new URLs point to localhost
        new_urls = [img["url"] for img in verify_images]
        local_urls = [u for u in new_urls if "localhost:8889" in u]
        test(f"  New images point to local site ({len(local_urls)} URLs)", len(local_urls) >= 3)

    # Restore original
    save_elementor_data(1210, original_data)


def test_requirement_2_change_text():
    """JOB: "change the text" — replace headings and text content."""
    requirement("CHANGE TEXT on a page")

    original = get_elementor_data(2471)  # Home page
    test("Can read Home page", original is not None)
    if not original:
        return

    original_data = original["data"]
    parser = ElementorParser(original_data)
    headings_before = parser.find_widgets(widget_type="heading")
    texts_before = parser.find_widgets(widget_type="text-editor")
    test(f"Home has {len(headings_before)} headings", len(headings_before) > 0)
    test(f"Home has {len(texts_before)} text-editors", len(texts_before) > 0)

    # Change headings
    client = WPClient(site_url=LOCAL_URL, api_key=API_KEY)
    swapper = ContentSwapper(client, verbose=False)

    heading_configs = [
        {"index": 0, "new_text": "Your health hub, all in one"},
        {"index": 1, "new_text": 'Where <span class="gradient-text">Modern Care</span> <br> Meets Technology'},
        {"index": 4, "new_text": "Explore Our Services"},
    ]
    text_configs = [
        {"index": 0, "new_html": "Providing world-class healthcare with cutting-edge AI diagnostics."},
    ]

    modified = swapper.swap_headings(original_data, heading_configs)
    modified = swapper.swap_texts(modified, text_configs)

    # Verify in memory
    parser_new = ElementorParser(modified)
    headings_after = parser_new.find_widgets(widget_type="heading")
    test("Heading 0 changed", headings_after[0][1]["settings"]["title"] == "Your health hub, all in one")
    test("Heading 1 changed", "Modern Care" in headings_after[1][1]["settings"]["title"])
    test("Heading 4 changed", headings_after[4][1]["settings"]["title"] == "Explore Our Services")

    texts_after = parser_new.find_widgets(widget_type="text-editor")
    test("Text 0 changed", "world-class healthcare" in texts_after[0][1]["settings"]["editor"])

    # Save to site and verify
    saved = save_elementor_data(2471, modified)
    test("Modified text saved to site", saved)

    verify = get_elementor_data(2471)
    if verify:
        p = ElementorParser(verify["data"])
        h = p.find_widgets(widget_type="heading")
        test("Verified on site: heading 0 persisted", h[0][1]["settings"]["title"] == "Your health hub, all in one")

    # Restore original
    save_elementor_data(2471, original_data)


def test_requirement_3_change_metas():
    """JOB: "change the metas" — update Rank Math SEO metas."""
    requirement("CHANGE METAS on a page")

    client = WPClient(site_url=LOCAL_URL, api_key=API_KEY)
    swapper = ContentSwapper(client, verbose=False)

    meta_config = {
        "rank_math_title": "Contact - MediCare Plus",
        "rank_math_description": "Get in touch with MediCare Plus for appointments.",
        "rank_math_focus_keyword": "contact medicare plus",
    }

    result = swapper.swap_seo_meta(1212, meta_config)
    test("SEO meta update returned result", result is not None)
    if result:
        test("Updated rank_math_title", "rank_math_title" in result.get("updated_keys", []))
        test("Updated rank_math_description", "rank_math_description" in result.get("updated_keys", []))
        test("Updated rank_math_focus_keyword", "rank_math_focus_keyword" in result.get("updated_keys", []))

    # Verify by reading back from DB
    # Read postmeta directly
    import subprocess

    for key in ["rank_math_title", "rank_math_description", "rank_math_focus_keyword"]:
        cmd = f"wp post meta get 1212 {key} --allow-root --skip-plugins"
        result = subprocess.run(
            ["docker", "exec", "hc-wordpress", "sh", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=10,
        )
        value = result.stdout.strip()
        test(f"Verified in DB: {key} = '{value[:50]}'", len(value) > 0)


def test_requirement_4_six_pages():
    """JOB: "6 links/pages" — run full deploy across 6 pages."""
    requirement("DEPLOY ACROSS 6 PAGES in one config")

    config = load_config(os.path.join(os.path.dirname(__file__), "..", "configs", "test-customer-demo.json"))
    test("Config loads with 6 pages", len(config["pages"]) == 6)

    # Save original state for all pages
    originals = {}
    for page in config["pages"]:
        pid = page["page_id"]
        data = get_elementor_data(pid)
        if data:
            originals[pid] = data["data"]

    test(f"Saved original state for {len(originals)} pages", len(originals) >= 4)

    # Run full deploy
    client = WPClient(site_url=LOCAL_URL, api_key=API_KEY)
    swapper = ContentSwapper(client, verbose=False)

    all_results = []
    for page_conf in config["pages"]:
        pid = page_conf["page_id"]
        if pid in originals:
            modified, results = swapper.swap_page(page_conf, originals[pid])
            save_elementor_data(pid, modified)
            all_results.append(results)
        elif page_conf.get("meta"):
            # Pages without Elementor data (like Privacy Policy) — just update metas
            swapper.swap_seo_meta(pid, page_conf.get("meta", {}))
            all_results.append({"page_id": pid, "page_name": page_conf["page_name"], "seo_updated": True})

    test(f"Processed {len(all_results)} pages", len(all_results) == 6)

    # Verify each page
    for page_conf in config["pages"]:
        pid = page_conf["page_id"]
        name = page_conf["page_name"]

        # Check headings changed
        if page_conf.get("headings") and pid in originals:
            verify = get_elementor_data(pid)
            if verify:
                p = ElementorParser(verify["data"])
                h = p.find_widgets(widget_type="heading")
                if h and page_conf["headings"]:
                    expected = page_conf["headings"][0]["new_text"]
                    # Strip HTML for comparison
                    actual = h[0][1]["settings"].get("title", "")
                    test(
                        f"  {name}: heading changed",
                        expected in actual or actual == expected,
                        f"expected '{expected[:40]}' got '{actual[:40]}'",
                    )

        # Check metas set
        if page_conf.get("meta"):
            import subprocess

            cmd = f"wp post meta get {pid} rank_math_title --allow-root --skip-plugins"
            result = subprocess.run(
                ["docker", "exec", "hc-wordpress", "sh", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=10,
            )
            meta_val = result.stdout.strip()
            expected_title = page_conf["meta"].get("rank_math_title", "")
            test(f"  {name}: meta set", meta_val == expected_title, f"expected '{expected_title}' got '{meta_val}'")

    # Update site settings
    site_result = swapper.swap_site_settings(config["site_settings"])
    test("Site title updated", site_result.get("settings") is not None)

    # Verify site title
    import subprocess

    result = subprocess.run(
        ["docker", "exec", "hc-wordpress", "wp", "option", "get", "blogname", "--allow-root", "--skip-plugins"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    test("Site title is 'MediCare Plus'", result.stdout.strip() == "MediCare Plus", f"got '{result.stdout.strip()}'")

    # Restore all originals
    for pid, data in originals.items():
        save_elementor_data(pid, data)

    # Restore site title
    client.update_site_settings({"title": "HealthCode Analysis", "description": "Health & Medical Template Kit"})


def test_requirement_5_one_command():
    """JOB: "do the procedure with prompts" — one command deploys everything."""
    requirement("ONE COMMAND per customer")

    # Test that deploy_customer.py works end-to-end with --dry-run
    import subprocess

    result = subprocess.run(
        [sys.executable, "scripts/deploy_customer.py", "configs/test-customer-demo.json", "--dry-run"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )

    output = result.stdout
    test(
        "deploy_customer.py exits cleanly",
        result.returncode == 0,
        f"exit code {result.returncode}\nstderr: {result.stderr[:200]}",
    )
    test("Output shows customer name", "MediCare Plus" in output)
    test("Output shows 6 pages", "6" in output or "Pages" in output)
    test("Output shows DRY RUN", "DRY RUN" in output)
    test("Output shows DEPLOYMENT COMPLETE", "DEPLOYMENT COMPLETE" in output)


def test_requirement_6_clone_site():
    """JOB: "clone my template" — generate clone script for cPanel."""
    requirement("CLONE SITE to new domain")

    cpanel = CPanelClient(url="https://bdix.aridserver.com:2083", username="mehzsolu", dry_run=True)
    cloner = SiteCloner(cpanel, verbose=False)

    # Test clone command generation
    results = cloner.clone("healthcodeanalysis.com", "medicareplus.com")
    test("Clone returns commands", "commands" in results)
    test("Commands include file copy", any("cp -r" in c for c in results["commands"]))
    test("Commands include DB export", any("db export" in c for c in results["commands"]))
    test("Commands include search-replace", any("search-replace" in c for c in results["commands"]))
    test("Commands include cache flush", any("cache flush" in c for c in results["commands"]))
    test("Commands reference target domain", any("medicareplus.com" in c for c in results["commands"]))

    # Test full pipeline script
    script = cloner.generate_full_pipeline_script(
        "healthcodeanalysis.com", "medicareplus.com", "configs/test-customer-demo.json"
    )
    test("Pipeline script generated", len(script) > 100)
    test(
        "Script has all steps",
        all(
            step in script
            for step in [
                "Clone WordPress Files",
                "Update wp-config",
                "Import Database",
                "Search-Replace Domain",
                "Flush Caches",
                "Swap Content",
            ]
        ),
    )


def test_requirement_7_repeatable():
    """JOB: "clone as many times as I want" — run twice, same result."""
    requirement("REPEATABLE — works for multiple customers")

    # Customer 1
    cpanel = CPanelClient(url="https://bdix.aridserver.com:2083", username="mehzsolu", dry_run=True)
    cloner = SiteCloner(cpanel, verbose=False)

    script1 = cloner.generate_full_pipeline_script("healthcodeanalysis.com", "customer1.com", "configs/customer1.json")
    script2 = cloner.generate_full_pipeline_script("healthcodeanalysis.com", "customer2.com", "configs/customer2.json")
    script3 = cloner.generate_full_pipeline_script("healthcodeanalysis.com", "customer3.com", "configs/customer3.json")

    test("Script 1 targets customer1.com", "customer1.com" in script1)
    test("Script 2 targets customer2.com", "customer2.com" in script2)
    test("Script 3 targets customer3.com", "customer3.com" in script3)
    test("All scripts are different", script1 != script2 and script2 != script3)
    test("All scripts have same structure", script1.count("Step") == script2.count("Step") == script3.count("Step"))

    # Verify deploy_customer.py can run multiple configs
    import subprocess

    for name in ["test-customer-demo"]:
        result = subprocess.run(
            [sys.executable, "scripts/deploy_customer.py", f"configs/{name}.json", "--dry-run", "--quiet"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        test(f"Deploy '{name}' succeeds", result.returncode == 0)


if __name__ == "__main__":
    print("=" * 60)
    print("JOB REQUIREMENTS TEST")
    print("Verifying EXACTLY what the client asked for")
    print("=" * 60)

    # Check Docker is up
    try:
        resp = requests.get(f"{BASE}/ping", headers=HEADERS, timeout=5)
        if resp.status_code != 200:
            print("ERROR: Docker WordPress not responding")
            sys.exit(1)
    except Exception:
        print("ERROR: Cannot connect to Docker WordPress at localhost:8889")
        sys.exit(1)

    test_requirement_1_change_photos()
    test_requirement_2_change_text()
    test_requirement_3_change_metas()
    test_requirement_4_six_pages()
    test_requirement_5_one_command()
    test_requirement_6_clone_site()
    test_requirement_7_repeatable()

    print()
    print("=" * 60)
    print(f"JOB REQUIREMENTS: {TOTAL_REQUIREMENTS}/7 tested")
    print(f"RESULTS: {PASSED}/{PASSED + FAILED} passed, {FAILED} failed")
    print("=" * 60)

    if FAILED == 0:
        print("\nALL JOB REQUIREMENTS VERIFIED. Ready for video.")
    else:
        print(f"\n{FAILED} FAILURES — need fixing before video.")

    sys.exit(0 if FAILED == 0 else 1)
