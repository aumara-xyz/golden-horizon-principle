# Note on the missing step of "Zeta Spectral Triples" (arXiv:2511.22755): a gap-free sufficient condition, and three measurements

Draft for the authors (Connes, Consani, Moscovici). Prepared 2026-09-03 by an amateur lab (Peter Viviani with Claude/Fable and OpenAI Codex), from an independent implementation of the construction in §§4–5 of the paper and hostile controls. Nothing here is a theorem. Every number below is reproducible from the code in `research/millennium-lab-v1/` (aumara-xyz/golden-horizon-principle, main).

## 1. Reproduction
Two independent implementations (one from eqs (4.2)–(4.4) with digamma/trigamma closed forms and python-flint linear algebra at 220 digits; one from the explicit formula with mpmath at 100–400 digits) agree on all 29,161 upper-triangle entries of QW_λ^N to ≤ 2.3e-100 for x = λ² ∈ {9, 12, 13, 14}, N = 120. The spectrum of D_log^{(λ,N)} reproduces Table 1 and Fig. 1 of the paper to the printed digit (e.g. λ=3: 1.58e-34 at k=1, 2.42e-7 at k=20; λ=√13: 2.44e-55, 3.54e-24, 2.0e-7, 2.04e-3 at k = 1, 20, 40, 50). Nine controls (prime deletion, archimedean-only, pseudo-primes at matched density, weight permutation) each destroy the match entirely and turn ε_N from ~1e-38 into an O(0.1) number. Even-simple was checked by certified Arb balls at x = 5, 9, 12, 13, 14, 20 (N = 120).

## 2. The prime-free comparison
The prolate candidate k_λ = E(h_λ) of §7, projected to E_N and fed to the same transform/root-finder (no Weil matrix), also lands on the zeros: 2.9e-30 at k=1 for x=13 (true ground state: 2.4e-55), 4.0e-33 for x=14 (true: 1.1e-60). So the finite Euler product contributes ≈25–28 orders of magnitude beyond what the dilation identity F_μ(E(h))(z) = ζ(½−iz)·(Mellin of h) already supplies, concentrated on the low zeros. At x=9 the gap is 15 orders.

## 3. A gap-free sufficient condition for the second missing step (§8)
With c_λ a scalar and |Im z| ≤ ½ − ε,
  sup_z |ξ̂_λ(z) − c_λ k̂_λ(z)| ≤ ‖ξ_λ − c_λ k_λ‖_{L²(d*u)} · λ^{½−ε} · (2 ln λ)^{½},
so, given Lemma 7.3, it suffices that
  (★)  ‖ξ_λ − c_λ k_λ‖_{L²(d*u)} = o(λ^{−½}(ln λ)^{−½}), with N → ∞ first.
(★) never involves the spectral gap Δ_λ = ε₂ − ε₁ of QW_λ^N.

## 4. Three measurements around (★)
(a) The gap route is numerically closed: with r = ‖(QW − μ)k_λ‖, the ratio r/Δ grows from 3e5 (x=5) to 7e42 (x=20), best fit exp(5.8x). No perturbation bound through Δ can give (★).
(b) The angle itself is small and decreasing: sin θ(λ) = ‖ξ_λ − c k_λ‖ (unit vectors, optimal c) is 4.1e-4 at x=5, 6.8e-5 at x=13, 3.0e-5 at x=20 (N=144), ≈2.0e-5 at x=25 and ≈1.6e-5 at x=30 once the prolate degree is ≥ 12x (under-resolved candidates give spuriously small angles); at fixed x the angle still decreases ~15 % per +40 in N, so these are upper estimates. The threshold λ^{−½}(ln λ)^{−½} at x=36 is ≈0.3. Numerically (★) holds by four orders of magnitude at every tested window; its RATE is bracketed: between λ^{−2} and λ^{−3} on x ∈ [13, 30] with resolved candidates (the N→∞ limit at each x would steepen the small-x end).
(c) The Gaussian limit is not usable: replacing h_λ by the undeformed Hermite combination h of Lemma 7.1, the angle of E(h) to ξ_λ is 0.28 (x=9), 0.34 (x=13), 0.36 (x=14), 0.38 (x=16), not decreasing. The λ^{−2} closeness of h_λ to h (Lemma 7.2) is destroyed by E, which sums ~λ/u dilates. Any proof of (★) must be carried out in prolate terms.

## 5. What we could not find in the literature
[CC21, §3–4] compares eigenvectors with prolate projections graphically and reports zero-discrepancy metrics A(μ), R(μ), NR(μ); [CCM25, §8] states the step qualitatively. We did not find the rate form (★), an angle-vs-λ table, or the Hermite negative (c) stated anywhere. If they are known to you, this note is only a confirmation from outside.

## 6. Questions
1. Is (★) the form in which you intend to attack the second step, or is the target det_reg → Ξ via the trace formula of [CCM23] directly?
2. Do you have a heuristic for the decay exponent of ‖ξ_λ − k_λ‖? Our data cannot separate λ^{−2} from λ^{−8}.
3. Is the failure of the Gaussian limit (c) expected from the Slepian approximate-intersection picture, or does it say something about which prolate modes must enter k_λ beyond n = 0, 4?

Code, matrices, certificates, and every wrong prediction we made along the way are in the repository.
