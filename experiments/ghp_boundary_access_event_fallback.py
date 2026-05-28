#!/usr/bin/env python3
"""Boundary Access Channel event-triggered fallback toy.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_return_loop as loop


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_event_fallback_outputs"

MASK_KEEP_NORMAL = 0.50
MASK_KEEP_DAMAGE = 0.10
DAMAGE_PROB = 0.22
DAMAGE_TRIGGER_THRESHOLD = 0.28
FALLBACK_GAIN = 0.32
WAKE_DECAY = 0.90


@dataclass(frozen=True)
class FallbackFamily:
    name: str
    source_word: str
    return_mode: str
    trigger_mode: str
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


def apply_damage(hist: np.ndarray, keep: float) -> np.ndarray:
    if hist.sum() == 0.0:
        return hist.copy()
    keep_mask = loop.RNG.random(hist.shape[0]) < keep
    damaged = hist * keep_mask
    if damaged.sum() == 0.0:
        top_idx = int(np.argmax(hist))
        damaged[top_idx] = hist[top_idx]
    return loop.normalize(damaged)


def damage_score(masked: np.ndarray, truth: np.ndarray) -> float:
    return max(0.0, 1.0 - loop.base.cosine(masked, truth))


def trigger_scale(trigger_mode: str, damage_level: float, rotated_wake: np.ndarray) -> float:
    if trigger_mode == "none":
        return 0.0
    if trigger_mode == "always":
        return 1.0
    if trigger_mode == "event":
        return 1.0 if damage_level >= DAMAGE_TRIGGER_THRESHOLD else 0.0
    if trigger_mode == "event_soft":
        return float(np.clip((damage_level - DAMAGE_TRIGGER_THRESHOLD) / max(1e-9, 1.0 - DAMAGE_TRIGGER_THRESHOLD), 0.0, 1.0))
    if trigger_mode == "event_active":
        if damage_level < DAMAGE_TRIGGER_THRESHOLD:
            return 0.0
        return 1.0 if rotated_wake.sum() > 0 else 0.0
    raise ValueError(trigger_mode)


def fallback_payload(mode: str, wake: np.ndarray, offsets: list[int], step: int, vocab_size: int) -> np.ndarray:
    rotated = np.roll(wake, offsets[step])
    if mode == "none":
        return np.zeros(vocab_size, dtype=float)
    if mode == "fibonacci":
        return rotated
    if mode == "binary":
        return np.roll(wake, step % 2)
    if mode == "tribonacci":
        trib_offsets = loop.return_offsets("tribonacci", loop.TIMESTEPS, vocab_size)
        return np.roll(wake, trib_offsets[step])
    if mode == "random":
        random_shift = int(loop.RNG.integers(0, vocab_size))
        return np.roll(wake, random_shift)
    if mode == "stale":
        return wake
    raise ValueError(mode)


def evaluate_family(family: FallbackFamily, words: dict[str, str], vocab_index: dict[str, int]) -> dict[str, float | str]:
    word = words[family.source_word]
    truth = loop.base.full_histogram(word, loop.base.KMER, vocab_index)
    fib_offsets = loop.return_offsets("fibonacci", loop.TIMESTEPS, len(vocab_index))

    access_scores: list[float] = []
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    shared_damage_scores: list[float] = []
    trigger_rates: list[float] = []
    damage_levels: list[float] = []

    limit = len(word) - loop.base.KMER + 1

    for _ in range(loop.TRIALS):
        start_a = int(loop.RNG.integers(0, limit))
        start_b = int(loop.RNG.integers(0, limit))
        wake = np.zeros(len(vocab_index), dtype=float)

        for step in range(loop.TIMESTEPS):
            current_a = loop.base.histogram_from_positions(
                word,
                loop.chunk_positions(len(word), loop.CHUNK, start_a + step),
                loop.base.KMER,
                vocab_index,
            )
            current_b = loop.base.histogram_from_positions(
                word,
                loop.chunk_positions(len(word), loop.SECOND_CHUNK, start_b + 2 * step),
                loop.base.KMER,
                vocab_index,
            )
            readable_a = loop.normalize(current_a)
            readable_b = loop.normalize(current_b)
            combined = loop.normalize(readable_a + readable_b)
            access_scores.append(loop.base.cosine(combined, truth))

            wake = loop.normalize(WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * readable_b)

            if float(loop.RNG.random()) >= DAMAGE_PROB:
                continue

            damaged = apply_damage(readable_a, MASK_KEEP_DAMAGE)
            masked_only = loop.base.cosine(damaged, truth)
            damage_level = damage_score(damaged, truth)
            damage_levels.append(damage_level)

            payload = fallback_payload(family.return_mode, wake, fib_offsets, step, len(vocab_index))
            scale = trigger_scale(family.trigger_mode, damage_level, payload)
            trigger_rates.append(scale)
            rescue = scale * payload

            recovered = loop.recover_from_sources(damaged, readable_b, FALLBACK_GAIN * rescue)
            recovered_score = loop.base.cosine(recovered, truth)
            repair_scores.append(recovered_score)
            repair_gain_scores.append(max(0.0, recovered_score - masked_only))
            shared_damage_scores.append(0.5 * (loop.base.cosine(recovered, readable_b) + loop.top_overlap(recovered, readable_b)))

    def mean_or_zero(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    metrics = {
        "family": family.name,
        "label": family.label,
        "return_mode": family.return_mode,
        "trigger_mode": family.trigger_mode,
        "access_fidelity": float(np.mean(access_scores)),
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "shared_overlap_after_damage": mean_or_zero(shared_damage_scores),
        "trigger_rate": mean_or_zero(trigger_rates),
        "damage_level": mean_or_zero(damage_levels),
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
    words = loop.build_words()
    vocab = loop.base.collect_vocabulary(words, loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    families = [
        FallbackFamily("no_return", "fibonacci", "none", "none", "No return"),
        FallbackFamily("always_fibonacci", "fibonacci", "fibonacci", "always", "Always Fibonacci fallback"),
        FallbackFamily("event_fibonacci", "fibonacci", "fibonacci", "event", "Event Fibonacci fallback"),
        FallbackFamily("event_soft_fibonacci", "fibonacci", "fibonacci", "event_soft", "Event-soft Fibonacci fallback"),
        FallbackFamily("event_binary", "fibonacci", "binary", "event", "Event binary fallback"),
        FallbackFamily("event_tribonacci", "fibonacci", "tribonacci", "event", "Event tribonacci fallback"),
        FallbackFamily("event_random", "fibonacci", "random", "event", "Event random fallback"),
        FallbackFamily("event_stale", "fibonacci", "stale", "event", "Event stale fallback"),
    ]

    rows = [evaluate_family(family, words, vocab_index) for family in families]
    ranked = sorted(rows, key=lambda row: float(row["score_event"]), reverse=True)
    core_ranked = sorted(rows, key=lambda row: float(row["score_core"]), reverse=True)
    write_csv(rows, OUT / "family_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    no_return = next(row for row in rows if row["family"] == "no_return")
    event_fib = next(row for row in rows if row["family"] == "event_fibonacci")
    best = ranked[0]
    best_core = core_ranked[0]

    report = f"""# Boundary Access Event Fallback

