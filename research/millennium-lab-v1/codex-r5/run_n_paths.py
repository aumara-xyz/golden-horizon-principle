#!/usr/bin/env python3
"""Run the preregistered three finite N(x) paths without target data.

The numerical kernel is the audited arbitrary-precision runner used for the
primary reconstruction.  This driver only fixes the registered grid, resumes
completed cases, and records which two exact-grid artifacts are reused.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
X_GRID = (8, 10, 12, 14, 16)
MULTIPLIERS = (8, 10, 12)
DPS = 100

REUSED = {
    (12, 120): "true-x12-N120-dps100.json",
    (14, 112): "mutation-x14-N112-dps100.json",
}


def artifact_name(x: int, n_max: int) -> str:
    return REUSED.get((x, n_max), f"npath-x{x}-N{n_max}-dps{DPS}.json")


def validate(path: Path, x: int, n_max: int) -> None:
    payload = json.loads(path.read_text())
    parameters = payload["parameters"]
    if (int(parameters["x"]), int(parameters["N"]), int(parameters["dps"])) != (
        x,
        n_max,
        DPS,
    ):
        raise RuntimeError(f"parameter mismatch in {path.name}")
    if payload.get("target_data_present") is not False:
        raise RuntimeError(f"target-data audit failed for {path.name}")
    if payload.get("scoring_present") is not False:
        raise RuntimeError(f"scoring audit failed for {path.name}")
    if len(payload["positive_roots"]) < 60:
        raise RuntimeError(f"root enumeration incomplete for {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    manifest = []
    for x in X_GRID:
        for multiplier in MULTIPLIERS:
            n_max = multiplier * x
            name = artifact_name(x, n_max)
            path = HERE / name
            reused = (x, n_max) in REUSED
            if args.force and reused:
                raise RuntimeError("--force cannot overwrite a separately registered artifact")
            if args.force or not path.exists():
                subprocess.run(
                    [
                        sys.executable,
                        str(HERE / "run_true_reconstruction.py"),
                        "--x",
                        str(x),
                        "--n",
                        str(n_max),
                        "--dps",
                        str(DPS),
                        "--output",
                        str(path),
                    ],
                    check=True,
                )
            validate(path, x, n_max)
            manifest.append(
                {
                    "x": x,
                    "path_multiplier": multiplier,
                    "N": n_max,
                    "artifact": name,
                    "reused_exact_grid_artifact": reused,
                }
            )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
