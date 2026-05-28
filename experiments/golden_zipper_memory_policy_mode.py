#!/usr/bin/env python3
"""v2C: memory-policy mode for the golden zipper toy."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from golden_zipper_v2_lib import (
    SEED,
    alpha_phase_diagram,
    balance_metrics,
    bar_family,
    build_slopes,
    complexity_metrics,
    compression_metric,
    ensure_dir,
    family_means,
    generate_sequence,
    memory_policy,
    periodicity_metrics,
    robust_std,
    save_samples,
    strongest_weakest,
    summarize_sequence,
    write_csv,
    write_text,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v2_memory_policy_outputs"
STEPS = 4096
WINDOW_SIZES = [0.20, 0.34, 0.47]
WINDOW_PHASES = [0.0, 0.17]


def plot_action_counts(rows: list[dict], path: Path) -> None:
    families = sorted({row["family"] for row in rows})
    writes = [np.mean([float(r["write_count"]) for r in rows if r["family"] == fam]) for fam in families]
    witness = [np.mean([float(r["witness_count"]) for r in rows if r["family"] == fam]) for fam in families]
    release = [np.mean([float(r["release_count"]) for r in rows if r["family"] == fam]) for fam in families]
    xs = np.arange(len(families))
    plt.figure(figsize=(11, 6))
    plt.bar(xs, writes, label="write", color="#2e7d32")
    plt.bar(xs, witness, bottom=writes, label="witness", color="#f9a825")
    plt.bar(xs, release, bottom=np.array(writes) + np.array(witness), label="release", color="#546e7a")
    plt.xticks(xs, families, rotation=30, ha="right")
    plt.ylabel("mean action count")
    plt.title("Memory-policy write / witness / release counts")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    rows = []
    samples = []
    compression_cap = 1.0
    for slope in build_slopes():
        for window_size in WINDOW_SIZES:
            for phase in WINDOW_PHASES:
                seq = generate_sequence(slope.alpha, STEPS, window_size, phase, mode="single")
                bal, spread = balance_metrics(seq)
                _, comp_dev = complexity_metrics(seq)
                periodicity, best_period = periodicity_metrics(seq)
                policy = memory_policy(seq)
                compress = compression_metric(seq)
                compression_cap = max(compression_cap, compress)
                row = {
                    "name": slope.name,
                    "family": slope.family,
                    "alpha": slope.alpha,
                    "window_size": window_size,
                    "phase": phase,
                    "balance_score": bal,
                    "balance_spread": spread,
                    "complexity_deviation": comp_dev,
                    "periodicity_match": periodicity,
                    "write_count": policy["write_count"],
                    "witness_count": policy["witness_count"],
                    "release_count": policy["release_count"],
                    "pollution": policy["pollution"],
                    "delayed_retention": policy["delayed_retention"],
                    "compression_score": compress,
                }
                rows.append(row)
                if window_size == 0.34 and phase == 0.0:
                    samples.append(f"[{slope.name}] {summarize_sequence(seq)}")

    for row in rows:
        row["tradeoff_score"] = (
            0.9 * (1.0 - min(float(row["periodicity_match"]) * 3.0, 1.0))
            + 1.1 * float(row["delayed_retention"])
            + 0.8 * (1.0 - float(row["pollution"]))
            + 0.5 * float(row["balance_score"])
            + 0.2 * float(row["compression_score"]) / compression_cap
        )

    write_csv(rows, OUT / "metrics.csv")
    save_samples(samples, OUT / "sample_sequences.txt")
    bar_family(rows, "pollution", "Memory-policy pollution by family", "pollution", OUT / "pollution_plot.png")
    bar_family(rows, "delayed_retention", "Delayed-meaning retention by family", "delayed retention", OUT / "delayed_retention_plot.png")
    plot_action_counts(rows, OUT / "write_witness_release_counts.png")
    alpha_phase_diagram(rows, "tradeoff_score", "Memory-policy phase diagram: tradeoff score", OUT / "phase_diagram.png", cmap="cividis")

    means = family_means(
        rows,
        [
            "balance_score",
            "periodicity_match",
            "pollution",
            "delayed_retention",
            "write_count",
            "witness_count",
            "release_count",
            "tradeoff_score",
        ],
    )
    strongest, weakest = strongest_weakest(rows, "tradeoff_score")
    golden = means["golden"]
    rational = means["rational_approx"]
    controls = means["rational_control"]
    randoms = means["random"]
    silver = means["silver"]
    bronze = means["bronze"]
    anti_lock = golden["periodicity_match"] < min(rational["periodicity_match"], controls["periodicity_match"])
    delayed = golden["delayed_retention"] > max(rational["delayed_retention"], controls["delayed_retention"], randoms["delayed_retention"])
    stable_write = golden["pollution"] <= randoms["pollution"] and golden["write_count"] > golden["release_count"]
    robust = robust_std(rows, "golden", "tradeoff_score") < 0.50

    report = [
        "# Golden Zipper v2C — Memory Policy Mode",
        "",
        "Toy telemetry only. Not physics evidence.",
        "",
        "This mode applies write / witness / release only after the base symbolic trail is generated. It asks whether golden sampling gives a better structured-enough-to-remember but irrational-enough-not-to-freeze tradeoff.",
        "",
        "## Family Means",
        "",
        "| Family | Phase-lock | Pollution | Delayed retention | Write | Witness | Release | Tradeoff |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for family in sorted(means):
        m = means[family]
        report.append(
            f"| {family} | {m['periodicity_match']:.3f} | {m['pollution']:.3f} | {m['delayed_retention']:.3f} | {m['write_count']:.1f} | {m['witness_count']:.1f} | {m['release_count']:.1f} | {m['tradeoff_score']:.3f} |"
        )
    report.extend(
        [
            "",
            "## Key Result",
            "",
            "Golden slope did not win every metric, but may occupy the best anti-locking / delayed-retention tradeoff region.",
            "",
            f"- Anti-locking vs rationals: **{'better' if anti_lock else 'mixed'}**",
            f"- Delayed-meaning retention: **{'better' if delayed else 'mixed'}**",
            f"- Stable write behavior: **{'better' if stable_write else 'mixed'}**",
            f"- Robust to window size/phase: **{'reasonably' if robust else 'not strongly'}**",
            f"- Silver beats golden? **{'no clear overall' if silver['tradeoff_score'] <= golden['tradeoff_score'] else 'yes on this toy score'}**",
            f"- Bronze beats golden? **{'no clear overall' if bronze['tradeoff_score'] <= golden['tradeoff_score'] else 'yes on this toy score'}**",
            "",
            f"Strongest run: `{strongest['name']}` window={strongest['window_size']:.2f} phase={strongest['phase']:.2f}",
            f"Weakest run: `{weakest['name']}` window={weakest['window_size']:.2f} phase={weakest['phase']:.2f}",
            "",
            "Do-not-claim: no confirmation, no write-law closure, no VPH derivation, no consciousness derivation.",
        ]
    )
    write_text(OUT / "report.md", "\n".join(report))

    print(f"files created: {OUT}")
    print(f"strongest result: {strongest['name']}")
    print(f"weakest result: {weakest['name']}")
    print(f"whether golden slope beat controls: {'mixed' if not (anti_lock and delayed) else 'yes'}")
    print(f"whether this deserves master hardening: {'maybe' if anti_lock or delayed else 'no'}")


if __name__ == "__main__":
    np.random.seed(SEED)
    main()
