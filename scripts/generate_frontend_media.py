"""Execute the explicitly approved one-image/one-video pilot without retries."""

from __future__ import annotations

import argparse
import base64
import json
import os
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import requests

from frontend_settings import PROJECT_ROOT, project_path


@dataclass(frozen=True)
class MediaSettings:
    values: dict[str, Any]
    key: str = field(repr=False)

    @classmethod
    def load(cls) -> MediaSettings:
        values = json.loads((PROJECT_ROOT / "frontend/media.config.json").read_text(encoding="utf-8"))
        key = os.environ.get(values["key_env"], "")
        if not key:
            for line in project_path(PROJECT_ROOT, values["key_file"]).read_text(encoding="utf-8").splitlines():
                name, separator, value = line.partition("=")
                if separator and name.strip() == values["key_env"]:
                    key = value.strip().strip("\"'")
        if not key or urlparse(values["base_url"]).scheme != "https":
            raise ValueError("Missing media credential or invalid HTTPS configuration")
        return cls(values, key)


def run(action: str) -> None:
    settings = MediaSettings.load()
    config = settings.values
    ledger_path = project_path(PROJECT_ROOT, config["ledger"])
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {"approved_budget": config["budget_usd"]}

    def save() -> None:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")

    def request(method: str, url: str, **kwargs: Any) -> requests.Response:
        origin = urlparse(config["base_url"])
        target = urlparse(url)
        if target.scheme != "https" or target.netloc != origin.netloc:
            raise ValueError("Refusing to send the media credential to a different origin")
        with requests.Session() as session:
            session.trust_env = False
            response = session.request(
                method,
                url,
                headers={"Authorization": "Bearer " + settings.key},
                timeout=config["timeout_seconds"],
                allow_redirects=False,
                **kwargs,
            )
        if not response.ok:
            ledger["last_http_status"] = response.status_code
            save()
            raise RuntimeError(f"Media request returned HTTP {response.status_code}; no automatic retry")
        return response

    if action == "image":
        if "image" in ledger:
            raise ValueError("The approved image attempt was already submitted; refusing a duplicate")
        if config["image_reserve_usd"] + config["video_estimate_usd"] > config["budget_usd"]:
            raise ValueError("Pilot estimates exceed the approved budget")
        ledger["image"] = {"status": "submitted", "model": config["image"]["model"]}
        save()
        result = request("POST", config["base_url"] + config["image_endpoint"], json=config["image"]).json()
        output = project_path(PROJECT_ROOT, config["image_output"])
        output.write_bytes(base64.b64decode(result["data"][0]["b64_json"], validate=True))
        ledger["image"] = {"status": "completed", "output": config["image_output"], "usage": result.get("usage", {})}
        save()
        print("Image downloaded. Reported usage:", json.dumps(result.get("usage", {})), flush=True)
    elif action == "video":
        if "video" in ledger:
            raise ValueError("A video job already exists; use poll, never resubmit")
        image_record = ledger.get("image", {})
        cost = image_record.get("usage", {}).get("cost")
        if image_record.get("status") != "accepted" or cost is None:
            raise ValueError("The image needs visual acceptance and a known charge before video submission")
        if cost + config["video_estimate_usd"] > config["budget_usd"]:
            raise ValueError("Video would exceed the approved budget")
        payload = dict(config["video"])
        encoded = base64.b64encode(project_path(PROJECT_ROOT, config["image_output"]).read_bytes()).decode()
        payload["frame_images"] = [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + encoded}, "frame_type": "first_frame"}
        ]
        ledger["video"] = {"status": "submitting"}
        save()
        ledger["video"] = request("POST", config["base_url"] + config["video_endpoint"], json=payload).json()
        save()
        print("Video job recorded:", ledger["video"].get("id"), ledger["video"].get("status"), flush=True)
    else:
        video = ledger.get("video", {})
        if not video.get("polling_url"):
            raise ValueError("No recorded polling URL; do not create a replacement job")
        result = request("GET", video["polling_url"]).json()
        ledger["video"] = result
        save()
        print("Video status:", result.get("status"), "usage:", json.dumps(result.get("usage", {})), flush=True)
        if result.get("status") == "completed":
            content = request("GET", result["unsigned_urls"][0]).content
            project_path(PROJECT_ROOT, config["video_output"]).write_bytes(content)
            print("Video downloaded:", len(content), "bytes", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["image", "video", "poll"])
    run(parser.parse_args().action)
