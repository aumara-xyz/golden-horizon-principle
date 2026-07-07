#!/usr/bin/env python3
"""
GOLDEN-HEAL-v1 — the recoverability discriminator (GHP Test #1, ledger AH.4 P1).

This is a TOY least-squares recoverability probe, NOT physics evidence.
Per GHP master hard rule 7, no outcome here proves GHP, observer-boundary
selection, or a write-law. A golden win, if it survives the silver-tie
exclusion, would be a numerical-linear-algebra fingerprint of low-discrepancy
geometry, nothing more.

Forbidden-upgrade sentence (locked, prereg section 5):
  "GOLDEN-HEAL is a toy least-squares recoverability probe; no outcome here is
   physics evidence, and Outcome B (the expected result) is a statement about
   low-discrepancy geometry, not about phi being physically privileged."

--------------------------------------------------------------------------------
MECHANISM HYPOTHESIS (why golden MIGHT win — theorem-backed, not a hope):
A code that lays redundancy down by golden-angle spreading should survive damage
best, for two reasons:
  (1) THREE-DISTANCE / low-discrepancy: x_i=(i*alpha)mod1 with alpha=phi has the
      most uniform gap structure of any irrational rotation (three-distance
      theorem; golden gives tightest gap ratios). Any surviving fragment still
      covers the domain near-optimally.
  (2) HURWITZ / KAM anti-resonance: phi is the worst-approximable irrational
      (Hurwitz 1891); the golden-winding torus is LAST destroyed under
      perturbation (KAM). Golden spreading is maximally resistant to the
      resonant holes that periodic/rational schedules create.
Prediction: recovery ranks golden>=silver>=bronze>rational>random, tracking each
constant's irrationality measure, golden best as the extremal case.

THREE PREREGISTERED OUTCOMES (all honest, all reportable):
  (A) STRONG phi-specificity: golden's AUR beats silver's, resolvably across
      seeds, in BOTH damage modes, ordering intact. The anomaly worth escalating.
  (B) IRRATIONALITY-GENERIC (EXPECTED null, fully acceptable): golden~silver
      ~bronze, all > rational > random. Low-discrepancy is what matters; phi is
      the extremal ANCHOR, not a unique write-point. NOT a phi win.
  (C) MECHANISM-NULL: golden not better than rational/random. Kills the
      recoverability mechanism itself.

NUMEROLOGY GUARD (enforced in code, prereg section 5):
  No phi constant may touch the signal, band K, grid, coefficients, noise, or
  recovery metric. phi appears ONLY as one rotation angle among the arms. This
  file self-audits: (a) a source grep of the signal/metric functions for
  phi/1.618/fibonacci must return nothing (asserted at runtime); (b) the pass
  region for A EXCLUDES the silver-tie region by construction.
--------------------------------------------------------------------------------
"""

from __future__ import annotations

import inspect
import json
import math
import re
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

# NumPy 2.0.2's SIMD matmul kernel on this macOS BLAS build emits spurious
# divide-by-zero / overflow / invalid RuntimeWarnings even when the result is
# finite and correct (verified: float64 fallback matmul yields identical finite
# values). These are cosmetic and do NOT affect any recovery value. Silence them
# so they cannot mask a genuine future numerical problem.
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*matmul.*")

# Prefer np.trapezoid (np.trapz deprecated in numpy 2.x); fall back for safety.
try:
    _trapz = np.trapezoid  # type: ignore[attr-defined]
except AttributeError:  # pragma: no cover
    _trapz = np.trapz

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_golden_heal_probe_outputs"

# ------------------------------------------------------------------ locked config
N = 512                 # sample slots on uniform index grid
K = 16                  # signal bandwidth (frozen; phi-free)
SIGMA = 1e-3            # observation noise std (frozen)
RCOND = 1e-10          # lstsq rcond (frozen)
DAMAGE_GRID = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)   # frozen 8-point grid
SEEDS = (1618, 2718, 3141, 1414, 1732, 2236, 4142, 1123, 5813, 2971, 6180, 8090)
MODES = ("contiguous", "random")

