#!/usr/bin/env python3
"""v54 plasticity relatedness nulls."""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41
import golden_zipper_v51_memory_plasticity_panel as v51

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v54_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "related_balanced": dict(random_plastic=False, plasticity_gain=0.12, anchor_gain=0.14),
    "random_balanced": dict(random_plastic=True, plasticity_gain=0.12, anchor_gain=0.14),
    "related_rigid": dict(random_plastic=False, plasticity_gain=0.00, anchor_gain=0.18),
    "random_overplastic": dict(random_plastic=True, plasticity_gain=0.24, anchor_gain=0.06),
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
    specs={spec.flow: spec for spec in v41.v31b.find_best_specs()}
    rows=list(csv.DictReader(V41_SUMMARY.open()))
    selected=[]
    for row in rows:
        spec=specs[row["flow"]]
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
    specs=load_best_conditions()
    rows=[]
    for spec, recall_condition in specs:
        for mode, config in MODES.items():
            seq, diag = v51.run_sequence(spec.alpha, spec.condition, recall_condition, "real", config["plasticity_gain"], config["anchor_gain"], config["random_plastic"])
            metrics = v51.evaluate_recall(seq, diag)
            rows.append({"flow": spec.flow, "mode": mode, **metrics, "score": v41.score_recall(metrics)})
    write_csv(rows, OUT / "mode_metrics.csv")
    summary=[]
    for flow in sorted({row["flow"] for row in rows}):
        subset=[row for row in rows if row["flow"]==flow]
        rb=next(row for row in subset if row["mode"]=="related_balanced")
        summary.append({
            "flow": flow,
            "related_balanced_score": rb["score"],
            "rewrite_drift_rate": rb["rewrite_drift_rate"],
            "related_vs_random_gap": rb["score"] - next(row for row in subset if row["mode"]=="random_balanced")["score"],
            "related_vs_rigid_gap": rb["score"] - next(row for row in subset if row["mode"]=="related_rigid")["score"],
            "related_vs_random_overplastic_gap": rb["score"] - next(row for row in subset if row["mode"]=="random_overplastic")["score"],
        })
    write_csv(summary, OUT / "summary.csv")
    golden=next(row for row in summary if row["flow"]=="golden")
    write_text(OUT / "report.md", f"""# Golden Zipper v54 - Plasticity Relatedness Nulls

Golden result:
- related balanced score: `{golden['related_balanced_score']:.3f}`
- rewrite drift rate: `{golden['rewrite_drift_rate']:.3f}`
- related vs random gap: `{golden['related_vs_random_gap']:.3f}`
- related vs rigid gap: `{golden['related_vs_rigid_gap']:.3f}`
- related vs random overplastic gap: `{golden['related_vs_random_overplastic_gap']:.3f}`
""")
    print(f"files created: {OUT}")
    print(f"golden related balanced score: {golden['related_balanced_score']:.3f}")
    print(f"golden related vs random gap: {golden['related_vs_random_gap']:.3f}")
    print(f"golden related vs rigid gap: {golden['related_vs_rigid_gap']:.3f}")


if __name__ == "__main__":
    main()
