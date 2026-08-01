#!/usr/bin/env python3
"""Experiment 5 — ZETA-HARP-TENSOR-COMPRESS v0.

The Harp amplitude vector at t = 4400 (N = 26) is reshaped 3x3x3 (qutrit layout,
padded to 27 with the reserved zero anchor at index 0) and 2x2x2x2x2 (qubit
layout, padded to 32), then decomposed by sequential-SVD tensor train. We report
relative L2 reconstruction error and |Delta M(t)| as functions of the bond-
dimension cap, for the zeta arm and nine control arms (10 arms total, matching
research/quantum/ZETA_HARP_TENSOR_COMPRESSION_PLAN.md):

   1. zeta_qutrit_lex        zeta phases, qutrit 3x3x3, lexicographic order
   2. zeta_qubit             zeta phases, qubit 2^5 layout, lexicographic order
   3. random_phase_qutrit    same magnitudes, iid uniform phases (seeded)
   4. permuted_phase_qutrit  zeta phases randomly permuted across terms
   5. amplitude_sorted_qutrit terms reordered by descending magnitude
   6. phase_sorted_qutrit    terms reordered by increasing phase
   7. mismatched_reshape_qutrit zeta amplitudes scattered by a fixed wrong
                             (seeded-permutation) assignment before the 3x3x3 reshape
   8. random_phase_qubit     control 3 in the qubit layout
   9. permuted_phase_qubit   control 4 in the qubit layout
  10. zeta_qutrit_balanced   zeta phases, balanced-ternary term->state order

Plus one scale probe at t = 10^6 (N = 398, padded into 3^6 = 729 and reshaped as
a six-qutrit train) so the N-scaling axis exists.

NUMBERS ONLY. No advantage language. The four confound distinctions (arithmetic
structure vs ordering vs low-N vs loose tolerance) are stated explicitly in the
output.
"""

import os
import numpy as np

import zhq_common as z

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs",
                   "tensor_compression_benchmark.json")

T_MAIN = 4400.0
T_SCALE = 1.0e6
SEEDS = {"random_phase": 771001, "permuted_phase": 771002, "mismatched_reshape": 771003}


def tt_curve(vec, shape, max_bonds, A, m_ref):
    """Error-vs-bond-cap curve for vec reshaped to `shape`."""
    x = vec.reshape(shape)
    nrm = np.linalg.norm(vec)
    w_ref = np.abs(vec)  # |w>-analog with the same magnitudes, for M reconstruction
    rows = []
    for chi in max_bonds:
        cores = z.tt_svd(x, chi)
        rec = z.tt_reconstruct(cores).reshape(-1)
        rel_err = float(np.linalg.norm(rec - vec) / nrm)
        m_rec = float(2 * A * np.real(np.vdot(w_ref, rec)))
        rows.append({
            "bond_cap": int(chi),
            "rel_l2_error": rel_err,
            "M_reconstructed": m_rec,
            "abs_M_error": abs(m_rec - m_ref),
            "params": z.tt_param_count(cores),
        })
    return rows


