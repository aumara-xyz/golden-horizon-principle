#!/usr/bin/env python3
"""v45 harsher prediction-error nulls.

This attacks the v42 admission-band object harder:
- moderate band
- over-wide band
- wrong-center band
- no band
- inverse-center band
- razor-thin band

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v45_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "moderate_band": (0.20, 0.18, 0.14),
    "wide_band": (0.20, 0.45, 0.14),
    "wrong_center": (0.45, 0.18, 0.14),
    "no_band": (0.20, 0.18, 0.00),
    "inverse_center": (0.65, 0.18, 0.14),
    "razor_band": (0.20, 0.04, 0.14),
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
        for mode, (center, width, gain) in MODES.items():
            recall_condition = v41.RecallCondition(
                admission_center=center,
                admission_width=width,
                admission_gain=gain,
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
        moderate = next(row for row in subset if row["mode"] == "moderate_band")
        summary_rows.append(
            {
                "flow": flow,
                "moderate_score": moderate["score"],
                "same_field_recall_rate": moderate["same_field_recall_rate"],
                "split_rate": moderate["split_rate"],
                "wide_band_gap": moderate["score"] - next(row for row in subset if row["mode"] == "wide_band")["score"],
                "wrong_center_gap": moderate["score"] - next(row for row in subset if row["mode"] == "wrong_center")["score"],
                "no_band_gap": moderate["score"] - next(row for row in subset if row["mode"] == "no_band")["score"],
                "inverse_center_gap": moderate["score"] - next(row for row in subset if row["mode"] == "inverse_center")["score"],
                "razor_band_gap": moderate["score"] - next(row for row in subset if row["mode"] == "razor_band")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["moderate_score"], reverse=True)
    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")

    report = f"""# Golden Zipper v45 - Harsher Prediction Error Nulls

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by moderate-band score: `{best['flow']}` with `{best['moderate_score']:.3f}`

Golden result:
- moderate score: `{golden['moderate_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- wide-band gap: `{golden['wide_band_gap']:.3f}`
- wrong-center gap: `{golden['wrong_center_gap']:.3f}`
- no-band gap: `{golden['no_band_gap']:.3f}`
- inverse-center gap: `{golden['inverse_center_gap']:.3f}`
- razor-band gap: `{golden['razor_band_gap']:.3f}`

Interpretation:
- This panel checks whether the moderate mismatch band is doing more than simply widening or moving the gate.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by moderate-band score: {best['flow']} {best['moderate_score']:.3f}")
    print(f"golden moderate score: {golden['moderate_score']:.3f}")
    print(f"golden wide-band gap: {golden['wide_band_gap']:.3f}")
    print(f"golden wrong-center gap: {golden['wrong_center_gap']:.3f}")
    print(f"golden no-band gap: {golden['no_band_gap']:.3f}")
    print(f"golden inverse-center gap: {golden['inverse_center_gap']:.3f}")
    print(f"golden razor-band gap: {golden['razor_band_gap']:.3f}")


if __name__ == "__main__":
    main()
