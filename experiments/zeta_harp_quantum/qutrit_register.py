#!/usr/bin/env python3
"""Experiment 2 — three-qutrit register mappings for the 26 active terms.

H27 = C3 (x) C3 (x) C3 is a CHOSEN register layout, never a zeta-derived topology.
Three mappings of the terms n = 1..26 onto the 26 noncentral basis states:

  1. lexicographic       — n -> base-3 digits of n
  2. balanced_ternary    — n -> balanced-ternary digits of (n - 13), shifted to trits
  3. gray_ternary        — n -> reflected-ternary Gray code of n

Each is verified to be a bijection onto the 26 noncentral states, with |0,0,0>
(the RESERVED REFERENCE BASIS STATE / INTERFACE ANCHOR) carrying exactly zero
amplitude. No mapping search was performed for pretty results: these are the
three mappings named in the adopted directive, reported neutrally.

The reconstructed M(t) is identical under all three mappings (basis relabeling
cannot change an inner product when applied to both states).
"""

import os
import numpy as np

import zhq_common as z

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "qutrit_register.json")

T_CHECK = [4300.0, 4400.0, 4500.0]


def mapping_report(name, mapping):
    indices = [z.trits_to_index(mapping[n]) for n in range(1, 27)]
    is_bijection = (len(set(indices)) == 26) and (0 not in indices) and all(0 <= i < 27 for i in indices)
    doc = {str(n): {"trits": list(mapping[n]), "index": z.trits_to_index(mapping[n])}
           for n in range(1, 27)}
    return indices, is_bijection, doc


def main():
    results = {"experiment": "qutrit_register", "mappings": {}, "reconstruction": {}}
    all_maps = {name: fn() for name, fn in z.MAPPINGS.items()}

    # The three mappings must be pairwise DISTINCT as index maps (guards against the
    # shift-collapse bug where balanced ternary degenerates to lexicographic).
    names = list(all_maps)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            mi, mj = all_maps[names[i]], all_maps[names[j]]
            assert any(mi[n] != mj[n] for n in range(1, 27)), \
                f"mappings {names[i]} and {names[j]} coincide"
    results["mappings_pairwise_distinct"] = True

    for name, mapping in all_maps.items():
        indices, is_bijection, doc = mapping_report(name, mapping)
        assert is_bijection, f"{name} is not a bijection onto the noncentral states"
        results["mappings"][name] = {
            "bijection_onto_26_noncentral_states": is_bijection,
            "reserved_state_index_0_used": False,
            "assignment": doc,
        }
        print(f"mapping {name}: bijection OK, |0,0,0> reserved")

    for t in T_CHECK:
        N, A, psi_terms = z.psi_state(t)
        w_terms = z.w_state(N)
        m_direct = z.M_direct(t)
        per_map = {}
        ms = []
        for name, mapping in all_maps.items():
            psi27 = z.embed_terms(psi_terms, mapping)
            w27 = z.embed_terms(w_terms, mapping)
            assert psi27[0] == 0 and w27[0] == 0, "reserved |0,0,0> must carry zero amplitude"
            m = float(2.0 * A * np.real(np.vdot(w27, psi27)))
            per_map[name] = {"M_reconstructed": m, "abs_err_vs_direct": abs(m - m_direct),
                             "anchor_amplitude": 0.0}
            ms.append(m)
            assert abs(m - m_direct) < z.TOL_IDENTITY
        spread = max(ms) - min(ms)
        assert spread < z.TOL_IDENTITY
        results["reconstruction"][str(t)] = {
            "M_direct": m_direct, "per_mapping": per_map,
            "cross_mapping_spread": spread,
        }
        print(f"t={t}: M_direct={m_direct:+.12f}, cross-mapping spread {spread:.3e}")

    results["statement"] = (
        "All three mappings are exact bijections of terms 1..26 onto the 26 noncentral "
        "three-qutrit basis states; |0,0,0> is reserved with zero amplitude in every "
        "mapping; reconstructed M(t) is mapping-independent. The 3x3x3 layout is a "
        "chosen register, not a zeta-derived topology. All three mappings are reported "
        "neutrally; none was selected for aesthetics of results."
    )
    results["meta"] = z.run_metadata(tolerances={"identity": z.TOL_IDENTITY})
    z.save_json(OUT, results)
    print("qutrit register: PASS")


if __name__ == "__main__":
    main()
