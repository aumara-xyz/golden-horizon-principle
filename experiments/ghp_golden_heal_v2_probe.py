#!/usr/bin/env python3
"""
GOLDEN-HEAL-v2 — coverage-stressed recoverability discriminator.
GHP ledger AH.4 Priority 1, contract 2 of 2 (FINAL contract on this mechanism).
Locked preregistration: experiments/GOLDEN_HEAL_PREREG_v2.md (date_locked 2026-07-03,
written after v1's audited run, before any v2 pipeline code executed).

This is a TOY least-squares recoverability probe, NOT physics evidence.

Forbidden-upgrade sentence (locked, prereg section 4):
  "GOLDEN-HEAL v2 is a toy least-squares recoverability probe in a
   coverage-stressed regime; no outcome here is physics evidence. Outcome B
   (the expected result) is a statement about low-discrepancy geometry, not
   about phi being physically privileged, and even Outcome A would be a
   numerical-linear-algebra fingerprint requiring independent replication
   before any ledger upgrade beyond 'toy anomaly.'"

--------------------------------------------------------------------------------
v1 CITATION (required in every v2 artifact; retro-tune guard, prereg section 4):
GOLDEN-HEAL-v1 (GOLDEN_HEAL_PREREG_v1.md + ghp_golden_heal_probe.py) returned
C_MECHANISM_NULL under its locked contract. THAT VERDICT STANDS and is not
reopened, softened, or superseded here. Its disclosed, verifier-confirmed
diagnosis: with N=512, K=16 (2K=32) and max damage 0.8, minimum survivors were
~102 >> 32, so least squares stayed heavily over-determined at every grid
point; all irrational/aperiodic arms tied at the recovery ceiling ~0.6996 with
~1e-5 differences (pure seed noise; random_irrational actually edged golden),
and the rational arms collapsed trivially (finite orbit -> rank-deficient
design). The coverage-stressed regime where three-distance geometry could
matter was NEVER entered. GH-B's descriptive negative (Fibonacci-convergent
approach to golden is MONOTONE, not the predicted odd/even oscillation) also
stands and is NOT rerun. It is FORBIDDEN to describe v2 as correcting or
overturning v1: v1 answered its own contract correctly.

v2 tests the SAME mechanism hypothesis (three-distance uniform coverage +
Hurwitz/KAM anti-resonance -> golden heals best) in the regime where it could
actually manifest: survivor counts comparable to and BELOW the
information-theoretic floor 2K, where the geometry of WHICH samples survive
decides solvability. Parameters derive from data-independent survivor-count
arithmetic (N*(1-d) vs 2K), locked before any v2 code ran.

REGIME-HUNT CLOSURE CLAUSE (locked): v2 is the ONE disclosed rerun in the
coverage-stressed regime. If v2 also returns C_MECHANISM_NULL the
recoverability-mechanism line is CLOSED at the ledger level; no preregistered
v3 on this hypothesis.

THREE PREREGISTERED OUTCOMES + WATCH (numeric thresholds locked in prereg
section 3; precedence A -> B -> C -> WATCH; all verdicts on the CB metric,
contiguous + adversarial modes only; random-erasure mode descriptive only).
The A pass-region EXCLUDES the silver tie BY CONSTRUCTION: a tie against
silver in either contiguous mode is at best Outcome B regardless of
rational/random comparisons; beating rational/random alone is textbook
low-discrepancy (Weyl / Koksma-Hlawka), never a phi claim.

NUMEROLOGY GUARD (enforced at runtime, prereg section 4): no phi / Fibonacci /
1.618 / sqrt5-derived constant anywhere except the pinned rotation-angle arm
definitions (rational_near = 8/13 is an ARM definition, not machinery). The
AST audit below walks the signal/damage/metric code paths and asserts no
phi-family identifier or phi-valued numeric literal appears. Seed list is
cleaned of phi-digit strings (v1 had 1618/6180/1123/5813; v2 uses 9001..9016).
--------------------------------------------------------------------------------
"""

from __future__ import annotations

import ast
import inspect
import json
import math
import re
import time
import warnings
from pathlib import Path

import numpy as np

# NumPy 2.0.2's SIMD matmul kernel on this macOS BLAS build emits spurious
# RuntimeWarnings even when results are finite and correct (verified in v1).
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*matmul.*")

try:
    _trapz = np.trapezoid  # type: ignore[attr-defined]
except AttributeError:  # pragma: no cover
    _trapz = np.trapz

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_golden_heal_v2_probe_outputs"

# ------------------------------------------------------------------ locked config
N = 256                  # sample slots on uniform index grid (prereg 1.1)
K = 32                   # signal bandwidth -> 2K = 64 unknowns (prereg 1.1)
TWO_K = 2 * K
SIGMA = 1e-3             # observation noise std (frozen, as v1)
RCOND = 1e-10            # lstsq rcond (frozen, as v1)
DAMAGE_GRID = (0.60, 0.70, 0.75, 0.80, 0.85, 0.90)      # frozen 6-point grid
CRITICAL_BAND = (0.75, 0.80, 0.85)                       # CB = mean over these d
CB_IDX = tuple(DAMAGE_GRID.index(d) for d in CRITICAL_BAND)
EXPECTED_SURVIVORS = (102, 77, 64, 51, 38, 26)           # prereg 1.3 table
SEEDS = tuple(range(9001, 9017))                         # 16 frozen seeds
MODES = ("contiguous", "adversarial", "random")
VERDICT_MODES = ("contiguous", "adversarial")            # mode 3 descriptive only

