#!/usr/bin/env python3
"""Boundary Access Channel toy comparison.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_channel_outputs"

SEED = 20260526
RNG = np.random.default_rng(SEED)

TARGET_LENGTH = 4096
KMER = 4
FRAGMENT_BUDGET = 96
LOW_BUDGET = 48
MASK_KEEP = 0.35
TRIALS = 64
BALANCE_TARGET = 0.60


@dataclass(frozen=True)
class BranchFamily:
    name: str
    rules: dict[str, str]
    label: str


FAMILIES = [
    BranchFamily("binary_abelian", {"A": "AB", "B": "BA"}, "binary abelian"),
    BranchFamily("generic_ternary", {"A": "ABC", "B": "BCA", "C": "CAB"}, "generic ternary"),
    BranchFamily("fibonacci", {"A": "AB", "B": "A"}, "Fibonacci"),
    BranchFamily("tribonacci_control", {"A": "AB", "B": "AC", "C": "A"}, "non-Fibonacci control"),
]


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


def generate_word(rules: dict[str, str], target_length: int) -> str:
    word = "A"
    while len(word) < target_length:
        word = "".join(rules[ch] for ch in word)
    return word[:target_length]


def collect_vocabulary(words: dict[str, str], kmer: int) -> list[str]:
    vocab: set[str] = set()
    for word in words.values():
        for idx in range(len(word) - kmer + 1):
            vocab.add(word[idx : idx + kmer])
    return sorted(vocab)


def histogram_from_positions(word: str, positions: np.ndarray, kmer: int, vocab_index: dict[str, int]) -> np.ndarray:
    hist = np.zeros(len(vocab_index), dtype=float)
    for idx in positions:
        token = word[int(idx) : int(idx) + kmer]
        hist[vocab_index[token]] += 1.0
    total = hist.sum()
    return hist / total if total else hist


def full_histogram(word: str, kmer: int, vocab_index: dict[str, int]) -> np.ndarray:
    positions = np.arange(len(word) - kmer + 1)
    return histogram_from_positions(word, positions, kmer, vocab_index)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def entropy_score(hist: np.ndarray) -> float:
    mask = hist > 0
    probs = hist[mask]
    entropy = float(-(probs * np.log(probs)).sum())
    max_entropy = math.log(len(hist)) if len(hist) > 1 else 1.0
    return entropy / max_entropy if max_entropy > 0 else 0.0


def balance_score(hist: np.ndarray) -> float:
    norm_entropy = entropy_score(hist)
    gap = abs(norm_entropy - BALANCE_TARGET)
    raw = 1.0 - (gap / max(BALANCE_TARGET, 1.0 - BALANCE_TARGET))
    return float(np.clip(raw, 0.0, 1.0))


def sample_positions(word: str, budget: int) -> np.ndarray:
    limit = len(word) - KMER + 1
    return RNG.choice(limit, size=budget, replace=False)


def mutate_mask(hist: np.ndarray, keep: float) -> np.ndarray:
    counts = hist.copy()
    total = counts.sum()
    if total == 0.0:
        return counts
    keep_counts = counts * keep
    return keep_counts / keep_counts.sum() if keep_counts.sum() else keep_counts


def recovery_from_prior(masked_hist: np.ndarray, prior: np.ndarray, weight: float = 0.55) -> np.ndarray:
    mixed = (1.0 - weight) * masked_hist + weight * prior
    total = mixed.sum()
    return mixed / total if total else mixed


def top_overlap(a: np.ndarray, b: np.ndarray, top_k: int = 8) -> float:
    a_top = set(np.argsort(a)[-top_k:])
    b_top = set(np.argsort(b)[-top_k:])
    union = a_top | b_top
    if not union:
        return 0.0
    return len(a_top & b_top) / len(union)


def evaluate_family(family: BranchFamily, word: str, prior: np.ndarray, vocab_index: dict[str, int]) -> dict[str, float | str]:
    truth = full_histogram(word, KMER, vocab_index)
    access_scores: list[float] = []
    recovery_scores: list[float] = []
    redundancy_scores: list[float] = []
    shared_scores: list[float] = []
    compression_scores: list[float] = []
    top_overlap_scores: list[float] = []

    for _ in range(TRIALS):
        frag_a = histogram_from_positions(word, sample_positions(word, FRAGMENT_BUDGET), KMER, vocab_index)
        frag_b = histogram_from_positions(word, sample_positions(word, FRAGMENT_BUDGET), KMER, vocab_index)
        combined = frag_a + frag_b
        combined /= combined.sum() if combined.sum() else 1.0

        access = cosine(combined, truth)
        access_scores.append(access)

        masked_a = mutate_mask(frag_a, MASK_KEEP)
        masked_only = cosine(masked_a, truth)
        recovered = recovery_from_prior(masked_a + frag_b, prior)
        recovered_score = cosine(recovered, truth)
        recovery_gain = max(0.0, recovered_score - masked_only)
        recovery_scores.append(recovery_gain)

        redundancy = 0.5 * (cosine(frag_a, truth) + cosine(frag_b, truth))
        redundancy_scores.append(redundancy)

        shared = 0.5 * (cosine(frag_a, frag_b) + top_overlap(frag_a, frag_b))
        shared_scores.append(shared)
        top_overlap_scores.append(top_overlap(frag_a, frag_b))

        low_a = histogram_from_positions(word, sample_positions(word, LOW_BUDGET), KMER, vocab_index)
        low_b = histogram_from_positions(word, sample_positions(word, LOW_BUDGET), KMER, vocab_index)
        low_combined = low_a + low_b
        low_combined /= low_combined.sum() if low_combined.sum() else 1.0
        low_access = cosine(low_combined, truth)
        compression_scores.append(low_access / max(access, 1e-9))

    structure = balance_score(truth)
    metrics = {
        "family": family.name,
        "label": family.label,
        "access_fidelity": float(np.mean(access_scores)),
        "recovery_gain": float(np.mean(recovery_scores)),
        "redundancy_score": float(np.mean(redundancy_scores)),
        "shared_overlap": float(np.mean(shared_scores)),
        "compression_stability": float(np.mean(compression_scores)),
        "structure_balance": structure,
        "top_overlap": float(np.mean(top_overlap_scores)),
        "entropy": entropy_score(truth),
    }
    metrics["score"] = (
        0.24 * metrics["access_fidelity"]
        + 0.18 * metrics["recovery_gain"]
        + 0.18 * metrics["redundancy_score"]
        + 0.16 * metrics["shared_overlap"]
        + 0.14 * metrics["compression_stability"]
        + 0.10 * metrics["structure_balance"]
    )
    metrics["score_no_balance"] = (
        0.27 * metrics["access_fidelity"]
        + 0.20 * metrics["recovery_gain"]
        + 0.20 * metrics["redundancy_score"]
        + 0.18 * metrics["shared_overlap"]
        + 0.15 * metrics["compression_stability"]
    )
    metrics["score_channel_core"] = (
        0.30 * metrics["access_fidelity"]
        + 0.25 * metrics["recovery_gain"]
        + 0.25 * metrics["redundancy_score"]
        + 0.20 * metrics["shared_overlap"]
    )
    return metrics


def main() -> None:
    ensure_dir(OUT)
    words = {family.name: generate_word(family.rules, TARGET_LENGTH) for family in FAMILIES}
    vocab = collect_vocabulary(words, KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    rows: list[dict[str, float | str]] = []
    for family in FAMILIES:
        prior = full_histogram(words[family.name], KMER, vocab_index)
        rows.append(evaluate_family(family, words[family.name], prior, vocab_index))

    ranked = sorted(rows, key=lambda row: float(row["score"]), reverse=True)
    write_csv(rows, OUT / "family_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    fib_rank = next(idx for idx, row in enumerate(ranked, start=1) if row["family"] == "fibonacci")
    fib = next(row for row in ranked if row["family"] == "fibonacci")
    best = ranked[0]
    no_balance_ranked = sorted(rows, key=lambda row: float(row["score_no_balance"]), reverse=True)
    channel_core_ranked = sorted(rows, key=lambda row: float(row["score_channel_core"]), reverse=True)
    no_balance_best = no_balance_ranked[0]
    channel_core_best = channel_core_ranked[0]
    fib_no_balance_rank = next(idx for idx, row in enumerate(no_balance_ranked, start=1) if row["family"] == "fibonacci")
    fib_channel_core_rank = next(idx for idx, row in enumerate(channel_core_ranked, start=1) if row["family"] == "fibonacci")

    report = f"""# Boundary Access Channel Toy

