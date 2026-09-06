# Fable round D6 — certificate hardening at L = 0.7 (2026-09-06)
Predictions: FABLE-PREDICTIONS-D6.md (commit bb517fe, before compute). New code: d6_checker.py, d6_tests.py, d6_sameform.py. Outputs: d6_constants.json, d6_tests.json, d6_sameform.json/.log. Codex's files untouched; d4_checker.py and d5_certify.py unchanged. Committed locally, not pushed. No new constructions, no larger window, no zero inputs, no novelty claim.

## D6.1 Corrected analytic statement

### Conventions (fixed throughout)
L = 7/10. For f ∈ L²([−L, L]; ℂ), extended by zero:
- Fourier: F(t) = (2π)^{−1/2} ∫ f(x) e^{−ixt} dx, so ‖F‖_{L²(ℝ)} = ‖f‖ (Plancherel). f̂(ξ) := ∫ f(x) e^{−iξx} dx = (2π)^{1/2} F(ξ) for real ξ; f̂ is entire.
- Autocorrelation: f̃(x) := conj(f(−x)), g := f ⋆ f̃, g(x) = ∫ f(y) conj(f(y − x)) dy. Then g is continuous, supp g ⊂ [−2L, 2L], g(−x) = conj(g(x)), and ĝ(ξ) = f̂(ξ)·conj(f̂(ξ̄)) for every complex ξ (substitute u = y − x). In particular ĝ(t) = |f̂(t)|² = 2π|F(t)|² for real t.
- Archimedean symbol: a(t) = Re ψ(¼ + it/2) − log π = ½[ψ(¼ + it/2) + ψ(¼ − it/2)] − log π (real, even, analytic on |Im t| < ½).
- Prime symbol: P(t) = Σ_{n = p^k ≤ e^{2L}} (2Λ(n)/√n) cos(t log n) = Σ_{n∈{2,3,4}} (2 log p/p^{k/2}) cos(t log n); e^{2L} = 4.0552 < 5. B := P(0) = Σ weights = 2.9419735…, |P| ≤ B.
- Ψ := a − P.
- Pole functional: Π(f) := ĝ(i/2) + ĝ(−i/2) = f̂(i/2) conj(f̂(−i/2)) + f̂(−i/2) conj(f̂(i/2)) = 2 Re[ f̂(i/2) conj(f̂(−i/2)) ], with f̂(±i/2) = ∫ f(x) e^{±x/2} dx. (Conjugations placed by ĝ(ξ) = f̂(ξ) conj(f̂(ξ̄)) with ξ̄ = ∓i/2.)

### The exact Weil form W and where it comes from (normalization derived)
Take the explicit formula in the form (for g continuous, compactly supported, of bounded variation; h(r) := ∫ g(x) e^{irx} dx)
 Σ_ρ h(γ_ρ) = h(i/2) + h(−i/2) − Σ_{n≥2} (Λ(n)/√n)[g(log n) + g(−log n)] + (1/2π) ∫_ℝ h(r) [Re ψ(¼ + ir/2) − log π] dr,
