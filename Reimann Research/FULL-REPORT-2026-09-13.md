# Compact-window Weil positivity: full report of the Golden Horizon Principle Riemann lab (rounds D1–D23)

Fable (Claude), 2026-09-13, for Peter Viviani. Branch `codex/metatron-prime-return-v0` of https://github.com/aumara-xyz/golden-horizon-principle. Every claim below carries one of four labels: **MEASURED** (interval-certified, or exact finite arithmetic), **MEASURED (floating)** (double-precision numerics with preregistered predictions and controls, not a certificate), **UNVERIFIED** (stated, not proved or not certified), **VOID** (tested and killed). There is no fifth label. Nothing in this document is a result about the Riemann Hypothesis itself; see §1.

## 1. The problem, and exactly what this lab did and did not do

The Riemann Hypothesis (RH) is equivalent (Weil, 1952) to the positivity of a quadratic form: for every nice test function f, a certain number W(f), built from f's Fourier transform, the Gamma function, and the primes, must be nonnegative. Positivity for ALL f, for functions supported in ALL intervals [−L, L], is RH. Positivity for functions supported in ONE fixed interval is a finite, checkable statement that RH implies and that says nothing about RH in return.

This lab proved and audited positivity for one interval (L = 0.7), built certified lower bounds for four intervals (L = 0.4 to 0.7), and measured in detail how the form behaves as the interval grows. It did not prove anything about other intervals and has no candidate for the argument that would. The only rigorous "outside" fact used for orientation: RH is a Π₁ statement, so if it were unprovable it would be true; the difficulty is entirely on the proof side.

Prior art that bounds this work: Yoshida, and Connes–Consani (Selecta 2021), prove positivity structurally for L ≤ (log 2)/2 = 0.3466, the largest interval in which no prime term appears. Zhu (arXiv 2608.24827, Sept 2026) proves positivity by computer-assisted envelope reduction for L = 0.8 with bound 8.9e-18. Everything here is at or below Zhu's window.

## 2. The discipline (why the numbers can be trusted as far as they go)

Predictions committed to git before any computation; every match paired with a control or mutation that would kill it; wrong predictions kept in the record; no zeta-zero ordinates in any construction, parameter, or window choice; three AI systems (Fable/Claude, Codex, Opus; later Astra) auditing each other; corrections appended with dates, never edited in place; everything pushed to the research branch. Two independent implementations of the certificate (Fable, Opus) agree to 20 digits; Codex's earlier position-space certificate agrees with Fable's frequency-space evaluation on identical functions to 1e-11.

## 3. The exact form (conventions, so the corpus is self-contained)

L = 7/10 unless stated. f ∈ L²([−L, L]; ℂ), extended by zero. Unitary Fourier transform F(t) = (2π)^{−1/2}∫f(x)e^{−ixt}dx. Archimedean symbol a(t) = Re ψ(¼ + it/2) − log π (ψ the digamma function). Prime symbol P(t) = Σ_{n = p^k ≤ e^{2L}} (2 log p/p^{k/2}) cos(t log n); at L = 0.7 the visible prime powers are 2, 3, 4. Ψ = a − P. Pole term Π(f) = 2 Re[f̂(i/2)·conj(f̂(−i/2))] with f̂(±i/2) = ∫f(x)e^{±x/2}dx; for real f = f_even + f_odd this is 2C² − 2S², C = ∫f cosh(x/2), S = ∫f sinh(x/2). Exact Weil form: W(f) = ∫_ℝ Ψ(t)|F(t)|² dt + Π(f), finite exactly when ∫|F|² log(2+|t|) < ∞, extended-valued (+∞) otherwise. Lower-envelope form used for certificates: R_T(f) = ∫_{|t|≤T}(Ψ − β)|F|² + β‖f‖² + Π, β = a(T) − B, B = Σ prime weights; W − R_T = ∫_{|t|>T}(Ψ − β)|F|² ≥ 0 because a is increasing and |P| ≤ B. Parity sectors decouple; complex f = f1 + i f2 gives W(f) = W(f1) + W(f2) after the cross term is shown to integrate to zero (D6; the pointwise identity claimed in D5 was false and was corrected). Dirichlet variant: a_χ(t) = Re ψ(¼ + a/2 + it/2) − log π, plus log q, weights χ(n)·2Λ(n)/√n, no pole.

## 4. Certified results (MEASURED, interval arithmetic)

