#!/usr/bin/env python3
"""Shared utilities for golden zipper v2 experiments."""

from __future__ import annotations

import csv
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PHI = (1.0 + math.sqrt(5.0)) / 2.0
GOLDEN = 1.0 / PHI
SILVER = math.sqrt(2.0) - 1.0
BRONZE = (math.sqrt(13.0) - 3.0) / 2.0

SEED = 1729
PERIOD_MAX = 256
BLOCK_LENGTHS = list(range(2, 13))


@dataclass(frozen=True)
class SlopeSpec:
    name: str
    family: str
    alpha: float


def wrap01(x: float) -> float:
    return x % 1.0


def in_window(x: float, start: float, width: float) -> bool:
    end = start + width
    if end <= 1.0:
        return start <= x < end
    return x >= start or x < (end % 1.0)


def build_slopes(random_count: int = 5) -> list[SlopeSpec]:
    slopes = [
        SlopeSpec("golden", "golden", GOLDEN),
        SlopeSpec("silver", "silver", SILVER),
        SlopeSpec("bronze", "bronze", BRONZE),
        SlopeSpec("near_golden_m0_020", "near_golden", GOLDEN - 0.020),
        SlopeSpec("near_golden_m0_010", "near_golden", GOLDEN - 0.010),
        SlopeSpec("near_golden_m0_005", "near_golden", GOLDEN - 0.005),
        SlopeSpec("near_golden_p0_005", "near_golden", GOLDEN + 0.005),
        SlopeSpec("near_golden_p0_010", "near_golden", GOLDEN + 0.010),
        SlopeSpec("near_golden_p0_020", "near_golden", GOLDEN + 0.020),
        SlopeSpec("rational_1_2", "rational_approx", 1.0 / 2.0),
        SlopeSpec("rational_2_3", "rational_approx", 2.0 / 3.0),
        SlopeSpec("rational_3_5", "rational_approx", 3.0 / 5.0),
        SlopeSpec("rational_5_8", "rational_approx", 5.0 / 8.0),
        SlopeSpec("rational_8_13", "rational_approx", 8.0 / 13.0),
        SlopeSpec("rational_13_21", "rational_approx", 13.0 / 21.0),
        SlopeSpec("control_1_3", "rational_control", 1.0 / 3.0),
        SlopeSpec("control_1_4", "rational_control", 1.0 / 4.0),
        SlopeSpec("control_2_5", "rational_control", 2.0 / 5.0),
    ]
    rng = np.random.default_rng(SEED)
    for idx in range(random_count):
        alpha = float(rng.uniform(0.05, 0.95))
        slopes.append(SlopeSpec(f"random_{idx+1}", "random", alpha))
    return slopes


def generate_sequence(
    alpha: float,
    steps: int,
    window_size: float,
    phase: float,
    mode: str = "single",
    drift_scale: float = 0.07,
) -> np.ndarray:
    seq = np.zeros(steps, dtype=np.int8)
    x = phase
    for n in range(steps):
        x = wrap01(x + alpha)
        if mode == "single":
            hit = in_window(x, phase, window_size)
        elif mode == "moving":
            drift = wrap01(phase + n * alpha * drift_scale)
            hit = in_window(x, drift, window_size)
        elif mode == "double":
            hit = in_window(x, phase, window_size / 2.0) or in_window(
                x, wrap01(phase + 0.5), window_size / 2.0
            )
        else:
            raise ValueError(mode)
        seq[n] = 1 if hit else 0
    return seq


def subwords(seq: np.ndarray, length: int) -> list[tuple[int, ...]]:
    n = len(seq)
    return [tuple(int(x) for x in seq[i : i + length]) for i in range(n - length + 1)]


def balance_metrics(seq: np.ndarray) -> tuple[float, float]:
    good = 0
    max_spread = 0
    for length in BLOCK_LENGTHS:
        counts = [sum(word) for word in subwords(seq, length)]
        spread = max(counts) - min(counts) if counts else 0
        max_spread = max(max_spread, spread)
        if spread <= 1:
            good += 1
    return good / len(BLOCK_LENGTHS), float(max_spread)


def complexity_metrics(seq: np.ndarray) -> tuple[float, float]:
    ratios = []
    deviations = []
    n = len(seq)
    for length in BLOCK_LENGTHS:
        words = subwords(seq, length)
        distinct = len(set(words))
        ideal = length + 1
        max_possible = min(2**length, n - length + 1)
        ratios.append(distinct / max_possible if max_possible else 0.0)
        deviations.append(abs(distinct - ideal) / ideal)
    return float(np.mean(ratios)), float(np.mean(deviations))


