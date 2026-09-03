#!/usr/bin/env python3
"""Build one true-prime finite Weil spectrum without target information."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import mpmath as mp

import weil_core as core


HERE = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--x", type=int, required=True)
    parser.add_argument("--n", type=int, default=120)
    parser.add_argument("--dps", type=int, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    mp.mp.dps = args.dps
    terms = core.prime_power_terms(args.x)
    even, odd, meta = core.parity_blocks(args.n, args.x, terms, args.dps)
    built_seconds = time.perf_counter() - started

    eigen_started = time.perf_counter()
    if args.previous is None:
        even_values, even_vectors = mp.eigsy(even)
        vector = core.normalize_vector(even_vectors[:, 0])
        minimum = even_values[0]
        eigen_method = "mpmath.eigsy full even block"
        first_even_values = [even_values[j] for j in range(min(4, even_values.rows))]
        residual = mp.sqrt(
            mp.fsum(
                abs(value) ** 2 for value in (even * vector - minimum * vector)
            )
        )
        odd_values = mp.eigsy(odd, eigvals_only=True)
        first_odd_values = [
            mp.nstr(odd_values[j], args.dps) for j in range(min(4, odd_values.rows))
        ]
    else:
        previous = json.loads(args.previous.read_text())
        if int(previous["parameters"]["x"]) != args.x or int(
            previous["parameters"]["N"]
        ) != args.n:
            raise RuntimeError("previous vector has incompatible x or N")
        initial = mp.matrix([mp.mpf(value) for value in previous["even_unit_vector"]])
        minimum, vector, residual = core.refine_ground(even, initial, 6)
        eigen_method = f"Rayleigh refinement from {args.previous.name}"
        first_even_values = [minimum]
        first_odd_values = previous["eigensolve"]["first_odd_values"]
    eigen_seconds = time.perf_counter() - eigen_started

    full = core.full_coefficients_from_even_mp(vector)
    root_started = time.perf_counter()
    roots = core.enumerate_positive_roots_mp(full, mp.log(args.x), 60, 32)
    root_seconds = time.perf_counter() - root_started

    direct_checks: list[dict[str, str | list[int]]] = []
    length = mp.log(args.x)
    alpha, beta, gamma = core.archimedean_arrays(args.n, length, args.dps)
    for n, m in [(0, 0), (0, 1), (1, 2), (3, 7), (-2, 5)]:
        formula = core.archimedean_entry_from_arrays(n, m, alpha, beta, gamma)
        direct = core.direct_archimedean_entry(n, m, length, args.dps)
        direct_checks.append(
            {
                "indices": [n, m],
                "formula": mp.nstr(formula, args.dps),
                "direct": mp.nstr(direct, args.dps),
                "absolute_difference": mp.nstr(abs(formula - direct), args.dps),
            }
        )

    delta_overlap = mp.fsum(full[j] for j in range(full.rows)) / mp.sqrt(length)
    payload = {
        "kind": "zero-blind true-prime finite Weil reconstruction",
        "parameters": {"x": args.x, "N": args.n, "dps": args.dps},
        "meta": meta,
        "terms": [term.__dict__ for term in terms],
        "matrix": {
            "even_sha256": core.matrix_digest(
                even, min(args.dps - 15, max(40, args.dps // 2))
            ),
            "odd_sha256": core.matrix_digest(
                odd, min(args.dps - 15, max(40, args.dps // 2))
            ),
            "symmetry_by_construction": True,
            "parity_reduction": "orthonormal even/odd blocks",
        },
        "eigensolve": {
            "method": eigen_method,
            "minimum": mp.nstr(minimum, args.dps),
            "first_even_values": [mp.nstr(value, args.dps) for value in first_even_values],
            "first_odd_values": first_odd_values,
            "residual_norm": mp.nstr(residual, args.dps),
            "delta_overlap_before_normalization": mp.nstr(delta_overlap, args.dps),
        },
        "even_unit_vector": [mp.nstr(vector[j], args.dps) for j in range(vector.rows)],
        "positive_roots": [mp.nstr(root, args.dps) for root in roots],
        "root_transform_residuals": [
            mp.nstr(abs(core.transform_mp(root, full, length)), args.dps) for root in roots
        ],
        "direct_archimedean_checks": direct_checks,
        "timings_seconds": {
            "build": built_seconds,
            "eigensolve_including_odd": eigen_seconds,
            "root_enumeration": root_seconds,
            "total_before_direct_checks": built_seconds + eigen_seconds + root_seconds,
        },
        "builder_sha256": sha256(HERE / "weil_core.py"),
        "runner_sha256": sha256(Path(__file__)),
        "target_data_present": False,
        "scoring_present": False,
    }
    core.write_json(args.output, payload)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "x": args.x,
                "N": args.n,
                "dps": args.dps,
                "root_count": len(roots),
                "seconds": time.perf_counter() - started,
            }
        )
    )


if __name__ == "__main__":
    main()
