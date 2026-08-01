#!/usr/bin/env python3
"""AH.4-P1 mechanical analysis — prereg section 2.2, applied exactly.

Primary rule (verbatim mechanics):
  For each f in {0.25, 0.50, 0.75}, at the primary constant `uniform`
  (scattered mode; burst is a separately-reported stressor):
      Delta(f) = median_seeds F_fib(f) - median_seeds F_ising(f)
  with a 95% bootstrap CI (10,000 resamples over the 20 seeds).
  Seeds are shared across arms (identical erasure draws), so the bootstrap
  resamples seed INDICES, paired across arms; each resample's statistic is
  median(fib[idx]) - median(ising[idx]); CI = percentile [2.5, 97.5].
  Bootstrap RNG seed fixed at 20260801 for reproducibility.

  STRUCTURAL ADVANTAGE iff Delta(f) > +0.02 AND CI excludes 0, at ALL THREE
  fractions; PRIMARY KILL (flat) iff |Delta(f)| <= 0.02 at all three;
  else INTERACTION/MIXED.

Also: Axis-B flatness (max pairwise |Delta| across constants within each
arm vs 0.02, scattered, per fraction), secondary contrasts (fib vs z3,
fib vs classical, uniform/scattered), and the burst stressor (reported
separately, no veto power).
"""
import json
import os
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "results.json")) as fh:
    R = json.load(fh)

FRACTIONS = R["fractions"]
CONSTANTS = list(R["constants"].keys())
ARMS = list(R["dims"].keys())
NBOOT = 10000
RNG = np.random.default_rng(20260801)


def cell(arm, const, f, mode):
    vals = R["cells"]["%s|%s|f%.2f|%s" % (arm, const, f, mode)]
    if isinstance(vals, dict):
        raise SystemExit("cell aborted; analysis cannot proceed on it")
    return np.asarray(vals, dtype=np.float64)


def delta_with_ci(a, b):
    """median(a) - median(b), paired bootstrap CI over seed indices."""
    n = len(a)
    d = float(np.median(a) - np.median(b))
    idx = RNG.integers(0, n, size=(NBOOT, n))
    boots = np.median(a[idx], axis=1) - np.median(b[idx], axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return d, float(lo), float(hi)


out = {"nboot": NBOOT, "bootstrap_rng_seed": 20260801,
       "primary": {}, "secondary": {}, "burst": {}, "axisB": {}}

# ---- primary rule: fib vs ising, uniform, scattered
per_f_structadv = []
per_f_flat = []
for f in FRACTIONS:
    d, lo, hi = delta_with_ci(cell("fib", "uniform", f, "scattered"),
                              cell("ising", "uniform", f, "scattered"))
    excl0 = (lo > 0.0) or (hi < 0.0)
    out["primary"]["f%.2f" % f] = {
        "delta": d, "ci95": [lo, hi], "ci_excludes_0": excl0,
        "median_fib": float(np.median(cell("fib", "uniform", f, "scattered"))),
        "median_ising": float(np.median(cell("ising", "uniform", f, "scattered"))),
    }
    per_f_structadv.append(d > 0.02 and excl0)
    per_f_flat.append(abs(d) <= 0.02)

if all(per_f_structadv):
    verdict = "STRUCTURAL ADVANTAGE"
elif all(per_f_flat):
    verdict = "PRIMARY KILL (flat)"
else:
    verdict = "INTERACTION/MIXED"
out["verdict"] = verdict

# ---- secondary contrasts (uniform, scattered)
for other in ("z3", "classical"):
    out["secondary"]["fib_vs_%s" % other] = {}
    for f in FRACTIONS:
        d, lo, hi = delta_with_ci(cell("fib", "uniform", f, "scattered"),
                                  cell(other, "uniform", f, "scattered"))
        out["secondary"]["fib_vs_%s" % other]["f%.2f" % f] = {
            "delta": d, "ci95": [lo, hi]}

# ---- burst stressor (separate, no veto): fib vs ising at uniform
for f in FRACTIONS:
    d, lo, hi = delta_with_ci(cell("fib", "uniform", f, "burst"),
                              cell("ising", "uniform", f, "burst"))
    out["burst"]["f%.2f" % f] = {"delta": d, "ci95": [lo, hi]}

# ---- Axis-B flatness: max pairwise |Delta| across constants within an arm
for arm in ARMS:
    per_f = {}
    for f in FRACTIONS:
        meds = {c: float(np.median(cell(arm, c, f, "scattered")))
                for c in CONSTANTS}
        maxpair = max(abs(meds[c1] - meds[c2])
                      for i, c1 in enumerate(CONSTANTS)
                      for c2 in CONSTANTS[i + 1:])
        per_f["f%.2f" % f] = {"medians": meds,
                              "max_pairwise_abs_delta": maxpair,
                              "flat_le_0.02": maxpair <= 0.02}
    out["axisB"][arm] = per_f
out["axisB_flat_all_arms_all_f"] = all(
    v["flat_le_0.02"] for arm in ARMS for v in out["axisB"][arm].values())

with open(os.path.join(HERE, "analysis.json"), "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)

print("VERDICT:", verdict)
for f in FRACTIONS:
    p = out["primary"]["f%.2f" % f]
    print("  f=%.2f  Delta=%+.6f  CI95=[%+.6f, %+.6f]  excl0=%s  (fib %.6f, ising %.6f)"
          % (f, p["delta"], p["ci95"][0], p["ci95"][1], p["ci_excludes_0"],
             p["median_fib"], p["median_ising"]))
print("Axis-B flat everywhere:", out["axisB_flat_all_arms_all_f"])
for k, v in out["secondary"].items():
    for fk, d in v.items():
        print("  %s %s: Delta=%+.6f CI=[%+.6f, %+.6f]"
              % (k, fk, d["delta"], d["ci95"][0], d["ci95"][1]))
for fk, d in out["burst"].items():
    print("  burst fib-ising %s: Delta=%+.6f CI=[%+.6f, %+.6f]"
          % (fk, d["delta"], d["ci95"][0], d["ci95"][1]))
