#!/usr/bin/env python3
"""v11 family panel for two-light delayed alignment."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v11_outputs"

SEED = 20260517
RNG = np.random.default_rng(SEED)

OFFSET_GRID = np.arange(-0.048, 0.0481, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
PHASES = [0.0]
BETAS = [0.0, 0.011]
LENGTHS = [4096]
MAX_ALIGNMENT_AGES = [4, 8, 13, 21]
ALIGNMENT_FACTORS = [0.10, 0.14, 0.20]


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
    alignment_factor: float


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


def bounded_cf_samples(count: int) -> list[AnchorSpec]:
    anchors = []
    for idx in range(count):
        coeffs = RNG.choice([1, 2, 3], size=6, replace=True).tolist()
        value = continued_fraction_value(coeffs, tail_ones=14)
        anchors.append(AnchorSpec(f"bounded_cf_{idx+1}", value, "bounded_cf"))
    return anchors


def noble_samples() -> list[AnchorSpec]:
    prefixes = [[2, 3], [1, 4, 2], [3, 1, 2], [2, 2, 4]]
    return [
        AnchorSpec(f"noble_{idx+1}", continued_fraction_value(prefix, tail_ones=18), "noble")
        for idx, prefix in enumerate(prefixes)
    ]


def random_irrational_samples(count: int) -> list[AnchorSpec]:
    anchors = []
    for idx in range(count):
        coeffs = RNG.integers(1, 8, size=8).tolist()
        value = continued_fraction_value(coeffs, tail_ones=8)
        anchors.append(AnchorSpec(f"random_irrat_{idx+1}", value, "random_irrational"))
    return anchors


def build_anchors() -> list[AnchorSpec]:
    base = [
        AnchorSpec("golden", 1.0 / PHI, "phi"),
        AnchorSpec("silver", math.sqrt(2.0) - 1.0, "metallic"),
        AnchorSpec("bronze", (math.sqrt(13.0) - 3.0) / 2.0, "metallic"),
        AnchorSpec("fib_13_21", 13.0 / 21.0, "rational"),
        AnchorSpec("fib_21_34", 21.0 / 34.0, "rational"),
        AnchorSpec("pi_mod1", math.pi % 1.0, "constant"),
        AnchorSpec("e_mod1", math.e % 1.0, "constant"),
    ]
    return base + noble_samples() + bounded_cf_samples(6) + random_irrational_samples(6)


def build_conditions() -> list[ObserverCondition]:
    return [
        ObserverCondition(
            window_width=window_width,
            phase=phase,
            beta=beta,
            length=length,
            max_alignment_age=max_alignment_age,
            alignment_factor=alignment_factor,
        )
        for window_width in WINDOW_WIDTHS
        for phase in PHASES
        for beta in BETAS
        for length in LENGTHS
        for max_alignment_age in MAX_ALIGNMENT_AGES
        for alignment_factor in ALIGNMENT_FACTORS
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


def build_sequence(alpha: float, condition: ObserverCondition) -> tuple[np.ndarray, dict[str, float]]:
    n = np.arange(condition.length, dtype=float)
    center = observer_center(condition)
    theta1 = wrap01(alpha * n + condition.phase)
    phi1 = wrap01((alpha / PHI) * n + 0.3 * condition.phase)
    theta2 = wrap01((alpha + condition.beta + 0.0618) * n + 0.17)
    phi2 = wrap01((alpha / (PHI * PHI) + 0.13) * n + 0.41)
    az1, _ = sphere_projection(theta1, phi1)
    az2, _ = sphere_projection(theta2, phi2)
    signed1 = wrap_signed(az1 - center)
    signed2 = wrap_signed(az2 - center)
    alignment = np.abs(wrap_signed(az1 - az2))
    near_both = (np.abs(signed1) < 0.58 * condition.window_width) & (np.abs(signed2) < 0.58 * condition.window_width)
    witness = near_both & (alignment < 0.34 * condition.window_width)
    write = witness & (alignment < condition.alignment_factor * condition.window_width)
    seq = np.full(condition.length, -1, dtype=np.int8)
    seq[witness] = 0
    seq[write] = 1
    return seq, {"center_share": float(np.mean(seq == 0))}


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


def score_sequence(seq: np.ndarray, condition: ObserverCondition) -> dict[str, float]:
    memory = evaluate_alignment_memory(seq, condition)
    phase_resist = phase_lock_resistance(seq)
    composite = (
        0.34 * phase_resist
        + 0.28 * memory["delayed_retention"]
        + 0.20 * (1.0 - memory["pollution"])
        + 0.18 * memory["witness_conversion"]
        + 0.08 * memory["return_interval_diversity"]
    )
    return {
        **memory,
        "phase_lock_resistance": phase_resist,
        "composite_score": float(composite),
    }


def summarize_family(rows: list[dict]) -> list[dict]:
    summaries = []
    families = sorted({row["family"] for row in rows})
    for family in families:
        subset = [row for row in rows if row["family"] == family]
        summaries.append(
            {
                "family": family,
                "count": len(subset),
                "mean_best_composite": float(np.mean([row["best_composite"] for row in subset])),
                "median_best_composite": float(np.median([row["best_composite"] for row in subset])),
                "mean_surrogate_gap": float(np.mean([row["surrogate_gap"] for row in subset])),
                "top3_frequency": float(np.mean([row["is_top3"] for row in subset])),
            }
        )
    return summaries


def plot_family_summary(rows: list[dict], path: Path) -> None:
    families = [row["family"] for row in rows]
    composites = [row["mean_best_composite"] for row in rows]
    gaps = [row["mean_surrogate_gap"] for row in rows]
    x = np.arange(len(families))
    width = 0.35
    plt.figure(figsize=(10, 5))
    plt.bar(x - width / 2, composites, width=width, label="mean best composite")
    plt.bar(x + width / 2, gaps, width=width, label="mean surrogate gap")
    plt.xticks(x, families, rotation=20)
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.tight_layout()
    plt.legend()
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
                seq, diag = build_sequence(alpha, condition)
                metrics = score_sequence(seq, condition)
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
                        "alignment_factor": condition.alignment_factor,
                        "center_share": diag["center_share"],
                        **metrics,
                    }
                )

    anchor_rows: list[dict] = []
    for anchor in anchors:
        subset = [row for row in direct_rows if row["anchor"] == anchor.name]
        best = max(subset, key=lambda row: row["composite_score"])
        seq, _ = build_sequence(best["alpha"], ObserverCondition(
            window_width=best["window_width"],
            phase=0.0,
            beta=best["beta"],
            length=best["length"],
            max_alignment_age=best["max_alignment_age"],
            alignment_factor=best["alignment_factor"],
        ))
        shuffled = np.array(seq, copy=True)
        RNG.shuffle(shuffled)
        density = density_random_surrogate(seq)
        shuf_score = score_sequence(shuffled, ObserverCondition(
            window_width=best["window_width"],
            phase=0.0,
            beta=best["beta"],
            length=best["length"],
            max_alignment_age=best["max_alignment_age"],
            alignment_factor=best["alignment_factor"],
        ))["composite_score"]
        dens_score = score_sequence(density, ObserverCondition(
            window_width=best["window_width"],
            phase=0.0,
            beta=best["beta"],
            length=best["length"],
            max_alignment_age=best["max_alignment_age"],
            alignment_factor=best["alignment_factor"],
        ))["composite_score"]
        anchor_rows.append(
            {
                "anchor": anchor.name,
                "family": anchor.family,
                "best_composite": best["composite_score"],
                "best_offset": best["offset"],
                "best_age": best["max_alignment_age"],
                "best_alignment_factor": best["alignment_factor"],
                "best_latency": best["mean_alignment_latency"],
                "surrogate_gap": best["composite_score"] - max(shuf_score, dens_score),
            }
        )

    ranked = sorted(anchor_rows, key=lambda row: row["best_composite"], reverse=True)
    top3 = {row["anchor"] for row in ranked[:3]}
    for row in anchor_rows:
        row["is_top3"] = 1.0 if row["anchor"] in top3 else 0.0

    family_rows = summarize_family(anchor_rows)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(anchor_rows, OUT / "anchor_summary.csv")
    write_csv(family_rows, OUT / "family_summary.csv")
    plot_family_summary(family_rows, OUT / "family_summary.png")

    best = ranked[0]
    golden = next(row for row in anchor_rows if row["anchor"] == "golden")
    phi_rank = next(idx for idx, row in enumerate(ranked, start=1) if row["anchor"] == "golden")
    report = f"""# Golden Zipper v11 - Alignment Family Panel

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best anchor: `{best['anchor']}` ({best['family']}) with composite `{best['best_composite']:.3f}`
Golden rank: `{phi_rank}` / `{len(ranked)}`
Golden composite: `{golden['best_composite']:.3f}`
Golden surrogate gap: `{golden['surrogate_gap']:.3f}`

Family means:
""" + "\n".join(
        f"- `{row['family']}`: mean best composite `{row['mean_best_composite']:.3f}`, mean surrogate gap `{row['mean_surrogate_gap']:.3f}`"
        for row in family_rows
    )
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best anchor: {best['anchor']}")
    print(f"golden rank: {phi_rank}")
    print(f"golden composite: {golden['best_composite']:.3f}")
    print(f"golden surrogate gap: {golden['surrogate_gap']:.3f}")


if __name__ == "__main__":
    main()
