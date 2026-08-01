#!/usr/bin/env python3
"""Experiment 1 — the exact overlap identity M(t) = 2 A_N Re<w_N|psi(t)>.

Checks the identity across a t-grid spanning [4250, 4580] (the interior of the
26-term window [2*pi*26^2, 2*pi*27^2) = [4247.4332676534, 4580.4420889339)), plus
spot heights t = 10^4 (N = 39) and t = 10^6 (N = 398): N grows with t and the
identity is N-generic — nothing about it is special to N = 26.

Asserts |M_direct - 2 A_N Re<w|psi>| < 1e-12 everywhere, and both state
normalizations |<psi|psi> - 1| < 1e-12 and |<w|w> - 1| < 1e-12.

Scope: exact embedding of the MAIN SUM only; the O(t^(-1/4)) remainder is outside
the register; no speedup claim; no RH claim.
"""

import os
import numpy as np

import zhq_common as z

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "overlap_identity.json")


def check_point(t):
    N, phi = z.phases(t)
    ns = np.arange(1, N + 1, dtype=np.float64)
    A, amps = z.amplitude_data(N)
    psi = amps * np.exp(1j * phi)
    w = amps.astype(np.complex128)

    m_direct = float(2.0 * np.sum(ns ** -0.5 * np.cos(phi)))
    overlap = complex(np.vdot(w, psi))
    m_overlap = float(2.0 * A * overlap.real)
    return {
        "t": float(t),
        "N": N,
        "A_N": A,
        "M_direct": m_direct,
        "M_overlap": m_overlap,
        "residual": abs(m_direct - m_overlap),
        "overlap_re": overlap.real,
        "overlap_im": overlap.imag,
        "psi_norm_err": abs(float(np.vdot(psi, psi).real) - 1.0),
        "w_norm_err": abs(float(np.vdot(w, w).real) - 1.0),
    }


def main():
    grid = [float(t) for t in range(4250, 4590, 10)]  # 4250..4580 inclusive, all N = 26
    spots = [1.0e4, 1.0e6]
    rows = [check_point(t) for t in grid + spots]

    max_resid = max(r["residual"] for r in rows)
    max_norm = max(max(r["psi_norm_err"], r["w_norm_err"]) for r in rows)
    for r in rows:
        assert r["residual"] < z.TOL_IDENTITY, r
        assert r["psi_norm_err"] < z.TOL_NORM and r["w_norm_err"] < z.TOL_NORM, r
    assert {r["N"] for r in rows if r["t"] <= 4580} == {26}
    assert next(r["N"] for r in rows if r["t"] == 1.0e4) == 39
    assert next(r["N"] for r in rows if r["t"] == 1.0e6) == 398

    result = {
        "experiment": "overlap_identity",
        "identity": "M(t) = 2 A_N Re<w_N|psi(t)>",
        "window_26": [4247.4332676534, 4580.4420889339],
        "grid": {"t_min": 4250, "t_max": 4580, "step": 10, "N": 26},
        "spot_heights": {"1e4": {"N": 39}, "1e6": {"N": 398}},
        "max_identity_residual": max_resid,
        "max_normalization_error": max_norm,
        "all_points_pass": True,
        "points": rows,
        "meta": z.run_metadata(tolerances={"identity": z.TOL_IDENTITY, "norm": z.TOL_NORM}),
    }
    z.save_json(OUT, result)
    print(f"overlap identity: {len(rows)} points, max residual {max_resid:.3e}, "
          f"max norm error {max_norm:.3e} — PASS")


if __name__ == "__main__":
    main()
