#!/usr/bin/env python3
"""Reconcile the final x=13 driver rerun with the frozen independent audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import mpmath as mp


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    audit_path = HERE / "outputs" / "weil-replay-audit.json"
    audit = json.loads(audit_path.read_text())
    rows = []
    mp.mp.dps = 450
    for stage in audit["root_precision_replay"]["stages"]:
        digits = int(stage["requested_digits"])
        driver_path = HERE / f"true-x13-N120-dps{digits}.json"
        driver = json.loads(driver_path.read_text())
        differences = [
            abs(mp.mpf(a) - mp.mpf(b))
            for a, b in zip(stage["positive_roots"], driver["positive_roots"])
        ]
        frozen = differences[19:50]
        rows.append(
            {
                "digits": digits,
                "audit_file_sha256": sha256(audit_path),
                "driver_file": driver_path.name,
                "driver_file_sha256": sha256(driver_path),
                "driver_builder_sha256": driver["builder_sha256"],
                "maximum_absolute_difference_first_60": mp.nstr(max(differences), 25),
                "maximum_absolute_difference_20_through_50": mp.nstr(max(frozen), 25),
                "worst_index_20_through_50": 20 + frozen.index(max(frozen)),
            }
        )
    output = HERE / "outputs" / "weil-replay-final-driver-reconciliation.json"
    output.write_text(json.dumps({"status": "MEASURED", "comparisons": rows}, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
