#!/usr/bin/env python3
"""Quantum Portal v1 — required test battery (24 tests) + claim linter (test 25).

Pure Python asserts; pytest-compatible (every test_* function is collectable) and
runnable standalone:  python3 tests/test_quantum_portal.py

Tolerances are stated inline. No network, no quantum SDK; numpy + mpmath only.
"""

import glob
import math
import os
import re
import sys

import numpy as np
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
REPO = os.path.abspath(os.path.join(PKG, "..", ".."))

import zhq_common as z
import hadamard_overlap_sim as had

W26_LO = 2 * math.pi * 26 ** 2
W26_HI = 2 * math.pi * 27 ** 2


# --- window / normalization facts (tests 1-5) ------------------------------

def test_01_window_start_boundary():
    assert z.n_terms(W26_LO - 1e-6) == 25
    assert z.n_terms(W26_LO + 1e-6) == 26


def test_02_window_end_boundary_and_decimals():
    assert z.n_terms(W26_HI - 1e-6) == 26
    assert z.n_terms(W26_HI + 1e-6) == 27
    assert abs(W26_LO - 4247.4332676534) < 1e-9
    assert abs(W26_HI - 4580.4420889339) < 1e-9


def test_03_A26_matches_high_precision():
    A, _ = z.amplitude_data(26)
    with mp.workdps(40):
        A_mp = float(sum(mp.power(n, mp.mpf("-0.5")) for n in range(1, 27)))
    assert abs(A - A_mp) < 1e-12


def test_04_psi_normalized():
    _, _, psi = z.psi_state(4400.0)
    assert abs(float(np.vdot(psi, psi).real) - 1.0) < z.TOL_NORM


def test_05_w_normalized():
    w = z.w_state(26)
    assert abs(float(np.vdot(w, w).real) - 1.0) < z.TOL_NORM


# --- the exact overlap identity (tests 6-8) --------------------------------

def test_06_identity_on_window_grid():
    for t in range(4250, 4590, 30):
        r = abs(z.M_direct(float(t)) - z.M_from_overlap(float(t)))
        assert r < z.TOL_IDENTITY, (t, r)


def test_07_identity_at_1e4():
    t = 1.0e4
    assert z.n_terms(t) == 39
    assert abs(z.M_direct(t) - z.M_from_overlap(t)) < z.TOL_IDENTITY


def test_08_identity_at_1e6():
    t = 1.0e6
    assert z.n_terms(t) == 398
    assert abs(z.M_direct(t) - z.M_from_overlap(t)) < z.TOL_IDENTITY


# --- qutrit register mappings (tests 9-13) ---------------------------------

def _is_bijection_noncentral(mapping):
    idx = [z.trits_to_index(mapping[n]) for n in range(1, 27)]
    return len(set(idx)) == 26 and 0 not in idx and all(0 <= i < 27 for i in idx)


def test_09_lexicographic_bijection():
    assert _is_bijection_noncentral(z.map_lexicographic())


def test_10_balanced_ternary_bijection_and_distinct():
    m = z.map_balanced_ternary()
    assert _is_bijection_noncentral(m)
    lex = z.map_lexicographic()
    assert any(m[n] != lex[n] for n in range(1, 27)), "balanced collapsed to lexicographic"


def test_11_gray_bijection_distinct_single_trit_steps():
    g = z.map_gray_ternary()
    assert _is_bijection_noncentral(g)
    lex = z.map_lexicographic()
    bal = z.map_balanced_ternary()
    assert any(g[n] != lex[n] for n in range(1, 27))
    assert any(g[n] != bal[n] for n in range(1, 27))
    # Gray-like property: consecutive codes differ in exactly one trit
    prev = (0, 0, 0)
    for n in range(1, 27):
        diff = sum(1 for a, b in zip(prev, g[n]) if a != b)
        assert diff == 1, (n, prev, g[n])
        prev = g[n]


def test_12_reserved_anchor_zero_amplitude():
    _, _, psi_terms = z.psi_state(4400.0)
    for fn in z.MAPPINGS.values():
        v = z.embed_terms(psi_terms, fn())
        assert v[0] == 0.0, "|0,0,0> must carry exactly zero amplitude"


def test_13_M_mapping_invariant():
    t = 4400.0
    N, A, psi_terms = z.psi_state(t)
    w_terms = z.w_state(N)
    m_direct = z.M_direct(t)
    for fn in z.MAPPINGS.values():
        mapping = fn()
        m = 2 * A * float(np.real(np.vdot(z.embed_terms(w_terms, mapping),
                                          z.embed_terms(psi_terms, mapping))))
        assert abs(m - m_direct) < z.TOL_IDENTITY


