#!/usr/bin/env python3
"""v47 field binding vs prediction error shootout.

This compares the focused late-stage lanes:
- v41b field-binding stack nulls
- v42 prediction-error field
- v45 harsher prediction-error nulls
- v46 observer window ablation

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v47_outputs"

SOURCES = {
    "v41b_field_stack": ROOT / "golden_zipper_v41b_outputs" / "summary.csv",
    "v42_prediction_error": ROOT / "golden_zipper_v42_outputs" / "summary.csv",
    "v45_harsher_prediction_error": ROOT / "golden_zipper_v45_outputs" / "summary.csv",
    "v46_window_ablation": ROOT / "golden_zipper_v46_outputs" / "summary.csv",
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
    for key in ("moderate_score", "nested_score", "real_score"):
        if key in row:
            return float(row[key])
    raise KeyError(row)


def pick_robustness(row: dict[str, str]) -> float:
    if "wide_band_gap" in row:
        return (
            float(row.get("wide_band_gap", 0.0))
            + float(row.get("wrong_center_gap", 0.0))
            + float(row.get("no_band_gap", 0.0))
            + float(row.get("inverse_center_gap", 0.0))
            + float(row.get("razor_band_gap", 0.0))
        )
    if "nested_vs_local_gap" in row:
        return (
            float(row.get("nested_vs_local_gap", 0.0))
            + float(row.get("nested_vs_over_blended_gap", 0.0))
            + float(row.get("nested_vs_blurred_local_gap", 0.0))
        )
    return (
        float(row.get("no_binding_gap", 0.0))
        + float(row.get("flat_binding_gap", 0.0))
        + float(row.get("no_multiscale_gap", 0.0))
        + float(row.get("no_band_gap", 0.0))
    )


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
    report = f"""# Golden Zipper v47 - Field Binding vs Prediction Error Shootout

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best golden lane: `{best['lane']}` with score `{best['golden_score']:.3f}` and robustness `{best['golden_robustness']:.3f}`

Ranking:
""" + "\n".join(
        f"- `{row['lane']}`: score `{row['golden_score']:.3f}`, robustness `{row['golden_robustness']:.3f}`"
        for row in ranked
    ) + "\n"
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best golden lane: {best['lane']} {best['golden_score']:.3f}")


if __name__ == "__main__":
    main()
