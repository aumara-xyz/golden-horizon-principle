#!/usr/bin/env python3
"""Order-relation control after rank-profile shortcuts are removed.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_coherent_chunk_control as chunk_control
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_low_dimensional_chooser as low_dim
import ghp_boundary_access_low_dimensional_failure_map as failure_map
import ghp_boundary_access_rank_matched_control as rank_matched
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_order_relation_control_outputs"

PACKS = [
    "baseline_six",
    "order_relation_only",
    "baseline_plus_order_relation",
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


def rank_vector(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(len(values), dtype=float)
    ranks -= ranks.mean()
    norm = np.linalg.norm(ranks)
    return ranks / norm if norm > 0.0 else ranks


def rank_corr(a: np.ndarray, b: np.ndarray) -> float:
    return float(rank_vector(a) @ rank_vector(b))


def top_index_overlap(a: np.ndarray, b: np.ndarray, frac: float) -> float:
    count = max(1, int(round(len(a) * frac)))
    a_top = set(np.argsort(a)[-count:].tolist())
    b_top = set(np.argsort(b)[-count:].tolist())
    return len(a_top & b_top) / count


def order_relation_features(row: dict[str, object]) -> np.ndarray:
    damaged = np.asarray(row["damaged"], dtype=float)
    helper = np.asarray(row["helper"], dtype=float)
    wake = np.asarray(row["wake"], dtype=float)
    deep_trace = np.asarray(row["deep_trace"], dtype=float)

    return np.array(
        [
            rank_corr(damaged, helper),
            rank_corr(damaged, wake),
            rank_corr(damaged, deep_trace),
            rank_corr(helper, wake),
            rank_corr(helper, deep_trace),
            top_index_overlap(damaged, helper, 0.10),
            top_index_overlap(damaged, wake, 0.10),
            top_index_overlap(damaged, deep_trace, 0.10),
        ],
        dtype=float,
    )


def features_for_pack(row: dict[str, object], pack: str) -> np.ndarray:
    baseline = low_dim.derived_features(row, "six_compass_with_pull")
    order = order_relation_features(row)
    if pack == "baseline_six":
        return baseline
    if pack == "order_relation_only":
        return order
    if pack == "baseline_plus_order_relation":
        return np.concatenate([baseline, order])
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
    generalization.TRIALS_PER_SCENARIO = 5
    try:
        words = generalization.build_words()
        vocab = generalization.base.collect_vocabulary(words, generalization.base.KMER)
        vocab_index = {token: idx for idx, token in enumerate(vocab)}

        train_rows: list[dict[str, object]] = []
        test_rows: list[dict[str, object]] = []
        for seed in local_switcher.TRAIN_SEEDS:
            train_rows.extend(rank_matched.collect_rows_for_seed(seed, generalization.TRAIN_SCENARIOS, words, vocab_index))
        for seed in local_switcher.TEST_SEEDS:
            test_rows.extend(rank_matched.collect_rows_for_seed(seed, failure_map.build_test_scenarios(), words, vocab_index))
    finally:
        generalization.TRIALS_PER_SCENARIO = old_trials

    summary_rows: list[dict[str, float | str]] = []
    scenario_rows: list[dict[str, float | str]] = []
    for pack in PACKS:
        summary, scenarios = evaluate_pack(train_rows, test_rows, pack)
        summary_rows.append(summary)
        scenario_rows.extend(scenarios)

    summary_rows = sorted(summary_rows, key=lambda row: float(row["overall_accuracy"]), reverse=True)
    write_csv(summary_rows, OUT / "order_relation_control_summary.csv")
    write_csv(scenario_rows, OUT / "order_relation_control_scenarios.csv")

    best = summary_rows[0]
    target = [row for row in scenario_rows if row["pack"] == best["pack"]]
    lines = [
        "# Boundary Access Order-Relation Control",
        "",
        "- question: after rank-profile shortcuts are removed, do order relations recover the chooser?",
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
