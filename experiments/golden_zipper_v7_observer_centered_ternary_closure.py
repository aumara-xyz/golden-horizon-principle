#!/usr/bin/env python3
"""v7 observer-centered ternary closure toy for Golden Zipper."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v7_outputs"

SEED = 20260517
RNG = np.random.default_rng(SEED)

OFFSET_GRID = np.arange(-0.06, 0.0601, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
PHASES = [0.0, 0.13]
BETAS = [0.0, 0.011]
LENGTHS = [4096]


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


def build_conditions() -> list[ObserverCondition]:
    return [
        ObserverCondition(window_width=window_width, phase=phase, beta=beta, length=length)
        for window_width in WINDOW_WIDTHS
        for phase in PHASES
        for beta in BETAS
        for length in LENGTHS
    ]


def build_models() -> list[ModelSpec]:
    return [
        ModelSpec("binary_baseline", "Binary Window"),
        ModelSpec("ternary_baseline", "Signed Ternary"),
        ModelSpec("observer_centered_closure", "Observer-Centered Closure"),
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


def delayed_retention(seq: np.ndarray, horizon: int = 8) -> float:
    kept = 0
    missed = 0
    for idx in np.where(seq == 0)[0]:
        window = seq[idx + 1 : idx + 1 + horizon]
        pos_hits = np.where(window == 1)[0]
        neg_hits = np.where(window == -1)[0]
        pos_first = pos_hits[0] if len(pos_hits) else None
        neg_first = neg_hits[0] if len(neg_hits) else None
        if pos_first is not None and (neg_first is None or pos_first < neg_first):
            kept += 1
        else:
            missed += 1
    total = kept + missed
    return kept / total if total else 0.0


def pollution_rate(seq: np.ndarray, horizon: int = 8) -> float:
    polluted = 0
    total = 0
    for idx in np.where(seq == 1)[0]:
        total += 1
        window = seq[idx + 1 : idx + 1 + horizon]
        pos_hits = np.where(window == 1)[0]
        neg_hits = np.where(window == -1)[0]
        pos_first = pos_hits[0] if len(pos_hits) else None
        neg_first = neg_hits[0] if len(neg_hits) else None
        if neg_first is not None and (pos_first is None or neg_first < pos_first):
            polluted += 1
    return polluted / total if total else 0.0


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


def base_series(alpha: float, condition: ObserverCondition, phase_lag: float, noise_amp: float) -> tuple[np.ndarray, np.ndarray]:
    n = np.arange(condition.length, dtype=float)
    center = wrap01(0.5 + condition.phase + condition.beta * n)
    signal = wrap01(alpha * n + condition.phase + phase_lag)
    if noise_amp > 0.0:
        signal = wrap01(signal + noise_amp * np.sin(2.0 * math.pi * (0.041 * n + alpha * 3.0)))
    return center, signal


def generate_binary_baseline(
    alpha: float,
    condition: ObserverCondition,
    phase_lag: float = 0.0,
    noise_amp: float = 0.0,
) -> tuple[np.ndarray, dict[str, float]]:
    center, signal = base_series(alpha, condition, phase_lag, noise_amp)
    dist = np.abs(wrap_signed(signal - center))
    inner = condition.window_width * 0.50
    outer = condition.window_width * 0.72
    seq = np.full(condition.length, -1, dtype=np.int8)
    seq[dist <= inner] = 1
    seq[(dist > inner) & (dist <= outer)] = 0
    diag = {
        "center_share": float(np.mean(seq == 0)),
        "closure_balance": 0.0,
    }
    return seq, diag


def generate_signed_ternary(
    alpha: float,
    condition: ObserverCondition,
    phase_lag: float = 0.0,
    noise_amp: float = 0.0,
) -> tuple[np.ndarray, dict[str, float]]:
    center, signal = base_series(alpha, condition, phase_lag, noise_amp)
    signed_dist = wrap_signed(signal - center)
    inner = condition.window_width * 0.18
    outer = condition.window_width * 0.60
    seq = np.zeros(condition.length, dtype=np.int8)
    seq[(signed_dist >= inner) & (signed_dist <= outer)] = 1
    seq[(signed_dist <= -inner) & (signed_dist >= -outer)] = -1
    active = seq != 0
    balance = symmetry_balance(seq)
    diag = {
        "center_share": float(np.mean(seq == 0)),
        "closure_balance": balance if np.any(active) else 0.0,
    }
    return seq, diag


def generate_observer_centered_closure(
    alpha: float,
    condition: ObserverCondition,
    phase_lag: float = 0.0,
    noise_amp: float = 0.0,
) -> tuple[np.ndarray, dict[str, float]]:
    n = np.arange(condition.length, dtype=float)
    center = np.full(condition.length, 0.5 + condition.phase, dtype=float)
    plus = wrap01(center + alpha * n + phase_lag)
    minus = wrap01(center - alpha * n + condition.beta * n - phase_lag)
    if noise_amp > 0.0:
        plus = wrap01(plus + noise_amp * np.sin(2.0 * math.pi * (0.031 * n + alpha * 2.0)))
        minus = wrap01(minus + 0.7 * noise_amp * np.cos(2.0 * math.pi * (0.047 * n + alpha * 2.7)))
    d_plus = wrap_signed(plus - center)
    d_minus = wrap_signed(minus - center)
    radius = condition.window_width * 0.50
    balance_tol = condition.window_width * 0.18
    mean_abs = 0.5 * (np.abs(d_plus) + np.abs(d_minus))
    balance_err = np.abs(np.abs(d_plus) - np.abs(d_minus))
    opposite = ((d_plus >= 0) & (d_minus <= 0)) | ((d_plus <= 0) & (d_minus >= 0))
    near = (np.abs(d_plus) <= radius) & (np.abs(d_minus) <= radius)
    witness = opposite & near & (balance_err <= 1.8 * balance_tol)
    write = witness & (balance_err <= balance_tol) & (mean_abs <= 0.72 * radius)
    seq = np.full(condition.length, -1, dtype=np.int8)
    seq[witness] = 0
    seq[write] = 1
    closure_balance = float(np.mean(1.0 - np.clip(balance_err[opposite & near] / max(radius, 1e-9), 0.0, 1.0))) if np.any(opposite & near) else 0.0
    diag = {
        "center_share": float(np.mean(seq == 0)),
        "closure_balance": closure_balance,
    }
    return seq, diag


def generate_sequence(
    model: str,
    alpha: float,
    condition: ObserverCondition,
    phase_lag: float = 0.0,
    noise_amp: float = 0.0,
) -> tuple[np.ndarray, dict[str, float]]:
    if model == "binary_baseline":
        return generate_binary_baseline(alpha, condition, phase_lag, noise_amp)
    if model == "ternary_baseline":
        return generate_signed_ternary(alpha, condition, phase_lag, noise_amp)
    return generate_observer_centered_closure(alpha, condition, phase_lag, noise_amp)


def sequence_score(seq: np.ndarray) -> dict[str, float]:
    phase_resist = phase_lock_resistance(seq)
    delayed = delayed_retention(seq)
    pollution = pollution_rate(seq)
    symmetry = symmetry_balance(seq)
    return {
        "phase_lock_resistance": phase_resist,
        "delayed_retention": delayed,
        "pollution": pollution,
        "symmetry_balance": symmetry,
    }


def evaluate_model_sequence(
    model: str,
    alpha: float,
    condition: ObserverCondition,
) -> dict[str, float]:
    seq, diag = generate_sequence(model, alpha, condition)
    shadow_seq, _ = generate_sequence(model, alpha, condition, phase_lag=0.009, noise_amp=0.0016)
    base = sequence_score(seq)
    rigidity = 1.0 - float(np.mean(seq != shadow_seq))
    composite = float(
        0.30 * base["phase_lock_resistance"]
        + 0.28 * base["delayed_retention"]
        + 0.22 * (1.0 - base["pollution"])
        + 0.20 * rigidity
    )
    surrogate_seq_score = 0.40 * base["phase_lock_resistance"] + 0.35 * base["delayed_retention"] + 0.25 * (1.0 - base["pollution"])
    return {
        **base,
        "rigidity_after_zipping": rigidity,
        "center_share": diag["center_share"],
        "closure_balance": diag["closure_balance"],
        "composite_score": composite,
        "surrogate_base_score": surrogate_seq_score,
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
                ]
                if condition_rows:
                    best_rows.append(max(condition_rows, key=lambda row: row["composite_score"]))
            if not best_rows:
                continue
            hotspot = float(np.median([row["offset"] for row in best_rows]))
            stability = float(np.mean([abs(row["offset"] - hotspot) <= 0.012 for row in best_rows]))
            reps = []
            real_surrogate_scores = []
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
                ]
                if not candidates:
                    continue
                rep = min(candidates, key=lambda row: abs(row["offset"] - hotspot))
                reps.append(rep)
                alpha = anchor.alpha + rep["offset"]
                seq, _ = generate_sequence(model.name, alpha, condition)
                real_surrogate_scores.append(rep["surrogate_base_score"])
                shuffled = np.array(seq, copy=True)
                RNG.shuffle(shuffled)
                shuffled_base = sequence_score(shuffled)
                shuffled_scores.append(
                    0.40 * shuffled_base["phase_lock_resistance"]
                    + 0.35 * shuffled_base["delayed_retention"]
                    + 0.25 * (1.0 - shuffled_base["pollution"])
                )
                markov = markov_surrogate(seq)
                markov_base = sequence_score(markov)
                markov_scores.append(
                    0.40 * markov_base["phase_lock_resistance"]
                    + 0.35 * markov_base["delayed_retention"]
                    + 0.25 * (1.0 - markov_base["pollution"])
                )
                density = density_random_surrogate(seq)
                density_base = sequence_score(density)
                density_scores.append(
                    0.40 * density_base["phase_lock_resistance"]
                    + 0.35 * density_base["delayed_retention"]
                    + 0.25 * (1.0 - density_base["pollution"])
                )
            surrogate_gap = float(
                np.mean(real_surrogate_scores)
                - max(np.mean(shuffled_scores), np.mean(markov_scores), np.mean(density_scores))
            )
            surrogate_rows.append(
                {
                    "anchor": anchor.name,
                    "model": model.name,
                    "real_score": float(np.mean(real_surrogate_scores)),
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
                    "rigidity_after_zipping": float(np.mean([row["rigidity_after_zipping"] for row in reps])),
                    "center_share": float(np.mean([row["center_share"] for row in reps])),
                    "closure_balance": float(np.mean([row["closure_balance"] for row in reps])),
                    "composite_score": float(np.mean([row["composite_score"] for row in reps])),
                    "surrogate_gap": surrogate_gap,
                }
            )
    return anchor_rows, surrogate_rows


def plot_model_summary(anchor_rows: list[dict], path: Path) -> None:
    models = sorted({row["model"] for row in anchor_rows})
    metrics = []
    for model in models:
        subset = [row for row in anchor_rows if row["model"] == model]
        metrics.append(
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
    plt.bar(x - width, [item[1] for item in metrics], width=width, label="mean composite")
    plt.bar(x, [item[2] for item in metrics], width=width, label="mean hotspot stability")
    plt.bar(x + width, [item[3] for item in metrics], width=width, label="mean surrogate gap")
    plt.xticks(x, models, rotation=20)
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.ylim(min(-0.05, min(item[3] for item in metrics) - 0.05), 1.0)
    plt.title("Model-level summary")
    plt.legend()
    plt.tight_layout()
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
    closure_rows = [row for row in anchor_rows if row["model"] == "observer_centered_closure"]
    golden_closure = next(row for row in closure_rows if row["anchor"] == "golden")
    closure_rank = sorted(closure_rows, key=lambda row: row["composite_score"], reverse=True)
    golden_rank = next(idx for idx, row in enumerate(closure_rank, start=1) if row["anchor"] == "golden")
    observer_beats_baselines = (
        model_means["observer_centered_closure"]["composite"] > model_means["binary_baseline"]["composite"]
        and model_means["observer_centered_closure"]["composite"] > model_means["ternary_baseline"]["composite"]
        and model_means["observer_centered_closure"]["surrogate_gap"] > 0.0
    )
    if observer_beats_baselines:
        verdict = "Promising but still toy-only: observer-centered closure beats the baselines on average."
    else:
        verdict = "Mixed/negative: the observer-centered closure idea is more faithful conceptually, but it does not decisively beat the baselines yet."
    top_closure = max(closure_rows, key=lambda row: row["composite_score"])
    return f"""# Golden Zipper v7 - Observer-Centered Ternary Closure

