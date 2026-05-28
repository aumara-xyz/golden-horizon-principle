#!/usr/bin/env python3
"""Seed stability check for integrated dual-cost harness lanes.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_boundary_modes as boundary_modes
import ghp_boundary_access_integrated_dual_cost as dual_cost
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_seed_stability_outputs"

SEEDS = [20260526, 20260527, 20260528, 20260529, 20260530]
TARGET_LANES = [
    ("current", 0.03, "light_cost"),
    ("high_noise", 0.03, "light_cost"),
]


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
    words = dual_cost.build_words()
    vocab = dual_cost.base.collect_vocabulary(words, dual_cost.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    rows: list[dict[str, float | str]] = []
    old_rng = event.loop.RNG

    for seed in SEEDS:
        event.loop.RNG = np.random.default_rng(seed)
        for mode_name, switch_cost, profile_name in TARGET_LANES:
            mode = next(mode for mode in dual_cost.MODES if mode.name == mode_name)
            for family in dual_cost.base.FAMILIES:
                metrics = dual_cost.evaluate_family_mode(family.name, mode, switch_cost, words, vocab_index)
                metrics["seed"] = seed
                metrics["profile"] = profile_name
                metrics["access_cost"] = dual_cost.COST_PROFILES[profile_name][mode_name]
                metrics["score_net"] = float(metrics["score_raw"]) - float(metrics["access_cost"])
                rows.append(metrics)

    event.loop.RNG = old_rng
    write_csv(rows, OUT / "seed_stability_metrics.csv")

    lines = [
        "# Boundary Access Seed Stability",
        "",
        f"- seeds `{SEEDS}`",
        "",
        "Winning family counts:",
    ]
    for mode_name, switch_cost, profile_name in TARGET_LANES:
        subset = [
            row for row in rows
            if row["mode"] == mode_name and float(row["switch_cost"]) == switch_cost and row["profile"] == profile_name
        ]
        winners: dict[str, int] = {}
        for seed in SEEDS:
            seed_rows = [row for row in subset if int(row["seed"]) == seed]
            best = max(seed_rows, key=lambda row: float(row["score_net"]))
            winners[str(best["family"])] = winners.get(str(best["family"]), 0) + 1
        lines.append(f"- {mode_name}: `{winners}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
