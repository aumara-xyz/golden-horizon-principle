#!/usr/bin/env python3
"""
SILVER-OPT v1 pipeline — allocation-code recovery simulation (K-RECOV-001 style).

Contract: experiments/SILVER_OPT_PREREG_v1.md (SIGNED 2026-08-01; SHA-256
034dbb47b56dcd956732d2873afac11e4748e8f093b46d82c6b07552a3f139d2 recorded in the
ledger). This file is ADDITIVE ONLY; the signed prereg is not touched.

Lane: constant-axis anomaly characterization. Explicitly GHP-independent.
No branch of this run is GHP physics evidence (prereg section 3).

--------------------------------------------------------------------------------
MODEL (K-RECOV-001 style; the external K-RECOV-001 source is not in this repo,
so the construction below is rebuilt from its ledger row and is fully disclosed):

- n shards, importance ranked: w_k = (k+1)^(-0.8) (Zipf exponent 0.8), rank 0
  most important.
- Redundancy budget B = round(0.3 * n) EXTRA copies (K-RECOV-001: 300 per
  1,000 shards; scaled to size). Every shard always has 1 base copy.
- Copies live in a linear slot array of exactly n + B slots for EVERY arm
  (identical total => damage masks over slot indices are arm-independent for
  the three non-adversarial geometries; fully paired comparisons).
- Layout rule (identical machinery for every arm; only per-shard copy counts
  differ): pass 0 places the base copy of every shard in rank order; pass p
  places copy p+1 of every shard with count > p, in rank order.
- Damage erases round(f * (n+B)) slots. A shard is recovered iff at least one
  of its copies survives.
- Recovery fidelity = importance-weighted recovered fraction:
      sum_{recovered} w_k / sum_k w_k          (zero damage => fidelity 1).

ARMS (allocation of the B extra copies):
- Noble tier arms (golden / silver / bronze) and exp-2: tiered heavy-tail
  allocation. Tier ell gives ONE extra copy to the top T_ell shards, where
  T_ell is the ell-th term of the arm's INTEGER sequence:
      golden : u1=1, u2=1, u_{k+1} = 1*u_k + u_{k-1}   (Fibonacci: 1,1,2,3,5,...)
      silver : u1=1, u2=2, u_{k+1} = 2*u_k + u_{k-1}   (Pell:      1,2,5,12,29,...)
      bronze : u1=1, u2=3, u_{k+1} = 3*u_k + u_{k-1}   (           1,3,10,33,109,...)
      exp-2  : u1=1,        u_{k+1} = 2*u_k            (           1,2,4,8,16,...)
  Tiers are consumed in order while budget remains; the final partial tier
  gives its remaining copies to the top ranks. Tier widths are capped at n.
  NUMEROLOGY GUARD (hard law 2): phi never appears as a literal anywhere in
  this file. The golden arm is DEFINED by the Fibonacci recurrence (the
  fusion-path counting of tau (x) tau = 1 (+) tau); its limiting ratio falls
  out of the recursion and is reported as a derived diagnostic only. The
  erasure channel, layout, recovery rule, and scorer contain no constant of
  any arm.
- greedy_rank: purpose-built water-filling control. Iteratively give the next
  extra copy to the shard with maximal marginal expected-recovery gain
  w_k * f_d^(1+e_k) * (1 - f_d) under iid per-copy loss at design point
  f_d = 0.5 (mid grid; no arm constant enters).
- uniform: B extras spread evenly across ALL ranks by Bresenham apportionment
  (importance-blind).
- phi_shuffled / silver_shuffled: tripwire controls. EXACTLY the parent arm's
  per-shard extras vector, randomly permuted across shards per seed (same
  numbers, wrong places). Multiset equality is asserted per seed.

DAMAGE GEOMETRIES (rules are arm-blind; identical erased slot sets across arms
except the tear, which is deterministic given the arm's layout):
1. uniform_random  : seeded uniform subset of slots.
2. contiguous_burst: seeded start, wrap-around contiguous block.
3. adversarial_tear: importance-targeted (the GH-RECOV stressor): erase slots
   in order of their shard's importance rank (most important first; stable
   slot-index tie-break), until the budget is spent. Deterministic; no rng.
4. periodic_stride : evenly spaced periodic pattern with seeded phase; exact
   erased count (spacing (n+B)/e >= 4/3 > 1 guarantees distinct slots).

STATISTIC (prereg section 1): per-cell (arm, size, fraction, geometry) median
across the 20 seeds (2000..2019, identical across cells). Contrasts:
  Delta_sg = median(silver) - median(golden)
  Delta_sn = median(silver) - median(best non-silver NOBLE arm), where noble =
             {golden, bronze} for the comparator (silver excluded), the
             comparator being the one with the higher cell median on the full
             data; 95% bootstrap CI, 10,000 paired seed resamples.

BRANCH CRITERIA (prereg section 2, applied mechanically):
- H1 iff Delta_sn > +0.02 with CI excluding 0 in >= 3 of 4 geometries at BOTH
  larger sizes (1000 and 4000).
- H0 iff all noble arms (golden, silver, bronze) are within +-0.02 of each
  other in every cell.
- H2 iff silver's advantage (Delta_sn > +0.02 with CI excluding 0, any cell)
  occurs in at most one geometry AND that geometry is the adversarial tear
  (and occurs in at least one cell there; an empty advantage set is H0
  territory, not H2).
- Anything else: UNRESOLVED. Precedence H1, H0, H2, UNRESOLVED; all three
  flags are recorded so overlap is visible.

OPERATIONALIZATION DECLARED BEFORE THE RUN (the prereg leaves fraction
aggregation inside a (geometry, size) unit unspecified): PRIMARY rule = a
geometry satisfies the H1 criterion at a size iff the per-cell test
(Delta_sn > 0.02 and CI low > 0) passes in a MAJORITY (>= 2 of 3) of damage
fractions at that (geometry, size). The strict all-3-of-3 variant is computed
and reported as sensitivity. This choice is written here, in the committed
pipeline, before the sweep has ever been executed.

Runtime: python3 + numpy, deterministic, offline, single-core. One full run.
Outputs: experiments/silver_opt_results/{results.json, summary.md, VERDICT.md}
"""

