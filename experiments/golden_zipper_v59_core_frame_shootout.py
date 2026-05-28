#!/usr/bin/env python3
"""v59 core-frame carry-forward shootout."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v59_outputs"

SOURCES = {
    "v41b_field_stack": ROOT / "golden_zipper_v41b_outputs" / "summary.csv",
    "v48_window_band": ROOT / "golden_zipper_v48_outputs" / "summary.csv",
    "v58_core_frame": ROOT / "golden_zipper_v58_outputs" / "summary.csv",
    "v58b_core_frame_nulls": ROOT / "golden_zipper_v58b_outputs" / "summary.csv",
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
    for key in ("real_score", "nested_moderate_score", "balanced_score"):
        if key in row:
            return float(row[key])
    raise KeyError(row)


def pick_robustness(row: dict[str, str]) -> float:
    keys = (
        "no_binding_gap",
        "shuffled_phase_gap",
        "flat_binding_gap",
        "no_multiscale_gap",
        "no_band_gap",
        "nested_moderate_vs_local_moderate_gap",
        "nested_moderate_vs_nested_exact_gap",
        "nested_moderate_vs_nested_novelty_gap",
        "balanced_vs_rigid_gap",
        "balanced_vs_touchup_gap",
        "balanced_vs_overwash_gap",
        "balanced_vs_random_gap",
    )
    return sum(float(row[k]) for k in keys if k in row)


def main() -> None:
    ensure_dir(OUT)
    rows = []
    for lane, path in SOURCES.items():
        source_rows = list(csv.DictReader(path.open()))
        golden = next(row for row in source_rows if row["flow"] == "golden")
        rows.append({"lane": lane, "golden_score": pick_score(golden), "golden_robustness": pick_robustness(golden)})

    ranked = sorted(rows, key=lambda row: (row["golden_score"], row["golden_robustness"]), reverse=True)
    write_csv(ranked, OUT / "lane_summary.csv")
    best = ranked[0]
    report_lines = [
        "# Golden Zipper v59 - Core Frame Carry Forward Shootout",
        "",
        f"Best carry-forward lane: `{best['lane']}` score `{best['golden_score']:.3f}` robustness `{best['golden_robustness']:.3f}`",
        "",
    ]
    report_lines.extend(
        f"- `{row['lane']}`: score `{row['golden_score']:.3f}`, robustness `{row['golden_robustness']:.3f}`"
        for row in ranked
    )
    write_text(OUT / "report.md", "\n".join(report_lines) + "\n")
    print(f"files created: {OUT}")
    print(f"best carry-forward lane: {best['lane']} {best['golden_score']:.3f}")


if __name__ == "__main__":
    main()
