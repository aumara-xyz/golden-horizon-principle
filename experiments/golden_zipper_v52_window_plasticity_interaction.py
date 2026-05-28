#!/usr/bin/env python3
"""v52 window plasticity interaction."""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41
import golden_zipper_v51_memory_plasticity_panel as v51

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v52_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "local_rigid": dict(window_levels=1, window_blend_gain=0.00, plasticity_gain=0.00, anchor_gain=0.18),
    "local_balanced": dict(window_levels=1, window_blend_gain=0.00, plasticity_gain=0.12, anchor_gain=0.14),
    "nested_rigid": dict(window_levels=2, window_blend_gain=0.14, plasticity_gain=0.00, anchor_gain=0.18),
    "nested_balanced": dict(window_levels=2, window_blend_gain=0.14, plasticity_gain=0.12, anchor_gain=0.14),
    "nested_overplastic": dict(window_levels=2, window_blend_gain=0.14, plasticity_gain=0.24, anchor_gain=0.06),
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    fieldnames = []
    seen = set()
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
        selected.append((spec, dict(
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
            admission_center=float(row["best_admission_center"]),
            admission_width=float(row["best_admission_width"]),
            admission_gain=float(row["best_admission_gain"]),
            split_threshold=0.24,
        )))
    return selected


def main() -> None:
    ensure_dir(OUT)
    specs = load_best_conditions()
    rows = []
    for spec, base_kwargs in specs:
        for mode, config in MODES.items():
            recall_condition = v41.RecallCondition(**base_kwargs, window_levels=config["window_levels"], window_blend_gain=config["window_blend_gain"])
            seq, diag = v51.run_sequence(spec.alpha, spec.condition, recall_condition, "real", config["plasticity_gain"], config["anchor_gain"], False)
            metrics = v51.evaluate_recall(seq, diag)
            rows.append({"flow": spec.flow, "mode": mode, **metrics, "score": v41.score_recall(metrics)})

    write_csv(rows, OUT / "mode_metrics.csv")
    summary_rows = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        nb = next(row for row in subset if row["mode"] == "nested_balanced")
        summary_rows.append({
            "flow": flow,
            "nested_balanced_score": nb["score"],
            "rewrite_drift_rate": nb["rewrite_drift_rate"],
            "nested_balanced_vs_local_balanced_gap": nb["score"] - next(row for row in subset if row["mode"] == "local_balanced")["score"],
            "nested_balanced_vs_nested_rigid_gap": nb["score"] - next(row for row in subset if row["mode"] == "nested_rigid")["score"],
            "nested_balanced_vs_nested_overplastic_gap": nb["score"] - next(row for row in subset if row["mode"] == "nested_overplastic")["score"],
        })
    write_csv(summary_rows, OUT / "summary.csv")
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    write_text(OUT / "report.md", f"""# Golden Zipper v52 - Window Plasticity Interaction

Golden result:
- nested balanced score: `{golden['nested_balanced_score']:.3f}`
- rewrite drift rate: `{golden['rewrite_drift_rate']:.3f}`
- nested balanced vs local balanced gap: `{golden['nested_balanced_vs_local_balanced_gap']:.3f}`
- nested balanced vs nested rigid gap: `{golden['nested_balanced_vs_nested_rigid_gap']:.3f}`
- nested balanced vs nested overplastic gap: `{golden['nested_balanced_vs_nested_overplastic_gap']:.3f}`
""")
    print(f"files created: {OUT}")
    print(f"golden nested balanced score: {golden['nested_balanced_score']:.3f}")
    print(f"golden nested balanced vs local balanced gap: {golden['nested_balanced_vs_local_balanced_gap']:.3f}")
    print(f"golden nested balanced vs nested rigid gap: {golden['nested_balanced_vs_nested_rigid_gap']:.3f}")


if __name__ == "__main__":
    main()
