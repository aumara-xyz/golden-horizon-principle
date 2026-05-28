#!/usr/bin/env python3
"""v2B: moving/spiral/two-window observer mode for the golden zipper toy."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from golden_zipper_v2_lib import (
    SEED,
    alpha_phase_diagram,
    balance_metrics,
    build_slopes,
    complexity_metrics,
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
OUT = ROOT / "golden_zipper_v2_spiral_window_outputs"
STEPS = 4096
WINDOW_SIZES = [0.20, 0.34, 0.47]
WINDOW_PHASES = [0.0, 0.17]
WINDOW_MODES = [("moving", 0.03), ("moving", 0.07), ("moving", 0.11), ("double", 0.0)]


def main() -> None:
    ensure_dir(OUT)
    rows = []
    samples = []
    for slope in build_slopes():
        for window_size in WINDOW_SIZES:
            for phase in WINDOW_PHASES:
                for mode, drift in WINDOW_MODES:
                    seq = generate_sequence(slope.alpha, STEPS, window_size, phase, mode=mode, drift_scale=drift if mode == "moving" else 0.0)
                    bal, spread = balance_metrics(seq)
                    comp_ratio, comp_dev = complexity_metrics(seq)
                    periodicity, best_period = periodicity_metrics(seq)
                    row = {
                        "name": slope.name,
                        "family": slope.family,
                        "alpha": slope.alpha,
                        "window_size": window_size,
                        "phase": phase,
                        "window_mode": mode,
                        "drift_scale": drift,
                        "balance_score": bal,
                        "balance_spread": spread,
                        "complexity_ratio": comp_ratio,
                        "complexity_deviation": comp_dev,
                        "periodicity_match": periodicity,
                        "best_period": best_period,
                    }
                    row["tradeoff_score"] = (
                        1.5 * bal
                        + 0.8 * (1.0 - min(spread / 4.0, 1.0))
                        + 0.9 * (1.0 - comp_dev)
                        + 1.5 * (1.0 - min(periodicity * 3.0, 1.0))
                    )
                    rows.append(row)
                    if window_size == 0.34 and phase == 0.0 and drift in (0.07, 0.0):
                        label = f"{mode}_d{drift:.2f}" if mode == "moving" else mode
                        samples.append(f"[{slope.name} | {label}] {summarize_sequence(seq)}")

    write_csv(rows, OUT / "metrics.csv")
    save_samples(samples, OUT / "sample_sequences.txt")
    alpha_phase_diagram(rows, "tradeoff_score", "Observer-window phase diagram: tradeoff score", OUT / "phase_diagram.png", cmap="plasma")
    alpha_phase_diagram(rows, "periodicity_match", "Observer-window phase diagram: phase-lock", OUT / "phase_lock_phase_diagram.png", cmap="magma")

    means = family_means(
        rows,
        ["balance_score", "balance_spread", "complexity_deviation", "periodicity_match", "tradeoff_score"],
    )
    strongest, weakest = strongest_weakest(rows, "tradeoff_score")
    golden = means["golden"]
    rational = means["rational_approx"]
    controls = means["rational_control"]
    silver = means["silver"]
    bronze = means["bronze"]
    robust = robust_std(rows, "golden", "tradeoff_score") < 0.50
    anti_lock_win = golden["periodicity_match"] < min(rational["periodicity_match"], controls["periodicity_match"])

    report = [
        "# Golden Zipper v2B — Spiral / Observer-Window Mode",
        "",
        "Toy telemetry only. Not physics evidence.",
        "",
        "This mode separates observer-window effects from the pure Sturmian test. It compares moving-phase windows and a two-window bidirectional observer variant.",
        "",
        "## Family Means",
        "",
        "| Family | Balance | Spread | Complexity dev. | Phase-lock | Tradeoff |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for family in sorted(means):
        m = means[family]
        report.append(
            f"| {family} | {m['balance_score']:.3f} | {m['balance_spread']:.3f} | {m['complexity_deviation']:.3f} | {m['periodicity_match']:.3f} | {m['tradeoff_score']:.3f} |"
        )
    report.extend(
        [
            "",
            "Key question: does golden sit in a broader admissible anti-locking band rather than as a single magical winner-point?",
            "",
            f"Answer from this sweep: **{'golden sits in a strong anti-locking region' if anti_lock_win else 'mixed / no unique region yet'}**.",
            f"Robustness to window shape and phase: **{'reasonable' if robust else 'limited'}**.",
            f"Silver vs golden tradeoff: **{'silver lower' if silver['tradeoff_score'] < golden['tradeoff_score'] else 'silver higher'}**.",
            f"Bronze vs golden tradeoff: **{'bronze lower' if bronze['tradeoff_score'] < golden['tradeoff_score'] else 'bronze higher'}**.",
            "",
            "Correct success language: Golden slope did not win every metric, but may occupy the best anti-locking tradeoff region.",
            "",
            f"Strongest run: `{strongest['name']}` / {strongest['window_mode']} / drift={strongest['drift_scale']:.2f} / window={strongest['window_size']:.2f} / phase={strongest['phase']:.2f}",
            f"Weakest run: `{weakest['name']}` / {weakest['window_mode']} / drift={weakest['drift_scale']:.2f} / window={weakest['window_size']:.2f} / phase={weakest['phase']:.2f}",
            "",
            "Do-not-claim: this does not prove GHP, phi as reality-code, or observer-boundary physics.",
        ]
    )
    write_text(OUT / "report.md", "\n".join(report))

    print(f"files created: {OUT}")
    print(f"strongest result: {strongest['name']}")
    print(f"weakest result: {weakest['name']}")
    print(f"whether golden slope beat controls: {'mixed' if not anti_lock_win else 'yes'}")
    print(f"whether this deserves master hardening: {'maybe' if anti_lock_win else 'no'}")


if __name__ == "__main__":
    np.random.seed(SEED)
    main()
