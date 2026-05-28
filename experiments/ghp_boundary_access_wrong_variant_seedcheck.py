#!/usr/bin/env python3
"""Seed check for contrasting wrong-signal variants.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_event_fallback as event
import ghp_boundary_access_wrong_signal_variants as variants


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_wrong_variant_seedcheck_outputs"

SEEDS = [20260526, 20260527, 20260528, 20260529, 20260530]
NOISE_LEVELS = [0.20, 0.30, 0.40]
TARGET_VARIANTS = ["permuted", "cross_family"]
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
    words = variants.build_words()
    vocab = variants.base.collect_vocabulary(words, variants.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    rows: list[dict[str, float | str]] = []
    old_rng = event.loop.RNG

    try:
        for seed in SEEDS:
            event.loop.RNG = np.random.default_rng(seed)
            for noise_level in NOISE_LEVELS:
                for wrong_variant in TARGET_VARIANTS:
                    for family_name in variants.FAMILIES:
                        metrics = variants.evaluate_family_variant(
                            family_name,
                            noise_level,
                            wrong_variant,
                            words,
                            vocab_index,
                        )
                        metrics["seed"] = seed
                        rows.append(metrics)
    finally:
        event.loop.RNG = old_rng

    write_csv(rows, OUT / "wrong_variant_seed_metrics.csv")

    lines = [
        "# Boundary Access Wrong Variant Seed Check",
        "",
        f"- seeds `{SEEDS}`",
        "",
        "Winning family counts by variant, noise, and score view:",
    ]
    for wrong_variant in TARGET_VARIANTS:
        subset = [row for row in rows if row["wrong_variant"] == wrong_variant]
        for noise_level in NOISE_LEVELS:
            noise_rows = [row for row in subset if float(row["noise_level"]) == noise_level]
            for view in VIEWS:
                winners: dict[str, int] = {}
                key = f"score_{view}"
                for seed in SEEDS:
                    seed_rows = [row for row in noise_rows if int(row["seed"]) == seed]
                    best = max(seed_rows, key=lambda row: float(row[key]))
                    family = str(best["family"])
                    winners[family] = winners.get(family, 0) + 1
                lines.append(f"- {wrong_variant} / noise {noise_level:.2f} / {view}: `{winners}`")

    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
