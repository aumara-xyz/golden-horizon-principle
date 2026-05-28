#!/usr/bin/env python3
"""Boundary Access Channel identity vs scene vs direction rescue split.

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
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_identity_scene_split_outputs"


@dataclass(frozen=True)
class RescueFamily:
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


def evaluate_damage_and_target(
    family: RescueFamily,
    damage_mode: str,
    words: dict[str, str],
    vocab_index: dict[str, int],
) -> dict[str, float | str]:
    word = words["fibonacci"]
    truth = event.loop.base.full_histogram(word, event.loop.base.KMER, vocab_index)

    repair_scores: list[float] = []
    repair_gain_scores: list[float] = []
    identity_scores: list[float] = []
    scene_scores: list[float] = []
    direction_scores: list[float] = []

    limit = len(word) - event.loop.base.KMER + 1

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

            wrong_hist = damage.make_wrong_signal(readable_a)
            if damage_mode == "missing":
                damaged = event.apply_damage(readable_a, event.MASK_KEEP_DAMAGE)
            elif damage_mode == "wrong":
                damaged = wrong_hist
            elif damage_mode == "overload":
                damaged = damage.make_overload(readable_a, wrong_hist)
            else:
                raise ValueError(damage_mode)

            masked_only = event.loop.base.cosine(damaged, truth)
            damage_level = event.damage_score(damaged, truth)
            payload = groove.groove_payload(
                family.name,
                wake,
                wake_history,
                deep_trace,
                frozen_old,
                len(vocab_index),
            )
            rescue = event.trigger_scale("event", damage_level, payload) * payload
            recovered = event.loop.recover_from_sources(damaged, readable_b, event.FALLBACK_GAIN * rescue)

            recovered_score = event.loop.base.cosine(recovered, truth)
            repair_scores.append(recovered_score)
            repair_gain_scores.append(max(0.0, recovered_score - masked_only))
            identity_scores.append(event.loop.base.cosine(recovered, deep_trace))
            scene_scores.append(event.loop.base.cosine(recovered, readable_a))
            direction_scores.append(event.loop.base.cosine(recovered, next_readable))

    def mean_or_zero(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    metrics = {
        "damage_mode": damage_mode,
        "family": family.name,
        "label": family.label,
        "repair_score": mean_or_zero(repair_scores),
        "repair_gain": mean_or_zero(repair_gain_scores),
        "identity_restore": mean_or_zero(identity_scores),
        "scene_restore": mean_or_zero(scene_scores),
        "direction_restore": mean_or_zero(direction_scores),
    }
    metrics["score_self"] = 0.50 * metrics["identity_restore"] + 0.30 * metrics["repair_gain"] + 0.20 * metrics["repair_score"]
    metrics["score_scene"] = 0.50 * metrics["scene_restore"] + 0.30 * metrics["repair_gain"] + 0.20 * metrics["repair_score"]
    metrics["score_direction"] = 0.50 * metrics["direction_restore"] + 0.30 * metrics["repair_gain"] + 0.20 * metrics["repair_score"]
    return metrics


def winner(rows: list[dict[str, float | str]], metric: str) -> dict[str, float | str]:
    return max(rows, key=lambda row: float(row[metric]))


def main() -> None:
    ensure_dir(OUT)
    words = event.loop.build_words()
    vocab = event.loop.base.collect_vocabulary(words, event.loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    families = [
        RescueFamily("no_return", "No return"),
        RescueFamily("fresh_echo", "Fresh echo"),
        RescueFamily("deep_trace", "Deep trace"),
        RescueFamily("layered_recent_deep", "Layered recent + deep"),
    ]
    damage_modes = ["missing", "wrong", "overload"]

    rows = [
        evaluate_damage_and_target(family, damage_mode, words, vocab_index)
        for damage_mode in damage_modes
        for family in families
    ]
    write_csv(rows, OUT / "identity_scene_metrics.csv")

    report_lines = ["# Boundary Access Identity vs Scene vs Direction", "", "Winners:"]
    for damage_mode in damage_modes:
        subset = [row for row in rows if row["damage_mode"] == damage_mode]
        self_win = winner(subset, "score_self")
        scene_win = winner(subset, "score_scene")
        direction_win = winner(subset, "score_direction")
        report_lines.extend(
            [
                f"- {damage_mode} / self: `{self_win['family']}` `{float(self_win['score_self']):.3f}`",
                f"- {damage_mode} / scene: `{scene_win['family']}` `{float(scene_win['score_scene']):.3f}`",
                f"- {damage_mode} / direction: `{direction_win['family']}` `{float(direction_win['score_direction']):.3f}`",
            ]
        )
    report_lines.extend(
        [
            "",
            "Interpretation:",
            "- This asks what the rescue is really preserving after damage.",
            "- If self, scene, and direction choose different winners, then repair has multiple jobs instead of one generic continuity rule.",
        ]
    )
    write_text(OUT / "report.md", "\n".join(report_lines) + "\n")
    print(f"files created: {OUT}")
    for damage_mode in damage_modes:
        subset = [row for row in rows if row["damage_mode"] == damage_mode]
        print(
            f"{damage_mode}: "
            f"self={winner(subset, 'score_self')['family']} "
            f"scene={winner(subset, 'score_scene')['family']} "
            f"direction={winner(subset, 'score_direction')['family']}"
        )


if __name__ == "__main__":
    main()
