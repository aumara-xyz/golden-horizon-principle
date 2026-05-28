#!/usr/bin/env python3
"""v5 derivation test for phi-anchor shear in the Golden Zipper toy."""

from __future__ import annotations

import csv
import math
import statistics
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v4_null_test import (
    PHI,
    compression_ratio,
    compute_tradeoff,
    phase_lock_score,
    precompute_policy_features,
    predictive_accuracy,
    simulate_memory_policy,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v5_outputs"
SEED = 1729
RNG = np.random.default_rng(SEED)

WINDOW_SIZES = [0.20, 0.382, 0.618]
PHASES = [0.0, 0.17]
LENGTHS = [5000]
MEMORY_CAPACITIES = [50, 100, 400]
OFFSET_GRID = np.arange(-0.08, 0.0801, 0.004)


@dataclass(frozen=True)
class AnchorSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class ObserverCondition:
    window_size: float
    phase: float
    length: int
    memory_capacity: int


@dataclass(frozen=True)
class PerturbationSpec:
    name: str
    phase_lag: float
    window_beta: float
    delay_steps: int
    noise_amp: float
    alpha_cutoff_q: int


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    fieldnames = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text)


def wrap01(x: np.ndarray | float) -> np.ndarray | float:
    return np.mod(x, 1.0)


def in_window_vector(x: np.ndarray, starts: np.ndarray, width: float) -> np.ndarray:
    ends = starts + width
    normal = ends <= 1.0
    hits = np.empty_like(x, dtype=bool)
    hits[normal] = (x[normal] >= starts[normal]) & (x[normal] < ends[normal])
    hits[~normal] = (x[~normal] >= starts[~normal]) | (x[~normal] < np.mod(ends[~normal], 1.0))
    return hits


def build_anchors() -> list[AnchorSpec]:
    golden = 1.0 / PHI
    silver = math.sqrt(2.0) - 1.0
    bronze = (math.sqrt(13.0) - 3.0) / 2.0
    bounded_probe = 1.0 / (2.0 + 1.0 / (1.0 + 1.0 / (2.0 + 1.0 / (1.0 + 1.0 / (2.0 + 1.0 / (1.0 + 1.0 / 2.0))))))
    return [
        AnchorSpec("golden", golden, "phi_anchor"),
        AnchorSpec("silver", silver, "metallic_anchor"),
        AnchorSpec("bronze", bronze, "metallic_anchor"),
        AnchorSpec("bounded_probe", bounded_probe, "bounded_anchor"),
    ]


def build_conditions() -> list[ObserverCondition]:
    conditions = []
    for window_size in WINDOW_SIZES:
        for phase in PHASES:
            for length in LENGTHS:
                for memory_capacity in MEMORY_CAPACITIES:
                    conditions.append(
                        ObserverCondition(
                            window_size=window_size,
                            phase=phase,
                            length=length,
                            memory_capacity=memory_capacity,
                        )
                    )
    return conditions


def build_policies() -> list[dict]:
    return [
        {
            "policy_id": 1,
            "confidence_write": 0.68,
            "confidence_witness": 0.48,
            "ambiguity_band": 0.05,
            "motif_write_min": 0.10,
            "motif_witness_min": 0.18,
            "max_witness_age": 5,
        },
        {
            "policy_id": 2,
            "confidence_write": 0.74,
            "confidence_witness": 0.55,
            "ambiguity_band": 0.10,
            "motif_write_min": 0.18,
            "motif_witness_min": 0.24,
            "max_witness_age": 20,
        },
        {
            "policy_id": 3,
            "confidence_write": 0.82,
            "confidence_witness": 0.58,
            "ambiguity_band": 0.14,
            "motif_write_min": 0.25,
            "motif_witness_min": 0.32,
            "max_witness_age": 20,
        },
        {
            "policy_id": 4,
            "confidence_write": 0.88,
            "confidence_witness": 0.62,
            "ambiguity_band": 0.18,
            "motif_write_min": 0.32,
            "motif_witness_min": 0.40,
            "max_witness_age": 100,
        },
    ]


