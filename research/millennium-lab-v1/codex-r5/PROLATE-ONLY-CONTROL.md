# Prolate-only hostile control

## Protocol correction: raw-basis primary

The R5.2 ledger did not authorize an inversion-even projection. The corrected primary is therefore `outputs/prolate-only-raw-blind.json`: `x=13`, `N=120`, 180-decimal arithmetic, a degree-200 prolate expansion, the raw complex coefficients of `E(h)`, and exact termwise projection rather than quadrature. It contains no reference targets, fitted scale, score, or accuracy field. The earlier even-projected artifact is retained below as a disclosed convention mutation.

A non-real finite transform has no canonical sequence of “first positive roots.” For this audit only, the 70 labels are defined *post hoc* by homotopy continuation from the first 70 positive roots of the zero-blind even mutation, followed by increasing real part. The even roots themselves are sign-bracketed in successive Fourier-lattice intervals. They depend only on `x`, `N`, and the constructed coefficients; no reference ordinate sets a bracket, seed, or stopping point. This is a reproducible label convention, not a preregistered or mathematically canonical root ordering.

**MEASURED under that convention:** four- and eight-step homotopies agree to at most `8.00e-154`; 512- and 1024-sample argument-principle contours both count exactly 70 roots in the disclosed rectangle; and the largest relative rational residual is `8.52e-182`. The degree-200/160 vector distance is `4.72e-55`, with at most `7.39e-26` root movement. The raw inversion-odd norm is only `1.72e-30`, but root conditioning magnifies it: over all 70 roots the maximum imaginary part is `0.705623` and the maximum complex shift from the even mutation is `0.754964`. On the frozen ordinals 20--50, both maxima are `0.0005879` (at ordinal 48). The exact even roots agree with the earlier quadrature artifact to `9.27e-59` on that frozen slice.

The finite complex roots and homotopy labels are **MEASURED** numerical objects. A canonical “first 70” definition and passage from the degree-200/`N=120` calculation to an infinite-mode prolate limit are **UNVERIFIED**. Optional degree-240 Arb all-root isolation was not completed; the artifact says so rather than presenting the contour audit as a formal certification.

Post-gate accuracy must use the continuation labels and the absolute complex distance `|z_j-gamma_j|` for each frozen ordinal `j=20,...,50`. RMSE, MAE, median, maximum, and threshold counts are then computed from those nonnegative distances. Target loading and scoring remain separate from the blind artifact.

After the ten pseudo-prime scores had been emitted first, `score_after_gate.py` applied that rule. **MEASURED under the post-hoc labels:** the raw control has RMSE `3.62268e-4`, MAE `1.27470e-4`, median distance `2.35836e-7`, and maximum distance `0.00180015` (ordinal 50) on roots 20--50. It therefore satisfies the lab landing threshold. The even mutation has RMSE `3.35666e-4` and maximum error `0.00179988`; it lands as well. Because the supposedly no-arithmetic control lands, zero-matching accuracy is **VOID** as evidence distinguishing the finite Weil construction. The analytic integer-dilation factor below explains the degeneracy without any software target leak.

## Earlier even-projected convention mutation

The earlier run `outputs/prolate-only-blind.json` uses `x=13`, `N=120`, 100-decimal arithmetic, a degree-200 even Legendre expansion of the prolate operator, and the zero-integral combination of labels 0 and 4. It applies the finite integer-dilation map `E`, takes an orthogonal inversion-even projection, and computes multiplicative Fourier coefficients by 24-point composite Gauss--Legendre quadrature with four panels per shortest retained Fourier cycle. Positive roots are scanned from zero with step `(2*pi/log(13))/32`; neither brackets nor stopping locations use a reference ordinate. The artifact stores 70 roots so the frozen ordinal range 20--50 can be scored later. Because the projection was not in the ledger, this is a mutation, not the protocol primary.

Its root mutations are `N=112`, `N=128`, and an 18-point/three-panel quadrature. Every mutation uses the same zero-blind scan. A degree-160 Legendre reconstruction is also compared on 33 fixed support points; this tests mode-cutoff convergence without paying for a redundant second projection.

The blind run found 70 strictly increasing positive sign-changing roots from `14.1347251417...` through `185.2297809107...`. The minimum adjacent spacing was `0.8451234963`; the largest transform residual at a reported root was `3.04e-103`, and the smallest finite-difference derivative diagnostic was `4.26e-31`. These are numerical robustness checks, not an exact simplicity proof. On the frozen ordinal slice 20--50, the maximum root movement was `6.75e-4` at `N=112`, `4.42e-4` at `N=128`, and `1.12e-29` under the quadrature mutation. Across all 70 roots the corresponding maxima were `2.95e-2`, `1.93e-2`, and `4.88e-28`. The primary/mutated coefficient distance was `1.02e-54`; the degree-200/degree-160 fixed-grid mode difference was `1.52e-54`.

The artifact SHA-256 is `a00593f714e9dec2daa55ca61c4e2519c9e4642429a7759ac0f1b313b0ed2750`. Its recorded construction-source SHA-256 matches the current runner (`d964103e584b889caf2a5420a54776a213ad332aec1d0b75fd8395255a46d25a`).

## Why landing would not be a software oracle

This control uses no zero table and no special-function zero finder. It is independent of the finite Weil matrix and its explicit prime-power comb. However, “no arithmetic matrix” is not the same as “arithmetically neutral.” For suitable even `h`, direct interchange of the sum and Mellin integral gives

\[
\int_0^\infty E(h)(u)u^{-iz}\,d^*u
=\zeta(1/2-iz)\int_0^\infty h(v)v^{-1/2-iz}\,dv.
\]

Thus the integer-dilation map `E(h)(u)=sqrt(u) sum_{m>=1} h(mu)` analytically contains the Dirichlet-series factor. In the undeformed Hermite limit this is precisely the mechanism behind the paper's Fourier representation of the completed function. The finite prolate/control transform is a compact-window approximation to that identity.

Consequently, if this hostile control later lands, the lab rule correctly makes zero-matching evidence from the Weil reconstruction **VOID** as a discriminator. The explanation would be a mathematical degeneracy in the control design—the supposedly prime-free control still carries arithmetic through the integer-dilation sum—not a hidden ordinate entering the software.
