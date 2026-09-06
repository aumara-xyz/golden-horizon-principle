# D8 predictions — can confinement limit the arithmetic contribution? (written before compute, 2026-09-06)
Scope: L ∈ {0.4, 0.7, 0.8, 1.0}, authentic prime powers n = p^k ≤ e^{2L}, weights w_n = 2Λ(n)/√n. Unitary Fourier F(t) = (2π)^{-1/2}∫f e^{-ixt}. No zero ordinates, no φ.

## Step 1 (identity) — PREDICTED to hold exactly
For f ∈ L²(ℝ) supported in [−L,L] and (T_a f)(x) = f(x−a): FT of T_a f is e^{−iat}F(t); Plancherel gives ⟨f, T_a f⟩ = ∫ e^{iat}|F|² dt, hence ∫cos(at)|F(t)|² dt = Re⟨f, T_a f⟩. Restriction to [−L,L] changes nothing because f vanishes outside. For real f the imaginary part vanishes automatically.

## Step 2 (single-shift lemma) — PREDICTED: the candidate bound is TRUE and SHARP
Claim: sup_f Re⟨f, T_a f⟩/‖f‖² = cos(π/(N+1)), N = ⌈2L/a⌉, for every a > 0 (value 0 for a ≥ 2L, consistent with N = 1).
Proof sketch to be written out: fibre [−L,L] over x₀ ∈ [−L, −L+a) into chains {x₀ + ja}; a.e. chain has q or q+1 points where 2L/a = q + r; the maximum chain length is N = ⌈2L/a⌉ a.e. (integer ratio: the only (q+1)-point chain is x₀ = −L, measure zero). On each chain Σ_j Re v_j conj(v_{j−1}) = ½ v*A_path v ≤ cos(π/(n+1))‖v‖² (path-graph adjacency eigenvalue 2cos(π/(n+1))); integrate over x₀. Sharpness: long chains have measure ra > 0 (or all chains when r = 0); put the Perron vector of the path on them and 0 elsewhere.
Exact companion identity (PREDICTED): Re⟨f,T_a f⟩ = ‖f‖² − ½‖f − T_a f‖²_{L²(ℝ)}, i.e. ∫(1−cos at)|F|² = ½‖f − T_af‖²_ℝ, the "boundary loss" being the mass pushed outside.
Controls (PREDICTED): (C1) path matrix P_N: numerical top eigenvalue = 2cos(π/(N+1)) to 1e-12 for N ≤ 12; (C2) periodic boundary (circle of length 2L, a | 2L): sup = 1, attained by constants — no loss; (C3) support enlargement at fixed a: N grows, loss 1 − cos(π/(N+1)) ≈ π²/(2N²) → 0; (C4) grid discretization with cell h: top eigenvalue equals the lemma value whenever a/h is an integer, and lies below cos(π/(N+1)) + 1e-9 otherwise.
Prior art (PREDICTED): elementary and almost certainly known in some form (compression of a translation to an interval; Toeplitz operators on Paley–Wiener space with symbol cos(at); discrete Dirichlet Laplacian on a path). NOT claimed new; a search of what is available offline will be recorded.

## Step 3 (prime-power sum) — PREDICTED numbers (hand-computed from the lemma; to be verified)
c_L := Σ_n w_n cos(π/(⌈2L/log n⌉+1)) versus B_L = Σ_n w_n:
| L | prime powers | B_L | c_L (single-shift sum) | c_L/B_L |
|---|---|---|---|---|
| 0.4 | 2 | 0.9803 | 0.4901 | 0.500 |
| 0.7 | 2,3,4 | 2.9420 | 1.6741 | 0.569 |
| 0.8 | 2,3,4 | 2.9420 | 1.6741 | 0.569 |
| 1.0 | 2,3,4,5,7 | 5.8530 | 3.130 | 0.535 |
Joint sup s_L := sup_f Σ_n w_n Re⟨f,T_{log n}f⟩/‖f‖² (finite grid approximation, NOT rigorous): PREDICTED s_L ≤ c_L always (trivially) and s_L < 0.95·c_L at L = 0.7 (different shifts have different extremizers). Grid values are lower bounds on the true sup up to discretization; Legendre-basis values converge slowly because extremizers are discontinuous.
Perturbation control (weights kept, shifts × 0.9 and × 1.1): c_L changes ONLY when a shift crosses a threshold 2L/m (staircase in N); PREDICTED: at L = 0.7, ×0.9 leaves c_L unchanged; ×1.1 changes it (log 2 · 1.1 = 0.7625 → N = ⌈1.836⌉ = 2, factor 0.5 instead of 0.7071), giving 1.471.
No-boundary control (periodic): c_L^{per} = B_L (no gain).

## Step 4 (crucial test) — PREDICTED: the combination is valid but destroys positivity
Valid family (to be derived): for θ ∈ [0,1], R_θ(f) := ∫_ℝ (a(t) − (1−θ)P(t) − θ c_L)|F|² dt + Π(f) ≤ W(f) for all f ∈ L²[−L,L], with exact equality at θ = 0 (R_0 = W), and per-shift weights θ_n allowed. Envelope threshold for R_θ: T_θ = 2π e^{(1−θ)B_L + θ c_L} (approximately; exact: a(T_θ) = (1−θ)B_L + θc_L). PREDICTED T-reduction: L = 0.7: 119 → 33.6 at θ = 1; L = 1.0: 2190 → 144.
Why the improvement cannot be localized to |t| > T: the frequency cutoff f_{>T} is not compactly supported, so the lemma does not apply to it; the only valid use is global (θ-family). PREDICTED obstruction: the minimum of R_θ becomes negative for every θ ≥ 0.25 at L = 0.7 (both sectors) because W's own minimum is ~1e-13 (even) / 5.9e-11 (odd) and the W-minimizer f* does not saturate the shift bounds: PREDICTED saturation s* := Σ w_n Re⟨f*,T_n f*⟩/‖f*‖² < c_L − 0.3 at L = 0.7 (even). PREDICTED λmin(R_1) < −0.1 at L = 0.7 even. At L = 0.4: PREDICTED λmin(W) > 1e-3 (small window, comfortable) and λmin(R_1) sign unknown — this is the one case where the combination might survive; I preregister no direction. L = 1.0: R_1 computable (T = 144); PREDICTED λmin(R_1) < 0; R_0 at L = 1.0 not computed (T = 2190 exceeds budget).
Success category PREDICTED: "a useful inequality whose limitations are precisely established" — the lemma reduces the envelope threshold and gives an exact positive decomposition W = ∫(a − B)|F|² + ½Σ w_n‖f − T_nf‖²_ℝ + Π, but any use that replaces the exact low-frequency prime comb loses more than the certificate's margin.
Scaling (PREDICTED, analytic): B_L ~ 4e^L, c_L/B_L → ≈ 0.5–0.6 as L → ∞ (shifts with log n ∈ (L, 2L] get factor ½), so T_θ=1 = 2πe^{c_L} stays doubly exponential in L: the barrier of Zhu Thm 1.4 is reduced in its constant only.

## Budget
≤ 2 h wall clock; all matrices in double precision (numpy/scipy) except where noted; no new rigorous certificate is produced in this round. Floating minima with |λ| < 1e-12 are reported as sign-unresolved.
