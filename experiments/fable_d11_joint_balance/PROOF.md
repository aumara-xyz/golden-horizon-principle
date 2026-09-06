# D11 — derivations and proof status (Fable, 2026-09-06)
Text proofs feeding ball-arithmetic checks; not proof-assistant certificates. Everything here was derived before reading Codex's schur.py / KERNEL-PROOF.md and then compared (D11.1).

## 1. Position-space form, kernel, pole, atoms (audit of D10 Claim A)
Conventions as in D6 §2 (unitary F, W = ∫Ψ|F|² + Π). The position-space form used by D10 is the one in weil_hidden_modes/PREDICTIONS.md:
 W(f) = Π(f) − (γ + log 4π)‖f‖² + ∫_0^∞ [‖f‖² − e^{u/2} Re g(u)]/sinh u du − Σ_n w_n Re g(log n),  g(u) = ∫ f(x+u) conj(f(x)) dx.
Two-sided kernel: Re g(u) = ½[g(u) + g(−u)] and g(u) = ∫∫ f(y) conj(f(x)) δ(y − x − u), so −∫_0^∞ e^{u/2} Re g(u)/sinh u du = ∫∫ conj(f(x)) k(x−y) f(y) with k(r) = −e^{|r|/2}/(2 sinh|r|): the ½ is exactly the symmetrization. Pole: Π = 2|∫f cosh(x/2)|² − 2|∫f sinh(x/2)|² = 2∫∫ f(x) conj(f(y)) [cosh(x/2)cosh(y/2) − sinh(x/2)sinh(y/2)] = 2∫∫ f conj(f) cosh((x−y)/2): kernel 2cosh(r/2). Prime atoms: −(w_n/2)[δ(y−x−log n) + δ(y−x+log n)]. Hence off the atoms and the diagonal,
 K(r) = 2cosh(r/2) − e^{r/2}/(2 sinh r) = (q + 1)/√q − q^{3/2}/(q² − 1) = (q³ − q − 1)/(√q (q² − 1)),  q = e^r > 1.
Check: q = 5/4 gives numerator −19/64, denominator (√5/2)(9/16) = 9√5/32, K = −19/(18√5); q = 25/16 gives numerator 5129/4096, denominator (5/4)(369/256) = 1845/1024, K = 5129/7380. Both agree with D10. Sign change at ρ³ − ρ − 1 = 0 (numerator increasing for q > 1). Constant: ∫_0^∞ (1 − e^{u/2})/sinh u du = ψ(¼) − ψ(½) = −π/2 − log 2 (expand 1/sinh u = 2Σ e^{−(2m+1)u}; each difference integral is elementary; monotone convergence after a sign change), so the scalar left after the jump-square rewrite is −(γ + log 4π) − π/2 − log 2 = ψ(¼) − log π = a₀ = a(0). Prime constant −B with B = Σ_n w_n over visible prime powers only. All of D10's Claim A identities reproduce. MEASURED (hand + this text).
Sharp-threshold corollary: for L > r*/2, r* = log ρ, pick d ∈ (r*/2, min(L, r*)); 2r* = 0.5624 < log 2 so no atom; signs (−,−,+). For L ≤ r*/2 every separation is ≤ r*: K ≤ 0, equality only at the two endpoints. Correct as stated.
The a.e.-gauge extension, which KERNEL-PROOF.md asserts without a written argument (my preregistered "most fragile" item): let φ be measurable with φ ≠ 0 a.e. and suppose φ(x) conj(φ(y)) K(|x−y|) is real and ≤ 0 for a.e. (x, y) ∈ ∪ I_i × I_j (i ≠ j). By Fubini the set of triples (x₁, x₂, x₃) ∈ I₁×I₂×I₃ for which all three pairs satisfy this has full measure. For such a triple the cyclic product [φ₁conj φ₂ K₁₂][φ₂ conj φ₃ K₂₃][φ₃ conj φ₁ K₃₁] = |φ₁φ₂φ₃|² K₁₂K₂₃K₃₁ is > 0 since the signs are (−,−,+), yet it is a product of three real nonpositive numbers, hence ≤ 0. Contradiction; the extension holds. Repaired, not refuted.

## 2. Pole axis and Schur identity (audit of Claim B)
p ≠ 0, q = p/‖p‖, v = q + e₀, U = 2vvᵀ/(vᵀv) − I. U is symmetric and Uᵀ U = I because (2vvᵀ/vᵀv)² = 2·2vvᵀ/vᵀv; Ue₀ = 2v(v₀)/(vᵀv) − e₀ with v₀ = q₀ + 1 and vᵀv = 2(1 + q₀), so Ue₀ = v − e₀ = q (needs q₀ ≠ −1; here q₀ > 0). For f = U(t, g): pᵀf = ‖p‖ qᵀU(t,g) = ‖p‖ e₀ᵀ(t, g) = ‖p‖t (using Uᵀq = e₀). With UᵀHU = [[a, bᵀ],[b, C]]:
 fᵀ(H + κppᵀ)f = a t² + 2t bᵀg + gᵀCg + κ‖p‖² t² = (g + tC⁻¹b)ᵀC(g + tC⁻¹b) + [a + κ‖p‖² − bᵀC⁻¹b] t²  (C ≻ 0).
