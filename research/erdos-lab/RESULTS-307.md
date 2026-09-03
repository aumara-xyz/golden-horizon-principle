# Erdős #307 — results (Fable, 2026-09-03). Predictions: PREDICTIONS-307.md (commit 3334119, before compute). Code: search_307.py.

Structure used (derived by hand, then confirmed by the positive control): a solution (P,Q) of (Σ_P 1/p)(Σ_Q 1/q)=1 with distinct primes forces numerator(Σ_Q 1/q) = ΠP and numerator(Σ_P 1/p) = ΠQ. Given Q, P is the set of prime factors of that numerator, which must be squarefree; then one exact rational check decides.

| test | outcome | status |
|---|---|---|
| P2 positive control (1 allowed, 15 primes, |Q|≤4) | recovers (1,5)×(2,3) and (1,41)×(2,3,7), the two examples on the problem page, in < 1 s | MEASURED, held |
| P1 main: Q ⊆ first 30 primes, |Q| ≤ 7, no 1 | 2,804,011 sets, 0 solutions, 543 s | MEASURED, held (bounded negative) |
| P3 filter rate < 5 % | 2,179,959 / 2,804,011 = 78 % pass the squarefree-and-disjoint filter | VOID; disjointness is automatic from the coprimality lemma, so the filter is only squarefreeness (~6/π²). Wrong prediction kept. |

What this is: a bounded negative and a structural lemma (A=ΠQ, B=ΠP). Whether the lemma is already in the literature: UNVERIFIED. The known bound |P∪Q| ≥ 60 means any solution has a large union; the smaller set can still be small, which is what this search covers. Not a resolution of #307.
Extension E1 (run after this file, not preregistered in the original file): |Q| = 8 over the first 30 primes (5.85M sets). PREDICTED: none.
