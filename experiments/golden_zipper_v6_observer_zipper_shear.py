#!/usr/bin/env python3
"""v6 toy observer-zipper shear test with ternary boundary states."""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v6_outputs"

SEED = 1729
RNG = np.random.default_rng(SEED)

OFFSET_GRID = np.arange(-0.06, 0.0601, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
PHASES = [0.0, 0.13]
BETAS = [0.011, 0.029]
LENGTHS = [2048]
MEMORY_CAPACITIES = [64]
BAND_MODES = ["counter_double", "counter_triple"]


@dataclass(frozen=True)
class AnchorSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class ObserverCondition:
    band_mode: str
    window_width: float
    phase: float
    beta: float
    length: int
    memory_capacity: int


@dataclass(frozen=True)
class PerturbationSpec:
    name: str
    phase_lag: float
    delay_steps: int
    noise_amp: float
    beta_scale: float
    zip_threshold_delta: float


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    fieldnames = []
    seen = set()
    for row in rows:
        for key in row:
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


def circular_distance(x: np.ndarray, centers: np.ndarray) -> np.ndarray:
    return np.abs(np.mod(x - centers + 0.5, 1.0) - 0.5)


def continued_fraction_value(coeffs: list[int], tail_ones: int = 16) -> float:
    full = list(coeffs) + [1] * tail_ones
    value = float(full[-1])
    for a in reversed(full[:-1]):
        value = float(a) + 1.0 / value
    return 1.0 / value


def build_random_badly_approximable() -> float:
    coeffs = RNG.choice([1, 2, 3], size=8, replace=True).tolist()
    return continued_fraction_value(coeffs, tail_ones=16)


def build_anchors() -> list[AnchorSpec]:
    golden = 1.0 / PHI
    silver = math.sqrt(2.0) - 1.0
    bronze = (math.sqrt(13.0) - 3.0) / 2.0
    bounded_probe = continued_fraction_value([2, 1, 2, 1, 2, 1, 2], tail_ones=12)
    random_bad = build_random_badly_approximable()
    return [
        AnchorSpec("golden", golden, "phi_anchor"),
        AnchorSpec("silver", silver, "metallic_anchor"),
        AnchorSpec("bronze", bronze, "metallic_anchor"),
        AnchorSpec("bounded_probe", bounded_probe, "bounded_anchor"),
        AnchorSpec("random_bad_cf", random_bad, "random_bounded_cf"),
    ]


def build_conditions() -> list[ObserverCondition]:
    conditions = []
    for band_mode in BAND_MODES:
        for window_width in WINDOW_WIDTHS:
            for phase in PHASES:
                for beta in BETAS:
                    for length in LENGTHS:
                        for memory_capacity in MEMORY_CAPACITIES:
                            conditions.append(
                                ObserverCondition(
                                    band_mode=band_mode,
                                    window_width=window_width,
                                    phase=phase,
                                    beta=beta,
                                    length=length,
                                    memory_capacity=memory_capacity,
                                )
                            )
    return conditions


def build_perturbations() -> list[PerturbationSpec]:
    return [
        PerturbationSpec("phase_small", 0.010, 0, 0.0, 1.00, 0.00),
        PerturbationSpec("phase_big", 0.028, 0, 0.0, 1.00, 0.00),
        PerturbationSpec("delay_3", 0.0, 3, 0.0, 1.00, 0.00),
        PerturbationSpec("delay_7", 0.0, 7, 0.0, 1.00, 0.00),
        PerturbationSpec("noise_small", 0.0, 0, 0.0014, 1.00, 0.00),
        PerturbationSpec("noise_big", 0.0, 0, 0.0036, 1.00, 0.00),
        PerturbationSpec("beta_loosen", 0.0, 0, 0.0, 0.82, 0.00),
        PerturbationSpec("beta_tighten", 0.0, 0, 0.0, 1.18, 0.00),
        PerturbationSpec("zip_soft", 0.0, 0, 0.0, 1.00, -0.030),
        PerturbationSpec("zip_hard", 0.0, 0, 0.0, 1.00, 0.030),
        PerturbationSpec("combo_small", 0.012, 3, 0.0014, 1.08, 0.015),
        PerturbationSpec("combo_big", 0.028, 7, 0.0036, 1.18, 0.030),
    ]


def band_centers(condition: ObserverCondition, perturb: PerturbationSpec) -> tuple[list[np.ndarray], list[np.ndarray]]:
    n = np.arange(condition.length, dtype=float)
    beta = condition.beta * perturb.beta_scale
    pos = [wrap01(condition.phase + beta * n)]
    neg = [wrap01(condition.phase + 0.5 - beta * n)]
    if condition.band_mode == "counter_triple":
        pos.append(wrap01(condition.phase + 0.33 + 0.55 * beta * n))
        neg.append(wrap01(condition.phase + 0.83 - 0.55 * beta * n))
    return pos, neg


def nearest_band_strength(x: np.ndarray, centers: list[np.ndarray], radius: float) -> np.ndarray:
    nearest = np.full(len(x), np.inf)
    for center in centers:
        nearest = np.minimum(nearest, circular_distance(x, center))
    return np.clip(1.0 - nearest / max(radius, 1e-9), 0.0, 1.0)


def zipper_sequence(
    alpha: float,
    condition: ObserverCondition,
    perturb: PerturbationSpec,
) -> tuple[np.ndarray, np.ndarray]:
    n = np.arange(condition.length, dtype=float)
    delayed_n = np.maximum(n - perturb.delay_steps, 0.0)
    x = delayed_n * alpha + condition.phase + perturb.phase_lag
    if perturb.noise_amp > 0:
        x = x + perturb.noise_amp * np.sin(2.0 * math.pi * (0.037 * n + alpha * 2.0))
    x = wrap01(x)

    pos_centers, neg_centers = band_centers(condition, perturb)
    radius = condition.window_width / (3.1 if condition.band_mode == "counter_triple" else 2.15)
    pos_strength = nearest_band_strength(x, pos_centers, radius)
    neg_strength = nearest_band_strength(x, neg_centers, radius)
    zipper_score = pos_strength - neg_strength
    zip_threshold = 0.12 + perturb.zip_threshold_delta

    seq = np.zeros(condition.length, dtype=np.int8)
    seq[zipper_score > zip_threshold] = 1
    seq[zipper_score < -zip_threshold] = -1
    return seq, zipper_score


def hamming_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return 1.0 - float(np.mean(a != b))


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


def ternary_phase_lock_score(seq: np.ndarray) -> tuple[float, dict[str, float]]:
    mismatch, best_period = approximate_periodicity(seq)
    ac = autocorr_peak(seq)
    spec = spectral_peak(seq)
    approx = 1.0 - mismatch
    period_term = 1.0 / best_period if best_period > 0 else 1.0
    score = float(np.mean([ac, spec, min(approx * period_term * 18.0, 1.0)]))
    return score, {
        "approx_mismatch": mismatch,
        "approx_period": float(best_period),
        "autocorr_peak": ac,
        "spectral_peak": spec,
    }


def ternary_context_features(
    seq: np.ndarray,
    context_len: int = 4,
    motif_len: int = 5,
) -> dict[str, np.ndarray | list[tuple[int, ...] | None]]:
    next_counts: dict[tuple[int, ...], Counter] = defaultdict(Counter)
    motif_counts: Counter = Counter()

    for i in range(context_len, len(seq)):
        ctx = tuple(int(x) for x in seq[i - context_len : i])
        next_counts[ctx][int(seq[i])] += 1
    for i in range(len(seq) - motif_len + 1):
        motif = tuple(int(x) for x in seq[i : i + motif_len])
        motif_counts[motif] += 1

    max_motif = max(motif_counts.values()) if motif_counts else 1
    prob_current = np.full(len(seq), 1.0 / 3.0, dtype=float)
    margin = np.zeros(len(seq), dtype=float)
    motif_score = np.zeros(len(seq), dtype=float)
    motif_ids: list[tuple[int, ...] | None] = [None] * len(seq)

    for i in range(context_len, len(seq)):
        ctx = tuple(int(x) for x in seq[i - context_len : i])
        counts = next_counts[ctx]
        total = sum(counts.values())
        if total:
            ordered = sorted((counts[-1], counts[0], counts[1]), reverse=True)
            prob_current[i] = counts[int(seq[i])] / total
            margin[i] = (ordered[0] - ordered[1]) / total if len(ordered) >= 2 else ordered[0] / total
        if i <= len(seq) - motif_len:
            motif = tuple(int(x) for x in seq[i : i + motif_len])
            motif_score[i] = motif_counts[motif] / max_motif
            motif_ids[i] = motif

    return {
        "prob_current": prob_current,
        "margin": margin,
        "motif_score": motif_score,
        "motif_ids": motif_ids,
    }


def future_resolution_array(seq: np.ndarray, horizon: int = 6) -> np.ndarray:
    ints = seq.astype(int)
    prefix = np.concatenate(([0], np.cumsum(ints)))
    future_sum = np.zeros(len(seq), dtype=int)
    for idx in range(len(seq)):
        stop = min(len(seq), idx + 1 + horizon)
        future_sum[idx] = int(prefix[stop] - prefix[idx + 1])
    resolved = np.sign(future_sum).astype(np.int8)
    resolved[np.abs(future_sum) < 2] = 0
    return resolved


def simulate_ternary_policy(
    seq: np.ndarray,
    features: dict[str, np.ndarray | list[tuple[int, ...] | None]],
    memory_capacity: int,
) -> dict[str, float]:
    prob_current = features["prob_current"]
    margin = features["margin"]
    motif_score = features["motif_score"]
    motif_ids = features["motif_ids"]

    durable: Counter = Counter()
    witness_buffer: list[dict] = []
    actions = Counter()
    delayed_kept = 0
    delayed_missed = 0
    polluted_writes = 0
    write_total = 0
    zero_share = float(np.mean(seq == 0))
    resolved_future = future_resolution_array(seq)

    for idx, sym in enumerate(seq):
        resolved = int(resolved_future[idx])
        candidate = int(sym) == 0 and resolved != 0
        pcur = float(prob_current[idx])
        pmargin = float(margin[idx])
        motif = motif_ids[idx]
        mscore = float(motif_score[idx])

        for item in list(witness_buffer):
            item["age"] += 1
            if resolved != 0 and item["resolved"] == resolved:
                delayed_kept += 1
                if item["motif"] is not None:
                    durable[item["motif"]] += 1
                witness_buffer.remove(item)
            elif item["age"] > 10:
                delayed_missed += int(item["candidate"])
                witness_buffer.remove(item)

        if int(sym) != 0 and pcur >= 0.56 and pmargin >= 0.10:
            action = "write"
        elif candidate or pmargin >= 0.05 or mscore >= 0.18:
            action = "witness"
        else:
            action = "release"
        actions[action] += 1

        if action == "write":
            write_total += 1
            if resolved != 0 and resolved != int(sym):
                polluted_writes += 1
            if motif is not None:
                if motif not in durable and len(durable) >= memory_capacity:
                    worst, _ = min(durable.items(), key=lambda kv: (kv[1], len(kv[0])))
                    del durable[worst]
                durable[motif] += 1
        elif action == "witness":
            witness_buffer.append(
                {
                    "motif": motif,
                    "age": 0,
                    "candidate": candidate,
                    "resolved": resolved,
                }
            )
            if len(witness_buffer) > memory_capacity:
                expired = witness_buffer.pop(0)
                delayed_missed += int(expired["candidate"])

    delayed_total = delayed_kept + delayed_missed
    return {
        "write_count": float(actions["write"]),
        "witness_count": float(actions["witness"]),
        "release_count": float(actions["release"]),
        "delayed_retention": delayed_kept / delayed_total if delayed_total else 0.0,
        "pollution": polluted_writes / write_total if write_total else 0.0,
        "zero_share": zero_share,
        "memory_load": min(len(durable) + len(witness_buffer), memory_capacity) / max(memory_capacity, 1),
    }


def evaluate_sequence(
    alpha: float,
    condition: ObserverCondition,
    perturb: PerturbationSpec,
) -> dict[str, float]:
    seq, zipper_score = zipper_sequence(alpha, condition, perturb)
    phase_lock, phase_parts = ternary_phase_lock_score(seq)
    features = ternary_context_features(seq)
    memory = simulate_ternary_policy(seq, features, condition.memory_capacity)

    shadow = PerturbationSpec(
        name="shadow",
        phase_lag=perturb.phase_lag + 0.007,
        delay_steps=perturb.delay_steps,
        noise_amp=perturb.noise_amp + 0.0008,
        beta_scale=perturb.beta_scale,
        zip_threshold_delta=perturb.zip_threshold_delta,
    )
    shadow_seq, _ = zipper_sequence(alpha, condition, shadow)
    rigidity = hamming_similarity(seq, shadow_seq)

    metric = {
        "phase_lock_resistance": 1.0 - phase_lock,
        "delayed_retention": memory["delayed_retention"],
        "pollution": memory["pollution"],
        "rigidity_after_zipping": rigidity,
        "zero_share": memory["zero_share"],
        "memory_load": memory["memory_load"],
        "write_count": memory["write_count"],
        "witness_count": memory["witness_count"],
        "release_count": memory["release_count"],
        "zipper_energy": float(np.mean(np.abs(zipper_score))),
        "approx_period": phase_parts["approx_period"],
        "autocorr_peak": phase_parts["autocorr_peak"],
        "spectral_peak": phase_parts["spectral_peak"],
    }
    metric["composite_score"] = float(
        0.28 * metric["phase_lock_resistance"]
        + 0.24 * metric["delayed_retention"]
        + 0.20 * (1.0 - metric["pollution"])
        + 0.20 * metric["rigidity_after_zipping"]
        + 0.08 * metric["zero_share"]
    )
    return metric


def plot_hotspots(rows: list[dict], path: Path) -> None:
    anchors = sorted({row["anchor"] for row in rows})
    plt.figure(figsize=(9, 5))
    for anchor in anchors:
        subset = [row for row in rows if row["anchor"] == anchor]
        xs = [row["global_hotspot_offset"] for row in subset]
        ys = [row["shear_hotspot_stability"] for row in subset]
        plt.scatter(xs, ys, s=36, alpha=0.75, label=anchor)
    plt.axvline(0.0, color="black", linestyle="--", linewidth=1.0)
    plt.xlabel("global hotspot offset")
    plt.ylabel("shear hotspot stability")
    plt.title("Observer-zipper hotspot stability by anchor")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_metric_bars(rows: list[dict], path: Path) -> None:
    anchors = [row["anchor"] for row in rows]
    phase_resist = [row["phase_lock_resistance"] for row in rows]
    delayed = [row["delayed_retention"] for row in rows]
    pollution = [1.0 - row["pollution"] for row in rows]
    rigidity = [row["rigidity_after_zipping"] for row in rows]

    x = np.arange(len(anchors))
    width = 0.2
    plt.figure(figsize=(10, 5))
    plt.bar(x - 1.5 * width, phase_resist, width=width, label="phase-lock resistance")
    plt.bar(x - 0.5 * width, delayed, width=width, label="delayed retention")
    plt.bar(x + 0.5 * width, pollution, width=width, label="1 - pollution")
    plt.bar(x + 1.5 * width, rigidity, width=width, label="rigidity after zipping")
    plt.xticks(x, anchors, rotation=20)
    plt.ylim(0.0, 1.0)
    plt.title("Anchor metric summary at hotspot")
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_offset_bands(rows: list[dict], path: Path) -> None:
    anchors = sorted({row["anchor"] for row in rows})
    fig, axes = plt.subplots(len(anchors), 1, figsize=(9, 2.6 * len(anchors)), sharex=True)
    if len(anchors) == 1:
        axes = [axes]
    for ax, anchor in zip(axes, anchors):
        subset = sorted([row for row in rows if row["anchor"] == anchor], key=lambda row: row["offset"])
        ax.plot([row["offset"] for row in subset], [row["mean_composite_score"] for row in subset], color="#0d47a1")
        ax.axvline(0.0, color="black", linestyle="--", linewidth=1.0)
        ax.set_ylabel(anchor)
    axes[-1].set_xlabel("offset from anchor")
    fig.suptitle("Direct observer-zipper composite bands", y=0.995)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    conditions = build_conditions()
    perturbations = build_perturbations()
    none = PerturbationSpec("none", 0.0, 0, 0.0, 1.0, 0.0)

    direct_rows = []
    for anchor in anchors:
        for condition in conditions:
            for offset in OFFSET_GRID:
                alpha = anchor.alpha + float(offset)
                if not (0.0 < alpha < 1.0):
                    continue
                metrics = evaluate_sequence(alpha, condition, none)
                direct_rows.append(
                    {
                        "anchor": anchor.name,
                        "anchor_family": anchor.family,
                        "alpha": alpha,
                        "offset": float(offset),
                        "band_mode": condition.band_mode,
                        "window_width": condition.window_width,
                        "phase": condition.phase,
                        "beta": condition.beta,
                        "length": condition.length,
                        "memory_capacity": condition.memory_capacity,
                        **metrics,
                    }
                )
    print(f"direct observer zipper rows: {len(direct_rows)}", flush=True)

    hotspot_rows = []
    for anchor in anchors:
        for condition in conditions:
            subset = [
                row
                for row in direct_rows
                if row["anchor"] == anchor.name
                and row["band_mode"] == condition.band_mode
                and row["window_width"] == condition.window_width
                and row["phase"] == condition.phase
                and row["beta"] == condition.beta
                and row["length"] == condition.length
                and row["memory_capacity"] == condition.memory_capacity
            ]
            best = max(subset, key=lambda row: row["composite_score"])
            hotspot_rows.append(
                {
                    "anchor": anchor.name,
                    "anchor_family": anchor.family,
                    "band_mode": condition.band_mode,
                    "window_width": condition.window_width,
                    "phase": condition.phase,
                    "beta": condition.beta,
                    "length": condition.length,
                    "memory_capacity": condition.memory_capacity,
                    "hotspot_offset": best["offset"],
                    "hotspot_alpha": best["alpha"],
                    "hotspot_score": best["composite_score"],
                    "phase_lock_resistance": best["phase_lock_resistance"],
                    "delayed_retention": best["delayed_retention"],
                    "pollution": best["pollution"],
                    "rigidity_after_zipping": best["rigidity_after_zipping"],
                }
            )
    print(f"direct hotspots: {len(hotspot_rows)}", flush=True)

    perturb_rows = []
    for hotspot in hotspot_rows:
        condition = ObserverCondition(
            band_mode=hotspot["band_mode"],
            window_width=hotspot["window_width"],
            phase=hotspot["phase"],
            beta=hotspot["beta"],
            length=int(hotspot["length"]),
            memory_capacity=int(hotspot["memory_capacity"]),
        )
        for perturb in perturbations:
            metrics = evaluate_sequence(float(hotspot["hotspot_alpha"]), condition, perturb)
            perturb_rows.append(
                {
                    **hotspot,
                    "perturbation": perturb.name,
                    "phase_lag": perturb.phase_lag,
                    "delay_steps": perturb.delay_steps,
                    "noise_amp": perturb.noise_amp,
                    "beta_scale": perturb.beta_scale,
                    "zip_threshold_delta": perturb.zip_threshold_delta,
                    **metrics,
                }
            )
    print(f"perturbed hotspot rows: {len(perturb_rows)}", flush=True)

    anchor_summary = []
    for anchor in anchors:
        direct_anchor = [row for row in hotspot_rows if row["anchor"] == anchor.name]
        perturb_anchor = [row for row in perturb_rows if row["anchor"] == anchor.name]
        hotspot_offsets = np.array([row["hotspot_offset"] for row in direct_anchor], dtype=float)
        global_hotspot = float(np.median(hotspot_offsets))
        stability = float(np.mean(np.abs(hotspot_offsets - global_hotspot) <= 0.012))
        perturb_stability = float(
            np.mean(
                [
                    abs(float(row["hotspot_offset"]) - global_hotspot) <= 0.016
                    and float(row["composite_score"]) >= float(row["hotspot_score"]) - 0.08
                    for row in perturb_anchor
                ]
            )
        )
        anchor_summary.append(
            {
                "anchor": anchor.name,
                "anchor_family": anchor.family,
                "alpha": anchor.alpha,
                "global_hotspot_offset": global_hotspot,
                "shear_hotspot_stability": stability,
                "perturbed_hotspot_stability": perturb_stability,
                "phase_lock_resistance": float(np.mean([row["phase_lock_resistance"] for row in direct_anchor])),
                "delayed_retention": float(np.mean([row["delayed_retention"] for row in direct_anchor])),
                "pollution": float(np.mean([row["pollution"] for row in direct_anchor])),
                "rigidity_after_zipping": float(np.mean([row["rigidity_after_zipping"] for row in direct_anchor])),
                "mean_hotspot_score": float(np.mean([row["hotspot_score"] for row in direct_anchor])),
                "mean_perturbed_score": float(np.mean([row["composite_score"] for row in perturb_anchor])),
            }
        )

    band_summary = []
    for anchor in anchors:
        for offset in OFFSET_GRID:
            subset = [
                row
                for row in direct_rows
                if row["anchor"] == anchor.name and abs(float(row["offset"]) - float(offset)) < 1e-9
            ]
            if not subset:
                continue
            band_summary.append(
                {
                    "anchor": anchor.name,
                    "offset": float(offset),
                    "mean_composite_score": float(np.mean([row["composite_score"] for row in subset])),
                    "mean_phase_lock_resistance": float(
                        np.mean([row["phase_lock_resistance"] for row in subset])
                    ),
                    "mean_delayed_retention": float(np.mean([row["delayed_retention"] for row in subset])),
                    "mean_pollution": float(np.mean([row["pollution"] for row in subset])),
                    "mean_rigidity_after_zipping": float(
                        np.mean([row["rigidity_after_zipping"] for row in subset])
                    ),
                }
            )

    write_csv(direct_rows, OUT / "direct_observer_metrics.csv")
    write_csv(hotspot_rows, OUT / "hotspot_metrics.csv")
    write_csv(perturb_rows, OUT / "perturbed_hotspot_metrics.csv")
    write_csv(anchor_summary, OUT / "anchor_summary.csv")
    write_csv(band_summary, OUT / "direct_band_summary.csv")

    plot_hotspots(anchor_summary, OUT / "anchor_hotspot_stability.png")
    plot_metric_bars(anchor_summary, OUT / "anchor_metric_summary.png")
    plot_offset_bands(band_summary, OUT / "direct_observer_bands.png")

    ranked = sorted(anchor_summary, key=lambda row: (row["shear_hotspot_stability"], row["mean_hotspot_score"]), reverse=True)
    strongest = ranked[0]
    weakest = ranked[-1]
    golden = next(row for row in anchor_summary if row["anchor"] == "golden")

    if golden["shear_hotspot_stability"] >= 0.60 and golden["perturbed_hotspot_stability"] >= 0.50:
        verdict = "C-leaning: golden hotspot survives the toy zipper, but not uniquely enough to harden."
    else:
        verdict = "D-leaning: toy zipper shear does not keep a durable golden hotspot."

    report = [
        "# Golden Zipper v6 - Observer Ternary Zipper Shear",
        "",
        "Toy telemetry only. Conservative by design. Not evidence for physics, consciousness, or write-law closure.",
        "",
        "## Setup",
        "",
        "The observer is modeled as a ternary zipper boundary on a circle-like phase line with states `-1, 0, +1`.",
        "Two flow families are used:",
        "- `counter_double`: one positive band and one counter-moving negative band",
        "- `counter_triple`: the same counter-flow plus a second offset pair to mimic a multi-band torus slice",
        "",
        "Anchors compared: golden, silver, bronze, bounded_probe, and one deterministic random bounded-CF control.",
        "",
        "## Metrics",
        "",
        "- shear hotspot stability: how tightly best offsets cluster across observer conditions",
        "- phase-lock resistance: `1 - phase_lock_score`, so higher is less periodic lock-in",
        "- delayed retention: witness-like uncertain states later resolved instead of dropped",
        "- pollution: fraction of writes contradicted by short-horizon future resolution",
        "- rigidity-after-zipping: similarity after a small shadow perturbation",
        "",
        "## Verdict",
        "",
        f"**{verdict}**",
        "",
        "## Anchor Summary",
        "",
        "| Anchor | Global hotspot | Stability | Perturbed stability | Phase-lock resistance | Delayed retention | Pollution | Rigidity |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in anchor_summary:
        report.append(
            f"| {row['anchor']} | {row['global_hotspot_offset']:.4f} | {row['shear_hotspot_stability']:.3f} | {row['perturbed_hotspot_stability']:.3f} | {row['phase_lock_resistance']:.3f} | {row['delayed_retention']:.3f} | {row['pollution']:.3f} | {row['rigidity_after_zipping']:.3f} |"
        )

    report.extend(
        [
            "",
            "## Reading",
            "",
            "This is a stress toy for symbolic behavior under ternary observer zipping. The numbers only say whether some anchors keep a reasonably stable local offset preference under these small observer distortions.",
            "",
            f"Strongest anchor in this toy: `{strongest['anchor']}` with stability `{strongest['shear_hotspot_stability']:.3f}` and mean hotspot score `{strongest['mean_hotspot_score']:.3f}`.",
            f"Weakest anchor in this toy: `{weakest['anchor']}` with stability `{weakest['shear_hotspot_stability']:.3f}` and mean hotspot score `{weakest['mean_hotspot_score']:.3f}`.",
            "",
            "## Golden-Specific Note",
            "",
            f"- Golden global hotspot offset: `{golden['global_hotspot_offset']:.4f}`",
            f"- Golden hotspot stability: `{golden['shear_hotspot_stability']:.3f}`",
            f"- Golden perturbed stability: `{golden['perturbed_hotspot_stability']:.3f}`",
            f"- Golden pollution: `{golden['pollution']:.3f}`",
            "",
            "## Do-Not-Claim Ledger",
            "",
            "- does not prove GHP",
            "- does not prove any anchor is fundamental",
            "- does not justify changing shared theory documents",
            "- does not count as physics evidence",
            "- does not establish observer realism",
        ]
    )
    write_text(OUT / "report.md", "\n".join(report))

    print(f"files created: {OUT}")
    print(f"verdict: {verdict}")
    print(f"strongest anchor: {strongest['anchor']}")
    print(f"weakest anchor: {weakest['anchor']}")
    print(f"golden hotspot stability: {golden['shear_hotspot_stability']:.3f}")


if __name__ == "__main__":
    main()
