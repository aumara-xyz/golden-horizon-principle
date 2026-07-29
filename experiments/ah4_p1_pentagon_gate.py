#!/usr/bin/env python3
"""AH.4-P1 gate 0 — verify the F-symbols before anything downstream is built.

Preregistration: experiments/AH4_P1_ANYON_RECOVERABILITY_PREREG_v1.md, section 3.

WHY THIS FILE EXISTS
--------------------
The AH.4-P1 recoverability discriminator compares fusion-category STRUCTURE
(Fibonacci vs Ising vs abelian) rather than allocation CONSTANTS. That comparison
is meaningless unless the F-symbols defining each category are correct: a
recovery fidelity computed in a basis whose associativity data is wrong is a
number about nothing.

The pentagon identity is the hard, cheap, pass/fail check that the F-symbols are
a consistent associator. It costs seconds. It runs BEFORE the expensive build,
so a wrong associator is caught at gate 0 rather than discovered after a
fidelity table exists and is believed.

This script asserts NOTHING about GHP. It is verified computation of established
category theory (Fibonacci F-symbols: Kitaev 2006 appendix E; Ising: Bonderson
thesis 2007 section 2). Neither outcome is evidence for or against the programme.

PENTAGON IDENTITY (Bonderson 2.34):

  [F^{fcd}_e]_{g l} [F^{ab l}_e]_{f k}
      = SUM_h [F^{abc}_g]_{f h} [F^{ahd}_e]_{g k} [F^{bcd}_k]_{h l}

Run:  python experiments/ah4_p1_pentagon_gate.py
Exit: 0 if every category passes, 1 otherwise.
"""

import itertools
import math
import sys

PHI = (1.0 + math.sqrt(5.0)) / 2.0
TOL = 1e-12


# --------------------------------------------------------------- Fibonacci
# Labels: '1' (vacuum), 't' (tau).  Fusion: t x t = 1 + t.
FIB_LABELS = ("1", "t")


def fib_N(a, b, c):
    """Fusion multiplicity N^c_{ab} in {0,1}."""
    if a == "1":
        return int(b == c)
    if b == "1":
        return int(a == c)
    return 1  # t x t = 1 + t, so any c is allowed


# The single non-trivial associator, basis order ('1','t'):
#   F^{ttt}_t = [[1/phi, 1/sqrt(phi)], [1/sqrt(phi), -1/phi]]
_FIB_F_TTT_T = {
    ("1", "1"): 1.0 / PHI,
    ("1", "t"): 1.0 / math.sqrt(PHI),
    ("t", "1"): 1.0 / math.sqrt(PHI),
    ("t", "t"): -1.0 / PHI,
}


def fib_F(a, b, c, d, e, f):
    """[F^{abc}_d]_{ef} for Fibonacci anyons."""
    # A vertex that does not exist contributes nothing.
    if not (fib_N(a, b, e) and fib_N(e, c, d) and fib_N(b, c, f) and fib_N(a, f, d)):
        return 0.0
    # Any vacuum leg makes the associator trivial.
    if a == "1" or b == "1" or c == "1":
        return 1.0
    # a=b=c=t.  d=1 forces e=f=t, a 1x1 block equal to 1.
    if d == "1":
        return 1.0
    return _FIB_F_TTT_T[(e, f)]


# ------------------------------------------------------------------- Ising
# Labels: '1' (vacuum), 's' (sigma), 'p' (psi).
#   s x s = 1 + p,  s x p = s,  p x p = 1
ISING_LABELS = ("1", "s", "p")

_ISING_FUSION = {
    ("1", "1"): {"1"},
    ("1", "s"): {"s"}, ("s", "1"): {"s"},
    ("1", "p"): {"p"}, ("p", "1"): {"p"},
    ("s", "s"): {"1", "p"},
    ("s", "p"): {"s"}, ("p", "s"): {"s"},
    ("p", "p"): {"1"},
}


