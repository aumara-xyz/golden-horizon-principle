#!/usr/bin/env python3
"""AH.4-P1 pipeline — the anyon fusion-tree recoverability discriminator.

Preregistration (SIGNED, locked 2026-08-01):
    experiments/AH4_P1_ANYON_RECOVERABILITY_PREREG_v1.md
Gate 0 (pentagon identity, PASS 2026-07-29):
    experiments/ah4_p1_pentagon_gate.py   (its category data is REUSED here)
Run manifest (declared before execution):
    experiments/ah4_p1_run_manifest.md

ONE parametrised pipeline over (category, constant).  NO per-arm
special-casing: every arm supplies only DATA (its basis strings, its
carrier-to-label adjacency kind, its theory dimension), and the identical
channel, identical Petz recovery, and identical entanglement-fidelity scorer
run on that data.  Any code branch keyed on an arm name below this docstring
is a build defect.

ARMS (n = 12 carriers, locked by the prereg)
--------------------------------------------
  fib       fusion-path (Bratteli) basis of 12 tau anyons, total charge
            vacuum.  dim = Fib(11) = 89 (Fibonacci numbers, F1=F2=1).
  ising     fusion-path basis of 12 sigma anyons, vacuum sector.
            dim = 2^5 = 32.
  z3        abelian arm: free leaf charges in Z3, total charge 0 mod 3.
            dim = 3^11 = 177147.  Everything is diagonal in the leaf basis,
            so the closed-form scorer below is exact without dense matrices.
  classical 12-carrier product-basis arm (bits, no charge constraint).
            dim = 2^12 = 4096.  The identical code rule instantiated here
            yields a majority-split (repetition-style) partition; no
            classical-specific code exists anywhere in this file.

CHANNEL (identical rule, all arms)
----------------------------------
For erased carrier set E: completely dephase the fusion-path internal-edge
labels adjacent to positions in E (path arms) / the leaf labels in E
(product arms).  This is a pinching:

    N(rho) = sum_kappa  P_kappa rho P_kappa

where kappa ranges over joint assignments of the dephased labels and
P_kappa projects onto the basis strings consistent with kappa.  The Kraus
operators are these orthogonal projectors; they sum to the identity, so N
is exactly trace-preserving.  Full spec in the run manifest.

RECOVERY: Petz (transpose) map of N with respect to the code space,
sigma = P_code / d_L:

    R(X) = sigma^{1/2} N^dag( N(sigma)^{-1/2} X N(sigma)^{-1/2} ) sigma^{1/2}

(N^dag = N for a pinching; inverses are pseudo-inverses on support).

SCORE: entanglement fidelity of R o N on the logical space,
F_e = <Omega| (I (x) R o N)(|Omega><Omega|) |Omega>, |Omega> the maximally
entangled state between a d_L-dim reference and the code space.

CLOSED FORM (derivation in the manifest; verified against a literal dense
construction in --selftest):  because N is a pinching, N(sigma) is
block-diagonal over kappa with blocks of rank <= d_L, and

    F_e = (1/4) * sum_kappa ( Tr sqrt(G_kappa) )^2          [d_L = 2]

where G_kappa is the 2x2 Gram matrix of the two code basis vectors
restricted to pinch block kappa.  This is what makes the 3^11-dim z3 arm
exact through the same interface.

PHI TRIPWIRE (prereg section 1.3): the golden ratio appears in this file
ONLY as the Axis-B allocation constant `golden`, on identical footing with
silver/bronze/uniform, inside the code-space selection profile.  It appears
NOWHERE in the erasure channel, the noise model, the recovery routine, or
the scorer.  The quantum dimension of the Fibonacci category is never used
by the pipeline at all; it is an output of the fusion rule, checked at
gate 0.

Run:
    python3 experiments/ah4_p1_pipeline.py --selftest   # gate + self-tests
    python3 experiments/ah4_p1_pipeline.py --run        # full 4x4 factorial
"""

import argparse
import importlib.util
import json
import math
import os
import sys
import warnings

import numpy as np

