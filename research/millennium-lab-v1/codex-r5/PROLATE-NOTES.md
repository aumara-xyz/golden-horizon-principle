# R5.2/R5.3 prolate candidate implementation

Status: **MEASURED** as a finite numerical construction. It does not establish the missing prolate-to-Weil bridge.

`prolate_candidate.py` solves the regular even eigenproblem

\[
-\partial_y[(\lambda^2-y^2)\partial_y]h+(2\pi\lambda y)^2h=\chi h
\]

after setting `z=y/lambda`. In the orthonormal Legendre basis, multiplication by `z^2` is parity-tridiagonal, so labels 0 and 4 are the first and third eigenvectors of one real symmetric tridiagonal matrix. Each mode has unit `L2[-lambda,lambda]` norm and positive value at zero. With `I_j` its exactly evaluated integral, the code forms

\[
h_\lambda=(I_0h_{4,\lambda}-I_4h_{0,\lambda})/
\sqrt{I_0^2+I_4^2}.
\]

This fixes the sign by a positive `h4` coefficient and makes the integral analytically zero. Per the preregistration, the function is extended by zero. The finite sum

\[
k_\lambda(u)=\sqrt u\sum_{1\le m\le\lambda/u}h_\lambda(mu)
\]

is integrated separately between every `log(lambda/m)` change point. Coefficients use the paper's basis

\[
V_n(u)=L^{-1/2}\exp(2\pi i n\log(\lambda u)/L),\qquad L=\log(\lambda^2),
\]

and are returned in `-N,...,N` order, normalized to Euclidean norm one.

The convergence ledger compares Legendre cutoffs 240/400 and composite piecewise Gauss-Legendre meshes with two/eight panels per shortest Fourier cycle at `N=144`. Each panel uses a fixed 20-point rule and no interval crosses an `E`-sum change point. The undeformed-Hermite control uses the full Schwartz Hermite combination rather than truncating it at the prolate endpoints. It is deliberately kept as a separate file and never used to select a construction parameter.

`bridge_metrics(matrix, coefficients, x=...)` is the join point for a Weil matrix in the same basis ordering. It reports the Rayleigh quotient, residual, even/odd gap, residual/gap, spectral separation, Davis--Kahan-style angle bound, actual finite-vector angle, and a uniform Mellin/Fourier-transform bound. The uniform functional estimate is

\[
\sup_{|\operatorname{Im}z|\le b}\|\ell_z\|_2
\le \sqrt{\sinh(bL)/b},
\]

by Bessel's inequality; therefore it is valid on each preregistered real half-width 32, 64, and 128 without a sampling argument.

Run from this directory with:

```bash
python3 run_prolate.py
python3 run_prolate_bridge.py
```

The implementation imports no reference-spectrum routine or data file and contains no reference ordinates.

`audit_prolate.py` checks the two prolate characteristic values against SciPy's independent `pro_cv` path, checks the analytic zero-integral normalization on every registered cutoff, and compares the stable entire transform formula with direct quadrature at a fixed complex point.

The bridge runner constructs each Weil matrix at 60 decimal digits through `weil_core.py`, then deliberately converts its even/odd blocks to binary64 for a first residual sweep. It records a conservative floating-point residual floor. A residual at that floor is a bound requiring high-precision refinement, not a measured decay value. The primary run is `N=120` on all thirteen registered `x` values; `N=96,144` are evaluated on the registered final five. The accepted seed-52025001 pseudo comb is reused unchanged across those final five, so this mutation tests the arithmetic-comb identity rather than re-fitting pseudo-prime density at each cutoff.

`run_prolate_high_precision_spotcheck.py` repeats one deliberately smaller case (`x=9,N=30`) without the binary64 matrix conversion. Its purpose is diagnostic: it demonstrates that a 60-digit eigensolve resolves the ordering that binary64 scrambles, while also showing that the double-precision candidate projection is nowhere near accurate enough to divide its residual by that tiny gap. It is not substituted for the registered `N=120` decay fit.

## Numerical outcome

**MEASURED:** across the thirteen registered cutoffs, the analytic zero-integral residual is at most `1.20e-16`; changing Legendre cutoff 240 to 400 changes the normalized coefficient vector by at most `8.92e-16`; and changing the composite mesh from two to eight panels per shortest Fourier cycle changes it by at most `1.16e-14`. The independent `pro_cv` characteristic-value comparison differs by at most `1.46e-11` in absolute value (about `1e-14` relatively at the largest value), and the direct transform audit differs by `2.80e-16`.

