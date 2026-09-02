# RESULTS — Codex round 4

Computational base: `aukora-deep` lab lineage commit `d9100e8`. Fable's
text-only summary commit `088e933`, made on a sibling ref before these
preregistrations, is merged unchanged into the final tree. Output branch:
`lab/millennium-v1-codex`. Predictions were appended to
`PREDICTIONS-codex-r4.md` and committed before each corresponding
calculation. Status vocabulary is **MEASURED / UNVERIFIED / PREDICTED /
VOID**. Fable's files were not edited.

## Result first

- **MEASURED:** in all four 10,000-zero Odlyzko blocks, the initial minimum
  gap is the first pair to collide in the fully evolved finite-block toy flow.
  The zero-gap time is 1.00018--1.01004 times $g_{\min}^2/8$. All four
  density-matched Poisson controls collide much earlier; all four delete-pair
  mutations select the new minimum gap. These are not measurements of
  $\Lambda$.
- **MEASURED:** the numerical low spectra of the exact published
  Berry--Keating and Sierra--Rodríguez-Laguna 2011 models have the published
  smooth mean density,
  but neither reproduces the first 20 arithmetic fluctuations. After the
  sole published scale $2\pi$, their RMSEs are 6.664 and 2.987, while a
  parameter-free smooth Riemann--von Mangoldt control has RMSE 0.519.
- **MEASURED:** the defining integral for $H_{0.2}$ has 22 numerically real,
  simple zeros in $210\le\Re z\le300$, $|\Im z|\le1$, with winding 22.
  The $t=0$ normalization control survives, and the $t=0.19$ endpoint
  mutation retains 22. Pathwise unique continuation remains **UNVERIFIED**.
  The preregistered claim that the Polymath Riemann--Siegel proposal roots would
  lie within 0.2 of the defining-integral roots is **VOID**: the largest
  displacement is 0.3334. This finite window supplies no bound on $\Lambda$.
- **MEASURED:** no named candidate tested in this lab has all three requested
  properties.

## Protocol

| Part | Prediction commit | Primary computation |
|---|---:|---|
| R4.1 | `c6f9358` | all-node finite-block heat-flow ODE |
| R4.2 | `bbf37eb` | published ODE and Bessel secular equation |
| R4.3 | `bff4c82` | Polymath proposal plus independent defining integral |
| R4.4 | `d97797a` | lab-wide source and prediction audit |

Every retained match has an explicit control and mutation below. Raw machine
outputs, source hashes, logs, and executable implementations are under
`codex-r4/`.

## R4.1 — $\Lambda$ from below, but only in a finite toy

The runner reproduces Fable's mirror-image dynamics

\[
 \dot x_j=\sum_{k\ne j}\frac{2}{x_j-x_k}
          +\sum_k\frac{2}{x_j+x_k}
\]

while dynamically evolving all 10,000 retained positive nodes and monitoring
all 9,999 gaps. Exact decimal offsets are retained before local centering. For
the remote blocks, the mirror field is recomputed at every call by a cubic
moment expansion with recorded first-omitted-tail bound below
$2.5\times10^{-40}$. DOP853 used `rtol=2e-9`, `atol=2e-12`; the event was
placed at $0.01g_{\min}$ and the remaining two-body time $\epsilon^2/8$ was
added. Thus “actual” below means the finite-block zero-gap estimate, not an
integration through the singularity.

### Primary collisions

| Block | exact midpoint $T$ | predicted $g_{\min}^2/8$ | full-block time | ratio | first colliding global pair |
|---|---:|---:|---:|---:|---:|
| A, first $10^4$ | 5448.908413286 | 1.77647103e-4 | 1.77801162e-4 | 1.000867 | 6709--6710 |
| B, near #$10^{12}$ | 267653396932.4000896404 | 3.85998709e-6 | 3.86067467e-6 | 1.000178 | 1000000008625--1000000008626 |
| C, near #$10^{21}$ | 144176897509546974243.30009392 | 3.51140900e-6 | 3.51394660e-6 | 1.000723 | 1000000000000000001635--1000000000000000001636 |
| D, near #$10^{22}$ | 1370919909931995308897.54512111 | 9.70474379e-6 | 9.80213467e-6 | 1.010035 | 10000000000000000006442--10000000000000000006443 |

**MEASURED:** all four registered identity/time predictions survive. As an
implementation control, the same all-node solver reproduces Fable's full
1,000-node T4 event `0.003317670111905755` and pair 922--923 exactly at stored
precision. A separately coded 1,024-node active-window calculation agrees
with all primary and mutation times within $7.1\times10^{-9}$ relative.

