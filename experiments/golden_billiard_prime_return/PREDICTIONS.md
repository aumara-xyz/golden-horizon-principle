# GOLDEN-BILLIARD-PRIME-RETURN v0 — preregistration

- Date locked: 2026-09-04
- Lane: Riemann adjacency; analogue and falsification instrument only.
- No zeta-zero ordinate may enter construction, parameter selection, or scoring.
- Controls run before the golden-ratio score.

## Frozen construction

Use a rectangular billiard of side lengths `a=1`, `b=r` with reflecting (Neumann)
boundary. Its primitive unfolded return paths are indexed by coprime non-negative integer
pairs `(m,n)`, excluding `(0,0)`, with lengths

`L_(m,n) = 2 sqrt((m a)^2 + (n b)^2)`.

Enumerate `0 <= m,n <= 256`, retain `gcd(m,n)=1`, sort distinct lengths, and take the
first 50. Apply exactly one scale by matching the shortest return to `log(2)`. Compare the
ordered 50 returns to the logarithms of the first 50 primes. The primary score is median
absolute error divided pointwise by the local adjacent spacing of `log(prime)`; smaller is
better. Rankwise comparison prevents a dense orbit catalogue from winning by nearest-
neighbor saturation.

## Controls

Controls are evaluated first:

1. Square `r=1`.
2. `r=sqrt(2)` and `r=sqrt(3)`.
3. Five hundred aspect ratios sampled log-uniformly on `[1,2]`, seed 20260904.

The golden result survives only if its score is below the 1st percentile of the random
aspect-ratio scores and remains there when the target is extended from 50 to 100 primes.

## Predictions

1. **PREDICTED:** `r=phi` will not survive the control threshold.
2. **PREDICTED:** the Neumann billiard has one constant zero-frequency mode, but it is
   generic to connected Neumann chambers.
3. **PREDICTED:** infinitely many reflected paths do not fix the density obstruction. A
   two-dimensional rectangular Laplacian has `N(k) ~ Area*k^2/(4*pi)`, not the
   Riemann-von Mangoldt `T log T` law.
4. **PREDICTED:** the integrable rectangle has Poisson-like rather than GUE-like unfolded
   spacings once exact degeneracies are handled.

## Interpretation rule

A failed alignment makes the golden rectangle `VOID` as prime-spectrum evidence. A
survivor would be `UNVERIFIED` pending a second implementation, alternative prime windows,
and a pseudo-prime control. Under no outcome is a numerical match an RH result.
