#!/usr/bin/env python3
"""Summarize the registered zero-blind N(x) path artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import median

import mpmath as mp

import weil_core as core
from run_n_paths import DPS, MULTIPLIERS, X_GRID, artifact_name


HERE = Path(__file__).resolve().parent
OUT = HERE / "n-paths-summary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def secular_derivative(z: mp.mpf, full: mp.matrix, length: mp.mpf) -> mp.mpf:
    n_max = (full.rows - 1) // 2
    total = -full[n_max] / (z * z)
    for n in range(1, n_max + 1):
        lattice = 2 * mp.pi * n / length
        coefficient = full[n_max + n]
        total -= 2 * coefficient * (z * z + lattice * lattice) / (
            z * z - lattice * lattice
        ) ** 2
    return mp.re(total)


def nearest_index_mismatches(left: list[mp.mpf], right: list[mp.mpf]) -> int:
    return sum(
        min(range(len(right)), key=lambda k: abs(right[k] - value)) != j
        for j, value in enumerate(left)
    )


def comparison(a: dict, b: dict, kind: str) -> dict:
    left = a["roots_mp"]
    right = b["roots_mp"]
    displacements = [abs(u - v) for u, v in zip(left, right)]
    frozen_band = displacements[19:50]
    return {
        "kind": kind,
        "left": {"x": a["x"], "N": a["N"], "path_multiplier": a["path_multiplier"]},
        "right": {"x": b["x"], "N": b["N"], "path_multiplier": b["path_multiplier"]},
        "max_displacement_roots_1_60": mp.nstr(max(displacements), 30),
        "median_displacement_roots_1_60": mp.nstr(median(displacements), 30),
        "max_displacement_ordinals_20_50": mp.nstr(max(frozen_band), 30),
        "median_displacement_ordinals_20_50": mp.nstr(median(frozen_band), 30),
        "nearest_ordinal_mismatches_roots_1_60": nearest_index_mismatches(left, right),
    }


def main() -> None:
    mp.mp.dps = DPS
    rows = []
    internal = {}
    for x in X_GRID:
        for multiplier in MULTIPLIERS:
            n_max = multiplier * x
            path = HERE / artifact_name(x, n_max)
            payload = json.loads(path.read_text())
            roots = [mp.mpf(value) for value in payload["positive_roots"][:60]]
            if len(roots) != 60 or any(b <= a for a, b in zip(roots, roots[1:])):
                raise RuntimeError(f"root ordering failed in {path.name}")
            if payload.get("target_data_present") is not False or payload.get(
                "scoring_present"
            ) is not False:
                raise RuntimeError(f"blindness audit failed in {path.name}")

            even = [mp.mpf(value) for value in payload["eigensolve"]["first_even_values"]]
            odd = [mp.mpf(value) for value in payload["eigensolve"]["first_odd_values"]]
            if len(even) < 2 or not odd:
                raise RuntimeError(f"low-spectrum output incomplete in {path.name}")
            gap = min(even[1], odd[0]) - even[0]
            residual = mp.mpf(payload["eigensolve"]["residual_norm"])
            vector = mp.matrix(
                [mp.mpf(value) for value in payload["even_unit_vector"]]
            )
            full = core.full_coefficients_from_even_mp(vector)
            length = mp.log(x)
            derivatives = [abs(secular_derivative(root, full, length)) for root in roots]
            lattice_step = 2 * mp.pi / length
            pole_distances = [
                min(abs(root - round(root / lattice_step) * lattice_step), lattice_step)
                for root in roots
            ]
            root_residuals = [mp.mpf(value) for value in payload["root_transform_residuals"][:60]]
            row = {
                "x": x,
                "path_multiplier": multiplier,
                "N": n_max,
                "dps": DPS,
                "artifact": path.name,
                "artifact_sha256": sha256(path),
                "reused_exact_grid_artifact": path.name != f"npath-x{x}-N{n_max}-dps{DPS}.json",
                "target_data_present": False,
                "scoring_present": False,
                "term_count": len(payload["terms"]),
                "low_spectrum": {
                    "even_1": mp.nstr(even[0], DPS),
                    "even_2": mp.nstr(even[1], DPS),
                    "odd_1": mp.nstr(odd[0], DPS),
                    "gap_to_nearest_competitor": mp.nstr(gap, DPS),
                    "even_ground_strictly_first": bool(gap > 0),
                    "ground_residual_norm": mp.nstr(residual, DPS),
                    "residual_over_gap": mp.nstr(residual / gap, 30),
                    "resolved_decimal_margin": float(-mp.log10(residual / gap)),
                },
                "root_diagnostics": {
                    "count": len(roots),
                    "strictly_positive_and_ordered": True,
                    "minimum_neighbor_spacing": mp.nstr(
                        min(b - a for a, b in zip(roots, roots[1:])), 30
                    ),
                    "minimum_absolute_secular_derivative": mp.nstr(min(derivatives), 30),
                    "minimum_distance_to_intrinsic_lattice_pole": mp.nstr(
                        min(pole_distances), 30
                    ),
                    "maximum_transform_residual": mp.nstr(max(root_residuals), 30),
                    "finite_simple_root_diagnostic": bool(
                        min(derivatives) > mp.mpf("1e-80")
                        and min(pole_distances) > mp.mpf("1e-80")
                    ),
                },
                "positive_roots": [mp.nstr(root, DPS) for root in roots],
            }
            rows.append(row)
            internal[(x, multiplier)] = {**row, "roots_mp": roots}

    fixed_x = []
    for x in X_GRID:
        fixed_x.append(
            comparison(internal[(x, 8)], internal[(x, 10)], "fixed x, 8x to 10x")
        )
        fixed_x.append(
            comparison(internal[(x, 10)], internal[(x, 12)], "fixed x, 10x to 12x")
        )
    along_path = []
    for multiplier in MULTIPLIERS:
        for x_left, x_right in zip(X_GRID, X_GRID[1:]):
            along_path.append(
                comparison(
                    internal[(x_left, multiplier)],
                    internal[(x_right, multiplier)],
                    f"path {multiplier}x, adjacent cutoff",
                )
            )

    n_band = [mp.mpf(item["max_displacement_ordinals_20_50"]) for item in fixed_x]
    x_band = [mp.mpf(item["max_displacement_ordinals_20_50"]) for item in along_path]
    local_N_vs_cutoff = []
    for x in X_GRID[:-1]:
        n_items = [item for item in fixed_x if item["left"]["x"] == x]
        x_items = [item for item in along_path if item["left"]["x"] == x]
        largest_n_shift = max(
            mp.mpf(item["max_displacement_ordinals_20_50"]) for item in n_items
        )
        smallest_path_cutoff_shift = min(
            mp.mpf(item["max_displacement_ordinals_20_50"]) for item in x_items
        )
        local_N_vs_cutoff.append(
            {
                "x": x,
                "largest_fixed_x_N_shift_ordinals_20_50": mp.nstr(
                    largest_n_shift, 30
                ),
                "smallest_path_shift_for_x_to_x_plus_2_ordinals_20_50": mp.nstr(
                    smallest_path_cutoff_shift, 30
                ),
                "N_shift_is_smaller": bool(largest_n_shift < smallest_path_cutoff_shift),
            }
        )

    check_path = HERE / "npath-x16-N192-dps140-check.json"
    check = json.loads(check_path.read_text())
    baseline = internal[(16, 12)]
    check_roots = [mp.mpf(value) for value in check["positive_roots"][:60]]
    check_displacements = [
        abs(a - b) for a, b in zip(baseline["roots_mp"], check_roots)
    ]
    precision_spot_check = {
        "x": 16,
        "N": 192,
        "baseline_dps": 100,
        "repeat_dps": 140,
        "repeat_artifact": check_path.name,
        "repeat_artifact_sha256": sha256(check_path),
        "repeat_method": check["eigensolve"]["method"],
        "absolute_ground_eigenvalue_displacement": mp.nstr(
            abs(
                mp.mpf(baseline["low_spectrum"]["even_1"])
                - mp.mpf(check["eigensolve"]["minimum"])
            ),
            50,
        ),
        "maximum_root_displacement_1_60": mp.nstr(max(check_displacements), 50),
        "maximum_root_displacement_ordinals_20_50": mp.nstr(
            max(check_displacements[19:50]), 50
        ),
        "repeat_ground_residual_norm": check["eigensolve"]["residual_norm"],
        "repeat_maximum_transform_residual": mp.nstr(
            max(mp.mpf(value) for value in check["root_transform_residuals"][:60]),
            50,
        ),
        "target_data_present": check.get("target_data_present"),
        "scoring_present": check.get("scoring_present"),
    }

    enumerator_mutations = []
    for x, multiplier in ((8, 12), (16, 12)):
        baseline = internal[(x, multiplier)]
        payload = json.loads((HERE / baseline["artifact"]).read_text())
        vector = mp.matrix(
            [mp.mpf(value) for value in payload["even_unit_vector"]]
        )
        full = core.full_coefficients_from_even_mp(vector)
        repeated_roots = core.enumerate_positive_roots_mp(
            full, mp.log(x), 60, subdivisions=64
        )
        displacement = [
            abs(a - b) for a, b in zip(baseline["roots_mp"], repeated_roots)
        ]
        enumerator_mutations.append(
            {
                "x": x,
                "N": multiplier * x,
                "baseline_subdivisions_per_lattice_interval": 32,
                "mutation_subdivisions_per_lattice_interval": 64,
                "repeated_root_count": len(repeated_roots),
                "maximum_root_displacement_1_60": mp.nstr(max(displacement), 50),
                "maximum_root_displacement_ordinals_20_50": mp.nstr(
                    max(displacement[19:50]), 50
                ),
            }
        )
    result = {
        "schema": "codex-r5-zero-blind-n-paths-v1",
        "status": "MEASURED",
        "construction": "authentic prime-power finite Weil matrices",
        "registered_x": list(X_GRID),
        "registered_path_multipliers": list(MULTIPLIERS),
        "precision_dps": DPS,
        "root_enumerator": "sign brackets inside successive intrinsic Fourier-lattice intervals, followed by arbitrary-precision refinement",
        "target_data_present": False,
        "scoring_present": False,
        "cases": rows,
        "fixed_x_N_convergence": fixed_x,
        "along_path_cutoff_continuity": along_path,
        "local_N_vs_cutoff_comparison": local_N_vs_cutoff,
        "precision_spot_check": precision_spot_check,
        "root_enumerator_mutations": enumerator_mutations,
        "aggregate": {
            "all_cases_have_60_positive_ordered_simple_diagnostic_roots": all(
                row["root_diagnostics"]["finite_simple_root_diagnostic"] for row in rows
            ),
            "all_cases_have_strict_even_ground_ordering": all(
                row["low_spectrum"]["even_ground_strictly_first"] for row in rows
            ),
            "all_fixed_x_nearest_ordinal_mismatch_counts_zero": all(
                item["nearest_ordinal_mismatches_roots_1_60"] == 0 for item in fixed_x
            ),
            "all_along_path_nearest_ordinal_mismatch_counts_zero": all(
                item["nearest_ordinal_mismatches_roots_1_60"] == 0 for item in along_path
            ),
            "maximum_fixed_x_N_displacement_ordinals_20_50": mp.nstr(max(n_band), 30),
            "median_fixed_x_N_max_displacement_ordinals_20_50": mp.nstr(median(n_band), 30),
            "minimum_adjacent_x_displacement_ordinals_20_50": mp.nstr(min(x_band), 30),
            "median_adjacent_x_max_displacement_ordinals_20_50": mp.nstr(median(x_band), 30),
            "every_fixed_x_N_change_smaller_than_every_adjacent_x_change": bool(
                max(n_band) < min(x_band)
            ),
            "at_each_available_x_N_change_smaller_than_local_x_plus_2_change": all(
                item["N_shift_is_smaller"] for item in local_N_vs_cutoff
            ),
        },
        "runner_sha256": sha256(HERE / "run_n_paths.py"),
        "summarizer_sha256": sha256(Path(__file__)),
        "core_sha256": sha256(HERE / "weil_core.py"),
    }
    core.write_json(OUT, result)
    print(json.dumps(result["aggregate"], indent=2))


if __name__ == "__main__":
    main()