### Density-matched controls and delete-pair mutations

| Block | Poisson predicted | Poisson actual | actual / predicted | pair in block | Poisson / Odlyzko |
|---|---:|---:|---:|---:|---:|
| A | 2.58501e-12 | 2.58501e-12 | $\approx1.0000$ | 6184--6185 | 1.45388e-8 |
| B | 5.48602e-10 | 5.48602e-10 | $\approx1.0000$ | 9099--9100 | 1.42100e-4 |
| C | 1.23659e-10 | 1.23660e-10 | $\approx1.0000$ | 4800--4801 | 3.51911e-5 |
| D | 9.88681e-11 | 9.88680e-11 | $\approx1.0000$ | 2393--2394 | 1.00864e-5 |

| Block | mutation predicted | mutation actual | actual / predicted | mutation global pair |
|---|---:|---:|---:|---:|
| A | 2.33864213e-4 | 2.34117738e-4 | 1.001084 | 4765--4766 |
| B | 1.61911222e-5 | 1.62042893e-5 | 1.000813 | 1000000004240--1000000004241 |
| C | 1.06924221e-5 | 1.07095256e-5 | 1.001600 | 1000000000000000006362--1000000000000000006363 |
| D | 1.38801004e-5 | 1.39328938e-5 | 1.003804 | 10000000000000000003763--10000000000000000003764 |

**MEASURED:** every fixed-seed Poisson control is below $10^{-3}$ of the
corresponding Odlyzko time, its initial closest pair collides first, and its
two-body ratio is within $10^{-5}$ of one at the supported event/tail
precision. After deleting both members
of each primary colliding pair, the new closest pair collides first and each
registered mutation ratio lies in 0.85--1.20.

### Scaling and the theorem boundary

**PREDICTED:** the GUE cubic small-gap CDF gives
$s_{\min}=O(n^{-1/3})$. With
$d(T)=\log(T/2\pi)/(2\pi)$ and fixed $n=10^4$,

\[
 |t_c|=O(n^{-2/3}d(T)^{-2}).
\]

The expected exponent is therefore $-2$ in density, equivalently in
$\log(T/2\pi)$; the literal power of $T$ is zero with a squared-log
correction. Poisson has $|t_c|=O(n^{-2}d^{-2})$, hence ensemble-scale ratio
$n^{-4/3}\simeq4.64\times10^{-6}$. **MEASURED:** the four realized Odlyzko
times give slope $-1.78035$ for $\log|t_c|$ on $\log d$. Its preregistered
sign is negative, but four extreme gaps do not measure the ensemble exponent.

