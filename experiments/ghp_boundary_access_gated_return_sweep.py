#!/usr/bin/env python3
"""Sweep gated-return thresholds for the Boundary Access Channel.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_gated_return as gated


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_gated_return_sweep_outputs"

PRESSURE_THRESHOLDS = [0.12, 0.25, 0.38, 0.50, 0.62]
SPARSITY_THRESHOLDS = [0.18, 0.30, 0.42, 0.54]
GATE_MODES = [
    ("pressure_soft", "soft pressure"),
    ("pressure_drift", "pressure plus drift"),
    ("pressure_or_sparse", "pressure or sparse"),
    ("pressure_and_sparse", "pressure and sparse"),
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


def main() -> None:
    ensure_dir(OUT)
    words = gated.loop.build_words()
    vocab = gated.loop.base.collect_vocabulary(words, gated.loop.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    no_return = gated.GatedFamily("fibonacci_no_return", "fibonacci", "none", "none", "Fibonacci no return")
    always_return = gated.GatedFamily("fibonacci_always_return", "fibonacci", "fibonacci", "always", "Fibonacci always return")

    no_metrics = gated.evaluate_family(no_return, words, vocab_index, gated.PRESSURE_THRESHOLD, gated.SPARSITY_THRESHOLD)
    always_metrics = gated.evaluate_family(always_return, words, vocab_index, gated.PRESSURE_THRESHOLD, gated.SPARSITY_THRESHOLD)

    rows: list[dict[str, float | str]] = []
    for pressure_threshold in PRESSURE_THRESHOLDS:
        for sparsity_threshold in SPARSITY_THRESHOLDS:
            for gate_mode, label in GATE_MODES:
                family = gated.GatedFamily(
                    f"fibonacci_{gate_mode}",
                    "fibonacci",
                    "fibonacci",
                    gate_mode,
                    f"Fibonacci {label}",
                )
                metrics = gated.evaluate_family(family, words, vocab_index, pressure_threshold, sparsity_threshold)
                rows.append(
                    {
                        "gate_mode": gate_mode,
                        "pressure_threshold": pressure_threshold,
                        "sparsity_threshold": sparsity_threshold,
                        "gate_rate": float(metrics["gate_rate"]),
                        "pressure_mean": float(metrics["pressure_mean"]),
                        "score": float(metrics["score"]),
                        "score_core": float(metrics["score_core"]),
                        "blended_diff_vs_no": float(metrics["score"]) - float(no_metrics["score"]),
                        "core_diff_vs_no": float(metrics["score_core"]) - float(no_metrics["score_core"]),
                        "blended_diff_vs_always": float(metrics["score"]) - float(always_metrics["score"]),
                        "core_diff_vs_always": float(metrics["score_core"]) - float(always_metrics["score_core"]),
                    }
                )

    rows.sort(
        key=lambda row: (
            float(row["core_diff_vs_no"]),
            float(row["core_diff_vs_always"]),
            float(row["blended_diff_vs_no"]),
        ),
        reverse=True,
    )
    write_csv(rows, OUT / "gated_return_sweep.csv")

    best = rows[0]
    positive_core_vs_no = sum(1 for row in rows if float(row["core_diff_vs_no"]) > 0)
    positive_core_vs_always = sum(1 for row in rows if float(row["core_diff_vs_always"]) > 0)
    positive_core_vs_both = sum(
        1
        for row in rows
        if float(row["core_diff_vs_no"]) > 0 and float(row["core_diff_vs_always"]) > 0
    )

    report = f"""# Boundary Access Gated Return Sweep

Configs:
- pressure thresholds `{PRESSURE_THRESHOLDS}`
- sparsity thresholds `{SPARSITY_THRESHOLDS}`
- gate modes `{[mode for mode, _ in GATE_MODES]}`

References:
- no-return core score `{float(no_metrics['score_core']):.6f}`
- always-return core score `{float(always_metrics['score_core']):.6f}`

Best core config:
- gate mode `{best['gate_mode']}`
- pressure threshold `{best['pressure_threshold']}`
- sparsity threshold `{best['sparsity_threshold']}`
- gate rate `{float(best['gate_rate']):.6f}`
- core diff vs no-return `{float(best['core_diff_vs_no']):.6f}`
- core diff vs always-return `{float(best['core_diff_vs_always']):.6f}`
- blended diff vs no-return `{float(best['blended_diff_vs_no']):.6f}`

Win counts:
- positive core vs no-return `{positive_core_vs_no}/{len(rows)}`
- positive core vs always-return `{positive_core_vs_always}/{len(rows)}`
- positive core vs both `{positive_core_vs_both}/{len(rows)}`

Interpretation:
- This asks whether return only helps when it is actually gated by pressure instead of flowing constantly.
- If some gated configs beat both no-return and always-return on the core score, then return may matter as a conditional stabilizer.
- If they do not, the current honest read stays with the anti-locking core and treats return as secondary texture at best.
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best gate: {best['gate_mode']} p={best['pressure_threshold']} s={best['sparsity_threshold']}")
    print(f"positive core vs no-return: {positive_core_vs_no}/{len(rows)}")
    print(f"positive core vs always-return: {positive_core_vs_always}/{len(rows)}")
    print(f"positive core vs both: {positive_core_vs_both}/{len(rows)}")


if __name__ == "__main__":
    main()
