# D22 — Astra's Test 2 executed: a certified lower profile, and brackets that do not close (Fable, 2026-09-13)
Predictions: PREDICTIONS.md (main section plus scoring trials 2–4, each appended before its run). Certificates: d22_certify.py (my D5 machinery parameterized in L, T, NE; 192-bit balls; finite block + discarded-space Schur; reproduces the L = 0.7/T = 120/N = 80 certificate to all printed digits). Candidate scoring: d22_score.py (D9 scorer copy; `compact2` extension with the cosh growth allowance). Interpreter: rebuilt venv (python-flint 0.6.0, numpy 2.0.2). Compute: ≈ 120 single-core CPU-minutes, at the cap; stopped there.

## 1. Certified all-function lower bounds on R_{L,T} (hence on W, given W ≥ R_T), ζ, 160 modes per parity, T = 160 — NEW rigorous results
| L | even lower bound | odd lower bound | checker |
|---|---|---|---|
| 0.40 | 1.44919164005e-4 | 1.24019265771e-2 | ACCEPT / ACCEPT |
| 0.50 | 7.14785349231e-7 | 1.42134532495e-4 | ACCEPT / ACCEPT |
| 0.60 | 1.10135673044e-9 | 4.12866743816e-7 | ACCEPT / ACCEPT |
| 0.70 | 2.67167228677e-13 | 1.58596369131e-10 | ACCEPT / ACCEPT |
| 0.70, T = 240, 192 modes | 3.37581912571e-13 | 2.03304233017e-10 | ACCEPT / ACCEPT |
All entry radii ≤ 4.5e-22, all tail bounds inside the checker's inequality. These are the first certified bounds at L = 0.4, 0.5, 0.6, and the first at L = 0.7 with T > 120. Successive log-slopes of the certified lower envelope (per unit L): even 53.1, 64.8, 83.2; odd 44.7, 58.4, 78.6. They are not compatible with a single slope; the old "64" was a local fit (Astra's prediction HELD, now on certified numbers). The T-dependence at fixed L is itself large: at L = 0.7 the certified bound rises 26 % from T = 160 to T = 240 (28 % odd), so R_T's lower envelope is not a cutoff-independent profile at the 10 % level.

## 2. Full-W upper bounds on frozen candidates — every bracket OPEN (four scoring trials, all kept)
| trial | candidate | why the bracket did not close |
|---|---|---|
| 1 (scores_trial1_untruncated.log) | the certificates' 160-mode minimizers | genuine ~1e-40 components up to degree 318 are amplified by the derivative tail bounds (n² per derivative): W radii 1e10–1e20 |
| 2 (scores_trial2_truncated.log) | same, components < 1e-16 zeroed | tails unchanged, falling like 1/T (L = 0.4 even: 2.3e-3 → 1.1e-4 from cutoff 128 to 1024): the minimizers do not vanish at ±L, so the zero-extended wave has a boundary jump and |F|² ~ t⁻² |
| 3 (scores_trial3_boundary_double.log) | 160-mode minimizer constrained to vanish with 4 derivatives at ±L, constraints in double precision | constraints held only to 1e-16 (useless after four derivatives at degree 300); 160 modes re-triggered the degree-320 quadrature blow-up |
| 4 (scores4.log, d22_score_cand2_*.json) | 80-mode constrained candidates, constraints enforced to 1e-47 in 60-digit arithmetic; reduced minima only 2.5–12.8 % above the unconstrained | tails still fall only like T^{-2}–T^{-4}: the derivative bound uses Plancherel norms of high derivatives of degree-158 polynomials, which are enormous even when the true Fourier tail is small; best achieved relative widths 0.92 (odd 0.4), 3.9 (even 0.4), 13 (even 0.5), 66 (even 0.6), 670 (even 0.7) at cutoff 512 |
No point enters the profile fit; Astra's "> 10 % difference somewhere" prediction is UNVERIFIED (no accepted point), as the protocol allows. The blocker is now precise: the D9 tail method bounds ∫_{|t|>T} a|F|² through boundary derivatives and derivative norms; for the candidates that matter it is loose by orders of magnitude relative to the true tail. Two repairs, each beyond this cap: (i) direct rigorous quadrature of the tail to T₂ ≈ 4000 with the crude bound beyond (≈ 20 CPU-min per wave); (ii) a spectral-side tail bound using exact Bessel asymptotics of the finite Legendre sum. Note: the control rerun overwrote the 128/256/512 score JSON for the even L = 0.5 candidate; those numbers are preserved in scores4.log.

## 3. Controls
- Monotonicity on one fixed wave (even, L = 0.5, trial-4 candidate): R₂₄₀ − R₁₆₀ = +2.86e-8 (certain ≥ 0); W − R₂₄₀ ≥ +2.83e-8 (certain ≥ 0). PASS.
- Scorer controls: D9's 11 controls and the D9 frozen-wave replay passed in D21 with the same scorer copy.
- Nested-space monotonicity (192 vs 160 modes at the SAME T) was not run: the cap allowed only T = 240/192 at L = 0.7 (a different T), so that control is NOT DONE.
- Survivor mutation in a sine/geometric basis: NOT DONE (no accepted point to mutate).

## 4. Prediction ledger
| prediction | outcome |
|---|---|
| Astra: decrease survives qualitatively | HELD (certified lower envelope falls 1.4e-4 → 2.7e-13 even) |
| Astra: at least one reduced minimum differs from a resolved full-W bracket by > 10 % | UNVERIFIED (no bracket resolved) |
| Astra: the slope stays a local fit | HELD (53 → 65 → 83 on certified lower bounds) |
| Fable (1): certified bounds match floating D12/D19 to 20 % | HELD at 0.4 (9 %), 0.5 (2 %), 0.7 (7 %); FAILED at 0.6 (37 % higher) |
| Fable (2): brackets close at 0.4 and 0.5 | FAILED (all open) |
| Fable (3): W within 10 % of R where brackets close | UNVERIFIED |
| Fable (4): single slope 50–75 | FAILED (slopes rise 53 → 83) |
| Fable (5): controls | monotonicity HELD; nested-space and mismatch controls NOT DONE |
| scoring-trial predictions 2, 3, 4 (brackets close at 0.4/0.5) | FAILED three times, each with its diagnosis kept |

## 5. What this round established
Positive: rigorous, checker-accepted lower bounds for the compact-window Weil form at four rooms and two cutoffs, showing the certified floor decays faster than exponentially in L (slope increasing) and depends on T at the 25 % level at L = 0.7. Negative: with the D9 tail method no two-sided bracket of the full infimum closes at 10 % at any tested L; the obstacle is not precision but the tail bound's structure. Unchanged: the L = 0.7 certificate; nothing about all windows or RH.
