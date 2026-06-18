#!/usr/bin/env python3
"""Oracle-gap probe for Boundary Access gated re-embedding.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np

import ghp_boundary_access_external_flow_signal as external_flow
import ghp_boundary_access_flow_continuity_control as flow_control
import ghp_boundary_access_gate_hardening as hardening
import ghp_boundary_access_gated_reembedding as gated
import ghp_boundary_access_integration_capacity as capacity_test
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_low_dimensional_chooser as low_dim
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_oracle_gap_probe_outputs"

GATE_PACKS = [
    "score_only",
    "capacity_context",
    "order_capacity_context",
    "full_local_context",
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


def score_context(row: dict[str, object], order_model, capacity_model) -> tuple[float, float, str, str]:
    order_score = model_score(capacity_test.features_for_pack(row, "order_plus_flow"), order_model)
    capacity_score = model_score(capacity_test.features_for_pack(row, "capacity_only"), capacity_model)
    return (
        order_score,
        capacity_score,
        family_from_score(order_score),
        family_from_score(capacity_score),
    )


def legal_gate_features(
    row: dict[str, object],
    order_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    capacity_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    pack: str,
) -> np.ndarray:
    order_score, capacity_score, order_choice, capacity_choice = score_context(row, order_model, capacity_model)
    score_features = np.array(
        [
            order_score,
            capacity_score,
            abs(order_score - 0.5),
            abs(capacity_score - 0.5),
            capacity_score - order_score,
            float(order_choice != capacity_choice),
        ],
        dtype=float,
    )
    if pack == "score_only":
        return score_features

    capacity_features = capacity_test.features_for_pack(row, "capacity_only")
    external_features = external_flow.external_flow_features(row)
    if pack == "capacity_context":
        return np.concatenate([capacity_features, external_features, score_features])

    order_features = capacity_test.features_for_pack(row, "order_plus_flow")
    if pack == "order_capacity_context":
        return np.concatenate([order_features, capacity_features, external_features, score_features])

    if pack == "full_local_context":
        baseline = low_dim.derived_features(row, "six_compass_with_pull")
        return np.concatenate([baseline, order_features, capacity_features, external_features, score_features])

    raise ValueError(pack)


def fit_opportunity_gate(
    rows: list[dict[str, object]],
    order_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    capacity_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    pack: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    gate_rows: list[dict[str, object]] = []
    for row in rows:
        _, _, order_choice, capacity_choice = score_context(row, order_model, capacity_model)
        target = str(row["target_family"])
        gate_rows.append(
            {
                "features": legal_gate_features(row, order_model, capacity_model, pack),
                "label": int(capacity_choice == target and order_choice != target),
            }
        )
    return local_switcher.fit_linear_probe(gate_rows)


def choose_threshold(
    rows: list[dict[str, object]],
    order_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    capacity_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    gate_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    pack: str,
) -> dict[str, float]:
    cached: list[tuple[float, str, str, str]] = []
    for row in rows:
        score = model_score(legal_gate_features(row, order_model, capacity_model, pack), gate_model)
        _, _, order_choice, capacity_choice = score_context(row, order_model, capacity_model)
        cached.append((score, order_choice, capacity_choice, str(row["target_family"])))
    scores = np.array([item[0] for item in cached], dtype=float)
    candidates = sorted(set(np.quantile(scores, np.linspace(0.0, 1.0, 101)).tolist() + [0.5]))
    best: dict[str, float] | None = None
    for threshold in candidates:
        correct: list[bool] = []
        open_flags: list[bool] = []
        for score, order_choice, capacity_choice, target in cached:
            gate_open = bool(score >= threshold)
            choice = capacity_choice if gate_open else order_choice
            correct.append(choice == target)
            open_flags.append(gate_open)
        candidate = {
            "threshold": float(threshold),
            "train_accuracy": float(np.mean(correct)),
            "train_open_rate": float(np.mean(open_flags)),
        }
        if best is None or (
            candidate["train_accuracy"],
            -candidate["train_open_rate"],
        ) > (
            best["train_accuracy"],
            -best["train_open_rate"],
        ):
            best = candidate
    assert best is not None
    return best


def base_choices(row: dict[str, object], order_model, capacity_model, coherence_gate, threshold_gate) -> dict[str, str | bool]:
    order_score, capacity_score, order_choice, capacity_choice = score_context(row, order_model, capacity_model)
    coherence_open = bool(hardening.predict_linear_gate(row, coherence_gate, order_model, capacity_model))
    disagreement = order_choice != capacity_choice
    capacity_margin = abs(capacity_score - 0.5)
    threshold_choice, threshold_open = hardening.choose_with_threshold(row, order_model, capacity_model, threshold_gate)
    target = str(row["target_family"])
    return {
        "order_plus_flow": order_choice,
        "capacity_only": capacity_choice,
        "coherence_margin_gate": capacity_choice if coherence_open and disagreement and capacity_margin >= 0.05 else order_choice,
        "threshold_gate": threshold_choice,
        "oracle_order_or_capacity": capacity_choice if capacity_choice == target and order_choice != target else order_choice,
        "coherence_margin_open": coherence_open and disagreement and capacity_margin >= 0.05,
        "threshold_open": threshold_open,
    }


def bucket_for(row: dict[str, object], choices: dict[str, str | bool]) -> str:
    order_correct = choices["order_plus_flow"] == row["target_family"]
    capacity_correct = choices["capacity_only"] == row["target_family"]
    if order_correct and capacity_correct:
        return "both_correct"
    if order_correct and not capacity_correct:
        return "order_only"
    if capacity_correct and not order_correct:
        return "capacity_only"
    return "both_wrong"


def evaluate(train_rows: list[dict[str, object]], test_rows: list[dict[str, object]]):
    order_model = fit_pack(train_rows, "order_plus_flow")
    capacity_model = fit_pack(train_rows, "capacity_only")
    coherence_gate = hardening.fit_linear_gate(train_rows, order_model, capacity_model, "coherent_foreign")
    threshold_gate = hardening.fit_threshold_gate(train_rows, order_model, capacity_model)

    gate_models = {
        pack: fit_opportunity_gate(train_rows, order_model, capacity_model, pack)
        for pack in GATE_PACKS
    }
    gate_thresholds = {
        pack: choose_threshold(train_rows, order_model, capacity_model, gate_models[pack], pack)
        for pack in GATE_PACKS
    }

    all_choices: list[dict[str, str | bool]] = []
    buckets: list[str] = []
    for row in test_rows:
        choices = base_choices(row, order_model, capacity_model, coherence_gate, threshold_gate)
        for pack in GATE_PACKS:
            score = model_score(legal_gate_features(row, order_model, capacity_model, pack), gate_models[pack])
            _, _, order_choice, capacity_choice = score_context(row, order_model, capacity_model)
            open_default = bool(score >= 0.5)
            open_calibrated = bool(score >= gate_thresholds[pack]["threshold"])
            choices[f"{pack}_gate"] = capacity_choice if open_default else order_choice
            choices[f"{pack}_calibrated_gate"] = capacity_choice if open_calibrated else order_choice
            choices[f"{pack}_gate_open"] = open_default
            choices[f"{pack}_calibrated_open"] = open_calibrated
        buckets.append(bucket_for(row, choices))
        all_choices.append(choices)

    policies = [
        "oracle_order_or_capacity",
        "coherence_margin_gate",
        "threshold_gate",
        "order_plus_flow",
        "capacity_only",
    ]
    for pack in GATE_PACKS:
        policies.extend([f"{pack}_gate", f"{pack}_calibrated_gate"])

    summary_rows: list[dict[str, float | str]] = []
    scenario_rows: list[dict[str, float | str]] = []
    for policy in policies:
        summary_rows.append(
            {
                "policy": policy,
                "overall_accuracy": float(np.mean([choice[policy] == row["target_family"] for choice, row in zip(all_choices, test_rows)])),
            }
        )
        for scenario in sorted({str(row["scenario"]) for row in test_rows}):
            pairs = [
                (choice, row)
                for choice, row in zip(all_choices, test_rows)
                if str(row["scenario"]) == scenario
            ]
            scenario_rows.append(
                {
                    "policy": policy,
                    "scenario": scenario,
                    "accuracy": float(np.mean([choice[policy] == row["target_family"] for choice, row in pairs])),
                }
            )

    bucket_rows: list[dict[str, float | str]] = []
    for scenario in ["all"] + sorted({str(row["scenario"]) for row in test_rows}):
        if scenario == "all":
            subset = buckets
        else:
            subset = [bucket for bucket, row in zip(buckets, test_rows) if str(row["scenario"]) == scenario]
        total = len(subset)
        for bucket in ["both_correct", "order_only", "capacity_only", "both_wrong"]:
            count = subset.count(bucket)
            bucket_rows.append(
                {
                    "scenario": scenario,
                    "bucket": bucket,
                    "count": count,
                    "rate": float(count / total) if total else 0.0,
                }
            )

    capture_rows: list[dict[str, float | str]] = []
    gate_keys = ["coherence_margin_open", "threshold_open"]
    for pack in GATE_PACKS:
        gate_keys.extend([f"{pack}_gate_open", f"{pack}_calibrated_open"])
    for gate_key in gate_keys:
        for bucket in ["capacity_only", "order_only", "both_wrong", "both_correct"]:
            flags = [bool(choice[gate_key]) for choice, row_bucket in zip(all_choices, buckets) if row_bucket == bucket]
            capture_rows.append(
                {
                    "gate": gate_key,
                    "bucket": bucket,
                    "open_rate": float(np.mean(flags)) if flags else 0.0,
                    "count": len(flags),
                }
            )

    threshold_rows = [
        {
            "gate": pack,
            "dimensions": int(len(legal_gate_features(test_rows[0], order_model, capacity_model, pack))),
            **gate_thresholds[pack],
        }
        for pack in GATE_PACKS
    ]

    return (
        sorted(summary_rows, key=lambda row: float(row["overall_accuracy"]), reverse=True),
        scenario_rows,
        bucket_rows,
        capture_rows,
        threshold_rows,
    )


def main() -> None:
    ensure_dir(OUT)
    full_run = os.environ.get("GHP_ORACLE_GAP_FULL") == "1"
    old_trials = generalization.TRIALS_PER_SCENARIO
    old_timesteps = generalization.event.loop.TIMESTEPS
    if full_run:
        scenarios = gated.TARGET_SCENARIOS
        train_seeds = local_switcher.TRAIN_SEEDS
        test_seeds = local_switcher.TEST_SEEDS
        generalization.TRIALS_PER_SCENARIO = 3
    else:
        scenarios = hardening.SCOUT_SCENARIOS
        train_seeds = local_switcher.TRAIN_SEEDS[:2]
        test_seeds = local_switcher.TEST_SEEDS[:1]
        generalization.TRIALS_PER_SCENARIO = 1
        generalization.event.loop.TIMESTEPS = 64
    try:
        words = generalization.build_words()
        vocab = generalization.base.collect_vocabulary(words, generalization.base.KMER)
        vocab_index = {token: idx for idx, token in enumerate(vocab)}

        train_rows: list[dict[str, object]] = []
        test_rows: list[dict[str, object]] = []
        for seed in train_seeds:
            train_rows.extend(flow_control.collect_rows_for_seed(seed, scenarios, words, vocab_index))
        for seed in test_seeds:
            test_rows.extend(flow_control.collect_rows_for_seed(seed, scenarios, words, vocab_index))
    finally:
        generalization.TRIALS_PER_SCENARIO = old_trials
        generalization.event.loop.TIMESTEPS = old_timesteps

    summary_rows, scenario_rows, bucket_rows, capture_rows, threshold_rows = evaluate(train_rows, test_rows)
    write_csv(summary_rows, OUT / "oracle_gap_summary.csv")
    write_csv(scenario_rows, OUT / "oracle_gap_scenarios.csv")
    write_csv(bucket_rows, OUT / "oracle_gap_buckets.csv")
    write_csv(capture_rows, OUT / "oracle_gap_gate_capture.csv")
    write_csv(threshold_rows, OUT / "oracle_gap_thresholds.csv")

    best = summary_rows[0]
    best_scenarios = [row for row in scenario_rows if row["policy"] == best["policy"]]
    lines = [
        "# Boundary Access Oracle-Gap Probe",
        "",
        "Status: targeted hard-lane toy telemetry only.",
        "",
        "- question: can legal local context learn when capacity should override order?",
        "- mode: `full`" if full_run else "- mode: `scout`",
        "- settings: same target grid as the coherence-gate full rerun, all train and test seeds, three trials per scenario"
        if full_run
        else "- settings: scout grid, two train seeds, one held-out test seed, one trial per scenario, 64 time steps",
        f"- best policy: `{best['policy']}`",
        f"- overall held-out accuracy: `{float(best['overall_accuracy']):.3f}`",
        "",
        "Ranking:",
    ]
    for row in summary_rows:
        lines.append(f"- {row['policy']}: `{float(row['overall_accuracy']):.3f}`")
    lines.extend(["", "Gate thresholds:"])
    for row in threshold_rows:
        lines.append(
            f"- {row['gate']} ({int(row['dimensions'])}D): threshold `{float(row['threshold']):.3f}`, "
            f"train accuracy `{float(row['train_accuracy']):.3f}`, train open rate `{float(row['train_open_rate']):.3f}`"
        )
    lines.extend(["", "Order-vs-capacity buckets:"])
    for row in [item for item in bucket_rows if item["scenario"] == "all"]:
        lines.append(f"- {row['bucket']}: `{float(row['rate']):.3f}` ({int(row['count'])})")
    lines.extend(["", "Best-policy scenario map:"])
    for row in sorted(best_scenarios, key=lambda item: str(item["scenario"])):
        lines.append(f"- {row['scenario']}: `{float(row['accuracy']):.3f}`")
    lines.extend(["", "Gate capture on the real oracle gap:"])
    for row in capture_rows:
        if row["bucket"] in {"capacity_only", "order_only"}:
            lines.append(f"- {row['gate']} / {row['bucket']}: `{float(row['open_rate']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
