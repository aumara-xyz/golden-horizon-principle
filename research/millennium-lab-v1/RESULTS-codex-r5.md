# RESULTS — Codex round 5: the Weil–prolate bridge

Computational base: `aukora-deep` commit `19cd2cb`. Output branch:
`lab/millennium-v1-codex`. Every numbered part was appended to
`PREDICTIONS-codex-r5.md` and committed before its registered calculation.
Protocol deviations and post-hoc diagnostics are retained where they
occurred: the substituted `N=8` direct replay, the unregistered inversion-even
projection and raw-root labels, the matched path controls, the Jensen
checkpoint choices, and the omitted graph repetition cutoff. Fable's files
were not edited. Status vocabulary is **MEASURED / UNVERIFIED / PREDICTED /
VOID**.

## Source correction first

**MEASURED:** both requested records exist, but the second paper is not dated
as previously remembered. [Connes–Consani–Moscovici,
*Zeta Spectral Triples*](https://arxiv.org/abs/2511.22755), was submitted 27
November 2025. [Chuk, *Weil positivity in compact windows: certified two-sided
bounds and a Landau–Widom decay law*](https://arxiv.org/abs/2608.24827), was
submitted to arXiv 25 August 2026 and its title page says 26 August 2026, not
27 August. The complete PDFs were read before any computation; their hashes,
exact title/date records, compliant short quotations, and faithful abstract
synopses are frozen in `PREDICTIONS-codex-r5.md`. The requested full verbatim
abstracts were not reproduced because each exceeds the per-source quotation
limit; this is an explicit R5.0 deliverable limitation, not a claim that the
synopses are verbatim. A 13-word abstract opener present in the preregistration
commit was redacted after computation solely to keep the aggregate quotation
within that limit; no prediction was changed.

The 2026 paper does not complete the 2025 program. It reports a fixed-window
simple/even certificate at `L=0.8`, while the convergence bridge is expressly
left untouched. Its archive contains TeX and two figures, but no executable
code, coefficient vector, interval matrix, quadrature order/nodes, or
machine-readable certificate. It does state a Gauss–Legendre family and
matrix sizes, but not enough machine detail to replay the enclosure. Equation
(4)'s fitted equality is Conjecture 10, and the decisive potential estimate
invoked for the conditional theorem
is not supplied. Those source-dependent numerical certificates remain
**UNVERIFIED** here. The 2025 archive likewise supplies no code, raw matrix,
eigenvector, root brackets, or interval certificate; its chance figure has no
stated null model and is **VOID** as evidence.

The two unproved conditions in the 2025 construction are, faithfully
paraphrased: prove that the compact-window Weil operator's bottom eigenvalue
is simple with an even eigenfunction; then prove that the prolate candidate
approaches that true ground state strongly enough to transfer its transform
zeros. Round 5 measures the finite versions separately.

## Result first

- **MEASURED:** the pseudo-prime gate completed before scoring or target
  access. When the separate scorer was allowed to run, all ten pseudo-prime
  controls missed, with RMSE `23.253`–`25.919`. This is the first computed
  accuracy reported in this document.
- **MEASURED:** an independent implementation reproduces the finite Weil
  matrices. At 100 digits, every one of 29,161 upper-triangle entries in each
  of `x=9,12,13,14` differs from the independently committed Fable builder by
  at most `2.286e-100`.
- **MEASURED:** after the pseudo-prime gate, the authentic `x=13` and `x=14`
  spectra land on frozen zero indices 20–50, with RMSE `7.477e-4` and
  `1.396e-6`. The archimedean control, weight permutation, and deletions of
  `2,3,5,7,11` all miss by order 20.
- **VOID:** this accuracy does not identify the finite Weil matrix as the
  source of the match. The initial prolate-only runner imposed an
  inversion-even projection not explicit in the ledger and lands with RMSE
  `3.357e-4`. A post-hoc audit of raw `E(h)` also lands at `3.623e-4` under a
  disclosed, noncanonical complex-root continuation; that root labeling is
  **UNVERIFIED**. Parameter-matched prolate controls also land in all eight
  `x=14,16` matching path cases. This is a mathematical control degeneracy,
  not a software oracle: the integer-dilation map has a zeta factor in its
  Mellin transform.
- **MEASURED:** the primary raw prolate-to-Weil residual/gap ratio does not
  show the predicted decay. It grows from `3.21e5` at `x=5` to `6.74e42` at
  `x=20`; on the final five points, `N=120` is described best among the
  registered models by `2.15e-8 exp(5.830 x)`. The actual vector angle gets
  smaller at the final endpoint, but the spectral gap collapses much faster,
  so every computed residual/separation angle bound is trivial.
- **MEASURED:** the finite `N=120` even ground state is separated from the
  first odd and second even levels at all six registered cutoffs and both
  mutations by direct Arb eigenvalue balls. Certified frustrated triangles
  obstruct the positivity-improving and M-matrix arguments, and minors through
  order four obstruct strict sign regularity. The continuous lemma remains
  **UNVERIFIED**.
- **UNVERIFIED:** no degree-2, degree-3, or degree-4 Jensen horizon was found.
  Thirty-six fixed diagnostic stress polynomials are certified hyperbolic by
  all three requested methods, but the checkpoint shifts were selected after
  no horizon was bracketed; there is no predecessor/horizon pair and no
  measured scaling exponent.
- **MEASURED:** the finite Kuipers–Hummel–Richter butterfly swarm reproduces
  its prime trace after correcting an internal sign inconsistency in the
  printed formula. Genuine unitary central coupling creates mixed `log(pq)`
  lengths and spoils every tested primitive-prime coefficient; the smooth
  Weyl term persists and dominates the oscillatory trace increasingly.

## Protocol and oracle gate

| Part | Prediction commit | Computation boundary |
|---|---:|---|
| R5.0 | `36e02d2` | both PDFs and source archives audited |
| R5.1 | `d1136f8` | independent builder frozen before Fable code was read |
| R5.2 | `322fe69` | controls frozen |
| R5.2 gate | `c3828f6` | ten blind pseudo spectra committed before scorer existed |
| R5.3 | `761f687` | raw prolate candidate, norms, rectangles, and fit fixed |
| R5.4 | `4018574` | structural tests and mutations fixed |
| R5.5 | `73e6d1c` | Jensen and graph main parameters fixed; graph `m` omission disclosed below |
| R5.6 | `8cae764` | stretch prerequisite and certificate standard fixed |

The blind gate produced 60 ordered roots for each of seeds `52025001` through
`52025010`, recorded the output SHA-256 `9df471b6...b98fe0`, passed a static
zero-source scan, and contained no score or target. It was committed before
`score_after_gate.py` was created. The scorer verifies those hashes and emits
the ten pseudo metrics before any authentic accuracy. Reference ordinates
enter only that post-gate scoring process; they enter no matrix, coefficient,
parameter, window, root bracket, or stopping rule. The JSON score record
contains all 31 individual absolute errors for every scored row.

## R5.1 — independent finite Weil reconstruction

### Construction and low spectrum

With `x=lambda^2`, `L=log x`, and `|n|<=N`, the independent builder evaluates

\[
 QW_\lambda(V_n,V_m)=W_{0,2}(V_n,V_m)-W_{\mathbb R}(V_n,V_m)
 -\sum_{p^a\le x}(\log p)p^{-a/2}q(V_n,V_m)(a\log p).
\]

It uses every prime power at or below the cutoff, separate full/parity algebraic
paths, and Eq. (5.25)'s perturbed-scaling transform. Selected entries were
replayed from the defining distributions by tanh–sinh quadrature; an `N=8`
full matrix was independently parity-projected; transform roots were also
checked with a companion-matrix route. No zeta-zero source is imported.

The prediction ledger had fixed a complete `N=12` direct-integral replay.
That replay was not finished: `N=8` was substituted as a cheaper diagnostic
without updating the ledger. The `N=8` result is **MEASURED**, while the
registered `N=12` complete replay remains **UNVERIFIED**.

The following 100-digit values are the low Weil-form spectrum reported before
the Fable diff. Scientific notation is shortened only in this table.

| `x` | first even | first odd | second even | finite ordering |
|---:|---:|---:|---:|---|
| 9 | `2.954058093e-38` | `1.127563264e-34` | `2.146101128e-31` | **MEASURED** |
| 12 | `5.122019734e-54` | `4.038815123e-50` | `1.693211454e-46` | **MEASURED** |
| 13 | `3.483988199e-59` | `3.055913398e-55` | `1.311854285e-51` | **MEASURED** |
| 14 | `1.459812952e-64` | `1.668002258e-60` | `9.384333647e-57` | **MEASURED** |

The perturbed scaling operator is the requested spectral candidate. Its first
five positive roots at 200 digits are below, shortened to 16 decimals. Values
which look identical at this display precision differ in the full JSON.

| `x` | root 1 | root 2 | root 3 | root 4 | root 5 |
|---:|---:|---:|---:|---:|---:|
| 9 | 14.13472514173469 | 21.02203963877155 | 25.01085758014569 | 30.42487612585951 | 32.93506158773919 |
| 12 | 14.13472514173469 | 21.02203963877155 | 25.01085758014569 | 30.42487612585951 | 32.93506158773919 |
| 13 | 14.13472514173469 | 21.02203963877155 | 25.01085758014569 | 30.42487612585951 | 32.93506158773919 |
| 14 | 14.13472514173469 | 21.02203963877155 | 25.01085758014569 | 30.42487612585951 | 32.93506158773919 |

All four requested cases were built at 100, 200, and 400 digits. The
production driver's maximum root movements on frozen indices 20--50 are:

| `x` | 100 to 200 digits | 200 to 400 digits |
|---:|---:|---:|
| 9 | `1.706e-67` | `1.089e-166` |
| 12 | `2.344e-52` | `1.791e-152` |
| 13 | `1.903e-49` | `8.328e-149` |
| 14 | `2.435e-46` | `4.895e-147` |

At `x=13,N=120`, the requested 100/200/400 working-digit replay gives the
same leading values, with maximum transform residuals at the reported roots
of `1.20e-101`, `1.72e-201`, and `1.64e-401`. The corresponding eigenpair
residuals are approximately `1.36e-130`, `4.31e-232`, and `4.78e-433` in the
guard-digit replay. The largest root displacement on frozen indices 20–50 is
`4.393e-49` from 100 to 200 digits and `1.114e-149` from 200 to 400 in the
fully independent replay. The production-driver comparison gives the same
rough conditioning loss. Thus the preregistered `1e-75` and `1e-160`
thresholds were too optimistic and are **VOID**; adding 100 working digits
still adds about 100 stable digits after the approximately 51-digit loss due
to the near-null spectral gap.

### Frozen accuracy, only after the pseudo control

“Lands” was frozen as RMSE at most `0.01` and maximum absolute error at most
`0.05`, with raw ordinal matching and no shift, fit, scale, or reordering.

| authentic case, 200 digits | RMSE | MAE | median absolute | maximum absolute | score |
|---|---:|---:|---:|---:|---|
| `x=9,N=120` | 3.581241 | 2.312907 | 1.509676 | 8.934310 | **MEASURED** miss |
| `x=12,N=120` | 0.0471578 | 0.0158599 | `2.893e-7` | 0.198089 | **MEASURED** miss |
| `x=13,N=120` | `7.47677e-4` | `2.41829e-4` | `1.045e-10` | 0.00300691 | **MEASURED** lands |
| `x=14,N=120` | `1.39592e-6` | `4.37794e-7` | `1.165e-14` | `5.34032e-6` | **MEASURED** lands |

The `x=13,14` landings survive all three precision runs and `N=112,128`.
For `x=13`, the mutation RMSE range is `7.240e-4`–`7.621e-4`; for `x=14`
it is `1.380e-6`–`1.469e-6`. All 60 reported roots are ordered and have a
nonzero numerical secular derivative. These are finite numerical spectra,
not a convergence theorem.

### Independent reconstruction diff and Fable disagreement table

Codex's builder and output were committed at `4a81d44` before Fable's
committed `ccm_triples.py` was inspected. The exact Fable source was then
replayed only through matrix construction; all 29,161 upper-triangle entries
were compared in all four requested cases. Fable serialized roots/eigenvalues
only for `x=9,13`: five roots at 30 significant digits and low eigenvalues at
15. That limits the spectral diff to those fields; a first-50
implementation-to-implementation spectral diff remains **UNVERIFIED**.

| Item | Fable | Codex / diff | Status |
|---|---:|---:|---|
| `x=9`, full upper triangle, 100 dps | committed formula builder | max `1.143e-100`, RMS `4.529e-102` | **MEASURED** agreement |
| `x=12`, full upper triangle, 100 dps | committed formula builder | max `2.286e-100`, RMS `9.643e-102` | **MEASURED** agreement |
| `x=13`, full upper triangle, 100 dps | committed formula builder | max `1.143e-100`, RMS `4.459e-102` | **MEASURED** agreement |
| `x=14`, full upper triangle, 100 dps | committed formula builder | max `1.714e-100`, RMS `5.749e-102` | **MEASURED** agreement |
| first five transform roots, `x=9` | 30 significant digits | max diff `3.753e-29` | **MEASURED** serialization agreement |
| first five transform roots, `x=13` | 30 significant digits | max diff `3.753e-29` | **MEASURED** serialization agreement |
| `x=9` displayed error vector | 49 roots; final row labelled `k=50` | final serialized error is actually index 49; Codex index-50 absolute error is 8.934310 | **MEASURED** disagreement |
| shared pseudo-first rule | accuracy commit `bc6f3bd` precedes control commit `3a9452f` | pseudo control did not precede Fable's first accuracy | **VOID** Fable accuracy under this round's protocol |

The protocol finding does not undo the implementation agreement. The raw
machine records are `independent-matrix-diff.json` and
`independent-reconstruction-diff.json`.

## R5.2 — hostile controls

### Primary controls

| construction | RMSE on 20–50 | maximum absolute | lands? | Status / interpretation |
|---|---:|---:|:---:|---|
| pseudo-primes, 10 seeds | 23.253–25.919 | 25.917–29.171 | no | **MEASURED** |
| archimedean only | 23.334 | 26.360 | no | **MEASURED** |
| smooth counting-law quantiles | 1.22168 | 1.94401 | no | **MEASURED** baseline |
| raw prolate `E(h)`, `x=13,N=120` | `3.62268e-4` | 0.00180015 | yes under post-hoc complex continuation | root labeling **UNVERIFIED**; **VOID** as an arithmetic-matrix discriminator |
| inversion-even prolate mutation, `x=13,N=120` | `3.35666e-4` | 0.00179988 | yes | numerical landing **MEASURED**; projection not explicit in ledger; discriminator **VOID** |
| true support, permuted weights | 25.374 | 28.946 | no | **MEASURED** |
| delete 2 and its powers | 22.974 | 26.443 | no | **MEASURED** |
| delete 3 and its powers | 25.410 | 29.199 | no | **MEASURED** |
| delete 5 and its powers | 22.733 | 26.048 | no | **MEASURED** |
| delete 7 and its powers | 23.062 | 26.533 | no | **MEASURED** |
| delete 11 and its powers | 22.710 | 26.022 | no | **MEASURED** |
| delete 13 | `7.47677e-4` | 0.00300691 | yes | **VOID** as a `p=13`-importance test |

**MEASURED:** these finite-Weil controls deliberately use the lowest
even-sector vector so that the same real-even transform and root enumerator
remain defined. That is not always the control's global ground state: the
archimedean-only and delete-`2,5,7,11` matrices have a lower odd eigenvalue.
Thus those rows are
generous sector-matched controls, not literal CCM global-ground replays; their
finite simple/even prerequisite already fails. Pseudo seeds `52025003`,
`52025006`, and `52025010` also have a lower odd sector. The permutation,
delete-3, delete-13, and authentic cases retain an even global minimum.

The pseudo prediction survives: no pseudo spectrum lands, all RMSEs greatly
exceed 0.5, and their range exceeds the authentic `x=12,13,14` spread. The
ablation ranking prediction is **VOID**: deleting 3, not 2, is most destructive
by RMSE, and deleting 13 changes nothing at the scale shown.

The `p=13` degeneracy is exact. At cutoff `x=13`, its support point is the
window endpoint and the matrix kernel there vanishes. Deleting it or changing
its weight by five percent therefore leaves the finite matrix unchanged; a
5% change to every surviving weight fails with RMSE `25.044`. Moving the
continuous cutoff to `x=13.25` while retaining the same prime-power set still
lands, with RMSE `1.427e-4`. Thus no special evidentiary role for the endpoint
prime survives.

The prolate-only control is more consequential, and its protocol defect is
retained. The ledger said to project raw `E(h)` into the Fourier basis; it did
not authorize the additional inversion-even projection imposed by the first
runner. That even-projected mutation lands and survives `N=112` and `N=128`
with RMSE `2.469e-4` and `4.197e-4`; a quadrature mutation returns
`3.357e-4`.

A post-hoc raw-complex audit was therefore run zero-blind. Because a nonreal
finite transform has no canonical “positive-root” order, it labels roots by
homotopy from the intrinsically bracketed even roots and then orders them by
real part. Under that disclosed convention, complex-distance scoring on
indices 20--50 gives RMSE `3.62268e-4`, MAE `1.27470e-4`, and maximum
`0.00180015`, so it also lands. Four versus eight homotopy steps agree to
`8.00e-154`, two contour resolutions each count 70 enclosed roots, and the
degree-160 mutation moves a root by at most `7.39e-26`. Nevertheless, the
post-hoc continuation label is **UNVERIFIED** as a canonical ordinal root
definition. The very small coefficient inversion defect, `1.719e-30`, can
still produce maximum `|Im z|=0.706` over all 70 ill-conditioned roots; on
indices 20--50 the maximum is `5.879e-4`.

Neither convention contains a Weil matrix or explicit prime comb, but neither
is arithmetically neutral:

\[
 \int_0^\infty \mathcal E(h)(u)u^{-iz}\,d^*u
 =\zeta(1/2-iz)\int_0^\infty h(v)v^{-1/2-iz}\,dv,
 \qquad \mathcal E(h)(u)=\sqrt u\sum_{m\ge1}h(mu).
\]

The finite compact-window calculation approximates this factorization. The
control landing is therefore explained without an ordinate leak, while the
claim that the finite Weil matrix supplies the observed zero locations is
**VOID** on this experiment.

### Three registered paths

| `x` | RMSE for `N=8x` | RMSE for `N=10x` | RMSE for `N=12x` | score |
|---:|---:|---:|---:|---|
| 8 | 6.93520 | 6.91621 | 6.88335 | **MEASURED** miss |
| 10 | 1.59860 | 1.58776 | 1.58530 | **MEASURED** miss |
| 12 | 0.049570 | 0.047158 | 0.046125 | **MEASURED** miss |
| 14 | `1.469e-6` | `1.364e-6` | `1.298e-6` | **MEASURED** lands |
| 16 | `3.017e-13` | `2.712e-13` | `2.607e-13` | **MEASURED** lands |

All 15 finite blocks have a strictly lower even level and 60 ordered,
numerically simple roots. At each fixed `x`, changing `N` moves indices 20–50
less than changing `x` by two, as predicted. A 140-digit replay at
`x=16,N=192` moves those roots by at most `1.254e-42`; doubling the root
enumerator subdivisions preserves all 60 roots. But nearest-neighbor labels
between cutoff nodes disagree for 29, 19, and 5 of the first 60 roots on
`8→10`, `10→12`, and `12→14`, before agreeing on `14→16`. Continuous-`x`
ordinal continuation and any infinite-path law remain **UNVERIFIED**.

### Post-hoc matched-control audit for every path landing

The original registration supplied only the `x=13,N=120` hostile-control
case, so the `x=14,16` path landings initially lacked same-parameter controls.
The following audit does not retroactively repair that preregistration gap.
It constructed a pseudo-prime, archimedean-only, and inversion-even prolate
spectrum at every matching `(x,N)` before its separate scorer ran; the scorer
emitted all pseudo metrics first. Construction was zero-blind, but the whole
audit is explicitly post-hoc.

The pseudo column is one seed (`52025001`) per cutoff, with that support
reused across `N`; it is not a fresh ten-seed ensemble. Every matched
archimedean matrix has a lower odd global level, so those rows use the same
generous lowest-even convention disclosed for the primary controls above.

| `x,N` | true-prime RMSE | matched pseudo RMSE | matched archimedean RMSE | matched prolate RMSE |
|---:|---:|---:|---:|---:|
| `14,112` | `1.46930e-6` | 28.0511 | 25.7566 | `1.61998e-5` |
| `14,120` | `1.39592e-6` | 28.0518 | 25.7570 | `2.07832e-5` |
| `14,128` | `1.37988e-6` | 28.0521 | 25.7573 | `1.93146e-5` |
| `14,140` | `1.36354e-6` | 28.0533 | 25.7577 | `1.44707e-5` |
| `14,168` | `1.29846e-6` | 28.0551 | 25.7584 | `1.17939e-5` |
| `16,128` | `3.01652e-13` | 32.0862 | 29.8467 | `4.80896e-9` |
| `16,160` | `2.71213e-13` | 32.0878 | 29.8475 | `3.04454e-9` |
| `16,192` | `2.60672e-13` | 32.0889 | 29.8481 | `4.25310e-9` |

**MEASURED:** all eight authentic and all eight prolate-only spectra land;
all pseudo and archimedean controls miss. The matched prolate maximum errors
are below `9.0e-5`. Its `x=14` pseudo support exactly replays the frozen
six-base/nine-term sampler; `x=16` generalizes the same zero-blind rule to the
authentic six-base/ten-term count. The largest control eigenpair
residual/gap diagnostic is `7.92e-45`, the largest binary64-seed-to-100-digit
root movement on indices 20--50 is `7.99e-14`, and the largest transform
residual is `2.64e-101`. These controls cover every numerical match, while
their post-hoc timing remains a protocol limitation. More importantly, the
same mathematical degeneracy survives every path: accuracy is **VOID** as a
test that the finite Weil matrix, rather than `E`, supplied the zero locations.

## R5.3 — measuring the missing bridge

The primary follows the frozen raw-complex convention. The regular prolate
modes 0 and 4 are combined to have zero integral, extended by zero, passed
through the finite integer-dilation map, projected to `E_N`, and normalized.
To escape the binary64 quadrature floor found in the first sweep,
`run_prolate_exact_grid.py` converts the 180-digit Legendre expansion to
powers and integrates every exponential term of the finite dilation sum in
closed form. Degree-200/160 cutoff pairs resolve `x<=16`; the same registered
construction at degrees 240/200 resolves `x=18,20`. In every final row the
residual exceeds ten times a conservative `4 ||M||_F delta` cutoff-action
diagnostic and the gap exceeds 100 times the arithmetic floor. This is a
high-precision convergence check, not an interval tail enclosure.

| `x` | `r` at `N=120` | `Delta` | `r/Delta` | actual `sin(angle)` |
|---:|---:|---:|---:|---:|
| 5 | `3.374e-9` | `1.050e-14` | `3.213e5` | `4.106e-4` |
| 6 | `9.132e-12` | `1.416e-19` | `6.447e7` | `2.952e-4` |
| 7 | `2.785e-14` | `1.641e-24` | `1.697e10` | `1.983e-4` |
| 8 | `6.575e-17` | `1.356e-29` | `4.848e12` | `2.062e-4` |
| 9 | `1.658e-19` | `1.127e-34` | `1.471e15` | `1.644e-4` |
| 10 | `3.815e-22` | `8.276e-40` | `4.609e17` | `1.403e-4` |
| 11 | `8.901e-25` | `6.865e-45` | `1.297e20` | `9.634e-5` |
| 12 | `2.179e-27` | `4.038e-50` | `5.396e22` | `9.144e-5` |
| 13 | `4.852e-30` | `3.056e-55` | `1.588e25` | `6.850e-5` |
| 14 | `9.305e-33` | `1.668e-60` | `5.579e27` | `6.210e-5` |
| 16 | `4.355e-38` | `5.606e-71` | `7.769e32` | `5.325e-5` |
| 18 | `2.123e-43` | `1.710e-81` | `1.241e38` | `3.873e-5` |
| 20 | `3.700e-49` | `5.494e-92` | `6.735e42` | `2.221e-5` |

**MEASURED:** the preregistered decay law is false on this finite grid. In
the registered form `r/Delta=C lambda^(-p)`, the last-five formal exponents
are `p=-192.72,-189.00,-192.18` at `N=96,120,144`; negative `p` means rapid
growth. All three discretizations retain that sign. Exponential growth in
`x=lambda^2` has the lowest AIC among the four registered fits:

| `N` | constant AIC | power AIC | `exp(a lambda)` AIC | `exp(a x)` AIC | fitted `a` |
|---:|---:|---:|---:|---:|---:|
| 96 | 29.30 | 10.24 | 7.95 | 5.30 | 5.967 |
| 120 | 29.04 | 0.58 | -8.14 | -9.72 | 5.830 |
| 144 | 29.21 | 2.33 | -5.18 | -21.94 | 5.932 |

This is a five-point finite-window description, not an asymptotic law. The
endpoint finite-vector angle is smaller even while the residual diagnostic
gets worse: `r/s` is already `3.21e5` at `x=5` and exceeds one everywhere. Hence
the asserted residual angle bound is only `sin(angle)<=1`. Cauchy–Schwarz then
gives the same bound on all three frozen real half-widths 32, 64, and 128
because only `|Im z|<=1/4` enters the evaluation norm. It increases from
`1.818` at `x=5` to `2.563` at `x=20`; it cannot transfer a zero on any of
the rectangles.

The raw/even-projected convention mutation gives `r/Delta=4.31810e14` versus
`4.31808e14` at `x=9,N=30`, and `1.58776e25` versus `7.36242e24` at
`x=13,N=120`. It changes a constant but not the failed trend. The
undeformed-Hermite ratio comparison remains **UNVERIFIED** because only its
binary64/composite-quadrature sweep exists and its uncertainty dominates the
near-null gap. Pseudo-prime seed `52025001` has well-resolved order-one
residuals `0.558`–`0.581`, so destruction of near-nullness is **MEASURED**;
however, its even gap becomes negative at `x=16,18,20`, so the registered
positive-gap final-five median comparison is **UNVERIFIED** rather than
forced into a signed ratio.

## R5.4 — finite simple/even lemma attempt

An independent Python-FLINT/Arb builder evaluated the same formula directly
at 180 decimal digits. `acb_mat.eig(algorithm="rump")` isolated the full even
and odd spectra. At `x=20`, a 260-digit residual replay reduced the difficult
even-ground relative residual upper bound to `1.30e-169`, below its
`5.49e-92` gap. All 56 independent mpmath/Arb entry-overlap checks pass, and
the final artifact contains no `nan` residual.

| case, `N=120` | first even | first odd | second even | separating gap | Status |
|---|---:|---:|---:|---:|---|
| `x=5` | `9.755e-18` | `1.051e-14` | `5.037e-12` | `1.050e-14` | **MEASURED** |
| `x=9` | `2.954e-38` | `1.128e-34` | `2.146e-31` | `1.127e-34` | **MEASURED** |
| `x=12` | `5.122e-54` | `4.039e-50` | `1.693e-46` | `4.038e-50` | **MEASURED** |
| `x=13` | `3.484e-59` | `3.056e-55` | `1.312e-51` | `3.056e-55` | **MEASURED** |
| `x=14` | `1.460e-64` | `1.668e-60` | `9.384e-57` | `1.668e-60` | **MEASURED** |
| `x=20` | `2.505e-96` | `5.494e-92` | `6.814e-88` | `5.494e-92` | **MEASURED** |
| `x=13`, delete 13 | unchanged | unchanged | unchanged | unchanged | **VOID** as mutation; ordering **MEASURED** |
| `x=13.25`, retain support through 13 | `1.264e-60` | `1.339e-56` | `7.398e-53` | `1.339e-56` | **MEASURED** |

The sign-conjugation tests fail constructively at every case. An
Arb-certified triangle has the wrong edge-sign product for entrywise-positive
off diagonals, and triangle `(0,1,2)` obstructs nonpositive M-matrix off
diagonals. A scalar shift cannot change either result. A deterministic search
found both positive and negative minors at every order one through four in
every tested even block; the selected determinant balls exclude zero. At `x=13`, for
example, the first positive-conjugation obstruction is `(0,5,38)` and the
cutoff mutation changes it to `(0,6,7)`.

This proves only eight finite matrix inequalities. It supplies no uniform
bound in `x`, no passage in `N`, and no theorem for the continuous compact
operator. Thus the requested partial argument is: the min–max/Arb route
**MEASURED** finite simple/even ordering, the three sign-structure promotion
routes are obstructed on the sample, and the first missing CCM condition
remains **UNVERIFIED**.

## R5.5a — rogue Jensen horizon

For `F(z)=8 xi(1/2+z)`, the standard positive theta-kernel integral used in
the [Riemann-zeta Jensen literature](https://arxiv.org/abs/1902.07321)
supplies the Taylor coefficients without a zero list; a second
[Xi-specific treatment](https://arxiv.org/abs/1910.01227) is the normalization
cross-reference. Multiplication by the registered rogue quartet gives the
exact coefficient recurrence

\[
 \gamma_\Gamma(n)=\gamma(n)+b_\Gamma n\gamma(n-1)
 +c_\Gamma n(n-1)\gamma(n-2),
\]

where `delta=1/4`,
`b=2(Gamma^2-delta^2)/(Gamma^2+delta^2)^2`, and
`c=1/(Gamma^2+delta^2)^2`.

No cubic nonhyperbolicity was resolved. For `Gamma=14.13`, every integer
shift through `floor(256 Gamma^2)=51,112` was screened. For `Gamma=100` and
`1000`, every shift through 100,000 plus 768 fixed geometric checkpoints up
to `256 Gamma^2` was screened; late binary64 cancellation is retained as
indeterminate, not classified. At shifts
`0, floor(Gamma log Gamma), floor(Gamma^2), floor(256 Gamma^2)` for each
Gamma, degrees 2, 3, and 4—36 polynomials total—were recomputed at 70 digits.
All 36 have disjoint real-compatible Arb root balls, exact-rational Sturm
count equal to degree, and positive Hermite inertia. These are isolated point
certificates, not certificates for the intervening shifts. The degrees and
ceiling were registered, but these four diagnostic checkpoint shifts were
selected only after the screen failed to bracket a horizon; they are not
preregistered mutations.

### Horizon-table addition

The older Li/Weil rows are repeated to make the requested addition explicit.
The first Li entry uses `Gamma=14.13` exactly; high-Gamma Li values are the
previous smooth-model extensions. The targeted Weil witness encodes Gamma
and is not a blind detector.

| criterion / deformation | `Gamma=14.13` | `Gamma=100` | `Gamma=1000` | Status |
|---|---:|---:|---:|---|
| Li positivity | `n=7,552` | model `571,135` | model `78,225,642` | first **MEASURED**; latter **UNVERIFIED** |
| Gamma-targeted compact Weil | `x=9.6380` | `x=12648.4` | `x=18188.4` | **MEASURED** but oracle-targeted |
| Nyman–Beurling / Báez-Duarte / Robin / Lagarias bare-quartet injection | not canonically defined | same | same | **UNVERIFIED** |
| cubic Jensen polynomial, this round | no horizon through exhaustive 51,112 screen | no certified horizon | no certified horizon | **UNVERIFIED** |

The preregistered finite, approximately quadratic Jensen-horizon prediction
is **UNVERIFIED**, with no exponent to report. Fixed low degree can be
insensitive to a rogue even when the full all-degrees Jensen criterion is not;
the computation does not justify extrapolating either a horizon or its
absence.

## R5.5b — quantum-graph surgery

The finite reconstruction follows [Kuipers–Hummel–Richter
(2014)](https://arxiv.org/abs/1307.6055) with inclusive prime cutoffs
`29,53,97,193` and `0<=k<=256`. The prediction ledger failed to specify the
independent repetition cutoff required by the source. The implementation
fixed `m<=8` before evaluating its traces and then used `m<=6,10` as
sensitivity mutations. This omission makes cutoff-specific amplitude
magnitudes not fully preregistered, although the repeated qualitative outcome
is **MEASURED**. The matched pseudo-prime swarm is evaluated first. A source
audit found that the plus sign printed after Eq. (14) contradicts Eqs.
(11)–(12), the paper's `p=2` example, and
Supplemental Eq. (B1). The uniquely consistent minus sign gives a finite
trace match at roundoff; the literal sign already misses `p=2,m=1` by
`sqrt(2)`.

| prime cutoff | primes | butterflies | authentic trace RMSE | pseudo versus prime RMSE | Weyl / oscillatory RMS |
|---:|---:|---:|---:|---:|---:|
| 29 | 10 | 80 | `4.81e-15` | 0.684 | 497.9 |
| 53 | 16 | 128 | `6.65e-15` | 0.853 | 842.5 |
| 97 | 25 | 200 | `1.07e-14` | 0.922 | 1359.1 |
| 193 | 44 | 352 | `1.82e-14` | 1.116 | 2500.9 |

The central surgery is the explicit unitary composition `S_C=C S_0` with
identity, normalized DFT, and fixed-seed Haar choices. Identity restores the
decoupled coefficients. DFT and Haar preserve unitarity, spoil every primitive
`log p` coefficient by more than 1%, and create two-step mixed lengths
`log(pq)`. In the directed-bond formalism of Kuipers--Hummel--Richter Eq. (5),
using this unitary matrix at the common vertex together with their matching
derivative boundary condition defines the self-adjoint Hamiltonian. The code
checks the finite boundary-matrix unitarity and trace coefficients, not the
operator domain or an eigenvalue list. Repetition-cutoff mutations `m<=6` and
`m<=10` give the same outcome. Central scattering leaves total length
unchanged, so the Weyl coefficient `L_tot/pi` neither cancels nor disappears:
it increasingly dominates the finite prime-trace RMS. More generally the
mixed lengths are logarithms of integer products, so exact arithmetic length
degeneracies remain; chaoticity itself was not tested.

### Three-yeses table

“Self-adjoint” below means a demonstrated discrete operator, not merely a
formal trace identity. Explicit prime support is not counted as a periodic
orbit construction.

| Candidate | Self-adjoint discrete spectrum? | Chaotic without arithmetic degeneracy? | Orbits of length `log p`? |
|---|---|---|---|
| bounded fixed-interval `xp` | **MEASURED** discrete comb | **VOID** integrable | **VOID** |
| modular Laplacian | **MEASURED** | **VOID** arithmetic degeneracy | **VOID** geodesics are not `log p` |
| finite GUE matrix | **MEASURED** finite matrix | **UNVERIFIED** as a classical flow | **VOID** |
| modular scattering | underlying Laplacian **MEASURED** self-adjoint; resonances are **VOID** as a discrete spectrum | **VOID** arithmetic degeneracy | **VOID** geodesics are not `log p` |
| Berry–Keating cutoff | **UNVERIFIED** | **VOID** integrable | **VOID** |
| Bender–Brody–Müller 2017 | **UNVERIFIED** domain | **UNVERIFIED**; no demonstrated mechanism | **VOID** |
| finite compact-window Weil form | **MEASURED** finite symmetric-matrix spectrum; **VOID** as an ordinate Hamiltonian | **UNVERIFIED**; no demonstrated mechanism | **VOID** prime support is not an orbit |
| CCM finite `D_log`, sampled cases this round | **MEASURED** self-adjoint discrete operator by Theorem 1.1 plus the certified finite hypotheses; asymptotic zero realization **UNVERIFIED** | **UNVERIFIED**; no demonstrated mechanism | **VOID** prime support is not an orbit |
| finite-field Frobenius | **VOID** as the requested integer operator | **VOID** | **VOID** |
| Berry–Keating compact 2011 | **MEASURED** cited discrete model | **VOID** integrable | **VOID** |
| Sierra–Rodríguez-Laguna 2011 | **MEASURED** cited discrete model | **VOID** integrable | **VOID** |
| coupled KHR butterfly swarm, this round | **MEASURED** unitary finite boundary matrix; its exact-unitary idealization is self-adjoint and discrete under KHR Eq. (5), but the domain/eigenvalues were not independently constructed | **VOID**: exact `log`-product arithmetic length degeneracies remain; chaos otherwise untested | **MEASURED** `log p` orbits remain, but wrong amplitudes and `log(pq)` pollution |

No row has three yeses or a demonstrated discrete spectrum equal to the
Riemann ordinates.

## R5.6 — stretch certificate

**UNVERIFIED:** the stretch computation was not promoted to an SDP/SOS run.
The mandatory prerequisite was a complete independent replay of the claimed
`L=0.8` outward-rounded tail certificate. The 2026 source states a
Gauss–Legendre scheme, matrix sizes, and aggregate error bounds, but omits the
quadrature order/nodes, coefficient data, interval matrix, and replayable
certificate. A complete independent reconstruction was not finished in this
round. Therefore no extension beyond `L=0.8` was attempted to completion or
claimed, and no negative conclusion about compact-window positivity follows.

## Prediction ledger

| Registered prediction | Outcome |
|---|---|
| R5.1-A: matrix identities and simple even finite ground | matrix identities and sampled direct checks **MEASURED** at 100 digits; substituted `N=8` complete replay **MEASURED**, registered `N=12` replay and predicted 200/400-digit direct-integral tolerances **UNVERIFIED**; finite even ordering separately **MEASURED** |
| R5.1-B: root reality/order and `<1e-75`, `<1e-160` precision shifts | reality/order **MEASURED**; numerical thresholds **VOID** |
| R5.1-C: independent implementations agree below `1e-70` / `1e-60` | all four matrices **MEASURED** below threshold; first-five roots agree at serialization precision, first 50 **UNVERIFIED** |
| R5.1-D: `N=112,128` preserve ordinal finite spectra | **MEASURED** |
| R5.2-A: no pseudo lands; every pseudo RMSE exceeds 0.5 | **MEASURED** |
| R5.2-B: arch/prolate/permutation miss; every deletion worsens; 2 then 13 most destructive | arch/permutation **MEASURED**; prolate miss and deletion ranking **VOID**; original even projection was not explicit in the ledger, while the post-hoc raw root labeling remains **UNVERIFIED** |
| R5.2-C: reality/simplicity, `N` smaller effect, no hostile path landing, no clean short law | finite reality and `N` effect **MEASURED**; no-hostile-landing prediction **VOID** because all eight matched prolate controls land; continuous ordinal path and clean-law component **UNVERIFIED** on five nodes |
| R5.2-D: landing cases survive precision and `N` mutations | **MEASURED**; prolate survives its added mutations too |
| R5.3-A: `r/Delta` decays as `lambda^-p`, `p` in 1.25–2.75 | **VOID**; ratio grows, with formal `p=-189.00` at `N=120` |
| R5.3-B: usable angle bound for `x>=12` | **VOID**; `r/s>1` everywhere and transform bound is trivial |
| R5.3-C: Hermite/pseudo larger; slope sign survives `N=96,144` | slope failure survives **MEASURED**; control ratio comparisons **UNVERIFIED** |
| R5.4-A: finite even ground ordering at six points | **MEASURED** by corrected Arb replay |
| R5.4-B: sign/M-matrix/minor routes obstructed | **MEASURED** finite obstructions; uniform lemma **UNVERIFIED** |
| R5.4-C: ordering survives delete-13 and cutoff-13.25 mutations | delete-13 is **VOID** as a mutation because the endpoint term vanishes identically, although equality/order are **MEASURED**; the genuine cutoff-13.25 mutation is **MEASURED** |
| R5.5-A: finite cubic Jensen horizons with near-quadratic scaling | **UNVERIFIED**; no certified horizon and no exponent |
| R5.5-B: graph trace match, coupling spoils primes, Weyl persists | qualitative result **MEASURED** across `m=6,8,10`; omitted `m` preregistration disclosed |
| R5.5-C: no three-yes graph row | **MEASURED** |
| R5.6-A: no valid extension in this run | **UNVERIFIED** exactly for the preregistered missing-certificate blocker |

## Honest paragraph

Round 5 independently reproduces a remarkable finite numerical construction,
but its strongest-looking output is not its strongest evidence. Authentic
prime weights pass controls that random and permuted weights fail, yet the
prolate-only control places the same zeros more accurately because the
integer-dilation map already carries zeta in Mellin space. That makes the zero
match **VOID** as a test of whether the finite Weil matrix supplied the
arithmetic. The test that cannot be bypassed is the missing bridge: a
quantitative residual small relative to the collapsing spectral gap, with a
usable uniform transform bound. Here the candidate vector really does move
closer to the finite ground state, but `r/Delta` grows by 37 orders of
magnitude and the computed residual angle bound never becomes informative.
The finite even-ground ordering is certifiable, but every simple sign-structure
proof attempted here is obstructed; the butterfly graphs keep either the
prime trace or genuine coupling, not both with the right Weyl law; and fixed
low-degree Jensen
polynomials did not expose the rogue. The open problem is unchanged: construct
and control an arithmetic self-adjoint object strongly enough that the
critical-line spectrum follows as a theorem, rather than reappearing through
an identity already containing zeta.

## Reproducibility map

- Finite Weil builder and replays: `codex-r5/weil_core.py`,
  `run_true_reconstruction.py`, `WEIL-REPLAY-AUDIT.md`, and `true-*.json`.
- Gate and scoring: `run_pseudo_gate.py`, `pseudo-gate.json`,
  `blind-pseudo-spectra.json`, `score_after_gate.py`, and
  `accuracy-after-pseudo-gate.json`.
- Fable diff: `compare_fable_matrix_replay.py`,
  `independent-matrix-diff.json`, `compare_fable_committed.py`, and
  `independent-reconstruction-diff.json`.
- Controls and paths: `run_hostile_control.py`, `run_survivor_mutation.py`,
  `run_prolate_only_control.py`, `run_prolate_only_raw_control.py`,
  `run_posthoc_matched_controls.py`, `score_posthoc_matched_controls.py`,
  `run_n_paths.py`, `N-PATHS-NOTES.md`, `POSTHOC-MATCHED-CONTROLS.md`,
  `outputs/prolate-only-raw-blind.json`, and both
  `outputs/posthoc-matched-controls-*.json` artifacts.
- Bridge and finite lemma: `run_prolate_exact_grid.py`,
  `prolate-bridge-data/`, `finite_lemma_audit.py`, and
  `outputs/finite-lemma-audit.json`.
- Jensen and graph: `r55a/` and `outputs/quantum-graph/`, with method notes in
  `r55a/NOTES.md` and `QUANTUM-GRAPH-NOTES.md`.
