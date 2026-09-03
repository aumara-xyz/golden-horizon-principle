#!/usr/bin/env python3
"""Round 5b Q2: frozen affine-Galerkin prolate/Weil commutators.

This is a zero-data construction.  It evaluates the authentic finite Weil
form and the two preregistered controls at 100 decimal working digits.  The
full Fourier-basis matrices are assembled independently of their parity
blocks.  Frobenius commutator norms use the exact orthogonal parity
decomposition of the full matrix, while ground-state actions are also replayed
directly in the full basis.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Sequence

import mpmath as mp
import numpy as np


HERE = Path(__file__).resolve().parent
CORE_DIR = HERE.parent / "codex-r5"
sys.path.insert(0, str(CORE_DIR))
import weil_core as core  # noqa: E402


OUTPUT = HERE / "outputs" / "q2-commutator-backup.json"
X_VALUES = (9, 13, 14, 16)
N = 120
DPS = 100
PSEUDO_SEED = 52025001


def nstr(value: mp.mpf | mp.mpc, digits: int = 80) -> str:
    return mp.nstr(value, digits)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector_norm(vector: mp.matrix) -> mp.mpf:
    return mp.sqrt(mp.fsum(abs(vector[i]) ** 2 for i in range(vector.rows)))


def frobenius_sq(matrix: mp.matrix) -> mp.mpf:
    return mp.fsum(abs(matrix[i, j]) ** 2 for i in range(matrix.rows) for j in range(matrix.cols))


def max_matrix_difference(left: mp.matrix, right: mp.matrix) -> mp.mpf:
    return max(
        abs(left[i, j] - right[i, j])
        for i in range(left.rows)
        for j in range(left.cols)
    )


def p_entry(m: int, n: int, x: int) -> mp.mpf:
    """Frozen exact entry of the transported classical prolate operator."""

    if m == n:
        return 2 * mp.pi**2 * n * n / 3 + 4 * mp.pi**2 * x * x / 3
    return mp.mpf(8 * x * x - 2 * m * n) / ((m - n) ** 2)


def full_prolate(x: int) -> mp.matrix:
    indices = range(-N, N + 1)
    result = mp.matrix(2 * N + 1)
    for i, m in enumerate(indices):
        for j in range(i, 2 * N + 1):
            n = j - N
            value = p_entry(m, n, x)
            result[i, j] = value
            result[j, i] = value
    return result


def full_weil(
    length: mp.mpf,
    terms: Sequence[core.ArithmeticTerm],
    alpha: Sequence[mp.mpf],
    beta: Sequence[mp.mpf],
    gamma: Sequence[mp.mpf],
) -> mp.matrix:
    """Assemble M directly in index order -N,...,N."""

    prepared = [(mp.log(term.mp_location()), term.mp_weight()) for term in terms]
    numerator: dict[int, mp.mpf] = {}
    diagonal_arithmetic: dict[int, mp.mpf] = {}
    for n in range(-N, N + 1):
        alpha_n = alpha[abs(n)] if n >= 0 else -alpha[abs(n)]
        numerator[n] = alpha_n + mp.fsum(
            weight * mp.sin(2 * mp.pi * n * y / length) / mp.pi
            for y, weight in prepared
        )
        diagonal_arithmetic[n] = mp.fsum(
            weight * 2 * (1 - y / length) * mp.cos(2 * mp.pi * n * y / length)
            for y, weight in prepared
        )

    result = mp.matrix(2 * N + 1)
    for i, n in enumerate(range(-N, N + 1)):
        for j in range(i, 2 * N + 1):
            m = j - N
            if n == m:
                value = (
                    core.pole_entry(n, n, length)
                    - (2 * gamma[abs(n)] - 2 * beta[abs(n)])
                    - diagonal_arithmetic[n]
                )
            else:
                value = core.pole_entry(n, m, length) + (numerator[n] - numerator[m]) / (n - m)
            result[i, j] = value
            result[j, i] = value
    return result


def project_parity(full: mp.matrix) -> tuple[mp.matrix, mp.matrix, mp.mpf]:
    """Orthogonally project a reflection-symmetric full matrix."""

    even = mp.matrix(N + 1)
    odd = mp.matrix(N)
    sqrt2 = mp.sqrt(2)
    even[0, 0] = full[N, N]
    for n in range(1, N + 1):
        even[0, n] = (full[N, N + n] + full[N, N - n]) / sqrt2
        even[n, 0] = (full[N + n, N] + full[N - n, N]) / sqrt2
    for n in range(1, N + 1):
        for m in range(1, N + 1):
            even[n, m] = (
                full[N + n, N + m]
                + full[N + n, N - m]
                + full[N - n, N + m]
                + full[N - n, N - m]
            ) / 2
            odd[n - 1, m - 1] = (
                full[N + n, N + m]
                - full[N + n, N - m]
                - full[N - n, N + m]
                + full[N - n, N - m]
            ) / 2

    cross = mp.mpf(0)
    for m in range(1, N + 1):
        cross = max(cross, abs((full[N, N + m] - full[N, N - m]) / sqrt2))
    for n in range(1, N + 1):
        for m in range(1, N + 1):
            value = (
                full[N + n, N + m]
                - full[N + n, N - m]
                + full[N - n, N + m]
                - full[N - n, N - m]
            ) / 2
            cross = max(cross, abs(value))
    return even, odd, cross


def direct_prolate_blocks(x: int) -> tuple[mp.matrix, mp.matrix]:
    even = mp.matrix(N + 1)
    odd = mp.matrix(N)
    even[0, 0] = p_entry(0, 0, x)
    for n in range(1, N + 1):
        value = mp.sqrt(2) * p_entry(0, n, x)
        even[0, n] = value
        even[n, 0] = value
    for n in range(1, N + 1):
        for m in range(n, N + 1):
            ev = p_entry(n, m, x) + p_entry(n, -m, x)
            od = p_entry(n, m, x) - p_entry(n, -m, x)
            even[n, m] = even[m, n] = ev
            odd[n - 1, m - 1] = odd[m - 1, n - 1] = od
    return even, odd


def matched_pseudo_terms(x: int) -> tuple[list[core.ArithmeticTerm], int, dict[str, int]]:
    authentic = core.prime_power_terms(x)
    desired_atoms = len(authentic)
    desired_bases = len({term.base for term in authentic})
    rng = np.random.Generator(np.random.PCG64DXSM(PSEUDO_SEED))
    attempts = 0
    while True:
        attempts += 1
        bases: list[float] = []
        while len(bases) < desired_bases:
            candidate = float(rng.uniform(2.0, float(x)))
            if rng.random() <= math.log(2.0) / math.log(candidate):
                bases.append(candidate)
        powers: list[tuple[float, float, int]] = []
        for base in sorted(bases):
            exponent = 1
            value = base
            while value <= x * (1 + 8 * np.finfo(float).eps):
                powers.append((value, base, exponent))
                exponent += 1
                value *= base
        if len(powers) == desired_atoms:
            break
        if attempts > 1_000_000:
            raise RuntimeError("matched pseudo sampler did not terminate")
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
    return terms, attempts, {
        "authentic_base_count": desired_bases,
        "authentic_atom_count": desired_atoms,
        "pseudo_base_count": len({term.base for term in terms}),
        "pseudo_atom_count": len(terms),
    }


def deterministic_vector(size: int, alternating: bool = False) -> mp.matrix:
    vector = mp.matrix([
        ((-1) ** i if alternating else 1) * mp.mpf(1) / (i + 1)
        for i in range(size)
    ])
    return core.normalize_vector(vector)


def inverse_smallest(matrix: mp.matrix, iterations: int = 6) -> tuple[mp.mpf, mp.matrix, mp.mpf]:
    vector = deterministic_vector(matrix.rows)
    for _ in range(iterations):
        vector = core.normalize_vector(mp.lu_solve(matrix, vector))
    value = (vector.T * matrix * vector)[0]
    residual = vector_norm(matrix * vector - value * vector)
    return value, vector, residual


def refine_numpy_seed(matrix: mp.matrix, index: int, iterations: int) -> tuple[mp.mpf, mp.matrix, mp.mpf]:
    values, vectors = np.linalg.eigh(np.array(matrix.tolist(), dtype=float))
    seed = mp.matrix([mp.mpf(format(vectors[i, index], ".17g")) for i in range(matrix.rows)])
    return core.refine_ground(matrix, seed, iterations=iterations)


def authentic_even_seed(x: int) -> mp.matrix:
    source_x = x if x in (9, 13, 14) else 14
    path = CORE_DIR / f"true-x{source_x}-N120-dps100.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return mp.matrix([mp.mpf(value) for value in payload["even_unit_vector"]])


def second_even_authentic(matrix: mp.matrix, ground: mp.matrix, x: int) -> tuple[mp.mpf, mp.mpf, str]:
    if x in (9, 13, 14):
        path = CORE_DIR / f"true-x{x}-N120-dps100.json"
        stored = json.loads(path.read_text(encoding="utf-8"))["eigensolve"]["first_even_values"][1]
        value = mp.mpf(stored)
        return value, mp.mpf("nan"), "committed 100-dps full eigsy value for the identical matrix"
    shift = mp.sqrt(frobenius_sq(matrix))
    deflated = matrix + shift * (ground * ground.T)
    vector = deterministic_vector(matrix.rows, alternating=True)
    for _ in range(6):
        vector = core.normalize_vector(mp.lu_solve(deflated, vector))
        vector = core.normalize_vector(vector - ground * (ground.T * vector)[0])
    value = (vector.T * matrix * vector)[0]
    residual = vector_norm(matrix * vector - value * vector)
    return value, residual, "100-dps inverse iteration after rank-one ground deflation"


def spectrum(
    kind: str, x: int, even: mp.matrix, odd: mp.matrix
) -> dict[str, object]:
    if kind == "authentic":
        seed = authentic_even_seed(x)
        ground_even, vector_even, residual_even = core.refine_ground(even, seed, iterations=3)
        if residual_even > mp.mpf("1e-70"):
            ground_even, vector_even, residual_even = inverse_smallest(even)
        ground_odd, vector_odd, residual_odd = inverse_smallest(odd)
        second_even, second_residual, second_method = second_even_authentic(even, vector_even, x)
        first = {"even": (ground_even, vector_even, residual_even), "odd": (ground_odd, vector_odd, residual_odd)}
        second_same = {"even": second_even, "odd": mp.inf}
        methods = {
            "even_ground": "100-dps Rayleigh refinement of a committed zero-data ground seed",
            "odd_ground": "100-dps unshifted inverse iteration",
            "second_even": second_method,
        }
        extra = {"second_even_residual": second_residual}
    else:
        float_even = np.linalg.eigvalsh(np.array(even.tolist(), dtype=float))
        float_odd = np.linalg.eigvalsh(np.array(odd.tolist(), dtype=float))
        sector = "even" if float_even[0] < float_odd[0] else "odd"
        block = even if sector == "even" else odd
        other_block = odd if sector == "even" else even
        value, vector, residual = refine_numpy_seed(block, 0, 2)
        second_value, _, second_residual = refine_numpy_seed(block, 1, 1)
        other_value, other_vector, other_residual = refine_numpy_seed(other_block, 0, 1)
        first = {
            sector: (value, vector, residual),
            "odd" if sector == "even" else "even": (other_value, other_vector, other_residual),
        }
        second_same = {sector: second_value, "odd" if sector == "even" else "even": mp.inf}
        methods = {"all": "binary64 ordering seed followed by 100-dps Rayleigh iteration"}
        extra = {"same_sector_second_residual": second_residual}

    ground_sector = min(("even", "odd"), key=lambda name: first[name][0])
    other_sector = "odd" if ground_sector == "even" else "even"
    ground_value, ground_vector, ground_residual = first[ground_sector]
    competitor_same = second_same[ground_sector]
    competitor_other = first[other_sector][0]
    next_value = min(competitor_same, competitor_other)
    gap = next_value - ground_value
    if not gap > 0:
        raise RuntimeError(f"nonpositive global gap for {kind}, x={x}")
    return {
        "ground_sector": ground_sector,
        "ground_value": ground_value,
        "ground_vector": ground_vector,
        "ground_residual": ground_residual,
        "ground_residual_over_gap": ground_residual / gap,
        "first_even": first["even"][0],
        "first_odd": first["odd"][0],
        "same_sector_second": competitor_same,
        "other_sector_first": competitor_other,
        "next_global_value": next_value,
        "gap": gap,
        "methods": methods,
        "extra": extra,
    }


def expand_vector(vector: mp.matrix, sector: str) -> mp.matrix:
    full = mp.matrix(2 * N + 1, 1)
    if sector == "even":
        full[N] = vector[0]
        for n in range(1, N + 1):
            full[N + n] = full[N - n] = vector[n] / mp.sqrt(2)
    else:
        for n in range(1, N + 1):
            full[N + n] = vector[n - 1] / mp.sqrt(2)
            full[N - n] = -vector[n - 1] / mp.sqrt(2)
    return full


def serialize_spectrum(data: dict[str, object]) -> dict[str, object]:
    return {
        "ground_sector": data["ground_sector"],
        "ground_value": nstr(data["ground_value"]),
        "first_even": nstr(data["first_even"]),
        "first_odd": nstr(data["first_odd"]),
        "same_sector_second": nstr(data["same_sector_second"]),
        "other_sector_first": nstr(data["other_sector_first"]),
        "next_global_value": nstr(data["next_global_value"]),
        "gap_delta": nstr(data["gap"]),
        "ground_eigen_residual_2": nstr(data["ground_residual"]),
        "ground_eigen_residual_over_gap": nstr(data["ground_residual_over_gap"]),
        "methods": data["methods"],
        "extra_residuals": {
            key: nstr(value) for key, value in data["extra"].items()
        },
    }


def evaluate_case(
    kind: str,
    x: int,
    terms: Sequence[core.ArithmeticTerm],
    alpha: Sequence[mp.mpf],
    beta: Sequence[mp.mpf],
    gamma: Sequence[mp.mpf],
    p_full: mp.matrix,
    p_even: mp.matrix,
    p_odd: mp.matrix,
) -> dict[str, object]:
    started = time.perf_counter()
    length = mp.log(x)
    full = full_weil(length, terms, alpha, beta, gamma)
    direct_even, direct_odd = core.parity_blocks_from_arrays(N, length, terms, alpha, beta, gamma, DPS)
    projected_even, projected_odd, cross = project_parity(full)
    parity_error = max(
        max_matrix_difference(direct_even, projected_even),
        max_matrix_difference(direct_odd, projected_odd),
    )

    c_even = projected_even * p_even - p_even * projected_even
    c_odd = projected_odd * p_odd - p_odd * projected_odd
    norm_c = mp.sqrt(frobenius_sq(c_even) + frobenius_sq(c_odd))
    norm_m = mp.sqrt(frobenius_sq(full))
    norm_p = mp.sqrt(frobenius_sq(p_full))
    c_f = norm_c / (norm_m * norm_p)

    direct_c_even = direct_even * p_even - p_even * direct_even
    direct_c_odd = direct_odd * p_odd - p_odd * direct_odd
    parity_norm_c = mp.sqrt(frobenius_sq(direct_c_even) + frobenius_sq(direct_c_odd))
    parity_c_f = parity_norm_c / (
        mp.sqrt(frobenius_sq(direct_even) + frobenius_sq(direct_odd))
        * mp.sqrt(frobenius_sq(p_even) + frobenius_sq(p_odd))
    )

    spec = spectrum(kind, x, direct_even, direct_odd)
    sector = spec["ground_sector"]
    vector = spec["ground_vector"]
    matrix_block = direct_even if sector == "even" else direct_odd
    p_block = p_even if sector == "even" else p_odd
    c_block = direct_c_even if sector == "even" else direct_c_odd
    action = c_block * vector
    residual = vector_norm(action)
    rho = residual / spec["gap"]

    full_vector = expand_vector(vector, sector)
    full_action = full * (p_full * full_vector) - p_full * (full * full_vector)
    full_action_error = vector_norm(full_action - expand_vector(action, sector))
    identity_action = (matrix_block - spec["ground_value"] * mp.eye(matrix_block.rows)) * (p_block * vector)
    identity_error = vector_norm(action - identity_action)
    eigen_residual_bound = mp.sqrt(frobenius_sq(p_block)) * spec["ground_residual"]

    return {
        "kind": kind,
        "term_count": len(terms),
        "terms": [term.__dict__ for term in terms],
        "metrics": {
            "full_normalized_frobenius_commutator_c_F": nstr(c_f),
            "full_frobenius_commutator_norm": nstr(norm_c),
            "full_weil_frobenius_norm": nstr(norm_m),
            "full_prolate_frobenius_norm": nstr(norm_p),
            "ground_commutator_residual_r_xi": nstr(residual),
            "gap_delta": nstr(spec["gap"]),
            "rho_r_xi_over_delta": nstr(rho),
            "classification": "below_gap" if rho < 1 else "above_gap",
        },
        "spectrum": serialize_spectrum(spec),
        "audits": {
            "full_weil_to_direct_parity_max_abs": nstr(parity_error),
            "full_weil_even_odd_cross_max_abs": nstr(cross),
            "full_fro_c_F_minus_direct_parity_c_F": nstr(abs(c_f - parity_c_f)),
            "full_action_minus_separate_parity_action_2": nstr(full_action_error),
            "eigenvector_commutator_identity_error_2": nstr(identity_error),
            "identity_error_upper_bound_from_eigen_residual": nstr(eigen_residual_bound),
        },
        "elapsed_seconds": time.perf_counter() - started,
    }


def main() -> None:
    mp.mp.dps = DPS
    started = time.perf_counter()
    records: list[dict[str, object]] = []
    pseudo_meta: dict[str, object] = {}
    for x in X_VALUES:
        length = mp.log(x)
        alpha, beta, gamma = core.archimedean_arrays(N, length, DPS)
        authentic = core.prime_power_terms(x)
        pseudo, attempts, counts = matched_pseudo_terms(x)
        pseudo_meta[str(x)] = {
            "rejection_attempts": attempts,
            "count_match": counts,
        }

        p_full = full_prolate(x)
        p_even, p_odd, p_cross = project_parity(p_full)
        p_even_direct, p_odd_direct = direct_prolate_blocks(x)
        p_audit = {
            "x": x,
            "full_to_direct_parity_max_abs": nstr(max(
                max_matrix_difference(p_even, p_even_direct),
                max_matrix_difference(p_odd, p_odd_direct),
            )),
            "full_even_odd_cross_max_abs": nstr(p_cross),
        }
        for kind, terms in (
            ("authentic", authentic),
            ("pseudo_prime", pseudo),
            ("archimedean_only", []),
        ):
            record = evaluate_case(kind, x, terms, alpha, beta, gamma, p_full, p_even, p_odd)
            record["x"] = x
            record["N"] = N
            record["prolate_assembly_audit"] = p_audit
            records.append(record)
            print(json.dumps({
                "finished": kind,
                "x": x,
                "rho": record["metrics"]["rho_r_xi_over_delta"],
                "seconds": record["elapsed_seconds"],
            }), flush=True)

    authentic_classifications = [
        row["metrics"]["classification"] for row in records if row["kind"] == "authentic"
    ]
    payload = {
        "schema": "codex-r5b-q2-commutator-backup-v1",
        "status": "MEASURED",
        "scope": "frozen affine-Galerkin PW commutator only",
        "parameters": {
            "x_values": list(X_VALUES),
            "N": N,
            "working_decimal_digits": DPS,
            "pseudo_seed": PSEUDO_SEED,
            "commutator_order": "M P - P M",
            "prolate_scalar_shift": None,
            "prolate_rescaling": None,
        },
        "prolate_entries": {
            "diagonal": "2*pi^2*n^2/3 + 4*pi^2*x^2/3",
            "off_diagonal": "(8*x^2 - 2*m*n)/(m-n)^2",
        },
        "pseudo_sampler": pseudo_meta,
        "records": records,
        "prediction_outcome": {
            "predicted_authentic_rho_above_one_at_all_x": True,
            "observed_authentic_classifications": authentic_classifications,
            "all_authentic_above_gap": all(value == "above_gap" for value in authentic_classifications),
        },
        "construction": {
            "target_data_present": False,
            "scoring_present": False,
            "full_basis_order": "-N,...,N",
            "full_frobenius_method": "exact orthogonal decomposition into independently projected even and odd blocks",
            "ground_gap_rule": "minimum across both parity sectors; each control uses its own matrix and ground vector",
        },
        "source_sha256": {
            "q2_commutator_backup.py": sha256(Path(__file__)),
            "weil_core.py": sha256(CORE_DIR / "weil_core.py"),
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    core.write_json(OUTPUT, payload)
    print(json.dumps({"output": str(OUTPUT), "seconds": payload["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
