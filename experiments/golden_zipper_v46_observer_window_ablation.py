#!/usr/bin/env python3
"""v46 observer window ablation.

This isolates what the observer-window is doing in the stronger field model:
- local only
- nested windows
- over-blended nested windows
- blurred local window

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v46_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "local_only": (1, 0.00, 0.72),
    "nested": (2, 0.14, 0.72),
    "over_blended": (3, 0.28, 0.72),
    "blurred_local": (1, 0.00, 0.88),
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
                    admission_center=float(row["best_admission_center"]),
                    admission_width=float(row["best_admission_width"]),
                    admission_gain=float(row["best_admission_gain"]),
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
        for mode, (levels, blend, decay) in MODES.items():
            recall_condition = v41.RecallCondition(
                recency_decay=decay,
                window_levels=levels,
                window_blend_gain=blend,
                **base_kwargs,
            )
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
        nested = next(row for row in subset if row["mode"] == "nested")
        local = next(row for row in subset if row["mode"] == "local_only")
        over = next(row for row in subset if row["mode"] == "over_blended")
        blur = next(row for row in subset if row["mode"] == "blurred_local")
        best = max(subset, key=lambda row: row["score"])
        summary_rows.append(
            {
                "flow": flow,
                "best_mode": best["mode"],
                "nested_score": nested["score"],
                "same_field_recall_rate": nested["same_field_recall_rate"],
                "same_core_recall_rate": nested["same_core_recall_rate"],
                "macro_window_rate": nested["macro_window_rate"],
                "split_rate": nested["split_rate"],
                "nested_vs_local_gap": nested["score"] - local["score"],
                "nested_vs_over_blended_gap": nested["score"] - over["score"],
                "nested_vs_blurred_local_gap": nested["score"] - blur["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["nested_score"], reverse=True)
    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")

    report = f"""# Golden Zipper v46 - Observer Window Ablation

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by nested-window score: `{best['flow']}` with `{best['nested_score']:.3f}`

Golden result:
- best mode: `{golden['best_mode']}`
- nested score: `{golden['nested_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- macro-window rate: `{golden['macro_window_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- nested vs local gap: `{golden['nested_vs_local_gap']:.3f}`
- nested vs over-blended gap: `{golden['nested_vs_over_blended_gap']:.3f}`
- nested vs blurred-local gap: `{golden['nested_vs_blurred_local_gap']:.3f}`
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by nested-window score: {best['flow']} {best['nested_score']:.3f}")
    print(f"golden best mode: {golden['best_mode']}")
    print(f"golden nested score: {golden['nested_score']:.3f}")
    print(f"golden nested vs local gap: {golden['nested_vs_local_gap']:.3f}")
    print(f"golden nested vs over-blended gap: {golden['nested_vs_over_blended_gap']:.3f}")
    print(f"golden nested vs blurred-local gap: {golden['nested_vs_blurred_local_gap']:.3f}")


if __name__ == "__main__":
    main()
