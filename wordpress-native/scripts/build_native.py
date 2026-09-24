"""Convert the approved semantic design to editable core Elementor widgets."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from jinja2 import Environment, FileSystemLoader, select_autoescape
from style_scope import scope_stylesheet

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "wordpress-native/build"
PLUGIN = OUT / "plugin"
IMPORT = OUT / "import"
ASSET_URL = "/wp-content/plugins/healthcode-native/assets"
SITE = json.loads((ROOT / "frontend/data/site.json").read_text(encoding="utf-8"))
CONFIG = json.loads((ROOT / "frontend/site.config.json").read_text(encoding="utf-8"))
TOOLS = json.loads((ROOT / "frontend/data/tools.json").read_text(encoding="utf-8"))
COUNTS: dict[str, int] = {}
COUNTER = 0
NOTICES = json.loads((ROOT / "wordpress-native/data/public-notices.json").read_text(encoding="utf-8"))
POLICY = json.loads((ROOT / "wordpress-native/data/publishing-policy.json").read_text(encoding="utf-8"))
ICON_PALETTE = json.loads((ROOT / "wordpress-native/data/icon-palette.json").read_text(encoding="utf-8"))


def native(kind, settings, children=None):
    global COUNTER
    COUNTER += 1
    COUNTS[kind] = COUNTS.get(kind, 0) + 1
    data = {
        "id": format(COUNTER, "07x"),
        "elType": "container" if kind == "container" else "widget",
        "settings": settings,
        "elements": children or [],
        "isInner": False,
    }
    if kind != "container":
        data["widgetType"] = kind
    return data


def attrs(node):
    return {
        k: " ".join(v) if isinstance(v, list) else str(v)
        for k, v in node.attrs.items()
        if k not in ["href", "src", "width", "height", "loading", "fetchpriority", "style"]
    }


def media_url(url):
    return ASSET_URL + url[len("/assets") :] if url.startswith("/assets/") else url


def svg_image(node):
    node["xmlns"] = "http://www.w3.org/2000/svg"
    if node.has_attr("viewbox"):
        node["viewBox"] = node.attrs.pop("viewbox")
    svg = str(node)
    color = ICON_PALETTE["default"]
    for context in ICON_PALETTE["ancestor_classes"]:
        if node.find_parent(class_=context["class"]) and (
            "within" not in context or node.find_parent(class_=context["within"])
        ):
            color = context["color"]
            break
    svg = svg.replace("currentColor", color)
    name = "icon-" + hashlib.sha256(svg.encode()).hexdigest()[:14] + ".svg"
    (PLUGIN / "assets" / name).write_text(svg, encoding="utf-8")
    return ASSET_URL + "/" + name


def rich(node):
    copy = BeautifulSoup(str(node), "html.parser")
    for svg, original in zip(copy.find_all("svg"), node.find_all("svg"), strict=True):
        image = copy.new_tag("img", src=svg_image(original), attrs={"class": "hc-inline-icon", "alt": ""})
        svg.replace_with(image)
    for image in copy.find_all("img"):
        image["src"] = media_url(image.get("src", ""))
    return str(copy)


def convert(node):
    if isinstance(node, NavigableString):
        return (
            native("text-editor", {"editor": str(node), "_css_classes": "hc-inline-widget"})
            if str(node).strip()
            else None
        )
    if not isinstance(node, Tag) or node.name in ["script", "source", "noscript"]:
        return None
    original = attrs(node)
    classes = " ".join(node.get("class", []))
    common = {"_css_classes": "", "hc_attributes": original}
    if "filter-bar" in node.get("class", []):
        search = node.select_one("[data-filter-search]")
        select = node.select_one("[data-filter-category]")
        clear = node.select_one("[data-clear-saved]")
        return native(
            "hcn-library-controls",
            {
                "search_label": search.get("placeholder", ""),
                "topic_label": node.select_one(".topic-select span").get_text(),
                "all_label": select.option.get_text(),
                "categories": "\n".join(o.get_text() for o in select.select("option")[1:]),
                "initial_count": int(node.select_one("[data-result-count]").get_text()),
                "clear_label": clear.get_text() if clear else "",
            },
        )
    if "tool-workbench" in node.get("class", []):
        tool_id = node.get("data-tool")
        if not tool_id:
            form = node.find(attrs={"data-tool": True})
            tool_id = form["data-tool"] if form else None
        if tool_id not in TOOLS:
            raise ValueError("Unknown tool " + str(tool_id))
        content = str(node)
        if "<?" in content:
            raise ValueError("Unexpected PHP in static tool")
        (PLUGIN / "templates" / ("tool-" + tool_id + ".php")).write_text(content, encoding="utf-8")
        return native("shortcode", {"shortcode": '[healthcode_tool id="' + tool_id + '"]'})
    if node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        return native("heading", {**common, "title": node.decode_contents(), "header_size": node.name})
    if node.name == "img":
        return native(
            "image",
            {
                **common,
                "image": {"url": media_url(node.get("src", "")), "id": 0},
                "image_size": "full",
                "caption_source": "none",
            },
        )
    if node.name == "svg":
        return native(
            "image",
            {
                "image": {"url": svg_image(node), "id": 0},
                "image_size": "full",
                "hc_attributes": {"class": "hc-inline-icon"},
                "_css_classes": "hc-icon-widget",
            },
        )
    if node.name == "picture":
        return convert(node.find("img"))
    if node.name == "video":
        return native(
            "video",
            {
                "video_type": "hosted",
                "insert_url": "yes",
                "external_url": {"url": media_url(CONFIG["client"]["frontier"]["video_url"])},
                "autoplay": "",
                "mute": "yes",
                "loop": "",
                "controls": "",
                "preload": "none",
                "_css_classes": "hc-neural-video",
            },
        )
    if node.name == "button" or (
        node.name == "a"
        and "brand" not in node.get("class", [])
        and not node.find(["div", "h1", "h2", "h3", "p", "img"])
    ):
        original["class"] = classes
        if node.name == "button":
            original["data-hc-button"] = "true"
        text = node.get_text(" ", strip=True) or "\u200b"
        settings = {
            **common,
            "hc_attributes": original,
            "text": text,
            "link": {"url": node.get("href", "")},
            "size": "sm",
        }
        if node.select_one("[data-save-label]"):
            settings["hc_save_label"] = True
        if node.select_one("[data-saved-count]"):
            settings["hc_saved_count"] = True
        svg = node.find("svg")
        if svg:
            settings["hc_icon"] = svg_image(svg)
        return native("button", settings)
    inline = ["span", "strong", "small", "em", "b", "i", "br", "sup", "sub", "code", "a"]
    if node.name in ["p", "span", "figcaption", "ul", "ol", "table"] or (
        node.name == "div"
        and all(c.name in inline for c in node.find_all(recursive=False))
        and not node.find(["a", "button"])
        and node.get_text(strip=True)
    ):
        return native(
            "text-editor", {"editor": rich(node), "_css_classes": "hc-inline-widget" if node.name == "span" else ""}
        )
    children = [v for child in node.children if (v := convert(child))]
    settings = {
        **common,
        "css_classes": classes,
        "content_width": "full",
        "flex_direction": "row",
        "flex_gap": {"column": "0", "row": "0", "isLinked": True, "unit": "px"},
        "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True},
        "html_tag": node.name
        if node.name in ["section", "article", "header", "footer", "main", "aside", "nav", "a"]
        else "div",
    }
    if node.get("id"):
        settings["_element_id"] = node["id"]
    if node.name == "a":
        settings["link"] = {"url": node.get("href", "")}
    return native("container", settings, children)


def build():
    for path in [PLUGIN / "templates", PLUGIN / "data", IMPORT, OUT / "gateway"]:
        path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "frontend-preview/assets", PLUGIN / "assets", dirs_exist_ok=True)
    shutil.copy2(ROOT / "wordpress-native/scripts/import.php", IMPORT / "import.php")
    for source in (ROOT / "wordpress-native/plugin").glob("*.php"):
        shutil.copy2(source, PLUGIN / source.name)
    shutil.copy2(ROOT / "wordpress-native/data/publishing-policy.json", PLUGIN / "data/publishing-policy.json")
    shutil.copy2(ROOT / "wordpress-native/data/editor-fields.json", PLUGIN / "data/editor-fields.json")
    for n in ["native-base", "native-adapter"]:
        shutil.copy2(ROOT / "wordpress-native/plugin" / f"{n}.css", PLUGIN / "assets/styles" / f"{n}.css")
    for p in (PLUGIN / "assets/styles").glob("*.css"):
        if p.stem not in ["native-base", "native-adapter"]:
            p.write_text(
                scope_stylesheet(p.read_text(encoding="utf-8").replace(">", " ").replace("/assets/", ASSET_URL + "/"))
            )
    application = PLUGIN / "assets/scripts/app.mjs"
    application.write_text(
        application.read_text(encoding="utf-8").replace("card.dataset.id", "card.dataset.storyId"), encoding="utf-8"
    )
    motion = PLUGIN / "assets/scripts/frontier.mjs"
    motion.write_text(
        motion.read_text(encoding="utf-8").replace(
            "const toggle = section.querySelector('[data-motion-toggle]');",
            "const toggle = section.querySelector('[data-motion-toggle]'); video.classList.add('frontier-film'); video.hidden=true; video.removeAttribute('src'); video.load();",
        )
    )
    (PLUGIN / "data/site.json").write_text(json.dumps(SITE), encoding="utf-8")
    (PLUGIN / "data/config.json").write_text(json.dumps(CONFIG["client"]), encoding="utf-8")
    (PLUGIN / "data/tools.json").write_text(json.dumps(TOOLS), encoding="utf-8")
    gateway_env = Environment(
        loader=FileSystemLoader(ROOT / "wordpress-native/templates"), autoescape=select_autoescape(["html", "xml"])
    )
    (OUT / "gateway/nginx.conf").write_text(
        gateway_env.get_template("nginx.conf.j2").render(
            delivery=json.loads((ROOT / "wordpress-native/data/delivery.json").read_text(encoding="utf-8")),
            policy=POLICY,
        )
    )
    home = BeautifulSoup((ROOT / "frontend-preview/index.html").read_text(encoding="utf-8"), "html.parser")
    footer_nav = home.select_one(".footer-links nav")
    for slug, label in [
        ("editorial-policy", "Editorial standards"),
        ("terms-of-use", "Terms"),
        ("accessibility", "Accessibility"),
    ]:
        link = home.new_tag("a", href="/" + slug + "/")
        link.string = label
        footer_nav.append(link)
    figure = home.select_one(".frontier-figure")
    header = convert(home.find("header"))
    footer = convert(home.find("footer"))
    header["elements"].insert(0, convert(home.select_one(".skip-link")))
    dialogs = "".join(
        str(el) for el in home.select("body > dialog, body > .toast, body > .library-trigger, body > .reading-progress")
    )
    (PLUGIN / "templates/dialogs.php").write_text(dialogs, encoding="utf-8")
    pages = []
    documents = {}
    env = Environment(loader=FileSystemLoader(ROOT / "frontend/templates"), autoescape=select_autoescape(["html"]))
    for slug, page in NOTICES.items():
        documents["/" + slug + "/"] = env.get_template("page.html").render(
            page=page,
            site=SITE,
            title=page["title"].replace("\n", " "),
            route="/" + slug + "/",
            public_origin=CONFIG["public_origin"],
            config=CONFIG["client"],
            tools=TOOLS,
        )
    for path in sorted((ROOT / "frontend-preview").rglob("index.html")):
        relative = path.parent.relative_to(ROOT / "frontend-preview").as_posix()
        route = "/" if relative == "." else "/" + relative + "/"
        documents.setdefault(route, path.read_text(encoding="utf-8"))
    for route, document in documents.items():
        soup = BeautifulSoup(document, "html.parser")
        main = soup.find("main")
        if not main:
            continue
        if route == "/":
            figure = soup.select_one(".frontier-annotation")
            if figure:
                figure.append(" · " + POLICY["editorial"]["artwork_disclosure"])
        elements = [v for child in main.children if (v := convert(child))]
        elements = [
            native(
                "container",
                {"html_tag": "main", "_element_id": "main", "css_classes": "hc-main", "content_width": "full"},
                elements,
            )
        ]
        description = soup.find("meta", attrs={"name": "description"})
        article = next(
            (
                post
                for post in json.loads((ROOT / "frontend/data/library.json").read_text(encoding="utf-8"))["posts"]
                if post["route"] == route
            ),
            None,
        )
        policy = json.loads((ROOT / "wordpress-native/data/publishing-policy.json").read_text(encoding="utf-8"))
        alias = SITE["aliases"].get(route.strip("/"))
        summary = (
            article["excerpt"] if article else (description.get("content", "") if description else SITE["description"])
        )
        if not article and route != "/":
            summary = soup.title.get_text().split(" — ")[0] + ". " + summary
        pages.append(
            {
                "route": route,
                "title": soup.title.get_text().split(" — ")[0],
                "description": summary,
                "image": media_url(article["image"]) if article else "",
                "indexable": not article and not alias and route not in policy["excluded_routes"],
                "redirect": "/" + alias + "/" if alias else "",
                "elements": elements,
            }
        )
    (IMPORT / "pages.json").write_text(
        json.dumps({"header": header, "footer": footer, "pages": pages}, ensure_ascii=False), encoding="utf-8"
    )
    (IMPORT / "widget-inventory.json").write_text(json.dumps(COUNTS, indent=2), encoding="utf-8")
    print("Native pages:", len(pages), "widget inventory:", COUNTS)


if __name__ == "__main__":
    build()
