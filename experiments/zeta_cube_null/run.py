#!/usr/bin/env python3
"""ZETA-CUBE-NULL v1 runner.

Executes the SIGNED contract at experiments/ZETA_CUBE_NULL_PREREG_v1.md
exactly: controls FIRST, fixed mapping, fixed scores S1/S2, mechanical
kill condition. The contract's stated prediction is NULL.

Contract definitions (verbatim from the prereg, section 2):
  - Mapping (fixed): ordinate t -> cell (floor(3t) mod 3, floor(9t) mod 3,
    floor(27t) mod 3); 27-cell occupancy over the first 10,000 ordinates.
  - S1 = chi-square of occupancy vs uniform (df 26).
  - S2 = mutual information between consecutive cell indices (order structure).
  - Controls, run BEFORE the real zeros:
      (a) 10,000 uniform random reals on the same range (RNG seed 6000);
      (b) the zeros with their GAPS SHUFFLED (seed 6001);
      (c) the first 10,000 primes scaled to the same range.
  - Kill condition: if the real zeros' scores fall within the controls'
    spread (2.5-97.5 percentile of 200 control replicates for S1; same
    for S2), verdict NULL.

Implementation notes (declared here, not in the contract):
  - 200 replicates are drawn for each of the two stochastic control
    families, from a single RNG per family seeded with the contract seed
    (6000 for uniform, 6001 for gap-shuffle). The primes control is
    deterministic (one instance), reported alongside.
  - The controls' spread used by the kill condition is the 2.5-97.5
    percentile band of the pooled 400 stochastic control replicates;
    per-family bands are reported as diagnostics.
  - S2 is the plug-in mutual information in bits over the 9,999
    consecutive (cell_i, cell_{i+1}) pairs.
No phi-related numeric literals appear in this analysis code.
"""

import json
import math
import os
import sys
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZEROS_FILE = os.path.join(HERE, "zeros1.txt")
ZEROS_URLS = [
    "https://www-users.cse.umn.edu/~odlyzko/zeta_tables/zeros1",
    "http://www.dtc.umn.edu/~odlyzko/zeta_tables/zeros1",
]
N_TARGET = 10_000
N_REPLICATES = 200
N_CELLS = 27
DF = 26
BAND_LO, BAND_HI = 2.5, 97.5


# ----------------------------------------------------------------------
# Data acquisition + integrity check
# ----------------------------------------------------------------------

def obtain_ordinates():
    """Return (ordinates, n, source_note). Odlyzko table preferred; mpmath
    fallback with reduced n=2000 if all downloads fail."""
    if not os.path.exists(ZEROS_FILE):
        for url in ZEROS_URLS:
            try:
                print(f"downloading {url} ...")
                urllib.request.urlretrieve(url, ZEROS_FILE)
                break
            except Exception as exc:  # noqa: BLE001
                print(f"  failed: {exc}")
        else:
            print("all downloads failed; computing 2000 ordinates with mpmath")
            import mpmath
            mpmath.mp.dps = 20
            ords = np.array(
                [float(mpmath.zetazero(k).imag) for k in range(1, 2001)]
            )
            return ords, 2000, "mpmath fallback (reduced n=2000)"
    vals = []
    with open(ZEROS_FILE) as fh:
        for line in fh:
            line = line.strip()
            if line:
                vals.append(float(line))
            if len(vals) >= N_TARGET:
                break
    if len(vals) < N_TARGET:
        raise SystemExit(f"MISSING-INPUT: only {len(vals)} ordinates in table")
    return np.array(vals), N_TARGET, "Odlyzko zeros1 table (first 10,000 of 100,000)"


def integrity_check(ordinates):
    """First three ordinates must match mpmath zetazero to 6 decimals."""
    import mpmath
    mpmath.mp.dps = 15
    ref = [float(mpmath.zetazero(k).imag) for k in (1, 2, 3)]
    ok = all(abs(ordinates[i] - ref[i]) < 5e-7 for i in range(3))
    return ok, ref


# ----------------------------------------------------------------------
# Fixed mapping + scores (verbatim from contract section 2)
# ----------------------------------------------------------------------

def cells_of(t):
    """ordinate t -> cell (floor(3t) mod 3, floor(9t) mod 3, floor(27t) mod 3),
    flattened to a single index in [0, 27)."""
    a = np.floor(3.0 * t).astype(np.int64) % 3
    b = np.floor(9.0 * t).astype(np.int64) % 3
    c = np.floor(27.0 * t).astype(np.int64) % 3
    return 9 * a + 3 * b + c