zeros ρ = ½ + iγ_ρ with multiplicity. With g = f ⋆ f̃: h(r) = ĝ(−r), so h(±i/2) = ĝ(∓i/2) and h(i/2) + h(−i/2) = Π(f); g(log n) + g(−log n) = 2 Re g(log n) = (1/2π)∫ h(r)·2cos(r log n) dr = ∫ |F(r)|²·2cos(r log n) dr (using ĝ(−r) = 2π|F(−r)|² and the substitution r → −r); the archimedean term is ∫ |F(r)|² a(r) dr. Terms with log n > 2L vanish because supp g ⊂ [−2L, 2L]. Hence
 W(f) := Π(f) + ∫_ℝ Ψ(t) |F(t)|² dt = Σ_ρ h(γ_ρ)   (identity on the explicit-formula class; positivity of the left side for all admissible f is Weil's criterion).
The three factors that could have been mis-normalized — the 2π between |f̂|² and |F|², the factor 2 in 2Λ(n)/√n (from g(log n) + g(−log n)), and the pole with both orderings — are fixed by this derivation and tested against Codex's independent position-space W in T4 below.

### Complex functions: the false pointwise identity and the true integrated one
For f = f1 + i f2 with f1, f2 real: F = F1 + iF2 and
 |F1 + iF2|² = |F1|² + |F2|² − 2 Im( conj(F1) F2 )   (pointwise; the cross term is generically nonzero — T1 measures 0.1578 at t = 1).
Because f1, f2 are real, F_j(−t) = conj(F_j(t)), so conj(F1)F2 at −t is the conjugate of its value at t and the cross term −2 Im(conj(F1)F2) is an ODD function of t. Ψ is even and Ψ|F|² is integrable on every f with finite W, hence the weighted integral of the cross term vanishes (absolutely convergent odd integrand):
 ∫ Ψ |F|² = ∫ Ψ |F1|² + ∫ Ψ |F2|².
Pole: f̂(i/2) = a1 + i a2, f̂(−i/2) = b1 + i b2 with a_j = ∫ f_j e^{x/2}, b_j = ∫ f_j e^{−x/2} real; Π(f) = 2 Re[(a1 + ia2)(b1 − ib2)] = 2(a1b1 + a2b2) = Π(f1) + Π(f2). The naive non-Hermitian expression 2 f̂(i/2) f̂(−i/2) = 2(a1b1 − a2b2) + 2i(a2b1 + a1b2) is wrong for complex f (T1: differs by 0.234 in the test case). So W(f) = W(f1) + W(f2).
Parity: for real f = f_e + f_o, F_e is real even and F_o is imaginary odd, so Ψ F_e conj(F_o) is odd and integrates to zero; f̂(±i/2) = C ± S with C = ∫ f_e cosh(x/2), S = ∫ f_o sinh(x/2), so Π(f) = 2(C + S)(C − S) = 2C² − 2S² = Π(f_e) + Π(f_o). Hence W(f) = W(f_e) + W(f_o), and a lower bound λ_e‖f_e‖² + λ_o‖f_o‖² ≥ min(λ_e, λ_o)‖f‖² covers every complex f ∈ L²([−L, L]).

### Domain
Since |a(t) − log(2 + |t|)| ≤ C₀ for all real t (a(t) = log(|t|/2) − log π + O(t⁻²)), and |P| ≤ B, the integral ∫ Ψ|F|² converges absolutely iff ∫ |F(t)|² log(2 + |t|) dt < ∞. Compact support plus L² does NOT imply this (Paley–Wiener functions may have |F|² ~ 1/(t log² t) along the real axis). Define
 𝒟_W := { f ∈ L²([−L, L]) : ∫ |F|² log(2 + |t|) dt < ∞ } ⊃ H^s([−L, L]) for every s > 0, ⊃ BV, ⊃ C_c^∞.
On all of L², W is well defined with values in (−∞, +∞]: Ψ ≥ inf Ψ = a(0) − B (a is increasing in |t|, shown below), so the negative part of Ψ|F|² is integrable and bounded by |a(0) − B|·‖f‖² ≤ 8.32‖f‖²; W(f) = +∞ exactly when f ∉ 𝒟_W. The identity with Σ_ρ h(γ_ρ) is only asserted on the explicit-formula class (g of bounded variation suffices; C_c^∞ ⊂ this class); it is not needed for the inequality below.

### Lower envelope R_T (bounded form on all of L²)
T := 120, β* := a(T) − B = 0.0076382575953959615868 ± 3.2e-24 > 0 (balls).
 R_T(f) := ∫_{|t| ≤ T} (Ψ(t) − β*) |F(t)|² dt + β*‖f‖² + Π(f).
R_T is a bounded Hermitian form on L²([−L, L]): |R_T(f)| ≤ (sup_{|t|≤T}|Ψ − β*| + β* + 2‖e^{x/2}‖²)‖f‖². For every f ∈ L²,
 W(f) − R_T(f) = ∫_{|t| > T} (Ψ(t) − β*) |F(t)|² dt ∈ [0, +∞],
because Ψ(t) ≥ a(t) − B ≥ a(T) − B = β* for |t| ≥ T. Monotonicity of a on t > 0: d/dt Re ψ(¼ + it/2) = Re[(i/2)ψ′(¼ + it/2)] = −½ Im ψ′(¼ + it/2), and Im ψ′(σ + it) = Σ_{k≥0} Im (σ + k + it)^{−2} = −Σ_k 2(σ+k)t/|σ + k + it|⁴ < 0 for t > 0. Equality W = R_T would force F ≡ 0 on |t| > T, impossible for f ≠ 0 with compact support (F entire), so W > R_T strictly on 𝒟_W∖{0}; the gap is not estimated.

### Corrected theorem (every hypothesis stated)
Let L = 7/10, T = 120, and W, R_T, 𝒟_W as above. Then:
(i) R_T(f) ≥ λ_e‖f‖² for all real even f ∈ L²([−L, L]), R_T(f) ≥ λ_o‖f‖² for all real odd f, with certified constants λ_e = 1.031·10⁻¹³, λ_o = 5.859·10⁻¹¹ (D6.2).
(ii) R_T(f) ≥ 1.031·10⁻¹³ ‖f‖² for all f ∈ L²([−L, L]; ℂ).
(iii) W(f) ≥ 1.031·10⁻¹³ ‖f‖² for all f ∈ L²([−L, L]; ℂ), with W(f) = +∞ off 𝒟_W.
(iv) For f in the explicit-formula class (in particular C_c^∞((−L, L))), Σ_ρ h(γ_ρ) ≥ 1.031·10⁻¹³ ‖f‖² with h(r) = |∫ f e^{irx} dx|² on real r.
Proof status: (i) is machine-certified modulo the analytic lemmas listed in D6.2; (ii) follows from (i) by the decoupling identities above (analytic); (iii) from (ii) and W ≥ R_T (analytic); (iv) from (iii) and the explicit formula (literature). What (iv) says about RH: nothing beyond consistency — the inequality is implied by RH and is here shown unconditionally for this one window; Zhu 2608.24827 proves the analogous statement for L = 0.8.

## D6.2 Constants, rounded downward (d6_checker.py; d6_constants.json)
Ball strings printed in the D5 JSONs enclose the computed balls, so parsing them is rigorous. Lower endpoint λ₀⁻ = mid − rad; the full-spectrum bound is the smaller eigenvalue μ of [[λ₀⁻, −off],[−off, d_low]] with off = ε_C + 2‖p_N‖ε_p (upper endpoint) and d_low = β* − ε_D − 2ε_p² (lower endpoint), which is ≥ λ₀⁻ − off²/(d_low − λ₀⁻).

| sector | λ₀ (ball) | λ₀⁻ | off | d_low | Schur correction | certified μ (lower) | advertised (rounded DOWN) |
|---|---|---|---|---|---|---|---|
| even | 1.03101776024e-13 ± 9.33e-26 | 1.03101776023907e-13 | 3.885e-16 | 7.638257595e-3 | 1.976e-29 | 1.03101776023907e-13 − 2e-29 | **1.031e-13** (3 sig: 1.03e-13) |
| odd | 5.85907085321e-11 ± 5.21e-24 | 5.85907085320948e-11 | 9.535e-17 | 7.638257595e-3 | 1.190e-30 | 5.85907085320948e-11 − 1.2e-30 | **5.859e-11** (3 sig: 5.85e-11) |

D5's advertised "5.86e-11" was rounded UP and is withdrawn; 5.859e-11 is the largest 4-significant-digit constant the endpoint supports (T2). The even constant 1.031e-13 was already valid. (Note: 5.85907085e-11 as printed in D5 §1 is itself ≤ the endpoint and was fine; the 3-digit rounding was the error.)

### Evidence classification (what is machine-certified, what needs a proof)
Machine-certified (Arb balls, 192 bits, one run each; replay by another party still outstanding):
- β*, a(0), a(T); sup_{[0,T]}|Ψ − β*| (given monotonicity); all 80×80 matrix entries with quadrature error balls (max radius 1.17e-22); pole vectors; ε_D, ε_C, ε_p as evaluated from their formulas; Gershgorin minimum of VᵀAV; λmin(VᵀV) ≥ 1 − 3e-25 (invertibility); λmax(VᵀV) ≤ 1 + 1e-24 (norm conversion).
Analytic, proved in the text or in FABLE-PREDICTIONS-D4.md, not machine-checked:
- the normalization derivation of W (D6.1); monotonicity of a; |P| ≤ B; Ψ ≥ β* on |t| ≥ T;
- sup_{x≥0}|j_n(x)| ≤ x^n/(2n+1)!!·e^{x²/(2(2n+3))} and the same for i_n (positive-series comparison (2n+3)(2n+5)⋯ ≥ (2n+3)^k), giving ε_D, ε_C, ε_p;
- Legendre coefficients of e^{±x/2}: ∫_{−1}^{1} e^{zs}P_n(s)ds = 2 i_n(z) (T6 checks numerically to 1e-31);
- the strip bound |j_n(z)| ≤ e^{|Im z|} from j_n(z) = (2 i^n)^{−1}∫_{−1}^{1} e^{izs} P_n(s) ds and |P_n| ≤ 1 (T6: no violation in 200 points, worst ratio 0.22);
- Trefethen ATAP Thm 19.3 (Gauss quadrature error ≤ (64/15) M ρ^{−2K}/(ρ² − 1) for f analytic in E_ρ, |f| ≤ M) and analyticity of the integrand inside the ellipse (F_n entire; a analytic for |Im t| < ½; ellipse semi-minor axis 0.375);
- the infinite Schur argument: for every finitely supported coefficient vector Q ≥ λ₀‖u‖² − 2·off·‖u‖‖v‖ + d_low‖v‖² ≥ μ‖c‖², extended to ℓ² by continuity of the bounded form R_T; ε_C bounds the Hilbert–Schmidt norm of the coupling block, which dominates the operator norm;
- the Gershgorin conversion λmin(A) ≥ λmin(VᵀAV)/λmax(VᵀV) for invertible V;
- correctness of python-flint/Arb.
Literature, not re-proved: the explicit formula on the bounded-variation class; Trefethen's theorem; Halmos (D5).

## D6.3 Adversarial verification (all preregistered)

| test | prediction | outcome |
|---|---|---|
| T1 pointwise cross term at t = 1 (f1 = q₀, f2 = q₁) | |·| > 1e-3 | 0.15777 — identity is false pointwise (HELD) |
| T1 weighted integral of the cross term | 0 to < 1e-25 (balls) | halves over [ε,T] and [−T,−ε] are ∓0.43548943558335592876; their sum is [± 1.04e-30], contains 0 (HELD). First attempt returned NaN from the removable singularity of the closed-form j₁ at t = 0; kept in d6_tests.json; repaired by splitting at ε = 1e-3 (the odd integrand integrates to exactly 0 on [−ε, ε]) |
| T1 Hermitian pole = Π(f1) + Π(f2); naive product differs | < 1e-25; > 1e-3 | [± 5.5e-56]; 0.2343 (HELD) |
| T2 endpoint checker: 5.86e-11 → REJECT, 5.859e-11 → ACCEPT, 1.031e-13 → ACCEPT, 1.032e-13 → REJECT | 4/4 | 4/4 (HELD) |
| T3 d4_checker.py (excess coupling, missing tail, uncertified λ₀, coupling 1e-5, positive control) | 5/5 | CHECKER OK, 5/5 (HELD) |
| T4 same form W, Codex's sine basis, frequency-space mpmath vs Codex's position-space Arb (6 entries + one parity zero) | |diff| < 1e-9 | diffs −1.6e-12 (1,1), −4.8e-12 (1,3), −6.4e-12 (2,2), −1.4e-11 (3,3), −1.3e-11 (2,4), −2.6e-11 (4,4); (1,2) = 4.9e-32 vs 0. All < 1e-9 (HELD). Every difference is negative and 25–30 % of the analytic estimate of the omitted tail ∫_{|t|>T_b}, which is positive — the signature of the SAME form truncated at T_b = 2·10⁴, not of a normalization mismatch (a wrong 2π, factor 2, or pole ordering would show at 1e-3 or larger) |
| T5 independent floating evaluation of six certified Legendre entries (mpmath besselj/digamma, tanh-sinh, 30 digits) | within 1e-15 of centres | all six INSIDE the certified balls: diffs ≤ 8.8e-20 (even (0,0)), ≤ 5e-22 for the others (HELD, stronger than predicted) |
| T6 strip bound, 200 random points | no violation | 0 violations, worst ratio 0.222 (HELD) |
| T6 Legendre/i_n identity, 20 points | ≤ 1e-25 | max error 1.1e-31 (HELD) |
T5 is a different quadrature (tanh-sinh vs Gauss–Legendre), a different Bessel implementation (mpmath hypergeometric vs my series/Rayleigh forms) and a different digamma; it is floating, so it is evidence, not a certificate. T4 is the only test that compares my form with Codex's on identical functions; a comparison of minima over different subspaces (Codex's 32 sine modes vs my 80 Legendre modes) is not made and would not be meaningful.

