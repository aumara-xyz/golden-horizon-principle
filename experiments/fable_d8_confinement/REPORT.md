# D8 — Can confinement limit the arithmetic contribution? (Fable, 2026-09-06)
Predictions: PREDICTIONS.md (commit 3bc0dd5, before compute). Code: d8_lemma.py (controls, prime sums, grid sup), d8_combined.py (θ-family at threshold T), the T-sweep script embedded in d8_tsweep.log / d8_tsweep_results.json. All computation floating (numpy/scipy double precision); nothing here is a certificate. No zero ordinates, no φ, no larger-window certificate. Committed locally, not pushed.

## 0. D7 reporting issue (closed; Opus's files untouched)
Recomputed outward from Opus's saved balls (`full_form_lower_bound` lower endpoint, `frozen_vector_score_upper` upper endpoint; python-flint parse of the printed balls, which enclose the computed balls): d8_step0_d7_sandwich_recheck.json.
| sector | lower (outward) | score upper (outward) | relative width | Opus printed | advertised constant supported |
|---|---|---|---|---|---|
| even | 1.03101781648891786e-13 | 1.03101781651300182e-13 | 2.336e-11 | 2.3e-14 (wrong ×1000) | 1.031e-13 ≤ lower: yes |
| odd | 5.85907085398902634e-11 | 5.85907085398936303e-11 | 5.747e-14 | 5.6e-15 (wrong ×10) | 5.859e-11 ≤ lower: yes |
Codex's readout is confirmed digit for digit. The sandwich still resolves the sign by 13 orders; only the printed widths were wrong. MEASURED.

## 1. Identity (proved)
For f ∈ L²(ℝ) supported in [−L, L], (T_a f)(x) = f(x − a), unitary F(t) = (2π)^{−1/2}∫f e^{−ixt}: the transform of T_a f is e^{−iat}F(t), and Plancherel gives ⟨f, T_a f⟩ = ∫ F(t) conj(e^{−iat}F(t)) dt = ∫ e^{iat}|F(t)|² dt, so
 ∫_ℝ cos(at)|F(t)|² dt = Re⟨f, T_a f⟩   (for real f the imaginary part is zero because |F|² is even).
Restricting T_a f back to [−L, L] changes nothing: the inner product only sees x ∈ [−L, L]. Hence the integrated prime contribution is exactly Σ_n w_n Re⟨f, T_{log n} f⟩, w_n = 2Λ(n)/√n, and the support constraint is retained. MEASURED (derivation), no numerics needed.

## 2. Truncated-translation lemma (proved, sharp)
**Lemma.** For a > 0 and f ∈ L²(ℝ) supported in [−L, L] (complex allowed):
 Re⟨f, T_a f⟩ ≤ cos(π/(N+1)) ‖f‖²,  N = ⌈2L/a⌉,
and the constant is attained (sup over f ≠ 0 equals cos(π/(N+1))). For a ≥ 2L the left side is 0 and N = 1 gives cos(π/2) = 0.
*Proof.* Write 2L/a = q + r, q ∈ ℕ, 0 ≤ r < 1. For x₀ ∈ [−L, −L + a) let the chain be x₀ + ja, j = 0, …, m(x₀), m = ⌊(L − x₀)/a⌋. Since (L − x₀)/a ∈ (q + r − 1, q + r], m = q for x₀ ∈ [−L, −L + ra] and m = q − 1 otherwise; so a.e. chain has at most N = ⌈2L/a⌉ points (if r = 0 the single (q+1)-point chain x₀ = −L has measure zero). Fubini: Re⟨f, T_a f⟩ = ∫_{−L}^{−L+a} Σ_{j=1}^{m} Re f(x₀+ja) conj(f(x₀+(j−1)a)) dx₀. For a chain vector v ∈ ℂ^{m+1}, Σ_j Re v_j conj(v_{j−1}) = ½ v*A_{m+1}v where A_{m+1} is the adjacency matrix of the path on m+1 vertices, whose eigenvalues are 2cos(πk/(m+2)); so the sum is ≤ cos(π/(m+2))‖v‖² ≤ cos(π/(N+1))‖v‖². Integrate over x₀ and use ∫Σ_j|v_j|² dx₀ = ‖f‖². Sharpness: the long chains (m+1 = N points) fill a set of x₀ of measure ra > 0 (all chains when r = 0); put the Perron eigenvector (sin(πj/(N+1)))_j of the path on each long chain and 0 on short chains. ∎
Exact companion identity (proved the same way, or by Plancherel on ℝ): ∫(1 − cos at)|F|² dt = ½‖f − T_a f‖²_{L²(ℝ)}; the "loss" is the mass translation pushes outside [−L, L] plus the internal difference energy: Re⟨f,T_af⟩ = ‖f‖² − ½∫_{−L+a}^{L}|f(x)−f(x−a)|²dx − ½(‖f‖²_{[−L,−L+a)} + ‖f‖²_{(L−a,L]}). Consequently W admits the exact positive decomposition
 W(f) = ∫(a(t) − B_L)|F|² dt + ½ Σ_n w_n ‖f − T_{log n} f‖²_{L²(ℝ)} + Π(f),
