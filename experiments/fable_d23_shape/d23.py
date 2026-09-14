#!/usr/bin/env python3
"""d23.py -- PROVENANCE REPAIR (D30 Task 4).

The D23 generating script was not committed with its round (D24 noted the gap; the
D23 RESULTS correction asks for it to be added as d23.py). This file is a
RECONSTRUCTION from the description in fable_d23_shape/RESULTS.md and the record in
d23_results.log, not the original source. Section A reproduces the log's fit numbers
on the same eight D22 certified lower bounds; section B reconstructs the prolate
overlap measurement with the time-frequency limiting operator in the same 80-mode
Legendre basis, using the saved D22 minimizers.

Run: python3 d23.py   (prints sections A and B in the d23_results.log format)
"""
import json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
D22 = HERE.parent / 'fable_d22_test2'

# The eight D22 certified lower bounds (lambda0_certified centers), from the D22
# cert logs cert_{parity}_L{L}_T160_N160.log in fable_d22_test2/.
LAM = {
    ('even', 0.4): 0.000144919164005, ('odd', 0.4): 0.0124019265771,
    ('even', 0.5): 7.14785349231e-7,  ('odd', 0.5): 0.000142134532495,
    ('even', 0.6): 1.10135673044e-9,  ('odd', 0.6): 4.12866743816e-7,
    ('even', 0.7): 2.67167228677e-13, ('odd', 0.7): 1.58596369131e-10,
}

def slopes(Ls, ys):
    return [ (ys[i] - ys[i-1]) / (Ls[i] - Ls[i-1]) for i in range(1, len(Ls)) ]

def section_A():
    print('A. profile models on certified lower bounds')
    for par in ('even', 'odd'):
        Ls = np.array([0.4, 0.5, 0.6, 0.7])
        y = np.array([math.log(LAM[(par, L)]) for L in Ls])
        X1 = np.vstack([np.ones_like(Ls), -Ls]).T
        (A1, B1), *_ = np.linalg.lstsq(X1, y, rcond=None)
        E = np.exp(2 * Ls)
        X2 = np.vstack([np.ones_like(E), -E]).T
        (A2, C2), *_ = np.linalg.lstsq(X2, y, rcond=None)
        meas = slopes(Ls, list(y))
        m1 = slopes(Ls, list(X1 @ np.array([A1, B1])))
        m2 = slopes(Ls, list(X2 @ np.array([A2, C2])))
        rms1 = math.sqrt(np.mean(((np.array(m1) - meas) / np.array(meas)) ** 2))
        rms2 = math.sqrt(np.mean(((np.array(m2) - meas) / np.array(meas)) ** 2))
        print(f"  {par} M1 linear  : params {A1:+.3f}, {B1:.3f} | measured slopes {[round(-s,1) for s in meas]} model {[round(-s,1) for s in m1]} | rel RMS slope err {rms1:.3f}")
        print(f"  {par} M2 exp(2L) : params {A2:+.3f}, {C2:.3f} | measured slopes {[round(-s,1) for s in meas]} model {[round(-s,1) for s in m2]} | rel RMS slope err {rms2:.3f}")

def legendre_phi(ns, x, L):
    u = x / L
    P = {0: np.ones_like(u)}
    if max(ns) > 0:
        P[1] = u.copy()
    for m in range(2, max(ns) + 1):
        P[m] = ((2 * m - 1) * u * P[m - 1] - (m - 1) * P[m - 2]) / m
    return np.stack([np.sqrt((2 * n + 1) / (2 * L)) * P[n] for n in ns])

def limiting_operator(ns, L, Omega, K=480, phi=None):
    """S[mn] = int int phi_m(x) sin(Omega(x-y))/(pi(x-y)) phi_n(y) dx dy."""
    xg, wg = np.polynomial.legendre.leggauss(K)
    x = L * xg
    w = L * wg
    if phi is None:
        phi = legendre_phi(ns, x, L)                # (M, K)
    diff = x[:, None] - x[None, :]
    small = np.abs(diff) < 1e-12
    safe = np.where(small, 1.0, diff)
    Ker = np.where(small, Omega / math.pi, np.sin(Omega * safe) / (math.pi * safe))
    S = (Ker * w[None, :]) @ phi.T                  # (K, M)
    return (phi * w) @ S                            # (M, M)

def section_B():
    print('B. prolate overlap of the certified minimizers')
    grid = np.arange(11.0, 19.01, 0.1)
    for par in ('even', 'odd'):
        for L in (0.4, 0.5, 0.6, 0.7):
            cand = json.loads((D22 / f'd22_cand2_{par}_L{L}.json').read_text())
            ns = np.array(cand['modes'], dtype=int)
            c = np.array([float(v) for v in cand['minimizer_frozen_40dig']])
            c = c / np.linalg.norm(c)
            best = (0.0, None, None)
            second = 0.0
            for Om in grid:
                S = limiting_operator(ns, L, Om)
                ev, evec = np.linalg.eigh(S)
                w0 = evec[:, -1]; w0 = w0 / np.linalg.norm(w0)
                ov = abs(float(c @ w0))
                w1 = evec[:, -2]; w1 = w1 / np.linalg.norm(w1)
                ov2 = abs(float(c @ w1))
                if ov > best[0]:
                    best = (ov, Om, ov2)
            print(f"  {par:>4} L={L}: max overlap with top prolate {best[0]:.5f} at Omega*={best[1]:.1f} "
                  f"(c=Omega*L={best[1]*L:.2f}); overlap with 2nd prolate there {best[2]:.4f}")

if __name__ == '__main__':
    section_A()
    section_B()
