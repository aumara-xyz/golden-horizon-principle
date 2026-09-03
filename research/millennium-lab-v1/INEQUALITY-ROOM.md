# The inequality room — the one sentence left in the CCM program, stated so it can be attacked (Fable, 2026-09-03)

Setting (CCM arXiv:2511.22755 §7–8): ξ_λ = ground state of QW_λ on [λ⁻¹, λ]; k_λ = E(h_λ), the prolate "educated guess"; ξ̂ = transform ∫ f(u) u^{−iz} d*u. Their Lemma 7.3 (proved): k̂_λ → Ξ uniformly on closed substrips of |Im z| < ½, after normalization. Their missing step: ξ_λ ≈ k_λ strongly enough that ξ̂_λ → Ξ too, whence Hurwitz gives real zeros in the limit.

## The needed inequality, made explicit
For a scalar c_λ (normalization), on the strip |Im z| ≤ ½ − ε:
  sup_z |ξ̂_λ(z) − c_λ k̂_λ(z)| ≤ ∫ |ξ_λ − c_λ k_λ| u^{Im z} d*u ≤ ‖ξ_λ − c_λ k_λ‖_{L²(d*u)} · λ^{½−ε} · (2 ln λ)^{½}.
So it SUFFICES to prove
  (★)  ‖ξ_λ − c_λ k_λ‖_{L²(d*u)} = o( λ^{−½} (ln λ)^{−½} )   as λ → ∞ (with N → ∞ first at each λ).
This route never mentions the spectral gap Δ_λ. The gap-based route (residual/gap ⇒ angle) is the one Codex measured dead (r/Δ grows like e^{5.8x}). (★) is the gap-free target.

## What is measured (Codex R5.3, N = 120, x = λ² from 5 to 20)
sin θ(λ) := ‖ξ_λ − c_λ k_λ‖ (unit vectors, optimal c) decays like λ^{−3.90} (fit over 13 points; in x: x^{−1.95}).
The transform-error bound above then behaves like λ^{−2.95} (ε = 0) and is 8×10⁻⁵ at x = 20.
Needed exponent for (★): anything below −½. Measured: −3.9. Margin: 3.4 powers of λ.
Reading: numerically, convergence of the songs is not close; it is comfortable. The obstacle is purely that nobody can PROVE any bound on ‖ξ_λ − k_λ‖ beyond the trivial one, because the standard tool (perturbation theory through the gap) gives nothing.

## Caveats that keep this honest
1. Fixed N = 120. (★) concerns the N → ∞ ground state at each λ. The angle at N = 96/144 was not tabulated by Codex (only r/Δ). UNVERIFIED that the angle is N-stable; it is plausible since the matrices converge, but it must be measured.
2. c_λ is an optimal scalar per λ; the Hurwitz argument tolerates any nonzero scalar, so this is fine, but the normalization to Ξ (their "e^{a+bs}" factor) must be tracked.
3. The fit is 13 points on a laptop. A trend, not a law.
4. Even if (★) is true, proving it may need the trace formula of Connes 2023 relating P_λ, P̂_λ, E to QW_λ; nothing here supplies that proof.

## What this contributes
Not a theorem. A sharpening: the open step is a single L²-distance bound with an explicit required rate, and the required rate is ~3.4 powers of λ weaker than what is observed. Anyone attacking the program needs only a crude estimate, not a sharp one. UNVERIFIED whether the authors have stated it in this form; §8 states the step qualitatively.

## Next measurements (cheap, if prolate functions are available)
- sin θ at N = 96, 144, 192 for x = 9, 13, 16: is the exponent N-stable?
- sin θ at x = 25, 30, 36 (N scaled with x): does −3.9 persist or steepen?
- the same with the undeformed Hermite h in place of h_λ: how much of the closeness is the prolate deformation?
