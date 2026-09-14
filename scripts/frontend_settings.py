"""Single typed configuration boundary for the editorial frontend."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "frontend" / "site.config.json"


def project_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Frontend paths must stay inside the project")
    return path


@dataclass(frozen=True)
class FrontendSettings:
    root: Path
    source_export: Path
    output: Path
    content: Path
    copy: Path
    tools: Path
    templates: Path
    assets: Path
    styles: Path
    scripts: Path
    preview_host: str
    preview_port: int
    public_origin: str
    client: dict[str, Any]
    content_groups: dict[str, int]
    words_per_minute: int
    image_width: int
    image_quality: int

    @classmethod
    def load(cls, config: Path = DEFAULT_CONFIG, root: Path = PROJECT_ROOT) -> FrontendSettings:
        values = json.loads(config.read_text(encoding="utf-8"))
        for key in ("source_export", "output", "content", "copy", "tools", "templates", "assets", "styles", "scripts"):
            values[key] = project_path(root, values[key])
        if values["output"] in (root.resolve(), values["source_export"]):
            raise ValueError("Preview output must be separate from source")
        if values["preview_host"] not in ("127.0.0.1", "::1", "localhost"):
            raise ValueError("Local preview must bind to loopback")
        if not 1024 <= values["preview_port"] <= 65535:
            raise ValueError("Invalid preview port")
        if urlparse(values["public_origin"]).scheme != "https":
            raise ValueError("Public origin must use HTTPS")
        if values["words_per_minute"] <= 0 or values["image_width"] <= 0:
            raise ValueError("Content and image dimensions must be positive")
        return cls(root=root.resolve(), **values)
