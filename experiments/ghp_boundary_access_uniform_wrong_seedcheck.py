#!/usr/bin/env python3
"""Seed check for the uniform-smear wrong-signal split.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_event_fallback as event
import ghp_boundary_access_uniform_damage_modes as damage_modes


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_uniform_wrong_seedcheck_outputs"

SEEDS = [20260526, 20260527, 20260528, 20260529, 20260530]
NOISE_LEVELS = [0.20, 0.30, 0.40]
VIEWS = ["balanced", "repair_heavy"]


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
    words = damage_modes.build_words()
    vocab = damage_modes.base.collect_vocabulary(words, damage_modes.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    rows: list[dict[str, float | str]] = []
    old_rng = event.loop.RNG

    try:
        for seed in SEEDS:
            event.loop.RNG = np.random.default_rng(seed)
            for noise_level in NOISE_LEVELS:
                for family_name in damage_modes.FAMILIES:
                    metrics = damage_modes.evaluate_family_damage(
                        family_name,
                        noise_level,
                        "wrong",
                        words,
                        vocab_index,
                    )
                    metrics["seed"] = seed
                    rows.append(metrics)
    finally:
        event.loop.RNG = old_rng

    write_csv(rows, OUT / "uniform_wrong_seed_metrics.csv")

    lines = [
        "# Boundary Access Uniform Wrong-Signal Seed Check",
        "",
        f"- seeds `{SEEDS}`",
        "",
        "Winning family counts by noise and score view:",
    ]
    for noise_level in NOISE_LEVELS:
        subset = [row for row in rows if float(row["noise_level"]) == noise_level]
        for view in VIEWS:
            winners: dict[str, int] = {}
            key = f"score_{view}"
            for seed in SEEDS:
                seed_rows = [row for row in subset if int(row["seed"]) == seed]
                best = max(seed_rows, key=lambda row: float(row[key]))
                family = str(best["family"])
                winners[family] = winners.get(family, 0) + 1
            lines.append(f"- noise {noise_level:.2f} / {view}: `{winners}`")

    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
