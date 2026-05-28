#!/usr/bin/env python3
"""v65 field presence vs smoothing."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v65_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"
MODES = ("real_field", "delta_slot", "flat_local", "global_smooth")


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
                    similarity_threshold=float(row["best_similarity_THRESHOLD"]) if "best_similarity_THRESHOLD" in row else float(row["best_similarity_threshold"]),
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


def delta_weights(center: int, slot_count: int, radius: int, width: float) -> np.ndarray:
    weights = np.zeros(slot_count, dtype=float)
    weights[center] = 1.0
    return weights


def flat_local_weights(center: int, slot_count: int, radius: int, width: float) -> np.ndarray:
    weights = np.zeros(slot_count, dtype=float)
    for idx in range(slot_count):
        distance = min((idx - center) % slot_count, (center - idx) % slot_count)
        if distance <= radius:
            weights[idx] = 1.0
    total = weights.sum()
    if total > 0:
        weights /= total
    return weights


def global_smooth_weights(center: int, slot_count: int, radius: int, width: float) -> np.ndarray:
    return np.full(slot_count, 1.0 / slot_count, dtype=float)


WEIGHT_FNS = {
    "real_field": v41.field_weights,
    "delta_slot": delta_weights,
    "flat_local": flat_local_weights,
    "global_smooth": global_smooth_weights,
}


def main() -> None:
    ensure_dir(OUT)
    specs = load_best_conditions()
    rows = []
    original_field_weights = v41.field_weights
    try:
        for spec, recall_condition in specs:
            for mode in MODES:
                v41.field_weights = WEIGHT_FNS[mode]
                seq, diag = v41.build_field_sequence(spec.alpha, spec.condition, recall_condition)
                metrics = v41.evaluate_recall(seq, diag)
                rows.append({"flow": spec.flow, "family": spec.family, "mode": mode, **metrics, "score": v41.score_recall(metrics)})
    finally:
        v41.field_weights = original_field_weights

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        real = next(row for row in subset if row["mode"] == "real_field")
        summary_rows.append(
            {
                "flow": flow,
                "real_score": real["score"],
                "same_field_recall_rate": real["same_field_recall_rate"],
                "same_core_recall_rate": real["same_core_recall_rate"],
                "real_vs_delta_gap": real["score"] - next(row for row in subset if row["mode"] == "delta_slot")["score"],
                "real_vs_flat_gap": real["score"] - next(row for row in subset if row["mode"] == "flat_local")["score"],
                "real_vs_global_gap": real["score"] - next(row for row in subset if row["mode"] == "global_smooth")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v65 - Field Presence vs Smoothing

Golden result:
- real score: `{golden['real_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- real vs delta gap: `{golden['real_vs_delta_gap']:.3f}`
- real vs flat gap: `{golden['real_vs_flat_gap']:.3f}`
- real vs global gap: `{golden['real_vs_global_gap']:.3f}`
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"golden real score: {golden['real_score']:.3f}")
    print(f"golden real vs delta gap: {golden['real_vs_delta_gap']:.3f}")
    print(f"golden real vs flat gap: {golden['real_vs_flat_gap']:.3f}")
    print(f"golden real vs global gap: {golden['real_vs_global_gap']:.3f}")


if __name__ == "__main__":
    main()
