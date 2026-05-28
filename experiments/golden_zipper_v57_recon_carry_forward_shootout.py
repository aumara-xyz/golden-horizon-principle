#!/usr/bin/env python3
"""v57 recon carry-forward shootout."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v57_outputs"
SOURCES = {
    "v41b_field_stack": ROOT / "golden_zipper_v41b_outputs" / "summary.csv",
    "v48_window_band": ROOT / "golden_zipper_v48_outputs" / "summary.csv",
    "v56_dual_recon": ROOT / "golden_zipper_v56_outputs" / "summary.csv",
    "v56b_dual_recon_nulls": ROOT / "golden_zipper_v56b_outputs" / "summary.csv",
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


def pick_score(row):
    for key in ("real_score","nested_moderate_score","dual_score"):
        if key in row:
            return float(row[key])
    raise KeyError(row)


def pick_robustness(row):
    keys=("no_binding_gap","flat_binding_gap","no_multiscale_gap","no_band_gap","nested_moderate_vs_local_moderate_gap","nested_moderate_vs_nested_exact_gap","nested_moderate_vs_nested_novelty_gap","dual_vs_rigid_gap","dual_vs_touchup_gap","dual_vs_meltheavy_gap","dual_vs_random_gap")
    return sum(float(row[k]) for k in keys if k in row)


def main() -> None:
    ensure_dir(OUT)
    rows=[]
    for lane, path in SOURCES.items():
        source_rows=list(csv.DictReader(path.open()))
        golden=next(row for row in source_rows if row["flow"]=="golden")
        rows.append({"lane": lane, "golden_score": pick_score(golden), "golden_robustness": pick_robustness(golden)})
    ranked=sorted(rows, key=lambda row: (row["golden_score"], row["golden_robustness"]), reverse=True)
    write_csv(ranked, OUT / "lane_summary.csv")
    best=ranked[0]
    write_text(OUT / "report.md", "# Golden Zipper v57 - Recon Carry Forward Shootout\n\n" + "\n".join(
        [f"Best lane: `{best['lane']}` score `{best['golden_score']:.3f}` robustness `{best['golden_robustness']:.3f}`",""] +
        [f"- `{row['lane']}`: score `{row['golden_score']:.3f}`, robustness `{row['golden_robustness']:.3f}`" for row in ranked]
    ) + "\n")
    print(f"files created: {OUT}")
    print(f"best lane: {best['lane']} {best['golden_score']:.3f}")


if __name__ == "__main__":
    main()
