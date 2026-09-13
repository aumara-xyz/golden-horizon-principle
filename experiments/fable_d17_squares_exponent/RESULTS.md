# D17 — prime powers carry weight of their own; the exponent 1/2 is where the two parities agree (Fable, 2026-09-13)
Predictions first (PREDICTIONS.md). Floating numpy (D15/D16 machinery), noise floor 3e-14; d17_results.log/json. Both tests are labeled mutations: the mutated forms are not explicit formulas of any L-function. MEASURED (floating); nothing certified.

## Test A — remove all prime POWERS (k ≥ 2) versus remove all PRIMES (k = 1)
| form, L | powers visible | base (even/odd) | no powers | no primes |
|---|---|---|---|---|
| ζ, 0.7 | 4 | 2.4e-13 / 1.5e-10 | −8.4e-13 / −1.2e-4 | −0.26 / −0.74 |
| χ₋₄, 1.2 | 9 | 1.3e-11 / 1.6e-8 | −3.0e-3 / −8.9e-2 | −0.44 / +0.29 |
| χ₋₃, 1.1 | 4, 8 | 9.8e-13 / 9.1e-10 | −0.16 / −0.32 | −0.87 / +0.35 |
| χ₅, 1.2 | 4, 8, 9 | 2.9e-10 / 2.4e-7 | −8.6e-2 / −0.31 | −1.52 / +0.68 |
Removing only the powers breaks positivity in every form, in both parities except ζ's even sector (which goes negative by 1e-12, still a sign flip). The squares and cubes are not a correction on top of the primes; they are load-bearing at the same scale, as the √x size of ψ(x) − θ(x) suggests. Removing the primes is far worse for the even sector (−0.26 to −1.52); for the Dirichlet forms the odd sector becomes positive without primes because their χ = −1 primes were hurting it (D15/D16 sign rule).

## Test B — weight exponent σ in n^{−σ} (0.5 = critical line), all else fixed
| σ | ζ, L = 0.6 (even / odd) | χ₋₄, L = 1.0 (even / odd) |
|---|---|---|
| 0.45 | −1.8e-2 / −9.1e-3 | −3.7e-2 / −2.6e-2 |
| 0.48 | −6.9e-3 / −2.1e-3 | −2.1e-3 / −1.0e-2 |
| 0.49 | −3.4e-3 / −2.0e-4 | **+7.7e-4** / −4.8e-3 |
| 0.50 | +7.6e-10 / +2.8e-7 | +5.0e-7 / +2.6e-4 |
| 0.51 | −2.9e-4 / −2.6e-3 | −1.9e-3 / **+5.2e-3** |
| 0.52 | −6.3e-4 / −6.0e-3 | −4.2e-3 / +1.0e-2 |
| 0.55 | −1.8e-3 / −1.7e-2 | −1.2e-2 / +2.4e-2 |
σ = 0.50 is the only grid point positive in BOTH parities, for both forms. For χ₋₄ each parity alone would tolerate a shift, but in opposite directions: the even sector prefers σ < 0.5, the odd sector σ > 0.5, and the critical exponent is exactly where their demands intersect. For ζ both parities fail on both sides.

## Prediction ledger
| prediction | outcome |
|---|---|
| A: powers alone are load-bearing in every form | HELD (4/4) |
| A: primes alone far worse, some parity < −0.3 | HELD (4/4) |
| B: σ = 0.5 unique positive point on the grid, both forms, even sector | HELD for ζ; FAILED for χ₋₄ (σ = 0.49 even positive). Unique point positive in BOTH parities: HELD for both forms |
| B: both directions fail at ±0.01 | HELD for ζ; for χ₋₄ each direction fails in one parity |
| B: σ < 0.5 fails harder than σ > 0.5 | HALF-HELD: true for the even sector, reversed for the odd sector, in both forms |
Kill rule (some σ ≠ 0.5 positive in both parities) not triggered.

## Reading
1. Squares and cubes of primes are not small print. In the compact window they hold up the form exactly like primes do, consistent with the classical fact that their contribution to the prime count is of size √x, the same order as the error RH controls.
2. The exponent 1/2 in the weights is rigid, but the mechanism is more interesting than "any deviation fails": the two parity sectors want to move in opposite directions, and 1/2 is the unique compromise. This is a finite-window shadow of the functional equation's symmetry point s ↔ 1 − s, and a concrete, checkable rule for any structural proposal: it must be parity-symmetric in exactly this sense.
3. No statement about RH follows; the mutated forms are not L-functions. This extends the D12–D16 map: every arithmetic ingredient (each place, each power, the exponent) is used at full precision by the compact-window form.

## Correction (appended 2026-09-13 after D21; nothing above edited)
The deletion and reweighting results in this file are statements about the fixed- or moving-ruler REDUCED form R_{L,T}, whose negative values are not negative witnesses for the full Weil form W (W − R_T is a discarded nonnegative tail). D21 (experiments/fable_d21_test1) scored frozen waves exactly with complete tails at ζ, L = 0.7: deleting prime 2 and removing all primes give certified W-negative witnesses in both parities (those claims stand for W); deleting the marginal power n = 4 gives reduced scores that are negative (odd) or ruler-dependent (even) while the exact W on the tested waves is POSITIVE. Claims here about newly entered / marginal places being "load-bearing" are therefore established for R only and UNVERIFIED for W; where D16/D17 recomputed B, β, T after a mutation, the ruler moved with the wave (Astra D20 critique, accepted).
