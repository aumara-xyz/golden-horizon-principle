#!/usr/bin/env python3
"""v26 reconsolidating nest collapse panel.

Toy telemetry only. Not physics evidence. Not proof of GHP.

This panel models:
- latent feeling-without-words
- collapse candidate at the observer boundary
- nested hold
- rendered memory
- retouch / reconsolidation
- rupture if novelty exceeds fit budget
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
OUT = ROOT / "golden_zipper_v26_outputs"

SEED = 20260521
RNG = np.random.default_rng(SEED)

LENGTH = 3072
OFFSET_GRID = np.arange(-0.036, 0.0361, 0.012)
WINDOW_WIDTHS = [0.16, 0.24]
BETAS = [0.0, 0.011]
FIT_BUDGETS = [0.22, 0.34, 0.48]
IMPORTANCE_WEIGHTS = [0.18, 0.30, 0.44]
RETOUCH_GAINS = [0.10, 0.18, 0.28]
NEST_DECAYS = [0.90, 0.95, 0.98]
WRITE_THRESHOLDS = [0.48, 0.64, 0.82]
RUPTURE_THRESHOLDS = [0.85, 1.05, 1.25]
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
    fit_budget: float
    importance_weight: float
    retouch_gain: float
    nest_decay: float
    write_threshold: float
    rupture_threshold: float


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
            fit_budget=fit_budget,
            importance_weight=importance_weight,
            retouch_gain=retouch_gain,
            nest_decay=nest_decay,
            write_threshold=write_threshold,
            rupture_threshold=rupture_threshold,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for fit_budget in FIT_BUDGETS
        for importance_weight in IMPORTANCE_WEIGHTS
        for retouch_gain in RETOUCH_GAINS
        for nest_decay in NEST_DECAYS
        for write_threshold in WRITE_THRESHOLDS
        for rupture_threshold in RUPTURE_THRESHOLDS
    ]
    if len(full) <= MAX_CONDITIONS:
        return full
    picks = np.sort(RNG.choice(len(full), size=MAX_CONDITIONS, replace=False))
    return [full[idx] for idx in picks]


def approximate_periodicity(seq: np.ndarray, max_period: int = 96) -> tuple[float, int]:
    work = seq[: min(len(seq), 3072)]
    best_mismatch = 1.0
    best_period = max_period + 1
    for period in range(1, min(max_period, len(work) // 2) + 1):
        mismatch = float(np.mean(work[:-period] != work[period:]))
        if mismatch < best_mismatch:
            best_mismatch = mismatch
            best_period = period
    return best_mismatch, best_period


def autocorr_peak(seq: np.ndarray, max_lag: int = 96) -> float:
    work = seq[: min(len(seq), 3072)].astype(float)
    centered = work - work.mean()
    denom = float(np.dot(centered, centered))
    if denom <= 1e-12:
        return 1.0
    peaks = []
    for lag in range(1, min(max_lag, len(centered) - 1) + 1):
        peaks.append(abs(float(np.dot(centered[:-lag], centered[lag:]) / denom)))
    return max(peaks) if peaks else 0.0


def spectral_peak(seq: np.ndarray) -> float:
    work = seq[: min(len(seq), 3072)].astype(float)
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
    reverse = 0.28 * np.sin(2.0 * math.pi * ((1.0 - alpha) * n + 0.19))
    slow = 0.18 * np.sin(2.0 * math.pi * ((alpha / PHI) * n + 0.31))
    return (core + reverse + slow).astype(float)


def build_sequence(alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    hidden = build_hidden_trace(alpha, condition)
    seq = np.full(LENGTH, -3, dtype=np.int8)  # -3 latent, -2 candidate, -1 fade, 0 nested hold, 1 rendered, 2 rupture

    nest = 0.0
    rendered = 0.0
    writes = 0
    holds = 0
    fades = 0
    ruptures = 0
    retouches = 0
    rewrite_drift = 0.0
    collapse_success = 0
    fit_errors: list[float] = []

    for idx in range(1, LENGTH):
        prev = hidden[idx - 1]
        cur = hidden[idx]
        distance_to_zero = abs(cur)
        near_boundary = distance_to_zero <= condition.window_width
        approach = max(0.0, condition.window_width - distance_to_zero) / max(condition.window_width, 1e-9)
        surprise = abs(cur - prev)
        importance = condition.importance_weight * (0.6 * approach + 0.4 * min(surprise, 1.0))
        fit_error = max(0.0, surprise - condition.fit_budget)
        fit_errors.append(fit_error)

        nest *= condition.nest_decay
        rendered *= 0.96

        if near_boundary:
            collapse_signal = importance - fit_error
            if collapse_signal > 0:
                seq[idx] = -2
                nest += collapse_signal
                collapse_success += 1
                if nest >= 0.08 and rendered <= 0.0:
                    seq[idx] = 0
                    holds += 1
                if rendered > 0.0:
                    retouches += 1
                    rewrite_drift += abs(collapse_signal - rendered) * condition.retouch_gain
                    rendered += condition.retouch_gain * collapse_signal
                elif nest >= condition.write_threshold:
                    seq[idx] = 1
                    writes += 1
                    rendered = nest
                    nest *= 0.55

        if fit_error >= condition.rupture_threshold:
            seq[idx] = 2
            ruptures += 1
            nest = 0.0
            rendered = 0.0
            continue

        if rendered > 0.0 and not near_boundary:
            rendered *= 0.985

        if nest < 0.04 and rendered < 0.04 and not near_boundary and seq[idx] < 0:
            seq[idx] = -1
            fades += 1

    return seq, {
        "writes": float(writes),
        "holds": float(holds),
        "fades": float(fades),
        "ruptures": float(ruptures),
        "retouches": float(retouches),
        "collapse_success": float(collapse_success),
        "rewrite_drift": rewrite_drift / max(retouches, 1.0),
        "mean_fit_error": float(np.mean(fit_errors)) if fit_errors else 0.0,
    }


def evaluate_model(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    writes = diag["writes"]
    holds = diag["holds"]
    fades = diag["fades"]
    ruptures = diag["ruptures"]
    retouches = diag["retouches"]
    total_events = writes + holds + fades + ruptures
    collapse_success = diag["collapse_success"] / max(np.sum(seq >= -2), 1.0)
    hold_to_write = writes / max(holds + writes, 1.0)
    retouch_survival = retouches / max(writes + retouches, 1.0)
    fade_rate = fades / max(total_events, 1.0)
    rupture_rate = ruptures / max(total_events, 1.0)
    rewrite_drift = diag["rewrite_drift"]
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] <= -1))) if len(seq) > 1 else 0.0
    phase_resist = phase_lock_resistance(seq)
    return {
        "write_count": writes,
        "hold_count": holds,
        "fade_count": fades,
        "rupture_count": ruptures,
        "collapse_success": collapse_success,
        "hold_to_write": hold_to_write,
        "retouch_survival": retouch_survival,
        "fade_rate": fade_rate,
        "rupture_rate": rupture_rate,
        "rewrite_drift": rewrite_drift,
        "mean_fit_error": diag["mean_fit_error"],
        "pollution": pollution,
        "phase_lock_resistance": phase_resist,
    }


def composite_score(metrics: dict[str, float]) -> float:
    fit_quality = 1.0 - min(metrics["mean_fit_error"] / 0.6, 1.0)
    drift_quality = 1.0 - min(metrics["rewrite_drift"] / 0.5, 1.0)
    return float(
        0.18 * metrics["phase_lock_resistance"]
        + 0.17 * metrics["hold_to_write"]
        + 0.16 * metrics["retouch_survival"]
        + 0.14 * metrics["collapse_success"]
        + 0.12 * fit_quality
        + 0.09 * drift_quality
        + 0.08 * (1.0 - metrics["rupture_rate"])
        + 0.06 * (1.0 - metrics["fade_rate"])
    )


def plot_flow_summary(rows: list[dict], path: Path) -> None:
    labels = [row["flow"] for row in rows]
    scores = [row["mean_composite"] for row in rows]
    holds = [row["mean_hold_to_write"] for row in rows]
    x = np.arange(len(labels))
    width = 0.35
    plt.figure(figsize=(10, 5))
    plt.bar(x - width / 2, scores, width=width, label="mean composite")
    plt.bar(x + width / 2, holds, width=width, label="hold->write")
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
                        "fit_budget": condition.fit_budget,
                        "importance_weight": condition.importance_weight,
                        "retouch_gain": condition.retouch_gain,
                        "nest_decay": condition.nest_decay,
                        "write_threshold": condition.write_threshold,
                        "rupture_threshold": condition.rupture_threshold,
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
            fit_budget=best["fit_budget"],
            importance_weight=best["importance_weight"],
            retouch_gain=best["retouch_gain"],
            nest_decay=best["nest_decay"],
            write_threshold=best["write_threshold"],
            rupture_threshold=best["rupture_threshold"],
        )
        seq, _ = build_sequence(best["alpha"], cond)
        density = density_random_surrogate(seq)
        density_metrics = evaluate_model(
            density,
            {
                "writes": float(np.sum(density == 1)),
                "holds": float(np.sum(density == 0)),
                "fades": float(np.sum(density == -1)),
                "ruptures": float(np.sum(density == 2)),
                "retouches": 0.0,
                "collapse_success": 0.0,
                "rewrite_drift": 0.0,
                "mean_fit_error": 0.0,
            },
        )
        mean_composite = float(np.mean([row["composite_score"] for row in subset]))
        flow_rows.append(
            {
                "flow": flow.name,
                "family": flow.family,
                "best_composite": best["composite_score"],
                "mean_composite": mean_composite,
                "mean_hold_to_write": float(np.mean([row["hold_to_write"] for row in subset])),
                "mean_retouch_survival": float(np.mean([row["retouch_survival"] for row in subset])),
                "mean_rupture_rate": float(np.mean([row["rupture_rate"] for row in subset])),
                "mean_rewrite_drift": float(np.mean([row["rewrite_drift"] for row in subset])),
                "mean_density_gap": mean_composite - composite_score(density_metrics),
            }
        )

    ranked = sorted(flow_rows, key=lambda row: row["mean_composite"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(flow_rows, OUT / "flow_summary.csv")
    plot_flow_summary(flow_rows, OUT / "flow_summary.png")

    best = ranked[0]
    golden = next(row for row in flow_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v26 - Reconsolidating Nest Collapse

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by mean composite: `{best['flow']}` with `{best['mean_composite']:.3f}`

Golden result:
- mean composite: `{golden['mean_composite']:.3f}`
- hold->write: `{golden['mean_hold_to_write']:.3f}`
- retouch survival: `{golden['mean_retouch_survival']:.3f}`
- rupture rate: `{golden['mean_rupture_rate']:.3f}`
- density gap: `{golden['mean_density_gap']:.3f}`

Interpretation:
- This panel tests whether memory behaves like a reconsolidating nest: collapse, hold, render, retouch, rewrite.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by mean composite: {best['flow']}")
    print(f"golden mean composite: {golden['mean_composite']:.3f}")
    print(f"golden hold->write: {golden['mean_hold_to_write']:.3f}")
    print(f"golden retouch survival: {golden['mean_retouch_survival']:.3f}")
    print(f"golden rupture rate: {golden['mean_rupture_rate']:.3f}")
    print(f"golden density gap: {golden['mean_density_gap']:.3f}")


if __name__ == "__main__":
    main()
