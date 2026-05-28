#!/usr/bin/env python3
"""v49 binding-band interaction.

This tests whether the prediction-error band still helps when binding is removed.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41
import golden_zipper_v41b_field_binding_stack_nulls as v41b


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v49_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "real_moderate": ("real", 0.20, 0.18, 0.14),
    "real_exact": ("real", 0.00, 0.10, 0.14),
    "real_no_band": ("real", 0.20, 0.18, 0.00),
    "no_binding_moderate": ("no_binding", 0.20, 0.18, 0.14),
    "no_binding_exact": ("no_binding", 0.00, 0.10, 0.14),
    "no_binding_no_band": ("no_binding", 0.20, 0.18, 0.00),
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
                    recency_decay=0.72,
                    resonance_gain=0.08,
                    field_radius=int(float(row["best_field_radius"])),
                    field_width=float(row["best_field_width"]),
                    field_support_gain=float(row["best_field_support_gain"]),
                    field_competition_gain=float(row["best_field_competition_gain"]),
                    phase_bind_gain=float(row["best_phase_bind_gain"]),
                    phase_bind_threshold=float(row["best_phase_bind_threshold"]),
                    window_levels=int(float(row["best_window_levels"])),
                    window_blend_gain=float(row["best_window_blend_gain"]),
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
        for mode, (binding_mode, center, width, gain) in MODES.items():
            recall_condition = v41.RecallCondition(
                admission_center=center,
                admission_width=width,
                admission_gain=gain,
                **base_kwargs,
            )
            seq, diag = v41b.run_sequence(spec.alpha, spec.condition, recall_condition, binding_mode)
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
        real_moderate = next(row for row in subset if row["mode"] == "real_moderate")
        real_exact = next(row for row in subset if row["mode"] == "real_exact")
        real_none = next(row for row in subset if row["mode"] == "real_no_band")
        no_moderate = next(row for row in subset if row["mode"] == "no_binding_moderate")
        no_exact = next(row for row in subset if row["mode"] == "no_binding_exact")
        no_none = next(row for row in subset if row["mode"] == "no_binding_no_band")
        summary_rows.append(
            {
                "flow": flow,
                "real_moderate_score": real_moderate["score"],
                "same_field_recall_rate": real_moderate["same_field_recall_rate"],
                "split_rate": real_moderate["split_rate"],
                "binding_help_under_moderate": real_moderate["score"] - no_moderate["score"],
                "moderate_help_with_binding": real_moderate["score"] - max(real_exact["score"], real_none["score"]),
                "moderate_help_without_binding": no_moderate["score"] - max(no_exact["score"], no_none["score"]),
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["real_moderate_score"], reverse=True)
    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")

    report = f"""# Golden Zipper v49 - Binding Band Interaction

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by real-moderate score: `{best['flow']}` with `{best['real_moderate_score']:.3f}`

Golden result:
- real-moderate score: `{golden['real_moderate_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- binding help under moderate: `{golden['binding_help_under_moderate']:.3f}`
- moderate help with binding: `{golden['moderate_help_with_binding']:.3f}`
- moderate help without binding: `{golden['moderate_help_without_binding']:.3f}`
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by real-moderate score: {best['flow']} {best['real_moderate_score']:.3f}")
    print(f"golden real-moderate score: {golden['real_moderate_score']:.3f}")
    print(f"golden binding help under moderate: {golden['binding_help_under_moderate']:.3f}")
    print(f"golden moderate help with binding: {golden['moderate_help_with_binding']:.3f}")
    print(f"golden moderate help without binding: {golden['moderate_help_without_binding']:.3f}")


if __name__ == "__main__":
    main()
