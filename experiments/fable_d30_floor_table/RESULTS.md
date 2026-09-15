# D30 Task 1–2 (Fable, Mac, zero cost) — the certified visible-form floor table, and the profile on certified numbers (2026-09-15)
Predictions first (PREDICTIONS.md). Certificates: d30_certify.py (d22 machinery with the prime set filtered to visible shifts log n < 2L; D24 §4.1 strengthening), 192-bit balls, eigenbasis Gershgorin finite floor, three Schur tails with the visible B, D24 §3.2 conservative allowance 6·N·q_max subtracted (it is ≤ 1.6e-19 everywhere, immaterial), shifted checker ACCEPT in every case. Interpreter: fresh venv, python-flint 0.6.0, arm64 Mac (the D22 certificates were built on the same machine; the Nebius box independently reproduced three of these floors in D26/D27 to all printed digits). MEASURED (interval).

## Certified all-function lower bounds ℓ on R_{L,T}, hence on W (visible form)
| L, T, modes | even ℓ | odd ℓ | visible shifts | gain over D22 (even / odd) |
|---|---|---|---|---|
| 0.4, 160, 160 | 1.723088702e-4 | 1.417157652e-2 | log 2 | +18.9 % / +14.3 % |
| 0.5, 160, 160 | 8.769318724e-7 | 1.809341968e-4 | log 2 | +22.7 % / +27.3 % |
| 0.6, 160, 160 | 1.311625544e-9 | 4.890293079e-7 | log 2, log 3 | +19.1 % / +18.4 % |
| 0.7, 160, 160 | 2.671671167e-13 | 1.585963690e-10 | log 2, log 3, log 4 | 0 / 0 (nothing invisible) |
| 0.7, 240, 192 | 3.375817505e-13 | see table.log / JSON (odd T240 finished after write-up; value in d30_cert_odd_L0.7_T240_N192.json) | log 2, log 3, log 4 | 0 |
The even 0.4 and odd 0.4/0.5 floors reproduce the Nebius D26/D27 certified values to every printed digit. These replace D22's void endpoints. Kill rule not triggered (no visible floor below its D22 counterpart).

## Profile on certified visible floors (T = 160), four points per parity
| parity | certified log-slopes | linear fit (slope, rel RMS error) | e^{2L} fit (C, rel RMS error) |
|---|---|---|---|
| even | 52.8, 65.1, 85.0 | 67.4 constant, 0.200 | A = 16.11, C = 11.08, **0.034** |
| odd | 43.6, 59.1, 80.3 | 60.8 constant, 0.268 | A = 18.40, C = 10.03, **0.091** |
Slopes increase with L in both parities; the e^{2L} model fits within 10 % and the linear model fails. This supersedes D23 §A (which was fitted on void D22 endpoints) with the same qualitative conclusion and nearly the same C. Four points, two parameters: a model comparison, not an asymptotic law.

## Prediction ledger
| prediction | outcome |
|---|---|
| visible floors exceed D22 by 0–25 % at 0.4–0.6, equal at 0.7 | HELD except odd L = 0.5 at +27.3 % (narrow miss, favorable direction) |
| slopes increase with L, both parities | HELD |
| e^{2L} fit ≤ 10 %, linear fails | HELD (3.4 %, 9.1 %) |
| T = 240 exceeds T = 160 at L = 0.7 by 20–30 % | HELD even (+26.4 %); odd recorded in JSON |
No RH content; five certified floors per parity for the compact-window Weil form at ζ, visible reduction, and a certified profile that falls faster than exponentially in L.
