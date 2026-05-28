#!/usr/bin/env python3
"""v21 revision ablation panel.

Toy telemetry only. Not physics evidence. Not proof of GHP.

This panel attacks the v19/v20 result by removing direct reward for revision
rate/size. Model revision only wins if downstream behavior improves.
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
OUT = ROOT / "golden_zipper_v21_outputs"

SEED = 20260520
RNG = np.random.default_rng(SEED)

LENGTH = 2048
OFFSET_GRID = np.arange(-0.024, 0.0241, 0.012)
WINDOW_WIDTHS = [0.16, 0.22, 0.30]
BETAS = [0.0, 0.007, 0.017]
LEARNING_RATES = [0.025, 0.06, 0.11]
MODEL_RATES = [0.035, 0.08, 0.17]
SURPRISE_HIGH = [0.24, 0.36, 0.52]
REVISION_THRESHOLDS = [0.025, 0.055, 0.10]
COHERENCE_LIMITS = [0.18, 0.32, 0.55]
WRITE_THRESHOLDS = [0.44, 0.58, 0.70]
MAX_CONDITIONS = 120


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
    model_rate: float
    surprise_high: float
    revision_threshold: float
    coherence_limit: float
    write_threshold: float


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
        AnchorSpec("silver", math.sqrt(2.0) - 1.0, "metallic"),
        AnchorSpec("fib_13_21", 13.0 / 21.0, "rational"),
        AnchorSpec("noble_1", continued_fraction_value([2, 3], tail_ones=18), "noble"),
        AnchorSpec("bounded_cf_2", continued_fraction_value([1, 2, 3, 1, 2, 3], tail_ones=14), "bounded_cf"),
        AnchorSpec("random_cf_1", continued_fraction_value([7, 2, 9, 3, 5, 4], tail_ones=8), "random_cf"),
        AnchorSpec("pi_mod1", math.pi % 1.0, "constant"),
    ]


def build_conditions() -> list[Condition]:
    full = [
        Condition(
            window_width=window_width,
            beta=beta,
            learning_rate=learning_rate,
            model_rate=model_rate,
            surprise_high=surprise_high,
            revision_threshold=revision_threshold,
            coherence_limit=coherence_limit,
            write_threshold=write_threshold,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for learning_rate in LEARNING_RATES
        for model_rate in MODEL_RATES
        for surprise_high in SURPRISE_HIGH
        for revision_threshold in REVISION_THRESHOLDS
        for coherence_limit in COHERENCE_LIMITS
        for write_threshold in WRITE_THRESHOLDS
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


def build_features(alpha: float, condition: Condition, mode: str) -> tuple[np.ndarray, np.ndarray]:
    n = np.arange(LENGTH, dtype=float)
    center = observer_center(condition)
    theta1 = wrap01(alpha * n)
    phi1 = wrap01((alpha / PHI) * n)
    theta2 = wrap01((alpha + condition.beta + 0.0618) * n + 0.17)
    phi2 = wrap01((alpha / (PHI * PHI) + 0.13) * n + 0.41)
    az1, _ = sphere_projection(theta1, phi1)
    az2, _ = sphere_projection(theta2, phi2)
    if mode == "random_projection":
        az2 = wrap01(RNG.random(LENGTH))
    elif mode == "phase_scrambled":
        phase = RNG.random(LENGTH)
        az2 = wrap01(np.sort(az2)[np.argsort(phase)])
    signed1 = wrap_signed(az1 - center)
    signed2 = wrap_signed(az2 - center)
    alignment = np.abs(wrap_signed(az1 - az2))
    near_both = (np.abs(signed1) < 0.58 * condition.window_width) & (np.abs(signed2) < 0.58 * condition.window_width)
    intensity = np.clip(1.0 - alignment / max(0.5 * condition.window_width, 1e-9), 0.0, 1.0)
    return intensity, near_both


def build_sequence(model: str, alpha: float, condition: Condition, mode: str) -> tuple[np.ndarray, dict[str, float]]:
    intensity, near_both = build_features(alpha, condition, mode)
    seq = np.full(LENGTH, -1, dtype=np.int8)
    prediction = 0.25
    rule_estimate = 0.50
    admitted = 0
    rejected = 0
    revisions = 0
    writes = 0
    witnesses = 0
    coherence_errors: list[float] = []

    for idx, value in enumerate(intensity):
        surprise = abs(value - prediction)
        new_prediction = (1.0 - condition.learning_rate) * prediction + condition.learning_rate * value
        proposed_rule = (1.0 - condition.model_rate) * rule_estimate + condition.model_rate * value
        revision_size = abs(proposed_rule - rule_estimate)
        coherence_cost = abs(proposed_rule - 0.5)
        coherence_errors.append(coherence_cost)

        if not near_both[idx]:
            prediction = new_prediction
            rule_estimate = 0.995 * rule_estimate + 0.005 * proposed_rule
            continue

        if model == "surprise_only":
            if surprise >= condition.surprise_high:
                admitted += 1
                seq[idx] = 1
            else:
                rejected += 1
        elif model in {"model_revision", "model_revision_witness"}:
            revision_ok = revision_size >= condition.revision_threshold and coherence_cost <= condition.coherence_limit
            intense_revision = surprise >= condition.surprise_high and coherence_cost <= condition.coherence_limit
            if revision_ok or intense_revision:
                admitted += 1
                revisions += 1
                seq[idx] = 1 if value >= condition.write_threshold or surprise >= condition.surprise_high else 0
            else:
                rejected += 1
        else:
            raise ValueError(model)

        if seq[idx] == 1:
            writes += 1
        elif seq[idx] == 0:
            witnesses += 1

        if seq[idx] >= 0:
            prediction = new_prediction
            rule_estimate = proposed_rule
        else:
            prediction = 0.995 * prediction + 0.005 * new_prediction
            rule_estimate = 0.998 * rule_estimate + 0.002 * proposed_rule

    return seq, {
        "admitted": float(admitted),
        "rejected": float(rejected),
        "revisions": float(revisions),
        "writes": float(writes),
        "witnesses": float(witnesses),
        "mean_coherence_error": float(np.mean(coherence_errors)),
    }


def evaluate_model(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    total_seen = diag["admitted"] + diag["rejected"]
    write_count = float(np.sum(seq == 1))
    witness_count = float(np.sum(seq == 0))
    admission_rate = diag["admitted"] / max(total_seen, 1.0)
    write_rate = write_count / max(diag["admitted"], 1.0)
    witness_rate = witness_count / max(diag["admitted"], 1.0)
    delayed_retention = write_count / max(write_count + witness_count, 1.0)
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] == -1))) if len(seq) > 1 else 0.0
    phase_resist = phase_lock_resistance(seq)
    return {
        "write_count": write_count,
        "witness_count": witness_count,
        "admission_rate": admission_rate,
        "write_rate": write_rate,
        "witness_rate": witness_rate,
        "mean_coherence_error": diag["mean_coherence_error"],
        "delayed_retention": delayed_retention,
        "pollution": pollution,
        "phase_lock_resistance": phase_resist,
    }


def downstream_score(metrics: dict[str, float]) -> float:
    balanced_admission = 1.0 - min(abs(metrics["admission_rate"] - 0.42) / 0.42, 1.0)
    balanced_write = 1.0 - min(abs(metrics["write_rate"] - 0.55) / 0.55, 1.0)
    coherence = 1.0 - min(metrics["mean_coherence_error"] / 0.55, 1.0)
    return float(
        0.22 * metrics["phase_lock_resistance"]
        + 0.20 * metrics["delayed_retention"]
        + 0.15 * balanced_admission
        + 0.14 * balanced_write
        + 0.12 * (1.0 - metrics["pollution"])
        + 0.10 * coherence
        + 0.07 * metrics["witness_rate"]
    )


def plot_summary(rows: list[dict], path: Path) -> None:
    labels = [f"{row['model']}:{row['mode']}" for row in rows]
    scores = [row["mean_downstream_score"] for row in rows]
    plt.figure(figsize=(12, 5))
    plt.bar(np.arange(len(labels)), scores)
    plt.xticks(np.arange(len(labels)), labels, rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    conditions = build_conditions()
    models = ["surprise_only", "model_revision", "model_revision_witness"]
    modes = ["real", "random_projection", "phase_scrambled"]

    direct_rows: list[dict] = []
    for model in models:
        print(f"model: {model}")
        for mode in modes:
            for anchor in anchors:
                for condition in conditions:
                    for offset in OFFSET_GRID:
                        alpha = anchor.alpha + float(offset)
                        if not (0.0 < alpha < 1.0):
                            continue
                        seq, diag = build_sequence(model, alpha, condition, mode)
                        metrics = evaluate_model(seq, diag)
                        direct_rows.append(
                            {
                                "model": model,
                                "mode": mode,
                                "anchor": anchor.name,
                                "family": anchor.family,
                                "alpha": alpha,
                                "offset": float(offset),
                                **metrics,
                                "downstream_score": downstream_score(metrics),
                            }
                        )

    summary_rows: list[dict] = []
    for model in models:
        for mode in modes:
            subset = [row for row in direct_rows if row["model"] == model and row["mode"] == mode]
            summary_rows.append(
                {
                    "model": model,
                    "mode": mode,
                    "best_anchor": max(subset, key=lambda row: row["downstream_score"])["anchor"],
                    "best_downstream_score": float(np.max([row["downstream_score"] for row in subset])),
                    "mean_downstream_score": float(np.mean([row["downstream_score"] for row in subset])),
                    "mean_phase_lock_resistance": float(np.mean([row["phase_lock_resistance"] for row in subset])),
                    "mean_delayed_retention": float(np.mean([row["delayed_retention"] for row in subset])),
                    "mean_pollution": float(np.mean([row["pollution"] for row in subset])),
                    "mean_coherence_error": float(np.mean([row["mean_coherence_error"] for row in subset])),
                }
            )

    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(summary_rows, OUT / "summary.csv")
    plot_summary(summary_rows, OUT / "summary.png")

    real_revision = next(row for row in summary_rows if row["model"] == "model_revision_witness" and row["mode"] == "real")
    real_surprise = next(row for row in summary_rows if row["model"] == "surprise_only" and row["mode"] == "real")
    best_null_revision = max(
        (row for row in summary_rows if row["model"] == "model_revision_witness" and row["mode"] != "real"),
        key=lambda row: row["mean_downstream_score"],
    )
    report = f"""# Golden Zipper v21 - Revision Ablation Panel

Toy telemetry only. Not physics evidence. Not proof of GHP.

This panel removes direct reward for revision rate and revision size.

Key comparisons:
- real `surprise_only` downstream score: `{real_surprise['mean_downstream_score']:.3f}`
- real `model_revision_witness` downstream score: `{real_revision['mean_downstream_score']:.3f}`
- best null `model_revision_witness`: `{best_null_revision['mode']}` at `{best_null_revision['mean_downstream_score']:.3f}`

Interpretation:
- If model revision still wins without direct revision reward, the v19 signal is less likely to be score-selected.
- If null projection still wins, the toy is not geometry-specific.
- This remains experiment-only telemetry.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"real surprise_only downstream: {real_surprise['mean_downstream_score']:.3f}")
    print(f"real model_revision_witness downstream: {real_revision['mean_downstream_score']:.3f}")
    print(f"best null model_revision_witness: {best_null_revision['mode']} {best_null_revision['mean_downstream_score']:.3f}")


if __name__ == "__main__":
    main()
