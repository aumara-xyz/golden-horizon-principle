# D33 (Fable, Mac) — is the L = 0.6 edge floor-limited? Partly. (2026-09-15; T = 320 rows pending, appended when done)
Predictions first (PREDICTIONS.md). Certificates: d30_certify.py (visible shifts, PREC env override), frozen D32 winners' W_hi reused with no rescoring. MEASURED (interval) for floors; ratios are arithmetic on certified endpoints.

| L = 0.6 | ℓ at T = 160 (D30) | ℓ at T = 240, 192 modes | ℓ_240/ℓ_160 | D32 winner W_hi | W_hi/ℓ_160 (D32) | W_hi/ℓ_240 | verdict |
|---|---|---|---|---|---|---|---|
| odd | 4.890293e-7 | 5.342321e-7 | 1.0924 | 6.096365e-7 | 1.2466 | **1.1411** | open |
| even | 1.311626e-9 | 1.434321e-9 | 1.0935 | 1.652266e-9 | 1.2597 | **1.1520** | open |
T = 320 with 256 modes at 192 bits FAILED (NO_VERDICT): the closed-form Bessel evaluation near order ≈ argument (T·L = 192) loses more than 192 bits and one entry overflowed; kept as d33_cert_odd_L0.6_T320_N256_FAILED_192bit.json. Rerun at 320 bits in progress (run320.log); the rows will be appended.

## Reading so far
1. The floor at L = 0.6 IS T-limited: raising T from 160 to 240 lifts the certified all-function floor by 9.2 % (odd) and 9.4 % (even) with no change to W. That is real slack in the D30 floors and it moves the brackets from 1.25/1.26 to 1.14/1.15 without touching the candidates.
2. But it is not the whole gap. My prediction ℓ_240/ℓ_160 ∈ [1.15, 1.35] FAILED (measured 1.09); the kill threshold (< 1.05) was not reached, so the hypothesis survives in weakened form: roughly 9 of the 25 points are floor slack at this T step, the rest sit in the candidate or in further T-dependence. The T = 320 rows decide how much more the floor can give.
3. At L = 0.7 the same step gave +26 %; at 0.6 it gives +9 %. The floor's T-sensitivity grows with L, consistent with the reduced form undercharging the boundary-jump tail of its own minimizer more severely as the margin collapses.
4. New toolchain trap recorded (precision loss of the closed-form Bessel near n ≈ |z|; use ≥ 320 bits for T·L ≳ 170).

**Provenance note (2026-09-15):** the 320-bit T=320 rerun finished (odd 587 s, even 517 s; run320.log "RUN320 DONE"). Its certificates d33_cert_{odd,even}_L0.6_T320_N256.json and logs log_{odd,even}_T320_320bit.log are the inputs to the D34 axis step (ℓ_320/ℓ_240 = 1.036) and were committed with this note; the D34/D35 rows live in experiments/fable_d34_*/ and fable_d35_*/.
