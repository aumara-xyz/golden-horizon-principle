# Post-hoc parameter-matched control audit

Status: **MEASURED**. This audit closes the control-coverage gap for every
authentic N-path spectrum outside `x=13` that meets the frozen landing rule on
ordinates 20--50. It was designed after those matches were known, so it is a
post-registration audit and not a replacement for `PREDICTIONS-codex-r5.md`.

## Ordering and blindness

`run_posthoc_matched_controls.py` constructed all spectra without a reference
ordinate, target table, fitted scale, score, or accuracy statistic. Its source
audit covered the runner, `weil_core.py`, and the reused prolate runner and found
no forbidden evaluator/table tokens. It wrote 60 roots for each of three
controls at each of the eight requested `(x,N)` pairs, then froze
`outputs/posthoc-matched-controls-blind.json` with SHA-256
`580c88750bc0a4e03ab495990c244d67e449cd8fef80ec023f1922a592cecb41`.
Construction took 484.904 seconds.

Only afterward did `score_posthoc_matched_controls.py` load the frozen targets.
Its first stdout metric and first persistent accuracy block contain all eight
pseudo-prime scores; archimedean-only, prolate-only, and authentic scores follow
in that order. The score window is exactly the user-frozen ordinal set 20--50,
with no fitted scale. A landing means RMSE at most `0.01` and maximum absolute
error at most `0.05`.

The pseudo construction reuses seed `52025001`, PCG64DXSM, continuous bases
uniform on `[2,x]`, and acceptance probability `log(2)/log(base)`. Complete
draws are rejected until their number of bases and number of powers equal the
authentic support counts fixed by `x`. At `x=14`, this is exactly the original
six-base/nine-power sampler (the runner checks byte-for-byte term equality and
attempt count against `weil_core.pseudo_prime_terms`). At `x=16`, the same rule
uses six bases and ten powers. One support per `x` is reused across `N` so that
the truncation path, rather than a new random draw, is varied.

Each finite-matrix control was built at 100 decimal digits. A binary64 ground
vector is only a seed: one 100-digit Rayleigh refinement reduced the largest
residual/binary64-gap ratio to `7.92e-45`; a full arbitrary-precision eigensolve
was implemented as a fallback but never triggered. All 60 construction-grid
roots were then refined against the 100-digit transform. Across all finite
controls, the largest ordinate-20--50 displacement from the binary64 seed list
was `7.99e-14`, and the largest final transform residual was `2.64e-101`.

The prolate-only controls use the already-surviving inversion-even convention:
100 digits, degree-200 even Legendre candidate, 24-point composite
Gauss--Legendre quadrature, four panels per shortest retained Fourier cycle,
and a root scan starting at zero on the intrinsic Fourier lattice. At fixed
`x`, the projection is computed through the largest requested `N` and its
prefix is used at smaller `N`; normalization cannot change its roots. The
largest transform residual was `7.52e-103`, and every reported root had a
nonzero finite-difference derivative diagnostic.

## Results

| x | N | authentic RMSE | pseudo RMSE | archimedean-only RMSE | prolate-only RMSE | control coverage |
|---:|---:|---:|---:|---:|---:|:---:|
| 14 | 112 | 1.4693e-6 | 28.0511 | 25.7566 | 1.61998e-5 | complete |
| 14 | 120 | 1.39592e-6 | 28.0518 | 25.7570 | 2.07832e-5 | complete |
| 14 | 128 | 1.37988e-6 | 28.0521 | 25.7573 | 1.93146e-5 | complete |
| 14 | 140 | 1.36354e-6 | 28.0533 | 25.7577 | 1.44707e-5 | complete |
| 14 | 168 | 1.29846e-6 | 28.0551 | 25.7584 | 1.17939e-5 | complete |
| 16 | 128 | 3.01652e-13 | 32.0862 | 29.8467 | 4.80896e-9 | complete |
| 16 | 160 | 2.71213e-13 | 32.0878 | 29.8475 | 3.04454e-9 | complete |
| 16 | 192 | 2.60672e-13 | 32.0889 | 29.8481 | 4.25310e-9 | complete |

The authentic count is 8/8 landings. Pseudo-prime and archimedean-only counts
are each 0/8. The parameter-matched prolate-only count is 8/8. The persistent
coverage audit verifies, rather than declares, that every authentic match has
all three same-`(x,N)` controls, sufficient root counts, and complete scores.

## Interpretation

The two ordinary nulls refute a generic smooth-density or random-comb
explanation at these parameters. They do not rescue the advertised arithmetic
match, because the strongest hostile control reproduces it at every pair. The
prolate construction omits the finite Weil arithmetic matrix, but its integer
dilation map satisfies a Mellin identity containing the zeta Dirichlet series.
This explains the landing as an analytic leakage in the control design, not as
a hidden target ordinate in the software. Under the lab rule, zero accuracy is
therefore **VOID** as evidence that the finite Weil matrix supplies the missing
arithmetic. The separate residual/gap decay question remains the meaningful
bridge test.
