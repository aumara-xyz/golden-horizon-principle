# D14 — "touch one prime and the whole pattern moves" (Fable, 2026-09-11)
Predictions first (PREDICTIONS.md). Floating numpy; d14_results.log/json; post-hoc numbers in d14_posthoc.log/json, labeled.

## Test A — VOID by its own kill rule; prediction FAILED
Predicted: the negative direction of the θ = 0.9 perturbed form at L = 0.60 peaks in frequency near t₁ = 2π/log 2 = 9.07. Measured peak: 5.11 (even), 4.07 (odd). Fraction of spectral mass within ±1.5 of 9.07: perturbed 0.135 vs authentic 0.035 (even, 4×) but 0.022 vs 0.193 (odd). Peak not near 9.07 in either parity → VOID as preregistered.
Why the design was wrong (post-hoc, not a held prediction): (i) at L = 0.60 the frequency resolution of a compactly supported wave is ≈ π/L ≈ 5, so 9.07 and 0 cannot be separated; (ii) scaling every visible power of 2 by θ corresponds to ζ(s)(1 − 2^{−s})^{1−θ}, whose injected "zeros" sit at s = 2πik/log 2 for ALL integers k including k = 0, i.e. one at s = 0 with weight (1 − θ), whose effect is at t ≈ 0, not 9.07; (iii) the sign: D9/D13 show the prime-2 term HELPS the near-null waves (their correlation at shift log 2 is negative), so weakening it hurts waves with cos(t log 2) ≈ −1, i.e. t ≈ π/log 2 = 4.53, 3π/log 2 = 13.6. Post-hoc measurement at L = 0.60: ⟨cos(t log 2)⟩ over |F|² of the perturbed minimizer = see d14_posthoc.log; the peaks at 5.1 and 4.1 are consistent with the anti-node 4.53 broadened by the ≈5 resolution. This is an explanation offered after the fact; it is not confirmed by a preregistered test and is recorded as UNVERIFIED.
What survives independent of the design error: the perturbed form is exactly the Weil form of a Beurling-type generalized prime system (ζ·(1 − 2^{−s})^{1−θ}), and such systems are the classical setting where the analogue of RH fails (Beurling generalized primes; Diamond–Montgomery–Vorhauer, cited from memory, UNVERIFIED). D13's "no slack" is the finite-window face of that: perturb the arithmetic and the spectral side acquires off-line content the form detects.

## Test B — the hard object is low-dimensional (tensor-network analogy)
| L | intrinsic modes of the minimizer, even / odd (1 − 1e-12 of norm) | certificate modes N | T |
|---|---|---|---|
| 0.4 | 17 / 16 | 68 | 60 |
| 0.5 | 17 / 19 | 76 | 60 |
| 0.6 | 25 / 27 | 95 | 77 |
| 0.7 | 13 / 47 | 170 | 155 |
Prediction "d ≤ 40 everywhere" FAILED for odd at L = 0.7 (47); "grows at most linearly while N grows with e^{B_L}" HELD. The near-null wave needs 13–47 Legendre modes; the certificate carries 68–170 because the envelope threshold T, not the object, sets the cost. Reading: as in the Flatiron/D-Wave result, the apparent hardness is not high intrinsic complexity of the object (its "entanglement" is low); it is exact cancellation inside a small subspace. Compression of the wave is therefore not the bottleneck and cannot be the missing idea; the missing idea is why the cancellation happens.

## Ledger
| prediction | outcome |
|---|---|
| A: perturbed minimizer peaks near 9.07 | FAILED; test VOID by kill rule |
| A: fraction near 9.07 ≥ 3× control | HELD even (4×), FAILED odd |
| B: d(L) ≤ 40 | FAILED (odd 0.7: 47) |
| B: d grows ≤ linearly while N grows exponentially | HELD |
No novelty claimed; nothing certified; nothing about other L or RH.
