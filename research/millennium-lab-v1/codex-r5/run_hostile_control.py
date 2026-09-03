#!/usr/bin/env python3
"""Build one zero-blind hostile finite-Weil control spectrum."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import mpmath as mp

import weil_core as core


HERE = Path(__file__).resolve().parent
X = 13
N = 120
DPS = 100


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--archimedean-only", action="store_true")
    group.add_argument("--permuted", action="store_true")
    group.add_argument("--delete-prime", type=int)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def source_audit() -> dict[str, object]:
    inspected = [Path(__file__), HERE / "weil_core.py"]
    banned = ["zeta" + "zero", "zeros" + ".txt", "14.134" + "725"]
    findings = []
    for path in inspected:
        source = path.read_text()
        for token in banned:
            if token.lower() in source.lower():
                findings.append({"file": path.name, "token": token})
    return {"inspected": [p.name for p in inspected], "findings": findings, "passed": not findings}


def main() -> None:
    args = parse_args()
    audit = source_audit()
    if not audit["passed"]:
        raise RuntimeError(f"zero-blind source audit failed: {audit['findings']}")
    if args.archimedean_only:
        label = "archimedean-only"
        terms: list[core.ArithmeticTerm] = []
    elif args.permuted:
        label = "true support, weight permutation seed 52025999"
        terms = core.permuted_weight_terms(X, 52025999)
    else:
        if args.delete_prime not in (2, 3, 5, 7, 11, 13):
            raise ValueError("registered deletion base must be 2, 3, 5, 7, 11, or 13")
        label = f"delete base prime {args.delete_prime} and all of its powers"
        terms = core.prime_power_terms(X, omitted_base=args.delete_prime)

    started = time.perf_counter()
    mp.mp.dps = DPS
    even, odd, meta = core.parity_blocks(N, X, terms, DPS)
    even_values, even_vectors = mp.eigsy(even)
    odd_values = mp.eigsy(odd, eigvals_only=True)
    vector = core.normalize_vector(even_vectors[:, 0])
    residual = mp.norm(even * vector - even_values[0] * vector)
    full = core.full_coefficients_from_even_mp(vector)
    roots = core.enumerate_positive_roots_mp(full, mp.log(X), 60, 32)

    payload = {
        "kind": "zero-blind hostile finite-Weil control",
        "label": label,
        "parameters": {"x": X, "N": N, "dps": DPS},
        "meta": meta,
        "terms": [term.__dict__ for term in terms],
        "source_audit": audit,
        "matrix": {
            "even_sha256": core.matrix_digest(even, 80),
            "odd_sha256": core.matrix_digest(odd, 80),
        },
        "low_spectrum": {
            "even": [mp.nstr(even_values[j], 90) for j in range(4)],
            "odd": [mp.nstr(odd_values[j], 90) for j in range(4)],
            "even_ground_residual": mp.nstr(residual, 90),
        },
        "even_unit_vector": [mp.nstr(vector[j], 100) for j in range(vector.rows)],
        "positive_roots": [mp.nstr(root, 100) for root in roots],
        "root_transform_residuals": [
            mp.nstr(abs(core.transform_mp(root, full, mp.log(X))), 90) for root in roots
        ],
        "builder_sha256": sha256(HERE / "weil_core.py"),
        "runner_sha256": sha256(Path(__file__)),
        "elapsed_seconds": time.perf_counter() - started,
        "target_data_present": False,
        "scoring_present": False,
    }
    core.write_json(args.output, payload)
    print(json.dumps({"output": str(args.output), "label": label, "root_count": len(roots), "seconds": payload["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
