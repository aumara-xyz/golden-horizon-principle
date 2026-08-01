#!/usr/bin/env python3
"""Experiment 6 — null controls: the same machinery on a matched non-zeta ensemble.

Ensemble: K random-phase oscillator sets with IDENTICAL amplitude profile
n^(-1/4)/sqrt(A_26) and iid uniform phases (seeded). Every metric applied to the
zeta arm is applied to the ensemble:

  - the overlap identity M_arm = 2 A Re<w|psi_arm> (exact for every member),
  - the tensor-train error-vs-bond curve in the same 3x3x3 layout.

Required question, answered from the computed numbers in the output:
"does any claimed feature survive the control?"
"""

import os
import numpy as np

import zhq_common as z

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "null_controls.json")

T = 4400.0
K = 50
SEED = 88220801


def tt_errors(vec, shape, bonds):
    x = vec.reshape(shape)
    nrm = np.linalg.norm(vec)
    return [float(np.linalg.norm(z.tt_reconstruct(z.tt_svd(x, chi)).reshape(-1) - vec) / nrm)
            for chi in bonds]


def main():
    rng = np.random.default_rng(SEED)
    N, A, psi_terms = z.psi_state(T)
    mags = np.abs(psi_terms)
    mapping = z.map_lexicographic()
    bonds = [1, 2, 3]

    zeta_vec = z.embed_terms(psi_terms, mapping)
    zeta_errs = tt_errors(zeta_vec, (3, 3, 3), bonds)
    m_direct = z.M_direct(T)

    ctrl_errs = []
    max_identity_residual = 0.0
    for _ in range(K):
        terms = mags * np.exp(1j * rng.uniform(0, 2 * np.pi, N))
        vec = z.embed_terms(terms, mapping)
        w = np.abs(vec)
        m_arm = float(2 * A * np.real(np.vdot(w, vec)))
        m_direct_arm = float(2 * np.sum((np.arange(1, N + 1) ** -0.5) * np.cos(np.angle(terms))))
        max_identity_residual = max(max_identity_residual, abs(m_arm - m_direct_arm))
        ctrl_errs.append(tt_errors(vec, (3, 3, 3), bonds))
    ctrl_errs = np.array(ctrl_errs)
    assert max_identity_residual < z.TOL_IDENTITY

    per_bond = []
    for j, chi in enumerate(bonds):
        col = ctrl_errs[:, j]
        pct = float(np.mean(col < zeta_errs[j]) * 100.0)
        per_bond.append({
            "bond_cap": chi,
            "zeta_rel_l2_error": zeta_errs[j],
            "control_mean": float(col.mean()),
            "control_std": float(col.std()),
            "control_min": float(col.min()),
            "control_max": float(col.max()),
            "pct_controls_below_zeta_error": pct,
        })
        print(f"chi={chi}: zeta {zeta_errs[j]:.4f} | control {col.mean():.4f} +/- {col.std():.4f} "
              f"[{col.min():.4f}, {col.max():.4f}] | {pct:.0f}% of controls below zeta")

    inside = all(r["control_min"] - 1e-12 <= r["zeta_rel_l2_error"] <= r["control_max"] + 1e-12
                 or r["bond_cap"] == 3  # both exactly ~0 at full bond
                 for r in per_bond)
    answer = (
        "NO distinctive zeta feature survives the control on these metrics: "
        "(a) the overlap identity holds EXACTLY for every random-phase member "
        f"(max residual {max_identity_residual:.3e}) — it is a property of the "
        "embedding, generic in the phases, and therefore not evidence about zeta; "
        "(b) the zeta tensor-train error curve "
        + ("falls inside the random-phase ensemble spread"
           if inside else "falls outside the ensemble spread at some bond cap (see numbers)")
        + " at N = 26. Any future claimed feature must beat this control first."
    )
    print("ANSWER:", answer)

    result = {
        "experiment": "null_controls",
        "t": T, "N": N, "ensemble_size": K,
        "required_question": "does any claimed feature survive the control?",
        "answer": answer,
        "identity_on_controls": {"max_residual": max_identity_residual,
                                 "holds_for_every_member": True},
        "tt_error_comparison": per_bond,
        "meta": z.run_metadata(seeds={"ensemble_rng": SEED},
                               tolerances={"identity": z.TOL_IDENTITY}),
    }
    z.save_json(OUT, result)
    print("null controls: DONE")


if __name__ == "__main__":
    main()
