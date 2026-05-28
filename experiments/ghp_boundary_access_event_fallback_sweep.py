#!/usr/bin/env python3
"""Sweep event-triggered fallback damage regimes.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_event_fallback as event


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_event_fallback_sweep_outputs"

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

    original = (event.MASK_KEEP_DAMAGE, event.DAMAGE_PROB, event.DAMAGE_TRIGGER_THRESHOLD)
    rows: list[dict[str, float | str]] = []
    try:
        for damage_keep in DAMAGE_KEEPS:
            for damage_prob in DAMAGE_PROBS:
                for trigger_threshold in TRIGGER_THRESHOLDS:
                    event.MASK_KEEP_DAMAGE = damage_keep
                    event.DAMAGE_PROB = damage_prob
                    event.DAMAGE_TRIGGER_THRESHOLD = trigger_threshold

                    no_return = event.evaluate_family(
                        event.FallbackFamily("no_return", "fibonacci", "none", "none", "No return"),
                        words,
                        vocab_index,
                    )
                    event_fib = event.evaluate_family(
                        event.FallbackFamily("event_fibonacci", "fibonacci", "fibonacci", "event", "Event Fibonacci fallback"),
                        words,
                        vocab_index,
                    )
                    event_soft = event.evaluate_family(
                        event.FallbackFamily("event_soft_fibonacci", "fibonacci", "fibonacci", "event_soft", "Event-soft Fibonacci fallback"),
                        words,
                        vocab_index,
                    )
                    event_random = event.evaluate_family(
                        event.FallbackFamily("event_random", "fibonacci", "random", "event", "Event random fallback"),
                        words,
                        vocab_index,
                    )

                    rows.append(
                        {
                            "damage_keep": damage_keep,
                            "damage_prob": damage_prob,
                            "trigger_threshold": trigger_threshold,
                            "fib_trigger_rate": float(event_fib["trigger_rate"]),
                            "fib_core_diff_vs_no": float(event_fib["score_core"]) - float(no_return["score_core"]),
                            "fib_event_diff_vs_no": float(event_fib["score_event"]) - float(no_return["score_event"]),
                            "fib_core_diff_vs_random": float(event_fib["score_core"]) - float(event_random["score_core"]),
                            "fib_event_diff_vs_random": float(event_fib["score_event"]) - float(event_random["score_event"]),
                            "soft_core_diff_vs_no": float(event_soft["score_core"]) - float(no_return["score_core"]),
                            "soft_event_diff_vs_no": float(event_soft["score_event"]) - float(no_return["score_event"]),
                        }
                    )
    finally:
        event.MASK_KEEP_DAMAGE, event.DAMAGE_PROB, event.DAMAGE_TRIGGER_THRESHOLD = original

    rows.sort(
        key=lambda row: (
            float(row["fib_core_diff_vs_no"]),
            float(row["fib_core_diff_vs_random"]),
            float(row["fib_event_diff_vs_no"]),
        ),
        reverse=True,
    )
    write_csv(rows, OUT / "event_fallback_sweep.csv")

    best = rows[0]
    positive_core_vs_no = sum(1 for row in rows if float(row["fib_core_diff_vs_no"]) > 0)
    positive_core_vs_random = sum(1 for row in rows if float(row["fib_core_diff_vs_random"]) > 0)
    positive_core_vs_both = sum(
        1 for row in rows if float(row["fib_core_diff_vs_no"]) > 0 and float(row["fib_core_diff_vs_random"]) > 0
    )

    report = f"""# Boundary Access Event Fallback Sweep

Configs:
- damage keeps `{DAMAGE_KEEPS}`
- damage probabilities `{DAMAGE_PROBS}`
- trigger thresholds `{TRIGGER_THRESHOLDS}`

Best Fibonacci-event config:
- damage keep `{best['damage_keep']}`
- damage probability `{best['damage_prob']}`
- trigger threshold `{best['trigger_threshold']}`
- Fibonacci trigger rate `{float(best['fib_trigger_rate']):.3f}`
- core diff vs no-return `{float(best['fib_core_diff_vs_no']):.6f}`
- core diff vs random `{float(best['fib_core_diff_vs_random']):.6f}`
- event diff vs no-return `{float(best['fib_event_diff_vs_no']):.6f}`

Win counts:
- positive core vs no-return `{positive_core_vs_no}/{len(rows)}`
- positive core vs random `{positive_core_vs_random}/{len(rows)}`
- positive core vs both `{positive_core_vs_both}/{len(rows)}`

Interpretation:
- This checks whether event-triggered Fibonacci fallback really helps after explicit damage.
- It only counts as a serious result if it beats both no-return and random fallback on the core score.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(
        "best config:",
        best["damage_keep"],
        best["damage_prob"],
        best["trigger_threshold"],
        f"fib_core_diff_vs_no={float(best['fib_core_diff_vs_no']):.6f}",
        f"fib_core_diff_vs_random={float(best['fib_core_diff_vs_random']):.6f}",
    )
    print(f"positive core vs no-return: {positive_core_vs_no}/{len(rows)}")
    print(f"positive core vs random: {positive_core_vs_random}/{len(rows)}")
    print(f"positive core vs both: {positive_core_vs_both}/{len(rows)}")


if __name__ == "__main__":
    main()
