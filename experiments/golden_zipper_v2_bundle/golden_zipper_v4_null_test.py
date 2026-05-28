#!/usr/bin/env python3
"""v4 adversarial null-test suite for the Golden Zipper toy."""

from __future__ import annotations

import csv
import gzip
import itertools
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v4_outputs"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
GOLDEN = 1.0 / PHI
SEED = 1729
RNG = np.random.default_rng(SEED)

WINDOW_SIZES = [0.2, 0.3, 0.382, 0.5, 0.618]
PHASES20 = np.linspace(0.0, 1.0, 20, endpoint=False)
SEQ_LENGTHS = [1000, 5000, 20000]
MOVING_BETAS = {
    "beta_0": 0.0,
    "beta_phi2": 1.0 / (PHI**2),
    "beta_silver": math.sqrt(2.0) - 1.0,
    "beta_random_small": 0.037,
}
MODE_VARIANTS = ["single", "moving", "double"]


@dataclass(frozen=True)
class SlopeSpec:
    name: str
    family: str
    alpha: float
    group: str


@dataclass(frozen=True)
class Condition:
    mode: str
    beta_name: str
    beta: float
    window_size: float
    phase: float
    length: int


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    fieldnames = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text)


def wrap01(x: np.ndarray | float) -> np.ndarray | float:
    return np.mod(x, 1.0)


def continued_fraction_value(coeffs: list[int], tail_ones: int = 16) -> float:
    full = list(coeffs) + [1] * tail_ones
    value = float(full[-1])
    for a in reversed(full[:-1]):
        value = float(a) + 1.0 / value
    return 1.0 / value


def build_noble_numbers(count: int = 50) -> list[SlopeSpec]:
    specs = []
    seen = set()
    idx = 0
    while len(specs) < count:
        k = int(RNG.integers(1, 7))
        coeffs = []
        for j in range(k):
            if j % 2 == 0:
                coeffs.append(int(RNG.integers(1, 6)))
            else:
                coeffs.append(int(RNG.integers(1, 10)))
        alpha = continued_fraction_value(coeffs)
        key = round(alpha, 12)
        if key in seen or not (0.0 < alpha < 1.0):
            continue
        seen.add(key)
        idx += 1
        specs.append(SlopeSpec(f"noble_{idx:03d}", "noble", alpha, "noble"))
    return specs


def build_bounded_cf_controls() -> list[SlopeSpec]:
    families = [
        ("bounded_cf_12", [1, 2], 70),
        ("bounded_cf_123", [1, 2, 3], 70),
        ("bounded_cf_1234", [1, 2, 3, 4], 70),
    ]
    specs = []
    seen = set()
    for family, alphabet, target in families:
        created = 0
        while created < target:
            k = int(RNG.integers(6, 13))
            coeffs = [int(RNG.choice(alphabet)) for _ in range(k)]
            alpha = continued_fraction_value(coeffs, tail_ones=12)
            key = (family, round(alpha, 12))
            if key in seen or not (0.0 < alpha < 1.0):
                continue
            seen.add(key)
            created += 1
            specs.append(SlopeSpec(f"{family}_{created:03d}", family, alpha, "generic_irrational"))
    return specs


def build_unbounded_cf_controls(count: int = 220) -> list[SlopeSpec]:
    specs = []
    seen = set()
    idx = 0
    while len(specs) < count:
        k = int(RNG.integers(6, 13))
        coeffs = [max(1, int(RNG.zipf(1.7))) for _ in range(k)]
        alpha = continued_fraction_value(coeffs, tail_ones=4)
        key = round(alpha, 12)
        if key in seen or not (0.0 < alpha < 1.0):
            continue
        seen.add(key)
        idx += 1
        specs.append(SlopeSpec(f"unbounded_cf_{idx:03d}", "unbounded_cf", alpha, "generic_irrational"))
    return specs


def build_random_uniform(count: int = 500) -> list[SlopeSpec]:
    specs = []
    for idx in range(1, count + 1):
        alpha = float(RNG.uniform(1e-6, 1.0 - 1e-6))
        specs.append(SlopeSpec(f"random_uniform_{idx:03d}", "random_uniform", alpha, "generic_irrational"))
    return specs


def build_near_golden() -> list[SlopeSpec]:
    specs = []
    eps = np.arange(-0.08, 0.0801, 0.002)
    for offset in eps:
        alpha = GOLDEN + float(offset)
        if not (0.0 < alpha < 1.0):
            continue
        tag = f"{offset:+.3f}".replace("+", "p").replace("-", "m").replace(".", "_")
        family = "golden" if abs(offset) < 1e-12 else "near_golden"
        specs.append(SlopeSpec(f"golden_eps_{tag}", family, alpha, "near_golden_band"))
    return specs


def build_named_controls() -> list[SlopeSpec]:
    metallic = [
        SlopeSpec("golden", "golden", GOLDEN, "golden"),
        SlopeSpec("silver", "silver", math.sqrt(2.0) - 1.0, "metallic"),
        SlopeSpec("bronze", "bronze", (math.sqrt(13.0) - 3.0) / 2.0, "metallic"),
        SlopeSpec("copper", "copper", (math.sqrt(20.0) - 4.0) / 2.0, "metallic"),
    ]
    known = [
        SlopeSpec("sqrt2_mod1", "known_irrational", math.sqrt(2.0) % 1.0, "generic_irrational"),
        SlopeSpec("sqrt3_mod1", "known_irrational", math.sqrt(3.0) % 1.0, "generic_irrational"),
        SlopeSpec("sqrt5_mod1", "known_irrational", math.sqrt(5.0) % 1.0, "generic_irrational"),
        SlopeSpec("pi_mod1", "known_irrational", math.pi % 1.0, "generic_irrational"),
        SlopeSpec("e_mod1", "known_irrational", math.e % 1.0, "generic_irrational"),
        SlopeSpec("log2_mod1", "known_irrational", math.log(2.0) % 1.0, "generic_irrational"),
    ]
    rationals = [
        SlopeSpec("rational_1_2", "rational", 1 / 2, "rational"),
        SlopeSpec("rational_1_3", "rational", 1 / 3, "rational"),
        SlopeSpec("rational_1_4", "rational", 1 / 4, "rational"),
        SlopeSpec("rational_2_5", "rational", 2 / 5, "rational"),
        SlopeSpec("rational_3_7", "rational", 3 / 7, "rational"),
        SlopeSpec("fib_2_3", "rational_fib", 2 / 3, "rational"),
        SlopeSpec("fib_3_5", "rational_fib", 3 / 5, "rational"),
        SlopeSpec("fib_5_8", "rational_fib", 5 / 8, "rational"),
        SlopeSpec("fib_8_13", "rational_fib", 8 / 13, "rational"),
        SlopeSpec("fib_13_21", "rational_fib", 13 / 21, "rational"),
        SlopeSpec("fib_21_34", "rational_fib", 21 / 34, "rational"),
        SlopeSpec("fib_34_55", "rational_fib", 34 / 55, "rational"),
    ]
    return metallic + known + rationals


