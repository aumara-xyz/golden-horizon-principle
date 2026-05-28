#!/usr/bin/env python3
"""v25 co-stabilizing pocket panel.

Toy telemetry only. Not physics evidence. Not proof of GHP.

This panel models memory as a nest-like pocket:
- a little stability allows accumulation to begin
- a little accumulation helps the pocket stabilize further
- witness becomes write if the loop reinforces itself enough
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
OUT = ROOT / "golden_zipper_v25_outputs"

SEED = 20260520
RNG = np.random.default_rng(SEED)

LENGTH = 3072
OFFSET_GRID = np.arange(-0.036, 0.0361, 0.012)
WINDOW_WIDTHS = [0.16, 0.24]
BETAS = [0.0, 0.011]
POCKET_GAINS = [0.12, 0.22, 0.34]
POCKET_DECAYS = [0.88, 0.94, 0.98]
STABILITY_GAINS = [0.08, 0.16, 0.26]
STABILITY_DECAYS = [0.90, 0.95]
COUPLINGS = [0.12, 0.22, 0.34]
WRITE_THRESHOLDS = [0.42, 0.58, 0.74]
RELEASE_THRESHOLDS = [0.06, 0.12]
OVERLOAD_THRESHOLDS = [1.10, 1.45]
MAX_CONDITIONS = 72


@dataclass(frozen=True)
class FlowSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class Condition:
    window_width: float
    beta: float
    pocket_gain: float
    pocket_decay: float
    stability_gain: float
    stability_decay: float
    coupling: float
    write_threshold: float
    release_threshold: float
    overload_threshold: float


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
            pocket_gain=pocket_gain,
            pocket_decay=pocket_decay,
            stability_gain=stability_gain,
            stability_decay=stability_decay,
            coupling=coupling,
            write_threshold=write_threshold,
            release_threshold=release_threshold,
            overload_threshold=overload_threshold,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for pocket_gain in POCKET_GAINS
        for pocket_decay in POCKET_DECAYS
        for stability_gain in STABILITY_GAINS
        for stability_decay in STABILITY_DECAYS
        for coupling in COUPLINGS
        for write_threshold in WRITE_THRESHOLDS
        for release_threshold in RELEASE_THRESHOLDS
        for overload_threshold in OVERLOAD_THRESHOLDS
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
    seq = np.full(LENGTH, -2, dtype=np.int8)  # -2 hidden, -1 release, 0 witness, 1 write, 2 overload

    pocket = 0.0
    stability = 0.0
    witness_open = False
    writes = 0
    witnesses = 0
    releases = 0
    overloads = 0
    witness_to_write = 0
    stable_write_count = 0
    contact_qualities: list[float] = []

    for idx in range(1, LENGTH):
        prev = hidden[idx - 1]
        cur = hidden[idx]
        distance_to_zero = abs(cur)
        near_boundary = distance_to_zero <= condition.window_width
        approach = max(0.0, condition.window_width - distance_to_zero) / max(condition.window_width, 1e-9)
        slope = abs(cur - prev)
        coherence = 1.0 - min(abs(cur - prev) / 1.4, 1.0)
        contact_quality = 0.6 * approach + 0.25 * slope + 0.15 * coherence
        contact_qualities.append(contact_quality)

        pocket *= condition.pocket_decay
        stability *= condition.stability_decay

        # Co-stabilizing loop: some stability helps pocketing, some pocketing helps stability.
        if near_boundary:
            stability += condition.stability_gain * coherence + condition.coupling * pocket * 0.15
            pocket += condition.pocket_gain * contact_quality * (0.4 + 0.6 * min(stability, 1.0))

            if not witness_open:
                seq[idx] = 0
                witnesses += 1
                witness_open = True

        if pocket + stability >= condition.overload_threshold:
            seq[idx] = 2
            overloads += 1
            pocket = 0.0
            stability = 0.0
            witness_open = False
            continue

        if witness_open and pocket >= condition.write_threshold and stability >= 0.18 and near_boundary:
            seq[idx] = 1
            writes += 1
            witness_to_write += 1
            stable_write_count += 1
            pocket *= 0.35
            stability *= 0.55
            witness_open = False
            continue

        if witness_open and pocket <= condition.release_threshold and not near_boundary:
            seq[idx] = -1
            releases += 1
            pocket = 0.0
            stability *= 0.7
            witness_open = False

    return seq, {
        "writes": float(writes),
        "witnesses": float(witnesses),
        "releases": float(releases),
        "overloads": float(overloads),
        "witness_to_write": float(witness_to_write),
        "stable_write_count": float(stable_write_count),
        "mean_contact_quality": float(np.mean(contact_qualities)) if contact_qualities else 0.0,
    }


def evaluate_model(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    writes = diag["writes"]
    witnesses = diag["witnesses"]
    releases = diag["releases"]
    overloads = diag["overloads"]
    total_events = writes + witnesses + releases + overloads
    witness_conversion = diag["witness_to_write"] / max(witnesses, 1.0)
    stability_success = diag["stable_write_count"] / max(writes, 1.0)
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
        "stability_success": stability_success,
        "delayed_retention": delayed_retention,
        "release_rate": release_rate,
        "overload_rate": overload_rate,
        "mean_contact_quality": diag["mean_contact_quality"],
        "pollution": pollution,
        "phase_lock_resistance": phase_resist,
    }


def composite_score(metrics: dict[str, float]) -> float:
    contact_quality = min(max(metrics["mean_contact_quality"] / 1.2, 0.0), 1.0)
    return float(
        0.18 * metrics["phase_lock_resistance"]
        + 0.18 * metrics["stability_success"]
        + 0.16 * metrics["witness_conversion"]
        + 0.15 * metrics["delayed_retention"]
        + 0.11 * contact_quality
        + 0.10 * (1.0 - metrics["pollution"])
        + 0.07 * (1.0 - metrics["overload_rate"])
        + 0.05 * (1.0 - metrics["release_rate"])
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
                        "pocket_gain": condition.pocket_gain,
                        "pocket_decay": condition.pocket_decay,
                        "stability_gain": condition.stability_gain,
                        "stability_decay": condition.stability_decay,
                        "coupling": condition.coupling,
                        "write_threshold": condition.write_threshold,
                        "release_threshold": condition.release_threshold,
                        "overload_threshold": condition.overload_threshold,
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
            pocket_gain=best["pocket_gain"],
            pocket_decay=best["pocket_decay"],
            stability_gain=best["stability_gain"],
            stability_decay=best["stability_decay"],
            coupling=best["coupling"],
            write_threshold=best["write_threshold"],
            release_threshold=best["release_threshold"],
            overload_threshold=best["overload_threshold"],
        )
        seq, _ = build_sequence(best["alpha"], cond)
        density = density_random_surrogate(seq)
        density_metrics = evaluate_model(
            density,
            {
                "writes": float(np.sum(density == 1)),
                "witnesses": float(np.sum(density == 0)),
                "releases": float(np.sum(density == -1)),
                "overloads": float(np.sum(density == 2)),
                "witness_to_write": 0.0,
                "stable_write_count": 0.0,
                "mean_contact_quality": 0.0,
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
                "mean_stability_success": float(np.mean([row["stability_success"] for row in subset])),
                "mean_overload_rate": float(np.mean([row["overload_rate"] for row in subset])),
                "mean_density_gap": mean_composite - composite_score(density_metrics),
            }
        )

    ranked = sorted(flow_rows, key=lambda row: row["mean_composite"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(flow_rows, OUT / "flow_summary.csv")
    plot_flow_summary(flow_rows, OUT / "flow_summary.png")

    best = ranked[0]
    golden = next(row for row in flow_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v25 - Co-Stabilizing Pocket

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by mean composite: `{best['flow']}` with `{best['mean_composite']:.3f}`

Golden result:
- mean composite: `{golden['mean_composite']:.3f}`
- witness conversion: `{golden['mean_witness_conversion']:.3f}`
- stability success: `{golden['mean_stability_success']:.3f}`
- density gap: `{golden['mean_density_gap']:.3f}`

Interpretation:
- This panel tests whether stabilization and accumulation should reinforce each other rather than occur in strict sequence.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by mean composite: {best['flow']}")
    print(f"golden mean composite: {golden['mean_composite']:.3f}")
    print(f"golden witness conversion: {golden['mean_witness_conversion']:.3f}")
    print(f"golden stability success: {golden['mean_stability_success']:.3f}")
    print(f"golden density gap: {golden['mean_density_gap']:.3f}")


if __name__ == "__main__":
    main()