# Locked thresholds (prereg section 3 — immutable post-data).
WINS_REQUIRED_A = 12        # >=12/16 golden-over-silver seed wins (per mode)
SIGN_TEST_ALPHA = 0.05      # exact one-sided binomial threshold
B_MARGIN = 0.05             # champion-vs-floor mean CB margin for Outcome B
B_WINS_REQUIRED = 12        # champion-vs-floor seed wins for Outcome B
C_MARGIN = 0.05             # pooled golden - random_positions null margin

# Deterministic substream tags (transparently arbitrary, phi-free).
TAG_COEFF = 101
TAG_NOISE = 202
TAG_START = 303
TAG_SUBSET = 404
TAG_RANDIRR = 505
TAG_RANDPOS = 606

# Pinned rotation angles — the ONLY phi-dependence in this file (prereg 0.5).
ALPHA_GOLDEN = (1.0 + math.sqrt(5.0)) / 2.0 - 1.0     # frac(phi)        = 0.6180339887498949
ALPHA_SILVER = math.sqrt(2.0) - 1.0                   # frac(1+sqrt2)    = 0.4142135623730951
ALPHA_BRONZE = (3.0 + math.sqrt(13.0)) / 2.0 - 3.0    # frac((3+sqrt13)/2) = 0.3027756377319946
ALPHA_RAT_NEAR = 8.0 / 13.0                           # hardest near-golden rational (arm def)
ALPHA_RAT_RES = 1.0 / 2.0                             # maximally resonant rational

ARMS = (
    "golden",
    "silver",              # THE REIGNING CHAMPION (T-112 / v1 tie) — not a strawman
    "bronze",
    "rational_near",
    "rational_resonant",
    "random_irrational",
    "random_positions",
)


# ============================================================ phi-free machinery
# NOTHING in this block may reference phi/golden/silver/bronze/fibonacci/sqrt5
# or carry a phi-family numeric literal. The runtime AST audit enforces it.

def build_signal_coeffs(seed: int) -> np.ndarray:
    """2K-dim bandlimited coeff vector, N(0,1) then L2-normalized. phi-free."""
    rng = np.random.default_rng([seed, TAG_COEFF])
    coeffs = rng.standard_normal(TWO_K)
    coeffs /= np.linalg.norm(coeffs)
    return coeffs


def grid_design_matrix() -> np.ndarray:
    """cos/sin design over band k=1..K at the N uniform grid slots. phi-free."""
    slots = np.arange(N) / N
    ks = np.arange(1, K + 1)
    ang = 2.0 * np.pi * np.outer(slots, ks)          # (N, K)
    return np.hstack([np.cos(ang), np.sin(ang)])     # (N, 2K)


def snap_to_slots(raw_positions: np.ndarray) -> tuple[np.ndarray, int]:
    """
    Map continuous positions in [0,1) to the nearest grid slot; collisions
    resolved next-free-slot (forward, wrap-around). Deterministic. Returns
    (slot index per sample index, collision count). phi-free.
    """
    taken = np.zeros(N, dtype=bool)
    slots = np.empty(N, dtype=np.int64)
    n_collisions = 0
    for i, p in enumerate(raw_positions):
        j = int(round(float(p) * N)) % N
        if taken[j]:
            n_collisions += 1
            while taken[j]:
                j = (j + 1) % N
        taken[j] = True
        slots[i] = j
    return slots, n_collisions


def recover_and_score(a_rows: np.ndarray, y_rows: np.ndarray,
                      coeffs: np.ndarray) -> tuple[float, bool]:
    """
    Least-squares reconstruction (numpy lstsq, rcond frozen; minimum-norm in the
    under-determined regime). Recovery = 1 - ||chat - coeffs|| / ||coeffs||
    (== function-space L2 by orthogonality of the cos/sin band on [0,1)).
    Returns (raw recovery, underdetermined flag). phi-free.
    """
    chat, *_ = np.linalg.lstsq(a_rows, y_rows, rcond=RCOND)
    err = np.linalg.norm(chat - coeffs) / np.linalg.norm(coeffs)
    return 1.0 - err, bool(a_rows.shape[0] < TWO_K)


def block_start(seed: int, d_idx: int) -> int:
    """Seeded contiguous-block start for mode 1; identical across arms. phi-free."""
    rng = np.random.default_rng([seed, TAG_START, d_idx])
    return int(rng.integers(0, N))


def random_erase_mask(seed: int, d_idx: int, n_erase: int) -> np.ndarray:
    """Seeded uniformly-random n_erase-subset for mode 3; identical across arms."""
    rng = np.random.default_rng([seed, TAG_SUBSET, d_idx])
    idx = rng.choice(N, size=n_erase, replace=False)
    surv = np.ones(N, dtype=bool)
    surv[idx] = False
    return surv


def critical_band_mean(rec_clipped: np.ndarray) -> float:
    """PRIMARY metric CB: mean clipped recovery over the critical band. phi-free."""
    return float(np.mean([rec_clipped[i] for i in CB_IDX]))


def aur_trapz(rec_clipped: np.ndarray) -> float:
    """SECONDARY metric AUR: trapezoid over the full damage grid. phi-free."""
    return float(_trapz(np.asarray(rec_clipped), np.asarray(DAMAGE_GRID)))


