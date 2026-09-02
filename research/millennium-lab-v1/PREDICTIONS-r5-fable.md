# Round 5 (Fable) — Connes–Consani–Moscovici "Zeta Spectral Triples" (arXiv:2511.22755, 27 Nov 2025), written before compute

Sources read in full: CCM 2025 (34 pp). Second source verified to exist: Chuk, "Weil positivity in compact windows..." arXiv:2608.24827 (25 Aug 2026) — claims certified simple/even ground state at a fixed window; not used here.
Their construction (my reading): L = 2 log λ; basis V_n, |n| ≤ N; real symmetric τ = W_{0,2} − W_R − Σ_p W_p (eqs 4.2, 4.4, 4.3); ξ = eigenvector of the smallest eigenvalue ε_N (assumed simple, even); spectrum of D_log^{(λ,N)} = real roots z of Σ_j ξ_j /(z − 2πj/L) (Prop 5.9 / Thm 5.10). Their reported accuracies: λ=3, N=120: |E_1−γ_1| = 1.6e-34, |E_20−γ_20| = 2.4e-7; λ=√13, N=120: 2.4e-55 (k=1), 3.5e-24 (k=20), 2e-7 (k=40), 2e-3 (k=50).
Rule: no zeta zero enters construction or parameter choice. Only λ, N, precision. Zeros are used for SCORING only, after the pseudo-prime control has run. Scoring window frozen: zeros 20–50 (and 1–20 reported separately).
Implementation: archimedean integrals via the geometric expansion ρ(x)=Σ_k e^{−(2k+1/2)x} with the ∫_0^∞ part in closed digamma/trigamma form and the ∫_L^∞ tail summed (converges like λ^{−4k}); prime part by direct evaluation at log p^k; W_{0,2} closed form; 220 digits; inverse iteration with python-flint.

P1 (reproduction, λ=3, N=120): |E_k − γ_k| within a factor 100 of Fig. 1 for k=1..20 (i.e. 1e-36 < |E_1−γ_1| < 1e-32; 1e-9 < |E_20−γ_20| < 1e-5).
P2 (λ=√13, N=120): within a factor 100 of their table at k=20, 30, 40, 50.
P3 (even-simple): ε_N simple with ε_2/ε_1 > 1e10 and ξ even to 1e-100 relative; log ε_N roughly linear in μ=λ² with slope between −12 and −8 per unit μ (their Fig. 4).
P4 controls, each run before scoring: (a) delete the prime 2 and its powers → |E_1−γ_1| > 1e-5; (b) pseudo-primes: replace the points log(p^k) by uniform random points in [0,L], same count and same weights, 5 seeds → |E_1−γ_1| > 1e-3 in every seed; (c) archimedean-only (no primes) → |E_1−γ_1| > 1e-2; (d) weight permutation among the prime powers → |E_1−γ_1| > 1e-6. If ANY control lands within 1e-10 of a zero the result is VOID as an oracle leak until explained.
P5 (what would kill the construction's story): if the spectrum matched zeros equally well with pseudo-primes, the "Euler product only" claim would be false. I predict it does not.
Honest expectation: P1–P4 hold; the object is real and arithmetic; the unproved bridge (prolate k_λ → ξ_λ convergence) is untouched by anything I compute today.
