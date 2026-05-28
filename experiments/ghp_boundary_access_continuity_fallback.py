#!/usr/bin/env python3
"""Boundary Access Channel continuity-fallback comparison.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_continuity_fallback_outputs"

NEARBY_SHIFT = 3
DELAY_BLEND = 0.55


@dataclass(frozen=True)
class ContinuityFamily:
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


def continuity_payload(
    family_name: str,
    current_wake: np.ndarray,
    previous_wake: np.ndarray,
    companion_wake: np.ndarray,
    vocab_size: int,
) -> np.ndarray:
    if family_name == "no_return":
        return np.zeros(vocab_size, dtype=float)
    if family_name == "stale_same":
        return current_wake
    if family_name == "nearby_shift":
        return np.roll(current_wake, NEARBY_SHIFT)
    if family_name == "delayed_blend":
        return event.loop.normalize(DELAY_BLEND * previous_wake + (1.0 - DELAY_BLEND) * current_wake)
    if family_name == "shuffled":
        indices = event.loop.RNG.permutation(vocab_size)
        return current_wake[indices]
    if family_name == "cross_family":
        return companion_wake
    raise ValueError(family_name)


def evaluate_family(family: ContinuityFamily, words: dict[str, str], vocab_index: dict[str, int]) -> dict[str, float | str]:
    word = words["fibonacci"]
    truth = event.loop.base.full_histogram(word, event.loop.base.KMER, vocab_index)
    companion_word = words["tribonacci_control"]

    access_scores: list[float] = []
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    shared_damage_scores: list[float] = []
    trigger_rates: list[float] = []

    limit = len(word) - event.loop.base.KMER + 1
    companion_limit = len(companion_word) - event.loop.base.KMER + 1

    for _ in range(event.loop.TRIALS):
        start_a = int(event.loop.RNG.integers(0, limit))
        start_b = int(event.loop.RNG.integers(0, limit))
        companion_start = int(event.loop.RNG.integers(0, companion_limit))

        wake = np.zeros(len(vocab_index), dtype=float)
        prev_wake = np.zeros(len(vocab_index), dtype=float)
        companion_wake = np.zeros(len(vocab_index), dtype=float)

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

            companion_frag = event.loop.base.histogram_from_positions(
                companion_word,
                event.loop.chunk_positions(len(companion_word), event.loop.CHUNK, companion_start + step),
                event.loop.base.KMER,
                vocab_index,
            )

            prev_wake = wake.copy()
            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * readable_b)
            companion_wake = event.loop.normalize(event.WAKE_DECAY * companion_wake + companion_frag)

            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                continue

            damaged = event.apply_damage(readable_a, event.MASK_KEEP_DAMAGE)
            masked_only = event.loop.base.cosine(damaged, truth)
            damage_level = event.damage_score(damaged, truth)

            payload = continuity_payload(family.name, wake, prev_wake, companion_wake, len(vocab_index))
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
        ContinuityFamily("no_return", "No return"),
        ContinuityFamily("stale_same", "Stale same wake"),
        ContinuityFamily("nearby_shift", "Nearby shifted wake"),
        ContinuityFamily("delayed_blend", "Delayed blended wake"),
        ContinuityFamily("shuffled", "Shuffled wake"),
        ContinuityFamily("cross_family", "Cross-family wake"),
    ]

    rows = [evaluate_family(family, words, vocab_index) for family in families]
    ranked = sorted(rows, key=lambda row: float(row["score_event"]), reverse=True)
    core_ranked = sorted(rows, key=lambda row: float(row["score_core"]), reverse=True)
    write_csv(rows, OUT / "family_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    best = ranked[0]
    best_core = core_ranked[0]
    stale = next(row for row in rows if row["family"] == "stale_same")
    nearby = next(row for row in rows if row["family"] == "nearby_shift")
    delayed = next(row for row in rows if row["family"] == "delayed_blend")

    report = f"""# Boundary Access Continuity Fallback

Config:
- damage mask keep `{event.MASK_KEEP_DAMAGE}`
- damage probability `{event.DAMAGE_PROB}`
- trigger threshold `{event.DAMAGE_TRIGGER_THRESHOLD}`
- nearby shift `{NEARBY_SHIFT}`
- delayed blend `{DELAY_BLEND}`

Best family:
- `{best['family']}` event score `{float(best['score_event']):.3f}`

Best core family:
- `{best_core['family']}` core score `{float(best_core['score_core']):.3f}`

Continuity comparison:
- stale same core score `{float(stale['score_core']):.3f}`
- nearby shift core score `{float(nearby['score_core']):.3f}`
- delayed blend core score `{float(delayed['score_core']):.3f}`

Interpretation:
- This tests whether stale wake rescue is real continuity or just easy fallback.
- If same-wake continuity clearly beats nearby, delayed, shuffled, and cross-family wake, then retained continuity is doing real work.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best family: {best['family']} {float(best['score_event']):.3f}")
    print(f"best core family: {best_core['family']} {float(best_core['score_core']):.3f}")


if __name__ == "__main__":
    main()
