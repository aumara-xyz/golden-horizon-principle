#!/usr/bin/env python3
"""Build zero-blind, parameter-matched controls for the R5 N-path matches.

This is a post-registration audit.  It constructs spectra only: no reference
ordinate, target table, fitted scale, score, or accuracy statistic is present.
The separate scorer must validate the resulting hash before it may evaluate
the frozen ordinal range 20--50.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

import mpmath as mp
import numpy as np

import run_prolate_only_control as prolate
import weil_core as core


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "outputs" / "posthoc-matched-controls-blind.json"
PAIRS = ((14, 112), (14, 120), (14, 128), (14, 140), (14, 168),
         (16, 128), (16, 160), (16, 192))
SEED = 52025001
MATRIX_DPS = 100
ROOT_COUNT = 60
PROLATE_DPS = 100
PROLATE_LMAX = 200
PROLATE_QUADRATURE_ORDER = 24
PROLATE_PANELS_PER_CYCLE = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_audit() -> dict[str, object]:
    """Reject target/evaluator tokens in every construction source."""

    inspected = [Path(__file__), HERE / "weil_core.py", HERE / "run_prolate_only_control.py"]
    banned = [
        "zeta" + "zero",
        "zeros" + ".txt",
        "14.134" + "725",
        "mpmath." + "zeta" + "zero",
    ]
    findings: list[dict[str, str]] = []
    for path in inspected:
        source = path.read_text(encoding="utf-8")
        for token in banned:
            if token.lower() in source.lower():
                findings.append({"file": path.name, "token": token})
    return {
        "inspected": [path.name for path in inspected],
        "banned_token_count": len(banned),
        "findings": findings,
        "passed": not findings,
    }


def matched_pseudo_terms(seed: int, x: int) -> tuple[list[core.ArithmeticTerm], int, dict[str, int]]:
    """Generalize the frozen pseudo sampler to exact base/power counts at x.

    The original gate accepts six continuous bases with probability
    log(2)/log(base), then rejects the complete comb unless it has nine terms.
    Here both counts are read from the authentic support *before* sampling.
    Thus x=14 exactly replays the old six-base/nine-term rule, while x=16 uses
    the same generator and seed with the authentic six-base/ten-term count.
    """

    authentic = core.prime_power_terms(x)
    desired_terms = len(authentic)
    desired_bases = len({term.base for term in authentic})
    rng = np.random.Generator(np.random.PCG64DXSM(seed))
    attempts = 0
    log2 = math.log(2.0)
    while True:
        attempts += 1
        bases: list[float] = []
        while len(bases) < desired_bases:
            candidate = float(rng.uniform(2.0, float(x)))
            if rng.random() <= log2 / math.log(candidate):
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
        if len(powers) == desired_terms:
            break
        if attempts > 1_000_000:
            raise RuntimeError("matched pseudo-prime rejection sampler did not terminate")

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
        "authentic_term_count": desired_terms,
        "pseudo_base_count": len({term.base for term in terms}),
        "pseudo_term_count": len(terms),
    }


def roots_from_even(even: mp.matrix, odd: mp.matrix, x: int) -> dict[str, object]:
    """Refine a blind binary64 seed at 100 dps and check the whole root list."""

    minimum_seed, vector_seed, even_values = core.float_ground(even)
    odd_values = np.linalg.eigvalsh(np.array(odd.tolist(), dtype=float))
    initial = mp.matrix([mp.mpf(format(value, ".17g")) for value in vector_seed])
    minimum, vector, residual = core.refine_ground(even, initial, iterations=1)
    gap_seed = mp.mpf(format(float(even_values[1] - even_values[0]), ".17g"))
    residual_over_gap = residual / abs(gap_seed)
    eigen_method = "one 100-dps Rayleigh refinement from binary64 ground seed"
    if residual_over_gap >= mp.mpf("1e-30"):
        # This path is deliberately expensive but prevents a small-gap control
        # from silently inheriting the wrong binary64 eigenspace.
        eigenvalues_mp, eigenvectors_mp = mp.eigsy(even)
        minimum = eigenvalues_mp[0]
        vector = core.normalize_vector(eigenvectors_mp[:, 0])
        residual = mp.norm(even * vector - minimum * vector)
        residual_over_gap = residual / abs(gap_seed)
        eigen_method = "fallback full mpmath.eigsy after residual/gap guard"
    if residual_over_gap >= mp.mpf("1e-30"):
        raise RuntimeError(f"unresolved ground state at x={x}: residual/gap={residual_over_gap}")

    full = core.full_coefficients_from_even_mp(vector)
    # Both scans start at zero on the fixed Fourier-lattice grid.  The 100-dps
    # vector is first scanned in binary64 only to produce construction-derived
    # brackets, then every root is refined against the 100-dps transform.
    full_float = np.array([float(full[j]) for j in range(full.rows)])
    root_seeds = core.enumerate_positive_roots(full_float, math.log(x), ROOT_COUNT)
    roots = core.refine_positive_roots(full, mp.log(x), root_seeds, MATRIX_DPS)
    root_residuals = [abs(core.transform_mp(root, full, mp.log(x))) for root in roots]

    seed_full = core.full_coefficients_from_even(vector_seed)
    seed_roots = core.enumerate_positive_roots(seed_full, math.log(x), ROOT_COUNT)
    convergence = [abs(root - mp.mpf(format(seed, ".17g"))) for root, seed in zip(roots, seed_roots)]
    return {
        "positive_roots": [mp.nstr(root, 90) for root in roots],
        "root_count": len(roots),
        "strictly_ordered": all(a < b for a, b in zip(roots[:-1], roots[1:])),
        "ground_refinement": {
            "method": eigen_method,
            "binary64_seed_eigenvalue": format(minimum_seed, ".17g"),
            "rayleigh_value_100dps": mp.nstr(minimum, 90),
            "residual_100dps": mp.nstr(residual, 30),
            "binary64_gap_to_second_even": mp.nstr(gap_seed, 30),
            "residual_over_binary64_gap": mp.nstr(residual_over_gap, 30),
        },
        "convergence_mutation_binary64_seed_to_100dps_refinement": {
            "maximum_root_difference_1_to_60": mp.nstr(max(convergence), 30),
            "maximum_root_difference_20_to_50": mp.nstr(max(convergence[19:50]), 30),
        },
        "maximum_transform_residual_100dps": mp.nstr(max(root_residuals), 30),
        "low_spectrum_binary64_diagnostic": {
            "even_ground": format(float(even_values[0]), ".17g"),
            "second_even": format(float(even_values[1]), ".17g"),
            "odd_ground": format(float(odd_values[0]), ".17g"),
        },
        "matrix_sha256_80_digits": {
            "even": core.matrix_digest(even, 80),
            "odd": core.matrix_digest(odd, 80),
        },
    }


def serialize_prolate_run(run: dict[str, object]) -> dict[str, object]:
    roots = run["roots"]
    return {
        "positive_roots": [mp.nstr(root, 90) for root in roots],
        "root_count": len(roots),
        "strictly_ordered": all(a < b for a, b in zip(roots[:-1], roots[1:])),
        "maximum_transform_residual": mp.nstr(max(run["residuals"]), 20),
        "minimum_absolute_derivative_diagnostic": mp.nstr(min(run["derivatives"]), 20),
        "scan_step": mp.nstr(run["scan_step"], 40),
    }


def main() -> None:
    audit = source_audit()
    if not audit["passed"]:
        raise RuntimeError(f"zero-blind source audit failed: {audit['findings']}")
    started = time.perf_counter()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Freeze one x-specific pseudo support.  Reusing it across N isolates the
    # truncation path; no target information participates in either draw.
    pseudo_by_x: dict[int, tuple[list[core.ArithmeticTerm], int, dict[str, int]]] = {}
    for x in (14, 16):
        pseudo_by_x[x] = matched_pseudo_terms(SEED, x)
    old_x14, old_attempts = core.pseudo_prime_terms(SEED, 14.0)
    x14_exact_replay = pseudo_by_x[14][1] == old_attempts and pseudo_by_x[14][0] == old_x14
    if not x14_exact_replay:
        raise RuntimeError("x=14 failed to replay the frozen six-base/nine-term sampler")

    records: list[dict[str, object]] = []
    mp.mp.dps = MATRIX_DPS
    for x, n_max in PAIRS:
        length = mp.log(x)
        alpha, beta, gamma = core.archimedean_arrays(n_max, length, MATRIX_DPS)
        pseudo_terms, attempts, counts = pseudo_by_x[x]
        pseudo_even, pseudo_odd = core.parity_blocks_from_arrays(
            n_max, length, pseudo_terms, alpha, beta, gamma, MATRIX_DPS
        )
        arch_even, arch_odd = core.parity_blocks_from_arrays(
            n_max, length, [], alpha, beta, gamma, MATRIX_DPS
        )
        records.append({
            "x": x,
            "N": n_max,
            "pseudo_prime": {
                "seed": SEED,
                "rejection_attempts": attempts,
                "count_match": counts,
                "terms": [term.__dict__ for term in pseudo_terms],
                "spectrum": roots_from_even(pseudo_even, pseudo_odd, x),
            },
            "archimedean_only": {
                "terms": [],
                "spectrum": roots_from_even(arch_even, arch_odd, x),
            },
        })
        print(json.dumps({"built": "finite controls", "x": x, "N": n_max}), flush=True)

    # The already-surviving x=13 confounder is the inversion-even projection of
    # the prolate candidate.  Match that convention at every uncovered pair.
    with mp.workdps(PROLATE_DPS):
        for x in (14, 16):
            n_values = [n for xx, n in PAIRS if xx == x]
            maximum_n = max(n_values)
            print(json.dumps({"building": "prolate candidate", "x": x}), flush=True)
            candidate = prolate.high_precision_candidate(x, PROLATE_LMAX)
            coefficients = prolate.project_even_candidate(
                candidate,
                maximum_n,
                quadrature_order=PROLATE_QUADRATURE_ORDER,
                panels_per_cycle=PROLATE_PANELS_PER_CYCLE,
            )
            # The imported enumerator uses its module's cutoff constant.
            prolate.X = x
            for n_max in n_values:
                run = prolate.enumerate_roots(coefficients, n_max, ROOT_COUNT)
                record = next(row for row in records if row["x"] == x and row["N"] == n_max)
                record["prolate_only"] = {
                    "convention": "orthogonal inversion-even projection",
                    "arithmetic_note": "no finite Weil matrix, but integer dilation E contains the zeta Dirichlet series analytically",
                    "spectrum": serialize_prolate_run(run),
                }
                print(json.dumps({"built": "prolate-only control", "x": x, "N": n_max}), flush=True)

    completed = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema": "codex-r5-posthoc-matched-controls-blind-v1",
        "status": "MEASURED",
        "registration": "post-hoc audit; not part of PREDICTIONS-codex-r5.md",
        "generated_utc": completed,
        "parameters": {
            "pairs": [list(pair) for pair in PAIRS],
            "matrix_decimal_digits": MATRIX_DPS,
            "root_count": ROOT_COUNT,
            "pseudo_seed": SEED,
            "prolate_decimal_digits": PROLATE_DPS,
            "prolate_legendre_cutoff": PROLATE_LMAX,
            "prolate_quadrature_order_per_panel": PROLATE_QUADRATURE_ORDER,
            "prolate_panels_per_shortest_cycle": PROLATE_PANELS_PER_CYCLE,
        },
        "construction_order": [
            "freeze x-specific pseudo supports",
            "build pseudo-prime and archimedean-only spectra for every pair",
            "build inversion-even prolate-only spectra for every pair",
            "write this blind artifact",
            "only then may the separate scorer run",
        ],
        "pseudo_sampler": {
            "mechanism": "PCG64DXSM; uniform continuous bases on [2,x], accept with log(2)/log(base), reject the complete comb until authentic base and prime-power counts match",
            "x14_exact_replay_of_frozen_sampler": x14_exact_replay,
            "support_reused_across_N_at_fixed_x": True,
        },
        "source_audit": audit,
        "target_data_present": False,
        "scoring_present": False,
        "records": records,
        "source_sha256": {
            Path(__file__).name: sha256(Path(__file__)),
            "weil_core.py": sha256(HERE / "weil_core.py"),
            "run_prolate_only_control.py": sha256(HERE / "run_prolate_only_control.py"),
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "sha256": sha256(OUTPUT),
        "record_count": len(records),
        "target_data_present": False,
        "scoring_present": False,
        "seconds": payload["elapsed_seconds"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
