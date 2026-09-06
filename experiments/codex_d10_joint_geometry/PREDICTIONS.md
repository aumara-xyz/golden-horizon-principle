# Codex D10 — joint geometry, before computation

2026-09-06. User requested a hard mathematical follow-through on the Viviani invariant analogy. The reported family connection is personal context, not mathematical evidence. No golden ratio, zero ordinate, physical observer, or fitted geometry enters a construction. Do not edit Fable or Opus files. Work stays at L=7/10. Compute budget: 25 minutes, excluding documentation and review. Commit this file before numerical tests.

## Analytic deductions made before the numerical experiment

These are not blind predictions: they were derived during design and are to be audited explicitly.

1. The Weil form has an exact jump-square rewrite, with a negative constant and the signed pole term left over. Its continuous off-diagonal kernel is K(r)=2 cosh(r/2)-exp(r/2)/(2 sinh r), plus negative prime-shift atoms. It changes sign when exp(r)^3-exp(r)-1=0. At a=log(5/4), K(a)=-19/(18 sqrt(5)) and K(2a)=5129/7380. The (-,-,+) triangle obstructs a local diagonal-gauge positive-conductance representation, not an arbitrary sum of squares or positivity.
2. A=(1/2)I+vv^T, v=(1,-1,1), is a positive three-variable control with that same sign pattern. Replacing its off-diagonals by -|A_ij| makes it indefinite. This tests the scope of the obstruction.
3. Isolating the analytically specified cosh/sinh pole vector gives an exact Schur completion of squares, conditional on positivity of the pole-orthogonal block. This is standard linear algebra, not a new theorem.

## Frozen tests and predictions

P1 — MEASURED only after checks: Arb enclosures of the exact kernel values at a and 2a will agree with the algebraic values; the signs persist on disjoint neighborhoods of radius 1/100 about -a,0,a. All eight real sign gauges fail to make every triangle edge nonpositive. Controls: pole-free kernel has nonpositive continuous edges; the positive frustrated 3x3 matrix remains positive; its independent-edge replacement is negative. Mutation: reverse the long edge, which removes this triangle obstruction.

P2 — PREDICTED: replay the unchanged Opus D7 R_120 builder in this directory solely as input data, then independently analyze its principal blocks of 20,40,80 Legendre modes PER PARITY. With p fixed by cosh/sinh, both authentic pole-orthogonal complements C and Schur scalars sigma will be positive. Verify by ball arithmetic; midpoint eigenvalues alone are not certification. Report the full gap, complement gap, first four complement eigenvalues, number below 1e-3 (midpoint diagnostic), Schur scalar, response norm, cancellation factor, and critical pole coefficient kappa_crit=(b^T C^-1 b-a)/||p||². Authentic kappa is +2 even and -2 odd. A positive finite R_120 block is not a new all-function or all-window result.

P3 — PREDICTED discriminator: at 80 modes, removing the fixed pole direction increases the minimum by at least 1000x in BOTH parities, but the complement still has an eigenvalue below 1e-3. The 1000x prediction may fail and must remain in the ledger. D7's already observed second eigenvalues (~1.9e-8 even,~4.7e-6 odd) and compression interlacing already exclude an order-one complement; that part is NOT an independent discovery.

P4 — PREDICTED controls: at 80 modes at least one archimedean-only or reversed-prime-weight control fails C>0 or sigma>0. Controls keep the SAME support, basis, pole vector, beta from authentic R_120, and frequency cutoff. For deleted/permuted primes, the fixed beta remains a valid envelope since the absolute-weight sum does not increase. Run controls before accepting authentic result tables. Pole mutation kappa=-2 in the even sector and +2 in the odd sector will be reported regardless of sign; positivity alone cannot validate the model. A negative reduced-form control is NOT a negative full-W witness.

P5 — PREDICTED full-form cross-check: use the already frozen D9 candidates and certified full W/pole intervals WITHOUT reselection. Lowering kappa by 1e-4 and 1e-2 from its authentic value makes both exact fixed-vector scores negative; raising kappa by these amounts preserves their positivity. This uses W_kappa=W+(kappa-kappa_auth)|<p,f>|² including D9's entire tail. No claim about all vectors follows from a positive candidate score.

## Verification and stop rules

- Known positive, indefinite, singular and interval-ambiguous controls before accepting a certified sign.
- Schur identity on exact-decimal test vectors, plus direct inertia / independently evaluated quadratic scores for any reported finite negative witness.
- Verify the pole-axis transformation is invertible; distinguish congruence from similarity and norm factors in every gap bound.
- Keep construction hashes and exact saved enclosures. Compact Arb strings can lose sign; export lower/upper endpoint enclosures separately and reparse them.
- Two independent analytical readers review kernel and Schur claims. Shared library and machine are disclosed.
- If interval elimination cannot resolve a sign, report UNVERIFIED or use a disclosed residual/preconditioner enclosure, not an unjustified decimal eigenvalue.
- No increase in L, no candidate optimization against zeros, no push. Update the research hub and commit results locally.

## Deliverable and honest target

RESULTS.md, PROOF.md, code and raw endpoints, controls, prediction ledger. The target is to see whether an exact joint identity removes the hard inequality or merely relocates it. Expected outcome: a sharply scoped obstruction to local pairwise squares and a finite cancellation-preserving decomposition whose remaining complement is still delicate. No expected RH breakthrough, new positivity theorem, or mathematical proof of a physical interpretation.
