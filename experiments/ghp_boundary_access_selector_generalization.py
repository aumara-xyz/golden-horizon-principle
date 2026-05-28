#!/usr/bin/env python3
"""Cross-scenario generalization test for Boundary Access selectors.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from pathlib import Path

import numpy as np

import ghp_boundary_access_belief_inertia_switcher as inertia_switcher
import ghp_boundary_access_channel_toy as base
import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_event_fallback as event
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_noise_regime_hardening as hardening
import ghp_boundary_access_strange_familiar_switcher as belief_switcher
import ghp_boundary_access_wrong_signal_variants as wrong_variants


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_selector_generalization_outputs"

TRAIN_SCENARIOS = [
    {"name": "uniform_train_020", "helper_kind": "uniform_mix", "noise_level": 0.20},
    {"name": "uniform_train_030", "helper_kind": "uniform_mix", "noise_level": 0.30},
    {"name": "uniform_train_040", "helper_kind": "uniform_mix", "noise_level": 0.40},
]

TEST_SCENARIOS = [
    {"name": "clean_current", "helper_kind": "current", "noise_level": 0.0},
    {"name": "uniform_mix_mid", "helper_kind": "uniform_mix", "noise_level": 0.30},
    {"name": "gaussian_mix_mid", "helper_kind": "gaussian_mix", "noise_level": 0.30},
    {"name": "delayed_uniform_mid", "helper_kind": "delayed_uniform", "noise_level": 0.30},
    {"name": "permute_mix_mid", "helper_kind": "permute_mix", "noise_level": 0.30},
    {"name": "cross_family_mid", "helper_kind": "cross_family", "noise_level": 0.30},
]
INTERNAL_VARIANTS = local_switcher.INTERNAL_VARIANTS
COHERENT_VARIANTS = local_switcher.COHERENT_VARIANTS
TRIALS_PER_SCENARIO = 8


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


def build_words() -> dict[str, str]:
    return {family.name: base.generate_word(family.rules, base.TARGET_LENGTH) for family in base.FAMILIES}


def collect_rows_for_seed(
    seed: int,
    scenarios: list[dict[str, float | str]],
    words: dict[str, str],
    vocab_index: dict[str, int],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    old_rng = event.loop.RNG
    event.loop.RNG = np.random.default_rng(seed)
    try:
        for family_name in local_switcher.FAMILY_NAMES:
            word = words[family_name]
            cross_family_name = "generic_ternary" if family_name != "generic_ternary" else "fibonacci"
            cross_word = words[cross_family_name]
            cross_truth = base.full_histogram(cross_word, base.KMER, vocab_index)
            limit = len(word) - base.KMER + 1
            cross_limit = len(cross_word) - base.KMER + 1

            for scenario in scenarios:
                for variant in INTERNAL_VARIANTS + COHERENT_VARIANTS:
                    for _ in range(TRIALS_PER_SCENARIO):
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
                            helper = hardening.helper_view(scenario, readable_b, prev_b, cross_family_b)

                            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * helper)
                            deep_trace = event.loop.normalize(groove.DEEP_DECAY * deep_trace + (1.0 - groove.DEEP_DECAY) * wake)

                            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                                prev_b = readable_b
                                continue

                            damaged = event.loop.normalize(wrong_variants.wrong_signal(variant, readable_a, cross_truth))
                            base_features = local_switcher.feature_row(damaged, helper, wake, deep_trace)
                            compact_features = belief_switcher.derive_axes(
                                {
                                    "features": base_features,
                                }
                            )
                            belief_features = inertia_switcher.derive_axes(
                                damaged,
                                helper,
                                wake,
                                deep_trace,
                            )

                            rows.append(
                                {
                                    "seed": seed,
                                    "scenario": str(scenario["name"]),
                                    "variant": variant,
                                    "label": 1 if variant in COHERENT_VARIANTS else 0,
                                    "target_family": "fibonacci" if variant in COHERENT_VARIANTS else "generic_ternary",
                                    "base_features": base_features,
                                    "strange_features": compact_features,
                                    "groove_features": belief_features[inertia_switcher.PACKS["groove_compass"]],
                                    "belief_features": belief_features,
                                }
                            )
                            prev_b = readable_b
    finally:
        event.loop.RNG = old_rng
    return rows


def train_full_switcher(train_rows: list[dict[str, object]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = []
    for row in train_rows:
        rows.append({"features": row["base_features"], "label": row["label"]})
    return local_switcher.fit_linear_probe(rows)


def train_compact_switcher(train_rows: list[dict[str, object]], key: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = []
    for row in train_rows:
        rows.append({"features": row[key], "label": row["label"]})
    return local_switcher.fit_linear_probe(rows)


def evaluate_rows(
    rows: list[dict[str, object]],
    full_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    strange_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    groove_model: tuple[np.ndarray, np.ndarray, np.ndarray],
    belief_model: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> list[dict[str, float | str]]:
    summary: list[dict[str, float | str]] = []
    scenario_names = sorted({str(row["scenario"]) for row in rows})
    for scenario_name in scenario_names:
        subset = [row for row in rows if row["scenario"] == scenario_name]
        for switcher_name, key, model in [
            ("always_generic_ternary", "", None),
            ("full_local_switcher", "base_features", full_model),
            ("strange_familiar_all_four", "strange_features", strange_model),
            ("groove_compass", "groove_features", groove_model),
            ("belief_all_axes", "belief_features", belief_model),
        ]:
            if model is None:
                chosen = ["generic_ternary"] * len(subset)
            else:
                mean, std, weights = model
                chosen = [
                    "fibonacci"
                    if local_switcher.predict_linear_probe(np.asarray(row[key], dtype=float), mean, std, weights) == 1
                    else "generic_ternary"
                    for row in subset
                ]
            accuracy = np.mean([choice == row["target_family"] for choice, row in zip(chosen, subset)])
            summary.append(
                {
                    "scenario": scenario_name,
                    "switcher": switcher_name,
                    "target_family_accuracy": float(accuracy),
                }
            )
    return summary


def main() -> None:
    ensure_dir(OUT)
    words = build_words()
    vocab = base.collect_vocabulary(words, base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    train_rows: list[dict[str, object]] = []
    test_rows: list[dict[str, object]] = []
    for seed in local_switcher.TRAIN_SEEDS:
        train_rows.extend(collect_rows_for_seed(seed, TRAIN_SCENARIOS, words, vocab_index))
    for seed in local_switcher.TEST_SEEDS:
        test_rows.extend(collect_rows_for_seed(seed, TEST_SCENARIOS, words, vocab_index))

    full_model = train_full_switcher(train_rows)
    strange_model = train_compact_switcher(train_rows, "strange_features")
    groove_model = train_compact_switcher(train_rows, "groove_features")
    belief_model = train_compact_switcher(train_rows, "belief_features")

    summary = evaluate_rows(test_rows, full_model, strange_model, groove_model, belief_model)
    write_csv(summary, OUT / "selector_generalization_summary.csv")

    lines = [
        "# Boundary Access Selector Generalization",
        "",
        "- train world: uniform-smear wrong/coherent split at `0.20`, `0.30`, `0.40`",
        "- test worlds: clean, Gaussian, delayed, permuted, cross-family, and uniform regimes",
        "",
        "Best switcher by scenario:",
    ]
    scenario_names = sorted({str(row["scenario"]) for row in summary})
    for scenario_name in scenario_names:
        subset = [row for row in summary if row["scenario"] == scenario_name]
        best = max(subset, key=lambda row: float(row["target_family_accuracy"]))
        lines.append(
            f"- {scenario_name}: `{best['switcher']}` `{float(best['target_family_accuracy']):.3f}`"
        )
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