import json
import os
import heapq
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "silver_opt_results")

# ---------------- locked configuration ----------------
SIZES = [250, 1000, 4000]
FRACTIONS = [0.25, 0.50, 0.75]
GEOMETRIES = ["uniform_random", "contiguous_burst", "adversarial_tear", "periodic_stride"]
SEEDS = list(range(2000, 2020))          # 20 seeds, identical across cells
ZIPF_EXPONENT = 0.8
BUDGET_RATIO = 0.3                       # K-RECOV-001: 300 extras / 1000 shards
GREEDY_DESIGN_F = 0.5                    # greedy water-filling design point (mid grid)
N_BOOT = 10_000
MARGIN = 0.02
BOOT_SEED = 20260801                     # date-tag; no arm constant
LARGER_SIZES = [1000, 4000]

ARMS = ["golden", "silver", "bronze", "exp2", "greedy_rank", "uniform",
        "phi_shuffled", "silver_shuffled"]
NOBLE_ARMS = ["golden", "silver", "bronze"]
NONSILVER_NOBLE = ["golden", "bronze"]
SHUFFLE_PARENT = {"phi_shuffled": "golden", "silver_shuffled": "silver"}
TIER_M = {"golden": 1, "silver": 2, "bronze": 3}   # u_{k+1} = m*u_k + u_{k-1}


# ---------------- arm sequences (integer recurrences only) ----------------
def metallic_sequence(m, cap, need):
    """u1=1, u2=m, u_{k+1}=m*u_k+u_{k-1}; terms capped at `cap`; generate until
    the capped terms sum to at least `need`. m=1 gives Fibonacci 1,1,2,3,5,...;
    m=2 gives Pell 1,2,5,12,...; m=3 gives bronze 1,3,10,33,..."""
    terms = [1, m]
    while sum(min(t, cap) for t in terms) < need:
        terms.append(m * terms[-1] + terms[-2])
    return [min(t, cap) for t in terms]


