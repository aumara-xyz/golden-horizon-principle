#!/usr/bin/env python3
"""Boundary Access helper-quality sweep for rescue policies.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_adaptive_policy as adaptive
import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_helper_quality_outputs"

NOISE_LEVEL = 0.35


@dataclass(frozen=True)
class HelperMode:
    name: str
    label: str


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


def helper_view(mode: str, readable_b: np.ndarray, prev_b: np.ndarray, truth: np.ndarray) -> np.ndarray:
    if mode == "current":
        return readable_b
    if mode == "delayed":
        return prev_b
    if mode == "noisy":
        noise = event.loop.RNG.random(len(readable_b))
        mixed = (1.0 - NOISE_LEVEL) * readable_b + NOISE_LEVEL * noise
        return event.loop.normalize(mixed)
    if mode == "illegal_truth":
        return truth
    raise ValueError(mode)


def evaluate(policy_name: str, helper_mode: HelperMode, words: dict[str, str], vocab_index: dict[str, int]) -> dict[str, float | str]:
    word = words["fibonacci"]
    truth = event.loop.base.full_histogram(word, event.loop.base.KMER, vocab_index)
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    identity_scores: list[float] = []
    scene_scores: list[float] = []
    direction_scores: list[float] = []

    limit = len(word) - event.loop.base.KMER + 1
    damage_modes = ["missing", "wrong", "overload"]

    for _ in range(event.loop.TRIALS):
        start_a = int(event.loop.RNG.integers(0, limit))
        start_b = int(event.loop.RNG.integers(0, limit))

        wake = np.zeros(len(vocab_index), dtype=float)
        deep_trace = np.zeros(len(vocab_index), dtype=float)
        frozen_old = np.zeros(len(vocab_index), dtype=float)
        prev_b = np.zeros(len(vocab_index), dtype=float)
        wake_history: deque[np.ndarray] = deque(maxlen=groove.MEDIUM_DELAY + 6)

        for step in range(event.loop.TIMESTEPS - 1):
            current_a = event.loop.base.histogram_from_positions(
                word,
                event.loop.chunk_positions(len(word), event.loop.CHUNK, start_a + step),
                event.loop.base.KMER,
                vocab_index,
            )
            current_b = event.loop.base.histogram_from_positions(
                word,
                event.loop.chunk_positions(len(word), event.loop.SECOND_CHUNK, start_b + 2 * step),
                event.loop.base.KMER,
                vocab_index,
            )
            next_a = event.loop.base.histogram_from_positions(
                word,
                event.loop.chunk_positions(len(word), event.loop.CHUNK, start_a + step + 1),
                event.loop.base.KMER,
                vocab_index,
            )

            readable_a = event.loop.normalize(current_a)
            readable_b = event.loop.normalize(current_b)
            next_readable = event.loop.normalize(next_a)

            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * readable_b)
            deep_trace = event.loop.normalize(groove.DEEP_DECAY * deep_trace + (1.0 - groove.DEEP_DECAY) * wake)
            wake_history.append(wake.copy())
            if step == groove.FROZEN_STEP:
                frozen_old = wake.copy()

            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                prev_b = readable_b
                continue

            damage_mode = damage_modes[int(event.loop.RNG.integers(0, len(damage_modes)))]
            damaged = adaptive.apply_damage_mode(damage_mode, readable_a)
            payload = adaptive.choose_payload(
                policy_name,
                damage_mode,
                wake,
                wake_history,
                deep_trace,
                frozen_old,
                len(vocab_index),
            )
            rescue = event.trigger_scale("event", event.damage_score(damaged, readable_a), payload) * payload
            helper = helper_view(helper_mode.name, readable_b, prev_b, truth)
            recovered = event.loop.normalize(0.34 * damaged + 0.33 * helper + 0.33 * rescue)

            masked_self = event.loop.base.cosine(damaged, readable_a)
            repair = event.loop.base.cosine(recovered, readable_a)
            repair_scores.append(repair)
            repair_gain_scores.append(max(0.0, repair - masked_self))
            identity_scores.append(event.loop.base.cosine(recovered, deep_trace))
            scene_scores.append(event.loop.base.cosine(recovered, readable_a))
            direction_scores.append(event.loop.base.cosine(recovered, next_readable))
            prev_b = readable_b

    def mean_or_zero(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    metrics = {
        "policy": policy_name,
        "helper_mode": helper_mode.name,
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "identity_restore": mean_or_zero(identity_scores),
        "scene_restore": mean_or_zero(scene_scores),
        "direction_restore": mean_or_zero(direction_scores),
    }
    metrics["score_total"] = (
        0.25 * metrics["repair_score"]
        + 0.20 * metrics["repair_gain"]
        + 0.20 * metrics["identity_restore"]
        + 0.20 * metrics["scene_restore"]
        + 0.15 * metrics["direction_restore"]
    )
    return metrics


def main() -> None:
    ensure_dir(OUT)
    words = event.loop.build_words()
    vocab = event.loop.base.collect_vocabulary(words, event.loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    helper_modes = [
        HelperMode("current", "Current helper"),
        HelperMode("delayed", "Delayed helper"),
        HelperMode("noisy", "Noisy helper"),
        HelperMode("illegal_truth", "Illegal truth helper"),
    ]
    policies = ["always_fresh", "always_deep", "adaptive_damage"]

    rows = [evaluate(policy, helper_mode, words, vocab_index) for helper_mode in helper_modes for policy in policies]
    ranked = sorted(rows, key=lambda row: (row["helper_mode"], -float(row["score_total"])))
    write_csv(rows, OUT / "helper_quality_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    lines = [
        "# Boundary Access Helper Quality",
        "",
        f"- noise level `{NOISE_LEVEL}`",
        "",
        "Best policy by helper mode:",
    ]
    for helper_mode in helper_modes:
        subset = [row for row in rows if row["helper_mode"] == helper_mode.name]
        best = max(subset, key=lambda row: float(row["score_total"]))
        lines.append(f"- {helper_mode.name}: `{best['policy']}` `{float(best['score_total']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")
    for helper_mode in helper_modes:
        subset = [row for row in rows if row["helper_mode"] == helper_mode.name]
        best = max(subset, key=lambda row: float(row["score_total"]))
        print(f"{helper_mode.name}: {best['policy']} {float(best['score_total']):.3f}")


if __name__ == "__main__":
    main()
