#!/usr/bin/env python3
"""Boundary Access helper-noise sweep for rescue policies.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_helper_quality as helper_quality
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_helper_noise_sweep_outputs"

NOISE_LEVELS = [0.0, 0.15, 0.35, 0.55, 0.75]
POLICIES = ["always_fresh", "always_deep", "adaptive_damage"]


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

    rows: list[dict[str, float | str]] = []
    old_noise = helper_quality.NOISE_LEVEL
    old_trials = event.loop.TRIALS
    event.loop.TRIALS = 24
    noisy_mode = helper_quality.HelperMode("noisy", "Noisy helper")

    for noise_level in NOISE_LEVELS:
        helper_quality.NOISE_LEVEL = noise_level
        noise_rows = [helper_quality.evaluate(policy, noisy_mode, words, vocab_index) for policy in POLICIES]
        for row in noise_rows:
            row["noise_level"] = noise_level
            rows.append(row)

    helper_quality.NOISE_LEVEL = old_noise
    event.loop.TRIALS = old_trials

    write_csv(rows, OUT / "noise_sweep_metrics.csv")

    lines = [
        "# Boundary Access Helper Noise Sweep",
        "",
        f"- noise levels `{NOISE_LEVELS}`",
        "",
        "Best policy by noise level:",
    ]
    for noise_level in NOISE_LEVELS:
        subset = [row for row in rows if row["noise_level"] == noise_level]
        best = max(subset, key=lambda row: float(row["score_total"]))
        lines.append(f"- noise `{noise_level}`: `{best['policy']}` `{float(best['score_total']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
