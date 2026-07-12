#!/usr/bin/env python3
"""Export rendered WordPress content to a domain-independent Pages bundle."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

DEFAULT_SOURCE = "http://127.0.0.1:8889"
DEFAULT_PUBLIC = "https://healthcodeanalysis.pages.dev"
ASSET_PREFIXES = ("/wp-content/", "/wp-includes/")
TEXT_ASSET_SUFFIXES = {".css", ".js", ".json", ".xml", ".svg"}
PRIVATE_ORIGIN_PATTERN = re.compile(
    r"(?:localhost|127\.0\.0\.1|https?://(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)|trycloudflare\.com|healthcodeanalysis\.com)",
    re.I,
)


class ExportError(RuntimeError):
    pass


def fetch_bytes(url: str, timeout: int = 60) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": "HealthCodeStaticPublisher/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ExportError(f"Failed to fetch {url}: {exc}") from exc


def fetch_json(url: str) -> Any:
    payload, _ = fetch_bytes(url)
    return json.loads(payload.decode("utf-8"))


def strip_html(value: str) -> str:
    value = re.sub(r"<style\b[^>]*>[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def public_path(item: dict[str, Any], kind: str) -> str:
    path = urlparse(item.get("link", "")).path
    if path and path != "/":
        return path if path.endswith("/") else f"{path}/"
    slug = item.get("slug", "")
    return "/" if kind == "pages" and slug in {"", "home"} else f"/{slug}/"


def rewrite_text(value: str, origins: set[str], public_url: str) -> str:
    for origin in sorted(origins, key=len, reverse=True):
        origin = origin.rstrip("/")
        value = value.replace(origin, public_url)
        value = value.replace(origin.replace("/", r"\/"), public_url.replace("/", r"\/"))
        value = value.replace(quote(origin, safe=""), quote(public_url, safe=""))
    value = value.replace("https://askme.healthcodeanalysis.workers.dev", f"{public_url}/askme-proxy")
    value = value.replace("https://askme.regenai-workers.workers.dev", f"{public_url}/askme-proxy")
    return value


def disable_wordpress_forms(document: str) -> str:
    """Prevent exported MetForm controls from submitting to nonexistent WP routes."""
    document = re.sub(
        r'(data-action=["\'])[^"\']*/wp-json/metform/v1/entries/insert/[^"\']*(["\'])',
        r'\1#\2 data-static-form="disabled"',
        document,
        flags=re.I,
    )
    if 'data-static-form="disabled"' not in document:
        return document
    guard = """<script id="healthcode-static-form-guard">
