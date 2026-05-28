#!/usr/bin/env python3
"""Focused regime surface for Fibonacci vs generic ternary under uniform helper smear.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import ghp_boundary_access_noise_regime_hardening as hardening


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_uniform_regime_surface_outputs"

NOISE_LEVELS = [0.0, 0.10, 0.20, 0.30, 0.40, 0.55, 0.70]
ACCESS_COSTS = [0.00, 0.02, 0.05]
FAMILIES = ["fibonacci", "generic_ternary"]
VIEWS = ["balanced", "access_heavy", "repair_heavy", "identity_heavy"]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict[str, float | str]], path: Path) -> None:
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
    words = hardening.build_words()
    vocab = hardening.base.collect_vocabulary(words, hardening.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    base_rows: list[dict[str, float | str]] = []
    for noise_level in NOISE_LEVELS:
        scenario = {
            "name": f"uniform_{noise_level:.2f}",
            "helper_kind": "uniform_mix",
            "noise_level": noise_level,
        }
        for family_name in FAMILIES:
            metrics = hardening.evaluate_family_scenario(family_name, scenario, words, vocab_index)
            metrics["noise_level"] = noise_level
            base_rows.append(metrics)

    surface_rows: list[dict[str, float | str]] = []
    for access_cost in ACCESS_COSTS:
        for noise_level in NOISE_LEVELS:
            subset = [row for row in base_rows if float(row["noise_level"]) == noise_level]
            for view in VIEWS:
                key = f"score_{view}"
                best = max(subset, key=lambda row: float(row[key]) - access_cost)
                fib = next(row for row in subset if row["family"] == "fibonacci")
                tern = next(row for row in subset if row["family"] == "generic_ternary")
                surface_rows.append(
                    {
                        "access_cost": access_cost,
                        "noise_level": noise_level,
                        "view": view,
                        "winner": best["family"],
                        "fibonacci_net": float(fib[key]) - access_cost,
                        "generic_ternary_net": float(tern[key]) - access_cost,
                        "margin": (float(fib[key]) - access_cost) - (float(tern[key]) - access_cost),
                    }
                )

    write_csv(base_rows, OUT / "uniform_regime_base_metrics.csv")
    write_csv(surface_rows, OUT / "uniform_regime_surface.csv")

    lines = [
        "# Boundary Access Uniform Regime Surface",
        "",
        "Winner by noise level and score view:",
    ]
    for access_cost in ACCESS_COSTS:
        lines.append("")
        lines.append(f"- access cost `{access_cost}`")
        for noise_level in NOISE_LEVELS:
            subset = [
                row for row in surface_rows
                if float(row["access_cost"]) == access_cost and float(row["noise_level"]) == noise_level
            ]
            bits = [f"{row['view']}=`{row['winner']}`" for row in subset]
            lines.append(f"  - noise `{noise_level}`: " + ", ".join(bits))
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
