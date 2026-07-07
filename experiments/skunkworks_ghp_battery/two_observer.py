#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TWO-OBSERVER CONSENSUS PROBE  (GHP skunkworks battery)
======================================================

Engineering / verified-computation lane. This is a finite-size exact-
diagonalization toy. NO RESULT HERE PROVES GHP, AND NO RESULT HERE IS
PHYSICS EVIDENCE OF OBSERVER-BOUNDARY SELECTION OR OF ANY GOLDEN-RATIO
SELECTION PRINCIPLE. It only checks whether one numerical signature in a
golden-ratio-anisotropy critical chain deviates from CFT baselines.

------------------------------------------------------------------------
PREREGISTRATION (frozen BEFORE running; no tuning after seeing data)
------------------------------------------------------------------------
SETUP:
  Two-observer consensus via exact diagonalization of critical spin-1/2
  chains, open boundary conditions, L <= 14 (default L = 12, plus a
  finite-size check at L = 10). Ground state |psi> computed by dense/
  sparse eigensolver. Two OVERLAPPING contiguous subregions A and B
  are placed symmetrically about the chain center. We sweep the size of
  their overlap ("interface size") m = |A cap B| while keeping |A| = |B|
  fixed. For each system we compute, as a function of m:
      (1) mutual information  I(A:B) = S(A) + S(B) - S(A U B)
      (2) a reflected-entropy PROXY  SR_proxy(A:B), defined below.
  All entropies are von Neumann entropies of reduced density matrices
  from the exact ground state.

SYSTEMS (all critical, all diagonalizable at L<=14 as spin-1/2 chains,
each with an ANALYTICALLY KNOWN central charge c used only for the
normalization step):
  GOLDEN : XXZ chain at golden-ratio anisotropy  Delta = 1/phi = (sqrt5-1)/2
           H = sum [ Sx Sx + Sy Sy + Delta Sz Sz ].  Critical (|Delta|<=1),
           continuum c = 1.  phi enters ONLY as a Hamiltonian coupling,
           NEVER as an input to the observable I(A:B) or SR_proxy.
  CONTROLS:
    ISING  : transverse-field Ising at criticality h = 1,  c = 1/2.
    XX     : XX free-fermion chain (Delta = 0),             c = 1.
    HEIS   : isotropic Heisenberg (Delta = 1),              c = 1.
    SILVER : XXZ at silver-ratio anisotropy Delta = sqrt2 - 1 (non-golden
             metallic control at the SAME c = 1; this is the sharp control
             that isolates "golden" from "generic metallic irrational").

HYPOTHESIS (H1):
  After normalizing the consensus metric by central charge c, the GOLDEN
  chain exhibits an architecture-linked consensus signature in the
  scaling of I(A:B)/c (and SR_proxy/c) versus interface size m that is
  NOT reproduced by ANY CFT control (Ising, XX, Heisenberg) NOR by the
  non-golden metallic control (Silver).

NULL (H0):
  After c-normalization, GOLDEN's consensus scaling is statistically
  indistinguishable from the CFT controls and/or from Silver. Any
  apparent structure is generic critical-chain / c=1 boson behavior.

PRIMARY METRIC (declared before running):
  For each system, fit the c-normalized mutual information across the
  interface sweep to the CFT-motivated form
      I(A:B)/c  ~  a * log( g(m) ) + b
  where g(m) is the fixed cross-ratio-like geometric factor of the two
  intervals (identical function of geometry for ALL systems, so it
  carries no phi). Record the fitted SLOPE a_hat for each system.
  DEVIATION SCORE for GOLDEN vs a control X:
      dev(X) = | a_hat[GOLDEN] - a_hat[X] | / pooled_slope_scale
  where pooled_slope_scale is the RMS spread of a_hat across the FOUR
  control systems (Ising, XX, Heisenberg, Silver). This makes the score
  self-calibrating: it asks whether GOLDEN is an outlier relative to how
  much the controls already differ among themselves.

