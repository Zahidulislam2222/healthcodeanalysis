#!/usr/bin/env python3
"""End-to-end swap tests — verifies actual image/text/heading/SEO/domain swapping."""

import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from config_validator import load_config
from content_swapper import ContentSwapper
from elementor_parser import ElementorParser

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name} — {detail}")
        failed += 1


# ── Realistic Elementor page data (mirrors About Us page) ──
ABOUT_PAGE_DATA = [
    {
        "id": "sec_hero",
        "elType": "section",
        "elements": [
            {
                "id": "col_hero",
                "elType": "column",
                "elements": [
                    {"id": "h_main", "elType": "widget", "widgetType": "heading", "settings": {"title": "About Us"}},
                    {
                        "id": "h_sub",
                        "elType": "widget",
                        "widgetType": "heading",
                        "settings": {"title": "A clinic you can trust"},
                    },
                    {
                        "id": "txt_about",
                        "elType": "widget",
                        "widgetType": "text-editor",
                        "settings": {"editor": "<p>HealthCode Analysis provides top-tier medical reviews.</p>"},
                    },
                    {
                        "id": "img_bg",
                        "elType": "widget",
                        "widgetType": "image",
                        "settings": {
                            "image": {
                                "url": "https://healthcodeanalysis.com/wp-content/uploads/2024/01/About-US.webp",
                                "id": 100,
                            }
                        },
                    },
                    {
                        "id": "img_doctor",
                        "elType": "widget",
                        "widgetType": "image",
                        "settings": {
                            "image": {
                                "url": "https://healthcodeanalysis.com/wp-content/uploads/2024/01/Doctor2-pose.png",
                                "id": 101,
                            }
                        },
                    },
                ],
            }
        ],
    },
    {
        "id": "sec_testimonials",
        "elType": "section",
        "elements": [
            {
                "id": "col_test",
                "elType": "column",
                "elements": [
                    {
                        "id": "img_t1",
                        "elType": "widget",
                        "widgetType": "image",
                        "settings": {
                            "image": {
                                "url": "https://healthcodeanalysis.com/wp-content/uploads/2024/01/Testimonial-3.png",
                                "id": 102,
                            }
                        },
                    },
                    {
                        "id": "img_t2",
                        "elType": "widget",
                        "widgetType": "image",
                        "settings": {
                            "image": {
                                "url": "https://healthcodeanalysis.com/wp-content/uploads/2024/01/Testimonial.png",
                                "id": 103,
                            }
                        },
                    },
                ],
            }
        ],
    },
]


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 1: Swap 4 images (filename match mode)")
print("=" * 60)

parser = ElementorParser(ABOUT_PAGE_DATA)

# Verify we find all 4
images_before = parser.get_all_images()
check("Found 4 images before swap", len(images_before) == 4, f"got {len(images_before)}")

# Do filename-mode swaps (same logic as content_swapper.py lines 67-75)
swaps = [
    ("About-US.webp", "https://newsite.com/uploads/new-about.webp", 200),
    ("Doctor2-pose.png", "https://newsite.com/uploads/team.png", 201),
    ("Testimonial-3.png", "https://newsite.com/uploads/test1.png", 202),
    ("Testimonial.png", "https://newsite.com/uploads/test2.png", 203),
]

for old_fn, new_url, new_id in swaps:
    all_imgs = parser.get_all_images()
    replaced = 0
    for img in all_imgs:
        if old_fn in img["url"]:
            count = parser.replace_image(img["url"], new_url, new_id)
            replaced += count
    check(f"Swapped '{old_fn}' ({replaced} replacements)", replaced >= 1)

# Verify after
result1 = parser.to_data()
result1_json = json.dumps(result1)
check("No old domain URLs remain", "healthcodeanalysis.com" not in result1_json)
check("New URLs present", "newsite.com" in result1_json)

images_after = ElementorParser(result1).get_all_images()
check("Still 4 images after swap", len(images_after) == 4, f"got {len(images_after)}")
for img in images_after:
    check(f"Image URL updated: {img['url'][:50]}", "newsite.com" in img["url"])

# Verify attachment IDs updated
widgets = result1[0]["elements"][0]["elements"]
for w in widgets:
    if w["widgetType"] == "image":
        aid = w["settings"]["image"]["id"]
        check(f"Attachment ID updated for {w['id']}", aid >= 200, f"got {aid}")
widgets2 = result1[1]["elements"][0]["elements"]
for w in widgets2:
    aid = w["settings"]["image"]["id"]
    check(f"Attachment ID updated for {w['id']}", aid >= 200, f"got {aid}")

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 2: Swap headings by index (6 headings like Home page)")
print("=" * 60)

