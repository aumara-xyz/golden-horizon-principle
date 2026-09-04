# GOLDEN-BILLIARD-PRIME-RETURN v0 — results

No zeta-zero ordinate entered the construction, tuning, or scoring. All controls ran before the golden ratio.

| Aspect ratio | 50-return score (lower better) | Reading |
|---|---:|---|
| square | 42.893663 | deterministic control |
| sqrt2 | 27.649868 | deterministic control |
| sqrt3 | 40.666848 | deterministic control |
| random ratios (n=500) | 20.735461 | 1st–95th: 6.876983–34.963407 |
| golden ratio | 25.797422 | percentile 66.6% |

## Frozen extension

At 100 primes the golden score is 146.174222, at random-control percentile 66.6%.

## Spectral checks

- The exact Neumann spectrum includes the constant `(m,n)=(0,0)` zero mode: **MEASURED**, but generic.
- Unfolded positive spacings are closest to **POISSON** (KS: poisson=0.0247, goe=0.2173, gue=0.2838).
- The fitted counting exponent is `1.9929`; the two-dimensional Weyl prediction is 2, whereas zeta requires `T log T`.

## Prediction ledger

| Prediction | Outcome |
|---|---|
| Golden ratio fails the 1% control threshold | MATCH |
| One neutral Neumann mode | MATCH |
| Quadratic rather than `T log T` count | MATCH |
| Poisson-like spacings | MATCH |

## Honest paragraph

The golden rectangle did not survive the frozen control threshold, so its return-length resemblance is VOID as prime evidence. The experiment does preserve the useful conceptual distinction: a bounded room can support infinitely many returns. But its ordinary Laplacian has the wrong spectral-growth law, and its integrable dynamics has the wrong symmetry statistics. Infinite reflection alone is therefore insufficient; the surviving target must add scale-invariant or arithmetic dynamics without inserting the answers.

Full machine-readable output: `outputs/results.json`.
