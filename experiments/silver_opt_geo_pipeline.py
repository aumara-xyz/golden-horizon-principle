#!/usr/bin/env python3
"""
SILVER-OPT-GEO v1 pipeline — placement-geometry test of the silver anomaly,
run on the ORIGINAL GH-RECOV substrate.

Contract: experiments/SILVER_OPT_GEO_PREREG_v1.md (SIGNED 2026-08-01; lock
protocol as the ledger records). This file is ADDITIVE ONLY; no signed contract
and no pinned pipeline is touched.

Lane: constant/placement-axis anomaly characterization. Explicitly
GHP-independent (prereg section 3 / M-006: no structural reading exists; no
branch of this test is GHP physics evidence).

--------------------------------------------------------------------------------
SUBSTRATE — REUSED VERBATIM, NOT REWRITTEN (the heart of this build)

The prereg pins the archived GH-RECOV probe (ghp_golden_heal_probe.py family,
commit 8a3c6ead) as the code substrate. The family member that carries the
critical band and the adversarial tear — the original home of the ~5-sigma
silver line — is experiments/ghp_golden_heal_v2_probe.py. This pipeline IMPORTS
that module (`ghv2`) and calls its functions unchanged:

  placement mechanism (verbatim):
    ghv2.rotation_raw          — low-discrepancy orbit p_i = frac(i*alpha)
    ghv2.snap_to_slots         — grid snapping, forward collision resolution
    ghv2.arm_slots             — arm dispatch (golden/silver/bronze/random_positions)
  signal + recovery score (verbatim, unmodified):
    ghv2.grid_design_matrix    — cos/sin band design over the N uniform slots
    ghv2.build_signal_coeffs   — 2K-dim L2-normalized coefficient draw
    ghv2.recover_and_score     — lstsq recovery score 1 - ||chat-c||/||c||
    ghv2.critical_band_mean    — CB, the original probe's PRIMARY metric
    ghv2.aur_trapz             — AUR, the original probe's secondary metric
  damage machinery (verbatim):
    ghv2.block_start           — seeded contiguous-block start (mode 1)
    ghv2.random_erase_mask     — seeded uniform-random erasure (mode 3)
    ghv2.DAMAGE_GRID / CRITICAL_BAND / CB_IDX / SIGMA / RCOND — frozen config
  and the exhaustive adversarial-tear scan (mode 2) is reproduced line-for-line
  from ghv2.run_arm_seed's mode-2 block (min of clipped recovery over all N
  wrap-around survivor windows) — same a_ext/y_ext double-stack slicing.

From the pinned SILVER-OPT v1 pipeline (experiments/silver_opt_pipeline.py,
`sopt`), also reused verbatim:
    sopt.damage_mask("periodic_stride", ...) — the stride rule where v1 found a
        golden-favored reversal (seeded phase, exact erased count)
    sopt.bootstrap_ci_median_diff — paired-seed 95% bootstrap CI on a median
        contrast (10,000 resamples), plus sopt.N_BOOT and sopt.MARGIN (0.02)

The substrate module is parameterized by its module globals (N, K, TWO_K,
A_GRID). The size-up run sets those globals and rebuilds A_GRID by calling the
substrate's own grid_design_matrix(); every reused function then executes its
original, byte-identical code at the new size. Nothing is reimplemented.

--------------------------------------------------------------------------------
DESIGN (prereg section 1)

Arms (6):
  golden, silver, bronze      — placement rotations, via ghv2.arm_slots
  uniform_random_placement    — ghv2.arm_slots("random_positions")
  golden_shuffled, silver_shuffled — TRIPWIRES: exactly the parent arm's
      index->slot assignment, permuted across sample indices per seed (same
      offsets, permuted positions). Multiset equality is asserted per seed.
      Damage acts on sample indices, so the permutation destroys the sequential
      low-discrepancy structure while keeping the identical point set.

Damage set — the original probe's, INCLUDING its critical band and adversarial
tear, plus the two SILVER-OPT v1 reversal geometries. Four geometry classes,
all verdict-bearing (prereg G-branches count "of 4 geometry classes"):
  contiguous_burst  — ghv2 mode 1: seeded contiguous wrap-around block
                      (identical shape to SILVER-OPT v1's contiguous_burst,
                      where v1 found a golden-favored reversal at low damage)
  adversarial_tear  — ghv2 mode 2: exhaustive worst contiguous block
                      (the GH-RECOV stressor; original home of the silver line)
  uniform_random    — ghv2 mode 3: seeded uniform-random erasure
  periodic_stride   — sopt stride rule (v1's high-damage golden reversal),
                      seeded phase per (seed, damage index)
Damage fractions: the original probe's frozen DAMAGE_GRID (0.60..0.90) with its
CRITICAL_BAND (0.75, 0.80, 0.85) intact.

Sizes: the original probe's (N=256, K=32) plus one size up (N=512, K=64) —
derived by doubling both, which preserves N/2K = 4 and the regime arithmetic
(survivors == 2K exactly at d=0.75 at both sizes; the critical band stays
critical). No new constant enters.

Seeds: 4000..4099 (100), identical across cells.

Metric: the original probe's recovery score, unmodified — per damage point
ghv2.recover_and_score, clipped to [0,1] exactly as the original does; per-cell
scalar = ghv2.critical_band_mean (CB), the original probe's primary metric.
AUR and the full per-d curves are recorded as descriptive diagnostics.

--------------------------------------------------------------------------------
OPERATIONALIZATION DECLARED BEFORE THE RUN (the prereg leaves the per-class
aggregation and the contrast estimator unspecified; declared here, in the
committed pipeline, before any sweep executes):
  - Per cell (size, geometry): per-seed CB per arm over the 100 seeds.
  - Contrast Delta_sg = median(silver CB) - median(golden CB), with a 95%
    paired bootstrap CI via sopt.bootstrap_ci_median_diff (reused verbatim);
    the mean contrast is computed and reported as sensitivity only.
  - G1 cell-qualification: Delta_sg > +MARGIN (0.02) AND CI low > 0. A geometry
    CLASS qualifies iff both sizes qualify. G1 iff >= 3 of 4 classes qualify.
  - G2 cell-qualification: Delta_sg < -MARGIN AND CI high < 0 (golden >= silver
    beyond the margin). Class rule as above; G2 iff >= 2 of 4 classes qualify.
  - G0: max pairwise |median CB difference| among {golden, silver, bronze}
    <= MARGIN in EVERY cell (both sizes, all four geometries).
  - Precedence G1 -> G0 -> G2 -> UNRESOLVED (mirrors SILVER-OPT v1's H1 -> H0
    -> H2 order); all three flags are recorded so any overlap is visible.
  - Tripwire contrasts (parent minus shuffled, per cell) are descriptive
    diagnostics only; no branch reads them.

NUMEROLOGY GUARD (hard law): no phi-family decimal literal appears ANYWHERE in
this file — not in the channel, not in the recovery, not in the scorer. The arm
rotation angles live only in the pinned substrate module and are consumed by
reference. A runtime AST audit of THIS file asserts no numeric literal within
1e-4 of any arm constant (phi, 1/phi, sqrt5, sqrt2-1, bronze fractional part);
the substrate's own audit (ghv2.audit_phi_free) is run once at its baseline
configuration before any size override. Derived diagnostics (the substrate's
pinned alphas, echoed into the config block of the results) flow from the
substrate module, never from literals here.

NO-CLAIMS (prereg section 3, verbatim obligations): constant/placement axis
only; M-006 forbids any structural reading (no silver fusion category exists);
not GHP evidence under any branch; T-111, T-112 and KAM are separately governed
and untouched by this result.

Runtime: python3 + numpy, deterministic, offline, single-core. The adversarial
tear is an exhaustive N-start scan per (arm, seed, damage): ~0.9M lstsq solves
at N=256 plus ~1.8M at N=512 for the full sweep — hours of single-core laptop
time. The sweep checkpoints per (size, arm, seed) to records.jsonl and resumes.
Outputs: experiments/silver_opt_geo_results/{results.json, summary.md, VERDICT.md}

Usage:
  python3 silver_opt_geo_pipeline.py --selftest   # self-tests only (no sweep)
  python3 silver_opt_geo_pipeline.py --run        # full preregistered sweep
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ghp_golden_heal_v2_probe as ghv2   # GH-RECOV substrate (commit 8a3c6ead family)
import silver_opt_pipeline as sopt        # SILVER-OPT v1 pinned pipeline

OUTDIR = HERE / "silver_opt_geo_results"
CKPT = OUTDIR / "records.jsonl"

# ---------------- locked configuration ----------------
BASE_N, BASE_K = ghv2.N, ghv2.K                 # (256, 32) — captured at import,
SIZES = ((BASE_N, BASE_K), (2 * BASE_N, 2 * BASE_K))  # plus one size up (doubled)
SEEDS = tuple(range(4000, 4100))                # 100 seeds, identical across cells
GEOMETRIES = ("contiguous_burst", "adversarial_tear",
              "uniform_random", "periodic_stride")
ARMS = ("golden", "silver", "bronze", "uniform_random_placement",
        "golden_shuffled", "silver_shuffled")
NOBLE_ARMS = ("golden", "silver", "bronze")
SHUFFLE_PARENT = {"golden_shuffled": "golden", "silver_shuffled": "silver"}
ARM_TO_SUBSTRATE = {"golden": "golden", "silver": "silver", "bronze": "bronze",
                    "uniform_random_placement": "random_positions"}

# Deterministic substream tags for NEW substreams only (style of ghv2's tags;
# transparently arbitrary, phi-free). Existing substreams keep ghv2's tags.
TAG_SHUFFLE = 707       # tripwire permutation stream
TAG_STRIDE = 808        # periodic-stride phase stream

MARGIN = sopt.MARGIN            # 0.02 — reused, not re-typed
N_BOOT = sopt.N_BOOT            # 10,000 paired resamples
BOOT_SEED = sopt.BOOT_SEED      # date-tag bootstrap seed; no arm constant

G1_CLASSES_REQUIRED = 3         # of 4 geometry classes (prereg G1)
G2_CLASSES_REQUIRED = 2         # of 4 geometry classes (prereg G2)


# ---------------- substrate size control ----------------
class substrate_size:
    """
    Run the substrate at (n, k) by setting ITS module globals and rebuilding
    A_GRID with ITS OWN grid_design_matrix(). The reused functions execute
    byte-identical code; nothing is reimplemented. Globals are restored on exit.
    """

    def __init__(self, n: int, k: int):
        self.n, self.k = n, k

    def __enter__(self):
        self.saved = (ghv2.N, ghv2.K, ghv2.TWO_K, ghv2.A_GRID)
        ghv2.N, ghv2.K, ghv2.TWO_K = self.n, self.k, 2 * self.k
        ghv2.A_GRID = ghv2.grid_design_matrix()
        return self

    def __exit__(self, *exc):
        ghv2.N, ghv2.K, ghv2.TWO_K, ghv2.A_GRID = self.saved
        return False


# ---------------- placement (substrate verbatim + tripwires) ----------------
def placement_slots(arm: str, seed: int):
    """
    index->slot assignment for one arm at the current substrate size.
    Parents come from ghv2.arm_slots unchanged. Shuffled tripwires permute the
    PARENT'S assignment across sample indices (same offsets, permuted
    positions); the slot multiset is identical by construction and asserted.
    """
    if arm in SHUFFLE_PARENT:
        parent = SHUFFLE_PARENT[arm]
        parent_slots, meta = ghv2.arm_slots(ARM_TO_SUBSTRATE[parent], seed)
        rng = np.random.default_rng([seed, TAG_SHUFFLE, ARMS.index(arm)])
        slots = parent_slots[rng.permutation(ghv2.N)]
        assert np.array_equal(np.sort(slots), np.sort(parent_slots)), \
            f"tripwire multiset mismatch: {arm} seed={seed}"
        return slots, {"alpha": meta["alpha"], "collisions": meta["collisions"],
                       "shuffled_parent": parent}
    slots, meta = ghv2.arm_slots(ARM_TO_SUBSTRATE[arm], seed)
    return slots, {"alpha": meta["alpha"], "collisions": meta["collisions"],
                   "shuffled_parent": None}


# ---------------- per-(arm, seed) cell at current substrate size ----------------
def run_arm_seed_geo(arm: str, seed: int, coeffs: np.ndarray,
                     eta: np.ndarray, geometries=GEOMETRIES) -> dict:
    """
    All requested damage geometries for one (arm, seed) at the current
    substrate size. Damage construction and scoring follow ghv2.run_arm_seed
    exactly (same double-stack wrap slicing, same clipping, same scored
    quantities); periodic_stride adds sopt's stride mask, scored by the same
    unmodified ghv2.recover_and_score.
    """
    n = ghv2.N
    slots, meta = placement_slots(arm, seed)
    a_arm = ghv2.A_GRID[slots]                    # (N, 2K) rows, sample-index order
    y_full = a_arm @ coeffs + ghv2.SIGMA * eta    # identical noise-by-index per arm
    a_ext = np.vstack([a_arm, a_arm])             # wrap-around slicing helper
    y_ext = np.concatenate([y_full, y_full])

    per_geom = {g: {"raw": [], "clipped": []} for g in geometries}

    for d_idx, d in enumerate(ghv2.DAMAGE_GRID):
        n_erase = int(round(d * n))
        n_surv = n - n_erase

        if "contiguous_burst" in geometries:
            # ghv2 mode 1 verbatim: seeded start, wrap-around block
            b = ghv2.block_start(seed, d_idx)
            r = (b + n_erase) % n                 # survivors = run r .. r+n_surv-1
            raw, _ = ghv2.recover_and_score(
                a_ext[r:r + n_surv], y_ext[r:r + n_surv], coeffs)
            per_geom["contiguous_burst"]["raw"].append(float(raw))
            per_geom["contiguous_burst"]["clipped"].append(
                float(min(max(raw, 0.0), 1.0)))

        if "adversarial_tear" in geometries:
            # ghv2 mode 2 verbatim: exhaustive min of clipped recovery over all
            # n wrap-around survivor windows (scored quantity is the clipped min)
            worst_clip = 2.0
            for run in range(n):
                raw_a, _ = ghv2.recover_and_score(
                    a_ext[run:run + n_surv], y_ext[run:run + n_surv], coeffs)
                clip_a = min(max(raw_a, 0.0), 1.0)
                if clip_a < worst_clip:
                    worst_clip = clip_a
            per_geom["adversarial_tear"]["raw"].append(float(worst_clip))
            per_geom["adversarial_tear"]["clipped"].append(float(worst_clip))

        if "uniform_random" in geometries:
            # ghv2 mode 3 verbatim: seeded uniform-random erasure
            surv = ghv2.random_erase_mask(seed, d_idx, n_erase)
            raw_r, _ = ghv2.recover_and_score(a_arm[surv], y_full[surv], coeffs)
            per_geom["uniform_random"]["raw"].append(float(raw_r))
            per_geom["uniform_random"]["clipped"].append(
                float(min(max(raw_r, 0.0), 1.0)))

        if "periodic_stride" in geometries:
            # sopt stride rule verbatim (seeded phase, exact erased count),
            # scored by the same unmodified substrate recovery score
            rng = np.random.default_rng([seed, TAG_STRIDE, d_idx])
            mask = sopt.damage_mask("periodic_stride", n, n_erase, rng, None)
            raw_s, _ = ghv2.recover_and_score(a_arm[~mask], y_full[~mask], coeffs)
            per_geom["periodic_stride"]["raw"].append(float(raw_s))
            per_geom["periodic_stride"]["clipped"].append(
                float(min(max(raw_s, 0.0), 1.0)))

    out = {"size_n": n, "size_k": ghv2.K, "arm": arm, "seed": seed,
           "alpha": meta["alpha"], "collisions": meta["collisions"],
           "shuffled_parent": meta["shuffled_parent"]}
    for g in geometries:
        clip = np.asarray(per_geom[g]["clipped"])
        out[g] = {"recoveries_raw": per_geom[g]["raw"],
                  "recoveries_clipped": [float(x) for x in clip],
                  "CB": ghv2.critical_band_mean(clip),
                  "AUR": ghv2.aur_trapz(clip)}
    return out


# ---------------- numerology audit of THIS file ----------------
def audit_new_module_numerology() -> dict:
    """
    AST scan of this pipeline's source: no numeric literal may fall within 1e-4
    of any arm constant. The forbidden values are DERIVED here (integer
    arithmetic and square roots), never typed as decimal literals.
    """
    phi = (1.0 + 5.0 ** 0.5) / 2.0
    forbidden = [phi, phi - 1.0, 5.0 ** 0.5,
                 2.0 ** 0.5 - 1.0,                    # silver rotation frac
                 (3.0 + 13.0 ** 0.5) / 2.0 - 3.0]     # bronze rotation frac
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
    return {"status": "PASSED", "numeric_literals_checked": n_checked,
            "forbidden_values_derived": [float(v) for v in forbidden]}


# ---------------- self-tests (run before any sweep) ----------------
def self_test() -> dict:
    report = {}
    t0 = time.time()

    # 0. numerology guards: substrate audit at its baseline config (before any
    #    size override), plus the AST audit of this new file.
    report["substrate_audit_baseline"] = ghv2.audit_phi_free()["status"]
    new_audit = audit_new_module_numerology()
    report["new_module_audit"] = (
        f"{new_audit['status']} ({new_audit['numeric_literals_checked']} "
        f"numeric literals checked)")

    # 1. zero damage gives the perfect score in every arm (both sizes).
    #    The channel identity check is noiseless (the substrate's frozen
    #    SIGMA=1e-3 observation noise makes the noisy zero-damage score
    #    ~1-O(SIGMA), reported below as disclosure, not asserted as 1).
    zd = {}
    for (n, k) in SIZES:
        with substrate_size(n, k):
            for seed in (SEEDS[0], SEEDS[len(SEEDS) // 2], SEEDS[-1]):
                coeffs = ghv2.build_signal_coeffs(seed)
                eta = np.random.default_rng(
                    [seed, ghv2.TAG_NOISE]).standard_normal(ghv2.N)
                for arm in ARMS:
                    slots, _ = placement_slots(arm, seed)
                    a_arm = ghv2.A_GRID[slots]
                    y_clean = a_arm @ coeffs
                    rec, ud = ghv2.recover_and_score(a_arm, y_clean, coeffs)
                    assert not ud, f"zero damage underdetermined: {arm} n={n}"
                    assert rec > 1.0 - 1e-9, (
                        f"zero-damage score not perfect: {arm} n={n} "
                        f"seed={seed} rec={rec}")
                    rec_noisy, _ = ghv2.recover_and_score(
                        a_arm, y_clean + ghv2.SIGMA * eta, coeffs)
                    key = f"n={n}"
                    zd.setdefault(key, {"min_clean": 1.0, "min_noisy": 1.0})
                    zd[key]["min_clean"] = min(zd[key]["min_clean"], float(rec))
                    zd[key]["min_noisy"] = min(zd[key]["min_noisy"],
                                               float(rec_noisy))
    report["zero_damage"] = {
        k: (f"PASS — perfect noiseless score every arm "
            f"(min {v['min_clean']:.12f}); with the substrate's frozen "
            f"observation noise, min {v['min_noisy']:.6f} (disclosure)")
        for k, v in zd.items()}

    # 2. shuffled arms use identical offset multisets to their parents, and are
    #    genuinely permuted; every arm's slot set is the full slot range
    #    (substrate snapping property, disclosed).
    for (n, k) in SIZES:
        with substrate_size(n, k):
            for seed in (SEEDS[0], SEEDS[len(SEEDS) // 2], SEEDS[-1]):
                for arm in ARMS:
                    slots, _ = placement_slots(arm, seed)
                    assert np.array_equal(np.sort(slots), np.arange(ghv2.N)), \
                        f"slot set not full range: {arm} n={n}"
                    if arm in SHUFFLE_PARENT:
                        pslots, _ = placement_slots(SHUFFLE_PARENT[arm], seed)
                        assert np.array_equal(np.sort(slots), np.sort(pslots)), \
                            f"tripwire multiset mismatch: {arm} n={n} seed={seed}"
                        assert not np.array_equal(slots, pslots), \
                            f"tripwire not permuted: {arm} n={n} seed={seed}"
    report["tripwire_multisets"] = (
        "PASS — golden_shuffled/silver_shuffled slot multisets identical to "
        "parents and genuinely permuted (3 seeds x both sizes); every arm "
        "occupies the full slot range after substrate snapping (disclosed)")

    # 3. erased-count exactness for every geometry, damage point, both sizes.
    for (n, k) in SIZES:
        with substrate_size(n, k):
            for d_idx, d in enumerate(ghv2.DAMAGE_GRID):
                n_erase = int(round(d * ghv2.N))
                surv = ghv2.random_erase_mask(SEEDS[0], d_idx, n_erase)
                assert int((~surv).sum()) == n_erase
                rng = np.random.default_rng([SEEDS[0], TAG_STRIDE, d_idx])
                mask = sopt.damage_mask("periodic_stride", ghv2.N, n_erase,
                                        rng, None)
                assert int(mask.sum()) == n_erase
                # burst/tear survivor windows are slice-exact by construction
                assert ghv2.N - n_erase == len(range(ghv2.N - n_erase))
    report["erase_counts"] = ("PASS — exact erased counts for uniform_random "
                              "and periodic_stride at every damage point, both "
                              "sizes (burst/tear windows slice-exact)")

    # 4. deterministic under fixed seed: two independent invocations of the
    #    full per-cell pipeline (all four geometries, adversarial included)
    #    must agree bit-for-bit, at both sizes.
    for (n, k) in SIZES:
        with substrate_size(n, k):
            for arm in ("golden", "silver_shuffled"):
                coeffs = ghv2.build_signal_coeffs(SEEDS[0])
                eta = np.random.default_rng(
                    [SEEDS[0], ghv2.TAG_NOISE]).standard_normal(ghv2.N)
                r1 = run_arm_seed_geo(arm, SEEDS[0], coeffs, eta)
                r2 = run_arm_seed_geo(arm, SEEDS[0], coeffs, eta)
                assert json.dumps(r1, sort_keys=True) == \
                    json.dumps(r2, sort_keys=True), \
                    f"nondeterministic: {arm} n={n}"
    report["determinism"] = ("PASS — bit-identical repeat of the full cell "
                             "(all 4 geometries incl. exhaustive adversarial "
                             "tear) for golden and silver_shuffled at both sizes")

    report["elapsed_seconds"] = round(time.time() - t0, 1)
    return report


# ---------------- sweep (checkpointed, resumable) ----------------
def run_sweep() -> list:
    OUTDIR.mkdir(exist_ok=True)
    done, records = set(), []
    if CKPT.exists():
        for line in CKPT.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            records.append(rec)
            done.add((rec["size_n"], rec["arm"], rec["seed"]))
        print(f"[SILVER-OPT-GEO] resuming: {len(records)} cells already done")
    t0 = time.time()
    with open(CKPT, "a") as fh:
        for (n, k) in SIZES:
            with substrate_size(n, k):
                for seed in SEEDS:
                    coeffs = ghv2.build_signal_coeffs(seed)
                    eta = np.random.default_rng(
                        [seed, ghv2.TAG_NOISE]).standard_normal(ghv2.N)
                    for arm in ARMS:
                        if (n, arm, seed) in done:
                            continue
                        rec = run_arm_seed_geo(arm, seed, coeffs, eta)
                        fh.write(json.dumps(rec) + "\n")
                        fh.flush()
                        records.append(rec)
                    print(f"[SILVER-OPT-GEO] n={n} seed={seed} done "
                          f"({time.time() - t0:8.1f}s elapsed)")
    return records


# ---------------- statistics + branches ----------------
def analyze(records: list) -> list:
    """Per (size, geometry) cell: 100-seed CB arrays per arm + contrasts."""
    cb = {}
    for rec in records:
        for g in GEOMETRIES:
            cb.setdefault((rec["size_n"], g), {}).setdefault(
                rec["arm"], {})[rec["seed"]] = rec[g]["CB"]
    rng = np.random.default_rng(BOOT_SEED)
    cells = []
    for (n, _k) in SIZES:
        for g in GEOMETRIES:
            arm_cb = {arm: np.array([cb[(n, g)][arm][s] for s in SEEDS])
                      for arm in ARMS}
            med = {arm: float(np.median(arm_cb[arm])) for arm in ARMS}
            mean = {arm: float(np.mean(arm_cb[arm])) for arm in ARMS}
            d_sg = med["silver"] - med["golden"]
            ci_sg = sopt.bootstrap_ci_median_diff(arm_cb["silver"],
                                                  arm_cb["golden"], rng)
            noble_spread = max(abs(med[x] - med[y])
                               for x in NOBLE_ARMS for y in NOBLE_ARMS)
            trip = {a: med[SHUFFLE_PARENT[a]] - med[a]
                    for a in SHUFFLE_PARENT}     # parent minus shuffled
            cells.append({
                "size": n, "geometry": g,
                "median_CB": med, "mean_CB_sensitivity": mean,
                "delta_sg_median": d_sg, "ci_sg": list(ci_sg),
                "delta_sg_mean_sensitivity": mean["silver"] - mean["golden"],
                "silver_advantage_G1": bool(d_sg > MARGIN and ci_sg[0] > 0.0),
                "golden_advantage_G2": bool(d_sg < -MARGIN and ci_sg[1] < 0.0),
                "noble_max_pairwise_gap": noble_spread,
                "noble_within_margin": bool(noble_spread <= MARGIN),
                "tripwire_parent_minus_shuffled_median_CB": trip,
            })
    return cells


def branch_verdict(cells: list) -> dict:
    def cell(n, g):
        return next(c for c in cells
                    if c["size"] == n and c["geometry"] == g)

    sizes_n = [n for (n, _k) in SIZES]
    g1_class = {g: all(cell(n, g)["silver_advantage_G1"] for n in sizes_n)
                for g in GEOMETRIES}
    g2_class = {g: all(cell(n, g)["golden_advantage_G2"] for n in sizes_n)
                for g in GEOMETRIES}
    g1 = sum(g1_class.values()) >= G1_CLASSES_REQUIRED
    g2 = sum(g2_class.values()) >= G2_CLASSES_REQUIRED
    g0 = all(c["noble_within_margin"] for c in cells)

    if g1:
        verdict = "G1_SILVER_GEOMETRY_REAL"
    elif g0:
        verdict = "G0_DISSOLVED"
    elif g2:
        verdict = "G2_REVERSED_ARTIFACT"
    else:
        verdict = "UNRESOLVED"
    return {"verdict": verdict,
            "g1_silver_geometry_real": g1,
            "g1_classes_qualifying": [g for g, v in g1_class.items() if v],
            "g0_dissolved_noble_plateau": g0,
            "g2_reversed_artifact": g2,
            "g2_classes_qualifying": [g for g, v in g2_class.items() if v],
            "class_rule": ("class qualifies iff its cell criterion holds at "
                           "BOTH sizes; G1 needs >=3/4 classes, G2 >=2/4; "
                           "precedence G1 -> G0 -> G2 -> UNRESOLVED "
                           "(declared pre-run in this pipeline)")}


# ---------------- reporting ----------------
NO_CLAIM_VERBATIM = (
    "Constant/placement axis only (M-006 forbids any structural reading: no "
    "silver fusion category exists). Not GHP evidence under any branch. The "
    "four-instrument line's other three instruments (T-111, T-112, KAM) are "
    "separately governed and untouched by this result."
)


def write_outputs(st: dict, cells: list, branches: dict) -> None:
    results = {
        "test_id": "SILVER-OPT-GEO-v1",
        "prereg": "experiments/SILVER_OPT_GEO_PREREG_v1.md",
        "substrate": {
            "module": "experiments/ghp_golden_heal_v2_probe.py "
                      "(GH-RECOV family, commit 8a3c6ead) — placement, signal, "
                      "recovery score, burst/tear/random damage reused verbatim",
            "stride_and_stats": "experiments/silver_opt_pipeline.py — "
                                "periodic_stride rule and paired bootstrap CI "
                                "reused verbatim",
            "alphas_pinned_in_substrate": {
                "golden": ghv2.ALPHA_GOLDEN, "silver": ghv2.ALPHA_SILVER,
                "bronze": ghv2.ALPHA_BRONZE},
            "frozen": {"sigma": ghv2.SIGMA, "rcond": ghv2.RCOND,
                       "damage_grid": list(ghv2.DAMAGE_GRID),
                       "critical_band": list(ghv2.CRITICAL_BAND)},
        },
        "config": {"sizes_n_k": [list(s) for s in SIZES],
                   "seeds": [SEEDS[0], SEEDS[-1]],
                   "n_seeds": len(SEEDS),
                   "geometries": list(GEOMETRIES), "arms": list(ARMS),
                   "shuffle_parents": SHUFFLE_PARENT,
                   "margin": MARGIN, "n_boot": N_BOOT,
                   "bootstrap_seed": BOOT_SEED,
                   "substream_tags_new": {"shuffle": TAG_SHUFFLE,
                                          "stride_phase": TAG_STRIDE}},
        "self_test": st,
        "cells": cells,
        "branches": branches,
        "no_claim_verbatim": NO_CLAIM_VERBATIM,
    }
    (OUTDIR / "results.json").write_text(json.dumps(results, indent=1))

    lines = ["# SILVER-OPT-GEO v1 — sweep summary\n",
             "Contract: `experiments/SILVER_OPT_GEO_PREREG_v1.md` (signed "
             "2026-08-01). Pipeline: `experiments/silver_opt_geo_pipeline.py`. "
             "Substrate reused verbatim from "
             "`experiments/ghp_golden_heal_v2_probe.py` (GH-RECOV family) and "
             "`experiments/silver_opt_pipeline.py`. Deterministic; seeds "
             f"{SEEDS[0]}-{SEEDS[-1]}.\n",
             "## Per-cell medians (CB) and the silver-vs-golden contrast\n",
             "| size | geometry | golden | silver | bronze | unif-rand | "
             "gold-shuf | silv-shuf | D_sg (med) | 95% CI | G1? | G2? |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        m = c["median_CB"]
        lines.append(
            f"| {c['size']} | {c['geometry']} | {m['golden']:.4f} | "
            f"{m['silver']:.4f} | {m['bronze']:.4f} | "
            f"{m['uniform_random_placement']:.4f} | "
            f"{m['golden_shuffled']:.4f} | {m['silver_shuffled']:.4f} | "
            f"{c['delta_sg_median']:+.4f} | "
            f"[{c['ci_sg'][0]:+.4f}, {c['ci_sg'][1]:+.4f}] | "
            f"{'YES' if c['silver_advantage_G1'] else 'no'} | "
            f"{'YES' if c['golden_advantage_G2'] else 'no'} |")
    lines.append("\n## Branch evaluation (mechanical)\n")
    lines.append("```json\n" + json.dumps(branches, indent=2) + "\n```\n")
    lines.append("## No-claims (verbatim)\n\n" + NO_CLAIM_VERBATIM + "\n")
    (OUTDIR / "summary.md").write_text("\n".join(lines))

    v = branches["verdict"]
    (OUTDIR / "VERDICT.md").write_text(
        "# SILVER-OPT-GEO v1 — verdict\n\n"
        f"**{v}**\n\n"
        "Mechanical evaluation of the locked branch criteria "
        "(see `summary.md` and `results.json`; class rule and precedence were "
        "declared in the committed pipeline before the sweep ran).\n\n"
        + NO_CLAIM_VERBATIM + "\n")
    print(f"[SILVER-OPT-GEO] verdict = {v}")
    print(f"[SILVER-OPT-GEO] wrote {OUTDIR / 'results.json'}, summary.md, "
          f"VERDICT.md")


# ---------------- main ----------------
def main() -> None:
    ap = argparse.ArgumentParser(description="SILVER-OPT-GEO v1 pipeline")
    ap.add_argument("--selftest", action="store_true",
                    help="run self-tests only (no sweep)")
    ap.add_argument("--run", action="store_true",
                    help="run the full preregistered sweep")
    args = ap.parse_args()

    if not args.selftest and not args.run:
        ap.print_help()
        print("\nNothing executed: pass --selftest or --run. The full sweep is "
              "a signed one-shot; do not run it casually.")
        return

    st = self_test()
    print("[SILVER-OPT-GEO] self-tests:")
    print(json.dumps(st, indent=2))
    if not args.run:
        return

    records = run_sweep()
    expected = len(SIZES) * len(ARMS) * len(SEEDS)
    assert len(records) == expected, (len(records), expected)
    cells = analyze(records)
    branches = branch_verdict(cells)
    write_outputs(st, cells, branches)


if __name__ == "__main__":
    main()
