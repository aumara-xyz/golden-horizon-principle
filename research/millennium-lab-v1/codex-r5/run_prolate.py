#!/usr/bin/env python3
"""Build the preregistered prolate candidates and convergence ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from prolate_candidate import (
    coefficient_distance,
    hermite_candidate_values,
    project_e_map,
    prolate_candidate,
    rectangle_transform_operator_bound,
)


X_GRID = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20)
N_GRID = (96, 120, 144)


def _projection_record(projection) -> dict:
    return {
        "x": projection.x,
        "lambda": float(np.sqrt(projection.x)),
        "N": projection.n_max,
        "source": projection.source,
        "mode_lmax": projection.mode_lmax,
        "quadrature_order": projection.quadrature_order,
        "panels_per_nyquist_cycle": projection.panels_per_nyquist_cycle,
        "raw_norm": projection.raw_norm,
        "inversion_defect_max_imaginary_coefficient": projection.inversion_defect,
        "indices": projection.indices.tolist(),
        "coefficients_real": projection.coefficients.real.tolist(),
        "coefficients_imag": projection.coefficients.imag.tolist(),
    }


def build(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    results: dict = {
        "schema": "codex-r5-prolate-v1",
        "status": "MEASURED",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "x_grid": list(X_GRID),
        "N_grid": list(N_GRID),
        "normalization": {
            "modes": "L2[-lambda,lambda]=1; value at zero positive",
            "combination": "L2=1; h4 coefficient positive; integral analytically zero",
            "projection": "Euclidean norm of V_-N,...,V_N coefficients equals one",
            "extension": "h_lambda is zero outside [-lambda,lambda]",
        },
        "mode_diagnostics": [],
        "projections": [],
        "convergence": [],
        "hermite_control": [],
        "rectangle_bounds": [],
    }

    for x in X_GRID:
        candidate = prolate_candidate(x, lmax=320)
        limiting_probe = np.linspace(-3.0, 3.0, 1201)
        candidate_probe = candidate.values(limiting_probe)
        hermite_probe = hermite_candidate_values(limiting_probe)
        if np.vdot(candidate_probe, hermite_probe).real < 0:
            candidate_probe = -candidate_probe
        results["mode_diagnostics"].append(
            {
                "x": x,
                "lambda": float(np.sqrt(x)),
                "c": float(2.0 * np.pi * x),
                "h0_eigenvalue": candidate.h0.eigenvalue,
                "h4_eigenvalue": candidate.h4.eigenvalue,
                "h0_integral": candidate.h0.integral,
                "h4_integral": candidate.h4.integral,
                "h0_weight": candidate.h0_weight,
                "h4_weight": candidate.h4_weight,
                "combination_integral": candidate.integral,
                "h0_truncation_residual": candidate.h0.truncation_residual,
                "h4_truncation_residual": candidate.h4.truncation_residual,
                "sup_difference_from_normalized_hermite_on_minus3_3": float(
                    np.max(np.abs(candidate_probe - hermite_probe))
                ),
            }
        )
        for n_max in N_GRID:
            projection = project_e_map(
                x,
                n_max,
                quadrature_order=20,
                panels_per_nyquist_cycle=4,
                mode_lmax=320,
            )
            record = _projection_record(projection)
            filename = f"prolate-x{x}-N{n_max}.json"
            path = output / filename
            path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            results["projections"].append(
                {
                    "x": x,
                    "N": n_max,
                    "file": filename,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "raw_norm": projection.raw_norm,
                    "inversion_defect": projection.inversion_defect,
                }
            )

        # Two independent convergence levers: Legendre truncation and the
        # piecewise Gauss-Legendre rule.  N=144 is the most demanding case.
        p_ref = project_e_map(
            x, 144, quadrature_order=20, panels_per_nyquist_cycle=8, mode_lmax=400
        )
        p_quad = project_e_map(
            x, 144, quadrature_order=20, panels_per_nyquist_cycle=2, mode_lmax=400
        )
        p_mode = project_e_map(
            x, 144, quadrature_order=20, panels_per_nyquist_cycle=8, mode_lmax=240
        )
        results["convergence"].append(
            {
                "x": x,
                "N": 144,
                "reference_quadrature_order": 20,
                "reference_panels_per_nyquist_cycle": 8,
                "reference_mode_lmax": 400,
                "quadrature_mutation_order": 20,
                "quadrature_mutation_panels_per_nyquist_cycle": 2,
                "mode_mutation_lmax": 240,
                "quadrature_phase_aligned_coefficient_distance": coefficient_distance(
                    p_ref.coefficients, p_quad.coefficients
                ),
                "mode_phase_aligned_coefficient_distance": coefficient_distance(
                    p_ref.coefficients, p_mode.coefficients
                ),
                "reference_raw_norm": p_ref.raw_norm,
            }
        )

        # The registered undeformed-Hermite mutation uses the full Schwartz
        # function, not a compact truncation, and the same Fourier projection.
        h_projection = project_e_map(
            x, 144, quadrature_order=20, panels_per_nyquist_cycle=8, source="hermite"
        )
        h_record = _projection_record(h_projection)
        h_filename = f"hermite-control-x{x}-N144.json"
        h_path = output / h_filename
        h_path.write_text(json.dumps(h_record, indent=2) + "\n", encoding="utf-8")
        results["hermite_control"].append(
            {
                "x": x,
                "N": 144,
                "file": h_filename,
                "sha256": hashlib.sha256(h_path.read_bytes()).hexdigest(),
                "phase_aligned_distance_from_prolate": coefficient_distance(
                    p_ref.coefficients, h_projection.coefficients
                ),
                "raw_norm": h_projection.raw_norm,
            }
        )
        results["rectangle_bounds"].append(
            {
                "x": x,
                "real_half_widths": [32, 64, 128],
                "imaginary_half_height": 0.25,
                "uniform_functional_norm_bound": rectangle_transform_operator_bound(x, 0.25),
            }
        )

    result_path = output / "prolate-summary.json"
    result_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "prolate-data",
    )
    args = parser.parse_args()
    results = build(args.output)
    print(json.dumps({
        "status": "MEASURED",
        "x_count": len(results["x_grid"]),
        "projection_count": len(results["projections"]),
        "convergence_count": len(results["convergence"]),
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
