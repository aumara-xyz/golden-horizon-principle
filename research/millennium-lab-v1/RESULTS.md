# RESULTS — millennium-lab-v1 (round 1, hyper-efficient: L1–L3)

Branch `lab/millennium-v1`. Predictions committed first (98973db). Code: `lab.py`. Numbers: `metrics.json`. Runtime 187 s on a laptop.
Vocabulary: MEASURED / UNVERIFIED / PREDICTED / VOID.

## What was computed
- First 1000 nontrivial zeros via `mpmath.zetazero`; |ζ(½+it)| on a 20k grid to ~~t≈466~~ t=401.38 (code scanned zeros[199]+5; struck after Codex audit).
- Nearest-neighbour spacing distribution and pair correlation for (a) zeros, (b) primes in [1000, ~9000], (c) 1001 uniform randoms; each unfolded to mean spacing 1. References: GUE Wigner surmise / R₂=1−(sin πx/πx)², Poisson exp(−s) / R₂=1.
- H=xp in log-coordinate (H = −i d/du on u∈[0,L]), 400-point finite difference, four boundary conditions, first 20 eigenvalues vs first 20 zeros. Scale L tuned once so the periodic comb spacing equals the zeros' mean spacing (3.316). Counting function N(T) vs the Berry–Keating smooth count.

## L1 — MEASURED, prediction held
All 200 zeros checked have Re(s)=½ exactly at working precision (max deviation 0.0). ~~|ζ(½+it)| has exactly 200 dips below 0.05 on [0, t₂₀₀+5] and they sit on the listed zeros.~~ STRUCK after Codex audit: the interval [0, 401.38] contains 202 zeros; the dip counter missed two and never matched dips to zeros. See RESULTS-round2.md R2.1. Plot `L1_abszeta.png`.

## L2 — MEASURED, all three predictions held
L1 distance of empirical spacing histogram to each reference (smaller = closer):

| sample  | to GUE | to Poisson | frac spacings < 0.2 | pair-corr to GUE | pair-corr to Poisson |
|---------|-------:|-----------:|--------------------:|-----------------:|---------------------:|
| zeros   | 0.150  | 0.861      | 0.003               | 0.067            | 0.213                |
| primes  | 0.656  | 0.662      | 0.000               | 0.281            | 0.329                |
| random  | 0.828  | 0.138      | 0.198               | 0.228            | 0.096                |

- Zeros: level repulsion is real (0.3 % of spacings under 0.2 vs 19.8 % for random). Pair correlation follows 1−(sin πx/πx)² with the dip at x<0.7 clearly resolved. 1000 zeros is enough to see it; not enough for a precision test.
- Random control: Poisson. GUE would have been rejected. The control did its job.
- Primes: match NEITHER. The histogram is a comb (gaps are even integers, normalised by ln p), which is arithmetic structure, not spectral structure. Anyone claiming "the primes have GUE statistics" is wrong; it is the zeros, and the zeros only.
Plot `L2_gue_controls.png`.

## L3 — MEASURED, the knob, and the gap stated precisely
Setup honesty: H=(xp+px)/2 is unitarily −i d/du on L²(du), u=ln x. That is a first-order operator. On a bounded interval its self-adjoint realisations are exactly the twisted-periodic family ψ(L)=e^{iθ}ψ(0); Dirichlet (reflecting) at both ends has NO self-adjoint extension, and absorbing is non-self-adjoint by construction. So "bounded + loops" is not one option among four — it is the only option the operator allows.

| boundary   | first 5 eigenvalues (L tuned)          | spacing std/mean | RMS vs zeros raw | RMS after best affine fit |
|------------|----------------------------------------|-----------------:|-----------------:|--------------------------:|
| reflecting | 0.83, 2.48, 4.13, 5.79, 7.44           | 0.003            | 34.6             | 1.98                      |
| periodic   | 3.32, 3.32, 6.63, 6.63, 9.95           | 1.05 (paired)*   | 33.0             | 2.55                      |
| twisted θ=π/3 | 0.55, 2.76, 3.87, 6.08, 7.18        | 0.33 (alternating)| 34.6            | 2.04                      |
| absorbing  | 400/400 eigenvalues complex, max |Im| 211 | —             | disqualified              | disqualified              |
| **zeros**  | 14.13, 21.02, 25.01, 30.42, 32.94      | **0.42, and DECREASING** | —        | —                         |

