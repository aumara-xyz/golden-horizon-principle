#!/usr/bin/env python3
"""v43 two-memory field competition.

This approximates two memory-fields competing for the same relational space:
- no rival pressure
- balanced rival pressure
- strong rival pressure
- absorbing rival pressure

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v43_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

MODES = {
    "no_rival": (1.00, 0.00),
    "balanced_rival": (1.00, 1.00),
    "strong_rival": (0.80, 2.00),
    "absorbing_rival": (0.50, 3.00),
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
        for mode, (support_scale, competition_scale) in MODES.items():
            recall_condition = v41.RecallCondition(
                field_support_gain=base_kwargs["field_support_gain"] * support_scale,
                field_competition_gain=base_kwargs["field_competition_gain"] * competition_scale,
                **{k: v for k, v in base_kwargs.items() if k not in {"field_support_gain", "field_competition_gain"}},
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
        balanced = next(row for row in subset if row["mode"] == "balanced_rival")
        no_rival = next(row for row in subset if row["mode"] == "no_rival")
        strong = next(row for row in subset if row["mode"] == "strong_rival")
        absorbing = next(row for row in subset if row["mode"] == "absorbing_rival")
        best = max(subset, key=lambda row: row["score"])
        summary_rows.append(
            {
                "flow": flow,
                "best_mode": best["mode"],
                "balanced_score": balanced["score"],
                "same_field_recall_rate": balanced["same_field_recall_rate"],
                "same_core_recall_rate": balanced["same_core_recall_rate"],
                "split_rate": balanced["split_rate"],
                "balanced_vs_no_rival_gap": balanced["score"] - no_rival["score"],
                "balanced_vs_strong_gap": balanced["score"] - strong["score"],
                "balanced_vs_absorbing_gap": balanced["score"] - absorbing["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["balanced_score"], reverse=True)
    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")

    report = f"""# Golden Zipper v43 - Two Memory Field Competition

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by balanced-rival score: `{best['flow']}` with `{best['balanced_score']:.3f}`

Golden result:
- best mode: `{golden['best_mode']}`
- balanced score: `{golden['balanced_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- balanced vs no-rival gap: `{golden['balanced_vs_no_rival_gap']:.3f}`
- balanced vs strong-rival gap: `{golden['balanced_vs_strong_gap']:.3f}`
- balanced vs absorbing-rival gap: `{golden['balanced_vs_absorbing_gap']:.3f}`

Interpretation:
- This panel asks how much rival field pressure the memory-field can tolerate before identity starts to collapse.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by balanced-rival score: {best['flow']} {best['balanced_score']:.3f}")
    print(f"golden best mode: {golden['best_mode']}")
    print(f"golden balanced score: {golden['balanced_score']:.3f}")
    print(f"golden balanced vs no-rival gap: {golden['balanced_vs_no_rival_gap']:.3f}")
    print(f"golden balanced vs strong-rival gap: {golden['balanced_vs_strong_gap']:.3f}")
    print(f"golden balanced vs absorbing-rival gap: {golden['balanced_vs_absorbing_gap']:.3f}")


if __name__ == "__main__":
    main()