document.addEventListener("submit", function (event) {
  if (!event.target.closest('[data-static-form="disabled"]')) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  window.alert("This WordPress form is available only in the live admin demo. The public static site does not accept submissions.");
}, true);
</script>"""
    return document.replace("</body>", guard + "\n</body>", 1)


def prefer_elementor_login_popup(document: str) -> str:
    """Remove the obsolete custom login dialog when the Elementor popup is present.

    WordPress currently renders both implementations. Their load timers otherwise
    open two dialogs in succession on the exported site.
    """
    if 'class="wpr-template-popup"' not in document or 'id="hca-custom-popup"' not in document:
        return document

    popup_start = document.find('<div id="hca-custom-popup"')
    style_start = document.find("<style", popup_start)
    style_end = document.find("</style>", style_start)
    script_start = document.find("<script", style_end)
    script_end = document.find("</script>", script_start)
    if min(popup_start, style_start, style_end, script_start, script_end) < 0:
        raise ExportError("Could not isolate the legacy custom login popup")

    legacy_script = document[script_start:script_end]
    if "openCustomPopup" not in legacy_script:
        raise ExportError("Legacy login popup script was not found after its markup")
    return document[:popup_start] + document[script_end + len("</script>"):]


class AssetCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: set[str] = set()

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if not value:
                continue
            candidates = value.split(",") if key in {"srcset", "data-srcset"} else [value]
            for candidate in candidates:
                self.urls.add(candidate.strip().split()[0])


def collect_css_urls(value: str) -> set[str]:
    return {
        match.group(2).strip()
        for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", value, flags=re.I)
        if match.group(2).strip() and not match.group(2).lstrip().startswith("data:")
    }


@dataclass
class StaticExporter:
    source_url: str
    public_url: str
    output_dir: Path
    chatbot_index: Path | None = None

    def __post_init__(self) -> None:
        self.source_url = self.source_url.rstrip("/")
        self.public_url = self.public_url.rstrip("/")
        self.origins = {
            self.source_url,
            "http://localhost:8888",
            "http://localhost:8889",
            "http://localhost",
            "https://localhost",
            "http://127.0.0.1:8888",
            "http://127.0.0.1:8889",
            "https://healthcodeanalysis.com",
            "http://healthcodeanalysis.com",
            "https://admin-demo.healthcodeanalysis.com",
        }

    def rest_collection(self, resource: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        while True:
            url = f"{self.source_url}/wp-json/wp/v2/{resource}?status=publish&per_page=100&page={page}"
            try:
                batch = fetch_json(url)
            except ExportError as exc:
                if "400" in str(exc) and page > 1:
                    break
                raise
            if not batch:
                break
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return items

    def export(self) -> dict[str, int]:
        pages = self.rest_collection("pages")
        posts = self.rest_collection("posts")
        categories = fetch_json(f"{self.source_url}/wp-json/wp/v2/categories?per_page=100")
        if not pages:
            raise ExportError("WordPress returned no published pages")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        asset_urls: set[str] = set()
        rendered = 0

        for kind, items in (("pages", pages), ("posts", posts)):
            for item in items:
                path = public_path(item, kind)
                source = "/" if path == "/" else (f"/?page_id={item['id']}" if kind == "pages" else f"/?p={item['id']}")
                payload, content_type = fetch_bytes(f"{self.source_url}{source}")
                if "text/html" not in content_type:
                    raise ExportError(f"Expected HTML for {kind[:-1]} {item['id']}, got {content_type}")
                document = rewrite_text(payload.decode("utf-8", errors="replace"), self.origins, self.public_url)
                document = prefer_elementor_login_popup(document)
                document = disable_wordpress_forms(document)
                target = self.output_dir / ("index.html" if path == "/" else path.strip("/") + "/index.html")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(document, encoding="utf-8")
                collector = AssetCollector()
                collector.feed(document)
                asset_urls.update(collector.urls)
                rendered += 1

        for category in categories:
            if not category.get("count") or category.get("slug") == "uncategorized":
                continue
            path = f"/category/{category['slug']}/"
            payload, content_type = fetch_bytes(f"{self.source_url}/?cat={category['id']}")
            if "text/html" not in content_type:
                raise ExportError(f"Expected HTML for category {category['id']}, got {content_type}")
            document = rewrite_text(payload.decode("utf-8", errors="replace"), self.origins, self.public_url)
            document = prefer_elementor_login_popup(document)
            document = disable_wordpress_forms(document)
            target = self.output_dir / path.strip("/") / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(document, encoding="utf-8")
            collector = AssetCollector()
            collector.feed(document)
            asset_urls.update(collector.urls)
            rendered += 1

        copied = self.copy_assets(asset_urls)
        index = self.build_content_index(posts, pages, categories)
        (self.output_dir / "content-index.json").write_text(
            json.dumps(index, ensure_ascii=True, separators=(",", ":")), encoding="utf-8"
        )
        if self.chatbot_index:
            self.chatbot_index.parent.mkdir(parents=True, exist_ok=True)
            self.chatbot_index.write_text(
                json.dumps(index, ensure_ascii=True, separators=(",", ":")), encoding="utf-8"
            )
        self.validate_public_bundle()
        return {
            "pages": len(pages),
            "posts": len(posts),
            "categories": sum(bool(item.get("count")) and item.get("slug") != "uncategorized" for item in categories),
            "rendered": rendered,
            "assets": copied,
        }

    def copy_assets(self, urls: set[str]) -> int:
        copied = 0
        pending = list(sorted(urls))
        visited: set[str] = set()
        while pending:
            raw_url = pending.pop(0)
            if raw_url in visited:
                continue
            visited.add(raw_url)
            parsed = urlparse(urljoin(self.public_url + "/", html.unescape(raw_url)))
            path = unquote(parsed.path)
            if not path.startswith(ASSET_PREFIXES) or ".." in Path(path).parts:
                continue
            target = self.output_dir / path.lstrip("/")
            try:
                payload, _ = fetch_bytes(f"{self.source_url}{path}")
            except ExportError:
                if target.exists():
                    continue
                raise
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.suffix.lower() in TEXT_ASSET_SUFFIXES:
                text = payload.decode("utf-8", errors="replace")
                text = rewrite_text(text, self.origins, self.public_url)
                if target.suffix.lower() == ".css":
                    pending.extend(collect_css_urls(text))
                payload = text.encode("utf-8")
            target.write_bytes(payload)
            copied += 1
        return copied

    def validate_public_bundle(self) -> None:
        violations = []
        for path in self.output_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_ASSET_SUFFIXES | {".html"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            match = PRIVATE_ORIGIN_PATTERN.search(text)
            if match:
                violations.append(f"{path.relative_to(self.output_dir)}: {match.group(0)}")
        if violations:
            raise ExportError("Private/backend origins remain in public bundle: " + "; ".join(violations[:10]))

    def build_content_index(
        self, posts: list[dict[str, Any]], pages: list[dict[str, Any]], categories: list[dict[str, Any]]
    ) -> dict[str, Any]:
        def normalize(item: dict[str, Any], kind: str) -> dict[str, Any]:
            path = public_path(item, kind)
            content = strip_html(item.get("content", {}).get("rendered", ""))
            excerpt = strip_html(item.get("excerpt", {}).get("rendered", "")) or content[:240]
            return {
                "id": item["id"],
                "slug": item.get("slug", ""),
                "date": item.get("date", ""),
                "modified": item.get("modified", ""),
                "link": self.public_url + path,
                "title": {"rendered": item.get("title", {}).get("rendered", "")},
                "excerpt": {"rendered": excerpt},
                "content": {"rendered": content, "text": content},
                "categories": item.get("categories", []),
            }

        normalized_categories = []
        for category in categories:
            normalized_categories.append(
                {
                    "id": category["id"],
                    "name": strip_html(category.get("name", "")),
                    "slug": category.get("slug", ""),
                    "count": category.get("count", 0),
                    "parent": category.get("parent", 0),
                    "link": f"{self.public_url}/category/{category.get('slug', '')}/",
                }
            )
        return {
            "version": 1,
            "source": "wordpress-static-export",
            "posts": [normalize(item, "posts") for item in posts],
            "pages": [normalize(item, "pages") for item in pages],
            "categories": normalized_categories,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--public-url", default=DEFAULT_PUBLIC)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "pages-demo")
    parser.add_argument(
        "--chatbot-index",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "workers" / "askme" / "content-index.json",
    )
    parser.add_argument("--clean", action="store_true", help="Remove generated HTML routes before exporting")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.clean and args.output.exists():
        for generated_assets in (args.output / "wp-content", args.output / "wp-includes"):
            if generated_assets.exists():
                shutil.rmtree(generated_assets)
        for path in args.output.rglob("index.html"):
            if path != args.output / "index.html":
                path.unlink()
        for path in sorted(args.output.glob("*/"), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                shutil.rmtree(path)
    try:
        result = StaticExporter(args.source, args.public_url, args.output, args.chatbot_index).export()
    except (ExportError, json.JSONDecodeError) as exc:
        print(f"Export failed: {exc}", file=sys.stderr)
        return 1
    print("Export complete: " + ", ".join(f"{key}={value}" for key, value in result.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