**MEASURED mutation:** the phase-aligned `N=144` distance from the deformed prolate candidate to the undeformed Hermite candidate decreases monotonically from `0.0637807` at `x=5` to `0.0143517` at `x=20`. This measures prolate-to-Hermite convergence, not prolate-to-Weil convergence.

**UNVERIFIED bridge law:** at every authentic-prime `N=120` point, and at every `N=96,144` last-five mutation, the computed near-null gap is below the conservative binary64/projection floor. Its apparent sign and the resulting signed `r/Delta` are therefore meaningless diagnostics. No power exponent or AIC comparison is reported. The undeformed-Hermite residuals lie at the same floor, so the registered Hermite comparison is also unresolved.

**MEASURED hostile contrast:** on the last five `N=120` matrices, the frozen pseudo-prime mutation has residuals `0.558`--`0.581`, whereas each authentic-prime residual is unresolved below an effective floor of `2.6e-13`--`2.8e-13`. Thus the pseudo comb destroys approximate nullness by at least twelve orders of magnitude. This does not measure the authentic `r/Delta` ratio because its denominator remains unresolved.

**MEASURED diagnostic, UNVERIFIED ratio:** at `x=9,N=30`, the 60-digit calculation gives even ground `4.0209984e-37`, odd ground `1.2489278e-33`, second even `1.9205063e-30`, and overlap `0.999999853555` (`sin(angle)=5.41193e-4`). The gap is `1.2485257e-33`, while the double candidate residual is `2.865e-15` and its mesh uncertainty is `1.499e-15`; hence dividing those numbers is not a measurement of the bridge law. This spot check explains why the binary64 finite-eigenvector angles in `bridge-summary.json` are explicitly marked **UNVERIFIED**.

## Arbitrary-precision analytic projection

`run_prolate_exact_bridge.py` removes the candidate-projection floor. It converts the arbitrary-precision Legendre series to powers, (h(y)=\sum_d H_dy^d), and integrates every term of the finite `E` sum exactly. With (a=\log\lambda), (b_m=\log(\lambda/m)), (\omega_n=2\pi n/L), and (\alpha_{d,n}=d+1/2-i\omega_n), the unnormalized coefficient is

\[
c_n=\frac{(-1)^n}{\sqrt L}\sum_{m\le x}\sum_d H_dm^d
\frac{e^{\alpha_{d,n}b_m}-e^{-\alpha_{d,n}a}}{\alpha_{d,n}}.
\]

There is no quadrature in this formula. The primary R5.3 vector retains the raw complex coefficients of `E(h)` as required by Eq. 7.6 and the prediction ledger. Taking their real parts and renormalizing is reported only as an inversion-even mutation. A later protocol audit found that the initial R5.2 prolate-only runner had also taken this projection even though the ledger did not authorize it. That artifact is retained as a disclosed mutation; `run_prolate_only_raw_control.py` supplies the corrected raw-basis hostile-control primary.

The registered exact grid uses 180-decimal arithmetic and Legendre cutoffs 200/160 through `x=16`. The initially coarse cutoff mutation did not resolve `x=18,20`, so those rows remain in the audit trail and were replaced by the registered-construction-preserving 240/200 cutoff replay. A conservative (4\lVert M\rVert_F\delta) action bound from the two cutoff vectors is below the residual in all 23 final rows; every gap is also above the 180-digit arithmetic floor.

| `x` | `r` at `N=120` | `Delta` | `r/Delta` |
|---:|---:|---:|---:|
| 5 | `3.374108e-9` | `1.050143e-14` | `3.212998e5` |
| 6 | `9.131668e-12` | `1.416498e-19` | `6.446650e7` |
| 7 | `2.785325e-14` | `1.641493e-24` | `1.696825e10` |
| 8 | `6.574837e-17` | `1.356237e-29` | `4.847854e12` |
| 9 | `1.657739e-19` | `1.127268e-34` | `1.470582e15` |
| 10 | `3.814572e-22` | `8.275962e-40` | `4.609219e17` |
| 11 | `8.900925e-25` | `6.865152e-45` | `1.296537e20` |
| 12 | `2.178988e-27` | `4.038303e-50` | `5.395802e22` |
| 13 | `4.851502e-30` | `3.055565e-55` | `1.587759e25` |
| 14 | `9.305050e-33` | `1.667856e-60` | `5.579048e27` |
| 16 | `4.355111e-38` | `5.605923e-71` | `7.768767e32` |
| 18 | `2.122792e-43` | `1.710169e-81` | `1.241276e38` |
| 20 | `3.700200e-49` | `5.493823e-92` | `6.735201e42` |

