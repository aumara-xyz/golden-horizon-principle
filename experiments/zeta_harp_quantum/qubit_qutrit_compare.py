#!/usr/bin/env python3
"""Experiment 4 — the same 26 amplitudes in a 5-qubit (32-dim) and a 3-qutrit
(27-dim) register.

Both registers reconstruct M(t) identically to tolerance; the only difference is
bookkeeping: 32 states with 6 unused vs 27 states with 1 unused (the reserved
|0,0,0| anchor). A random permutation of the register basis applied to BOTH
states leaves the reconstructed M(t) unchanged (inner products are basis-blind),
which is the machine-checked reminder that no register layout carries physical
content here.

The closeness of 27 to 26 proves nothing about hardware superiority of qutrits;
see research/quantum/ZETA_HARP_QUANTUM_RESOURCE_AUDIT.md.
"""

import os
import numpy as np

import zhq_common as z

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "qubit_qutrit_compare.json")

T_POINTS = [4300.0, 4400.0, 4500.0]
PERM_SEED = 314159
N_PERMS = 5


def embed_flat(terms, dim):
    """Terms 1..26 at indices 1..26 of a dim-vector; index 0 reserved with zero amplitude."""
    v = np.zeros(dim, dtype=np.complex128)
    v[1:len(terms) + 1] = terms
    return v


def main():
    rng = np.random.default_rng(PERM_SEED)
    rows = []
    for t in T_POINTS:
        N, A, psi_terms = z.psi_state(t)
        w_terms = z.w_state(N)
        m_direct = z.M_direct(t)

        row = {"t": t, "N": N, "M_direct": m_direct, "registers": {}}
        for label, dim in (("qubit_5x2_dim32", 32), ("qutrit_3x3_dim27", 27)):
            psi_r = embed_flat(psi_terms, dim)
            w_r = embed_flat(w_terms, dim)
            m = float(2 * A * np.real(np.vdot(w_r, psi_r)))
            unused = dim - N
            perm_spread = 0.0
            for _ in range(N_PERMS):
                p = rng.permutation(dim)
                m_p = float(2 * A * np.real(np.vdot(w_r[p], psi_r[p])))
                perm_spread = max(perm_spread, abs(m_p - m))
            assert abs(m - m_direct) < z.TOL_IDENTITY
            assert perm_spread < z.TOL_IDENTITY
            row["registers"][label] = {
                "dim": dim, "used_states": N, "unused_states": unused,
                "M_reconstructed": m, "abs_err_vs_direct": abs(m - m_direct),
                "max_abs_change_under_basis_permutation": perm_spread,
            }
        diff = abs(row["registers"]["qubit_5x2_dim32"]["M_reconstructed"]
                   - row["registers"]["qutrit_3x3_dim27"]["M_reconstructed"])
        assert diff < z.TOL_IDENTITY
        row["qubit_vs_qutrit_abs_diff"] = diff
        rows.append(row)
        print(f"t={t}: M_direct={m_direct:+.12f}, qubit-vs-qutrit diff {diff:.3e}, "
              f"unused states 6 (qubit) / 1 (qutrit)")

    result = {
        "experiment": "qubit_qutrit_compare",
        "resource_table_N26": {
            "qubit": {"units": 5, "states": 32, "unused": 6},
            "qutrit": {"units": 3, "states": 27, "unused": 1},
            "warning": "closeness of 27 to 26 proves nothing about hardware superiority",
        },
        "points": rows,
        "meta": z.run_metadata(
            seeds={"permutation_rng": PERM_SEED, "n_permutations_per_register": N_PERMS},
            tolerances={"identity": z.TOL_IDENTITY},
        ),
    }
    z.save_json(OUT, result)
    print("qubit/qutrit compare: PASS")


if __name__ == "__main__":
    main()
