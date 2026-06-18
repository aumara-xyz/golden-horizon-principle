#!/usr/bin/env python3
"""Flow-continuity control for Boundary Access repair.

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
import ghp_boundary_access_order_relation_control as order_control
import ghp_boundary_access_rank_matched_control as rank_matched
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_flow_continuity_control_outputs"

PACKS = [
    "baseline_six",
    "order_relation_only",
    "flow_only",
    "baseline_plus_flow",
    "order_plus_flow",
    "baseline_plus_order_flow",
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


def delta(current: np.ndarray, previous: np.ndarray) -> np.ndarray:
    return np.asarray(current, dtype=float) - np.asarray(previous, dtype=float)


def top_delta_overlap(a: np.ndarray, b: np.ndarray, positive: bool) -> float:
    count = max(1, int(round(len(a) * 0.10)))
    if positive:
        a_idx = set(np.argsort(a)[-count:].tolist())
        b_idx = set(np.argsort(b)[-count:].tolist())
    else:
        a_idx = set(np.argsort(a)[:count].tolist())
        b_idx = set(np.argsort(b)[:count].tolist())
    return len(a_idx & b_idx) / count


def flow_features(row: dict[str, object]) -> np.ndarray:
    damaged_delta = delta(row["damaged"], row["prev_readable_a"])
    helper_delta = delta(row["helper"], row["prev_helper"])
    wake_delta = delta(row["wake"], row["prev_wake"])
    deep_delta = delta(row["deep_trace"], row["prev_deep_trace"])

    base = local_switcher.base
    return np.array(
        [
            base.cosine(damaged_delta, helper_delta),
            base.cosine(damaged_delta, wake_delta),
            base.cosine(damaged_delta, deep_delta),
            base.cosine(helper_delta, wake_delta),
            base.cosine(helper_delta, deep_delta),
            order_control.rank_corr(damaged_delta, helper_delta),
            order_control.rank_corr(damaged_delta, wake_delta),
            order_control.rank_corr(damaged_delta, deep_delta),
            top_delta_overlap(damaged_delta, helper_delta, positive=True),
            top_delta_overlap(damaged_delta, wake_delta, positive=True),
            top_delta_overlap(damaged_delta, deep_delta, positive=True),
            top_delta_overlap(damaged_delta, helper_delta, positive=False),
            top_delta_overlap(damaged_delta, wake_delta, positive=False),
            top_delta_overlap(damaged_delta, deep_delta, positive=False),
            float(np.linalg.norm(damaged_delta)),
            float(np.linalg.norm(helper_delta)),
            float(np.linalg.norm(wake_delta)),
        ],
        dtype=float,
    )


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
                for variant in rank_matched.VARIANTS:
                    for _ in range(generalization.TRIALS_PER_SCENARIO):
                        start_a = int(event.loop.RNG.integers(0, limit))
                        start_b = int(event.loop.RNG.integers(0, limit))
                        cross_start_b = int(event.loop.RNG.integers(0, cross_limit))

                        wake = np.zeros(len(vocab_index), dtype=float)
                        deep_trace = np.zeros(len(vocab_index), dtype=float)
                        prev_b = np.zeros(len(vocab_index), dtype=float)
                        prev_readable_a = np.zeros(len(vocab_index), dtype=float)
                        prev_helper = np.zeros(len(vocab_index), dtype=float)
                        prev_wake = np.zeros(len(vocab_index), dtype=float)
                        prev_deep_trace = np.zeros(len(vocab_index), dtype=float)

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

                            next_wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * helper)
                            next_deep = event.loop.normalize(
                                generalization.groove.DEEP_DECAY * deep_trace
                                + (1.0 - generalization.groove.DEEP_DECAY) * next_wake
                            )

                            if float(event.loop.RNG.random()) < event.DAMAGE_PROB:
                                if variant == "cross_rankmatched":
                                    damaged = rank_matched.rank_match(cross_family_b, readable_a)
                                else:
                                    damaged = event.loop.normalize(
                                        generalization.wrong_variants.wrong_signal(variant, readable_a, cross_truth)
                                    )

                                base_features = local_switcher.feature_row(damaged, helper, next_wake, next_deep)
                                belief_features = chunk_control.inertia_switcher.derive_axes(damaged, helper, next_wake, next_deep)
                                rows.append(
                                    {
                                        "seed": seed,
                                        "scenario": str(scenario["name"]),
                                        "helper_kind": str(scenario["helper_kind"]),
                                        "noise_level": float(scenario["noise_level"]),
                                        "variant": variant,
                                        "label": 1 if variant in rank_matched.COHERENT_VARIANTS else 0,
                                        "target_family": "fibonacci"
                                        if variant in rank_matched.COHERENT_VARIANTS
                                        else "generic_ternary",
                                        "base_features": base_features,
                                        "belief_features": belief_features,
                                        "damaged": damaged,
                                        "helper": helper,
                                        "wake": next_wake.copy(),
                                        "deep_trace": next_deep.copy(),
                                        "prev_readable_a": prev_readable_a.copy(),
                                        "prev_helper": prev_helper.copy(),
                                        "prev_wake": prev_wake.copy(),
                                        "prev_deep_trace": prev_deep_trace.copy(),
                                    }
                                )

                            prev_readable_a = readable_a.copy()
                            prev_helper = helper.copy()
                            prev_wake = next_wake.copy()
                            prev_deep_trace = next_deep.copy()
                            wake = next_wake
                            deep_trace = next_deep
                            prev_b = readable_b
    finally:
        event.loop.RNG = old_rng
    return rows


def features_for_pack(row: dict[str, object], pack: str) -> np.ndarray:
    baseline = low_dim.derived_features(row, "six_compass_with_pull")
    order = order_control.order_relation_features(row)
    flow = flow_features(row)
    if pack == "baseline_six":
        return baseline
    if pack == "order_relation_only":
        return order
    if pack == "flow_only":
        return flow
    if pack == "baseline_plus_flow":
        return np.concatenate([baseline, flow])
    if pack == "order_plus_flow":
        return np.concatenate([order, flow])
    if pack == "baseline_plus_order_flow":
        return np.concatenate([baseline, order, flow])
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
    write_csv(summary_rows, OUT / "flow_continuity_summary.csv")
    write_csv(scenario_rows, OUT / "flow_continuity_scenarios.csv")

    best = summary_rows[0]
    target = [row for row in scenario_rows if row["pack"] == best["pack"]]
    lines = [
        "# Boundary Access Flow-Continuity Control",
        "",
        "- question: does the chooser improve when it tracks local order moving through time?",
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
