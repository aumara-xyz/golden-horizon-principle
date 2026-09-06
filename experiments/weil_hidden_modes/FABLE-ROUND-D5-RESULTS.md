# Fable round D5 — results (2026-09-06)
Predictions: FABLE-PREDICTIONS-D5.md (commit 9c6a093, before compute). Code: d5_certify.py (parity-aware copy of d4_certify_v2.py), d5_dilation.py. Outputs: d5_results_*.json, d5_run_*.log, d5_dilation_results.json. Codex's files untouched. Committed locally, not pushed. No zeta-zero ordinates anywhere. No φ.

## 1. Certificate verdicts (L = 0.7, T♯ = 120, 80 Legendre modes per sector, 192-bit balls)

| sector | pole term | λ₀ = certified λmin(A) | ε_C | ε_D | ε_p | ‖pole vec‖ | max entry radius | checker |
|---|---|---|---|---|---|---|---|---|
| even (rerun of run 4 + invertibility) | +2C² | 1.03101776e-13 | 3.89e-16 | 3.05e-38 | 2.4e-406 | 1.2077 | 1.16e-22 | ACCEPT, margin 1.031e-13 |
| odd | −2S² (derived) | 5.85907085e-11 | 9.53e-17 | 3.05e-38 | ~1e-406 | 0.2420 | 1.17e-22 | ACCEPT, margin 5.859e-11 |
| odd, MUTATION pole sign flipped (+2S²) | wrong sign | 1.7188e-6 | same | same | same | same | same | ACCEPT (meaningless; control only) |