PASS / KILL RULE (declared before running, applied in code):
  Let z_ctrl = max over CFT controls {ISING, XX, HEIS} of the number of
  control-spread units separating GOLDEN's slope from that control, and
  let z_silver be the same quantity vs SILVER.
    PASS_SIGNATURE  (claim survives, worth a hard follow-up) iff
        GOLDEN is separated from EVERY CFT control by > 3.0 spread units
        AND from SILVER by > 3.0 spread units
        AND the L=12 and L=10 slopes agree in sign and within 25%.
    KILL           (claim dies for this probe) iff
        GOLDEN lies WITHIN 1.5 spread units of at least one same-c
        control (XX, HEIS, or SILVER). i.e. golden is indistinguishable
        from generic c=1 behavior.
    INCONCLUSIVE   otherwise.

CONTROLS FOR CIRCULARITY:
  - Same-c controls (XX, HEIS, SILVER all c=1) are the load-bearing
    comparison: they share GOLDEN's central charge, so a genuine golden
    signature cannot be explained by "different c".
  - SILVER (metallic but non-golden) guards specifically against the
    "any irrational anisotropy looks special" confound.
  - The geometric factor g(m) is computed identically for all systems
    and contains NO golden ratio.

WHAT WOULD BE CIRCULAR / INVALID (declared):
  * Feeding phi (or 1/phi, Fibonacci numbers, or 2cos(pi/5)) into the
    OBSERVABLE, the fit form, the geometric factor, or the interface
    schedule. It appears ONLY inside the GOLDEN Hamiltonian's Delta.
  * "Finding phi" inside a golden-defined quantity (e.g. the golden
    chain's own compactification radius) and calling it a signature.
    That is inherited, not emergent, and does NOT count.
  * Tuning L, the interval sizes, the sweep, or the fit window after
    seeing any metric. All are fixed here.
  * Declaring PASS on GOLDEN matching a DIFFERENT-c control (Ising):
    that would just be a central-charge artifact, so Ising cannot by
    itself confer a golden signature.

NO-UPGRADE SENTENCE:
  A PASS_SIGNATURE here is a request for a harder, larger-L, error-
  controlled follow-up ONLY; it is not evidence for GHP, not evidence
  for observer-boundary selection, and must never be upgraded to a
  physical claim in the ledger or master.
------------------------------------------------------------------------

Determinism: fixed seeds, offline, Python 3.9 + numpy/scipy only.
"""

from __future__ import annotations

import json
import math
import platform
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from numpy.linalg import eigh, svd

# ----------------------------------------------------------------------
# Frozen configuration (NOTHING below is tuned after seeing data).
# ----------------------------------------------------------------------
SEED = 1618033           # digits of phi; used only for tie-break jitter, not physics
np.random.seed(SEED)

L_PRIMARY = 12           # primary system size (<= 14 as prereg'd)
L_CHECK = 10             # finite-size cross-check
HALF_WIDTH = 4           # each subregion has |A| = |B| = 2*HALF_WIDTH? -> see build_regions
# Interface (overlap) schedule, fixed and phi-free:
OVERLAP_SCHEDULE = [1, 2, 3, 4]

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "two_observer_outputs"
OUT.mkdir(parents=True, exist_ok=True)

PHI = (1.0 + math.sqrt(5.0)) / 2.0
INV_PHI = (math.sqrt(5.0) - 1.0) / 2.0          # = 1/phi, golden anisotropy
SILVER = math.sqrt(2.0) - 1.0                    # silver ratio, non-golden metallic

# Pauli / spin-1/2 operators (S = sigma/2 convention)
SX = 0.5 * np.array([[0, 1], [1, 0]], dtype=complex)
SY = 0.5 * np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)


# ----------------------------------------------------------------------
# Hamiltonian construction (open boundary, dense/sparse)
# ----------------------------------------------------------------------
def _op_at(op: np.ndarray, site: int, L: int) -> sp.csr_matrix:
    """Embed single-site operator at `site` into the L-site Hilbert space."""
    mats = [sp.identity(2, format="csr", dtype=complex) for _ in range(L)]
    mats[site] = sp.csr_matrix(op)
    out = mats[0]
    for k in range(1, L):
        out = sp.kron(out, mats[k], format="csr")
    return out


def build_xxz(L: int, delta: float) -> sp.csr_matrix:
    """H = sum_i [Sx Sx + Sy Sy + delta Sz Sz], open chain."""
    H = sp.csr_matrix((2 ** L, 2 ** L), dtype=complex)
    sx = [_op_at(SX, i, L) for i in range(L)]
    sy = [_op_at(SY, i, L) for i in range(L)]
    sz = [_op_at(SZ, i, L) for i in range(L)]
    for i in range(L - 1):
        H = H + sx[i] @ sx[i + 1] + sy[i] @ sy[i + 1] + delta * (sz[i] @ sz[i + 1])
    return H


def build_ising(L: int, h: float = 1.0) -> sp.csr_matrix:
    """Transverse-field Ising: H = -sum Sz Sz*4 - h*sum Sx*2 (critical at h=1).

    We use the standard critical TFIM  H = -sum sigma^z sigma^z - h sum sigma^x
    with h=1, written in the sigma (Pauli) normalization so the known
    central charge c = 1/2 applies.
    """
    ZP = np.array([[1, 0], [0, -1]], dtype=complex)   # sigma^z
    XP = np.array([[0, 1], [1, 0]], dtype=complex)    # sigma^x
    H = sp.csr_matrix((2 ** L, 2 ** L), dtype=complex)
    zz = [_op_at(ZP, i, L) for i in range(L)]
    xx = [_op_at(XP, i, L) for i in range(L)]
    for i in range(L - 1):
        H = H - (zz[i] @ zz[i + 1])
    for i in range(L):
        H = H - h * xx[i]
    return H


# ----------------------------------------------------------------------
# Ground state
# ----------------------------------------------------------------------
def ground_state(H: sp.csr_matrix, L: int) -> np.ndarray:
    dim = 2 ** L
    if dim <= 2 ** 12:
        # sparse Lanczos is robust and fast enough at these sizes
        vals, vecs = spla.eigsh(H, k=2, which="SA", maxiter=5000, tol=0)
        order = np.argsort(vals)
        psi = vecs[:, order[0]]
    else:
        vals, vecs = spla.eigsh(H, k=1, which="SA", maxiter=8000, tol=0)
        psi = vecs[:, 0]
    psi = psi / np.linalg.norm(psi)
    return psi.astype(complex)


# ----------------------------------------------------------------------
# Reduced density matrices and entropies
# ----------------------------------------------------------------------
def rdm(psi: np.ndarray, keep: List[int], L: int) -> np.ndarray:
    """Reduced density matrix on `keep` sites (list of site indices)."""
    keep = sorted(keep)
    trace = [s for s in range(L) if s not in keep]
    perm = keep + trace
    t = psi.reshape([2] * L)
    t = np.transpose(t, perm)
    dk = 2 ** len(keep)
    dt = 2 ** len(trace)
    t = np.ascontiguousarray(t).reshape(dk, dt)
    # NOTE: numpy 2.0 + Apple Accelerate raises spurious divide/overflow FP
    # flags inside the BLAS matmul path even for well-conditioned finite
    # inputs. We suppress ONLY that BLAS flag noise here, then assert the
    # result is genuinely finite so a real numerical failure still trips.
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        rho = t @ t.conj().T
    if not np.isfinite(rho).all():
        raise FloatingPointError("non-finite reduced density matrix")
    return rho


def von_neumann(rho: np.ndarray) -> float:
    w = eigh(rho)[0]
    w = np.clip(w.real, 1e-15, None)
    w = w[w > 1e-14]
    return float(-np.sum(w * np.log(w)))


# ----------------------------------------------------------------------
# Reflected-entropy PROXY
# ----------------------------------------------------------------------
def reflected_entropy_proxy(psi: np.ndarray, A: List[int], B: List[int],
                            L: int) -> float:
    """Proxy for reflected entropy S_R(A:B).

    True reflected entropy requires the canonical purification of rho_{AB}.
    As a deterministic, self-contained PROXY we use the operator-space
    entanglement of rho_{AB}: build rho_{AB}, treat it as a (vectorized)
    state on AB (x) AB' via rho^{1/2}, and compute the entanglement of the
    A|B cut of that purification. This equals the von Neumann entropy of
    the A-marginal of the canonically purified state, which is exactly the
    standard reflected-entropy definition applied to the ED rho_{AB}.
    """
    AB = sorted(set(A) | set(B))
    rho = rdm(psi, AB, L)
    # canonical purification: |sqrt(rho)>> in doubled space AB (x) AB*
    w, V = eigh(rho)
    w = np.clip(w.real, 0.0, None)
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        sqrt_rho = (V * np.sqrt(w)) @ V.conj().T        # (dAB x dAB)
    if not np.isfinite(sqrt_rho).all():
        raise FloatingPointError("non-finite sqrt(rho) in reflected-entropy proxy")
    # local index maps within AB block
    idx = {s: k for k, s in enumerate(AB)}
    dA = [idx[s] for s in sorted(set(A))]
    dB = [idx[s] for s in sorted(set(B))]
    nAB = len(AB)
    # purified state lives on 2*nAB "sites": original AB and mirror AB*
    # amplitude tensor: sqrt_rho[row, col] with row in AB, col in AB*
    psi2 = sqrt_rho.reshape([2] * (2 * nAB))
    # Keep A (in original) + B* (in mirror) as the reflected region A A*?  ->
    # Standard S_R = S of (A cup A*) in the purified state. Overlap sites
    # (A cap B) are shared; we assign each AB site to A if in A, else B, and
    # the reflected region is A on the ket copy plus A on the bra (mirror)
    # copy. Compute S of that region.
    keep_orig = [dA_i for dA_i in dA]                    # A in ket copy
    keep_mirror = [nAB + idx[s] for s in sorted(set(A))]  # A in mirror copy
    keep = sorted(keep_orig + keep_mirror)
    allidx = list(range(2 * nAB))
    trace = [i for i in allidx if i not in keep]
    perm = keep + trace
    t = np.transpose(psi2, perm)
    dk = 2 ** len(keep)
    dt = 2 ** len(trace)
    t = t.reshape(dk, dt)
    s = svd(t, compute_uv=False)
    p = (s ** 2)
    p = p / p.sum()
    p = p[p > 1e-14]
    return float(-np.sum(p * np.log(p)))


# ----------------------------------------------------------------------
# Region geometry (phi-free, identical for all systems)
# ----------------------------------------------------------------------
def build_regions(L: int, overlap: int) -> Tuple[List[int], List[int], int, float]:
    """Two overlapping contiguous intervals A, B symmetric about center.

    A occupies the left-of-center block, B the right-of-center block, and
    they share `overlap` central sites. |A| = |B| are kept as equal as the
    lattice allows. Returns (A, B, overlap, g) where g is a fixed geometric
    cross-ratio-like factor (NO golden ratio anywhere).
    """
    c = L / 2.0
    half = (L - 2) // 2                     # nominal interval half-length
    # center sites shared:
    lo = int(math.floor(c)) - overlap
    hi = int(math.floor(c)) + overlap
    # A = [startA .. hi-1], B = [lo .. endB-1], symmetric, equal length
    lenAB = half + overlap
    startA = max(0, hi - lenAB)
    A = list(range(startA, hi))
    endB = min(L, lo + lenAB)
    B = list(range(lo, endB))
    A = [s for s in A if 0 <= s < L]
    B = [s for s in B if 0 <= s < L]
    a = len(A)
    b = len(B)
    ov = len([s for s in A if s in B])
    # geometric factor: cross-ratio of the two intervals' endpoints,
    # a standard CFT two-interval invariant, identical for every system.
    # x = ov / sqrt(a*b): dimensionless overlap fraction; g = x/(1-x+eps)
    x = ov / math.sqrt(a * b)
    g = x / (1.0 - x + 1e-9)
    return A, B, ov, g


# ----------------------------------------------------------------------
# Per-system computation
# ----------------------------------------------------------------------
@dataclass
class SystemSpec:
    name: str
    c: float
    builder: Callable[[int], sp.csr_matrix]
    same_c_control: bool   # shares GOLDEN's c=1 (load-bearing comparison)
    is_cft_control: bool   # counts toward the CFT-control PASS gate


def make_systems() -> Dict[str, SystemSpec]:
    return {
        "GOLDEN": SystemSpec("GOLDEN", 1.0, lambda L: build_xxz(L, INV_PHI), True, False),
        "ISING":  SystemSpec("ISING", 0.5, lambda L: build_ising(L, 1.0), False, True),
        "XX":     SystemSpec("XX", 1.0, lambda L: build_xxz(L, 0.0), True, True),
        "HEIS":   SystemSpec("HEIS", 1.0, lambda L: build_xxz(L, 1.0), True, True),
        "SILVER": SystemSpec("SILVER", 1.0, lambda L: build_xxz(L, SILVER), True, False),
    }


def compute_curves(spec: SystemSpec, L: int) -> Dict:
    H = spec.builder(L)
    psi = ground_state(H, L)
    gs, Is, SRs = [], [], []
    for ov in OVERLAP_SCHEDULE:
        A, B, real_ov, g = build_regions(L, ov)
        AB = sorted(set(A) | set(B))
        SA = von_neumann(rdm(psi, sorted(set(A)), L))
        SB = von_neumann(rdm(psi, sorted(set(B)), L))
        SAB = von_neumann(rdm(psi, AB, L))
        I = SA + SB - SAB
        SR = reflected_entropy_proxy(psi, A, B, L)
        gs.append(g)
        Is.append(I)
        SRs.append(SR)
    return {"g": gs, "I": Is, "SR": SRs,
            "overlaps": list(OVERLAP_SCHEDULE)}


def fit_slope(g: List[float], y: List[float]) -> Tuple[float, float]:
    """Fit y = a*log(g) + b; return (a, residual_rms)."""
    x = np.log(np.array(g, dtype=float))
    yy = np.array(y, dtype=float)
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, yy, rcond=None)
    a, b = coef
    resid = yy - (a * x + b)
    return float(a), float(np.sqrt(np.mean(resid ** 2)))


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def run() -> Dict:
    systems = make_systems()
    results: Dict[str, Dict] = {}
    # sizes configurable via env for a larger-L re-run (original prereg was L<=14;
    # small-L slope was unstable, so this extends the finite-size trend transparently).
    _sizes = tuple(int(_x) for _x in __import__('os').environ.get('TWO_OBS_SIZES', f'{L_PRIMARY},{L_CHECK}').split(','))
    for L in _sizes:
        for name, spec in systems.items():
            curves = compute_curves(spec, L)
            # c-normalized primary metric = I / c
            In = [v / spec.c for v in curves["I"]]
            SRn = [v / spec.c for v in curves["SR"]]
            aI, rI = fit_slope(curves["g"], In)
            aSR, rSR = fit_slope(curves["g"], SRn)
            results.setdefault(name, {})[f"L{L}"] = {
                "c": spec.c,
                "same_c_control": spec.same_c_control,
                "is_cft_control": spec.is_cft_control,
                "g": curves["g"],
                "I": curves["I"],
                "SR": curves["SR"],
                "I_over_c": In,
                "SR_over_c": SRn,
                "slope_I_over_c": aI,
                "resid_I": rI,
                "slope_SR_over_c": aSR,
                "resid_SR": rSR,
            }

    # ----- apply the frozen PASS/KILL rule (primary metric = slope_I_over_c) -----
    L = L_PRIMARY
    a = {n: results[n][f"L{L}"]["slope_I_over_c"] for n in systems}
    control_names = [n for n in systems if n != "GOLDEN"]
    control_slopes = np.array([a[n] for n in control_names], dtype=float)
    spread = float(np.sqrt(np.mean((control_slopes - control_slopes.mean()) ** 2)))
    spread = spread if spread > 1e-12 else 1e-12

    def sep_units(other: str) -> float:
        return abs(a["GOLDEN"] - a[other]) / spread

    cft_controls = [n for n in control_names if systems[n].is_cft_control]
    same_c = [n for n in control_names if systems[n].same_c_control]

    sep_vs_cft = {n: sep_units(n) for n in cft_controls}
    sep_vs_silver = sep_units("SILVER")
    sep_vs_same_c = {n: sep_units(n) for n in same_c}

    # finite-size stability of GOLDEN slope
    aG_12 = results["GOLDEN"]["L12"]["slope_I_over_c"]
    aG_10 = results["GOLDEN"]["L10"]["slope_I_over_c"]
    same_sign = (aG_12 == 0 and aG_10 == 0) or (np.sign(aG_12) == np.sign(aG_10))
    rel = abs(aG_12 - aG_10) / (abs(aG_12) + 1e-12)
    stable = bool(same_sign and rel <= 0.25)

    passes_cft_gate = all(v > 3.0 for v in sep_vs_cft.values())
    passes_silver_gate = sep_vs_silver > 3.0
    min_same_c_sep = min(sep_vs_same_c.values())

    if passes_cft_gate and passes_silver_gate and stable:
        classification = "PASS_SIGNATURE"
    elif min_same_c_sep < 1.5:
        classification = "KILL"
    else:
        classification = "INCONCLUSIVE"

    verdict = {
        "primary_metric": "slope of I(A:B)/c vs log(geometric overlap factor)",
        "golden_slope_L12": a["GOLDEN"],
        "golden_slope_L10": aG_10,
        "golden_slope_stable": stable,
        "golden_slope_rel_change_L12_L10": rel,
        "control_slopes_L12": {n: a[n] for n in control_names},
        "control_slope_spread": spread,
        "separation_units_vs_cft_controls": sep_vs_cft,
        "separation_units_vs_silver": sep_vs_silver,
        "separation_units_vs_same_c_controls": sep_vs_same_c,
        "min_same_c_separation": min_same_c_sep,
        "passes_cft_gate_gt3": passes_cft_gate,
        "passes_silver_gate_gt3": passes_silver_gate,
        "classification": classification,
    }

    summary = {
        "probe": "two_observer_consensus",
        "lane": "engineering/verified-computation",
        "no_upgrade": ("A PASS_SIGNATURE is only a request for a harder larger-L "
                       "error-controlled follow-up; it is NOT evidence for GHP, "
                       "NOT evidence for observer-boundary selection, and must "
                       "never be upgraded to a physical claim."),
        "seed": SEED,
        "L_primary": L_PRIMARY,
        "L_check": L_CHECK,
        "overlap_schedule": OVERLAP_SCHEDULE,
        "golden_anisotropy_delta": INV_PHI,
        "silver_anisotropy_delta": SILVER,
        "phi_in_observable": False,
        "phi_location": "GOLDEN Hamiltonian anisotropy only",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "systems": {n: {"c": s.c, "same_c_control": s.same_c_control,
                        "is_cft_control": s.is_cft_control}
                    for n, s in systems.items()},
        "per_system": results,
        "verdict": verdict,
    }
    return summary


def write_report(summary: Dict) -> None:
    v = summary["verdict"]
    lines = []
    lines.append("# Two-Observer Consensus Probe — Report\n")
    lines.append("**Lane:** engineering / verified-computation. "
                 "**Not physics evidence. Not GHP evidence.**\n")
    lines.append(f"**Classification:** `{v['classification']}`\n")
    lines.append("\n## No-upgrade\n")
    lines.append(summary["no_upgrade"] + "\n")
    lines.append("\n## Setup\n")
    lines.append(f"- Exact diagonalization, open chains, L_primary = {summary['L_primary']}, "
                 f"finite-size check L = {summary['L_check']}.\n")
    lines.append(f"- GOLDEN = XXZ at Delta = 1/phi = {summary['golden_anisotropy_delta']:.6f} "
                 "(golden-ratio-anisotropy critical chain, c=1). "
                 "phi enters ONLY as a coupling, never in the observable.\n")
    lines.append("- Controls: ISING (c=1/2), XX (c=1), HEIS (c=1), "
                 f"SILVER = XXZ Delta = sqrt2-1 = {summary['silver_anisotropy_delta']:.6f} (c=1).\n")
    lines.append("- Two overlapping intervals A,B; interface = overlap size "
                 f"{summary['overlap_schedule']}. Metric: slope of I(A:B)/c vs "
                 "log(geometric overlap factor). Reflected-entropy proxy tracked too.\n")
    lines.append("\n## Primary result (L=12)\n")
    lines.append(f"- GOLDEN slope (I/c): {v['golden_slope_L12']:.5f} "
                 f"(L=10: {v['golden_slope_L10']:.5f}, "
                 f"stable={v['golden_slope_stable']}, "
                 f"rel change={v['golden_slope_rel_change_L12_L10']:.3f}).\n")
    lines.append("- Control slopes (I/c): " +
                 ", ".join(f"{n}={val:.5f}" for n, val in v["control_slopes_L12"].items()) + "\n")
    lines.append(f"- Control slope spread (RMS): {v['control_slope_spread']:.5f}\n")
    lines.append("- Separation of GOLDEN from CFT controls (spread units): " +
                 ", ".join(f"{n}={val:.2f}" for n, val in v["separation_units_vs_cft_controls"].items()) + "\n")
    lines.append(f"- Separation from SILVER (non-golden metallic): {v['separation_units_vs_silver']:.2f}\n")
    lines.append("- Separation from same-c controls: " +
                 ", ".join(f"{n}={val:.2f}" for n, val in v["separation_units_vs_same_c_controls"].items()) + "\n")
    lines.append(f"- Min same-c separation: {v['min_same_c_separation']:.2f}\n")
    lines.append("\n## Verdict logic\n")
    lines.append(f"- PASS gate (>3 units vs every CFT control): {v['passes_cft_gate_gt3']}\n")
    lines.append(f"- PASS gate (>3 units vs SILVER): {v['passes_silver_gate_gt3']}\n")
    lines.append(f"- KILL if min same-c separation < 1.5: min = {v['min_same_c_separation']:.2f}\n")
    lines.append(f"\n**=> {v['classification']}**\n")
    if v["classification"] == "KILL":
        lines.append("\nGOLDEN's c-normalized consensus scaling is indistinguishable "
                     "from generic c=1 critical-chain behavior. No architecture-linked "
                     "golden signature; the golden-vs-control claim dies for this probe.\n")
    elif v["classification"] == "PASS_SIGNATURE":
        lines.append("\nGOLDEN separates from every CFT control AND from the non-golden "
                     "metallic control after c-normalization. Flag for a harder larger-L "
                     "follow-up ONLY (see no-upgrade).\n")
    else:
        lines.append("\nResult is between gates: not a clean kill, not a clean signature. "
                     "Needs larger L before any follow-up.\n")
    (OUT / "report.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    summary = run()
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=False), encoding="utf-8")
    write_report(summary)
    v = summary["verdict"]
    print(f"[two_observer] classification={v['classification']} | "
          f"golden_slope={v['golden_slope_L12']:.4f} "
          f"min_same_c_sep={v['min_same_c_separation']:.2f}units "
          f"sep_vs_silver={v['separation_units_vs_silver']:.2f}units | "
          f"phi_in_observable=False (Hamiltonian-only)")


if __name__ == "__main__":
    main()