| statement | value | where |
|---|---|---|
| For all f ∈ L²([−0.7, 0.7]; ℂ): R₁₂₀(f) ≥ λ‖f‖², hence W(f) ≥ λ‖f‖² | λ_even = 1.031e-13, λ_odd = 5.859e-11 (rounded down from certified endpoints 1.03101776e-13, 5.85907085e-11) | D4–D7 (Fable), independently rebuilt by Opus (D7) with agreement to 20 digits |
| Certified lower bounds at other rooms (T = 160, 160 modes per parity) | L = 0.40: 1.449e-4 / 1.240e-2; 0.50: 7.148e-7 / 1.421e-4; 0.60: 1.101e-9 / 4.129e-7; 0.70: 2.672e-13 / 1.586e-10 (even / odd) | D22 |
| L = 0.70 at T = 240, 192 modes | 3.376e-13 / 2.033e-10 | D22 |
| Negative witnesses for mutated forms (exact scores with complete tails, ζ, L = 0.7): removing prime 2, or removing all primes, gives W < 0 on explicit frozen waves in both parities | e.g. prime-free odd W ≈ −0.7; delete-2 odd W = −0.489 ± 6e-4 | D9 (Codex), D21 |
| Frozen-wave sandwiches of the minimum at L = 0.7 | relative width 2.34e-11 (even), 5.75e-14 (odd) | D7 (Opus), corrected widths D8 §0 |
| Truncated-translation lemma: Re⟨f, T_a f⟩ ≤ cos(π/(⌈2L/a⌉+1))‖f‖², sharp | proved (text proof), controls exact | D8 |
| Observer-code tomography (side lane, not RH): 3-axis line sums of a 3×3×3 ternary cube have an 8-dimensional ghost space over GF(3); adding six face-diagonal families makes the 81-sum code injective | exact | D18 |

Method notes that matter for reuse: Arb's `bessel_j` on wide complex balls returns useless enclosures (width ~1e19); use elementary Bessel forms and a hand-built Gauss–Legendre quadrature with a Bernstein-ellipse error bound. Interval LDL cannot certify a 1e-13 eigenvalue at condition number 1e14; use the eigenbasis Gershgorin bound λmin(A) ≥ Gersh_min(VᵀAV)/λmax(VᵀV) with V's invertibility certified. Positivity of the finite block plus three tail bounds (discarded block, coupling, pole tail) combine by a 2×2 Schur inequality to cover all of L².

## 5. The measured map (MEASURED (floating) unless noted; all preregistered, controls passed, failures listed in §6)

1. **Where the primes become load-bearing (D12).** The prime-free form (Gamma + pole) stays positive only to L ≈ 0.370 (odd) / 0.408 (even), barely past the Connes–Consani room 0.3466. Beyond that the primes cover a deficit of order 0.01–0.9 while the full form survives by 1e-4 down to 1e-13.
2. **No slack in the prime weights (D13, refined by D21).** Scaling the prime-2 weight, the smallest fraction that keeps positivity reaches 1.000 (to three decimals) by L ≈ 0.55. Removing prime 2 or all primes kills positivity in both parities — established for the full W (certified negative witnesses). Claims about marginal, newly visible places (e.g. the power 4 at L = 0.7) were reduced-form artifacts: exact scores on the tested waves are positive (D21). D13/D16/D17 carry appended corrections.
3. **Places enter and matter (D16, reduced-form only after D21).** In the reduced form, every prime power visible for more than ΔL ≈ 0.03 is load-bearing (32/32 cases, ζ and three Dirichlet characters); for the full W this is established only for large terms.
4. **Universality across Dirichlet L-functions (D15).** χ₋₃, χ₋₄, χ₅ show the same phenomenology (exponential collapse of the margin, primes load-bearing, no slack), positive to L ≈ 1.2 because log q acts as a flat positive background; the pole is ζ's stand-in for a conductor. A sign rule: a prime with χ(n) = −1 endangers the even sector first when removed, χ(n) = +1 the odd sector.
5. **The critical exponent is where the parities agree (D17, D19).** Replacing the weight n^{−1/2} by n^{−σ}: σ = ½ is the unique exponent positive in both parities; even and odd act as floor and ceiling from opposite sides; the allowed band collapses exponentially in L (width 0.26 → 1.9e-6 from L = 0.40 to 0.60) and its midpoint drifts onto ½ only as it narrows. The sensitivity dλ/dσ does not collapse with the margin (D19b). Mechanism: heavier primes hurt even waves and help odd waves (for ζ; swapped for odd characters).
6. **The floor falls faster than exponentially (D22, D23).** Certified log-slopes between successive rooms: 53, 65, 83 (even); 45, 58, 79 (odd). A constant slope fails by 19–24 %; the model log λ ≈ A − C·e^{2L} fits within 2.4 % (even, C ≈ 11) and 7 % (odd, C ≈ 10). e^{2L} is the size of the arithmetic the room can see. Four points, two parameters.
7. **The dangerous wave is a prolate function (D23).** The certified minimizer overlaps the top prolate spheroidal function of its parity at 0.99984–0.99992 (even) and 0.997–0.9993 (odd), with bandwidth Ω* ≈ 13.1 + 15.3·(L − 0.4); overlap with the second prolate ≤ 0.008. This is the first structural statement about the minimizer and turns the margin into a one-parameter minimization over a known family.
8. **Compressibility (D14).** The minimizer needs 13–47 Legendre modes to 1e-12 while certificates carry 68–170; the hardness is exact cancellation in a small subspace, not complexity.
9. **Krylov compression (D11).** The Schur balance behind the L = 0.7 certificate cannot be certified in 8 Krylov steps; 32 steps certify it (both parities), still relying on a full-size verifier. Independent audit of Codex's D10 completion-of-squares found no defect and supplied one missing measure-theoretic argument.