# Environment artifact, documented in the run manifest: numpy built against
# macOS Accelerate raises spurious "divide by zero / overflow / invalid
# encountered in matmul" RuntimeWarnings on ANY matmul (verified: an
# all-ones 50x50 @ 50x50 triggers all three in this environment; the BLAS
# leaves FP status flags set).  Correctness here is enforced by explicit
# assertions and the dense-vs-closed-form cross-check in --selftest, never
# by FP warnings, so exactly these spurious messages are filtered.
warnings.filterwarnings("ignore", message=".*encountered in matmul")

# ----------------------------------------------------------------- constants
N_CARRIERS = 12                      # locked, prereg section 1.4
D_LOGICAL = 2                        # locked by the build order; manifest
ERASURE_FRACTIONS = (0.25, 0.50, 0.75)
MODES = ("scattered", "burst")       # burst reported separately (stressor)
SEEDS = tuple(range(1000, 1020))     # prereg: seeds 1000-1019 inclusive

# Axis B allocation constants (metallic means; uniform == flat profile).
# The ONLY sanctioned appearance of the golden ratio in this pipeline
# (prereg section 1.3, declared entry point #2).
CONSTANTS = {
    "golden": (1.0 + math.sqrt(5.0)) / 2.0,     # 1.618033988749895
    "silver": 1.0 + math.sqrt(2.0),             # 2.414213562373095
    "bronze": (3.0 + math.sqrt(13.0)) / 2.0,    # 3.302775637731995
    "uniform": 1.0,                              # c = 1  =>  w_i = 1 (flat)
}

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_gate():
    """Import the verified gate-0 module (category data source of truth)."""
    path = os.path.join(_HERE, "ah4_p1_pentagon_gate.py")
    spec = importlib.util.spec_from_file_location("ah4_p1_pentagon_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GATE = _load_gate()

# --------------------------------------------------------------------- arms
# Each arm is DATA: (basis, kind, theory_dim, theory_note).
#   basis : int8 array (D, 12); column j holds the numeric label of slot j.
#           path arms:   slot j = internal edge e_{j+1} of the left-to-right
#                        (Bratteli) fusion chain; e_12 is the total charge.
#           product arms: slot j = leaf label of carrier j.
#   kind  : "path" or "product" — declares WHERE the pairing information
#           lives relative to a carrier (prereg channel definition), i.e.
#           which slots a carrier is adjacent to.  This is channel-spec
#           data, not per-arm code.
# Numeric label maps (used for basis columns, signatures, and pinch keys):
#   fib   : '1' -> 0, 't' -> 1
#   ising : '1' -> 0, 's' -> 1, 'p' -> 2
#   z3    : charge q -> q
#   classical : bit b -> b

def _enumerate_paths(labels, start, fuse_with, N_fun, vacuum, n):
    """All fusion paths e_1..e_n with e_1 = start, e_n = vacuum, where
    e_{j+1} is an allowed fusion outcome of e_j x fuse_with under N_fun.
    Enumerated depth-first in numeric label order => lexicographic order."""
    num = {lab: i for i, lab in enumerate(labels)}
    paths = []

    def extend(prefix):
        if len(prefix) == n:
            if prefix[-1] == vacuum:
                paths.append(tuple(num[x] for x in prefix))
            return
        for nxt in labels:  # numeric order == labels order in gate module
            if N_fun(prefix[-1], fuse_with, nxt):
                extend(prefix + [nxt])

    extend([start])
    return np.array(paths, dtype=np.int8)


def _fibonacci_number(k):
    """F(k) with F(1) = F(2) = 1, computed independently for the dim check."""
    a, b = 1, 1
    for _ in range(k - 2):
        a, b = b, a + b
    return b


def build_arms(n=N_CARRIERS):
    arms = {}

    fib_basis = _enumerate_paths(
        GATE.FIB_LABELS, "t", "t", GATE.fib_N, "1", n)
    arms["fib"] = dict(
        basis=fib_basis, kind="path",
        theory_dim=_fibonacci_number(n - 1),
        theory_note="Fib(%d) = %d (F1=F2=1)" % (n - 1, _fibonacci_number(n - 1)))

    ising_basis = _enumerate_paths(
        GATE.ISING_LABELS, "s", "s", GATE.ising_N, "1", n)
    arms["ising"] = dict(
        basis=ising_basis, kind="path",
        theory_dim=2 ** (n // 2 - 1),
        theory_note="2^%d = %d" % (n // 2 - 1, 2 ** (n // 2 - 1)))

    grid = np.arange(3 ** n, dtype=np.int64)
    digits = np.stack([(grid // 3 ** j) % 3 for j in range(n)], axis=1)
    z3_basis = digits[digits.sum(axis=1) % 3 == 0].astype(np.int8)
    # canonical lexicographic order (leftmost slot most significant)
    z3_basis = z3_basis[np.lexsort(tuple(z3_basis[:, j]
                                         for j in range(n - 1, -1, -1)))]
    arms["z3"] = dict(
        basis=z3_basis, kind="product",
        theory_dim=3 ** (n - 1),
        theory_note="3^%d = %d" % (n - 1, 3 ** (n - 1)))

    grid = np.arange(2 ** n, dtype=np.int64)
    cl_basis = np.stack([(grid >> (n - 1 - j)) & 1 for j in range(n)],
                        axis=1).astype(np.int8)
    arms["classical"] = dict(
        basis=cl_basis, kind="product",
        theory_dim=2 ** n,
        theory_note="2^%d = %d" % (n, 2 ** n))

    return arms


# ------------------------------------------------------- code-space selection
def importance_weights(constant_value, n=N_CARRIERS):
    """w_i proportional to c^(-i/2), positions i = 1..n.  c = 1 => flat."""
    i = np.arange(1, n + 1, dtype=np.float64)
    return constant_value ** (-i / 2.0)


def select_code_space(basis, constant_value):
    """The single deterministic code-space selection rule (all arms).

    1. signature sig(s) = sum_i w_i * label_i(s) over the basis columns,
       with w_i = c^(-i/2)  (only the RANKING of sig matters, so the
       normalisation of w is irrelevant).
    2. Rank all D basis strings by (sig, lexicographic string) ascending.
    3. |0_L> = uniform superposition of the first floor(D/2) strings,
       |1_L> = uniform superposition of the remaining ceil(D/2).

    Returns (a0, a1): real amplitude vectors of length D (disjoint support,
    orthonormal by construction).
    """
    D, n = basis.shape
    w = importance_weights(constant_value, n)
    sig = basis.astype(np.float64) @ w
    # np.lexsort: LAST key is primary => (sig, col_1, col_2, ..., col_n)
    order = np.lexsort(tuple(basis[:, j] for j in range(n - 1, -1, -1))
                       + (sig,))
    half = D // 2
    a0 = np.zeros(D)
    a1 = np.zeros(D)
    a0[order[:half]] = 1.0 / math.sqrt(half)
    a1[order[half:]] = 1.0 / math.sqrt(D - half)
    return a0, a1


# ------------------------------------------------------------------- channel
def erased_set(seed, f_index, mode, n=N_CARRIERS):
    """Erasure draw.  Seeds drive erasure positions ONLY (prereg 1.4) and
    are identical across all arms and constants for a given (f, mode, seed).
    scattered: uniform random subset of size k = round(f*n).
    burst: contiguous block of size k at a uniform random offset
    (non-wraparound, offset in 0..n-k)."""
    k = round(ERASURE_FRACTIONS[f_index] * n)
    rng = np.random.default_rng([seed, f_index, MODES.index(mode)])
    if mode == "scattered":
        return np.sort(rng.choice(n, size=k, replace=False))
    off = int(rng.integers(0, n - k + 1))
    return np.arange(off, off + k)


def dephased_slots(kind, erased, n=N_CARRIERS):
    """Which basis-string slots the channel dephases, per the prereg rule.
    path arms   : the internal edges adjacent to erased carrier c are
                  e_c and e_{c+1} (1-indexed edges; e_0 before carrier 1 is
                  the fixed vacuum and is not a slot) => slots c-1 and c in
                  0-indexed columns, clipped to [0, n-1].  (Slot n-1 = the
                  total charge, constant across the sector; dephasing a
                  constant label is a no-op and is retained for uniformity.)
    product arms: the erased leaves themselves."""
    if kind == "path":
        cols = set()
        for c in erased:            # c is a 0-indexed carrier
            for j in (c - 1, c):    # 0-indexed edge columns e_c, e_{c+1}
                if 0 <= j <= n - 1:
                    cols.add(j)
        return sorted(cols)
    return sorted(int(c) for c in erased)


def pinch_keys(basis, slots):
    """Integer key of the dephased-label assignment kappa for every basis
    string (base-3 encoding; all arms' labels live in {0,1,2})."""
    D = basis.shape[0]
    if not slots:
        return np.zeros(D, dtype=np.int64), 1
    keys = np.zeros(D, dtype=np.int64)
    m = 1
    for j in slots:
        keys += basis[:, j].astype(np.int64) * m
        m *= 3
    return keys, m


# ------------------------------------------------- Petz recovery + scorer
def entanglement_fidelity(basis, a0, a1, slots):
    """Entanglement fidelity of (Petz recovery) o (dephasing pinching) on
    the logical space — exact closed form, identical for every arm.

    N(rho) = sum_kappa P_kappa rho P_kappa ;  sigma = P_code / 2 ;
    R = Petz map of N w.r.t. sigma.  Since N is a pinching, N(sigma) is
    block-diagonal over kappa with blocks B_kappa = (1/2) U_kappa U_kappa^T,
    U_kappa = [P_kappa a0, P_kappa a1], and (manifest, derivation D1):

        F_e = (1/4) sum_kappa ( Tr sqrt(G_kappa) )^2 ,
        G_kappa = U_kappa^T U_kappa   (2x2 Gram matrix).

    Verified against the literal dense Petz construction in --selftest.
    """
    keys, nbins = pinch_keys(basis, slots)
    w00 = np.bincount(keys, weights=a0 * a0, minlength=nbins)
    w11 = np.bincount(keys, weights=a1 * a1, minlength=nbins)
    w01 = np.bincount(keys, weights=a0 * a1, minlength=nbins)
    tr = w00 + w11
    det = np.clip(w00 * w11 - w01 * w01, 0.0, None)
    # (Tr sqrt(G))^2 = Tr(G) + 2 sqrt(det(G)) for a 2x2 PSD matrix
    return 0.25 * float(np.sum(tr + 2.0 * np.sqrt(det)))


def entanglement_fidelity_dense(basis, a0, a1, slots):
    """Independent LITERAL construction (self-test verifier only; feasible
    for the small path arms).  Builds the purified state, applies the
    pinching channel and the Petz map step by step with explicit matrices
    and an eigendecomposition pseudo-inverse-sqrt.  No closed form used."""
    D = basis.shape[0]
    keys, _ = pinch_keys(basis, slots)
    same = (keys[:, None] == keys[None, :]).astype(np.float64)  # pinch mask

    c = np.stack([a0, a1])                       # 2 x D code isometry rows
    sigma = 0.5 * (np.outer(a0, a0) + np.outer(a1, a1))
    sqrt_sigma = sigma * math.sqrt(2.0)          # sigma^{1/2}; code proj /sqrt2

    Nsigma = sigma * same                        # pinched sigma
    evals, evecs = np.linalg.eigh(Nsigma)
    inv_sqrt = np.zeros_like(evals)
    thr = 1e-12 * max(1.0, float(evals.max()))
    nz = evals > thr
    inv_sqrt[nz] = 1.0 / np.sqrt(evals[nz])
    A = (evecs * inv_sqrt) @ evecs.T             # N(sigma)^{-1/2} (pseudo)

    # purification |Omega> = (1/sqrt2)(|0>|0_L> + |1>|1_L>), on C^2 (x) C^D
    omega = (c / math.sqrt(2.0)).reshape(2 * D)
    rho = np.outer(omega, omega)
    big_same = np.kron(np.ones((2, 2)), same)

    rho1 = rho * big_same                        # channel N (pinching)
    assert abs(np.trace(rho1) - 1.0) < 1e-12    # N trace-preserving
    bigA = np.kron(np.eye(2), A)
    rho2 = bigA @ rho1 @ bigA                    # sandwich N(sigma)^{-1/2}
    rho3 = rho2 * big_same                       # N^dag (= N, pinching)
    bigS = np.kron(np.eye(2), sqrt_sigma)
    rho4 = bigS @ rho3 @ bigS                    # sandwich sigma^{1/2}
    assert abs(np.trace(rho4) - 1.0) < 1e-9     # Petz TP on support
    return float(omega @ rho4 @ omega)


# ----------------------------------------------------------------- factorial
def run_cell(arm, a0, a1, f_index, mode, seed):
    E = erased_set(seed, f_index, mode)
    slots = dephased_slots(arm["kind"], E)
    return entanglement_fidelity(arm["basis"], a0, a1, slots)


def full_run(out_path):
    arms = build_arms()
    results = {
        "test_id": "AH4-P1-ANYON-RECOV-v1",
        "n_carriers": N_CARRIERS, "d_logical": D_LOGICAL,
        "fractions": list(ERASURE_FRACTIONS), "modes": list(MODES),
        "seeds": list(SEEDS),
        "constants": {k: repr(v) for k, v in CONSTANTS.items()},
        "dims": {name: int(arm["basis"].shape[0]) for name, arm in arms.items()},
        "cells": {},
    }
    for arm_name, arm in arms.items():
        for const_name, c in CONSTANTS.items():
            a0, a1 = select_code_space(arm["basis"], c)
            for f_index, f in enumerate(ERASURE_FRACTIONS):
                for mode in MODES:
                    key = "%s|%s|f%.2f|%s" % (arm_name, const_name, f, mode)
                    results["cells"][key] = [
                        run_cell(arm, a0, a1, f_index, mode, seed)
                        for seed in SEEDS]
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
    print("wrote %s  (%d cells x %d seeds)" %
          (out_path, len(results["cells"]), len(SEEDS)))
    print("Analysis follows prereg section 2.2 (primary constant `uniform`,"
          " scattered mode; burst is a separately-reported stressor).")


# ---------------------------------------------------------------- self-tests
def selftest():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name,
                               ("  " + detail) if detail else ""))

    print("AH.4-P1 pipeline self-tests")
    print("=" * 60)

    print("\n1. pentagon gate (gate 0 must still pass)")
    for name, labels, F in (("fib", GATE.FIB_LABELS, GATE.fib_F),
                            ("ising", GATE.ISING_LABELS, GATE.ising_F),
                            ("z3", GATE.Z3_LABELS, GATE.z3_F)):
        worst, checked = GATE.pentagon_residuals(labels, F)
        check("pentagon[%s]" % name, worst < GATE.TOL,
              "max residual %.3e over %d assignments" % (worst, checked))

    print("\n2. dimensions vs theory")
    arms = build_arms()
    for name, arm in arms.items():
        D = arm["basis"].shape[0]
        check("dim[%s]" % name, D == arm["theory_dim"],
              "built %d, theory %s" % (D, arm["theory_note"]))
        uniq = len({tuple(r) for r in arm["basis"].tolist()})
        check("basis-strings-distinct[%s]" % name, uniq == D)

    print("\n3. code space: d_L = 2 embeddable, codewords orthonormal")
    for name, arm in arms.items():
        check("embeddable[%s]" % name, arm["basis"].shape[0] >= D_LOGICAL)
        for cname, c in CONSTANTS.items():
            a0, a1 = select_code_space(arm["basis"], c)
            g = np.array([[a0 @ a0, a0 @ a1], [a0 @ a1, a1 @ a1]])
            if not np.allclose(g, np.eye(2), atol=1e-12):
                check("orthonormal[%s,%s]" % (name, cname), False)
                break
        else:
            check("orthonormal[%s, all constants]" % name, True)

    print("\n4. f = 0 gives fidelity 1.0 to machine precision (every arm)")
    for name, arm in arms.items():
        worst = 0.0
        for cname, c in CONSTANTS.items():
            a0, a1 = select_code_space(arm["basis"], c)
            F = entanglement_fidelity(arm["basis"], a0, a1, [])
            worst = max(worst, abs(F - 1.0))
        check("f0[%s]" % name, worst < 1e-12, "max |F-1| = %.3e" % worst)

    print("\n5. fidelities within [0,1] (sweep: all arms/constants/f/modes,"
          " seeds 1000-1004)")
    lo, hi = 1.0, 0.0
    for name, arm in arms.items():
        for cname, c in CONSTANTS.items():
            a0, a1 = select_code_space(arm["basis"], c)
            for f_index in range(len(ERASURE_FRACTIONS)):
                for mode in MODES:
                    for seed in SEEDS[:5]:
                        F = run_cell(arm, a0, a1, f_index, mode, seed)
                        lo, hi = min(lo, F), max(hi, F)
    check("bounds", -1e-12 <= lo and hi <= 1.0 + 1e-12,
          "observed range [%.6f, %.6f] over 480 evaluations" % (lo, hi))

    print("\n6. determinism under fixed seed (recompute from scratch)")
    def batch():
        vals = []
        arms2 = build_arms()
        for name in ("fib", "ising", "z3", "classical"):
            arm = arms2[name]
            a0, a1 = select_code_space(arm["basis"], CONSTANTS["uniform"])
            for f_index in (0, 1, 2):
                for mode in MODES:
                    vals.append(run_cell(arm, a0, a1, f_index, mode, 1000))
        return vals
    v1, v2 = batch(), batch()
    check("deterministic", v1 == v2, "%d values bitwise identical" % len(v1))
    same_draw = all(
        np.array_equal(erased_set(s, fi, m), erased_set(s, fi, m))
        for s in SEEDS for fi in range(3) for m in MODES)
    check("erasure draws reproducible", same_draw)

    print("\n7. closed-form scorer vs literal dense Petz construction")
    worst = 0.0
    ncmp = 0
    for name in ("fib", "ising"):
        arm = arms[name]
        for cname in ("uniform", "golden"):
            a0, a1 = select_code_space(arm["basis"], CONSTANTS[cname])
            for f_index in (0, 1):
                for mode in MODES:
                    E = erased_set(1000, f_index, mode)
                    slots = dephased_slots(arm["kind"], E)
                    Ffast = entanglement_fidelity(arm["basis"], a0, a1, slots)
                    Fdense = entanglement_fidelity_dense(
                        arm["basis"], a0, a1, slots)
                    worst = max(worst, abs(Ffast - Fdense))
                    ncmp += 1
    check("closed-form == dense Petz", worst < 1e-10,
          "max |diff| = %.3e over %d comparisons (fib+ising)" % (worst, ncmp))

    print("\n8. channel is a partition (Kraus projectors sum to identity)")
    for name, arm in arms.items():
        a0, a1 = select_code_space(arm["basis"], CONSTANTS["uniform"])
        E = erased_set(1000, 2, "scattered")
        slots = dephased_slots(arm["kind"], E)
        keys, nbins = pinch_keys(arm["basis"], slots)
        mass = (np.bincount(keys, weights=a0 * a0, minlength=nbins).sum()
                + np.bincount(keys, weights=a1 * a1, minlength=nbins).sum())
        check("partition[%s]" % name, abs(mass - 2.0) < 1e-12,
              "sum Tr G_kappa = %.15f (expect 2)" % mass)

    print("\n" + "=" * 60)
    print("SELF-TESTS %s" % ("ALL PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                    help="run the pre-registered self-tests and exit")
    ap.add_argument("--run", action="store_true",
                    help="run the full 4x4 factorial (all cells, all seeds)")
    ap.add_argument("--out", default=os.path.join(_HERE, "ah4_p1_results.json"))
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.run:
        full_run(args.out)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
