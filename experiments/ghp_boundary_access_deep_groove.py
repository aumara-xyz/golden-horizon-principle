#!/usr/bin/env python3
"""Boundary Access Channel deep-groove rescue comparison.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_deep_groove_outputs"

MEDIUM_DELAY = 4
DEEP_DECAY = 0.97
LAYER_BLEND = 0.58
FROZEN_STEP = 12


@dataclass(frozen=True)
class GrooveFamily:
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


def groove_payload(
    family_name: str,
    fresh_wake: np.ndarray,
    wake_history: deque[np.ndarray],
    deep_trace: np.ndarray,
    frozen_old: np.ndarray,
    vocab_size: int,
) -> np.ndarray:
    if family_name == "no_return":
        return np.zeros(vocab_size, dtype=float)
    if family_name == "fresh_echo":
        return fresh_wake
    if family_name == "short_delay":
        return wake_history[-2] if len(wake_history) >= 2 else fresh_wake
    if family_name == "medium_delay":
        return wake_history[-(MEDIUM_DELAY + 1)] if len(wake_history) > MEDIUM_DELAY else wake_history[0]
    if family_name == "deep_trace":
        return deep_trace
    if family_name == "frozen_old":
        return frozen_old if frozen_old.sum() > 0 else deep_trace
    if family_name == "layered_recent_deep":
        return event.loop.normalize(LAYER_BLEND * deep_trace + (1.0 - LAYER_BLEND) * fresh_wake)
    raise ValueError(family_name)


def evaluate_family(family: GrooveFamily, words: dict[str, str], vocab_index: dict[str, int]) -> dict[str, float | str]:
    word = words["fibonacci"]
    truth = event.loop.base.full_histogram(word, event.loop.base.KMER, vocab_index)

    access_scores: list[float] = []
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    shared_damage_scores: list[float] = []
    trigger_rates: list[float] = []

    limit = len(word) - event.loop.base.KMER + 1

    for _ in range(event.loop.TRIALS):
        start_a = int(event.loop.RNG.integers(0, limit))
        start_b = int(event.loop.RNG.integers(0, limit))

        wake = np.zeros(len(vocab_index), dtype=float)
        deep_trace = np.zeros(len(vocab_index), dtype=float)
        frozen_old = np.zeros(len(vocab_index), dtype=float)
        wake_history: deque[np.ndarray] = deque(maxlen=MEDIUM_DELAY + 6)

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
            deep_trace = event.loop.normalize(DEEP_DECAY * deep_trace + (1.0 - DEEP_DECAY) * wake)
            wake_history.append(wake.copy())

            if step == FROZEN_STEP:
                frozen_old = wake.copy()

            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                continue

            damaged = event.apply_damage(readable_a, event.MASK_KEEP_DAMAGE)
            masked_only = event.loop.base.cosine(damaged, truth)
            damage_level = event.damage_score(damaged, truth)

            payload = groove_payload(
                family.name,
                wake,
                wake_history,
                deep_trace,
                frozen_old,
                len(vocab_index),
            )
            scale = event.trigger_scale("event", damage_level, payload)
            trigger_rates.append(scale)
            rescue = scale * payload

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
        "family": family.name,
        "label": family.label,
        "access_fidelity": float(np.mean(access_scores)),
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "shared_overlap_after_damage": mean_or_zero(shared_damage_scores),
        "trigger_rate": mean_or_zero(trigger_rates),
    }
    metrics["score_event"] = (
        0.20 * metrics["access_fidelity"]
        + 0.35 * metrics["repair_score"]
        + 0.30 * metrics["repair_gain"]
        + 0.15 * metrics["shared_overlap_after_damage"]
    )
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
        GrooveFamily("no_return", "No return"),
        GrooveFamily("fresh_echo", "Fresh echo"),
        GrooveFamily("short_delay", "Short delay"),
        GrooveFamily("medium_delay", "Medium delay"),
        GrooveFamily("deep_trace", "Deep trace"),
        GrooveFamily("frozen_old", "Frozen old wake"),
        GrooveFamily("layered_recent_deep", "Layered recent + deep"),
    ]

    rows = [evaluate_family(family, words, vocab_index) for family in families]
    ranked = sorted(rows, key=lambda row: float(row["score_event"]), reverse=True)
    core_ranked = sorted(rows, key=lambda row: float(row["score_core"]), reverse=True)
    write_csv(rows, OUT / "family_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    best = ranked[0]
    best_core = core_ranked[0]
    deep_trace = next(row for row in rows if row["family"] == "deep_trace")
    fresh = next(row for row in rows if row["family"] == "fresh_echo")
    layered = next(row for row in rows if row["family"] == "layered_recent_deep")
    short_delay = next(row for row in rows if row["family"] == "short_delay")

    report = f"""# Boundary Access Deep Groove

Config:
- damage mask keep `{event.MASK_KEEP_DAMAGE}`
- damage probability `{event.DAMAGE_PROB}`
- trigger threshold `{event.DAMAGE_TRIGGER_THRESHOLD}`
- deep decay `{DEEP_DECAY}`
- medium delay `{MEDIUM_DELAY}`
- frozen step `{FROZEN_STEP}`
- layer blend `{LAYER_BLEND}`

Best family:
- `{best['family']}` event score `{float(best['score_event']):.3f}`

Best core family:
- `{best_core['family']}` core score `{float(best_core['score_core']):.3f}`

Depth comparison:
- fresh echo core score `{float(fresh['score_core']):.3f}`
- short delay core score `{float(short_delay['score_core']):.3f}`
- deep trace core score `{float(deep_trace['score_core']):.3f}`
- layered recent + deep core score `{float(layered['score_core']):.3f}`

Interpretation:
- This asks whether rescue is strongest from fresh local continuity, delayed continuity, or deeper retained identity trace.
- If deep or layered families beat fresh echo, then the repair lane looks more like identity continuity than immediate local recall.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best family: {best['family']} {float(best['score_event']):.3f}")
    print(f"best core family: {best_core['family']} {float(best_core['score_core']):.3f}")


if __name__ == "__main__":
    main()
