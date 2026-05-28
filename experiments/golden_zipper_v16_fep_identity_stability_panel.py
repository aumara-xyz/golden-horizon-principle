#!/usr/bin/env python3
"""v16 FEP-style identity stability panel.

Toy telemetry only. Not physics evidence. Not proof of GHP.

This panel gives the observer a simple identity/homeostasis variable. An
appearance is useful only if it is surprising enough to notice while preserving
the observer's stable trajectory.
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
OUT = ROOT / "golden_zipper_v16_outputs"

SEED = 20260520
RNG = np.random.default_rng(SEED)

LENGTH = 4096
OFFSET_GRID = np.arange(-0.03, 0.0301, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
BETAS = [0.0, 0.011]
LEARNING_RATES = [0.035, 0.07, 0.12]
IDENTITY_ELASTICITIES = [0.015, 0.035, 0.065]
SURPRISE_LOW = [0.06, 0.12]
SURPRISE_HIGH = [0.32, 0.48]
IDENTITY_TOLERANCES = [0.12, 0.20, 0.30]
WRITE_THRESHOLDS = [0.48, 0.62]
MAX_CONDITIONS = 216


@dataclass(frozen=True)
class AnchorSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class Condition:
    window_width: float
    beta: float
    learning_rate: float
    identity_elasticity: float
    surprise_low: float
    surprise_high: float
    identity_tolerance: float
    write_threshold: float


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
        AnchorSpec("silver", math.sqrt(2.0) - 1.0, "metallic"),
    ]


def build_models() -> list[ModelSpec]:
    return [
        ModelSpec("raw_write", "Raw Write"),
        ModelSpec("surprise_only", "Surprise Only"),
        ModelSpec("identity_only", "Identity Only"),
        ModelSpec("identity_bandpass", "Identity Band-Pass"),
        ModelSpec("identity_bandpass_witness", "Identity Band-Pass + Witness"),
    ]


def build_conditions() -> list[Condition]:
    full = [
        Condition(
            window_width=window_width,
            beta=beta,
            learning_rate=learning_rate,
            identity_elasticity=identity_elasticity,
            surprise_low=surprise_low,
            surprise_high=surprise_high,
            identity_tolerance=identity_tolerance,
            write_threshold=write_threshold,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for learning_rate in LEARNING_RATES
        for identity_elasticity in IDENTITY_ELASTICITIES
        for surprise_low in SURPRISE_LOW
        for surprise_high in SURPRISE_HIGH
        for identity_tolerance in IDENTITY_TOLERANCES
        for write_threshold in WRITE_THRESHOLDS
        if surprise_low < surprise_high
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


def build_features(alpha: float, condition: Condition) -> tuple[np.ndarray, np.ndarray]:
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
    intensity = np.clip(1.0 - alignment / max(0.5 * condition.window_width, 1e-9), 0.0, 1.0)
    return intensity, near_both


def build_sequence(model: str, alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    intensity, near_both = build_features(alpha, condition)
    seq = np.full(LENGTH, -1, dtype=np.int8)
    prediction = 0.25
    identity = 0.50
    witness_charge = 0.0
    admitted = 0
    rejected_low = 0
    rejected_high = 0
    identity_breaks = 0
    writes = 0
    witnesses = 0
    identity_errors: list[float] = []

    for idx, value in enumerate(intensity):
        surprise = abs(value - prediction)
        prediction = (1.0 - condition.learning_rate) * prediction + condition.learning_rate * value
        projected_identity = (1.0 - condition.identity_elasticity) * identity + condition.identity_elasticity * value
        identity_error = abs(projected_identity - 0.5)
        identity_errors.append(identity_error)
        witness_charge *= 0.88

        if not near_both[idx]:
            identity = projected_identity
            continue

        if model == "raw_write":
            admitted += 1
            seq[idx] = 1 if value >= condition.write_threshold else 0
        elif model == "surprise_only":
            if surprise >= condition.surprise_high:
                admitted += 1
                seq[idx] = 1
            else:
                rejected_low += 1
        elif model == "identity_only":
            if identity_error <= condition.identity_tolerance:
                admitted += 1
                seq[idx] = 1 if value >= condition.write_threshold else 0
            else:
                identity_breaks += 1
        elif model in {"identity_bandpass", "identity_bandpass_witness"}:
            if surprise < condition.surprise_low:
                rejected_low += 1
            elif surprise > condition.surprise_high:
                rejected_high += 1
            elif identity_error > condition.identity_tolerance:
                identity_breaks += 1
            else:
                admitted += 1
                if model == "identity_bandpass":
                    seq[idx] = 1 if value >= condition.write_threshold else 0
                else:
                    witness_charge = max(witness_charge, 0.35) + 0.45 * value + 0.25 * surprise
                    seq[idx] = 1 if value >= condition.write_threshold or witness_charge >= 1.0 else 0
                    if seq[idx] == 1:
                        witness_charge = 0.0

        if seq[idx] == 1:
            writes += 1
        elif seq[idx] == 0:
            witnesses += 1

        if seq[idx] >= 0:
            identity = projected_identity
        else:
            identity = (0.995 * identity) + 0.005 * 0.5

    return seq, {
        "admitted": float(admitted),
        "rejected_low": float(rejected_low),
        "rejected_high": float(rejected_high),
        "identity_breaks": float(identity_breaks),
        "writes": float(writes),
        "witnesses": float(witnesses),
        "mean_identity_error": float(np.mean(identity_errors)),
    }


def evaluate_model(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    total_seen = diag["admitted"] + diag["rejected_low"] + diag["rejected_high"] + diag["identity_breaks"]
    write_count = float(np.sum(seq == 1))
    witness_count = float(np.sum(seq == 0))
    admission_rate = diag["admitted"] / max(total_seen, 1.0)
    write_rate = write_count / max(diag["admitted"], 1.0)
    witness_rate = witness_count / max(diag["admitted"], 1.0)
    overload_rate = diag["rejected_high"] / max(total_seen, 1.0)
    ignored_rate = diag["rejected_low"] / max(total_seen, 1.0)
    identity_break_rate = diag["identity_breaks"] / max(total_seen, 1.0)
    delayed_retention = write_count / max(write_count + witness_count, 1.0)
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] == -1))) if len(seq) > 1 else 0.0
    phase_resist = phase_lock_resistance(seq)
    return {
        "write_count": write_count,
        "witness_count": witness_count,
        "admission_rate": admission_rate,
        "write_rate": write_rate,
        "witness_rate": witness_rate,
        "overload_rate": overload_rate,
        "ignored_rate": ignored_rate,
        "identity_break_rate": identity_break_rate,
        "mean_identity_error": diag["mean_identity_error"],
        "delayed_retention": delayed_retention,
        "pollution": pollution,
        "phase_lock_resistance": phase_resist,
    }


def composite_score(metrics: dict[str, float]) -> float:
    balanced_admission = 1.0 - min(abs(metrics["admission_rate"] - 0.42) / 0.42, 1.0)
    balanced_write = 1.0 - min(abs(metrics["write_rate"] - 0.55) / 0.55, 1.0)
    identity_stability = 1.0 - min(metrics["mean_identity_error"] / 0.30, 1.0)
    return float(
        0.20 * metrics["phase_lock_resistance"]
        + 0.18 * metrics["delayed_retention"]
        + 0.15 * balanced_admission
        + 0.13 * balanced_write
        + 0.13 * identity_stability
        + 0.10 * (1.0 - metrics["pollution"])
        + 0.07 * (1.0 - metrics["identity_break_rate"])
        + 0.04 * metrics["witness_rate"]
    )


def plot_model_summary(rows: list[dict], path: Path) -> None:
    labels = [row["model"] for row in rows]
    comps = [row["mean_composite"] for row in rows]
    gaps = [row["mean_surrogate_gap"] for row in rows]
    x = np.arange(len(labels))
    width = 0.35
    plt.figure(figsize=(11, 5))
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
                    metrics = evaluate_model(seq, diag)
                    direct_rows.append(
                        {
                            "model": model.name,
                            "anchor": anchor.name,
                            "family": anchor.family,
                            "alpha": alpha,
                            "offset": float(offset),
                            "window_width": condition.window_width,
                            "beta": condition.beta,
                            "learning_rate": condition.learning_rate,
                            "identity_elasticity": condition.identity_elasticity,
                            "surprise_low": condition.surprise_low,
                            "surprise_high": condition.surprise_high,
                            "identity_tolerance": condition.identity_tolerance,
                            "write_threshold": condition.write_threshold,
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
            learning_rate=best["learning_rate"],
            identity_elasticity=best["identity_elasticity"],
            surprise_low=best["surprise_low"],
            surprise_high=best["surprise_high"],
            identity_tolerance=best["identity_tolerance"],
            write_threshold=best["write_threshold"],
        )
        seq, _ = build_sequence(model.name, best["alpha"], cond)
        surrogate = density_random_surrogate(seq)
        surrogate_diag = {
            "admitted": float(np.sum(surrogate >= 0)),
            "rejected_low": 0.0,
            "rejected_high": 0.0,
            "identity_breaks": 0.0,
            "writes": float(np.sum(surrogate == 1)),
            "witnesses": float(np.sum(surrogate == 0)),
            "mean_identity_error": 0.0,
        }
        surrogate_metrics = evaluate_model(surrogate, surrogate_diag)
        mean_composite = float(np.mean([row["composite_score"] for row in subset]))
        model_rows.append(
            {
                "model": model.name,
                "best_anchor": best["anchor"],
                "best_composite": best["composite_score"],
                "mean_composite": mean_composite,
                "mean_admission_rate": float(np.mean([row["admission_rate"] for row in subset])),
                "mean_write_rate": float(np.mean([row["write_rate"] for row in subset])),
                "mean_identity_error": float(np.mean([row["mean_identity_error"] for row in subset])),
                "mean_identity_break_rate": float(np.mean([row["identity_break_rate"] for row in subset])),
                "mean_surrogate_gap": mean_composite - composite_score(surrogate_metrics),
            }
        )

    ranked = sorted(model_rows, key=lambda row: row["mean_composite"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(model_rows, OUT / "model_summary.csv")
    plot_model_summary(model_rows, OUT / "model_summary.png")

    best = ranked[0]
    raw = next(row for row in model_rows if row["model"] == "raw_write")
    band = next(row for row in model_rows if row["model"] == "identity_bandpass")
    witness = next(row for row in model_rows if row["model"] == "identity_bandpass_witness")

    report = f"""# Golden Zipper v16 - FEP Identity Stability Panel

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best model by mean composite: `{best['model']}` with `{best['mean_composite']:.3f}`

Key comparisons:
- `raw_write` mean composite: `{raw['mean_composite']:.3f}`
- `identity_bandpass` mean composite: `{band['mean_composite']:.3f}`
- `identity_bandpass_witness` mean composite: `{witness['mean_composite']:.3f}`
- `identity_bandpass_witness` mean surrogate gap: `{witness['mean_surrogate_gap']:.3f}`

Interpretation:
- This panel asks whether an observer writes better when it has something like identity/homeostasis to preserve.
- Success would mean identity-aware admission beats raw/surprise-only controls and keeps a positive surrogate gap.
- Failure means the current identity rule is not yet a clean write primitive.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best model by mean composite: {best['model']}")
    print(f"raw_write mean composite: {raw['mean_composite']:.3f}")
    print(f"identity_bandpass mean composite: {band['mean_composite']:.3f}")
    print(f"identity_bandpass_witness mean composite: {witness['mean_composite']:.3f}")
    print(f"identity_bandpass_witness surrogate gap: {witness['mean_surrogate_gap']:.3f}")


if __name__ == "__main__":
    main()