def doubling_sequence(cap, need):
    terms = [1]
    while sum(min(t, cap) for t in terms) < need:
        terms.append(2 * terms[-1])
    return [min(t, cap) for t in terms]


def limiting_ratio(m, iters=64):
    """Diagnostic only: ratio u_{k+1}/u_k of the recurrence (falls out of the
    recursion; never used by any machinery)."""
    a, b = 1.0, float(m)
    for _ in range(iters):
        a, b = b, m * b + a
    return b / a


# ---------------- allocations (extras vector, sums to B) ----------------
def alloc_tiered(widths, n, budget):
    extras = np.zeros(n, dtype=np.int64)
    left = budget
    for w in widths:
        w = min(w, n)
        if left <= 0:
            break
        if left >= w:
            extras[:w] += 1
            left -= w
        else:
            extras[:left] += 1
            left = 0
    assert left == 0, "tier widths did not cover the budget"
    return extras


def alloc_uniform(n, budget):
    k = np.arange(n + 1, dtype=np.int64)
    marks = np.floor(k * budget / n).astype(np.int64)
    return np.diff(marks)


def alloc_greedy(n, budget, weights, f_design):
    extras = np.zeros(n, dtype=np.int64)
    # marginal gain of adding an extra to shard i at current extras e:
    #   w_i * f^(1+e) * (1-f)
    heap = [(-(weights[i] * (f_design ** 1) * (1.0 - f_design)), i, 0)
            for i in range(n)]
    heapq.heapify(heap)
    for _ in range(budget):
        neg_gain, i, e = heapq.heappop(heap)
        extras[i] += 1
        e2 = e + 1
        gain2 = weights[i] * (f_design ** (1 + e2)) * (1.0 - f_design)
        heapq.heappush(heap, (-gain2, i, e2))
    return extras


def base_extras(arm, n, budget, weights):
    if arm in TIER_M:
        return alloc_tiered(metallic_sequence(TIER_M[arm], n, budget), n, budget)
    if arm == "exp2":
        return alloc_tiered(doubling_sequence(n, budget), n, budget)
    if arm == "greedy_rank":
        return alloc_greedy(n, budget, weights, GREEDY_DESIGN_F)
    if arm == "uniform":
        return alloc_uniform(n, budget)
    raise ValueError(arm)


# ---------------- layout / damage / scoring ----------------
def build_layout(extras):
    counts = extras + 1                       # base copy + extras
    passes = [np.nonzero(counts > p)[0] for p in range(int(counts.max()))]
    return np.concatenate(passes)             # slot -> shard rank


def damage_mask(geom, total, e_count, rng, slot_shard):
    mask = np.zeros(total, dtype=bool)
    if e_count == 0:
        return mask
    if geom == "uniform_random":
        idx = rng.choice(total, size=e_count, replace=False)
    elif geom == "contiguous_burst":
        start = int(rng.integers(total))
        idx = (start + np.arange(e_count)) % total
    elif geom == "periodic_stride":
        phase = float(rng.random()) * total
        pos = np.floor((np.arange(e_count) + 0.5) * (total / e_count) + phase)
        idx = pos.astype(np.int64) % total
        assert len(np.unique(idx)) == e_count
    elif geom == "adversarial_tear":
        order = np.argsort(slot_shard, kind="stable")   # most important first
        idx = order[:e_count]
    else:
        raise ValueError(geom)
    mask[idx] = True
    return mask


def fidelity(slot_shard, erased, weights):
    n = len(weights)
    survived = np.zeros(n, dtype=bool)
    survived[slot_shard[~erased]] = True
    # identical summation path for numerator and denominator so that
    # zero damage yields exactly 1.0 (self-test requirement)
    num = np.where(survived, weights, 0.0).sum()
    den = np.where(np.ones(n, dtype=bool), weights, 0.0).sum()
    return float(num / den)


