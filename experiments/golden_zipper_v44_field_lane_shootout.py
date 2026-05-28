#!/usr/bin/env python3
"""v44 field-lane shootout.

This compares the recent field-memory lanes on one shared readout:
- v37 relational field identity
- v38 field phase binding
- v39 multiscale observer window
- v40 multiscale phase binding
- v41 prediction-band binding
- v42 prediction-error field
- v43 competition pressure

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v44_outputs"

SOURCES = {
    "v37_field_presence": ROOT / "golden_zipper_v37_outputs" / "summary.csv",
    "v38_phase_binding": ROOT / "golden_zipper_v38_outputs" / "summary.csv",
    "v39_multiscale_window": ROOT / "golden_zipper_v39_outputs" / "summary.csv",
    "v40_multiscale_binding": ROOT / "golden_zipper_v40_outputs" / "summary.csv",
    "v41_admission_band": ROOT / "golden_zipper_v41_outputs" / "summary.csv",
    "v42_prediction_error": ROOT / "golden_zipper_v42_outputs" / "summary.csv",
    "v43_competition_pressure": ROOT / "golden_zipper_v43_outputs" / "summary.csv",
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
    for key in ("mean_score", "moderate_score", "balanced_score", "real_score"):
        if key in row:
            return float(row[key])
    if "best_score" in row:
        return float(row["best_score"])
    raise KeyError(f"no score field in row: {row}")


def pick_gap(row: dict[str, str]) -> float:
    for key in ("density_gap", "moderate_vs_none_gap", "balanced_vs_no_rival_gap", "no_binding_gap"):
        if key in row:
            return float(row[key])
    return 0.0


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
                "golden_gap": pick_gap(golden),
            }
        )

    ranked = sorted(rows, key=lambda row: (row["golden_score"], row["golden_gap"]), reverse=True)
    write_csv(ranked, OUT / "lane_summary.csv")

    best = ranked[0]
    report = f"""# Golden Zipper v44 - Field Lane Shootout

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best golden lane: `{best['lane']}` with score `{best['golden_score']:.3f}` and gap `{best['golden_gap']:.3f}`

Ranking:
""" + "\n".join(
        f"- `{row['lane']}`: score `{row['golden_score']:.3f}`, gap `{row['golden_gap']:.3f}`"
        for row in ranked
    ) + "\n"
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best golden lane: {best['lane']} {best['golden_score']:.3f}")


if __name__ == "__main__":
    main()
