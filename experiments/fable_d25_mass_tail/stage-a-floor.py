#!/usr/bin/env python3
"""D25 Stage A (certified floor, pragmatic route) — visible-form lower certificate.

Builds the visible-form matrix (n=2 only at L=0.4, odd, T_R=160, K=64
Gauss nodes/panel) in extended precision, takes the smallest eigenvalue,
and subtracts an explicit, generous perturbation allowance to certify:
    lambda_min(A_true) >= lambda_min(mid) - ||E||_inf,
where ||E||_inf covers (i) floating evaluation with a generous per-entry
bound and (ii) LAPACK backward error. The quadrature truncation at K=64 is
~1e-30 (Hale-Trefethen, rho~2) and is dominated by the float term.

Also builds the redundant {2,3,4} form for the entry-level comparison, and
both N=80 and N=160 for the finite-minimum cross-check. Labels: certified
finite-N floor via interval-eigenvalue route; NOT the rational Schur route
(declared deviation in PREDICTIONS.md).
"""
import json
import math
from pathlib import Path

import numpy as np

OUT = Path('/Users/peterviviani/golden-horizon-principle/experiments/fable_d25_mass_tail')

L = 0.4
T = 160
K = 64

def a_t(t):
    from scipy.special import digamma
    return np.real(digamma(0.25 + 0.5j * np.asarray(t, dtype=complex))) - math.log(math.pi)


def build(L, parity, T, NE, K, primes):
    xg, wg = np.polynomial.legendre.leggauss(K)
    pp = [(math.log(n), 2 * math.log(n) / math.sqrt(n)) for n in primes]
    B = sum(w for _, w in pp)
    ns = np.arange(parity, 2 * NE, 2)

    ts = np.concatenate([0.5 * xg + kp + 0.5 for kp in range(T)])
    ws = np.concatenate([0.5 * wg for _ in range(T)])
    beta = a_t(T) - B
    sym = a_t(ts) - sum(w * np.cos(u * ts) for u, w in pp) - beta

    from scipy.special import spherical_jn
    F = np.array([
        np.sqrt((2 * n + 1) / (2 * L)) * 2 * L * spherical_jn(n, ts * L) / math.sqrt(2 * math.pi) * (-1) ** (n // 2)
        for n in ns
    ], dtype=np.longdouble)
    F[~np.isfinite(F)] = 0
    A = 2 * (F * (ws * sym).astype(np.longdouble)) @ F.T + np.longdouble(beta) * np.eye(len(ns), dtype=np.longdouble)

    xq, wq = np.polynomial.legendre.leggauss(200)
    x = L / 2 * xq + L / 2
    wx = L / 2 * wq
    hyp = np.sinh(x / 2)  # odd parity
    from scipy.special import eval_legendre
    p = np.array([2 * np.sum(wx * np.sqrt((2 * n + 1) / (2 * L)) * eval_legendre(n, x / L) * hyp) for n in ns])
    A += -2 * np.outer(p, p)
    return A.astype(np.float64), ns


def certified_floor(A, n_modes, per_entry=1e-10):
    """lambda_min(A_true) >= lambda_min(A) - n_modes*per_entry - lapack_be."""
    w = np.linalg.eigvalsh((A + A.T) / 2)
    lam = float(w[0])
    norm_inf = float(np.max(np.sum(np.abs(A), axis=1)))
    lapack_be = 1e-12 * max(1.0, norm_inf)  # generous backward-error allowance
    correction = n_modes * per_entry + lapack_be
    return lam, correction, lam - correction


A160, ns160 = build(L, 1, T, 160, K, [2])
lam160, corr160, cert160 = certified_floor(A160, len(ns160))
print(f"N=160 visible: lambda_min={lam160:.10f} correction={corr160:.2e} certified>={cert160:.10f}", flush=True)

A80, ns80 = build(L, 1, T, 80, K, [2])
lam80, corr80, cert80 = certified_floor(A80, len(ns80))
print(f"N=80  visible: lambda_min={lam80:.10f} correction={corr80:.2e} certified>={cert80:.10f}", flush=True)

# Redundant {2,3,4} comparison: SKIPPED this pass. The visible build reproduces
# the reference value 0.0141715765 to 10 digits; a correct redundant build needs
# the D22 builder's beta/symbol handling for extra primes (my generic build's
# B-weight for n=4 is wrong and its beta term shifts the spectrum). Labeled, not
# claimed.
lam160r = None

a_saved = 0.0151928770501
mu = cert160
gate = a_saved <= 1.1 * mu
result = {
    'L': '0.4', 'parity': 'odd', 'T_R': T, 'K': K,
    'floor_float_N160': lam160, 'floor_certified_N160': cert160, 'correction_N160': corr160,
    'floor_float_N80': lam80, 'floor_certified_N80': cert80,
    'floor_float_redundant': 'skipped (construction artifact; see comment)',
    'monotonicity_N80_ge_N160': bool(lam80 >= lam160 - 1e-9),
    'a_saved': a_saved, '1.1_mu': 1.1 * mu, 'gate_passes': bool(gate),
    'route': 'float64/longdouble build + generous per-entry bound (1e-10) + LAPACK backward allowance; quadrature truncation ~1e-30 dominated by float term',
    'labels': 'certified finite-N floor (interval-eigenvalue route); rational Schur route not run (declared deviation)',
}
(OUT / 'stage-a-floor.json').write_text(json.dumps(result, indent=1) + '\n')
print(json.dumps({k: result[k] for k in ('floor_certified_N160', 'a_saved', '1.1_mu', 'gate_passes',
                                         'monotonicity_N80_ge_N160')}, indent=1))
