#!/usr/bin/env python3
"""v2A: pure Sturmian mode for the golden zipper toy."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from golden_zipper_v2_lib import (
    GOLDEN,
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
    periodicity_metrics,
    robust_std,
    save_samples,
    strongest_weakest,
    summarize_sequence,
    write_csv,
    write_text,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v2_sturmian_pure_outputs"
STEPS = 4096
WINDOW_SIZES = [0.20, 0.34, 0.47]
WINDOW_PHASES = [0.0, 0.17, 0.31]


def main() -> None:
    ensure_dir(OUT)
    rows = []
    samples = []
    for slope in build_slopes():
        for window_size in WINDOW_SIZES:
            for phase in WINDOW_PHASES:
                seq = generate_sequence(slope.alpha, STEPS, window_size, phase, mode="single")
                bal, spread = balance_metrics(seq)
                comp_ratio, comp_dev = complexity_metrics(seq)
                periodicity, best_period = periodicity_metrics(seq)
                compress = compression_metric(seq)
                row = {
                    "name": slope.name,
                    "family": slope.family,
                    "alpha": slope.alpha,
                    "window_size": window_size,
                    "phase": phase,
                    "balance_score": bal,
                    "balance_spread": spread,
                    "complexity_ratio": comp_ratio,
                    "complexity_deviation": comp_dev,
                    "periodicity_match": periodicity,
                    "best_period": best_period,
                    "compression_score": compress,
                }
                row["tradeoff_score"] = (
                    1.8 * bal
                    + 1.0 * (1.0 - min(spread / 4.0, 1.0))
                    + 1.0 * (1.0 - comp_dev)
                    + 1.3 * (1.0 - min(periodicity * 3.0, 1.0))
                    + 0.3 * compress / 20.0
                )
                rows.append(row)
                if window_size == 0.34 and phase == 0.0:
                    samples.append(f"[{slope.name}] {summarize_sequence(seq)}")

    write_csv(rows, OUT / "metrics.csv")
    save_samples(samples, OUT / "sample_sequences.txt")
    bar_family(rows, "balance_score", "Pure mode balance by family", "balance score", OUT / "balance_plot.png")
    bar_family(rows, "complexity_deviation", "Pure mode complexity deviation", "complexity deviation", OUT / "complexity_plot.png")
    bar_family(rows, "periodicity_match", "Pure mode exact phase-lock score", "phase-lock score", OUT / "periodicity_plot.png")
    alpha_phase_diagram(rows, "tradeoff_score", "Pure mode phase diagram: tradeoff score", OUT / "phase_diagram.png")

    means = family_means(
        rows,
        [
            "balance_score",
            "balance_spread",
            "complexity_deviation",
            "periodicity_match",
            "compression_score",
            "tradeoff_score",
        ],
    )
    golden = means["golden"]
    rational = means["rational_approx"]
    controls = means["rational_control"]
    silver = means["silver"]
    bronze = means["bronze"]
    strongest, weakest = strongest_weakest(rows, "tradeoff_score")

    golden_tradeoff_win = golden["tradeoff_score"] > max(silver["tradeoff_score"], bronze["tradeoff_score"], means["random"]["tradeoff_score"])
    anti_lock_win = golden["periodicity_match"] < min(rational["periodicity_match"], controls["periodicity_match"])
    robust = robust_std(rows, "golden", "tradeoff_score") < 0.45

    report = [
        "# Golden Zipper v2A — Pure Sturmian Mode",
        "",
        "Toy telemetry only. Not physics evidence.",
        "",
        "This mode tests only irrational rotation plus finite single-window coding. No write/witness/release policy is applied.",
        "",
        "## Family Means",
        "",
        "| Family | Balance | Spread | Complexity dev. | Phase-lock | Compression | Tradeoff |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for family in sorted(means):
        m = means[family]
        report.append(
            f"| {family} | {m['balance_score']:.3f} | {m['balance_spread']:.3f} | {m['complexity_deviation']:.3f} | {m['periodicity_match']:.3f} | {m['compression_score']:.3f} | {m['tradeoff_score']:.3f} |"
        )
    report.extend(
        [
            "",
            "## Questions",
            "",
            f"1. Does golden/Sturmian sampling produce stronger balance than controls? **{'No / mixed' if golden['balance_score'] <= max(rational['balance_score'], controls['balance_score']) else 'Yes'}**.",
            f"2. Does golden sampling avoid phase-lock better than rational controls? **{'Yes' if anti_lock_win else 'No / mixed'}**.",
            "3. Delayed-meaning retention is not tested in pure mode.",
            f"4. Does silver or bronze beat golden on any metric? **silver tradeoff {'higher' if silver['tradeoff_score'] > golden['tradeoff_score'] else 'lower'}; bronze tradeoff {'higher' if bronze['tradeoff_score'] > golden['tradeoff_score'] else 'lower'}**.",
            f"5. Are results robust to window size and phase? **{'reasonably' if robust else 'not strongly'}**.",
            f"6. Does this support only symbolic intuition, or a genuine toy-model advantage? **{'golden may occupy a strong anti-locking tradeoff region' if golden_tradeoff_win and anti_lock_win else 'mixed telemetry only'}**.",
            "",
            "Correct success language: Golden slope did not win every metric, but may occupy the best anti-locking tradeoff region.",
            "",
            f"Strongest run: `{strongest['name']}` window={strongest['window_size']:.2f} phase={strongest['phase']:.2f}",
            f"Weakest run: `{weakest['name']}` window={weakest['window_size']:.2f} phase={weakest['phase']:.2f}",
            "",
            "Do-not-claim: does not prove GHP, phi as reality-code, VPH, consciousness, or write-law closure.",
        ]
    )
    write_text(OUT / "report.md", "\n".join(report))

    print(f"files created: {OUT}")
    print(f"strongest result: {strongest['name']}")
    print(f"weakest result: {weakest['name']}")
    print(f"whether golden slope beat controls: {'mixed' if not anti_lock_win or golden['balance_score'] <= max(rational['balance_score'], controls['balance_score']) else 'yes'}")
    print(f"whether this deserves master hardening: {'maybe' if anti_lock_win else 'no'}")


if __name__ == "__main__":
    np.random.seed(SEED)
    main()
