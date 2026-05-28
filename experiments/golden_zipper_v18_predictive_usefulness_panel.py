#!/usr/bin/env python3
"""v18 predictive usefulness panel.

Toy telemetry only. Not physics evidence. Not proof of GHP.

This panel asks whether a surprise should count as memory only when admitting it
improves short-horizon prediction. Large surprise is allowed to become durable
if it helps future prediction rather than merely being novel.
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
OUT = ROOT / "golden_zipper_v18_outputs"

SEED = 20260520
RNG = np.random.default_rng(SEED)

LENGTH = 2048
OFFSET_GRID = np.arange(-0.024, 0.0241, 0.012)
WINDOW_WIDTHS = [0.18, 0.24]
BETAS = [0.0, 0.011]
LEARNING_RATES = [0.035, 0.07, 0.12]
ASSIMILATION_RATES = [0.08, 0.16, 0.28]
SURPRISE_LOW = [0.06, 0.12]
SURPRISE_HIGH = [0.32, 0.48]
UTILITY_THRESHOLDS = [0.01, 0.025, 0.05]
LOOKAHEADS = [5, 13, 21]
WRITE_THRESHOLDS = [0.48, 0.62]
MAX_CONDITIONS = 60


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
    assimilation_rate: float
    surprise_low: float
    surprise_high: float
    utility_threshold: float
    lookahead: int
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
        ModelSpec("assimilated_surprise", "Assimilated Surprise"),
        ModelSpec("predictive_usefulness", "Predictive Usefulness"),
        ModelSpec("predictive_usefulness_witness", "Predictive Usefulness + Witness"),
    ]


def build_conditions() -> list[Condition]:
    full = [
        Condition(
            window_width=window_width,
            beta=beta,
            learning_rate=learning_rate,
            assimilation_rate=assimilation_rate,
            surprise_low=surprise_low,
            surprise_high=surprise_high,
            utility_threshold=utility_threshold,
            lookahead=lookahead,
            write_threshold=write_threshold,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for learning_rate in LEARNING_RATES
        for assimilation_rate in ASSIMILATION_RATES
        for surprise_low in SURPRISE_LOW
        for surprise_high in SURPRISE_HIGH
        for utility_threshold in UTILITY_THRESHOLDS
        for lookahead in LOOKAHEADS
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


def predict_future_error(values: np.ndarray, idx: int, prediction: float, updated_prediction: float, lookahead: int) -> float:
    end = min(len(values), idx + lookahead + 1)
    future = values[idx + 1 : end]
    if len(future) == 0:
        return 0.0
    old_error = float(np.mean(np.abs(future - prediction)))
    new_error = float(np.mean(np.abs(future - updated_prediction)))
    return old_error - new_error


def build_sequence(model: str, alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    intensity, near_both = build_features(alpha, condition)
    seq = np.full(LENGTH, -1, dtype=np.int8)
    prediction = 0.25
    belief = 0.50
    witness_charge = 0.0
    admitted = 0
    rejected_low = 0
    rejected_useless = 0
    writes = 0
    witnesses = 0
    total_utility = 0.0
    useful_writes = 0

    for idx, value in enumerate(intensity):
        surprise = abs(value - prediction)
        updated_prediction = (1.0 - condition.learning_rate) * prediction + condition.learning_rate * value
        tentative_belief = (1.0 - condition.assimilation_rate) * belief + condition.assimilation_rate * value
        utility = predict_future_error(intensity, idx, prediction, updated_prediction, condition.lookahead)
        witness_charge *= 0.88

        if not near_both[idx]:
            prediction = updated_prediction
            belief = 0.98 * belief + 0.02 * tentative_belief
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
        elif model == "assimilated_surprise":
            if surprise < condition.surprise_low:
                rejected_low += 1
            else:
                admitted += 1
                seq[idx] = 1 if value >= condition.write_threshold else 0
        elif model in {"predictive_usefulness", "predictive_usefulness_witness"}:
            if surprise < condition.surprise_low:
                rejected_low += 1
            elif utility < condition.utility_threshold:
                rejected_useless += 1
                seq[idx] = 0 if model == "predictive_usefulness_witness" else -1
            else:
                admitted += 1
                total_utility += utility
                if model == "predictive_usefulness":
                    seq[idx] = 1 if value >= condition.write_threshold or surprise >= condition.surprise_high else 0
                else:
                    witness_charge = max(witness_charge, 0.35) + 0.55 * utility + 0.35 * min(surprise, condition.surprise_high)
                    seq[idx] = 1 if value >= condition.write_threshold or witness_charge >= 0.85 else 0
                    if seq[idx] == 1:
                        witness_charge = 0.0

        if seq[idx] == 1:
            writes += 1
            if utility > 0:
                useful_writes += 1
        elif seq[idx] == 0:
            witnesses += 1

        if seq[idx] >= 0 or model in {"raw_write", "assimilated_surprise"}:
            prediction = updated_prediction
            belief = tentative_belief
        else:
            prediction = 0.995 * prediction + 0.005 * updated_prediction
            belief = 0.995 * belief + 0.005 * tentative_belief

    return seq, {
        "admitted": float(admitted),
        "rejected_low": float(rejected_low),
        "rejected_useless": float(rejected_useless),
        "writes": float(writes),
        "witnesses": float(witnesses),
        "total_utility": float(total_utility),
        "useful_writes": float(useful_writes),
    }


def evaluate_model(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    total_seen = diag["admitted"] + diag["rejected_low"] + diag["rejected_useless"]
    write_count = float(np.sum(seq == 1))
    witness_count = float(np.sum(seq == 0))
    admission_rate = diag["admitted"] / max(total_seen, 1.0)
    write_rate = write_count / max(diag["admitted"], 1.0)
    witness_rate = witness_count / max(diag["admitted"] + diag["rejected_useless"], 1.0)
    useless_reject_rate = diag["rejected_useless"] / max(total_seen, 1.0)
    useful_write_rate = diag["useful_writes"] / max(write_count, 1.0)
    mean_utility = diag["total_utility"] / max(diag["admitted"], 1.0)
    delayed_retention = write_count / max(write_count + witness_count, 1.0)
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] == -1))) if len(seq) > 1 else 0.0
    phase_resist = phase_lock_resistance(seq)
    return {
        "write_count": write_count,
        "witness_count": witness_count,
        "admission_rate": admission_rate,
        "write_rate": write_rate,
        "witness_rate": witness_rate,
        "useless_reject_rate": useless_reject_rate,
        "useful_write_rate": useful_write_rate,
        "mean_utility": mean_utility,
        "delayed_retention": delayed_retention,
        "pollution": pollution,
        "phase_lock_resistance": phase_resist,
    }


def composite_score(metrics: dict[str, float]) -> float:
    balanced_admission = 1.0 - min(abs(metrics["admission_rate"] - 0.42) / 0.42, 1.0)
    balanced_write = 1.0 - min(abs(metrics["write_rate"] - 0.55) / 0.55, 1.0)
    utility_score = min(max(metrics["mean_utility"] / 0.08, 0.0), 1.0)
    return float(
        0.18 * metrics["phase_lock_resistance"]
        + 0.16 * metrics["delayed_retention"]
        + 0.15 * metrics["useful_write_rate"]
        + 0.14 * utility_score
        + 0.12 * balanced_admission
        + 0.10 * balanced_write
        + 0.09 * (1.0 - metrics["pollution"])
        + 0.06 * metrics["witness_rate"]
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
                            "assimilation_rate": condition.assimilation_rate,
                            "surprise_low": condition.surprise_low,
                            "surprise_high": condition.surprise_high,
                            "utility_threshold": condition.utility_threshold,
                            "lookahead": condition.lookahead,
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
            assimilation_rate=best["assimilation_rate"],
            surprise_low=best["surprise_low"],
            surprise_high=best["surprise_high"],
            utility_threshold=best["utility_threshold"],
            lookahead=best["lookahead"],
            write_threshold=best["write_threshold"],
        )
        seq, _ = build_sequence(model.name, best["alpha"], cond)
        surrogate = density_random_surrogate(seq)
        surrogate_diag = {
            "admitted": float(np.sum(surrogate >= 0)),
            "rejected_low": 0.0,
            "rejected_useless": 0.0,
            "writes": float(np.sum(surrogate == 1)),
            "witnesses": float(np.sum(surrogate == 0)),
            "total_utility": 0.0,
            "useful_writes": 0.0,
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
                "mean_useful_write_rate": float(np.mean([row["useful_write_rate"] for row in subset])),
                "mean_utility": float(np.mean([row["mean_utility"] for row in subset])),
                "mean_surrogate_gap": mean_composite - composite_score(surrogate_metrics),
            }
        )

    ranked = sorted(model_rows, key=lambda row: row["mean_composite"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(model_rows, OUT / "model_summary.csv")
    plot_model_summary(model_rows, OUT / "model_summary.png")

    best = ranked[0]
    raw = next(row for row in model_rows if row["model"] == "raw_write")
    surprise = next(row for row in model_rows if row["model"] == "surprise_only")
    predictive = next(row for row in model_rows if row["model"] == "predictive_usefulness")
    witness = next(row for row in model_rows if row["model"] == "predictive_usefulness_witness")

    report = f"""# Golden Zipper v18 - Predictive Usefulness Panel

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best model by mean composite: `{best['model']}` with `{best['mean_composite']:.3f}`

Key comparisons:
- `raw_write` mean composite: `{raw['mean_composite']:.3f}`
- `surprise_only` mean composite: `{surprise['mean_composite']:.3f}`
- `predictive_usefulness` mean composite: `{predictive['mean_composite']:.3f}`
- `predictive_usefulness_witness` mean composite: `{witness['mean_composite']:.3f}`
- `predictive_usefulness_witness` mean surrogate gap: `{witness['mean_surrogate_gap']:.3f}`

Interpretation:
- This panel asks whether a surprising appearance becomes memory when it improves future prediction.
- Success would mean predictive-usefulness models beat raw and surprise-only controls while keeping a positive surrogate gap.
- Failure means the current future-utility rule is not yet a clean write primitive.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best model by mean composite: {best['model']}")
    print(f"raw_write mean composite: {raw['mean_composite']:.3f}")
    print(f"surprise_only mean composite: {surprise['mean_composite']:.3f}")
    print(f"predictive_usefulness mean composite: {predictive['mean_composite']:.3f}")
    print(f"predictive_usefulness_witness mean composite: {witness['mean_composite']:.3f}")
    print(f"predictive_usefulness_witness surrogate gap: {witness['mean_surrogate_gap']:.3f}")


if __name__ == "__main__":
    main()
