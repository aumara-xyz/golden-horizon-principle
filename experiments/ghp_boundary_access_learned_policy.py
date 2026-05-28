#!/usr/bin/env python3
"""Boundary Access learned rescue policy under mixed context.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_context_adaptive_policy as context_policy
import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_helper_quality as helper_quality
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_learned_policy_outputs"

LEARNED_ACTIONS = ["fresh_echo", "deep_trace", "layered_recent_deep"]
EPSILON = 0.12


@dataclass(frozen=True)
class Policy:
    name: str
    label: str


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


def select_learned_action(
    estimates: dict[tuple[str, str], dict[str, float]],
    counts: dict[tuple[str, str], dict[str, int]],
    key: tuple[str, str],
) -> str:
    if float(event.loop.RNG.random()) < EPSILON:
        return LEARNED_ACTIONS[int(event.loop.RNG.integers(0, len(LEARNED_ACTIONS)))]
    action_scores = estimates[key]
    action_counts = counts[key]
    unseen = [action for action in LEARNED_ACTIONS if action_counts[action] == 0]
    if unseen:
        return unseen[0]
    return max(LEARNED_ACTIONS, key=lambda action: action_scores[action])


def choose_family(
    policy_name: str,
    damage_mode: str,
    helper_mode: str,
    estimates: dict[tuple[str, str], dict[str, float]],
    counts: dict[tuple[str, str], dict[str, int]],
) -> str:
    if policy_name == "always_fresh":
        return "fresh_echo"
    if policy_name == "always_deep":
        return "deep_trace"
    if policy_name == "always_layered":
        return "layered_recent_deep"
    if policy_name == "adaptive_context":
        return context_policy.choose_family("adaptive_context", damage_mode, helper_mode)
    if policy_name == "learned_context":
        return select_learned_action(estimates, counts, (damage_mode, helper_mode))
    raise ValueError(policy_name)


def evaluate_policy(policy: Policy, words: dict[str, str], vocab_index: dict[str, int]) -> dict[str, float | str]:
    word = words["fibonacci"]
    truth = event.loop.base.full_histogram(word, event.loop.base.KMER, vocab_index)
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    identity_scores: list[float] = []
    scene_scores: list[float] = []
    direction_scores: list[float] = []
    learned_reward = defaultdict(lambda: {action: 0.0 for action in LEARNED_ACTIONS})
    learned_counts = defaultdict(lambda: {action: 0 for action in LEARNED_ACTIONS})

    limit = len(word) - event.loop.base.KMER + 1
    helper_modes = ["current", "delayed", "noisy"]
    damage_modes = ["missing", "wrong", "overload"]

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
            next_a = event.loop.base.histogram_from_positions(
                word,
                event.loop.chunk_positions(len(word), event.loop.CHUNK, start_a + step + 1),
                event.loop.base.KMER,
                vocab_index,
            )

            readable_a = event.loop.normalize(current_a)
            readable_b = event.loop.normalize(current_b)
            next_readable = event.loop.normalize(next_a)

            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * readable_b)
            deep_trace = event.loop.normalize(groove.DEEP_DECAY * deep_trace + (1.0 - groove.DEEP_DECAY) * wake)
            wake_history.append(wake.copy())
            if step == groove.FROZEN_STEP:
                frozen_old = wake.copy()

            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                prev_b = readable_b
                continue

            damage_mode = damage_modes[int(event.loop.RNG.integers(0, len(damage_modes)))]
            helper_mode = helper_modes[int(event.loop.RNG.integers(0, len(helper_modes)))]
            damaged = context_policy.adaptive.apply_damage_mode(damage_mode, readable_a)
            family_name = choose_family(policy.name, damage_mode, helper_mode, learned_reward, learned_counts)
            payload = groove.groove_payload(
                family_name,
                wake,
                wake_history,
                deep_trace,
                frozen_old,
                len(vocab_index),
            )
            rescue = event.trigger_scale("event", event.damage_score(damaged, readable_a), payload) * payload
            helper = helper_quality.helper_view(helper_mode, readable_b, prev_b, truth)
            recovered = event.loop.normalize(0.34 * damaged + 0.33 * helper + 0.33 * rescue)

            masked_self = event.loop.base.cosine(damaged, readable_a)
            repair = event.loop.base.cosine(recovered, readable_a)
            gain = max(0.0, repair - masked_self)
            identity = event.loop.base.cosine(recovered, deep_trace)
            scene = event.loop.base.cosine(recovered, readable_a)
            direction = event.loop.base.cosine(recovered, next_readable)

            repair_scores.append(repair)
            repair_gain_scores.append(gain)
            identity_scores.append(identity)
            scene_scores.append(scene)
            direction_scores.append(direction)

            if policy.name == "learned_context":
                reward = 0.30 * repair + 0.25 * gain + 0.20 * identity + 0.15 * scene + 0.10 * direction
                key = (damage_mode, helper_mode)
                learned_counts[key][family_name] += 1
                count = learned_counts[key][family_name]
                current = learned_reward[key][family_name]
                learned_reward[key][family_name] = current + (reward - current) / count

            prev_b = readable_b

    def mean_or_zero(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    metrics = {
        "policy": policy.name,
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "identity_restore": mean_or_zero(identity_scores),
        "scene_restore": mean_or_zero(scene_scores),
        "direction_restore": mean_or_zero(direction_scores),
    }
    metrics["score_learned"] = (
        0.25 * metrics["repair_score"]
        + 0.20 * metrics["repair_gain"]
        + 0.20 * metrics["identity_restore"]
        + 0.20 * metrics["scene_restore"]
        + 0.15 * metrics["direction_restore"]
    )
    if policy.name == "learned_context":
        summary_parts: list[str] = []
        for key in sorted(learned_reward):
            best = max(LEARNED_ACTIONS, key=lambda action: learned_reward[key][action])
            summary_parts.append(f"{key[0]}/{key[1]}->{best}")
        metrics["learned_map"] = ";".join(summary_parts)
    return metrics


def main() -> None:
    ensure_dir(OUT)
    words = event.loop.build_words()
    vocab = event.loop.base.collect_vocabulary(words, event.loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    policies = [
        Policy("always_fresh", "Always fresh"),
        Policy("always_deep", "Always deep"),
        Policy("always_layered", "Always layered"),
        Policy("adaptive_context", "Adaptive context"),
        Policy("learned_context", "Learned context"),
    ]

    rows = [evaluate_policy(policy, words, vocab_index) for policy in policies]
    ranked = sorted(rows, key=lambda row: float(row["score_learned"]), reverse=True)
    write_csv(rows, OUT / "learned_policy_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    best = ranked[0]
    learned_row = next(row for row in rows if row["policy"] == "learned_context")
    report = f"""# Boundary Access Learned Policy

Best policy:
- `{best['policy']}` learned score `{float(best['score_learned']):.3f}`

Learned map:
- `{learned_row.get('learned_map', '')}`

Interpretation:
- This tests whether online contextual learning can recover a better rescue map than hand-written routing.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
