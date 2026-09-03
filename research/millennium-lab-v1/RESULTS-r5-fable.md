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

## Reconciliation after Codex round 5 (added later)
- Implementation agreement MEASURED: all 29,161 upper-triangle entries of my matrix agree with Codex's independent builder to ≤ 2.3e-100 at 100 digits for x = 9, 12, 13, 14; first roots agree to 3.8e-29 (my serialization precision).
- Protocol lapse, conceded and STRUCK: my accuracy commit (bc6f3bd) preceded my control commit (3a9452f). Under the round's own rule (pseudo-prime control before any accuracy number) my primary accuracy table above is VOID as a protocol result; the numbers themselves were reproduced by Codex after a proper gate. The drop-7 control was not preregistered; labelled so above.
- Indexing error, conceded: at x=9 my scan found 49 roots, so the last error I displayed as k=50 was k=49. Codex's k=50 error there is 8.93.
- The substantive finding is Codex's, not mine: a prime-free candidate (the prolate "educated guess" k_λ = E(h_λ), pushed through the same basis and root finder) ALSO lands on zeros 20–50 with RMSE 3.6e-4, versus 7.5e-4 for the true Weil ground state at x=13. Reason (identity, not leak): the integer-dilation map E has ζ(1/2 − iz) as a factor of its Mellin transform (Riemann 1859; CCM Lemma 7.1). So under the frozen RMSE-on-20–50 rule the accuracy does not discriminate "the finite Weil matrix computed the zeros" from "the ground state is close to a function whose transform already contains ζ". My scoring rule was too coarse: it is dominated by the worst zeros where both candidates sit at ~1e-3, and hides the low zeros where the Weil ground state has 55 digits. UNVERIFIED and decisive for the next step: the per-zero error of the prime-free candidate at k = 1…20. If it is far from 1e-55, the Weil matrix carries arithmetic beyond the identity; if it also reaches ~1e-55, the finite Euler product is doing nothing the identity does not.
- The bridge, MEASURED by Codex: the prolate candidate gets closer to the true ground state in angle (sin θ from 4e-4 at x=5 to 2e-5 at x=20) while the spectral gap collapses far faster (Δ from 1e-14 to 5e-92), so r/Δ grows like exp(5.8 x) and every standard perturbation bound is trivial. Their preregistered decay law was VOID. This is the sharpest statement in the lab of why the CCM missing step is hard: the closeness improves polynomially, the gap dies exponentially.
- Finite simple-even ordering certified at six cutoffs with Arb; three sign-structure proof routes obstructed by explicit certified counter-triangles. Jensen low-degree horizon not found. Butterfly-graph coupling destroys the prime trace. Chuk 2026 certificate not replayable from its archive.
