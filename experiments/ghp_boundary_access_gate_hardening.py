#!/usr/bin/env python3
"""Hardening pass for the gated re-embedding lane.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_external_flow_signal as external_flow
import ghp_boundary_access_gated_reembedding as gated
import ghp_boundary_access_integration_capacity as capacity_test
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_flow_continuity_control as flow_control
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_gate_hardening_outputs"
SCOUT_SCENARIOS = [
    {"name": "current", "helper_kind": "current", "noise_level": 0.0},
    {"name": "cross_family_0.45", "helper_kind": "cross_family", "noise_level": 0.45},
    {"name": "cross_family_0.60", "helper_kind": "cross_family", "noise_level": 0.60},
    {"name": "permute_mix_0.60", "helper_kind": "permute_mix", "noise_level": 0.60},
    {"name": "gaussian_mix_0.60", "helper_kind": "gaussian_mix", "noise_level": 0.60},
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


def fit_pack(rows: list[dict[str, object]], pack: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    selected = [{"features": capacity_test.features_for_pack(row, pack), "label": row["label"]} for row in rows]
    return local_switcher.fit_linear_probe(selected)


def coherence_features(
    row: dict[str, object],
    order_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    capacity_model: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> np.ndarray:
    order_features = capacity_test.features_for_pack(row, "order_plus_flow")
    capacity_features = capacity_test.features_for_pack(row, "capacity_only")
    external_features = external_flow.external_flow_features(row)
    order_score = model_score(order_features, order_model)
    capacity_score = model_score(capacity_features, capacity_model)
    return np.concatenate(
        [
            capacity_features,
            external_features,
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


def fit_linear_gate(
    rows: list[dict[str, object]],
    order_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    capacity_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    label_kind: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    gate_rows = []
    for row in rows:
        order_choice = family_from_score(model_score(capacity_test.features_for_pack(row, "order_plus_flow"), order_model))
        capacity_choice = family_from_score(model_score(capacity_test.features_for_pack(row, "capacity_only"), capacity_model))
        target = str(row["target_family"])
        scenario = str(row["scenario"])
        if label_kind == "opportunity":
            label = int(capacity_choice == target and order_choice != target)
        elif label_kind == "coherent_foreign":
            label = int(scenario.startswith("cross_family"))
        else:
            raise ValueError(label_kind)
        gate_rows.append({"features": coherence_features(row, order_model, capacity_model), "label": label})
    return local_switcher.fit_linear_probe(gate_rows)


def predict_linear_gate(row, model, order_model, capacity_model) -> int:
    return local_switcher.predict_linear_probe(coherence_features(row, order_model, capacity_model), *model)


def fit_threshold_gate(rows, order_model, capacity_model) -> dict[str, float | bool]:
    score_rows = []
    for row in rows:
        order_score = model_score(capacity_test.features_for_pack(row, "order_plus_flow"), order_model)
        capacity_score = model_score(capacity_test.features_for_pack(row, "capacity_only"), capacity_model)
        score_rows.append(
            {
                "order_score": order_score,
                "capacity_score": capacity_score,
                "target_family": row["target_family"],
            }
        )

    candidates = []
    for require_disagreement in [True, False]:
        for min_capacity_margin in np.linspace(0.0, 0.50, 11):
            for max_order_margin in np.linspace(0.05, 0.60, 12):
                correct = []
                open_rate = []
                for row in score_rows:
                    order_score = float(row["order_score"])
                    capacity_score = float(row["capacity_score"])
                    order_choice = family_from_score(order_score)
                    capacity_choice = family_from_score(capacity_score)
                    disagreement = order_choice != capacity_choice
                    gate_open = (
                        abs(capacity_score - 0.5) >= min_capacity_margin
                        and abs(order_score - 0.5) <= max_order_margin
                        and (disagreement or not require_disagreement)
                    )
                    choice = capacity_choice if gate_open else order_choice
                    correct.append(choice == row["target_family"])
                    open_rate.append(gate_open)
                candidates.append(
                    {
                        "require_disagreement": require_disagreement,
                        "min_capacity_margin": float(min_capacity_margin),
                        "max_order_margin": float(max_order_margin),
                        "train_accuracy": float(np.mean(correct)),
                        "train_open_rate": float(np.mean(open_rate)),
                    }
                )
    # Prefer accuracy, then lower open rate as the less-invasive gate.
    return sorted(candidates, key=lambda item: (item["train_accuracy"], -item["train_open_rate"]), reverse=True)[0]


def choose_with_threshold(row, order_model, capacity_model, threshold: dict[str, float | bool]) -> tuple[str, bool]:
    order_score = model_score(capacity_test.features_for_pack(row, "order_plus_flow"), order_model)
    capacity_score = model_score(capacity_test.features_for_pack(row, "capacity_only"), capacity_model)
    order_choice = family_from_score(order_score)
    capacity_choice = family_from_score(capacity_score)
    disagreement = order_choice != capacity_choice
    gate_open = (
        abs(capacity_score - 0.5) >= float(threshold["min_capacity_margin"])
        and abs(order_score - 0.5) <= float(threshold["max_order_margin"])
        and (disagreement or not bool(threshold["require_disagreement"]))
    )
    return capacity_choice if gate_open else order_choice, bool(gate_open)


def evaluate(train_rows: list[dict[str, object]], test_rows: list[dict[str, object]]):
    order_model = fit_pack(train_rows, "order_plus_flow")
    capacity_model = fit_pack(train_rows, "capacity_only")
    opportunity_gate = fit_linear_gate(train_rows, order_model, capacity_model, "opportunity")
    coherence_gate = fit_linear_gate(train_rows, order_model, capacity_model, "coherent_foreign")
    threshold = fit_threshold_gate(train_rows, order_model, capacity_model)

    policies = [
        "order_plus_flow",
        "capacity_only",
        "opportunity_linear_gate",
        "coherence_linear_gate",
        "coherence_disagreement_gate",
        "coherence_margin_gate",
        "threshold_gate",
        "oracle_order_or_capacity",
    ]
    choices: list[dict[str, str | bool]] = []
    for row in test_rows:
        order_score = model_score(capacity_test.features_for_pack(row, "order_plus_flow"), order_model)
        capacity_score = model_score(capacity_test.features_for_pack(row, "capacity_only"), capacity_model)
        order_choice = family_from_score(order_score)
        capacity_choice = family_from_score(capacity_score)
        opportunity_open = bool(predict_linear_gate(row, opportunity_gate, order_model, capacity_model))
        coherence_open = bool(predict_linear_gate(row, coherence_gate, order_model, capacity_model))
        disagreement = order_choice != capacity_choice
        capacity_margin = abs(capacity_score - 0.5)
        threshold_choice, threshold_open = choose_with_threshold(row, order_model, capacity_model, threshold)
        target = str(row["target_family"])
        choices.append(
            {
                "order_plus_flow": order_choice,
                "capacity_only": capacity_choice,
                "opportunity_linear_gate": capacity_choice if opportunity_open else order_choice,
                "coherence_linear_gate": capacity_choice if coherence_open else order_choice,
                "coherence_disagreement_gate": capacity_choice if coherence_open and disagreement else order_choice,
                "coherence_margin_gate": capacity_choice if coherence_open and disagreement and capacity_margin >= 0.05 else order_choice,
                "threshold_gate": threshold_choice,
                "oracle_order_or_capacity": capacity_choice if capacity_choice == target and order_choice != target else order_choice,
                "opportunity_open": opportunity_open,
                "coherence_open": coherence_open,
                "coherence_disagreement_open": coherence_open and disagreement,
                "coherence_margin_open": coherence_open and disagreement and capacity_margin >= 0.05,
                "threshold_open": threshold_open,
            }
        )

    summary_rows: list[dict[str, float | str]] = []
    scenario_rows: list[dict[str, float | str]] = []
    gate_rows: list[dict[str, float | str]] = []
    scenarios = sorted({str(row["scenario"]) for row in test_rows})
    for policy in policies:
        summary_rows.append(
            {
                "policy": policy,
                "overall_accuracy": float(np.mean([choice[policy] == row["target_family"] for choice, row in zip(choices, test_rows)])),
            }
        )
        for scenario in scenarios:
            pairs = [(choice, row) for choice, row in zip(choices, test_rows) if str(row["scenario"]) == scenario]
            scenario_rows.append(
                {
                    "policy": policy,
                    "scenario": scenario,
                    "accuracy": float(np.mean([choice[policy] == row["target_family"] for choice, row in pairs])),
                }
            )

    for gate_name, key in [
        ("opportunity_linear_gate", "opportunity_open"),
        ("coherence_linear_gate", "coherence_open"),
        ("coherence_disagreement_gate", "coherence_disagreement_open"),
        ("coherence_margin_gate", "coherence_margin_open"),
        ("threshold_gate", "threshold_open"),
    ]:
        for scenario in scenarios:
            subset = [choice for choice, row in zip(choices, test_rows) if str(row["scenario"]) == scenario]
            gate_rows.append({"gate": gate_name, "scenario": scenario, "open_rate": float(np.mean([choice[key] for choice in subset]))})

    return (
        sorted(summary_rows, key=lambda row: float(row["overall_accuracy"]), reverse=True),
        scenario_rows,
        gate_rows,
        threshold,
    )


def main() -> None:
    ensure_dir(OUT)
    old_trials = generalization.TRIALS_PER_SCENARIO
    old_timesteps = generalization.event.loop.TIMESTEPS
    generalization.TRIALS_PER_SCENARIO = 1
    generalization.event.loop.TIMESTEPS = 64
    try:
        words = generalization.build_words()
        vocab = generalization.base.collect_vocabulary(words, generalization.base.KMER)
        vocab_index = {token: idx for idx, token in enumerate(vocab)}

        train_rows: list[dict[str, object]] = []
        test_rows: list[dict[str, object]] = []
        for seed in local_switcher.TRAIN_SEEDS[:2]:
            train_rows.extend(flow_control.collect_rows_for_seed(seed, SCOUT_SCENARIOS, words, vocab_index))
        for seed in local_switcher.TEST_SEEDS[:1]:
            test_rows.extend(flow_control.collect_rows_for_seed(seed, SCOUT_SCENARIOS, words, vocab_index))
    finally:
        generalization.TRIALS_PER_SCENARIO = old_trials
        generalization.event.loop.TIMESTEPS = old_timesteps

    summary_rows, scenario_rows, gate_rows, threshold = evaluate(train_rows, test_rows)
    write_csv(summary_rows, OUT / "gate_hardening_summary.csv")
    write_csv(scenario_rows, OUT / "gate_hardening_scenarios.csv")
    write_csv(gate_rows, OUT / "gate_hardening_open_rates.csv")
    write_csv([threshold], OUT / "threshold_gate_selected.csv")

    best = summary_rows[0]
    best_scenarios = [row for row in scenario_rows if row["policy"] == best["policy"]]
    lines = [
        "# Boundary Access Gate Hardening",
        "",
        "Status: scout telemetry only; shortened run for directional testing.",
        "",
        "- question: can the capacity alarm become less blunt by separating coherent outside flow from other hard motion?",
        "- scout settings: 64 time steps, one trial per scenario, two train seeds, one held-out test seed",
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
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
