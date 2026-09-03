#!/usr/bin/env python3
"""Blind raw-basis prolate-only hostile control for R5.2.

The primary keeps the complex Fourier coefficients of raw E(h), as required
by the R5.3 convention audit.  The earlier inversion-even projection remains
an explicitly named mutation.  No reference ordinates or score enter this
construction or its intrinsic root continuation.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import mpmath as mp

from run_prolate_exact_bridge import exact_e_projection, phase_aligned_distance
from run_prolate_only_control import high_precision_candidate
from weil_core import enumerate_positive_roots_mp, transform_mp


HERE = Path(__file__).resolve().parent
X = 13
N = 120
ROOT_COUNT = 70
GUARD_COUNT = ROOT_COUNT + 1
WORK_DPS = 180
PRIMARY_LMAX = 200
MUTATION_LMAX = 160
HOMOTOPY_STEPS = 4
# Full degree-240 Arb all-root isolation is an optional finite-polynomial audit.
# Keep it off in the default blind run: doubled homotopy/contour checks are the
# registered numerical diagnostic, while the infinite-mode claim stays UNVERIFIED.
ATTEMPT_ARB_ISOLATION = False


def mp_vector(values: list[mp.mpc]) -> mp.matrix:
    result = mp.matrix(len(values), 1)
    for index, value in enumerate(values):
        result[index] = value
    return result


def rational_value_and_derivative(
    z: mp.mpc, coefficients: list[mp.mpc], lattice: list[mp.mpf]
) -> tuple[mp.mpc, mp.mpc, mp.mpf]:
    value = mp.mpc(0)
    derivative = mp.mpc(0)
    absolute_sum = mp.mpf(0)
    for coefficient, pole in zip(coefficients, lattice):
        denominator = z - pole
        term = coefficient / denominator
        value += term
        derivative -= term / denominator
        absolute_sum += abs(term)
    return value, derivative, absolute_sum


def newton_root(
    coefficients: list[mp.mpc], lattice: list[mp.mpf], seed: mp.mpc
) -> tuple[mp.mpc, int]:
    z = mp.mpc(seed)
    tolerance = mp.power(10, -(mp.mp.dps - 30))
    for iteration in range(1, 81):
        value, derivative, _ = rational_value_and_derivative(z, coefficients, lattice)
        if derivative == 0:
            raise ArithmeticError("zero derivative in raw-control Newton step")
        correction = value / derivative
        z -= correction
        if abs(correction) <= tolerance * max(1, abs(z)):
            return z, iteration
    raise ArithmeticError("raw-control Newton iteration did not converge")


def track_homotopy(
    even: list[mp.mpc],
    raw: list[mp.mpc],
    seeds: list[mp.mpf],
    lattice: list[mp.mpf],
    steps: int,
) -> tuple[list[mp.mpc], int]:
    roots = [mp.mpc(seed) for seed in seeds]
    maximum_iterations = 0
    for step in range(1, steps + 1):
        tau = mp.mpf(step) / steps
        coefficients = [a + tau * (b - a) for a, b in zip(even, raw)]
        updated = []
        for root in roots:
            value, iterations = newton_root(coefficients, lattice, root)
            updated.append(value)
            maximum_iterations = max(maximum_iterations, iterations)
        roots = updated
    return roots, maximum_iterations


def numerical_winding(
    coefficients: list[mp.mpc],
    lattice: list[mp.mpf],
    left: mp.mpf,
    right: mp.mpf,
    height: mp.mpf,
    samples_per_side: int,
) -> dict:
    points: list[mp.mpc] = []
    for k in range(samples_per_side):
        points.append(mp.mpc(left + (right-left)*k/samples_per_side, -height))
    for k in range(samples_per_side):
        points.append(mp.mpc(right, -height + 2*height*k/samples_per_side))
    for k in range(samples_per_side):
        points.append(mp.mpc(right - (right-left)*k/samples_per_side, height))
    for k in range(samples_per_side):
        points.append(mp.mpc(left, height - 2*height*k/samples_per_side))
    points.append(points[0])
    values = []
    relative_boundary_minimum = mp.inf
    for point in points:
        value, _, absolute_sum = rational_value_and_derivative(
            point, coefficients, lattice
        )
        values.append(value)
        relative_boundary_minimum = min(
            relative_boundary_minimum, abs(value) / absolute_sum
        )
    argument_change = mp.fsum(
        mp.arg(second / first) for first, second in zip(values[:-1], values[1:])
    )
    winding = int(mp.nint(argument_change / (2 * mp.pi)))
    pole_count = sum(left < pole < right for pole in lattice)
    return {
        "samples_per_side": samples_per_side,
        "winding_zeros_minus_poles": winding,
        "enclosed_poles": pole_count,
        "inferred_enclosed_zeros": winding + pole_count,
        "relative_boundary_minimum": relative_boundary_minimum,
    }


def try_arb_polynomial_isolation(
    coefficients: list[mp.mpc], numerical_roots: list[mp.mpc], length: mp.mpf
) -> dict:
    """Isolate the rounded finite rational numerator with Arb when available."""

    try:
        from flint import acb, acb_poly, arb, ctx
    except ImportError:
        return {
            "status": "UNVERIFIED",
            "reason": "python-flint is unavailable; numerical homotopy checks remain",
        }

    ctx.dps = 220

    def ball(value: mp.mpc) -> acb:
        return acb(
            arb(mp.nstr(mp.re(value), 175)),
            arb(mp.nstr(mp.im(value), 175)),
        )

    x_polynomial = acb_poly([0, 1])
    lattice = [
        acb(2 * arb.pi() * n / arb(X).log()) for n in range(-N, N + 1)
    ]
    denominator = acb_poly.from_roots(lattice)
    numerator = acb_poly()
    for coefficient, pole in zip(coefficients, lattice):
        quotient, remainder = divmod(denominator, x_polynomial - pole)
        if any(not coefficient.contains(0) for coefficient in remainder):
            return {
                "status": "UNVERIFIED",
                "reason": "Arb synthetic division left a nonzero enclosure",
            }
        numerator += ball(coefficient) * quotient
    try:
        isolated = numerator.roots(1e-90)
    except (ValueError, ZeroDivisionError) as exc:
        return {
            "status": "UNVERIFIED",
            "reason": f"Arb all-root isolation failed: {exc}",
            "polynomial_degree": numerator.degree(),
        }

    unused = set(range(len(isolated)))
    matched = []
    matched_real_radii = []
    matched_imaginary_radii = []
    for numerical in numerical_roots:
        closest = min(
            unused,
            key=lambda index: abs(
                complex(float(isolated[index].real.mid()), float(isolated[index].imag.mid()))
                - complex(float(mp.re(numerical)), float(mp.im(numerical)))
            ),
        )
        root_ball = isolated[closest]
        unused.remove(closest)
        matched_real_radii.append(root_ball.real.rad())
        matched_imaginary_radii.append(root_ball.imag.rad())
        matched.append({
            "contains_numerical_root": bool(root_ball.contains(ball(numerical))),
            "real_radius": str(root_ball.real.rad()),
            "imaginary_radius": str(root_ball.imag.rad()),
        })
    success = len(isolated) == numerator.degree() and all(
        item["contains_numerical_root"] for item in matched
    )
    return {
        "status": "MEASURED" if success else "UNVERIFIED",
        "scope": (
            "Arb isolation of the rounded finite coefficient polynomial; "
            "not an interval proof of the infinite-mode prolate limit"
        ),
        "working_decimal_digits": ctx.dps,
        "polynomial_degree": numerator.degree(),
        "isolated_root_count": len(isolated),
        "first_70_matched": success,
        "maximum_matched_real_radius": str(max(matched_real_radii)),
        "maximum_matched_imaginary_radius": str(max(matched_imaginary_radii)),
    }


def serialize_complex(value: mp.mpc, digits: int = 140) -> dict[str, str]:
    return {
        "real": mp.nstr(mp.re(value), digits),
        "imaginary": mp.nstr(mp.im(value), digits),
    }


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    output = HERE / "outputs" / "prolate-only-raw-blind.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with mp.workdps(WORK_DPS):
        length = mp.log(X)
        lattice = [2 * mp.pi * n / length for n in range(-N, N + 1)]
        print("building degree-200/160 raw prolate candidates", flush=True)
        candidate = high_precision_candidate(X, PRIMARY_LMAX)
        cutoff_candidate = high_precision_candidate(X, MUTATION_LMAX)
        raw_projection = exact_e_projection(candidate, N)
        cutoff_projection = exact_e_projection(cutoff_candidate, N)
        raw = raw_projection["full"]
        even = raw_projection["even_projected"]["full"]
        cutoff_raw = cutoff_projection["full"]
        cutoff_even = cutoff_projection["even_projected"]["full"]

        print("intrinsically bracketing the even mutation and guard root", flush=True)
        even_seeds = enumerate_positive_roots_mp(
            mp_vector(even), length, GUARD_COUNT, 32
        )
        cutoff_seeds = enumerate_positive_roots_mp(
            mp_vector(cutoff_even), length, GUARD_COUNT, 32
        )

        print(
            f"tracking raw roots at {HOMOTOPY_STEPS}/"
            f"{2 * HOMOTOPY_STEPS} homotopy steps",
            flush=True,
        )
        roots_32, iterations_32 = track_homotopy(
            even, raw, even_seeds, lattice, HOMOTOPY_STEPS
        )
        roots_64, iterations_64 = track_homotopy(
            even, raw, even_seeds, lattice, 2 * HOMOTOPY_STEPS
        )
        cutoff_roots, cutoff_iterations = track_homotopy(
            cutoff_even, cutoff_raw, cutoff_seeds, lattice, HOMOTOPY_STEPS
        )

        primary = roots_64[:ROOT_COUNT]
        even_primary = even_seeds[:ROOT_COUNT]
        cutoff_primary = cutoff_roots[:ROOT_COUNT]
        homotopy_displacements = [abs(a-b) for a, b in zip(primary, roots_32)]
        cutoff_displacements = [abs(a-b) for a, b in zip(primary, cutoff_primary)]
        even_displacements = [abs(a-b) for a, b in zip(primary, even_primary)]
        real_displacements = [abs(mp.re(a)-b) for a, b in zip(primary, even_primary)]
        imaginary_parts = [abs(mp.im(root)) for root in primary]
        residuals = []
        relative_residuals = []
        derivatives = []
        for root in primary:
            value, derivative, absolute_sum = rational_value_and_derivative(
                root, raw, lattice
            )
            residuals.append(abs(value))
            relative_residuals.append(abs(value) / absolute_sum)
            derivatives.append(abs(derivative))

        left = mp.re(primary[0]) / 2
        right = (mp.re(primary[-1]) + mp.re(roots_64[ROOT_COUNT])) / 2
        height = max(mp.mpf(1), 4 * max(imaginary_parts) + mp.mpf("0.25"))
        print("checking the enclosing rectangle at two contour resolutions", flush=True)
        winding_checks = [
            numerical_winding(raw, lattice, left, right, height, samples)
            for samples in (512, 1024)
        ]
        ordered = all(
            mp.re(second) > mp.re(first) for first, second in zip(primary[:-1], primary[1:])
        )
        continuation_measured = (
            ordered
            and max(homotopy_displacements) < mp.mpf("1e-100")
            and all(item["inferred_enclosed_zeros"] == ROOT_COUNT for item in winding_checks)
        )

        if ATTEMPT_ARB_ISOLATION:
            print(
                "attempting Arb isolation of the rounded degree-240 numerator",
                flush=True,
            )
            arb_isolation = try_arb_polynomial_isolation(raw, primary, length)
        else:
            arb_isolation = {
                "status": "UNVERIFIED",
                "reason": (
                    "optional degree-240 Arb all-root isolation disabled in the "
                    "default run; doubled homotopy and contour checks are retained"
                ),
            }
        rows = []
        for index, (root, even_root) in enumerate(zip(primary, even_primary), start=1):
            rows.append({
                "ordinal": index,
                "raw_root": serialize_complex(root),
                "even_mutation_root": mp.nstr(even_root, 140),
                "absolute_shift_from_even_mutation": mp.nstr(
                    abs(root-even_root), 40
                ),
                "absolute_real_shift_from_even_mutation": mp.nstr(
                    abs(mp.re(root)-even_root), 40
                ),
                "absolute_imaginary_part": mp.nstr(abs(mp.im(root)), 40),
                "relative_rational_residual": mp.nstr(relative_residuals[index-1], 20),
            })

        legacy_path = HERE / "outputs" / "prolate-only-blind.json"
        legacy_even_comparison = {
            "status": "UNVERIFIED",
            "reason": "the earlier even-projected blind artifact was not found",
        }
        if legacy_path.exists():
            legacy_payload = json.loads(legacy_path.read_text(encoding="utf-8"))
            legacy_roots = [
                mp.mpf(value)
                for value in legacy_payload["primary"]["positive_roots"][:ROOT_COUNT]
            ]
            if len(legacy_roots) == ROOT_COUNT:
                raw_to_legacy = [
                    abs(raw_root - legacy_root)
                    for raw_root, legacy_root in zip(primary, legacy_roots)
                ]
                exact_even_to_legacy = [
                    abs(exact_root - legacy_root)
                    for exact_root, legacy_root in zip(even_primary, legacy_roots)
                ]
                legacy_even_comparison = {
                    "status": "MEASURED",
                    "role": (
                        "comparison only after raw roots were constructed; the legacy "
                        "roots were not continuation seeds or parameter inputs"
                    ),
                    "artifact": str(legacy_path.relative_to(HERE)),
                    "artifact_sha256": source_hash(legacy_path),
                    "maximum_raw_complex_distance": mp.nstr(max(raw_to_legacy), 40),
                    "maximum_exact_even_distance": mp.nstr(
                        max(exact_even_to_legacy), 40
                    ),
                    "frozen_20_50_maximum_raw_complex_distance": mp.nstr(
                        max(raw_to_legacy[19:50]), 40
                    ),
                    "frozen_20_50_maximum_exact_even_distance": mp.nstr(
                        max(exact_even_to_legacy[19:50]), 40
                    ),
                }

        payload = {
            "schema": "codex-r5-prolate-only-raw-blind-v1",
            "status": "MEASURED" if continuation_measured else "UNVERIFIED",
            "formal_infinite_mode_certification_status": "UNVERIFIED",
            "formal_certification_limit": (
                "finite-mode homotopy and rounded-polynomial isolation do not "
                "prove that the degree-200 prolate vector equals its infinite-mode limit"
            ),
            "blind_artifact": True,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "construction": {
                "x": X,
                "N": N,
                "working_decimal_digits": WORK_DPS,
                "primary_legendre_cutoff": PRIMARY_LMAX,
                "legendre_cutoff_mutation": MUTATION_LMAX,
                "primary_convention": "normalized raw complex coefficients of E(h)",
                "mutation_convention": "orthogonal inversion-even projection Re(c_n)",
                "intrinsic_seed_rule": (
                    "sign brackets from zero in successive Fourier-lattice intervals "
                    "for the even mutation; complex homotopy continuation to raw E(h)"
                ),
                "homotopy_steps_primary": 2 * HOMOTOPY_STEPS,
                "reference_spectrum_input": False,
                "special_function_zero_finder": False,
            },
            "root_label": (
                "post-hoc audit convention (not preregistered): continuation labels "
                "from the first 70 intrinsically bracketed positive even-mutation "
                "roots, then ordered by increasing real part"
            ),
            "root_definition_status": "UNVERIFIED",
            "root_definition_limit": (
                "a non-real finite transform has no canonical first-positive-root "
                "ordering; continuation from the even mutation is a disclosed "
                "post-hoc audit convention"
            ),
            "roots": rows,
            "diagnostics": {
                "raw_inversion_odd_norm": mp.nstr(
                    raw_projection["inversion_odd_norm"], 50
                ),
                "raw_vs_cutoff_vector_distance": mp.nstr(
                    phase_aligned_distance(raw, cutoff_raw), 50
                ),
                "maximum_absolute_imaginary_part": mp.nstr(max(imaginary_parts), 40),
                "median_absolute_imaginary_part": mp.nstr(
                    sorted(imaginary_parts)[len(imaginary_parts)//2], 40
                ),
                "maximum_absolute_shift_from_even_mutation": mp.nstr(
                    max(even_displacements), 40
                ),
                "maximum_absolute_real_shift_from_even_mutation": mp.nstr(
                    max(real_displacements), 40
                ),
                "maximum_coarse_vs_doubled_homotopy_displacement": mp.nstr(
                    max(homotopy_displacements), 40
                ),
                "maximum_legendre_cutoff_root_displacement": mp.nstr(
                    max(cutoff_displacements), 40
                ),
                "maximum_rational_residual": mp.nstr(max(residuals), 20),
                "maximum_relative_rational_residual": mp.nstr(
                    max(relative_residuals), 20
                ),
                "minimum_rational_derivative": mp.nstr(min(derivatives), 20),
                "roots_ordered_by_real_part": ordered,
                "maximum_newton_iterations": max(
                    iterations_32, iterations_64, cutoff_iterations
                ),
                "winding_checks": [
                    {
                        key: mp.nstr(value, 30) if isinstance(value, mp.mpf) else value
                        for key, value in item.items()
                    }
                    for item in winding_checks
                ],
                "rectangle": {
                    "left_real": mp.nstr(left, 40),
                    "right_real": mp.nstr(right, 40),
                    "imaginary_half_height": mp.nstr(height, 40),
                },
                "arb_polynomial_isolation": arb_isolation,
                "legacy_even_artifact_comparison": legacy_even_comparison,
            },
            "post_gate_scoring_rule": (
                "For frozen ordinals 20--50, compare continuation-labelled z_j "
                "to each real ordinate gamma_j by |z_j-gamma_j|; use those "
                "nonnegative distances for RMSE, MAE, median, maximum, and landing thresholds."
            ),
        }
    payload["construction_source_sha256"] = source_hash(Path(__file__))
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "root_count": len(payload["roots"]),
        "maximum_absolute_imaginary_part": payload["diagnostics"]["maximum_absolute_imaginary_part"],
        "maximum_absolute_shift_from_even_mutation": payload["diagnostics"]["maximum_absolute_shift_from_even_mutation"],
        "arb_status": payload["diagnostics"]["arb_polynomial_isolation"]["status"],
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
