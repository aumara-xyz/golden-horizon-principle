# D13 — how much of each prime is load-bearing? (Fable, 2026-09-11)
Predictions first (PREDICTIONS.md). Floating numpy, T = max(1.3·2π e^{B_L}, 60), authentic β kept, noise floor 3e-14. d13_results.json / .log. MEASURED (floating); nothing certified; no zero ordinates, no φ.

## Test 1 — minimal weight of prime 2 (θ* = smallest fraction of the authentic n = 2 weight that keeps λmin > 0)
| L | even θ* | odd θ* | λmin at θ = 1 (even / odd) |
|---|---|---|---|
| 0.40 | 0.000 (not needed) | 0.826 | 1.5e-4 / 1.3e-2 |
| 0.45 | 0.818 | 0.984 | 1.2e-5 / 2.0e-3 |
| 0.50 | 0.980 | 0.999 | 7.3e-7 / 1.5e-4 |
| 0.55 | 0.999 | 1.000 | 2.7e-8 / 7.7e-6 |
| 0.60 | 1.000 | 1.000 | 7.6e-10 / 2.8e-7 |
From L ≈ 0.55 on, the authentic weight 2log2/√2 is the minimal weight to three decimals: removing 0.1 % of the prime-2 term breaks positivity. There is no slack.

## Test 2 — which prime powers are essential at L = 0.7
| subset on | even λmin | odd λmin |
|---|---|---|
| none | −0.253 | −0.740 |
| {2} | −0.108 | −0.515 |
| {3} | −0.454 | −0.489 |
| {4} | −0.258 | −0.736 |
| {2,3} | +3.1e-13 | −1.95e-5 |
| {2,4} | −0.116 | −0.508 |
| {3,4} | −0.459 | −0.489 |
| {2,3,4} | +2.4e-13 | +1.5e-10 |
Even needs 2 and 3; odd needs 2, 3 AND 4. The prime power 4, whose shift log 4 = 1.386 barely fits in 2L = 1.4 and whose contribution at the D9 odd candidate was 2.6e-9, is nevertheless load-bearing: without it a different vector drives the odd form to −1.95e-5.

## Test 3 — controls
L = 0.30 (no prime fits): λmin identical for every θ in both parities (7.100085024460258e-3, 0.21608372944630191). Mutation at L = 0.5, shift 1.1·log 2 with the authentic weight: no θ ∈ [0,1] restores positivity in either parity (θ* = None). The shift must be log 2 exactly; a 10 % wrong shift is not fixable by any weight.

## Prediction ledger
| prediction | outcome |
|---|---|
| θ* increases with L, both parities | HELD |
| odd θ*(0.5) > 0.8 | HELD (0.999) |
| even θ*(0.5) ∈ (0.3, 0.8) | FAILED (0.980) |
| both θ* > 0.9 at L = 0.60 | HELD (1.000, 1.000) |
| at L = 0.7 only subsets containing 2 positive; {2} alone positive | FAILED: {2} alone negative in both; even needs {2,3}, odd needs {2,3,4} |
| {3,4} negative | HELD |
| L = 0.30 control identical | HELD |
| mutation moves θ* by > 0.1 | HELD in the strongest form (no θ works) |

## Reading
Weil positivity in these rooms is razor-tight in the arithmetic data: the exact prime-power weights 2Λ(n)/√n and the exact shifts log n are all needed, with no measurable slack, from L ≈ 0.55 on, and every visible prime power (including the smallest, most marginal one) is essential at L = 0.7. This is what "positivity ⇔ RH" predicts qualitatively — a form built from wrong primes has no reason to be positive — but here it is measured: the cushion between "true arithmetic" and "broken" is 1e-13 wide and closes at the first 0.1 % perturbation. Consequences for the named target of D12: a structural proof beyond L ≈ 0.4 cannot bound, average, drop, or approximate any prime term; it must use the exact explicit-formula weights and shifts as identities. Nothing here bears on other L or on RH.
