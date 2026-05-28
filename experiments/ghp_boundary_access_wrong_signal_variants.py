#!/usr/bin/env python3
"""Uniform-smear crossover across multiple wrong-signal constructions.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from pathlib import Path

import numpy as np

import ghp_boundary_access_channel_toy as base
import ghp_boundary_access_context_adaptive_policy as context_policy
import ghp_boundary_access_damage_split as damage_split
import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_event_fallback as event
import ghp_boundary_access_noise_regime_hardening as hardening


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_wrong_signal_variants_outputs"

NOISE_LEVELS = [0.20, 0.30, 0.40]
FAMILIES = ["fibonacci", "generic_ternary"]
WRONG_VARIANTS = ["rolled", "reversed", "permuted", "cross_family"]
ACCESS_COST = 0.02
SWITCH_COST = 0.03

SCORE_VIEWS = {
    "balanced": {
        "access_fidelity": 0.20,
        "repair_score": 0.20,
        "repair_gain": 0.15,
        "identity_restore": 0.15,
        "scene_restore": 0.15,
        "direction_restore": 0.15,
    },
    "repair_heavy": {
        "access_fidelity": 0.12,
        "repair_score": 0.28,
        "repair_gain": 0.22,
        "identity_restore": 0.14,
        "scene_restore": 0.14,
        "direction_restore": 0.10,
    },
}


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


def score_with_weights(metrics: dict[str, float | str], weights: dict[str, float]) -> float:
    return sum(float(metrics[name]) * weight for name, weight in weights.items())


def wrong_signal(
    variant: str,
    readable_a: np.ndarray,
    cross_family_truth: np.ndarray,
) -> np.ndarray:
    if variant == "rolled":
        return damage_split.make_wrong_signal(readable_a)
    if variant == "reversed":
        return readable_a[::-1].copy()
    if variant == "permuted":
        return readable_a[event.loop.RNG.permutation(len(readable_a))]
    if variant == "cross_family":
        return cross_family_truth
    raise ValueError(variant)


def evaluate_family_variant(
    family_name: str,
    noise_level: float,
    variant: str,
    words: dict[str, str],
    vocab_index: dict[str, int],
) -> dict[str, float | str]:
    word = words[family_name]
    cross_family_name = "generic_ternary" if family_name != "generic_ternary" else "fibonacci"
    cross_truth = base.full_histogram(words[cross_family_name], base.KMER, vocab_index)
    truth = base.full_histogram(word, base.KMER, vocab_index)
    scenario = {
        "name": f"uniform_{noise_level:.2f}",
        "helper_kind": "uniform_mix",
        "noise_level": noise_level,
    }

    access_scores: list[float] = []
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    identity_scores: list[float] = []
    scene_scores: list[float] = []
    direction_scores: list[float] = []
    switch_paid: list[float] = []

    limit = len(word) - base.KMER + 1
    prev_policy_family: str | None

    for _ in range(event.loop.TRIALS):
        start_a = int(event.loop.RNG.integers(0, limit))
        start_b = int(event.loop.RNG.integers(0, limit))
        wake = np.zeros(len(vocab_index), dtype=float)
        deep_trace = np.zeros(len(vocab_index), dtype=float)
        frozen_old = np.zeros(len(vocab_index), dtype=float)
        prev_b = np.zeros(len(vocab_index), dtype=float)
        prev_policy_family = None
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
            next_a = event.loop.base.histogram_from_positions(
                word,
                event.loop.chunk_positions(len(word), event.loop.CHUNK, start_a + step + 1),
                event.loop.base.KMER,
                vocab_index,
            )

            readable_a = event.loop.normalize(current_a)
            readable_b = event.loop.normalize(current_b)
            next_readable = event.loop.normalize(next_a)
            helper = hardening.helper_view(scenario, readable_b, prev_b, readable_b)
            combined = event.loop.normalize(readable_a + helper)
            access_scores.append(base.cosine(combined, truth))

            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * helper)
            deep_trace = event.loop.normalize(groove.DEEP_DECAY * deep_trace + (1.0 - groove.DEEP_DECAY) * wake)
            wake_history.append(wake.copy())
            if step == groove.FROZEN_STEP:
                frozen_old = wake.copy()

            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                prev_b = readable_b
                continue

            damaged = event.loop.normalize(wrong_signal(variant, readable_a, cross_truth))
            policy_family = context_policy.choose_family("adaptive_context", "wrong", "noisy")
            payload = groove.groove_payload(
                policy_family,
                wake,
                wake_history,
                deep_trace,
                frozen_old,
                len(vocab_index),
            )
            rescue = event.trigger_scale("event", event.damage_score(damaged, readable_a), payload) * payload
            recovered = event.loop.normalize(0.34 * damaged + 0.33 * helper + 0.33 * rescue)

            penalty = SWITCH_COST if prev_policy_family is not None and policy_family != prev_policy_family else 0.0
            prev_policy_family = policy_family
            switch_paid.append(penalty)

            masked_self = base.cosine(damaged, readable_a)
            repair = max(0.0, base.cosine(recovered, readable_a) - penalty)
            repair_scores.append(repair)
            repair_gain_scores.append(max(0.0, repair - masked_self))
            identity_scores.append(max(0.0, base.cosine(recovered, deep_trace) - penalty))
            scene_scores.append(max(0.0, base.cosine(recovered, readable_a) - penalty))
            direction_scores.append(max(0.0, base.cosine(recovered, next_readable) - penalty))
            prev_b = readable_b

    def mean_or_zero(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    metrics = {
        "family": family_name,
        "noise_level": noise_level,
        "wrong_variant": variant,
        "access_fidelity": mean_or_zero(access_scores),
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "identity_restore": mean_or_zero(identity_scores),
        "scene_restore": mean_or_zero(scene_scores),
        "direction_restore": mean_or_zero(direction_scores),
        "avg_switch_paid": mean_or_zero(switch_paid),
    }
    for view_name, weights in SCORE_VIEWS.items():
        metrics[f"score_{view_name}"] = score_with_weights(metrics, weights) - ACCESS_COST
    return metrics


def main() -> None:
    ensure_dir(OUT)
    words = build_words()
    vocab = base.collect_vocabulary(words, base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    rows = [
        evaluate_family_variant(family_name, noise_level, variant, words, vocab_index)
        for noise_level in NOISE_LEVELS
        for variant in WRONG_VARIANTS
        for family_name in FAMILIES
    ]
    write_csv(rows, OUT / "wrong_signal_variant_metrics.csv")

    lines = [
        "# Boundary Access Wrong Signal Variants",
        "",
        f"- access cost `{ACCESS_COST}`",
        f"- switch cost `{SWITCH_COST}`",
        "",
        "Winner by noise, wrong-signal variant, and score view:",
    ]
    for noise_level in NOISE_LEVELS:
        for variant in WRONG_VARIANTS:
            subset = [
                row for row in rows
                if float(row["noise_level"]) == noise_level and row["wrong_variant"] == variant
            ]
            bits = []
            for view_name in SCORE_VIEWS:
                best = max(subset, key=lambda row: float(row[f"score_{view_name}"]))
                bits.append(f"{view_name}=`{best['family']}`")
            lines.append(f"- noise `{noise_level}` / {variant}: " + ", ".join(bits))
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