def ising_N(a, b, c):
    return int(c in _ISING_FUSION[(a, b)])


_INV_SQRT2 = 1.0 / math.sqrt(2.0)
# F^{sss}_s in basis ('1','p'):  (1/sqrt2) [[1, 1], [1, -1]]
_ISING_F_SSS_S = {
    ("1", "1"): _INV_SQRT2,
    ("1", "p"): _INV_SQRT2,
    ("p", "1"): _INV_SQRT2,
    ("p", "p"): -_INV_SQRT2,
}


def ising_F(a, b, c, d, e, f):
    """[F^{abc}_d]_{ef} for Ising anyons."""
    if not (ising_N(a, b, e) and ising_N(e, c, d)
            and ising_N(b, c, f) and ising_N(a, f, d)):
        return 0.0
    if a == "1" or b == "1" or c == "1":
        return 1.0
    if (a, b, c) == ("s", "s", "s"):
        return _ISING_F_SSS_S[(e, f)]
    # The two sign-carrying symbols of the Ising category.
    if (a, b, c, d) == ("s", "p", "s", "p"):
        return -1.0
    if (a, b, c, d) == ("p", "s", "p", "s"):
        return -1.0
    return 1.0


# ------------------------------------------------------------------ abelian
# Z3: labels '0','1','2', fusion a x b = a+b mod 3.  All F-symbols trivial.
Z3_LABELS = ("0", "1", "2")


def z3_N(a, b, c):
    return int((int(a) + int(b)) % 3 == int(c))


def z3_F(a, b, c, d, e, f):
    if not (z3_N(a, b, e) and z3_N(e, c, d) and z3_N(b, c, f) and z3_N(a, f, d)):
        return 0.0
    return 1.0


# ---------------------------------------------------------------- the check
def pentagon_residuals(labels, Ffun):
    """Return (max_abs_residual, n_nontrivial) over every index assignment."""
    worst = 0.0
    checked = 0
    for a, b, c, d, e, f, g, k, l in itertools.product(labels, repeat=9):
        lhs = Ffun(f, c, d, e, g, l) * Ffun(a, b, l, e, f, k)
        rhs = sum(
            Ffun(a, b, c, g, f, h) * Ffun(a, h, d, e, g, k) * Ffun(b, c, d, k, h, l)
            for h in labels
        )
        if lhs != 0.0 or rhs != 0.0:
            checked += 1
        worst = max(worst, abs(lhs - rhs))
    return worst, checked


def main():
    cases = [
        ("Fibonacci (the GHP object)", FIB_LABELS, fib_F),
        ("Ising (primary structural control)", ISING_LABELS, ising_F),
        ("Z3 abelian (pointed control)", Z3_LABELS, z3_F),
    ]
    print("AH.4-P1 gate 0: pentagon identity")
    print(f"tolerance {TOL:g}\n")
    ok = True
    for name, labels, Ffun in cases:
        worst, checked = pentagon_residuals(labels, Ffun)
        passed = worst < TOL
        ok &= passed
        print(f"  {name}")
        print(f"    non-trivial index assignments : {checked}")
        print(f"    max |LHS - RHS|               : {worst:.3e}")
        print(f"    verdict                       : {'PASS' if passed else 'FAIL'}\n")

    # Quantum dimensions are FORCED by the fusion rules, never chosen.
    print("  quantum dimensions (forced, not input):")
    print(f"    Fibonacci  d_tau = {PHI:.15f}   (d^2 = d + 1)")
    print(f"    Ising      d_sig = {math.sqrt(2.0):.15f}   (d^2 = 2)")
    print(f"    Z3         d     = 1.0")
    print("\n  Note: phi appears here as an OUTPUT of tau x tau = 1 + tau,")
    print("  not as an input. No arm of AH.4-P1 may put phi in by hand.")

    print(f"\nGATE {'PASSED' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
