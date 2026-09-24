"""Normalize an explicit WordPress snapshot into safe editorial source data."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from PIL import Image

from frontend_settings import DEFAULT_CONFIG, FrontendSettings, project_path


def clean_text(value: str) -> str:
    value = html.unescape(value)
    repairs = {
        "\xe2\u20ac\u2122": "\u2019",
        "\xe2\u20ac\u0153": "\u201c",
        "\xe2\u20ac\x9d": "\u201d",
        "\xe2\u20ac\u201d": "\u2014",
        "\xe2\u20ac\u201c": "\u2013",
        "\xe2\u20ac\xa2": "\xb7",
        "\xe2\u201a\u201a": "\u2082",
        "\xc2": "",
    }
    for broken, correct in repairs.items():
        value = value.replace(broken, correct)
    return re.sub(r"\s+", " ", value).strip()


def route_from_link(link: str) -> str:
    path = unquote(urlparse(link).path)
    if not path.startswith("/") or ".." in Path(path).parts or "\\" in path:
        raise ValueError("Unsafe content route")
    return path.rstrip("/") + "/"


def import_content(settings: FrontendSettings) -> int:
    source = json.loads((settings.source_export / "content-index.json").read_text(encoding="utf-8"))
    categories = {item["id"]: item for item in source["categories"]}
    posts = []
    for item in source["posts"]:
        route = route_from_link(item["link"])
        document = project_path(settings.source_export, urlparse(item["link"]).path.strip("/") + "/index.html")
        if not document.exists():
            document = project_path(settings.source_export, route.strip("/") + "/index.html")
        soup = BeautifulSoup(document.read_text(encoding="utf-8"), "html.parser")
        content = soup.select_one(".jkit-post-content")
        blocks = []
        if content:
            for bad in content.select("script,style,form,input,button,select,textarea,iframe"):
                bad.decompose()
            for element in content.select("h2,h3,h4,p,li,blockquote"):
                if element.find_parent(["p", "li", "blockquote"]):
                    continue
                text = clean_text(element.get_text(" ", strip=True))
                if text:
                    blocks.append(
                        {
                            "type": "heading"
                            if element.name.startswith("h")
                            else "bullet"
                            if element.name == "li"
                            else "paragraph",
                            "text": text,
                        }
                    )
        if not blocks:
            blocks = [
                {"type": "paragraph", "text": clean_text(item["content"].get("text", item["content"]["rendered"]))}
            ]
        image_meta = soup.select_one('meta[property="og:image"]')
        image_path = ""
        if image_meta:
            image_url = str(image_meta.get("content", ""))
            rel = unquote(urlparse(image_url).path).lstrip("/")
            original = project_path(settings.source_export, rel)
            if original.is_file():
                with Image.open(original) as image:
                    if image.width > 200 and image.height > 150:
                        image.thumbnail((settings.image_width, settings.image_width))
                        target = settings.assets / "images" / f"{item['id']}.webp"
                        target.parent.mkdir(parents=True, exist_ok=True)
                        image.convert("RGB").save(target, "WEBP", quality=settings.image_quality)
                        image_path = f"/assets/images/{item['id']}.webp"
        ids = item.get("categories", [])
        group = "insights"
        for group_name, parent_id in settings.content_groups.items():
            if any(i == parent_id or categories.get(i, {}).get("parent") == parent_id for i in ids):
                group = group_name
        leaves = [categories[i] for i in ids if i in categories and categories[i].get("parent")]
        category = (
            leaves[0]
            if leaves
            else next((categories[i] for i in ids if i in categories), {"name": "Insights", "slug": "medintel"})
        )
        title = clean_text(BeautifulSoup(item["title"]["rendered"], "html.parser").get_text())
        posts.append(
            {
                "id": item["id"],
                "slug": unquote(item["slug"]),
                "route": route,
                "title": title,
                "excerpt": clean_text(item["excerpt"]["rendered"]),
                "date": item["date"][:10],
                "category": clean_text(category["name"]),
                "category_slug": category["slug"],
                "categories": ids,
                "group": group,
                "image": image_path,
                "blocks": blocks,
                "minutes": max(1, math.ceil(sum(len(b["text"].split()) for b in blocks) / settings.words_per_minute)),
                "demo": True,
            }
        )
    result = {
        "posts": posts,
        "categories": [
            {"id": c["id"], "name": clean_text(c["name"]), "slug": c["slug"], "parent": c["parent"]}
            for c in categories.values()
            if c["slug"] != "uncategorized"
        ],
        "source_routes": sorted(
            {route_from_link(x["link"]) for x in source["posts"] + source["pages"]}
            | {
                route_from_link(c["link"])
                for c in source["categories"]
                if c.get("count") and c["slug"] != "uncategorized"
            }
        ),
    }
    settings.content.parent.mkdir(parents=True, exist_ok=True)
    settings.content.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(posts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    print(f"Imported {import_content(FrontendSettings.load(args.config))} articles from the local snapshot.")