So R_κ ≻ 0 ⇔ C ≻ 0 and σ := a + κ‖p‖² − bᵀC⁻¹b > 0 (necessity: put t = 1, g = −C⁻¹b). Matches D10.

## 3. Residual bracket (D11.2), proved
For C ≻ 0 and any x: q − (2bᵀx − xᵀCx) = bᵀC⁻¹b − 2bᵀx + xᵀCx = (x − C⁻¹b)ᵀC(x − C⁻¹b) = rᵀC⁻¹r with r = b − Cx. Hence F(x) := 2bᵀx − xᵀCx ≤ q, and if C ⪰ δI then rᵀC⁻¹r ≤ ‖r‖²/δ, so q ≤ F(x) + ‖r‖²/δ. Therefore
 σ ∈ [a + κ‖p‖² − F(x) − ‖r‖²/δ,  a + κ‖p‖² − F(x)].
The upper endpoint is exactly the score of the vector U(1, −x) in the original coordinates (put t = 1, g = −x in §2 with the residual retained), so an upper endpoint < 0 is a finite negative witness that can be scored directly; a lower endpoint > 0 certifies σ > 0 given C ⪰ δI. A Krylov/Gauss value F alone is a LOWER bound on q, i.e. only an upper bound on σ; it cannot certify positivity. ‖r‖ is bounded above by √(Σ (abs upper of r_i)²) to avoid interval squares straddling zero.

## 4. δ certificate (my lemma, from D4/D6)
For any real V with λmin(VᵀV) ≥ g_l > 0 (Gershgorin), V is invertible; if D = VᵀCV has Gershgorin lower bound d_min > 0 then for y = Vx: yᵀCy = xᵀDx ≥ d_min‖x‖² ≥ d_min‖y‖²/λmax(VᵀV) ≥ (d_min/g_u)‖y‖². So C ⪰ δI with δ = d_min/g_u. V is the frozen 60-digit mpmath eigenbasis of the midpoint; the bound is rigorous for the balls of V actually used. Refusal when d_min ≤ 0 is not resolved; a certified negative Gershgorin interval reports indefiniteness. Cost: one 79×79 eigensolve at 60 digits plus three 79³ ball products (≈ 4–8 s per family). This is a FULL-SIZE verifier; any success below is "compressed response construction", not a short complete certificate.

## 5. Quadrature-error hypotheses (for MY H, independent of D10's Opus-built H)
My builder (d5_certify.py machinery): unit panels on [0, 120], K = 48 Gauss nodes, Bernstein ellipse ρ = 2 with semi-minor axis 0.375 < 0.5 (nearest digamma pole), so the integrand (a − P − β)·F_m F_n is analytic on the ellipse: F_n entire (spherical Bessel), P entire, a analytic for |Im t| < ½. Error per panel ≤ (64/15)·h·M_ρ·ρ^{−2K}/(ρ² − 1) (Trefethen ATAP Thm 19.3, cited; Opus's independently derived constant 8Mρ/((ρ−1)ρ^{2K}) is 11× more conservative and would also close), with M_ρ ≤ (box bound of |a − P − β| via ψ(s) = ψ(s+1) − 1/s)·|c_m||c_n| e^{2bL} using |j_n(z)| ≤ e^{|Im z|} (Poisson integral, DLMF 10.54.2). Nodes/weights are Arb's rigorous Legendre-root enclosures. Radii ≈ 1.2e-22 versus D10/Opus 1.4e-25. UNVERIFIED citation status of the Trefethen constant remains as in D7 and does not affect the verdict (Opus's constant suffices).

## 6. Infinite discarded-block and coupling bounds
Not needed for any finite R_120 statement in D10 or D11. They are needed only to pass from the 80-mode block to all f ∈ L²[−L, L] (D4/D6/D7: ε_D, ε_C, ε_p with the Schur 2×2 argument). Scoped accordingly: nothing in D11 changes the all-function statement, and nothing in D11 says anything about other L.

## 7. Krylov recipe (frozen in PREDICTIONS.md)
Lanczos on the midpoint matrix C_mid with start vector b_mid, full double reorthogonalization, m steps, Galerkin (CG-equivalent) solve T_m y = Q_mᵀ b_mid (m-dimensional), x_m = Q_m y, frozen as 60-digit decimals. No preconditioner. No full inverse, no eigenvectors, no adaptation to σ enter x_m. A full-size solve appears only in the labeled FULL_SOLVE_DIAGNOSTIC row.
