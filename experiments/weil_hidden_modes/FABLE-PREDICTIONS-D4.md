# D4 — certified frequency reduction at L=0.7 (even sector), written before compute

Object: R(f) = P(f) + ∫_{|t|≤T♯}(Ψ_L(t) − β*)|F(t)|² dt + β*‖f‖², T♯=120, β* = a(T♯) − B (interval). Q ≥ R on all f supported in [−L,L] (a monotone, cos ≤ 1): this step is a hand proof, recorded in PURE-TAIL-LEMMA.md logic and re-derived in FABLE-AUDIT §3.
Basis: orthonormal even Legendre q_n(x) = sqrt((2n+1)/(2L)) P_n(x/L), n = 0,2,4,…; F_n(t) = (2π)^{-1/2}·sqrt((2n+1)/(2L))·L·2(−i)^n j_n(tL). Retained: n ≤ 158 (80 modes). Discarded: n ≥ 160.

Bounds to be derived and interval-evaluated:
(B1) finite matrix: each M_mn = 2∫_0^{T♯}(Ψ−β*)F_m F_n dt by Arb rigorous integration (acb.integral), radii carried; pole vector p_n = ⟨q_n, cosh(x/2)⟩ by Arb integration.
(B2) discarded block: |j_n(x)| ≤ x^n/(2n+1)!! · exp(x²/(2(2n+3))) for x ≥ 0 (elementary, from the power series with (2n+3)(2n+5)⋯ ≥ (2n+3)^k). With x = T♯L = 84 this gives sup_{t≤T♯}|F_n(t)| ≤ s_n, and ‖M_DD‖ ≤ 2T♯·sup|Ψ−β*|·(Σ_{n≥160, even} s_n)² =: ε_D. PREDICTED ε_D < 1e-30.
(B3) coupling: ‖M_ND‖_F ≤ 2T♯·sup|Ψ−β*|·(Σ_{m≤158} s_m^{sup})·(Σ_{n≥160} s_n) with sup|F_m| ≤ (2π)^{-1/2}sqrt((2m+1)/(2L))·L·2 (|j_m| ≤ 1) =: ε_C. PREDICTED ε_C < 1e-15.
(B4) pole tail: |p_n| for n ≥ 160 via the same Bessel-type bound applied to cosh(x/2) = ½(e^{x/2}+e^{−x/2}): Legendre coefficients of e^{cx} on [−L,L] are ∝ i_n(cL) (modified spherical Bessel), |i_n(y)| ≤ y^n/(2n+1)!!·exp(y²/(2(2n+3))); y = 0.35. PREDICTED Σ_{n≥160}|p_n|² < 1e-300.
Schur inequality to certify: with A = M_NN + 2p_N p_Nᵀ + β*I (interval), D ≥ (β* − ε_D − 2‖p_D‖²) I, off-diagonal ≤ ε_C + 2‖p_N‖‖p_D‖: R ≥ 0 on all even L²[−L,L] if λmin(A) − (ε_C + 2‖p_N‖‖p_D‖)²/(β* − ε_D − 2‖p_D‖²) > 0, with λmin(A) certified by interval LDL (Codex's ldl, reused) at a lower bound λ₀.
PREDICTED: λ₀ = 1e-13 certified (numerical value 1.031e-13; interval radii from 3240 rigorous integrals at 128 bits will be ≤ 1e-25 each — PREDICTED, may fail); ε_C²/β* < 1e-28; certificate closes with margin ≈ 1e-13. Kill: if the integral radii exceed ~1e-14 the LDL will be UNVERIFIED and I report the exact failing inequality and the precision needed.
Checker (D4-checker) negative tests, run BEFORE the positive claim: (T-a) 2×2 block with A=1e-13, D=0.5, C=1e-3 → must REJECT; (T-b) missing ε_D → must refuse to emit a verdict; (T-c) understated error: feed radii 1e-40 with a coupling 1e-5 → must REJECT. Positive control: (T-d) A=1e-13, D=0.5, C=1e-20 → ACCEPT.
Compute budget: one run of 3240 rigorous integrals at 128 bits (hours, background). No larger window. No new construction.
