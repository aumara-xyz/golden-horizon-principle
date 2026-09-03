#!/usr/bin/env python3
"""Run the ten preregistered pseudo-prime controls before scoring exists."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import mpmath as mp
import numpy as np

import weil_core as core


HERE = Path(__file__).resolve().parent
BLIND_OUTPUT = HERE / "blind-pseudo-spectra.json"
GATE_OUTPUT = HERE / "pseudo-gate.json"
SEEDS = list(range(52025001, 52025011))
X = 13
N = 120
DPS = 100


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def static_audit() -> dict[str, object]:
    """Reject direct evaluator/table imports and the familiar first target digits."""

    inspected = [Path(__file__), HERE / "weil_core.py"]
    banned = [
        "zeta" + "zero",
        "zeros" + ".txt",
        "14.134" + "725",
        "mpmath." + "zeta" + "zero",
    ]
    findings: list[dict[str, str]] = []
    for path in inspected:
        text = path.read_text()
        for token in banned:
            if token.lower() in text.lower():
                findings.append({"file": path.name, "token": token})
    return {
        "inspected": [path.name for path in inspected],
        "banned_token_count": len(banned),
        "findings": findings,
        "passed": not findings,
    }


def main() -> None:
    audit = static_audit()
    if not audit["passed"]:
        raise RuntimeError(f"zero-blind static audit failed: {audit['findings']}")

    mp.mp.dps = DPS
    length = mp.log(X)
    alpha, beta, gamma = core.archimedean_arrays(N, length, DPS)
    runs: list[dict[str, object]] = []
    for seed in SEEDS:
        terms, attempts = core.pseudo_prime_terms(seed, float(X))
        even, odd = core.parity_blocks_from_arrays(
            N, length, terms, alpha, beta, gamma, DPS
        )
        even_minimum, even_vector, even_values = core.float_ground(even)
        odd_values = np.linalg.eigvalsh(np.array(odd.tolist(), dtype=float))
        full = core.full_coefficients_from_even(even_vector)
        roots = core.enumerate_positive_roots(full, float(length), 60)
        roots_payload = "\n".join(format(root, ".17g") for root in roots).encode()
        runs.append(
            {
                "seed": seed,
                "rejection_attempts": attempts,
                "terms": [term.__dict__ for term in terms],
                "matrix_dps": DPS,
                "spectral_seed_solver": "numpy.linalg.eigh binary64",
                "even_matrix_sha256_80_digits": core.matrix_digest(even, 80),
                "odd_matrix_sha256_80_digits": core.matrix_digest(odd, 80),
                "even_minimum_binary64": format(even_minimum, ".17g"),
                "second_even_binary64": format(float(even_values[1]), ".17g"),
                "odd_minimum_binary64": format(float(odd_values[0]), ".17g"),
                "roots": [format(root, ".17g") for root in roots],
                "roots_sha256": hashlib.sha256(roots_payload).hexdigest(),
            }
        )

    blind_payload = {
        "kind": "density-and-count-matched pseudo-prime spectra",
        "parameters": {"x": X, "N": N, "matrix_dps": DPS, "seeds": SEEDS},
        "scoring_present": False,
        "target_data_present": False,
        "static_audit": audit,
        "runs": runs,
    }
    core.write_json(BLIND_OUTPUT, blind_payload)
    gate_payload = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "blind_output": BLIND_OUTPUT.name,
        "blind_output_sha256": sha256(BLIND_OUTPUT),
        "run_count": len(runs),
        "seeds": SEEDS,
        "all_root_counts": [len(run["roots"]) for run in runs],
        "static_audit": audit,
        "scoring_present": False,
        "target_data_present": False,
        "gate_complete": len(runs) == 10 and audit["passed"],
        "builder_sha256": sha256(HERE / "weil_core.py"),
        "runner_sha256": sha256(Path(__file__)),
    }
    core.write_json(GATE_OUTPUT, gate_payload)
    print(json.dumps({"gate": str(GATE_OUTPUT), "complete": gate_payload["gate_complete"]}))


if __name__ == "__main__":
    main()
