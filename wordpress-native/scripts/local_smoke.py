"""Bounded loopback-only HTTP smoke measurement; never a production capacity claim."""
from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

import requests
from import_local import loopback_only
from native_settings import NativeEnvironment


@dataclass(frozen=True)
class SmokePlan:
    requests: int
    concurrency: int
    timeout_seconds: float
    pause_seconds: float
    maximum_requests: int
    maximum_concurrency: int
    path: str
    expected_status: int

    @classmethod
    def load(cls, path: Path) -> SmokePlan:
        plan = cls(**json.loads(path.read_text(encoding="utf-8")))
        if not 1 <= plan.requests <= plan.maximum_requests or not 1 <= plan.concurrency <= plan.maximum_concurrency:
            raise ValueError("Smoke request/concurrency limits exceeded")
        if plan.timeout_seconds <= 0 or plan.pause_seconds < 0 or not plan.path.startswith("/") or plan.path.startswith("//"):
            raise ValueError("Invalid smoke timing or relative path")
        return plan


def measure(environment: NativeEnvironment, plan: SmokePlan, marker: str) -> dict:
    loopback_only(environment.site_url)
    if environment.wp_environment_type != "local":
        raise ValueError("Smoke measurement is restricted to the local environment")
    url = environment.site_url.rstrip("/") + plan.path

    def probe(_index: int) -> dict:
        started = time.perf_counter()
        try:
            with requests.Session() as session:
                session.trust_env = False
                response = session.get(url, timeout=plan.timeout_seconds, allow_redirects=False)
                result = {
                    "success": response.status_code == plan.expected_status and marker in response.text,
                    "status": response.status_code,
                    "cache": response.headers.get("X-HealthCode-Cache", "NONE"),
                }
        except requests.RequestException:
            result = {"success": False, "status": "transport_error", "cache": "NONE"}
        result["milliseconds"] = round((time.perf_counter() - started) * 1000, 2)
        time.sleep(plan.pause_seconds)
        return result

    warmup = probe(0)
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=plan.concurrency) as pool:
        observations = list(pool.map(probe, range(plan.requests)))
    elapsed = time.perf_counter() - started
    latencies = sorted(float(item["milliseconds"]) for item in observations)
    return {
        "status": "LOCAL_SMOKE_NOT_PRODUCTION_CAPACITY",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "requests": plan.requests,
        "concurrency": plan.concurrency,
        "successful_responses": sum(bool(item["success"]) for item in observations),
        "warmup_success": warmup["success"],
        "elapsed_seconds": round(elapsed, 3),
        "observed_requests_per_second": round(plan.requests / elapsed, 2),
        "median_ms": round(median(latencies), 2),
        "p95_ms": latencies[math.ceil(len(latencies) * 0.95) - 1],
        "cache_status_counts": dict(Counter(str(item["cache"]) for item in observations)),
        "http_status_counts": dict(Counter(str(item["status"]) for item in observations)),
        "limitations": "Loopback HTTP only; no browser/media load or failover exercise. No production capacity or uptime claim.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    report = measure(NativeEnvironment.load(args.environment), SmokePlan.load(args.plan), policy["site_name"])
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["warmup_success"] and report["successful_responses"] == report["requests"] else 1)
