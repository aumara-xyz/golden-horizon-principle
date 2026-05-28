#!/usr/bin/env python3
"""v12 panel: badly approximable structure versus alignment-memory performance."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import PHI


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v12_outputs"

SEED = 20260517
RNG = np.random.default_rng(SEED)

OFFSET_GRID = np.arange(-0.036, 0.0361, 0.006)
WINDOW_WIDTHS = [0.18, 0.24]
BETAS = [0.0, 0.011]
LENGTHS = [4096]
MAX_ALIGNMENT_AGES = [4, 8, 13, 21]
ALIGNMENT_FACTORS = [0.10, 0.20]
CF_CHECK_DEPTH = 10


@dataclass(frozen=True)
class AnchorSpec:
    name: str
    alpha: float
    family: str
    cf_bound_hint: float


@dataclass(frozen=True)
class ObserverCondition:
    window_width: float
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


def continued_fraction_prefix(x: float, depth: int = CF_CHECK_DEPTH) -> list[int]:
    coeffs: list[int] = []
    value = float(x)
    for _ in range(depth):
        if value <= 0:
            break
        inv = 1.0 / value
        a = int(math.floor(inv + 1e-12))
        coeffs.append(max(a, 1))
        frac = inv - a
        if abs(frac) < 1e-12:
            break
        value = frac
    return coeffs


def max_partial_quotient(x: float, depth: int = CF_CHECK_DEPTH) -> int:
    coeffs = continued_fraction_prefix(x, depth)
    return max(coeffs) if coeffs else 0


def boundedness_score(x: float, depth: int = CF_CHECK_DEPTH) -> float:
    coeffs = continued_fraction_prefix(x, depth)
    if not coeffs:
        return 0.0
    return 1.0 / (1.0 + max(coeffs))


def diophantine_margin(x: float, q_max: int = 55) -> float:
    best = float("inf")
    for q in range(1, q_max + 1):
        p = round(x * q)
        err = abs(x - p / q)
        scaled = q * q * err
        if scaled < best:
            best = scaled
    return best


def build_anchors() -> list[AnchorSpec]:
    anchors = [
        AnchorSpec("golden", 1.0 / PHI, "phi", 1.0),
        AnchorSpec("silver", math.sqrt(2.0) - 1.0, "metallic", 2.0),
        AnchorSpec("bronze", (math.sqrt(13.0) - 3.0) / 2.0, "metallic", 3.0),
        AnchorSpec("fib_13_21", 13.0 / 21.0, "rational", 21.0),
        AnchorSpec("fib_21_34", 21.0 / 34.0, "rational", 34.0),
        AnchorSpec("pi_mod1", math.pi % 1.0, "constant", 8.0),
        AnchorSpec("e_mod1", math.e % 1.0, "constant", 6.0),
    ]
    noble_prefixes = [[2, 3], [1, 4, 2], [3, 1, 2], [2, 2, 4]]
    for idx, prefix in enumerate(noble_prefixes, start=1):
        anchors.append(AnchorSpec(f"noble_{idx}", continued_fraction_value(prefix, tail_ones=18), "noble", 1.0))
    for idx in range(8):
        coeffs = RNG.choice([1, 2, 3], size=6, replace=True).tolist()
        anchors.append(AnchorSpec(f"bounded_cf_{idx+1}", continued_fraction_value(coeffs, tail_ones=14), "bounded_cf", 3.0))
    for idx in range(8):
        coeffs = RNG.integers(1, 10, size=8).tolist()
        anchors.append(AnchorSpec(f"random_irrat_{idx+1}", continued_fraction_value(coeffs, tail_ones=8), "random_irrational", 9.0))
    return anchors


def build_conditions() -> list[ObserverCondition]:
    return [
        ObserverCondition(
            window_width=window_width,
            beta=beta,
            length=length,
            max_alignment_age=max_alignment_age,
            alignment_factor=alignment_factor,
        )
        for window_width in WINDOW_WIDTHS
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
    return wrap01(0.5 + condition.beta * n)


def sphere_projection(theta: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.cos(2.0 * math.pi * theta) * np.cos(math.pi * (phi - 0.5))
    y = np.sin(2.0 * math.pi * theta) * np.cos(math.pi * (phi - 0.5))
    z = np.sin(math.pi * (phi - 0.5))
    azimuth = wrap01(np.arctan2(y, x) / (2.0 * math.pi))
    elevation = np.arctan2(z, np.sqrt(x * x + y * y))
    return azimuth, elevation


def build_sequence(alpha: float, condition: ObserverCondition) -> np.ndarray:
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
    witness = near_both & (alignment < 0.34 * condition.window_width)
    write = witness & (alignment < condition.alignment_factor * condition.window_width)
    seq = np.full(condition.length, -1, dtype=np.int8)
    seq[witness] = 0
    seq[write] = 1
    return seq


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


def plot_scatter(rows: list[dict], xkey: str, ykey: str, path: Path, title: str) -> None:
    families = sorted({row["family"] for row in rows})
    colors = plt.cm.tab10(np.linspace(0, 1, len(families)))
    plt.figure(figsize=(8, 6))
    for color, family in zip(colors, families):
        subset = [row for row in rows if row["family"] == family]
        plt.scatter([row[xkey] for row in subset], [row[ykey] for row in subset], s=36, alpha=0.8, label=family, color=color)
    plt.xlabel(xkey)
    plt.ylabel(ykey)
    plt.title(title)
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
                seq = build_sequence(alpha, condition)
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
                        **metrics,
                    }
                )

    anchor_rows: list[dict] = []
    for anchor in anchors:
        subset = [row for row in direct_rows if row["anchor"] == anchor.name]
        best = max(subset, key=lambda row: row["composite_score"])
        cond = ObserverCondition(
            window_width=best["window_width"],
            beta=best["beta"],
            length=best["length"],
            max_alignment_age=best["max_alignment_age"],
            alignment_factor=best["alignment_factor"],
        )
        seq = build_sequence(best["alpha"], cond)
        shuf = np.array(seq, copy=True)
        RNG.shuffle(shuf)
        dens = density_random_surrogate(seq)
        shuf_score = score_sequence(shuf, cond)["composite_score"]
        dens_score = score_sequence(dens, cond)["composite_score"]
        anchor_rows.append(
            {
                "anchor": anchor.name,
                "family": anchor.family,
                "alpha": anchor.alpha,
                "best_composite": best["composite_score"],
                "best_offset": best["offset"],
                "best_age": best["max_alignment_age"],
                "best_alignment_factor": best["alignment_factor"],
                "best_latency": best["mean_alignment_latency"],
                "surrogate_gap": best["composite_score"] - max(shuf_score, dens_score),
                "cf_max": float(max_partial_quotient(anchor.alpha)),
                "cf_boundedness": float(boundedness_score(anchor.alpha)),
                "diophantine_margin": float(diophantine_margin(anchor.alpha)),
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
                "mean_cf_boundedness": float(np.mean([row["cf_boundedness"] for row in subset])),
                "mean_diophantine_margin": float(np.mean([row["diophantine_margin"] for row in subset])),
            }
        )

    corr_boundedness = float(np.corrcoef(
        [row["cf_boundedness"] for row in anchor_rows],
        [row["best_composite"] for row in anchor_rows],
    )[0, 1])
    corr_margin = float(np.corrcoef(
        [row["diophantine_margin"] for row in anchor_rows],
        [row["best_composite"] for row in anchor_rows],
    )[0, 1])

    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(anchor_rows, OUT / "anchor_summary.csv")
    write_csv(family_rows, OUT / "family_summary.csv")
    plot_scatter(anchor_rows, "cf_boundedness", "best_composite", OUT / "boundedness_vs_composite.png", "CF boundedness vs best composite")
    plot_scatter(anchor_rows, "diophantine_margin", "best_composite", OUT / "margin_vs_composite.png", "Diophantine margin vs best composite")

    best = ranked[0]
    golden = next(row for row in anchor_rows if row["anchor"] == "golden")
    golden_rank = next(idx for idx, row in enumerate(ranked, start=1) if row["anchor"] == "golden")
    report = f"""# Golden Zipper v12 - Badly Approximable Panel

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best anchor: `{best['anchor']}` ({best['family']}) with composite `{best['best_composite']:.3f}`
Golden rank: `{golden_rank}` / `{len(ranked)}`
Golden composite: `{golden['best_composite']:.3f}`
Golden surrogate gap: `{golden['surrogate_gap']:.3f}`

Correlations:
- `cf_boundedness` vs composite: `{corr_boundedness:.3f}`
- `diophantine_margin` vs composite: `{corr_margin:.3f}`

Family means:
""" + "\n".join(
        f"- `{row['family']}`: composite `{row['mean_best_composite']:.3f}`, surrogate gap `{row['mean_surrogate_gap']:.3f}`"
        for row in family_rows
    )
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best anchor: {best['anchor']}")
    print(f"golden rank: {golden_rank}")
    print(f"golden composite: {golden['best_composite']:.3f}")
    print(f"golden surrogate gap: {golden['surrogate_gap']:.3f}")
    print(f"corr cf_boundedness/composite: {corr_boundedness:.3f}")
    print(f"corr diophantine_margin/composite: {corr_margin:.3f}")


if __name__ == "__main__":
    main()