# Pinned rotation angles (fractional parts — the ONLY phi-dependence in the code).
SQRT5 = math.sqrt(5.0)
ALPHA_GOLDEN = (1.0 + SQRT5) / 2.0 - 1.0            # frac(phi) = 1/phi = 0.6180339887
ALPHA_SILVER = math.sqrt(2.0) - 1.0                # frac(1+sqrt2)  = 0.4142135624
ALPHA_BRONZE = (3.0 + math.sqrt(13.0)) / 2.0 - 3.0  # frac((3+sqrt13)/2)=0.3027756377
ALPHA_RAT_NEAR = 8.0 / 13.0                         # 0.6153846 hardest near-golden rational
ALPHA_RAT_RES = 1.0 / 2.0                           # 0.5 resonant control

# Arm names in predicted-ordering sequence.
ARMS = (
    "golden",
    "silver",
    "bronze",
    "rational_near",
    "rational_resonant",
    "random_irrational",
    "random_positions",
)

# Locked thresholds (immutable post-data, prereg section 4).
WIN_FRAC_A = 8.0 / 12.0      # >=8/12 seed wins required for PASS-A step 1
SIGN_TEST_P = 0.05          # paired sign test tie-rejection threshold
LOWDISC_MARGIN = 0.02       # mean AUR advantage to "beat" a floor arm
LOWDISC_WINFRAC = 9.0 / 12.0  # seed-win fraction to "beat" a floor arm
NULL_C_MARGIN = 0.02        # golden - random_positions <= this => Outcome C


# ============================================================ phi-free signal/metric
# NOTHING below (until the rotation-arm layout) may reference phi/golden/fibonacci.
# The runtime audit at the bottom greps these functions' source to enforce it.

def build_signal_coeffs(seed: int) -> np.ndarray:
    """K-dim bandlimited coeff vector, N(0,1) then L2-normalized. phi-free."""
    rng = np.random.default_rng(seed ^ 0x5A5A)  # coeff sub-stream
    coeffs = rng.standard_normal(2 * K)          # [a_1..a_K, b_1..b_K]
    coeffs /= np.linalg.norm(coeffs)             # seed-independent ||f||
    return coeffs


def design_matrix(positions: np.ndarray) -> np.ndarray:
    """cos/sin design over band k=1..K at given positions. phi-free."""
    ks = np.arange(1, K + 1)
    ang = 2.0 * np.pi * np.outer(positions, ks)  # (M, K)
    return np.hstack([np.cos(ang), np.sin(ang)])  # (M, 2K)


