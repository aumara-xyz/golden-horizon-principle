#!/usr/bin/env python3
"""Boundary Access Channel return-loop toy.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_channel_toy as base


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_return_loop_outputs"

SEED = 20260526
RNG = np.random.default_rng(SEED)

TIMESTEPS = 160
TRIALS = 48
CHUNK = 80
SECOND_CHUNK = 56
WAKE_GAIN = 0.42
WAKE_DECAY = 0.78
MASK_KEEP = 0.38


@dataclass(frozen=True)
class LoopFamily:
    name: str
    source_word: str
    return_mode: str
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


def build_words() -> dict[str, str]:
    words = {family.name: base.generate_word(family.rules, base.TARGET_LENGTH) for family in base.FAMILIES}
    return words


def fib_numbers(limit: int) -> list[int]:
    nums = [1, 1]
    while len(nums) < limit:
        nums.append(nums[-1] + nums[-2])
    return nums[:limit]


def trib_numbers(limit: int) -> list[int]:
    nums = [1, 1, 2]
    while len(nums) < limit:
        nums.append(nums[-1] + nums[-2] + nums[-3])
    return nums[:limit]


def return_offsets(mode: str, steps: int, vocab_size: int) -> list[int]:
    if mode == "none":
        return [0] * steps
    if mode == "binary":
        return [idx % 2 for idx in range(steps)]
    if mode == "ternary":
        return [idx % 3 for idx in range(steps)]
    if mode == "fibonacci":
        return [num % vocab_size for num in fib_numbers(steps)]
    if mode == "tribonacci":
        return [num % vocab_size for num in trib_numbers(steps)]
    raise ValueError(mode)


def chunk_positions(word_len: int, width: int, start: int) -> np.ndarray:
    limit = word_len - base.KMER + 1
    return np.array([(start + idx) % limit for idx in range(width)], dtype=int)


def normalize(hist: np.ndarray) -> np.ndarray:
    total = hist.sum()
    return hist / total if total else hist


def recover_from_sources(masked: np.ndarray, other: np.ndarray, wake: np.ndarray) -> np.ndarray:
    mixed = 0.34 * masked + 0.33 * other + 0.33 * wake
    return normalize(mixed)


def top_overlap(a: np.ndarray, b: np.ndarray, top_k: int = 8) -> float:
    a_top = set(np.argsort(a)[-top_k:])
    b_top = set(np.argsort(b)[-top_k:])
    union = a_top | b_top
    if not union:
        return 0.0
    return len(a_top & b_top) / len(union)


def evaluate_loop_family(family: LoopFamily, words: dict[str, str], vocab_index: dict[str, int]) -> dict[str, float | str]:
    word = words[family.source_word]
    truth = base.full_histogram(word, base.KMER, vocab_index)
    offsets = return_offsets(family.return_mode, TIMESTEPS, len(vocab_index))

    access_scores: list[float] = []
    recovery_scores: list[float] = []
    shared_scores: list[float] = []
    wake_gain_scores: list[float] = []
    wake_balance_scores: list[float] = []

    limit = len(word) - base.KMER + 1

    for _ in range(TRIALS):
        start_a = int(RNG.integers(0, limit))
        start_b = int(RNG.integers(0, limit))
        wake = np.zeros(len(vocab_index), dtype=float)

        for step in range(TIMESTEPS):
            current_a = base.histogram_from_positions(word, chunk_positions(len(word), CHUNK, start_a + step), base.KMER, vocab_index)
            current_b = base.histogram_from_positions(word, chunk_positions(len(word), SECOND_CHUNK, start_b + 2 * step), base.KMER, vocab_index)

            rotated_wake = np.roll(wake, offsets[step])
            readable_a = normalize(current_a + WAKE_GAIN * rotated_wake)
            readable_b = normalize(current_b + WAKE_GAIN * rotated_wake)

            combined = normalize(readable_a + readable_b)
            access_scores.append(base.cosine(combined, truth))

            masked = base.mutate_mask(readable_a, MASK_KEEP)
            masked_only = base.cosine(masked, truth)
            recovered = recover_from_sources(masked, readable_b, rotated_wake)
            recovered_score = base.cosine(recovered, truth)
            recovery_scores.append(max(0.0, recovered_score - masked_only))

            shared_scores.append(0.5 * (base.cosine(readable_a, readable_b) + top_overlap(readable_a, readable_b)))

            no_wake_combined = normalize(current_a + current_b)
            wake_gain_scores.append(max(0.0, base.cosine(combined, truth) - base.cosine(no_wake_combined, truth)))

            wake_balance_scores.append(base.balance_score(rotated_wake) if rotated_wake.sum() > 0 else 0.0)

            wake = normalize(WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * readable_b)

    metrics = {
        "family": family.name,
        "label": family.label,
        "access_fidelity": float(np.mean(access_scores)),
        "recovery_gain": float(np.mean(recovery_scores)),
        "shared_overlap": float(np.mean(shared_scores)),
        "wake_gain": float(np.mean(wake_gain_scores)),
        "wake_balance": float(np.mean(wake_balance_scores)),
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
    words = build_words()
    vocab = base.collect_vocabulary(words, base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    families = [
        LoopFamily("binary_return_loop", "binary_abelian", "binary", "binary return loop"),
        LoopFamily("generic_ternary_return_loop", "generic_ternary", "ternary", "generic ternary return loop"),
        LoopFamily("fibonacci_no_return_loop", "fibonacci", "none", "Fibonacci no-return loop"),
        LoopFamily("fibonacci_return_loop", "fibonacci", "fibonacci", "Fibonacci return loop"),
        LoopFamily("tribonacci_return_loop", "tribonacci_control", "tribonacci", "tribonacci return loop"),
    ]

    rows = [evaluate_loop_family(family, words, vocab_index) for family in families]
    ranked = sorted(rows, key=lambda row: float(row["score"]), reverse=True)
    core_ranked = sorted(rows, key=lambda row: float(row["score_core"]), reverse=True)
    write_csv(rows, OUT / "family_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    fib = next(row for row in rows if row["family"] == "fibonacci_return_loop")
    fib_rank = next(idx for idx, row in enumerate(ranked, start=1) if row["family"] == "fibonacci_return_loop")
    fib_core_rank = next(idx for idx, row in enumerate(core_ranked, start=1) if row["family"] == "fibonacci_return_loop")
    fib_no_return = next(row for row in rows if row["family"] == "fibonacci_no_return_loop")
    best = ranked[0]
    best_core = core_ranked[0]

    report = f"""# Boundary Access Return Loop

