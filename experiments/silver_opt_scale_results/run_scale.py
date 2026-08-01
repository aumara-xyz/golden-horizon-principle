#!/usr/bin/env python3
"""
SILVER-OPT-SCALE v1 runner — maps the die-off curve of the silver tear line.

Contract: experiments/SILVER_OPT_SCALE_PREREG_v1.md (SIGNED 2026-08-01).

This file is a WRAPPER. It reuses experiments/silver_opt_geo_pipeline.py
UNMODIFIED (imported as `geo`): placement, tripwire construction, damage,
scoring, per-cell runner, analysis (median contrast + paired bootstrap CI)
are all geo's functions executing their original code. The only things this
wrapper does are:

  1. INJECT the preregistered configuration into geo's module globals:
       sizes      {256, 320, 384, 448, 512, 640, 768, 1024}, K = N/8
                  (N/2K held at 4, exactly as GEO)
       geometries {adversarial_tear, periodic_stride}
       arms       {golden, silver, bronze, golden_shuffled, silver_shuffled}
       seeds      5000..5099 (100, fresh)
     Everything else (MARGIN, N_BOOT, BOOT_SEED, DAMAGE_GRID, CRITICAL_BAND,
     SIGMA, RCOND, CB metric) is consumed from geo / its substrate untouched.
  2. Drive the sweep (checkpointed to this directory's records.jsonl,
     resumable, parallel across (size, seed) worker processes — each cell is
     deterministic and self-contained, so execution order and parallelism
     cannot change any number).
  3. Apply the SCALE branch rules mechanically and write
     results.json / summary.md / VERDICT.md here.

DISCLOSURES (declared before any sweep data existed):
  - geo.run_arm_seed_geo's `geometries` default was bound at its definition to
    GEO's 4-tuple, so this wrapper passes the injected 2-geometry tuple
    EXPLICITLY on every call. No geo code is modified.
  - geo.placement_slots derives the tripwire permutation substream from
    ARMS.index(arm). With the injected 5-arm tuple the indices are
    (golden_shuffled=3, silver_shuffled=4) instead of GEO's (4, 5). The
    streams are fresh-and-deterministic either way, and the seed block
    (5000..5099) is itself fresh, so no comparison to GEO's streams exists.
  - The sweep runs cells in parallel worker processes. Every number produced
    is a pure function of (size, arm, seed) via geo's deterministic code;
    BLAS threading is pinned to 1 thread per worker.

BRANCH RULES — mechanical operationalization of the prereg (section 2),
declared here and committed BEFORE the sweep ran. All quantities refer to the
adversarial_tear geometry's Delta_sg(n) = median silver CB - median golden CB
with its 95% paired bootstrap CI [lo(n), hi(n)] (geo.analyze verbatim), over
the eight sizes in increasing order:
  excl_pos(n) := lo(n) > 0                    "CI excludes 0" (positive side)
  incl0(n)    := lo(n) <= 0 <= hi(n)          "CI includes 0"
  - S0 (no reproduction): incl0(256). Evaluated first — the anchor cell
    failing to reproduce pre-empts any curve reading.
  - S1 (crossover located): Delta_sg(256) > MARGIN and excl_pos(256); the
    excl_pos pattern over increasing sizes is a strict prefix (excl_pos for
    the first m sizes, incl0 for ALL remaining sizes, 1 <= m < 8 — so the
    advantage actually dies off within the scanned range and never returns);
    and Delta_sg is monotonically decreasing WITHIN CIs: for every
    consecutive pair, Delta_sg(n_{i+1}) <= Delta_sg(n_i) OR the two CIs
    overlap. n* := the last size whose CI excludes 0 (= size index m-1).
  - S2 (non-monotone): some size has incl0 and some STRICTLY LARGER size has
    excl_pos — the advantage re-emerges after dying.
  - Precedence S0 -> S1 -> S2 -> UNRESOLVED (S1 and S2 are mutually
    exclusive by the prefix condition; all flags are recorded regardless).
  - Anything else: UNRESOLVED, no re-cutting.

NUMEROLOGY GUARD: no phi-family decimal literal in this file; an AST audit of
THIS file (forbidden values derived arithmetically or taken by reference from
the pinned substrate) runs before anything else, alongside geo's own audits.

NO-CLAIMS (prereg section 3): constant/placement axis; not GHP physics under
any branch.

Usage (from the repo's experiments/ directory or anywhere):
  python3 run_scale.py --selftest   # audits + geo self-tests at injected size list
  python3 run_scale.py --run        # full preregistered sweep + branch + reports
"""