def one_sided_sign_p(wins: int, n: int) -> float:
    """Exact one-sided binomial P(X >= wins | n, 1/2). Ties already count against."""
    total = sum(math.comb(n, k) for k in range(wins, n + 1))
    return total / 2.0 ** n


# ============================================================ arm sample layouts

def rotation_raw(alpha: float) -> np.ndarray:
    """Low-discrepancy orbit p_i = frac(i*alpha), i=0..N-1."""
    return np.mod(np.arange(N) * alpha, 1.0)


def draw_random_irrational(seed: int) -> float:
    """
    Fresh alpha per seed, uniform on (0,1); rejected if within 1e-3 of any
    pinned alpha or a low-order rational p/q (q<=20). Any-irrationality control.
    """
    rng = np.random.default_rng([seed, TAG_RANDIRR])
    pinned = (ALPHA_GOLDEN, ALPHA_SILVER, ALPHA_BRONZE, ALPHA_RAT_NEAR, ALPHA_RAT_RES)
    low_order = [p / q for q in range(2, 21) for p in range(1, q)]
    for _ in range(10000):
        a = float(rng.random())
        if a <= 1e-6 or a >= 1 - 1e-6:
            continue
        if any(abs(a - c) < 1e-3 for c in pinned):
            continue
        if any(abs(a - r) < 1e-3 for r in low_order):
            continue
        return a
    raise RuntimeError("could not draw a clean random irrational")


def arm_slots(arm: str, seed: int) -> tuple[np.ndarray, dict]:
    """Single parametrized generator — no per-arm special-casing of the metric."""
    if arm == "golden":
        raw, alpha = rotation_raw(ALPHA_GOLDEN), ALPHA_GOLDEN
    elif arm == "silver":
        raw, alpha = rotation_raw(ALPHA_SILVER), ALPHA_SILVER
    elif arm == "bronze":
        raw, alpha = rotation_raw(ALPHA_BRONZE), ALPHA_BRONZE
    elif arm == "rational_near":
        raw, alpha = rotation_raw(ALPHA_RAT_NEAR), ALPHA_RAT_NEAR
    elif arm == "rational_resonant":
        raw, alpha = rotation_raw(ALPHA_RAT_RES), ALPHA_RAT_RES
    elif arm == "random_irrational":
        alpha = draw_random_irrational(seed)
        raw = rotation_raw(alpha)
    elif arm == "random_positions":
        rng = np.random.default_rng([seed, TAG_RANDPOS])
        raw, alpha = rng.random(N), None
    else:
        raise ValueError(arm)
    slots, n_coll = snap_to_slots(raw)
    return slots, {"alpha": alpha, "collisions": n_coll}


# ============================================================ per-(arm,seed) pipeline

A_GRID = grid_design_matrix()   # fixed (N, 2K) — precomputed ONCE, sliced everywhere


def run_arm_seed(arm: str, seed: int, coeffs: np.ndarray,
                 eta: np.ndarray) -> dict:
    """
    All three damage modes for one (arm, seed). Design rows and observations
    are precomputed once and sliced per survivor set (prereg section 5).
    """
    slots, meta = arm_slots(arm, seed)
    a_arm = A_GRID[slots]                        # (N, 2K) rows in sample-index order
    y_full = a_arm @ coeffs + SIGMA * eta        # identical noise-by-index every arm
    a_ext = np.vstack([a_arm, a_arm])            # wrap-around slicing helper
    y_ext = np.concatenate([y_full, y_full])

    per_mode: dict = {m: {"raw": [], "clipped": [], "underdet": []} for m in MODES}
    adv_argmin, adv_mean_over_starts = [], []

    for d_idx, d in enumerate(DAMAGE_GRID):
        n_erase = int(round(d * N))
        n_surv = N - n_erase

        # ---- mode 1: contiguous wrap-around block, seeded random start
        b = block_start(seed, d_idx)
        r = (b + n_erase) % N                    # survivors = run r .. r+n_surv-1
        raw, ud = recover_and_score(a_ext[r:r + n_surv], y_ext[r:r + n_surv], coeffs)
        per_mode["contiguous"]["raw"].append(raw)
        per_mode["contiguous"]["clipped"].append(min(max(raw, 0.0), 1.0))
        per_mode["contiguous"]["underdet"].append(ud)

        # ---- mode 2: ADVERSARIAL contiguous — exhaustive min over all N starts
        worst_clip, worst_run, clip_sum = 2.0, -1, 0.0
        for run in range(N):
            raw_a, ud_a = recover_and_score(
                a_ext[run:run + n_surv], y_ext[run:run + n_surv], coeffs)
            clip_a = min(max(raw_a, 0.0), 1.0)
            clip_sum += clip_a
            if clip_a < worst_clip:
                worst_clip, worst_run = clip_a, run
        per_mode["adversarial"]["raw"].append(worst_clip)   # scored quantity is clipped min
        per_mode["adversarial"]["clipped"].append(worst_clip)
        per_mode["adversarial"]["underdet"].append(bool(n_surv < TWO_K))
        adv_argmin.append(int((worst_run - n_erase) % N))   # worst BLOCK start
        adv_mean_over_starts.append(clip_sum / N)

        # ---- mode 3: random erasure (descriptive only)
        surv = random_erase_mask(seed, d_idx, n_erase)
        raw_r, ud_r = recover_and_score(a_arm[surv], y_full[surv], coeffs)
        per_mode["random"]["raw"].append(raw_r)
        per_mode["random"]["clipped"].append(min(max(raw_r, 0.0), 1.0))
        per_mode["random"]["underdet"].append(ud_r)

    out = {"arm": arm, "seed": seed, "alpha": meta["alpha"],
           "collisions": meta["collisions"],
           "adversarial_argmin_block_start": adv_argmin,
           "adversarial_mean_over_starts": [float(x) for x in adv_mean_over_starts]}
    for m in MODES:
        clip = np.asarray(per_mode[m]["clipped"])
        out[m] = {
            "recoveries_raw": [float(x) for x in per_mode[m]["raw"]],
            "recoveries_clipped": [float(x) for x in clip],
            "underdetermined": [bool(x) for x in per_mode[m]["underdet"]],
            "CB": critical_band_mean(clip),
            "AUR": aur_trapz(clip),
        }
    return out