HOME_DATA = [
    {
        "id": "s1",
        "elType": "section",
        "elements": [
            {
                "id": "c1",
                "elType": "column",
                "elements": [
                    {"id": "h0", "elType": "widget", "widgetType": "heading", "settings": {"title": "Original Hero"}},
                    {
                        "id": "h1",
                        "elType": "widget",
                        "widgetType": "heading",
                        "settings": {"title": "Where <span>HealthCode</span> Meets Innovation"},
                    },
                    {
                        "id": "h2",
                        "elType": "widget",
                        "widgetType": "heading",
                        "settings": {"title": "Choose Your Path"},
                    },
                ],
            }
        ],
    },
    {
        "id": "s2",
        "elType": "section",
        "elements": [
            {
                "id": "c2",
                "elType": "column",
                "elements": [
                    {"id": "h3", "elType": "widget", "widgetType": "heading", "settings": {"title": "Section 1"}},
                    {"id": "h4", "elType": "widget", "widgetType": "heading", "settings": {"title": "Section 2"}},
                    {"id": "h5", "elType": "widget", "widgetType": "heading", "settings": {"title": "Section 3"}},
                ],
            }
        ],
    },
]

parser2 = ElementorParser(HOME_DATA)

heading_swaps = [
    (0, "Your main hero tagline"),
    (1, 'Where <span class="gradient-text">Your Brand</span> <br> Meets Innovation'),
    (2, "Choose Your Path Updated"),
    (3, "New Section 1 Title"),
    (4, "New Section 2 Title"),
    (5, "New Section 3 Title"),
]

for idx, new_text in heading_swaps:
    result = parser2.replace_heading_by_index(idx, new_text)
    check(f"Heading[{idx}] swap returned True", result is True or result is None or result)

r2 = parser2.to_data()
r2_json = json.dumps(r2)

check("Old 'Original Hero' gone", "Original Hero" not in r2_json)
check("New hero tagline present", "Your main hero tagline" in r2_json)
check("HTML preserved in heading", "gradient-text" in r2_json)
check("Old 'Section 1' replaced", '"Section 1"' not in r2_json or "New Section 1 Title" in r2_json)
check("New section titles present", "New Section 2 Title" in r2_json and "New Section 3 Title" in r2_json)

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 3: Swap text-editor widgets by index")
print("=" * 60)

TEXT_DATA = [
    {
        "id": "s1",
        "elType": "section",
        "elements": [
            {
                "id": "c1",
                "elType": "column",
                "elements": [
                    {
                        "id": "t0",
                        "elType": "widget",
                        "widgetType": "text-editor",
                        "settings": {"editor": "<p>Original description paragraph one.</p>"},
                    },
                    {
                        "id": "t1",
                        "elType": "widget",
                        "widgetType": "text-editor",
                        "settings": {"editor": "<p>Original secondary text block.</p>"},
                    },
                ],
            }
        ],
    }
]

parser3 = ElementorParser(TEXT_DATA)
parser3.replace_text_editor_by_index(0, "Your main description paragraph here.")
parser3.replace_text_editor_by_index(1, "Secondary description here.")

r3 = parser3.to_data()
r3_json = json.dumps(r3)

check("Old text 0 gone", "Original description paragraph one" not in r3_json)
check("Old text 1 gone", "Original secondary text block" not in r3_json)
check("New text 0 present", "Your main description paragraph here." in r3_json)
check("New text 1 present", "Secondary description here." in r3_json)

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 4: Bulk domain replacement")
print("=" * 60)

DOMAIN_DATA = [
    {
        "id": "s1",
        "elType": "section",
        "elements": [
            {
                "id": "c1",
                "elType": "column",
                "elements": [
                    {
                        "id": "img1",
                        "elType": "widget",
                        "widgetType": "image",
                        "settings": {
                            "image": {"url": "https://healthcodeanalysis.com/wp-content/uploads/photo.jpg", "id": 1},
                            "link": {"url": "https://healthcodeanalysis.com/about"},
                        },
                    },
                    {
                        "id": "txt1",
                        "elType": "widget",
                        "widgetType": "text-editor",
                        "settings": {"editor": '<p>Visit <a href="https://healthcodeanalysis.com">our site</a></p>'},
                    },
                    {
                        "id": "btn1",
                        "elType": "widget",
                        "widgetType": "button",
                        "settings": {"link": {"url": "https://healthcodeanalysis.com/contact"}, "text": "Contact Us"},
                    },
                ],
            }
        ],
    }
]

