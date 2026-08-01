#!/usr/bin/env python3
"""Experiment 3 — pure-numpy state-vector Hadamard test for Re<w|psi> and Im<w|psi>.

Circuit (ancilla qubit + 27-dim register, total dimension 54):

    |0>|psi>  --H(anc)-->  --c-V-->  [--Sdg(anc)--]  --H(anc)-->  measure ancilla

with V a unitary satisfying V|psi> = |w> (constructed explicitly from the two
states by completing each to an orthonormal basis; V = B_w B_psi^dagger).

Noiseless probabilities:
    real variant:  p0 = (1 + Re<psi|V|psi>)/2 = (1 + Re<psi|w>)/2 = (1 + Re<w|psi>)/2
    imag variant (S^dagger on ancilla before the final H):
                   p0 = (1 - Im<w|psi>)/2, i.e. Im<w|psi> = 1 - 2 p0
                   (convention derived in-line and verified numerically below)

Exact noiseless recovery is asserted against the analytic overlap, then shot-based
estimation at 10^3 / 10^4 / 10^5 shots with binomial confidence intervals.

STATE PREPARATION IS AN ASSUMED ORACLE: |psi(t)> and the unitary V are handed to
the simulator as classical data. No preparation cost is claimed, no speedup is
claimed. This is a classical simulation of a textbook readout primitive applied
to the exact embedding.
"""

import os
import numpy as np

import zhq_common as z

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "hadamard_overlap_sim.json")

T_POINTS = [4300.0, 4400.0, 4500.0]
SHOT_LEVELS = [10 ** 3, 10 ** 4, 10 ** 5]
SEED = 20260801


def complete_to_unitary(v):
    """Return a unitary whose first column is v (Gram-Schmidt on [v, e_0, e_1, ...])."""
    d = len(v)
    cols = [v / np.linalg.norm(v)]
    for k in range(d):
        e = np.zeros(d, dtype=np.complex128)
        e[k] = 1.0
        for c in cols:
            e = e - np.vdot(c, e) * c
        nrm = np.linalg.norm(e)
        if nrm > 1e-10:
            cols.append(e / nrm)
        if len(cols) == d:
            break
    return np.stack(cols, axis=1)


def build_V(psi, w):
    """Unitary V with V|psi> = |w>."""
    B_psi = complete_to_unitary(psi)
    B_w = complete_to_unitary(w)
    return B_w @ B_psi.conj().T


def hadamard_test(psi, V, imag=False):
    """Simulate the Hadamard test; return noiseless p0 (ancilla measured 0)."""
    d = len(psi)
    # state layout: [ancilla=0 block | ancilla=1 block]
    state = np.zeros(2 * d, dtype=np.complex128)
    state[:d] = psi                                  # |0>|psi>
    # H on ancilla
    a0, a1 = state[:d].copy(), state[d:].copy()
    state[:d] = (a0 + a1) / np.sqrt(2)
    state[d:] = (a0 - a1) / np.sqrt(2)
    # controlled-V on the |1> block
    state[d:] = V @ state[d:]
    if imag:
        # S^dagger on ancilla: |1> -> -i|1>
        state[d:] *= -1j
    # H on ancilla
    a0, a1 = state[:d].copy(), state[d:].copy()
    state[:d] = (a0 + a1) / np.sqrt(2)
    state[d:] = (a0 - a1) / np.sqrt(2)
    return float(np.linalg.norm(state[:d]) ** 2)


def main():
    # macOS Accelerate BLAS raises spurious floating-point status flags on complex
    # matmul (divide/overflow/invalid RuntimeWarnings with correct results). Every
    # quantity below is verified against explicit tolerances by assert, so the
    # bogus flags are silenced rather than trusted.
    np.seterr(divide="ignore", over="ignore", invalid="ignore")
    rng = np.random.default_rng(SEED)
    mapping = z.map_lexicographic()
    points = []
    for t in T_POINTS:
        N, A, psi_terms = z.psi_state(t)
        w_terms = z.w_state(N)
        psi27 = z.embed_terms(psi_terms, mapping)
        w27 = z.embed_terms(w_terms, mapping)
        overlap = complex(np.vdot(w27, psi27))       # <w|psi>

        V = build_V(psi27, w27)
        unit_err = float(np.max(np.abs(V @ V.conj().T - np.eye(27))))
        map_err = float(np.linalg.norm(V @ psi27 - w27))

        p0_re = hadamard_test(psi27, V, imag=False)
        p0_im = hadamard_test(psi27, V, imag=True)
        re_est = 2 * p0_re - 1
        im_est = 1 - 2 * p0_im
        re_err = abs(re_est - overlap.real)
        im_err = abs(im_est - overlap.imag)
        assert unit_err < 1e-10 and map_err < 1e-10
        assert re_err < z.TOL_EXACT_SIM, (re_est, overlap.real)
        assert im_err < z.TOL_EXACT_SIM, (im_est, overlap.imag)

        shots_rows = []
        for shots in SHOT_LEVELS:
            k0 = int(rng.binomial(shots, p0_re))
            p_hat = k0 / shots
            ci_half_p = 1.96 * np.sqrt(max(p_hat * (1 - p_hat), 1e-12) / shots)
            est = 2 * p_hat - 1
            shots_rows.append({
                "shots": shots,
                "p0_true": p0_re,
                "p0_hat": p_hat,
                "overlap_re_true": overlap.real,
                "overlap_re_est": est,
                "abs_error": abs(est - overlap.real),
                "ci95_half_width_overlap": 2 * ci_half_p,
            })
        points.append({
            "t": t, "N": N, "A_N": A,
            "overlap_re": overlap.real, "overlap_im": overlap.imag,
            "M_t": float(2 * A * overlap.real),
            "V_unitarity_err": unit_err, "V_maps_psi_to_w_err": map_err,
            "noiseless": {
                "p0_real_variant": p0_re, "p0_imag_variant": p0_im,
                "re_recovery_err": re_err, "im_recovery_err": im_err,
                "imag_convention": "S^dagger on ancilla => p0 = (1 - Im<w|psi>)/2",
            },
            "shot_estimation_real_variant": shots_rows,
        })
        print(f"t={t}: Re<w|psi>={overlap.real:+.9f}, noiseless err {re_err:.2e}/{im_err:.2e}; "
              + "; ".join(f"{r['shots']} shots -> |err| {r['abs_error']:.4f} (CI95 ±{r['ci95_half_width_overlap']:.4f})"
                          for r in shots_rows))

    result = {
        "experiment": "hadamard_overlap_sim",
        "oracle_disclosure": (
            "state preparation for |psi(t)>, |w_N> and the unitary V are ASSUMED ORACLES "
            "supplied as classical data; their cost is NOT claimed and no speedup is claimed"
        ),
        "points": points,
        "meta": z.run_metadata(
            seeds={"shot_rng": SEED},
            tolerances={"noiseless_recovery": z.TOL_EXACT_SIM, "unitarity": 1e-10},
        ),
    }
    z.save_json(OUT, result)
    print("hadamard overlap sim: PASS")


if __name__ == "__main__":
    main()
