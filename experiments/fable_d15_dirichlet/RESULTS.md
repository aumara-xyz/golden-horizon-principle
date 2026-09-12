# D15 — the compact-window phenomenology is not special to ζ: Dirichlet L-functions (Fable, 2026-09-13)
Predictions first (PREDICTIONS.md). Floating numpy; d15_results.log (grid), d15_slack.log/json (slack and removal tests). The grid run was cut off by the session after L = 1.2 (L = 1.3, 1.4 not computed; its JSON was not written); the log is the record. ζ control (same code path) reproduces D12 at every L to within display precision (e.g. 2.7e-13 at L = 0.7): kill rule not triggered. MEASURED (floating); nothing certified; no zero ordinates, no φ.

## λmin of the compact-window Weil form (even / odd sector)
| L | ζ | χ₋₄ (q=4, odd) | χ₋₃ (q=3, odd) | χ₅ (q=5, even) |
|---|---|---|---|---|
| 0.3 | 7.1e-3 / 2.2e-1 | 5.5e-1 / 1.6 | 2.6e-1 / 1.3 | 4.8e-1 / 1.8 |
| 0.5 | 7.3e-7 / 1.5e-4 | 1.4e-1 / 1.1 | 2.0e-2 / 3.8e-1 | 8.7e-2 / 8.8e-1 |
| 0.7 | 2.7e-13 / 1.7e-10 | 6.1e-3 / 3.3e-1 | 1.7e-4 / 2.5e-2 | 4.2e-3 / 1.7e-1 |
| 0.9 | — | 1.9e-5 / 6.3e-3 | 4.8e-8 / 2.4e-5 | 3.3e-5 / 7.7e-3 |
| 1.0 | — | 5.0e-7 / 2.6e-4 | 5.7e-10 / 3.9e-7 | 1.8e-6 / 5.0e-4 |
| 1.1 | — | 3.9e-9 / 3.5e-6 | 9.8e-13 / 9.1e-10 | 4.1e-8 / 2.5e-5 |
| 1.2 | — | 1.3e-11 / 1.6e-8 | 2e-15 (noise) / 4.9e-13 | 2.9e-10 / 2.4e-7 |
Decay of the even margin per unit L (fit 0.3–1.2): χ₋₄ 27, χ₋₃ 36, χ₅ 24, versus ζ 64. Positive on the whole computed grid (χ₋₃ reaches the double-precision floor at 1.2).

## Slack test at the largest L with margin in (1e-10, 1e-5)
| character, L, prime | weight ×1.0 (even / odd) | ×0.999 | ×0 |
|---|---|---|---|
| χ₋₃, L = 0.9, prime 2 (χ = −1) | +4.8e-8 / +2.4e-5 | −3.4e-4 / +4.5e-4 | −0.59 / +0.24 |
| χ₋₄, L = 1.0, prime 3 (χ = −1) | +5.0e-7 / +2.6e-4 | −1.5e-4 / +8.8e-4 | −0.53 / +0.60 |
| χ₅, L = 1.0, prime 2 (χ = −1) | +1.8e-6 / +5.0e-4 | −4.2e-4 / +7.8e-4 | −0.65 / +0.19 |
A 0.1 % change of one prime weight flips the even sector negative for all three characters. The odd sector moves the other way: for these characters the sign-flipped prime (χ(n) = −1) helps one parity and hurts the other, and the parity that it hurts is the one at the edge.
Small-room check (L = 0.5, remove prime 2): χ₋₃ even +2.0e-2 → −0.15, odd +0.38 → +0.82; χ₅ even +8.7e-2 → −0.11, odd +0.88 → +1.32. Even sector needs the negative-weight prime already at L = 0.5; the odd sector is better off without it.

## Prediction ledger
| prediction | outcome |
|---|---|
| (1) positive to L = 1.2 for χ₋₄ and χ₅ | HELD (and χ₋₃ to the noise floor) |
| (2) margin decays exponentially with rate 20–45 per unit L | HELD (24–36; ζ is 64) |
| (3) removing a χ = −1 prime RAISES λmin at small L | HALF-FAILED: true for the odd sector, false for the even sector, at L = 0.5 for both characters |
| (4) no-slack once the margin is small (×0.999 flips sign) | HELD, all three characters, even sector |
| ζ control reproduces D12 | HELD |

## Reading
1. The log q term makes the room bigger for free: every Dirichlet L-function tested stays positive to L ≈ 1.2, twice ζ's reach, with the same exponential collapse of the margin (rate 24–36 instead of 64). The phenomenology — exponential margin decay, primes becoming load-bearing, no slack in the weights — is universal across the family, not a peculiarity of ζ's pole.
2. The pole is not what makes ζ hard. L(s,χ) has no pole and shows the same behavior later, with the conductor's log q playing the role of extra positive background. So the D12 "three-way balance" is really two-way (archimedean+conductor vs exact primes) with the pole as ζ's substitute for a conductor. That reframes the named target from D12: what must be understood is the archimedean term against the exact prime data; the pole is ζ's version of log q.
3. Parity asymmetry: a prime with χ(n) = −1 enters with the opposite sign, so it helps one parity sector and hurts the other; the endangered sector is always the one it hurts. This is a clean, checkable pattern for anyone proposing a structural argument: the sign structure of the character decides which sector is critical.
4. Nothing here bears on GRH or RH. It is a map of where the finite method's margin lives across the simplest family, and it says the map is the same everywhere. That universality is the one observation from D12–D15 I would put in front of a number theorist.
