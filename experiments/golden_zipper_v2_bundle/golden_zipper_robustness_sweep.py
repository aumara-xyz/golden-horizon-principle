#!/usr/bin/env python3
"""v3: robustness sweep for the golden zipper memory-policy tradeoff."""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v2_lib import (
    GOLDEN,
    SEED,
    balance_metrics,
    build_slopes,
    complexity_metrics,
    compression_metric,
    ensure_dir,
    family_means,
    generate_sequence,
    periodicity_metrics,
    save_samples,
    strongest_weakest,
    summarize_sequence,
    write_csv,
    write_text,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v3_robustness_outputs"
STEPS = 4096
WINDOW_SIZES = [0.20, 0.34, 0.47]
WINDOW_PHASES = [0.0, 0.17]

CONFIDENCE_WRITE_VALUES = [0.70, 0.80, 0.90]
CONFIDENCE_WITNESS_VALUES = [0.50, 0.575, 0.65]
AMBIGUITY_BAND_VALUES = [0.05, 0.125, 0.20]
MOTIF_WRITE_MIN_VALUES = [0.10, 0.25, 0.40]
MOTIF_WITNESS_MIN_VALUES = [0.15, 0.325, 0.50]


def precompute_policy_features(seq: np.ndarray) -> dict[str, np.ndarray]:
    context_len = 4
    motif_len = 6
    next_counts: dict[tuple[int, ...], Counter] = defaultdict(Counter)
    motif_counts: Counter = Counter()
    for i in range(context_len, len(seq)):
        ctx = tuple(int(x) for x in seq[i - context_len : i])
        next_counts[ctx][int(seq[i])] += 1
    for i in range(len(seq) - motif_len + 1):
        motif = tuple(int(x) for x in seq[i : i + motif_len])
        motif_counts[motif] += 1
    max_motif = max(motif_counts.values()) if motif_counts else 1

    confidence_arr = np.full(len(seq), 0.5, dtype=float)
    motif_arr = np.zeros(len(seq), dtype=float)
    for i, sym in enumerate(seq):
        if i >= context_len:
            ctx = tuple(int(x) for x in seq[i - context_len : i])
            counts = next_counts[ctx]
            total = sum(counts.values())
            confidence_arr[i] = counts[int(sym)] / total if total else 0.5
            if i <= len(seq) - motif_len:
                motif = tuple(int(x) for x in seq[i : i + motif_len])
                motif_arr[i] = motif_counts[motif] / max_motif
    return {"confidence": confidence_arr, "motif": motif_arr}


def memory_policy_with_thresholds(
    seq: np.ndarray,
    features: dict[str, np.ndarray],
    *,
    confidence_write: float,
    confidence_witness: float,
    ambiguity_band: float,
    motif_write_min: float,
    motif_witness_min: float,
) -> dict[str, float]:
    confidence_arr = features["confidence"]
    motif_arr = features["motif"]

    actions = []
    contradicted_writes = 0
    total_writes = 0
    delayed_kept = 0
    delayed_missed = 0

    for i, _sym in enumerate(seq):
        confidence = float(confidence_arr[i])
        motif_score = float(motif_arr[i])

        ambiguous = abs(confidence - 0.5) <= ambiguity_band
        if confidence >= confidence_write or (
            confidence >= confidence_witness and motif_score >= motif_write_min
        ):
            action = "write"
        elif ambiguous or confidence >= confidence_witness or motif_score >= motif_witness_min:
            action = "witness"
        else:
            action = "release"
        actions.append(action)

        if action == "write":
            total_writes += 1
            if motif_score < max(0.08, motif_write_min * 0.5):
                contradicted_writes += 1

        delayed_candidate = (
            max(0.12, motif_write_min * 0.75) <= motif_score <= max(motif_witness_min, motif_write_min + 0.10)
            and confidence < confidence_write
        )
        if delayed_candidate and action == "witness":
            delayed_kept += 1
        elif delayed_candidate and action == "release":
            delayed_missed += 1

    delayed_total = delayed_kept + delayed_missed
    counts = Counter(actions)
    return {
        "write_count": float(counts["write"]),
        "witness_count": float(counts["witness"]),
        "release_count": float(counts["release"]),
        "pollution": contradicted_writes / total_writes if total_writes else 0.0,
        "delayed_retention": delayed_kept / delayed_total if delayed_total else 0.0,
    }


def plot_rank_table(rows: list[dict], path: Path) -> None:
    families = sorted({row["family"] for row in rows})
    rank_cols = ["top1_count", "top2_count", "top3_count"]
    data = np.array([[float(row[col]) for col in rank_cols] for row in rows])
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(data, cmap="YlOrBr", aspect="auto")
    ax.set_xticks(np.arange(len(rank_cols)), labels=["#1", "#2", "#3"])
    ax.set_yticks(np.arange(len(families)), labels=families)
    ax.set_title("Robustness table: family rank counts across threshold sweep")
    for i in range(len(families)):
        for j in range(len(rank_cols)):
            ax.text(j, i, int(data[i, j]), ha="center", va="center", color="black")
    fig.colorbar(im, ax=ax, label="count")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_near_golden(rows: list[dict], path: Path) -> None:
    subset = sorted(
        [
            row
            for row in rows
            if row["family"] in {"golden", "near_golden"}
            and abs(float(row["alpha"]) - GOLDEN) <= 0.05
        ],
        key=lambda row: float(row["alpha"]),
    )
    xs = [float(row["alpha"]) for row in subset]
    ys = [float(row["tradeoff_score"]) for row in subset]
    plt.figure(figsize=(8, 5))
    plt.plot(xs, ys, marker="o", color="#1565c0")
    plt.axvline(GOLDEN, color="gold", linestyle="--", linewidth=1.5, label="golden")
    plt.xlabel("alpha")
    plt.ylabel("mean tradeoff score")
    plt.title("Near-golden perturbation sweep")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_pareto(rows: list[dict], x_key: str, y_key: str, title: str, path: Path, invert_x: bool = False) -> None:
    families = sorted({row["family"] for row in rows})
    colors = plt.cm.tab10(np.linspace(0, 1, len(families)))
    plt.figure(figsize=(8, 6))
    for family, color in zip(families, colors):
        subset = [row for row in rows if row["family"] == family]
        x = np.mean([float(row[x_key]) for row in subset])
        y = np.mean([float(row[y_key]) for row in subset])
        plt.scatter(x, y, color=color, s=70, label=family)
        plt.text(x, y, family, fontsize=8, ha="left", va="bottom")
    plt.xlabel(x_key + (" (lower is better)" if invert_x else ""))
    plt.ylabel(y_key)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    sequences = []
    samples = []
    compression_cap = 1.0
    slopes = build_slopes()
    for slope in slopes:
        for window_size in WINDOW_SIZES:
            for phase in WINDOW_PHASES:
                seq = generate_sequence(slope.alpha, STEPS, window_size, phase, mode="single")
                bal, spread = balance_metrics(seq)
                _, comp_dev = complexity_metrics(seq)
                periodicity, _ = periodicity_metrics(seq)
                compress = compression_metric(seq)
                compression_cap = max(compression_cap, compress)
                sequences.append(
                    {
                        "name": slope.name,
                        "family": slope.family,
                        "alpha": slope.alpha,
                        "window_size": window_size,
                        "phase": phase,
                        "seq": seq,
                        "balance_score": bal,
                        "balance_spread": spread,
                        "complexity_deviation": comp_dev,
                        "periodicity_match": periodicity,
                        "compression_score": compress,
                        "policy_features": precompute_policy_features(seq),
                    }
                )
                if window_size == 0.34 and phase == 0.0:
                    samples.append(f"[{slope.name}] {summarize_sequence(seq)}")

    policy_grid = list(
        itertools.product(
            CONFIDENCE_WRITE_VALUES,
            CONFIDENCE_WITNESS_VALUES,
            AMBIGUITY_BAND_VALUES,
            MOTIF_WRITE_MIN_VALUES,
            MOTIF_WITNESS_MIN_VALUES,
        )
    )

    rows = []
    family_rank_rows = []
    for policy_id, (
        confidence_write,
        confidence_witness,
        ambiguity_band,
        motif_write_min,
        motif_witness_min,
    ) in enumerate(policy_grid, start=1):
        policy_rows = []
        for base in sequences:
            policy = memory_policy_with_thresholds(
                base["seq"],
                base["policy_features"],
                confidence_write=confidence_write,
                confidence_witness=confidence_witness,
                ambiguity_band=ambiguity_band,
                motif_write_min=motif_write_min,
                motif_witness_min=motif_witness_min,
            )
            row = {
                "policy_id": policy_id,
                "name": base["name"],
                "family": base["family"],
                "alpha": base["alpha"],
                "window_size": base["window_size"],
                "phase": base["phase"],
                "confidence_write": confidence_write,
                "confidence_witness": confidence_witness,
                "ambiguity_band": ambiguity_band,
                "motif_write_min": motif_write_min,
                "motif_witness_min": motif_witness_min,
                "balance_score": base["balance_score"],
                "balance_spread": base["balance_spread"],
                "complexity_deviation": base["complexity_deviation"],
                "periodicity_match": base["periodicity_match"],
                "compression_score": base["compression_score"],
                "write_count": policy["write_count"],
                "witness_count": policy["witness_count"],
                "release_count": policy["release_count"],
                "pollution": policy["pollution"],
                "delayed_retention": policy["delayed_retention"],
            }
            row["tradeoff_score"] = (
                0.9 * (1.0 - min(float(row["periodicity_match"]) * 3.0, 1.0))
                + 1.1 * float(row["delayed_retention"])
                + 0.8 * (1.0 - float(row["pollution"]))
                + 0.5 * float(row["balance_score"])
                + 0.2 * float(row["compression_score"]) / compression_cap
            )
            rows.append(row)
            policy_rows.append(row)

        family_scores = []
        for family in sorted({row["family"] for row in policy_rows}):
            subset = [row for row in policy_rows if row["family"] == family]
            family_scores.append(
                {
                    "family": family,
                    "tradeoff_score": float(np.mean([float(row["tradeoff_score"]) for row in subset])),
                }
            )
        ranked = sorted(family_scores, key=lambda row: row["tradeoff_score"], reverse=True)
        for rank, ranked_row in enumerate(ranked[:3], start=1):
            family_rank_rows.append(
                {
                    "policy_id": policy_id,
                    "rank": rank,
                    "family": ranked_row["family"],
                    "tradeoff_score": ranked_row["tradeoff_score"],
                }
            )

    write_csv(rows, OUT / "metrics.csv")
    write_csv(family_rank_rows, OUT / "ranked_policies.csv")
    save_samples(samples, OUT / "sample_sequences.txt")

    rank_counts = []
    for family in sorted({row["family"] for row in rows}):
        top1 = sum(1 for row in family_rank_rows if row["family"] == family and row["rank"] == 1)
        top2 = sum(1 for row in family_rank_rows if row["family"] == family and row["rank"] == 2)
        top3 = sum(1 for row in family_rank_rows if row["family"] == family and row["rank"] == 3)
        rank_counts.append(
            {
                "family": family,
                "top1_count": top1,
                "top2_count": top2,
                "top3_count": top3,
            }
        )
    write_csv(rank_counts, OUT / "robustness_table.csv")
    plot_rank_table(rank_counts, OUT / "robustness_table.png")

    aggregated = family_means(
        rows,
        [
            "periodicity_match",
            "delayed_retention",
            "pollution",
            "write_count",
            "witness_count",
            "release_count",
            "tradeoff_score",
        ],
    )
    plot_near_golden(
        [
            {
                "family": family,
                "alpha": np.mean([float(row["alpha"]) for row in rows if row["name"] == name]),
                "tradeoff_score": np.mean([float(row["tradeoff_score"]) for row in rows if row["name"] == name]),
            }
            for name, family in sorted({(row["name"], row["family"]) for row in rows})
        ],
        OUT / "near_golden_perturbation_plot.png",
    )
    plot_pareto(rows, "periodicity_match", "delayed_retention", "Pareto: phase-lock vs delayed retention", OUT / "pareto_phase_lock_vs_delayed_retention.png", invert_x=True)
    plot_pareto(rows, "pollution", "delayed_retention", "Pareto: pollution vs delayed retention", OUT / "pareto_pollution_vs_delayed_retention.png", invert_x=True)

    strongest, weakest = strongest_weakest(rows, "tradeoff_score")
    golden_counts = next(row for row in rank_counts if row["family"] == "golden")
    total_policies = len(policy_grid)
    golden_top_tier = golden_counts["top1_count"] + golden_counts["top2_count"] + golden_counts["top3_count"]
    golden_support = golden_top_tier / total_policies
    golden_is_robust = golden_support >= 0.60 and golden_counts["top1_count"] > 0

    report = [
        "# Golden Zipper v3 — Robustness Sweep",
        "",
        "Toy telemetry only. Not physics evidence.",
        "",
        "This sweep varies the memory-policy thresholds to test whether golden remains top-tier across many plausible write / witness / release policies, or only under one chosen policy.",
        "",
        f"Threshold grid size: **{total_policies}** policy settings.",
        "",
        "## Robustness Table",
        "",
        "| Family | #1 count | #2 count | #3 count | Mean tradeoff | Mean phase-lock | Mean delayed retention | Mean pollution |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rank_counts:
        family = row["family"]
        means = aggregated[family]
        report.append(
            f"| {family} | {row['top1_count']} | {row['top2_count']} | {row['top3_count']} | {means['tradeoff_score']:.3f} | {means['periodicity_match']:.3f} | {means['delayed_retention']:.3f} | {means['pollution']:.3f} |"
        )
    report.extend(
        [
            "",
            "## Supports",
            "",
            (
                "Golden remains robustly top-tier in anti-locking / delayed-retention tradeoff across threshold sweeps."
                if golden_is_robust
                else "Golden remains competitive on anti-locking / delayed-retention, but the advantage is not fully robust across the threshold sweep."
            ),
            "",
            "- The sweep cleanly separates policy tuning from the underlying symbolic trail.",
            "- Near-golden perturbations help show whether golden is a point winner or part of a broader admissible band.",
            "- The Pareto views make it easier to see whether lower phase-lock comes with retention costs.",
            "",
            "## Does Not Support",
            "",
            "- no proof",
            "- no physics evidence",
            "- no write-law closure",
            "- no VPH derivation",
            "- no consciousness claim",
            "",
            "## Next Test",
            "",
            "- expand the near-golden band beyond +/-0.02 into a denser local alpha sweep",
            "- test whether the same tradeoff survives moving-window observer variants under the same threshold grid",
            "- compare the top-tier families against a null family of low-discrepancy irrational slopes, not only silver/bronze/random controls",
            "",
            f"Strongest run: `{strongest['name']}` policy={int(strongest['policy_id'])} window={strongest['window_size']:.2f} phase={strongest['phase']:.2f}",
            f"Weakest run: `{weakest['name']}` policy={int(weakest['policy_id'])} window={weakest['window_size']:.2f} phase={weakest['phase']:.2f}",
            "",
            (
                "Success language: Golden remains robustly top-tier in anti-locking / delayed-retention tradeoff across threshold sweeps."
                if golden_is_robust
                else "Failure language: Golden's advantage depends on the chosen memory policy and should remain symbolic only."
            ),
        ]
    )
    write_text(OUT / "report.md", "\n".join(report))

    print(f"files created: {OUT}")
    print(f"strongest result: {strongest['name']}")
    print(f"weakest result: {weakest['name']}")
    print(f"whether golden slope beat controls: {'yes' if aggregated['golden']['tradeoff_score'] > max(aggregated['rational_approx']['tradeoff_score'], aggregated['rational_control']['tradeoff_score']) else 'mixed'}")
    print(
        "whether this deserves master hardening: "
        + ("maybe" if golden_is_robust else "not yet")
    )


if __name__ == "__main__":
    np.random.seed(SEED)
    main()