# ---------------- self-tests (run before the sweep) ----------------
def self_test():
    report = {}
    for n in SIZES:
        budget = int(round(BUDGET_RATIO * n))
        w = (np.arange(1, n + 1, dtype=np.float64)) ** (-ZIPF_EXPONENT)
        for arm in ARMS:
            if arm in SHUFFLE_PARENT:
                parent = SHUFFLE_PARENT[arm]
                ex_parent = base_extras(parent, n, budget, w)
                rng = np.random.default_rng([SEEDS[0], n, 7, ARMS.index(arm)])
                ex = ex_parent[rng.permutation(n)]
                # tripwire integrity: same numbers, permuted positions
                assert np.array_equal(np.sort(ex), np.sort(ex_parent)), \
                    f"shuffle multiset mismatch: {arm} n={n}"
            else:
                ex = base_extras(arm, n, budget, w)
            assert int(ex.sum()) == budget, f"budget violated: {arm} n={n}"
            layout = build_layout(ex)
            assert len(layout) == n + budget
            # zero damage => fidelity exactly 1
            fid0 = fidelity(layout, np.zeros(n + budget, dtype=bool), w)
            assert fid0 == 1.0, f"zero-damage fidelity != 1: {arm} n={n} ({fid0})"
        # damage-count exactness on one representative mask set
        total = n + budget
        for f in FRACTIONS:
            e_count = int(round(f * total))
            for geom in GEOMETRIES:
                rng = np.random.default_rng([SEEDS[0], n, int(f * 100),
                                             GEOMETRIES.index(geom)])
                layout = build_layout(base_extras("golden", n, budget, w))
                m = damage_mask(geom, total, e_count, rng, layout)
                assert int(m.sum()) == e_count, f"erase count off: {geom}"
        report[str(n)] = "PASS (budget, layout size, zero-damage fidelity=1, " \
                         "shuffle multiset, erase counts)"
    return report


# ---------------- sweep ----------------
def run_sweep():
    fids = {arm: {} for arm in ARMS}   # arm -> cell key -> list of 20 fidelities
    for n in SIZES:
        budget = int(round(BUDGET_RATIO * n))
        total = n + budget
        w = (np.arange(1, n + 1, dtype=np.float64)) ** (-ZIPF_EXPONENT)
        det_layouts = {arm: build_layout(base_extras(arm, n, budget, w))
                       for arm in ARMS if arm not in SHUFFLE_PARENT}
        det_extras = {arm: base_extras(arm, n, budget, w)
                      for arm in ARMS if arm not in SHUFFLE_PARENT}
        for si, seed in enumerate(SEEDS):
            # shuffled-arm layouts are per-seed
            layouts = dict(det_layouts)
            for arm, parent in SHUFFLE_PARENT.items():
                rng = np.random.default_rng([seed, n, 7, ARMS.index(arm)])
                ex = det_extras[parent][rng.permutation(n)]
                layouts[arm] = build_layout(ex)
            for f in FRACTIONS:
                e_count = int(round(f * total))
                for geom in GEOMETRIES:
                    key = (n, f, geom)
                    # damage rng depends only on (seed, size, fraction, geometry):
                    # identical erased slot-set across arms for non-tear geoms.
                    rng = np.random.default_rng([seed, n, int(f * 100),
                                                 GEOMETRIES.index(geom)])
                    if geom == "adversarial_tear":
                        for arm in ARMS:
                            mask = damage_mask(geom, total, e_count, rng,
                                               layouts[arm])
                            fids[arm].setdefault(key, []).append(
                                fidelity(layouts[arm], mask, w))
                    else:
                        mask = damage_mask(geom, total, e_count, rng, None)
                        for arm in ARMS:
                            fids[arm].setdefault(key, []).append(
                                fidelity(layouts[arm], mask, w))
    return fids


