#!/usr/bin/env python3
"""Independent Round-5b Q2 commutator computation for one frozen x.

This file contains no zeta-zero data.  It implements the affine-log weak-form
Galerkin convention committed in PREDICTIONS-codex-r5b.md and compares the
authentic finite Weil matrix with matched pseudo-prime and archimedean-only
controls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import mpmath as mp
import numpy as np


HERE = Path(__file__).resolve().parent
R5 = HERE.parent / "codex-r5"
sys.path.insert(0, str(R5))

import weil_core as core  # noqa: E402


X_VALUES = (9, 13, 14, 16)
N_MAX = 120
WORK_DPS = 100
PSEUDO_SEED = 52025001
PSEUDO_TARGETS = {9: (4, 7), 13: (6, 9), 14: (6, 9), 16: (6, 10)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--x", type=int, choices=X_VALUES, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mpstr(value: mp.mpf | mp.mpc, digits: int = 80) -> str:
    return mp.nstr(value, digits)


def vector_norm(vector: mp.matrix) -> mp.mpf:
    return mp.sqrt(mp.fsum(abs(vector[index]) ** 2 for index in range(vector.rows)))


def frobenius_squared(matrix: mp.matrix) -> mp.mpf:
    return mp.fsum(
        abs(matrix[row, column]) ** 2
        for row in range(matrix.rows)
        for column in range(matrix.cols)
    )


def matched_pseudo_terms(x: int) -> tuple[list[core.ArithmeticTerm], int, list[str]]:
    """Round-5 sampler generalized to the frozen authentic counts at each x."""

    base_count, atom_count = PSEUDO_TARGETS[x]
    rng = np.random.Generator(np.random.PCG64DXSM(PSEUDO_SEED))
    attempts = 0
    while True:
        attempts += 1
        bases: list[float] = []
        while len(bases) < base_count:
            candidate = float(rng.uniform(2.0, float(x)))
            if rng.random() <= math.log(2.0) / math.log(candidate):
                bases.append(candidate)
        bases.sort()
        powers: list[tuple[float, float, int]] = []
        for base in bases:
            exponent = 1
            value = base
            while value <= x * (1.0 + 8.0 * np.finfo(float).eps):
                powers.append((value, base, exponent))
                exponent += 1
                value *= base
        if len(powers) == atom_count:
            break
        if attempts > 1_000_000:
            raise RuntimeError("matched pseudo-prime sampler did not terminate")
    terms = [
        core.ArithmeticTerm(
            format(value, ".17g"),
            format(math.log(base) / math.sqrt(value), ".17g"),
            format(base, ".17g"),
            exponent,
            "base_log_over_sqrt",
        )
        for value, base, exponent in sorted(powers)
    ]
    return terms, attempts, [format(base, ".17g") for base in bases]


def pw_entry(n: int, m: int, x: int) -> mp.mpf:
    if n == m:
        return 2 * mp.pi**2 * n * n / 3 + 4 * mp.pi**2 * x * x / 3
    return mp.mpf(8 * x * x - 2 * n * m) / ((m - n) ** 2)


def pw_parity_blocks(x: int) -> tuple[mp.matrix, mp.matrix]:
    even = mp.matrix(N_MAX + 1)
    odd = mp.matrix(N_MAX)
    sqrt2 = mp.sqrt(2)
    even[0, 0] = pw_entry(0, 0, x)
    for n in range(1, N_MAX + 1):
        value = sqrt2 * pw_entry(0, n, x)
        even[0, n] = value
        even[n, 0] = value
    for n in range(1, N_MAX + 1):
        for m in range(n, N_MAX + 1):
            same = pw_entry(n, m, x)
            reflected = pw_entry(n, -m, x)
            even_value = same + reflected
            odd_value = same - reflected
            even[n, m] = even_value
            even[m, n] = even_value
            odd[n - 1, m - 1] = odd_value
            odd[m - 1, n - 1] = odd_value
    return even, odd


def quadrature_entry(n: int, m: int, x: int) -> mp.mpc:
    """Independent weak-form integral in centered log coordinate t."""

    a = mp.log(mp.sqrt(x))
    length = 2 * a
    potential = (2 * mp.pi * x / a) ** 2

    def basis(index: int, t: mp.mpf) -> mp.mpc:
        return mp.exp(2 * mp.pi * mp.j * index * (t + a) / length) / mp.sqrt(length)

    def integrand(t: mp.mpf) -> mp.mpc:
        vm = basis(m, t)
        vn = basis(n, t)
        derivative_m_conjugate = -mp.j * mp.pi * m * mp.conj(vm) / a
        derivative_n = mp.j * mp.pi * n * vn / a
        return (
            (a * a - t * t) * derivative_m_conjugate * derivative_n
            + potential * t * t * mp.conj(vm) * vn
        )

    return mp.quad(integrand, [-a, 0, a])


def solve_local_pair(matrix: mp.matrix) -> list[dict[str, object]]:
    """Refine the lowest two eigenpairs from binary64 seeds at 100 dps."""

    array = np.array(matrix.tolist(), dtype=float)
    _, vectors = np.linalg.eigh(array)
    output: list[dict[str, object]] = []
    for ordinal in range(2):
        initial = mp.matrix(
            [mp.mpf(repr(float(value))) for value in vectors[:, ordinal]]
        )
        eigenvalue, vector, residual = core.refine_ground(
            matrix, initial, iterations=7
        )
        output.append(
            {"value": eigenvalue, "vector": vector, "residual": residual}
        )
    output.sort(key=lambda item: item["value"])
    if not output[1]["value"] > output[0]["value"]:
        raise RuntimeError("local eigenpair refinement did not separate two values")
    return output


def authentic_ground(
    x: int, even: mp.matrix, odd: mp.matrix
) -> tuple[str, mp.mpf, mp.mpf, mp.matrix, mp.mpf, dict[str, object]]:
    """Use committed target-free high-precision Ritz data as a stable seed/audit."""

    if x in (9, 13, 14):
        high_path = R5 / f"true-x{x}-N120-dps400.json"
        coarse_path = R5 / f"true-x{x}-N120-dps100.json"
        high = json.loads(high_path.read_text(encoding="utf-8"))
        coarse = json.loads(coarse_path.read_text(encoding="utf-8"))
        initial = mp.matrix([mp.mpf(value) for value in high["even_unit_vector"]])
        epsilon, vector, residual = core.refine_ground(even, initial, iterations=3)
        even_second = mp.mpf(coarse["eigensolve"]["first_even_values"][1])
        odd_ground = mp.mpf(coarse["eigensolve"]["first_odd_values"][0])
        gap = min(even_second, odd_ground) - epsilon
        source = {
            "high_path": str(high_path.relative_to(HERE.parent)),
            "high_sha256": sha256(high_path),
            "coarse_path": str(coarse_path.relative_to(HERE.parent)),
            "coarse_sha256": sha256(coarse_path),
        }
        return "even", epsilon, gap, vector, residual, source

    grid_path = R5 / "prolate-bridge-data" / "exact-projection-grid.json"
    grid = json.loads(grid_path.read_text(encoding="utf-8"))
    row = next(
        item for item in grid["rows"] if item["x"] == x and item["N"] == N_MAX
    )
    coefficient_path = R5 / "prolate-data" / "prolate-x16-N120.json"
    coefficients = json.loads(coefficient_path.read_text(encoding="utf-8"))
    real = [mp.mpf(repr(value)) for value in coefficients["coefficients_real"]]
    initial = mp.matrix(N_MAX + 1, 1)
    initial[0] = real[N_MAX]
    for n in range(1, N_MAX + 1):
        initial[n] = (real[N_MAX - n] + real[N_MAX + n]) / mp.sqrt(2)
    epsilon, vector, residual = core.refine_ground(even, initial, iterations=7)
    even_second = mp.mpf(row["metrics"]["even_second"])
    odd_ground = mp.mpf(row["metrics"]["odd_ground"])
    gap = min(even_second, odd_ground) - epsilon
    source = {
        "grid_path": str(grid_path.relative_to(HERE.parent)),
        "grid_sha256": sha256(grid_path),
        "coefficient_path": str(coefficient_path.relative_to(HERE.parent)),
        "coefficient_sha256": sha256(coefficient_path),
    }
    return "even", epsilon, gap, vector, residual, source


def control_ground(
    even: mp.matrix, odd: mp.matrix
) -> tuple[str, mp.mpf, mp.mpf, mp.matrix, mp.mpf, dict[str, object]]:
    even_pairs = solve_local_pair(even)
    odd_pairs = solve_local_pair(odd)
    if even_pairs[0]["value"] < odd_pairs[0]["value"]:
        parity = "even"
        ground = even_pairs[0]
        next_value = min(even_pairs[1]["value"], odd_pairs[0]["value"])
    else:
        parity = "odd"
        ground = odd_pairs[0]
        next_value = min(odd_pairs[1]["value"], even_pairs[0]["value"])
    gap = next_value - ground["value"]
    if not gap > 0:
        raise RuntimeError("control global ground-state gap is not positive")
    return (
        parity,
        ground["value"],
        gap,
        ground["vector"],
        ground["residual"],
        {
            "even_low_values": [mpstr(item["value"]) for item in even_pairs],
            "odd_low_values": [mpstr(item["value"]) for item in odd_pairs],
        },
    )


def case_metrics(
    label: str,
    x: int,
    matrix_even: mp.matrix,
    matrix_odd: mp.matrix,
    pw_even: mp.matrix,
    pw_odd: mp.matrix,
    ground_data: tuple[str, mp.mpf, mp.mpf, mp.matrix, mp.mpf, dict[str, object]],
    term_count: int,
) -> dict[str, object]:
    parity, epsilon, gap, xi, eig_residual, source = ground_data
    comm_even = matrix_even * pw_even - pw_even * matrix_even
    comm_odd = matrix_odd * pw_odd - pw_odd * matrix_odd
    comm_norm = mp.sqrt(
        frobenius_squared(comm_even) + frobenius_squared(comm_odd)
    )
    matrix_norm = mp.sqrt(
        frobenius_squared(matrix_even) + frobenius_squared(matrix_odd)
    )
    pw_norm = mp.sqrt(frobenius_squared(pw_even) + frobenius_squared(pw_odd))
    normalized_frobenius = comm_norm / (matrix_norm * pw_norm)

    matrix_block = matrix_even if parity == "even" else matrix_odd
    pw_block = pw_even if parity == "even" else pw_odd
    direct_action = matrix_block * (pw_block * xi) - pw_block * (matrix_block * xi)
    action_residual = vector_norm(direct_action) / vector_norm(xi)
    rho = action_residual / gap
    shifted_residual = matrix_block * xi - epsilon * xi
    identity_action = shifted_residual * 0
    identity_action = (matrix_block - epsilon * mp.eye(matrix_block.rows)) * (pw_block * xi)
    identity_action -= pw_block * shifted_residual
    identity_difference = vector_norm(direct_action - identity_action)
    return {
        "x": x,
        "matrix": label,
        "term_count": term_count,
        "ground_parity": parity,
        "ground_eigenvalue": mpstr(epsilon),
        "ground_gap": mpstr(gap),
        "normalized_frobenius_commutator": mpstr(normalized_frobenius),
        "ground_action_commutator_residual": mpstr(action_residual),
        "ground_action_over_gap": mpstr(rho),
        "predicted_above_gap": True,
        "prediction_held": bool(rho > 1),
        "status": "MEASURED" if rho > 1 else "UNVERIFIED",
        "diagnostics": {
            "ground_eigensolve_residual": mpstr(eig_residual),
            "ground_eigensolve_residual_over_gap": mpstr(eig_residual / gap),
            "commutator_skew_defect_even": mpstr(
                frobenius_squared(comm_even + comm_even.T) ** mp.mpf("0.5")
            ),
            "commutator_skew_defect_odd": mpstr(
                frobenius_squared(comm_odd + comm_odd.T) ** mp.mpf("0.5")
            ),
            "direct_vs_eigenvector_identity": mpstr(identity_difference),
            "matrix_frobenius_norm": mpstr(matrix_norm),
            "pw_frobenius_norm": mpstr(pw_norm),
            "commutator_frobenius_norm": mpstr(comm_norm),
            "ground_source": source,
        },
    }


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with mp.workdps(WORK_DPS):
        x = args.x
        length = mp.log(x)
        print(f"x={x}: archimedean arrays and P blocks", flush=True)
        alpha, beta, gamma = core.archimedean_arrays(N_MAX, length, WORK_DPS)
        pw_even, pw_odd = pw_parity_blocks(x)
        true_terms = core.prime_power_terms(x)
        pseudo_terms, pseudo_attempts, pseudo_bases = matched_pseudo_terms(x)
        controls = [
            ("authentic", true_terms),
            ("pseudo-prime", pseudo_terms),
            ("archimedean-only", []),
        ]
        records: list[dict[str, object]] = []
        for label, terms in controls:
            print(f"x={x}: building and testing {label}", flush=True)
            even, odd = core.parity_blocks_from_arrays(
                N_MAX, length, terms, alpha, beta, gamma, WORK_DPS
            )
            if label == "authentic":
                ground = authentic_ground(x, even, odd)
            else:
                ground = control_ground(even, odd)
            records.append(
                case_metrics(
                    label, x, even, odd, pw_even, pw_odd, ground, len(terms)
                )
            )

        print(f"x={x}: independent weak-form entry audit", flush=True)
        samples = [(0, 0), (0, 1), (1, 1), (1, -1), (7, 13), (13, -7)]
        quadrature_rows = []
        for n, m in samples:
            numeric = quadrature_entry(n, m, x)
            closed = pw_entry(n, m, x)
            quadrature_rows.append(
                {
                    "n": n,
                    "m": m,
                    "closed": mpstr(closed),
                    "quadrature": {"real": mpstr(mp.re(numeric)), "imag": mpstr(mp.im(numeric))},
                    "absolute_difference": mpstr(abs(numeric - closed)),
                }
            )
        maximum_quadrature_difference = max(
            mp.mpf(row["absolute_difference"]) for row in quadrature_rows
        )
        checks_pass = bool(
            maximum_quadrature_difference < mp.mpf("1e-85")
            and all(
                mp.mpf(record["diagnostics"]["ground_eigensolve_residual_over_gap"])
                < mp.mpf("1e-20")
                for record in records
            )
            and all(record["prediction_held"] for record in records)
        )
        payload = {
            "schema": "codex-r5b-q2-independent-v1",
            "status": "MEASURED" if checks_pass else "UNVERIFIED",
            "parameters": {"x": x, "N": N_MAX, "working_decimal_digits": WORK_DPS},
            "pw_convention": {
                "transport": "endpoint-preserving affine unitary from y to centered t=log(u)",
                "compression": "weak-form Galerkin compression in shifted V_n basis",
                "canonical_EPW_inverse": False,
                "scalar_shift_or_rescaling": False,
            },
            "pseudo_control": {
                "seed": PSEUDO_SEED,
                "target_base_count": PSEUDO_TARGETS[x][0],
                "target_atom_count": PSEUDO_TARGETS[x][1],
                "attempts": pseudo_attempts,
                "bases": pseudo_bases,
            },
            "records": records,
            "pw_quadrature_audit": {
                "samples": quadrature_rows,
                "maximum_absolute_difference": mpstr(maximum_quadrature_difference),
            },
            "all_checks_passed": checks_pass,
            "source_sha256": {
                str(Path(__file__).relative_to(HERE.parent)): sha256(Path(__file__)),
                str((R5 / "weil_core.py").relative_to(HERE.parent)): sha256(R5 / "weil_core.py"),
            },
            "target_data_present": False,
            "elapsed_seconds": time.perf_counter() - started,
        }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": payload["status"],
                "seconds": payload["elapsed_seconds"],
                "rho": {
                    record["matrix"]: record["ground_action_over_gap"]
                    for record in records
                },
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
