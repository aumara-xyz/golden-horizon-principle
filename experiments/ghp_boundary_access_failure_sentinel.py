#!/usr/bin/env python3
"""Failure-sentinel probe for Boundary Access.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np

import ghp_boundary_access_gate_hardening as hardening
import ghp_boundary_access_gated_reembedding as gated
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_oracle_gap_probe as oracle_gap
import ghp_boundary_access_selector_generalization as generalization
import ghp_boundary_access_flow_continuity_control as flow_control


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_failure_sentinel_outputs"
PACKS = ["score_only", "capacity_context", "order_capacity_context", "full_local_context"]


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


def fit_sentinel(rows: list[dict[str, object]], order_model, capacity_model, pack: str):
    sentinel_rows: list[dict[str, object]] = []
    for row in rows:
        _, _, order_choice, capacity_choice = oracle_gap.score_context(row, order_model, capacity_model)
        target = str(row["target_family"])
        label = int(order_choice != target and capacity_choice != target)
        sentinel_rows.append(
            {
                "features": oracle_gap.legal_gate_features(row, order_model, capacity_model, pack),
                "label": label,
            }
        )
    return local_switcher.fit_linear_probe(sentinel_rows)


def score_rows(rows: list[dict[str, object]], order_model, capacity_model, model, pack: str):
    scored = []
    for row in rows:
        _, _, order_choice, capacity_choice = oracle_gap.score_context(row, order_model, capacity_model)
        target = str(row["target_family"])
        if order_choice == target and capacity_choice == target:
            bucket = "both_correct"
        elif order_choice == target and capacity_choice != target:
            bucket = "order_only"
        elif capacity_choice == target and order_choice != target:
            bucket = "capacity_only"
        else:
            bucket = "both_wrong"
        score = oracle_gap.model_score(oracle_gap.legal_gate_features(row, order_model, capacity_model, pack), model)
        scored.append({"row": row, "bucket": bucket, "score": score})
    return scored


def choose_sparse_threshold(scored_train: list[dict[str, object]], max_false_alarm: float) -> dict[str, float]:
    scores = sorted({float(item["score"]) for item in scored_train})
    best: dict[str, float] | None = None
    for threshold in scores:
        both_wrong = [item for item in scored_train if item["bucket"] == "both_wrong"]
        both_correct = [item for item in scored_train if item["bucket"] == "both_correct"]
        useful_gap = [item for item in scored_train if item["bucket"] in {"order_only", "capacity_only"}]
        both_wrong_capture = float(np.mean([float(item["score"]) >= threshold for item in both_wrong])) if both_wrong else 0.0
        both_correct_false_alarm = (
            float(np.mean([float(item["score"]) >= threshold for item in both_correct])) if both_correct else 0.0
        )
        useful_gap_false_alarm = (
            float(np.mean([float(item["score"]) >= threshold for item in useful_gap])) if useful_gap else 0.0
        )
        if both_correct_false_alarm > max_false_alarm:
            continue
        candidate = {
            "threshold": float(threshold),
            "train_both_wrong_capture": both_wrong_capture,
            "train_both_correct_false_alarm": both_correct_false_alarm,
            "train_useful_gap_false_alarm": useful_gap_false_alarm,
        }
        if best is None or (
            candidate["train_both_wrong_capture"],
            -candidate["train_useful_gap_false_alarm"],
        ) > (
            best["train_both_wrong_capture"],
            -best["train_useful_gap_false_alarm"],
        ):
            best = candidate
    if best is None:
        return {
            "threshold": 0.5,
            "train_both_wrong_capture": 0.0,
            "train_both_correct_false_alarm": 0.0,
            "train_useful_gap_false_alarm": 0.0,
        }
    return best


def evaluate(train_rows: list[dict[str, object]], test_rows: list[dict[str, object]]):
    order_model = oracle_gap.fit_pack(train_rows, "order_plus_flow")
    capacity_model = oracle_gap.fit_pack(train_rows, "capacity_only")

    summary_rows: list[dict[str, float | str]] = []
    bucket_rows: list[dict[str, float | str]] = []
    scenario_rows: list[dict[str, float | str]] = []
    threshold_rows: list[dict[str, float | str]] = []
    for pack in PACKS:
        model = fit_sentinel(train_rows, order_model, capacity_model, pack)
        scored_train = score_rows(train_rows, order_model, capacity_model, model, pack)
        scored_test = score_rows(test_rows, order_model, capacity_model, model, pack)
        sparse = choose_sparse_threshold(scored_train, max_false_alarm=0.05)
        thresholds = {
            "default": 0.5,
            "sparse_5pct_false_alarm": sparse["threshold"],
        }
        threshold_rows.append({"pack": pack, **sparse})

        for threshold_name, threshold in thresholds.items():
            flags = [float(item["score"]) >= float(threshold) for item in scored_test]
            labels = [item["bucket"] == "both_wrong" for item in scored_test]
            true_positive = sum(flag and label for flag, label in zip(flags, labels))
            false_positive = sum(flag and not label for flag, label in zip(flags, labels))
            false_negative = sum((not flag) and label for flag, label in zip(flags, labels))
            precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
            recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
            summary_rows.append(
                {
                    "sentinel": f"{pack}_{threshold_name}",
                    "dimensions": int(
                        len(oracle_gap.legal_gate_features(test_rows[0], order_model, capacity_model, pack))
                    ),
                    "open_rate": float(np.mean(flags)),
                    "precision": float(precision),
                    "both_wrong_recall": float(recall),
                }
            )
            for bucket in ["both_wrong", "both_correct", "order_only", "capacity_only"]:
                subset = [item for item in scored_test if item["bucket"] == bucket]
                bucket_rows.append(
                    {
                        "sentinel": f"{pack}_{threshold_name}",
                        "bucket": bucket,
                        "open_rate": float(np.mean([float(item["score"]) >= float(threshold) for item in subset]))
                        if subset
                        else 0.0,
                        "count": len(subset),
                    }
                )
            for scenario in sorted({str(item["row"]["scenario"]) for item in scored_test}):
                subset = [item for item in scored_test if str(item["row"]["scenario"]) == scenario]
                scenario_rows.append(
                    {
                        "sentinel": f"{pack}_{threshold_name}",
                        "scenario": scenario,
                        "open_rate": float(np.mean([float(item["score"]) >= float(threshold) for item in subset])),
                    }
                )

    return (
        sorted(summary_rows, key=lambda row: (float(row["both_wrong_recall"]), float(row["precision"])), reverse=True),
        bucket_rows,
        scenario_rows,
        threshold_rows,
    )


def main() -> None:
    ensure_dir(OUT)
    full_run = os.environ.get("GHP_FAILURE_SENTINEL_FULL") == "1"
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

    summary_rows, bucket_rows, scenario_rows, threshold_rows = evaluate(train_rows, test_rows)
    write_csv(summary_rows, OUT / "failure_sentinel_summary.csv")
    write_csv(bucket_rows, OUT / "failure_sentinel_buckets.csv")
    write_csv(scenario_rows, OUT / "failure_sentinel_scenarios.csv")
    write_csv(threshold_rows, OUT / "failure_sentinel_thresholds.csv")

    best = summary_rows[0]
    lines = [
        "# Boundary Access Failure Sentinel",
        "",
        "Status: targeted hard-lane toy telemetry only.",
        "",
        "- question: can legal local context detect when both order and capacity are wrong?",
        "- mode: `full`" if full_run else "- mode: `scout`",
        "- settings: same target grid as the coherence-gate full rerun, all train and test seeds, three trials per scenario"
        if full_run
        else "- settings: scout grid, two train seeds, one held-out test seed, one trial per scenario, 64 time steps",
        f"- best sentinel: `{best['sentinel']}`",
        f"- open rate: `{float(best['open_rate']):.3f}`",
        f"- precision: `{float(best['precision']):.3f}`",
        f"- both-wrong recall: `{float(best['both_wrong_recall']):.3f}`",
        "",
        "Ranking:",
    ]
    for row in summary_rows:
        lines.append(
            f"- {row['sentinel']} ({int(row['dimensions'])}D): open `{float(row['open_rate']):.3f}`, "
            f"precision `{float(row['precision']):.3f}`, recall `{float(row['both_wrong_recall']):.3f}`"
        )
    lines.extend(["", "Sparse thresholds:"])
    for row in threshold_rows:
        lines.append(
            f"- {row['pack']}: threshold `{float(row['threshold']):.3f}`, "
            f"train both-wrong capture `{float(row['train_both_wrong_capture']):.3f}`, "
            f"train both-correct false alarm `{float(row['train_both_correct_false_alarm']):.3f}`"
        )
    lines.extend(["", "Best-sentinel bucket opens:"])
    for row in [item for item in bucket_rows if item["sentinel"] == best["sentinel"]]:
        lines.append(f"- {row['bucket']}: `{float(row['open_rate']):.3f}` ({int(row['count'])})")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