Toy telemetry only. Not physics evidence. Not proof of GHP. Not proof that phi is fundamental. Not write-law closure.

## Executive Summary

{verdict}

This run tested three models:
- `binary_baseline`: single-window hit/miss coding with a thin witness band
- `ternary_baseline`: signed ternary coding around an observer-centered window
- `observer_centered_closure`: `0` as witness center, with `+1` and `-1` treated as opposite strands that must close around the observer to count as a write

## Model Means

| Model | Mean composite | Mean hotspot stability | Mean surrogate gap |
|---|---:|---:|---:|
| binary_baseline | {model_means['binary_baseline']['composite']:.3f} | {model_means['binary_baseline']['stability']:.3f} | {model_means['binary_baseline']['surrogate_gap']:.3f} |
| ternary_baseline | {model_means['ternary_baseline']['composite']:.3f} | {model_means['ternary_baseline']['stability']:.3f} | {model_means['ternary_baseline']['surrogate_gap']:.3f} |
| observer_centered_closure | {model_means['observer_centered_closure']['composite']:.3f} | {model_means['observer_centered_closure']['stability']:.3f} | {model_means['observer_centered_closure']['surrogate_gap']:.3f} |

Best model by mean composite: `{best_model}`.

## Observer-Centered Closure Read

- Top anchor under observer-centered closure: `{top_closure['anchor']}` with composite `{top_closure['composite_score']:.3f}`
- Golden rank under observer-centered closure: `{golden_rank}` / `{len(closure_rows)}`
- Golden closure composite: `{golden_closure['composite_score']:.3f}`
- Golden closure hotspot stability: `{golden_closure['hotspot_stability']:.3f}`
- Golden closure surrogate gap: `{golden_closure['surrogate_gap']:.3f}`

