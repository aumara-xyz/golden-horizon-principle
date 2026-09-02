# R4.3 Polymath 15 miniature — audit notes

Status vocabulary in this directory is literal: **MEASURED** means a
repeatable finite-precision computation; **UNVERIFIED** means that no interval
or analytic certificate was produced.  Nothing here measures or bounds the
de Bruijn–Newman constant.

## Scope and normalization

The registered rectangle is

\[
  210\leq \Re z\leq300,\qquad |\Im z|\leq1,
\]

at `t=0.2`; the mutation is `t=0.19`, and the independent control is `t=0`.
The final-paper normalization is

\[
H_0(z)=\frac18\xi\!\left(\frac12+\frac{iz}{2}\right),\qquad
H_t(z)=\int_0^\infty e^{tu^2}\Phi(u)\cos(zu)\,du,
\]

\[
\Phi(u)=\sum_{n\ge1}(2\pi^2n^4e^{9u}-3\pi n^2e^{5u})
e^{-\pi n^2e^{4u}}.
\]

The proposal evaluator is D.H.J. Polymath (2019), Theorem 1.3, equations
(13)–(24):

\[
\frac{H_t(z)}{B_t(z)}=f_t(z)+O_{\leq}(e_A+e_B+e_{C,0}),
\]

with the two length-`N` sums in equation (14), `N` from equation (19), and the
explicit bounds in equations (23)–(24).  On this whole rectangle `N=4`.  The
code implements the published `M_0`, `alpha`, `M_t`, `B_t`, `s_*`, `gamma`,
and `kappa` definitions directly.  It does not copy the project repository's
`Ht_Effective` routine.

## Independent evaluator

All reported actual roots and argument-principle counts use the defining
`Phi` integral, not `f_t`.  The implementation uses arbitrary-precision
tanh–sinh quadrature on `0 <= u <= 1.25`, 12 terms of `Phi`, and analytic
differentiation under the integral.  The primary pass uses 70 decimal digits
and tanh–sinh degree 8 (2,383 nodes); the convergence pass uses 100 digits and
degree 9 (5,125 nodes).  Multiplication by `exp(pi*z/8)` removes the numerical
decay without moving zeros or changing a closed-contour winding.

Each endpoint or control integral root was refined by 160 bisections; the
three intermediate continuation samples used 120.  The largest endpoint
final bracket width was `5.45e-50`; bracket width, however, is not the accuracy
of the quadrature.  The independent degree-8/degree-9 replay differed by as
much as `3.03e-24`, so narrative root values are capped at 20 decimal places.
Longer JSON/CSV strings are retained only as working values.

The omitted `u` tail and `n >= 13` terms are super-exponentially small at these
cutoffs, but that statement was not packaged as an interval bound.  It is
therefore part of the numerical convergence evidence, not a certificate.

## Results

| case | real brackets | rectangle winding, 48 edges | winding, 96 edges | local windings | minimum real-root separation |
|---|---:|---:|---:|---:|---:|
| `t=0.20` | 22 | 22 | 22 | 22 × 1 | 2.04462871919 |
| `t=0.19` mutation | 22 | 22 | 22 | 22 × 1 | 2.02898754892 |
| `t=0` control | 21 | 21 | 21 | 21 × 1 | 1.69024726765 |

**MEASURED:** on the registered rectangle the defining-integral winding equals
the sum of disjoint winding-one contours around the real roots.  The analytic
integral derivative is nonzero numerically at every root.  Thus the finite
calculation supports “22 real and simple zeros” at `t=0.2`, and the same claim
at `t=0.19`.  This is not an interval-certified assertion.

The 100-digit/degree-9 replay retained winding 22; the largest paired root
motion from the 70-digit/degree-8 run was `3.03e-24`.  At `t=0`, all 21
integral roots pair with `z=2*gamma_n`, with maximum displacement `4.66e-25`.
Both are below the registered `1e-8` thresholds.

The mutation moved every paired root: minimum shift
`0.00094200161706962145`, maximum shift `0.017325898108631838`.
At the intermediate samples `t=0.1925, 0.195, 0.1975`, the tracker found 22
ordered real roots each time; the minimum sampled separation was `2.02899`
and the largest adjacent-sample shift was `0.00434043`.  This is **MEASURED**
sampled continuation.  Unique continuation at every intervening value of `t`
remains **UNVERIFIED**.

