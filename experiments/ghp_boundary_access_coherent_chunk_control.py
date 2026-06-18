#!/usr/bin/env python3
"""Coherent-chunk control for Boundary Access order-scramble repair.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_belief_inertia_switcher as inertia_switcher
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_low_dimensional_chooser as low_dim
import ghp_boundary_access_low_dimensional_failure_map as failure_map
import ghp_boundary_access_order_scramble_repair as repair
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_coherent_chunk_control_outputs"

VARIANTS = ["rolled", "reversed", "permuted", "cross_chunk"]
COHERENT_VARIANTS = ["cross_chunk"]
PACKS = [
    "baseline_six",
    "damage_rank_only",
    "rank_shape_only",
    "six_plus_rank_shape",
    "six_plus_scramble_signature",
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


def collect_rows_for_seed(
    seed: int,
    scenarios: list[dict[str, float | str]],
    words: dict[str, str],
    vocab_index: dict[str, int],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    event = generalization.event
    old_rng = event.loop.RNG
    event.loop.RNG = np.random.default_rng(seed)
    try:
        for family_name in local_switcher.FAMILY_NAMES:
            word = words[family_name]
            cross_family_name = "generic_ternary" if family_name != "generic_ternary" else "fibonacci"
            cross_word = words[cross_family_name]
            cross_truth = generalization.base.full_histogram(cross_word, generalization.base.KMER, vocab_index)
            limit = len(word) - generalization.base.KMER + 1
            cross_limit = len(cross_word) - generalization.base.KMER + 1

            for scenario in scenarios:
                for variant in VARIANTS:
                    for _ in range(generalization.TRIALS_PER_SCENARIO):
                        start_a = int(event.loop.RNG.integers(0, limit))
                        start_b = int(event.loop.RNG.integers(0, limit))
                        cross_start_b = int(event.loop.RNG.integers(0, cross_limit))

                        wake = np.zeros(len(vocab_index), dtype=float)
                        deep_trace = np.zeros(len(vocab_index), dtype=float)
                        prev_b = np.zeros(len(vocab_index), dtype=float)

                        for step in range(event.loop.TIMESTEPS - 1):
                            current_a = event.loop.base.histogram_from_positions(
                                word,
                                event.loop.chunk_positions(len(word), event.loop.CHUNK, start_a + step),
                                event.loop.base.KMER,
                                vocab_index,
                            )
                            current_b = event.loop.base.histogram_from_positions(
                                word,
                                event.loop.chunk_positions(len(word), event.loop.SECOND_CHUNK, start_b + 2 * step),
                                event.loop.base.KMER,
                                vocab_index,
                            )
                            cross_b = event.loop.base.histogram_from_positions(
                                cross_word,
                                event.loop.chunk_positions(len(cross_word), event.loop.SECOND_CHUNK, cross_start_b + 2 * step),
                                event.loop.base.KMER,
                                vocab_index,
                            )

                            readable_a = event.loop.normalize(current_a)
                            readable_b = event.loop.normalize(current_b)
                            cross_family_b = event.loop.normalize(cross_b)
                            helper = generalization.hardening.helper_view(scenario, readable_b, prev_b, cross_family_b)

                            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * helper)
                            deep_trace = event.loop.normalize(
                                generalization.groove.DEEP_DECAY * deep_trace
                                + (1.0 - generalization.groove.DEEP_DECAY) * wake
                            )

                            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                                prev_b = readable_b
                                continue

                            if variant == "cross_chunk":
                                damaged = cross_family_b
                            else:
                                damaged = event.loop.normalize(generalization.wrong_variants.wrong_signal(variant, readable_a, cross_truth))

                            base_features = local_switcher.feature_row(damaged, helper, wake, deep_trace)
                            belief_features = inertia_switcher.derive_axes(damaged, helper, wake, deep_trace)
                            rows.append(
                                {
                                    "seed": seed,
                                    "scenario": str(scenario["name"]),
                                    "helper_kind": str(scenario["helper_kind"]),
                                    "noise_level": float(scenario["noise_level"]),
                                    "variant": variant,
                                    "label": 1 if variant in COHERENT_VARIANTS else 0,
                                    "target_family": "fibonacci"
                                    if variant in COHERENT_VARIANTS
                                    else "generic_ternary",
                                    "base_features": base_features,
                                    "belief_features": belief_features,
                                    "damaged": damaged,
                                    "helper": helper,
                                    "wake": wake.copy(),
                                    "deep_trace": deep_trace.copy(),
                                }
                            )
                            prev_b = readable_b
    finally:
        event.loop.RNG = old_rng
    return rows


def features_for_pack(row: dict[str, object], pack: str) -> np.ndarray:
    baseline = low_dim.derived_features(row, "six_compass_with_pull")
    rank_shape = repair.rank_shape_features(row)
    if pack == "baseline_six":
        return baseline
    if pack == "damage_rank_only":
        return rank_shape[[2, 3, 4]]
    if pack == "rank_shape_only":
        return rank_shape
    if pack == "six_plus_rank_shape":
        return np.concatenate([baseline, rank_shape])
    if pack == "six_plus_scramble_signature":
        return np.concatenate([baseline, rank_shape[-2:]])
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
            train_rows.extend(collect_rows_for_seed(seed, generalization.TRAIN_SCENARIOS, words, vocab_index))
        for seed in local_switcher.TEST_SEEDS:
            test_rows.extend(collect_rows_for_seed(seed, failure_map.build_test_scenarios(), words, vocab_index))
    finally:
        generalization.TRIALS_PER_SCENARIO = old_trials

    summary_rows: list[dict[str, float | str]] = []
    scenario_rows: list[dict[str, float | str]] = []
    for pack in PACKS:
        summary, scenarios = evaluate_pack(train_rows, test_rows, pack)
        summary_rows.append(summary)
        scenario_rows.extend(scenarios)

    summary_rows = sorted(summary_rows, key=lambda row: float(row["overall_accuracy"]), reverse=True)
    write_csv(summary_rows, OUT / "coherent_chunk_control_summary.csv")
    write_csv(scenario_rows, OUT / "coherent_chunk_control_scenarios.csv")

    best = summary_rows[0]
    target = [row for row in scenario_rows if row["pack"] == best["pack"]]
    lines = [
        "# Boundary Access Coherent-Chunk Control",
        "",
        "- question: does rank-shape repair survive when coherent outside signal is local-chunk-shaped instead of full-truth-shaped?",
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
