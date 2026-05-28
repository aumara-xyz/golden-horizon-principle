#!/usr/bin/env python3
"""v61 field-stack harsher nulls.

Push harder on the best carry-forward lane:
- real stack
- no binding
- shuffled phase
- no multiscale
- no band
- exact-match band
- novelty-heavy band
- wrong-center band
- razor-thin band
"""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41
import golden_zipper_v41b_field_binding_stack_nulls as v41b


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v61_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = [
    "real",
    "no_binding",
    "shuffled_phase",
    "no_multiscale",
    "no_band",
    "exact_band",
    "novelty_band",
    "wrong_center_band",
    "razor_band",
]


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


def tweak_condition(condition: v41.RecallCondition, mode: str) -> v41.RecallCondition:
    if mode == "exact_band":
        return v41.RecallCondition(**{**condition.__dict__, "admission_center": 0.00})
    if mode == "novelty_band":
        return v41.RecallCondition(**{**condition.__dict__, "admission_center": 0.35})
    if mode == "wrong_center_band":
        return v41.RecallCondition(**{**condition.__dict__, "admission_center": 0.55})
    if mode == "razor_band":
        return v41.RecallCondition(**{**condition.__dict__, "admission_width": 0.06})
    return condition


def base_mode(mode: str) -> str:
    if mode in {"exact_band", "novelty_band", "wrong_center_band", "razor_band"}:
        return "real"
    return mode


def main() -> None:
    ensure_dir(OUT)
    specs = load_best_conditions()
    rows = []
    for spec, recall_condition in specs:
        for mode in MODES:
            run_mode = base_mode(mode)
            tweaked = tweak_condition(recall_condition, mode)
            seq, diag = v41b.run_sequence(spec.alpha, spec.condition, tweaked, run_mode)
            metrics = v41b.evaluate_recall(seq, diag)
            rows.append({"flow": spec.flow, "family": spec.family, "mode": mode, **metrics, "score": v41.score_recall(metrics)})

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        real = next(row for row in subset if row["mode"] == "real")
        summary_rows.append(
            {
                "flow": flow,
                "real_score": real["score"],
                "same_field_recall_rate": real["same_field_recall_rate"],
                "same_core_recall_rate": real["same_core_recall_rate"],
                "no_binding_gap": real["score"] - next(row for row in subset if row["mode"] == "no_binding")["score"],
                "shuffled_phase_gap": real["score"] - next(row for row in subset if row["mode"] == "shuffled_phase")["score"],
                "no_multiscale_gap": real["score"] - next(row for row in subset if row["mode"] == "no_multiscale")["score"],
                "no_band_gap": real["score"] - next(row for row in subset if row["mode"] == "no_band")["score"],
                "exact_band_gap": real["score"] - next(row for row in subset if row["mode"] == "exact_band")["score"],
                "novelty_band_gap": real["score"] - next(row for row in subset if row["mode"] == "novelty_band")["score"],
                "wrong_center_gap": real["score"] - next(row for row in subset if row["mode"] == "wrong_center_band")["score"],
                "razor_band_gap": real["score"] - next(row for row in subset if row["mode"] == "razor_band")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v61 - Field Stack Harsher Nulls

Golden result:
- real score: `{golden['real_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- no-binding gap: `{golden['no_binding_gap']:.3f}`
- shuffled-phase gap: `{golden['shuffled_phase_gap']:.3f}`
- no-multiscale gap: `{golden['no_multiscale_gap']:.3f}`
- no-band gap: `{golden['no_band_gap']:.3f}`
- exact-band gap: `{golden['exact_band_gap']:.3f}`
- novelty-band gap: `{golden['novelty_band_gap']:.3f}`
- wrong-center gap: `{golden['wrong_center_gap']:.3f}`
- razor-band gap: `{golden['razor_band_gap']:.3f}`
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"golden real score: {golden['real_score']:.3f}")
    print(f"golden no-binding gap: {golden['no_binding_gap']:.3f}")
    print(f"golden shuffled-phase gap: {golden['shuffled_phase_gap']:.3f}")
    print(f"golden wrong-center gap: {golden['wrong_center_gap']:.3f}")


if __name__ == "__main__":
    main()