# ============================================================ aggregation + verdict

def metric_table(records: list[dict], metric: str) -> dict:
    """{mode: {arm: np.array over 16 seeds}} of CB or AUR."""
    tab = {m: {a: np.zeros(len(SEEDS)) for a in ARMS} for m in MODES}
    for rec in records:
        j = SEEDS.index(rec["seed"])
        for m in MODES:
            tab[m][rec["arm"]][j] = rec[m][metric]
    return tab


def classify(cb: dict) -> dict:
    """Locked verdict logic (prereg section 3). Precedence A -> B -> C -> WATCH."""
    n_seed = len(SEEDS)
    per_mode = {}
    for mode in VERDICT_MODES:
        g, s = cb[mode]["golden"], cb[mode]["silver"]
        gap = g - s
        wins = int(np.sum(gap > 0))                       # ties count against golden
        mean_gap = float(np.mean(gap))
        sigma_between = float(np.std(gap, ddof=1))
        p = one_sided_sign_p(wins, n_seed)
        cond1 = wins >= WINS_REQUIRED_A
        cond2 = mean_gap > sigma_between
        cond3 = p < SIGN_TEST_ALPHA
        mean_cb = {a: float(np.mean(cb[mode][a])) for a in ARMS}
        cond4 = (
            mean_cb["golden"] >= mean_cb["bronze"]
            and mean_cb["golden"] > mean_cb["rational_near"]
            and mean_cb["golden"] > mean_cb["rational_resonant"]
            and mean_cb["golden"] > mean_cb["random_irrational"]
            and mean_cb["golden"] > mean_cb["random_positions"]
        )
        # Outcome-B floor checks: golden/silver/bronze vs both floors.
        b_checks = {}
        for champ in ("golden", "silver", "bronze"):
            for floor in ("rational_resonant", "random_positions"):
                fgap = cb[mode][champ] - cb[mode][floor]
                fwins = int(np.sum(fgap > 0))
                fmean = float(np.mean(fgap))
                b_checks[f"{champ}_vs_{floor}"] = {
                    "mean_gap": fmean, "wins": fwins,
                    "ok": bool(fmean >= B_MARGIN and fwins >= B_WINS_REQUIRED)}
        per_mode[mode] = {
            "gap_mean": mean_gap, "gap_sigma_between": sigma_between,
            "golden_wins_over_silver": wins, "sign_test_p_one_sided": p,
            "cond1_wins_ge_12of16": bool(cond1),
            "cond2_gap_gt_sigma_between": bool(cond2),
            "cond3_sign_p_lt_05": bool(cond3),
            "cond4_ordering_sane": bool(cond4),
            "silver_step_ok": bool(cond1 and cond2 and cond3),
            "pass_A_mode": bool(cond1 and cond2 and cond3 and cond4),
            "mean_CB": mean_cb,
            "B_floor_checks": b_checks,
            "B_all_floors_ok": bool(all(v["ok"] for v in b_checks.values())),
        }

    pass_a = all(per_mode[m]["pass_A_mode"] for m in VERDICT_MODES)
    silver_step_both = all(per_mode[m]["silver_step_ok"] for m in VERDICT_MODES)
    b_floors_both = all(per_mode[m]["B_all_floors_ok"] for m in VERDICT_MODES)
    # Outcome C: pooled over both contiguous modes x 16 seeds (32 paired values).
    pooled_gap = np.concatenate([
        cb[m]["golden"] - cb[m]["random_positions"] for m in VERDICT_MODES])
    c_pooled = float(np.mean(pooled_gap))
    c_null = bool(c_pooled <= C_MARGIN)

    ordering_anomaly = False
    if pass_a:
        verdict = "A_STRONG_PHI"
    elif silver_step_both:
        # A criteria 1-3 passed in BOTH modes; failure was only criterion 4.
        # Prereg: WATCH (ordering anomaly), explicitly NOT B.
        verdict = "WATCH"
        ordering_anomaly = True
    elif b_floors_both:
        verdict = "B_IRRATIONALITY_GENERIC"
    elif c_null:
        verdict = "C_MECHANISM_NULL"
    else:
        verdict = "WATCH"

    return {"per_mode": per_mode, "pass_A": bool(pass_a),
            "silver_step_both_modes": bool(silver_step_both),
            "B_floors_both_modes": bool(b_floors_both),
            "C_pooled_golden_minus_random_positions": c_pooled,
            "C_null": c_null, "ordering_anomaly": bool(ordering_anomaly),
            "verdict": verdict}