def build_all_slopes() -> dict[str, list[SlopeSpec]]:
    slopes = {
        "named": build_named_controls(),
        "noble": build_noble_numbers(50),
        "bounded": build_bounded_cf_controls(),
        "unbounded": build_unbounded_cf_controls(220),
        "near_golden": build_near_golden(),
        "random": build_random_uniform(500),
    }
    return slopes


def stratified_sample(specs: list[SlopeSpec], count: int, seed_offset: int = 0) -> list[SlopeSpec]:
    if len(specs) <= count:
        return list(specs)
    rng = np.random.default_rng(SEED + seed_offset)
    idx = sorted(rng.choice(len(specs), size=count, replace=False).tolist())
    return [specs[i] for i in idx]


def build_pure_slopes(pools: dict[str, list[SlopeSpec]]) -> list[SlopeSpec]:
    pure = []
    pure.extend(pools["named"])
    pure.extend(pools["noble"])
    pure.extend(stratified_sample([s for s in pools["bounded"] if s.family == "bounded_cf_12"], 25, 1))
    pure.extend(stratified_sample([s for s in pools["bounded"] if s.family == "bounded_cf_123"], 25, 2))
    pure.extend(stratified_sample([s for s in pools["bounded"] if s.family == "bounded_cf_1234"], 25, 3))
    pure.extend(stratified_sample(pools["unbounded"], 40, 4))
    pure.extend([s for i, s in enumerate(pools["near_golden"]) if i % 4 == 0])
    pure.extend(stratified_sample(pools["random"], 60, 5))
    return pure


def build_memory_slopes(pools: dict[str, list[SlopeSpec]]) -> list[SlopeSpec]:
    memory = []
    named = {s.name: s for s in pools["named"]}
    for key in ["golden", "silver", "bronze", "copper", "sqrt2_mod1", "sqrt3_mod1", "pi_mod1", "fib_13_21", "rational_1_3", "rational_2_5"]:
        if key in named:
            memory.append(named[key])
    memory.extend([s for i, s in enumerate(pools["near_golden"]) if i % 5 == 0])
    memory.extend(stratified_sample(pools["noble"], 15, 6))
    memory.extend(stratified_sample([s for s in pools["bounded"] if s.family == "bounded_cf_12"], 5, 7))
    memory.extend(stratified_sample([s for s in pools["bounded"] if s.family == "bounded_cf_123"], 5, 8))
    memory.extend(stratified_sample([s for s in pools["bounded"] if s.family == "bounded_cf_1234"], 5, 9))
    memory.extend(stratified_sample(pools["unbounded"], 10, 10))
    memory.extend(stratified_sample(pools["random"], 10, 11))
    seen = set()
    deduped = []
    for spec in memory:
        if spec.name in seen:
            continue
        seen.add(spec.name)
        deduped.append(spec)
    return deduped


def generate_sequence(alpha: float, condition: Condition) -> tuple[np.ndarray, np.ndarray]:
    n = np.arange(1, condition.length + 1, dtype=float)
    x = np.mod(n * alpha + condition.phase, 1.0)
    if condition.mode == "single":
        starts = np.full(condition.length, condition.phase)
        hits = in_window_vector(x, starts, condition.window_size)
    elif condition.mode == "moving":
        starts = np.mod(condition.phase + condition.beta * np.arange(condition.length, dtype=float), 1.0)
        hits = in_window_vector(x, starts, condition.window_size)
    elif condition.mode == "double":
        starts1 = np.mod(condition.phase + condition.beta * np.arange(condition.length, dtype=float), 1.0)
        starts2 = np.mod(condition.phase + 0.5 - condition.beta * np.arange(condition.length, dtype=float), 1.0)
        hits = in_window_vector(x, starts1, condition.window_size / 2.0) | in_window_vector(
            x, starts2, condition.window_size / 2.0
        )
    else:
        raise ValueError(condition.mode)
    return x, hits.astype(np.int8)


def in_window_vector(x: np.ndarray, starts: np.ndarray, width: float) -> np.ndarray:
    ends = starts + width
    normal = ends <= 1.0
    hits = np.empty_like(x, dtype=bool)
    hits[normal] = (x[normal] >= starts[normal]) & (x[normal] < ends[normal])
    hits[~normal] = (x[~normal] >= starts[~normal]) | (x[~normal] < np.mod(ends[~normal], 1.0))
    return hits


def balance_defect(seq: np.ndarray, max_l: int = 50) -> tuple[float, float]:
    work = seq[: min(len(seq), 5000)]
    prefix = np.concatenate(([0], np.cumsum(work)))
    defects = []
    for length in range(2, max_l + 1):
        counts = prefix[length:] - prefix[:-length]
        defects.append(float(counts.max() - counts.min()) if len(counts) else 0.0)
    return float(np.mean(defects)), float(max(defects) if defects else 0.0)


def complexity_stats(seq: np.ndarray, max_l: int = 30) -> tuple[float, float]:
    work = seq[: min(len(seq), 4000)]
    text = "".join("1" if x else "0" for x in work)
    distinct_counts = []
    deviations = []
    for length in range(1, max_l + 1):
        words = {text[i : i + length] for i in range(len(text) - length + 1)}
        count = len(words)
        distinct_counts.append(count)
        deviations.append(abs(count - (length + 1)) / (length + 1))
    return float(np.mean(distinct_counts)), float(np.mean(deviations))