Statement certified (MEASURED): for every real f ∈ L²[−0.7, 0.7] of either parity, R_T(f) ≥ λ_sector·‖f‖² with λ_even = 1.03e-13, λ_odd = 5.86e-11 (Schur lower bounds on the full spectrum: λ₀ − off²/(d_low − λ₀), i.e. the same numbers minus < 1e-26). Because W(f1 + i f2) = W(f1) + W(f2) and the parity sectors decouple for real f (§2), this covers every complex f ∈ L²[−0.7, 0.7] with constant 1.03e-13, conditional on the analytic identity W ≥ R_T of §2.
Checker: d4_checker.py, unchanged (5/5 tests). Checker inputs are all interval upper bounds. Interval LDL (Codex's ldl) remains UNVERIFIED at every shift for all three matrices (cond ≈ 1e14); certification is by the eigenbasis bound of §3.

### 1a. The pole term in the odd sector (derived, not assumed)
For real f, the pole contribution is 2·(∫f e^{x/2}dx)(∫f e^{−x/2}dx) (Codex's `pole(i,½)·pole(j,−½)` symmetrized is the same quantity in the sine basis). With f = f_e + f_o: ∫f e^{±x/2} = C ± S, C = ∫f_e cosh(x/2), S = ∫f_o sinh(x/2). Hence pole = 2C² − 2S². The odd-sector pole term is −2S² ≤ 0: it is not zero, and it lowers the form. The mutation confirms it is load-bearing: flipping its sign raises λ₀ from 5.9e-11 to 1.7e-6 (factor 2.9e4; predicted "> factor 10": HELD).
Pole-vector tail for odd n: s_n = ∫q_n sinh(x/2) = √((2n+1)/(2L))·2L·i_n(L/2), |i_n(y)| ≤ y^n/(2n+1)!!·e^{y²/(2(2n+3))}; the discarded block is ≥ (β* − ε_D − 2‖s_D‖²)I and the coupling ≤ ε_C + 2‖s_N‖‖s_D‖ exactly as in the even case (the sign of −2ssᵀ does not enter a norm bound).

## 2. Even/odd derivation: exact form vs lower envelope (where equality holds)
Conventions. f real, supp f ⊂ [−L, L], f ∈ L²; F(t) = (2π)^{−1/2}∫f(x)e^{−ixt}dx (unitary: ‖F‖_{L²(ℝ)} = ‖f‖). Even f ⇒ F real even; odd f ⇒ F imaginary odd.
Exact frequency form (EQUALITY, for every such f): W(f) = ∫_ℝ Ψ(t)|F(t)|² dt + 2(∫f e^{x/2})(∫f e^{−x/2}), with Ψ(t) = Re ψ(¼ + it/2) − log π − Σ_{p^k ≤ e^{2L}} (2 log p / p^{k/2}) cos(t·k log p). At L = 0.7 the prime-power sum has exactly the three terms 2, 3, 4. This is the Weil explicit formula written for the autocorrelation g = f ⋆ f̃ (ĝ = |F|² on ℝ, ĝ(±i/2) = f̂(±i/2)f̂(∓i/2)), the archimedean term as the digamma symbol, the prime terms as multiplication by cosines in t. Status: standard analysis (Weil; Zhu 2608.24827 §2), matched numerically against Codex's sine-basis W in D2; NOT interval-checked in this round. Everything below is conditional on it.
Lower envelope (INEQUALITY): with β* = a(T♯) − B, a(t) = Re ψ(¼ + it/2) − log π,
 W(f) = R_T(f) + ∫_{|t|>T♯} (Ψ(t) − β*)|F(t)|² dt,  R_T(f) := ∫_{|t|≤T♯}(Ψ − β*)|F|² + β*‖f‖² + pole.
The dropped integral is ≥ 0 because Ψ(t) ≥ a(t) − B ≥ a(T♯) − B = β* for |t| ≥ T♯, using (i) |prime comb| ≤ B = Σ weights and (ii) a is increasing on t > 0: d/dt Re ψ(¼ + it/2) = −½ Im ψ′(¼ + it/2) and Im ψ′(σ + it) = −Σ_k 2(σ+k)t/|σ+k+it|⁴ < 0 for t > 0. So W ≥ R_T on all of L²[−L, L]; equality only if F vanishes on |t| > T♯, impossible for nonzero compactly supported f, so the inequality is strict but the gap is not estimated. The certificate is a statement about R_T; the numbers λ_sector are lower bounds for W by this inequality.
Parity decoupling (real f): ∫Ψ F_e conj(F_o) is the integral of an odd function = 0; pole = 2C² − 2S² has no cross term. Complex f = f1 + i f2: |F|² = |F1|² + |F2|², and the pole cross term is i·(f̂2(i/2)f̂1(−i/2) − f̂1(i/2)f̂2(−i/2)), purely imaginary, so it drops from the (real) form. Hence W(f) = W(f1) + W(f2) and the two real parity certificates cover all complex f.

## 3. The eigenbasis certificate, made explicit (addresses "congruence preserves inertia, not eigenvalues")
Let V be any real matrix (here mpmath eigsy at 60 digits, cast to balls), B = VᵀAV computed in ball arithmetic. Congruence preserves only inertia, so B ≻ 0 ⇔ A ≻ 0 needs V invertible, and a numerical lower bound needs V's norm. Both are certified:
 (a) invertibility: λmin(VᵀV) ≥ min_i (VᵀV_ii − Σ_{j≠i}|VᵀV_ij|) = 1 − 3e-25 > 0 (Gershgorin, balls);
 (b) conversion: for y = Vx, yᵀAy = xᵀBx ≥ λmin(B)‖x‖² and ‖y‖² ≤ λmax(VᵀV)‖x‖², so λmin(A) ≥ λmin(B)/λmax(VᵀV) with λmax(VᵀV) ≤ 1 + 1e-24 (Gershgorin upper). λmin(B) ≥ min Gershgorin row bound of B; off-diagonals of B are ≤ 2.1e-21.
Result: λmin(A) ≥ Gersh_min(B)/λmax(VᵀV), rigorous for the ball-valued V actually used. This replaces the preregistered interval LDL, which cannot resolve a 1e-13 pivot through 1e-22 radii at condition number 1e14 (kept as UNVERIFIED in every JSON).

## 4. Two-observer test: Halmos dilation (established mathematics, reproduced)
U = [[A, D_{A*}],[D_A, −A*]], D_A = (I − A*A)^{1/2}, D_{A*} = (I − AA*)^{1/2}. Unitarity: U*U has blocks A*A + D_A² = I, D_{A*}² + AA* = I, and off-diagonal A*D_{A*} − D_A A* = 0 by the intertwining relation A D_A = D_{A*} A (true for polynomials in A*A, hence for the square root by continuity). Halmos 1950 (from memory, UNVERIFIED citation).

| case | ‖A‖ | eig(A) | max |Im eig A| | eig(A) inside disk | eig(U) on circle | U*U − I | ‖PU²P − A²‖ | ‖PU³P − A³‖ |
|---|---|---|---|---|---|---|---|---|
| control: diag(0.5, −0.3) | 0.5 | 0.5, −0.3 (real) | 0 | yes | yes (to 1.6e-16) | 1.6e-16 | 1.179 (PU²P = I exactly) | 0.464 |
| mutation: [[0.5,0.6],[−0.3,0.4]] (nonnormal 0.40) | 0.79 | 0.45 ± 0.421i | 0.421 | yes (|λ| = 0.616) | yes (5.7e-16) | 5.7e-16 | 0.806 | 1.141 |
| mutation 3×3 (nonnormal 0.71) | 0.88 | 0.144 ± 0.655i, 0.311 | 0.655 | yes | yes (2.6e-15) | 2.6e-15 | 1.073 | 1.358 |

Preregistered question — does completing a lossy subsystem into a norm-preserving whole force the subsystem's resonances onto the real line or the unit circle? Answer: NO (PREDICTED no: HELD). The subsystem block of U is A itself; its eigenvalues (0.45 ± 0.42i) are unchanged, strictly inside the disk, off the real axis, while every eigenvalue of U has modulus 1. Unitarity of the whole constrains the whole's spectrum, not the block's.
One-step vs repeated evolution: the upper-left block of U² is A² + D_{A*}D_A (identity checked to 1e-16 in all cases), not A²; for the diagonal control it is exactly I. So the Halmos U is a one-step dilation only. Power dilations (PUⁿP = Aⁿ for all n) exist in infinite dimension (Sz.-Nagy) and for any fixed finite horizon N in dimension (N+1)·dim (Egerváry) — cited from memory, UNVERIFIED, not used.

## 5. What this buys, and what it cannot buy (the missing bridge)
Establishes: "information leaving one observer" can always be modelled as the compression of a unitary on a larger space; this is a theorem about contractions, not about any physical channel. The resonances of the open subsystem are the eigenvalues of the contraction and are not moved by the completion. So an argument of the form "the universe is unitary, therefore the observer's resonances are real / on a line" is false as stated: the toy is a counterexample.
Does NOT establish anything about RH. A zeta connection would need, in addition: (1) a specific operator built without zero ordinates whose construction is forced by an equation, not chosen to fit; (2) domain and self-adjointness (or unitarity) properties proved, not assumed — the dilation shows unitarity of an ambient space says nothing about the block; (3) an exact spectral identity: the resonances/eigenvalues equal the nontrivial zeros with correct multiplicities, none missing, none extra — the Weil form above is the only place in this directory where "all zeros with multiplicity" enters, and it enters as a positivity criterion, not as a spectrum. Nothing in §4 satisfies (1)–(3). φ was not required by any equation here and was not inserted. No identification with Hawking radiation or quantum foam is made.

## 6. Prediction ledger
| prediction (FABLE-PREDICTIONS-D5.md) | outcome |
|---|---|
| odd λ₀ ∈ [1.0e-10, 3.4e-10] | FAILED: 5.86e-11. Wrong by factor 1.7 below the range; 80 Legendre modes go lower than Codex's 32 sine modes (3.31e-10), consistent but my interval was too narrow. Kept. |
| odd ε_C < 1e-15, ε_D < 1e-30, ε_p < 1e-300 | HELD (9.5e-17, 3.1e-38, ~1e-406) |
| odd verdict ACCEPT, margin ≈ λ₀ | HELD |
| pole-sign mutation changes λ₀ by > factor 10 | HELD (factor 2.9e4) |
| even rerun unchanged with invertibility certified | HELD (1.03101776e-13; λmin(VᵀV) ≥ 1 − 3e-25) |
| U unitary to 1e-14, eig(A) unchanged, eig(U) on circle | HELD |
| ‖PU²P − A²‖ > 0.1 for control and mutation; control gives PU²P = I | HELD (1.179 = ‖I − A²‖; 0.806; 1.073) |
Earlier rounds' failures (D4 runs 1, 2, 3, 4a; the D2 all-functions overclaim; the non-alignment target; Lee–Yang) remain in FABLE-AUDIT.md.

## 7. Established / reproduced / possibly new
Established mathematics (not mine): Weil explicit formula and positivity criterion; the frequency-envelope reduction (Zhu 2608.24827, whose Theorem covers L = 0.8, both parities, bound 8.9e-18); Halmos dilation; Sz.-Nagy/Egerváry power dilations; Gershgorin; Trefethen's Bernstein-ellipse quadrature bound.
Reproduced here: compact-window Weil positivity at the smaller window L = 0.7 with explicit constants (even 1.03e-13, odd 5.86e-11) by an independent implementation, tails bounded, all failures on record. Codex's 16- and 32-mode certificates agree with these to the extent the spans overlap.
Possibly new: nothing claimed. The only candidates — the exact-polynomial Bessel evaluation and the strip bound as a quadrature error device — are engineering, and the compact-window statement is weaker than Zhu's. Prior-work check was limited to Zhu v2 and Codex's files; no literature search beyond that.

## 8. For an eight-year-old
Imagine a room with a mirror on each wall, and you can make any ripple you like in it, even ripples too wiggly to draw. Every ripple gets a score, and the big question needs every score to be at least zero. Last time we could only promise that for ripples that look the same in both mirrors. This time we also promised it for the upside-down ones, where one mirror shows a hill and the other a valley — and we found those ripples have a hidden weight pulling their score down (the minus sign), which we had to measure instead of guessing. Both kinds pass in this one small room, by a tiny but real margin. Then we played a different game: if a leaky bucket is put inside a bigger bucket that never leaks, do the leaky bucket's wobbles have to become perfect? No. The big bucket is perfect, the small one still wobbles exactly the way it did. So "the whole thing is perfect" does not fix the part. That's what we learned, and it is not the answer to the big question — it only tells us which doors are locked.