def cb_ranking(cb: dict) -> list[tuple[str, float]]:
    """Arms ranked by mean CB pooled over the two VERDICT (contiguous) modes."""
    pooled = {a: float(np.mean(np.concatenate(
        [cb[m][a] for m in VERDICT_MODES]))) for a in ARMS}
    return sorted(pooled.items(), key=lambda kv: kv[1], reverse=True)


# ============================================================ numerology self-audit

def audit_phi_free() -> dict:
    """
    AST audit of the signal/damage/metric code paths (prereg section 4).
    Walks each audited function's AST and asserts (a) no phi-family identifier
    is referenced and (b) no numeric literal is within 1e-4 of a phi-family
    value. Comments/docstrings are not code and are ignored. Also asserts the
    locked config carries no phi-family value and the survivor-count table
    matches the prereg. Raises AssertionError on any violation.
    """
    forbidden = re.compile(r"phi|golden|silver|bronze|fibonacci|sqrt5", re.IGNORECASE)
    phi_val = (1.0 + math.sqrt(5.0)) / 2.0
    phi_family = [phi_val, phi_val - 1.0, math.sqrt(5.0),
                  1.618, 0.618, 2.236, 8.0 / 13.0, 13.0 / 8.0]

    audited = (build_signal_coeffs, grid_design_matrix, snap_to_slots,
               recover_and_score, block_start, random_erase_mask,
               critical_band_mean, aur_trapz, one_sided_sign_p, run_arm_seed)
    # run_arm_seed orchestrates damage + scoring; it references arm_slots (layout)
    # but must itself contain no phi-family name other than that call chain.
    exempt_names = {"arm_slots"}  # layout dispatch — the arms live there by design

    for fn in audited:
        tree = ast.parse(inspect.getsource(fn))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id not in exempt_names:
                assert not forbidden.search(node.id), (
                    f"NUMEROLOGY GUARD FAILED: name '{node.id}' in {fn.__name__}")
            if isinstance(node, ast.Attribute):
                assert not forbidden.search(node.attr), (
                    f"NUMEROLOGY GUARD FAILED: attr '{node.attr}' in {fn.__name__}")
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                    and not isinstance(node.value, bool):
                for pv in phi_family:
                    assert abs(float(node.value) - pv) > 1e-4, (
                        f"NUMEROLOGY GUARD FAILED: phi-valued literal "
                        f"{node.value} in {fn.__name__}")

    # Locked-config integrity + phi-freedom.
    assert N == 256 and K == 32 and TWO_K == 64
    assert abs(SIGMA - 1e-3) < 1e-15 and abs(RCOND - 1e-10) < 1e-24
    assert DAMAGE_GRID == (0.60, 0.70, 0.75, 0.80, 0.85, 0.90)
    assert CRITICAL_BAND == (0.75, 0.80, 0.85) and CB_IDX == (2, 3, 4)
    assert SEEDS == tuple(range(9001, 9017)) and len(SEEDS) == 16
    assert WINS_REQUIRED_A == 12 and abs(SIGN_TEST_ALPHA - 0.05) < 1e-15
    assert abs(B_MARGIN - 0.05) < 1e-15 and B_WINS_REQUIRED == 12
    assert abs(C_MARGIN - 0.05) < 1e-15
    survivors = tuple(N - int(round(d * N)) for d in DAMAGE_GRID)
    assert survivors == EXPECTED_SURVIVORS, survivors
    for name, val in (("N", N), ("K", K), ("SIGMA", SIGMA), ("RCOND", RCOND),
                      ("WINS_REQUIRED_A", WINS_REQUIRED_A), ("B_MARGIN", B_MARGIN),
                      ("C_MARGIN", C_MARGIN)):
        for pv in phi_family:
            assert abs(float(val) - pv) > 1e-4, f"{name} collides with phi family"
    for sd in SEEDS:
        assert str(sd) not in ("1618", "6180", "1123", "5813", "2358", "3581"), sd
    # Exact one-sided binomial sanity pin from the prereg: 12/16 -> p = 0.0384...
    assert abs(one_sided_sign_p(12, 16) - 2517.0 / 65536.0) < 1e-15

    return {"status": "PASSED",
            "audited_functions": [f.__name__ for f in audited],
            "forbidden_pattern": forbidden.pattern,
            "phi_family_values_checked": phi_family,
            "survivor_table_verified": list(survivors)}


# ============================================================ main

