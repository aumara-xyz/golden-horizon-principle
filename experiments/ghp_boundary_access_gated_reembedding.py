#!/usr/bin/env python3
"""Gated re-embedding test for capacity alarms.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_flow_continuity_control as flow_control
import ghp_boundary_access_integration_capacity as capacity_test
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_low_dimensional_failure_map as failure_map
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_gated_reembedding_outputs"

TARGET_SCENARIOS = [
    {"name": "current", "helper_kind": "current", "noise_level": 0.0},
    {"name": "cross_family_0.30", "helper_kind": "cross_family", "noise_level": 0.30},
    {"name": "cross_family_0.45", "helper_kind": "cross_family", "noise_level": 0.45},
    {"name": "cross_family_0.60", "helper_kind": "cross_family", "noise_level": 0.60},
    {"name": "permute_mix_0.60", "helper_kind": "permute_mix", "noise_level": 0.60},
    {"name": "gaussian_mix_0.60", "helper_kind": "gaussian_mix", "noise_level": 0.60},
    {"name": "delayed_uniform_0.60", "helper_kind": "delayed_uniform", "noise_level": 0.60},
    {"name": "uniform_mix_0.60", "helper_kind": "uniform_mix", "noise_level": 0.60},
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


def model_score(features: np.ndarray, model: tuple[np.ndarray, np.ndarray, np.ndarray]) -> float:
    mean, std, weights = model
    x_norm = (features - mean) / std
    x_aug = np.concatenate([x_norm, np.array([1.0])])
    return float(x_aug @ weights)


def family_from_score(score: float) -> str:
    return "fibonacci" if score >= 0.5 else "generic_ternary"


def gate_features(
    row: dict[str, object],
    order_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    capacity_model: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> np.ndarray:
    order_features = capacity_test.features_for_pack(row, "order_plus_flow")
    capacity_features = capacity_test.features_for_pack(row, "capacity_only")
    order_score = model_score(order_features, order_model)
    capacity_score = model_score(capacity_features, capacity_model)
    return np.concatenate(
        [
            capacity_features,
            np.array(
                [
                    order_score,
                    capacity_score,
                    abs(order_score - 0.5),
                    abs(capacity_score - 0.5),
                    capacity_score - order_score,
                    float(family_from_score(order_score) != family_from_score(capacity_score)),
                ],
                dtype=float,
            ),
        ]
    )


def fit_pack(rows: list[dict[str, object]], pack: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    selected = [{"features": capacity_test.features_for_pack(row, pack), "label": row["label"]} for row in rows]
    return local_switcher.fit_linear_probe(selected)


def fit_gate(
    rows: list[dict[str, object]],
    order_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    capacity_model: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    gate_rows = []
    for row in rows:
        order_choice = family_from_score(model_score(capacity_test.features_for_pack(row, "order_plus_flow"), order_model))
        capacity_choice = family_from_score(model_score(capacity_test.features_for_pack(row, "capacity_only"), capacity_model))
        target = str(row["target_family"])
        label = int(capacity_choice == target and order_choice != target)
        gate_rows.append({"features": gate_features(row, order_model, capacity_model), "label": label})
    return local_switcher.fit_linear_probe(gate_rows)


def predict_gate(row: dict[str, object], gate_model: tuple[np.ndarray, np.ndarray, np.ndarray], order_model, capacity_model) -> int:
    return local_switcher.predict_linear_probe(gate_features(row, order_model, capacity_model), *gate_model)


def choices_for_row(row: dict[str, object], order_model, capacity_model, gate_model) -> dict[str, str]:
    order_choice = family_from_score(model_score(capacity_test.features_for_pack(row, "order_plus_flow"), order_model))
    capacity_choice = family_from_score(model_score(capacity_test.features_for_pack(row, "capacity_only"), capacity_model))
    gate_open = bool(predict_gate(row, gate_model, order_model, capacity_model))
    disagreement_gate_open = gate_open and order_choice != capacity_choice
    target = str(row["target_family"])
    oracle_choice = capacity_choice if capacity_choice == target and order_choice != target else order_choice
    return {
        "order_plus_flow": order_choice,
        "capacity_only": capacity_choice,
        "trained_capacity_gate": capacity_choice if gate_open else order_choice,
        "disagreement_capacity_gate": capacity_choice if disagreement_gate_open else order_choice,
        "oracle_order_or_capacity": oracle_choice,
    }


def evaluate(train_rows: list[dict[str, object]], test_rows: list[dict[str, object]]) -> tuple[list[dict], list[dict], list[dict]]:
    order_model = fit_pack(train_rows, "order_plus_flow")
    capacity_model = fit_pack(train_rows, "capacity_only")
    gate_model = fit_gate(train_rows, order_model, capacity_model)

    all_choices = [choices_for_row(row, order_model, capacity_model, gate_model) for row in test_rows]
    policies = list(all_choices[0])
    summary_rows: list[dict[str, float | str]] = []
    scenario_rows: list[dict[str, float | str]] = []
    gate_rows: list[dict[str, float | str]] = []

    for policy in policies:
        accuracy = float(np.mean([choices[policy] == row["target_family"] for choices, row in zip(all_choices, test_rows)]))
        summary_rows.append({"policy": policy, "overall_accuracy": accuracy})
        for scenario in sorted({str(row["scenario"]) for row in test_rows}):
            pairs = [(choices, row) for choices, row in zip(all_choices, test_rows) if str(row["scenario"]) == scenario]
            scenario_accuracy = float(np.mean([choices[policy] == row["target_family"] for choices, row in pairs]))
            scenario_rows.append({"policy": policy, "scenario": scenario, "accuracy": scenario_accuracy})

    for scenario in sorted({str(row["scenario"]) for row in test_rows}):
        subset = [row for row in test_rows if str(row["scenario"]) == scenario]
        opened = [predict_gate(row, gate_model, order_model, capacity_model) for row in subset]
        gate_rows.append({"scenario": scenario, "gate_open_rate": float(np.mean(opened))})

    return (
        sorted(summary_rows, key=lambda row: float(row["overall_accuracy"]), reverse=True),
        scenario_rows,
        gate_rows,
    )


def main() -> None:
    ensure_dir(OUT)
    old_trials = generalization.TRIALS_PER_SCENARIO
    generalization.TRIALS_PER_SCENARIO = 3
    try:
        words = generalization.build_words()
        vocab = generalization.base.collect_vocabulary(words, generalization.base.KMER)
        vocab_index = {token: idx for idx, token in enumerate(vocab)}
        scenarios = TARGET_SCENARIOS

        train_rows: list[dict[str, object]] = []
        test_rows: list[dict[str, object]] = []
        for seed in local_switcher.TRAIN_SEEDS:
            train_rows.extend(flow_control.collect_rows_for_seed(seed, scenarios, words, vocab_index))
        for seed in local_switcher.TEST_SEEDS:
            test_rows.extend(flow_control.collect_rows_for_seed(seed, scenarios, words, vocab_index))
    finally:
        generalization.TRIALS_PER_SCENARIO = old_trials

    summary_rows, scenario_rows, gate_rows = evaluate(train_rows, test_rows)
    write_csv(summary_rows, OUT / "gated_reembedding_summary.csv")
    write_csv(scenario_rows, OUT / "gated_reembedding_scenarios.csv")
    write_csv(gate_rows, OUT / "gated_reembedding_gate_rates.csv")

    best = summary_rows[0]
    target = [row for row in scenario_rows if row["policy"] == best["policy"]]
    lines = [
        "# Boundary Access Gated Re-embedding",
        "",
        "- question: can capacity act as a gated alarm instead of a general chooser?",
        "- training: targeted hard-lane grid on train seeds; held-out test seeds",
        f"- best policy: `{best['policy']}`",
        f"- overall held-out accuracy: `{float(best['overall_accuracy']):.3f}`",
        "",
        "Ranking:",
    ]
    for row in summary_rows:
        lines.append(f"- {row['policy']}: `{float(row['overall_accuracy']):.3f}`")
    lines.extend(["", "Best-policy scenario map:"])
    for row in sorted(target, key=lambda item: str(item["scenario"])):
        lines.append(f"- {row['scenario']}: `{float(row['accuracy']):.3f}`")
    lines.extend(["", "Gate-open rates:"])
    for row in gate_rows:
        lines.append(f"- {row['scenario']}: `{float(row['gate_open_rate']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
