#!/usr/bin/env python3
"""Numerology tripwire, made mechanical: can a given constant even BE a quantum
dimension of the discrete series?

Not AH.4-P1 specific. This is a general guard for the programme, written because
the same question keeps arriving in a different costume: "gold and silver both
showed up, so what about bronze?" It has a hard answer, and the answer is cheap
to check, so it should be checkable rather than argued.

THE TWO FAMILIES
----------------
Two different sequences get conflated because they share exactly one member.

  METALLIC MEANS      x^2 - n*x - 1 = 0,  i.e. x = n + 1/x
                      gold 1.618, silver 2.414, bronze 3.303, copper 4.236, ...
                      unbounded above.

  QUANTUM DIMENSIONS  d = 2*cos(pi/(k+2)) for the fundamental object of SU(2)_k
  OF THE DISCRETE     1, sqrt2, phi, sqrt3, 1.802, ... increasing, bounded by 2.
  SERIES

THE BOUND
---------
Jones (1983): the index of a subfactor takes values in
{4cos^2(pi/n) : n >= 3} union [4, infinity). Below 4 the spectrum is DISCRETE.
Since index = d^2, any object with d < 2 has d = 2cos(pi/n) for some n, and
2cos(pi/n) < 2 always. So:

  **A constant >= 2 cannot be the quantum dimension of an object in the
    discrete series.** Above index 4 there is a continuum and no rigid
    classification, so there is no canonical category attached to such a value.

CONSEQUENCE, which is the useful part: of the metallic means, ONLY gold is below
2, and it is the unique member of both families. There is no silver category and
no bronze category to look for. Asking for one is asking which substance is
noblest, and this programme's repeated answer is that the substance is not what
carries the result.

Run:  python experiments/quantum_dimension_admissibility.py
Exit: 0 always. This reports; it does not gate.
"""

import math

TOL = 1e-9
METALS = [(1, "gold"), (2, "silver"), (3, "bronze"), (4, "copper"), (5, "n=5")]
KNOWN = {
    1: "abelian (Z_N)",
    2: "Ising",
    3: "Fibonacci",
    4: "SU(2)_4",
    5: "SU(2)_5",
}


def metallic(n):
    """Positive root of x^2 - n x - 1 = 0."""
    return (n + math.sqrt(n * n + 4)) / 2.0


def quantum_dim(k):
    """Fundamental-object dimension of SU(2)_k."""
    return 2.0 * math.cos(math.pi / (k + 2))


def main():
    print("Quantum-dimension admissibility (Jones 1983 index bound)\n")

    print("FAMILY A: metallic means, x = n + 1/x")
    metals = {}
    for n, name in METALS:
        x = metallic(n)
        metals[name] = x
        print(f"  {name:7s} n={n}:  d = {x:.9f}   index d^2 = {x * x:.6f}")

    print("\nFAMILY B: discrete series, d = 2*cos(pi/(k+2))")
    dims = {}
    for k in range(1, 10):
        d = quantum_dim(k)
        dims[k] = d
        print(f"  SU(2)_{k}:      d = {d:.9f}   index d^2 = {d * d:.6f}"
              f"   {KNOWN.get(k, '')}")
    print(f"  limit k->inf: d -> 2.000000000  (supremum, never attained)")

    print("\nADMISSIBILITY: which metallic means can be discrete-series dimensions?")
    overlap = []
    for name, x in metals.items():
        if x >= 2.0:
            print(f"  {name:7s} {x:.6f}  >= 2  ->  EXCLUDED. No canonical category.")
        else:
            hit = [k for k, d in dims.items() if abs(d - x) < TOL]
            if hit:
                overlap.append(name)
                print(f"  {name:7s} {x:.6f}  <  2  ->  ADMISSIBLE, at SU(2)_{hit[0]}"
                      f" ({KNOWN[hit[0]]})")
            else:
                print(f"  {name:7s} {x:.6f}  <  2  ->  below the bound but not in the series")

    print(f"\nINTERSECTION OF THE TWO FAMILIES: {overlap}")
    phi = metallic(1)
    print(f"  phi is the unique overlap, satisfying both defining equations:")
    print(f"    metallic   phi^2 - phi - 1      = {phi * phi - phi - 1.0:.3e}")
    print(f"    Chebyshev  phi - 2*cos(pi/5)    = {phi - 2 * math.cos(math.pi / 5):.3e}")

    print(f"\nA CORRECTION THIS MAKES MECHANICAL:")
    print(f"  Ising's dimension  sqrt2  = {math.sqrt(2.0):.9f}")
    print(f"  The silver mean    1+sqrt2 = {metallic(2):.9f}")
    print(f"  These are DIFFERENT NUMBERS. They share a continued-fraction tail,")
    print(f"  which matters for approximability, and nothing else. Ising's")
    print(f"  dimension is not a metallic mean at all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
