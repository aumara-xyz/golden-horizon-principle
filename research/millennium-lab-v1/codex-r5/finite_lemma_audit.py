#!/usr/bin/env python3
"""Finite-N structural audit for the Round 5 simple/even lemma attempt.

The construction is target-blind.  It evaluates the published finite Weil
matrix, splits parity algebraically, looks for signed-cycle and sign-regular
obstructions, and replays the decisive finite claims with Arb balls.

Run with the locally installed python-flint wheel, for example

    PYTHONPATH=/private/tmp/codex-r5-python python3 finite_lemma_audit.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import time
from typing import Iterable, Sequence

import mpmath as mp
import numpy as np

import weil_core as core

try:
    from flint import acb, acb_mat, arb, arb_mat, ctx
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "python-flint is required for the outward-rounded replay; set "
        "PYTHONPATH=/private/tmp/codex-r5-python"
    ) from exc


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "outputs" / "finite-lemma-audit.json"
N = 120


@dataclass(frozen=True)
class Case:
    label: str
    x: str
    prime_cutoff: int
    omitted_base: int | None = None
    mutation: str | None = None


CASES = [
    Case("x=5", "5", 5),
    Case("x=9", "9", 9),
    Case("x=12", "12", 12),
    Case("x=13", "13", 13),
    Case("x=14", "14", 14),
    Case("x=20", "20", 20),
    Case("x=13 delete p=13", "13", 13, 13, "delete every power of base 13"),
    Case(
        "x=13.25 fixed p^a<=13",
        "13.25",
        13,
        None,
        "continuous cutoff changed while the arithmetic support is fixed",
    ),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mpstr(value: mp.mpf, digits: int) -> str:
    return mp.nstr(value, digits)


def arb_ball_record(value: arb) -> dict[str, object]:
    return {
        "ball": str(value),
        "lower": str(value.lower()),
        "upper": str(value.upper()),
        "contains_zero": bool(value.contains(0)),
        "sign": 1 if value > 0 else (-1 if value < 0 else 0),
    }


def acb_ball_record(value: acb) -> dict[str, object]:
    return {"real": arb_ball_record(value.real), "imag": arb_ball_record(value.imag)}


def arb_lerch_two(z: arb, a: acb, dps: int) -> acb:
    """Enclose Phi(z,2,a) by a finite geometric series plus a tail ball."""

    # Here Re(a)=1/4 and 0<z<=1/25.  After K terms,
    # |tail| <= z^K / ((K+1/4)^2 (1-z)).
    K = max(80, 2 * dps)
    total = acb(0)
    power = arb(1)
    for k in range(K):
        total += power / (a + k) ** 2
        power *= z
    lower_denominator = arb(K) + arb(1) / 4
    tail = power / (lower_denominator**2 * (1 - z))
    # Radius construction is itself rounded outwards by Arb.
    error = arb(0, tail.upper())
    return total + acb(error, error)


def arb_archimedean_arrays(
    n_max: int, length: arb, dps: int
) -> tuple[list[arb], list[arb], list[arb]]:
    """Outward-rounded replay of Proposition 4.2 used by weil_core.py."""

    pi = arb.pi()
    z = (-2 * length).exp()
    decay = (-length / 2).exp()
    quarter = arb(1) / 4

    def hyper_unit(a: acb) -> acb:
        # b-c=-1 exactly, supplied to Arb's continuation logic.
        return acb(z).hypgeom_2f1(1, a, a + 1, bc=True)

    f0 = hyper_unit(acb(quarter)).real
    c_plus_w = (
        ((length / 2).exp() - 1).log()
        - ((length / 2).exp() + 1).log()
    ) / 2
    c_plus_w += ((length / 2).exp()).atan() - pi / 4
    c_plus_w += arb.const_euler() / 2 + (8 * pi).log() / 2

    alpha: list[arb] = []
    beta: list[arb] = []
    gamma: list[arb] = []
    for n in range(n_max + 1):
        nn = arb(n)
        a = acb(quarter, pi * nn / length)
        hyp = hyper_unit(a)
        sin_integral = decay * (
            2 * length * hyp / acb(length, 4 * pi * nn)
        ).imag
        sin_integral += a.digamma().imag / 2

        xcos_integral = -length * decay * (
            2 * length * hyp / acb(4 * pi * nn, -length)
        ).imag
        xcos_integral -= decay * arb_lerch_two(z, a, dps).real / 4
        xcos_integral += a.polygamma(1).real / 4

        cos_minus_one = -decay * (
            2 * length * hyp / acb(length, 4 * pi * nn)
        ).real
        cos_minus_one += 2 * decay * f0
        cos_minus_one -= (a.digamma() - acb(quarter).digamma()).real / 2

        alpha.append(sin_integral / pi)
        beta.append(xcos_integral / length)
        gamma.append(cos_minus_one + c_plus_w)
    return alpha, beta, gamma


def arb_prime_terms(case: Case) -> list[tuple[arb, arb, int, int]]:
    result: list[tuple[arb, arb, int, int]] = []
    for term in core.prime_power_terms(case.prime_cutoff, case.omitted_base):
        p = int(term.base)
        q = int(term.location)
        result.append((arb(q).log(), arb(p).log() / arb(q).sqrt(), p, q))
    return result


def arb_pole_entry(n: int, m: int, length: arb) -> arb:
    pi = arb.pi()
    numerator = 32 * length * (length / 4).sinh() ** 2
    numerator *= length**2 - 16 * pi**2 * m * n
    denominator = (length**2 + 16 * pi**2 * m * m) * (
        length**2 + 16 * pi**2 * n * n
    )
    return numerator / denominator


def arb_parity_blocks(case: Case, n_max: int, dps: int) -> tuple[arb_mat, arb_mat]:
    """Build the two parity blocks entirely with outward-rounded Arb balls."""

    ctx.dps = dps
    length = arb(case.x).log()
    alpha, beta, gamma = arb_archimedean_arrays(n_max, length, dps)
    terms = arb_prime_terms(case)
    off: dict[int, arb] = {}
    diagonal_arithmetic: dict[int, arb] = {}
    pi = arb.pi()
    for n in range(-n_max, n_max + 1):
        alpha_n = alpha[abs(n)] if n >= 0 else -alpha[abs(n)]
        sine_sum = arb(0)
        diagonal_sum = arb(0)
        for y, weight, _p, _q in terms:
            sine_sum += weight * (2 * pi * n * y / length).sin() / pi
            diagonal_sum += (
                weight
                * 2
                * (1 - y / length)
                * (2 * pi * n * y / length).cos()
            )
        off[n] = alpha_n + sine_sum
        diagonal_arithmetic[n] = diagonal_sum

    def entry(n: int, m: int) -> arb:
        if n == m:
            return (
                arb_pole_entry(n, n, length)
                - (2 * gamma[abs(n)] - 2 * beta[abs(n)])
                - diagonal_arithmetic[n]
            )
        return arb_pole_entry(n, m, length) + (off[n] - off[m]) / (n - m)

    even = arb_mat(n_max + 1, n_max + 1)
    odd = arb_mat(n_max, n_max)
    sqrt2 = arb(2).sqrt()
    even[0, 0] = entry(0, 0)
    for n in range(1, n_max + 1):
        value = sqrt2 * entry(0, n)
        even[0, n] = value
        even[n, 0] = value
    for n in range(1, n_max + 1):
        for m in range(n, n_max + 1):
            a = entry(n, m)
            b = entry(n, -m)
            even[n, m] = even[m, n] = a + b
            odd[n - 1, m - 1] = odd[m - 1, n - 1] = a - b
    return even, odd


def sign(value: float, tolerance: float = 1e-14) -> int:
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def first_frustrated_triangle(array: np.ndarray, target_edge_sign: int) -> dict[str, object] | None:
    """Find a lexicographic signed triangle obstructing sign propagation."""

    size = array.shape[0]
    for i, j, k in itertools.combinations(range(size), 3):
        edge_values = [array[i, j], array[j, k], array[i, k]]
        edge_signs = [sign(value) for value in edge_values]
        if 0 in edge_signs:
            continue
        # Relations s_i*s_j = target/sign(A_ij).  Their triangle product
        # must be +1 for a solution.
        relation_product = math.prod(target_edge_sign * value for value in edge_signs)
        if relation_product == -1:
            return {
                "indices": [i, j, k],
                "edge_values": edge_values,
                "edge_signs": edge_signs,
                "target_off_diagonal_sign": target_edge_sign,
                "relation_product": relation_product,
            }
    return None


def determinant(array: np.ndarray, rows: Sequence[int], cols: Sequence[int]) -> float:
    return float(np.linalg.det(array[np.ix_(rows, cols)]))


def minor_sign_witnesses(array: np.ndarray, max_index: int = 12) -> dict[str, object]:
    """Find deterministic opposite-sign witnesses for minor orders 1--4."""

    indices = range(min(max_index, array.shape[0]))
    result: dict[str, object] = {}
    for order in range(1, 5):
        combos = list(itertools.combinations(indices, order))
        positive = None
        negative = None
        checked = 0
        # The lexical scan is capped deterministically; it is an obstruction
        # search, not a claim that all minors have been enumerated.
        for rows in combos:
            for cols in combos:
                checked += 1
                value = determinant(array, rows, cols)
                scale = max(1.0, float(np.linalg.norm(array[np.ix_(rows, cols)], ord=2)) ** order)
                if abs(value) <= 1e-12 * scale:
                    continue
                item = {"rows": list(rows), "cols": list(cols), "value": value}
                if value > 0 and positive is None:
                    positive = item
                if value < 0 and negative is None:
                    negative = item
                if positive is not None and negative is not None:
                    break
            if positive is not None and negative is not None:
                break
        result[str(order)] = {
            "checked_until_witness": checked,
            "positive": positive,
            "negative": negative,
            "opposite_signs_found": positive is not None and negative is not None,
        }
    return result


def arb_minor(matrix: arb_mat, witness: dict[str, object]) -> arb:
    rows = witness["rows"]
    cols = witness["cols"]
    sub = arb_mat(len(rows), len(cols))
    for i, row in enumerate(rows):
        for j, col in enumerate(cols):
            sub[i, j] = matrix[row, col]
    return sub.det()


def interval_eigenpairs(
    matrix: arb_mat, algorithm: str = "rump"
) -> tuple[list[acb], acb_mat]:
    """Return Arb-enclosed eigenpairs sorted by the real midpoint."""

    values, vectors = acb_mat(matrix).eig(
        algorithm=algorithm, nonstop=False, right=True
    )
    order = sorted(range(len(values)), key=lambda j: float(values[j].real.mid()))
    sorted_vectors = acb_mat(matrix.nrows(), matrix.ncols())
    for new_j, old_j in enumerate(order):
        for i in range(matrix.nrows()):
            sorted_vectors[i, new_j] = vectors[i, old_j]
    return [values[j] for j in order], sorted_vectors


def enclosed_pair_residual(
    matrix: arb_mat, value: acb, vectors: acb_mat, column: int
) -> dict[str, object]:
    """Direct outward-rounded residual of one enclosed eigenpair."""

    a = acb_mat(matrix)
    vector = acb_mat(matrix.nrows(), 1)
    for i in range(matrix.nrows()):
        vector[i, 0] = vectors[i, column]
    residual = a * vector - vector * value
    residual_squared = arb(0)
    vector_squared = arb(0)
    for i in range(matrix.nrows()):
        residual_squared += abs(residual[i, 0]) ** 2
        vector_squared += abs(vector[i, 0]) ** 2
    # Rounding a nonnegative quantity centered at zero may give a tiny
    # symmetric ball.  Intersecting with [0,+inf) before sqrt is rigorous.
    relative_residual = residual_squared.nonnegative_part().sqrt()
    relative_residual /= vector_squared.nonnegative_part().sqrt()
    return {
        "eigenvalue": acb_ball_record(value),
        "relative_residual_norm": arb_ball_record(relative_residual),
    }


def matrix_sample_agreement(
    mp_matrix: mp.matrix, arb_matrix: arb_mat, digits: int
) -> list[dict[str, object]]:
    samples = [(0, 0), (0, 1), (1, 2), (3, 7), (17, 41), (60, 120), (119, 120)]
    output = []
    for i, j in samples:
        value = arb_matrix[i, j]
        mp_value = mpstr(mp_matrix[i, j], digits)
        mpmath_rounding_ball = arb(mp_value, arb(10) ** (-(digits - 2)))
        output.append(
            {
                "indices": [i, j],
                "mpmath": mp_value,
                "arb": arb_ball_record(value),
                "mpmath_rounding_ball": str(mpmath_rounding_ball),
                "arb_overlaps_mpmath_rounded_value": bool(
                    value.overlaps(mpmath_rounding_ball)
                ),
            }
        )
    return output


def source_audit() -> dict[str, object]:
    inspected = [Path(__file__), HERE / "weil_core.py"]
    # Assemble forbidden spellings so the audit does not match itself.
    banned = ["zeta" + "zero", "zeros" + ".txt", "14.134" + "725"]
    findings = []
    for path in inspected:
        source = path.read_text()
        for token in banned:
            if token.lower() in source.lower():
                findings.append({"file": path.name, "token": token})
    return {
        "inspected": [path.name for path in inspected],
        "forbidden_token_findings": findings,
        "passed": not findings,
    }


def run_case(case: Case, mp_dps: int, arb_dps: int) -> dict[str, object]:
    started = time.perf_counter()
    mp.mp.dps = mp_dps
    terms = core.prime_power_terms(case.prime_cutoff, case.omitted_base)
    even, odd, meta = core.parity_blocks(N, case.x, terms, mp_dps)

    even_np = np.array([[float(even[i, j]) for j in range(even.cols)] for i in range(even.rows)])
    positivity_cycle = first_frustrated_triangle(even_np, +1)
    m_matrix_cycle = first_frustrated_triangle(even_np, -1)
    minor_witnesses = minor_sign_witnesses(even_np)

    arb_started = time.perf_counter()
    even_arb, odd_arb = arb_parity_blocks(case, N, arb_dps)
    arb_build_seconds = time.perf_counter() - arb_started

    # Certify the signed-cycle edges and determinant witnesses directly.
    for cycle in [positivity_cycle, m_matrix_cycle]:
        if cycle is None:
            continue
        i, j, k = cycle["indices"]
        cycle["arb_edges"] = [
            arb_ball_record(even_arb[i, j]),
            arb_ball_record(even_arb[j, k]),
            arb_ball_record(even_arb[i, k]),
        ]
        cycle["all_edge_signs_certified"] = all(
            item["sign"] != 0 for item in cycle["arb_edges"]
        )

    for _order, entry in minor_witnesses.items():
        for orientation in ["positive", "negative"]:
            witness = entry[orientation]
            if witness is None:
                continue
            ball = arb_minor(even_arb, witness)
            witness["arb"] = arb_ball_record(ball)
            witness["certified_expected_sign"] = (
                ball > 0 if orientation == "positive" else ball < 0
            )

    eig_started = time.perf_counter()
    eigen_error = None
    try:
        even_enclosures, even_vectors = interval_eigenpairs(even_arb)
        odd_enclosures, odd_vectors = interval_eigenpairs(odd_arb)
    except (ValueError, RuntimeError) as exc:
        even_enclosures = []
        odd_enclosures = []
        even_vectors = acb_mat(0, 0)
        odd_vectors = acb_mat(0, 0)
        eigen_error = f"{type(exc).__name__}: {exc}"
    arb_eig_seconds = time.perf_counter() - eig_started

    interval_ordering = False
    lowest_enclosures: dict[str, object]
    if len(even_enclosures) >= 2 and len(odd_enclosures) >= 1:
        e0 = even_enclosures[0]
        e1 = even_enclosures[1]
        o0 = odd_enclosures[0]
        interval_ordering = bool(
            e0.imag.contains(0)
            and e1.imag.contains(0)
            and o0.imag.contains(0)
            and e0.real.upper() < e1.real.lower()
            and e0.real.upper() < o0.real.lower()
        )
        lowest_enclosures = {
            "even_0": acb_ball_record(e0),
            "even_1": acb_ball_record(e1),
            "odd_0": acb_ball_record(o0),
        }
        ritz = {
            "even_0": enclosed_pair_residual(even_arb, e0, even_vectors, 0),
            "even_1": enclosed_pair_residual(even_arb, e1, even_vectors, 1),
            "odd_0": enclosed_pair_residual(odd_arb, o0, odd_vectors, 0),
        }
    else:
        lowest_enclosures = {}
        ritz = {}

    if lowest_enclosures:
        numeric_low_spectrum = {
            "even_0": str(even_enclosures[0].real.mid()),
            "even_1": str(even_enclosures[1].real.mid()),
            "odd_0": str(odd_enclosures[0].real.mid()),
            "even_0_below_even_1_and_odd_0": bool(interval_ordering),
        }
    else:
        # This is only a diagnostic fallback if Arb cannot isolate the pairs.
        float_even = np.linalg.eigvalsh(even_np)
        float_odd = np.linalg.eigvalsh(
            np.array([[float(odd[i, j]) for j in range(odd.cols)] for i in range(odd.rows)])
        )
        numeric_low_spectrum = {
            "even_0": repr(float_even[0]),
            "even_1": repr(float_even[1]),
            "odd_0": repr(float_odd[0]),
            "even_0_below_even_1_and_odd_0": bool(
                float_even[0] < float_even[1] and float_even[0] < float_odd[0]
            ),
            "binary64_fallback": True,
        }

    payload = {
        "label": case.label,
        "parameters": {
            "x": case.x,
            "N": N,
            "prime_cutoff": case.prime_cutoff,
            "omitted_base": case.omitted_base,
            "mpmath_dps": mp_dps,
            "arb_dps": arb_dps,
            "mutation": case.mutation,
        },
        "term_count": len(terms),
        "analytic_mutation_note": (
            "The omitted q=13 atom lies at y=log(x)=L, where every q-entry "
            "vanishes identically; deleting base 13 is therefore an exact "
            "no-op for x=13."
            if case.x == "13" and case.omitted_base == 13
            else None
        ),
        "meta": meta,
        "numeric_low_spectrum": numeric_low_spectrum,
        "structural_tests": {
            "positive_offdiagonal_sign_conjugation": {
                "exists": positivity_cycle is None,
                "obstructing_triangle": positivity_cycle,
            },
            "m_matrix_offdiagonal_sign_conjugation": {
                "exists": m_matrix_cycle is None,
                "obstructing_triangle": m_matrix_cycle,
            },
            "minor_sign_witnesses": minor_witnesses,
            "strict_sign_regular_through_order_4": all(
                not item["opposite_signs_found"] for item in minor_witnesses.values()
            ),
        },
        "arb_replay": {
            "backend": "python-flint 0.6.0 / Arb outward-rounded balls",
            "mpmath_sample_containment": matrix_sample_agreement(
                even, even_arb, min(mp_dps - 15, arb_dps - 15)
            ),
            "enclosed_eigenpair_residuals": ritz,
            "full_eigenvalue_enclosure_error": eigen_error,
            "lowest_eigenvalue_enclosures": lowest_enclosures,
            "finite_simple_even_ordering_certified": interval_ordering,
        },
        "timings_seconds": {
            "arb_build": arb_build_seconds,
            "arb_eigensolve": arb_eig_seconds,
            "total": time.perf_counter() - started,
        },
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mp-dps", type=int, default=180)
    parser.add_argument("--arb-dps", type=int, default=180)
    parser.add_argument("--case", action="append", help="run only a named case; repeatable")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = source_audit()
    if not audit["passed"]:
        raise RuntimeError(f"target-blind source audit failed: {audit}")
    chosen = CASES
    if args.case:
        wanted = set(args.case)
        chosen = [case for case in CASES if case.label in wanted]
        missing = wanted - {case.label for case in chosen}
        if missing:
            raise ValueError(f"unknown case labels: {sorted(missing)}")

    started = time.perf_counter()
    records = []
    for case in chosen:
        print(json.dumps({"state": "starting", "case": case.label}), flush=True)
        record = run_case(case, args.mp_dps, args.arb_dps)
        records.append(record)
        print(
            json.dumps(
                {
                    "state": "finished",
                    "case": case.label,
                    "certified_ordering": record["arb_replay"][
                        "finite_simple_even_ordering_certified"
                    ],
                    "seconds": record["timings_seconds"]["total"],
                }
            ),
            flush=True,
        )

    payload = {
        "kind": "Round 5.4 finite simple/even structural and interval audit",
        "status_vocabulary": ["MEASURED", "UNVERIFIED", "PREDICTED", "VOID"],
        "source_audit": audit,
        "cases": records,
        "summary": {
            "case_count": len(records),
            "all_numeric_simple_even": all(
                case["numeric_low_spectrum"]["even_0_below_even_1_and_odd_0"]
                for case in records
            ),
            "all_interval_orderings_certified": all(
                case["arb_replay"]["finite_simple_even_ordering_certified"]
                for case in records
            ),
            "all_positive_conjugations_obstructed": all(
                not case["structural_tests"]["positive_offdiagonal_sign_conjugation"][
                    "exists"
                ]
                for case in records
            ),
            "all_m_matrix_conjugations_obstructed": all(
                not case["structural_tests"]["m_matrix_offdiagonal_sign_conjugation"][
                    "exists"
                ]
                for case in records
            ),
            "any_strict_sign_regular_through_order_4": any(
                case["structural_tests"]["strict_sign_regular_through_order_4"]
                for case in records
            ),
        },
        "builder_sha256": sha256(HERE / "weil_core.py"),
        "runner_sha256": sha256(Path(__file__)),
        "elapsed_seconds": time.perf_counter() - started,
        "target_data_present": False,
        "scoring_present": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "summary": payload["summary"]}))


if __name__ == "__main__":
    main()
