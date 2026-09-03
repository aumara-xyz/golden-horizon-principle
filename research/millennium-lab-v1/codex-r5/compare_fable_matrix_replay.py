#!/usr/bin/env python3
"""Replay the committed Fable matrix builder and diff every matrix entry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import mpmath as mp

import weil_core as core


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FABLE_REF = "lab/millennium-v1"
FABLE_PATH = "research/millennium-lab-v1/ccm_triples.py"
DPS = 100
N = 120


def committed_source() -> bytes:
    return subprocess.check_output(["git", "show", f"{FABLE_REF}:{FABLE_PATH}"], cwd=REPO)


def replay_fable_matrix(source: str, x: int) -> list[list[mp.mpf]]:
    # Stop the exact committed program immediately after it constructs T.
    # The stripped import and ctx assignment belong only to its later Flint
    # eigensolve and cannot affect the mpmath matrix construction.
    prefix = source.split("tb=time.time()-t0", 1)[0]
    prefix = prefix.replace("from flint import arb_mat, arb, ctx\n", "")
    prefix = prefix.replace("mp.mp.dps=a.dps; ctx.dps=a.dps;", "mp.mp.dps=a.dps;")
    old_argv = sys.argv
    try:
        sys.argv = [
            FABLE_PATH,
            "--lam2", str(x),
            "--N", str(N),
            "--dps", str(DPS),
            "--out", "/tmp/codex-r5-fable-unused.json",
        ]
        namespace: dict[str, object] = {"__name__": "fable_matrix_prefix"}
        exec(compile(prefix, f"{FABLE_REF}:{FABLE_PATH}", "exec"), namespace)
    finally:
        sys.argv = old_argv
    return namespace["T"]


def main() -> None:
    raw_source = committed_source()
    source = raw_source.decode()
    rows = []
    mp.mp.dps = DPS
    for x in (9, 12, 13, 14):
        started = time.perf_counter()
        fable = replay_fable_matrix(source, x)
        length = mp.log(x)
        alpha, beta, gamma = core.archimedean_arrays(N, length, DPS)
        terms = core.prime_power_terms(x)
        maximum = mp.mpf(0)
        worst = None
        sum_squares = mp.mpf(0)
        count = 0
        indices = list(range(-N, N + 1))
        samples = []
        sample_set = {(-120, -120), (-120, 120), (-7, 3), (0, 0), (0, 1), (31, 77), (120, 120)}
        for i, n in enumerate(indices):
            for j in range(i, len(indices)):
                m = indices[j]
                codex = core.weil_entry(n, m, length, terms, alpha, beta, gamma)
                difference = abs(codex - fable[i][j])
                sum_squares += difference * difference
                count += 1
                if difference > maximum:
                    maximum = difference
                    worst = [n, m]
                if (n, m) in sample_set:
                    samples.append(
                        {
                            "indices": [n, m],
                            "codex": mp.nstr(codex, 90),
                            "fable": mp.nstr(fable[i][j], 90),
                            "absolute_difference": mp.nstr(difference, 25),
                        }
                    )
        rows.append(
            {
                "x": x,
                "N": N,
                "dps": DPS,
                "upper_triangle_entry_count": count,
                "maximum_absolute_entry_difference": mp.nstr(maximum, 30),
                "rms_entry_difference": mp.nstr(mp.sqrt(sum_squares / count), 30),
                "worst_indices": worst,
                "samples": samples,
                "elapsed_seconds": time.perf_counter() - started,
            }
        )
    payload = {
        "status": "MEASURED",
        "fable_ref": FABLE_REF,
        "fable_head": subprocess.check_output(["git", "rev-parse", FABLE_REF], cwd=REPO, text=True).strip(),
        "fable_builder_sha256": hashlib.sha256(raw_source).hexdigest(),
        "replay_scope": "exact committed source through construction of T; unused Flint import/ctx assignment stripped",
        "rows": rows,
    }
    output = HERE / "independent-matrix-diff.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