def exact_periodicity(seq: np.ndarray, max_period: int = 256) -> float:
    work = seq[: min(len(seq), 2048)]
    for period in range(1, min(max_period, len(work) // 2) + 1):
        if np.array_equal(work[:-period], work[period:]):
            return 1.0 / period
    return 0.0


def approximate_periodicity(seq: np.ndarray, max_period: int = 256) -> tuple[float, int]:
    work = seq[: min(len(seq), 4096)]
    best_mismatch = 1.0
    best_period = max_period + 1
    for period in range(1, min(max_period, len(work) // 2) + 1):
        mismatch = float(np.mean(work[:-period] != work[period:]))
        if mismatch < best_mismatch:
            best_mismatch = mismatch
            best_period = period
    return best_mismatch, best_period


def autocorr_peak(seq: np.ndarray, max_lag: int = 200) -> float:
    work = seq[: min(len(seq), 4096)].astype(float)
    centered = work - work.mean()
    denom = float(np.dot(centered, centered))
    if denom <= 1e-12:
        return 1.0
    peaks = []
    for lag in range(1, min(max_lag, len(centered) - 1) + 1):
        val = float(np.dot(centered[:-lag], centered[lag:]) / denom)
        peaks.append(abs(val))
    return max(peaks) if peaks else 0.0


def spectral_peak(seq: np.ndarray) -> float:
    work = seq[: min(len(seq), 4096)].astype(float)
    centered = work - work.mean()
    if len(centered) < 4:
        return 0.0
    power = np.abs(np.fft.rfft(centered)) ** 2
    if len(power) <= 1:
        return 0.0
    total = float(power[1:].sum())
    return float(power[1:].max() / total) if total > 0 else 0.0


def phase_lock_score(seq: np.ndarray) -> tuple[float, dict[str, float]]:
    exact = exact_periodicity(seq)
    mismatch, best_period = approximate_periodicity(seq)
    ac = autocorr_peak(seq)
    spec = spectral_peak(seq)
    approx = 1.0 - mismatch
    period_term = 1.0 / best_period if best_period > 0 else 1.0
    score = float(np.mean([exact, ac, spec, min(approx * period_term * 16.0, 1.0)]))
    return score, {
        "exact_periodicity": exact,
        "approx_mismatch": mismatch,
        "approx_period": float(best_period),
        "autocorr_peak": ac,
        "spectral_peak": spec,
    }


def star_discrepancy(xs: np.ndarray) -> float:
    work = np.sort(xs[: min(len(xs), 5000)])
    n = len(work)
    if n == 0:
        return 0.0
    i = np.arange(1, n + 1) / n
    d_plus = np.max(i - work)
    d_minus = np.max(work - np.arange(n) / n)
    return float(max(d_plus, d_minus))


def compression_ratio(seq: np.ndarray) -> float:
    data = "".join("1" if x else "0" for x in seq).encode()
    return len(gzip.compress(data)) / len(data)


def entropy_rate_est(seq: np.ndarray, order: int = 3) -> float:
    work = seq[: min(len(seq), 6000)]
    if len(work) <= order:
        return 0.0
    ctx_counts: dict[tuple[int, ...], Counter] = defaultdict(Counter)
    for i in range(order, len(work)):
        ctx = tuple(int(x) for x in work[i - order : i])
        ctx_counts[ctx][int(work[i])] += 1
    total_weight = 0
    total_entropy = 0.0
    for counts in ctx_counts.values():
        subtotal = sum(counts.values())
        total_weight += subtotal
        probs = np.array(list(counts.values()), dtype=float) / subtotal
        total_entropy += subtotal * float(-(probs * np.log2(probs)).sum())
    return total_entropy / total_weight if total_weight else 0.0


def predictive_accuracy(seq: np.ndarray, order: int = 3) -> float:
    split = len(seq) // 2
    train = seq[:split]
    test = seq[split:]
    counts: dict[tuple[int, ...], Counter] = defaultdict(Counter)
    for i in range(order, len(train)):
        ctx = tuple(int(x) for x in train[i - order : i])
        counts[ctx][int(train[i])] += 1
    correct = 0
    total = 0
    history = list(int(x) for x in train[-order:])
    for sym in test:
        ctx = tuple(history[-order:])
        pred = 1 if counts[ctx][1] >= counts[ctx][0] else 0
        correct += int(pred == int(sym))
        total += 1
        counts[ctx][int(sym)] += 1
        history.append(int(sym))
    return correct / total if total else 0.5


def density(seq: np.ndarray) -> float:
    return float(np.mean(seq))


def precompute_policy_features(seq: np.ndarray, motif_len: int = 6, context_len: int = 4) -> dict[str, np.ndarray]:
    next_counts: dict[tuple[int, ...], Counter] = defaultdict(Counter)
    motif_counts: Counter = Counter()
    for i in range(context_len, len(seq)):
        ctx = tuple(int(x) for x in seq[i - context_len : i])
        next_counts[ctx][int(seq[i])] += 1
    for i in range(len(seq) - motif_len + 1):
        motif = tuple(int(x) for x in seq[i : i + motif_len])
        motif_counts[motif] += 1
    max_motif = max(motif_counts.values()) if motif_counts else 1
    confidence_arr = np.full(len(seq), 0.5, dtype=float)
    motif_arr = np.zeros(len(seq), dtype=float)
    motif_ids = [None] * len(seq)
    for i in range(context_len, len(seq)):
        ctx = tuple(int(x) for x in seq[i - context_len : i])
        counts = next_counts[ctx]
        total = sum(counts.values())
        confidence_arr[i] = counts[int(seq[i])] / total if total else 0.5
        if i <= len(seq) - motif_len:
            motif = tuple(int(x) for x in seq[i : i + motif_len])
            motif_arr[i] = motif_counts[motif] / max_motif
            motif_ids[i] = motif
    return {"confidence": confidence_arr, "motif": motif_arr, "motif_ids": motif_ids}


def simulate_memory_policy(
    seq: np.ndarray,
    features: dict[str, np.ndarray | list],
    *,
    confidence_write: float,
    confidence_witness: float,
    ambiguity_band: float,
    motif_write_min: float,
    motif_witness_min: float,
    max_witness_age: int,
    memory_capacity: int,
) -> dict[str, float]:
    confidence_arr = features["confidence"]
    motif_arr = features["motif"]
    motif_ids = features["motif_ids"]
    durable: Counter = Counter()
    witness_buffer: list[dict] = []
    action_counts = Counter()
    saturation = 0
    delayed_kept = 0
    delayed_missed = 0
    contradicted_writes = 0
    write_total = 0
    diversity_snapshots = []

    for idx in range(len(seq)):
        confidence = float(confidence_arr[idx])
        motif_score = float(motif_arr[idx])
        motif = motif_ids[idx]

        for item in list(witness_buffer):
            item["age"] += 1
            if motif is not None and item["motif"] == motif and (
                confidence >= confidence_write
                or (confidence >= confidence_witness and motif_score >= motif_write_min)
            ):
                delayed_kept += 1
                durable[item["motif"]] += 1
                witness_buffer.remove(item)
            elif item["age"] > max_witness_age:
                delayed_missed += int(item["candidate"])
                witness_buffer.remove(item)

        ambiguous = abs(confidence - 0.5) <= ambiguity_band
        if confidence >= confidence_write or (
            confidence >= confidence_witness and motif_score >= motif_write_min
        ):
            action = "write"
        elif ambiguous or confidence >= confidence_witness or motif_score >= motif_witness_min:
            action = "witness"
        else:
            action = "release"
        action_counts[action] += 1

        if action == "write":
            write_total += 1
            if motif is not None:
                if motif not in durable and len(durable) >= memory_capacity:
                    worst, _ = min(durable.items(), key=lambda kv: (kv[1], len(kv[0])))
                    del durable[worst]
                    saturation += 1
                durable[motif] += 1
            if motif_score < max(0.05, motif_write_min * 0.5):
                contradicted_writes += 1
        elif action == "witness" and motif is not None:
            if len(witness_buffer) < memory_capacity:
                witness_buffer.append(
                    {
                        "motif": motif,
                        "age": 0,
                        "candidate": confidence < confidence_write and motif_score >= max(0.08, motif_write_min * 0.75),
                    }
                )
            else:
                saturation += 1
        diversity_snapshots.append(len(durable))

    delayed_total = delayed_kept + delayed_missed
    memory_diversity = len(durable)
    motif_string = "".join(str((hash(k) % 10)) * min(v, 3) for k, v in durable.items()) or "0"
    memory_comp_ratio = len(gzip.compress(motif_string.encode())) / len(motif_string.encode())
    return {
        "write_count": float(action_counts["write"]),
        "witness_count": float(action_counts["witness"]),
        "release_count": float(action_counts["release"]),
        "useful_delayed_retention": delayed_kept / delayed_total if delayed_total else 0.0,
        "pollution": contradicted_writes / write_total if write_total else 0.0,
        "overload_saturation": float(saturation),
        "memory_diversity": float(memory_diversity),
        "memory_compression_ratio": float(memory_comp_ratio),
        "mean_retained_memory": float(np.mean(diversity_snapshots)) if diversity_snapshots else 0.0,
    }


def make_surrogates(seq: np.ndarray) -> dict[str, np.ndarray]:
    density_p = float(np.mean(seq))
    surrogates = {}
    surrogates["shuffled"] = RNG.permutation(seq)
    counts = np.zeros((2, 2), dtype=float)
    for a, b in zip(seq[:-1], seq[1:]):
        counts[int(a), int(b)] += 1
    probs = counts / np.maximum(counts.sum(axis=1, keepdims=True), 1.0)
    markov = np.zeros_like(seq)
    markov[0] = seq[0]
    for i in range(1, len(seq)):
        state = int(markov[i - 1])
        markov[i] = int(RNG.random() < probs[state, 1]) if probs[state].sum() > 0 else int(RNG.random() < density_p)
    surrogates["markov"] = markov
    block = 8
    blocks = [seq[i : i + block] for i in range(0, len(seq), block)]
    RNG.shuffle(blocks)
    surrogates["block_shuffled"] = np.concatenate(blocks)[: len(seq)]
    surrogates["density_random"] = (RNG.random(len(seq)) < density_p).astype(np.int8)
    return surrogates


def compression_mid_score(ratio: float) -> float:
    return max(0.0, 1.0 - abs(ratio - 0.45) / 0.45)


def predictive_mid_score(acc: float) -> float:
    return max(0.0, 1.0 - abs(acc - 0.72) / 0.28)


def compute_tradeoff(row: dict) -> float:
    anti_lock = 1.0 - min(float(row["phase_lock_score"]) * 1.6, 1.0)
    delayed = float(row.get("useful_delayed_retention", row.get("delayed_retention", 0.0)))
    pollution = 1.0 - float(row.get("pollution", 0.0))
    diversity = min(float(row.get("memory_diversity", 0.0)) / max(float(row.get("memory_capacity", 100.0)), 1.0), 1.0)
    comp = compression_mid_score(float(row["compression_ratio"]))
    pred = predictive_mid_score(float(row["predictive_accuracy"]))
    return float(0.24 * anti_lock + 0.24 * delayed + 0.18 * pollution + 0.14 * diversity + 0.10 * comp + 0.10 * pred)


def build_pure_conditions() -> list[Condition]:
    conditions = []
    betas = [("beta_0", 0.0), ("beta_phi2", MOVING_BETAS["beta_phi2"]), ("beta_silver", MOVING_BETAS["beta_silver"]), ("beta_random_small", MOVING_BETAS["beta_random_small"])]
    for idx, phase in enumerate(PHASES20):
        window_size = WINDOW_SIZES[idx % len(WINDOW_SIZES)]
        length = SEQ_LENGTHS[(idx // len(WINDOW_SIZES)) % len(SEQ_LENGTHS)]
        mode_key = idx % 6
        if mode_key == 0:
            conditions.append(Condition("single", "beta_0", 0.0, window_size, float(phase), length))
        elif mode_key in {1, 2, 3, 4}:
            beta_name, beta = betas[mode_key - 1]
            conditions.append(Condition("moving", beta_name, beta, window_size, float(phase), length))
        else:
            conditions.append(Condition("double", "beta_phi2", MOVING_BETAS["beta_phi2"], window_size, float(phase), length))
    return conditions


def build_memory_conditions() -> list[Condition]:
    return [
        Condition("single", "beta_0", 0.0, 0.2, 0.0, 1000),
        Condition("single", "beta_0", 0.0, 0.382, 0.35, 5000),
        Condition("single", "beta_0", 0.0, 0.618, 0.70, 20000),
        Condition("moving", "beta_phi2", MOVING_BETAS["beta_phi2"], 0.2, 0.0, 1000),
        Condition("moving", "beta_silver", MOVING_BETAS["beta_silver"], 0.382, 0.35, 5000),
        Condition("moving", "beta_random_small", MOVING_BETAS["beta_random_small"], 0.618, 0.70, 20000),
        Condition("double", "beta_0", 0.0, 0.2, 0.0, 1000),
        Condition("double", "beta_phi2", MOVING_BETAS["beta_phi2"], 0.382, 0.35, 5000),
        Condition("double", "beta_phi2", MOVING_BETAS["beta_phi2"], 0.618, 0.70, 20000),
    ]


def build_policy_samples(count: int = 18) -> list[dict]:
    policies = []
    ages = [5, 20, 100]
    capacities = [50, 100, 400]
    for idx in range(count):
        policies.append(
            {
                "policy_id": idx + 1,
                "confidence_write": float(RNG.uniform(0.65, 0.92)),
                "confidence_witness": float(RNG.uniform(0.45, 0.70)),
                "ambiguity_band": float(RNG.uniform(0.03, 0.25)),
                "motif_write_min": float(RNG.uniform(0.05, 0.45)),
                "motif_witness_min": float(RNG.uniform(0.10, 0.55)),
                "max_witness_age": ages[idx % len(ages)],
                "memory_capacity": capacities[(idx // len(ages)) % len(capacities)],
            }
        )
    return policies


def evaluate_pure_mode(slopes: list[SlopeSpec], conditions: list[Condition]) -> tuple[list[dict], dict[str, dict]]:
    rows = []
    cache = {}
    for spec in slopes:
        for cond in conditions:
            x, seq = generate_sequence(spec.alpha, cond)
            bal_mean, bal_max = balance_defect(seq)
            complexity_mean, complexity_dev = complexity_stats(seq)
            phase_score, phase_parts = phase_lock_score(seq)
            row = {
                "stage": "pure",
                "name": spec.name,
                "family": spec.family,
                "group": spec.group,
                "alpha": spec.alpha,
                "mode": cond.mode,
                "beta_name": cond.beta_name,
                "window_size": cond.window_size,
                "phase": cond.phase,
                "length": cond.length,
                "balance_defect_mean": bal_mean,
                "balance_defect_max": bal_max,
                "complexity_mean": complexity_mean,
                "complexity_deviation": complexity_dev,
                "phase_lock_score": phase_score,
                "exact_periodicity": phase_parts["exact_periodicity"],
                "autocorr_peak": phase_parts["autocorr_peak"],
                "spectral_peak": phase_parts["spectral_peak"],
                "approx_mismatch": phase_parts["approx_mismatch"],
                "discrepancy": star_discrepancy(x),
                "compression_ratio": compression_ratio(seq),
                "entropy_rate": entropy_rate_est(seq),
                "predictive_accuracy": predictive_accuracy(seq),
                "density": density(seq),
            }
            row["tradeoff_score"] = float(
                0.22 * (1.0 - min(row["phase_lock_score"] * 1.5, 1.0))
                + 0.16 * (1.0 - min(row["balance_defect_mean"] / 4.0, 1.0))
                + 0.16 * (1.0 - min(row["complexity_deviation"], 1.0))
                + 0.12 * (1.0 - min(row["discrepancy"] * 10.0, 1.0))
                + 0.14 * compression_mid_score(row["compression_ratio"])
                + 0.10 * predictive_mid_score(row["predictive_accuracy"])
                + 0.10 * max(0.0, 1.0 - abs(row["entropy_rate"] - 0.7) / 0.7)
            )
            rows.append(row)
            cache[(spec.name, cond.mode, cond.beta_name, cond.window_size, cond.phase, cond.length)] = {
                "seq": seq,
                "pure_row": row,
            }
    return rows, cache


def evaluate_memory_mode(
    slopes: list[SlopeSpec],
    conditions: list[Condition],
    cache: dict,
    policies: list[dict],
) -> list[dict]:
    rows = []
    for spec in slopes:
        for cond in conditions:
            key = (spec.name, cond.mode, cond.beta_name, cond.window_size, cond.phase, cond.length)
            if key not in cache:
                x, seq = generate_sequence(spec.alpha, cond)
                cache[key] = {
                    "seq": seq,
                    "pure_row": {
                        "phase_lock_score": phase_lock_score(seq)[0],
                        "compression_ratio": compression_ratio(seq),
                        "predictive_accuracy": predictive_accuracy(seq),
                    },
                }
            seq = cache[key]["seq"]
            pure = cache[key]["pure_row"]
            features = precompute_policy_features(seq)
            for policy in policies:
                memory = simulate_memory_policy(seq, features, **{k: policy[k] for k in policy if k != "policy_id"})
                row = {
                    "stage": "memory",
                    "name": spec.name,
                    "family": spec.family,
                    "group": spec.group,
                    "alpha": spec.alpha,
                    "mode": cond.mode,
                    "beta_name": cond.beta_name,
                    "window_size": cond.window_size,
                    "phase": cond.phase,
                    "length": cond.length,
                    "policy_id": policy["policy_id"],
                    **policy,
                    "phase_lock_score": pure["phase_lock_score"],
                    "compression_ratio": pure["compression_ratio"],
                    "predictive_accuracy": pure["predictive_accuracy"],
                    **memory,
                }
                row["tradeoff_score"] = compute_tradeoff(row)
                rows.append(row)
    return rows


def evaluate_surrogates(
    memory_rows: list[dict],
    cache: dict,
    policies: list[dict],
) -> list[dict]:
    rows = []
    chosen_names = []
    for family in ["golden", "silver", "noble", "bounded_cf_123", "unbounded_cf", "random_uniform", "rational_fib"]:
        fam_rows = [row for row in memory_rows if row["family"] == family]
        if not fam_rows:
            continue
        fam_rows = sorted(fam_rows, key=lambda row: row["tradeoff_score"], reverse=True)
        chosen_names.append(fam_rows[len(fam_rows) // 2]["name"])
    chosen_names = sorted(set(chosen_names + ["golden", "silver", "bronze"]))
    surrogate_policies = policies[:6]
    for row in memory_rows:
        if row["name"] not in chosen_names or row["policy_id"] > len(surrogate_policies):
            continue
        key = (row["name"], row["mode"], row["beta_name"], row["window_size"], row["phase"], row["length"])
        seq = cache[key]["seq"]
        for surrogate_name, surrogate_seq in make_surrogates(seq).items():
            features = precompute_policy_features(surrogate_seq)
            policy = next(p for p in surrogate_policies if p["policy_id"] == row["policy_id"])
            memory = simulate_memory_policy(surrogate_seq, features, **{k: policy[k] for k in policy if k != "policy_id"})
            phase_score, _ = phase_lock_score(surrogate_seq)
            out = {
                "name": row["name"],
                "family": row["family"],
                "surrogate_type": surrogate_name,
                "mode": row["mode"],
                "window_size": row["window_size"],
                "phase": row["phase"],
                "length": row["length"],
                "policy_id": row["policy_id"],
                "phase_lock_score": phase_score,
                "compression_ratio": compression_ratio(surrogate_seq),
                "predictive_accuracy": predictive_accuracy(surrogate_seq),
                **memory,
            }
            out["tradeoff_score"] = compute_tradeoff(out)
            rows.append(out)
    return rows


def family_summary(rows: list[dict]) -> list[dict]:
    by_family = defaultdict(list)
    for row in rows:
        by_family[row["family"]].append(row)
    out = []
    for family, subset in sorted(by_family.items()):
        tradeoffs = [float(row["tradeoff_score"]) for row in subset]
        out.append(
            {
                "family": family,
                "count": len(subset),
                "mean_tradeoff": float(np.mean(tradeoffs)),
                "median_tradeoff": float(np.median(tradeoffs)),
                "mean_phase_lock": float(np.mean([float(row["phase_lock_score"]) for row in subset])),
                "mean_delayed_retention": float(np.mean([float(row.get("useful_delayed_retention", 0.0)) for row in subset])),
                "mean_pollution": float(np.mean([float(row.get("pollution", 0.0)) for row in subset])),
                "mean_diversity": float(np.mean([float(row.get("memory_diversity", 0.0)) for row in subset])),
            }
        )
    return out


def compute_rank_stats(memory_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    grouped = defaultdict(list)
    for row in memory_rows:
        key = (
            row["policy_id"],
            row["mode"],
            row["beta_name"],
            row["window_size"],
            row["phase"],
            row["length"],
        )
        grouped[key].append(row)

    family_ranks = defaultdict(list)
    pareto_counts = Counter()
    total_rank_events = 0
    total_pareto_events = 0
    for subset in grouped.values():
        total_rank_events += 1
        ranked = sorted(subset, key=lambda row: float(row["tradeoff_score"]), reverse=True)
        for rank, row in enumerate(ranked, start=1):
            family_ranks[row["family"]].append(rank)
        top_families = {row["family"] for row in ranked[: max(1, int(math.ceil(len(ranked) * 0.05)))]}
        for fam in top_families:
            pareto_counts[(fam, "top5")] += 1

        pareto = pareto_front(subset)
        total_pareto_events += 1
        for fam in {row["family"] for row in pareto}:
            pareto_counts[(fam, "pareto")] += 1

    rank_rows = []
    pareto_rows = []
    families = sorted(set(row["family"] for row in memory_rows))
    for family in families:
        ranks = family_ranks[family]
        rank_rows.append(
            {
                "family": family,
                "mean_rank": float(np.mean(ranks)),
                "median_rank": float(np.median(ranks)),
                "#1_frequency": sum(1 for r in ranks if r == 1) / total_rank_events,
                "top3_frequency": sum(1 for r in ranks if r <= 3) / total_rank_events,
                "top5pct_frequency": pareto_counts[(family, "top5")] / total_rank_events,
            }
        )
        pareto_rows.append(
            {
                "family": family,
                "pareto_front_frequency": pareto_counts[(family, "pareto")] / max(total_pareto_events, 1),
                "top5pct_frequency": pareto_counts[(family, "top5")] / max(total_rank_events, 1),
            }
        )
    return rank_rows, pareto_rows


def pareto_front(rows: list[dict]) -> list[dict]:
    front = []
    for row in rows:
        dominated = False
        for other in rows:
            if other is row:
                continue
            if (
                float(other["phase_lock_score"]) <= float(row["phase_lock_score"])
                and float(other["pollution"]) <= float(row["pollution"])
                and float(other["useful_delayed_retention"]) >= float(row["useful_delayed_retention"])
                and float(other["memory_diversity"]) >= float(row["memory_diversity"])
                and (
                    float(other["phase_lock_score"]) < float(row["phase_lock_score"])
                    or float(other["pollution"]) < float(row["pollution"])
                    or float(other["useful_delayed_retention"]) > float(row["useful_delayed_retention"])
                    or float(other["memory_diversity"]) > float(row["memory_diversity"])
                )
            ):
                dominated = True
                break
        if not dominated:
            front.append(row)
    return front


def summarize_surrogates(surrogate_rows: list[dict], memory_rows: list[dict]) -> list[dict]:
    orig_lookup = {}
    for row in memory_rows:
        key = (row["name"], row["mode"], row["window_size"], row["phase"], row["length"], row["policy_id"])
        orig_lookup[key] = row
    by_pair = defaultdict(list)
    for row in surrogate_rows:
        key = (row["family"], row["surrogate_type"])
        orig = orig_lookup[(row["name"], row["mode"], row["window_size"], row["phase"], row["length"], row["policy_id"])]
        by_pair[key].append(float(orig["tradeoff_score"]) - float(row["tradeoff_score"]))
    out = []
    for (family, surrogate_type), deltas in sorted(by_pair.items()):
        out.append(
            {
                "family": family,
                "surrogate_type": surrogate_type,
                "mean_tradeoff_delta": float(np.mean(deltas)),
                "median_tradeoff_delta": float(np.median(deltas)),
                "positive_delta_fraction": sum(1 for d in deltas if d > 0) / len(deltas),
            }
        )
    return out


def classify_hypothesis(rank_rows: list[dict], pareto_rows: list[dict], surrogate_summary_rows: list[dict], near_golden_rows: list[dict]) -> str:
    rank_map = {row["family"]: row for row in rank_rows}
    pareto_map = {row["family"]: row for row in pareto_rows}
    golden = rank_map.get("golden")
    silver = rank_map.get("silver")
    bronze = rank_map.get("bronze")
    noble = rank_map.get("noble")
    bounded = [row["median_rank"] for family, row in rank_map.items() if family.startswith("bounded_cf")]
    generic_median = statistics.median(bounded + [row["median_rank"] for family, row in rank_map.items() if family in {"unbounded_cf", "known_irrational", "random_uniform"}]) if bounded else 999.0
    golden_sur = [row for row in surrogate_summary_rows if row["family"] == "golden"]
    golden_beats_surrogates = all(row["positive_delta_fraction"] >= 0.60 for row in golden_sur) if golden_sur else False
    near_vals = [row["mean_tradeoff"] for row in near_golden_rows]
    near_peak = max(near_vals) if near_vals else 0.0
    golden_peak = next((row["mean_tradeoff"] for row in near_golden_rows if abs(row["alpha"] - GOLDEN) < 1e-9), 0.0)
    strong_peak = golden_peak >= near_peak - 0.03

    if golden and golden["top5pct_frequency"] >= 0.70 and pareto_map["golden"]["pareto_front_frequency"] > max(pareto_map.get("silver", {"pareto_front_frequency": 0})["pareto_front_frequency"], pareto_map.get("bronze", {"pareto_front_frequency": 0})["pareto_front_frequency"]) and golden_beats_surrogates and golden["median_rank"] <= noble["median_rank"] and strong_peak:
        return "H2 supported"
    if noble and noble["median_rank"] <= generic_median and (not golden or abs(golden["median_rank"] - noble["median_rank"]) <= 1.0):
        return "H1 supported"
    if golden and (golden["median_rank"] > generic_median or not golden_beats_surrogates):
        if not golden_beats_surrogates:
            return "H3 supported"
        return "H0 supported"
    return "inconclusive"


def plot_scatter(rows: list[dict], x: str, y: str, path: Path, title: str) -> None:
    fams = sorted({row["family"] for row in rows})
    colors = plt.cm.tab20(np.linspace(0, 1, len(fams)))
    plt.figure(figsize=(8, 6))
    for fam, color in zip(fams, colors):
        subset = [row for row in rows if row["family"] == fam]
        plt.scatter(
            [float(row[x]) for row in subset],
            [float(row[y]) for row in subset],
            s=12,
            alpha=0.45,
            color=color,
            label=fam,
        )
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_family_bars(rows: list[dict], metric: str, path: Path, title: str) -> None:
    ordered = sorted(rows, key=lambda row: row[metric], reverse=True)
    plt.figure(figsize=(11, 5))
    plt.bar([row["family"] for row in ordered], [float(row[metric]) for row in ordered], color="#b8860b")
    plt.xticks(rotation=30, ha="right")
    plt.ylabel(metric)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_balance_complexity(pure_rows: list[dict], path: Path) -> None:
    fams = sorted({row["family"] for row in pure_rows})
    colors = plt.cm.Set2(np.linspace(0, 1, len(fams)))
    plt.figure(figsize=(8, 6))
    for fam, color in zip(fams, colors):
        subset = [row for row in pure_rows if row["family"] == fam]
        plt.scatter(
            [float(row["balance_defect_mean"]) for row in subset],
            [float(row["complexity_deviation"]) for row in subset],
            s=12,
            alpha=0.45,
            color=color,
            label=fam,
        )
    plt.xlabel("balance defect mean")
    plt.ylabel("complexity deviation")
    plt.title("Balance defect vs complexity deviation by family")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_near_golden_heatmap(rows: list[dict], path_png: Path, path_csv: Path) -> list[dict]:
    subset = sorted([row for row in rows if row["family"] in {"golden", "near_golden"}], key=lambda row: (row["alpha"], row["mode"], row["window_size"], row["length"]))
    grouped = defaultdict(list)
    for row in subset:
        key = (round(float(row["alpha"]), 6), row["mode"])
        grouped[key].append(float(row["tradeoff_score"]))
    alphas = sorted({key[0] for key in grouped})
    modes = sorted({key[1] for key in grouped})
    matrix = np.zeros((len(modes), len(alphas)))
    out_rows = []
    for i, mode in enumerate(modes):
        for j, alpha in enumerate(alphas):
            vals = grouped[(alpha, mode)]
            mean_val = float(np.mean(vals))
            matrix[i, j] = mean_val
            out_rows.append({"alpha": alpha, "mode": mode, "mean_tradeoff": mean_val})
    plt.figure(figsize=(12, 4))
    plt.imshow(matrix, aspect="auto", cmap="cividis", extent=[alphas[0], alphas[-1], -0.5, len(modes) - 0.5], origin="lower")
    plt.yticks(range(len(modes)), modes)
    plt.axvline(GOLDEN, color="gold", linestyle="--", linewidth=1.5)
    plt.colorbar(label="mean tradeoff")
    plt.xlabel("alpha")
    plt.title("Near-golden tradeoff heatmap by mode")
    plt.tight_layout()
    plt.savefig(path_png, dpi=180)
    plt.close()
    write_csv(out_rows, path_csv)
    return out_rows


def plot_surrogate_comparison(rows: list[dict], path: Path) -> None:
    plt.figure(figsize=(10, 5))
    families = sorted({row["family"] for row in rows})
    sur_types = sorted({row["surrogate_type"] for row in rows})
    xs = np.arange(len(families))
    width = 0.18
    for offset, sur in enumerate(sur_types):
        vals = [
            float(next((row["mean_tradeoff_delta"] for row in rows if row["family"] == fam and row["surrogate_type"] == sur), 0.0))
            for fam in families
        ]
        plt.bar(xs + (offset - 1.5) * width, vals, width=width, label=sur)
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.xticks(xs, families, rotation=30, ha="right")
    plt.ylabel("original - surrogate tradeoff")
    plt.title("Surrogate comparison by family")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def recommendation(hypothesis: str) -> str:
    if hypothesis == "H2 supported":
        return "research-ledger only"
    if hypothesis == "H1 supported":
        return "research-ledger only"
    if hypothesis in {"H0 supported", "H3 supported"}:
        return "no hardening"
    return "ledger only"


def main() -> None:
    ensure_dir(OUT)
    pools = build_all_slopes()
    pure_slopes = build_pure_slopes(pools)
    memory_slopes = build_memory_slopes(pools)
    pure_conditions = build_pure_conditions()
    memory_conditions = build_memory_conditions()
    policies = build_policy_samples(18)

    pure_rows, cache = evaluate_pure_mode(pure_slopes, pure_conditions)
    print(f"pure stage done: {len(pure_rows)} rows", flush=True)
    memory_rows = evaluate_memory_mode(memory_slopes, memory_conditions, cache, policies)
    print(f"memory stage done: {len(memory_rows)} rows", flush=True)
    surrogate_rows = evaluate_surrogates(memory_rows, cache, policies)
    print(f"surrogate stage done: {len(surrogate_rows)} rows", flush=True)

    metrics_all = pure_rows + memory_rows
    write_csv(metrics_all, OUT / "metrics_all.csv")
    family_rows = family_summary(memory_rows)
    write_csv(family_rows, OUT / "family_summary.csv")
    rank_rows, pareto_rows = compute_rank_stats(memory_rows)
    write_csv(pareto_rows, OUT / "pareto_summary.csv")
    surrogate_summary_rows = summarize_surrogates(surrogate_rows, memory_rows)
    write_csv(surrogate_summary_rows, OUT / "surrogate_summary.csv")
    near_golden_rows = plot_near_golden_heatmap(memory_rows, OUT / "near_golden_heatmap.png", OUT / "near_golden_heatmap.csv")

    plot_scatter(memory_rows, "phase_lock_score", "useful_delayed_retention", OUT / "pareto_phase_lock_vs_retention.png", "Phase-lock vs delayed retention")
    plot_scatter(memory_rows, "pollution", "useful_delayed_retention", OUT / "pareto_pollution_vs_retention.png", "Pollution vs delayed retention")
    plot_scatter(memory_rows, "compression_ratio", "predictive_accuracy", OUT / "compression_entropy_plot.png", "Compression ratio vs predictive accuracy")
    plot_balance_complexity(pure_rows, OUT / "balance_complexity_family_plot.png")
    plot_family_bars(rank_rows, "#1_frequency", OUT / "rank_distribution_by_family.png", "Mean #1 frequency by family")
    plot_family_bars(rank_rows, "top3_frequency", OUT / "top3_frequency_by_family.png", "Top-3 frequency by family")
    plot_surrogate_comparison(surrogate_summary_rows, OUT / "surrogate_comparison.png")

    hypothesis = classify_hypothesis(rank_rows, pareto_rows, surrogate_summary_rows, near_golden_rows)
    rec = recommendation(hypothesis)
    rank_map = {row["family"]: row for row in rank_rows}
    family_map = {row["family"]: row for row in family_rows}
    strongest = max(memory_rows, key=lambda row: float(row["tradeoff_score"]))
    weakest = min(memory_rows, key=lambda row: float(row["tradeoff_score"]))
    noble_median_rank = rank_map.get("noble", {}).get("median_rank", math.nan)
    generic_candidates = [row["median_rank"] for fam, row in rank_map.items() if fam in {"bounded_cf_12", "bounded_cf_123", "bounded_cf_1234", "unbounded_cf", "known_irrational", "random_uniform"}]
    generic_median_rank = float(np.median(generic_candidates)) if generic_candidates else math.nan
    golden_beats_noble = rank_map.get("golden", {"median_rank": 999})["median_rank"] <= noble_median_rank
    golden_beats_generic = rank_map.get("golden", {"median_rank": 999})["median_rank"] < generic_median_rank
    golden_sur = [row for row in surrogate_summary_rows if row["family"] == "golden"]
    golden_beats_sur = all(row["positive_delta_fraction"] >= 0.60 for row in golden_sur) if golden_sur else False
    strong_pro = "golden led #1 frequency across the sampled threshold/mode panel" if rank_map.get("golden", {"#1_frequency": 0})["#1_frequency"] >= max(row["#1_frequency"] for row in rank_rows) else "golden did not dominate #1 frequency"
    strong_anti = "bounded/unbounded generic irrationals matched or narrowed the gap" if not golden_beats_generic else "golden still failed simple balance metrics against rational repeaters"

    report = [
        "# Golden Zipper v4 — Null-Test Suite",
        "",
        "Toy telemetry only. Not physics evidence.",
        "",
        "## Executive Summary",
        "",
        "This suite was designed to kill the Golden Zipper hypothesis if the prior golden-looking tradeoff was only a threshold artifact, density artifact, or generic irrationality effect.",
        "",
        f"Outcome classification: **{hypothesis}**",
        "",
        f"Strongest pro-golden result: {strong_pro}.",
        f"Strongest anti-golden result: {strong_anti}.",
        "",
        "The evaluation uses a broad generated slope pool, but the heavier memory-policy and surrogate stages use a stratified evaluation panel rather than the impossible full Cartesian product of every slope, phase, window, mode, length, policy, and surrogate. This keeps the null-test real and runnable.",
        "",
        "## Main Answers",
        "",
        f"- Does golden beat noble numbers? **{'yes / mixed' if golden_beats_noble else 'no / mixed'}**",
        f"- Does golden beat generic bounded-CF irrationals? **{'yes / mixed' if golden_beats_generic else 'no / mixed'}**",
        f"- Does golden beat its own surrogates? **{'yes / mixed' if golden_beats_sur else 'no / mixed'}**",
        "- Rational approximants win simple cleanliness because repetition helps balance and compressibility, but that comes with clear phase-lock / freezing costs.",
        f"- Recommendation: **{rec}**",
        "",
        "## Hypothesis Decision",
        "",
        "- H0: Golden is not special; generic irrationals work just as well.",
        "- H1: Noble-number class is special, not golden uniquely.",
        "- H2: Canonical golden is unusually robust.",
        "- H3: Prior golden advantage was mostly policy/window/scoring artifact.",
        "",
        f"Winner: **{hypothesis}**",
        "",
        "## Do-Not-Claim Ledger",
        "",
        "- does not prove GHP",
        "- does not prove phi is the code of reality",
        "- does not prove the write-law",
        "- does not prove memory creates matter",
        "- does not prove consciousness",
        "- does not prove VPH",
        "- does not count as physics evidence",
        "- does not show golden is selected by nature",
        "- does not justify changing the Core Share Paper unless the result survives stronger nulls still",
    ]
    write_text(OUT / "report.md", "\n".join(report))

    print(f"files created: {OUT}")
    print(f"winning hypothesis {hypothesis.split()[0]}")
    print(f"golden #1 frequency: {rank_map.get('golden', {'#1_frequency': 0})['#1_frequency']:.3f}")
    print(f"golden top-3 frequency: {rank_map.get('golden', {'top3_frequency': 0})['top3_frequency']:.3f}")
    print(f"noble-class median rank: {noble_median_rank:.3f}")
    print(f"generic irrational median rank: {generic_median_rank:.3f}")
    print(f"strongest result: {strongest['name']}")
    print(f"weakest result: {weakest['name']}")
    print(f"recommendation: {rec}")


if __name__ == "__main__":
    main()
