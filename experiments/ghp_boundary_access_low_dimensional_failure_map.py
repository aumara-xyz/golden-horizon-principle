#!/usr/bin/env python3
"""Failure map for compact Boundary Access chooser packs.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_low_dimensional_chooser as low_dim
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_low_dimensional_failure_map_outputs"

PACKS = [
    "six_compass_with_pull",
    "five_groove_compass",
    "three_fit_inertia_pull",
    "one_scalar_spine",
    "all_axes",
]

LEVELS = [0.0, 0.15, 0.30, 0.45, 0.60]
HELPER_KINDS = [
    "current",
    "uniform_mix",
    "gaussian_mix",
    "delayed_uniform",
    "permute_mix",
    "cross_family",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict[str, float | str]], path: Path) -> None:
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


def build_test_scenarios() -> list[dict[str, float | str]]:
    scenarios: list[dict[str, float | str]] = [{"name": "current", "helper_kind": "current", "noise_level": 0.0}]
    for kind in HELPER_KINDS:
        if kind == "current":
            continue
        for level in LEVELS:
            scenarios.append(
                {
                    "name": f"{kind}_{level:.2f}",
                    "helper_kind": kind,
                    "noise_level": level,
                }
            )
    return scenarios


def evaluate_pack(
    test_rows: list[dict[str, object]],
    pack: str,
    model: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for scenario in sorted({str(row["scenario"]) for row in test_rows}):
        subset = [row for row in test_rows if str(row["scenario"]) == scenario]
        chosen = [low_dim.choose_family(row, pack, model) for row in subset]
        accuracy = float(np.mean([choice == row["target_family"] for choice, row in zip(chosen, subset)]))
        helper_kind, level_text = scenario.rsplit("_", 1) if scenario != "current" else ("current", "0.00")
        rows.append(
            {
                "pack": pack,
                "scenario": scenario,
                "helper_kind": helper_kind,
                "noise_level": float(level_text),
                "accuracy": accuracy,
            }
        )
    return rows


def summarize_failures(rows: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    summary: list[dict[str, float | str]] = []
    for pack in PACKS:
        subset = [row for row in rows if row["pack"] == pack]
        worst = min(subset, key=lambda row: float(row["accuracy"]))
        best = max(subset, key=lambda row: float(row["accuracy"]))
        below_075 = sum(1 for row in subset if float(row["accuracy"]) < 0.75)
        below_070 = sum(1 for row in subset if float(row["accuracy"]) < 0.70)
        summary.append(
            {
                "pack": pack,
                "mean_accuracy": float(np.mean([float(row["accuracy"]) for row in subset])),
                "worst_scenario": str(worst["scenario"]),
                "worst_accuracy": float(worst["accuracy"]),
                "best_scenario": str(best["scenario"]),
                "best_accuracy": float(best["accuracy"]),
                "scenarios_below_075": below_075,
                "scenarios_below_070": below_070,
            }
        )
    return sorted(summary, key=lambda row: (float(row["mean_accuracy"]), -float(row["scenarios_below_075"])), reverse=True)


def main() -> None:
    ensure_dir(OUT)
    old_trials = generalization.TRIALS_PER_SCENARIO
    generalization.TRIALS_PER_SCENARIO = 5
    try:
        words = generalization.build_words()
        vocab = generalization.base.collect_vocabulary(words, generalization.base.KMER)
        vocab_index = {token: idx for idx, token in enumerate(vocab)}

        train_rows: list[dict[str, object]] = []
        test_rows: list[dict[str, object]] = []
        for seed in local_switcher.TRAIN_SEEDS:
            train_rows.extend(generalization.collect_rows_for_seed(seed, generalization.TRAIN_SCENARIOS, words, vocab_index))
        for seed in local_switcher.TEST_SEEDS:
            test_rows.extend(generalization.collect_rows_for_seed(seed, build_test_scenarios(), words, vocab_index))
    finally:
        generalization.TRIALS_PER_SCENARIO = old_trials

    models = {pack: low_dim.fit_pack(train_rows, pack) for pack in PACKS}
    scenario_rows: list[dict[str, float | str]] = []
    for pack, model in models.items():
        scenario_rows.extend(evaluate_pack(test_rows, pack, model))

    summary_rows = summarize_failures(scenario_rows)
    write_csv(summary_rows, OUT / "failure_summary.csv")
    write_csv(scenario_rows, OUT / "failure_map.csv")

    best = summary_rows[0]
    lines = [
        "# Boundary Access Low-Dimensional Failure Map",
        "",
        "- question: where does the compact chooser start to slip?",
        f"- best mean pack: `{best['pack']}` `{float(best['mean_accuracy']):.3f}`",
        f"- worst scenario for best pack: `{best['worst_scenario']}` `{float(best['worst_accuracy']):.3f}`",
        "",
        "Pack summary:",
    ]
    for row in summary_rows:
        lines.append(
            "- "
            f"{row['pack']}: mean `{float(row['mean_accuracy']):.3f}`, "
            f"worst `{row['worst_scenario']}` `{float(row['worst_accuracy']):.3f}`, "
            f"below `.75` `{int(row['scenarios_below_075'])}`"
        )
    lines.extend(["", "Best-pack map:"])
    for row in [item for item in scenario_rows if item["pack"] == best["pack"]]:
        lines.append(f"- {row['scenario']}: `{float(row['accuracy']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
