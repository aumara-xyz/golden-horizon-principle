#!/usr/bin/env python3
"""Boundary Access Channel sweep and alternating-return control.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import ghp_boundary_access_channel_toy as base


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_channel_sweep_outputs"

BALANCE_TARGETS = [0.45, 0.60, 0.75]
FRAGMENT_BUDGETS = [64, 96, 160]
MASK_KEEPS = [0.25, 0.35, 0.50]


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


def alternating_return_word(word: str) -> str:
    swapped = {"A": "B", "B": "A", "C": "B"}
    chars: list[str] = []
    for idx, ch in enumerate(word):
        if idx % 2 == 0:
            chars.append(ch)
        else:
            chars.append(swapped.get(ch, ch))
    return "".join(chars)


def fibonacci_block_return_word(word: str) -> str:
    swapped = {"A": "B", "B": "A", "C": "B"}
    fib_blocks = [1, 1]
    while sum(fib_blocks) < len(word):
        fib_blocks.append(fib_blocks[-1] + fib_blocks[-2])

    chars: list[str] = []
    cursor = 0
    flip = False
    for block in fib_blocks:
        if cursor >= len(word):
            break
        segment = word[cursor : cursor + block]
        if flip:
            chars.extend(swapped.get(ch, ch) for ch in segment)
        else:
            chars.extend(segment)
        cursor += block
        flip = not flip
    return "".join(chars)[: len(word)]


def collect_words() -> dict[str, str]:
    words = {family.name: base.generate_word(family.rules, base.TARGET_LENGTH) for family in base.FAMILIES}
    words["fibonacci_alt_return"] = alternating_return_word(words["fibonacci"])
    words["fibonacci_fibblock_return"] = fibonacci_block_return_word(words["fibonacci"])
    return words


def rank_family(rows: list[dict[str, float | str]], score_key: str) -> list[dict[str, float | str]]:
    return sorted(rows, key=lambda row: float(row[score_key]), reverse=True)


def main() -> None:
    ensure_dir(OUT)
    alt_family = base.BranchFamily("fibonacci_alt_return", {}, "Fibonacci alternating return control")
    fibblock_family = base.BranchFamily("fibonacci_fibblock_return", {}, "Fibonacci block-return control")
    families = list(base.FAMILIES) + [alt_family, fibblock_family]
    words = collect_words()
    vocab = base.collect_vocabulary(words, base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    rows: list[dict[str, float | str]] = []
    blended_wins: Counter[str] = Counter()
    no_balance_wins: Counter[str] = Counter()
    core_wins: Counter[str] = Counter()
    fib_ranks: defaultdict[str, list[int]] = defaultdict(list)

    for balance_target in BALANCE_TARGETS:
        base.BALANCE_TARGET = balance_target
        for fragment_budget in FRAGMENT_BUDGETS:
            base.FRAGMENT_BUDGET = fragment_budget
            base.LOW_BUDGET = max(24, fragment_budget // 2)
            for mask_keep in MASK_KEEPS:
                base.MASK_KEEP = mask_keep
                config_rows: list[dict[str, float | str]] = []
                for family in families:
                    word = words[family.name]
                    prior = base.full_histogram(word, base.KMER, vocab_index)
                    metrics = base.evaluate_family(family, word, prior, vocab_index)
                    row = {
                        "balance_target": balance_target,
                        "fragment_budget": fragment_budget,
                        "mask_keep": mask_keep,
                        **metrics,
                    }
                    rows.append(row)
                    config_rows.append(row)

                blended_ranked = rank_family(config_rows, "score")
                no_balance_ranked = rank_family(config_rows, "score_no_balance")
                core_ranked = rank_family(config_rows, "score_channel_core")
                blended_wins[str(blended_ranked[0]["family"])] += 1
                no_balance_wins[str(no_balance_ranked[0]["family"])] += 1
                core_wins[str(core_ranked[0]["family"])] += 1
                fib_ranks["score"].append(
                    next(idx for idx, row in enumerate(blended_ranked, start=1) if row["family"] == "fibonacci")
                )
                fib_ranks["score_no_balance"].append(
                    next(idx for idx, row in enumerate(no_balance_ranked, start=1) if row["family"] == "fibonacci")
                )
                fib_ranks["score_channel_core"].append(
                    next(idx for idx, row in enumerate(core_ranked, start=1) if row["family"] == "fibonacci")
                )

    write_csv(rows, OUT / "sweep_metrics.csv")

    family_summary: list[dict[str, float | str]] = []
    for family in families:
        family_rows = [row for row in rows if row["family"] == family.name]
        summary = {
            "family": family.name,
            "label": family.label,
            "mean_score": sum(float(row["score"]) for row in family_rows) / len(family_rows),
            "mean_no_balance": sum(float(row["score_no_balance"]) for row in family_rows) / len(family_rows),
            "mean_channel_core": sum(float(row["score_channel_core"]) for row in family_rows) / len(family_rows),
            "blended_wins": blended_wins[family.name],
            "no_balance_wins": no_balance_wins[family.name],
            "core_wins": core_wins[family.name],
        }
        family_summary.append(summary)
    write_csv(sorted(family_summary, key=lambda row: float(row["mean_score"]), reverse=True), OUT / "family_summary.csv")

    report = f"""# Boundary Access Channel Sweep

Configs:
- balance targets `{BALANCE_TARGETS}`
- fragment budgets `{FRAGMENT_BUDGETS}`
- mask keeps `{MASK_KEEPS}`

Fibonacci average ranks:
- blended score `{sum(fib_ranks['score']) / len(fib_ranks['score']):.2f}`
- no-balance score `{sum(fib_ranks['score_no_balance']) / len(fib_ranks['score_no_balance']):.2f}`
- channel-core score `{sum(fib_ranks['score_channel_core']) / len(fib_ranks['score_channel_core']):.2f}`

Win counts:
- blended `{dict(blended_wins)}`
- no-balance `{dict(no_balance_wins)}`
- channel-core `{dict(core_wins)}`

Alternating-return control:
- included as `fibonacci_alt_return`
- purpose: test "recycled but altered return" without claiming a full negative-Fibonacci derivation

Fibonacci-block return control:
- included as `fibonacci_fibblock_return`
- purpose: test recycled return in growing Fibonacci-sized segments instead of raw every-other-step flipping

Interpretation:
- if Fibonacci keeps winning channel-core but not blended score, that supports the anti-locking-core reading more than the "wins everything" reading
- if the alternating-return control helps, the recycled-information intuition may be worth formalizing
- if generic non-Fibonacci families match or beat Fibonacci across all score views, the strong minimal-architecture claim weakens
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"fibonacci mean blended rank: {sum(fib_ranks['score']) / len(fib_ranks['score']):.2f}")
    print(f"fibonacci mean channel-core rank: {sum(fib_ranks['score_channel_core']) / len(fib_ranks['score_channel_core']):.2f}")


if __name__ == "__main__":
    main()
