#!/usr/bin/env python3
"""Boundary Access policy+mode net score under explicit access costs.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_boundary_modes as boundary_modes
import ghp_boundary_access_boundary_policy_grid as policy_grid
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_mode_policy_net_outputs"

COST_PROFILES = {
    "light_cost": {
        "current": 0.02,
        "high_noise": 0.01,
        "no_helper": 0.0,
        "illegal_truth": 0.08,
    },
    "strict_cheat": {
        "current": 0.02,
        "high_noise": 0.01,
        "no_helper": 0.0,
        "illegal_truth": 0.18,
    },
    "ops_heavy": {
        "current": 0.04,
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

    base_rows = [policy_grid.evaluate(policy, mode, words, vocab_index) for mode in policy_grid.MODES for policy in policy_grid.POLICIES]

    rows: list[dict[str, float | str]] = []
    for profile_name, profile in COST_PROFILES.items():
        for row in base_rows:
            mode = str(row["mode"])
            new_row = dict(row)
            new_row["profile"] = profile_name
            new_row["access_cost"] = profile[mode]
            new_row["net_score"] = float(row["score_grid"]) - float(profile[mode])
            rows.append(new_row)

    write_csv(rows, OUT / "mode_policy_net.csv")

    lines = [
        "# Boundary Access Mode + Policy Net",
        "",
        "Best combo by profile:",
    ]
    for profile_name in COST_PROFILES:
        subset = [row for row in rows if row["profile"] == profile_name]
        best = max(subset, key=lambda row: float(row["net_score"]))
        lines.append(
            f"- {profile_name}: mode=`{best['mode']}` policy=`{best['policy']}` net=`{float(best['net_score']):.3f}`"
        )
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
