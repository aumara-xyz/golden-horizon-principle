#!/usr/bin/env python3
"""v13 recognition-collapse panel for delayed two-light alignment."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v13_outputs"

SEED = 20260517
RNG = np.random.default_rng(SEED)

OFFSET_GRID = np.arange(-0.036, 0.0361, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
BETAS = [0.0, 0.011]
LENGTHS = [4096]
MAX_ALIGNMENT_AGES = [4, 13, 21]
WITNESS_FACTORS = [0.28, 0.42]
RECOGNITION_FACTORS = [0.10, 0.20]
DECAYS = [0.82, 0.96]
NEAR_MISS_BOOSTS = [0.00, 0.16]


@dataclass(frozen=True)
class AnchorSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class Condition:
    window_width: float
    beta: float
    length: int
    max_alignment_age: int
    witness_factor: float
    recognition_factor: float
    decay: float
    near_miss_boost: float


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
        AnchorSpec("noble_1", continued_fraction_value([2, 3], tail_ones=18), "noble"),
        AnchorSpec("bounded_cf_2", continued_fraction_value([1, 2, 3, 1, 2, 3], tail_ones=14), "bounded_cf"),
        AnchorSpec("random_irrat_1", continued_fraction_value([7, 2, 9, 3, 5, 4, 8, 6], tail_ones=8), "random_irrational"),
        AnchorSpec("fib_13_21", 13.0 / 21.0, "rational"),
    ]


def build_conditions() -> list[Condition]:
    return [
        Condition(
            window_width=window_width,
            beta=beta,
            length=length,
            max_alignment_age=max_alignment_age,
            witness_factor=witness_factor,
            recognition_factor=recognition_factor,
            decay=decay,
            near_miss_boost=near_miss_boost,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for length in LENGTHS
        for max_alignment_age in MAX_ALIGNMENT_AGES
        for witness_factor in WITNESS_FACTORS
        for recognition_factor in RECOGNITION_FACTORS
        for decay in DECAYS
        for near_miss_boost in NEAR_MISS_BOOSTS
        if recognition_factor < witness_factor
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


def observer_center(condition: Condition) -> np.ndarray:
    n = np.arange(condition.length, dtype=float)
    return wrap01(0.5 + condition.beta * n)


def sphere_projection(theta: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.cos(2.0 * math.pi * theta) * np.cos(math.pi * (phi - 0.5))
    y = np.sin(2.0 * math.pi * theta) * np.cos(math.pi * (phi - 0.5))
    z = np.sin(math.pi * (phi - 0.5))
    azimuth = wrap01(np.arctan2(y, x) / (2.0 * math.pi))
    elevation = np.arctan2(z, np.sqrt(x * x + y * y))
    return azimuth, elevation


def build_alignment_trace(alpha: float, condition: Condition) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = np.arange(condition.length, dtype=float)
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
    return alignment, signed1, near_both


def recognition_collapse_trace(alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    alignment, _, near_both = build_alignment_trace(alpha, condition)
    witness_thresh = condition.witness_factor * condition.window_width
    recog_thresh = condition.recognition_factor * condition.window_width

    seq = np.full(condition.length, -1, dtype=np.int8)
    memory_charge = 0.0
    pending_age = 0
    recognized = 0
    near_misses = 0
    collapse_total = 0
    witness_total = 0

    for idx, gap in enumerate(alignment):
        memory_charge *= condition.decay
        if memory_charge > 0:
            pending_age += 1
        else:
            pending_age = 0

        if near_both[idx] and gap < witness_thresh:
            witness_total += 1
            memory_charge = max(memory_charge, 0.6) + condition.near_miss_boost
            seq[idx] = 0
            if gap < recog_thresh or (memory_charge >= 1.0 and pending_age <= condition.max_alignment_age):
                seq[idx] = 1
                collapse_total += 1
                recognized += 1
                memory_charge = 0.0
                pending_age = 0
            elif memory_charge >= 0.85:
                near_misses += 1
        elif pending_age > condition.max_alignment_age:
            memory_charge = 0.0
            pending_age = 0

    return seq, {
        "recognized_collapses": float(recognized),
        "near_misses": float(near_misses),
        "collapse_total": float(collapse_total),
        "witness_total": float(witness_total),
    }


def evaluate_recognition(seq: np.ndarray, diag: dict[str, float], condition: Condition) -> dict[str, float]:
    writes = float(np.sum(seq == 1))
    witnesses = float(np.sum(seq == 0))
    delayed_retention = writes / max(witnesses + writes, 1.0)
    recognition_rate = diag["recognized_collapses"] / max(diag["witness_total"], 1.0)
    near_miss_rate = diag["near_misses"] / max(diag["witness_total"], 1.0)
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] == -1))) if len(seq) > 1 else 0.0
    latency_proxy = float(condition.max_alignment_age / max(diag["recognized_collapses"], 1.0))
    phase_resist = phase_lock_resistance(seq)
    return {
        "write_count": writes,
        "witness_count": witnesses,
        "delayed_retention": delayed_retention,
        "recognition_rate": recognition_rate,
        "near_miss_rate": near_miss_rate,
        "pollution": pollution,
        "latency_proxy": latency_proxy,
        "phase_lock_resistance": phase_resist,
    }


def composite_score(metrics: dict[str, float]) -> float:
    return float(
        0.28 * metrics["phase_lock_resistance"]
        + 0.24 * metrics["recognition_rate"]
        + 0.18 * metrics["delayed_retention"]
        + 0.14 * (1.0 - metrics["pollution"])
        + 0.10 * metrics["near_miss_rate"]
        + 0.06 * min(1.0 / max(metrics["latency_proxy"], 1e-9), 1.0)
    )


def plot_policy_scatter(rows: list[dict], path: Path) -> None:
    plt.figure(figsize=(8, 6))
    for family in sorted({row["family"] for row in rows}):
        subset = [row for row in rows if row["family"] == family]
        plt.scatter(
            [row["recognition_rate"] for row in subset],
            [row["best_composite"] for row in subset],
            s=36,
            alpha=0.8,
            label=family,
        )
    plt.xlabel("recognition_rate")
    plt.ylabel("best_composite")
    plt.title("Recognition rate vs best composite")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    conditions = build_conditions()

    direct_rows: list[dict] = []
    total = len(anchors)
    for idx, anchor in enumerate(anchors, start=1):
        print(f"scanning {idx}/{total}: {anchor.name}")
        for condition in conditions:
            for offset in OFFSET_GRID:
                alpha = anchor.alpha + float(offset)
                if not (0.0 < alpha < 1.0):
                    continue
                seq, diag = recognition_collapse_trace(alpha, condition)
                metrics = evaluate_recognition(seq, diag, condition)
                direct_rows.append(
                    {
                        "anchor": anchor.name,
                        "family": anchor.family,
                        "alpha": alpha,
                        "offset": float(offset),
                        "window_width": condition.window_width,
                        "beta": condition.beta,
                        "length": condition.length,
                        "max_alignment_age": condition.max_alignment_age,
                        "witness_factor": condition.witness_factor,
                        "recognition_factor": condition.recognition_factor,
                        "decay": condition.decay,
                        "near_miss_boost": condition.near_miss_boost,
                        **metrics,
                        "composite_score": composite_score(metrics),
                    }
                )

    anchor_rows: list[dict] = []
    for anchor in anchors:
        subset = [row for row in direct_rows if row["anchor"] == anchor.name]
        best = max(subset, key=lambda row: row["composite_score"])
        cond = Condition(
            window_width=best["window_width"],
            beta=best["beta"],
            length=best["length"],
            max_alignment_age=best["max_alignment_age"],
            witness_factor=best["witness_factor"],
            recognition_factor=best["recognition_factor"],
            decay=best["decay"],
            near_miss_boost=best["near_miss_boost"],
        )
        seq, diag = recognition_collapse_trace(best["alpha"], cond)
        dens = density_random_surrogate(seq)
        dens_metrics = evaluate_recognition(dens, {"recognized_collapses": 0.0, "near_misses": 0.0, "collapse_total": 0.0, "witness_total": float(np.sum(dens >= 0))}, cond)
        anchor_rows.append(
            {
                "anchor": anchor.name,
                "family": anchor.family,
                "best_composite": best["composite_score"],
                "best_offset": best["offset"],
                "best_age": best["max_alignment_age"],
                "best_witness_factor": best["witness_factor"],
                "best_recognition_factor": best["recognition_factor"],
                "best_decay": best["decay"],
                "best_near_miss_boost": best["near_miss_boost"],
                "recognition_rate": best["recognition_rate"],
                "near_miss_rate": best["near_miss_rate"],
                "surrogate_gap": best["composite_score"] - composite_score(dens_metrics),
            }
        )

    ranked = sorted(anchor_rows, key=lambda row: row["best_composite"], reverse=True)
    family_rows = []
    for family in sorted({row["family"] for row in anchor_rows}):
        subset = [row for row in anchor_rows if row["family"] == family]
        family_rows.append(
            {
                "family": family,
                "count": len(subset),
                "mean_best_composite": float(np.mean([row["best_composite"] for row in subset])),
                "mean_surrogate_gap": float(np.mean([row["surrogate_gap"] for row in subset])),
                "mean_recognition_rate": float(np.mean([row["recognition_rate"] for row in subset])),
                "mean_near_miss_rate": float(np.mean([row["near_miss_rate"] for row in subset])),
            }
        )

    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(anchor_rows, OUT / "anchor_summary.csv")
    write_csv(family_rows, OUT / "family_summary.csv")
    plot_policy_scatter(anchor_rows, OUT / "recognition_vs_composite.png")

    best = ranked[0]
    golden = next(row for row in anchor_rows if row["anchor"] == "golden")
    golden_rank = next(idx for idx, row in enumerate(ranked, start=1) if row["anchor"] == "golden")
    report = f"""# Golden Zipper v13 - Recognition Collapse Panel

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best anchor: `{best['anchor']}` ({best['family']}) with composite `{best['best_composite']:.3f}`
Golden rank: `{golden_rank}` / `{len(ranked)}`
Golden composite: `{golden['best_composite']:.3f}`
Golden surrogate gap: `{golden['surrogate_gap']:.3f}`
Golden best recognition rate: `{golden['recognition_rate']:.3f}`

Family means:
""" + "\n".join(
        f"- `{row['family']}`: composite `{row['mean_best_composite']:.3f}`, recognition `{row['mean_recognition_rate']:.3f}`, surrogate gap `{row['mean_surrogate_gap']:.3f}`"
        for row in family_rows
    )
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best anchor: {best['anchor']}")
    print(f"golden rank: {golden_rank}")
    print(f"golden composite: {golden['best_composite']:.3f}")
    print(f"golden surrogate gap: {golden['surrogate_gap']:.3f}")
    print(f"golden recognition rate: {golden['recognition_rate']:.3f}")


if __name__ == "__main__":
    main()
