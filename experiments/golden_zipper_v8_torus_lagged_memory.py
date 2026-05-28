#!/usr/bin/env python3
"""v8 torus/sphere lagged-memory toy for Golden Zipper."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v8_outputs"

SEED = 20260517
RNG = np.random.default_rng(SEED)

OFFSET_GRID = np.arange(-0.06, 0.0601, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
PHASES = [0.0]
BETAS = [0.0, 0.011]
LENGTHS = [4096]
MAX_CLOSURE_AGES = [4, 13]
MEMORY_CAPACITIES = [34]


@dataclass(frozen=True)
class AnchorSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class ObserverCondition:
    window_width: float
    phase: float
    beta: float
    length: int
    max_closure_age: int
    memory_capacity: int


@dataclass(frozen=True)
class ModelSpec:
    name: str
    label: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
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


def wrap01(x: np.ndarray | float) -> np.ndarray | float:
    return np.mod(x, 1.0)


def wrap_signed(x: np.ndarray | float) -> np.ndarray | float:
    return np.mod(np.asarray(x) + 0.5, 1.0) - 0.5


def continued_fraction_value(coeffs: list[int], tail_ones: int = 16) -> float:
    values = list(coeffs) + [1] * tail_ones
    out = float(values[-1])
    for coeff in reversed(values[:-1]):
        out = float(coeff) + 1.0 / out
    return 1.0 / out


def build_anchors() -> list[AnchorSpec]:
    golden = 1.0 / PHI
    silver = math.sqrt(2.0) - 1.0
    bronze = (math.sqrt(13.0) - 3.0) / 2.0
    noble_a = continued_fraction_value([2, 3], tail_ones=18)
    noble_b = continued_fraction_value([1, 4, 2], tail_ones=18)
    bounded_probe = continued_fraction_value([2, 1, 2, 1, 2, 1], tail_ones=12)
    random_bad = continued_fraction_value(RNG.choice([1, 2, 3], size=8, replace=True).tolist(), tail_ones=18)
    return [
        AnchorSpec("golden", golden, "phi_anchor"),
        AnchorSpec("silver", silver, "metallic_anchor"),
        AnchorSpec("bronze", bronze, "metallic_anchor"),
        AnchorSpec("noble_a", noble_a, "noble_anchor"),
        AnchorSpec("noble_b", noble_b, "noble_anchor"),
        AnchorSpec("bounded_probe", bounded_probe, "bounded_anchor"),
        AnchorSpec("random_bad_cf", random_bad, "random_bounded_cf"),
        AnchorSpec("pi_mod1", math.pi % 1.0, "constant_control"),
        AnchorSpec("e_mod1", math.e % 1.0, "constant_control"),
        AnchorSpec("fib_13_21", 13.0 / 21.0, "rational_control"),
    ]


def build_models() -> list[ModelSpec]:
    return [
        ModelSpec("flat_ternary", "Flat Ternary"),
        ModelSpec("torus_single_flow", "Torus Single Flow"),
        ModelSpec("torus_counter_flow", "Torus Counter Flow"),
        ModelSpec("sphere_projected_torus", "Sphere-Projected Torus"),
    ]


def build_conditions() -> list[ObserverCondition]:
    return [
        ObserverCondition(
            window_width=window_width,
            phase=phase,
            beta=beta,
            length=length,
            max_closure_age=max_closure_age,
            memory_capacity=memory_capacity,
        )
        for window_width in WINDOW_WIDTHS
        for phase in PHASES
        for beta in BETAS
        for length in LENGTHS
        for max_closure_age in MAX_CLOSURE_AGES
        for memory_capacity in MEMORY_CAPACITIES
    ]


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
        peaks.append(abs(float(np.dot(centered[:-lag], centered[lag:]) / denom)))
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


def phase_lock_resistance(seq: np.ndarray) -> float:
    mismatch, best_period = approximate_periodicity(seq)
    ac = autocorr_peak(seq)
    spec = spectral_peak(seq)
    approx = 1.0 - mismatch
    period_term = 1.0 / best_period if best_period > 0 else 1.0
    lock_score = float(np.mean([ac, spec, min(approx * period_term * 18.0, 1.0)]))
    return 1.0 - lock_score


def symmetry_balance(seq: np.ndarray) -> float:
    pos = int(np.sum(seq == 1))
    neg = int(np.sum(seq == -1))
    nonzero = pos + neg
    if nonzero == 0:
        return 0.0
    return 1.0 - abs(pos - neg) / nonzero


def density_random_surrogate(seq: np.ndarray) -> np.ndarray:
    values, counts = np.unique(seq, return_counts=True)
    probs = counts / counts.sum()
    return RNG.choice(values, size=len(seq), p=probs).astype(np.int8)


def markov_surrogate(seq: np.ndarray) -> np.ndarray:
    symbols = [-1, 0, 1]
    index = {symbol: idx for idx, symbol in enumerate(symbols)}
    counts = np.ones((3, 3), dtype=float)
    for a, b in zip(seq[:-1], seq[1:]):
        counts[index[int(a)], index[int(b)]] += 1.0
    probs = counts / counts.sum(axis=1, keepdims=True)
    out = np.empty_like(seq)
    out[0] = seq[0]
    for idx in range(1, len(seq)):
        out[idx] = RNG.choice(symbols, p=probs[index[int(out[idx - 1])]])
    return out.astype(np.int8)


def base_center(condition: ObserverCondition) -> np.ndarray:
    n = np.arange(condition.length, dtype=float)
    return wrap01(0.5 + condition.phase + condition.beta * n)


def generate_sequence(
    model: str,
    alpha: float,
    condition: ObserverCondition,
    phase_lag: float = 0.0,
    noise_amp: float = 0.0,
) -> tuple[np.ndarray, dict[str, np.ndarray | float]]:
    n = np.arange(condition.length, dtype=float)
    center = base_center(condition)

    if model == "flat_ternary":
        signal = wrap01(alpha * n + condition.phase + phase_lag)
        if noise_amp > 0.0:
            signal = wrap01(signal + noise_amp * np.sin(2.0 * math.pi * (0.041 * n + alpha * 3.0)))
        signed = wrap_signed(signal - center)
        inner = condition.window_width * 0.20
        outer = condition.window_width * 0.62
        seq = np.zeros(condition.length, dtype=np.int8)
        seq[(signed >= inner) & (signed <= outer)] = 1
        seq[(signed <= -inner) & (signed >= -outer)] = -1
        return seq, {"return_signal": signed, "center_share": float(np.mean(seq == 0))}

    theta = wrap01(alpha * n + condition.phase + phase_lag)
    phi = wrap01((alpha / PHI) * n + 0.5 * condition.phase - phase_lag)
    if model == "torus_counter_flow":
        phi = wrap01(1.0 - phi + 0.17)
    if model == "sphere_projected_torus":
        x = np.cos(2.0 * math.pi * theta) * (1.2 + 0.35 * np.cos(2.0 * math.pi * phi))
        y = np.sin(2.0 * math.pi * theta) * (1.2 + 0.35 * np.cos(2.0 * math.pi * phi))
        z = 0.55 * np.sin(2.0 * math.pi * phi)
        if noise_amp > 0.0:
            z = z + noise_amp * np.sin(2.0 * math.pi * (0.037 * n + alpha * 2.0))
        az = wrap01(np.arctan2(y, x) / (2.0 * math.pi))
        elevation = np.arctan2(z, np.sqrt(x * x + y * y))
        signed = wrap_signed(az - center)
        gate = np.abs(elevation) < (0.48 + condition.window_width)
        inner = condition.window_width * 0.16
        outer = condition.window_width * 0.58
        seq = np.zeros(condition.length, dtype=np.int8)
        seq[gate & (signed >= inner) & (signed <= outer)] = 1
        seq[gate & (signed <= -inner) & (signed >= -outer)] = -1
        return seq, {"return_signal": signed, "center_share": float(np.mean(seq == 0))}

    if noise_amp > 0.0:
        theta = wrap01(theta + noise_amp * np.sin(2.0 * math.pi * (0.031 * n + alpha * 2.2)))
        phi = wrap01(phi + 0.7 * noise_amp * np.cos(2.0 * math.pi * (0.047 * n + alpha * 2.6)))
    readout = 0.58 * np.sin(2.0 * math.pi * theta) + 0.42 * np.sin(2.0 * math.pi * phi)
    signed = wrap_signed(readout * condition.window_width + condition.phase - center)
    inner = condition.window_width * 0.14
    outer = condition.window_width * 0.56
    seq = np.zeros(condition.length, dtype=np.int8)
    seq[(signed >= inner) & (signed <= outer)] = 1
    seq[(signed <= -inner) & (signed >= -outer)] = -1
    return seq, {"return_signal": signed, "center_share": float(np.mean(seq == 0))}


def evaluate_lagged_memory(
    seq: np.ndarray,
    condition: ObserverCondition,
) -> dict[str, float]:
    pending_plus: list[int] = []
    pending_minus: list[int] = []
    write_latencies: list[int] = []
    witness_expired = 0
    writes = 0
    polluted = 0
    release_count = 0
    future_horizon = condition.max_closure_age

    for idx, sym in enumerate(seq):
        pending_plus = [age + 1 for age in pending_plus if age + 1 <= condition.max_closure_age]
        pending_minus = [age + 1 for age in pending_minus if age + 1 <= condition.max_closure_age]
        witness_expired += int(sym == 0 and len(pending_plus) + len(pending_minus) >= condition.memory_capacity)

        if sym == 1:
            if pending_minus:
                latency = min(pending_minus)
                pending_minus.remove(latency)
                write_latencies.append(latency)
                writes += 1
                future = seq[idx + 1 : idx + 1 + future_horizon]
                if np.any(future == -1) and not np.any(future == 1):
                    polluted += 1
            elif len(pending_plus) < condition.memory_capacity:
                pending_plus.append(0)
            else:
                release_count += 1
        elif sym == -1:
            if pending_plus:
                latency = min(pending_plus)
                pending_plus.remove(latency)
                write_latencies.append(latency)
                writes += 1
                future = seq[idx + 1 : idx + 1 + future_horizon]
                if np.any(future == 1) and not np.any(future == -1):
                    polluted += 1
            elif len(pending_minus) < condition.memory_capacity:
                pending_minus.append(0)
            else:
                release_count += 1
        else:
            release_count += 1

    delayed_retention = writes / max(writes + witness_expired + len(pending_plus) + len(pending_minus), 1)
    pollution = polluted / writes if writes else 0.0
    witness_conversion = writes / max(np.sum(seq != 0), 1)
    latency_mean = float(np.mean(write_latencies)) if write_latencies else float(condition.max_closure_age)
    if len(write_latencies) >= 2:
        return_diversity = float(np.std(write_latencies) / (np.mean(write_latencies) + 1e-9))
    else:
        return_diversity = 0.0
    return {
        "write_count": float(writes),
        "release_count": float(release_count),
        "witness_expired": float(witness_expired),
        "delayed_retention": delayed_retention,
        "pollution": pollution,
        "witness_conversion": witness_conversion,
        "mean_closure_latency": latency_mean,
        "return_interval_diversity": return_diversity,
    }


def sequence_base_score(seq: np.ndarray, condition: ObserverCondition) -> dict[str, float]:
    lagged = evaluate_lagged_memory(seq, condition)
    phase_resist = phase_lock_resistance(seq)
    symmetry = symmetry_balance(seq)
    return {
        **lagged,
        "phase_lock_resistance": phase_resist,
        "symmetry_balance": symmetry,
    }


def evaluate_model_sequence(
    model: str,
    alpha: float,
    condition: ObserverCondition,
) -> dict[str, float]:
    seq, diag = generate_sequence(model, alpha, condition)
    shadow_seq, _ = generate_sequence(model, alpha, condition, phase_lag=0.008, noise_amp=0.0015)
    base = sequence_base_score(seq, condition)
    rigidity = 1.0 - float(np.mean(seq != shadow_seq))
    surrogate_core = (
        0.34 * base["phase_lock_resistance"]
        + 0.28 * base["delayed_retention"]
        + 0.20 * (1.0 - base["pollution"])
        + 0.18 * base["witness_conversion"]
    )
    composite = float(
        surrogate_core
        + 0.10 * base["return_interval_diversity"]
        + 0.10 * rigidity
        + 0.05 * base["symmetry_balance"]
    )
    return {
        **base,
        "rigidity_after_perturbation": rigidity,
        "center_share": float(diag["center_share"]),
        "composite_score": composite,
        "surrogate_base_score": surrogate_core,
    }


def summarize_hotspots(
    anchors: list[AnchorSpec],
    models: list[ModelSpec],
    conditions: list[ObserverCondition],
    direct_rows: list[dict],
) -> tuple[list[dict], list[dict]]:
    anchor_rows: list[dict] = []
    surrogate_rows: list[dict] = []
    for anchor in anchors:
        for model in models:
            subset = [row for row in direct_rows if row["anchor"] == anchor.name and row["model"] == model.name]
            best_rows = []
            for condition in conditions:
                condition_rows = [
                    row
                    for row in subset
                    if row["window_width"] == condition.window_width
                    and row["phase"] == condition.phase
                    and row["beta"] == condition.beta
                    and row["length"] == condition.length
                    and row["max_closure_age"] == condition.max_closure_age
                    and row["memory_capacity"] == condition.memory_capacity
                ]
                if condition_rows:
                    best_rows.append(max(condition_rows, key=lambda row: row["composite_score"]))
            if not best_rows:
                continue
            hotspot = float(np.median([row["offset"] for row in best_rows]))
            stability = float(np.mean([abs(row["offset"] - hotspot) <= 0.012 for row in best_rows]))
            reps = []
            real_scores = []
            shuffled_scores = []
            markov_scores = []
            density_scores = []
            for condition in conditions:
                candidates = [
                    row
                    for row in subset
                    if row["window_width"] == condition.window_width
                    and row["phase"] == condition.phase
                    and row["beta"] == condition.beta
                    and row["length"] == condition.length
                    and row["max_closure_age"] == condition.max_closure_age
                    and row["memory_capacity"] == condition.memory_capacity
                ]
                if not candidates:
                    continue
                rep = min(candidates, key=lambda row: abs(row["offset"] - hotspot))
                reps.append(rep)
                alpha = anchor.alpha + rep["offset"]
                seq, _ = generate_sequence(model.name, alpha, condition)
                real_scores.append(rep["surrogate_base_score"])
                shuffled = np.array(seq, copy=True)
                RNG.shuffle(shuffled)
                shuf_base = sequence_base_score(shuffled, condition)
                shuffled_scores.append(
                    0.34 * shuf_base["phase_lock_resistance"]
                    + 0.28 * shuf_base["delayed_retention"]
                    + 0.20 * (1.0 - shuf_base["pollution"])
                    + 0.18 * shuf_base["witness_conversion"]
                )
                markov = markov_surrogate(seq)
                markov_base = sequence_base_score(markov, condition)
                markov_scores.append(
                    0.34 * markov_base["phase_lock_resistance"]
                    + 0.28 * markov_base["delayed_retention"]
                    + 0.20 * (1.0 - markov_base["pollution"])
                    + 0.18 * markov_base["witness_conversion"]
                )
                density = density_random_surrogate(seq)
                density_base = sequence_base_score(density, condition)
                density_scores.append(
                    0.34 * density_base["phase_lock_resistance"]
                    + 0.28 * density_base["delayed_retention"]
                    + 0.20 * (1.0 - density_base["pollution"])
                    + 0.18 * density_base["witness_conversion"]
                )
            surrogate_gap = float(
                np.mean(real_scores)
                - max(np.mean(shuffled_scores), np.mean(markov_scores), np.mean(density_scores))
            )
            surrogate_rows.append(
                {
                    "anchor": anchor.name,
                    "model": model.name,
                    "real_score": float(np.mean(real_scores)),
                    "shuffled_score": float(np.mean(shuffled_scores)),
                    "markov_score": float(np.mean(markov_scores)),
                    "density_score": float(np.mean(density_scores)),
                    "surrogate_gap": surrogate_gap,
                }
            )
            anchor_rows.append(
                {
                    "anchor": anchor.name,
                    "anchor_family": anchor.family,
                    "model": model.name,
                    "global_hotspot_offset": hotspot,
                    "hotspot_stability": stability,
                    "phase_lock_resistance": float(np.mean([row["phase_lock_resistance"] for row in reps])),
                    "delayed_retention": float(np.mean([row["delayed_retention"] for row in reps])),
                    "pollution": float(np.mean([row["pollution"] for row in reps])),
                    "witness_conversion": float(np.mean([row["witness_conversion"] for row in reps])),
                    "mean_closure_latency": float(np.mean([row["mean_closure_latency"] for row in reps])),
                    "return_interval_diversity": float(np.mean([row["return_interval_diversity"] for row in reps])),
                    "rigidity_after_perturbation": float(np.mean([row["rigidity_after_perturbation"] for row in reps])),
                    "center_share": float(np.mean([row["center_share"] for row in reps])),
                    "composite_score": float(np.mean([row["composite_score"] for row in reps])),
                    "surrogate_gap": surrogate_gap,
                }
            )
    return anchor_rows, surrogate_rows


def plot_model_summary(anchor_rows: list[dict], path: Path) -> None:
    models = sorted({row["model"] for row in anchor_rows})
    aggregates = []
    for model in models:
        subset = [row for row in anchor_rows if row["model"] == model]
        aggregates.append(
            (
                model,
                float(np.mean([row["composite_score"] for row in subset])),
                float(np.mean([row["hotspot_stability"] for row in subset])),
                float(np.mean([row["surrogate_gap"] for row in subset])),
            )
        )
    x = np.arange(len(models))
    width = 0.24
    plt.figure(figsize=(10, 5))
    plt.bar(x - width, [item[1] for item in aggregates], width=width, label="mean composite")
    plt.bar(x, [item[2] for item in aggregates], width=width, label="mean stability")
    plt.bar(x + width, [item[3] for item in aggregates], width=width, label="mean surrogate gap")
    plt.xticks(x, models, rotation=20)
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.title("v8 model summary")
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_anchor_model_heatmap(anchor_rows: list[dict], metric: str, path: Path, title: str) -> None:
    anchors = sorted({row["anchor"] for row in anchor_rows})
    models = sorted({row["model"] for row in anchor_rows})
    matrix = np.zeros((len(anchors), len(models)))
    for i, anchor in enumerate(anchors):
        for j, model in enumerate(models):
            row = next(row for row in anchor_rows if row["anchor"] == anchor and row["model"] == model)
            matrix[i, j] = row[metric]
    plt.figure(figsize=(8, 6))
    plt.imshow(matrix, aspect="auto", cmap="viridis")
    plt.colorbar()
    plt.xticks(np.arange(len(models)), models, rotation=20)
    plt.yticks(np.arange(len(anchors)), anchors)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def build_report(anchor_rows: list[dict]) -> str:
    models = sorted({row["model"] for row in anchor_rows})
    model_means = {}
    for model in models:
        subset = [row for row in anchor_rows if row["model"] == model]
        model_means[model] = {
            "composite": float(np.mean([row["composite_score"] for row in subset])),
            "stability": float(np.mean([row["hotspot_stability"] for row in subset])),
            "surrogate_gap": float(np.mean([row["surrogate_gap"] for row in subset])),
        }
    best_model = max(models, key=lambda model: model_means[model]["composite"])
    torus_rows = [row for row in anchor_rows if row["model"] == "sphere_projected_torus"]
    golden = next(row for row in torus_rows if row["anchor"] == "golden")
    golden_rank = next(
        idx
        for idx, row in enumerate(sorted(torus_rows, key=lambda row: row["composite_score"], reverse=True), start=1)
        if row["anchor"] == "golden"
    )
    torus_beats_flat = (
        model_means["sphere_projected_torus"]["composite"] > model_means["flat_ternary"]["composite"]
        and model_means["sphere_projected_torus"]["surrogate_gap"] > 0.0
    )
    if torus_beats_flat:
        verdict = "Promising: the torus/sphere delayed-memory model beats the flat baseline on average."
    else:
        verdict = "Mixed/negative: closed-surface delayed memory is interesting, but it does not beat the simpler flat ternary baseline yet."
    top_torus = max(torus_rows, key=lambda row: row["composite_score"])
    return f"""# Golden Zipper v8 - Torus Lagged Memory

