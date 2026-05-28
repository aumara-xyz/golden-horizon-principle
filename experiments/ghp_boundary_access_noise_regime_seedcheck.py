#!/usr/bin/env python3
"""Seed check for the hardening pass on Boundary Access noise regimes.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_event_fallback as event
import ghp_boundary_access_noise_regime_hardening as hardening


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_noise_regime_seedcheck_outputs"

SEEDS = [20260526, 20260527, 20260528, 20260529, 20260530]
SCENARIO_NAMES = ["clean_current", "uniform_mix_mid", "uniform_mix_high", "gaussian_mix_mid"]
SCORE_VIEWS = ["balanced", "repair_heavy"]


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
    words = hardening.build_words()
    vocab = hardening.base.collect_vocabulary(words, hardening.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    scenario_map = {str(s["name"]): s for s in hardening.SCENARIOS}
    rows: list[dict[str, float | str]] = []

    old_rng = event.loop.RNG
    try:
        for seed in SEEDS:
            event.loop.RNG = np.random.default_rng(seed)
            for scenario_name in SCENARIO_NAMES:
                scenario = scenario_map[scenario_name]
                for family in hardening.base.FAMILIES:
                    metrics = hardening.evaluate_family_scenario(family.name, scenario, words, vocab_index)
                    metrics["seed"] = seed
                    rows.append(metrics)
    finally:
        event.loop.RNG = old_rng

    write_csv(rows, OUT / "seedcheck_metrics.csv")

    lines = [
        "# Boundary Access Noise Regime Seed Check",
        "",
        f"- seeds `{SEEDS}`",
        "",
        "Winning family counts by scenario and score view:",
    ]
    for scenario_name in SCENARIO_NAMES:
        subset = [row for row in rows if row["scenario"] == scenario_name]
        for view in SCORE_VIEWS:
            winners: dict[str, int] = {}
            key = f"score_{view}"
            for seed in SEEDS:
                seed_rows = [row for row in subset if int(row["seed"]) == seed]
                best = max(seed_rows, key=lambda row: float(row[key]))
                family = str(best["family"])
                winners[family] = winners.get(family, 0) + 1
            lines.append(f"- {scenario_name} / {view}: `{winners}`")

    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
