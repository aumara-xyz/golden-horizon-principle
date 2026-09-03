# R5.2 three registered N(x) paths

Status: **MEASURED** for the finite computations below; **UNVERIFIED** for any
continuum or infinite-path inference.

## Protocol and implementation

The frozen grid was evaluated at

\[
x\in\{8,10,12,14,16\},\qquad N\in\{8x,10x,12x\}.
\]

Every matrix used the authentic prime-power comb, including all powers
`q=p^a <= x`, the same orthonormal even/odd parity split, and 100-decimal-digit
arithmetic.  The lowest even vector came from a full arbitrary-precision
eigensolve.  Its first 60 positive transform roots were found only by sign
brackets inside consecutive intrinsic Fourier-lattice intervals and then
arbitrary-precision refinement.  No target, scoring function, fitted scale, or
external ordinate was loaded.  Every artifact records
`target_data_present=false` and `scoring_present=false`.

Thirteen cases were recomputed.  The exact matching, already generated
artifacts `true-x12-N120-dps100.json` and
`mutation-x14-N112-dps100.json` were reused after parameter and blindness
checks.  `run_n_paths.py` is the resumable fixed-grid driver;
`summarize_n_paths.py` independently checks the roots and creates
`n-paths-summary.json`.  The maximum discrepancy between a closed-form
archimedean entry and its direct quadrature control was
`1.143e-100` over the sampled entries.

## Low spectra and numerical resolution

Here `gap` is
`min(second even, first odd) - first even`.  `r/gap` is the computed ground
eigenpair residual divided by this gap, not the prolate residual from R5.3.

| x | path | N | first even | gap | eigenpair r/gap | max root residual |
|---:|:---:|---:|---:|---:|---:|---:|
| 8 | 8x | 64 | 5.159560e-33 | 1.527601e-29 | 6.53e-72 | 1.78e-101 |
| 8 | 10x | 80 | 4.974686e-33 | 1.466836e-29 | 6.79e-72 | 1.29e-101 |
| 8 | 12x | 96 | 4.623698e-33 | 1.439202e-29 | 9.40e-72 | 1.59e-101 |
| 10 | 8x | 80 | 1.944498e-43 | 9.364294e-40 | 7.73e-62 | 2.01e-101 |
| 10 | 10x | 100 | 1.784385e-43 | 8.877495e-40 | 1.40e-61 | 1.02e-101 |
| 10 | 12x | 120 | 1.744459e-43 | 8.275962e-40 | 1.36e-61 | 1.72e-101 |
| 12 | 8x | 96 | 5.762606e-54 | 4.415552e-50 | 1.58e-51 | 1.49e-101 |
| 12 | 10x | 120 | 5.122020e-54 | 4.038303e-50 | 2.67e-51 | 1.17e-101 |
| 12 | 12x | 144 | 4.820889e-54 | 3.964536e-50 | 3.56e-51 | 1.38e-101 |
| 14 | 8x | 112 | 1.561731e-64 | 1.728862e-60 | 4.75e-41 | 1.75e-101 |
| 14 | 10x | 140 | 1.412158e-64 | 1.526315e-60 | 6.05e-41 | 1.64e-101 |
| 14 | 12x | 168 | 1.311129e-64 | 1.419852e-60 | 8.46e-41 | 2.20e-101 |
| 16 | 8x | 128 | 3.628570e-75 | 5.481029e-71 | 2.06e-30 | 1.84e-101 |
| 16 | 10x | 160 | 3.210830e-75 | 4.688103e-71 | 2.36e-30 | 2.27e-101 |
| 16 | 12x | 192 | 3.054207e-75 | 4.308506e-71 | 2.95e-30 | 1.93e-101 |

**MEASURED:** the even ground value is strictly below both competitors in all
15 finite blocks.  All cases yield 60 positive, strictly ordered roots.  Their
smallest neighbor spacing is `0.8451`; their minimum absolute secular
derivative is `1.604e-35`; the closest any root lies to an intrinsic lattice
pole is `2.496e-4`.  These are finite simple-root diagnostics, not interval
certificates.

The least favorable case, `(x,N)=(16,192)`, was rebuilt at 140 digits and its
ground vector refined from the 100-digit result.  The ground eigenvalue moved
by `3.331e-102`; the maximum displacement among roots 1--60 was `2.923e-37`,
and among ordinals 20--50 it was `1.254e-42`.  The repeated eigenpair residual
was `1.375e-142`.  This precision mutation confirms that 100 digits resolve
the finite spectrum used in the path table.

As an independent enumerator mutation, the maximum-N cases at `x=8` and
`x=16` were rerun with 64 rather than 32 subdivisions in every intrinsic
lattice interval.  Both returned the same 60 roots; the maximum displacements
were `1.026e-85` and `7.208e-69`, respectively (`1.966e-71` on ordinals
20--50 for the latter).

## Path diagnostics

**MEASURED:** at every fixed `x`, both `8x -> 10x` and `10x -> 12x`
comparisons retain the same nearest ordinal for all 60 roots.  Over ordinals
20--50, the largest fixed-`x` displacement is `0.103754` (at `x=8`), while the
median of the ten per-comparison maxima is `0.00711543`.  The N-dependence
drops sharply with the cutoff: by `x=16` those two maxima are
`1.271e-13` and `4.396e-14`.

The preregistered local comparison survives at every point where `x+2` is in
the grid:

| x | largest N-change displacement, ordinals 20--50 | smallest x-to-x+2 displacement | N change smaller? |
|---:|---:|---:|:---:|
| 8 | 1.037535e-1 | 1.071349e1 | yes |
| 10 | 4.125085e-2 | 4.455996 | yes |
| 12 | 1.059001e-2 | 1.935653e-1 | yes |
| 14 | 4.072289e-7 | 4.964825e-6 | yes |

There is no clean uniform finite-path law: the per-comparison maxima vary by
more than twelve orders of magnitude.  Moreover, nearest-neighbor labels
across successive cutoff nodes disagree for 29, 19, and 5 of the first 60
roots on the transitions `8 -> 10`, `10 -> 12`, and `12 -> 14`, respectively;
they agree for `14 -> 16`.  The counts are the same on all three paths.  Each
endpoint spectrum is real, simple, and ordered, but continuity in continuous
`x` is therefore **UNVERIFIED** by this discrete grid.  These five points on
each path are not evidence for a limit as `x,N -> infinity`.

The JSON summary contains all 60 roots, complete low-spectrum strings,
artifact hashes, pairwise displacements, root slopes, pole separations, and
the 140-digit precision replay.