parser4 = ElementorParser(DOMAIN_DATA)
count = parser4.bulk_replace_domain("healthcodeanalysis.com", "newcustomer.com")
check(f"Domain replaced ({count} refs)", count >= 4, f"only {count}")

r4_json = parser4.to_json()
check("No old domain left", "healthcodeanalysis.com" not in r4_json)
check("New domain present", "newcustomer.com" in r4_json)

r4 = parser4.to_data()
check("Image URL updated", "newcustomer.com" in r4[0]["elements"][0]["elements"][0]["settings"]["image"]["url"])
check("Link URL updated", "newcustomer.com" in r4[0]["elements"][0]["elements"][0]["settings"]["link"]["url"])
check("Text link updated", "newcustomer.com" in r4[0]["elements"][0]["elements"][1]["settings"]["editor"])
check("Button URL updated", "newcustomer.com" in r4[0]["elements"][0]["elements"][2]["settings"]["link"]["url"])

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 5: Config validation (customer-template.json)")
print("=" * 60)

config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "customer-template.json")
config = load_config(config_path)
check("Config validates successfully", config is not None)
check("Has customer_name", "customer_name" in config)
check("Has domain", "domain" in config)
check("Has 6 pages", len(config.get("pages", [])) == 6, f"got {len(config.get('pages', []))}")
check("Has site_settings", "site_settings" in config)
check("Site settings has title", "title" in config.get("site_settings", {}))
check("Site settings has logo_file", "logo_file" in config.get("site_settings", {}))
check("Site settings has favicon_file", "favicon_file" in config.get("site_settings", {}))

# Verify each page has required fields
for page in config["pages"]:
    pid = page["page_id"]
    pname = page.get("page_name", f"ID={pid}")
    check(f"Page '{pname}' has page_id", "page_id" in page)
    check(f"Page '{pname}' has headings list", isinstance(page.get("headings"), list))
    check(f"Page '{pname}' has texts list", isinstance(page.get("texts"), list))
    check(f"Page '{pname}' has images list", isinstance(page.get("images"), list))
    check(f"Page '{pname}' has meta dict", isinstance(page.get("meta"), dict))
    check(f"Page '{pname}' has rank_math_title", "rank_math_title" in page.get("meta", {}))
    check(f"Page '{pname}' has rank_math_description", "rank_math_description" in page.get("meta", {}))

# Verify About Us page has 4 images (job requirement)
about_page = next(p for p in config["pages"] if p["page_id"] == 1210)
check("About Us has 4 images", len(about_page["images"]) == 4, f"got {len(about_page['images'])}")
for img in about_page["images"]:
    check(f"Image '{img['old_url']}' has match_mode", "match_mode" in img)
    check(f"Image '{img['old_url']}' has new_file", "new_file" in img)

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 6: deploy_customer.py --dry-run end-to-end")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "scripts/deploy_customer.py", "configs/customer-template.json", "--dry-run"],
    capture_output=True,
    text=True,
    cwd=os.path.join(os.path.dirname(__file__), ".."),
)
output = result.stdout + result.stderr
check("deploy --dry-run exits 0", result.returncode == 0, f"exit={result.returncode}\n{output[:500]}")
check("DRY RUN mode shown", "DRY RUN" in output, output[:200])
check("Processes Home page", "Home" in output or "2471" in output, output[:300])
check("Processes About Us page", "About" in output or "1210" in output)
check("Shows config summary", "customer_name" in output.lower() or "CUSTOMER_NAME" in output)

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 7: clone_site.py --generate-script --dry-run")
print("=" * 60)

result = subprocess.run(
    [
        sys.executable,
        "scripts/clone_site.py",
        "--source",
        "healthcodeanalysis.com",
        "--target",
        "newcustomer.com",
        "--generate-script",
        "--dry-run",
    ],
    capture_output=True,
    text=True,
    cwd=os.path.join(os.path.dirname(__file__), ".."),
)
script_output = result.stdout
check("clone --generate-script exits 0", result.returncode == 0, f"exit={result.returncode}\n{result.stderr[:300]}")
check("Script has shebang", "#!/bin/bash" in script_output)
check("Script has source domain", "healthcodeanalysis.com" in script_output)
check("Script has target domain", "newcustomer.com" in script_output)
check("Script uses public_html path", "public_html" in script_output, "Should use /home/user/public_html")
check("Script has wp search-replace", "search-replace" in script_output)
check("Script has wp-config sed", "wp-config.php" in script_output)
check("Script has cache flush", "cache flush" in script_output or "rewrite flush" in script_output)

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 8: Logo/favicon activation after upload")
print("=" * 60)

