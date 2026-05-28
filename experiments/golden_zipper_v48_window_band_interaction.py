#!/usr/bin/env python3
"""v48 window-band interaction.

This tests whether the prediction-error band and nested observer windows
help separately or mostly as a pair.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v48_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "local_exact": dict(window_levels=1, window_blend_gain=0.00, recency_decay=0.72, admission_center=0.00, admission_width=0.10, admission_gain=0.14),
    "local_moderate": dict(window_levels=1, window_blend_gain=0.00, recency_decay=0.72, admission_center=0.20, admission_width=0.18, admission_gain=0.14),
    "nested_exact": dict(window_levels=2, window_blend_gain=0.14, recency_decay=0.72, admission_center=0.00, admission_width=0.10, admission_gain=0.14),
    "nested_moderate": dict(window_levels=2, window_blend_gain=0.14, recency_decay=0.72, admission_center=0.20, admission_width=0.18, admission_gain=0.14),
    "nested_novelty": dict(window_levels=2, window_blend_gain=0.14, recency_decay=0.72, admission_center=0.35, admission_width=0.18, admission_gain=0.14),
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
            rows.append(
                {
                    "flow": spec.flow,
                    "family": spec.family,
                    "mode": mode,
                    **metrics,
                    "score": v41.score_recall(metrics),
                }
            )

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        local_exact = next(row for row in subset if row["mode"] == "local_exact")
        local_moderate = next(row for row in subset if row["mode"] == "local_moderate")
        nested_exact = next(row for row in subset if row["mode"] == "nested_exact")
        nested_moderate = next(row for row in subset if row["mode"] == "nested_moderate")
        nested_novelty = next(row for row in subset if row["mode"] == "nested_novelty")
        best = max(subset, key=lambda row: row["score"])
        summary_rows.append(
            {
                "flow": flow,
                "best_mode": best["mode"],
                "nested_moderate_score": nested_moderate["score"],
                "same_field_recall_rate": nested_moderate["same_field_recall_rate"],
                "same_core_recall_rate": nested_moderate["same_core_recall_rate"],
                "split_rate": nested_moderate["split_rate"],
                "nested_moderate_vs_local_moderate_gap": nested_moderate["score"] - local_moderate["score"],
                "nested_moderate_vs_nested_exact_gap": nested_moderate["score"] - nested_exact["score"],
                "nested_moderate_vs_nested_novelty_gap": nested_moderate["score"] - nested_novelty["score"],
                "nested_moderate_vs_local_exact_gap": nested_moderate["score"] - local_exact["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["nested_moderate_score"], reverse=True)
    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")

    report = f"""# Golden Zipper v48 - Window Band Interaction

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by nested-moderate score: `{best['flow']}` with `{best['nested_moderate_score']:.3f}`

Golden result:
- best mode: `{golden['best_mode']}`
- nested moderate score: `{golden['nested_moderate_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- nested-moderate vs local-moderate gap: `{golden['nested_moderate_vs_local_moderate_gap']:.3f}`
- nested-moderate vs nested-exact gap: `{golden['nested_moderate_vs_nested_exact_gap']:.3f}`
- nested-moderate vs nested-novelty gap: `{golden['nested_moderate_vs_nested_novelty_gap']:.3f}`
- nested-moderate vs local-exact gap: `{golden['nested_moderate_vs_local_exact_gap']:.3f}`
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by nested-moderate score: {best['flow']} {best['nested_moderate_score']:.3f}")
    print(f"golden best mode: {golden['best_mode']}")
    print(f"golden nested moderate score: {golden['nested_moderate_score']:.3f}")
    print(f"golden nested-moderate vs local-moderate gap: {golden['nested_moderate_vs_local_moderate_gap']:.3f}")
    print(f"golden nested-moderate vs nested-exact gap: {golden['nested_moderate_vs_nested_exact_gap']:.3f}")
    print(f"golden nested-moderate vs nested-novelty gap: {golden['nested_moderate_vs_nested_novelty_gap']:.3f}")


if __name__ == "__main__":
    main()
