# R4.2 implementation notes

All numerical statements below are **MEASURED**. The prediction ledger was committed at `bbf37eb` before either spectrum was run. No parameter was fitted to the zeta ordinates.

## Frozen models

Berry and Keating, *J. Phys. A* **44** (2011) 285203, [doi:10.1088/1751-8113/44/28/285203](https://doi.org/10.1088/1751-8113/44/28/285203), define on the positive half-line

\[
 \chi''(x)=\left(\frac{h(x)}{\eta^2}+\frac{i g(x)}{\eta}\right)\chi(x),\quad
 h(x)=1-\frac{E^2x^2}{4(1+x^2)^2},\quad
 g(x)=\frac{E(1-x^2)}{2(1+x^2)^2},
\]

with \(\chi'(0)/\chi(0)=e^{i\alpha}/\eta\) and a decaying solution at infinity (their Eqs. 2.7--2.9, 2.22, and 3.2--3.3). The run fixed \(\eta=1/(2\pi)\), \(\alpha=0\), integrated the decaying branch backward from \(x_{\max}\), and located the real energies at which \(\eta\chi'(0)/\chi(0)=1\). This is the exact differential problem; the semiclassical area quantization was not substituted.

Sierra and Rodriguez-Laguna, *Phys. Rev. Lett.* **106** (2011) 200201, [doi:10.1103/PhysRevLett.106.200201](https://doi.org/10.1103/PhysRevLett.106.200201), give the exact secular equation

\[
 e^{-i\vartheta/2}K_{1/2+iE/(2\hbar)}(h/\hbar)
 +e^{i\vartheta/2}K_{1/2-iE/(2\hbar)}(h/\hbar)=0
\]

(their Eq. 14). The run fixed \(h=1\), \(\hbar=1/(2\pi)\), and \(\vartheta=\pi/4\). There is no spatial discretization in this calculation: meshes of 0.002 and 0.001 only bracketed zeros of the published Bessel equation, which were then refined by multiprecision bisection.

For both models the reported raw value is \(E_n\), and the only rescaling is the published mean-density map \(t_n=2\pi E_n\). The first 20 positive levels are compared by ordinal index with the first 20 positive zeta ordinates.

## Spectrum and controls

| Sequence | RMSE, raw | RMSE after \(2\pi\) | Pearson after \(2\pi\) | maximum absolute residual after \(2\pi\) |
|---|---:|---:|---:|---:|
| Berry--Keating | 43.948969 | 6.664356 | 0.998318 | 13.001269 |
| Sierra--Rodriguez-Laguna | 44.369587 | 2.986576 | 0.999492 | 5.015691 |
| Smooth Riemann--von Mangoldt midpoint quantiles | n/a | 0.518942 | 0.999603 | 0.901765 |

The smooth control is parameter-free: its \(n\)-th value solves \(\theta(T)/\pi+1=n-1/2\), with \(\theta\) the Riemann--Siegel theta function. Its RMSE is smaller than Berry--Keating's by a factor of 12.84 and smaller than Sierra--Rodriguez-Laguna's by a factor of 5.76. The large correlations therefore measure shared monotone mean density, not the arithmetic fluctuations.

No candidate level lies within \(10^{-6}\) of the corresponding zeta ordinate. Sierra--Rodriguez-Laguna has the smaller of the two candidate RMSEs.

## Convergence and independent residuals

| Check | **MEASURED** value |
|---|---:|
| Berry--Keating: maximum scaled change, \(x_{\max}=30\), tolerances \(10^{-11}\), versus \(x_{\max}=40\), tolerances \(10^{-12}\) | \(2.252\times10^{-11}\) |
| Berry--Keating: maximum relative residual in the independently integrated nonlocal identity \(\eta^2\phi'(0)+\int_0^\infty\phi(x)\,dx=0\) | \(1.284\times10^{-12}\) |
| Sierra--Rodriguez-Laguna: maximum scaled change, mesh 0.002 at 60 decimal digits versus mesh 0.001 at 80 decimal digits | 0 at binary64 output precision |
| Sierra--Rodriguez-Laguna: maximum relative residual from direct quadrature of its nonlocal boundary condition, all 20 levels | \(9.270\times10^{-15}\) |

The Berry--Keating terminal condition uses the leading decaying asymptotic \(\chi'=-\chi/\eta\) at finite \(x_{\max}\). The cutoff comparison and the nonlocal identity bound its observed effect for these levels; they do not constitute a general error proof. The Sierra--Rodriguez-Laguna root equation is exact up to special-function evaluation and root refinement.

## Registered phase mutations

Changing Berry--Keating to \(\alpha=\pi/2\) changed every ordinally paired scaled level by more than 0.1; the smallest shift was 14.1521. This unusually large ordinal shift includes spectral flow: the first positive mutated level corresponds to a later part of the helical eigencurve, so the magnitude must not be read as a continuously tracked eigenbranch displacement.

Changing Sierra--Rodriguez-Laguna to \(\vartheta=3\pi/4\) changed every scaled level by more than 0.1; the shifts ranged from 0.5356 to 0.7556. Both mutations preserve the papers' self-adjoint discrete construction and leading mean density while moving the low spectrum.

## Prediction audit

| Registered statement | Outcome |
|---|---|
| 20 real ordered positive levels for each exact model | **MEASURED**: held |
| \(2\pi\) improves raw RMSE by at least three; correlation above 0.99 | **MEASURED**: held; improvement factors 6.59 and 14.86 |
| scaled RMSE above 1, maximum residual above 2, no \(10^{-6}\) match | **MEASURED**: held for both |
| Sierra--Rodriguez-Laguna has lower candidate RMSE | **MEASURED**: held |
| registered convergence thresholds and independent residual controls | **MEASURED**: held |
| neither candidate beats the smooth control by more than 20 percent | **MEASURED**: held; both are substantially worse |
| phase mutation moves at least one scaled level by more than 0.1 | **MEASURED**: held for both |

## Three-yeses rows

| Candidate | Self-adjoint with discrete spectrum? | Chaotic without arithmetic degeneracy? | Orbits of length \(\log p\)? |
|---|---:|---:|---:|
| Berry--Keating compact Hamiltonian (2011) | yes | no | no |
| Sierra--Rodriguez-Laguna \(x(p+\ell_p^2/p)\) (2011) | yes | no | no |

The first column records the constructions established in the cited papers, not a new proof in this run. Both classical models have one degree of freedom and are integrable. Berry--Keating has one primitive orbit per energy; Sierra--Rodriguez-Laguna has \(T_E\sim\log(E/h)\), not prime-indexed periods \(\log p\). Neither row has three yeses.

## Artifacts

- `run_r42.py`: frozen implementation.
- `metrics-r42.json`: full configurations, roots, comparisons, convergence data, residuals, mutations, and table flags.
- `spectra-r42.csv`: the 20 ordinal comparisons.
- `bk-partial.json` and `srl-partial.json`: outputs frozen immediately after the separate model runs.
- `run-r42.log`: root and summary log.

Python used NumPy 2.0.2, SciPy 1.13.1, and mpmath 1.3.0.
