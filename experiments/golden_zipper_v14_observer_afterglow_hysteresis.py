#!/usr/bin/env python3
"""v14 observer afterglow hysteresis panel for delayed two-light alignment."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v14_outputs"

SEED = 20260520
RNG = np.random.default_rng(SEED)

OFFSET_GRID = np.arange(-0.036, 0.0361, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
BETAS = [0.0, 0.011]
LENGTH = 4096
MAX_ALIGNMENT_AGES = [4, 8, 13]
TRACE_DECAYS = [0.84, 0.92]
TRACE_STRENGTHS = [0.55, 0.85]
REFRESH_BOOSTS = [0.0, 0.14, 0.24]


@dataclass(frozen=True)
class AnchorSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class Condition:
    window_width: float
    beta: float
    max_alignment_age: int
    trace_decay: float
    trace_strength: float
    refresh_boost: float


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
        AnchorSpec("golden", 1.0 / PHI, "phi"),
        AnchorSpec("fib_13_21", 13.0 / 21.0, "rational"),
        AnchorSpec("noble_1", continued_fraction_value([2, 3], tail_ones=18), "noble"),
        AnchorSpec("bounded_cf_2", continued_fraction_value([1, 2, 3, 1, 2, 3], tail_ones=14), "bounded_cf"),
        AnchorSpec("random_irrat_1", continued_fraction_value([7, 2, 9, 3, 5, 4, 8, 6], tail_ones=8), "random_irrational"),
    ]


def build_models() -> list[ModelSpec]:
    return [
        ModelSpec("click_only", "Click Only"),
        ModelSpec("glow_only", "Glow Only"),
        ModelSpec("click_afterglow", "Click + Afterglow"),
        ModelSpec("click_afterglow_refresh", "Click + Afterglow + Refresh"),
    ]


def build_conditions() -> list[Condition]:
    return [
        Condition(
            window_width=window_width,
            beta=beta,
            max_alignment_age=max_alignment_age,
            trace_decay=trace_decay,
            trace_strength=trace_strength,
            refresh_boost=refresh_boost,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for max_alignment_age in MAX_ALIGNMENT_AGES
        for trace_decay in TRACE_DECAYS
        for trace_strength in TRACE_STRENGTHS
        for refresh_boost in REFRESH_BOOSTS
    ]


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


def observer_center(condition: Condition) -> np.ndarray:
    n = np.arange(LENGTH, dtype=float)
    return wrap01(0.5 + condition.beta * n)


def sphere_projection(theta: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.cos(2.0 * math.pi * theta) * np.cos(math.pi * (phi - 0.5))
    y = np.sin(2.0 * math.pi * theta) * np.cos(math.pi * (phi - 0.5))
    z = np.sin(math.pi * (phi - 0.5))
    azimuth = wrap01(np.arctan2(y, x) / (2.0 * math.pi))
    elevation = np.arctan2(z, np.sqrt(x * x + y * y))
    return azimuth, elevation


def build_alignment_trace(alpha: float, condition: Condition) -> tuple[np.ndarray, np.ndarray]:
    n = np.arange(LENGTH, dtype=float)
    center = observer_center(condition)
    theta1 = wrap01(alpha * n)
    phi1 = wrap01((alpha / PHI) * n)
    theta2 = wrap01((alpha + condition.beta + 0.0618) * n + 0.17)
    phi2 = wrap01((alpha / (PHI * PHI) + 0.13) * n + 0.41)
    az1, _ = sphere_projection(theta1, phi1)
    az2, _ = sphere_projection(theta2, phi2)
    signed1 = wrap_signed(az1 - center)
    signed2 = wrap_signed(az2 - center)
    alignment = np.abs(wrap_signed(az1 - az2))
    near_both = (np.abs(signed1) < 0.58 * condition.window_width) & (np.abs(signed2) < 0.58 * condition.window_width)
    return alignment, near_both


def build_sequence(model: str, alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    alignment, near_both = build_alignment_trace(alpha, condition)
    witness_thresh = 0.28 * condition.window_width
    click_thresh = 0.12 * condition.window_width

    seq = np.full(LENGTH, -1, dtype=np.int8)
    glow = 0.0
    glow_age = 0
    clicks = 0
    refreshed = 0
    overwrites = 0
    witness_total = 0
    glow_ticks = 0

    for idx, gap in enumerate(alignment):
        glow *= condition.trace_decay
        if glow > 0.02:
            glow_age += 1
            glow_ticks += 1
        else:
            glow = 0.0
            glow_age = 0

        if not near_both[idx]:
            if glow > 0.0 and model in {"glow_only", "click_afterglow", "click_afterglow_refresh"}:
                seq[idx] = 0
            continue

        if gap < witness_thresh:
            witness_total += 1
            seq[idx] = 0

        if model == "click_only":
            if gap < click_thresh:
                seq[idx] = 1
                clicks += 1
            continue

        if model == "glow_only":
            if gap < witness_thresh:
                glow = max(glow, condition.trace_strength)
            if glow >= 0.7 and glow_age <= condition.max_alignment_age:
                seq[idx] = 1
                clicks += 1
                glow *= 0.65
            continue

        if model == "click_afterglow":
            if gap < click_thresh:
                seq[idx] = 1
                clicks += 1
                glow = max(glow, condition.trace_strength)
                glow_age = 0
            elif glow >= 0.72 and glow_age <= condition.max_alignment_age:
                seq[idx] = 1
                glow *= 0.60
            elif gap < witness_thresh:
                glow = max(glow, 0.4 * condition.trace_strength)
            continue

        if model == "click_afterglow_refresh":
            if gap < click_thresh:
                seq[idx] = 1
                clicks += 1
                if glow > 0.25:
                    refreshed += 1
                glow = max(glow, condition.trace_strength + condition.refresh_boost)
                glow_age = 0
            elif glow >= 0.68 and glow_age <= condition.max_alignment_age:
                seq[idx] = 1
                if gap < witness_thresh:
                    refreshed += 1
                    glow = min(1.3, glow + 0.25 + condition.refresh_boost)
                    glow_age = 0
                else:
                    glow *= 0.72
            elif gap < witness_thresh:
                if glow > 0.45:
                    refreshed += 1
                elif glow > 0.08:
                    overwrites += 1
                glow = max(glow, 0.45 * condition.trace_strength + condition.refresh_boost)

    return seq, {
        "clicks": float(clicks),
        "refreshed": float(refreshed),
        "overwrites": float(overwrites),
        "witness_total": float(witness_total),
        "glow_ticks": float(glow_ticks),
    }


def evaluate_model(seq: np.ndarray, diag: dict[str, float], condition: Condition) -> dict[str, float]:
    writes = float(np.sum(seq == 1))
    witnesses = float(np.sum(seq == 0))
    delayed_retention = writes / max(writes + witnesses, 1.0)
    click_rate = diag["clicks"] / max(diag["witness_total"], 1.0)
    refresh_rate = diag["refreshed"] / max(diag["witness_total"], 1.0)
    overwrite_rate = diag["overwrites"] / max(diag["witness_total"], 1.0)
    glow_persistence = diag["glow_ticks"] / float(LENGTH)
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] == -1))) if len(seq) > 1 else 0.0
    phase_resist = phase_lock_resistance(seq)
    return {
        "write_count": writes,
        "witness_count": witnesses,
        "delayed_retention": delayed_retention,
        "click_rate": click_rate,
        "refresh_rate": refresh_rate,
        "overwrite_rate": overwrite_rate,
        "glow_persistence": glow_persistence,
        "pollution": pollution,
        "phase_lock_resistance": phase_resist,
    }


def composite_score(metrics: dict[str, float]) -> float:
    balance_glow = 1.0 - min(abs(metrics["glow_persistence"] - 0.18) / 0.18, 1.0)
    return float(
        0.25 * metrics["phase_lock_resistance"]
        + 0.20 * metrics["delayed_retention"]
        + 0.18 * metrics["click_rate"]
        + 0.14 * metrics["refresh_rate"]
        + 0.12 * (1.0 - metrics["pollution"])
        + 0.07 * balance_glow
        + 0.04 * (1.0 - metrics["overwrite_rate"])
    )


def plot_model_summary(rows: list[dict], path: Path) -> None:
    labels = [row["model"] for row in rows]
    comps = [row["mean_composite"] for row in rows]
    gaps = [row["mean_surrogate_gap"] for row in rows]
    x = np.arange(len(labels))
    width = 0.35
    plt.figure(figsize=(10, 5))
    plt.bar(x - width / 2, comps, width=width, label="mean composite")
    plt.bar(x + width / 2, gaps, width=width, label="mean surrogate gap")
    plt.xticks(x, labels, rotation=18)
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    models = build_models()
    conditions = build_conditions()

    direct_rows: list[dict] = []
    for model in models:
        print(f"model: {model.name}")
        for anchor in anchors:
            for condition in conditions:
                for offset in OFFSET_GRID:
                    alpha = anchor.alpha + float(offset)
                    if not (0.0 < alpha < 1.0):
                        continue
                    seq, diag = build_sequence(model.name, alpha, condition)
                    metrics = evaluate_model(seq, diag, condition)
                    direct_rows.append(
                        {
                            "model": model.name,
                            "anchor": anchor.name,
                            "family": anchor.family,
                            "alpha": alpha,
                            "offset": float(offset),
                            "window_width": condition.window_width,
                            "beta": condition.beta,
                            "max_alignment_age": condition.max_alignment_age,
                            "trace_decay": condition.trace_decay,
                            "trace_strength": condition.trace_strength,
                            "refresh_boost": condition.refresh_boost,
                            **metrics,
                            "composite_score": composite_score(metrics),
                        }
                    )

    model_rows: list[dict] = []
    for model in models:
        subset = [row for row in direct_rows if row["model"] == model.name]
        best = max(subset, key=lambda row: row["composite_score"])
        cond = Condition(
            window_width=best["window_width"],
            beta=best["beta"],
            max_alignment_age=best["max_alignment_age"],
            trace_decay=best["trace_decay"],
            trace_strength=best["trace_strength"],
            refresh_boost=best["refresh_boost"],
        )
        seq, diag = build_sequence(model.name, best["alpha"], cond)
        surrogate = density_random_surrogate(seq)
        surrogate_metrics = evaluate_model(
            surrogate,
            {"clicks": 0.0, "refreshed": 0.0, "overwrites": 0.0, "witness_total": float(np.sum(surrogate >= 0)), "glow_ticks": 0.0},
            cond,
        )
        model_rows.append(
            {
                "model": model.name,
                "best_anchor": best["anchor"],
                "best_composite": best["composite_score"],
                "mean_composite": float(np.mean([row["composite_score"] for row in subset])),
                "mean_click_rate": float(np.mean([row["click_rate"] for row in subset])),
                "mean_refresh_rate": float(np.mean([row["refresh_rate"] for row in subset])),
                "mean_glow_persistence": float(np.mean([row["glow_persistence"] for row in subset])),
                "mean_surrogate_gap": float(np.mean([row["composite_score"] for row in subset])) - composite_score(surrogate_metrics),
            }
        )

    ranked = sorted(model_rows, key=lambda row: row["mean_composite"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(model_rows, OUT / "model_summary.csv")
    plot_model_summary(model_rows, OUT / "model_summary.png")

    best = ranked[0]
    click_only = next(row for row in model_rows if row["model"] == "click_only")
    afterglow = next(row for row in model_rows if row["model"] == "click_afterglow")
    refresh = next(row for row in model_rows if row["model"] == "click_afterglow_refresh")

    report = f"""# Golden Zipper v14 - Observer Afterglow Hysteresis

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best model by mean composite: `{best['model']}` with `{best['mean_composite']:.3f}`

Key comparisons:
- `click_only` mean composite: `{click_only['mean_composite']:.3f}`
- `click_afterglow` mean composite: `{afterglow['mean_composite']:.3f}`
- `click_afterglow_refresh` mean composite: `{refresh['mean_composite']:.3f}`
- `click_afterglow_refresh` mean surrogate gap: `{refresh['mean_surrogate_gap']:.3f}`

Interpretation:
- If `click_afterglow` beats `click_only`, the observer seems to benefit from a short witness trace.
- If `click_afterglow_refresh` beats both, then memory behaves more like click-plus-refresh than either pure click or pure accumulation.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best model by mean composite: {best['model']}")
    print(f"click_only mean composite: {click_only['mean_composite']:.3f}")
    print(f"click_afterglow mean composite: {afterglow['mean_composite']:.3f}")
    print(f"click_afterglow_refresh mean composite: {refresh['mean_composite']:.3f}")
    print(f"click_afterglow_refresh surrogate gap: {refresh['mean_surrogate_gap']:.3f}")


if __name__ == "__main__":
    main()
