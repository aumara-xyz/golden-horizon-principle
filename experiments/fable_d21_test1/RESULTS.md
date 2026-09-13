# D21 — Astra's Test 1 executed: the deletion failures are in the lower approximation, not (yet) in W (Fable, 2026-09-13)
Predictions: PREDICTIONS.md (trial 1 and trial 2 sections, each committed before its run). Scorer: provenance-recorded copy of D9's score.py (PROVENANCE.txt has both hashes), functions only, with `compact2` extended to accumulate the compact prime integral so the fixed-ruler reduced score R_T can be evaluated on the same frozen wave. Interpreter: fresh venv, python-flint 0.6.0, numpy 2.0.2 (the old /private/tmp venv was wiped; recorded). Controls: D9's 11 scorer controls PASS; D9 frozen even wave rescored → overlaps D9's saved W interval (PASS). Trial 1 kept (d21_results_trial1.*): 160-mode double-precision waves carry ~1e-17 noise in degrees to 319 that the 12th-derivative tail bounds amplify to useless W enclosures (radii 1e10–1e20); trial 2 freezes the same eigenvectors with |c| < 1e-13 zeroed (74–134 modes) and adds the operator route for delete-4. All scores normalized by the enclosed norm; W − R_T ≥ 0 certain on every wave (identity check PASS, 24/24).

## Results (ζ, L = 0.7, frozen waves from the fixed-ruler reduced form at T = 160 and 240; exact scores at compact cutoff 128 with complete tail)
| case | parity, wave | fixed-ruler reduced score R | exact W_mut on the same wave | class |
|---|---|---|---|---|
| delete n = 4 | even, T160 | +1.73e-13 (POSITIVE) | UNVERIFIED (134 modes, noise) | (b*) R positive |
| delete n = 4 | even, T240 | +4.45e-13 (POSITIVE) | POSITIVE, W ∈ (0, 3e-8]; operator route: 1.031e-13 + w₄I₄ = +6.8e-14 > 0 (I₄ = −5.0e-14) | (b*) R positive, W positive |
| delete n = 4 | odd, T160 | −3.13e-5 (NEGATIVE) | **POSITIVE**, W ∈ (0, 3.1e-3] | (b) R-negative, W positive |
| delete n = 4 | odd, T240 | −7.07e-6 (NEGATIVE) | **POSITIVE**, W ∈ (0, 7.9e-4] | (b) R-negative, W positive |
| delete n = 2 | even, T160 / T240 | −0.460 / −0.458 | NEGATIVE / NEGATIVE ([−0.4 ± 0.06] at T240) | (a) certified W-negative |
| delete n = 2 | odd, T160 / T240 | −0.489 / −0.489 | NEGATIVE, −0.489 ± 6e-4 | (a) certified W-negative |
| prime-free | even, T160 / T240 | −0.255 / −0.253 | NEGATIVE ([−0.2 ± 0.056] at T240) | (a) certified W-negative |
| prime-free | odd, T160 / T240 | −0.742 / −0.740 | NEGATIVE, −0.7 ± 0.05 | (a) certified W-negative |
Survivor mutation (K = 80 nodes, 400 bits, same vectors): all eight class-(a) signs unchanged.