which shows why the crude constant B_L is exact precisely on functions nearly invariant under every prime shift.
Edge cases handled: integer ratio 2L/a (measure-zero long chain), measure-zero endpoints (irrelevant in L²), a ≥ 2L (zero overlap). Complex f: the path form is Hermitian, so nothing changes.

### Controls (d8_lemma_results.json)
| control | prediction | outcome |
|---|---|---|
| C1 path matrix P_N, N ≤ 12: top eigenvalue = 2cos(π/(N+1)) | error < 1e-12 | max error 8.9e-16 (HELD) |
| C4 grid discretisation (M = 1400 cells, shift = integer cells) vs lemma, 12 (L, n) cases | equal | equal to 9 digits in every case (HELD) |
| C2 periodic boundary (circulant shift) | sup = 1, constants keep full correlation | 1.000000 in every case (HELD) |
| C3 support enlargement at a = log 2: loss 1 − cos(π/(N+1)) | ≈ π²/(2(N+1)²) → 0 | N = 2,3,3,6,12,24 for L = 0.4…8: loss 0.50, 0.29, 0.29, 0.099, 0.029, 0.0079 (HELD) |

### Prior art (assessed, not exhaustive)
The operator f ↦ P_{[−L,L]}(T_a + T_{−a})f/2 is the compression of a translation to an interval, equivalently the Toeplitz operator with symbol cos(at) on the Paley–Wiener space PW_L (Rochberg, "Toeplitz and Hankel operators on the Paley–Wiener space", Integral Equations Operator Theory 1987). The chain/path-graph evaluation of its norm is elementary and I regard it as known in substance; I did not find the explicit cos(π/(⌈2L/a⌉+1)) formula in the two searches made (search log in this report; no MathSciNet access). Classical small-support positivity — Yoshida, and Connes–Consani "Weil positivity and trace formula, the archimedean place" (Selecta 2021) — covers supp f ⊂ [−log2/2, log2/2], i.e. exactly the range where no prime shift overlaps the support (2L ≤ log 2), so the lemma is trivial there. Bombieri, "Remarks on Weil's quadratic functional in the theory of prime numbers I" (2000) studies the minimum on [−t, t]. Zhu 2608.24827 (v2) proves the L = 0.8 window by the pointwise envelope with the comb constant B_L shown optimal by equidistribution — the pointwise statement this round explicitly does not revive. Status of the lemma: MEASURED (proved here), NOT claimed new.

## 3. The prime-power sum (d8_lemma_results.json)
c_L := Σ_n w_n cos(π/(⌈2L/log n⌉ + 1)) (sum of single-shift bounds, rigorous by the lemma); s_L^grid := top eigenvalue of Σ_n w_n (S_n + S_nᵀ)/2 on a 1400-cell grid with shifts rounded to whole cells (finite approximation: a lower bound for the true joint sup of the rounded-shift problem, not an operator bound).
| L | prime powers | B_L (crude) | c_L (single-shift sum) | c_L/B_L | s_L^grid (joint, non-rigorous) | s/B | T_env with B | T_env with c |
|---|---|---|---|---|---|---|---|---|
| 0.4 | 2 | 0.9803 | 0.4901 | 0.500 | 0.4901 | 0.50 | 16.7 | 10.3 |
| 0.7 | 2,3,4 | 2.9420 | 1.6740 | 0.569 | 1.1723 | 0.40 | 119.1 | 33.5 |
| 0.8 | 2,3,4 | 2.9420 | 1.6740 | 0.569 | 1.2191 | 0.41 | 119.1 | 33.5 |
| 1.0 | 2,3,4,5,7 | 5.8525 | 3.1293 | 0.535 | 1.9454 | 0.33 | 2187 | 143.6 |
Predicted c_L values (0.4901, 1.6741, 1.6741, 3.130) HELD to 4 digits. Joint sup < 0.95·c_L at L = 0.7: HELD (0.70·c_L); the Legendre-basis top eigenvalue of the same operator (1.164 with 141 modes) lies below the grid value, as predicted for discontinuous extremizers.
Perturbation control (weights kept, shifts scaled): ×0.9 leaves c_{0.7} unchanged (HELD); ×1.1 gives 1.1244, NOT the predicted 1.471 — my hand prediction missed that 1.1·log 4 = 1.525 > 2L = 1.4 drops that term to zero. PREDICTION FAILED on the value; the staircase claim (c depends on shifts only through N) holds. No-boundary control: periodic joint sup = B_L exactly in all four cases (HELD): the entire gain is the boundary.

