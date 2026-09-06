# D6 predictions — certificate hardening at L=0.7. Written before compute. No new constructions.

## D6.1 analytic repair (to be derived in the results doc; predictions about what the derivation will show)
- The pointwise identity |F1+iF2|² = |F1|²+|F2|² in D5 §2 is FALSE; the cross term is −2 Im(conj(F1)F2)(t), an odd function of t when f1, f2 are real, so its integral against the even weight Ψ vanishes. Integrated identity survives.
- Complex pole term: for g = f ⋆ f̃ with f̃(x) = conj(f(−x)), ĝ(ξ) = f̂(ξ)·conj(f̂(ξ̄)); pole = ĝ(i/2)+ĝ(−i/2) = 2 Re[f̂(i/2) conj(f̂(−i/2))]. With f = f1 + i f2 it equals pole(f1)+pole(f2); the naive non-Hermitian 2 f̂(i/2) f̂(−i/2) differs for complex f. Parity certificates still cover all complex f.
- Domain: W is finite exactly when ∫|F|² log(2+|t|) dt < ∞; on all of L²[−L,L] W is well defined in (−∞, +∞] because Ψ is bounded below (Ψ ≥ a(0) − B); R_T is a bounded form on all of L². The certified inequality W ≥ R_T ≥ λ‖f‖² holds on all of L² in the extended sense; the identification of W with the sum over zeros is only used on the classical explicit-formula class (e.g. f piecewise C¹, or C_c^∞), and is not needed for the positivity statement.

## D6.2 constants (rounded DOWN; rigorous endpoints from the ball strings, which enclose the computed balls)
- even: λ₀ lower endpoint 1.0310177602e-13 − 9.4e-26; Schur correction off²/(d_low − λ₀) ≈ 2.0e-29; advertised W ≥ 1.031e-13 ‖f‖² is VALID (1.031e-13 < endpoint).
- odd: λ₀ lower endpoint 5.8590708532e-11 − 5.3e-24; correction ≈ 1.2e-30; advertised 5.86e-11 is INVALID (upward rounding, as the directive says); corrected advertised constant 5.859e-11.
- The invertibility and norm-conversion steps re-derive unchanged; quadrature and tail bounds unchanged. PREDICTED: no constant changes beyond the odd rounding.

## D6.3 adversarial tests (d6_tests.py, d6_checker.py; d4_checker.py unchanged)
T1 complex identity: f1 = q_0, f2 = q_1 (Legendre), t = 1: |F1+iF2|² − |F1|² − |F2|² ≠ 0 (PREDICTED |·| > 1e-3); ∫_{−T}^{T} Ψ·(cross term) dt = 0 to ball precision (PREDICTED |·| < 1e-25 in balls); Hermitian pole for f1 + i f2 equals pole(f1)+pole(f2) (< 1e-25) and the naive product formula differs (PREDICTED |diff| > 1e-3).
T2 endpoint checker: claimed 5.86e-11 against certified lower endpoint → REJECT; claimed 5.859e-11 → ACCEPT; claimed 1.031e-13 (even) → ACCEPT; claimed 1.032e-13 → REJECT.
T3 d4_checker.py five tests → 5/5 unchanged.
T4 same quadratic form, different method and basis: Codex's 'authentic' W entries (sine basis f_j = sin(jπ(x+L)/(2L))/√L, position-space Arb integrals, 384 bits) versus my frequency-space evaluation ∫Ψ F_i F_j + pole_ij in mpmath (30 digits, closed-form sine transforms, integral to T_b = 2·10⁴ plus an analytic tail estimate). PREDICTED: |difference| < 1e-9 for (1,1),(1,3),(2,2),(3,3),(2,4),(4,4); (1,2) = 0 exactly by parity. This is a same-form test; it is NOT a comparison of minima over different subspaces.
T5 independent floating evaluation of my Legendre entries with mpmath (its own Bessel and digamma, tanh-sinh quadrature): (0,0),(0,2),(20,40) even and (1,1),(1,3) odd. PREDICTED: within 1e-15 of the certified ball centres (ball radii 1.2e-22).
T6 numerical sanity of the two analytic lemmas used in the quadrature bound: |j_n(x+iy)| ≤ e^{|y|} at 200 random points (n ≤ 158, |x| ≤ 90, |y| ≤ 0.3) — PREDICTED no violation; ∫_{−1}^{1} e^{zs}P_n(s)ds = 2 i_n(z) at 20 points — PREDICTED agreement to 1e-25.
Kill conditions: any T4 difference > 1e-9 means my form and Codex's are not the same form (normalization error somewhere) and the certificate's connection to Codex's W is VOID until resolved; any T5 miss > 1e-12 means a quadrature or Bessel error in the certificate.

## D6.4 predicted verdict
"Certificate survives with corrected exposition (odd advertised constant re-rounded to 5.859e-11)". Remaining analytic obligations will be listed, not closed.