## What This Supports

- Treating `0` as an observer/witness center is a better-posed toy than flattening everything into a binary memory string.
- The real question looks more and more like a boundary-closure problem, not a raw phi-sequence problem.

## What This Does Not Support

- does not prove GHP
- does not prove phi uniquely optimizes writable memory
- does not prove observer-centered closure is the right physical abstraction
- does not prove a ternary write-law
- does not justify changing the core paper or master

## Recommendation

Stay in experiment mode. If observer-centered closure is competitive but not dominant, the next right move is a narrower v7b around the winning anchors with explicit pair-closure geometry and a stronger surrogate panel.
"""


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    models = build_models()
    conditions = build_conditions()

    direct_rows: list[dict] = []
    for anchor in anchors:
        for model in models:
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
                            **metrics,
                        }
                    )

    anchor_rows, surrogate_rows = summarize_hotspots(anchors, models, conditions, direct_rows)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(anchor_rows, OUT / "anchor_summary.csv")
    write_csv(surrogate_rows, OUT / "surrogate_summary.csv")
    plot_model_summary(anchor_rows, OUT / "model_summary.png")
    plot_anchor_model_heatmap(anchor_rows, "composite_score", OUT / "anchor_model_composite.png", "Anchor/model composite score")
    plot_anchor_model_heatmap(anchor_rows, "hotspot_stability", OUT / "anchor_model_stability.png", "Anchor/model hotspot stability")
    plot_anchor_model_heatmap(anchor_rows, "surrogate_gap", OUT / "anchor_model_surrogates.png", "Anchor/model surrogate gap")
    report = build_report(anchor_rows)
    write_text(OUT / "report.md", report)

    closure_rows = [row for row in anchor_rows if row["model"] == "observer_centered_closure"]
    golden = next(row for row in closure_rows if row["anchor"] == "golden")
    models = sorted(
        {row["model"] for row in anchor_rows},
        key=lambda name: np.mean([row["composite_score"] for row in anchor_rows if row["model"] == name]),
        reverse=True,
    )
    print(f"files created: {OUT}")
    print(f"best model: {models[0]}")
    print(f"golden observer-centered rank: {sorted(closure_rows, key=lambda row: row['composite_score'], reverse=True).index(golden) + 1}")
    print(f"golden observer-centered composite: {golden['composite_score']:.3f}")
    print(f"golden observer-centered stability: {golden['hotspot_stability']:.3f}")


if __name__ == "__main__":
    main()