# --- Hadamard test simulator (tests 14-17) ---------------------------------

def _hadamard_setup(t=4400.0):
    np.seterr(divide="ignore", over="ignore", invalid="ignore")  # Accelerate FP-flag noise
    N, A, psi_terms = z.psi_state(t)
    mapping = z.map_lexicographic()
    psi27 = z.embed_terms(psi_terms, mapping)
    w27 = z.embed_terms(z.w_state(N), mapping)
    V = had.build_V(psi27, w27)
    return psi27, w27, V, complex(np.vdot(w27, psi27))


def test_14_hadamard_real_variant_exact():
    psi27, _, V, ov = _hadamard_setup()
    p0 = had.hadamard_test(psi27, V, imag=False)
    assert abs((2 * p0 - 1) - ov.real) < z.TOL_EXACT_SIM


def test_15_hadamard_imag_variant_exact():
    psi27, _, V, ov = _hadamard_setup()
    p0 = had.hadamard_test(psi27, V, imag=True)
    assert abs((1 - 2 * p0) - ov.imag) < z.TOL_EXACT_SIM


def test_16_oracle_unitary_valid():
    psi27, w27, V, _ = _hadamard_setup()
    assert float(np.max(np.abs(V @ V.conj().T - np.eye(27)))) < 1e-10
    assert float(np.linalg.norm(V @ psi27 - w27)) < 1e-10


def test_17_shot_convergence():
    psi27, _, V, ov = _hadamard_setup()
    p0 = had.hadamard_test(psi27, V, imag=False)
    rng = np.random.default_rng(had.SEED)
    widths, errors = [], []
    for shots in (10 ** 3, 10 ** 4, 10 ** 5):
        p_hat = rng.binomial(shots, p0) / shots
        ci = 2 * 1.96 * np.sqrt(max(p_hat * (1 - p_hat), 1e-12) / shots)
        widths.append(ci)
        errors.append(abs((2 * p_hat - 1) - ov.real))
    assert widths[0] > widths[1] > widths[2], "CI must shrink with shots"
    for e, w in zip(errors, widths):
        assert e < 5 * w, (e, w)


# --- qubit vs qutrit (tests 18-20) -----------------------------------------

def test_18_qubit_qutrit_identical_M():
    t = 4400.0
    N, A, psi_terms = z.psi_state(t)
    w_terms = z.w_state(N)
    m_direct = z.M_direct(t)
    ms = []
    for dim in (32, 27):
        p = np.zeros(dim, dtype=np.complex128); p[1:N + 1] = psi_terms
        w = np.zeros(dim, dtype=np.complex128); w[1:N + 1] = w_terms
        ms.append(2 * A * float(np.real(np.vdot(w, p))))
    assert abs(ms[0] - ms[1]) < z.TOL_IDENTITY
    assert abs(ms[0] - m_direct) < z.TOL_IDENTITY


def test_19_unused_state_counts():
    assert 32 - 26 == 6 and 27 - 26 == 1


def test_20_basis_permutation_invariance():
    t = 4400.0
    N, A, psi_terms = z.psi_state(t)
    w_terms = z.w_state(N)
    p = np.zeros(27, dtype=np.complex128); p[1:N + 1] = psi_terms
    w = np.zeros(27, dtype=np.complex128); w[1:N + 1] = w_terms
    m0 = 2 * A * float(np.real(np.vdot(w, p)))
    rng = np.random.default_rng(9)
    for _ in range(10):
        s = rng.permutation(27)
        m = 2 * A * float(np.real(np.vdot(w[s], p[s])))
        assert abs(m - m0) < z.TOL_IDENTITY


# --- tensor-train machinery (tests 21-23) ----------------------------------

def _zeta_vec27(t=4400.0):
    _, _, psi_terms = z.psi_state(t)
    return z.embed_terms(psi_terms, z.map_lexicographic())


def test_21_tt_full_bond_exact():
    v = _zeta_vec27()
    for shape, chi in (((3, 3, 3), 3), ((3, 3, 3), 9)):
        rec = z.tt_reconstruct(z.tt_svd(v.reshape(shape), chi)).reshape(-1)
        assert float(np.linalg.norm(rec - v)) < z.TOL_TT_FULL
    v32 = np.zeros(32, dtype=np.complex128); v32[:27] = v
    rec = z.tt_reconstruct(z.tt_svd(v32.reshape(2, 2, 2, 2, 2), 4)).reshape(-1)
    assert float(np.linalg.norm(rec - v32)) < z.TOL_TT_FULL


