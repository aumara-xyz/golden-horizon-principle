#!/usr/bin/env python3
"""v58b core-frame nulls.

This attacks the new core-frame rule:
- balanced frame recolor
- rigid core
- touchup frame
- overwash frame
- random frame recolor
"""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v58_core_frame_recall as v58
import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v58b_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "balanced_frame": dict(frame_gain=0.12, core_anchor=0.22, random_frame=False),
    "rigid_core": dict(frame_gain=0.00, core_anchor=0.18, random_frame=False),
    "touchup_frame": dict(frame_gain=0.05, core_anchor=0.20, random_frame=False),
    "overwash_frame": dict(frame_gain=0.24, core_anchor=0.10, random_frame=False),
    "random_frame": dict(frame_gain=0.12, core_anchor=0.22, random_frame=True),
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
                v41.RecallCondition(
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
    for spec, recall_condition in specs:
        for mode, config in MODES.items():
            seq, diag = v58.run_sequence(spec.alpha, spec.condition, recall_condition, **config)
            metrics = v58.evaluate_recall(seq, diag)
            rows.append({"flow": spec.flow, "family": spec.family, "mode": mode, **metrics, "score": v41.score_recall(metrics)})

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        balanced = next(row for row in subset if row["mode"] == "balanced_frame")
        summary_rows.append(
            {
                "flow": flow,
                "balanced_score": balanced["score"],
                "same_field_recall_rate": balanced["same_field_recall_rate"],
                "same_core_recall_rate": balanced["same_core_recall_rate"],
                "frame_shift_rate": balanced["frame_shift_rate"],
                "balanced_vs_rigid_gap": balanced["score"] - next(row for row in subset if row["mode"] == "rigid_core")["score"],
                "balanced_vs_touchup_gap": balanced["score"] - next(row for row in subset if row["mode"] == "touchup_frame")["score"],
                "balanced_vs_overwash_gap": balanced["score"] - next(row for row in subset if row["mode"] == "overwash_frame")["score"],
                "balanced_vs_random_gap": balanced["score"] - next(row for row in subset if row["mode"] == "random_frame")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v58b - Core Frame Nulls

Golden result:
- balanced score: `{golden['balanced_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- frame shift rate: `{golden['frame_shift_rate']:.3f}`
- balanced vs rigid gap: `{golden['balanced_vs_rigid_gap']:.3f}`
- balanced vs touchup gap: `{golden['balanced_vs_touchup_gap']:.3f}`
- balanced vs overwash gap: `{golden['balanced_vs_overwash_gap']:.3f}`
- balanced vs random gap: `{golden['balanced_vs_random_gap']:.3f}`
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"golden balanced score: {golden['balanced_score']:.3f}")
    print(f"golden balanced vs rigid gap: {golden['balanced_vs_rigid_gap']:.3f}")
    print(f"golden balanced vs random gap: {golden['balanced_vs_random_gap']:.3f}")


if __name__ == "__main__":
    main()
