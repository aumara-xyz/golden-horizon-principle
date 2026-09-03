#!/usr/bin/env python3
"""Independent formula and precision replay for ``weil_core``.

The checks in this file use only the formulas and parameter values in
Connes--Consani--Moscovici, arXiv:2511.22755v1.  In particular, no target
spectral data are imported or embedded here.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time
from typing import Sequence

import mpmath as mp
import numpy as np

import weil_core as core


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "outputs" / "weil-replay-audit.json"


def fresh_prime_power_terms(x: int, dps: int) -> list[core.ArithmeticTerm]:
    """Construct the finite prime comb without a fixed decimal precision cap."""

    terms: list[core.ArithmeticTerm] = []
    with mp.workdps(dps):
        for base in range(2, x + 1):
            if not core._is_prime(base):
                continue
            exponent = 1
            location = base
            while location <= x:
                weight = mp.log(base) / mp.sqrt(location)
                terms.append(
                    core.ArithmeticTerm(
                        str(location), mp.nstr(weight, dps), str(base), exponent
                    )
                )
                exponent += 1
                location *= base
    return terms


def real_matrix(matrix: mp.matrix) -> mp.matrix:
    """Remove rigorously negligible zero imaginary parts from real formulas."""

    return mp.matrix(
        [[mp.re(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]
    )


def max_abs(values: Sequence[mp.mpf]) -> mp.mpf:
    """Maximum absolute value, including the empty-sequence case."""

    return max((abs(value) for value in values), default=mp.mpf(0))


def vector_norm(vector: mp.matrix) -> mp.mpf:
    """Euclidean norm of a real column vector."""

    return mp.sqrt(mp.fsum(vector[i] * vector[i] for i in range(vector.rows)))


def dot(left: mp.matrix, right: mp.matrix) -> mp.mpf:
    """Real Euclidean inner product of two column vectors."""

    return mp.fsum(left[i] * right[i] for i in range(left.rows))


def normalized(vector: mp.matrix) -> mp.matrix:
    """Return a unit vector with a deterministic overall sign."""

    result = vector / vector_norm(vector)
    if mp.fsum(result) < 0:
        result = -result
    return result


def rayleigh_inverse_refine(
    matrix: mp.matrix,
    seed: mp.matrix,
    dps: int,
    maximum_steps: int = 6,
) -> tuple[mp.mpf, mp.matrix, list[dict[str, str]]]:
    """Refine an isolated eigenpair with high-precision Rayleigh iteration.

    A lower-precision symmetric eigensolve supplies ``seed``.  Each step solves
    the shifted linear system at the target precision.  For the N=120 even
    block this avoids recomputing all 121 eigenvectors at every later precision.
    """

    with mp.workdps(dps):
        matrix = real_matrix(matrix)
        vector = normalized(mp.matrix([mp.mpf(seed[i]) for i in range(seed.rows)]))
        identity = mp.eye(matrix.rows)
        trace: list[dict[str, str]] = []
        target = mp.power(10, -(dps - 25))
        eigenvalue = dot(vector, matrix * vector)

        for step in range(maximum_steps + 1):
            residual_vector = matrix * vector - eigenvalue * vector
            residual = vector_norm(residual_vector)
            trace.append(
                {
                    "step": str(step),
                    "rayleigh_quotient": mp.nstr(eigenvalue, dps),
                    "residual_2": mp.nstr(residual, 20),
                }
            )
            if residual <= target or step == maximum_steps:
                break
            try:
                candidate = mp.lu_solve(matrix - eigenvalue * identity, vector)
            except ZeroDivisionError:
                # At finite precision, exact singularity means the iterate has
                # already reached the representable eigenpair.
                break
            candidate = normalized(candidate)
            if dot(candidate, vector) < 0:
                candidate = -candidate
            vector = candidate
            eigenvalue = dot(vector, matrix * vector)

        return eigenvalue, vector, trace


def full_coefficients_mp(even_vector: mp.matrix) -> mp.matrix:
    """Expand an even-parity vector to Fourier indices -N,...,N."""

    n_max = even_vector.rows - 1
    full = mp.matrix(2 * n_max + 1, 1)
    full[n_max] = even_vector[0]
    for n in range(1, n_max + 1):
        value = even_vector[n] / mp.sqrt(2)
        full[n_max - n] = value
        full[n_max + n] = value
    return full


def direct_transform(z: mp.mpf, coefficients: mp.matrix, length: mp.mpf) -> mp.mpc:
    """Direct Mellin/Fourier integral, independent of the sinc implementation."""

    n_max = (coefficients.rows - 1) // 2
    phase = mp.exp(mp.j * z * length / 2)

    def integrand(position: mp.mpf) -> mp.mpc:
        series = mp.fsum(
            coefficients[n + n_max]
            * mp.exp(2 * mp.pi * mp.j * n * position / length)
            for n in range(-n_max, n_max + 1)
        )
        return series * phase * mp.exp(-mp.j * z * position) / mp.sqrt(length)

    return mp.quad(integrand, [0, length / 4, length / 2, 3 * length / 4, length])


def closed_transform(z: mp.mpf, coefficients: mp.matrix, length: mp.mpf) -> mp.mpf:
    """Equation (5.25), evaluated through its centered-sinc continuation."""

    n_max = (coefficients.rows - 1) // 2
    return mp.sqrt(length) * mp.fsum(
        coefficients[n + n_max]
        * (-1 if n % 2 else 1)
        * mp.sincpi(n - z * length / (2 * mp.pi))
        for n in range(-n_max, n_max + 1)
    )


def direct_full_matrix(
    n_max: int,
    x: int,
    terms: Sequence[core.ArithmeticTerm],
    dps: int,
) -> tuple[mp.matrix, list[mp.mpf], list[mp.mpf], list[mp.mpf]]:
    """Build the full matrix entry-by-entry, bypassing the structured path."""

    with mp.workdps(dps):
        length = mp.log(x)
        alpha, beta, gamma = core.archimedean_arrays(n_max, length, dps)
        indices = list(range(-n_max, n_max + 1))
        matrix = mp.matrix(2 * n_max + 1)
        for row, n in enumerate(indices):
            for column, m in enumerate(indices):
                matrix[row, column] = mp.re(
                    core.weil_entry(n, m, length, terms, alpha, beta, gamma)
                )
        return matrix, alpha, beta, gamma


def projected_parity_blocks(full: mp.matrix, n_max: int) -> tuple[mp.matrix, mp.matrix]:
    """Project a full reflection-symmetric matrix onto parity bases."""

    even_basis = mp.matrix(2 * n_max + 1, n_max + 1)
    odd_basis = mp.matrix(2 * n_max + 1, n_max)
    even_basis[n_max, 0] = 1
    for n in range(1, n_max + 1):
        even_basis[n_max - n, n] = 1 / mp.sqrt(2)
        even_basis[n_max + n, n] = 1 / mp.sqrt(2)
        odd_basis[n_max + n, n - 1] = 1 / mp.sqrt(2)
        odd_basis[n_max - n, n - 1] = -1 / mp.sqrt(2)
    return even_basis.T * full * even_basis, odd_basis.T * full * odd_basis


def formula_audit(dps: int = 100) -> dict[str, object]:
    """Replay scalar, structured, parity, and transform identities."""

    payload: dict[str, object] = {"dps": dps, "x_cases": {}}
    with mp.workdps(dps):
        for x in (12, 13, 14):
            n_max = 8
            terms = fresh_prime_power_terms(x, dps + 15)
            length = mp.log(x)
            full, alpha, beta, gamma = direct_full_matrix(n_max, x, terms, dps)
            even, odd = core.parity_blocks_from_arrays(
                n_max, length, terms, alpha, beta, gamma, dps
            )
            even = real_matrix(even)
            odd = real_matrix(odd)
            projected_even, projected_odd = projected_parity_blocks(full, n_max)

            scalar_pairs = ((0, 0), (1, 1), (4, 4), (0, 1), (1, 2), (-2, 3), (7, -8))
            scalar_errors: list[mp.mpf] = []
            pole_errors: list[mp.mpf] = []
            whole_entry_errors: list[mp.mpf] = []
            for n, m in scalar_pairs:
                closed = core.archimedean_entry_from_arrays(n, m, alpha, beta, gamma)
                direct = core.direct_archimedean_entry(n, m, length, dps)
                scalar_errors.append(closed - direct)
                direct_pole = mp.quad(
                    lambda y: core.q_entry(n, m, y, length)
                    * (mp.exp(y / 2) + mp.exp(-y / 2)),
                    [0, length / 4, length / 2, 3 * length / 4, length],
                )
                pole_errors.append(core.pole_entry(n, m, length) - direct_pole)
                direct_arithmetic = mp.fsum(
                    term.mp_weight()
                    * core.q_entry(n, m, mp.log(term.mp_location()), length)
                    for term in terms
                )
                direct_whole = direct_pole - direct - direct_arithmetic
                closed_whole = core.weil_entry(
                    n, m, length, terms, alpha, beta, gamma
                )
                whole_entry_errors.append(closed_whole - direct_whole)

            symmetry_errors = [
                full[i, j] - full[j, i]
                for i in range(full.rows)
                for j in range(full.cols)
            ]
            reflection_errors = [
                full[i, j] - full[full.rows - 1 - i, full.cols - 1 - j]
                for i in range(full.rows)
                for j in range(full.cols)
            ]
            even_errors = [
                even[i, j] - projected_even[i, j]
                for i in range(even.rows)
                for j in range(even.cols)
            ]
            odd_errors = [
                odd[i, j] - projected_odd[i, j]
                for i in range(odd.rows)
                for j in range(odd.cols)
            ]

            even_values, even_vectors = mp.eigsy(even)
            odd_values = mp.eigsy(odd, eigvals_only=True)
            even_vector = normalized(even_vectors[:, 0])
            coefficients = full_coefficients_mp(even_vector)
            step = 2 * mp.pi / length
            transform_points = (
                step * mp.mpf("0.37"),
                step * mp.mpf("2.25"),
                step * mp.mpf("5.625"),
            )
            transform_errors = [
                closed_transform(z, coefficients, length)
                - direct_transform(z, coefficients, length)
                for z in transform_points
            ]

            coefficients_float = np.array(
                [float(coefficients[i]) for i in range(coefficients.rows)], dtype=float
            )
            normalized_coefficients_mp = coefficients / mp.fsum(coefficients)
            indices = list(range(-n_max, n_max + 1))
            perturbed = mp.diag(indices) - mp.matrix(
                [
                    [mp.mpf(indices[row]) * normalized_coefficients_mp[row] for _ in indices]
                    for row in range(len(indices))
                ]
            )
            companion = [
                value * (2 * mp.pi / length)
                for value in mp.eig(perturbed, left=False, right=False)
            ]
            companion_positive = sorted(
                mp.re(value)
                for value in companion
                if mp.re(value) > mp.mpf("1e-30") and abs(mp.im(value)) < mp.mpf("1e-70")
            )
            intrinsic_cutoff = n_max * 2 * mp.pi / length
            companion_inside = [
                value for value in companion_positive if value < intrinsic_cutoff
            ]
            enumerated = core.enumerate_positive_roots(
                coefficients_float, float(length), count=len(companion_inside)
            )
            enumerated_mp = core.enumerate_positive_roots_mp(
                coefficients, length, count=len(companion_inside)
            )
            root_errors = [
                enumerated[index] - companion_inside[index]
                for index in range(len(enumerated))
            ]
            root_errors_mp = [
                enumerated_mp[index] - companion_inside[index]
                for index in range(len(enumerated_mp))
            ]

            payload["x_cases"][str(x)] = {
                "term_count": len(terms),
                "maximum_archimedean_closed_vs_quadrature": mp.nstr(
                    max_abs(scalar_errors), 20
                ),
                "maximum_pole_closed_vs_quadrature": mp.nstr(
                    max_abs(pole_errors), 20
                ),
                "maximum_whole_entry_closed_vs_quadrature": mp.nstr(
                    max_abs(whole_entry_errors), 20
                ),
                "maximum_full_symmetry_error": mp.nstr(max_abs(symmetry_errors), 20),
                "maximum_reflection_error": mp.nstr(max_abs(reflection_errors), 20),
                "maximum_even_projection_error": mp.nstr(max_abs(even_errors), 20),
                "maximum_odd_projection_error": mp.nstr(max_abs(odd_errors), 20),
                "even_minimum": mp.nstr(even_values[0], 30),
                "odd_minimum": mp.nstr(odd_values[0], 30),
                "even_wins": bool(even_values[0] < odd_values[0]),
                "maximum_transform_closed_vs_direct": mp.nstr(
                    max_abs(transform_errors), 20
                ),
                "maximum_enumerator_vs_companion_error": format(
                    float(max(abs(value) for value in root_errors)), ".17g"
                ),
                "maximum_mp_enumerator_vs_companion_error": mp.nstr(
                    max_abs(root_errors_mp), 20
                ),
                "enumerated_positive_roots": [format(value, ".17g") for value in enumerated],
                "mp_enumerated_positive_roots": [
                    mp.nstr(value, 30) for value in enumerated_mp
                ],
                "companion_positive_roots": [
                    mp.nstr(value, 30) for value in companion_inside
                ],
            }
    return payload


def precision_floor_audit() -> dict[str, object]:
    """Check that display serialization does not cap arithmetic precision."""

    x = 13
    n_max = 8
    with mp.workdps(230):
        frozen = core.prime_power_terms(x)
        fresh = fresh_prime_power_terms(x, 225)
        frozen_even, _, _ = core.parity_blocks(n_max, x, frozen, 220)
        fresh_even, _, _ = core.parity_blocks(n_max, x, fresh, 220)
        frozen_even = real_matrix(frozen_even)
        fresh_even = real_matrix(fresh_even)
        differences = [
            frozen_even[i, j] - fresh_even[i, j]
            for i in range(frozen_even.rows)
            for j in range(frozen_even.cols)
        ]
        return {
            "x": x,
            "n_max": n_max,
            "serialized_display_weight_digits": 80,
            "core_weight_modes": sorted({term.weight_mode for term in frozen}),
            "maximum_matrix_difference_against_225_digit_weights": mp.nstr(
                max_abs(differences), 30
            ),
            "frozen_terms": [asdict(term) for term in frozen],
        }


def ground_precision_replay(
    x: int = 13,
    n_max: int = 120,
    requested_precisions: Sequence[int] = (100, 200, 400),
) -> dict[str, object]:
    """Compute and refine the N=120 lowest even eigenpair across precisions."""

    stages: list[dict[str, object]] = []
    seed: mp.matrix | None = None
    for requested in requested_precisions:
        working = requested + 30
        with mp.workdps(working):
            terms = fresh_prime_power_terms(x, working + 5)
            start = time.monotonic()
            even, odd, _ = core.parity_blocks(n_max, x, terms, working)
            even = real_matrix(even)
            odd = real_matrix(odd)
            build_seconds = time.monotonic() - start

            if seed is None:
                start = time.monotonic()
                values, vectors = mp.eigsy(even)
                solve_seconds = time.monotonic() - start
                eigenvalue = values[0]
                vector = normalized(vectors[:, 0])
                trace = [
                    {
                        "step": "full-symmetric-eigensolve",
                        "rayleigh_quotient": mp.nstr(eigenvalue, working),
                        "residual_2": mp.nstr(
                            vector_norm(even * vector - eigenvalue * vector), 20
                        ),
                    }
                ]
                second_even = values[1]
            else:
                start = time.monotonic()
                eigenvalue, vector, trace = rayleigh_inverse_refine(
                    even, seed, working
                )
                solve_seconds = time.monotonic() - start
                # Only the nearest competing eigenvalue is needed for a gap
                # check.  A full eigensolve is retained as an independent
                # validation because N=120 is inexpensive at these precisions.
                validation_values = mp.eigsy(even, eigvals_only=True)
                second_even = validation_values[1]
                validation_error = abs(eigenvalue - validation_values[0])
                trace.append(
                    {
                        "step": "full-eigval-validation",
                        "rayleigh_quotient": mp.nstr(validation_values[0], working),
                        "residual_2": mp.nstr(validation_error, 20),
                    }
                )

            odd_minimum = mp.eigsy(odd, eigvals_only=True)[0]
            residual = vector_norm(even * vector - eigenvalue * vector)
            gap = min(second_even, odd_minimum) - eigenvalue
            coefficient_payload = "\n".join(
                mp.nstr(vector[i], requested) for i in range(vector.rows)
            ).encode()
            stages.append(
                {
                    "requested_digits": requested,
                    "working_digits": working,
                    "build_seconds": build_seconds,
                    "solve_seconds_excluding_validation": solve_seconds,
                    "minimum_even": mp.nstr(eigenvalue, requested),
                    "second_even": mp.nstr(second_even, requested),
                    "minimum_odd": mp.nstr(odd_minimum, requested),
                    "parity_gap": mp.nstr(gap, requested),
                    "residual_2": mp.nstr(residual, 30),
                    "eigenvector_sha256": hashlib.sha256(coefficient_payload).hexdigest(),
                    "refinement_trace": trace,
                }
            )
            seed = mp.matrix([mp.mpf(vector[i]) for i in range(vector.rows)])

    return {
        "x": x,
        "n_max": n_max,
        "method": "100-digit eigsy seed, then guarded Rayleigh inverse iteration with full-eigenvalue validation",
        "stages": stages,
    }


def root_precision_replay(
    x: int = 13,
    n_max: int = 120,
    requested_precisions: Sequence[int] = (100, 200, 400),
    root_count: int = 60,
) -> dict[str, object]:
    """Repeat the first construction-derived roots across exact precisions."""

    stages: list[dict[str, object]] = []
    root_sets: list[list[mp.mpf]] = []
    seed: mp.matrix | None = None
    for requested in requested_precisions:
        working = requested
        with mp.workdps(working):
            terms = fresh_prime_power_terms(x, working + 5)
            even, _, _ = core.parity_blocks(n_max, x, terms, working)
            even = real_matrix(even)
            if seed is None:
                eigenvalues, eigenvectors = mp.eigsy(even)
                eigenvalue = eigenvalues[0]
                vector = normalized(eigenvectors[:, 0])
                refinement_steps: list[dict[str, str]] = []
            else:
                eigenvalue, vector, refinement_steps = rayleigh_inverse_refine(
                    even, seed, working
                )

            full = full_coefficients_mp(vector)
            roots = core.enumerate_positive_roots_mp(
                full, mp.log(x), root_count, subdivisions=32
            )
            root_residual = max_abs(
                [core.transform_mp(root, full, mp.log(x)) for root in roots]
            )
            eigen_residual = vector_norm(even * vector - eigenvalue * vector)
            stages.append(
                {
                    "requested_digits": requested,
                    "working_digits": working,
                    "minimum_even": mp.nstr(eigenvalue, requested),
                    "eigen_residual_2": mp.nstr(eigen_residual, 30),
                    "maximum_transform_residual": mp.nstr(root_residual, 30),
                    "refinement_trace": refinement_steps,
                    "positive_roots": [mp.nstr(root, requested) for root in roots],
                }
            )
            root_sets.append([+root for root in roots])
            seed = mp.matrix([mp.mpf(vector[index]) for index in range(vector.rows)])

    with mp.workdps(max(requested_precisions) + 40):
        score_indices = range(19, 50)
        comparisons: list[dict[str, str | int]] = []
        for index in score_indices:
            first_difference = abs(root_sets[1][index] - root_sets[0][index])
            second_difference = abs(root_sets[2][index] - root_sets[1][index])
            comparisons.append(
                {
                    "root_index": index + 1,
                    "absolute_100_vs_200": mp.nstr(first_difference, 20),
                    "absolute_200_vs_400": mp.nstr(second_difference, 20),
                }
            )
        maximum_first = max(
            abs(root_sets[1][index] - root_sets[0][index]) for index in score_indices
        )
        maximum_second = max(
            abs(root_sets[2][index] - root_sets[1][index]) for index in score_indices
        )

    return {
        "x": x,
        "n_max": n_max,
        "root_count": root_count,
        "selection": "positive roots 1--60 in order; construction-derived binary64 seeds refined at each working precision",
        "stages": stages,
        "roots_20_through_50_precision_differences": comparisons,
        "maximum_absolute_difference_20_through_50": {
            "100_vs_200": mp.nstr(maximum_first, 20),
            "200_vs_400": mp.nstr(maximum_second, 20),
        },
    }


def compare_root_driver_outputs(root_replay: dict[str, object]) -> dict[str, object]:
    """Compare this replay with the separately executed reconstruction driver."""

    comparisons: list[dict[str, object]] = []
    with mp.workdps(450):
        for stage in root_replay["stages"]:
            requested = int(stage["requested_digits"])
            driver_path = HERE / f"true-x13-N120-dps{requested}.json"
            driver = json.loads(driver_path.read_text())
            audit_roots = [mp.mpf(value) for value in stage["positive_roots"]]
            driver_roots = [mp.mpf(value) for value in driver["positive_roots"]]
            all_differences = [
                abs(audit - recorded)
                for audit, recorded in zip(audit_roots, driver_roots)
            ]
            frozen_differences = all_differences[19:50]
            maximum_all = max(all_differences)
            maximum_frozen = max(frozen_differences)
            comparisons.append(
                {
                    "digits": requested,
                    "driver_file": driver_path.name,
                    "driver_builder_sha256": driver["builder_sha256"],
                    "maximum_absolute_difference_first_60": mp.nstr(maximum_all, 20),
                    "worst_index_first_60": all_differences.index(maximum_all) + 1,
                    "maximum_absolute_difference_20_through_50": mp.nstr(
                        maximum_frozen, 20
                    ),
                    "worst_index_20_through_50": frozen_differences.index(maximum_frozen)
                    + 20,
                }
            )
    return {
        "meaning": "independent audit driver versus run_true_reconstruction.py outputs",
        "comparisons": comparisons,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--with-ground-replay", action="store_true")
    parser.add_argument("--with-root-precision-replay", action="store_true")
    parser.add_argument("--ground-replay-cache", type=Path)
    parser.add_argument("--root-precision-cache", type=Path)
    args = parser.parse_args()

    payload: dict[str, object] = {
        "source": "Connes--Consani--Moscovici, arXiv:2511.22755v1",
        "formula_audit": formula_audit(),
        "precision_floor_audit": precision_floor_audit(),
    }
    if args.with_ground_replay:
        payload["ground_precision_replay"] = ground_precision_replay()
    elif args.ground_replay_cache:
        cache = json.loads(args.ground_replay_cache.read_text())
        payload["ground_precision_replay"] = cache["ground_precision_replay"]
    if args.with_root_precision_replay:
        payload["root_precision_replay"] = root_precision_replay()
    elif args.root_precision_cache:
        cache = json.loads(args.root_precision_cache.read_text())
        payload["root_precision_replay"] = cache["root_precision_replay"]
    if "root_precision_replay" in payload:
        payload["root_driver_comparison"] = compare_root_driver_outputs(
            payload["root_precision_replay"]
        )

    gate_path = HERE / "pseudo-gate.json"
    payload["builder_provenance"] = {
        "blind_gate_builder_sha256": json.loads(gate_path.read_text())["builder_sha256"],
        "audit_builder_sha256": hashlib.sha256((HERE / "weil_core.py").read_bytes()).hexdigest(),
        "blind_gate_note": "The frozen gate used the committed pre-fix builder and binary64-threshold scoring; its artifacts were not overwritten.",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "ground_replay": args.with_ground_replay or bool(args.ground_replay_cache),
                "root_precision_replay": args.with_root_precision_replay
                or bool(args.root_precision_cache),
            }
        )
    )


if __name__ == "__main__":
    main()