## 4. The crucial test: combining with the archimedean term
### 4a. What is valid
For θ ∈ [0, 1] (or per-shift θ_n), since ∫P|F|² = Σ_n w_n Re⟨f, T_n f⟩ ≤ c_L‖f‖² for every f ∈ L²[−L, L],
 W(f) ≥ R_θ(f) := ∫_ℝ (a(t) − (1−θ)P(t) − θ c_L) |F(t)|² dt + Π(f),  with R_0 = W.
R_θ is a legitimate lower bound on the whole of L²[−L, L], including complex f and both parities (Π enters with its parity-correct sign +2C² − 2S²), and its envelope threshold is a(T_θ) = (1−θ)B_L + θc_L, i.e. T_θ falls from 119 to 33.5 (L = 0.7) and from 2187 to 144 (L = 1.0) at θ = 1 — as predicted.
### 4b. Why it cannot be localised to high frequencies
The envelope proof needs a bound on ∫_{|t|>T} P|F|² only. Writing this as Re⟨f_{>T}, T_a f_{>T}⟩ with f_{>T} the high-pass part is correct, but f_{>T} is not supported in [−L, L] (its low-pass complement is band-limited, hence never compactly supported), so the lemma does not apply to it. Any attempt to use the lemma on a frequency-cut function is invalid; the θ-family is the general valid combination of this kind. This is the obstruction predicted in the directive, made precise.
### 4c. What happens to positivity (MEASURED, floating; d8_combined_results.json, d8_tsweep_results.json)
L = 0.7, T = 160 (away from the threshold so the reduction is not the limiting factor), Legendre basis, 174 modes:
| θ | λ_min(R_θ) even | score of the W-minimizer f* under R_θ, even | λ_min odd | score odd |
|---|---|---|---|---|
| 0 | +2.5e-13 | +2.5e-13 | +1.6e-10 | +1.6e-10 |
| 0.1 | −0.188 | −0.164 | −0.234 | −0.192 |
| 0.25 | −0.474 | −0.411 | −0.592 | −0.480 |
| 0.5 | −0.954 | −0.821 | −1.193 | −0.961 |
| 1 | −1.923 | −1.642 | −2.409 | −1.921 |
The scores obey R_θ(f*) = W(f*) − θ (c_L − s*) to 1e-12, where s* := Σ_n w_n Re⟨f*, T_n f*⟩/‖f*‖² is the prime saturation of the W-minimizer: s* = 0.032 (even), −0.247 (odd), against c_L = 1.674 and B_L = 2.942. Same picture at L = 0.4 (λ_min(R_1) = −0.49 / −0.63), L = 0.8 (−2.05 / −2.61) and L = 1.0 (−3.71 / −4.45); the eight per-shift {0,1}³ combinations at L = 0.7 are all negative except (0,0,0). Predictions "negative for every θ ≥ 0.25", "s* < c_L − 0.3", "λ_min(R_1) < −0.1" all HELD; the sign at L = 0.4, for which I preregistered no direction, is negative too.
**The obstruction, stated exactly.** The vector that decides positivity is almost orthogonal to every prime shift: for the even minimizer the whole prime term is 0.032‖f*‖² out of a possible 2.94‖f*‖², and for the odd minimizer it is negative (the shifts anti-correlate). A better bound on the prime term can only lower the form by θ(c_L − s*) ≈ 1.6 θ; at the minimizer there is nothing to gain, because the prime comb already averages to ≈ 0 against |F*|². Positivity at the minimizer is decided by the archimedean term against the pole term alone. Better prime-term numbers therefore are not a positivity result, and this family cannot become one. Success category: **a useful inequality whose limitations are precisely established** (lower envelope threshold, exact positive decomposition; no route to positivity through the prime term).
### 4d. Two things found on the way (exploratory, MEASURED floating, not preregistered)
1. The envelope threshold is not automatically enough. At the minimal T (β ≈ 0.01) the reduced form R_T is negative at L = 0.4 (−1.1e-4 even, −1.2e-3 odd, T = 17) and at L = 0.8 (−6e-8 even, −1.9e-3 odd, T = 120.3), and becomes positive for larger T (L = 0.4: +1.7e-4 / +1.4e-2 by T = 160; L = 0.8: sign-unresolved at the 1e-14 noise floor for T = 160, 240, consistent with Zhu's tiny 8.9e-18). R_T is monotone increasing in T (R_{T'} − R_T = ∫_T^{T'}(Ψ − β_T)|F|² + (β_{T'} − β_T)∫_{>T'}|F|² ≥ 0), so a T-margin costs only matrix size. The L = 0.7 certificate at T = 120 (0.8 % above threshold) is NOT a threshold artifact: its minimum rises only from 0.94e-13 (T = 120, 80 modes; certified 1.031e-13) to 2.5e-13 (T = 160) and 3.3e-13 (T = 240) even, and 5.86e-11 → 1.6e-10 → 2.0e-10 odd. Floating results at T = 400, L = 0.8 (424 modes) broke down (spurious −2) and are VOID.
2. My prediction λ_min(W) > 1e-3 at L = 0.4 FAILED for the even sector (≈ 1.7e-4); the odd sector (≈ 1.4e-2) held.

## 5. Scaling limitations (analytic)
B_L = Σ_{n ≤ e^{2L}} 2Λ(n)/√n ~ 4e^{L}. Shifts with log n ∈ (L, 2L] have N = 2 and get factor ½; those in (2L/3, L] get 0.707, etc. Hence c_L ≈ 4e^{L}[½(1 − e^{−L/2}) + 0.707(e^{−L/2} − e^{−2L/3}) + …], so c_L/B_L tends to a constant near 0.55 (measured 0.50–0.57 for L ≤ 1). The envelope threshold with c_L, T = 2πe^{c_L}, remains doubly exponential in L: the lemma changes the constant in the exponent of Zhu's Theorem 1.4 barrier, not its type, and even that only for a form that has lost positivity. The joint sup s_L is smaller still (0.33 B_L at L = 1) but is not rigorous and suffers the same obstruction.

## 6. Prediction ledger
| prediction | outcome |
|---|---|
| identity ∫cos(at)|F|² = Re⟨f,T_af⟩ | HELD (proved) |
| lemma true and sharp; a ≥ 2L gives 0; complex f included | HELD (proved) |
| C1–C4 controls | HELD (table §2) |
| c_L table (0.4901, 1.6741, 1.6741, 3.130) | HELD |
| joint sup < 0.95 c_L at L = 0.7 | HELD (0.70) |
| perturbation ×0.9 unchanged; ×1.1 = 1.471 | ×0.9 HELD; ×1.1 FAILED (1.124; missed the a > 2L cutoff of log 4) |
| periodic no-boundary control = B_L | HELD |
| R_θ ≤ W valid; T_θ: 119 → 33.6, 2187 → 144 | HELD (33.5 / 143.6) |
| localisation to |t| > T invalid (support destroyed) | HELD (argument §4b) |
| λ_min(R_θ) < 0 for θ ≥ 0.25, both sectors, L = 0.7 | HELD (already at θ = 0.1) |
| s* < c_L − 0.3 (even, L = 0.7) | HELD (0.032) |
| λ_min(R_1) < −0.1 (even, L = 0.7) | HELD (−1.92) |
| λ_min(W) > 1e-3 at L = 0.4 | FAILED even (1.7e-4), HELD odd (1.4e-2) |
| L = 1.0: λ_min(R_1) < 0 | HELD (−3.7 / −4.5); R_0 at L = 1 not computed (budget) |
| lemma not new | HELD as far as checked (Rochberg 1987 context; formula not located) |
| success category "useful inequality with precise limitations" | HELD |

## 7. Complete-form verdict
The truncated-translation lemma is true, sharp and elementary; it halves the arithmetic constant (c_L/B_L ≈ 0.5–0.57) and lowers the envelope threshold by a factor 3.5 at L = 0.7 and 15 at L = 1. Combined with the archimedean term it yields a valid lower bound R_θ ≤ W for every f, but R_θ is negative for every θ > 0 at every L tested, by an amount θ(c_L − s*) with s* ≈ 0 at the minimizer. The improvement acts exactly where the form is not in danger and is absent where it is. This is an obstruction to the attempted combination, precisely established, and not an RH advance. Unaffected: the L = 0.7 certificates (both sectors), whose margins are not threshold artifacts (§4d).

## 8. Plain language
Imagine sliding a picture along a table and asking how much it still overlaps itself; if the table is short, part of the picture falls off the edge every time you slide it, so the overlap can never be perfect — and we worked out exactly the best overlap possible (a cosine of π over one more than the number of slides that fit). That cuts in half the "worst case" the primes could contribute. But when we look at the one wave that comes closest to breaking the rule, the primes barely touch it at all: its score is decided by the other two players, the smooth gamma-function term and the pole term. So a better handle on the primes helps where nothing was wrong and does nothing where it matters. Everything checked here still lives in one small room; the question of every room is untouched.