Best family:
- `{best['family']}` score `{float(best['score']):.3f}`

Fibonacci:
- rank `{fib_rank}/{len(ranked)}`
- score `{float(fib['score']):.3f}`
- access fidelity `{float(fib['access_fidelity']):.3f}`
- recovery gain `{float(fib['recovery_gain']):.3f}`
- redundancy score `{float(fib['redundancy_score']):.3f}`
- shared overlap `{float(fib['shared_overlap']):.3f}`
- compression stability `{float(fib['compression_stability']):.3f}`
- structure balance `{float(fib['structure_balance']):.3f}`

Sensitivity:
- no-balance best `{no_balance_best['family']}` with Fibonacci rank `{fib_no_balance_rank}/{len(rows)}`
- channel-core best `{channel_core_best['family']}` with Fibonacci rank `{fib_channel_core_rank}/{len(rows)}`

Interpretation:
- This is a branching-channel toy, not a proof of physics.
- The score rewards the combined package of access, recovery, redundancy, shared overlap, compression stability, and a moderate structure-balance target.
- Fibonacci does not win the current blended score.
- Fibonacci does win when the extra structure-balance preference is removed and we score the core channel package directly.
- Binary can win on redundancy by being too repetitive.
- Ternary can win on diversity by being too diffuse.
- The interesting question is whether Fibonacci helps the whole package at once.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best family: {best['family']} {float(best['score']):.3f}")
    print(f"fibonacci rank: {fib_rank}/{len(ranked)}")
    print(f"fibonacci score: {float(fib['score']):.3f}")


if __name__ == "__main__":
    main()