# ---------------- statistics ----------------
def bootstrap_ci_median_diff(a, b, rng):
    """95% CI for median(a) - median(b), paired seed resampling."""
    a = np.asarray(a); b = np.asarray(b)
    idx = rng.integers(0, len(a), size=(N_BOOT, len(a)))
    d = np.median(a[idx], axis=1) - np.median(b[idx], axis=1)
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def analyze(fids):
    rng = np.random.default_rng(BOOT_SEED)
    cells = []
    for n in SIZES:
        for f in FRACTIONS:
            for geom in GEOMETRIES:
                key = (n, f, geom)
                med = {arm: float(np.median(fids[arm][key])) for arm in ARMS}
                comp = max(NONSILVER_NOBLE, key=lambda a: med[a])
                d_sg = med["silver"] - med["golden"]
                d_sn = med["silver"] - med[comp]
                ci_sg = bootstrap_ci_median_diff(fids["silver"][key],
                                                 fids["golden"][key], rng)
                ci_sn = bootstrap_ci_median_diff(fids["silver"][key],
                                                 fids[comp][key], rng)
                noble_spread = max(abs(med[x] - med[y])
                                   for x in NOBLE_ARMS for y in NOBLE_ARMS)
                cells.append({
                    "size": n, "fraction": f, "geometry": geom,
                    "medians": med,
                    "comparator_nonsilver_noble": comp,
                    "delta_sg": d_sg, "ci_sg": ci_sg,
                    "delta_sn": d_sn, "ci_sn": ci_sn,
                    "silver_advantage": bool(d_sn > MARGIN and ci_sn[0] > 0.0),
                    "noble_max_pairwise_gap": noble_spread,
                    "noble_within_margin": bool(noble_spread <= MARGIN),
                })
    return cells


def branch_verdict(cells):
    def cell(n, f, geom):
        return next(c for c in cells if c["size"] == n and c["fraction"] == f
                    and c["geometry"] == geom)

    # H1 — primary (majority of fractions) and strict (all fractions) variants
    geom_pass_primary, geom_pass_strict = {}, {}
    for geom in GEOMETRIES:
        ok_primary, ok_strict = True, True
        for n in LARGER_SIZES:
            hits = sum(1 for f in FRACTIONS if cell(n, f, geom)["silver_advantage"])
            if hits < 2:
                ok_primary = False
            if hits < 3:
                ok_strict = False
        geom_pass_primary[geom] = ok_primary
        geom_pass_strict[geom] = ok_strict
    h1_primary = sum(geom_pass_primary.values()) >= 3
    h1_strict = sum(geom_pass_strict.values()) >= 3

    # H0 — all noble arms within +-0.02 everywhere
    h0 = all(c["noble_within_margin"] for c in cells)

    # H2 — silver advantage confined to the adversarial tear (and present there)
    adv_geoms = sorted({c["geometry"] for c in cells if c["silver_advantage"]})
    h2 = (len(adv_geoms) >= 1) and (set(adv_geoms) <= {"adversarial_tear"})

    if h1_primary:
        verdict = "H1"
    elif h0:
        verdict = "H0"
    elif h2:
        verdict = "H2"
    else:
        verdict = "UNRESOLVED"
    return {
        "verdict": verdict,
        "h1_primary_majority_rule": h1_primary,
        "h1_strict_all_fractions_rule": h1_strict,
        "h1_geometries_passing_primary": [g for g, v in geom_pass_primary.items() if v],
        "h1_geometries_passing_strict": [g for g, v in geom_pass_strict.items() if v],
        "h0_noble_plateau": h0,
        "h2_geometry_artifact": h2,
        "geometries_with_silver_advantage_any_cell": adv_geoms,
    }


