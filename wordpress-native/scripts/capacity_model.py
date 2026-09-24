"""Offline planning arithmetic; this is never a benchmark or a provisioner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def model(plan: dict) -> dict:
    assumptions = plan["illustrative_assumptions"]
    interval = float(assumptions["seconds_between_page_views"])
    hit = float(assumptions["edge_cache_hit_ratio"])
    if interval <= 0 or not 0 <= hit <= 1:
        raise ValueError("Invalid request interval or cache ratio")
    availability = float(plan["availability_target"])
    if not 0 < availability < 1:
        raise ValueError("Availability target must be between zero and one")
    scenarios = []
    for users in plan["concurrent_reader_targets"]:
        if users <= 0:
            raise ValueError("Reader targets must be positive")
        page_views = users / interval
        requests = page_views * assumptions["requests_per_page_view"]
        origin_rps = requests * (1 - hit)
        scenarios.append(
            {
                "concurrent_readers": users,
                "page_views_per_second": round(page_views, 2),
                "edge_requests_per_second": round(requests, 2),
                "origin_requests_per_second": round(origin_rps, 2),
                "approx_origin_requests_in_flight": round(origin_rps * assumptions["origin_response_seconds"], 2),
                "estimated_edge_gigabits_per_second": round(
                    page_views * assumptions["bytes_per_page_view"] * 8 / 1_000_000_000, 3
                ),
            }
        )
    return {
        "status": "ILLUSTRATIVE_MODEL_NOT_MEASURED_CAPACITY",
        "assumptions": assumptions,
        "time_based_error_budget_minutes": round((1 - availability) * plan["availability_window_days"] * 24 * 60, 2),
        "scenarios": scenarios,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    print(json.dumps(model(json.loads(args.plan.read_text(encoding="utf-8"))), indent=2))
