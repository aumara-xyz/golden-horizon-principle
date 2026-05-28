#!/usr/bin/env python3
"""Local-feature switcher for coherence tether vs contradiction scrubber.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from pathlib import Path

import numpy as np

import ghp_boundary_access_channel_toy as base
import ghp_boundary_access_context_adaptive_policy as context_policy
import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_event_fallback as event
import ghp_boundary_access_noise_regime_hardening as hardening
import ghp_boundary_access_wrong_signal_variants as wrong_variants


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_local_switcher_outputs"

TRAIN_SEEDS = [20260526, 20260527, 20260528]
TEST_SEEDS = [20260529, 20260530]
NOISE_LEVELS = [0.20, 0.30, 0.40]
INTERNAL_VARIANTS = ["rolled", "reversed", "permuted"]
COHERENT_VARIANTS = ["cross_family"]
FAMILY_NAMES = ["fibonacci", "generic_ternary"]
FEATURE_NAMES = [
    "damage_helper_cos",
    "damage_wake_cos",
    "damage_deep_cos",
    "helper_wake_cos",
    "helper_deep_cos",
    "damage_helper_overlap",
    "damage_deep_overlap",
    "damage_entropy",
    "helper_entropy",
    "entropy_gap",
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


def build_words() -> dict[str, str]:
    return {family.name: base.generate_word(family.rules, base.TARGET_LENGTH) for family in base.FAMILIES}


def entropy(hist: np.ndarray) -> float:
    return base.entropy_score(hist)


def top_overlap(a: np.ndarray, b: np.ndarray) -> float:
    return base.top_overlap(a, b)


def feature_row(
    damaged: np.ndarray,
    helper: np.ndarray,
    wake: np.ndarray,
    deep_trace: np.ndarray,
) -> np.ndarray:
    values = np.array(
        [
            base.cosine(damaged, helper),
            base.cosine(damaged, wake),
            base.cosine(damaged, deep_trace),
            base.cosine(helper, wake),
            base.cosine(helper, deep_trace),
            top_overlap(damaged, helper),
            top_overlap(damaged, deep_trace),
            entropy(damaged),
            entropy(helper),
            abs(entropy(damaged) - entropy(helper)),
        ],
        dtype=float,
    )
    return values


def collect_events_for_seed(seed: int, words: dict[str, str], vocab_index: dict[str, int]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    old_rng = event.loop.RNG
    event.loop.RNG = np.random.default_rng(seed)
    try:
        for family_name in FAMILY_NAMES:
            word = words[family_name]
            truth = base.full_histogram(word, base.KMER, vocab_index)
            cross_family_name = "generic_ternary" if family_name != "generic_ternary" else "fibonacci"
            cross_truth = base.full_histogram(words[cross_family_name], base.KMER, vocab_index)
            limit = len(word) - base.KMER + 1

            for noise_level in NOISE_LEVELS:
                scenario = {
                    "name": f"uniform_{noise_level:.2f}",
                    "helper_kind": "uniform_mix",
                    "noise_level": noise_level,
                }
                for variant in INTERNAL_VARIANTS + COHERENT_VARIANTS:
                    for _ in range(event.loop.TRIALS):
                        start_a = int(event.loop.RNG.integers(0, limit))
                        start_b = int(event.loop.RNG.integers(0, limit))
                        wake = np.zeros(len(vocab_index), dtype=float)
                        deep_trace = np.zeros(len(vocab_index), dtype=float)
                        frozen_old = np.zeros(len(vocab_index), dtype=float)
                        prev_b = np.zeros(len(vocab_index), dtype=float)
                        wake_history: deque[np.ndarray] = deque(maxlen=groove.MEDIUM_DELAY + 6)

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

                            readable_a = event.loop.normalize(current_a)
                            readable_b = event.loop.normalize(current_b)
                            helper = hardening.helper_view(scenario, readable_b, prev_b, readable_b)

                            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * helper)
                            deep_trace = event.loop.normalize(groove.DEEP_DECAY * deep_trace + (1.0 - groove.DEEP_DECAY) * wake)
                            wake_history.append(wake.copy())
                            if step == groove.FROZEN_STEP:
                                frozen_old = wake.copy()

                            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                                prev_b = readable_b
                                continue

                            damaged = event.loop.normalize(wrong_variants.wrong_signal(variant, readable_a, cross_truth))
                            rows.append(
                                {
                                    "seed": seed,
                                    "family_name": family_name,
                                    "noise_level": noise_level,
                                    "variant": variant,
                                    "label": 1 if variant in COHERENT_VARIANTS else 0,
                                    "features": feature_row(damaged, helper, wake, deep_trace),
                                    "target_family": "fibonacci" if variant in COHERENT_VARIANTS else "generic_ternary",
                                    "helper_truth_cos": base.cosine(helper, truth),
                                    "helper_cross_cos": base.cosine(helper, cross_truth),
                                }
                            )
                            prev_b = readable_b
    finally:
        event.loop.RNG = old_rng
    return rows


def matrix_from_rows(rows: list[dict[str, object]]) -> tuple[np.ndarray, np.ndarray]:
    x = np.vstack([row["features"] for row in rows]).astype(float)
    y = np.array([int(row["label"]) for row in rows], dtype=float)
    return x, y


def fit_linear_probe(train_rows: list[dict[str, object]]) -> tuple[np.ndarray, np.ndarray]:
    x, y = matrix_from_rows(train_rows)
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std[std == 0.0] = 1.0
    x_norm = (x - mean) / std
    x_norm = np.nan_to_num(x_norm, nan=0.0, posinf=0.0, neginf=0.0)
    x_aug = np.hstack([x_norm, np.ones((x_norm.shape[0], 1))])
    weights, _, _, _ = np.linalg.lstsq(x_aug, y, rcond=None)
    return mean, std, weights


def predict_linear_probe(features: np.ndarray, mean: np.ndarray, std: np.ndarray, weights: np.ndarray) -> int:
    x_norm = (features - mean) / std
    x_aug = np.concatenate([x_norm, np.array([1.0])])
    score = float(x_aug @ weights)
    return 1 if score >= 0.5 else 0


def evaluate_switchers(
    rows: list[dict[str, object]],
    mean: np.ndarray,
    std: np.ndarray,
    weights: np.ndarray,
) -> list[dict[str, float | str]]:
    summary: list[dict[str, float | str]] = []
    switchers = {
        "always_fibonacci": lambda row: "fibonacci",
        "always_generic_ternary": lambda row: "generic_ternary",
        "linear_probe": lambda row: "fibonacci"
        if predict_linear_probe(row["features"], mean, std, weights) == 1
        else "generic_ternary",
        "oracle": lambda row: str(row["target_family"]),
    }

    for name, chooser in switchers.items():
        chosen = [chooser(row) for row in rows]
        accuracy = np.mean([choice == row["target_family"] for choice, row in zip(chosen, rows)])
        summary.append(
            {
                "switcher": name,
                "target_family_accuracy": float(accuracy),
            }
        )

    for noise_level in NOISE_LEVELS:
        subset = [row for row in rows if float(row["noise_level"]) == noise_level]
        for name, chooser in switchers.items():
            chosen = [chooser(row) for row in subset]
            accuracy = np.mean([choice == row["target_family"] for choice, row in zip(chosen, subset)])
            summary.append(
                {
                    "switcher": name,
                    "noise_level": noise_level,
                    "target_family_accuracy": float(accuracy),
                }
            )
    return summary


def feature_importance(mean: np.ndarray, std: np.ndarray, weights: np.ndarray) -> list[tuple[str, float]]:
    scaled = np.abs(weights[:-1] / std)
    ranked = sorted(zip(FEATURE_NAMES, scaled.tolist()), key=lambda item: item[1], reverse=True)
    return ranked


def main() -> None:
    ensure_dir(OUT)
    words = build_words()
    vocab = base.collect_vocabulary(words, base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    train_rows: list[dict[str, object]] = []
    test_rows: list[dict[str, object]] = []
    for seed in TRAIN_SEEDS:
        train_rows.extend(collect_events_for_seed(seed, words, vocab_index))
    for seed in TEST_SEEDS:
        test_rows.extend(collect_events_for_seed(seed, words, vocab_index))

    mean, std, weights = fit_linear_probe(train_rows)
    summary = evaluate_switchers(test_rows, mean, std, weights)
    write_csv(summary, OUT / "switcher_summary.csv")

    importances = feature_importance(mean, std, weights)
    feature_rows = [{"feature": name, "importance": value} for name, value in importances]
    write_csv(feature_rows, OUT / "feature_importance.csv")

    overall = {row["switcher"]: row["target_family_accuracy"] for row in summary if "noise_level" not in row}
    lines = [
        "# Boundary Access Local Switcher",
        "",
        f"- train seeds `{TRAIN_SEEDS}`",
        f"- test seeds `{TEST_SEEDS}`",
        "",
        "Overall target-family accuracy:",
        f"- always_fibonacci: `{overall['always_fibonacci']:.3f}`",
        f"- always_generic_ternary: `{overall['always_generic_ternary']:.3f}`",
        f"- linear_probe: `{overall['linear_probe']:.3f}`",
        f"- oracle: `{overall['oracle']:.3f}`",
        "",
        "Top local features:",
    ]
    for name, value in importances[:5]:
        lines.append(f"- {name}: `{value:.4f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
