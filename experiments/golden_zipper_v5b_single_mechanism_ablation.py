#!/usr/bin/env python3
"""v5b single-mechanism ablation for direct-band mapping from exact anchors."""

from __future__ import annotations

import csv
import math
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
OUT = ROOT / "golden_zipper_v5b_outputs"

WINDOW_SIZES = [0.20, 0.382, 0.618]
PHASES = [0.0, 0.17]
LENGTHS = [5000]
MEMORY_CAPACITIES = [50, 100, 400]
OFFSET_GRID = np.arange(-0.08, 0.0801, 0.004)
DIRECT_BAND_DELTA = 0.01


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
class MechanismSpec:
    mechanism: str
    variant: str
    phase_lag: float = 0.0
    window_beta: float = 0.0
    delay_steps: int = 0
    noise_amp: float = 0.0
    alpha_cutoff_q: int = 0


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
    bounded_probe = 1.0 / (
        2.0
        + 1.0
        / (1.0 + 1.0 / (2.0 + 1.0 / (1.0 + 1.0 / (2.0 + 1.0 / (1.0 + 1.0 / 2.0)))))
    )
    return [
        AnchorSpec("golden", golden, "phi_anchor"),
        AnchorSpec("silver", silver, "metallic_anchor"),
        AnchorSpec("bronze", bronze, "metallic_anchor"),
        AnchorSpec("bounded_probe", bounded_probe, "bounded_anchor"),
    ]


def build_conditions() -> list[ObserverCondition]:
    rows = []
    for window_size in WINDOW_SIZES:
        for phase in PHASES:
            for length in LENGTHS:
                for memory_capacity in MEMORY_CAPACITIES:
                    rows.append(
                        ObserverCondition(
                            window_size=window_size,
                            phase=phase,
                            length=length,
                            memory_capacity=memory_capacity,
                        )
                    )
    return rows


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


def build_mechanism_specs() -> list[MechanismSpec]:
    return [
        MechanismSpec("phase_lag", "small", phase_lag=0.015),
        MechanismSpec("phase_lag", "big", phase_lag=0.045),
        MechanismSpec("window_drift", "small", window_beta=0.004),
        MechanismSpec("window_drift", "big", window_beta=0.011),
        MechanismSpec("delay", "small", delay_steps=3),
        MechanismSpec("delay", "big", delay_steps=8),
        MechanismSpec("noise", "small", noise_amp=0.0015),
        MechanismSpec("noise", "big", noise_amp=0.0045),
        MechanismSpec("rational_cutoff", "q34", alpha_cutoff_q=34),
        MechanismSpec("rational_cutoff", "q55", alpha_cutoff_q=55),
    ]


def approx_alpha(anchor_alpha: float, q: int) -> float:
    if q <= 0:
        return anchor_alpha
    return round(anchor_alpha * q) / q


def generate_anchor_sequence(
    alpha: float,
    condition: ObserverCondition,
    mechanism: MechanismSpec | None = None,
) -> np.ndarray:
    mechanism = mechanism or MechanismSpec("none", "exact")
    alpha_eff = approx_alpha(alpha, mechanism.alpha_cutoff_q)
    n = np.arange(condition.length, dtype=float)
    delayed_n = np.maximum(n - mechanism.delay_steps, 0.0)
    x = delayed_n * alpha_eff + condition.phase + mechanism.phase_lag
    if mechanism.noise_amp > 0.0:
        x = x + mechanism.noise_amp * np.sin(2.0 * math.pi * (0.071 * n + alpha * 3.0))
    x = wrap01(x)
    starts = wrap01(condition.phase + mechanism.window_beta * n)
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


def summarize_direct_bands(direct_rows: list[dict]) -> list[dict]:
    band_rows = []
    grouped = {}
    for row in direct_rows:
        key = (
            row["anchor"],
            row["window_size"],
            row["phase"],
            row["length"],
            row["memory_capacity"],
        )
        grouped.setdefault(key, []).append(row)
    for key, rows in grouped.items():
        best = max(rows, key=lambda row: row["mean_tradeoff"])
        band = [row for row in rows if row["mean_tradeoff"] >= best["mean_tradeoff"] - DIRECT_BAND_DELTA]
        offsets = [float(row["offset"]) for row in band]
        band_rows.append(
            {
                "anchor": key[0],
                "window_size": key[1],
                "phase": key[2],
                "length": key[3],
                "memory_capacity": key[4],
                "best_offset": float(best["offset"]),
                "best_tradeoff": float(best["mean_tradeoff"]),
                "band_low_offset": float(min(offsets)),
                "band_high_offset": float(max(offsets)),
                "band_width": float(max(offsets) - min(offsets)),
                "band_count": len(band),
            }
        )
    return band_rows


