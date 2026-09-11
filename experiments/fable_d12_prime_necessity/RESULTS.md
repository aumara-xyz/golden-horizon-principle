# D12 — where the primes become load-bearing (Fable, 2026-09-11)
Predictions committed first (PREDICTIONS.md). Floating double precision (numpy), exploratory; d12_results.log/json (coarse grid, T = max(1.3·T_env, 60)), d12_fine.log/json (crossings, T = 60). No zero ordinates, no φ, no new models. MEASURED (floating) throughout; nothing certified.

## Result
| form | even sector | odd sector |
|---|---|---|
| prime-free (archimedean + pole) positive for all L ≤ log2/2 = 0.3466 | yes | yes (consistency with Connes–Consani 2021: HELD) |
| first L where the prime-free form turns negative, L_c | 0.407–0.409 | 0.369–0.371 |
| prime-free minimum at L = 0.7 | −0.249 | −0.735 |
| full form minimum at L = 0.7 | +2.4e-13 | +1.5e-10 |
| archimedean only (no pole) | negative at every L (−1.1 to −2.3) | POSITIVE for L ≤ 0.375, negative beyond |
| decay of the full minimum, fit on 0.35 ≤ L ≤ 0.70 | λmin ≈ e^{17.1 − 64.1 L} (factor ≈ 600 per 0.1 in L) | λmin ≈ e^{18.9 − 57.4 L} (factor ≈ 310 per 0.1) |
Beyond L ≈ 0.725 the full-form minimum is below the double-precision noise floor (±1.5e-14) and its sign is unresolved here; the certified values at L = 0.7 (1.03e-13 even, 5.86e-11 odd) sit on the fitted lines to within a factor 2–3 (different T).

## Reading
1. The Connes–Consani room (half-width 0.3466) is, to within 7 % (odd) and 18 % (even), the LARGEST room in which the primes can be ignored. As soon as the shift log 2 fits inside the support, the archimedean-plus-pole form fails within a few hundredths of L, while the full form survives. The primes are not a perturbation on top of a structurally positive background: from L ≈ 0.37 on, they cover a deficit of order 0.01–0.9 and leave a margin of 1e-4 down to 1e-13.
2. Any structural extension of Weil positivity beyond 0.37 must therefore use the prime terms with O(1) accuracy, in the odd sector first. "Bound the primes crudely and let the archimedean term carry it" is dead by measurement, which is consistent with D8 (a better prime bound is useless because the danger is not there) and complementary to it: the prime term must be used exactly, not bounded.
3. The margin of the full form shrinks by roughly e^{−6} per 0.1 of L. Extrapolated (not a prediction, a fit) it reaches 1e-18 near L = 0.83 and 1e-30 near L = 1.0 — the same doubly-hard regime Zhu's Theorem 1.4 describes from the other side. The room does not gradually get harder; the margin collapses exponentially in L while the deficit the primes must cover grows linearly.
4. Odd-sector surprise: without the pole the odd archimedean form is positive in small rooms (the odd pole is −2S² and only hurts), so for odd functions in rooms below 0.375 positivity needs neither pole nor primes. The three-way balance is a large-room phenomenon in both parities.

## Prediction ledger
| prediction | outcome |
|---|---|
| prime-free form ≥ 0 for L ≤ L₀, both parities | HELD |
| L_c(odd) ∈ (0.40, 0.60) | FAILED: 0.370 (primes needed almost immediately) |
| L_c(even) ∈ (0.45, 0.65) | FAILED: 0.408 |
| L_c(odd) < L_c(even) | HELD |
| full form positive on the grid | HELD to L = 0.725; unresolved (noise floor) beyond |
| archimedean-only negative at every L | FAILED for odd, L ≤ 0.375 (positive); HELD for even |

## Named target for any structural proposal
Produce an inequality valid for all f supported in [−L, L] that (i) reduces to the Connes–Consani archimedean argument at L ≤ 0.3466, (ii) uses the shift-log-2 term with enough precision to close a deficit of 0.0145 at L = 0.375 (odd) and 5.6e-5 at L = 0.409 (even), and (iii) does not lose more than the margins tabulated above. This lab can falsify any candidate on this grid in under two minutes.