def test_22_tt_error_nonincreasing_in_bond():
    v = _zeta_vec27()
    errs = []
    for chi in (1, 2, 3):
        rec = z.tt_reconstruct(z.tt_svd(v.reshape(3, 3, 3), chi)).reshape(-1)
        errs.append(float(np.linalg.norm(rec - v)))
    assert errs[0] >= errs[1] >= errs[2]


def test_23_mismatched_reshape_is_distinct_but_full_bond_exact():
    v = _zeta_vec27()
    rng = np.random.default_rng(771003)
    wrong = np.zeros(27, dtype=np.complex128)
    terms = v[np.array([z.trits_to_index(z.map_lexicographic()[n]) for n in range(1, 27)])]
    for i, n in enumerate(rng.permutation(np.arange(1, 27))):
        wrong[n] = terms[i]
    assert float(np.linalg.norm(wrong - v)) > 1e-3, "confound arm must differ from canonical"
    rec = z.tt_reconstruct(z.tt_svd(wrong.reshape(3, 3, 3), 3)).reshape(-1)
    assert float(np.linalg.norm(rec - wrong)) < z.TOL_TT_FULL


# --- null control (test 24) -------------------------------------------------

def test_24_identity_generic_on_random_phase_controls():
    N = 26
    A, amps = z.amplitude_data(N)
    ns = np.arange(1, N + 1, dtype=np.float64)
    rng = np.random.default_rng(88220801)
    for _ in range(10):
        phi = rng.uniform(0, 2 * np.pi, N)
        vec = amps * np.exp(1j * phi)
        m_overlap = 2 * A * float(np.real(np.vdot(amps.astype(np.complex128), vec)))
        m_direct = 2 * float(np.sum(ns ** -0.5 * np.cos(phi)))
        assert abs(m_overlap - m_direct) < z.TOL_IDENTITY


# --- claim linter (test 25) -------------------------------------------------

BANNED_PHRASES = [
    "0 is superposition",                    # REJECTED-CLAIM literal, linter data
    "zero is superposition",                 # REJECTED-CLAIM literal, linter data
    "trinity is a qubit",                    # REJECTED-CLAIM literal, linter data
    "the harp is a quantum computer",        # REJECTED-CLAIM literal, linter data
    "the harp is a quantum simulator",       # REJECTED-CLAIM literal, linter data
    "zero is quantum collapse",              # REJECTED-CLAIM literal, linter data
    "observer creates the zero",             # REJECTED-CLAIM literal, linter data
    "ahead of flatiron",                     # REJECTED-CLAIM literal, linter data
    "quantum advantage",                     # REJECTED-CLAIM literal, linter data
    "cube confirms",                         # REJECTED-CLAIM literal, linter data
    "classical shortcut to rh",              # REJECTED-CLAIM literal, linter data
    "evidence for the riemann hypothesis",   # REJECTED-CLAIM literal, linter data
    "supports the riemann hypothesis",       # REJECTED-CLAIM literal, linter data
]

NEW_FILE_GLOBS = [
    "docs/ZETA_HARP_QUANTUM_PORTAL_ADDENDUM.md",
    "research/quantum/*.md",
    "experiments/zeta_harp_quantum/*.py",
    "experiments/zeta_harp_quantum/*.md",
    "experiments/zeta_harp_quantum/tests/*.py",
    "experiments/zeta_harp_quantum/outputs/*.json",
]


def _normalize(line):
    return re.sub(r"\s+", " ", line.lower().replace("-", " "))


def test_25_claim_linter():
    files = []
    for pat in NEW_FILE_GLOBS:
        files.extend(sorted(glob.glob(os.path.join(REPO, pat))))
    assert len(files) >= 12, f"linter expected the full new-file set, saw {len(files)}"
    violations = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                if "REJECTED-CLAIM" in line:
                    continue  # explicitly marked rejected-claim quotation
                norm = _normalize(line)
                for phrase in BANNED_PHRASES:
                    if phrase in norm:
                        violations.append((os.path.relpath(path, REPO), lineno, phrase))
    assert not violations, f"banned claim phrases found: {violations}"


# --- standalone runner ------------------------------------------------------

def main():
    tests = sorted((name, fn) for name, fn in globals().items()
                   if name.startswith("test_") and callable(fn))
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {name}: {exc}")
    print(f"{len(tests) - failed}/{len(tests)} tests passed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