def plot_direct_bands(direct_rows: list[dict], band_rows: list[dict], path: Path) -> None:
    anchors = sorted({row["anchor"] for row in direct_rows})
    fig, axes = plt.subplots(len(anchors), 1, figsize=(9, 3 * len(anchors)), sharex=True)
    if len(anchors) == 1:
        axes = [axes]
    for ax, anchor in zip(axes, anchors):
        subset = sorted(
            [
                row
                for row in direct_rows
                if row["anchor"] == anchor and row["window_size"] == 0.382 and row["phase"] == 0.0 and row["memory_capacity"] == 100
            ],
            key=lambda row: row["offset"],
        )
        band = next(
            row
            for row in band_rows
            if row["anchor"] == anchor and row["window_size"] == 0.382 and row["phase"] == 0.0 and row["memory_capacity"] == 100
        )
        ax.plot([row["offset"] for row in subset], [row["mean_tradeoff"] for row in subset], color="#0d47a1")
        ax.axvspan(band["band_low_offset"], band["band_high_offset"], color="#ffcc80", alpha=0.35)
        ax.axvline(0.0, color="black", linestyle="--", linewidth=1.0)
        ax.set_title(anchor)
        ax.set_ylabel("mean tradeoff")
    axes[-1].set_xlabel("offset from exact anchor")
    fig.suptitle("Direct scan bands at window 0.382, phase 0.0, capacity 100", y=0.995)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_band_match_heatmap(summary_rows: list[dict], path: Path) -> None:
    anchors = sorted({row["anchor"] for row in summary_rows})
    columns = sorted(
        {(row["mechanism"], row["variant"]) for row in summary_rows},
        key=lambda item: (item[0], item[1]),
    )
    matrix = np.zeros((len(anchors), len(columns)))
    for i, anchor in enumerate(anchors):
        for j, column in enumerate(columns):
            match = next(
                row
                for row in summary_rows
                if row["anchor"] == anchor and row["mechanism"] == column[0] and row["variant"] == column[1]
            )
            matrix[i, j] = match["band_match_fraction"]
    plt.figure(figsize=(12, 4.5))
    plt.imshow(matrix, cmap="YlGnBu", vmin=0.0, vmax=1.0, aspect="auto")
    plt.xticks(range(len(columns)), [f"{mech}\n{variant}" for mech, variant in columns], fontsize=8)
    plt.yticks(range(len(anchors)), anchors)
    for i in range(len(anchors)):
        for j in range(len(columns)):
            plt.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=7)
    plt.colorbar(label="band-match fraction")
    plt.title("How often a single mechanism lands inside the direct near-best band")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_effective_offsets(summary_rows: list[dict], path: Path) -> None:
    anchors = sorted({row["anchor"] for row in summary_rows})
    columns = sorted(
        {(row["mechanism"], row["variant"]) for row in summary_rows},
        key=lambda item: (item[0], item[1]),
    )
    x = np.arange(len(columns))
    plt.figure(figsize=(12, 5))
    for idx, anchor in enumerate(anchors):
        subset = [
            next(
                row
                for row in summary_rows
                if row["anchor"] == anchor and row["mechanism"] == mech and row["variant"] == variant
            )
            for mech, variant in columns
        ]
        y = [row["mean_effective_offset"] for row in subset]
        plt.plot(x, y, marker="o", linewidth=1.5, label=anchor)
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1.0)
    plt.xticks(x, [f"{mech}\n{variant}" for mech, variant in columns], fontsize=8)
    plt.ylabel("mean effective offset")
    plt.title("Mean effective offsets induced by one mechanism at a time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    anchors = build_anchors()
    conditions = build_conditions()
    policies = build_policies()
    mechanisms = build_mechanism_specs()

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
                direct_cache[
                    (
                        anchor.name,
                        round(float(offset), 6),
                        condition.window_size,
                        condition.phase,
                        condition.length,
                        condition.memory_capacity,
                    )
                ] = (seq, metrics)

    band_rows = summarize_direct_bands(direct_rows)
    band_lookup = {
        (
            row["anchor"],
            row["window_size"],
            row["phase"],
            row["length"],
            row["memory_capacity"],
        ): row
        for row in band_rows
    }

    derived_rows = []
    for anchor in anchors:
        for condition in conditions:
            key = (anchor.name, condition.window_size, condition.phase, condition.length, condition.memory_capacity)
            base_direct = [
                row
                for row in direct_rows
                if row["anchor"] == anchor.name
                and row["window_size"] == condition.window_size
                and row["phase"] == condition.phase
                and row["length"] == condition.length
                and row["memory_capacity"] == condition.memory_capacity
            ]
            band = band_lookup[key]
            best_direct = max(base_direct, key=lambda row: row["mean_tradeoff"])
            for mechanism in mechanisms:
                seq = generate_anchor_sequence(anchor.alpha, condition, mechanism)
                metrics = evaluate_memory_tradeoff(seq, condition.memory_capacity, policies)
                best_match = None
                best_dist = 1.0
                for candidate in base_direct:
                    cand_seq, _ = direct_cache[
                        (
                            anchor.name,
                            round(float(candidate["offset"]), 6),
                            condition.window_size,
                            condition.phase,
                            condition.length,
                            condition.memory_capacity,
                        )
                    ]
                    dist = hamming_distance(seq, cand_seq)
                    if dist < best_dist:
                        best_dist = dist
                        best_match = candidate
                effective_offset = float(best_match["offset"]) if best_match else 0.0
                derived_rows.append(
                    {
                        "anchor": anchor.name,
                        "anchor_family": anchor.family,
                        "mechanism": mechanism.mechanism,
                        "variant": mechanism.variant,
                        "window_size": condition.window_size,
                        "phase": condition.phase,
                        "length": condition.length,
                        "memory_capacity": condition.memory_capacity,
                        "phase_lag": mechanism.phase_lag,
                        "window_beta": mechanism.window_beta,
                        "delay_steps": mechanism.delay_steps,
                        "noise_amp": mechanism.noise_amp,
                        "alpha_cutoff_q": mechanism.alpha_cutoff_q,
                        "effective_offset": effective_offset,
                        "match_distance": best_dist,
                        "in_direct_band": band["band_low_offset"] <= effective_offset <= band["band_high_offset"],
                        "band_low_offset": band["band_low_offset"],
                        "band_high_offset": band["band_high_offset"],
                        "direct_best_offset": float(best_direct["offset"]),
                        "derived_tradeoff": metrics["mean_tradeoff"],
                        "direct_best_tradeoff": best_direct["mean_tradeoff"],
                        "tradeoff_gap_to_direct_best": metrics["mean_tradeoff"] - best_direct["mean_tradeoff"],
                        **metrics,
                    }
                )

    anchor_mechanism_summary = []
    for anchor in anchors:
        for mechanism in mechanisms:
            subset = [
                row
                for row in derived_rows
                if row["anchor"] == anchor.name
                and row["mechanism"] == mechanism.mechanism
                and row["variant"] == mechanism.variant
            ]
            anchor_mechanism_summary.append(
                {
                    "anchor": anchor.name,
                    "mechanism": mechanism.mechanism,
                    "variant": mechanism.variant,
                    "runs": len(subset),
                    "band_match_fraction": float(np.mean([float(row["in_direct_band"]) for row in subset])),
                    "mean_effective_offset": float(np.mean([row["effective_offset"] for row in subset])),
                    "median_effective_offset": float(np.median([row["effective_offset"] for row in subset])),
                    "mean_abs_effective_offset": float(np.mean([abs(row["effective_offset"]) for row in subset])),
                    "mean_match_distance": float(np.mean([row["match_distance"] for row in subset])),
                    "mean_tradeoff_gap_to_direct_best": float(
                        np.mean([row["tradeoff_gap_to_direct_best"] for row in subset])
                    ),
                    "mean_direct_band_width": float(
                        np.mean([row["band_high_offset"] - row["band_low_offset"] for row in subset])
                    ),
                }
            )

    mechanism_summary = []
    for mechanism in mechanisms:
        subset = [
            row
            for row in derived_rows
            if row["mechanism"] == mechanism.mechanism and row["variant"] == mechanism.variant
        ]
        mechanism_summary.append(
            {
                "mechanism": mechanism.mechanism,
                "variant": mechanism.variant,
                "runs": len(subset),
                "band_match_fraction": float(np.mean([float(row["in_direct_band"]) for row in subset])),
                "mean_effective_offset": float(np.mean([row["effective_offset"] for row in subset])),
                "mean_abs_effective_offset": float(np.mean([abs(row["effective_offset"]) for row in subset])),
                "mean_match_distance": float(np.mean([row["match_distance"] for row in subset])),
                "mean_tradeoff_gap_to_direct_best": float(
                    np.mean([row["tradeoff_gap_to_direct_best"] for row in subset])
                ),
            }
        )

    write_csv(direct_rows, OUT / "direct_band_metrics.csv")
    write_csv(band_rows, OUT / "direct_band_summary.csv")
    write_csv(derived_rows, OUT / "single_mechanism_metrics.csv")
    write_csv(anchor_mechanism_summary, OUT / "anchor_mechanism_summary.csv")
    write_csv(mechanism_summary, OUT / "mechanism_summary.csv")

    plot_direct_bands(direct_rows, band_rows, OUT / "direct_anchor_bands.png")
    plot_band_match_heatmap(anchor_mechanism_summary, OUT / "mechanism_band_match_heatmap.png")
    plot_effective_offsets(anchor_mechanism_summary, OUT / "effective_offsets_by_mechanism.png")

    any_positive_match = any(row["band_match_fraction"] > 0.0 for row in anchor_mechanism_summary)
    top_matches = sorted(
        anchor_mechanism_summary,
        key=lambda row: (row["band_match_fraction"], -row["mean_match_distance"], row["mean_tradeoff_gap_to_direct_best"]),
        reverse=True,
    )[:5]
    weakest_matches = sorted(
        anchor_mechanism_summary,
        key=lambda row: (row["band_match_fraction"], -row["mean_match_distance"], row["mean_tradeoff_gap_to_direct_best"]),
    )[:5]
    best_overall = max(derived_rows, key=lambda row: row["derived_tradeoff"])
    worst_overall = min(derived_rows, key=lambda row: row["derived_tradeoff"])

    report = [
        "# Golden Zipper v5b - Single-Mechanism Ablation",
        "",
        "Toy telemetry only. Not physics evidence. Not proof of GHP. Not a claim of unique phi recovery.",
        "",
        "## Setup",
        "",
        "This run starts from exact anchors (`golden`, `silver`, `bronze`, `bounded_probe`) and turns on exactly one perturbation mechanism at a time.",
        "",
        "Mechanisms scanned:",
        "- `phase_lag` only",
        "- `window_drift` only",
        "- `delay` only",
        "- `noise` only",
        "- `rational_cutoff` only",
        "",
        f"Direct near-best band definition: offsets whose direct-scan mean tradeoff stays within `{DIRECT_BAND_DELTA:.3f}` of the condition-wise direct best.",
        "",
        "A derived run counts as a band match when its nearest direct-scan effective offset lands inside that band.",
        "",
        "## Conservative Read",
        "",
        "This is a mapping test, not a uniqueness test. A high band-match fraction only says a given one-knob perturbation can often imitate a direct near-best offset under this toy scorer.",
        "",
        "## Mechanism Summary",
        "",
        "| Mechanism | Variant | Band-match fraction | Mean effective offset | Mean tradeoff gap |",
        "|---|---|---:|---:|---:|",
    ]
    for row in mechanism_summary:
        report.append(
            f"| {row['mechanism']} | {row['variant']} | {row['band_match_fraction']:.3f} | {row['mean_effective_offset']:.4f} | {row['mean_tradeoff_gap_to_direct_best']:.3f} |"
        )
    report.extend(
        [
            "",
            "## Anchor-Mechanism Readout",
            "",
            (
                "No anchor-mechanism pair reached a positive band-match fraction under the current narrow direct-band rule, so the table below lists the closest misses."
                if not any_positive_match
                else "The table below lists the strongest positive matches."
            ),
            "",
            "| Anchor | Mechanism | Variant | Band-match fraction | Mean effective offset | Mean match distance |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in top_matches:
        report.append(
            f"| {row['anchor']} | {row['mechanism']} | {row['variant']} | {row['band_match_fraction']:.3f} | {row['mean_effective_offset']:.4f} | {row['mean_match_distance']:.3f} |"
        )
    report.extend(
        [
            "",
            "## Farthest Misses",
            "",
            "| Anchor | Mechanism | Variant | Band-match fraction | Mean effective offset | Mean match distance |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in weakest_matches:
        report.append(
            f"| {row['anchor']} | {row['mechanism']} | {row['variant']} | {row['band_match_fraction']:.3f} | {row['mean_effective_offset']:.4f} | {row['mean_match_distance']:.3f} |"
        )
    report.extend(
        [
            "",
            "## Best / Worst Derived Runs",
            "",
            f"- Best derived tradeoff: `{best_overall['anchor']}` / `{best_overall['mechanism']}` / `{best_overall['variant']}` / capacity `{best_overall['memory_capacity']}` / effective offset `{best_overall['effective_offset']:.4f}` / tradeoff `{best_overall['derived_tradeoff']:.3f}`",
            f"- Weakest derived tradeoff: `{worst_overall['anchor']}` / `{worst_overall['mechanism']}` / `{worst_overall['variant']}` / capacity `{worst_overall['memory_capacity']}` / effective offset `{worst_overall['effective_offset']:.4f}` / tradeoff `{worst_overall['derived_tradeoff']:.3f}`",
            "",
            "## Do-Not-Claim Ledger",
            "",
            "- does not prove GHP",
            "- does not prove phi is uniquely rescued by a single perturbation mechanism",
            "- does not show that any mechanism is physically real",
            "- does not justify changing the core paper",
            "- does not show uniqueness against a broader control family",
        ]
    )
    write_text(OUT / "report.md", "\n".join(report))

    print(f"files created: {OUT}")
    print(f"direct rows: {len(direct_rows)}")
    print(f"derived rows: {len(derived_rows)}")


if __name__ == "__main__":
    main()
