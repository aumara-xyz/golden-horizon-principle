#!/usr/bin/env python3
"""External-flow signal test for the remaining cross-family weak lane.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_flow_continuity_control as flow_control
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_low_dimensional_failure_map as failure_map
import ghp_boundary_access_rank_matched_control as rank_matched
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_external_flow_signal_outputs"

PACKS = [
    "order_plus_flow",
    "external_flow_only",
    "order_flow_external",
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


def external_flow_features(row: dict[str, object]) -> np.ndarray:
    helper_delta = flow_control.delta(row["helper"], row["prev_helper"])
    wake_delta = flow_control.delta(row["wake"], row["prev_wake"])
    deep_delta = flow_control.delta(row["deep_trace"], row["prev_deep_trace"])
    damaged_delta = flow_control.delta(row["damaged"], row["prev_readable_a"])
    base = local_switcher.base

    helper_wake_flow = base.cosine(helper_delta, wake_delta)
    helper_deep_flow = base.cosine(helper_delta, deep_delta)
    damaged_helper_flow = base.cosine(damaged_delta, helper_delta)
    damaged_deep_flow = base.cosine(damaged_delta, deep_delta)
    external_pull = damaged_helper_flow - damaged_deep_flow
    helper_inertia_break = helper_wake_flow - helper_deep_flow
    helper_speed = float(np.linalg.norm(helper_delta))
    deep_speed = float(np.linalg.norm(deep_delta))
    speed_ratio = helper_speed / (deep_speed + 1e-9)

    return np.array(
        [
            helper_wake_flow,
            helper_deep_flow,
            damaged_helper_flow,
            damaged_deep_flow,
            external_pull,
            helper_inertia_break,
            helper_speed,
            speed_ratio,
        ],
        dtype=float,
    )


def features_for_pack(row: dict[str, object], pack: str) -> np.ndarray:
    order = flow_control.order_control.order_relation_features(row)
    flow = flow_control.flow_features(row)
    external = external_flow_features(row)
    if pack == "order_plus_flow":
        return np.concatenate([order, flow])
    if pack == "external_flow_only":
        return external
    if pack == "order_flow_external":
        return np.concatenate([order, flow, external])
    raise ValueError(pack)


def fit_pack(rows: list[dict[str, object]], pack: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    selected = [{"features": features_for_pack(row, pack), "label": row["label"]} for row in rows]
    return local_switcher.fit_linear_probe(selected)


def choose_family(row: dict[str, object], pack: str, model: tuple[np.ndarray, np.ndarray, np.ndarray]) -> str:
    mean, std, weights = model
    prediction = local_switcher.predict_linear_probe(features_for_pack(row, pack), mean, std, weights)
    return "fibonacci" if prediction == 1 else "generic_ternary"


def evaluate_pack(
    train_rows: list[dict[str, object]],
    test_rows: list[dict[str, object]],
    pack: str,
) -> tuple[dict[str, float | str], list[dict[str, float | str]]]:
    model = fit_pack(train_rows, pack)
    chosen = [choose_family(row, pack, model) for row in test_rows]
    overall = float(np.mean([choice == row["target_family"] for choice, row in zip(chosen, test_rows)]))
    summary = {"pack": pack, "dimensions": int(len(features_for_pack(test_rows[0], pack))), "overall_accuracy": overall}

    scenario_rows: list[dict[str, float | str]] = []
    for scenario in sorted({str(row["scenario"]) for row in test_rows}):
        subset = [row for row in test_rows if str(row["scenario"]) == scenario]
        subset_chosen = [choose_family(row, pack, model) for row in subset]
        accuracy = float(np.mean([choice == row["target_family"] for choice, row in zip(subset_chosen, subset)]))
        scenario_rows.append({"pack": pack, "scenario": scenario, "accuracy": accuracy})
    return summary, scenario_rows


def main() -> None:
    ensure_dir(OUT)
    old_trials = generalization.TRIALS_PER_SCENARIO
    generalization.TRIALS_PER_SCENARIO = 4
    try:
        words = generalization.build_words()
        vocab = generalization.base.collect_vocabulary(words, generalization.base.KMER)
        vocab_index = {token: idx for idx, token in enumerate(vocab)}

        train_rows: list[dict[str, object]] = []
        test_rows: list[dict[str, object]] = []
        for seed in local_switcher.TRAIN_SEEDS:
            train_rows.extend(flow_control.collect_rows_for_seed(seed, generalization.TRAIN_SCENARIOS, words, vocab_index))
        for seed in local_switcher.TEST_SEEDS:
            test_rows.extend(flow_control.collect_rows_for_seed(seed, failure_map.build_test_scenarios(), words, vocab_index))
    finally:
        generalization.TRIALS_PER_SCENARIO = old_trials

    summary_rows: list[dict[str, float | str]] = []
    scenario_rows: list[dict[str, float | str]] = []
    for pack in PACKS:
        summary, scenarios = evaluate_pack(train_rows, test_rows, pack)
        summary_rows.append(summary)
        scenario_rows.extend(scenarios)

    summary_rows = sorted(summary_rows, key=lambda row: float(row["overall_accuracy"]), reverse=True)
    write_csv(summary_rows, OUT / "external_flow_summary.csv")
    write_csv(scenario_rows, OUT / "external_flow_scenarios.csv")

    best = summary_rows[0]
    target = [row for row in scenario_rows if row["pack"] == best["pack"]]
    lines = [
        "# Boundary Access External Flow Signal",
        "",
        "- question: does an external-flow signal help distinguish new coherent flow from old scrambled flow?",
        f"- best pack: `{best['pack']}`",
        f"- dimensions: `{int(best['dimensions'])}`",
        f"- overall held-out accuracy: `{float(best['overall_accuracy']):.3f}`",
        "",
        "Ranking:",
    ]
    for row in summary_rows:
        lines.append(f"- {row['pack']} ({int(row['dimensions'])}D): `{float(row['overall_accuracy']):.3f}`")
    lines.extend(["", "Best-pack scenario map:"])
    for row in sorted(target, key=lambda item: str(item["scenario"])):
        lines.append(f"- {row['scenario']}: `{float(row['accuracy']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
