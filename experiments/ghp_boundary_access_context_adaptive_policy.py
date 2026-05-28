#!/usr/bin/env python3
"""Boundary Access context-adaptive rescue under mixed damage and helper quality.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_adaptive_policy as adaptive
import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_helper_quality as helper_quality
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_context_adaptive_policy_outputs"


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


def choose_family(policy_name: str, damage_mode: str, helper_mode: str) -> str:
    if policy_name == "always_fresh":
        return "fresh_echo"
    if policy_name == "always_deep":
        return "deep_trace"
    if policy_name == "always_layered":
        return "layered_recent_deep"
    if policy_name == "adaptive_damage":
        return "fresh_echo" if damage_mode == "missing" else "deep_trace"
    if policy_name == "adaptive_helper":
        return "deep_trace" if helper_mode == "noisy" else "fresh_echo"
    if policy_name == "adaptive_context":
        if helper_mode == "noisy":
            return "deep_trace"
        if damage_mode == "missing":
            return "fresh_echo"
        if damage_mode == "wrong":
            return "layered_recent_deep"
        return "deep_trace"
    raise ValueError(policy_name)


def evaluate_policy(policy: Policy, words: dict[str, str], vocab_index: dict[str, int]) -> dict[str, float | str]:
    word = words["fibonacci"]
    truth = event.loop.base.full_histogram(word, event.loop.base.KMER, vocab_index)
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    identity_scores: list[float] = []
    scene_scores: list[float] = []
    direction_scores: list[float] = []
    helper_counts = {"current": 0, "delayed": 0, "noisy": 0}
    damage_counts = {"missing": 0, "wrong": 0, "overload": 0}

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
            damage_counts[damage_mode] += 1
            helper_counts[helper_mode] += 1

            damaged = adaptive.apply_damage_mode(damage_mode, readable_a)
            family_name = choose_family(policy.name, damage_mode, helper_mode)
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
            repair_scores.append(repair)
            repair_gain_scores.append(max(0.0, repair - masked_self))
            identity_scores.append(event.loop.base.cosine(recovered, deep_trace))
            scene_scores.append(event.loop.base.cosine(recovered, readable_a))
            direction_scores.append(event.loop.base.cosine(recovered, next_readable))
            prev_b = readable_b

    def mean_or_zero(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    total_helper = sum(helper_counts.values()) or 1
    total_damage = sum(damage_counts.values()) or 1
    metrics = {
        "policy": policy.name,
        "label": policy.label,
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "identity_restore": mean_or_zero(identity_scores),
        "scene_restore": mean_or_zero(scene_scores),
        "direction_restore": mean_or_zero(direction_scores),
        "current_share": helper_counts["current"] / total_helper,
        "delayed_share": helper_counts["delayed"] / total_helper,
        "noisy_share": helper_counts["noisy"] / total_helper,
        "missing_share": damage_counts["missing"] / total_damage,
        "wrong_share": damage_counts["wrong"] / total_damage,
        "overload_share": damage_counts["overload"] / total_damage,
    }
    metrics["score_context"] = (
        0.25 * metrics["repair_score"]
        + 0.20 * metrics["repair_gain"]
        + 0.20 * metrics["identity_restore"]
        + 0.20 * metrics["scene_restore"]
        + 0.15 * metrics["direction_restore"]
    )
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
        Policy("adaptive_damage", "Adaptive by damage"),
        Policy("adaptive_helper", "Adaptive by helper"),
        Policy("adaptive_context", "Adaptive by damage + helper"),
    ]

    rows = [evaluate_policy(policy, words, vocab_index) for policy in policies]
    ranked = sorted(rows, key=lambda row: float(row["score_context"]), reverse=True)
    write_csv(rows, OUT / "context_policy_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    best = ranked[0]
    report = f"""# Boundary Access Context-Adaptive Policy

Best policy:
- `{best['policy']}` context score `{float(best['score_context']):.3f}`

Interpretation:
- This mixes damage type and helper quality together.
- If a context-aware policy wins here, then rescue really is multi-factor rather than a single fixed continuity rule.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best policy: {best['policy']} {float(best['score_context']):.3f}")


if __name__ == "__main__":
    main()