# ---------------- reporting ----------------
NO_CLAIM_VERBATIM = (
    "Not GHP evidence; not φ physics; not a fusion-category statement "
    "(M-006 forbids the reading); not a universal coding-theory law from one "
    "family of synthetic codes. H1, if it lands, is an anomaly *characterized*, "
    "not an anomaly *explained* — explanation gets its own preregistration."
)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    st = self_test()
    fids = run_sweep()
    cells = analyze(fids)
    branches = branch_verdict(cells)

    diagnostics = {
        "derived_limiting_ratios_report_only": {
            "golden_fibonacci": limiting_ratio(1),
            "silver_pell": limiting_ratio(2),
            "bronze": limiting_ratio(3),
        },
        "note": ("ratios are diagnostics derived by iterating the integer "
                 "recurrences; no machinery consumes them"),
    }

    results = {
        "test_id": "SILVER-OPT-v1",
        "prereg": "experiments/SILVER_OPT_PREREG_v1.md",
        "prereg_sha256": "034dbb47b56dcd956732d2873afac11e4748e8f093b46d82c6b07552a3f139d2",
        "config": {
            "sizes": SIZES, "fractions": FRACTIONS, "geometries": GEOMETRIES,
            "seeds": SEEDS, "zipf_exponent": ZIPF_EXPONENT,
            "budget_ratio": BUDGET_RATIO, "greedy_design_f": GREEDY_DESIGN_F,
            "n_boot": N_BOOT, "margin": MARGIN, "bootstrap_seed": BOOT_SEED,
            "arms": ARMS, "noble_arms": NOBLE_ARMS,
            "shuffle_parents": SHUFFLE_PARENT,
        },
        "self_test": st,
        "diagnostics": diagnostics,
        "cells": [
            {**c, "fidelities": {arm: fids[arm][(c["size"], c["fraction"],
                                                 c["geometry"])] for arm in ARMS}}
            for c in cells
        ],
        "branches": branches,
        "no_claim_verbatim": NO_CLAIM_VERBATIM,
    }
    with open(os.path.join(OUTDIR, "results.json"), "w") as fh:
        json.dump(results, fh, indent=1)

    # ---- summary.md ----
    lines = []
    lines.append("# SILVER-OPT v1 — sweep summary\n")
    lines.append("Contract: `experiments/SILVER_OPT_PREREG_v1.md` (signed "
                 "2026-08-01). Pipeline: `experiments/silver_opt_pipeline.py`. "
                 "Deterministic; seeds 2000-2019.\n")
    lines.append("Self-tests: " + "; ".join(f"n={k}: {v}" for k, v in st.items())
                 + "\n")
    lines.append("Derived limiting ratios (diagnostic only, from the integer "
                 "recurrences): "
                 + ", ".join(f"{k}={v:.10f}" for k, v in
                             diagnostics["derived_limiting_ratios_report_only"].items())
                 + "\n")
    lines.append("\n## Per-cell medians and contrasts\n")
    lines.append("| size | frac | geometry | golden | silver | bronze | exp2 | "
                 "greedy | uniform | phi-shuf | silver-shuf | D_sg | D_sn "
                 "(comp) | 95% CI D_sn | silver adv |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        m = c["medians"]
        lines.append(
            f"| {c['size']} | {c['fraction']:.2f} | {c['geometry']} "
            f"| {m['golden']:.4f} | {m['silver']:.4f} | {m['bronze']:.4f} "
            f"| {m['exp2']:.4f} | {m['greedy_rank']:.4f} | {m['uniform']:.4f} "
            f"| {m['phi_shuffled']:.4f} | {m['silver_shuffled']:.4f} "
            f"| {c['delta_sg']:+.4f} | {c['delta_sn']:+.4f} "
            f"({c['comparator_nonsilver_noble']}) "
            f"| [{c['ci_sn'][0]:+.4f}, {c['ci_sn'][1]:+.4f}] "
            f"| {'YES' if c['silver_advantage'] else 'no'} |")
    lines.append("\n## Branch evaluation (mechanical)\n")
    lines.append("```json\n" + json.dumps(branches, indent=2) + "\n```\n")
    with open(os.path.join(OUTDIR, "summary.md"), "w") as fh:
        fh.write("\n".join(lines))

    print(json.dumps(branches, indent=2))
    print("wrote", os.path.join(OUTDIR, "results.json"))
    print("wrote", os.path.join(OUTDIR, "summary.md"))
    return results


if __name__ == "__main__":
    main()