# Verify the content_swapper code now calls update_site_settings after upload
source = inspect.getsource(ContentSwapper.swap_site_settings)
check("Logo activation code exists", "custom_logo" in source, "swap_site_settings should set custom_logo")
check("Favicon activation code exists", "site_icon" in source, "swap_site_settings should set site_icon")
check("Calls update_site_settings for logo", "update_site_settings" in source and "custom_logo" in source)
check("Calls update_site_settings for favicon", "update_site_settings" in source and "site_icon" in source)

# Verify PHP side supports custom_logo
php_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "healthcode-api-bridge.php")
with open(php_path) as f:
    php_code = f.read()
check("PHP supports custom_logo", "custom_logo" in php_code and "set_theme_mod" in php_code)
check("PHP supports site_icon", "site_icon" in php_code)

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 9: Mixed widget types (images in nested sections)")
print("=" * 60)

# Test deeply nested structure (inner sections)
NESTED_DATA = [
    {
        "id": "outer_sec",
        "elType": "section",
        "elements": [
            {
                "id": "outer_col",
                "elType": "column",
                "elements": [
                    {
                        "id": "inner_sec",
                        "elType": "section",
                        "elements": [
                            {
                                "id": "inner_col",
                                "elType": "column",
                                "elements": [
                                    {
                                        "id": "deep_img",
                                        "elType": "widget",
                                        "widgetType": "image",
                                        "settings": {"image": {"url": "https://old.com/deep-photo.jpg", "id": 50}},
                                    },
                                    {
                                        "id": "deep_h",
                                        "elType": "widget",
                                        "widgetType": "heading",
                                        "settings": {"title": "Deeply Nested Heading"},
                                    },
                                    {
                                        "id": "deep_t",
                                        "elType": "widget",
                                        "widgetType": "text-editor",
                                        "settings": {"editor": "<p>Deeply nested text.</p>"},
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }
]

pn = ElementorParser(NESTED_DATA)
imgs = pn.get_all_images()
check("Finds image in deeply nested section", len(imgs) == 1)
check("Correct deep image URL", "deep-photo.jpg" in imgs[0]["url"])

pn.replace_image("https://old.com/deep-photo.jpg", "https://new.com/new-photo.jpg", 999)
pn.replace_heading_by_index(0, "Updated Deep Heading")
pn.replace_text_editor_by_index(0, "<p>Updated deep text.</p>")

rn = pn.to_data()
rn_json = json.dumps(rn)
check("Deep image swapped", "new-photo.jpg" in rn_json and "deep-photo.jpg" not in rn_json)
check("Deep heading swapped", "Updated Deep Heading" in rn_json and "Deeply Nested Heading" not in rn_json)
check("Deep text swapped", "Updated deep text" in rn_json and "Deeply nested text" not in rn_json)

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 10: Repeater field images (testimonials/galleries)")
print("=" * 60)

REPEATER_DATA = [
    {
        "id": "s1",
        "elType": "section",
        "elements": [
            {
                "id": "c1",
                "elType": "column",
                "elements": [
                    {
                        "id": "slider1",
                        "elType": "widget",
                        "widgetType": "image-carousel",
                        "settings": {
                            "carousel": [
                                {"image": {"url": "https://old.com/slide1.jpg", "id": 10}},
                                {"image": {"url": "https://old.com/slide2.jpg", "id": 11}},
                                {"image": {"url": "https://old.com/slide3.jpg", "id": 12}},
                            ]
                        },
                    }
                ],
            }
        ],
    }
]

pr = ElementorParser(REPEATER_DATA)
rimgs = pr.get_all_images()
check("Finds 3 repeater images", len(rimgs) == 3, f"got {len(rimgs)}")

pr.replace_image("https://old.com/slide1.jpg", "https://new.com/new-slide1.jpg", 100)
pr.replace_image("https://old.com/slide2.jpg", "https://new.com/new-slide2.jpg", 101)
pr.replace_image("https://old.com/slide3.jpg", "https://new.com/new-slide3.jpg", 102)

rr = pr.to_data()
rr_json = json.dumps(rr)
check("Repeater slide 1 swapped", "new-slide1.jpg" in rr_json and "slide1.jpg" not in rr_json.replace("new-slide1", ""))
check("Repeater slide 2 swapped", "new-slide2.jpg" in rr_json)
check("Repeater slide 3 swapped", "new-slide3.jpg" in rr_json)
check("No old URLs remain", "old.com" not in rr_json)

print()


# ═══════════════════════════════════════════════════════════
print("=" * 60)
total = passed + failed
print(f"RESULTS: {passed}/{total} passed, {failed} failed")
print("=" * 60)

sys.exit(1 if failed else 0)