Toy telemetry only. Not physics evidence. Not proof of GHP. Not proof that phi is fundamental. Not write-law closure.

## Executive Summary

{verdict}

This run compared:
- `flat_ternary`
- `torus_single_flow`
- `torus_counter_flow`
- `sphere_projected_torus`

All four used the same lagged witness-to-write rule, so the comparison is about geometry, not just scoring.

## Model Means

| Model | Mean composite | Mean hotspot stability | Mean surrogate gap |
|---|---:|---:|---:|
| flat_ternary | {model_means['flat_ternary']['composite']:.3f} | {model_means['flat_ternary']['stability']:.3f} | {model_means['flat_ternary']['surrogate_gap']:.3f} |
| torus_single_flow | {model_means['torus_single_flow']['composite']:.3f} | {model_means['torus_single_flow']['stability']:.3f} | {model_means['torus_single_flow']['surrogate_gap']:.3f} |
| torus_counter_flow | {model_means['torus_counter_flow']['composite']:.3f} | {model_means['torus_counter_flow']['stability']:.3f} | {model_means['torus_counter_flow']['surrogate_gap']:.3f} |
| sphere_projected_torus | {model_means['sphere_projected_torus']['composite']:.3f} | {model_means['sphere_projected_torus']['stability']:.3f} | {model_means['sphere_projected_torus']['surrogate_gap']:.3f} |

