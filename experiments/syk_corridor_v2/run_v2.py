#!/usr/bin/env python3
"""
run_v2.py — SYK-CORRIDOR-v2 official-run wrapper (laptop execution).

Governing contract (SIGNED, byte-frozen):
  experiments/SYK_CORRIDOR_PREREG_v2.md
Pinned runtime (byte-unchanged; this wrapper REFUSES to run on any hash
mismatch and never edits the pipeline):
  experiments/syk_corridor/pipeline.py
    contract pin  f5ad157c871a061a7244ed3767b9abe0affa034f1bdaac668343650a71c34511
  experiments/op179_nu_to_beta.py
    contract pin  b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e

WHAT THIS WRAPPER DOES (and all it does):
  1. sha256-verifies pipeline.py and op179_nu_to_beta.py against the contract
     pins, before AND after the run (tamper check across the run window).
  2. Records the as-signed sha256 of SYK_CORRIDOR_PREREG_v2.md (measured, not
     asserted — the contract's hash direction is one-way, contract -> pipeline).
  3. Executes `python3 pipeline.py` as a subprocess, byte-unchanged, with NO
     --venue-nebius flag: this is a laptop execution, and per PREREG v2
     (runtime note carried from v1 section 5) a laptop execution is
     PIPELINE-VALIDATION language territory; the certified corridor run is the
     Nebius execution only. Asserting the Nebius venue here would be false.
  4. Copies the pipeline's pinned output (experiments/syk_corridor/
     results_v2.json, the path the contract itself names) into
     experiments/syk_corridor_v2/results.json wrapped with this provenance
     block. The pinned output file is left in place, untouched.

This wrapper contains NO physics, NO band arithmetic, and NO golden-ratio
numeric literals; every bucket in results.json is the mechanical output of the
byte-frozen op179 functions as invoked by the byte-pinned pipeline.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent            # experiments/syk_corridor_v2
EXPERIMENTS = HERE.parent                          # experiments/
PIPELINE = EXPERIMENTS / "syk_corridor" / "pipeline.py"
OP179 = EXPERIMENTS / "op179_nu_to_beta.py"
CONTRACT = EXPERIMENTS / "SYK_CORRIDOR_PREREG_v2.md"
PINNED_OUTPUT = EXPERIMENTS / "syk_corridor" / "results_v2.json"
WRAPPED_OUTPUT = HERE / "results.json"

PIPELINE_PIN = "f5ad157c871a061a7244ed3767b9abe0affa034f1bdaac668343650a71c34511"
OP179_PIN = "b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins(stage: str) -> dict:
    got_pipeline = sha256_of(PIPELINE)
    got_op179 = sha256_of(OP179)
    if got_pipeline != PIPELINE_PIN:
        raise SystemExit(
            f"REFUSING TO RUN ({stage}): pipeline.py sha256 {got_pipeline} "
            f"does not match the contract pin {PIPELINE_PIN}"
        )
    if got_op179 != OP179_PIN:
        raise SystemExit(
            f"REFUSING TO RUN ({stage}): op179_nu_to_beta.py sha256 {got_op179} "
            f"does not match the contract pin {OP179_PIN}"
        )
    print(f"[{stage}] pipeline.py  sha256 = {got_pipeline}  (MATCHES contract pin)")
    print(f"[{stage}] op179        sha256 = {got_op179}  (MATCHES contract pin)")
    return {"pipeline_sha256": got_pipeline, "op179_sha256": got_op179}


def main() -> None:
    t0 = time.time()
    contract_sha = sha256_of(CONTRACT)
    print(f"contract SYK_CORRIDOR_PREREG_v2.md sha256 = {contract_sha} (measured)")
    pre = verify_pins("pre-run")

    print("\nExecuting byte-pinned pipeline (laptop venue; no --venue-nebius; "
          "PIPELINE-VALIDATION labeling per the contract)...\n", flush=True)
    proc = subprocess.run(
        [sys.executable, str(PIPELINE)],
        cwd=str(PIPELINE.parent),
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"pipeline exited nonzero ({proc.returncode}); no wrap produced")

    post = verify_pins("post-run")
    if not PINNED_OUTPUT.exists():
        raise SystemExit(f"pipeline did not write {PINNED_OUTPUT}")

    with open(PINNED_OUTPUT) as f:
        pipeline_out = json.load(f)

    wrapped = {
        "wrapper_provenance": {
            "wrapper": "experiments/syk_corridor_v2/run_v2.py",
            "run_kind": "OFFICIAL LAPTOP RUN under the SIGNED v2 contract — "
                        "PIPELINE-VALIDATION labeling; NOT the certified Nebius "
                        "run (contract section 6(d) remains undischarged)",
            "contract": "experiments/SYK_CORRIDOR_PREREG_v2.md",
            "contract_sha256_measured": contract_sha,
            "pipeline_sha256_pre_run": pre["pipeline_sha256"],
            "pipeline_sha256_post_run": post["pipeline_sha256"],
            "op179_sha256": post["op179_sha256"],
            "pipeline_byte_unchanged": True,
            "venue_nebius_asserted": False,
            "cloud_spend_usd": 0.0,
            "budget_cap_usd": 400.0,
            "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "wall_seconds": None,  # filled below
        },
        "pipeline_output": pipeline_out,
    }
    wrapped["wrapper_provenance"]["wall_seconds"] = round(time.time() - t0, 1)
    with open(WRAPPED_OUTPUT, "w") as f:
        json.dump(wrapped, f, indent=1)
    print(f"\nWROTE {WRAPPED_OUTPUT}")
    print(f"wall time: {wrapped['wrapper_provenance']['wall_seconds']:.1f}s")


if __name__ == "__main__":
    main()
