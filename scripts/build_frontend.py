"""Build the local Evidence Atlas edition from normalized editorial data."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from frontend_settings import FrontendSettings


def build(settings: FrontendSettings | None = None) -> int:
    settings = settings or FrontendSettings.load()
    library = json.loads(settings.content.read_text(encoding="utf-8"))
    site = json.loads(settings.copy.read_text(encoding="utf-8"))
    tools = json.loads(settings.tools.read_text(encoding="utf-8"))
    posts = library["posts"]
    env = Environment(
        loader=FileSystemLoader(settings.templates), autoescape=select_autoescape(["html"]), undefined=StrictUndefined
    )
    output = settings.output
    output.mkdir(parents=True, exist_ok=True)
    manifest = output / "build-manifest.json"
    previous = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    generated: set[str] = set()
    for source in (settings.assets, settings.styles, settings.scripts):
        destination = output / "assets" / ("" if source == settings.assets else source.name)
        for asset in source.rglob("*"):
            if asset.is_file():
                target = destination / asset.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(asset, target)
                generated.add(target.relative_to(output).as_posix())
    index = [
        {key: p[key] for key in ("id", "title", "excerpt", "route", "category", "group", "image", "minutes")}
        for p in posts
    ]
    (output / "assets" / "library-index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    generated.add("assets/library-index.json")
    rendered: set[str] = set()

    def render(route: str, template: str, **context: Any) -> None:
        relative = route.strip("/")
        target = (output / relative / "index.html").resolve()
        if not target.is_relative_to(output.resolve()):
            raise ValueError("Page route escaped preview directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        content = env.get_template(template).render(
            site=site,
            config=settings.client,
            public_origin=settings.public_origin,
            tools=tools,
            all_posts=posts,
            route=route,
            **context,
        )
        target.write_text(content, encoding="utf-8")
        generated.add(target.relative_to(output.resolve()).as_posix())
        rendered.add(route)

    featured = [p for slug in site["featured_slugs"] for p in posts if p["slug"] == slug]
    reviews = [p for p in posts if p["group"] == "reviews"]
    tool_posts = [p for p in posts if p["slug"] in site["tool_slugs"]]
    render("/", "home.html", title=site["brand"], featured=featured, reviews=reviews, tool_posts=tool_posts)
    for post in posts:
        tool_id = site["tool_slugs"].get(post["slug"])
        render(
            post["route"],
            "article.html",
            title=post["title"],
            post=post,
            tool=tools.get(tool_id),
            blocks=tools[tool_id]["guide"] if tool_id else post["blocks"],
            tool_id=tool_id,
            related=[p for p in posts if p["group"] == post["group"] and p["id"] != post["id"]][
                : settings.client["related_limit"]
            ],
        )
    for slug in [*site["pages"], *site["aliases"]]:
        page = site["pages"][site["aliases"].get(slug, slug)]
        group = page.get("group")
        selected = [p for p in posts if group in ("all", "saved") or p["group"] == group]
        if page.get("categories"):
            selected = [p for p in selected if set(p["categories"]) & set(page["categories"])]
        render(
            f"/{slug}/",
            "archive.html" if group else "page.html",
            title=page["title"].replace("\n", " "),
            page=page,
            posts=selected,
            saved=group == "saved",
        )
    for category in library["categories"]:
        selected = [p for p in posts if category["id"] in p["categories"]]
        if selected:
            page = {
                "eyebrow": site["labels"]["category_eyebrow"],
                "title": category["name"],
                "description": site["labels"]["category_description"],
            }
            render(
                f"/category/{category['slug']}/",
                "archive.html",
                title=category["name"],
                page=page,
                posts=selected,
                saved=False,
            )
    missing = set(library["source_routes"]) - rendered
    if missing:
        raise ValueError(f"Unbuilt source routes: {sorted(missing)}")
    html = env.get_template("404.html").render(
        site=site,
        config=settings.client,
        public_origin=settings.public_origin,
        tools=tools,
        title="Page not found",
        route="/404/",
        all_posts=posts,
    )
    (output / "404.html").write_text(html, encoding="utf-8")
    generated.add("404.html")
    for obsolete in set(previous) - generated:
        target = (output / obsolete).resolve()
        if not target.is_relative_to(output.resolve()) or Path(obsolete).is_absolute():
            raise ValueError("Invalid path in previous build manifest")
        if target.is_file():
            target.unlink()
    manifest.write_text(json.dumps(sorted(generated), indent=2), encoding="utf-8")
    print(f"Built {len(rendered)} routes and a real 404 page in {output.name}.")
    return len(rendered)


if __name__ == "__main__":
    build()