Best family:
- `{best['family']}` score `{float(best['score']):.3f}`

Best core family:
- `{best_core['family']}` core score `{float(best_core['score_core']):.3f}`

Fibonacci return loop:
- blended rank `{fib_rank}/{len(rows)}`
- core rank `{fib_core_rank}/{len(rows)}`
- access fidelity `{float(fib['access_fidelity']):.3f}`
- recovery gain `{float(fib['recovery_gain']):.3f}`
- shared overlap `{float(fib['shared_overlap']):.3f}`
- wake gain `{float(fib['wake_gain']):.3f}`
- wake balance `{float(fib['wake_balance']):.3f}`

Fibonacci return vs no-return:
- return score `{float(fib['score']):.3f}`
- no-return score `{float(fib_no_return['score']):.3f}`
- return core score `{float(fib['score_core']):.3f}`
- no-return core score `{float(fib_no_return['score_core']):.3f}`

Interpretation:
- This is the first toy where the wake actually goes back into the channel with decay.
- The question is not whether the same thing returns.
- The question is whether recycled-but-altered return helps preserve readable, recoverable, shared structure.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best family: {best['family']} {float(best['score']):.3f}")
    print(f"fibonacci return rank: {fib_rank}/{len(rows)}")
    print(f"fibonacci return core rank: {fib_core_rank}/{len(rows)}")


if __name__ == "__main__":
    main()
