# Opus round D7 — independent certificate audit: predictions written BEFORE compute

Auditor: Claude Opus 5 (independent of Fable, who produced D4–D6, and of Codex, who produced the sine-basis certificates).
Repository: /Users/peterviviani/golden-horizon-principle, branch `codex/metatron-prime-return-v0`, HEAD at time of preregistration: **b68b14c988c6a8e14ab565135fcea14c3700de55**.
Scope: verify or refute the L = 7/10, T = 120 compact-window certificate as stated in FABLE-ROUND-D6-RESULTS.md. No larger windows, no new physical models, no search for matching constants. The two 0.7s (GHP c = 7/10 and support half-width L = 0.7) are explicitly NOT investigated here.

## Compute budget (set before running anything)
- Total wall clock of computation: **≤ 90 minutes**.
- Any single run: **≤ 20 minutes** (enforced by Python-level mode/panel limits and background execution; `timeout` is unavailable).
- Precision: 192–256 bit Arb balls via python-flint 0.6.0 at /private/tmp/weil-arb-gTYWza/venv/bin/python.
- If the full 80-mode reconstruction of both sectors exceeds the budget, I report partial results (fewer modes) and explicitly DO NOT promote them to a verification of the 80-mode constants.

## Independently derived objects (derivation recorded in the results file, not here)
I derived, from the Riemann–von Mangoldt/Weil explicit formula and not from Fable's text:
W(f) = Pi(f) + int_R Psi(t) |F(t)|^2 dt, Psi = a - P, a(t) = Re psi(1/4 + it/2) - log pi,
P(t) = sum_{n in {2,3,4}} (2 Lambda(n)/sqrt n) cos(t log n), Pi(f) = 2 Re[ fhat(i/2) conj(fhat(-i/2)) ],
R_T(f) = int_{|t|<=T} (Psi - beta*) |F|^2 dt + beta* ||f||^2 + Pi(f), beta* = a(T) - B, B = P(0).
Predicted before checking Fable's numbers: B = 2.9419735..., beta*(T=120) = 0.00763..., and the T threshold for beta* > 0 is T = 2 pi e^B ~ 119.07, i.e. T = 120 is barely above threshold.

## Preregistered claim: which step is MOST LIKELY TO FAIL
**P0 (primary).** The **quadrature-error theorem constant**. d5_certify.py uses `Cq = (64/15) h rho^(-2K)/(rho^2 - 1)` attributed to Trefethen ATAP Thm 19.3. My recollection of ATAP Thm 19.3 has the denominator `(1 - rho^(-2n))`, not `(rho^2 - 1)`; with rho = 2 those differ by a factor ~3. **PREDICTED: the cited constant is misquoted (too small by a factor between 3 and 4), i.e. a genuine defect in the citation, but HARMLESS**, because the entry error bound is ~6e-23 and a factor 4 leaves it ~2e-22, still 9 orders below the 1.03e-13 eigenvalue. I will therefore NOT rely on any remembered ATAP constant: I will derive my own Gauss-quadrature error bound from Bernstein's Chebyshev-coefficient theorem (|a_k| <= 2 M rho^-k) plus positivity of Gauss weights, giving error <= h * 8 M rho / ((rho - 1) rho^{2K}), and use that.
Ranked runners-up, all of which I predict will SURVIVE: (P1) the infinite discarded-block/coupling operator-norm bounds; (P2) the congruence-to-eigenvalue conversion lambda_min(A) >= lambda_min(V^T A V)/lambda_max(V^T V); (P3) the Hermitian pole decomposition for complex f; (P4) the domain statement for W on L^2 minus D_W.
I explicitly do NOT assume the remaining obligations are editorial: P0 is a substantive misquotation if confirmed, and the "independent replay" obligation is precisely what D7.2 tests.

