#!/usr/bin/env python3
"""v22c resonant zero-boundary panel.

Toy telemetry only. Not physics evidence. Not proof of GHP.

This version keeps the soft zero-boundary membrane from v22b, but adds
resonance: repeated near-boundary touches can accumulate until witness becomes
write instead of mostly falling back to release.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v22c_outputs"

SEED = 20260520
RNG = np.random.default_rng(SEED)

LENGTH = 4096
OFFSET_GRID = np.arange(-0.036, 0.0361, 0.012)
WINDOW_WIDTHS = [0.18, 0.26]
BETAS = [0.0, 0.011]
DRIFTS = [0.0, 0.003]
MEMBRANE_GAINS = [0.18, 0.30, 0.42]
MEMBRANE_DECAYS = [0.82, 0.90, 0.96]
RESONANCE_GAINS = [0.10, 0.18, 0.28]
RESONANCE_DECAYS = [0.86, 0.93]
WRITE_THRESHOLDS = [0.34, 0.48, 0.62]
OVERLOAD_THRESHOLDS = [1.20, 1.50, 1.85]
STABILITY_WINDOWS = [5, 9]
MAX_CONDITIONS = 60


@dataclass(frozen=True)
class FlowSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class Condition:
    window_width: float
    beta: float
    drift: float
    membrane_gain: float
    membrane_decay: float
    resonance_gain: float
    resonance_decay: float
    write_threshold: float
    overload_threshold: float
    stability_window: int


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


def continued_fraction_value(coeffs: list[int], tail_ones: int = 16) -> float:
    values = list(coeffs) + [1] * tail_ones
    out = float(values[-1])
    for coeff in reversed(values[:-1]):
        out = float(coeff) + 1.0 / out
    return 1.0 / out


def build_flows() -> list[FlowSpec]:
    return [
        FlowSpec("golden", 1.0 / PHI, "phi"),
        FlowSpec("silver", math.sqrt(2.0) - 1.0, "metallic"),
        FlowSpec("bounded_cf_2", continued_fraction_value([1, 2, 3, 1, 2, 3], tail_ones=14), "bounded_cf"),
        FlowSpec("random_cf_1", continued_fraction_value([7, 2, 9, 3, 5, 4], tail_ones=8), "random_cf"),
        FlowSpec("fib_13_21", 13.0 / 21.0, "rational"),
        FlowSpec("pi_mod1", math.pi % 1.0, "constant"),
    ]


def build_conditions() -> list[Condition]:
    full = [
        Condition(
            window_width=window_width,
            beta=beta,
            drift=drift,
            membrane_gain=membrane_gain,
            membrane_decay=membrane_decay,
            resonance_gain=resonance_gain,
            resonance_decay=resonance_decay,
            write_threshold=write_threshold,
            overload_threshold=overload_threshold,
            stability_window=stability_window,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for drift in DRIFTS
        for membrane_gain in MEMBRANE_GAINS
        for membrane_decay in MEMBRANE_DECAYS
        for resonance_gain in RESONANCE_GAINS
        for resonance_decay in RESONANCE_DECAYS
        for write_threshold in WRITE_THRESHOLDS
        for overload_threshold in OVERLOAD_THRESHOLDS
        for stability_window in STABILITY_WINDOWS
    ]
    if len(full) <= MAX_CONDITIONS:
        return full
    picks = np.sort(RNG.choice(len(full), size=MAX_CONDITIONS, replace=False))
    return [full[idx] for idx in picks]


def approximate_periodicity(seq: np.ndarray, max_period: int = 96) -> tuple[float, int]:
    work = seq[: min(len(seq), 4096)]
    best_mismatch = 1.0
    best_period = max_period + 1
    for period in range(1, min(max_period, len(work) // 2) + 1):
        mismatch = float(np.mean(work[:-period] != work[period:]))
        if mismatch < best_mismatch:
            best_mismatch = mismatch
            best_period = period
    return best_mismatch, best_period


def autocorr_peak(seq: np.ndarray, max_lag: int = 96) -> float:
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


def build_hidden_trace(alpha: float, condition: Condition) -> np.ndarray:
    n = np.arange(LENGTH, dtype=float)
    core = np.sin(2.0 * math.pi * (alpha * n + condition.beta))
    reverse = 0.30 * np.sin(2.0 * math.pi * ((1.0 - alpha) * n + 0.19))
    slow = 0.22 * np.sin(2.0 * math.pi * ((alpha / PHI) * n + 0.31))
    drift = condition.drift * (n / max(LENGTH - 1, 1))
    return (core + reverse + slow + drift).astype(float)


def build_sequence(alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    hidden = build_hidden_trace(alpha, condition)
    seq = np.full(LENGTH, -2, dtype=np.int8)

    membrane = 0.0
    resonance = 0.0
    witness_open = False
    witness_index = -1
    stable_crossings = 0
    witness_total = 0
    release_total = 0
    overload_total = 0
    witness_to_write = 0
    crossing_quality: list[float] = []

    for idx in range(1, LENGTH):
        prev = hidden[idx - 1]
        cur = hidden[idx]
        distance_to_zero = abs(cur)
        approach = max(0.0, condition.window_width - distance_to_zero) / max(condition.window_width, 1e-9)
        slope = abs(cur - prev)
        local = hidden[max(0, idx - condition.stability_window) : min(LENGTH, idx + condition.stability_window + 1)]
        local_stability = float(np.std(local))
        quality = approach + slope - local_stability

        membrane = membrane * condition.membrane_decay + condition.membrane_gain * max(0.0, quality)
        resonance = resonance * condition.resonance_decay

        near_boundary = distance_to_zero <= condition.window_width
        if near_boundary:
            resonance += condition.resonance_gain * max(0.0, approach)

        if membrane + resonance >= condition.overload_threshold:
            seq[idx] = 2
            overload_total += 1
            membrane = 0.0
            resonance = 0.0
            witness_open = False
            witness_index = -1
            continue

        if not near_boundary:
            if witness_open and witness_index >= 0 and seq[witness_index] == 0:
                seq[witness_index] = -1
                release_total += 1
                witness_open = False
                witness_index = -1
            continue

        effective_pressure = membrane + resonance
        if effective_pressure >= condition.write_threshold and local_stability <= condition.window_width:
            seq[idx] = 1
            stable_crossings += 1
            crossing_quality.append(quality + resonance)
            if witness_open:
                witness_to_write += 1
                witness_open = False
                witness_index = -1
            membrane *= 0.35
            resonance *= 0.25
            continue

        if not witness_open:
            seq[idx] = 0
            witness_total += 1
            witness_open = True
            witness_index = idx
            crossing_quality.append(quality + resonance)

    return seq, {
        "stable_crossings": float(stable_crossings),
        "witness_total": float(witness_total),
        "release_total": float(release_total),
        "overload_total": float(overload_total),
        "witness_to_write": float(witness_to_write),
        "mean_crossing_quality": float(np.mean(crossing_quality)) if crossing_quality else 0.0,
    }


def evaluate_model(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    writes = float(np.sum(seq == 1))
    witnesses = float(np.sum(seq == 0))
    releases = float(np.sum(seq == -1))
    overloads = float(np.sum(seq == 2))
    total_events = writes + witnesses + releases + overloads
    witness_conversion = diag["witness_to_write"] / max(diag["witness_total"], 1.0)
    delayed_retention = writes / max(writes + witnesses, 1.0)
    release_rate = releases / max(total_events, 1.0)
    overload_rate = overloads / max(total_events, 1.0)
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] <= -1))) if len(seq) > 1 else 0.0
    phase_resist = phase_lock_resistance(seq)
    return {
        "write_count": writes,
        "witness_count": witnesses,
        "release_count": releases,
        "overload_count": overloads,
        "witness_conversion": witness_conversion,
        "delayed_retention": delayed_retention,
        "release_rate": release_rate,
        "overload_rate": overload_rate,
        "mean_crossing_quality": diag["mean_crossing_quality"],
        "pollution": pollution,
        "phase_lock_resistance": phase_resist,
    }


def composite_score(metrics: dict[str, float]) -> float:
    crossing_quality = min(max((metrics["mean_crossing_quality"] + 0.3) / 1.4, 0.0), 1.0)
    return float(
        0.20 * metrics["phase_lock_resistance"]
        + 0.18 * metrics["delayed_retention"]
        + 0.18 * metrics["witness_conversion"]
        + 0.14 * crossing_quality
        + 0.12 * (1.0 - metrics["pollution"])
        + 0.10 * (1.0 - metrics["overload_rate"])
        + 0.08 * (1.0 - metrics["release_rate"])
    )


def plot_flow_summary(rows: list[dict], path: Path) -> None:
    labels = [row["flow"] for row in rows]
    scores = [row["mean_composite"] for row in rows]
    witness = [row["mean_witness_conversion"] for row in rows]
    x = np.arange(len(labels))
    width = 0.35
    plt.figure(figsize=(10, 5))
    plt.bar(x - width / 2, scores, width=width, label="mean composite")
    plt.bar(x + width / 2, witness, width=width, label="witness conversion")
    plt.xticks(x, labels, rotation=20)
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    flows = build_flows()
    conditions = build_conditions()

    direct_rows: list[dict] = []
    for flow in flows:
        print(f"flow: {flow.name}")
        for condition in conditions:
            for offset in OFFSET_GRID:
                alpha = flow.alpha + float(offset)
                if not (0.0 < alpha < 1.0):
                    continue
                seq, diag = build_sequence(alpha, condition)
                metrics = evaluate_model(seq, diag)
                direct_rows.append(
                    {
                        "flow": flow.name,
                        "family": flow.family,
                        "alpha": alpha,
                        "offset": float(offset),
                        "window_width": condition.window_width,
                        "beta": condition.beta,
                        "drift": condition.drift,
                        "membrane_gain": condition.membrane_gain,
                        "membrane_decay": condition.membrane_decay,
                        "resonance_gain": condition.resonance_gain,
                        "resonance_decay": condition.resonance_decay,
                        "write_threshold": condition.write_threshold,
                        "overload_threshold": condition.overload_threshold,
                        "stability_window": condition.stability_window,
                        **metrics,
                        "composite_score": composite_score(metrics),
                    }
                )

    flow_rows: list[dict] = []
    for flow in flows:
        subset = [row for row in direct_rows if row["flow"] == flow.name]
        best = max(subset, key=lambda row: row["composite_score"])
        cond = Condition(
            window_width=best["window_width"],
            beta=best["beta"],
            drift=best["drift"],
            membrane_gain=best["membrane_gain"],
            membrane_decay=best["membrane_decay"],
            resonance_gain=best["resonance_gain"],
            resonance_decay=best["resonance_decay"],
            write_threshold=best["write_threshold"],
            overload_threshold=best["overload_threshold"],
            stability_window=best["stability_window"],
        )
        seq, _ = build_sequence(best["alpha"], cond)
        density = density_random_surrogate(seq)
        density_metrics = evaluate_model(
            density,
            {
                "stable_crossings": 0.0,
                "witness_total": float(np.sum(density == 0)),
                "release_total": float(np.sum(density == -1)),
                "overload_total": float(np.sum(density == 2)),
                "witness_to_write": 0.0,
                "mean_crossing_quality": 0.0,
            },
        )
        mean_composite = float(np.mean([row["composite_score"] for row in subset]))
        flow_rows.append(
            {
                "flow": flow.name,
                "family": flow.family,
                "best_composite": best["composite_score"],
                "mean_composite": mean_composite,
                "mean_witness_conversion": float(np.mean([row["witness_conversion"] for row in subset])),
                "mean_overload_rate": float(np.mean([row["overload_rate"] for row in subset])),
                "mean_release_rate": float(np.mean([row["release_rate"] for row in subset])),
                "mean_crossing_quality": float(np.mean([row["mean_crossing_quality"] for row in subset])),
                "mean_density_gap": mean_composite - composite_score(density_metrics),
            }
        )

    ranked = sorted(flow_rows, key=lambda row: row["mean_composite"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(flow_rows, OUT / "flow_summary.csv")
    plot_flow_summary(flow_rows, OUT / "flow_summary.png")

    best = ranked[0]
    golden = next(row for row in flow_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v22c - Resonant Zero Boundary

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by mean composite: `{best['flow']}` with `{best['mean_composite']:.3f}`

Golden result:
- mean composite: `{golden['mean_composite']:.3f}`
- witness conversion: `{golden['mean_witness_conversion']:.3f}`
- overload rate: `{golden['mean_overload_rate']:.3f}`
- density gap: `{golden['mean_density_gap']:.3f}`

Interpretation:
- This panel adds resonance to the zero-boundary membrane so repeated touches can mature witness into write.
- Success here means witness finally behaves like a real intermediate state.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by mean composite: {best['flow']}")
    print(f"golden mean composite: {golden['mean_composite']:.3f}")
    print(f"golden witness conversion: {golden['mean_witness_conversion']:.3f}")
    print(f"golden overload rate: {golden['mean_overload_rate']:.3f}")
    print(f"golden density gap: {golden['mean_density_gap']:.3f}")


if __name__ == "__main__":
    main()
