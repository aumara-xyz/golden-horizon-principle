#!/usr/bin/env python3
"""v62 window hierarchy specificity.

Ask whether the nested-window benefit is really about hierarchy:
- local moderate
- repeated-local stack
- nested moderate
- coarse-heavy nested
- over-blended nested
"""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v62_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "local_moderate": dict(window_levels=1, window_blend_gain=0.00, recency_decay=0.72, admission_center=0.20, admission_width=0.18, admission_gain=0.14),
    "repeated_local": dict(window_levels=2, window_blend_gain=0.00, recency_decay=0.72, admission_center=0.20, admission_width=0.18, admission_gain=0.14),
    "nested_moderate": dict(window_levels=2, window_blend_gain=0.14, recency_decay=0.72, admission_center=0.20, admission_width=0.18, admission_gain=0.14),
    "coarse_heavy": dict(window_levels=3, window_blend_gain=0.20, recency_decay=0.82, admission_center=0.20, admission_width=0.18, admission_gain=0.14),
    "over_blended": dict(window_levels=3, window_blend_gain=0.28, recency_decay=0.72, admission_center=0.20, admission_width=0.18, admission_gain=0.14),
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
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


def load_best_conditions():
    specs = {spec.flow: spec for spec in v41.v31b.find_best_specs()}
    rows = list(csv.DictReader(V41_SUMMARY.open()))
    selected = []
    for row in rows:
        spec = specs[row["flow"]]
        selected.append(
            (
                spec,
                dict(
                    context_pressure=float(row["best_context_pressure"]),
                    similarity_threshold=float(row["best_similarity_threshold"]),
                    recall_window=int(float(row["best_recall_window"])),
                    recall_gain=0.14,
                    layer_window=13,
                    resonance_gain=0.08,
                    field_radius=int(float(row["best_field_radius"])),
                    field_width=float(row["best_field_width"]),
                    field_support_gain=float(row["best_field_support_gain"]),
                    field_competition_gain=float(row["best_field_competition_gain"]),
                    phase_bind_gain=float(row["best_phase_bind_gain"]),
                    phase_bind_threshold=float(row["best_phase_bind_threshold"]),
                    split_threshold=0.24,
                ),
            )
        )
    return selected


def main() -> None:
    ensure_dir(OUT)
    specs = load_best_conditions()
    rows = []
    for spec, base_kwargs in specs:
        for mode, overrides in MODES.items():
            recall_condition = v41.RecallCondition(**base_kwargs, **overrides)
            seq, diag = v41.build_field_sequence(spec.alpha, spec.condition, recall_condition)
            metrics = v41.evaluate_recall(seq, diag)
            rows.append({"flow": spec.flow, "family": spec.family, "mode": mode, **metrics, "score": v41.score_recall(metrics)})

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        local = next(row for row in subset if row["mode"] == "local_moderate")
        repeated = next(row for row in subset if row["mode"] == "repeated_local")
        nested = next(row for row in subset if row["mode"] == "nested_moderate")
        coarse = next(row for row in subset if row["mode"] == "coarse_heavy")
        over = next(row for row in subset if row["mode"] == "over_blended")
        summary_rows.append(
            {
                "flow": flow,
                "best_mode": max(subset, key=lambda row: row["score"])["mode"],
                "nested_score": nested["score"],
                "same_field_recall_rate": nested["same_field_recall_rate"],
                "same_core_recall_rate": nested["same_core_recall_rate"],
                "nested_vs_local_gap": nested["score"] - local["score"],
                "nested_vs_repeated_local_gap": nested["score"] - repeated["score"],
                "nested_vs_coarse_heavy_gap": nested["score"] - coarse["score"],
                "nested_vs_over_blended_gap": nested["score"] - over["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v62 - Window Hierarchy Specificity

Golden result:
- best mode: `{golden['best_mode']}`
- nested score: `{golden['nested_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- nested vs local gap: `{golden['nested_vs_local_gap']:.3f}`
- nested vs repeated-local gap: `{golden['nested_vs_repeated_local_gap']:.3f}`
- nested vs coarse-heavy gap: `{golden['nested_vs_coarse_heavy_gap']:.3f}`
- nested vs over-blended gap: `{golden['nested_vs_over_blended_gap']:.3f}`
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"golden best mode: {golden['best_mode']}")
    print(f"golden nested score: {golden['nested_score']:.3f}")
    print(f"golden nested vs repeated-local gap: {golden['nested_vs_repeated_local_gap']:.3f}")


if __name__ == "__main__":
    main()
