# millennium-lab-v1 — summary (Fable's version, 2026-09-02)

For someone who wasn't here. Everything below was computed on a laptop in one day, with predictions committed before each computation, and audited by a second system (Codex) whose corrections are struck into the originals. Nothing here is new to mathematics. The value is that the shape of the open problem is now measured, not recited.

## Every result, with who found it first

| what we measured | first found by |
|---|---|
| 100,000 zeros on Re(s)=½; zero tables at heights 10⁴, 10¹², 10²¹, 10²² | Riemann 1859; Odlyzko's tables 1980s–2000s |
| spacing and pair correlation follow GUE; fit improves with height | Montgomery 1973, Odlyzko 1987 |
| primes fall out of the zeros at ln pᵏ with weights ln p/p^{k/2} (measured to 6 digits) | Riemann's explicit formula 1859; von Mangoldt 1895 |
| number-variance saturates; prime-2 ripple period ln(T/2π)/ln 2 stretches with height | Berry 1988; Bogomolny–Keating 1996 |
| every self-adjoint xp on a bounded interval gives a comb | Berry–Keating 1999 |
| Berry–Keating smooth count is not uniformly within 1 (sup 1.234 at zero #871) | measured here; consistent with Berry–Keating |
| modular surface: proven critical line, Poisson statistics, wrong "primes" | Selberg 1956; Bogomolny–Georgeot–Giannoni–Schmit 1992 |
| on the line, \|1 − 1/ρ\| = 1 exactly: zeros are equidistant from 0 and 1; Li's criterion | Li 1997 |
| a rogue zero at height γ sits ~1/γ² off Li's circle; first negative λₙ at n = 7638 for (β=0.75, γ=14.13) | follows from Li 1997; exact index confirmed zero-free by Codex |
| λ₁₀₀ = 118.6038 (Fable's 118.385 struck: wrong tail power) | Keiper 1992 / Coffey 2004 values |
| the line is a ridge of λ₁ but not of all λₙ (valleys from n≈33) | follows from Li 1997 |
| de Bruijn–Newman flow: forward → comb; backward → closest pair collides at t = −g²/8 (predicted to 2 %) | de Bruijn 1950, Newman 1976, Rodgers–Tao 2018 |
| targeted Weil test sees a rogue with primes ≤ 10; blind Li needs n ≈ 7600 | Weil 1952; instance computed by Codex |
| L(E,1) = 0.65551438857 for y²=x³−x; L′(E,1) for 37a | Birch–Swinnerton-Dyer 1965; LMFDB |
| finite-field RH: Frobenius eigenvalues have modulus √p for all 45 good primes < 200 | Hasse 1933, Weil 1948, Deligne 1974 |
| Gram's law first fails at Gram index 126; fails 20.6 % of the time by 10⁵ | Hutchinson 1925 |
| base-27 structure, musical ratios, geodesic-length = ln p: all VOID with base-rate controls; the last is the identity 2 ln εₜ ≈ ln(t²−2) | — |

## Predictions that failed (kept)
Fable: L3 ordering self-correction (registered order actually held); L1 "exactly 200 dips" (202); smooth-count sup 1.01 (1.234); comb 571 (572); λ₁₀₀ tail power; Maass parity labels reversed; "Selberg control shows no closeness" (identity); Lehmer pair top-5 (6th); KS<0.3 and pair-corr<0.02 missed by 0.002/0.003; KS falling monotonically above 10¹² (noise floor); valley fraction ≈½ (measured ⅓); blanket "γ² horizon for every criterion" (ill-posed).
Codex: 0.3912 attributed to Fable (was Antigravity's uncommitted text); "Turing-style" independence overstated; rogue horizon would move by >25 (it didn't); permuted-spacing control (invariant); Weyl unfolding would flip Poisson-vs-GUE in one parity (it didn't).
Antigravity (audited, not a participant in the ledger): 15 "CONFIRMED" → 2 survivors; L(E,1)=0.3912, Li truncation, fabricated L6 control, "conservation of energy enforces ½" all VOID.

## The three-yeses table
| candidate | self-adjoint, discrete, zeros as spectrum | chaotic without arithmetic degeneracy | orbits of length ln p |
|---|---|---|---|
| plain xp, any boundary | yes (twisted-periodic) | no (comb) | no |
| random matrices (GUE) | yes | yes | no primes at all |
| modular surface Laplacian | yes, proven critical line | no (Poisson) | no (lengths 2 ln ε_d) |
| Berry–Keating cutoff | UNVERIFIED | no | no |
| Bender–Brody–Müller 2017 | UNVERIFIED (domain disputed) | no | no |
| Weil / Connes–Consani | UNVERIFIED | no | prime support, not orbits |
| finite-field Frobenius (the proven case) | yes | n/a | yes, in its own world |
No row over the integers has three yeses. That row is the Riemann Hypothesis.

## The open problem in one sentence
Find a self-adjoint operator whose spectrum is chaotic without arithmetic degeneracy and whose closed orbits have lengths ln p, or find the positivity that makes such an operator unnecessary; the finite-field case shows both pieces exist there and neither is known over the integers.
