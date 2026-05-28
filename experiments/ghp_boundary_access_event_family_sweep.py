#!/usr/bin/env python3
"""Sweep event-fallback families across damage regimes.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_event_family_sweep_outputs"

DAMAGE_KEEPS = [0.06, 0.10, 0.16]
DAMAGE_PROBS = [0.12, 0.22, 0.34]
TRIGGER_THRESHOLDS = [0.20, 0.28, 0.40]


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

    families = [
        event.FallbackFamily("no_return", "fibonacci", "none", "none", "No return"),
        event.FallbackFamily("always_fibonacci", "fibonacci", "fibonacci", "always", "Always Fibonacci fallback"),
        event.FallbackFamily("event_fibonacci", "fibonacci", "fibonacci", "event", "Event Fibonacci fallback"),
        event.FallbackFamily("event_soft_fibonacci", "fibonacci", "fibonacci", "event_soft", "Event-soft Fibonacci fallback"),
        event.FallbackFamily("event_binary", "fibonacci", "binary", "event", "Event binary fallback"),
        event.FallbackFamily("event_tribonacci", "fibonacci", "tribonacci", "event", "Event tribonacci fallback"),
        event.FallbackFamily("event_random", "fibonacci", "random", "event", "Event random fallback"),
        event.FallbackFamily("event_stale", "fibonacci", "stale", "event", "Event stale fallback"),
    ]

    original = (event.MASK_KEEP_DAMAGE, event.DAMAGE_PROB, event.DAMAGE_TRIGGER_THRESHOLD)
    rows: list[dict[str, float | str]] = []
    core_wins: Counter[str] = Counter()
    event_wins: Counter[str] = Counter()
    try:
        for damage_keep in DAMAGE_KEEPS:
            for damage_prob in DAMAGE_PROBS:
                for trigger_threshold in TRIGGER_THRESHOLDS:
                    event.MASK_KEEP_DAMAGE = damage_keep
                    event.DAMAGE_PROB = damage_prob
                    event.DAMAGE_TRIGGER_THRESHOLD = trigger_threshold

                    metrics = [event.evaluate_family(family, words, vocab_index) for family in families]
                    best_event = max(metrics, key=lambda row: float(row["score_event"]))
                    best_core = max(metrics, key=lambda row: float(row["score_core"]))
                    event_wins[str(best_event["family"])] += 1
                    core_wins[str(best_core["family"])] += 1

                    for row in metrics:
                        rows.append(
                            {
                                "damage_keep": damage_keep,
                                "damage_prob": damage_prob,
                                "trigger_threshold": trigger_threshold,
                                "family": row["family"],
                                "score_event": float(row["score_event"]),
                                "score_core": float(row["score_core"]),
                                "trigger_rate": float(row["trigger_rate"]),
                                "repair_score": float(row["repair_score"]),
                                "repair_gain": float(row["repair_gain"]),
                            }
                        )
    finally:
        event.MASK_KEEP_DAMAGE, event.DAMAGE_PROB, event.DAMAGE_TRIGGER_THRESHOLD = original

    write_csv(rows, OUT / "event_family_sweep.csv")

    report = f"""# Boundary Access Event Family Sweep

Configs:
- damage keeps `{DAMAGE_KEEPS}`
- damage probabilities `{DAMAGE_PROBS}`
- trigger thresholds `{TRIGGER_THRESHOLDS}`

Event-score win counts:
- `{dict(sorted(event_wins.items()))}`

Core-score win counts:
- `{dict(sorted(core_wins.items()))}`

Interpretation:
- This checks which fallback family actually wins once explicit damage exists.
- If Fibonacci does not win the core score here, the stronger read is that event rescue matters more than Fibonacci structure in this lane.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"event wins: {dict(sorted(event_wins.items()))}")
    print(f"core wins: {dict(sorted(core_wins.items()))}")


if __name__ == "__main__":
    main()
