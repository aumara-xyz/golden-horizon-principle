#!/usr/bin/env python3
"""v69 phi vs IIT bridge check."""

from __future__ import annotations

import csv
from pathlib import Path

import golden_zipper_v67_perturbational_coherence_cloud as v67


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v69_outputs"


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


def main() -> None:
    ensure_dir(OUT)
    rows: list[dict] = []
    for condition in v67.load_best_conditions():
        metrics = v67.simulate_echo(condition, "coherence_weighted_cloud")
        rows.append({"flow": condition.flow, "family": condition.family, **metrics})

    write_csv(rows, OUT / "flow_metrics.csv")
    ranked = sorted(rows, key=lambda row: row["score"], reverse=True)
    write_csv(ranked, OUT / "ranking.csv")
    golden_rank = next(idx for idx, row in enumerate(ranked, start=1) if row["flow"] == "golden")
    golden = next(row for row in ranked if row["flow"] == "golden")
    best = ranked[0]
    report = f"""# Golden Zipper v69 - Phi vs IIT Bridge Check

Best flow:
- `{best['flow']}` score `{best['score']:.3f}`

Golden:
- rank `{golden_rank}/{len(ranked)}`
- score `{golden['score']:.3f}`
- spread rate `{golden['spread_rate']:.3f}`
- differentiation score `{golden['differentiation_score']:.3f}`
- integration score `{golden['integration_score']:.3f}`
- recovery score `{golden['recovery_score']:.3f}`
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"best flow: {best['flow']} {best['score']:.3f}")
    print(f"golden rank: {golden_rank}/{len(ranked)}")
    print(f"golden score: {golden['score']:.3f}")


if __name__ == "__main__":
    main()