def main() -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    audit = audit_phi_free()
    print(f"[GOLDEN-HEAL-v2] numerology guard: {audit['status']} "
          f"({len(audit['audited_functions'])} functions AST-audited)")

    records = []
    for seed in SEEDS:
        coeffs = build_signal_coeffs(seed)
        eta = np.random.default_rng([seed, TAG_NOISE]).standard_normal(N)
        for arm in ARMS:
            records.append(run_arm_seed(arm, seed, coeffs, eta))
        print(f"[GOLDEN-HEAL-v2] seed {seed} done "
              f"({time.time() - t0:6.1f}s elapsed)")

    cb = metric_table(records, "CB")
    aur = metric_table(records, "AUR")
    verdict = classify(cb)
    ranking = cb_ranking(cb)

    # ---- regime check (arithmetic, not tuned): the grid crosses 2K by design.
    survivors = [N - int(round(d * N)) for d in DAMAGE_GRID]
    regime = {
        "twoK": TWO_K, "survivors_per_grid_point": survivors,
        "underdetermined_grid_points": [d for d, s in zip(DAMAGE_GRID, survivors)
                                        if s < TWO_K],
        "note": ("v2 enters the coverage-stressed regime v1 never reached: "
                 "exactly-determined at d=0.75 (64 = 2K) and under-determined "
                 "at d >= 0.80. UNDERDETERMINED points are minimum-norm lstsq, "
                 "logged and still scored, per the locked contract.")}

    # ---- adversarial diagnostics: catastrophe depth per arm x d (pooled seeds)
    adv_diag = {}
    for arm in ARMS:
        rows = [r for r in records if r["arm"] == arm]
        per_d = []
        for d_idx, d in enumerate(DAMAGE_GRID):
            worst = float(np.mean([r["adversarial"]["recoveries_clipped"][d_idx]
                                   for r in rows]))
            mean_all = float(np.mean([r["adversarial_mean_over_starts"][d_idx]
                                      for r in rows]))
            per_d.append({"d": d, "mean_worst_case": worst,
                          "mean_over_all_starts": mean_all,
                          "catastrophe_depth": mean_all - worst})
        adv_diag[arm] = per_d

    # ---- mode-3 descriptive gap (caveat flag only, no verdict weight)
    rnd_gap = cb["random"]["golden"] - cb["random"]["silver"]
    mode3 = {"golden_minus_silver_mean_CB": float(np.mean(rnd_gap)),
             "golden_wins": int(np.sum(rnd_gap > 0)),
             "direction_consistent_with_contiguous": bool(
                 np.sign(np.mean(rnd_gap)) == np.sign(
                     verdict["per_mode"]["contiguous"]["gap_mean"]))}

    # ---- collision rates (per arm; pooled over seeds for the random arms)
    collisions = {arm: {
        "mean": float(np.mean([r["collisions"] for r in records if r["arm"] == arm])),
        "min": int(min(r["collisions"] for r in records if r["arm"] == arm)),
        "max": int(max(r["collisions"] for r in records if r["arm"] == arm)),
    } for arm in ARMS}

    elapsed = time.time() - t0

    summary = {
        "test_id": "GOLDEN-HEAL-v2",
        "prereg": "experiments/GOLDEN_HEAL_PREREG_v2.md (locked 2026-07-03)",
        "lane": "engineering / verified-computation. NOT physics evidence.",
        "forbidden_upgrade": (
            "GOLDEN-HEAL v2 is a toy least-squares recoverability probe in a "
            "coverage-stressed regime; no outcome here is physics evidence. "
            "Outcome B (the expected result) is a statement about low-discrepancy "
            "geometry, not about phi being physically privileged, and even "
            "Outcome A would be a numerical-linear-algebra fingerprint requiring "
            "independent replication before any ledger upgrade beyond 'toy anomaly.'"),
        "v1_citation": (
            "GOLDEN-HEAL-v1 (GOLDEN_HEAL_PREREG_v1.md + ghp_golden_heal_probe.py) "
            "returned C_MECHANISM_NULL under its locked contract; that verdict "
            "STANDS and is not corrected or overturned by v2. v1 diagnosis: "
            "minimum survivors ~102 >> 2K=32 kept the system over-determined "
            "everywhere; all irrational/aperiodic arms tied at ceiling ~0.6996 "
            "(~1e-5 seed noise; random_irrational edged golden); rational arms "
            "collapsed by rank deficiency. GH-B monotone finding also stands."),
        "config": {"N": N, "K": K, "twoK": TWO_K, "sigma": SIGMA, "rcond": RCOND,
                   "damage_grid": list(DAMAGE_GRID),
                   "critical_band": list(CRITICAL_BAND),
                   "survivors_per_grid_point": survivors,
                   "seeds": list(SEEDS), "modes": list(MODES),
                   "verdict_modes": list(VERDICT_MODES), "arms": list(ARMS),
                   "thresholds": {"A_wins": WINS_REQUIRED_A,
                                  "A_sign_p": SIGN_TEST_ALPHA,
                                  "B_margin": B_MARGIN, "B_wins": B_WINS_REQUIRED,
                                  "C_margin": C_MARGIN},
                   "substream_tags": {"coeff": TAG_COEFF, "noise": TAG_NOISE,
                                      "block_start": TAG_START,
                                      "random_subset": TAG_SUBSET,
                                      "random_irrational": TAG_RANDIRR,
                                      "random_positions": TAG_RANDPOS}},
        "alphas": {"golden": ALPHA_GOLDEN, "silver": ALPHA_SILVER,
                   "bronze": ALPHA_BRONZE, "rational_near": ALPHA_RAT_NEAR,
                   "rational_resonant": ALPHA_RAT_RES},
        "classification": verdict["verdict"],
        "verdict_trace": verdict,
        "regime": regime,
        "CB_ranking_pooled_contiguous_modes": [
            {"arm": a, "mean_CB": v} for a, v in ranking],
        "mean_CB_per_mode": {m: {a: float(np.mean(cb[m][a])) for a in ARMS}
                             for m in MODES},
        "mean_AUR_per_mode": {m: {a: float(np.mean(aur[m][a])) for a in ARMS}
                              for m in MODES},
        "golden_vs_silver_CB": {
            m: {"mean_gap": verdict["per_mode"][m]["gap_mean"],
                "sigma_between": verdict["per_mode"][m]["gap_sigma_between"],
                "golden_wins": verdict["per_mode"][m]["golden_wins_over_silver"],
                "sign_test_p_one_sided": verdict["per_mode"][m]["sign_test_p_one_sided"]}
            for m in VERDICT_MODES},
        "adversarial_diagnostics": adv_diag,
        "mode3_random_erasure_descriptive": mode3,
        "collision_stats": collisions,
        "records": records,
        "numerology_guard": audit,
        "runtime_seconds": elapsed,
        "regime_hunt_closure": (
            "TRIGGERED: v2 returned C_MECHANISM_NULL; per prereg section 0.3 the "
            "recoverability-mechanism line is CLOSED. No preregistered v3."
            if verdict["verdict"] == "C_MECHANISM_NULL" else
            "not triggered (verdict != C)."),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    write_report(summary, cb, aur, verdict, ranking, adv_diag, mode3,
                 collisions, regime, elapsed)

    print(f"[GOLDEN-HEAL-v2] classification = {verdict['verdict']}")
    print(f"[GOLDEN-HEAL-v2] CB ranking (pooled contiguous modes): "
          f"{[(a, round(v, 4)) for a, v in ranking]}")
    for m in VERDICT_MODES:
        pm = verdict["per_mode"][m]
        print(f"[GOLDEN-HEAL-v2] {m}: G-S gap={pm['gap_mean']:+.4f} "
              f"sigma_between={pm['gap_sigma_between']:.4f} "
              f"wins={pm['golden_wins_over_silver']}/16 "
              f"p={pm['sign_test_p_one_sided']:.4f}")
    print(f"[GOLDEN-HEAL-v2] C pooled (golden - random_positions) = "
          f"{verdict['C_pooled_golden_minus_random_positions']:+.4f} "
          f"(null margin {C_MARGIN})")
    print(f"[GOLDEN-HEAL-v2] runtime = {elapsed:.1f}s")
    print(f"[GOLDEN-HEAL-v2] wrote {OUT / 'summary.json'} and {OUT / 'report.md'}")


def write_report(summary, cb, aur, verdict, ranking, adv_diag, mode3,
                 collisions, regime, elapsed) -> None:
    v = verdict["verdict"]
    label = {
        "A_STRONG_PHI": "OUTCOME A — STRONG phi-specificity",
        "B_IRRATIONALITY_GENERIC": "OUTCOME B — IRRATIONALITY-GENERIC (expected result)",
        "C_MECHANISM_NULL": "OUTCOME C — MECHANISM-NULL (line CLOSED per prereg 0.3)",
        "WATCH": "WATCH — none clean; no promotion",
    }[v]
    ln = []
    ln.append("# GOLDEN-HEAL-v2 — coverage-stressed recoverability discriminator\n")
    ln.append(f"**Classification: {label}**\n")
    ln.append("> Lane: engineering / verified-computation. **NOT physics evidence.** "
              + summary["forbidden_upgrade"] + "\n")
    ln.append("## v1 verdict (STANDS — required citation, retro-tune guard)\n")
    ln.append(summary["v1_citation"] + " v2 is a NEW timestamped contract "
              "(GOLDEN_HEAL_PREREG_v2.md) testing the same mechanism in the "
              "coverage-stressed regime; it does not correct or overturn v1 — "
              "v1 answered its own contract correctly.\n")
    ln.append("## Regime (the point of v2)\n")
    ln.append("| d | survivors | vs 2K = 64 |")
    ln.append("|---|---|---|")
    for d, s in zip(DAMAGE_GRID, regime["survivors_per_grid_point"]):
        rel = ("over-determined" if s > TWO_K else
               "EXACTLY determined" if s == TWO_K else "UNDER-determined")
        band = " **<- critical band**" if d in CRITICAL_BAND else ""
        ln.append(f"| {d:.2f} | {s} | {rel}{band} |")
    ln.append("")
    ln.append(f"- {regime['note']}\n")
    ln.append("## Primary metric — critical-band CB ranking "
              "(pooled contiguous + adversarial modes)\n")
    ln.append("| rank | arm | mean CB |")
    ln.append("|---|---|---|")
    for i, (a, val) in enumerate(ranking, 1):
        ln.append(f"| {i} | {a} | {val:.4f} |")
    ln.append("")
    ln.append("## Mean CB per mode (16 seeds)\n")
    ln.append("| arm | contiguous | adversarial | random (descriptive) |")
    ln.append("|---|---|---|---|")
    for a in ARMS:
        ln.append(f"| {a} | " + " | ".join(
            f"{float(np.mean(cb[m][a])):.4f}" for m in MODES) + " |")
    ln.append("")
    ln.append("## Golden-vs-silver on CB (the ONLY place a phi claim can live)\n")
    ln.append("| mode | mean gap (G-S) | sigma_between | golden wins | "
              "one-sided p | silver step (A1-A3)? |")
    ln.append("|---|---|---|---|---|---|")
    for m in VERDICT_MODES:
        pm = verdict["per_mode"][m]
        ln.append(f"| {m} | {pm['gap_mean']:+.4f} | "
                  f"{pm['gap_sigma_between']:.4f} | "
                  f"{pm['golden_wins_over_silver']}/16 | "
                  f"{pm['sign_test_p_one_sided']:.4f} | "
                  f"{'PASS' if pm['silver_step_ok'] else 'fail'} |")
    ln.append("")
    ln.append("## Verdict logic (locked thresholds, precedence A -> B -> C -> WATCH)\n")
    for m in VERDICT_MODES:
        pm = verdict["per_mode"][m]
        ln.append(f"### mode: {m}")
        ln.append(f"- A1 golden>silver in >=12/16 seeds: **{pm['cond1_wins_ge_12of16']}** "
                  f"({pm['golden_wins_over_silver']}/16)")
        ln.append(f"- A2 mean gap > sigma_between: **{pm['cond2_gap_gt_sigma_between']}** "
                  f"({pm['gap_mean']:+.4f} vs {pm['gap_sigma_between']:.4f})")
        ln.append(f"- A3 one-sided sign test p<0.05: **{pm['cond3_sign_p_lt_05']}** "
                  f"(p={pm['sign_test_p_one_sided']:.4f})")
        ln.append(f"- A4 ordering sane: **{pm['cond4_ordering_sane']}**")
        ln.append(f"- PASS-A this mode: **{pm['pass_A_mode']}**")
        ln.append("- B floor checks (need mean gap >= 0.05 AND >= 12/16 wins):")
        for k, chk in pm["B_floor_checks"].items():
            ln.append(f"  - {k}: mean_gap={chk['mean_gap']:+.4f}, "
                      f"wins={chk['wins']}/16 -> "
                      f"{'ok' if chk['ok'] else 'FAIL'}")
        ln.append(f"- B all floors ok this mode: **{pm['B_all_floors_ok']}**")
        ln.append("")
    ln.append(f"- **PASS-A (both modes): {verdict['pass_A']}**")
    ln.append(f"- Silver step (A1-A3) both modes: {verdict['silver_step_both_modes']}"
              + (" -> ordering anomaly, WATCH not B" if verdict["ordering_anomaly"] else ""))
    ln.append(f"- **B floors both modes: {verdict['B_floors_both_modes']}**")
    ln.append(f"- **C pooled mean(CB_golden - CB_random_positions) over 32 paired "
              f"values: {verdict['C_pooled_golden_minus_random_positions']:+.4f} "
              f"(<= {C_MARGIN} => C: {verdict['C_null']})**")
    ln.append(f"- **VERDICT: {v}**\n")
    ln.append("## Adversarial mode — worst-block anatomy\n")
    ln.append("(mean over 16 seeds; 'catastrophe depth' = mean-over-all-256-starts "
              "minus worst-case, i.e. how much a schedule's WORST block underperforms "
              "its typical block)\n")
    ln.append("| arm | " + " | ".join(f"d={d:.2f} worst / depth" for d in DAMAGE_GRID) + " |")
    ln.append("|---|" + "|".join(["---"] * len(DAMAGE_GRID)) + "|")
    for a in ARMS:
        cells = " | ".join(f"{row['mean_worst_case']:.3f} / {row['catastrophe_depth']:.3f}"
                           for row in adv_diag[a])
        ln.append(f"| {a} | {cells} |")
    ln.append("")
    ln.append("## Mode 3 — random erasure (descriptive ONLY, no verdict weight)\n")
    ln.append(f"- golden - silver mean CB gap: {mode3['golden_minus_silver_mean_CB']:+.4f} "
              f"({mode3['golden_wins']}/16 golden wins); direction "
              f"{'consistent with' if mode3['direction_consistent_with_contiguous'] else 'REVERSED vs'} "
              "the contiguous mode (flagged as caveat only).\n")
    ln.append("## Secondary metric — AUR (descriptive, no verdict weight)\n")
    ln.append("| arm | contiguous | adversarial | random |")
    ln.append("|---|---|---|---|")
    for a in ARMS:
        ln.append(f"| {a} | " + " | ".join(
            f"{float(np.mean(aur[m][a])):.4f}" for m in MODES) + " |")
    ln.append("")
    ln.append("## Grid snapping — collision rates (per arm, over 16 seeds)\n")
    ln.append("| arm | mean collisions | min | max |")
    ln.append("|---|---|---|---|")
    for a in ARMS:
        c = collisions[a]
        ln.append(f"| {a} | {c['mean']:.1f} | {c['min']} | {c['max']} |")
    ln.append("")
    ln.append("## Numerology guard\n")
    ln.append(f"- AST audit of signal/damage/metric code paths: **PASSED** "
              f"({len(summary['numerology_guard']['audited_functions'])} functions: "
              f"{', '.join(summary['numerology_guard']['audited_functions'])}).")
    ln.append("- phi enters ONLY as pinned rotation angles (rational_near = 8/13 is "
              "an arm definition, not machinery).")
    ln.append("- Seed list 9001..9016 — phi-digit strings removed (v1 had "
              "1618/6180/1123/5813).")
    ln.append("- A pass-region EXCLUDES the silver tie by construction; a win over "
              "rational/random alone is textbook low-discrepancy = Outcome B, "
              "never a phi claim.")
    ln.append("- Rational-arm collapse is pre-disclosed (v1: literal rank deficiency; "
              "v2 grid-snapped analogue: catastrophic coverage holes under "
              "contiguous damage) and carries no evidential weight.")
    ln.append(f"- Regime-hunt closure clause: {summary['regime_hunt_closure']}\n")
    ln.append(f"_Runtime: {elapsed:.1f}s. Deterministic: python3 + numpy, "
              f"all substreams seeded from the frozen seed list._\n")
    (OUT / "report.md").write_text("\n".join(ln))


if __name__ == "__main__":
    main()