Config:
- normal mask keep `{MASK_KEEP_NORMAL}`
- damage mask keep `{MASK_KEEP_DAMAGE}`
- damage probability `{DAMAGE_PROB}`
- damage trigger threshold `{DAMAGE_TRIGGER_THRESHOLD}`
- fallback gain `{FALLBACK_GAIN}`
- wake decay `{WAKE_DECAY}`

Best family:
- `{best['family']}` event score `{float(best['score_event']):.3f}`

Best core family:
- `{best_core['family']}` core score `{float(best_core['score_core']):.3f}`

Reference comparison:
- no-return event score `{float(no_return['score_event']):.3f}`
- no-return core score `{float(no_return['score_core']):.3f}`
- event-fibonacci event score `{float(event_fib['score_event']):.3f}`
- event-fibonacci core score `{float(event_fib['score_core']):.3f}`
- event-fibonacci trigger rate `{float(event_fib['trigger_rate']):.3f}`

Interpretation:
- This tests return as a fallback after explicit damage, not as normal flow.
- The question is whether Fibonacci fallback rescues a damaged channel better than no-return and stronger controls.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best family: {best['family']} {float(best['score_event']):.3f}")
    print(f"best core family: {best_core['family']} {float(best_core['score_core']):.3f}")


if __name__ == "__main__":
    main()
