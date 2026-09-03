#!/usr/bin/env python3
"""Arbitrary-precision analytic prolate projection for the R5.3 bridge.

This diagnostic expands the high-precision Legendre prolate candidate into
powers and integrates every term of the finite E-map exactly in t=log(u).
It therefore avoids the binary64/composite-quadrature floor in the original
bridge sweep.  The construction contains no reference zero data.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import mpmath as mp
import numpy as np

from prolate_candidate import project_e_map
from run_prolate_only_control import high_precision_candidate
from weil_core import parity_blocks, prime_power_terms


HERE = Path(__file__).resolve().parent
CASES = (
    # x, N, working dps, primary Legendre cutoff, cutoff mutation
    (9, 30, 140, 200, 160),
    (13, 120, 180, 200, 160),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _add_scaled(target: list[mp.mpf], source: list[mp.mpf], scale: mp.mpf) -> None:
    if len(target) < len(source):
        target.extend([mp.mpf(0)] * (len(source) - len(target)))
    for index, value in enumerate(source):
        target[index] += scale * value


def legendre_series_to_powers(standard: list[mp.mpf]) -> list[mp.mpf]:
    """Convert sum_l standard[l] P_l(z) to coefficients of z**j."""

    maximum = len(standard) - 1
    result = [mp.mpf(0)] * (maximum + 1)
    previous = [mp.mpf(1)]
    _add_scaled(result, previous, standard[0])
    if maximum == 0:
        return result
    current = [mp.mpf(0), mp.mpf(1)]
    _add_scaled(result, current, standard[1])
    for degree in range(1, maximum):
        following = [mp.mpf(0)] * (degree + 2)
        upward = mp.mpf(2 * degree + 1) / (degree + 1)
        downward = mp.mpf(degree) / (degree + 1)
        for index, value in enumerate(current):
            following[index + 1] += upward * value
        for index, value in enumerate(previous):
            following[index] -= downward * value
        _add_scaled(result, following, standard[degree + 1])
        previous, current = current, following
    return result


def exact_e_projection(candidate: dict, n_max: int) -> dict:
    r"""Project E(h) by exact termwise integration on [-log(lambda),log(lambda)].

    If h(lambda*z)=sum_j b_j z^j and q_n=2*pi*n/log(x), interchange the
    finite m-sum with the integral.  For n>=0 this gives

      c_n=(-1)^n/sqrt(L) sum_j b_j/(j+1/2-iq_n)
          * [sum_{m<=x}(lambda/m)^(1/2-iq_n)
             - lambda^(-1/2+iq_n) sum_{m<=x}(m/x)^j].

    This is just the antiderivative of exp((j+1/2-iq_n)t); no numerical
    quadrature or spectral ordinate enters it.
    """

    x = int(candidate["x"])
    lam = candidate["lambda"]
    length = mp.log(x)
    powers = legendre_series_to_powers(candidate["standard_legendre_coefficients"])
    active = [(j, value) for j, value in enumerate(powers) if value]
    scaled_power_sums = [
        mp.fsum((mp.mpf(m) / x) ** j for m in range(1, x + 1))
        for j, _ in active
    ]
    positive: list[mp.mpc] = []
    for n in range(n_max + 1):
        q = 2 * mp.pi * n / length
        upper = mp.fsum(
            mp.power(lam / m, mp.mpf("0.5") - 1j * q)
            for m in range(1, x + 1)
        )
        lower_phase = mp.power(lam, -mp.mpf("0.5") + 1j * q)
        total = mp.fsum(
            coefficient * (upper - lower_phase * power_sum)
            / (j + mp.mpf("0.5") - 1j * q)
            for (j, coefficient), power_sum in zip(active, scaled_power_sums)
        )
        positive.append(((-1) ** n) * total / mp.sqrt(length))

    # The registered R5.3 primary is raw E(h), so retain this complex vector.
    # The orthogonal inversion-even projection is returned separately as a
    # mutation; unlike the prolate-only R5.2 control, it is not the primary.
    unprojected_norm = mp.sqrt(
        abs(positive[0]) ** 2
        + 2 * mp.fsum(abs(value) ** 2 for value in positive[1:])
    )
    inversion_odd_norm = mp.sqrt(
        2 * mp.fsum(mp.im(value) ** 2 for value in positive[1:])
    ) / unprojected_norm
    raw_full = [mp.conj(positive[n]) for n in range(n_max, 0, -1)] + positive
    full = [value / unprojected_norm for value in raw_full]

    projected = [mp.re(value) for value in positive]
    projected_raw_norm = mp.sqrt(
        projected[0] ** 2
        + 2 * mp.fsum(value**2 for value in projected[1:])
    )
    projected = [value / projected_raw_norm for value in projected]
    projected_full = list(reversed(projected[1:])) + projected

    even = mp.matrix(n_max + 1, 1)
    odd = mp.matrix(n_max, 1)
    even[0] = full[n_max]
    for n in range(1, n_max + 1):
        even[n] = (full[n_max - n] + full[n_max + n]) / mp.sqrt(2)
        odd[n - 1] = (full[n_max - n] - full[n_max + n]) / mp.sqrt(2)
    projected_even = mp.matrix(n_max + 1, 1)
    projected_odd = mp.matrix(n_max, 1)
    projected_even[0] = projected[0]
    for n in range(1, n_max + 1):
        projected_even[n] = mp.sqrt(2) * projected[n]
        projected_odd[n - 1] = mp.mpf(0)
    integral_from_powers = 2 * lam * mp.fsum(
        powers[j] / (j + 1) for j in range(0, len(powers), 2)
    )
    return {
        "full": full,
        "even": even,
        "odd": odd,
        "raw_norm": unprojected_norm,
        "inversion_odd_norm": inversion_odd_norm,
        "even_projected": {
            "full": projected_full,
            "even": projected_even,
            "odd": projected_odd,
            "raw_norm": projected_raw_norm,
        },
        "integral_from_power_expansion": integral_from_powers,
        "largest_power_coefficient": max(abs(value) for value in powers),
        "last_power_coefficient": powers[-1],
    }


def phase_aligned_distance(first: list[mp.mpc], second: list[mp.mpc]) -> mp.mpf:
    overlap = mp.fsum(mp.conj(a) * b for a, b in zip(first, second))
    phase = mp.conj(overlap) / abs(overlap) if overlap else mp.mpc(1)
    return mp.sqrt(mp.fsum(abs(a - phase * b) ** 2 for a, b in zip(first, second)))


def double_projection_distance(x: int, n_max: int, exact: list[mp.mpc]) -> dict:
    projection = project_e_map(
        x,
        n_max,
        quadrature_order=20,
        panels_per_nyquist_cycle=8,
        mode_lmax=400,
    )
    converted = [mp.mpc(complex(value)) for value in projection.coefficients]
    distance = phase_aligned_distance(exact, converted)
    return {
        "phase_aligned_distance": distance,
        "double_raw_norm": projection.raw_norm,
        "double_inversion_defect": projection.inversion_defect,
    }


def _conjugate_dot(left: mp.matrix, right: mp.matrix) -> mp.mpc:
    return mp.fsum(mp.conj(left[j]) * right[j] for j in range(left.rows))


def _matrix_metrics(
    even_matrix: mp.matrix,
    odd_matrix: mp.matrix,
    projection: dict,
    even_values: list[mp.mpf],
    odd_values: list[mp.mpf],
    ground: mp.matrix,
    x: int,
) -> dict:
    even = projection["even"]
    odd = projection["odd"]
    even_action = even_matrix * even
    odd_action = odd_matrix * odd
    mu = mp.re(_conjugate_dot(even, even_action) + _conjugate_dot(odd, odd_action))
    even_residual = even_action - mu * even
    odd_residual = odd_action - mu * odd
    residual = mp.sqrt(
        mp.re(
            _conjugate_dot(even_residual, even_residual)
            + _conjugate_dot(odd_residual, odd_residual)
        )
    )
    gap = min(even_values[1], odd_values[0]) - even_values[0]
    separation = min(abs(even_values[1] - mu), abs(odd_values[0] - mu))
    overlap = abs(_conjugate_dot(ground, even))
    actual_sin = mp.sqrt(max(mp.mpf(0), 1 - overlap**2))
    raw_angle_bound = residual / separation
    asserted_angle_bound = min(mp.mpf(1), raw_angle_bound)
    height = mp.mpf("0.25")
    operator_bound = mp.sqrt(mp.sinh(height * mp.log(x)) / height)
    vector_bound = mp.sqrt(
        max(mp.mpf(0), 2 - 2 * mp.sqrt(max(mp.mpf(0), 1 - asserted_angle_bound**2)))
    )
    return {
        "mu": mu,
        "residual": residual,
        "gap": gap,
        "residual_over_gap": residual / gap,
        "separation_from_competitors": separation,
        "residual_over_separation": raw_angle_bound,
        "asserted_sin_angle_bound": asserted_angle_bound,
        "actual_sin_angle": actual_sin,
        "uniform_transform_bound_imaginary_quarter": operator_bound * vector_bound,
        "ground_overlap": overlap,
        "even_ground": even_values[0],
        "even_second": even_values[1],
        "odd_ground": odd_values[0],
    }


def _reference_spectrum_or_solve(
    x: int,
    n_max: int,
    even_matrix: mp.matrix,
    odd_matrix: mp.matrix,
) -> tuple[list[mp.mpf], list[mp.mpf], mp.matrix, str]:
    # The already committed reconstruction is zero-blind.  Reusing its
    # high-precision vector and first Ritz values avoids another 121x121 full
    # eigensolve while leaving the matrix action independently rebuilt here.
    saved = HERE / f"true-x{x}-N{n_max}-dps200.json"
    coarse = HERE / f"true-x{x}-N{n_max}-dps100.json"
    if saved.exists() and coarse.exists():
        saved_payload = json.loads(saved.read_text(encoding="utf-8"))
        coarse_payload = json.loads(coarse.read_text(encoding="utf-8"))
        ground = mp.matrix([mp.mpf(value) for value in saved_payload["even_unit_vector"]])
        even_ground = mp.mpf(saved_payload["eigensolve"]["minimum"])
        even_second = mp.mpf(coarse_payload["eigensolve"]["first_even_values"][1])
        odd_ground = mp.mpf(coarse_payload["eigensolve"]["first_odd_values"][0])
        return [even_ground, even_second], [odd_ground], ground, "committed zero-blind 100/200-dps Ritz data"

    even_spectrum, even_vectors = mp.eigsy(even_matrix)
    odd_spectrum = mp.eigsy(odd_matrix, eigvals_only=True)
    ground = even_vectors[:, 0]
    return (
        [even_spectrum[0], even_spectrum[1]],
        [odd_spectrum[0]],
        ground,
        "fresh mpmath.eigsy",
    )


def _serialize(value):
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, (mp.mpf, mp.mpc)):
        return mp.nstr(value, max(30, mp.mp.dps - 20))
    if isinstance(value, np.floating):
        return float(value)
    return value


def run_case(x: int, n_max: int, dps: int, lmax: int, mutation_lmax: int) -> dict:
    started = time.perf_counter()
    with mp.workdps(dps):
        print(f"x={x} N={n_max}: high-precision prolate modes", flush=True)
        candidate = high_precision_candidate(x, lmax)
        mutation_candidate = high_precision_candidate(x, mutation_lmax)
        print(f"x={x} N={n_max}: exact analytic E projections", flush=True)
        projection = exact_e_projection(candidate, n_max)
        mutation = exact_e_projection(mutation_candidate, n_max)
        mode_cutoff_distance = phase_aligned_distance(projection["full"], mutation["full"])
        double_check = double_projection_distance(x, n_max, projection["full"])

        print(f"x={x} N={n_max}: high-precision Weil matrix and bridge action", flush=True)
        even_matrix, odd_matrix, matrix_meta = parity_blocks(
            n_max, x, prime_power_terms(x), dps
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
        output = {
            "x": x,
            "lambda": mp.sqrt(x),
            "N": n_max,
            "working_decimal_digits": dps,
            "legendre_cutoff": lmax,
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
                "largest_power_coefficient": projection["largest_power_coefficient"],
                "last_power_coefficient": projection["last_power_coefficient"],
                "legendre_cutoff_vector_distance": mode_cutoff_distance,
                "double_projection_check": double_check,
                "first_even_coefficients": [projection["even"][j] for j in range(8)],
            },
            "metrics": metrics,
            "even_projected_mutation_metrics": even_projected_metrics,
            "elapsed_seconds": time.perf_counter() - started,
        }
        print(
            f"x={x} N={n_max}: r={mp.nstr(metrics['residual'], 12)} "
            f"gap={mp.nstr(metrics['gap'], 12)} "
            f"r/gap={mp.nstr(metrics['residual_over_gap'], 12)}",
            flush=True,
        )
        return _serialize(output)


def main() -> None:
    output = HERE / "prolate-bridge-data" / "exact-projection-diagnostic.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "codex-r5-prolate-exact-projection-v1",
        "status": "MEASURED",
        "scope": "analytic-projection rescue diagnostic at x=9,N=30 and x=13,N=120",
        "method": (
            "high-precision Legendre-to-power conversion followed by exact "
            "finite exponential antiderivatives for every E-map term"
        ),
        "reference_zero_data_used": False,
        "cases": [run_case(*case) for case in CASES],
        "source_sha256": sha256(Path(__file__)),
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