def main():
    N, A, psi_terms = z.psi_state(T_MAIN)
    assert N == 26
    mags = np.abs(psi_terms)
    phis = np.angle(psi_terms)
    m_ref = z.M_direct(T_MAIN)

    lex = z.map_lexicographic()
    bal = z.map_balanced_ternary()

    def q3(terms, mapping=lex):
        return z.embed_terms(terms, mapping, dim=27)

    def q2(terms):
        v = np.zeros(32, dtype=np.complex128)
        v[1:27] = terms
        return v

    rng_rp = np.random.default_rng(SEEDS["random_phase"])
    rand_phase_terms = mags * np.exp(1j * rng_rp.uniform(0, 2 * np.pi, N))
    rng_pp = np.random.default_rng(SEEDS["permuted_phase"])
    perm = rng_pp.permutation(N)
    perm_phase_terms = mags * np.exp(1j * phis[perm])
    amp_order = np.argsort(-mags)
    phase_order = np.argsort(phis)
    rng_mm = np.random.default_rng(SEEDS["mismatched_reshape"])
    wrong_assign = rng_mm.permutation(np.arange(1, 27))
    mismatched = np.zeros(27, dtype=np.complex128)
    for i, n in enumerate(wrong_assign):
        mismatched[n] = psi_terms[i]

    # For control arms, M is reconstructed against the matched |w>-analog of that
    # arm (same magnitudes), i.e. each arm is scored against its own reference sum.
    arms = {
        "zeta_qutrit_lex":         (q3(psi_terms),               (3, 3, 3), [1, 2, 3]),
        "zeta_qubit":              (q2(psi_terms),               (2, 2, 2, 2, 2), [1, 2, 3, 4]),
        "random_phase_qutrit":     (q3(rand_phase_terms),        (3, 3, 3), [1, 2, 3]),
        "permuted_phase_qutrit":   (q3(perm_phase_terms),        (3, 3, 3), [1, 2, 3]),
        "amplitude_sorted_qutrit": (q3(psi_terms[amp_order]),    (3, 3, 3), [1, 2, 3]),
        "phase_sorted_qutrit":     (q3(psi_terms[phase_order]),  (3, 3, 3), [1, 2, 3]),
        "mismatched_reshape_qutrit": (mismatched,                (3, 3, 3), [1, 2, 3]),
        "random_phase_qubit":      (q2(rand_phase_terms),        (2, 2, 2, 2, 2), [1, 2, 3, 4]),
        "permuted_phase_qubit":    (q2(perm_phase_terms),        (2, 2, 2, 2, 2), [1, 2, 3, 4]),
        "zeta_qutrit_balanced":    (q3(psi_terms, bal),          (3, 3, 3), [1, 2, 3]),
    }
    assert len(arms) == 10

    arm_results = {}
    for name, (vec, shape, bonds) in arms.items():
        m_arm_ref = float(2 * A * np.real(np.vdot(np.abs(vec), vec)))
        curve = tt_curve(vec, shape, bonds, A, m_arm_ref)
        arm_results[name] = {"shape": list(shape), "M_reference_for_arm": m_arm_ref,
                             "curve": curve}
        head = ", ".join(f"chi={r['bond_cap']}: {r['rel_l2_error']:.4f}" for r in curve)
        print(f"{name:28s} {head}")

    # Scale probe: t ~ 1e6, N = 398, padded into 3^6 = 729, six-qutrit train.
    N6, A6, psi6_terms = z.psi_state(T_SCALE)
    assert N6 == 398
    vec6 = np.zeros(729, dtype=np.complex128)
    vec6[1:N6 + 1] = psi6_terms          # index 0 reserved, lexicographic order
    m6_ref = float(2 * A6 * np.real(np.vdot(np.abs(vec6), vec6)))
    scale_bonds = [1, 2, 3, 6, 9, 14, 20, 27]
    scale_curve = tt_curve(vec6, (3, 3, 3, 3, 3, 3), scale_bonds, A6, m6_ref)
    print("scale probe (t=1e6, N=398, 3^6): "
          + ", ".join(f"chi={r['bond_cap']}: {r['rel_l2_error']:.4f}" for r in scale_curve))

    confounds = {
        "1_arithmetic_structure_vs_ordering": (
            "any zeta-vs-random difference must be split between the arithmetic "
            "structure of the phases theta(t) - t ln n and the mere ORDERING of terms "
            "in the register; compare arm 1 against arms 4/5/6/10 (same multiset of "
            "amplitudes, different order) before attributing anything to arithmetic"
        ),
        "2_ordering_vs_layout": (
            "the term->state assignment is a chosen layout; arm 7 (mismatched reshape) "
            "and arm 10 (balanced-ternary order) measure how much the curve moves under "
            "layout changes alone, with the phase content untouched"
        ),
        "3_low_N": (
            "at N = 26 the full tensor is 3x3x3 with maximal bond dimension 3; every "
            "curve is dominated by the smallness of the register, and NO compressibility "
            "statement at N = 26 generalizes; the t = 1e6 (N = 398) probe exists to give "
            "the N-scaling axis, and even that is a single point on it"
        ),
        "4_loose_tolerance": (
            "a 'compresses well' statement is meaningless without a stated tolerance; "
            "full error-vs-bond curves are reported instead of any thresholded verdict, "
            "and all tolerances used anywhere in this experiment are recorded in meta"
        ),
    }

    result = {
        "experiment": "tensor_compression_benchmark",
        "version": "ZETA-HARP-TENSOR-COMPRESS v0",
        "t_main": T_MAIN, "N_main": N, "t_scale": T_SCALE, "N_scale": N6,
        "arms": arm_results,
        "scale_probe": {"shape": [3, 3, 3, 3, 3, 3], "padded_dim": 729,
                        "M_reference_for_arm": m6_ref, "curve": scale_curve},
        "confound_distinctions": confounds,
        "reading": (
            "numbers only: at N = 26 all qutrit arms reach exact reconstruction at the "
            "maximal bond cap 3 and all qubit arms at cap 4, as dimension counting "
            "requires; differences between zeta and control arms at intermediate caps "
            "are reported above without interpretation"
        ),
        "notes": [
            "arm 5 (amplitude_sorted_qutrit) coincides with arm 1 because the "
            "magnitudes n^(-1/4) are already in descending order — the sort is the "
            "identity permutation; it is retained as the ordering-confound null it is",
        ],
        "meta": z.run_metadata(seeds=SEEDS, tolerances={"tt_full_bond": z.TOL_TT_FULL}),
    }
    z.save_json(OUT, result)
    print("tensor compression benchmark: DONE (numbers only)")


if __name__ == "__main__":
    main()
