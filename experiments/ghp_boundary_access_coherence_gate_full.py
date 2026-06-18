#!/usr/bin/env python3
"""Full-size coherence-gate rerun for Boundary Access gated re-embedding.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

from pathlib import Path

import ghp_boundary_access_gate_hardening as hardening
import ghp_boundary_access_gated_reembedding as gated
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_flow_continuity_control as flow_control
import ghp_boundary_access_selector_generalization as generalization


OUT = Path(__file__).resolve().parent / "ghp_boundary_access_coherence_gate_full_outputs"


def main() -> None:
    hardening.ensure_dir(OUT)
    old_trials = generalization.TRIALS_PER_SCENARIO
    generalization.TRIALS_PER_SCENARIO = 3
    try:
        words = generalization.build_words()
        vocab = generalization.base.collect_vocabulary(words, generalization.base.KMER)
        vocab_index = {token: idx for idx, token in enumerate(vocab)}

        train_rows: list[dict[str, object]] = []
        test_rows: list[dict[str, object]] = []
        for seed in local_switcher.TRAIN_SEEDS:
            train_rows.extend(flow_control.collect_rows_for_seed(seed, gated.TARGET_SCENARIOS, words, vocab_index))
        for seed in local_switcher.TEST_SEEDS:
            test_rows.extend(flow_control.collect_rows_for_seed(seed, gated.TARGET_SCENARIOS, words, vocab_index))
    finally:
        generalization.TRIALS_PER_SCENARIO = old_trials

    summary_rows, scenario_rows, gate_rows, threshold = hardening.evaluate(train_rows, test_rows)
    hardening.write_csv(summary_rows, OUT / "coherence_gate_full_summary.csv")
    hardening.write_csv(scenario_rows, OUT / "coherence_gate_full_scenarios.csv")
    hardening.write_csv(gate_rows, OUT / "coherence_gate_full_open_rates.csv")
    hardening.write_csv([threshold], OUT / "threshold_gate_selected.csv")

    best = summary_rows[0]
    best_scenarios = [row for row in scenario_rows if row["policy"] == best["policy"]]
    lines = [
        "# Boundary Access Coherence Gate Full Rerun",
        "",
        "Status: full-size targeted hard-lane toy telemetry only.",
        "",
        "- question: does the coherent-foreign gate survive the full target scenario grid?",
        "- settings: target hard-lane scenarios, all train seeds, all held-out test seeds, three trials per scenario, full time horizon",
        f"- best policy: `{best['policy']}`",
        f"- overall held-out accuracy: `{float(best['overall_accuracy']):.3f}`",
        "",
        "Ranking:",
    ]
    for row in summary_rows:
        lines.append(f"- {row['policy']}: `{float(row['overall_accuracy']):.3f}`")
    lines.extend(["", "Selected threshold gate:"])
    for key, value in threshold.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "Best-policy scenario map:"])
    for row in sorted(best_scenarios, key=lambda item: str(item["scenario"])):
        lines.append(f"- {row['scenario']}: `{float(row['accuracy']):.3f}`")
    lines.extend(["", "Gate open rates:"])
    for row in gate_rows:
        lines.append(f"- {row['gate']} / {row['scenario']}: `{float(row['open_rate']):.3f}`")
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