The published `f_t` formula proposed 22 roots.  Its maximum displacement from
the defining-integral root was `0.33343477145541338`, so the registered `<0.2`
pairing prediction failed.  The point-sampled Theorem 1.3 error test also did
not give a whole-boundary Rouché certificate: the sampled minimum of
`|f_t|-(e_A+e_B+e_C0)` was `-0.364159...` at `t=0.2`.  This is why `f_t` is
used only to propose brackets here.

### Prediction accounting

- **MEASURED, survived:** 22 roots at `t=0.2`; all accounted for by real,
  simple local contours; minimum separation greater than 0.25; 70/100-digit
  root motion below `1e-8`; mutation retains 22 and shifts at least one by
  more than `1e-4`.
- **MEASURED, failed:** the Riemann–Siegel-to-integral pairing displacement is
  `0.3334`, not below `0.2`.
- **MEASURED, survived:** the `t=0` count is 21, exactly the number of
  tabulated values `z=2*gamma_n` in the fixed rectangle, and the paired
  numerical roots agree within `4.66e-25`. The ledger did
  not predict that this control would have the primary case's count of 22.
- **UNVERIFIED:** unique continuation at every `t` between `0.19` and `0.20`.
  Five sampled times support the ordinal pairing, but do not establish the
  continuous statement.
- **UNVERIFIED:** an interval/Rouché proof that the reported winding is valid
  on every contour arc.  The 48/96 meshes and 70/100-digit quadratures agree,
  but agreement is not a proof.

An exploratory 32-edge mesh aliased two windings (20, 20, 19 rather than 22,
22, 21).  Those raw values remain in `r43_results.json`; the registered 48-edge
and doubled 96-edge audit is in `r43_contour_audit.json`.

## What the full Polymath argument says

D.H.J. Polymath's Theorem 1.1 proves **Lambda <= 0.22**.  The proof applies its
Theorem 1.2 with `t0=y0=0.2` and
`X=6*10^10+83952-0.5`: verified RH below `X/2`, an asymptotic zero-free region
for `H_t0` to the right, and a finite intermediate-time barrier together give
`Lambda <= t0 + y0^2/2 = 0.22`.

The published architecture does not establish `Lambda=0`: its criterion
requires positive `t0` and `y0`, its effective approximation is stated for
`t>0`, and the paper explicitly notes that the relevant asymptotic is not
uniform as `t` approaches zero.  A finite RH verification supplies only the
left-hand part of the barrier.  Sending both positive parameters to zero
would require new uniform control at `t=0` (or RH itself), not merely a larger
version of this finite computation.  This is a limitation of the published
argument, not a theorem that every conceivable refinement is impossible.
More quantitatively, Theorem 1.5 reaches its asymptotic real-zero regime only
for `x >= exp(C/t)`, and Section 10 explains that RH verification through
height `T` leads at this architecture's scale to a positive `O(1/log T)` upper
bound.  No finite `T` makes that bound zero.

## Primary provenance

- Final paper, arXiv:1904.12438v2 (4 August 2019):
  <https://arxiv.org/html/1904.12438> and
  <https://arxiv.org/pdf/1904.12438v2>.  Relevant anchors: equations (1)–(4),
  Theorems 1.1–1.3, equations (13)–(24), Corollary 1.4, and Section 8.
- Polymath development wiki, “Effective bounds on H_t — second approach”:
  <https://michaelnielsen.org/polymath/index.php?title=Effective_bounds_on_H_t_-_second_approach>.
- Project code consulted for provenance, especially `Ht_complex` and
  `Ht_Effective`; not imported or executed by this audit:
  <https://github.com/km-git-acc/dbn_upper_bound/blob/master/dbn_upper_bound/python/mputility.py>.
- Prediction ledger commit: `bff4c82`.

Machine-readable results and full root rows are in `r43_results.json`,
`r43_contour_audit.json`, and `r43_roots.csv`.  `SHA256SUMS` freezes the local
artifacts.
