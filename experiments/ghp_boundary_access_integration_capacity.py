#!/usr/bin/env python3
"""Integration-capacity test for coherent external flow.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_external_flow_signal as external_flow
import ghp_boundary_access_flow_continuity_control as flow_control
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_low_dimensional_failure_map as failure_map
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_integration_capacity_outputs"

PACKS = [
    "order_plus_flow",
    "capacity_only",
    "order_flow_capacity",
    "order_flow_capacity_external",
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


def integration_capacity_features(row: dict[str, object]) -> np.ndarray:
    damaged = np.asarray(row["damaged"], dtype=float)
    helper = np.asarray(row["helper"], dtype=float)
    wake = np.asarray(row["wake"], dtype=float)
    deep = np.asarray(row["deep_trace"], dtype=float)
    prev_helper = np.asarray(row["prev_helper"], dtype=float)
    prev_wake = np.asarray(row["prev_wake"], dtype=float)
    prev_deep = np.asarray(row["prev_deep_trace"], dtype=float)

    helper_delta = flow_control.delta(helper, prev_helper)
    wake_delta = flow_control.delta(wake, prev_wake)
    deep_delta = flow_control.delta(deep, prev_deep)
    base = local_switcher.base

    damaged_helper = base.cosine(damaged, helper)
    damaged_wake = base.cosine(damaged, wake)
    damaged_deep = base.cosine(damaged, deep)
    helper_wake = base.cosine(helper, wake)
    helper_deep = base.cosine(helper, deep)
    wake_deep = base.cosine(wake, deep)

    novelty_cost = 1.0 - damaged_deep
    boundary_cost = 1.0 - helper_wake
    deep_update_cost = 1.0 - helper_deep
    self_stability = wake_deep
    external_compatibility = damaged_helper * helper_wake
    integration_capacity = external_compatibility * max(0.0, self_stability)
    rupture_pressure = novelty_cost * boundary_cost

    helper_wake_flow_cost = np.linalg.norm(helper_delta - wake_delta)
    helper_deep_flow_cost = np.linalg.norm(helper_delta - deep_delta)
    update_speed_gap = abs(float(np.linalg.norm(helper_delta)) - float(np.linalg.norm(wake_delta)))

    return np.array(
        [
            novelty_cost,
            boundary_cost,
            deep_update_cost,
            self_stability,
            external_compatibility,
            integration_capacity,
            rupture_pressure,
            helper_wake_flow_cost,
            helper_deep_flow_cost,
            update_speed_gap,
        ],
        dtype=float,
    )


def features_for_pack(row: dict[str, object], pack: str) -> np.ndarray:
    order = flow_control.order_control.order_relation_features(row)
    flow = flow_control.flow_features(row)
    capacity = integration_capacity_features(row)
    external = external_flow.external_flow_features(row)
    if pack == "order_plus_flow":
        return np.concatenate([order, flow])
    if pack == "capacity_only":
        return capacity
    if pack == "order_flow_capacity":
        return np.concatenate([order, flow, capacity])
    if pack == "order_flow_capacity_external":
        return np.concatenate([order, flow, capacity, external])
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
    write_csv(summary_rows, OUT / "integration_capacity_summary.csv")
    write_csv(scenario_rows, OUT / "integration_capacity_scenarios.csv")

    best = summary_rows[0]
    target = [row for row in scenario_rows if row["pack"] == best["pack"]]
    lines = [
        "# Boundary Access Integration Capacity",
        "",
        "- question: does update-cost / boundary-compatibility help when coherent external flow is hard to integrate?",
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