## What this changes
1. The old D16/D17 "−8.4e-13 after deleting 4 (even)" was a moving-ruler artifact: with β, T fixed the reduced score is +1.7e-13 / +4.5e-13, and the exact W on the T240 wave is certified positive by two routes. Astra's prediction HELD. D13's +3.1e-13 (fixed β) was the right protocol.
2. **Deleting n = 4 in the odd sector does not produce a negative W on the waves that make the reduced form negative.** R is −3e-5 and −7e-6 on those waves; their exact W is positive, because the discarded tail ∫_{|t|>T}(Ψ − β)|F|² is 1e-3 to 3e-3 on them: the mutated minimizers are high-frequency waves that the envelope undervalues. My prediction (2) FAILED. Consequence: D13's "odd needs {2,3,4} at L = 0.7", D16's "every visible place is load-bearing within ΔL ≈ 0.03 (32/32)" and D17's "prime powers alone are load-bearing (4/4)" are statements about the reduced form R_{L,T}; for the full W they are established only where the deleted term is large (delete 2, prime-free: class a here), and for the marginal newly-entered places they are UNVERIFIED — with the ζ/odd/n = 4 case now known to be POSITIVE on the two tested waves. Class (b) never proves positivity of the mutated W on all waves; it removes the evidence for negativity.
3. What survives as full-W fact at L = 0.7: prime 2 is load-bearing in both parities (class a, four waves, survivor-checked); the prime-free form is negative in both parities (class a, agreeing with D9's frozen witness). Everything about places that have just entered the room is downgraded to reduced-form-only.

## Prediction ledger
| prediction | outcome |
|---|---|
| Astra: even delete-4 gives no certified negative W witness | HELD |
| Astra: prime-free odd witness survives | HELD (both parities) |
| Fable (1): delete-4 even reduced score positive with fixed ruler; W positive | HELD (W certified on the T240 wave; T160 wave UNVERIFIED from noise) |
| Fable (2): delete-4 odd W certified NEGATIVE | **FAILED** — W positive on both waves |
| Fable (3): delete-2 and prime-free class (a) both parities | HELD |
| Fable (4): W − R_T ≥ 0 on every wave; tail < 1e-6 relative | first part HELD (24/24); second part FAILED — tails are 1e-3–0.18 on the mutated minimizers (that is exactly why R misleads) |
| Fable (5): D9 replay overlaps | HELD |
| trial-1 expectation that 160-mode waves score cleanly | FAILED (noise amplification); repaired in trial 2, kept |

## Corrections propagated
Dated correction notes appended (not edited in place) to D13, D16 and D17 RESULTS.md: their deletion results are reduced-form statements; full-W status per this round.

## D21.1 — repairs requested by the Codex/Astra review (appended 2026-09-13; frozen trial-2 vectors reused, no reselection; d21_1.py, d21_1_results.json/.log)
Repairs: (1) crossing-zero rejection — "certainly ≥ 0" now requires the lower endpoint ≥ 0, with planted controls ([−1,1] → not certain; [1,2] → certain; [−2,−1] → NEGATIVE; [±1e-40] → UNRESOLVED) that must pass before scoring; (2) cutoffs separated — every table score is R₁₂₈ / W on a wave SELECTED at T = 160 or 240; the selector minimum is reported as "not a score"; (3) ledger — trial 2 predicted I₄ > 0 for the even delete-4 wave; measured I₄ = −5.0e-14 (NEGATIVE) on the T240 wave: FAILED, kept; the W sign stays positive because w₄|I₄| = 3.5e-14 < 1.031e-13; (4) quadrature bound — the compact prime integral's error now carries the complex-cosine growth allowance Σ|w_n| cosh(u_n b) on the Bernstein ellipse (Mp ≈ 1.2–3.4; resulting error 3.9e-33, immaterial here; the point is that it is now justified rather than covered by unused weight); rigorous lower/upper endpoints exported for W, R₁₂₈, the excess W − R₁₂₈ and I₄, and each accepted sign re-derived by reparsing the exported endpoint strings; survivor rechecks (K = 80, 400 bits, same vectors) run for positive AND negative signs.
| case, wave | R₁₂₈ | W (route) | excess ≥ 0 certain | survivor K80/400 | endpoint reparse |
|---|---|---|---|---|---|
| delete-4 even, T160 wave | POSITIVE | POSITIVE via monotonicity W ≥ R₁₂₈ (direct enclosure useless, noise) | not certain (UNRESOLVED, correctly) | POSITIVE | UNRESOLVED (direct), sign from route |
| delete-4 even, T240 | POSITIVE | POSITIVE (direct) | yes | POSITIVE | POSITIVE |
| delete-4 odd, T160 / T240 | NEGATIVE / NEGATIVE | POSITIVE / POSITIVE (direct) | yes / yes | POSITIVE / POSITIVE | POSITIVE / POSITIVE |
| delete-2 even, T160 / T240 | NEGATIVE | NEGATIVE / NEGATIVE | yes | NEGATIVE | NEGATIVE |
| delete-2 odd, T160 / T240 | NEGATIVE | NEGATIVE / NEGATIVE | yes | NEGATIVE | NEGATIVE |
| prime-free even / odd, both waves | NEGATIVE | NEGATIVE (4/4) | yes | NEGATIVE | NEGATIVE |
Every D21 classification survives the stricter checker. Fixed-wave versus all-wave: every W sign above is a statement about ONE frozen wave. Class (a) signs are genuine negative witnesses for the mutated full form (a single negative wave suffices). Class (b) positive signs say nothing about other waves; the mutated "delete-4" forms may or may not be positive definite — UNVERIFIED.
