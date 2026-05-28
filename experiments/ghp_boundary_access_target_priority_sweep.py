#!/usr/bin/env python3
"""Boundary Access target-priority sweep for rescue policies.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_context_adaptive_policy as context_policy
import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_target_priority_sweep_outputs"

PRIORITIES = {
    "self_first": (0.45, 0.15, 0.15, 0.15, 0.10),
    "scene_first": (0.15, 0.15, 0.45, 0.15, 0.10),
    "direction_first": (0.15, 0.15, 0.15, 0.45, 0.10),
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


def main() -> None:
    ensure_dir(OUT)
    words = event.loop.build_words()
    vocab = event.loop.base.collect_vocabulary(words, event.loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}
    policies = [
        context_policy.Policy("always_fresh", "Always fresh"),
        context_policy.Policy("always_deep", "Always deep"),
        context_policy.Policy("always_layered", "Always layered"),
        context_policy.Policy("adaptive_damage", "Adaptive by damage"),
        context_policy.Policy("adaptive_helper", "Adaptive by helper"),
        context_policy.Policy("adaptive_context", "Adaptive by damage + helper"),
    ]

    base_rows = [context_policy.evaluate_policy(policy, words, vocab_index) for policy in policies]
    rows: list[dict[str, float | str]] = []
    for priority_name, weights in PRIORITIES.items():
        w_repair, w_gain, w_identity, w_scene, w_direction = weights
        for row in base_rows:
            new_row = dict(row)
            new_row["priority"] = priority_name
            new_row["priority_score"] = (
                w_repair * float(row["repair_score"])
                + w_gain * float(row["repair_gain"])
                + w_identity * float(row["identity_restore"])
                + w_scene * float(row["scene_restore"])
                + w_direction * float(row["direction_restore"])
            )
            rows.append(new_row)

    write_csv(rows, OUT / "priority_metrics.csv")

    lines = [
        "# Boundary Access Target Priority Sweep",
        "",
        "Best policy by priority:",
    ]
    for priority_name in PRIORITIES:
        subset = [row for row in rows if row["priority"] == priority_name]
        best = max(subset, key=lambda row: float(row["priority_score"]))
        lines.append(f"- {priority_name}: `{best['policy']}` `{float(best['priority_score']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
