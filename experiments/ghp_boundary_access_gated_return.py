#!/usr/bin/env python3
"""Boundary Access Channel gated-return toy.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_return_loop as loop


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_gated_return_outputs"

WAKE_GAIN = 0.22
WAKE_DECAY = 0.90
MASK_KEEP = 0.50
PRESSURE_THRESHOLD = 0.12
SPARSITY_THRESHOLD = 0.18


@dataclass(frozen=True)
class GatedFamily:
    name: str
    source_word: str
    return_mode: str
    gate_mode: str
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


def active_support(hist: np.ndarray, floor: float = 1e-9) -> float:
    return float(np.count_nonzero(hist > floor)) / float(hist.size)


def drift_score(current: np.ndarray, previous: np.ndarray | None) -> float:
    if previous is None:
        return 0.0
    return max(0.0, 1.0 - loop.base.cosine(current, previous))


def pressure_score(current_a: np.ndarray, current_b: np.ndarray, previous: np.ndarray | None) -> tuple[float, float, float]:
    combined = loop.normalize(current_a + current_b)
    sparsity = 1.0 - active_support(combined)
    overlap = 0.5 * (loop.base.cosine(current_a, current_b) + loop.top_overlap(current_a, current_b))
    drift = drift_score(combined, previous)
    pressure = 0.45 * sparsity + 0.35 * (1.0 - overlap) + 0.20 * drift
    return pressure, sparsity, drift


def gate_scale(
    gate_mode: str,
    pressure: float,
    sparsity: float,
    drift: float,
    threshold: float,
    sparsity_threshold: float,
) -> float:
    if gate_mode == "none":
        return 0.0
    if gate_mode == "always":
        return 1.0
    if gate_mode == "pressure":
        return 1.0 if pressure >= threshold else 0.0
    if gate_mode == "sparse":
        return 1.0 if sparsity >= sparsity_threshold else 0.0
    if gate_mode == "pressure_soft":
        return float(np.clip((pressure - threshold) / max(1e-9, 1.0 - threshold), 0.0, 1.0))
    if gate_mode == "pressure_or_sparse":
        return 1.0 if pressure >= threshold or sparsity >= sparsity_threshold else 0.0
    if gate_mode == "pressure_and_sparse":
        return 1.0 if pressure >= threshold and sparsity >= sparsity_threshold else 0.0
    if gate_mode == "pressure_drift":
        return 1.0 if pressure >= threshold and drift > 0.03 else 0.0
    raise ValueError(gate_mode)


def evaluate_family(
    family: GatedFamily,
    words: dict[str, str],
    vocab_index: dict[str, int],
    pressure_threshold: float,
    sparsity_threshold: float,
) -> dict[str, float | str]:
    word = words[family.source_word]
    truth = loop.base.full_histogram(word, loop.base.KMER, vocab_index)
    offsets = loop.return_offsets(family.return_mode, loop.TIMESTEPS, len(vocab_index))

    access_scores: list[float] = []
    recovery_scores: list[float] = []
    shared_scores: list[float] = []
    wake_gain_scores: list[float] = []
    wake_balance_scores: list[float] = []
    gate_rates: list[float] = []
    pressure_scores: list[float] = []

    limit = len(word) - loop.base.KMER + 1

    for _ in range(loop.TRIALS):
        start_a = int(loop.RNG.integers(0, limit))
        start_b = int(loop.RNG.integers(0, limit))
        wake = np.zeros(len(vocab_index), dtype=float)
        previous_combined: np.ndarray | None = None

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

            pressure, sparsity, drift = pressure_score(current_a, current_b, previous_combined)
            scale = gate_scale(
                family.gate_mode,
                pressure,
                sparsity,
                drift,
                pressure_threshold,
                sparsity_threshold,
            )
            rotated_wake = np.roll(wake, offsets[step])
            gated_wake = scale * rotated_wake

            readable_a = loop.normalize(current_a + WAKE_GAIN * gated_wake)
            readable_b = loop.normalize(current_b + WAKE_GAIN * gated_wake)
            combined = loop.normalize(readable_a + readable_b)

            access_scores.append(loop.base.cosine(combined, truth))

            masked = loop.base.mutate_mask(readable_a, MASK_KEEP)
            masked_only = loop.base.cosine(masked, truth)
            recovered = loop.recover_from_sources(masked, readable_b, gated_wake)
            recovered_score = loop.base.cosine(recovered, truth)
            recovery_scores.append(max(0.0, recovered_score - masked_only))

            shared_scores.append(0.5 * (loop.base.cosine(readable_a, readable_b) + loop.top_overlap(readable_a, readable_b)))

            no_wake_combined = loop.normalize(current_a + current_b)
            wake_gain_scores.append(max(0.0, loop.base.cosine(combined, truth) - loop.base.cosine(no_wake_combined, truth)))
            wake_balance_scores.append(loop.base.balance_score(gated_wake) if gated_wake.sum() > 0 else 0.0)

            gate_rates.append(scale)
            pressure_scores.append(pressure)

            wake = loop.normalize(WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * readable_b)
            previous_combined = combined

    metrics = {
        "family": family.name,
        "label": family.label,
        "gate_mode": family.gate_mode,
        "access_fidelity": float(np.mean(access_scores)),
        "recovery_gain": float(np.mean(recovery_scores)),
        "shared_overlap": float(np.mean(shared_scores)),
        "wake_gain": float(np.mean(wake_gain_scores)),
        "wake_balance": float(np.mean(wake_balance_scores)),
        "gate_rate": float(np.mean(gate_rates)),
        "pressure_mean": float(np.mean(pressure_scores)),
    }
    metrics["score"] = (
        0.34 * metrics["access_fidelity"]
        + 0.24 * metrics["recovery_gain"]
        + 0.22 * metrics["shared_overlap"]
        + 0.12 * metrics["wake_gain"]
        + 0.08 * metrics["wake_balance"]
    )
    metrics["score_core"] = (
        0.42 * metrics["access_fidelity"]
        + 0.30 * metrics["recovery_gain"]
        + 0.28 * metrics["shared_overlap"]
    )
    return metrics


def main() -> None:
    ensure_dir(OUT)
    words = loop.build_words()
    vocab = loop.base.collect_vocabulary(words, loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    families = [
        GatedFamily("fibonacci_no_return", "fibonacci", "none", "none", "Fibonacci no return"),
        GatedFamily("fibonacci_always_return", "fibonacci", "fibonacci", "always", "Fibonacci always return"),
        GatedFamily("fibonacci_pressure_gate", "fibonacci", "fibonacci", "pressure", "Fibonacci pressure gate"),
        GatedFamily("fibonacci_sparse_gate", "fibonacci", "fibonacci", "sparse", "Fibonacci sparse gate"),
        GatedFamily("fibonacci_pressure_soft_gate", "fibonacci", "fibonacci", "pressure_soft", "Fibonacci pressure soft gate"),
        GatedFamily("fibonacci_pressure_or_sparse_gate", "fibonacci", "fibonacci", "pressure_or_sparse", "Fibonacci pressure or sparse gate"),
        GatedFamily("fibonacci_pressure_and_sparse_gate", "fibonacci", "fibonacci", "pressure_and_sparse", "Fibonacci pressure and sparse gate"),
        GatedFamily("fibonacci_pressure_drift_gate", "fibonacci", "fibonacci", "pressure_drift", "Fibonacci pressure plus drift gate"),
    ]

    rows = [
        evaluate_family(family, words, vocab_index, PRESSURE_THRESHOLD, SPARSITY_THRESHOLD)
        for family in families
    ]
    ranked = sorted(rows, key=lambda row: float(row["score"]), reverse=True)
    core_ranked = sorted(rows, key=lambda row: float(row["score_core"]), reverse=True)

    write_csv(rows, OUT / "family_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    best = ranked[0]
    best_core = core_ranked[0]
    fib_no = next(row for row in rows if row["family"] == "fibonacci_no_return")
    fib_always = next(row for row in rows if row["family"] == "fibonacci_always_return")
    fib_gate = next(row for row in rows if row["family"] == "fibonacci_pressure_or_sparse_gate")

    report = f"""# Boundary Access Gated Return

