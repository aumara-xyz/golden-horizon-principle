#!/usr/bin/env python3
"""Integrated Boundary Access harness with both access and repair-switch costs.

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
OUT = ROOT / "ghp_boundary_access_integrated_dual_cost_outputs"

COST_PROFILES = {
    "light_cost": {
        "current": 0.02,
        "high_noise": 0.01,
        "no_helper": 0.0,
        "illegal_truth": 0.08,
    },
    "strict_cheat": {
        "current": 0.02,
        "high_noise": 0.01,
        "no_helper": 0.0,
        "illegal_truth": 0.18,
    },
}

SWITCH_COSTS = [0.0, 0.03]

MODES = [
    boundary_modes.BoundaryMode("current", "Current local access"),
    boundary_modes.BoundaryMode("high_noise", "High-noise local access"),
    boundary_modes.BoundaryMode("no_helper", "No helper access"),
    boundary_modes.BoundaryMode("illegal_truth", "Illegal truth access"),
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


def evaluate_family_mode(
    family_name: str,
    mode: boundary_modes.BoundaryMode,
    switch_cost: float,
    words: dict[str, str],
    vocab_index: dict[str, int],
) -> dict[str, float | str]:
    word = words[family_name]
    truth = base.full_histogram(word, base.KMER, vocab_index)
    access_scores: list[float] = []
    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    identity_scores: list[float] = []
    scene_scores: list[float] = []
    direction_scores: list[float] = []
    switch_paid: list[float] = []

    limit = len(word) - base.KMER + 1
    helper_name_for_policy = "noisy" if "noise" in mode.name else ("current" if mode.name == "illegal_truth" else mode.name)
    damage_modes = ["missing", "wrong", "overload"]

    for _ in range(event.loop.TRIALS):
        start_a = int(event.loop.RNG.integers(0, limit))
        start_b = int(event.loop.RNG.integers(0, limit))
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
            next_a = event.loop.base.histogram_from_positions(
                word,
                event.loop.chunk_positions(len(word), event.loop.CHUNK, start_a + step + 1),
                event.loop.base.KMER,
                vocab_index,
            )

            readable_a = event.loop.normalize(current_a)
            readable_b = event.loop.normalize(current_b)
            next_readable = event.loop.normalize(next_a)
            helper = boundary_modes.helper_from_mode(mode.name, readable_b, prev_b, truth)
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

            penalty = switch_cost if prev_policy_family is not None and policy_family != prev_policy_family else 0.0
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
        "mode": mode.name,
        "switch_cost": switch_cost,
        "access_fidelity": mean_or_zero(access_scores),
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "identity_restore": mean_or_zero(identity_scores),
        "scene_restore": mean_or_zero(scene_scores),
        "direction_restore": mean_or_zero(direction_scores),
        "avg_switch_paid": mean_or_zero(switch_paid),
    }
    metrics["score_raw"] = (
        0.20 * metrics["access_fidelity"]
        + 0.20 * metrics["repair_score"]
        + 0.15 * metrics["repair_gain"]
        + 0.15 * metrics["identity_restore"]
        + 0.15 * metrics["scene_restore"]
        + 0.15 * metrics["direction_restore"]
    )
    return metrics


def main() -> None:
    ensure_dir(OUT)
    words = build_words()
    vocab = base.collect_vocabulary(words, base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    rows = [
        evaluate_family_mode(family.name, mode, switch_cost, words, vocab_index)
        for family in base.FAMILIES
        for mode in MODES
        for switch_cost in SWITCH_COSTS
    ]
    net_rows: list[dict[str, float | str]] = []
    for profile_name, profile in COST_PROFILES.items():
        for row in rows:
            new_row = dict(row)
            mode = str(row["mode"])
            new_row["profile"] = profile_name
            new_row["access_cost"] = profile[mode]
            new_row["score_net"] = float(row["score_raw"]) - float(profile[mode])
            net_rows.append(new_row)

    write_csv(rows, OUT / "dual_cost_raw_metrics.csv")
    write_csv(net_rows, OUT / "dual_cost_net_metrics.csv")

    lines = [
        "# Boundary Access Integrated Dual Cost",
        "",
        "Best family by mode/profile/switch-cost:",
    ]
    for profile_name in COST_PROFILES:
        for switch_cost in SWITCH_COSTS:
            for mode in MODES:
                subset = [
                    row for row in net_rows
                    if row["profile"] == profile_name and row["mode"] == mode.name and float(row["switch_cost"]) == switch_cost
                ]
                best = max(subset, key=lambda row: float(row["score_net"]))
                lines.append(
                    f"- {profile_name} / switch {switch_cost} / {mode.name}: family=`{best['family']}` net=`{float(best['score_net']):.3f}`"
                )
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