def periodicity_metrics(seq: np.ndarray) -> tuple[float, int]:
    prefix = seq[: min(len(seq), 1024)]
    for period in range(1, min(PERIOD_MAX, len(prefix) // 2) + 1):
        if np.array_equal(prefix[:-period], prefix[period:]):
            return 1.0 / period, period
    return 0.0, PERIOD_MAX + 1


def lz78_phrase_count(seq: np.ndarray) -> int:
    dictionary = set()
    phrases = 0
    i = 0
    text = "".join(str(int(x)) for x in seq)
    while i < len(text):
        j = i + 1
        while j <= len(text) and text[i:j] in dictionary:
            j += 1
        dictionary.add(text[i:j])
        phrases += 1
        i = j
    return phrases


def predictive_score(seq: np.ndarray) -> float:
    counts: dict[tuple[int, int], Counter] = defaultdict(Counter)
    correct = 0
    total = 0
    for i in range(2, len(seq)):
        ctx = (int(seq[i - 2]), int(seq[i - 1]))
        if counts[ctx]:
            pred = 1 if counts[ctx][1] >= counts[ctx][0] else 0
            correct += int(pred == int(seq[i]))
            total += 1
        counts[ctx][int(seq[i])] += 1
    return correct / total if total else 0.5


def compression_metric(seq: np.ndarray) -> float:
    phrases = lz78_phrase_count(seq)
    return predictive_score(seq) / max(phrases / len(seq), 1e-9)


def memory_policy(seq: np.ndarray) -> dict[str, float]:
    context_len = 4
    motif_len = 6
    next_counts: dict[tuple[int, ...], Counter] = defaultdict(Counter)
    motif_counts: Counter = Counter()
    for i in range(context_len, len(seq)):
        ctx = tuple(int(x) for x in seq[i - context_len : i])
        next_counts[ctx][int(seq[i])] += 1
    for i in range(len(seq) - motif_len + 1):
        motif = tuple(int(x) for x in seq[i : i + motif_len])
        motif_counts[motif] += 1
    max_motif = max(motif_counts.values()) if motif_counts else 1

    actions = []
    contradicted_writes = 0
    total_writes = 0
    delayed_kept = 0
    delayed_missed = 0

    for i, sym in enumerate(seq):
        if i < context_len:
            confidence = 0.5
            motif_score = 0.0
        else:
            ctx = tuple(int(x) for x in seq[i - context_len : i])
            counts = next_counts[ctx]
            total = sum(counts.values())
            confidence = counts[int(sym)] / total if total else 0.5
            if i <= len(seq) - motif_len:
                motif = tuple(int(x) for x in seq[i : i + motif_len])
                motif_score = motif_counts[motif] / max_motif
            else:
                motif_score = 0.0
        ambiguous = abs(confidence - 0.5) <= 0.14
        if confidence >= 0.82 or (confidence >= 0.70 and motif_score >= 0.25):
            action = "write"
        elif ambiguous or confidence >= 0.52 or motif_score >= 0.35:
            action = "witness"
        else:
            action = "release"
        actions.append(action)
        if action == "write":
            total_writes += 1
            if motif_score < 0.08:
                contradicted_writes += 1
        delayed_candidate = 0.18 <= motif_score <= 0.45 and confidence < 0.72
        if delayed_candidate and action == "witness":
            delayed_kept += 1
        elif delayed_candidate and action == "release":
            delayed_missed += 1

    delayed_total = delayed_kept + delayed_missed
    counts = Counter(actions)
    return {
        "write_count": float(counts["write"]),
        "witness_count": float(counts["witness"]),
        "release_count": float(counts["release"]),
        "pollution": contradicted_writes / total_writes if total_writes else 0.0,
        "delayed_retention": delayed_kept / delayed_total if delayed_total else 0.0,
    }


def summarize_sequence(seq: np.ndarray, width: int = 96) -> str:
    return "".join(str(int(x)) for x in seq[:width])


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text)


def family_means(rows: list[dict], numeric_keys: list[str]) -> dict[str, dict[str, float]]:
    out = {}
    for family in sorted({row["family"] for row in rows}):
        subset = [row for row in rows if row["family"] == family]
        out[family] = {key: float(np.mean([float(row[key]) for row in subset])) for key in numeric_keys}
    return out


def alpha_phase_diagram(
    rows: list[dict],
    metric: str,
    title: str,
    path: Path,
    cmap: str = "viridis",
) -> None:
    alphas = np.array([float(r["alpha"]) for r in rows])
    phases = np.array([float(r.get("phase", 0.0)) for r in rows])
    values = np.array([float(r[metric]) for r in rows])
    plt.figure(figsize=(8, 6))
    plt.scatter(alphas, phases, c=values, cmap=cmap, s=30)
    plt.axvline(GOLDEN, color="gold", linestyle="--", linewidth=1.5, label="golden")
    plt.colorbar(label=metric)
    plt.xlabel("alpha")
    plt.ylabel("phase")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def bar_family(rows: list[dict], metric: str, title: str, ylabel: str, path: Path) -> None:
    fams = sorted({r["family"] for r in rows})
    vals = [np.mean([float(r[metric]) for r in rows if r["family"] == fam]) for fam in fams]
    plt.figure(figsize=(10, 5))
    plt.bar(fams, vals, color="#d9a404")
    plt.xticks(rotation=30, ha="right")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def save_samples(samples: list[str], path: Path) -> None:
    path.write_text("\n\n".join(samples))


def strongest_weakest(rows: list[dict], score_key: str) -> tuple[dict, dict]:
    scored = sorted(rows, key=lambda row: float(row[score_key]), reverse=True)
    return scored[0], scored[-1]


def robust_std(rows: list[dict], family: str, key: str) -> float:
    vals = [float(r[key]) for r in rows if r["family"] == family]
    return statistics.pstdev(vals) if len(vals) > 1 else 0.0
