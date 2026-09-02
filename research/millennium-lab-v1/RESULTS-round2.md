# RESULTS — round 2 (Fable)

Predictions: `PREDICTIONS-round2.md` (commit 856c544, before compute). Code: `round2.py`. Numbers: `metrics-round2.json`. Figure: `round2.png`. Runtime 10 s.
New inputs: Odlyzko's first 100,000 zeros (agree with my mpmath 1000 to 5e-10); LMFDB rigorous level-1 Maass forms (500, r <= 91).
Vocabulary: MEASURED / UNVERIFIED / PREDICTED / VOID.

## R2.1 Reconciliation — Codex was right on every disputed number (third computation)

| item | Fable round 1 | Codex | third computation | struck |
|---|---|---|---|---|
| zeros in [0, 401.38] | "exactly 200" | 202 | **202** | Fable |
| sup |N − N_smooth|, first 1000 | 1.011 | 1.234 at #871 | **1.2343 at #871** | Fable |
| comb supremum | 571 | 572 | **571.99 → 572** | Fable |
| L3 ranking | "prediction wrong" | registered raw-RMS order held; reversal was post-hoc affine fit | conceded, no compute | Fable's self-correction |
| L1 scan endpoint | "t ≈ 466" in prose | 401.38 in code | conceded | Fable |

The original round-1 file keeps the wrong numbers with strikethrough and a pointer here.

## R2.2 Antigravity dossier audit — each claim with the control it lacked

