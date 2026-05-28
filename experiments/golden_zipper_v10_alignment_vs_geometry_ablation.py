#!/usr/bin/env python3
"""v10 ablation: delayed two-light alignment versus geometry."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v10_outputs"

SEED = 20260517
RNG = np.random.default_rng(SEED)

OFFSET_GRID = np.arange(-0.048, 0.0481, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
PHASES = [0.0]
BETAS = [0.0, 0.011]
LENGTHS = [4096]
MAX_ALIGNMENT_AGES = [4, 8, 13]
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
    max_alignment_age: int
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
    return [
        AnchorSpec("golden", 1.0 / PHI, "phi_anchor"),
        AnchorSpec("silver", math.sqrt(2.0) - 1.0, "metallic_anchor"),
        AnchorSpec("noble_a", continued_fraction_value([2, 3], tail_ones=18), "noble_anchor"),
        AnchorSpec("bounded_probe", continued_fraction_value([2, 1, 2, 1, 2, 1], tail_ones=12), "bounded_anchor"),
        AnchorSpec("pi_mod1", math.pi % 1.0, "constant_control"),
        AnchorSpec("fib_13_21", 13.0 / 21.0, "rational_control"),
    ]


def build_models() -> list[ModelSpec]:
    return [
        ModelSpec("one_light_recurrence", "One Light"),
        ModelSpec("two_light_plain", "Two Light Plain"),
        ModelSpec("two_light_contact_ring", "Two Light Contact Ring"),
        ModelSpec("two_light_no_ring", "Two Light No Ring"),
        ModelSpec("two_light_random_projection", "Two Light Random Projection"),
        ModelSpec("two_light_shuffled_time", "Two Light Shuffled Time"),
    ]


def build_conditions() -> list[ObserverCondition]:
    return [
        ObserverCondition(
            window_width=window_width,
            phase=phase,
            beta=beta,
            length=length,
            max_alignment_age=max_alignment_age,
            memory_capacity=memory_capacity,
        )
        for window_width in WINDOW_WIDTHS
        for phase in PHASES
        for beta in BETAS
        for length in LENGTHS
        for max_alignment_age in MAX_ALIGNMENT_AGES
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


def observer_center(condition: ObserverCondition) -> np.ndarray:
    n = np.arange(condition.length, dtype=float)
    return wrap01(0.5 + condition.phase + condition.beta * n)


def sphere_projection(theta: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.cos(2.0 * math.pi * theta) * np.cos(math.pi * (phi - 0.5))
    y = np.sin(2.0 * math.pi * theta) * np.cos(math.pi * (phi - 0.5))
    z = np.sin(math.pi * (phi - 0.5))
    azimuth = wrap01(np.arctan2(y, x) / (2.0 * math.pi))
    elevation = np.arctan2(z, np.sqrt(x * x + y * y))
    return azimuth, elevation


def build_lights(model: str, alpha: float, condition: ObserverCondition) -> dict[str, np.ndarray]:
    n = np.arange(condition.length, dtype=float)
    theta1 = wrap01(alpha * n + condition.phase)
    phi1 = wrap01((alpha / PHI) * n + 0.3 * condition.phase)
    theta2 = wrap01((alpha + condition.beta + 0.0618) * n + 0.17)
    phi2 = wrap01((alpha / (PHI * PHI) + 0.13) * n + 0.41)

    if model == "one_light_recurrence":
        theta2 = theta1.copy()
        phi2 = phi1.copy()
    elif model == "two_light_random_projection":
        theta2 = wrap01(RNG.random(condition.length))
        phi2 = wrap01(RNG.random(condition.length))
    elif model == "two_light_shuffled_time":
        theta2 = np.array(theta2, copy=True)
        phi2 = np.array(phi2, copy=True)
        RNG.shuffle(theta2)
        RNG.shuffle(phi2)
    elif model == "two_light_contact_ring":
        theta2 = wrap01(1.0 - theta1 + 0.19)
        phi2 = wrap01(1.0 - phi1 + 0.07)

    az1, el1 = sphere_projection(theta1, phi1)
    az2, el2 = sphere_projection(theta2, phi2)
    return {"az1": az1, "el1": el1, "az2": az2, "el2": el2}


def build_sequence(model: str, alpha: float, condition: ObserverCondition) -> tuple[np.ndarray, dict[str, float]]:
    center = observer_center(condition)
    lights = build_lights(model, alpha, condition)
    az1 = lights["az1"]
    az2 = lights["az2"]
    el1 = lights["el1"]
    el2 = lights["el2"]

    signed1 = wrap_signed(az1 - center)
    signed2 = wrap_signed(az2 - center)
    alignment = np.abs(wrap_signed(az1 - az2))
    contact_signal = np.abs(el1 - el2)
    contact_ring = np.abs(0.5 * (el1 + el2)) < (0.34 + 0.5 * condition.window_width)

    seq = np.full(condition.length, -1, dtype=np.int8)
    if model == "one_light_recurrence":
        near = np.abs(signed1) < (0.54 * condition.window_width)
        seq[near] = 0
        seq[near & (np.abs(signed1) < 0.22 * condition.window_width)] = 1
    else:
        near_both = (np.abs(signed1) < 0.58 * condition.window_width) & (np.abs(signed2) < 0.58 * condition.window_width)
        witness = near_both & (alignment < 0.34 * condition.window_width)
        if model == "two_light_contact_ring":
            witness = witness & contact_ring
            write = witness & (alignment < 0.14 * condition.window_width) & (contact_signal < 0.28 + 0.4 * condition.window_width)
        elif model == "two_light_no_ring":
            write = witness & (alignment < 0.14 * condition.window_width)
        else:
            write = witness & (alignment < 0.14 * condition.window_width)
        seq[witness] = 0
        seq[write] = 1

    return seq, {
        "contact_ring_rate": float(np.mean(contact_ring)),
        "center_share": float(np.mean(seq == 0)),
    }


def evaluate_alignment_memory(seq: np.ndarray, condition: ObserverCondition) -> dict[str, float]:
    pending = 0
    pending_age = 0
    writes = 0
    witness_expired = 0
    release_count = 0
    polluted = 0
    latencies: list[int] = []

    for idx, sym in enumerate(seq):
        if pending:
            pending_age += 1
            if pending_age > condition.max_alignment_age:
                witness_expired += 1
                pending = 0
                pending_age = 0

        if sym == 0:
            if not pending:
                pending = 1
                pending_age = 0
            else:
                release_count += 1
        elif sym == 1:
            if pending:
                writes += 1
                latencies.append(pending_age)
                future = seq[idx + 1 : idx + 1 + condition.max_alignment_age]
                if np.any(future == -1):
                    polluted += 1
                pending = 0
                pending_age = 0
            else:
                release_count += 1
        else:
            release_count += 1

    delayed_retention = writes / max(writes + witness_expired, 1)
    witness_conversion = writes / max(np.sum(seq >= 0), 1)
    pollution = polluted / writes if writes else 0.0
    mean_latency = float(np.mean(latencies)) if latencies else float(condition.max_alignment_age)
    interval_diversity = float(np.std(latencies) / (np.mean(latencies) + 1e-9)) if len(latencies) >= 2 else 0.0
    return {
        "write_count": float(writes),
        "witness_expired": float(witness_expired),
        "release_count": float(release_count),
        "delayed_retention": delayed_retention,
        "witness_conversion": witness_conversion,
        "pollution": pollution,
        "mean_alignment_latency": mean_latency,
        "return_interval_diversity": interval_diversity,
    }


def sequence_base_score(seq: np.ndarray, condition: ObserverCondition) -> dict[str, float]:
    memory = evaluate_alignment_memory(seq, condition)
    phase_resist = phase_lock_resistance(seq)
    return {**memory, "phase_lock_resistance": phase_resist}


def evaluate_model_sequence(model: str, alpha: float, condition: ObserverCondition) -> dict[str, float]:
    seq, diag = build_sequence(model, alpha, condition)
    shadow_seq, _ = build_sequence(model, alpha + 0.004, condition)
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
        + 0.08 * rigidity
        + 0.08 * diag["contact_ring_rate"]
    )
    return {
        **base,
        "contact_ring_rate": diag["contact_ring_rate"],
        "center_share": diag["center_share"],
        "rigidity_after_perturbation": rigidity,
        "composite_score": composite,
        "surrogate_base_score": surrogate_core,
    }


def summarize_results(
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
                    and row["max_alignment_age"] == condition.max_alignment_age
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
                    and row["max_alignment_age"] == condition.max_alignment_age
                    and row["memory_capacity"] == condition.memory_capacity
                ]
                if not candidates:
                    continue
                rep = min(candidates, key=lambda row: abs(row["offset"] - hotspot))
                reps.append(rep)
                alpha = anchor.alpha + rep["offset"]
                seq, _ = build_sequence(model.name, alpha, condition)
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
                    "mean_alignment_latency": float(np.mean([row["mean_alignment_latency"] for row in reps])),
                    "contact_ring_rate": float(np.mean([row["contact_ring_rate"] for row in reps])),
                    "rigidity_after_perturbation": float(np.mean([row["rigidity_after_perturbation"] for row in reps])),
                    "composite_score": float(np.mean([row["composite_score"] for row in reps])),
                    "surrogate_gap": surrogate_gap,
                }
            )
    return anchor_rows, surrogate_rows


def plot_model_summary(anchor_rows: list[dict], path: Path) -> None:
    models = sorted({row["model"] for row in anchor_rows})
    values = []
    for model in models:
        subset = [row for row in anchor_rows if row["model"] == model]
        values.append(
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
    plt.bar(x - width, [v[1] for v in values], width=width, label="mean composite")
    plt.bar(x, [v[2] for v in values], width=width, label="mean stability")
    plt.bar(x + width, [v[3] for v in values], width=width, label="mean surrogate gap")
    plt.xticks(x, models, rotation=20)
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.tight_layout()
    plt.legend()
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
    align_rows = [row for row in anchor_rows if row["model"] == "two_light_plain"]
    contact_rows = [row for row in anchor_rows if row["model"] == "two_light_contact_ring"]
    golden_plain = next(row for row in align_rows if row["anchor"] == "golden")
    golden_contact = next(row for row in contact_rows if row["anchor"] == "golden")
    if (
        model_means["two_light_plain"]["surrogate_gap"] > model_means["two_light_contact_ring"]["surrogate_gap"]
        and model_means["two_light_plain"]["surrogate_gap"] > model_means["two_light_random_projection"]["surrogate_gap"]
    ):
        verdict = "Alignment itself looks stronger than the contact-ring geometry."
    elif model_means["two_light_contact_ring"]["composite"] > model_means["two_light_plain"]["composite"]:
        verdict = "The contact ring adds some value, but the null panel is still too competitive."
    else:
        verdict = "The geometry embellishment is not buying enough yet; the core effect is still mostly in the alignment rule."
    return f"""# Golden Zipper v10 - Alignment vs Geometry Ablation

