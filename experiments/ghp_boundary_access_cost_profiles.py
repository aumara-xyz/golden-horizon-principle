#!/usr/bin/env python3
"""Boundary Access mode scores under explicit access-cost profiles.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_boundary_modes as boundary_modes
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_cost_profiles_outputs"

COST_PROFILES = {
    "light_cost": {
        "current": 0.02,
        "delayed": 0.01,
        "low_noise": 0.03,
        "high_noise": 0.01,
        "no_helper": 0.0,
        "illegal_truth": 0.08,
    },
    "strict_cheat": {
        "current": 0.02,
        "delayed": 0.01,
        "low_noise": 0.03,
        "high_noise": 0.01,
        "no_helper": 0.0,
        "illegal_truth": 0.18,
    },
    "ops_heavy": {
        "current": 0.04,
        "delayed": 0.03,
        "low_noise": 0.06,
        "high_noise": 0.02,
        "no_helper": 0.0,
        "illegal_truth": 0.16,
    },
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict[str, float | str]], path: Path) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text)


def main() -> None:
    ensure_dir(OUT)
    words = event.loop.build_words()
    vocab = event.loop.base.collect_vocabulary(words, event.loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    base_rows = [boundary_modes.evaluate_mode(mode, words, vocab_index) for mode in [
        boundary_modes.BoundaryMode("current", "Current local access"),
        boundary_modes.BoundaryMode("delayed", "Delayed local access"),
        boundary_modes.BoundaryMode("low_noise", "Low-noise local access"),
        boundary_modes.BoundaryMode("high_noise", "High-noise local access"),
        boundary_modes.BoundaryMode("no_helper", "No helper access"),
        boundary_modes.BoundaryMode("illegal_truth", "Illegal truth access"),
    ]]

    rows: list[dict[str, float | str]] = []
    for profile_name, profile in COST_PROFILES.items():
        for row in base_rows:
            new_row = dict(row)
            mode = str(row["mode"])
            new_row["profile"] = profile_name
            new_row["access_cost"] = profile[mode]
            new_row["net_score"] = float(row["score_boundary"]) - float(profile[mode])
            rows.append(new_row)

    write_csv(rows, OUT / "cost_profile_metrics.csv")

    lines = [
        "# Boundary Access Cost Profiles",
        "",
        "Best access mode by profile:",
    ]
    for profile_name in COST_PROFILES:
        subset = [row for row in rows if row["profile"] == profile_name]
        best = max(subset, key=lambda row: float(row["net_score"]))
        lines.append(f"- {profile_name}: `{best['mode']}` net `{float(best['net_score']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
