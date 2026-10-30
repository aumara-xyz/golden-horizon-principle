# Route A: rational Suzuki mesh versus uniform time mesh

**Status:** RAN, float64 diagnostics. No interval positivity certificate and no RH proof.

## Frozen comparison

Three 110-node meshes were used:

1. The earlier baseline t_i=i/20, from 0.05 through 5.5.
2. A rational-address arithmetic mesh u_i=1/n_i, containing all 68 prime powers through 244, the endpoint 244, and a deterministic spacing fill to 110 nodes.
3. A uniform time mesh on the same interval as mesh 2: [log2,log244].

The matched interval matters: equal matrix dimension alone does not give equal coverage. The arithmetic mesh's actual integer addresses are retained exactly in results.json. It has 186 ordered divisibility relations, giving rational mixed-ray alignments.

The prime-side formula is Suzuki equation (1.1), with no zero ordinates. Arithmetic-weight mutations sigma=.45 and.55 retain the authentic smooth terms and change only n^-1/2 to n^-sigma. They are synthetic controls, not L-functions.

## Authentic finite matrices

| Mesh | min eigenvalue of K | condition2(K) | condition2(Kc) | min LDL block pivot of K |
| --- | ---: | ---: | ---: | ---: |
| Original uniform time | 0.005436825465 | 974.136 | 17364.930 | 0.01574139515 |
| Arithmetic reciprocals | 0.003062834456 | 1858.400 | 8391.956 | 0.01211083438 |
| Matched uniform time | 0.007570259214 | 695.962 | 9714.748 | 0.01669123923 |

The arithmetic grid did not improve the intrinsic conditioning in this test. Its unscaled matrix is worse conditioned than the matched uniform matrix. Compactification changes raw conditioning through diagonal weights; after diagonal normalization, the K and Kc correlation matrices agree within 4.45e-16, as the algebra predicts.

There is therefore no evidence here for a universal conditioning gain from spherical/compact folding. Exact arithmetic breakpoints remain useful for bookkeeping and piecewise evaluation.

## Negative controls

| Mesh | Negative eigenvalues at sigma=.45, K / Kc | Negative eigenvalues at sigma=.55, K / Kc |
| --- | ---: | ---: |
| Original uniform time | 5 / 5 | 5 / 5 |
| Arithmetic reciprocals | 3 / 3 | 4 / 4 |
| Matched uniform time | 5 / 5 | 5 / 5 |

Every mesh detects both modified negative controls. Each matrix and its own compactified matrix have the same inertia. Counts need not agree across different sets of sample points.

The 4-by-4 matrix with diagonal 1 and off-diagonal -2/5 retains its negative full eigenvalue despite positive 3-by-3 principal submatrices, both before and after positive diagonal congruence.

## Interval-certification readiness

If every entry of an N-by-N symmetric matrix has error at most epsilon, its spectral perturbation is at most N*epsilon. A **certified** positive lower bound for lambda_min would therefore furnish an entrywise error budget lambda_min/N. The floating diagnostic budgets for the authentic unscaled matrices are:

- Original uniform: 4.9425686e-5.
- Arithmetic reciprocals: 2.7843950e-5.
- Matched uniform: 6.8820538e-5.

These are targets for a future outward-rounded evaluator, not certified endpoints. The implementation reports a separate analytic Lerch truncation bound, which does not cover floating roundoff, transcendental evaluations, or matrix factorization error. LDL reconstruction residuals are small but do not replace interval input enclosures.

No new interval certificate is claimed for Route A. The exact statement preserved here is Kc=D K D and its finite inertia equivalence. Route C supplies a separate interval-certified finite test.

## Reproduction and source

Run `python3 run.py` with NumPy and SciPy. Formula source: Masatoshi Suzuki, *Aspects of the screw function corresponding to the Riemann zeta-function*, https://arxiv.org/abs/2206.03682 . The run plan was frozen before execution but is exploratory because prior baseline results were known. Cached evaluation times in the JSON are operational observations, not a fair cross-mesh speed benchmark.
