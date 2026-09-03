#!/usr/bin/env python3
"""Run registered post-gate mutations of the x=13 survivor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import mpmath as mp

import weil_core as core


HERE = Path(__file__).resolve().parent
N = 120
DPS = 100


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scaled(term: core.ArithmeticTerm, factor: mp.mpf) -> core.ArithmeticTerm:
    return core.ArithmeticTerm(
        term.location,
        mp.nstr(term.mp_weight() * factor, DPS),
        term.base,
        term.exponent,
        "literal",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mutation",
        choices=("prime13-plus5", "delete13-survivors-plus5", "cutoff13.25"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    mp.mp.dps = DPS

    x: str | int = 13
    original = core.prime_power_terms(13)
    if args.mutation == "prime13-plus5":
        terms = [scaled(t, mp.mpf("1.05")) if t.base == "13" else t for t in original]
        label = "x=13, base-prime 13 weight multiplied by 1.05"
    elif args.mutation == "delete13-survivors-plus5":
        terms = [scaled(t, mp.mpf("1.05")) for t in original if t.base != "13"]
        label = "x=13, delete base prime 13 and multiply every surviving weight by 1.05"
    else:
        x = "13.25"
        terms = original
        label = "cutoff x=13.25 with the x=13 prime-power set"

    started = time.perf_counter()
    even, odd, meta = core.parity_blocks(N, x, terms, DPS)
    even_values, even_vectors = mp.eigsy(even)
    odd_values = mp.eigsy(odd, eigvals_only=True)
    vector = core.normalize_vector(even_vectors[:, 0])
    full = core.full_coefficients_from_even_mp(vector)
    roots = core.enumerate_positive_roots_mp(full, mp.log(mp.mpf(str(x))), 60, 32)
    payload = {
        "kind": "zero-blind survivor mutation",
        "label": label,
        "mutation": args.mutation,
        "parameters": {"x": str(x), "N": N, "dps": DPS},
        "meta": meta,
        "terms": [term.__dict__ for term in terms],
        "low_spectrum": {
            "even": [mp.nstr(even_values[j], 90) for j in range(4)],
            "odd": [mp.nstr(odd_values[j], 90) for j in range(4)],
        },
        "even_matrix_sha256": core.matrix_digest(even, 80),
        "positive_roots": [mp.nstr(root, 100) for root in roots],
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
