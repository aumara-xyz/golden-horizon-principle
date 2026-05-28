#!/usr/bin/env python3
"""v50 carry-forward shootout.

This compares the newest focused lanes to decide what to carry forward:
- v41b field stack
- v45 harsher prediction-error nulls
- v46 observer window ablation
- v48 window-band interaction
- v49 binding-band interaction
- v49b binding-band nulls

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v50_outputs"

SOURCES = {
    "v41b_field_stack": ROOT / "golden_zipper_v41b_outputs" / "summary.csv",
    "v45_harsher_prediction_error": ROOT / "golden_zipper_v45_outputs" / "summary.csv",
    "v46_window_ablation": ROOT / "golden_zipper_v46_outputs" / "summary.csv",
    "v48_window_band_interaction": ROOT / "golden_zipper_v48_outputs" / "summary.csv",
    "v49_binding_band_interaction": ROOT / "golden_zipper_v49_outputs" / "summary.csv",
    "v49b_binding_band_nulls": ROOT / "golden_zipper_v49b_outputs" / "summary.csv",
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


def pick_score(row: dict[str, str]) -> float:
    for key in ("real_score", "moderate_score", "nested_score", "nested_moderate_score", "real_moderate_score"):
        if key in row:
            return float(row[key])
    raise KeyError(row)


def pick_robustness(row: dict[str, str]) -> float:
    keys = [
        "no_binding_gap",
        "flat_binding_gap",
        "no_multiscale_gap",
        "no_band_gap",
        "wide_band_gap",
        "wrong_center_gap",
        "inverse_center_gap",
        "razor_band_gap",
        "nested_vs_local_gap",
        "nested_vs_blurred_local_gap",
        "nested_moderate_vs_local_moderate_gap",
        "nested_moderate_vs_nested_exact_gap",
        "nested_moderate_vs_nested_novelty_gap",
        "binding_help_under_moderate",
        "moderate_help_with_binding",
        "real_vs_shuffled_gap",
        "real_vs_flat_gap",
        "moderate_vs_no_band_gap",
    ]
    total = 0.0
    for key in keys:
        if key in row:
            total += float(row[key])
    return total


def main() -> None:
    ensure_dir(OUT)

    rows = []
    for lane, path in SOURCES.items():
        source_rows = list(csv.DictReader(path.open()))
        golden = next(row for row in source_rows if row["flow"] == "golden")
        rows.append(
            {
                "lane": lane,
                "golden_score": pick_score(golden),
                "golden_robustness": pick_robustness(golden),
            }
        )

    ranked = sorted(rows, key=lambda row: (row["golden_score"], row["golden_robustness"]), reverse=True)
    write_csv(ranked, OUT / "lane_summary.csv")

    best = ranked[0]
    report = f"""# Golden Zipper v50 - Carry Forward Shootout

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best carry-forward lane: `{best['lane']}` with score `{best['golden_score']:.3f}` and robustness `{best['golden_robustness']:.3f}`

Ranking:
""" + "\n".join(
        f"- `{row['lane']}`: score `{row['golden_score']:.3f}`, robustness `{row['golden_robustness']:.3f}`"
        for row in ranked
    ) + "\n"
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best carry-forward lane: {best['lane']} {best['golden_score']:.3f}")


if __name__ == "__main__":
    main()
