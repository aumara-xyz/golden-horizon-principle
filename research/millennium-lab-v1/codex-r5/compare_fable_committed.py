#!/usr/bin/env python3
"""Compare committed, independently built Codex and Fable low spectra."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import mpmath as mp


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FABLE_REF = "lab/millennium-v1"
FABLE_COMMIT = "bc6f3bd"


def git_blob(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{FABLE_REF}:{path}"], cwd=REPO)


def main() -> None:
    mp.mp.dps = 450
    scored = json.loads((HERE / "accuracy-after-pseudo-gate.json").read_text())
    matrix_diff_path = HERE / "independent-matrix-diff.json"
    matrix_diff = json.loads(matrix_diff_path.read_text()) if matrix_diff_path.exists() else None
    source_path = "research/millennium-lab-v1/ccm_triples.py"
    source = git_blob(source_path)
    rows = []
    for x in (9, 13):
        fable_path = f"research/millennium-lab-v1/r5-lam{x}.json"
        fable = json.loads(git_blob(fable_path))
        codex_path = HERE / f"true-x{x}-N120-dps200.json"
        codex = json.loads(codex_path.read_text())
        root_differences = [
            abs(mp.mpf(a) - mp.mpf(b))
            for a, b in zip(fable["roots_first5"], codex["positive_roots"][:5])
        ]
        codex_score = next(
            row
            for row in scored["true_prime_scores"]
            if row["label"] == f"true primes x={x}, N=120, dps=200"
        )
        fable_rounded_errors = [mp.mpf(value) for value in fable["abs_err"][19:50]]
        error_rounding_differences = [
            abs(a - mp.mpf(b))
            for a, b in zip(fable_rounded_errors, codex_score["absolute_errors"])
        ]
        even = [mp.mpf(v) for v in codex["eigensolve"]["first_even_values"]]
        odd = [mp.mpf(v) for v in codex["eigensolve"]["first_odd_values"]]
        rows.append(
            {
                "x": x,
                "N": 120,
                "common_precision_note": "Fable serialized roots_first5 to 30 significant digits and eps1/eps2 to 15",
                "root_absolute_differences_first5": [mp.nstr(v, 25) for v in root_differences],
                "maximum_root_absolute_difference_first5": mp.nstr(max(root_differences), 25),
                "maximum_difference_between_fable_3sig_and_codex_absolute_errors_20_to_50": mp.nstr(
                    max(error_rounding_differences), 12
                ),
                "compared_absolute_error_count_from_index_20": len(error_rounding_differences),
                "codex_even_minimum": mp.nstr(even[0], 40),
                "fable_eps1": fable["eps1"],
                "codex_nearest_competitor": mp.nstr(min(even[1] if len(even) > 1 else mp.inf, odd[0]), 40),
                "fable_eps2": fable["eps2"],
                "fable_raw_matrix_available": False,
                "fable_full_root_vector_available": False,
            }
        )
    output = {
        "status": "MEASURED",
        "fable_reconstruction_commit": FABLE_COMMIT,
        "fable_branch_head_at_comparison": subprocess.check_output(
            ["git", "rev-parse", FABLE_REF], cwd=REPO, text=True
        ).strip(),
        "fable_builder_sha256": hashlib.sha256(source).hexdigest(),
        "scope": "diff limited to fields serialized by the independently committed Fable output",
        "matrix_entrywise_diff_status": "MEASURED" if matrix_diff is not None else "UNVERIFIED",
        "matrix_entrywise_diff_reason": (
            "the exact committed Fable source was replayed through construction of T; see independent-matrix-diff.json"
            if matrix_diff is not None
            else "the Fable commit did not serialize its matrix"
        ),
        "matrix_diff_file": matrix_diff_path.name if matrix_diff is not None else None,
        "protocol_audit": {
            "prediction_commit": "213b1f6",
            "primary_accuracy_commit": "bc6f3bd",
            "hostile_control_commit": "3a9452f",
            "pseudo_control_preceded_first_accuracy": False,
            "consequence_under_round5_rule": "Fable accuracy evidence is VOID for the shared gate-order rule; this does not alter the numerical implementation diff",
            "x9_serialized_root_count": 49,
            "x9_results_table_last_column_label": "k=50",
            "x9_last_serialized_error_is_index": 49,
        },
        "rows": rows,
    }
    path = HERE / "independent-reconstruction-diff.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(path)


if __name__ == "__main__":
    main()