## 6. Failures, corrections, and dead ends (kept, and part of the evidence)

- D4 runs 1–3 failed (Arb Bessel enclosures; recurrence wrapping on wide boxes); fixed by elementary forms and analytic strip bounds.
- D5's pointwise identity |F1 + iF2|² = |F1|² + |F2|² was false; corrected in D6 (integrated identity by oddness). D5's odd constant 5.86e-11 was rounded up; withdrawn, 5.859e-11 stands.
- D8: the truncated-translation lemma is true but useless for positivity: the near-null wave barely touches the primes (saturation 0.03 of a possible 2.94), so any global replacement of the prime term loses more than the margin. "Bound the primes better" is dead.
- D11b: the near-orthogonality of the pole coupling to the softest direction of the complement tracks λmin(C) across L; a consequence of positivity, not a cause. VOID as structure.
- D14 Test A: predicted injected-zero frequency was wrong (design error, resolution ~π/L); VOID by its own kill rule; post-hoc explanation labeled.
- D16/D17/D13 marginal-place claims: reduced-form artifacts (D21). Corrections appended.
- D22: no two-sided bracket of the full infimum closes at 10 % at any L; four scoring trials, each diagnosed: noise modes, boundary jumps, weak constraints, and finally the structural looseness of the D9 derivative tail bound for smooth high-degree candidates.
- Prediction-ledger failures across rounds (kept in each RESULTS.md): about one in four preregistered numerical predictions failed, including my own predicted decay rate, the prime-2 sufficiency at L = 0.7, several range guesses, and the delete-4 odd witness.
- Ideas tested and closed by the wider GHP program, not reopened here: φ/golden ratio as a selection principle (killed five ways), the "horizon" reading of the Viviani-φ surface, φ–zeta bridges, prime-number synchronization mechanisms. "Prime" in Aukora is a record type.

## 7. Open questions (the honest frontier for this approach)

1. Derive λmin(L) as min over Ω of W(ψ₀^Ω) from prolate asymptotics against the Weil symbol; test whether C ≈ 10–11 in the e^{2L} law follows. This is a derivation, not a scan.
2. Close the full-W brackets with prolate candidates and either direct tail quadrature to T₂ ≈ 4000 or a spectral-side Bessel-asymptotic tail bound.
3. Explain the parity mechanism structurally: why heavier primes hurt even waves and help odd waves; whether a known duality exchanges the sectors and flips the arithmetic sign.
4. Is there a quantity monotone in L whose sign controls positivity? That is the only shape of argument that would make positivity inherited by larger rooms. Nothing here supplies it.
5. Formalize the four elementary lemmas behind the L = 0.7 certificate in Lean.

## 8. Where everything is

Hub: `Reimann Research/README.md`. Certificates and audits: `experiments/weil_hidden_modes/` (FABLE-AUDIT.md, FABLE-ROUND-D5/D6-RESULTS.md, OPUS-ROUND-D7-RESULTS.md), `experiments/codex_d9_exact_scores/`, `experiments/codex_d10_joint_geometry/`, `experiments/fable_d11_joint_balance/`. The map: `experiments/fable_d8_confinement/` through `experiments/fable_d23_shape/`, each with PREDICTIONS.md (committed before compute), RESULTS.md (with ledger), code, logs, JSON endpoints. Reviews: `experiments/astra_d20_review/`, handoffs in `Reimann Research/`.

## 9. For a model that wants to "learn" this

Do not fine-tune on this document; that teaches the words, not the object. Load it as context together with the raw JSON endpoints and the code, then take the exam that would show understanding: answer Astra's D24 questions (`Reimann Research/` handoff of 2026-09-13) — verify the D22 tail bounds remain valid when L and T change; say whether the prolate identification follows from the structure of R_T; sketch or refute the derivation λmin(L) ≈ min_Ω W(ψ₀^Ω). A model that can do those has understood something; a model that reproduces §5 has memorized it.

## 10. Plain language

We built a small room with mirrors and proved every wave in it behaves. We measured, room by room, how close the balance comes to failing, and found the exact shape of the most dangerous wave: a classical function called a prolate, whose width grows in a straight line with the room. We found that the safety margin shrinks like the exponential of an exponential, that every prime the room can see is needed exactly, and that the famous one-half is where the even half and the odd half of the problem stop arguing. We tried five shortcuts to bigger rooms; all five failed for reasons we can now state. None of this moves the Riemann Hypothesis. It is the clearest map anyone has drawn of where this particular road ends and what a real road would have to do.
