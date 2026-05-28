#!/usr/bin/env python3
"""Boundary Access helper-gain sweep for identity/scene rescue split.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_identity_scene_ablation as ablation
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_identity_scene_helper_sweep_outputs"

HELPER_GAINS = [0.0, 0.12, 0.25, 0.40]
TOTAL_SIDE_GAIN = 0.66


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


def winner(rows: list[dict[str, float | str]], metric: str) -> dict[str, float | str]:
    return max(rows, key=lambda row: float(row[metric]))


def main() -> None:
    ensure_dir(OUT)
    words = event.loop.build_words()
    vocab = event.loop.base.collect_vocabulary(words, event.loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    families = [
        ablation.RescueFamily("fresh_echo", "Fresh echo"),
        ablation.RescueFamily("deep_trace", "Deep trace"),
        ablation.RescueFamily("layered_recent_deep", "Layered recent + deep"),
    ]
    damage_modes = ["missing", "wrong", "overload"]

    old_trials = event.loop.TRIALS
    event.loop.TRIALS = 16
    rows: list[dict[str, float | str]] = []

    for helper_gain in HELPER_GAINS:
        ablation.HELPER_GAIN = helper_gain
        ablation.RESCUE_GAIN = TOTAL_SIDE_GAIN - helper_gain
        for damage_mode in damage_modes:
            metrics = [
                ablation.evaluate_family(family, damage_mode, words, vocab_index)
                for family in families
            ]
            self_win = winner(metrics, "score_self")
            scene_win = winner(metrics, "score_scene")
            direction_win = winner(metrics, "score_direction")
            rows.append(
                {
                    "helper_gain": helper_gain,
                    "rescue_gain": ablation.RESCUE_GAIN,
                    "damage_mode": damage_mode,
                    "self_winner": self_win["family"],
                    "scene_winner": scene_win["family"],
                    "direction_winner": direction_win["family"],
                    "self_score": float(self_win["score_self"]),
                    "scene_score": float(scene_win["score_scene"]),
                    "direction_score": float(direction_win["score_direction"]),
                }
            )

    event.loop.TRIALS = old_trials
    write_csv(rows, OUT / "helper_sweep.csv")

    lines = [
        "# Boundary Access Identity/Scene Helper Sweep",
        "",
        f"- helper gains `{HELPER_GAINS}`",
        f"- total side gain `{TOTAL_SIDE_GAIN}`",
        "",
        "Interpretation:",
        "- This asks whether the self-vs-scene split is robust or just a helper-channel weighting artifact.",
        "- If winners change as helper gain moves, then rescue target is context-sensitive rather than fixed.",
        "",
        "Winner summary:",
    ]
    for row in rows:
        lines.append(
            f"- helper `{row['helper_gain']}` / {row['damage_mode']}: "
            f"self=`{row['self_winner']}` scene=`{row['scene_winner']}` direction=`{row['direction_winner']}`"
        )
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")
    print("rows:", len(rows))


if __name__ == "__main__":
    main()