Toy telemetry only. Not physics evidence. Not proof of GHP.

## Executive Summary

{verdict}

## Model Means

| Model | Mean composite | Mean hotspot stability | Mean surrogate gap |
|---|---:|---:|---:|
| one_light_recurrence | {model_means['one_light_recurrence']['composite']:.3f} | {model_means['one_light_recurrence']['stability']:.3f} | {model_means['one_light_recurrence']['surrogate_gap']:.3f} |
| two_light_plain | {model_means['two_light_plain']['composite']:.3f} | {model_means['two_light_plain']['stability']:.3f} | {model_means['two_light_plain']['surrogate_gap']:.3f} |
| two_light_contact_ring | {model_means['two_light_contact_ring']['composite']:.3f} | {model_means['two_light_contact_ring']['stability']:.3f} | {model_means['two_light_contact_ring']['surrogate_gap']:.3f} |
| two_light_no_ring | {model_means['two_light_no_ring']['composite']:.3f} | {model_means['two_light_no_ring']['stability']:.3f} | {model_means['two_light_no_ring']['surrogate_gap']:.3f} |
| two_light_random_projection | {model_means['two_light_random_projection']['composite']:.3f} | {model_means['two_light_random_projection']['stability']:.3f} | {model_means['two_light_random_projection']['surrogate_gap']:.3f} |
| two_light_shuffled_time | {model_means['two_light_shuffled_time']['composite']:.3f} | {model_means['two_light_shuffled_time']['stability']:.3f} | {model_means['two_light_shuffled_time']['surrogate_gap']:.3f} |