def score_s1(cells, n):
    """S1 = chi-square of 27-cell occupancy vs uniform (df 26)."""
    counts = np.bincount(cells, minlength=N_CELLS).astype(float)
    expected = n / N_CELLS
    return float(np.sum((counts - expected) ** 2 / expected))


def score_s2(cells):
    """S2 = plug-in mutual information (bits) between consecutive cell indices."""
    x, y = cells[:-1], cells[1:]
    n = len(x)
    joint = np.zeros((N_CELLS, N_CELLS), dtype=float)
    np.add.at(joint, (x, y), 1.0)
    joint /= n
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)
    mask = joint > 0
    outer = np.outer(px, py)
    return float(np.sum(joint[mask] * np.log2(joint[mask] / outer[mask])))


def scores_of(t, n):
    cells = cells_of(t)
    return score_s1(cells, n), score_s2(cells)


# ----------------------------------------------------------------------
# Controls (run FIRST, by law)
# ----------------------------------------------------------------------

def first_primes(k):
    """First k primes by sieve."""
    limit = max(int(k * (math.log(k) + math.log(math.log(k)))) + 10, 100)
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(limit ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p:: p] = False
    primes = np.flatnonzero(sieve)
    if len(primes) < k:
        raise SystemExit("MISSING-INPUT: sieve limit too small")
    return primes[:k].astype(float)


def run_controls(ordinates, n):
    lo, hi = float(ordinates[0]), float(ordinates[-1])

    # (a) uniform reals on the same range, seed 6000, 200 replicates
    rng_u = np.random.default_rng(6000)
    uniform_s1, uniform_s2 = [], []
    for _ in range(N_REPLICATES):
        s1, s2 = scores_of(rng_u.uniform(lo, hi, size=n), n)
        uniform_s1.append(s1)
        uniform_s2.append(s2)

    # (b) gap-shuffled zeros, seed 6001, 200 replicates
    gaps = np.diff(ordinates)
    rng_g = np.random.default_rng(6001)
    shuffle_s1, shuffle_s2 = [], []
    for _ in range(N_REPLICATES):
        g = rng_g.permutation(gaps)
        t = ordinates[0] + np.concatenate(([0.0], np.cumsum(g)))
        s1, s2 = scores_of(t, n)
        shuffle_s1.append(s1)
        shuffle_s2.append(s2)

    # (c) first n primes scaled linearly to the same range (deterministic)
    p = first_primes(n)
    p_scaled = lo + (p - p[0]) * (hi - lo) / (p[-1] - p[0])
    primes_s1, primes_s2 = scores_of(p_scaled, n)

    return {
        "uniform": {"S1": uniform_s1, "S2": uniform_s2},
        "shuffled": {"S1": shuffle_s1, "S2": shuffle_s2},
        "primes": {"S1": primes_s1, "S2": primes_s2},
    }


def band(values):
    return [float(np.percentile(values, BAND_LO)),
            float(np.percentile(values, BAND_HI))]


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    ordinates, n, source = obtain_ordinates()
    ok, ref = integrity_check(ordinates)
    print(f"data: {source}; n={n}")
    print(f"integrity check (first 3 vs mpmath, 6 decimals): {'PASS' if ok else 'FAIL'}")
    if not ok:
        raise SystemExit("MISSING-INPUT: integrity check failed; refusing to score")

    # Controls FIRST, per contract section 2.
    print("running controls FIRST ...")
    controls = run_controls(ordinates, n)

    pooled_s1 = controls["uniform"]["S1"] + controls["shuffled"]["S1"]
    pooled_s2 = controls["uniform"]["S2"] + controls["shuffled"]["S2"]
    band_s1 = band(pooled_s1)
    band_s2 = band(pooled_s2)

    # Real zeros, scored AFTER the controls.
    print("scoring real zeros ...")
    real_s1, real_s2 = scores_of(ordinates, n)

    s1_within = band_s1[0] <= real_s1 <= band_s1[1]
    s2_within = band_s2[0] <= real_s2 <= band_s2[1]
    verdict = "NULL" if (s1_within and s2_within) else "DEVIATION"

    results = {
        "test_id": "ZETA-CUBE-NULL-v1",
        "contract": "experiments/ZETA_CUBE_NULL_PREREG_v1.md (SIGNED)",
        "data_source": source,
        "n": n,
        "integrity_check": {
            "pass": ok,
            "mpmath_first_three": ref,
            "table_first_three": [float(v) for v in ordinates[:3]],
        },
        "range": [float(ordinates[0]), float(ordinates[-1])],
        "controls_run_first": True,
        "n_replicates_per_family": N_REPLICATES,
        "control_bands_2p5_97p5": {
            "pooled": {"S1": band_s1, "S2": band_s2},
            "uniform": {"S1": band(controls["uniform"]["S1"]),
                        "S2": band(controls["uniform"]["S2"])},
            "shuffled": {"S1": band(controls["shuffled"]["S1"]),
                         "S2": band(controls["shuffled"]["S2"])},
        },
        "control_medians": {
            "uniform": {"S1": float(np.median(controls["uniform"]["S1"])),
                        "S2": float(np.median(controls["uniform"]["S2"]))},
            "shuffled": {"S1": float(np.median(controls["shuffled"]["S1"])),
                         "S2": float(np.median(controls["shuffled"]["S2"]))},
        },
        "primes_control": controls["primes"],
        "real_zeros": {"S1": real_s1, "S2": real_s2},
        "kill_condition": {
            "S1_within_band": s1_within,
            "S2_within_band": s2_within,
            "rule": "NULL iff both S1 and S2 fall within the pooled 2.5-97.5 "
                    "percentile band of the 400 stochastic control replicates",
        },
        "verdict": verdict,
        "s2_units": "bits (plug-in MI over 9,999 consecutive cell pairs)"
                    if n == N_TARGET else
                    f"bits (plug-in MI over {n-1} consecutive cell pairs)",
    }

    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump(results, fh, indent=2)

    write_verdict(results)
    print(f"S1 real={real_s1:.3f} band={band_s1}")
    print(f"S2 real={real_s2:.5f} band={band_s2}")
    print(f"VERDICT: {verdict}")


