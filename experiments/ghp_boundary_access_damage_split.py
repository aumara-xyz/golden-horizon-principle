#!/usr/bin/env python3
"""Boundary Access Channel damage-type split for rescue families.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_damage_split_outputs"

OVERLOAD_GAIN = 1.35
WRONG_SHIFT = 7


@dataclass(frozen=True)
class SplitFamily:
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


def make_wrong_signal(hist: np.ndarray) -> np.ndarray:
    return np.roll(hist, WRONG_SHIFT)


def make_overload(hist: np.ndarray, wrong_hist: np.ndarray) -> np.ndarray:
    overloaded = hist + OVERLOAD_GAIN * wrong_hist
    return event.loop.normalize(overloaded)


def evaluate_damage_mode(
    family: SplitFamily,
    damage_mode: str,
    words: dict[str, str],
    vocab_index: dict[str, int],
) -> dict[str, float | str]:
    word = words["fibonacci"]
    truth = event.loop.base.full_histogram(word, event.loop.base.KMER, vocab_index)

    access_scores: list[float] = []
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    shared_damage_scores: list[float] = []

    limit = len(word) - event.loop.base.KMER + 1

    for _ in range(event.loop.TRIALS):
        start_a = int(event.loop.RNG.integers(0, limit))
        start_b = int(event.loop.RNG.integers(0, limit))

        wake = np.zeros(len(vocab_index), dtype=float)
        deep_trace = np.zeros(len(vocab_index), dtype=float)
        frozen_old = np.zeros(len(vocab_index), dtype=float)
        wake_history: deque[np.ndarray] = deque(maxlen=groove.MEDIUM_DELAY + 6)

        for step in range(event.loop.TIMESTEPS):
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

            readable_a = event.loop.normalize(current_a)
            readable_b = event.loop.normalize(current_b)
            combined = event.loop.normalize(readable_a + readable_b)
            access_scores.append(event.loop.base.cosine(combined, truth))

            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * readable_b)
            deep_trace = event.loop.normalize(groove.DEEP_DECAY * deep_trace + (1.0 - groove.DEEP_DECAY) * wake)
            wake_history.append(wake.copy())
            if step == groove.FROZEN_STEP:
                frozen_old = wake.copy()

            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                continue

            wrong_hist = make_wrong_signal(readable_a)
            if damage_mode == "missing":
                damaged = event.apply_damage(readable_a, event.MASK_KEEP_DAMAGE)
            elif damage_mode == "wrong":
                damaged = wrong_hist
            elif damage_mode == "overload":
                damaged = make_overload(readable_a, wrong_hist)
            else:
                raise ValueError(damage_mode)

            masked_only = event.loop.base.cosine(damaged, truth)
            damage_level = event.damage_score(damaged, truth)
            payload = groove.groove_payload(
                family.name,
                wake,
                wake_history,
                deep_trace,
                frozen_old,
                len(vocab_index),
            )
            rescue = event.trigger_scale("event", damage_level, payload) * payload

            recovered = event.loop.recover_from_sources(damaged, readable_b, event.FALLBACK_GAIN * rescue)
            recovered_score = event.loop.base.cosine(recovered, truth)
            repair_scores.append(recovered_score)
            repair_gain_scores.append(max(0.0, recovered_score - masked_only))
            shared_damage_scores.append(
                0.5 * (event.loop.base.cosine(recovered, readable_b) + event.loop.top_overlap(recovered, readable_b))
            )

    def mean_or_zero(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    metrics = {
        "damage_mode": damage_mode,
        "family": family.name,
        "label": family.label,
        "access_fidelity": float(np.mean(access_scores)),
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "shared_overlap_after_damage": mean_or_zero(shared_damage_scores),
    }
    metrics["score_core"] = (
        0.45 * metrics["repair_score"]
        + 0.40 * metrics["repair_gain"]
        + 0.15 * metrics["shared_overlap_after_damage"]
    )
    return metrics


def main() -> None:
    ensure_dir(OUT)
    words = event.loop.build_words()
    vocab = event.loop.base.collect_vocabulary(words, event.loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    families = [
        SplitFamily("no_return", "No return"),
        SplitFamily("fresh_echo", "Fresh echo"),
        SplitFamily("deep_trace", "Deep trace"),
        SplitFamily("layered_recent_deep", "Layered recent + deep"),
    ]
    damage_modes = ["missing", "wrong", "overload"]

    rows = [
        evaluate_damage_mode(family, damage_mode, words, vocab_index)
        for damage_mode in damage_modes
        for family in families
    ]
    write_csv(rows, OUT / "damage_split_metrics.csv")

    winners = {}
    for damage_mode in damage_modes:
        subset = [row for row in rows if row["damage_mode"] == damage_mode]
        winners[damage_mode] = max(subset, key=lambda row: float(row["score_core"]))

    report = f"""# Boundary Access Damage Split

Winners by damage mode:
- missing signal: `{winners['missing']['family']}` core score `{float(winners['missing']['score_core']):.3f}`
- wrong signal: `{winners['wrong']['family']}` core score `{float(winners['wrong']['score_core']):.3f}`
- overload: `{winners['overload']['family']}` core score `{float(winners['overload']['score_core']):.3f}`

Interpretation:
- This asks whether different rescue families help different kinds of observer failure.
- If the winner changes by damage type, then repair is not one generic memory trick.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    for damage_mode in damage_modes:
        winner = winners[damage_mode]
        print(f"{damage_mode}: {winner['family']} {float(winner['score_core']):.3f}")


if __name__ == "__main__":
    main()