Config:
- wake gain `{WAKE_GAIN}`
- wake decay `{WAKE_DECAY}`
- mask keep `{MASK_KEEP}`
- pressure threshold `{PRESSURE_THRESHOLD}`
- sparsity threshold `{SPARSITY_THRESHOLD}`

Best family:
- `{best['family']}` score `{float(best['score']):.3f}`

Best core family:
- `{best_core['family']}` core score `{float(best_core['score_core']):.3f}`

Reference comparison:
- no-return score `{float(fib_no['score']):.3f}`
- always-return score `{float(fib_always['score']):.3f}`
- pressure-or-sparse gate score `{float(fib_gate['score']):.3f}`
- no-return core score `{float(fib_no['score_core']):.3f}`
- always-return core score `{float(fib_always['score_core']):.3f}`
- pressure-or-sparse gate core score `{float(fib_gate['score_core']):.3f}`
- pressure-or-sparse gate rate `{float(fib_gate['gate_rate']):.3f}`

Interpretation:
- This tests return as pressure relief instead of constant recycling.
- If a gated family beats both no-return and always-return on the core score, then return may matter only under stress.
- If no-return still wins, the anti-locking core remains the clearest live result.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best family: {best['family']} {float(best['score']):.3f}")
    print(f"best core family: {best_core['family']} {float(best_core['score_core']):.3f}")


if __name__ == "__main__":
    main()
