#!/usr/bin/env python3
"""Sweep weak/strong return-loop regimes for the Boundary Access Channel.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_return_loop as loop


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_return_loop_sweep_outputs"

GAINS = [0.10, 0.22, 0.34, 0.42, 0.56]
DECAYS = [0.45, 0.62, 0.78, 0.90]
MASKS = [0.25, 0.38, 0.50]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict[str, float | str]], path: Path) -> None:
    if not rows:
        return
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text)


def main() -> None:
    ensure_dir(OUT)
    words = loop.build_words()
    vocab = loop.base.collect_vocabulary(words, loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    fib_no = loop.LoopFamily("fibonacci_no_return_loop", "fibonacci", "none", "Fibonacci no-return loop")
    fib_yes = loop.LoopFamily("fibonacci_return_loop", "fibonacci", "fibonacci", "Fibonacci return loop")

    rows: list[dict[str, float | str]] = []
    original = (loop.WAKE_GAIN, loop.WAKE_DECAY, loop.MASK_KEEP)
    try:
        for gain in GAINS:
            for decay in DECAYS:
                for mask in MASKS:
                    loop.WAKE_GAIN = gain
                    loop.WAKE_DECAY = decay
                    loop.MASK_KEEP = mask

                    no_return = loop.evaluate_loop_family(fib_no, words, vocab_index)
                    with_return = loop.evaluate_loop_family(fib_yes, words, vocab_index)

                    rows.append(
                        {
                            "wake_gain": gain,
                            "wake_decay": decay,
                            "mask_keep": mask,
                            "return_score": float(with_return["score"]),
                            "no_return_score": float(no_return["score"]),
                            "return_core_score": float(with_return["score_core"]),
                            "no_return_core_score": float(no_return["score_core"]),
                            "blended_diff": float(with_return["score"]) - float(no_return["score"]),
                            "core_diff": float(with_return["score_core"]) - float(no_return["score_core"]),
                        }
                    )
    finally:
        loop.WAKE_GAIN, loop.WAKE_DECAY, loop.MASK_KEEP = original

    rows.sort(key=lambda row: (float(row["blended_diff"]), float(row["core_diff"])), reverse=True)
    write_csv(rows, OUT / "return_loop_sweep.csv")

    best = rows[0]
    positive_blended = sum(1 for row in rows if float(row["blended_diff"]) > 0)
    positive_core = sum(1 for row in rows if float(row["core_diff"]) > 0)

    report = f"""# Boundary Access Return-Loop Sweep

Configs:
- wake gains `{GAINS}`
- wake decays `{DECAYS}`
- mask keeps `{MASKS}`

Best blended-diff config:
- wake gain `{best['wake_gain']}`
- wake decay `{best['wake_decay']}`
- mask keep `{best['mask_keep']}`
- blended diff `{float(best['blended_diff']):.6f}`
- core diff `{float(best['core_diff']):.6f}`

Win counts:
- positive blended diff cases `{positive_blended}/{len(rows)}`
- positive core diff cases `{positive_core}/{len(rows)}`

Interpretation:
- Weak return can help the blended score in some regimes.
- Return does not improve the core channel score in any tested regime.
- The current disciplined read is that recycled wake may add texture, but it does not yet improve the actual access-plus-recovery core package.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(
        "best config:",
        best["wake_gain"],
        best["wake_decay"],
        best["mask_keep"],
        f"blended_diff={float(best['blended_diff']):.6f}",
        f"core_diff={float(best['core_diff']):.6f}",
    )
    print(f"positive blended cases: {positive_blended}/{len(rows)}")
    print(f"positive core cases: {positive_core}/{len(rows)}")


if __name__ == "__main__":
    main()