**MEASURED bridge law:** the preregistered decay prediction fails. Although the actual finite-vector sine angle improves from `4.11e-4` at `x=5` to `2.22e-5` at `x=20`, the near-null gap collapses much faster than the residual. Thus every residual/separation angle bound is the trivial value one. On the final five `x` values, the formal power exponents are `p=-192.72,-189.00,-192.18` for `N=96,120,144`; a negative `p` means growth, not decay. The lowest-AIC model among the frozen constant, power, exponential-in-lambda, and exponential-in-`x` comparisons is exponential growth in `x` for all three `N`: its slopes are `5.967`, `5.830`, and `5.932`, respectively. This is a five-point finite-window description, not an asymptotic theorem.

| `N` | constant AIC | power AIC | `exp(a lambda)` AIC | `exp(a x)` AIC | fitted `a` in `x` |
|---:|---:|---:|---:|---:|---:|
| 96 | `29.30` | `10.24` | `7.95` | `5.30` | `5.967` |
| 120 | `29.04` | `0.58` | `-8.14` | `-9.72` | `5.830` |
| 144 | `29.21` | `2.33` | `-5.18` | `-21.94` | `5.932` |

**UNVERIFIED R5.3-C Hermite ratio:** the registered undeformed-Hermite final-five rows exist at `N=96,120,144`, but only in the binary64/composite-quadrature sweep. Their candidate uncertainty and matrix floor dominate the true-prime near-null gaps, so no Hermite `r/Delta` median comparison is retained.

**MEASURED pseudo non-nullness, UNVERIFIED positive-gap comparison:** seed `52025001` has `N=120` residuals from `0.5583` to `0.5810`, well above the numerical floor. Its parity gaps are positive at `x=13,14` but negative at `x=16,18,20`, where the even ground is not globally lowest. The literal signed-ratio median is `-1.2594`, but it is not a Davis--Kahan ratio comparable to the positive-gap primary. Thus the pseudo comb demonstrably destroys near-nullness, while the preregistered final-five positive `r/Delta` median comparison remains **UNVERIFIED**.

At the independent `x=9,N=30` spot check, the raw primary gives `r/Delta=4.3181007e14`; the even-projected mutation gives `4.3180807e14`. At `x=13,N=120` the corresponding values are `1.5877594e25` and `7.3624154e24`. The convention changes constants but not the failed decay prediction.

## Raw prolate-only root audit

**MEASURED under a post-hoc convention:** the raw `x=13,N=120` finite transform has 70 complex roots obtained by continuation from the zero-blind even-control roots. Four versus eight homotopy steps move them by at most `8.00e-154`, two contour discretizations both infer 70 enclosed roots, and the largest relative residual is `8.52e-182`. The raw/even maximum complex displacement on frozen ordinals 20--50 is `5.87889e-4`; across all 70 it grows to `0.754964`, illustrating the severe high-index conditioning despite an inversion-odd coefficient norm of only `1.72e-30`.

The phrase “first 70 complex roots” is **UNVERIFIED** as a canonical mathematical definition: increasing real part after homotopy from the even roots is an audit label, not a preregistered ordering. Formal infinite-mode certification is also **UNVERIFIED**. The blind raw artifact is `outputs/prolate-only-raw-blind.json`; post-gate frozen accuracy is defined by `|z_j-gamma_j|`, with all target loading kept outside the construction runner. The earlier `outputs/prolate-only-blind.json` remains the inversion-even mutation rather than being overwritten.

After the pseudo-prime gate, the separate scorer gives the raw continuation-labelled roots 20--50 RMSE `3.62268e-4`, median distance `2.35836e-7`, and maximum distance `0.00180015`; the even mutation gives RMSE `3.35666e-4` and maximum distance `0.00179988`. Both meet the frozen landing rule. Accordingly, the match is **VOID** as evidence for the missing bridge: the integer-dilation map already supplies the zeta Dirichlet factor, so this hostile control is not arithmetically neutral even though it contains no prime matrix or ordinate table.