Best model by mean composite: `{best_model}`

## Golden Read

- `two_light_plain` golden composite: `{golden_plain['composite_score']:.3f}`, surrogate gap `{golden_plain['surrogate_gap']:.3f}`
- `two_light_contact_ring` golden composite: `{golden_contact['composite_score']:.3f}`, surrogate gap `{golden_contact['surrogate_gap']:.3f}`
"""


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    models = build_models()
    conditions = build_conditions()

    direct_rows: list[dict] = []
    total = len(anchors) * len(models)
    idx = 0
    for anchor in anchors:
        for model in models:
            idx += 1
            print(f"scanning {idx}/{total}: {anchor.name} / {model.name}")
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
                            "max_alignment_age": condition.max_alignment_age,
                            "memory_capacity": condition.memory_capacity,
                            **metrics,
                        }
                    )

    anchor_rows, surrogate_rows = summarize_results(anchors, models, conditions, direct_rows)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(anchor_rows, OUT / "anchor_summary.csv")
    write_csv(surrogate_rows, OUT / "surrogate_summary.csv")
    plot_model_summary(anchor_rows, OUT / "model_summary.png")
    report = build_report(anchor_rows)
    write_text(OUT / "report.md", report)

    plain_rows = [row for row in anchor_rows if row["model"] == "two_light_plain"]
    golden = next(row for row in plain_rows if row["anchor"] == "golden")
    best_model = max(
        sorted({row["model"] for row in anchor_rows}),
        key=lambda name: np.mean([row["composite_score"] for row in anchor_rows if row["model"] == name]),
    )
    print(f"files created: {OUT}")
    print(f"best model: {best_model}")
    print(f"golden plain rank: {sorted(plain_rows, key=lambda row: row['composite_score'], reverse=True).index(golden) + 1}")
    print(f"golden plain composite: {golden['composite_score']:.3f}")
    print(f"golden plain surrogate gap: {golden['surrogate_gap']:.3f}")


if __name__ == "__main__":
    main()
