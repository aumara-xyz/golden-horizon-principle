#!/usr/bin/env python3
"""High-precision spot check showing why the binary64 bridge sweep is unresolved."""

from __future__ import annotations

import json
from pathlib import Path

import mpmath as mp
import numpy as np

from prolate_candidate import coefficient_distance, project_e_map
from weil_core import parity_blocks, prime_power_terms


X = 9
N = 30
DPS = 60


def _mp_vector(projection) -> tuple[mp.matrix, mp.matrix]:
    full = projection.coefficients
    even, odd = mp.matrix(N + 1, 1), mp.matrix(N, 1)
    even[0] = mp.mpc(complex(full[N]))
    for n in range(1, N + 1):
        even[n] = mp.mpc(complex((full[N - n] + full[N + n]) / np.sqrt(2.0)))
        odd[n - 1] = mp.mpc(complex((full[N - n] - full[N + n]) / np.sqrt(2.0)))
    return even, odd


def main() -> None:
    output = Path(__file__).resolve().parent / "prolate-bridge-data" / "high-precision-spotcheck.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    even_matrix, odd_matrix, _ = parity_blocks(N, X, prime_power_terms(X), DPS)
    candidate = project_e_map(
        X, N, quadrature_order=20, panels_per_nyquist_cycle=8, mode_lmax=400
    )
    candidate_coarse = project_e_map(
        X, N, quadrature_order=20, panels_per_nyquist_cycle=4, mode_lmax=400
    )
    coefficient_uncertainty = coefficient_distance(
        candidate.coefficients, candidate_coarse.coefficients
    )
    even, odd = _mp_vector(candidate)
    with mp.workdps(DPS):
        even_values, even_vectors = mp.eigsy(even_matrix)
        odd_values, _ = mp.eigsy(odd_matrix)
        mu = (even.T.conjugate() * even_matrix * even + odd.T.conjugate() * odd_matrix * odd)[0]
        residual_even = even_matrix * even - mu * even
        residual_odd = odd_matrix * odd - mu * odd
        residual = mp.sqrt(
            (residual_even.T.conjugate() * residual_even)[0]
            + (residual_odd.T.conjugate() * residual_odd)[0]
        )
        gap = min(even_values[1], odd_values[0]) - even_values[0]
        overlap = abs((even_vectors[:, 0].T.conjugate() * even)[0])
        payload = {
            "status": "MEASURED",
            "scope": "diagnostic x=9,N=30; not the registered N=120 decay fit",
            "matrix_dps": DPS,
            "x": X,
            "N": N,
            "even_ground": mp.nstr(even_values[0], 50),
            "even_second": mp.nstr(even_values[1], 50),
            "odd_ground": mp.nstr(odd_values[0], 50),
            "gap": mp.nstr(gap, 50),
            "candidate_ground_overlap": mp.nstr(overlap, 40),
            "candidate_actual_sin_angle": mp.nstr(mp.sqrt(1 - overlap**2), 40),
            "candidate_mu": mp.nstr(mu, 40),
            "candidate_residual": mp.nstr(residual, 40),
            "formal_residual_over_gap": mp.nstr(residual / gap, 40),
            "coefficient_uncertainty_4_vs_8_panels_per_cycle": coefficient_uncertainty,
            "ratio_status": "UNVERIFIED",
            "ratio_reason": "the double-precision candidate projection uncertainty dominates the 60-digit Weil gap",
        }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