## Numerical predictions (to be scored HELD / FAILED, failures preserved)
1. **N1** My independent matrix build reproduces the three even cross-check entries of d5_results_even_NE80_pole+1.json: M(0,0) = -2.8719459474324615205, M(0,2) = 0.066388923568830598971, M(20,40) = 0.055741017294763338419, each to within 1e-18.
2. **N2** Even sector certified lower bound reproduces to at least 8 significant digits: 1.0310177602e-13.
3. **N3** Odd sector certified lower bound reproduces to at least 8 significant digits: 5.8590708532e-11.
4. **N4** Independently recomputed tail constants agree in order of magnitude: eps_D < 1e-35, eps_C in [1e-16, 1e-15] (even) and [1e-17, 1e-16] (odd), eps_p < 1e-400.
5. **N5** The full-form (infinite-dimensional) lower bound after the Schur correction differs from the finite-block bound by less than 1e-28 in the even sector.
6. **N6 (sensitive direction, upper bound).** Freezing an approximate even-sector minimizing vector as an exact dyadic 80-vector c and evaluating R_T(c)/||c||^2 rigorously gives a ball whose upper endpoint lies in [1.0310177e-13, 1.0310179e-13] and whose lower endpoint is > 0. This is an UPPER bound on the minimum, not a certificate.
7. **N7** The certified lower bound and the frozen-vector score sandwich the true minimum to relative width < 1e-6.
8. **N8** The advertised constants are correct after downward rounding: 1.031e-13 ACCEPT, 1.032e-13 REJECT, 5.859e-11 ACCEPT, 5.86e-11 REJECT, reproduced by my own independent endpoint checker.
9. **N9 (pole sign is load-bearing in the even sector).** Replacing +2 p p^T by -2 p p^T in the even sector makes the form indefinite: approximate lambda_min < -0.5.
10. **N10 (pole sign is NOT caught by a positivity checker in the odd sector).** Replacing -2 s s^T by +2 s s^T in the odd sector leaves the form positive definite with lambda_min ~ 1.7e-6, i.e. a generic positivity checker ACCEPTS the wrong model. This is a model-validation failure, not a checker failure, and I predict it reproduces.
11. **N11** Independent evaluation of the pole vector by the closed form p_n = sqrt((2n+1)/(2L)) * 2L * i_n(L/2) (modified spherical Bessel) agrees with the certificate's ||p_N|| = 1.20771838681 (even) and 0.242040702857 (odd) to 1e-11.
12. **N12 (control) Singular basis.** My own congruence certifier, fed a rank-deficient V, must refuse to emit a bound.
13. **N13 (control) Nonorthogonal invertible basis.** Fed V = Q diag(1, 10, ..., ) with Q orthogonal, my certifier must still return a correct (smaller) lower bound, not an inflated one; specifically the returned bound must remain <= the frozen-vector score of N6.
14. **N14 (control) Missing tail evidence.** With eps_D withheld, the verdict must be NO_VERDICT, not ACCEPT.
15. **N15 (control) Excessive coupling.** With off = 1e-5 and lambda0 = 1e-13, the certified 2x2 Schur inequality must fail and the verdict must be REJECT.

## Kill conditions
- If N1 fails by more than 1e-15, my form and Fable's are not the same form and the audit verdict becomes "specific defect found" or "UNVERIFIED", not "verified".
- If N2 or N3 fails in the first 6 significant digits, the reported constants are refuted.
- If N6's ball straddles zero, the reconstruction cannot resolve the sign and I report UNVERIFIED with the precision needed.
- If P0 is confirmed AND the corrected constant pushes the entry error above 1e-14, the certificate is VOID until re-run.

## Verdict labels available
MEASURED / UNVERIFIED / PREDICTED / VOID; final verdict one of: independently verified (with scope and constants) / positive with a weaker independently certified bound / specific defect found / UNVERIFIED naming the obligation.

No zeta zero ordinates are used anywhere. No novelty is claimed. Committed locally before compute; not pushed.