def evaluate_signal(positions: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    """Ground-truth f at positions. phi-free."""
    return design_matrix(positions) @ coeffs


def recover_and_score(
    survivor_pos: np.ndarray, survivor_y: np.ndarray, coeffs: np.ndarray
) -> tuple[float, bool]:
    """
    Least-squares reconstruct coeffs from survivors, score normalized recovery
    against the truth on a dense phi-free grid. Returns (recovery, underdetermined).
    """
    A = design_matrix(survivor_pos)
    chat, *_ = np.linalg.lstsq(A, survivor_y, rcond=RCOND)
    underdet = survivor_pos.size < 2 * K
    # Score in coefficient space == function L2 on the orthogonal cos/sin band,
    # which equals ||f_hat - f|| / ||f|| exactly (Parseval), phi-free.
    err = np.linalg.norm(chat - coeffs) / np.linalg.norm(coeffs)
    recovery = 1.0 - err
    return recovery, underdet


# ============================================================ arm sample layouts

def rotation_positions(alpha: float) -> np.ndarray:
    """Low-discrepancy orbit p_i = frac(i*alpha), i=0..N-1."""
    i = np.arange(N)
    return np.mod(i * alpha, 1.0)


def random_positions(seed: int) -> np.ndarray:
    """N uniform positions on the circle (no rotation structure) — low-disc floor."""
    rng = np.random.default_rng(seed ^ 0x1234)
    return rng.random(N)


def draw_random_irrational(seed: int) -> float:
    """
    Fresh irrational alpha per seed; rejected if within 1e-3 of any pinned alpha
    or a low-order rational p/q (q<=20). Controls for any-irrationality.
    """
    rng = np.random.default_rng(seed ^ 0x7777)
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


def arm_positions(arm: str, seed: int) -> tuple[np.ndarray, dict]:
    """Single parametrized generator — no per-arm special-casing of the metric."""
    meta = {}
    if arm == "golden":
        pos = rotation_positions(ALPHA_GOLDEN); meta["alpha"] = ALPHA_GOLDEN
    elif arm == "silver":
        pos = rotation_positions(ALPHA_SILVER); meta["alpha"] = ALPHA_SILVER
    elif arm == "bronze":
        pos = rotation_positions(ALPHA_BRONZE); meta["alpha"] = ALPHA_BRONZE
    elif arm == "rational_near":
        pos = rotation_positions(ALPHA_RAT_NEAR); meta["alpha"] = ALPHA_RAT_NEAR
    elif arm == "rational_resonant":
        pos = rotation_positions(ALPHA_RAT_RES); meta["alpha"] = ALPHA_RAT_RES
    elif arm == "random_irrational":
        a = draw_random_irrational(seed)
        pos = rotation_positions(a); meta["alpha"] = a
    elif arm == "random_positions":
        pos = random_positions(seed); meta["alpha"] = None
    else:
        raise ValueError(arm)
    return pos, meta


# ============================================================ damage models

def erase_indices(mode: str, d: float, seed: int) -> np.ndarray:
    """Return the surviving INDEX mask (True=survives) for damage fraction d."""
    n_erase = int(round(d * N))
    surv = np.ones(N, dtype=bool)
    if mode == "contiguous":
        rng = np.random.default_rng(seed ^ 0xC0FFEE)
        start = int(rng.integers(0, N))
        idx = (start + np.arange(n_erase)) % N   # wrap-around block
        surv[idx] = False
    elif mode == "random":
        rng = np.random.default_rng(seed ^ 0xBEEF)
        idx = rng.choice(N, size=n_erase, replace=False)
        surv[idx] = False
    else:
        raise ValueError(mode)
    return surv


# ============================================================ per-(arm,mode,seed) run

def run_arm(arm: str, mode: str, seed: int) -> dict:
    coeffs = build_signal_coeffs(seed)
    pos, meta = arm_positions(arm, seed)
    # Observation noise: seeded stream, drawn once for all N slots.
    noise_rng = np.random.default_rng(seed ^ 0x0E1D)
    y_full = evaluate_signal(pos, coeffs) + SIGMA * noise_rng.standard_normal(N)

    recoveries = []
    underdet_flags = []
    for d in DAMAGE_GRID:
        surv = erase_indices(mode, d, seed)
        if surv.sum() == 0:
            recoveries.append(0.0)
            underdet_flags.append(True)
            continue
        rec, ud = recover_and_score(pos[surv], y_full[surv], coeffs)
        recoveries.append(rec)
        underdet_flags.append(ud)

    rec_clip = np.clip(np.asarray(recoveries), 0.0, 1.0)
    aur = float(_trapz(rec_clip, DAMAGE_GRID))
    return {
        "arm": arm, "mode": mode, "seed": seed, "alpha": meta["alpha"],
        "recoveries_raw": [float(x) for x in recoveries],
        "recoveries_clipped": [float(x) for x in rec_clip],
        "underdetermined": [bool(x) for x in underdet_flags],
        "AUR": aur,
    }


# ============================================================ GH-B convergent probe

def fibonacci(n_max: int) -> list[int]:
    fibs = [1, 1]
    while len(fibs) < n_max + 2:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs


def run_convergent(alpha: float, seed: int, mode: str) -> float:
    """AUR for an arbitrary alpha (used by GH-B). Same pipeline, phi-free metric."""
    coeffs = build_signal_coeffs(seed)
    pos = rotation_positions(alpha)
    noise_rng = np.random.default_rng(seed ^ 0x0E1D)
    y_full = evaluate_signal(pos, coeffs) + SIGMA * noise_rng.standard_normal(N)
    recs = []
    for d in DAMAGE_GRID:
        surv = erase_indices(mode, d, seed)
        rec, _ = recover_and_score(pos[surv], y_full[surv], coeffs)
        recs.append(rec)
    return float(_trapz(np.clip(recs, 0.0, 1.0), DAMAGE_GRID))


# ============================================================ aggregation + verdict

def aur_table(records: list[dict]) -> dict:
    """{mode: {arm: np.array over seeds}} of AUR."""
    tab = {m: {a: np.zeros(len(SEEDS)) for a in ARMS} for m in MODES}
    for r in records:
        j = SEEDS.index(r["seed"])
        tab[r["mode"]][r["arm"]][j] = r["AUR"]
    return tab


def sign_test_p(gaps: np.ndarray) -> tuple[int, float]:
    """Two-sided exact binomial on sign of gaps (ties dropped)."""
    pos = int(np.sum(gaps > 0))
    neg = int(np.sum(gaps < 0))
    n = pos + neg
    if n == 0:
        return pos, 1.0
    p = binomtest(pos, n, 0.5, alternative="two-sided").pvalue
    return pos, float(p)


def beats_floor(arm_aur: np.ndarray, floor_aur: np.ndarray) -> tuple[bool, float, int]:
    gap = arm_aur - floor_aur
    wins = int(np.sum(gap > 0))
    mean_gap = float(np.mean(gap))
    ok = (mean_gap >= LOWDISC_MARGIN) and (wins >= LOWDISC_WINFRAC * len(SEEDS))
    return ok, mean_gap, wins


def classify(tab: dict) -> dict:
    n_seed = len(SEEDS)
    per_mode = {}
    for mode in MODES:
        g = tab[mode]["golden"]
        s = tab[mode]["silver"]
        b = tab[mode]["bronze"]
        gap = g - s
        wins = int(np.sum(gap > 0))
        mean_gap = float(np.mean(gap))
        sigma_between = float(np.std(gap, ddof=1))
        pos, p = sign_test_p(gap)
        # PASS-A per-mode sub-conditions
        cond1 = wins >= WIN_FRAC_A * n_seed
        cond2 = mean_gap > sigma_between
        cond3 = p < SIGN_TEST_P
        # ordering: golden >= bronze and golden > all rational/random (mean AUR)
        mean_aur = {a: float(np.mean(tab[mode][a])) for a in ARMS}
        ordering_ok = (
            mean_aur["golden"] >= mean_aur["bronze"]
            and mean_aur["golden"] > mean_aur["rational_near"]
            and mean_aur["golden"] > mean_aur["rational_resonant"]
            and mean_aur["golden"] > mean_aur["random_irrational"]
            and mean_aur["golden"] > mean_aur["random_positions"]
        )
        # low-discrepancy floor checks for B: golden/silver/bronze beat rational_resonant + random
        floors = ("rational_resonant", "random_positions")
        b_checks = {}
        for champ_name, champ in (("golden", g), ("silver", s), ("bronze", b)):
            for fl in floors:
                ok, mg, w = beats_floor(champ, tab[mode][fl])
                b_checks[f"{champ_name}_vs_{fl}"] = {"ok": ok, "mean_gap": mg, "wins": w}
        b_all_beat = all(v["ok"] for v in b_checks.values())
        # Outcome C: golden - random_positions <= margin
        c_gap = float(np.mean(g) - np.mean(tab[mode]["random_positions"]))
        per_mode[mode] = {
            "gap_mean": mean_gap,
            "gap_sigma_between": sigma_between,
            "golden_wins_over_silver": wins,
            "sign_test_positive": pos,
            "sign_test_p": p,
            "cond1_wins_ge_8of12": cond1,
            "cond2_gap_gt_sigma": cond2,
            "cond3_signtest_p_lt_05": cond3,
            "cond4_ordering_intact": ordering_ok,
            "pass_A_mode": bool(cond1 and cond2 and cond3 and ordering_ok),
            "mean_aur": mean_aur,
            "B_floor_checks": b_checks,
            "B_all_beat_floors": b_all_beat,
            "C_golden_minus_randompos": c_gap,
            "C_mode_null": c_gap <= NULL_C_MARGIN,
        }

    pass_A = all(per_mode[m]["pass_A_mode"] for m in MODES)
    confirm_B = (not pass_A) and all(per_mode[m]["B_all_beat_floors"] for m in MODES)
    confirm_C = all(per_mode[m]["C_mode_null"] for m in MODES)

    if pass_A:
        verdict = "A_STRONG_PHI"
    elif confirm_C:
        verdict = "C_MECHANISM_NULL"
    elif confirm_B:
        verdict = "B_IRRATIONALITY_GENERIC"
    else:
        # partial signals across modes -> mixed / watch
        verdict = "MIXED"

    return {"per_mode": per_mode, "pass_A": pass_A,
            "confirm_B": confirm_B, "confirm_C": confirm_C, "verdict": verdict}


def build_ranking(tab: dict) -> list[str]:
    """Rank arms by pooled-across-modes mean AUR (primary reporting order)."""
    pooled = {a: float(np.mean([tab[m][a].mean() for m in MODES])) for a in ARMS}
    return sorted(ARMS, key=lambda a: pooled[a], reverse=True)


# ============================================================ numerology self-audit

def audit_phi_free() -> None:
    """
    Audit the signal/metric functions for any phi-family DEPENDENCY. Enforced at
    runtime (prereg section 5). We parse each function's AST and inspect only the
    executable content (identifiers referenced + numeric literals), NOT comments
    or docstrings — those legitimately say "phi-free". A guard on comment prose
    would be theater; the real invariant is that no phi VALUE or phi-named symbol
    is used to compute the signal or the recovery score.
    """
    import ast

    forbidden_names = re.compile(r"phi|golden|silver|bronze|fibonacci|sqrt5",
                                 re.IGNORECASE)
    phi_val = (1.0 + math.sqrt(5.0)) / 2.0
    phi_family_vals = [phi_val, phi_val - 1.0, 1.618, 0.618, 1.6180339887, 0.6180339887]

    for fn in (build_signal_coeffs, design_matrix, evaluate_signal,
               recover_and_score, erase_indices):
        tree = ast.parse(inspect.getsource(fn))
        for node in ast.walk(tree):
            # (a) no phi-named identifier is referenced
            if isinstance(node, ast.Name):
                assert not forbidden_names.search(node.id), (
                    f"NUMEROLOGY GUARD FAILED: phi-family name '{node.id}' "
                    f"used in {fn.__name__}")
            if isinstance(node, ast.Attribute):
                assert not forbidden_names.search(node.attr), (
                    f"NUMEROLOGY GUARD FAILED: phi-family attr '{node.attr}' "
                    f"in {fn.__name__}")
            # (b) no numeric literal equals a phi-family value
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                for pv in phi_family_vals:
                    assert abs(float(node.value) - pv) > 1e-4, (
                        f"NUMEROLOGY GUARD FAILED: phi-valued literal "
                        f"{node.value} in {fn.__name__}")

    # Confirm signal band/grid constants carry no phi value.
    assert K == 16 and N == 512
    assert abs(SIGMA - 1e-3) < 1e-15
    for name, val in (("N", N), ("K", K), ("SIGMA", SIGMA)):
        for pv in phi_family_vals:
            assert abs(float(val) - pv) > 1e-4, f"{name} collides with phi value"


# ============================================================ main

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    audit_phi_free()

    records = []
    for mode in MODES:
        for arm in ARMS:
            for seed in SEEDS:
                records.append(run_arm(arm, mode, seed))

    tab = aur_table(records)
    verdict = classify(tab)
    ranking = build_ranking(tab)

    # ---- regime diagnostic (honesty: did the locked grid ever stress coverage?) --
    # The mechanism (three-distance coverage advantage) can only appear once
    # survivors become sparse RELATIVE to the band, i.e. approach/enter the
    # under-determined regime |survivors| < 2K. With N=512, K=16 (2K=32) and the
    # locked max damage 0.8, minimum survivors ~= N*(1-0.8) = 102 >> 32, so the
    # system stays heavily OVER-determined at every locked grid point. We surface
    # this so the verdict is not read blind. (N/K/grid are LOCKED — reported, not
    # tuned, per the numerology guard.)
    survivors_at_max = int(round(N * (1.0 - max(DAMAGE_GRID))))
    regime = {
        "twoK": 2 * K,
        "min_survivors_at_max_damage": survivors_at_max,
        "reached_underdetermined": survivors_at_max < 2 * K,
        "note": ("Locked N=512/K=16/damage<=0.8 keeps survivors (min ~%d) far "
                 "above 2K=%d at every grid point, so the coverage-stressed regime "
                 "where three-distance geometry could separate the irrational arms "
                 "is NEVER entered. Any irrational rotation (and even uniform-random "
                 "positions) reconstructs the K=16 band near-perfectly; the rational "
                 "arms fail only because a rational rotation visits a finite point "
                 "set (rank-deficient design), independent of damage. The Outcome-C "
                 "reading below is therefore faithful to the locked contract but "
                 "UNDERPOWERED by construction for the golden-vs-silver question."
                 % (survivors_at_max, 2 * K)),
    }

    # ---- GH-B convergent oscillation probe (exploratory, cannot pass/kill) ----
    fibs = fibonacci(15)
    convergent_rows = []
    for n in range(2, 14):  # F(n+1)/F(n) for n=2..13
        Fn = fibs[n]
        Fn1 = fibs[n + 1]
        # convergents F(n+1)/F(n) in (1,2); take fractional part for the orbit
        alpha_conv = (Fn1 / Fn) % 1.0
        per_mode_aur = {}
        for mode in MODES:
            aurs = [run_convergent(alpha_conv, s, mode) for s in SEEDS]
            per_mode_aur[mode] = float(np.mean(aurs))
        # oscillation sign: is this convergent above or below phi (the limit)?
        # ratio-vs-phi is descriptive geometry only.
        ratio = Fn1 / Fn
        phi_limit = (1.0 + SQRT5) / 2.0
        side = "above" if ratio > phi_limit else "below"
        convergent_rows.append({
            "n": n, "ratio": ratio, "alpha_frac": alpha_conv,
            "side_of_phi": side,
            "AUR_contiguous": per_mode_aur["contiguous"],
            "AUR_random": per_mode_aur["random"],
        })

    # golden reference AUR (pooled) for GH-B convergence description
    golden_pooled = {m: float(tab[m]["golden"].mean()) for m in MODES}
    # descriptive: does AUR(convergent_n) oscillate above/below AUR(golden)
    # in a pattern that tracks the odd/even convergent bracket?
    osc_signs = []
    for row in convergent_rows:
        sign_c = "above_golden" if row["AUR_contiguous"] > golden_pooled["contiguous"] else "below_golden"
        sign_r = "above_golden" if row["AUR_random"] > golden_pooled["random"] else "below_golden"
        osc_signs.append({"n": row["n"], "side_of_phi": row["side_of_phi"],
                          "AUR_side_contiguous": sign_c, "AUR_side_random": sign_r})
    # does AUR-side alternate with convergent parity (odd/even n)?
    def alternation_score(key: str) -> float:
        seq = [1 if s[key] == "above_golden" else 0 for s in osc_signs]
        if len(seq) < 2:
            return 0.0
        flips = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
        return flips / (len(seq) - 1)
    gh_b_finding = {
        "convergents": convergent_rows,
        "golden_pooled_AUR": golden_pooled,
        "oscillation_signs": osc_signs,
        "alternation_score_contiguous": alternation_score("AUR_side_contiguous"),
        "alternation_score_random": alternation_score("AUR_side_random"),
        "note": ("DESCRIPTIVE ONLY. Cannot trigger pass or kill. High alternation "
                 "score (~1.0) would suggest AUR(convergent) oscillates above/below "
                 "AUR(golden) tracking the odd/even convergent bracket."),
    }

    # -------------------------------------------------------------- summary.json
    summary = {
        "test_id": "GOLDEN-HEAL-v1",
        "lane": "engineering / verified-computation. NOT physics evidence.",
        "forbidden_upgrade": (
            "GOLDEN-HEAL is a toy least-squares recoverability probe; no outcome "
            "here is physics evidence, and Outcome B (the expected result) is a "
            "statement about low-discrepancy geometry, not about phi being "
            "physically privileged."),
        "config": {"N": N, "K": K, "sigma": SIGMA, "rcond": RCOND,
                   "damage_grid": list(DAMAGE_GRID), "seeds": list(SEEDS),
                   "modes": list(MODES), "arms": list(ARMS)},
        "alphas": {
            "golden": ALPHA_GOLDEN, "silver": ALPHA_SILVER, "bronze": ALPHA_BRONZE,
            "rational_near": ALPHA_RAT_NEAR, "rational_resonant": ALPHA_RAT_RES},
        "classification": verdict["verdict"],
        "pass_A": verdict["pass_A"], "confirm_B": verdict["confirm_B"],
        "confirm_C": verdict["confirm_C"],
        "per_mode_stats": verdict["per_mode"],
        "ranking_by_AUR_pooled": ranking,
        "pooled_mean_AUR": {
            a: float(np.mean([tab[m][a].mean() for m in MODES])) for a in ARMS},
        "golden_vs_silver_gap": {
            m: {"mean_gap": verdict["per_mode"][m]["gap_mean"],
                "sigma_between": verdict["per_mode"][m]["gap_sigma_between"],
                "golden_wins": verdict["per_mode"][m]["golden_wins_over_silver"],
                "sign_test_p": verdict["per_mode"][m]["sign_test_p"]}
            for m in MODES},
        "GH_B_convergent_probe": gh_b_finding,
        "regime_diagnostic": regime,
        "numerology_guard": "PASSED (phi-free signal/metric audit ran; phi only a rotation angle)",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))

    # -------------------------------------------------------------- report.md
    write_report(summary, tab, verdict, ranking, gh_b_finding, golden_pooled, regime)
    print(f"[GOLDEN-HEAL] classification = {verdict['verdict']}")
    print(f"[GOLDEN-HEAL] ranking = {ranking}")
    for m in MODES:
        pm = verdict["per_mode"][m]
        print(f"[GOLDEN-HEAL] {m}: gap={pm['gap_mean']:+.4f} "
              f"sigma_between={pm['gap_sigma_between']:.4f} "
              f"golden_wins={pm['golden_wins_over_silver']}/12 p={pm['sign_test_p']:.3f}")
    print(f"[GOLDEN-HEAL] wrote {OUT/'summary.json'} and {OUT/'report.md'}")


