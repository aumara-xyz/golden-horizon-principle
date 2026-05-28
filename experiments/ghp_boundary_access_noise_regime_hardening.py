#!/usr/bin/env python3
"""Hardening pass for the Boundary Access noise-regime split.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from pathlib import Path

import numpy as np

import ghp_boundary_access_boundary_modes as boundary_modes
import ghp_boundary_access_channel_toy as base
import ghp_boundary_access_context_adaptive_policy as context_policy
import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_noise_regime_hardening_outputs"

SCENARIOS = [
    {"name": "clean_current", "helper_kind": "current", "noise_level": 0.0},
    {"name": "uniform_mix_low", "helper_kind": "uniform_mix", "noise_level": 0.15},
    {"name": "uniform_mix_mid", "helper_kind": "uniform_mix", "noise_level": 0.30},
    {"name": "uniform_mix_high", "helper_kind": "uniform_mix", "noise_level": 0.55},
    {"name": "gaussian_mix_mid", "helper_kind": "gaussian_mix", "noise_level": 0.30},
    {"name": "delayed_uniform_mid", "helper_kind": "delayed_uniform", "noise_level": 0.30},
    {"name": "permute_mix_mid", "helper_kind": "permute_mix", "noise_level": 0.30},
    {"name": "cross_family_mid", "helper_kind": "cross_family", "noise_level": 0.30},
]

SCORE_VIEWS = {
    "balanced": {
        "access_fidelity": 0.20,
        "repair_score": 0.20,
        "repair_gain": 0.15,
        "identity_restore": 0.15,
        "scene_restore": 0.15,
        "direction_restore": 0.15,
    },
    "access_heavy": {
        "access_fidelity": 0.34,
        "repair_score": 0.18,
        "repair_gain": 0.12,
        "identity_restore": 0.12,
        "scene_restore": 0.14,
        "direction_restore": 0.10,
    },
    "repair_heavy": {
        "access_fidelity": 0.12,
        "repair_score": 0.28,
        "repair_gain": 0.22,
        "identity_restore": 0.14,
        "scene_restore": 0.14,
        "direction_restore": 0.10,
    },
    "identity_heavy": {
        "access_fidelity": 0.12,
        "repair_score": 0.16,
        "repair_gain": 0.12,
        "identity_restore": 0.28,
        "scene_restore": 0.16,
        "direction_restore": 0.16,
    },
}

ACCESS_COST = 0.02
SWITCH_COST = 0.03


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


def normalize(vec: np.ndarray) -> np.ndarray:
    total = float(vec.sum())
    return vec / total if total else vec


def permuted_view(readable_b: np.ndarray) -> np.ndarray:
    permuted = readable_b[event.loop.RNG.permutation(len(readable_b))]
    return normalize(permuted)


def gaussian_view(readable_b: np.ndarray, noise_level: float) -> np.ndarray:
    perturb = event.loop.RNG.normal(loc=0.0, scale=noise_level, size=len(readable_b))
    mixed = np.clip(readable_b + perturb, 0.0, None)
    return normalize(mixed)


def helper_view(
    scenario: dict[str, float | str],
    readable_b: np.ndarray,
    prev_b: np.ndarray,
    cross_family_b: np.ndarray,
) -> np.ndarray:
    kind = str(scenario["helper_kind"])
    level = float(scenario["noise_level"])
    if kind == "current":
        return readable_b
    if kind == "uniform_mix":
        noise = event.loop.RNG.random(len(readable_b))
        mixed = (1.0 - level) * readable_b + level * noise
        return normalize(mixed)
    if kind == "gaussian_mix":
        mixed = (1.0 - level) * readable_b + level * gaussian_view(readable_b, level)
        return normalize(mixed)
    if kind == "delayed_uniform":
        noise = event.loop.RNG.random(len(readable_b))
        mixed = 0.5 * prev_b + 0.5 * normalize((1.0 - level) * readable_b + level * noise)
        return normalize(mixed)
    if kind == "permute_mix":
        mixed = (1.0 - level) * readable_b + level * permuted_view(readable_b)
        return normalize(mixed)
    if kind == "cross_family":
        mixed = (1.0 - level) * readable_b + level * cross_family_b
        return normalize(mixed)
    raise ValueError(kind)


def score_with_weights(metrics: dict[str, float | str], weights: dict[str, float]) -> float:
    return sum(float(metrics[name]) * weight for name, weight in weights.items())


def evaluate_family_scenario(
    family_name: str,
    scenario: dict[str, float | str],
    words: dict[str, str],
    vocab_index: dict[str, int],
) -> dict[str, float | str]:
    word = words[family_name]
    cross_family_name = "generic_ternary" if family_name != "generic_ternary" else "fibonacci"
    cross_word = words[cross_family_name]
    truth = base.full_histogram(word, base.KMER, vocab_index)

    access_scores: list[float] = []
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    identity_scores: list[float] = []
    scene_scores: list[float] = []
    direction_scores: list[float] = []
    switch_paid: list[float] = []

    limit = len(word) - base.KMER + 1
    cross_limit = len(cross_word) - base.KMER + 1
    damage_modes = ["missing", "wrong", "overload"]
    helper_name_for_policy = "noisy" if scenario["name"] != "clean_current" else "current"

    for _ in range(event.loop.TRIALS):
        start_a = int(event.loop.RNG.integers(0, limit))
        start_b = int(event.loop.RNG.integers(0, limit))
        cross_start_b = int(event.loop.RNG.integers(0, cross_limit))
        wake = np.zeros(len(vocab_index), dtype=float)
        deep_trace = np.zeros(len(vocab_index), dtype=float)
        frozen_old = np.zeros(len(vocab_index), dtype=float)
        prev_b = np.zeros(len(vocab_index), dtype=float)
        prev_policy_family: str | None = None
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
            cross_b = event.loop.base.histogram_from_positions(
                cross_word,
                event.loop.chunk_positions(len(cross_word), event.loop.SECOND_CHUNK, cross_start_b + 2 * step),
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
            cross_family_b = event.loop.normalize(cross_b)
            next_readable = event.loop.normalize(next_a)
            helper = helper_view(scenario, readable_b, prev_b, cross_family_b)
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

            damage_mode = damage_modes[int(event.loop.RNG.integers(0, len(damage_modes)))]
            damaged = context_policy.adaptive.apply_damage_mode(damage_mode, readable_a)
            policy_family = context_policy.choose_family("adaptive_context", damage_mode, helper_name_for_policy)
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
        "scenario": str(scenario["name"]),
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


def summarize_winners(rows: list[dict[str, float | str]]) -> list[str]:
    lines = [
        "# Boundary Access Noise Regime Hardening",
        "",
        f"- access cost `{ACCESS_COST}`",
        f"- switch cost `{SWITCH_COST}`",
        "",
        "Best family by scenario and score view:",
    ]
    for scenario in SCENARIOS:
        scenario_name = str(scenario["name"])
        subset = [row for row in rows if row["scenario"] == scenario_name]
        winner_bits: list[str] = []
        for view_name in SCORE_VIEWS:
            best = max(subset, key=lambda row: float(row[f"score_{view_name}"]))
            winner_bits.append(f"{view_name}=`{best['family']}`")
        lines.append(f"- {scenario_name}: " + ", ".join(winner_bits))
    return lines


def main() -> None:
    ensure_dir(OUT)
    words = build_words()
    vocab = base.collect_vocabulary(words, base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    rows = [
        evaluate_family_scenario(family.name, scenario, words, vocab_index)
        for scenario in SCENARIOS
        for family in base.FAMILIES
    ]
    write_csv(rows, OUT / "noise_regime_metrics.csv")
    write_text(OUT / "report.md", "\n".join(summarize_winners(rows)) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