## D6.4 Prediction ledger
| prediction | outcome |
|---|---|
| pointwise identity false, integrated identity true by oddness | HELD |
| Hermitian pole decouples; naive product does not | HELD |
| even 1.031e-13 valid; odd 5.86e-11 invalid → 5.859e-11 | HELD |
| no constant changes beyond the odd rounding | HELD |
| T1–T3, T5, T6 as tabulated | HELD (T1 needed one repair, kept) |
| T4 |diff| < 1e-9 | HELD (max |diff| 2.6e-11, consistent with the tail estimate) |
| verdict "survives with corrected exposition" | HELD |

## Exact remaining audit obligations
1. Independent replay of d5_certify.py (both sectors) by another party on another machine; ideally an independent ball-arithmetic implementation of the same R_T.
2. A machine-checked (or refereed) proof of the four analytic lemmas that feed the tails: the j_n/i_n series bounds, the strip bound, the Legendre coefficient formula, and Ψ ≥ β* on |t| ≥ T. All are elementary; none is currently more than a text proof plus numerical spot checks.
3. The explicit-formula identity W(f) = Σ_ρ h(γ_ρ) on the bounded-variation class is taken from the literature; the statement (iv) depends on it, (i)–(iii) do not.
4. The digamma box bound in the quadrature error (2.4e4, loose) and the Frobenius-for-operator-norm substitution are rigorous but wasteful; not an obligation, noted for anyone tightening constants.
5. No statement here applies to any window other than L = 0.7, T = 120.

## Verdict
**Certificate survives with corrected exposition.**
- Analytic: the D5 pointwise identity was false; the integrated identity holds by oddness and the Hermitian pole decouples, so the parity certificates cover all complex f ∈ L²([−L, L]). The domain is now stated: W ∈ (−∞, +∞] on all of L², finite exactly on 𝒟_W; R_T is bounded on all of L²; W ≥ R_T on all of L²; the zero-sum identity is used only on the explicit-formula class.
- Numerical: no repair to any certified quantity. One advertised constant was rounded upward and is corrected: odd 5.86e-11 → 5.859e-11. Even 1.031e-13 stands. Both include the Schur correction (< 2e-29).
- Same form: Codex's position-space W and my frequency-space W agree on identical functions to the accuracy of the truncation (T4), so the two certificates certify the same quadratic form.
- Open, listed above: independent replay; refereed proofs of four elementary lemmas; the literature explicit formula behind statement (iv). None of these is a specified inequality that remains open; all are verification obligations.
No novelty claimed. Stop.
