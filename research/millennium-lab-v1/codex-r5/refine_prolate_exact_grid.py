#!/usr/bin/env python3
"""Replace unresolved x=18,20 rows with higher-mode-cutoff exact projections."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

from run_prolate_exact_grid import _power_fit, run_x_family


HERE = Path(__file__).resolve().parent


def main() -> None:
    path = HERE / "prolate-bridge-data" / "exact-projection-grid.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    with ProcessPoolExecutor(max_workers=2) as executor:
        families = list(executor.map(run_x_family, (18, 20)))
    replacements = [row for family in families for row in family["rows"]]
    rows = [row for row in payload["rows"] if row["x"] not in (18, 20)]
    rows.extend(replacements)
    rows.sort(key=lambda row: (row["N"] != 120, row["N"], row["x"]))
    payload["rows"] = rows
    payload["status"] = (
        "MEASURED"
        if all(row["metrics"]["ratio_status"] == "MEASURED" for row in rows)
        else "UNVERIFIED"
    )
    payload["power_fit_last_five"] = {
        str(n_max): _power_fit(rows, n_max) for n_max in (96, 120, 144)
    }
    grid_source = HERE / "run_prolate_exact_grid.py"
    payload["source_sha256"] = hashlib.sha256(grid_source.read_bytes()).hexdigest()
    payload["high_cutoff_refinement"] = {
        "x": [18, 20],
        "primary_legendre_cutoff": 240,
        "mutation_legendre_cutoff": 200,
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "rows": len(rows),
        "power_fit_last_five": payload["power_fit_last_five"],
        "output": str(path),
    }, indent=2))


if __name__ == "__main__":
    main()
