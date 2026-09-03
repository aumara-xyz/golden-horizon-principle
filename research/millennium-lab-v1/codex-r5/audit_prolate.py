#!/usr/bin/env python3
"""Independent numerical checks for the Round-5 prolate module."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import pro_cv

from prolate_candidate import (
    prolate_candidate,
    transform_basis_values,
)


X_GRID = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20)


def direct_basis_transform(z: complex, x: float, n: int) -> complex:
    length = np.log(x)
    half = length / 2.0

    def integrand(t: float) -> complex:
        basis = np.exp(2j * np.pi * n * (t + half) / length) / np.sqrt(length)
        return basis * np.exp(-1j * z * t)

    real = quad(lambda t: float(np.real(integrand(t))), -half, half, epsabs=2e-14)[0]
    imag = quad(lambda t: float(np.imag(integrand(t))), -half, half, epsabs=2e-14)[0]
    return complex(real, imag)


def main() -> None:
    directory = Path(__file__).resolve().parent
    mode_checks = []
    for x in X_GRID:
        candidate = prolate_candidate(x, lmax=400)
        c = 2.0 * np.pi * x
        mode_checks.append({
            "x": x,
            "h0_characteristic_difference_vs_scipy_pro_cv": candidate.h0.eigenvalue - pro_cv(0, 0, c),
            "h4_characteristic_difference_vs_scipy_pro_cv": candidate.h4.eigenvalue - pro_cv(0, 4, c),
            "zero_integral_residual": candidate.integral,
            "combination_coefficient_norm": float(np.linalg.norm(candidate.coefficients)),
        })

    z = 3.25 + 0.2j
    transform_checks = []
    for n in (-3, 0, 4):
        closed = complex(transform_basis_values(z, 13, np.asarray([n]))[0])
        direct = direct_basis_transform(z, 13, n)
        transform_checks.append({
            "x": 13,
            "n": n,
            "z": [z.real, z.imag],
            "closed_form": [closed.real, closed.imag],
            "direct_quadrature": [direct.real, direct.imag],
            "absolute_difference": abs(closed - direct),
        })

    payload = {
        "status": "MEASURED",
        "mode_checks": mode_checks,
        "max_characteristic_value_difference": max(
            max(
                abs(row["h0_characteristic_difference_vs_scipy_pro_cv"]),
                abs(row["h4_characteristic_difference_vs_scipy_pro_cv"]),
            )
            for row in mode_checks
        ),
        "max_zero_integral_residual": max(abs(row["zero_integral_residual"]) for row in mode_checks),
        "max_mode_norm_error": max(abs(row["combination_coefficient_norm"] - 1.0) for row in mode_checks),
        "transform_checks": transform_checks,
        "max_transform_formula_difference": max(row["absolute_difference"] for row in transform_checks),
    }
    output = directory / "prolate-data" / "prolate-audit.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "max_characteristic_value_difference": payload["max_characteristic_value_difference"],
        "max_zero_integral_residual": payload["max_zero_integral_residual"],
        "max_transform_formula_difference": payload["max_transform_formula_difference"],
    }, indent=2))


if __name__ == "__main__":
    main()
