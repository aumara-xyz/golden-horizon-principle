#!/usr/bin/env python3
"""
SYK-CORRIDOR-v1 laptop pipeline — PRELIMINARY-LAPTOP / PIPELINE-VALIDATION run.

Governing contract (SIGNED, byte-frozen; this script must never modify it):
  experiments/SYK_CORRIDOR_PREREG_v1.md
  sha256 59a46ff9b19b05b6c99dd0a58fb14629aecb11e0e5c2a94662e465820843f3d0
Sole verdict bookkeeper (byte-frozen; imported, never reimplemented):
  experiments/op179_nu_to_beta.py
  sha256 b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e

WHAT THIS RUN IS AND IS NOT
---------------------------
- The prereg pins the PRIMARY route as DIRECT-BETA (prereg section 3.1): measure the
  revival degradation rate Gamma(d) per master section 5.7, fit log Gamma vs log d
  (d ~ 2^N per the master 5.10A.1 glossary, as the prereg pins), extrapolate per
  prereg section 2, and apply the beta buckets of op179_nu_to_beta.py DIRECTLY
  (beta_bucket_point / beta_bucket_ci). The nu-route is CLOSED: the
  ChannelExponentAssignment port stays UNFILLED, nu_to_beta_verdict is never called,
  and m1_quotient_confirmation_flag is never called (prereg sections 3.2 and 4).
- The prereg pins the compute venue as Nebius (prereg section 5). This run executes
  the identical exact-diagonalization computation on a laptop. Exact diagonalization
  is venue-independent arithmetic, but because the venue field is pinned, THIS RUN
  IS NOT THE CERTIFIED CORRIDOR RUN. Everything it emits is labeled
  PRELIMINARY-LAPTOP / PIPELINE-VALIDATION. No SYK number from this run may be
  reported as GHP support in either direction (prereg section 6).
- The "repaired SYK/C3 pipeline (twelve scripts)" named in the prereg runtime line is
  NOT present in this repository (master Addendum U.4 locates it under
  `.epsilon/reports/syk_mass_transition_*` / `scripts/syk_mass_transition.py`, an
  external tree). This file is a rebuild, not a modification of that pipeline.

PINNED BY THE CONTRACT (verbatim sources quoted in the prereg; do not change):
  P-1  Official sizes N in {14, 18, 22}; N = 10 telemetry only (fit ban CARRIED).
  P-2  kappa grid [0, 15.8, 16.2, 16.4, 16.6, 16.7, 16.8, 16.85, 16.9, 16.95,
       17.0, 17.1, 17.2, 17.5, 18.0]; fitted crossing must be strictly interior
       with >= 2 grid points each side, else VOID.
  P-3  40 disorder seeds per size, explicit range 5000-5039 inclusive.
  P-4  Bootstrap: 2000 resamples everywhere; nu search interval [0.30, 1.50];
       fitted nu strictly interior; <= 5% bootstrap mass in the outermost grid
       cell at either edge, else DEGENERATE -> not certifiable.
  P-5  Convergence: per-size collapse R^2 >= 0.98; cross-size collapse
       correlation >= 0.99.
  P-6  Finite-size acceptance: primary linear fit in 1/N over official sizes,
       bootstrap uncertainty on the extrapolated intercept, applied to the
       direct-beta fit slope and identically to the nu telemetry lane.
  P-7  d ~ 2^N (master 5.10A.1 glossary) for the primary log Gamma vs log d fit.
  P-8  J_ijkl Gaussian with variance 6 J^2 / N^3, J = 1 (master 5.10 pseudocode
       "variance = 6 J^2 / N^3"; U.4 j4_scale = 1.0).
  P-9  Even-parity sector (boundary v2 section 6.3).
  P-10 Verdict bookkeeping only via op179_nu_to_beta.py bucket functions.

IMPLEMENTATION CHOICES (IC) — disclosed, NOT pinned by any repo source. The master
explicitly delegates these ("It does not fix the low-level implementation (random
couplings generator, 4-body-term construction, scaling-fit function); those are
standard numerical-linear-algebra choices left to the implementer", section 5.10).
Each is a certification caveat; a certified run must either ratify or re-pin them:
  IC-1 Majorana representation: Jordan-Wigner, {psi_a, psi_b} = delta_ab
       (psi^2 = 1/2), N/2 qubits, Hilbert dim 2^(N/2), even-parity sector
       dim 2^(N/2 - 1).
  IC-2 Mass term: H2 = i * sum_{i<j} K_ij psi_i psi_j with K_ij Gaussian,
       variance kappa^2 / N (the standard SYK_2 normalization; j2_scale = 1.0
       per U.4). The lost .epsilon convention that placed the crossing near
       kappa ~ 16.9 could not be recovered from the repo; a 6-seed calibration
       pilot (seeds 1-6, outside the pinned range, discarded) showed every
       standard convention drifts the crossover with N. The pinned mechanical
       bracketing / degeneracy rules adjudicate the consequence.
  IC-3 Gamma operationalization: the repo defines Gamma only by its scaling law
       ("Revival degradation rate: Gamma ~ 1/d^beta", master 5.7; "revival
       proportional to 1/d^beta_crit", 5.10A.1). Operational definition used
       here: Gamma := fitted linear slope of the disorder-averaged normalized
       spectral form factor g(t) = |Tr e^{-iHt}|^2 / d_sector^2 in its ramp
       window (between dip and plateau). Under GUE universality the ramp is
       g_c(t) ~ t / (d_sector * t_H), i.e. Gamma_GUE ~ 1/d_sector^2 up to the
       slowly-varying many-body bandwidth — reproducing the pinned
       assignment-independent standard null beta_crit = 2 (Fermi golden rule
       under GUE, master 5.10A.1) when d is the sector Hilbert dimension.
       The SFF is the object master 5.7 names as "The test".
  IC-4 kappa at which Gamma is measured: the sources pin no kappa for the
       direct-beta observable. Primary column: kappa = 0 (the undeformed SYK_4
       point of the pinned grid — the Module C chaotic observer, and the point
       where the GUE standard null applies). beta(kappa) is reported at every
       pinned grid point as telemetry; if the crossing fit is valid, beta at
       the grid point nearest the fitted crossing is reported alongside.
  IC-5 Per-size beta for the pinned 1/N extrapolation: pairwise log-log slopes
       between consecutive official sizes, assigned to the pair midpoint N
       (the only per-size direct-beta slope constructible from three sizes
       without inventing an intra-size d variation).
  IC-6 Collapse observable: mean adjacent-gap ratio <r> (central 50% of the
       sector spectrum), the standard unfolding-free spectral-transition
       statistic (GUE ~ 0.5996, Poisson ~ 0.3863); collapse ansatz
       r(N, kappa) = f((kappa - kappa_c) * N^(1/nu)) with a cubic master curve,
       fitted over the 14 pinned grid points kappa >= 15.8 (kappa = 0 is the
       pure-SYK4 reference point).
  IC-7 Ramp-window detection constants and the SFF time grid (documented at the
       function definitions below); windows are frozen from the full-sample
       mean curve and reused unchanged for every bootstrap resample.

GOLDEN-RATIO DISCIPLINE: this file contains no golden-ratio numeric literals
(neither the ratio nor its reciprocal); all band arithmetic is imported from
op179_nu_to_beta.py, which derives its constants algebraically.

Run:  python3 pipeline.py            (self-tests, full pinned sweep, analysis)
      python3 pipeline.py --selftest (self-tests only)
Outputs: results_laptop.json (this directory).
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # experiments/
import op179_nu_to_beta as op179  # noqa: E402  (P-10: sole verdict bookkeeper)

# ----------------------------------------------------------------------------
# Pinned constants (P-1 .. P-7). Do not edit without a new signed prereg.
# ----------------------------------------------------------------------------
KAPPA_GRID = [0.0, 15.8, 16.2, 16.4, 16.6, 16.7, 16.8, 16.85, 16.9, 16.95,
              17.0, 17.1, 17.2, 17.5, 18.0]                      # P-2
COLLAPSE_KAPPAS = KAPPA_GRID[1:]                                  # IC-6
OFFICIAL_N = [14, 18, 22]                                         # P-1
TELEMETRY_N = [10]                                                # P-1
SEEDS = list(range(5000, 5040))                                   # P-3
N_BOOT = 2000                                                     # P-4
NU_LO, NU_HI, NU_STEP = 0.30, 1.50, 0.01                          # P-4
EDGE_MASS_MAX = 0.05                                              # P-4
R2_MIN = 0.98                                                     # P-5
XCORR_MIN = 0.99                                                  # P-5
GUE_R = 0.5996          # reference value, diagnostics only
POISSON_R = 0.3863      # reference value, diagnostics only

# ----------------------------------------------------------------------------
# Majorana SYK4 + random 2-fermion mass, exact, even-parity sector (IC-1/IC-2)
# ----------------------------------------------------------------------------

def majorana_perm_reps(N: int):
    """Jordan-Wigner Majoranas as row-permutation reps (col, val):
    M[r, col[r]] = val[r].  Convention {psi_a, psi_b} = delta_ab."""
    Q = N // 2
    dim = 1 << Q
    b = np.arange(dim)
    reps = []
    for k in range(Q):
        pc = np.zeros(dim, dtype=np.int64)
        for j in range(k):
            pc += (b >> j) & 1
        zpar = 1.0 - 2.0 * (pc % 2)
        bit = (b >> k) & 1
        col = b ^ (1 << k)
        inv_sqrt2 = 1.0 / np.sqrt(2.0)
        reps.append((col, zpar * inv_sqrt2 + 0j))                       # X-type
        reps.append((col, zpar * (1j * (2.0 * bit - 1.0)) * inv_sqrt2))  # Y-type
    return reps


def _compose(repA, repB):
    colA, valA = repA
    colB, valB = repB
    return (colB[colA], valA * valB[colA])


class TermCache:
    """Precomputed permutation reps of all i<j pair products and i<j<k<l quads
    for one N, plus flattened index/value arrays for fast dense accumulation."""

    def __init__(self, N: int):
        self.N = N
        self.dim = 1 << (N // 2)
        reps = majorana_perm_reps(N)
        pair_reps = {}
        for i, j in combinations(range(N), 2):
            pair_reps[(i, j)] = _compose(reps[i], reps[j])
        self.pair_idx = list(combinations(range(N), 2))
        self.quad_idx = list(combinations(range(N), 4))
        rows = np.arange(self.dim, dtype=np.int64)

        def flatten(term_list):
            n_t = len(term_list)
            flat = np.empty((n_t, self.dim), dtype=np.int64)
            vals = np.empty((n_t, self.dim), dtype=np.complex128)
            for t, (col, val) in enumerate(term_list):
                flat[t] = rows * self.dim + col
                vals[t] = val
            return flat.ravel(), vals

        quads = [_compose(pair_reps[(i, j)], pair_reps[(k, l)])
                 for (i, j, k, l) in self.quad_idx]
        self.quad_flat, self.quad_vals = flatten(quads)
        self.pair_flat, self.pair_vals = flatten(
            [pair_reps[p] for p in self.pair_idx])

        b = np.arange(self.dim)
        pc = np.zeros(self.dim, dtype=np.int64)
        for j in range(N // 2):
            pc += (b >> j) & 1
        self.even = np.where(pc % 2 == 0)[0]

    def _accumulate(self, flat, vals, coeffs):
        w = (coeffs[:, None] * vals).ravel()
        d2 = self.dim * self.dim
        Hr = np.bincount(flat, weights=w.real, minlength=d2)
        Hi = np.bincount(flat, weights=w.imag, minlength=d2)
        return (Hr + 1j * Hi).reshape(self.dim, self.dim)

    def build(self, seed: int):
        """Draw one disorder realization (P-8, IC-2 unit-variance mass base).
        Returns (H4_even, H2unit_even); H(kappa) = H4 + (kappa/sqrt(N)) H2unit."""
        rng = np.random.default_rng([seed, self.N])
        J = rng.normal(0.0, math.sqrt(6.0 / self.N ** 3), size=len(self.quad_idx))
        K = rng.normal(0.0, 1.0, size=len(self.pair_idx))
        H4 = self._accumulate(self.quad_flat, self.quad_vals, J)
        H2u = self._accumulate(self.pair_flat, 1j * self.pair_vals, K)
        ix = np.ix_(self.even, self.even)
        return H4[ix], H2u[ix]

    def mass_scale(self, kappa: float) -> float:
        return kappa / math.sqrt(self.N)          # IC-2: var kappa^2 / N


# ----------------------------------------------------------------------------
# Observables
# ----------------------------------------------------------------------------

def r_stat(E: np.ndarray, frac: float = 0.5) -> float:
    """Mean adjacent-gap ratio over the central `frac` of the sorted spectrum
    (IC-6). Unfolding-free."""
    E = np.sort(E)
    n = len(E)
    lo = int(n * (0.5 - frac / 2.0))
    hi = int(n * (0.5 + frac / 2.0))
    d = np.diff(E[lo:hi])
    return float(np.mean(np.minimum(d[:-1], d[1:]) / np.maximum(d[:-1], d[1:])))


def sff_curves(spectra: np.ndarray, times: np.ndarray) -> np.ndarray:
    """Per-seed normalized SFF g(t) = |sum_n e^{-i E_n t}|^2 / d^2 (IC-3)."""
    d = spectra.shape[1]
    phase = np.exp(-1j * spectra[:, :, None] * times[None, None, :])
    tr = phase.sum(axis=1)
    return (np.abs(tr) ** 2) / (d * d)


def make_time_grid(spectra: np.ndarray, n_t: int = 240):
    """Log-spaced grid from 0.05/sigma_E to 5 * t_H (IC-7).
    t_H = 2*pi / (mean central level spacing)."""
    sig = float(np.mean(np.std(spectra, axis=1)))
    d = spectra.shape[1]
    lo = int(d * 0.25)
    hi = int(d * 0.75)
    Es = np.sort(spectra, axis=1)
    delta = float(np.mean((Es[:, hi] - Es[:, lo]) / (hi - lo)))
    t_H = 2.0 * math.pi / delta
    t = np.geomspace(0.05 / sig, 5.0 * t_H, n_t)
    return t, t_H


def ramp_window(g_mean: np.ndarray, times: np.ndarray, t_H: float, d: int):
    """Mechanical dip/ramp/plateau detection on the full-sample mean SFF (IC-7).
    Frozen and reused for every bootstrap resample.
    Returns (i0, i1, info) — index window for the linear ramp fit."""
    w = 7  # log-time smoothing width (points)
    kern = np.ones(w) / w
    gs = np.convolve(g_mean, kern, mode="same")
    plateau = 1.0 / d  # analytic long-time average for a non-degenerate spectrum
    pre = times < t_H
    if not np.any(pre):
        pre = np.ones_like(times, dtype=bool)
    i_dip = int(np.argmin(np.where(pre, gs, np.inf)))
    t_dip = times[i_dip]
    above = np.where((times > t_dip) & (gs >= 0.6 * plateau))[0]
    i_end = int(above[0]) if len(above) else len(times) - 1
    i_start = int(np.searchsorted(times, 1.5 * t_dip))
    if i_end - i_start < 5:                       # fallback: widen mechanically
        i_start = i_dip
        above = np.where((times > t_dip) & (gs >= 0.8 * plateau))[0]
        i_end = int(above[0]) if len(above) else len(times) - 1
    info = dict(t_dip=float(t_dip), t_end=float(times[min(i_end, len(times) - 1)]),
                plateau=plateau, n_points=int(i_end - i_start))
    return i_start, i_end, info


def ramp_slope(g_mean: np.ndarray, times: np.ndarray, i0: int, i1: int) -> float:
    """Gamma := linear LS slope of g(t) on the frozen ramp window (IC-3)."""
    if i1 - i0 < 3:
        return float("nan")
    t = times[i0:i1]
    y = g_mean[i0:i1]
    A = np.vstack([t, np.ones_like(t)]).T
    slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(slope)


# ----------------------------------------------------------------------------
# Collapse fit (nu telemetry lane) — IC-6, P-2, P-4
# ----------------------------------------------------------------------------

NU_GRID = np.round(np.arange(NU_LO, NU_HI + 1e-9, NU_STEP), 10)


def collapse_cost(rbar: dict, Ns, kappas: np.ndarray, nu: float, kc: float) -> float:
    """SSE of a pooled cubic master-curve fit in x = (kappa - kc) * N^(1/nu)."""
    xs, ys = [], []
    for N in Ns:
        xs.append((kappas - kc) * (N ** (1.0 / nu)))
        ys.append(rbar[N])
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    xn = x / (np.max(np.abs(x)) + 1e-300)
    V = np.vander(xn, 4)
    coef, _, _, _ = np.linalg.lstsq(V, y, rcond=None)
    resid = y - V @ coef
    return float(resid @ resid)


def fit_collapse(rbar: dict, Ns, kappas: np.ndarray, kc_step: float = 0.01):
    """Grid-scan nu over the pinned search interval (P-4) x kc over the pinned
    grid span; returns (nu_hat, kc_hat, cost)."""
    kcs = np.arange(kappas[0] + 0.05, kappas[-1] - 0.05 + 1e-9, kc_step)
    best = (None, None, np.inf)
    for nu in NU_GRID:
        for kc in kcs:
            c = collapse_cost(rbar, Ns, kappas, nu, kc)
            if c < best[2]:
                best = (float(nu), float(kc), c)
    return best


def collapse_quality(rbar: dict, Ns, kappas: np.ndarray, nu: float, kc: float):
    """Per-size R^2 vs the pooled master curve (P-5) and pairwise cross-size
    Pearson correlations of the collapsed curves (P-5)."""
    xs = {N: (kappas - kc) * (N ** (1.0 / nu)) for N in Ns}
    x_all = np.concatenate([xs[N] for N in Ns])
    y_all = np.concatenate([rbar[N] for N in Ns])
    scale = np.max(np.abs(x_all)) + 1e-300
    V = np.vander(x_all / scale, 4)
    coef, _, _, _ = np.linalg.lstsq(V, y_all, rcond=None)

    r2 = {}
    for N in Ns:
        y = rbar[N]
        pred = np.vander(xs[N] / scale, 4) @ coef
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2[N] = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    xcorr = {}
    for a, b in combinations(Ns, 2):
        xa, ya = xs[a], rbar[a]
        xb, yb = xs[b], rbar[b]
        lo = max(xa.min(), xb.min())
        hi = min(xa.max(), xb.max())
        sel = (xa >= lo) & (xa <= hi)
        if np.sum(sel) < 3:
            xcorr[f"{a}x{b}"] = float("nan")
            continue
        order = np.argsort(xb)
        yb_i = np.interp(xa[sel], xb[order], yb[order])
        ya_s = ya[sel]
        if np.std(ya_s) == 0 or np.std(yb_i) == 0:
            xcorr[f"{a}x{b}"] = float("nan")
        else:
            xcorr[f"{a}x{b}"] = float(np.corrcoef(ya_s, yb_i)[0, 1])
    return r2, xcorr


# ----------------------------------------------------------------------------
# Direct-beta lane (P-6, P-7, IC-3/IC-4/IC-5)
# ----------------------------------------------------------------------------

def pairwise_beta(gammas: dict, Ns, log_d: dict):
    """beta at pair midpoints via local log-log slopes (IC-5), then the pinned
    primary linear fit in 1/N extrapolated to intercept (P-6).
    Returns (beta_pairs, beta_inf) or NaNs when any Gamma <= 0."""
    pairs = list(zip(Ns[:-1], Ns[1:]))
    mids, betas = [], []
    for a, b in pairs:
        ga, gb = gammas[a], gammas[b]
        if not (ga > 0 and gb > 0):
            return [float("nan")] * len(pairs), float("nan")
        slope = (math.log(gb) - math.log(ga)) / (log_d[b] - log_d[a])
        betas.append(abs(slope))
        mids.append(0.5 * (a + b))
    if len(betas) >= 2:
        coef = np.polyfit([1.0 / m for m in mids], betas, 1)
        beta_inf = float(coef[1])  # intercept at 1/N -> 0
    else:
        beta_inf = float("nan")
    return betas, beta_inf


# ----------------------------------------------------------------------------
# Self-tests (Hermiticity, parity, GUE level repulsion, determinism)
# ----------------------------------------------------------------------------

def selftest():
    print("SELF-TESTS")
    tc = TermCache(14)
    H4, H2 = tc.build(1)
    kap = 16.9
    H = H4 + tc.mass_scale(kap) * H2
    herm = float(np.max(np.abs(H - H.conj().T)))
    assert herm < 1e-12, f"Hermiticity violated: {herm}"
    print(f"  hermiticity            : OK (max |H - H^dag| = {herm:.2e})")

    # parity preservation: full-space H must be block diagonal in parity
    rows = np.arange(tc.dim)
    rng = np.random.default_rng([1, 14])
    J = rng.normal(0.0, math.sqrt(6.0 / 14 ** 3), size=len(tc.quad_idx))
    Hfull = tc._accumulate(tc.quad_flat, tc.quad_vals, J)
    odd = np.setdiff1d(rows, tc.even)
    off = float(np.max(np.abs(Hfull[np.ix_(tc.even, odd)])))
    assert off < 1e-14, f"parity mixing: {off}"
    print(f"  even-parity block      : OK (max cross-parity element = {off:.2e})")

    # determinism under fixed seed
    H4b, H2b = tc.build(1)
    assert np.array_equal(H4, H4b) and np.array_equal(H2, H2b)
    hsh = hashlib.sha256(H4.tobytes()).hexdigest()[:16]
    print(f"  determinism            : OK (H4 sha256[:16] = {hsh})")

    # level repulsion at kappa = 0: SYK4 at N = 14, 18 is GUE class (N mod 8 in
    # {2, 6}); expect <r> near the GUE value ~ 0.60
    rs = []
    tc18 = TermCache(18)
    for s in (1, 2, 3, 4, 5, 6):
        H4s, _ = tc18.build(s)
        rs.append(r_stat(np.linalg.eigvalsh(H4s)))
    rmean = float(np.mean(rs))
    assert 0.55 < rmean < 0.65, f"GUE r-statistic sanity failed: {rmean}"
    print(f"  level repulsion (SYK4) : OK (<r> at N=18, kappa=0: {rmean:.4f}; "
          f"GUE ref {GUE_R}, Poisson ref {POISSON_R})")

    # op179 bucket functions respond (bookkeeping smoke test, no physics)
    assert op179.beta_bucket_point(2.0) == "KILL"
    assert op179.beta_bucket_ci(0.8, 1.2) == "STRONG_PASS"
    print("  op179 bucket import    : OK (point(2.0)=KILL, ci(0.8,1.2)=STRONG_PASS)")
    print("SELF-TESTS: ALL PASSED\n")


# ----------------------------------------------------------------------------
# Sweep + analysis
# ----------------------------------------------------------------------------

def run_sweep(sizes):
    """Exact diagonalization over the pinned (N, kappa, seed) grid.
    Returns {N: {"spectra": (n_seed, n_kappa, d) array, "r": (n_seed, n_kappa)}}."""
    out = {}
    kappas = np.array(KAPPA_GRID)
    for N in sizes:
        t0 = time.time()
        tc = TermCache(N)
        d = len(tc.even)
        spec = np.empty((len(SEEDS), len(kappas), d))
        rmat = np.empty((len(SEEDS), len(kappas)))
        for si, s in enumerate(SEEDS):
            H4, H2 = tc.build(s)
            for ki, kap in enumerate(kappas):
                E = np.linalg.eigvalsh(H4 + tc.mass_scale(kap) * H2)
                spec[si, ki] = E
                rmat[si, ki] = r_stat(E)
        out[N] = {"spectra": spec, "r": rmat, "d_sector": d}
        print(f"  N={N:2d}: d_sector={d:5d}, {len(SEEDS)} seeds x "
              f"{len(kappas)} kappas done in {time.time()-t0:.1f}s")
    return out


def analyze(data):
    kappas = np.array(KAPPA_GRID)
    ck = np.array(COLLAPSE_KAPPAS)
    ck_cols = [KAPPA_GRID.index(k) for k in COLLAPSE_KAPPAS]
    rng = np.random.default_rng(20260801)
    results = {}

    # ---------- r-statistic tables ----------
    rtab = {}
    for N, d in data.items():
        rtab[N] = {
            "mean": d["r"].mean(axis=0).tolist(),
            "sem": (d["r"].std(axis=0, ddof=1) / math.sqrt(len(SEEDS))).tolist(),
        }
    results["r_statistic"] = {"kappa_grid": KAPPA_GRID, "per_size": rtab,
                              "gue_ref": GUE_R, "poisson_ref": POISSON_R}

    # ---------- nu telemetry lane: collapse over official sizes ----------
    Ns = OFFICIAL_N
    rbar = {N: data[N]["r"][:, ck_cols].mean(axis=0) for N in Ns}
    nu_hat, kc_hat, cost = fit_collapse(rbar, Ns, ck)
    r2, xcorr = collapse_quality(rbar, Ns, ck, nu_hat, kc_hat)

    # bracketing rule (P-2): strictly interior with >= 2 grid points each side
    below = int(np.sum(ck < kc_hat))
    above = int(np.sum(ck > kc_hat))
    bracket_ok = (ck[0] < kc_hat < ck[-1]) and below >= 2 and above >= 2

    # bootstrap (P-4) — resample seeds independently per size, coarse-to-fine kc
    print("  bootstrapping nu collapse (2000 resamples)...")
    t0 = time.time()
    nu_boot = np.empty(N_BOOT)
    kc_boot = np.empty(N_BOOT)
    for bi in range(N_BOOT):
        rb = {}
        for N in Ns:
            idx = rng.integers(0, len(SEEDS), len(SEEDS))
            rb[N] = data[N]["r"][idx][:, ck_cols].mean(axis=0)
        nb, kb, _ = fit_collapse(rb, Ns, ck, kc_step=0.05)
        nu_boot[bi] = nb
        kc_boot[bi] = kb
    print(f"    done in {time.time()-t0:.0f}s")

    interior = NU_LO < nu_hat < NU_HI
    lo_mass = float(np.mean(nu_boot <= NU_LO + NU_STEP))
    hi_mass = float(np.mean(nu_boot >= NU_HI - NU_STEP))
    degenerate = (not interior) or lo_mass > EDGE_MASS_MAX or hi_mass > EDGE_MASS_MAX

    # pairwise collapse nu -> pinned 1/N extrapolation (P-6, telemetry lane)
    nu_pairs = {}
    for a, b in zip(Ns[:-1], Ns[1:]):
        np_hat, kp_hat, _ = fit_collapse({a: rbar[a], b: rbar[b]}, [a, b], ck,
                                         kc_step=0.02)
        nu_pairs[f"{a}-{b}"] = {"nu": np_hat, "kappa_c": kp_hat,
                                "midpoint_N": 0.5 * (a + b)}
    if len(nu_pairs) >= 2:
        mids = [v["midpoint_N"] for v in nu_pairs.values()]
        nus = [v["nu"] for v in nu_pairs.values()]
        nu_inf = float(np.polyfit([1.0 / m for m in mids], nus, 1)[1])
    else:
        nu_inf = float("nan")

    results["nu_telemetry_lane"] = {
        "status": "TELEMETRY ONLY — nu-route CLOSED by prereg section 3.2; no "
                  "nu-derived number may enter any bucket, verdict, or gate",
        "collapse_fit": {"nu": nu_hat, "kappa_c": kc_hat, "sse": cost},
        "bracketing": {"kappa_c": kc_hat, "grid_points_below": below,
                       "grid_points_above": above, "rule_satisfied": bracket_ok,
                       "consequence_if_false": "run VOID per prereg section 1"},
        "bootstrap": {
            "resamples": N_BOOT,
            "nu_ci95": [float(np.percentile(nu_boot, 2.5)),
                        float(np.percentile(nu_boot, 97.5))],
            "kappa_c_ci95": [float(np.percentile(kc_boot, 2.5)),
                             float(np.percentile(kc_boot, 97.5))],
            "edge_mass_low": lo_mass, "edge_mass_high": hi_mass,
            "fitted_nu_interior": interior,
            "DEGENERATE": degenerate,
            "consequence_if_degenerate": "run not certifiable per prereg section 2",
        },
        "convergence": {
            "per_size_R2": {str(k): v for k, v in r2.items()},
            "R2_threshold": R2_MIN,
            "R2_pass": all(v >= R2_MIN for v in r2.values() if not math.isnan(v)),
            "cross_size_correlation": xcorr,
            "xcorr_threshold": XCORR_MIN,
            "xcorr_pass": all(v >= XCORR_MIN for v in xcorr.values()
                              if not math.isnan(v)),
        },
        "pairwise_nu_and_extrapolation": {"pairs": nu_pairs,
                                          "nu_intercept_1_over_N": nu_inf},
    }

    # ---------- direct-beta lane (PRIMARY per prereg section 3.1) ----------
    log_d_pinned = {N: N * math.log(2.0) for N in Ns}        # P-7: d ~ 2^N
    log_d_sector = {N: math.log(data[N]["d_sector"]) for N in Ns}

    # SFF and Gamma for every (N, kappa); windows frozen from full-sample means
    sff = {N: {} for N in Ns + TELEMETRY_N}
    for N in Ns + TELEMETRY_N:
        d = data[N]["d_sector"]
        for ki, kap in enumerate(KAPPA_GRID):
            spec = data[N]["spectra"][:, ki, :]
            times, t_H = make_time_grid(spec)
            g = sff_curves(spec, times)
            gm = g.mean(axis=0)
            i0, i1, info = ramp_window(gm, times, t_H, d)
            sff[N][kap] = {"times": times, "g_seeds": g, "window": (i0, i1),
                           "info": info, "t_H": t_H,
                           "gamma": ramp_slope(gm, times, i0, i1)}

    def beta_lane(kappa_key):
        gammas = {N: sff[N][kappa_key]["gamma"] for N in Ns}
        bp_pin, binf_pin = pairwise_beta(gammas, Ns, log_d_pinned)
        bp_sec, binf_sec = pairwise_beta(gammas, Ns, log_d_sector)
        # pooled 3-size slope (cross-check)
        ln_g = [math.log(gammas[N]) if gammas[N] > 0 else float("nan") for N in Ns]
        pooled_pin = pooled_sec = float("nan")
        if all(not math.isnan(v) for v in ln_g):
            pooled_pin = abs(float(np.polyfit(
                [log_d_pinned[N] for N in Ns], ln_g, 1)[0]))
            pooled_sec = abs(float(np.polyfit(
                [log_d_sector[N] for N in Ns], ln_g, 1)[0]))
        # bootstrap over seeds (P-4: 2000 resamples), windows frozen (IC-7)
        boot_pin = np.empty(N_BOOT)
        boot_sec = np.empty(N_BOOT)
        bad = 0
        for bi in range(N_BOOT):
            gb = {}
            ok = True
            for N in Ns:
                e = sff[N][kappa_key]
                idx = rng.integers(0, len(SEEDS), len(SEEDS))
                gm = e["g_seeds"][idx].mean(axis=0)
                i0, i1 = e["window"]
                gam = ramp_slope(gm, e["times"], i0, i1)
                if not gam > 0:
                    ok = False
                    break
                gb[N] = gam
            if not ok:
                bad += 1
                boot_pin[bi] = np.nan
                boot_sec[bi] = np.nan
                continue
            _, boot_pin[bi] = pairwise_beta(gb, Ns, log_d_pinned)
            _, boot_sec[bi] = pairwise_beta(gb, Ns, log_d_sector)
        bp = boot_pin[~np.isnan(boot_pin)]
        bs = boot_sec[~np.isnan(boot_sec)]
        ci_pin = ([float(np.percentile(bp, 2.5)), float(np.percentile(bp, 97.5))]
                  if len(bp) > 100 else [float("nan")] * 2)
        ci_sec = ([float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
                  if len(bs) > 100 else [float("nan")] * 2)
        return {
            "gamma_per_size": {str(N): gammas[N] for N in Ns},
            "gamma_telemetry_N10": sff[10][kappa_key]["gamma"],
            "windows": {str(N): sff[N][kappa_key]["info"] for N in Ns},
            "primary_d_2powN": {
                "beta_pairs_midpoints": bp_pin,
                "beta_intercept_1_over_N": binf_pin,
                "beta_pooled_slope": pooled_pin,
                "ci95_intercept": ci_pin,
            },
            "diagnostic_d_sector": {
                "beta_pairs_midpoints": bp_sec,
                "beta_intercept_1_over_N": binf_sec,
                "beta_pooled_slope": pooled_sec,
                "ci95_intercept": ci_sec,
            },
            "bootstrap_invalid_resamples": bad,
        }

    print("  direct-beta lane: primary column kappa=0 (IC-4) + bootstrap...")
    beta0 = beta_lane(0.0)
    # telemetry: point estimates at every pinned kappa (no bootstrap)
    beta_by_kappa = {}
    for kap in KAPPA_GRID:
        gam = {N: sff[N][kap]["gamma"] for N in Ns}
        bp_pin, binf_pin = pairwise_beta(gam, Ns, log_d_pinned)
        bp_sec, binf_sec = pairwise_beta(gam, Ns, log_d_sector)
        beta_by_kappa[str(kap)] = {
            "gamma": {str(N): gam[N] for N in Ns},
            "beta_intercept_d_2powN": binf_pin,
            "beta_intercept_d_sector": binf_sec,
        }

    # beta at the grid point nearest the fitted crossing, if bracketing held
    near = None
    if bracket_ok:
        near = float(ck[np.argmin(np.abs(ck - kc_hat))])
        print(f"  direct-beta lane: crossing-adjacent column kappa={near} + bootstrap...")
        beta_cross = beta_lane(near)
    else:
        beta_cross = None

    results["direct_beta_lane"] = {
        "status": "PRIMARY ROUTE per prereg section 3.1 — PRELIMINARY-LAPTOP / "
                  "PIPELINE-VALIDATION (venue pinned as Nebius in prereg "
                  "section 5; this laptop execution is not the certified run)",
        "gamma_operationalization": "IC-3 (see module docstring): ramp slope of "
                                    "disorder-averaged g(t)=|Tr e^{-iHt}|^2/d_sector^2; "
                                    "NOT pinned by any repo source — certification "
                                    "caveat",
        "d_convention_note": "prereg section 3.1 pins d ~ 2^N (glossary); the "
                             "physical sector Hilbert dimension is 2^(N/2-1); both "
                             "reported; the two differ by a factor ~2 in beta",
        "primary_kappa0": beta0,
        "crossing_adjacent": {"kappa": near, "result": beta_cross},
        "beta_by_kappa_telemetry": beta_by_kappa,
    }

    # ---------- buckets via op179 (P-10) ----------
    def buckets(tag, binf, ci):
        entry = {"beta": binf, "ci95": ci}
        if not math.isnan(binf):
            entry["point_bucket"] = op179.beta_bucket_point(binf)
        if not any(math.isnan(v) for v in ci):
            entry["ci_bucket"] = op179.beta_bucket_ci(ci[0], ci[1])
        return {tag: entry}

    bucket_block = {}
    bucket_block.update(buckets(
        "kappa0_d_2powN_PINNED_CONVENTION",
        beta0["primary_d_2powN"]["beta_intercept_1_over_N"],
        beta0["primary_d_2powN"]["ci95_intercept"]))
    bucket_block.update(buckets(
        "kappa0_d_sector_DIAGNOSTIC",
        beta0["diagnostic_d_sector"]["beta_intercept_1_over_N"],
        beta0["diagnostic_d_sector"]["ci95_intercept"]))
    if beta_cross is not None:
        bucket_block.update(buckets(
            "crossing_d_2powN_PINNED_CONVENTION",
            beta_cross["primary_d_2powN"]["beta_intercept_1_over_N"],
            beta_cross["primary_d_2powN"]["ci95_intercept"]))
        bucket_block.update(buckets(
            "crossing_d_sector_DIAGNOSTIC",
            beta_cross["diagnostic_d_sector"]["beta_intercept_1_over_N"],
            beta_cross["diagnostic_d_sector"]["ci95_intercept"]))

    results["op179_buckets_PRELIMINARY_LAPTOP"] = {
        "WARNING": "NOT A CERTIFIED VERDICT. Venue pinned as Nebius (prereg "
                   "section 5) and the Gamma operationalization (IC-3) is not "
                   "source-pinned. Bucket labels below are the mechanical output "
                   "of the byte-frozen op179 functions applied to "
                   "PRELIMINARY-LAPTOP numbers, for pipeline validation only. "
                   "Per prereg section 6, no SYK number may be reported as GHP "
                   "support in either direction.",
        "buckets": bucket_block,
    }

    # ---------- certifiability roll-up ----------
    results["certification_gates"] = {
        "venue_is_nebius": False,
        "crossing_bracketing_ok": bool(bracket_ok),
        "nu_bootstrap_nondegenerate": (not degenerate),
        "collapse_R2_pass": results["nu_telemetry_lane"]["convergence"]["R2_pass"],
        "cross_size_corr_pass": results["nu_telemetry_lane"]["convergence"]["xcorr_pass"],
        "gamma_operationalization_source_pinned": False,
        "CERTIFIED_VERDICT": False,
        "status": "PIPELINE-VALIDATION ONLY",
    }
    return results


def main():
    selftest()
    if "--selftest" in sys.argv:
        return
    print(f"PINNED SWEEP: N in {OFFICIAL_N} official + {TELEMETRY_N} telemetry; "
          f"seeds {SEEDS[0]}-{SEEDS[-1]}; {len(KAPPA_GRID)} kappa points")
    data = run_sweep(TELEMETRY_N + OFFICIAL_N)
    print("ANALYSIS")
    results = analyze(data)
    meta = {
        "test_id": "SYK-CORRIDOR-v1",
        "label": "PRELIMINARY-LAPTOP / PIPELINE-VALIDATION",
        "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prereg_sha256": "59a46ff9b19b05b6c99dd0a58fb14629aecb11e0e5c2a94662e465820843f3d0",
        "op179_sha256": "b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e",
        "seeds": [SEEDS[0], SEEDS[-1]],
        "kappa_grid": KAPPA_GRID,
        "official_sizes": OFFICIAL_N,
        "telemetry_sizes": TELEMETRY_N,
        "nu_route": "CLOSED (prereg section 3.2); ChannelExponentAssignment port "
                    "UNFILLED; nu_to_beta_verdict and "
                    "m1_quotient_confirmation_flag NEVER CALLED",
        "spend_usd": 0.0,
        "budget_cap_usd": 400.0,
    }
    out = {"meta": meta, "results": results}
    out_path = HERE / "results_laptop.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\nWROTE {out_path}")
    cg = results["certification_gates"]
    print("CERTIFICATION GATES:", json.dumps(cg, indent=1))


if __name__ == "__main__":
    main()
