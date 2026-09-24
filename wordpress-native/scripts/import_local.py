"""Import an approved native layout locally, then invalidate matching cached HTML."""

from __future__ import annotations

import argparse
import ipaddress
import json
import math
import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from native_settings import NativeEnvironment


def validate_local_endpoint(endpoint: str) -> str:
    """Only local IPC transports are accepted; TCP and SSH are never local proof."""
    parsed = urlsplit(endpoint)
    if parsed.query or parsed.fragment or "\\" in endpoint or "/../" in endpoint:
        raise ValueError("Docker endpoint must be a local Unix socket or named pipe")
    if parsed.scheme == "unix" and not parsed.netloc and parsed.path.startswith("/"):
        return endpoint
    if endpoint.startswith("npipe:////./pipe/") and len(endpoint) > len("npipe:////./pipe/"):
        return endpoint
    raise ValueError("Docker endpoint must be a local Unix socket or named pipe")


def local_docker_command(docker: str, timeout: float) -> tuple[list[str], dict[str, str]]:
    environment = dict(os.environ)
    if environment.get("DOCKER_HOST"):
        validate_local_endpoint(environment["DOCKER_HOST"])
    result = subprocess.run(
        [docker, "context", "inspect"], capture_output=True, check=False, timeout=timeout, env=environment
    )
    if result.returncode:
        raise RuntimeError("Cannot verify Docker context; no import was attempted")
    endpoint = validate_local_endpoint(json.loads(result.stdout)[0]["Endpoints"]["docker"]["Host"])
    if environment.get("DOCKER_HOST") and not environment.get("DOCKER_CONTEXT"):
        endpoint = validate_local_endpoint(environment["DOCKER_HOST"])
    for key in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
        environment.pop(key, None)
    return [docker, "--host", endpoint], environment


def loopback_only(url: str) -> None:
    host = urlsplit(url).hostname
    if host == "localhost":
        return
    if not host or not ipaddress.ip_address(host).is_loopback:
        raise ValueError("This importer is restricted to local preview URLs")


def import_layouts(docker: str, environment: Path, compose: Path, project: str, timeout: float) -> None:
    settings = NativeEnvironment.load(environment)
    loopback_only(settings.site_url)
    if settings.wp_environment_type != "local":
        raise ValueError("Only the local environment can use the layout-replacing importer")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Command timeout must be positive")
    executable, process_environment = local_docker_command(docker, timeout)
    base = [*executable, "compose", "-p", project, "--env-file", str(environment), "-f", str(compose)]
    # Do not expose Compose's resolved environment or command output containing secrets.
    for arguments in [
        ["run", "--rm", "-T", "cli", "eval-file", "/import/import.php"],
        ["restart", "gateway"],
    ]:
        result = subprocess.run(
            base + arguments, capture_output=True, check=False, timeout=timeout, env=process_environment
        )
        if result.returncode:
            raise RuntimeError("Local import/cache invalidation failed; inspect the local service state")
    print("Native layouts imported locally and gateway cache invalidated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", required=True)
    parser.add_argument("--environment", required=True, type=Path)
    parser.add_argument("--compose", required=True, type=Path)
    parser.add_argument("--project", required=True)
    parser.add_argument("--timeout", required=True, type=float)
    parser.add_argument(
        "--replace-native-layouts",
        required=True,
        action="store_true",
        help="Acknowledge that the approved import replaces local Elementor content",
    )
    arguments = parser.parse_args()
    import_layouts(arguments.docker, arguments.environment, arguments.compose, arguments.project, arguments.timeout)