def build_perturbations() -> list[PerturbationSpec]:
    return [
        PerturbationSpec("phase_small", 0.015, 0.0, 0, 0.0, 0),
        PerturbationSpec("phase_big", 0.045, 0.0, 0, 0.0, 0),
        PerturbationSpec("window_drift_small", 0.0, 0.004, 0, 0.0, 0),
        PerturbationSpec("window_drift_big", 0.0, 0.011, 0, 0.0, 0),
        PerturbationSpec("delay_3", 0.0, 0.0, 3, 0.0, 0),
        PerturbationSpec("delay_8", 0.0, 0.0, 8, 0.0, 0),
        PerturbationSpec("noise_small", 0.0, 0.0, 0, 0.0015, 0),
        PerturbationSpec("noise_big", 0.0, 0.0, 0, 0.0045, 0),
        PerturbationSpec("cutoff_34", 0.0, 0.0, 0, 0.0, 34),
        PerturbationSpec("cutoff_55", 0.0, 0.0, 0, 0.0, 55),
        PerturbationSpec("combo_small", 0.018, 0.004, 3, 0.0015, 34),
        PerturbationSpec("combo_big", 0.045, 0.011, 8, 0.0045, 55),
    ]


def approx_alpha(anchor_alpha: float, q: int) -> float:
    if q <= 0:
        return anchor_alpha
    return round(anchor_alpha * q) / q


def generate_anchor_sequence(
    alpha: float,
    condition: ObserverCondition,
    perturb: PerturbationSpec | None = None,
) -> np.ndarray:
    perturb = perturb or PerturbationSpec("none", 0.0, 0.0, 0, 0.0, 0)
    alpha_eff = approx_alpha(alpha, perturb.alpha_cutoff_q)
    n = np.arange(condition.length, dtype=float)
    delayed_n = np.maximum(n - perturb.delay_steps, 0.0)
    x = delayed_n * alpha_eff + condition.phase + perturb.phase_lag
    if perturb.noise_amp > 0:
        x = x + perturb.noise_amp * np.sin(2.0 * math.pi * (0.071 * n + alpha * 3.0))
    x = wrap01(x)
    starts = wrap01(condition.phase + perturb.window_beta * n)
    hits = in_window_vector(x, starts, condition.window_size)
    return hits.astype(np.int8)


def hamming_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(a != b))


def evaluate_memory_tradeoff(seq: np.ndarray, memory_capacity: int, policies: list[dict]) -> dict[str, float]:
    phase_score, phase_parts = phase_lock_score(seq)
    compress = compression_ratio(seq)
    predict = predictive_accuracy(seq)
    features = precompute_policy_features(seq)
    rows = []
    for policy in policies:
        memory = simulate_memory_policy(
            seq,
            features,
            confidence_write=policy["confidence_write"],
            confidence_witness=policy["confidence_witness"],
            ambiguity_band=policy["ambiguity_band"],
            motif_write_min=policy["motif_write_min"],
            motif_witness_min=policy["motif_witness_min"],
            max_witness_age=policy["max_witness_age"],
            memory_capacity=memory_capacity,
        )
        row = {
            "phase_lock_score": phase_score,
            "compression_ratio": compress,
            "predictive_accuracy": predict,
            "memory_capacity": float(memory_capacity),
            **memory,
        }
        row["tradeoff_score"] = compute_tradeoff(row)
        rows.append(row)
    return {
        "mean_tradeoff": float(np.mean([row["tradeoff_score"] for row in rows])),
        "max_tradeoff": float(np.max([row["tradeoff_score"] for row in rows])),
        "mean_retention": float(np.mean([row["useful_delayed_retention"] for row in rows])),
        "mean_pollution": float(np.mean([row["pollution"] for row in rows])),
        "mean_phase_lock": phase_score,
        "mean_diversity": float(np.mean([row["memory_diversity"] for row in rows])),
        "mean_write": float(np.mean([row["write_count"] for row in rows])),
        "mean_witness": float(np.mean([row["witness_count"] for row in rows])),
        "mean_release": float(np.mean([row["release_count"] for row in rows])),
        "autocorr_peak": phase_parts["autocorr_peak"],
        "spectral_peak": phase_parts["spectral_peak"],
    }