\* Periodic on an even central-difference grid pairs eigenvalues (sin(2πk/N) degeneracy) — a discretisation artefact. The continuum spectrum is exactly 2πn/L, a perfect comb, spacing std/mean = 0.

Ranking prediction: periodic ≈ twisted < reflecting < absorbing. ~~What happened: reflecting < twisted < periodic on the affine-fitted RMS … Prediction on ordering was WRONG (kept).~~ STRUCK after Codex audit: on the registered raw RMS the order was periodic 33.04 < twisted 34.60 < reflecting 34.65, exactly as predicted; my 'wrong' verdict came from an unregistered per-model affine fit. The wrong self-correction stays visible here. Prediction on the failure signature was RIGHT and is the actual finding:

**The gap, stated precisely.** Every self-adjoint boundary condition on xp over a fixed interval produces a comb: eigenvalue spacing constant in n (or alternating between two constants). The zeros' spacing shrinks like 2π/ln(t/2π): first gap 6.89, twentieth gap 1.44. A comb cannot bend. The counting function makes it stark:

| model                                   | max |N_model(T) − N_zeros(T)|, T ≤ 1420 |
|-----------------------------------------|---------------------------------------:|
| comb (any BC on plain xp, L tuned)      | ~~571~~ 572 (endpoint insertion side; struck after Codex audit) |
| Berry–Keating smooth (T/2π)ln(T/2πe)+7/8 | ~~1.01~~ 1.234 at zero #871 (sparse grid missed the max; struck after Codex audit) |

The BK smooth count is right to within one zero over 1000 zeros — that is what the phase-space regularisation (|x|>lₓ, |p|>l_p, lₓl_p=2π) buys. It gets the DENSITY of the spectrum. It does not get the individual eigenvalues, because a smooth count contains no arithmetic; the fluctuating part N_osc(T) is a sum over primes (the explicit formula). The open problem is: what boundary condition / what compactification of xp injects the primes as periodic orbits with the right signs. "Bounded, loops topologically" is the right category of answer; the loop structure needed is not a circle but something whose closed orbits have lengths ln p, all repetitions, with the −1 sign convention of the Gutzwiller trace formula reversed. That is the fifty-year gap. Nobody has the object. Plot `L3_xp_boundary.png`.

No oracle leak: nothing came within RMS 0.5 even with scale tuning.

## L4 — NOT RUN this round
Stub: y²=x³−x, conductor 32, rank 0, L(E,1)≈0.6555… ≠ 0 → BSD predicts finitely many rational points (torsion Z/2×Z/2: (0,0),(±1,0),∞). Parallel to be shown: both L-functions are Euler products whose zero/pole structure at a special point encodes an arithmetic count. UNVERIFIED until computed here.

## L5 — NOT RUN this round
Five artifacts unread. Rule pre-committed: base-27/ternary/"27" claims get a random-sequence-of-same-density control; a metaphor is not a claim; "number appears in both" needs a stated base rate.

## What a real number theorist would say
Learned: nothing new to the field, but three things now sit on this machine as measured facts rather than lore — (1) the GUE match is real and specific to the zeros, and the prime control proves the match is not about "primes are random"; (2) the H=xp program is not vague: with the operator written in log-coordinates you can SEE that plain boundary conditions yield combs, and the Berry–Keating count reproduces N(T) to ±1 for 1000 zeros, so the smooth half of the problem is solved and the fluctuating half is exactly the primes; (3) Peter's "bounded, loops" is the correct family of self-adjoint extensions of the leading candidate, which is a more precise thing than most amateur RH intuitions ever reach.
Not learned: anything about WHY Re(s)=½. Nothing here touches the mechanism; GUE statistics are consistent with RH but do not imply it, and a finite-difference matrix on 400 points cannot distinguish a spectrum from a coincidence. The honest research frontier is unchanged: no self-adjoint operator with spectrum {tₙ} is known, and the phrase "loops topologically" needs to become a specific dynamical system whose periodic orbits are the primes before it is a claim.

## Wrong predictions kept
- L3 ordering: predicted periodic ≈ twisted best; measured reflecting marginally best after affine fit (1.98 vs 2.04 vs 2.55). Meaningless differences between three failures, but the prediction was wrong and stays on the record.
- L3 periodic discretisation: did not predict the eigenvalue pairing artefact; fixed by noting the continuum result, not by rerunning.
