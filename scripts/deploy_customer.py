"""
Master Deploy Script — One command per customer.
Reads customer config, connects to WordPress, swaps all content.

Usage:
    python deploy_customer.py configs/customer-abc.json [--dry-run] [--verbose]
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Ensure scripts dir is in path
sys.path.insert(0, os.path.dirname(__file__))

from config_validator import ConfigValidationError, load_config, print_config_summary
from content_swapper import ContentSwapper
from wp_client import WPClient


def load_env():
    """Load .env file if it exists."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)


def main():
    parser = argparse.ArgumentParser(description="Deploy customer content to WordPress site")
    parser.add_argument("config", help="Path to customer config JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying the site")
    parser.add_argument("--verbose", "-v", action="store_true", default=True, help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    parser.add_argument("--site-url", help="Override WP_SITE_URL from env")
    parser.add_argument("--username", help="Override WP_USERNAME from env")
    parser.add_argument("--app-password", help="Override WP_APP_PASSWORD from env")
    parser.add_argument("--skip-images", action="store_true", help="Skip image uploads")
    parser.add_argument("--skip-seo", action="store_true", help="Skip SEO meta updates")
    parser.add_argument("--skip-site-settings", action="store_true", help="Skip site settings update")
    parser.add_argument("--page-id", type=int, help="Only process a specific page ID")

    args = parser.parse_args()
    verbose = not args.quiet

    # Load environment
    load_env()

    # Load and validate config
    if verbose:
        print("=" * 60)
        print("HealthCode Analysis — Customer Deployment")
        print("=" * 60)
        print()

    try:
        config = load_config(args.config)
    except ConfigValidationError as e:
        print("ERROR: Invalid config file:")
        for err in e.errors:
            print(f"  - {err}")
        sys.exit(1)

    if verbose:
        print_config_summary(config)
        print()

    if args.dry_run:
        print("*** DRY RUN MODE — No changes will be made ***")
        print()

    # Connect to WordPress
    client = WPClient(
        site_url=args.site_url or config.get("domain_url") or config.get("domain") or os.getenv("WP_SITE_URL"),
        username=args.username or os.getenv("WP_USERNAME"),
        app_password=args.app_password or os.getenv("WP_APP_PASSWORD"),
        dry_run=args.dry_run,
    )

    if not args.dry_run:
        if verbose:
            print("Testing connection...")
        conn = client.test_connection()
        if not conn.get("connected"):
            print(f"ERROR: Cannot connect to WordPress: {conn.get('error')}")
            sys.exit(1)
        if verbose:
            print(f"Connected to: {conn.get('title')} ({conn.get('url')})")
            print()

    swapper = ContentSwapper(client, verbose=verbose)
    all_results = []
    start_time = time.time()

    # Process site settings
    site_settings = config.get("site_settings", {})
    if site_settings and not args.skip_site_settings:
        if verbose:
            print("\n--- Site Settings ---")
        results = swapper.swap_site_settings(site_settings)
        all_results.append({"type": "site_settings", "results": results})

    # Process each page
    pages = config.get("pages", [])
    for page_conf in pages:
        page_id = page_conf["page_id"]

        # Skip if --page-id specified and doesn't match
        if args.page_id and page_id != args.page_id:
            continue

        # Skip images if requested
        if args.skip_images:
            page_conf = {**page_conf, "images": []}

        # Skip SEO if requested
        if args.skip_seo:
            page_conf = {**page_conf, "meta": {}}

        # Get current Elementor data
        if args.dry_run:
            # In dry-run, use mock Elementor data
            mock_data = _generate_mock_elementor(page_conf)
            modified_data, page_results = swapper.swap_page(page_conf, mock_data)
        else:
            elementor_data = client.get_elementor_data(page_id)
            if elementor_data is None:
                if verbose:
                    print(f"\n[SKIP] Page {page_id}: No Elementor data found")
                continue

            # Handle response format from our custom endpoint
            if isinstance(elementor_data, dict) and "data" in elementor_data:
                elementor_data = elementor_data["data"]

            modified_data, page_results = swapper.swap_page(page_conf, elementor_data)

            # Save modified Elementor data back
            if verbose:
                print(f"  [SAVE] Writing Elementor data for page {page_id}")
            client.update_elementor_data(page_id, modified_data)

        all_results.append(page_results)

    # Flush cache
    if not args.dry_run:
        if verbose:
            print("\n--- Flushing Caches ---")
        cache_result = client.flush_cache()
        if verbose:
            print(f"  Cache flush: {cache_result}")

    # Summary
    elapsed = time.time() - start_time
    if verbose:
        print()
        print("=" * 60)
        print("DEPLOYMENT COMPLETE")
        print("=" * 60)
        print(f"Customer: {config.get('customer_name')}")
        print(f"Pages processed: {len([r for r in all_results if isinstance(r, dict) and 'page_id' in r])}")
        print(f"Time: {elapsed:.1f}s")
        if args.dry_run:
            print("Mode: DRY RUN (no changes made)")
        print()

    return all_results


def _generate_mock_elementor(page_conf):
    """Generate mock Elementor data for dry-run testing based on page config."""
    elements = []

    # Mock headings
    for i, _h in enumerate(page_conf.get("headings", [])):
        elements.append(
            {
                "id": f"mock_heading_{i}",
                "elType": "widget",
                "widgetType": "heading",
                "settings": {"title": f"[Current Heading {i}]", "size": "h2"},
                "elements": [],
            }
        )

    # Mock text editors
    for i, _t in enumerate(page_conf.get("texts", [])):
        elements.append(
            {
                "id": f"mock_text_{i}",
                "elType": "widget",
                "widgetType": "text-editor",
                "settings": {"editor": f"<p>[Current text {i}]</p>"},
                "elements": [],
            }
        )

    # Mock images
    for i, img in enumerate(page_conf.get("images", [])):
        old_url = img.get("old_url", f"placeholder-{i}.jpg")
        if img.get("match_mode") == "filename":
            full_url = f"https://example.com/wp-content/uploads/2025/12/{old_url}"
        else:
            full_url = old_url
        elements.append(
            {
                "id": f"mock_image_{i}",
                "elType": "widget",
                "widgetType": "image",
                "settings": {"image": {"url": full_url, "id": 100 + i}},
                "elements": [],
            }
        )

    return [{"id": "mock_container", "elType": "container", "settings": {}, "elements": elements}]


if __name__ == "__main__":
    main()