def plot_anchor_offsets(rows: list[dict], path: Path) -> None:
    anchors = sorted({row["anchor"] for row in rows})
    plt.figure(figsize=(10, 5))
    for anchor in anchors:
        subset = [row for row in rows if row["anchor"] == anchor]
        xs = [row["effective_offset"] for row in subset]
        ys = [row["derived_tradeoff"] for row in subset]
        plt.scatter(xs, ys, s=24, alpha=0.55, label=anchor)
    plt.axvline(0.0, color="black", linestyle="--", linewidth=1.0)
    plt.xlabel("effective offset from anchor")
    plt.ylabel("derived tradeoff")
    plt.title("Derived effective offsets from exact anchors")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_direct_bands(rows: list[dict], path: Path) -> None:
    anchors = sorted({row["anchor"] for row in rows})
    fig, axes = plt.subplots(len(anchors), 1, figsize=(9, 3 * len(anchors)), sharex=True)
    if len(anchors) == 1:
        axes = [axes]
    for ax, anchor in zip(axes, anchors):
        subset = sorted([row for row in rows if row["anchor"] == anchor], key=lambda row: row["offset"])
        ax.plot([row["offset"] for row in subset], [row["mean_tradeoff"] for row in subset], color="#0d47a1")
        ax.axvline(0.0, color="black", linestyle="--", linewidth=1.0)
        ax.set_title(anchor)
        ax.set_ylabel("mean tradeoff")
    axes[-1].set_xlabel("offset from anchor")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_peak_offsets(rows: list[dict], path: Path) -> None:
    anchors = sorted({row["anchor"] for row in rows})
    capacities = sorted({row["memory_capacity"] for row in rows})
    matrix = np.zeros((len(anchors), len(capacities)))
    for i, anchor in enumerate(anchors):
        for j, capacity in enumerate(capacities):
            subset = [row for row in rows if row["anchor"] == anchor and row["memory_capacity"] == capacity]
            best = max(subset, key=lambda row: row["mean_tradeoff"])
            matrix[i, j] = best["offset"]
    plt.figure(figsize=(6, 4))
    plt.imshow(matrix, cmap="coolwarm", aspect="auto")
    plt.xticks(range(len(capacities)), capacities)
    plt.yticks(range(len(anchors)), anchors)
    plt.colorbar(label="best offset")
    plt.title("Best direct offset by anchor and capacity")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    conditions = build_conditions()
    policies = build_policies()
    perturbations = build_perturbations()

    direct_rows = []
    direct_cache: dict[tuple[str, float, float, float, int, int], tuple[np.ndarray, dict[str, float]]] = {}
    for anchor in anchors:
        for condition in conditions:
            for offset in OFFSET_GRID:
                alpha = anchor.alpha + float(offset)
                if not (0.0 < alpha < 1.0):
                    continue
                seq = generate_anchor_sequence(alpha, condition, None)
                metrics = evaluate_memory_tradeoff(seq, condition.memory_capacity, policies)
                row = {
                    "anchor": anchor.name,
                    "anchor_family": anchor.family,
                    "alpha": alpha,
                    "offset": float(offset),
                    "window_size": condition.window_size,
                    "phase": condition.phase,
                    "length": condition.length,
                    "memory_capacity": condition.memory_capacity,
                    **metrics,
                }
                direct_rows.append(row)
                direct_cache[(anchor.name, round(offset, 6), condition.window_size, condition.phase, condition.length, condition.memory_capacity)] = (seq, metrics)
    print(f"direct band done: {len(direct_rows)} rows", flush=True)

    derived_rows = []
    summary_rows = []
    for anchor in anchors:
        for condition in conditions:
            base_direct = [row for row in direct_rows if row["anchor"] == anchor.name and row["window_size"] == condition.window_size and row["phase"] == condition.phase and row["length"] == condition.length and row["memory_capacity"] == condition.memory_capacity]
            best_direct = max(base_direct, key=lambda row: row["mean_tradeoff"])
            for perturb in perturbations:
                seq = generate_anchor_sequence(anchor.alpha, condition, perturb)
                metrics = evaluate_memory_tradeoff(seq, condition.memory_capacity, policies)
                best_match = None
                best_dist = 1.0
                for candidate in base_direct:
                    cand_seq, _ = direct_cache[(anchor.name, round(candidate["offset"], 6), condition.window_size, condition.phase, condition.length, condition.memory_capacity)]
                    dist = hamming_distance(seq, cand_seq)
                    if dist < best_dist:
                        best_dist = dist
                        best_match = candidate
                derived_row = {
                    "anchor": anchor.name,
                    "anchor_family": anchor.family,
                    "window_size": condition.window_size,
                    "phase": condition.phase,
                    "length": condition.length,
                    "memory_capacity": condition.memory_capacity,
                    "perturbation": perturb.name,
                    "phase_lag": perturb.phase_lag,
                    "window_beta": perturb.window_beta,
                    "delay_steps": perturb.delay_steps,
                    "noise_amp": perturb.noise_amp,
                    "alpha_cutoff_q": perturb.alpha_cutoff_q,
                    "effective_offset": float(best_match["offset"]) if best_match else 0.0,
                    "direct_best_offset": float(best_direct["offset"]),
                    "match_distance": best_dist,
                    "derived_tradeoff": metrics["mean_tradeoff"],
                    "direct_best_tradeoff": best_direct["mean_tradeoff"],
                    "tradeoff_gap_to_direct_best": metrics["mean_tradeoff"] - best_direct["mean_tradeoff"],
                    **metrics,
                }
                derived_rows.append(derived_row)
    print(f"derived shear done: {len(derived_rows)} rows", flush=True)

    for anchor in anchors:
        anchor_subset = [row for row in derived_rows if row["anchor"] == anchor.name]
        abs_offsets = [abs(row["effective_offset"]) for row in anchor_subset]
        direct_best_offsets = [row["direct_best_offset"] for row in anchor_subset]
        offset_match = [
            abs(row["effective_offset"] - row["direct_best_offset"]) <= 0.02
            for row in anchor_subset
        ]
        summary_rows.append(
            {
                "anchor": anchor.name,
                "mean_effective_offset": float(np.mean([row["effective_offset"] for row in anchor_subset])),
                "median_effective_offset": float(np.median([row["effective_offset"] for row in anchor_subset])),
                "nonzero_offset_fraction": sum(val > 0.004 for val in abs_offsets) / len(abs_offsets),
                "offset_match_fraction": sum(offset_match) / len(offset_match),
                "mean_match_distance": float(np.mean([row["match_distance"] for row in anchor_subset])),
                "mean_tradeoff_gap_to_direct_best": float(np.mean([row["tradeoff_gap_to_direct_best"] for row in anchor_subset])),
                "mean_derived_tradeoff": float(np.mean([row["derived_tradeoff"] for row in anchor_subset])),
                "mean_direct_best_offset": float(np.mean(direct_best_offsets)),
            }
        )

    write_csv(direct_rows, OUT / "direct_band_metrics.csv")
    write_csv(derived_rows, OUT / "derived_shear_metrics.csv")
    write_csv(summary_rows, OUT / "anchor_summary.csv")

    plot_anchor_offsets(derived_rows, OUT / "derived_effective_offsets.png")
    plot_direct_bands(direct_rows, OUT / "direct_anchor_bands.png")
    plot_peak_offsets(direct_rows, OUT / "anchor_peak_offsets_by_capacity.png")

    phi_summary = next(row for row in summary_rows if row["anchor"] == "golden")
    silver_summary = next(row for row in summary_rows if row["anchor"] == "silver")
    bronze_summary = next(row for row in summary_rows if row["anchor"] == "bronze")
    bounded_summary = next(row for row in summary_rows if row["anchor"] == "bounded_probe")

    phi_survives = (
        abs(phi_summary["mean_effective_offset"]) > 0.01
        and phi_summary["offset_match_fraction"] >= 0.45
        and phi_summary["mean_tradeoff_gap_to_direct_best"] > -0.03
    )
    phi_unique = phi_survives and phi_summary["offset_match_fraction"] > max(
        silver_summary["offset_match_fraction"],
        bronze_summary["offset_match_fraction"],
        bounded_summary["offset_match_fraction"],
    )

    if phi_unique:
        verdict = "B-supported / phi-anchor shear survives as a testable derivation lane"
        recommendation = "ledger-only after manual review, no master hardening yet"
    elif phi_survives:
        verdict = "C-leaning / anchor-shear seems generic across multiple irrational anchors"
        recommendation = "wait, compare to broader anchors before any ledger note"
    else:
        verdict = "D/E-leaning / current shear derivation does not rescue phi cleanly"
        recommendation = "no hardening, keep symbolic only"

    strongest = max(derived_rows, key=lambda row: row["derived_tradeoff"])
    weakest = min(derived_rows, key=lambda row: row["derived_tradeoff"])

    report = [
        "# Golden Zipper v5 - Phi Anchor Shear Derivation Test",
        "",
        "Toy telemetry only. Not physics evidence. Not proof of GHP. Not write-law closure.",
        "",
        "## Executive Summary",
        "",
        "This test starts from exact anchors and applies finite-observer distortions: phase lag, window drift, delay, noise, and rational approximation cutoff. It then asks whether the resulting symbolic trails land in the same near-anchor band that direct offset scans prefer.",
        "",
        f"Verdict: **{verdict}**",
        f"Recommendation: **{recommendation}**",
        "",
        "## What This Supports",
        "",
        f"- Golden mean effective offset: `{phi_summary['mean_effective_offset']:.4f}`",
        f"- Golden offset-match fraction to its own direct best band: `{phi_summary['offset_match_fraction']:.3f}`",
        f"- Golden mean tradeoff gap to direct best: `{phi_summary['mean_tradeoff_gap_to_direct_best']:.3f}`",
        "",
        "## Anchor Comparison",
        "",
        "| Anchor | Mean effective offset | Offset-match fraction | Mean tradeoff gap |",
        "|---|---:|---:|---:|",
    ]
    for row in summary_rows:
        report.append(
            f"| {row['anchor']} | {row['mean_effective_offset']:.4f} | {row['offset_match_fraction']:.3f} | {row['mean_tradeoff_gap_to_direct_best']:.3f} |"
        )
    report.extend(
        [
            "",
            "## Reading",
            "",
            "If the phi-shear idea is real, the exact phi anchor should, under finite observation, generate symbolic trails whose effective offsets cluster near the same near-phi band that direct scans prefer.",
            "",
            "This test does not ask whether exact phi wins raw memory tradeoff. It asks whether near-phi winners can be produced from exact phi by finite-observer distortion rather than chosen by hand.",
            "",
            "## Red-Team View",
            "",
            "The skeptical threat remains scoring artifact and generic-anchor behavior. If silver, bronze, or a bounded irrational anchor produce the same kind of shear-band mapping, then the result does not rescue phi uniquely.",
            "",
            "## Strongest Result",
            "",
            f"- Strongest derived run: `{strongest['anchor']}` / `{strongest['perturbation']}` / capacity `{strongest['memory_capacity']}` / effective offset `{strongest['effective_offset']:.4f}` / tradeoff `{strongest['derived_tradeoff']:.3f}`",
            "",
            "## Weakest Result",
            "",
            f"- Weakest derived run: `{weakest['anchor']}` / `{weakest['perturbation']}` / capacity `{weakest['memory_capacity']}` / effective offset `{weakest['effective_offset']:.4f}` / tradeoff `{weakest['derived_tradeoff']:.3f}`",
            "",
            "## Do-Not-Claim Ledger",
            "",
            "- does not prove GHP",
            "- does not prove phi is the code of reality",
            "- does not prove the write-law",
            "- does not prove memory creates matter",
            "- does not prove consciousness",
            "- does not prove VPH",
            "- does not count as physics evidence",
            "- does not justify changing the core share paper",
        ]
    )
    write_text(OUT / "report.md", "\n".join(report))

    print(f"files created: {OUT}")
    print(f"verdict: {verdict}")
    print(f"golden mean effective offset: {phi_summary['mean_effective_offset']:.4f}")
    print(f"golden offset-match fraction: {phi_summary['offset_match_fraction']:.3f}")
    print(f"silver offset-match fraction: {silver_summary['offset_match_fraction']:.3f}")
    print(f"bronze offset-match fraction: {bronze_summary['offset_match_fraction']:.3f}")
    print(f"bounded probe offset-match fraction: {bounded_summary['offset_match_fraction']:.3f}")
    print(f"strongest result: {strongest['anchor']} / {strongest['perturbation']}")
    print(f"weakest result: {weakest['anchor']} / {weakest['perturbation']}")
    print(f"recommendation: {recommendation}")


if __name__ == "__main__":
    main()