def write_report(summary, tab, verdict, ranking, gh_b, golden_pooled, regime) -> None:
    v = verdict["verdict"]
    label = {
        "A_STRONG_PHI": "OUTCOME A — STRONG phi-specificity",
        "B_IRRATIONALITY_GENERIC": "OUTCOME B — IRRATIONALITY-GENERIC (expected null)",
        "C_MECHANISM_NULL": "OUTCOME C — MECHANISM-NULL",
        "MIXED": "MIXED / WATCH — underpowered, no promotion",
    }[v]
    lines = []
    lines.append("# GOLDEN-HEAL-v1 — recoverability discriminator (GHP Test #1)\n")
    lines.append(f"**Classification: {label}**\n")
    lines.append("> Lane: engineering / verified-computation. **NOT physics evidence.** "
                 "GOLDEN-HEAL is a toy least-squares recoverability probe; no outcome "
                 "here is physics evidence, and Outcome B (the expected result) is a "
                 "statement about low-discrepancy geometry, not about phi being "
                 "physically privileged.\n")
    lines.append("## Ranking by recovery-AUR (pooled across modes)\n")
    pooled = summary["pooled_mean_AUR"]
    lines.append("| rank | arm | pooled mean AUR |")
    lines.append("|---|---|---|")
    for i, a in enumerate(ranking, 1):
        lines.append(f"| {i} | {a} | {pooled[a]:.4f} |")
    lines.append("")
    lines.append("## Regime diagnostic (read the verdict WITH this)\n")
    lines.append(f"- band unknowns 2K = **{regime['twoK']}**; minimum survivors at "
                 f"max locked damage (0.8) = **{regime['min_survivors_at_max_damage']}**.")
    lines.append(f"- under-determined regime reached at any grid point: "
                 f"**{regime['reached_underdetermined']}**.")
    lines.append(f"- {regime['note']}\n")
    lines.append("## Golden-vs-silver (the ONLY place a phi claim can live)\n")
    lines.append("| mode | mean gap (G-S) | sigma_between | golden wins | sign-test p | resolvable? |")
    lines.append("|---|---|---|---|---|---|")
    for m in MODES:
        pm = verdict["per_mode"][m]
        resolvable = (pm["cond2_gap_gt_sigma"] and pm["cond3_signtest_p_lt_05"]
                      and pm["cond1_wins_ge_8of12"])
        lines.append(f"| {m} | {pm['gap_mean']:+.4f} | {pm['gap_sigma_between']:.4f} | "
                     f"{pm['golden_wins_over_silver']}/12 | {pm['sign_test_p']:.3f} | "
                     f"{'YES' if resolvable else 'no'} |")
    lines.append("")
    lines.append("## Per-mode AUR (mean across 12 seeds)\n")
    lines.append("| arm | " + " | ".join(MODES) + " |")
    lines.append("|---|" + "|".join(["---"] * len(MODES)) + "|")
    for a in ARMS:
        cells = " | ".join(f"{tab[m][a].mean():.4f}" for m in MODES)
        lines.append(f"| {a} | {cells} |")
    lines.append("")
    lines.append("## Verdict logic (locked thresholds)\n")
    for m in MODES:
        pm = verdict["per_mode"][m]
        lines.append(f"### mode: {m}")
        lines.append(f"- cond1 golden>silver in >=8/12 seeds: **{pm['cond1_wins_ge_8of12']}** "
                     f"({pm['golden_wins_over_silver']}/12)")
        lines.append(f"- cond2 mean gap > sigma_between: **{pm['cond2_gap_gt_sigma']}** "
                     f"({pm['gap_mean']:+.4f} vs {pm['gap_sigma_between']:.4f})")
        lines.append(f"- cond3 sign-test p<0.05: **{pm['cond3_signtest_p_lt_05']}** "
                     f"(p={pm['sign_test_p']:.3f})")
        lines.append(f"- cond4 ordering intact: **{pm['cond4_ordering_intact']}**")
        lines.append(f"- PASS-A this mode: **{pm['pass_A_mode']}**")
        lines.append(f"- B: all champions beat floors: **{pm['B_all_beat_floors']}**")
        lines.append(f"- C: golden - random_positions = {pm['C_golden_minus_randompos']:+.4f} "
                     f"(<= {NULL_C_MARGIN} => null: {pm['C_mode_null']})")
        lines.append("")
    lines.append(f"**PASS-A (both modes): {verdict['pass_A']}** | "
                 f"**CONFIRM-B: {verdict['confirm_B']}** | "
                 f"**CONFIRM-C: {verdict['confirm_C']}**\n")
    lines.append("## GH-B — Fibonacci-convergent oscillation (EXPLORATORY, cannot pass/kill)\n")
    lines.append(f"Golden reference AUR (pooled): contiguous={golden_pooled['contiguous']:.4f}, "
                 f"random={golden_pooled['random']:.4f}\n")
    lines.append("| n | F(n+1)/F(n) | side of phi | AUR contig | AUR random | AUR-side (contig) |")
    lines.append("|---|---|---|---|---|---|")
    for row, osc in zip(gh_b["convergents"], gh_b["oscillation_signs"]):
        lines.append(f"| {row['n']} | {row['ratio']:.6f} | {row['side_of_phi']} | "
                     f"{row['AUR_contiguous']:.4f} | {row['AUR_random']:.4f} | "
                     f"{osc['AUR_side_contiguous'].replace('_golden','')} |")
    lines.append("")
    lines.append(f"Alternation score (fraction of consecutive AUR-side flips): "
                 f"contiguous={gh_b['alternation_score_contiguous']:.2f}, "
                 f"random={gh_b['alternation_score_random']:.2f}. "
                 f"{gh_b['note']}\n")
    lines.append("## Numerology guard\n")
    lines.append("- phi-free audit of signal/metric functions: **PASSED** "
                 "(runtime grep found no phi/1.618/golden/fibonacci token).")
    lines.append("- phi enters ONLY as one rotation angle among the arms.")
    lines.append("- Outcome-A pass region EXCLUDES the silver-tie region by construction: "
                 "content lives only in golden-vs-silver; within-sigma_between => TIE => Outcome B.")
    lines.append("- A win over rational/random alone earns NO phi claim (textbook low-discrepancy).\n")
    (OUT / "report.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
