# PREDICTIONS — round 2 (Fable), written before compute

Inputs new this round: Odlyzko's first 100,000 zeros (zeros1, 9 dp), LMFDB rigorous level-1 Maass forms (500 forms, r<=91, 280 even / 220 odd).
Vocabulary: MEASURED / UNVERIFIED / PREDICTED / VOID. Antigravity's CONFIRMED/proves vocabulary is not inherited.

## R2.1 Reconciliation of Codex vs Fable round 1 (third computation)
- PREDICTED: Codex right. Interval [0, zeros[199]+5 = 401.38] contains 202 zeros. My "exactly 200 dips" is VOID.
- PREDICTED: sup |N(T) - N_smooth(T)| over first 1000 zeros at one-sided limits ~ 1.234 at zero #871; my 1.011 (sparse grid) VOID.
- PREDICTED: comb supremum 572 (Codex), my 571 VOID (endpoint insertion).
- Conceded without compute: my registered L3 ranking (periodic < twisted < reflecting on raw RMS) HELD; my reported "prediction wrong" used a post-hoc affine fit. The correction is struck in RESULTS.md; the wrong self-correction stays in the record.
- Conceded: I reported the L1 scan "to t~466"; the code scanned to 401.38. VOID.

## R2.2 Antigravity dossier audit: each claim gets the control it lacked
- L4 L(E32,1) = 0.3912: PREDICTED VOID. Raw Euler product at s=1 is outside absolute convergence. Functional-equation series (root number +1, N=32): PREDICTED 0.65551... Independent recompute from point counts.
- L6 Fourier peaks at ln p from 100 zeros with height>=4, distance=10: PREDICTED the same detector fires on a random control spectrum of the same density (noise std of sum of 100 cosines ~ sqrt(50) ~ 7 > 4). Detection protocol VOID. Phenomenon itself: PREDICTED MEASURED with 100k zeros: peaks at ln(p^k) with heights proportional to the von Mangoldt weight ln p / p^{k/2}; ratio peak(ln3)/peak(ln2) ~ 1.29, peak(ln4)/peak(ln2) ~ 0.71; random control shows no such peaks. This is the explicit formula (a theorem), so status is MEASURED, never "proves".
- Musical chord (gamma2/gamma1 ~ 3:2, gamma3/gamma1 ~ 7:4 within 0.02): PREDICTED VOID. Base rate: fraction of a uniform ratio in [1.1,2] within 0.02 of a just-intonation interval with numerator, denominator <= 9 is > 50%. Two hits is unremarkable (base rate > 25%).
- Selberg geodesic lengths 2 ln((t+sqrt(t^2-4))/2) ~ ln p (t=3 -> ln 7, t=5 -> ln 23): PREDICTED VOID. For traces t=3..40, distance to nearest ln(p^k) will be no smaller than for random lengths in the same range (percentile within [5,95]). The true fact: modular geodesic lengths are 2 ln(eps_d), fundamental units of real quadratic fields, indexed by class numbers, not by rational primes.
- Li coefficients from 100 zeros (lambda_10 = 1.9683, lambda_100 = 87.63): PREDICTED numerically wrong from truncation. Anchor: lambda_1 = 1 + gamma_E/2 - ln(4 pi)/2 = 0.0230957 exactly. From 100k zeros PREDICTED lambda_1 within 1e-4 of anchor; lambda_10 ~ 2.28 (Keiper), lambda_100 within 10% of (n/2)(ln n + gamma_E - 1 - ln 2pi) + 1/2 = ~117.
- "Off-line zero instability probe" (x^0.75 vs x^0.5): VOID as evidence; it is the identity |x^rho| = x^beta. No compute.
- "Re(s)=1/2 enforced by conservation of energy": VOID. No such derivation exists in the literature or in Antigravity's code.
- Gram's law "locks zero crossings in each interval": PREDICTED first violation at Gram index 126 (known), and violations > 5% of Gram intervals by index 100,000. Tested on Odlyzko zeros.

## R2.3 Track 1 (Coulomb gas = GUE) with 100k zeros
- PREDICTED: locally unfolded nearest-neighbour spacings of 100k zeros have KS distance < 0.02 to the empirical spacing law of GUE matrices (N=1000 Hermitian, 10 draws, bulk only) and > 0.3 to exponential. Pair correlation L1 to 1-(sin pi x/pi x)^2 < 0.02.
- PREDICTED: the surmise and the true GUE law are NOT separable at this height (both KS < 0.02), because finite-height corrections ~ 1/ln T at T ~ 7.5e4 are of the same order.
- PREDICTED: positions are NOT reproduced: two GUE draws differ from each other as much as from the zeros (the gas fixes statistics, not positions). Control built in.

## R2.4 Track 3 (Selberg / Maass forms): the bounded looping system that DOES have a proven "RH"
- Fact to carry: for a finite-area hyperbolic surface, the Selberg zeta function's nontrivial zeros lie on Re(s)=1/2 BECAUSE the Laplacian is self-adjoint: Hilbert-Polya is a theorem there. Its "primes" are closed geodesics, lengths 2 ln eps_d.
- PREDICTED (Bogomolny-Georgeot-Giannoni-Schmit 1992): within each symmetry class (even 280 / odd 220), Weyl-unfolded Maass spacings are POISSON, not GUE: KS to exponential < KS to GUE; fraction of spacings < 0.2 between 0.12 and 0.25 (Poisson 0.18) versus ~0.009 for GUE. Kill condition: repulsion (fraction < 0.05) would falsify my reading of the literature.
- Control: mixing the two symmetry classes must look even more Poisson (superposition), so the within-class result is the one that counts.

## R2.5 Track 4 (Li contradiction machine)
- PREDICTED: true lambda_n from 100k zeros positive and monotone for n <= 200, matching Coffey asymptotic within 10% by n=100.
- PREDICTED: injecting a rogue quadruple {rho, 1-rho, conj} with beta=0.75 at gamma=14.13 makes lambda_n negative first at n_crit between 1,000 and 30,000; for beta=0.6, later; n_crit grows ~ |1-rho|^2 / (2 beta - 1), i.e. like gamma^2. Consequence (honest): the machine works but a rogue zero at height gamma hides until n ~ gamma^2, so no finite lambda_n table proves RH.

## R2.6 Track 6 (closest pairs)
- PREDICTED: among 100k locally-unfolded spacings, fraction s < 0.1 ~ 0.0011 (GUE cubic law (pi^2/9) s^3), s < 0.2 ~ 0.0088; Poisson would give 0.095 / 0.18.
- PREDICTED: the Lehmer pair (7005.063, 7005.101; normalized ~0.042) is among the 5 closest in the first 100k. No prediction on whether it is the closest.

## R2.7 Track 5 (golden ratio / KAM): VOID by category, no compute
xp is integrable and uniformly hyperbolic; there are no invariant tori to perturb, so KAM/noble-torus stability is the wrong category. "Base prime is 1" is not a claim: 1 is excluded from the primes so that factorization is unique.

## R2.8 Track 2 (scattering): deferred
The real object is the Lax-Phillips / Faddeev-Pavlov scattering on the modular surface, S-matrix built from zeta(2s-1)/zeta(2s). Not computed this round; UNVERIFIED here.