def write_verdict(r):
    b = r["control_bands_2p5_97p5"]
    lines = [
        "# VERDICT — ZETA-CUBE-NULL v1",
        "",
        f"- test_id: {r['test_id']}",
        f"- contract: {r['contract']}",
        f"- data: {r['data_source']}, n={r['n']}",
        f"- integrity check: {'PASS' if r['integrity_check']['pass'] else 'FAIL'} "
        "(first three ordinates match mpmath zetazero to 6 decimals)",
        "",
        "## Scores (controls run FIRST, per contract)",
        "",
        "| series | S1 (chi-square, df 26) | S2 (MI, bits) |",
        "|---|---|---|",
        f"| uniform control band (2.5–97.5 pct, 200 reps) | "
        f"{b['uniform']['S1'][0]:.3f} – {b['uniform']['S1'][1]:.3f} | "
        f"{b['uniform']['S2'][0]:.5f} – {b['uniform']['S2'][1]:.5f} |",
        f"| gap-shuffled control band (2.5–97.5 pct, 200 reps) | "
        f"{b['shuffled']['S1'][0]:.3f} – {b['shuffled']['S1'][1]:.3f} | "
        f"{b['shuffled']['S2'][0]:.5f} – {b['shuffled']['S2'][1]:.5f} |",
        f"| pooled control band (kill-condition band) | "
        f"{b['pooled']['S1'][0]:.3f} – {b['pooled']['S1'][1]:.3f} | "
        f"{b['pooled']['S2'][0]:.5f} – {b['pooled']['S2'][1]:.5f} |",
        f"| primes scaled (deterministic control) | "
        f"{r['primes_control']['S1']:.3f} | {r['primes_control']['S2']:.5f} |",
        f"| **real zeros** | **{r['real_zeros']['S1']:.3f}** | "
        f"**{r['real_zeros']['S2']:.5f}** |",
        "",
        "## Kill condition (applied mechanically)",
        "",
        f"- S1 within pooled band: {r['kill_condition']['S1_within_band']}",
        f"- S2 within pooled band: {r['kill_condition']['S2_within_band']}",
        f"- Rule: {r['kill_condition']['rule']}.",
        "",
        f"## Verdict: **{r['verdict']}**",
        "",
        "The contract's stated prediction was NULL. "
        + ("That prediction held: the base-3 digit mapping of the zero "
           "ordinates is statistically indistinguishable from the controls. "
           "A NULL confirms known equidistribution and closes the digit-cube "
           "door with a receipt."
           if r["verdict"] == "NULL" else
           "The real zeros separated from the controls on at least one "
           "score; per the contract this is a numerics/equidistribution "
           "finding only, to be escalated as its own question."),
        "",
        "## Fence (verbatim from the SIGNED contract)",
        "",
        "Under no outcome does this test bear on the Riemann Hypothesis, "
        "GHP, φ, or the 27-cell frame's symbolic uses.",
        "",
    ]
    with open(os.path.join(HERE, "VERDICT.md"), "w") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