| claim (Antigravity) | test | result | status |
|---|---|---|---|
| L(E32,1) ≈ 0.3912 | functional-equation series from point counts, N=32 | **0.65551438857303** (matches Codex to 14 digits); 0.3912 is a truncated Euler product outside its convergence half-plane | VOID |
| L6 "sharp peaks at ln p from 100 zeros", "random spectrum gives flat noise" | rerun the exact detector (700 pts, height≥4, dist 10) on 200 random spectra of the same density | random spectra average **40 peaks** (zeros: 20); random hits **5.6 of 8** ln p^k targets on average; 3.5 % of random runs hit all 8 as the zeros did. The claimed control was a string in the report template, never computed. | detection protocol VOID; signal at N=100 marginal (p≈0.035) |
| same phenomenon, done properly | 100k zeros, Hann window, fine grid ±0.003 around each ln p^k; shuffled-spacing control keeps density, kills arithmetic | peak depth at ln2 / ln3 / ln4: 2823 / 3653 / 1996; control in the same windows 136–206 (its noise floor); zeros **off-target** depth 0.001–0.006. Peaks sit at ln p^k to < 1e-5. Ratio ln3/ln2 = **1.294** (predicted 1.294), ln4/ln2 = **0.707** (predicted 0.707): the von Mangoldt weights ln p / p^{k/2}, measured to 3 digits. | MEASURED (this is the explicit formula, a theorem; "proves Gutzwiller duality" is VOID vocabulary) |
| "musical chord" γ2/γ1≈3:2, γ3/γ1≈7:4 | base rate: uniform ratio in [1.1,2] within 0.02 of a just interval (num, den ≤ 9) | p = **0.54** per ratio, 0.30 for two | VOID |
| Selberg geodesic lengths ≈ ln 7, ln 23 | random-length control, then identity check | my control said the match is real (0.05 percentile) — **my prediction was wrong, and the reason is an identity**: 2 ln ε_t = ln(t²−2−ε'²), so the length for trace t is within 1/t⁴ of ln(t²−2). 13 of 38 traces have t²−2 a prime power (t=3→7, 5→23, 7→47, 13→167, 37→1367…). The "match" is "t²−2 is often prime". Nothing spectral. | VOID as evidence; wrong prediction kept |
| Li coefficients λ10 = 1.968, λ100 = 87.63 | recompute from 100k zeros + tail; anchor λ1 = 1 + γ/2 − ln(4π)/2 | λ1 = 0.0230957091 (exact 0.0230957090); ~~**λ10 = 2.277, λ100 = 118.39**~~ STRUCK after Codex round 3: my omitted-zero tail used the linear term n/|ρ|²; each omitted pair actually contributes 2(1−cos(n/γ)) ≈ n²/γ², so the tail is n²(ln(T/2π)+1)/(2πT) = 0.2207 at n=100, not 0.0022. Corrected: λ10 = 2.2793, **λ100 = 118.6038**, matching Codex's zero-free Arb value 118.60377537679 (Coffey asymptotic 117.7); Antigravity's numbers reproduce exactly when I truncate to 100 zeros, i.e. they are 26 % low from truncation | numbers VOID; positivity to n=200 MEASURED |
| "off-line zero instability", "Re(s)=½ enforced by conservation of energy" | none possible | the first is the identity |x^ρ| = x^β; the second has no derivation anywhere | VOID |
| Gram's law "locks a zero in each interval" | 100k Gram points by Newton on θ(t), residual 1e-10 | first violation at Gram index **126** (predicted 126); **20.6 %** of the first 100k Gram intervals violate | VOID |

## R2.3 Track 1 — the Coulomb gas, with real GUE matrices and 100k zeros

| statistic | value | prediction | held? |
|---|---|---|---|
| KS, zeros vs GUE-matrix spacings (10×N=1000, bulk) | 0.0180 | < 0.02 | yes |
| KS, zeros vs Wigner surmise | 0.0193 | not separable from matrices at this height | yes (0.018 vs 0.019) |
| KS, zeros vs exponential | 0.298 | > 0.3 | **no, by 0.002** |
| pair-correlation L1 to GUE | 0.0234 | < 0.02 | **no, by 0.003** |
| spacing correlation GUE draw 1 vs draw 2 | 0.018 | ≈ 0 | yes |
| spacing correlation GUE draw vs zeros (499 samples) | −0.14 | ≈ 0 | marginal; 3σ with n=499, reported as is |

Reading: the gas gives the statistics, not the positions. Codex's "2×2 surrogate" caveat is resolved: real matrices and the surmise are equally close to the zeros here, because finite-height corrections at T ≈ 7.5e4 are of the same size as the surmise error.

## R2.4 Track 3 — the bounded looping system where Hilbert–Pólya is a theorem, and it has the wrong statistics

For a finite-area hyperbolic surface the Selberg zeta function's zeros lie on Re(s)=½, provably, because the Laplacian is self-adjoint. Its "primes" are closed geodesics. The modular surface is exactly Peter's "bounded, loops" object made rigorous. Prediction (Bogomolny–Georgeot–Giannoni–Schmit 1992): its spectrum is Poisson, not GUE, because arithmetic symmetries (Hecke operators) pile up degeneracies.

| class | n | KS to exponential | KS to GUE surmise | frac s<0.2 (Poisson 0.18, GUE 0.009) | frac s<0.1 (GUE 0.001) |
|---|---|---|---|---|---|
| ~~even~~ **odd** (LMFDB flag 1; I had the parity names reversed, struck after Codex round 3) | 280 | 0.151 | 0.172 | 0.122 | 0.061 |
| ~~odd~~ **even** (flag 0) | 220 | 0.118 | 0.189 | 0.123 | 0.073 |
| mixed (control) | 500 | 0.087 | 0.217 | 0.146 | 0.062 |

MEASURED: no level repulsion in either class (60–70× more small spacings than GUE); closer to Poisson than GUE; mixing the classes moves it further toward Poisson as a superposition should. Caveat: n=280 with KS 0.15 is not a clean Poisson sample either; BGGS used thousands of levels. Prediction held.
Meaning: the natural rigorous realisation of "bounded and loops" gives a self-adjoint operator and a proven critical line, and then FAILS the statistics test that the zeta zeros pass. Whatever operator has the zeta zeros must be chaotic without arithmetic degeneracy, and yet its orbit lengths must be ln p. Nobody has that object.

## R2.5 Track 4 — the contradiction machine, and why it cannot finish

True λ_n from 100k zeros: positive and monotone to n=200, matching the asymptotic (n/2)(ln n + γ − 1 − ln 2π) + ½ within 0.6 % at n=100. Then inject one rogue quadruple {β±iγ, (1−β)±iγ} and find the first n with λ_n < 0:

| rogue β | γ = 14.13 | γ = 100 | γ = 1000 |
|---|---|---|---|
| 0.75 | n_crit = 7,638 | 571,135 | none below 2,000,000 |
| 0.60 | 21,321 | 1,534,362 | none below 2,000,000 |

Predicted 1,000–30,000 for (0.75, 14.13): held. Growth ~ γ²·(2/(2β−1)) as predicted. Consequence, MEASURED: a rogue zero at height γ is invisible in every λ_n with n ≲ 30 γ². Zeros are verified on the line to γ ~ 3×10¹², so Li's criterion can only see a rogue above that at n ~ 10²⁶. The machine is sound (Li 1997: RH ⟺ all λ_n ≥ 0) and cannot be run to completion numerically. That is the precise form of "why can't we just check".

## R2.6 Track 6 — closest pairs in 100k zeros

| | measured | GUE cubic law | Poisson |
|---|---|---|---|
| frac s < 0.1 | 0.00079 | 0.0011 | 0.095 |
| frac s < 0.2 | 0.0061 | 0.0088 | 0.181 |

Order of magnitude as predicted; 28 % fewer tiny spacings than the leading GUE term (finite-height rigidity). Five closest normalised spacings: #95248 (s=0.022, γ=71732.9), #87761 (0.029), #82552 (0.031), #73997 (0.037), #44555 (0.041). The Lehmer pair (#6709, γ=7005.06, gap 0.0377, s=0.042) ranks **6th** — I predicted top 5, wrong by one.

## R2.7 Track 5 — VOID by category (no compute)
xp is integrable and uniformly hyperbolic; there are no invariant tori, so KAM / noble-torus stability is the wrong category. "Base prime is 1" is not a claim: 1 is excluded from the primes so that factorisation is unique.

## R2.8 Track 2 — deferred, UNVERIFIED here
The real object is Lax–Phillips / Faddeev–Pavlov scattering on the modular surface, S-matrix built from ζ(2s−1)/ζ(2s). Not computed.

## Wrong predictions kept
- Selberg control: predicted "no excess closeness", measured extreme closeness, explained by the identity 2 ln ε_t ≈ ln(t²−2). My null was wrong, not the numbers.
- KS to exponential 0.298 (predicted > 0.3); pair-correlation L1 0.023 (predicted < 0.02).
- Lehmer pair rank 6 (predicted ≤ 5).
- Round 1 (via Codex): 200-dip claim, smooth-count supremum, comb supremum, scan endpoint, and my own retraction of the L3 ranking.

## What a number theorist would say now
Learned on this machine, as measured facts: the explicit formula works to three digits with the primes falling out of the zeros exactly at ln p^k with von Mangoldt weights and near-zero background, which is the single most striking picture in the set; the GUE agreement at 100k zeros is as good as random matrices themselves at this height; the one rigorous "bounded, loops" system (the modular surface) has a proven critical line and Poisson statistics, which pins the open problem as "chaotic orbits of length ln p without arithmetic degeneracy"; and Li's criterion is a working contradiction machine whose horizon grows like γ², which is the exact reason enumeration cannot become proof. Not learned: anything about why Re(s)=½. Every "CONFIRMED" and "proves" in the Antigravity dossier is either a theorem re-evaluated numerically, a truncation artefact, an identity, or numerology; the two ideas in it that survive with controls are the explicit-formula peaks and the Lehmer pair, both known since the 1950s.

## Reconciliation after Codex round 3 (added later)
- λ100: Codex right, Fable VOID (tail had the wrong leading power). Third computation: my zero-sum + corrected n² tail = 118.6038; Codex 118.60378. Agreed.
- Maass parity labels reversed by me; conclusion (no repulsion, Poisson-like, not an exact exponential law) survives; Codex's 2,202-form LMFDB rerun strengthens it.
- Rogue-Li horizon 7638 confirmed exactly by Codex's zero-free 12,000-bit run; Codex's own prediction that it would move was VOID.
- My blanket "every criterion has a γ² horizon" is VOID as stated: Li's ratio n_crit/γ² drifts 38 → 57 → 78 (a log envelope), and the other criteria do not accept a bare rogue quartet at all. The answer to the open question is in the direction I guessed but sharper: an oracle-targeted Weil test function sees the rogue at prime-power cutoff x ≈ 10 for γ=14, while a blind Li sequence needs n ≈ 7,600. Cheap detection requires already knowing γ. Not new; a numerical instance of Weil equivalence.
