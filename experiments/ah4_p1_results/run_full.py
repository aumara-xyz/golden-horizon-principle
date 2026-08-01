#!/usr/bin/env python3
"""AH.4-P1 full preregistered run wrapper.

Executes the identical parametrised pipeline (experiments/ah4_p1_pipeline.py)
over the full sweep: 4 categories x 4 constants x (3 fractions x 2 modes)
x 20 seeds (1000-1019).  Adds ONLY:
  - per-cell wall-clock timing,
  - a 120-second per-cell abort guard (budget honesty): a cell whose
    cumulative wall time exceeds 120 s is aborted between seeds, recorded
    as {"aborted": true, ...} with the partial seed values discarded from
    analysis (never extrapolated),
  - a per-cell median summary table.
No physics, channel, recovery, scoring, or selection code lives here.
"""
import importlib.util
import json
import os
import statistics
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.join(HERE, "..", "ah4_p1_pipeline.py")
spec = importlib.util.spec_from_file_location("ah4_p1_pipeline", PIPE)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

CELL_BUDGET_S = 120.0

arms = P.build_arms()
results = {
    "test_id": "AH4-P1-ANYON-RECOV-v1",
    "n_carriers": P.N_CARRIERS, "d_logical": P.D_LOGICAL,
    "fractions": list(P.ERASURE_FRACTIONS), "modes": list(P.MODES),
    "seeds": list(P.SEEDS),
    "constants": {k: repr(v) for k, v in P.CONSTANTS.items()},
    "dims": {name: int(arm["basis"].shape[0]) for name, arm in arms.items()},
    "cell_budget_seconds": CELL_BUDGET_S,
    "cells": {},
    "cell_seconds": {},
    "aborted_cells": [],
}

t_total = time.monotonic()
for arm_name, arm in arms.items():
    for const_name, c in P.CONSTANTS.items():
        a0, a1 = P.select_code_space(arm["basis"], c)
        for f_index, f in enumerate(P.ERASURE_FRACTIONS):
            for mode in P.MODES:
                key = "%s|%s|f%.2f|%s" % (arm_name, const_name, f, mode)
                t0 = time.monotonic()
                vals = []
                aborted = False
                for seed in P.SEEDS:
                    if time.monotonic() - t0 > CELL_BUDGET_S:
                        aborted = True
                        break
                    vals.append(P.run_cell(arm, a0, a1, f_index, mode, seed))
                dt = time.monotonic() - t0
                results["cell_seconds"][key] = round(dt, 4)
                if aborted:
                    results["aborted_cells"].append(key)
                    results["cells"][key] = {
                        "aborted": True,
                        "seeds_completed": len(vals),
                        "elapsed_seconds": round(dt, 4),
                    }
                else:
                    results["cells"][key] = vals

out = os.path.join(HERE, "results.json")
with open(out, "w") as fh:
    json.dump(results, fh, indent=1, sort_keys=True)

# per-cell median summary table
lines = ["# AH.4-P1 per-cell median summary",
         "",
         "Total wall time: %.1f s.  Cell budget: %.0f s.  Aborted cells: %s"
         % (time.monotonic() - t_total, CELL_BUDGET_S,
            results["aborted_cells"] or "none"),
         "",
         "| arm | constant | f | mode | median F_e | min | max | cell s |",
         "|---|---|---|---|---|---|---|---|"]
for arm_name in arms:
    for const_name in P.CONSTANTS:
        for f in P.ERASURE_FRACTIONS:
            for mode in P.MODES:
                key = "%s|%s|f%.2f|%s" % (arm_name, const_name, f, mode)
                cell = results["cells"][key]
                if isinstance(cell, dict):
                    lines.append("| %s | %s | %.2f | %s | ABORTED (%d/20 seeds, %.1f s) | | | %.1f |"
                                 % (arm_name, const_name, f, mode,
                                    cell["seeds_completed"],
                                    cell["elapsed_seconds"],
                                    cell["elapsed_seconds"]))
                else:
                    lines.append("| %s | %s | %.2f | %s | %.6f | %.6f | %.6f | %.2f |"
                                 % (arm_name, const_name, f, mode,
                                    statistics.median(cell), min(cell),
                                    max(cell), results["cell_seconds"][key]))
with open(os.path.join(HERE, "summary_table.md"), "w") as fh:
    fh.write("\n".join(lines) + "\n")

print("wrote %s (%d cells; aborted: %d)" %
      (out, len(results["cells"]), len(results["aborted_cells"])))
