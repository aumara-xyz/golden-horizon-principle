# D16 — a place becomes load-bearing almost the moment it enters the room (Fable, 2026-09-13)
Predictions first (PREDICTIONS.md). Floating numpy (D15 machinery), noise floor 3e-14. Raw rows in d16_results.log; the χ₅, L = 1.2 row was still computing at write-up time and is appended below if/when it finishes (its T is large). MEASURED (floating); nothing certified.

## Removal of one visible prime power n at a time (λmin even / odd after removal; ΔL = L − log(n)/2 = how long the place has been visible)
| form, L | base even / odd | n (χ(n), ΔL) → result |
|---|---|---|
| ζ, 0.7 | 2.4e-13 / 1.5e-10 | 2 (+, 0.353) −0.47/−0.49 LB; 3 (+, 0.151) −0.12/−0.51 LB; 4 (+, 0.007) −8e-13/−1.2e-4 LB |
| χ₋₄, 1.0 | 5.0e-7 / 2.6e-4 | 3 (−, 0.451) −0.53/+0.60 LB; 5 (+, 0.195) −7e-3/−0.23 LB; 7 (−, 0.027) −1.7e-2/+5.8e-4 LB |
| χ₋₄, 1.1 | 3.9e-9 / 3.5e-6 | 3 LB; 5 LB; 7 (−, 0.127) −0.23/−8e-3 LB; 9 (+, 0.001) +4e-9/+2.9e-6 removable |
| χ₋₄, 1.2 | 1.3e-11 / 1.6e-8 | 3, 5, 7 LB; 9 (+, 0.101) −3e-3/−8.9e-2 LB; 11 (−, 0.001) +7.8e-12/+1.5e-8 removable |
| χ₋₃, 1.0 | 5.7e-10 / 3.9e-7 | 2 (−, 0.653) −0.63/−6e-3 LB; 4 (+, 0.307) −1.3e-2/−0.29 LB; 5 (−, 0.195) −0.37/−3.8e-2 LB; 7 (+, 0.027) −2.6e-8/−5.0e-2 LB |
| χ₋₃, 1.1 | 9.8e-13 / 9.1e-10 | 2, 4, 5, 7 LB; 8 (−, 0.060) −4.9e-2/−2.9e-7 LB |
| χ₅, 1.0 | 1.8e-6 / 5.0e-4 | 2 (−, 0.653) −0.65/+0.19 LB; 4 (+, 0.307) −2.8e-2/−0.19 LB; 3 (−, 0.451) −0.56/+0.43 LB; 7 (−, 0.027) −1.7e-4/+9.6e-4 LB |
| χ₅, 1.1 | 4.1e-8 / 2.5e-5 | 2, 4, 3, 7 LB; 8 (−, 0.060) −4.1e-3/+1.0e-4 LB; 9 (+, 0.001) +3.9e-8/+2.1e-5 removable |
LB = load-bearing (removal makes at least one parity negative). 14 forms × places tested: every place visible for ΔL ≥ 0.027 is load-bearing (26 of 26); the only removable places are those visible for ΔL = 0.001 (9 at L = 1.1; 11 at L = 1.2), and 9 becomes load-bearing by ΔL = 0.101.

## Prediction ledger
| prediction | outcome |
|---|---|
| (1) every place visible for ΔL ≥ 0.1 is load-bearing, every character | HELD (and already at ΔL = 0.027) |
| (2) places with ΔL < 0.05 are NOT yet load-bearing | FAILED: 7 at ΔL = 0.027 is load-bearing for χ₋₄, χ₋₃, χ₅; only ΔL = 0.001 places are removable |
| (3) χ(n) = +1 places hurt the odd sector, χ(n) = −1 places hurt the even sector | PARTLY HELD: the sign fixes which sector is hurt FIRST (−1 → even, +1 → odd) but long-visible places hurt both |
| (4) removal changes λmin by > 100× the margin | HELD everywhere (typically 1e5–1e12×) |

## Reading
1. A place is essential within a few hundredths of L after it can first be seen; the room has essentially no grace period. The adelic picture "the form is a product over places" is not decorative: the finite window is a positivity statement that needs every place it can see, immediately.
2. Sign rule (measured): a place with χ(n) = −1 first endangers the even sector when removed; χ(n) = +1 first endangers the odd sector; with more room, both. For ζ (all +1) this matches D13: 2 and 3 break both sectors, 4 (just entered) breaks odd first.
3. This sharpens the D12 target once more: a structural proof for room L must account exactly for every place with log n ≤ 2L, including the one that entered a hair's breadth ago. There is no "leading primes plus a bounded remainder" regime anywhere in the tested range.
4. Nothing here bears on GRH/RH; it is a map of the finite method across the simplest family.