These are truncated-block times, not measurements, estimates, or bounds for
$\Lambda$. [Rodgers--Tao (2018)](https://arxiv.org/abs/1801.05914) proved
$\Lambda\ge0$: every negative heat time has a nonreal zero somewhere.
[D.H.J. Polymath (2019)](https://arxiv.org/abs/1904.12438) proved
$\Lambda\le0.22$: all zeros are real from heat time 0.22 onward. Neither
theorem equates $\Lambda$ to the first collision of a truncated block.

## R4.2 — two published 2011 compact models

### Operators and numerical realization

Berry--Keating's compact half-line quantization was evaluated through their
exact differential problem (Eqs. 2.7--2.9 and 2.22),

\[
 \chi''=\left(\frac{h(x)}{\eta^2}+\frac{i g(x)}{\eta}\right)\chi,
\quad h=1-\frac{E^2x^2}{4(1+x^2)^2},\quad
 g=\frac{E(1-x^2)}{2(1+x^2)^2},
\]

with $\eta=1/(2\pi)$, self-adjoint phase $\alpha=0$, and the decaying
solution shot backward by adaptive DOP853 from $x_{\max}=30$. The convergence
run used $x_{\max}=40$ and tighter tolerances. This is an ODE discretization,
not the semiclassical area rule.

Sierra--Rodríguez-Laguna was evaluated through their exact Eq. 14,

\[
 e^{-i\vartheta/2}K_{1/2+iE/(2\hbar)}(h/\hbar)+
 e^{i\vartheta/2}K_{1/2-iE/(2\hbar)}(h/\hbar)=0,
\]

with $h=1$, $\hbar=1/(2\pi)$, $\vartheta=\pi/4$. There is no spatial mesh:
energy meshes 0.002/60 decimal digits and 0.001/80 digits only bracket roots
of the published special-function equation. For both models $E$ is raw and
$t=2\pi E$ is the sole scale fixed by the published mean density; no fit or
offset used the zeta ordinates. Sources: [Berry--Keating
2011](https://doi.org/10.1088/1751-8113/44/28/285203) and
[Sierra--Rodríguez-Laguna 2011](https://doi.org/10.1103/PhysRevLett.106.200201).

### First 20 levels

| $n$ | zeta $\gamma_n$ | BK raw $E_n$ | BK $2\pi E_n$ | SRL raw $E_n$ | SRL $2\pi E_n$ |
|---:|---:|---:|---:|---:|---:|
| 1 | 14.134725 | 4.318828 | 27.135994 | 3.047883 | 19.150416 |
| 2 | 21.022040 | 4.913020 | 30.869412 | 3.904424 | 24.532220 |
| 3 | 25.010858 | 5.474752 | 34.398883 | 4.618686 | 29.020063 |
| 4 | 30.424876 | 6.010976 | 37.768076 | 5.259210 | 33.044588 |
| 5 | 32.935062 | 6.526428 | 41.006757 | 5.852013 | 36.769280 |
| 6 | 37.586178 | 7.024514 | 44.136325 | 6.410436 | 40.277955 |
| 7 | 40.918719 | 7.507783 | 47.172792 | 6.942445 | 43.620668 |
| 8 | 43.327073 | 7.978202 | 50.128521 | 7.453269 | 46.830270 |
| 9 | 48.005151 | 8.437329 | 53.013301 | 7.946568 | 49.929761 |
| 10 | 49.773832 | 8.886423 | 55.835043 | 8.425029 | 52.936021 |
| 11 | 52.970321 | 9.326520 | 58.600255 | 8.890697 | 55.861894 |
| 12 | 56.446248 | 9.758485 | 61.314368 | 9.345170 | 58.717435 |
| 13 | 59.347044 | 10.183047 | 63.981974 | 9.789732 | 61.510699 |
| 14 | 60.831779 | 10.600832 | 66.606995 | 10.225429 | 64.248263 |
| 15 | 65.112544 | 11.012379 | 69.192817 | 10.653129 | 66.935583 |
| 16 | 67.079811 | 11.418155 | 71.742386 | 11.073563 | 69.577251 |
| 17 | 69.546402 | 11.818573 | 74.258287 | 11.487354 | 72.177173 |
| 18 | 72.067158 | 12.213996 | 76.742800 | 11.895035 | 74.738709 |
| 19 | 75.704691 | 12.604746 | 79.197952 | 12.297071 | 77.264776 |
| 20 | 77.144840 | 12.991110 | 81.625553 | 12.693868 | 79.757923 |

| Sequence | raw RMSE | scaled RMSE | scaled Pearson | scaled maximum residual |
|---|---:|---:|---:|---:|
| Berry--Keating | 43.948969 | 6.664356 | 0.998318 | 13.001269 |
| Sierra--Rodríguez-Laguna | 44.369587 | 2.986576 | 0.999492 | 5.015691 |
| smooth Riemann--von Mangoldt midpoint control | -- | 0.518942 | 0.999603 | 0.901765 |

**MEASURED:** $2\pi$ improves each raw RMSE by more than three, but both
candidates are worse than the parameter-free smooth control; neither has an
ordinal match within $10^{-6}$. The correlations are a mean-density effect.
The controls are independent residual identities: BK's nonlocal identity has
maximum relative residual $1.284\times10^{-12}$; SRL's direct nonlocal-boundary
quadrature has maximum relative residual $9.27\times10^{-15}$.

The convergence mutations change the scaled BK levels by at most
$2.252\times10^{-11}$ and the displayed SRL levels by zero at binary64 output
precision. Phase mutations $\alpha=\pi/2$ and $\vartheta=3\pi/4$ preserve the
published self-adjoint discrete constructions but move at least one scaled
level by more than 0.1. The BK ordinal shifts 14.15--19.29 include spectral
flow and are not continuously tracked eigenbranch displacements; SRL shifts
are 0.536--0.756.

| Candidate | Self-adjoint with discrete spectrum? | Chaotic without arithmetic degeneracy? | Orbits of length $\log p$? |
|---|---|---|---|
| Berry--Keating compact Hamiltonian (2011) | yes in the cited construction; low spectrum **MEASURED** here | no (**VOID**) | no (**VOID**) |
| Sierra--Rodríguez-Laguna (2011) | yes in the cited construction; low spectrum **MEASURED** here | no (**VOID**) | no (**VOID**) |

Both classical systems have one degree of freedom and are integrable. BK has
one primitive orbit per energy; SRL has $T_E\sim\log(E/h)$ rather than a
prime-indexed family. Neither row has three yeses.

## R4.3 — Polymath 15 in miniature

The normalization is

\[
 H_0(z)=\frac18\xi\!\left(\frac12+\frac{iz}{2}\right),\qquad
 H_t(z)=\int_0^\infty e^{tu^2}\Phi(u)\cos(zu)\,du.
\]

The primary proposal evaluator implements D.H.J. Polymath's Theorem 1.3,
$H_t(z)/B_t(z)=f_t(z)+O_{\le}(e_A+e_B+e_{C,0})$, with both length-$N$
sums and the published $e_A+e_B+e_{C,0}$ error bound. The sharper
$-C_t/B_t$ correction discussed after Corollary 1.4 was not used. On the registered rectangle
$210\le\Re z\le300$, $|\Im z|\le1$ at $t=0.2$, $N=4$ throughout. The
independent evaluator uses the defining $\Phi$ integral, 12 terms,
$0\le u\le1.25$, analytic differentiation, and 70-digit tanh--sinh
quadrature; the replay uses 100 digits and twice the contour mesh. Sources:
the [final Polymath paper](https://arxiv.org/abs/1904.12438) and its
[development wiki](https://michaelnielsen.org/polymath/index.php?title=Effective_bounds_on_H_t_-_second_approach).

| Case | real brackets | rectangle winding 48 / 96 | local windings | minimum separation | control/mutation |
|---|---:|---:|---:|---:|---|
| $t=0.20$ | 22 | 22 / 22 | 22 times 1 | 2.044629 | primary |
| $t=0.19$ | 22 | 22 / 22 | 22 times 1 | 2.028988 | registered mutation |
| $t=0$ | 21 | 21 / 21 | 21 times 1 | 1.690247 | normalization control |

**MEASURED:** in this rectangle, every defining-integral bracket lies on the
real segment, the full winding equals the sum of disjoint winding-one local
contours, and every analytic derivative is numerically nonzero. Each endpoint
or control root used 160 bisections, with maximum final bracket width
$5.45\times10^{-50}$; the three intermediate samples used 120. The
70/100-digit evaluator replay changes a root by at most
$3.03\times10^{-24}$. At $t=0$, the 21 roots are exactly the number of
tabulated $z=2\gamma_n$ in the rectangle and agree within
$4.66\times10^{-25}$, so the normalization control survives. Corresponding
$t=0.19$ and $0.20$ roots move by 0.000942--0.017326. At the intermediate
samples $t=0.1925,0.195,0.1975$, all 22 roots remain real, ordered, and
separated by at least 2.02899. Continuous unique tracking through every
$t\in[0.19,0.20]$ remains **UNVERIFIED**; the five sampled slices are
**MEASURED**, not a pathwise certificate.

The proposal $f_t$ finds 22 brackets, but its maximum displacement from the
defining-integral roots is 0.333435. The registered `<0.2` claim is therefore
**VOID**. A sampled minimum of
$|f_t|-(e_A+e_B+e_{C,0})$ is negative, so no whole-boundary interval/Rouché
certificate was obtained. Reality and simplicity in this modest window are
numerical **MEASURED** statements, not a proof for all zeros.

The full Polymath 15 argument established $\Lambda\le0.22$, not that every
zero of $H_{0.2}$ is real. Its Theorem 1.2 combines verified RH below
$X/2$, an asymptotic zero-free region at $t_0$, and an intermediate barrier;
using $t_0=y_0=0.2$ and
$X=6\times10^{10}+83952-1/2$ gives
$\Lambda\le t_0+y_0^2/2=0.22$. The published architecture does not reach
zero: it requires positive $t_0,y_0$, its effective estimates are not uniform
as $t_0\to0$ and begin at a threshold of size $\exp(C/t_0)$, while a finite
RH verification yields only a positive $O(1/\log T)$ scale. Reaching zero
would need new uniform control at $t=0$ or RH itself, not a larger version of
this finite-window computation.

## Round-4 prediction audit

| Registered claim | Outcome |
|---|---|
| minimum pair and $g_{\min}^2/8$ predict all four full-block events | **MEASURED** |
| density exponent $-2$; four realized times have negative fitted slope | **PREDICTED** ensemble exponent; **MEASURED** slope $-1.78035$ |
| all Poisson controls much earlier; all delete-pair mutations select the new minimum | **MEASURED** |
| both 2011 spectra share the mean density but miss arithmetic fluctuations | **MEASURED** |
| convergence, residual, smooth-density, and phase controls | **MEASURED** |
| 22 real/simple $H_{0.2}$ zeros in the finite rectangle | **MEASURED**; interval proof **UNVERIFIED** |
| proposal/integral displacement below 0.2 | **VOID**; measured maximum 0.333435 |
| $t=0$ count equals the applicable $2\gamma_n$ count | **MEASURED** |
| endpoint $t=0.19$ mutation retains 22 and moves roots | **MEASURED**; pathwise unique continuation **UNVERIFIED** |
| no named row has all three requested properties | **MEASURED** audit result |

## Cumulative three-yeses table

The first column asks only whether the cited construction supplies a
self-adjoint discrete spectrum; it does not silently say that spectrum equals
the Riemann ordinates. The final two columns require an actual dynamical
mechanism and prime-labelled periodic orbits, not a statistical resemblance
or explicit-formula support.

| Candidate | Self-adjoint with discrete spectrum? | Chaotic without arithmetic degeneracy? | Orbits of length $\log p$? |
|---|---|---|---|
| fixed-interval $xp$ | yes (**MEASURED**) | no (**VOID**) | no (**VOID**) |
| modular-surface Laplacian | yes (**MEASURED**) | no: Hecke arithmetic degeneracy (**VOID**) | no (**VOID**) |
| Berry--Keating phase-space cutoff | operator not supplied (**UNVERIFIED**) | no (**VOID**) | no (**VOID**) |
| Bender--Brody--Müller (2017) | domain/self-adjointness disputed (**UNVERIFIED**) | no demonstrated mechanism (**UNVERIFIED**) | no (**VOID**) |
| Weil / Connes--Consani finite test family | discrete Hamiltonian not supplied (**UNVERIFIED**) | no demonstrated mechanism (**UNVERIFIED**) | explicit $\log(p^k)$ support is not an orbit construction (**VOID**) |
| Berry--Keating compact Hamiltonian (2011) | yes in the cited construction; spectrum **MEASURED** | no (**VOID**) | no (**VOID**) |
| Sierra--Rodríguez-Laguna (2011) | yes in the cited construction; spectrum **MEASURED** | no (**VOID**) | no (**VOID**) |

No row has three yeses.

## Honest paragraph

Round 4 made the finite claims harder to fake and left the global problem
untouched. The minimum-gap collision law is extremely accurate for four fully
evolved 10,000-body truncations, but an omitted infinite exterior is exactly
what prevents those times from saying anything quantitative about $\Lambda$.
The two 2011 operators really are named self-adjoint discrete constructions,
and their numerics converge, but a smooth quantile control predicts the first
20 ordinates better because all three contain only the mean counting law; none
contains prime-labelled orbit fluctuations. The Polymath miniature correctly
counts a finite set of real, simple $H_{0.2}$ zeros and also catches its own
proposal error, but a finite winding calculation is not the global barrier
argument and the global barrier stops at 0.22. Across the lab, every surviving
pattern is either an established theorem seen numerically or a finite model
whose missing structure can now be named. The missing item remains a proved
self-adjoint arithmetic dynamical object, not more decimal agreement.

## Reproduction map

- R4.1: `codex-r4/r41_full_flow.py`, `r41-full-results.json`,
  `r41-full-results.csv`, `r41-full-run.log`, and `r41-full-notes.md`.
  `r41_truncated_flow.py` and its outputs are retained as the independent
  active-window surrogate, not the primary measurement. Download Odlyzko's
  official `zeros1`, `zeros3`, `zeros4`, and `zeros5` tables from
  <https://www-users.cse.umn.edu/~odlyzko/zeta_tables/>, save them as
  `zeros1.txt`, `zeros3.txt`, `zeros4.txt`, and `zeros5.txt`, then run
  `python3 codex-r4/r41_full_flow.py --data-dir /path/to/tables`; the runner enforces
  the four SHA-256 values stored in `r41-full-results.json`.
- R4.2: `codex-r4/r42/run_r42.py`, `metrics-r42.json`,
  `spectra-r42.csv`, `run-r42.log`, and `NOTES.md`.
- R4.3: `codex-r4/r43/r43_polymath.py`, `r43_contour_audit.py`,
  `r43_results.json`, `r43_contour_audit.json`, `r43_roots.csv`,
  `SHA256SUMS`, and `NOTES.md`.
- Round-level hashes: `codex-r4/MANIFEST.json`; regenerate them with
  `python3 codex-r4/build_manifest.py` after any edit.
