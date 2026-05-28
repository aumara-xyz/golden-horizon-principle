#!/usr/bin/env python3
"""v53 binding plasticity interaction."""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41
import golden_zipper_v51_memory_plasticity_panel as v51

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v53_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "real_rigid": dict(binding_mode="real", plasticity_gain=0.00, anchor_gain=0.18),
    "real_balanced": dict(binding_mode="real", plasticity_gain=0.12, anchor_gain=0.14),
    "no_binding_rigid": dict(binding_mode="no_binding", plasticity_gain=0.00, anchor_gain=0.18),
    "no_binding_balanced": dict(binding_mode="no_binding", plasticity_gain=0.12, anchor_gain=0.14),
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    fieldnames=[];seen=set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key);fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text)


def load_best_conditions():
    specs = {spec.flow: spec for spec in v41.v31b.find_best_specs()}
    rows = list(csv.DictReader(V41_SUMMARY.open()))
    selected=[]
    for row in rows:
        spec = specs[row["flow"]]
        selected.append((spec, v41.RecallCondition(
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
        )))
    return selected


def main() -> None:
    ensure_dir(OUT)
    specs = load_best_conditions()
    rows=[]
    for spec, recall_condition in specs:
        for mode, config in MODES.items():
            seq, diag = v51.run_sequence(spec.alpha, spec.condition, recall_condition, config["binding_mode"], config["plasticity_gain"], config["anchor_gain"], False)
            metrics = v51.evaluate_recall(seq, diag)
            rows.append({"flow": spec.flow, "mode": mode, **metrics, "score": v41.score_recall(metrics)})
    write_csv(rows, OUT / "mode_metrics.csv")
    summary=[]
    for flow in sorted({row["flow"] for row in rows}):
        subset=[row for row in rows if row["flow"]==flow]
        rb=next(row for row in subset if row["mode"]=="real_balanced")
        rr=next(row for row in subset if row["mode"]=="real_rigid")
        nb=next(row for row in subset if row["mode"]=="no_binding_balanced")
        nr=next(row for row in subset if row["mode"]=="no_binding_rigid")
        summary.append({
            "flow": flow,
            "real_balanced_score": rb["score"],
            "binding_plasticity_help": rb["score"] - rr["score"],
            "no_binding_plasticity_help": nb["score"] - nr["score"],
            "binding_help_under_balanced": rb["score"] - nb["score"],
        })
    write_csv(summary, OUT / "summary.csv")
    golden=next(row for row in summary if row["flow"]=="golden")
    write_text(OUT / "report.md", f"""# Golden Zipper v53 - Binding Plasticity Interaction

Golden result:
- real balanced score: `{golden['real_balanced_score']:.3f}`
- binding plasticity help: `{golden['binding_plasticity_help']:.3f}`
- no-binding plasticity help: `{golden['no_binding_plasticity_help']:.3f}`
- binding help under balanced: `{golden['binding_help_under_balanced']:.3f}`
""")
    print(f"files created: {OUT}")
    print(f"golden real balanced score: {golden['real_balanced_score']:.3f}")
    print(f"golden binding plasticity help: {golden['binding_plasticity_help']:.3f}")
    print(f"golden no-binding plasticity help: {golden['no_binding_plasticity_help']:.3f}")


if __name__ == "__main__":
    main()