from __future__ import annotations

import os

# Pin BLAS threading BEFORE numpy loads (workers re-execute this on spawn).
for _v in ("VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS",
           "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import ast
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent          # .../experiments/silver_opt_scale_results
EXPERIMENTS = HERE.parent                        # .../experiments
for p in (str(EXPERIMENTS),):
    if p not in sys.path:
        sys.path.insert(0, p)

import silver_opt_geo_pipeline as geo            # reused UNMODIFIED
import ghp_golden_heal_v2_probe as ghv2          # pinned substrate (by reference)

OUTDIR = HERE
CKPT = OUTDIR / "records.jsonl"

# ---------------- preregistered injection (contract section 1) ----------------
SCALE_NS = (256, 320, 384, 448, 512, 640, 768, 1024)
SCALE_SIZES = tuple((n, n // 8) for n in SCALE_NS)       # K = N/8  <=>  N/2K = 4
SCALE_SEEDS = tuple(range(5000, 5100))                   # 100 fresh seeds
SCALE_GEOMETRIES = ("adversarial_tear", "periodic_stride")
SCALE_ARMS = ("golden", "silver", "bronze", "golden_shuffled", "silver_shuffled")

def inject() -> None:
    """Set geo's module globals to the preregistered SCALE configuration.
    geo's functions read these globals at call time; its code is untouched."""
    geo.SIZES = SCALE_SIZES
    geo.SEEDS = SCALE_SEEDS
    geo.GEOMETRIES = SCALE_GEOMETRIES
    geo.ARMS = SCALE_ARMS
    geo.OUTDIR = OUTDIR
    geo.CKPT = CKPT

inject()   # at import time, so spawned workers inherit the injection too

MARGIN = geo.MARGIN            # 0.02, consumed by reference — never re-typed


# ---------------- numerology audit of THIS file ----------------
def audit_wrapper_numerology() -> dict:
    """AST scan of this wrapper: no numeric literal within 1e-4 of any arm
    constant. Forbidden values are derived / taken by substrate reference."""
    phi = (1.0 + 5.0 ** 0.5) / 2.0
    forbidden = [phi, phi - 1.0, 5.0 ** 0.5,
                 ghv2.ALPHA_GOLDEN, ghv2.ALPHA_SILVER, ghv2.ALPHA_BRONZE]
    tree = ast.parse(Path(__file__).read_text())
    n_checked = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                and not isinstance(node.value, bool):
            n_checked += 1
            for pv in forbidden:
                assert abs(float(node.value) - pv) > 1e-4, (
                    f"NUMEROLOGY GUARD FAILED: forbidden constant {node.value} "
                    f"at line {node.lineno}")
    return {"status": "PASSED", "numeric_literals_checked": n_checked}


def run_audits_and_selftests() -> dict:
    report = {"wrapper_audit": audit_wrapper_numerology(),
              "geo_pipeline_audit": geo.audit_new_module_numerology()["status"],
              "injected_config_check": {
                  "sizes_n_k": [list(s) for s in geo.SIZES],
                  "n_over_2k_all_4": all(n == 8 * k for n, k in geo.SIZES),
                  "seeds": [geo.SEEDS[0], geo.SEEDS[-1], len(geo.SEEDS)],
                  "geometries": list(geo.GEOMETRIES),
                  "arms": list(geo.ARMS)}}
    assert report["injected_config_check"]["n_over_2k_all_4"]
    # geo's own self-tests, executing at the INJECTED configuration (all eight
    # sizes; zero-damage identity, tripwire multisets, exact erase counts,
    # bit-identical determinism of the full cell).
    report["geo_self_test"] = geo.self_test()
    return report


# ---------------- parallel checkpointed sweep ----------------
def _work(task):
    """One (n, k, seed): run the needed arms with the injected geometries.
    Pure function of its arguments via geo's deterministic code."""
    n, k, seed, arms_needed = task
    with geo.substrate_size(n, k):
        coeffs = ghv2.build_signal_coeffs(seed)
        eta = np.random.default_rng(
            [seed, ghv2.TAG_NOISE]).standard_normal(ghv2.N)
        return [geo.run_arm_seed_geo(arm, seed, coeffs, eta,
                                     geometries=SCALE_GEOMETRIES)
                for arm in arms_needed]


def run_sweep(workers: int) -> list:
    done, records = set(), []
    if CKPT.exists():
        for line in CKPT.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            records.append(rec)
            done.add((rec["size_n"], rec["arm"], rec["seed"]))
        print(f"[SILVER-OPT-SCALE] resuming: {len(records)} cells already done",
              flush=True)
    tasks = []
    for (n, k) in SCALE_SIZES:
        for seed in SCALE_SEEDS:
            arms_needed = tuple(a for a in SCALE_ARMS
                                if (n, a, seed) not in done)
            if arms_needed:
                tasks.append((n, k, seed, arms_needed))
    total = len(SCALE_SIZES) * len(SCALE_SEEDS) * len(SCALE_ARMS)
    print(f"[SILVER-OPT-SCALE] {len(tasks)} (size,seed) tasks to run "
          f"({len(records)}/{total} cells done)", flush=True)
    t0 = time.time()
    ndone = 0
    with open(CKPT, "a") as fh, ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_work, t): t for t in tasks}
        for fut in as_completed(futs):
            n, _k, seed, _arms = futs[fut]
            for rec in fut.result():
                fh.write(json.dumps(rec) + "\n")
                records.append(rec)
            fh.flush()
            ndone += 1
            if ndone % 25 == 0 or ndone == len(tasks):
                print(f"[SILVER-OPT-SCALE] {ndone}/{len(tasks)} tasks "
                      f"({time.time() - t0:8.1f}s elapsed, last n={n} "
                      f"seed={seed})", flush=True)
    return records


# ---------------- branch evaluation (mechanical; declared pre-run above) ----
def scale_branch(cells: list) -> dict:
    tear = sorted((c for c in cells if c["geometry"] == "adversarial_tear"),
                  key=lambda c: c["size"])
    sizes = [c["size"] for c in tear]
    assert sizes == list(SCALE_NS), sizes
    d = [c["delta_sg_median"] for c in tear]
    lo = [c["ci_sg"][0] for c in tear]
    hi = [c["ci_sg"][1] for c in tear]
    excl_pos = [l > 0.0 for l in lo]
    incl0 = [l <= 0.0 <= h for l, h in zip(lo, hi)]

    s0 = incl0[0]
    base_qual = (d[0] > MARGIN) and excl_pos[0]

    m = 0
    while m < len(sizes) and excl_pos[m]:
        m += 1
    prefix = (m >= 1) and (m < len(sizes)) and all(incl0[j]
                                                   for j in range(m, len(sizes)))

    def overlap(i, j):
        return lo[j] <= hi[i] and lo[i] <= hi[j]

    mono_within_ci = all(d[i + 1] <= d[i] or overlap(i, i + 1)
                         for i in range(len(sizes) - 1))
    s1 = bool(base_qual and prefix and mono_within_ci)
    n_star = sizes[m - 1] if (s1 and m >= 1) else None

    s2 = any(incl0[i] and any(excl_pos[j] for j in range(i + 1, len(sizes)))
             for i in range(len(sizes)))

    if s0:
        verdict = "S0_NO_REPRODUCTION"
    elif s1:
        verdict = "S1_CROSSOVER_LOCATED"
    elif s2:
        verdict = "S2_NON_MONOTONE"
    else:
        verdict = "UNRESOLVED"

    return {"verdict": verdict, "n_star": n_star,
            "flags": {"s0_no_reproduction": bool(s0),
                      "s1_crossover_located": s1,
                      "s2_non_monotone": bool(s2),
                      "base_qual_256": bool(base_qual),
                      "prefix_pattern": bool(prefix),
                      "monotone_within_cis": bool(mono_within_ci),
                      "n_leading_excl_pos": m},
            "tear_curve": [{"n": n_, "delta_sg_median": d_,
                            "ci95": [l_, h_],
                            "ci_excludes_0_pos": e_, "ci_includes_0": z_}
                           for n_, d_, l_, h_, e_, z_
                           in zip(sizes, d, lo, hi, excl_pos, incl0)],
            "rule": ("S0 iff CI(256) includes 0 (evaluated first). "
                     "S1 iff Delta_sg(256)>MARGIN with CI(256) excluding 0 "
                     "positively, the positive-exclusion pattern is a strict "
                     "prefix of the size list (dies off within range, never "
                     "returns), and Delta_sg decreases monotonically within "
                     "CIs (consecutive decrease OR CI overlap); n* = last "
                     "size whose CI excludes 0. S2 iff the advantage "
                     "re-emerges (CI excluding 0 positively at a size "
                     "strictly above one whose CI includes 0). Precedence "
                     "S0 -> S1 -> S2 -> UNRESOLVED; declared and committed "
                     "before the sweep ran.")}


# ---------------- reporting ----------------
NO_CLAIM_VERBATIM = ("Constant/placement axis; not GHP physics under any "
                     "branch; no phi literal in code (derived only).")


def write_outputs(st: dict, cells: list, branches: dict) -> None:
    results = {
        "test_id": "SILVER-OPT-SCALE-v1",
        "prereg": "experiments/SILVER_OPT_SCALE_PREREG_v1.md",
        "pipeline_reused_unmodified": "experiments/silver_opt_geo_pipeline.py",
        "wrapper": "experiments/silver_opt_scale_results/run_scale.py",
        "substrate": {
            "module": "experiments/ghp_golden_heal_v2_probe.py (GH-RECOV "
                      "family) — placement, signal, recovery score, tear "
                      "damage verbatim via silver_opt_geo_pipeline",
            "alphas_pinned_in_substrate": {
                "golden": ghv2.ALPHA_GOLDEN, "silver": ghv2.ALPHA_SILVER,
                "bronze": ghv2.ALPHA_BRONZE},
            "frozen": {"sigma": ghv2.SIGMA, "rcond": ghv2.RCOND,
                       "damage_grid": list(ghv2.DAMAGE_GRID),
                       "critical_band": list(ghv2.CRITICAL_BAND)}},
        "config": {"sizes_n_k": [list(s) for s in SCALE_SIZES],
                   "n_over_2k": 4,
                   "seeds": [SCALE_SEEDS[0], SCALE_SEEDS[-1]],
                   "n_seeds": len(SCALE_SEEDS),
                   "geometries": list(SCALE_GEOMETRIES),
                   "arms": list(SCALE_ARMS),
                   "margin": MARGIN, "n_boot": geo.N_BOOT,
                   "bootstrap_seed": geo.BOOT_SEED},
        "self_test": st,
        "cells": cells,
        "branches": branches,
        "no_claim_verbatim": NO_CLAIM_VERBATIM,
    }
    (OUTDIR / "results.json").write_text(json.dumps(results, indent=1))

    lines = ["# SILVER-OPT-SCALE v1 — sweep summary\n",
             "Contract: `experiments/SILVER_OPT_SCALE_PREREG_v1.md` (signed "
             "2026-08-01). Runner: `experiments/silver_opt_scale_results/"
             "run_scale.py` wrapping `experiments/silver_opt_geo_pipeline.py` "
             "UNMODIFIED. Deterministic; seeds "
             f"{SCALE_SEEDS[0]}-{SCALE_SEEDS[-1]}; N/2K = 4 at every size.\n",
             "## The deliverable — Delta_sg(tear) die-off curve\n",
             "| n | golden med CB | silver med CB | D_sg (med) | 95% CI | "
             "CI excl 0 (+)? |",
             "|---|---|---|---|---|---|"]
    tear = sorted((c for c in cells if c["geometry"] == "adversarial_tear"),
                  key=lambda c: c["size"])
    for c in tear:
        m = c["median_CB"]
        lines.append(
            f"| {c['size']} | {m['golden']:.4f} | {m['silver']:.4f} | "
            f"{c['delta_sg_median']:+.4f} | "
            f"[{c['ci_sg'][0]:+.4f}, {c['ci_sg'][1]:+.4f}] | "
            f"{'YES' if c['ci_sg'][0] > 0 else 'no'} |")
    lines.append("\n## All cells (both geometries)\n")
    lines.append("| size | geometry | golden | silver | bronze | gold-shuf | "
                 "silv-shuf | D_sg (med) | 95% CI |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for c in sorted(cells, key=lambda c: (c["geometry"], c["size"])):
        m = c["median_CB"]
        lines.append(
            f"| {c['size']} | {c['geometry']} | {m['golden']:.4f} | "
            f"{m['silver']:.4f} | {m['bronze']:.4f} | "
            f"{m['golden_shuffled']:.4f} | {m['silver_shuffled']:.4f} | "
            f"{c['delta_sg_median']:+.4f} | "
            f"[{c['ci_sg'][0]:+.4f}, {c['ci_sg'][1]:+.4f}] |")
    lines.append("\n## Branch evaluation (mechanical)\n")
    lines.append("```json\n" + json.dumps(branches, indent=2) + "\n```\n")
    lines.append("## No-claims (verbatim)\n\n" + NO_CLAIM_VERBATIM + "\n")
    (OUTDIR / "summary.md").write_text("\n".join(lines))

    v = branches["verdict"]
    curve = " -> ".join(
        f"{p['n']}:{p['delta_sg_median']:+.3f}" for p in branches["tear_curve"])
    (OUTDIR / "VERDICT.md").write_text(
        "# SILVER-OPT-SCALE v1 — verdict\n\n"
        f"**{v}**"
        + (f" — crossover scale n* = {branches['n_star']}\n\n"
           if branches["n_star"] is not None else "\n\n")
        + f"Delta_sg(tear) curve: {curve}\n\n"
        "Mechanical evaluation of the locked branch criteria (see "
        "`summary.md` and `results.json`; the operationalization was "
        "declared in the committed runner before the sweep ran).\n\n"
        + NO_CLAIM_VERBATIM + "\n")
    print(f"[SILVER-OPT-SCALE] verdict = {v}  n* = {branches['n_star']}",
          flush=True)


# ---------------- main ----------------
def main() -> None:
    ap = argparse.ArgumentParser(description="SILVER-OPT-SCALE v1 runner")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    if not args.selftest and not args.run:
        ap.print_help()
        print("\nNothing executed: pass --selftest or --run. The full sweep "
              "is a signed one-shot; do not run it casually.")
        return

    st = run_audits_and_selftests()
    print("[SILVER-OPT-SCALE] audits + self-tests:")
    print(json.dumps(st, indent=2), flush=True)
    if not args.run:
        return

    records = run_sweep(args.workers)
    expected = len(SCALE_SIZES) * len(SCALE_ARMS) * len(SCALE_SEEDS)
    assert len(records) == expected, (len(records), expected)
    cells = geo.analyze(records)             # geo verbatim, injected globals
    branches = scale_branch(cells)
    write_outputs(st, cells, branches)


if __name__ == "__main__":
    main()
