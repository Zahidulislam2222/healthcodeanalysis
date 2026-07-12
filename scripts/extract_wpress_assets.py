from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "healthcodeanalysis-com-20260408-134414-6x2yr0zixkut.wpress"
PAGES = ROOT / "pages-demo"
HTML = PAGES / "index.html"
HEADER_SIZE = 4377


def iter_entries():
    offset = 0
    total = ARCHIVE.stat().st_size
    with ARCHIVE.open("rb") as fh:
        while offset < total:
            fh.seek(offset)
            header = fh.read(HEADER_SIZE)
            if len(header) < HEADER_SIZE:
                return
            name = header[:255].split(b"\0", 1)[0].decode("utf-8", "replace")
            size_raw = header[255:269].split(b"\0", 1)[0].decode("ascii", "ignore")
            if not name or not size_raw:
                return
            size = int(size_raw)
            yield name, offset + HEADER_SIZE, size
            offset += HEADER_SIZE + size


def archive_index():
    index: dict[str, tuple[int, int]] = {}
    for name, data_offset, size in iter_entries():
        index.setdefault(name, (data_offset, size))
    return index


def referenced_paths(text: str) -> set[str]:
    paths = set()
    for match in re.finditer(r"https://healthcodeanalysis\.pages\.dev/((?:wp-content|wp-includes)/[^'\" )<>\s]+)", text):
        path = match.group(1).replace("&amp;", "&")
        path = re.split(r"[?#]", path)[0]
        if path:
            paths.add(path)
    return paths


def extract_file(index: dict[str, tuple[int, int]], relative_path: str) -> bool:
    basename = Path(relative_path).name
    found = index.get(basename)
    if not found:
        return False
    data_offset, size = found
    target = PAGES / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with ARCHIVE.open("rb") as src:
        src.seek(data_offset)
        target.write_bytes(src.read(size))
    return True


def css_url_paths(css_path: Path) -> set[str]:
    text = css_path.read_text(errors="ignore")
    paths = set()
    for raw in re.findall(r"url\(([^)]+)\)", text):
        value = raw.strip().strip("'\"")
        if not value or value.startswith(("data:", "http:", "https:", "#")):
            continue
        value = re.split(r"[?#]", value)[0]
        resolved = (css_path.parent / value).resolve()
        try:
            rel = resolved.relative_to(PAGES.resolve()).as_posix()
        except ValueError:
            continue
        paths.add(rel)
    return paths


def main() -> None:
    index = archive_index()
    text = HTML.read_text(errors="ignore")
    pending = referenced_paths(text)
    extracted = 0
    missing: set[str] = set()
    seen: set[str] = set()

    local_design_css = ROOT / "scripts/healthcode-design-system/css/healthcode-theme.css"
    local_design_js = ROOT / "scripts/healthcode-design-system/js/healthcode-animations.js"
    design_css_target = PAGES / "wp-content/plugins/healthcode-design-system/css/healthcode-theme.css"
    design_js_target = PAGES / "wp-content/plugins/healthcode-design-system/js/healthcode-animations.js"
    design_css_target.parent.mkdir(parents=True, exist_ok=True)
    design_js_target.parent.mkdir(parents=True, exist_ok=True)
    design_css_target.write_bytes(local_design_css.read_bytes())
    design_js_target.write_bytes(local_design_js.read_bytes())

    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        if extract_file(index, path):
            extracted += 1
            target = PAGES / path
            if target.suffix.lower() == ".css":
                pending.update(css_url_paths(target) - seen)
        elif path not in {
            "wp-content/plugins/healthcode-design-system/css/healthcode-theme.css",
            "wp-content/plugins/healthcode-design-system/js/healthcode-animations.js",
        }:
            missing.add(path)

    print(f"Extracted {extracted} archive assets")
    print(f"Copied HealthCode design assets")
    if missing:
        print("Missing assets:")
        for path in sorted(missing):
            print(path)


if __name__ == "__main__":
    main()