Best model by mean composite: `{best_model}`.

## Sphere/torus Read

- Top anchor under `sphere_projected_torus`: `{top_torus['anchor']}` with composite `{top_torus['composite_score']:.3f}`
- Golden rank under `sphere_projected_torus`: `{golden_rank}` / `{len(torus_rows)}`
- Golden torus composite: `{golden['composite_score']:.3f}`
- Golden hotspot stability: `{golden['hotspot_stability']:.3f}`
- Golden surrogate gap: `{golden['surrogate_gap']:.3f}`
- Golden mean closure latency: `{golden['mean_closure_latency']:.3f}`

## What This Supports

- Delayed witness-to-write rules fit the observer intuition better than instant closure.
- Closed-surface return geometry is worth testing directly rather than compressing everything into a flat line.

## What This Does Not Support

- does not prove GHP
- does not prove torus/sphere geometry is the correct physical model
- does not prove phi uniquely organizes memory
- does not justify hardening the paper or master

## Recommendation

Use this as a geometry diagnostic. If a torus/sphere mode becomes competitive, the next pass should tighten around its winning anchors and vary only the return geometry, not everything at once.
"""


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    models = build_models()
    conditions = build_conditions()

    direct_rows: list[dict] = []
    total_groups = len(anchors) * len(models)
    group_idx = 0
    for anchor in anchors:
        for model in models:
            group_idx += 1
            print(f"scanning {group_idx}/{total_groups}: {anchor.name} / {model.name}")
            for condition in conditions:
                for offset in OFFSET_GRID:
                    alpha = anchor.alpha + float(offset)
                    if not (0.0 < alpha < 1.0):
                        continue
                    metrics = evaluate_model_sequence(model.name, alpha, condition)
                    direct_rows.append(
                        {
                            "anchor": anchor.name,
                            "anchor_family": anchor.family,
                            "model": model.name,
                            "model_label": model.label,
                            "alpha": alpha,
                            "offset": float(offset),
                            "window_width": condition.window_width,
                            "phase": condition.phase,
                            "beta": condition.beta,
                            "length": condition.length,
                            "max_closure_age": condition.max_closure_age,
                            "memory_capacity": condition.memory_capacity,
                            **metrics,
                        }
                    )

    anchor_rows, surrogate_rows = summarize_hotspots(anchors, models, conditions, direct_rows)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(anchor_rows, OUT / "anchor_summary.csv")
    write_csv(surrogate_rows, OUT / "surrogate_summary.csv")
    plot_model_summary(anchor_rows, OUT / "model_summary.png")
    plot_anchor_model_heatmap(anchor_rows, "composite_score", OUT / "anchor_model_composite.png", "Anchor/model composite")
    plot_anchor_model_heatmap(anchor_rows, "surrogate_gap", OUT / "anchor_model_surrogates.png", "Anchor/model surrogate gap")
    report = build_report(anchor_rows)
    write_text(OUT / "report.md", report)

    torus_rows = [row for row in anchor_rows if row["model"] == "sphere_projected_torus"]
    golden = next(row for row in torus_rows if row["anchor"] == "golden")
    best_model = max(
        sorted({row["model"] for row in anchor_rows}),
        key=lambda name: np.mean([row["composite_score"] for row in anchor_rows if row["model"] == name]),
    )
    print(f"files created: {OUT}")
    print(f"best model: {best_model}")
    print(
        "golden torus rank: "
        f"{sorted(torus_rows, key=lambda row: row['composite_score'], reverse=True).index(golden) + 1}"
    )
    print(f"golden torus composite: {golden['composite_score']:.3f}")
    print(f"golden torus stability: {golden['hotspot_stability']:.3f}")


if __name__ == "__main__":
    main()
