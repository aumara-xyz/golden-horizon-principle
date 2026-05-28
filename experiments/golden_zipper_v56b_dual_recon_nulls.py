#!/usr/bin/env python3
"""v56b dual recon nulls."""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41
import golden_zipper_v56_dual_reconsolidation_panel as v56

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v56b_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "dual_recon": dict(binding_mode="real", mode_kind="dual_recon", random_plastic=False),
    "rigid": dict(binding_mode="real", mode_kind="rigid", random_plastic=False),
    "touch_up": dict(binding_mode="real", mode_kind="touch_up", random_plastic=False),
    "melt_heavy": dict(binding_mode="real", mode_kind="melt_heavy", random_plastic=False),
    "dual_random": dict(binding_mode="real", mode_kind="dual_recon", random_plastic=True),
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
        writer=csv.DictWriter(handle, fieldnames=fieldnames)
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
            seq, diag = v56.run_sequence(spec.alpha, spec.condition, recall_condition, **config)
            metrics = v56.evaluate_recall(seq, diag)
            rows.append({"flow": spec.flow, "mode": mode, **metrics, "score": v41.score_recall(metrics)})
    write_csv(rows, OUT / "mode_metrics.csv")
    summary=[]
    for flow in sorted({row["flow"] for row in rows}):
        subset=[row for row in rows if row["flow"]==flow]
        dual=next(row for row in subset if row["mode"]=="dual_recon")
        summary.append({
            "flow": flow,
            "dual_score": dual["score"],
            "rewrite_drift_rate": dual["rewrite_drift_rate"],
            "dual_vs_rigid_gap": dual["score"] - next(row for row in subset if row["mode"]=="rigid")["score"],
            "dual_vs_touchup_gap": dual["score"] - next(row for row in subset if row["mode"]=="touch_up")["score"],
            "dual_vs_meltheavy_gap": dual["score"] - next(row for row in subset if row["mode"]=="melt_heavy")["score"],
            "dual_vs_random_gap": dual["score"] - next(row for row in subset if row["mode"]=="dual_random")["score"],
        })
    write_csv(summary, OUT / "summary.csv")
    golden=next(row for row in summary if row["flow"]=="golden")
    write_text(OUT / "report.md", f"""# Golden Zipper v56b - Dual Recon Nulls

Golden result:
- dual score: `{golden['dual_score']:.3f}`
- rewrite drift rate: `{golden['rewrite_drift_rate']:.3f}`
- dual vs rigid gap: `{golden['dual_vs_rigid_gap']:.3f}`
- dual vs touch-up gap: `{golden['dual_vs_touchup_gap']:.3f}`
- dual vs melt-heavy gap: `{golden['dual_vs_meltheavy_gap']:.3f}`
- dual vs random gap: `{golden['dual_vs_random_gap']:.3f}`
""")
    print(f"files created: {OUT}")
    print(f"golden dual score: {golden['dual_score']:.3f}")
    print(f"golden dual vs rigid gap: {golden['dual_vs_rigid_gap']:.3f}")
    print(f"golden dual vs touch-up gap: {golden['dual_vs_touchup_gap']:.3f}")
    print(f"golden dual vs random gap: {golden['dual_vs_random_gap']:.3f}")


if __name__ == "__main__":
    main()
