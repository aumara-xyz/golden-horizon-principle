#!/usr/bin/env python3
"""Boundary Access adaptive rescue policy under mixed damage.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_access_damage_split as damage
import ghp_boundary_access_deep_groove as groove
import ghp_boundary_access_identity_scene_ablation as ablation
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_adaptive_policy_outputs"


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


def choose_payload(
    policy_name: str,
    damage_mode: str,
    wake: np.ndarray,
    wake_history: deque[np.ndarray],
    deep_trace: np.ndarray,
    frozen_old: np.ndarray,
    vocab_size: int,
) -> np.ndarray:
    if policy_name == "no_return":
        family_name = "no_return"
    elif policy_name == "always_fresh":
        family_name = "fresh_echo"
    elif policy_name == "always_deep":
        family_name = "deep_trace"
    elif policy_name == "always_layered":
        family_name = "layered_recent_deep"
    elif policy_name == "adaptive_damage":
        family_name = "fresh_echo" if damage_mode == "missing" else "deep_trace"
    elif policy_name == "adaptive_balanced":
        if damage_mode == "missing":
            family_name = "fresh_echo"
        elif damage_mode == "wrong":
            family_name = "layered_recent_deep"
        else:
            family_name = "deep_trace"
    else:
        raise ValueError(policy_name)
    return groove.groove_payload(family_name, wake, wake_history, deep_trace, frozen_old, vocab_size)


def apply_damage_mode(damage_mode: str, readable_a: np.ndarray) -> np.ndarray:
    wrong_hist = damage.make_wrong_signal(readable_a)
    if damage_mode == "missing":
        return event.apply_damage(readable_a, event.MASK_KEEP_DAMAGE)
    if damage_mode == "wrong":
        return wrong_hist
    if damage_mode == "overload":
        return damage.make_overload(readable_a, wrong_hist)
    raise ValueError(damage_mode)


def evaluate_policy(policy: Policy, words: dict[str, str], vocab_index: dict[str, int]) -> dict[str, float | str]:
    word = words["fibonacci"]
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    identity_scores: list[float] = []
    scene_scores: list[float] = []
    direction_scores: list[float] = []
    mode_counts = {"missing": 0, "wrong": 0, "overload": 0}

    limit = len(word) - event.loop.base.KMER + 1
    damage_modes = ["missing", "wrong", "overload"]

    for _ in range(event.loop.TRIALS):
        start_a = int(event.loop.RNG.integers(0, limit))
        start_b = int(event.loop.RNG.integers(0, limit))

        wake = np.zeros(len(vocab_index), dtype=float)
        deep_trace = np.zeros(len(vocab_index), dtype=float)
        frozen_old = np.zeros(len(vocab_index), dtype=float)
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
                continue

            damage_mode = damage_modes[int(event.loop.RNG.integers(0, len(damage_modes)))]
            mode_counts[damage_mode] += 1
            damaged = apply_damage_mode(damage_mode, readable_a)

            payload = choose_payload(
                policy.name,
                damage_mode,
                wake,
                wake_history,
                deep_trace,
                frozen_old,
                len(vocab_index),
            )
            rescue = event.trigger_scale("event", event.damage_score(damaged, readable_a), payload) * payload
            recovered = ablation.recover_ablation(damaged, readable_b, rescue)

            masked_self = event.loop.base.cosine(damaged, readable_a)
            repair = event.loop.base.cosine(recovered, readable_a)
            repair_scores.append(repair)
            repair_gain_scores.append(max(0.0, repair - masked_self))
            identity_scores.append(event.loop.base.cosine(recovered, deep_trace))
            scene_scores.append(event.loop.base.cosine(recovered, readable_a))
            direction_scores.append(event.loop.base.cosine(recovered, next_readable))

    def mean_or_zero(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    total_modes = sum(mode_counts.values()) or 1
    metrics = {
        "policy": policy.name,
        "label": policy.label,
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "identity_restore": mean_or_zero(identity_scores),
        "scene_restore": mean_or_zero(scene_scores),
        "direction_restore": mean_or_zero(direction_scores),
        "missing_share": mode_counts["missing"] / total_modes,
        "wrong_share": mode_counts["wrong"] / total_modes,
        "overload_share": mode_counts["overload"] / total_modes,
    }
    metrics["score_mixed"] = (
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
        Policy("no_return", "No return"),
        Policy("always_fresh", "Always fresh"),
        Policy("always_deep", "Always deep"),
        Policy("always_layered", "Always layered"),
        Policy("adaptive_damage", "Adaptive by damage"),
        Policy("adaptive_balanced", "Adaptive balanced"),
    ]

    rows = [evaluate_policy(policy, words, vocab_index) for policy in policies]
    ranked = sorted(rows, key=lambda row: float(row["score_mixed"]), reverse=True)
    write_csv(rows, OUT / "policy_metrics.csv")
    write_csv(ranked, OUT / "ranking.csv")

    best = ranked[0]
    report = f"""# Boundary Access Adaptive Policy

Best policy:
- `{best['policy']}` mixed score `{float(best['score_mixed']):.3f}`

Interpretation:
- This tests whether an explicit rescue policy keyed to damage type beats any one fixed rescue family in a mixed-damage environment.
- If adaptive policies win, then context-sensitive rescue is carrying real signal.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best policy: {best['policy']} {float(best['score_mixed']):.3f}")


if __name__ == "__main__":
    main()
