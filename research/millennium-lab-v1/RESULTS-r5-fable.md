# RESULTS — round 5 (Fable): Connes–Consani–Moscovici "Zeta Spectral Triples", independent implementation

Predictions: PREDICTIONS-r5-fable.md (commit 213b1f6, before compute). Code: ccm_triples.py (mpmath special functions + python-flint 0.6.0 linear algebra, 220 digits). Outputs: r5-lam9.json, r5-lam13.json, r5-ctrl-*.json. Codex implements the same object independently from the explicit formula; the two are compared only after both are committed.
Source: arXiv:2511.22755 (Connes, Consani, Moscovici, 27 Nov 2025). Implemented from their eqs (4.2), (4.3), (4.4), Lemma 2.3, Prop 5.9, Thm 5.10. No zeta zero enters the construction; zeros used for scoring only, after the pseudo-prime control.

## Primary reproduction — MEASURED, to the published digit
| λ² | N | digits | |E_k−γ_k| k=1 | k=20 | k=30 | k=40 | k=50 | paper (k=1 / 20 / 40 / 50) |
|---|---|---|---|---|---|---|---|---|
| 9 | 120 | 220 | 1.58e-34 | 2.42e-7 | 3.0e-2 | 2.8 | 8.8 (49 roots found) | 1.6e-34 / 2.4e-7 / — / — (Fig. 1 stops at 20) |
| 13 | 120 | 220 | 2.44e-55 | 3.54e-24 | 4.21e-15 | 2.0e-7 | 2.04e-3 | 2.44e-55 / 3.54e-24 / 2.e-7 / 2.04e-3 |
Every comparable entry matches the paper. P1, P2 held. First root at λ²=9: 14.1347251417346937904572519836 (true: ...983562...).

## Even-simple — MEASURED, with one wrong prediction
| λ² | ε₁ | ε₂ | ε₂/ε₁ | evenness |
|---|---|---|---|---|
| 9 | 2.95e-38 | 1.13e-34 | 3.8e3 | 4e-190 |
| 13 | 3.48e-59 | 3.06e-55 | 8.8e3 | 9e-174 |
Simple and even, as the theorem requires. I predicted a gap ratio > 1e10; it is ~4–9×10³. Wrong, kept. log ε₁ vs μ=λ²: slope −12.05 per unit μ from two points; predicted [−12, −8]; marginally outside. Kept.

## Hostile controls (λ²=9, N=120, 220 digits; all preregistered thresholds on |E₁−γ₁|)
| control | ε₁ | min error over first 20 zeros | threshold | verdict |
|---|---|---|---|---|
| delete prime 2 and powers | 0.088 | 1.47 | > 1e-5 | held |
| archimedean only (no primes) | −0.017 | 10.9 | > 1e-2 | held |
| pseudo-primes, seed 0..4 (random points in [0,L], same count and weights) | 0.12, 0.048, 0.038, −0.035, −0.069 | 12.8, 4.8, 12.3, 12.7, 9.3 | > 1e-3 each | held, all five |
| weight permutation, seeds 0,1 | −0.029, 0.066 | 12.7, 0.31 | > 1e-6 | held |
| delete prime 7 (not preregistered) | −1.42 | 4.4e-17 at k=1, 1.7e-3 at k=10 | — | MEASURED: primes 2,3,5 alone still give 17 digits of the first zero; accuracy grows with each prime, as the paper's λ=√12/√13/√14 columns show |
No oracle leak: every control that breaks the true prime positions destroys the match entirely, and the near-singular ground eigenvalue (1e-38) becomes an ordinary number (|ε₁| ~ 0.02–1.4). The tiny eigenvalue IS the arithmetic.

## What this establishes and what it does not
MEASURED: the CCM operator is a real, finite, self-adjoint construction from the Euler product over p ≤ λ² whose spectrum matches the first 50 zeros to the printed accuracy, and the match is entirely carried by the true primes. It is the first row of the three-yeses table with prime input and a genuine "yes" in the self-adjoint column, at finite (λ, N).
UNVERIFIED (their §8, untouched here): (1) simple-even for the infinite-dimensional QW_λ; (2) the prolate trial state k_λ approximating ξ_λ strongly enough for det_reg → Ξ. Nothing I computed bears on either. Convergence in (N, λ) → ∞ is the whole open problem; the 220-digit match at finite parameters does not prove it, and the authors say so.
Three-yeses columns for this row: self-adjoint discrete spectrum — yes at finite (λ,N); chaotic without arithmetic degeneracy — not a dynamical system, column does not apply as posed; orbits of length ln p — the prime powers enter as explicit-formula support, not orbits (Codex's convention). The row is not three yeses. It is the most alive row on the table.

## Disagreement to resolve with Codex
Gemini deep-research report (received from Peter, unaudited) states Weil positivity localized at height γ needs primes up to exp(cγ); Codex's round-3 targeted witness needed x≈10 at γ=14. UNVERIFIED which is right as stated; likely blind vs oracle-targeted.
