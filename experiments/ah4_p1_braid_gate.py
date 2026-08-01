#!/usr/bin/env python3
"""AH.4-P1 gate 1: braid-group image, and the confound it exposes.

Preregistration: experiments/AH4_P1_ANYON_RECOVERABILITY_PREREG_v1.md, section 2.4.
Runs after gate 0 (pentagon). Both gates are standalone checks of published
mathematics and are exempt from the pre-signing prohibition, per prereg section 0.1:
their failure would invalidate the design, so they must run first.

WHY THIS FILE EXISTS
--------------------
The AH.4-P1 handoff asserted, from the literature and without checking, that
Fibonacci anyons are universal for quantum computation by braiding alone while
Ising anyons are not. That assertion is load-bearing: it is the sharpest
structural asymmetry between the two arms of the experiment. An assertion in a
preregistration that nobody has run is exactly the kind of claim this programme
does not permit, so this checks it.

THE TEST
--------
Braiding three anyons of the same type gives a 2-dimensional representation of
the 3-strand braid group B_3. Take the two generators, close the group under
multiplication, and count DISTINCT matrices up to global phase (two operations
differing by a global phase are physically the same operation).

  - FINITE image  => braiding reaches finitely many operations. Not universal.
  - UNBOUNDED     => dense in SU(2). Braiding alone is universal
                     (Freedman, Larsen and Wang 2002).

Prediction, recorded before the first run: Ising saturates at a small finite
count, Fibonacci grows without bound.

WHAT THIS IS NOT
----------------
Not evidence for GHP under either outcome. It is verified computation of
established representation theory, and both outcomes were known in advance from
the literature. Its purpose is to check that OUR data are right before an
expensive build rests on them, and to size a confound in the experiment design.

THE CONFOUND IT SIZES (prereg section 2.4)
------------------------------------------
If the Fibonacci arm recovers better, two explanations are live: the fusion
structure itself (capacity phi against sqrt2), or simply that its recovery
routine has a richer set of operations available. Those are different claims and
the second is much weaker. The gap measured here is what the matched
operation-budget control in section 2.4 exists to close.

Data, both standard:
  Fibonacci  R = diag(e^{-4i.pi/5}, e^{3i.pi/5})
             F = [[1/phi, phi^-1/2], [phi^-1/2, -1/phi]]
  Ising      R = e^{-i.pi/8} diag(1, i)
             F = (1/sqrt2) [[1, 1], [1, -1]]
In both cases sigma_1 = R and sigma_2 = F R F, and F is an involution (asserted).

Run:  python experiments/ah4_p1_braid_gate.py
Exit: 0 if the literature claim is reproduced, 1 otherwise.
"""

import cmath
import math
import sys

PHI = (1.0 + math.sqrt(5.0)) / 2.0
ROUND = 6              # dedup precision on matrix entries
MAX_ELEMENTS = 60000   # growth past this is read as unbounded
CLIFFORD_ORDER = 24    # |single-qubit Clifford group| modulo global phase


def mat_mul(A, B):
    return (
        A[0] * B[0] + A[1] * B[2], A[0] * B[1] + A[1] * B[3],
        A[2] * B[0] + A[3] * B[2], A[2] * B[1] + A[3] * B[3],
    )


def canonical(M):
    """Hashable key for a matrix up to GLOBAL PHASE."""
    for z in M:
        if abs(z) > 1e-9:
            M = tuple(w * cmath.exp(-1j * cmath.phase(z)) for w in M)
            break
    return tuple((round(z.real, ROUND), round(z.imag, ROUND)) for z in M)


def close_group(gens):
    """Breadth-first closure. Returns (elements, growth by word length)."""
    ident = (1 + 0j, 0j, 0j, 1 + 0j)
    seen = {canonical(ident)}
    frontier = [ident]
    growth = []
    depth = 0
    while frontier and len(seen) < MAX_ELEMENTS:
        depth += 1
        new = []
        for M in frontier:
            for g in gens:
                P = mat_mul(g, M)
                k = canonical(P)
                if k not in seen:
                    seen.add(k)
                    new.append(P)
        frontier = new
        growth.append((depth, len(seen), len(new)))
        if not new:
            break
    return seen, growth


