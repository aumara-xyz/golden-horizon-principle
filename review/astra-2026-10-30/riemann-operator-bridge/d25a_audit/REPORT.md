# D25A independent audit: selected prolate correlations

**Status:** RAN, bounded floating computation; exact support and nodal lemmas stated separately. No RH claim. The original Mac-local script was not available here; this is an independent implementation of the equations in the supplied report.

## Definition and reproduced values

Use the standard prolate differential operator on [-1,1], with parameter

$$c(L)=\tfrac12L[13.1+15.3(L-0.4)]=7.65L^2+3.49L.$$

Its lowest even/odd eigenvectors are computed in orthonormal Legendre bases. Physical waves on [-L,L] are normalized by 1/sqrt(L) and set to zero outside that interval. Correlation is C_f(a)=integral f(x)f(x+a) dx. Gauss-Legendre quadrature integrates each finite polynomial product exactly in exact arithmetic; the executed evaluations use float64.

| L | Independently computed odd crossover, 96 coefficients | Difference, 32 minus 96 coefficients |
| ---: | ---: | ---: |
| 0.40 | 0.278058979211603 | 3.89e-16 |
| 0.70 | 0.384965644274112 | 2.22e-16 |
| 1.00 | 0.418033631581685 | 5.55e-17 |
| 1.20 | 0.431191101921975 | 5.55e-17 |
| 2.00 | 0.459784432858166 | 6.07e-11 |

All five match the supplied six-decimal values. At L=.70:

| n | Even correlation at log(n) | Odd correlation at log(n) |
| ---: | ---: | ---: |
| 2 | 0.193736908967628 | -0.490430177504084 |
| 3 | 0.008388756587496 | -0.089604663133821 |
| 4 | 0.000010676240827 | -0.000360525986689 |

The 33-point L sweep from .40 through 2.00 has every **visible** prime-power odd correlation negative. The largest crossover is 0.459784432858166, below the proposed Hermite limiting value 2/sqrt(15.3)=0.511309992564914.

## Exact statements that require no numerical sweep

1. For compact support [-L,L], C_f(a)=0 whenever |a|>=2L. Consequently the assertion of strict negativity for every prime power without a support qualification is false.
2. If a ground state is positive throughout (-L,L), its correlation is positive for every 0<a<2L.
3. If f is odd and positive on (0,L), then C_f(a)<0 for L<=a<2L: throughout the overlap, x<=0 and x+a>=0, so the product is negative except at measure-zero boundaries/nodes. Therefore for L<=log2 the sign of every visible prime-power odd correlation follows directly from the one-node property. No Hermite ceiling is needed in that restricted range.
4. Having one node alone does not imply a unique correlation crossing for every smaller shift 0<a<L. The relevant quantitative statements about the selected PSWF family need additional analysis.

## The Hermite comparison is an asymptotic target, not a uniform theorem

The quadratic bandwidth has c(L)/L² -> kappa=7.65. For an ideal Hermite first excited wave proportional to x*exp(-kappa*x²/2), its normalized correlation is

$$C(a)=\exp(-\kappa a^2/4)(1-\kappa a^2/2),$$

and its crossover is sqrt(2/kappa)=2/sqrt(15.3). A justified convergence to that wave would identify a limiting crossover. It would not, by itself, establish that every finite-L crossover approaches from below, or establish a uniform rate, or control the full Weil quadratic form.

This run confirms the proposed ceiling on the frozen finite sweep. It does not prove the all-L bound or the absence of later correlation sign changes for the exact infinite-dimensional functions.

## Counterfactual bandwidth control

Keep c(.4) fixed but grow c only linearly with L. This remains a legitimate lowest even/odd prolate pair. At L=2 its odd crossover is 0.772847360321883, larger than log2, and its correlation at log2 is **positive**, 0.133565462365801.

Thus the observed prime-shift sign pattern depends on the selected bandwidth family. It is not an automatic consequence of one node, parity, a spherical lift, or a golden-ratio parameter. The supplied bandwidth fit remains a model choice until it is related rigorously to the full arithmetic minimizer.

## What survives

The supplied finite D25A numbers reproduce accurately. They give a good specified family of test waves. They do not solve the coupling between that family and the rest of the Weil form. Route B tests that remaining issue directly, including the stated nodal-polynomial controls and symmetric bounce mutations.

Run: `python3 run.py`. Dependencies: NumPy and SciPy. PLAN.md was frozen before this independent computation; prior reported results were already known, so this is exploratory replication rather than blind preregistration.
