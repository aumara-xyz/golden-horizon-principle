#!/usr/bin/env python3
"""Registered R5.3 grid using the exact analytic prolate E-map projection."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import time

import mpmath as mp

from run_prolate_exact_bridge import (
    _matrix_metrics,
    _reference_spectrum_or_solve,
    _serialize,
    double_projection_distance,
    exact_e_projection,
    phase_aligned_distance,
)
from run_prolate_only_control import high_precision_candidate
from weil_core import parity_blocks, prime_power_terms


HERE = Path(__file__).resolve().parent
X_GRID = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20)
FINAL_FIVE = (13, 14, 16, 18, 20)
PRIMARY_N = 120
MUTATION_N = (96, 144)
WORK_DPS = 180
PRIMARY_LMAX = 200
MUTATION_LMAX = 160


def _frobenius_norm(even: mp.matrix, odd: mp.matrix) -> mp.mpf:
    return mp.sqrt(
        mp.fsum(abs(even[row, column]) ** 2 for row in range(even.rows) for column in range(even.cols))
        + mp.fsum(abs(odd[row, column]) ** 2 for row in range(odd.rows) for column in range(odd.cols))
    )


def run_x_family(x: int) -> dict:
    started = time.perf_counter()
    with mp.workdps(WORK_DPS):
        primary_lmax = 240 if x >= 18 else PRIMARY_LMAX
        mutation_lmax = 200 if x >= 18 else MUTATION_LMAX
        print(f"x={x}: solving degree-{primary_lmax}/{mutation_lmax} prolate modes", flush=True)
        candidate = high_precision_candidate(x, primary_lmax)
        mutation_candidate = high_precision_candidate(x, mutation_lmax)
        n_values = (PRIMARY_N,) + (MUTATION_N if x in FINAL_FIVE else ())
        rows = []
        for n_max in n_values:
            print(f"x={x} N={n_max}: exact projection", flush=True)
            projection = exact_e_projection(candidate, n_max)
            mutation = exact_e_projection(mutation_candidate, n_max)
            cutoff_distance = phase_aligned_distance(projection["full"], mutation["full"])
            double_check = double_projection_distance(x, n_max, projection["full"])

            print(f"x={x} N={n_max}: Weil matrix / low spectrum", flush=True)
            even_matrix, odd_matrix, matrix_meta = parity_blocks(
                n_max, x, prime_power_terms(x), WORK_DPS
            )
            even_values, odd_values, ground, spectrum_source = _reference_spectrum_or_solve(
                x, n_max, even_matrix, odd_matrix
            )
            metrics = _matrix_metrics(
                even_matrix, odd_matrix, projection, even_values, odd_values, ground, x
            )
            even_projected_metrics = _matrix_metrics(
                even_matrix,
                odd_matrix,
                projection["even_projected"],
                even_values,
                odd_values,
                ground,
                x,
            )
            matrix_bound = _frobenius_norm(even_matrix, odd_matrix)
            # For unit vectors separated by delta, both the Rayleigh quotient
            # and residual map change by at most a small multiple of ||M||delta.
            # 4*||M||_F*delta is a conservative finite diagnostic bound.
            cutoff_action_bound = 4 * matrix_bound * cutoff_distance
            arithmetic_floor = matrix_bound * mp.power(10, -(WORK_DPS - 25))
            metrics["matrix_frobenius_bound"] = matrix_bound
            metrics["legendre_cutoff_action_bound"] = cutoff_action_bound
            metrics["arithmetic_precision_floor"] = arithmetic_floor
            metrics["residual_resolved_above_cutoff_bound"] = bool(
                metrics["residual"] > 10 * cutoff_action_bound
            )
            metrics["gap_resolved_above_arithmetic_floor"] = bool(
                metrics["gap"] > 100 * arithmetic_floor
            )
            metrics["ratio_status"] = (
                "MEASURED"
                if metrics["residual_resolved_above_cutoff_bound"]
                and metrics["gap_resolved_above_arithmetic_floor"]
                and metrics["gap"] > 0
                else "UNVERIFIED"
            )
            row = {
                "x": x,
                "lambda": mp.sqrt(x),
                "N": n_max,
                "working_decimal_digits": WORK_DPS,
                "legendre_cutoff": primary_lmax,
                "legendre_cutoff_mutation": mutation_lmax,
                "spectrum_source": spectrum_source,
                "matrix_meta": matrix_meta,
                "projection": {
                    "raw_norm": projection["raw_norm"],
                    "inversion_odd_norm": projection["inversion_odd_norm"],
                    "even_projected_raw_norm": projection["even_projected"]["raw_norm"],
                    "zero_integral_from_power_expansion": projection[
                        "integral_from_power_expansion"
                    ],
                    "legendre_cutoff_vector_distance": cutoff_distance,
                    "double_projection_check": double_check,
                },
                "metrics": metrics,
                "even_projected_mutation_metrics": even_projected_metrics,
            }
            rows.append(_serialize(row))
            print(
                f"x={x} N={n_max}: r/gap={mp.nstr(metrics['residual_over_gap'], 10)} "
                f"[{metrics['ratio_status']}]",
                flush=True,
            )
        return {
            "x": x,
            "elapsed_seconds": time.perf_counter() - started,
            "rows": rows,
        }


def _power_fit(rows: list[dict], n_max: int) -> dict:
    selected = sorted(
        (
            row for row in rows
            if row["N"] == n_max and row["x"] in FINAL_FIVE
            and row["metrics"]["ratio_status"] == "MEASURED"
        ),
        key=lambda row: row["x"],
    )
    if len(selected) != len(FINAL_FIVE):
        return {
            "status": "UNVERIFIED",
            "available_x": [row["x"] for row in selected],
        }
    with mp.workdps(80):
        xs = [mp.log(mp.sqrt(row["x"])) for row in selected]
        ys = [mp.log(mp.mpf(row["metrics"]["residual_over_gap"])) for row in selected]
        xmean = mp.fsum(xs) / len(xs)
        ymean = mp.fsum(ys) / len(ys)
        slope = mp.fsum((x-xmean)*(y-ymean) for x, y in zip(xs, ys)) / mp.fsum(
            (x-xmean)**2 for x in xs
        )
        intercept = ymean - slope * xmean
        residuals = [y - intercept - slope*x for x, y in zip(xs, ys)]
        return {
            "status": "MEASURED",
            "model": "r/gap=C*lambda^(-p)",
            "x": list(FINAL_FIVE),
            "p": mp.nstr(-slope, 50),
            "C": mp.nstr(mp.exp(intercept), 50),
            "rss_log": mp.nstr(mp.fsum(value**2 for value in residuals), 50),
        }


def main() -> None:
    output = HERE / "prolate-bridge-data" / "exact-projection-grid.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    # Three independent x-families amortize the pure-Python arbitrary-precision
    # eigensolves without recomputing a prolate candidate for each N mutation.
    worker_count = min(3, len(X_GRID), max(1, os.cpu_count() or 1))
    families = []
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = {executor.submit(run_x_family, x): x for x in X_GRID}
        for future in as_completed(futures):
            family = future.result()
            families.append(family)
            print(
                f"completed x={family['x']} in {family['elapsed_seconds']:.1f}s",
                flush=True,
            )
    families.sort(key=lambda item: item["x"])
    rows = [row for family in families for row in family["rows"]]
    rows.sort(key=lambda row: (row["N"] != PRIMARY_N, row["N"], row["x"]))
    payload = {
        "schema": "codex-r5-prolate-exact-grid-v1",
        "status": "MEASURED" if all(
            row["metrics"]["ratio_status"] == "MEASURED" for row in rows
        ) else "UNVERIFIED",
        "scope": "registered primary x grid and N=96/144 last-five mutations",
        "method": "exact finite exponential antiderivatives after high-precision Legendre-to-power expansion",
        "reference_zero_data_used": False,
        "parallel_x_workers": worker_count,
        "rows": rows,
        "power_fit_last_five": {
            str(n_max): _power_fit(rows, n_max)
            for n_max in (96, 120, 144)
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "row_count": len(rows),
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
