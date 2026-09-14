"""Typed environment boundary for native WordPress build/deployment tooling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class NativeEnvironment:
    wp_image: str
    db_image: str
    cli_image: str
    edge_image: str
    wp_port: int
    db_name: str
    db_user: str
    db_password: str = field(repr=False)
    db_root_password: str = field(repr=False)
    admin_user: str
    admin_password: str = field(repr=False)
    admin_email: str
    site_url: str
    wp_environment_type: str

    @classmethod
    def load(cls, path: Path) -> NativeEnvironment:
        values = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip().lower()] = value.strip()
        expected = set(cls.__dataclass_fields__)
        if set(values) != expected:
            raise ValueError("Environment keys differ from the typed settings contract")
        instance = cls(
            wp_image=values["wp_image"],
            db_image=values["db_image"],
            cli_image=values["cli_image"],
            edge_image=values["edge_image"],
            wp_port=int(values["wp_port"]),
            db_name=values["db_name"],
            db_user=values["db_user"],
            db_password=values["db_password"],
            db_root_password=values["db_root_password"],
            admin_user=values["admin_user"],
            admin_password=values["admin_password"],
            admin_email=values["admin_email"],
            site_url=values["site_url"],
            wp_environment_type=values["wp_environment_type"],
        )
        if not 1 <= instance.wp_port <= 65535:
            raise ValueError("Invalid WordPress port")
        if instance.wp_environment_type not in {"local", "development", "staging", "production"}:
            raise ValueError("Invalid WordPress environment type")
        parsed = urlsplit(instance.site_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Invalid site URL")
        if instance.wp_environment_type == "production" and parsed.scheme != "https":
            raise ValueError("Production requires HTTPS")
        if not all((instance.db_password, instance.db_root_password, instance.admin_password)):
            raise ValueError("Required private credentials are missing")
        return instance