def generators(kind):
    if kind == "fibonacci":
        R = (cmath.exp(-4j * math.pi / 5), 0j, 0j, cmath.exp(3j * math.pi / 5))
        s = 1.0 / math.sqrt(PHI)
        F = (1.0 / PHI + 0j, s + 0j, s + 0j, -1.0 / PHI + 0j)
    elif kind == "ising":
        ph = cmath.exp(-1j * math.pi / 8)
        R = (ph, 0j, 0j, ph * 1j)
        r = 1.0 / math.sqrt(2.0)
        F = (r + 0j, r + 0j, r + 0j, -r + 0j)
    else:
        raise ValueError(kind)
    assert all(abs(a - b) < 1e-9 for a, b in zip(mat_mul(F, F), (1, 0, 0, 1))), \
        f"{kind}: F is not an involution; the data are wrong"
    return [R, mat_mul(F, mat_mul(R, F))]


def main():
    print("AH.4-P1 gate 1: braid-group image on 3 strands")
    print(f"counted up to global phase, cap {MAX_ELEMENTS}\n")

    results = {}
    for kind, label, dim in [
        ("fibonacci", "Fibonacci (d = phi)  ", PHI),
        ("ising", "Ising     (d = sqrt2)", math.sqrt(2.0)),
    ]:
        elements, growth = close_group(generators(kind))
        finite = len(elements) < MAX_ELEMENTS
        results[kind] = (len(elements), finite)
        print(f"  {label}  quantum dimension {dim:.9f}")
        for d, total, new in growth[:6]:
            print(f"      words <= {d:2d} : {total:6d} distinct  (+{new})")
        if len(growth) > 6:
            d, total, new = growth[-1]
            print(f"      ...")
            print(f"      words <= {d:2d} : {total:6d} distinct  (+{new})")
        if finite:
            print(f"      CLOSED at {len(elements)}: FINITE image, not universal\n")
        else:
            print(f"      still growing at cap: UNBOUNDED image, dense in SU(2)\n")

    fib_n, fib_finite = results["fibonacci"]
    isg_n, isg_finite = results["ising"]

    # The Ising count is not an arbitrary number. Braiding Ising anyons is known
    # to generate exactly the single-qubit Clifford group, which has order 24
    # modulo global phase, and is classically simulable (Gottesman-Knill).
    clifford_match = (isg_n == CLIFFORD_ORDER)
    print(f"  Ising image order {isg_n} vs |Clifford / phase| = {CLIFFORD_ORDER}: "
          f"{'MATCH' if clifford_match else 'MISMATCH'}")
    if clifford_match:
        print("    Consistent with the textbook result that Ising braiding yields")
        print("    Clifford operations only, hence Gottesman-Knill simulable.")

    reproduced = (not fib_finite) and isg_finite and clifford_match
    print(f"\n  CLAIM UNDER TEST: Fibonacci universal by braiding, Ising not.")
    print(f"  RESULT: {'REPRODUCED' if reproduced else 'NOT REPRODUCED'}")
    if reproduced:
        print(f"\n  CONFOUND SIZE for prereg section 2.4: the sqrt2-arm is exhausted")
        print(f"  by {isg_n} operations; the phi-arm is not exhausted at all. A")
        print(f"  Fibonacci win under an UNBOUNDED operation budget is therefore")
        print(f"  ambiguous between structure and operational richness. The matched")
        print(f"  operation-budget control exists to separate them.")

    print(f"\nGATE {'PASSED' if reproduced else 'FAILED'}")
    return 0 if reproduced else 1


if __name__ == "__main__":
    sys.exit(main())
