# R5.4 finite simple/even lemma audit

## Outcome

**MEASURED (finite statement only).** For each of the six registered points
$x\in\{5,9,12,13,14,20\}$ at $N=120$, and for both registered mutations,
an independently assembled, outward-rounded Arb matrix has one isolated
lowest eigenvalue in the even block.  Its enclosure is strictly below the
enclosures of the second even and first odd eigenvalues.  Thus the lowest
eigenvalue is simple and even for these eight finite matrices.

**UNVERIFIED.** This is not a result for the continuous compact-window
operator, for all $\lambda$, or for any limit in $N$.  No uniform mechanism
was found that would promote the eight finite certificates.  In particular,
the global first missing condition in Connes--Consani--Moscovici remains
**UNVERIFIED**.

| case | $\epsilon_{0,e}$ | $\epsilon_{1,e}$ | $\epsilon_{0,o}$ | certified separating gap | positive-conjugation obstruction | M-matrix obstruction | status |
|---|---:|---:|---:|---:|---|---|---|
| $x=5$ | $9.754959\,10^{-18}$ | $5.037135\,10^{-12}$ | $1.051119\,10^{-14}$ | $1.050143\,10^{-14}$ | $(0,2,48)$ | $(0,1,2)$ | **MEASURED** |
| $x=9$ | $2.954058\,10^{-38}$ | $2.146101\,10^{-31}$ | $1.127563\,10^{-34}$ | $1.127268\,10^{-34}$ | $(0,3,65)$ | $(0,1,2)$ | **MEASURED** |
| $x=12$ | $5.122020\,10^{-54}$ | $1.693211\,10^{-46}$ | $4.038815\,10^{-50}$ | $4.038303\,10^{-50}$ | $(0,2,15)$ | $(0,1,2)$ | **MEASURED** |
| $x=13$ | $3.483988\,10^{-59}$ | $1.311854\,10^{-51}$ | $3.055913\,10^{-55}$ | $3.055565\,10^{-55}$ | $(0,5,38)$ | $(0,1,2)$ | **MEASURED** |
| $x=14$ | $1.459813\,10^{-64}$ | $9.384334\,10^{-57}$ | $1.668002\,10^{-60}$ | $1.667856\,10^{-60}$ | $(0,2,72)$ | $(0,1,2)$ | **MEASURED** |
| $x=20$ | $2.504714\,10^{-96}$ | $6.814324\,10^{-88}$ | $5.494073\,10^{-92}$ | $5.493823\,10^{-92}$ | $(0,3,23)$ | $(0,1,2)$ | **MEASURED** |
| $x=13$, delete base 13 | $3.483988\,10^{-59}$ | $1.311854\,10^{-51}$ | $3.055913\,10^{-55}$ | $3.055565\,10^{-55}$ | $(0,5,38)$ | $(0,1,2)$ | **MEASURED** |
| $x=13.25$, retain $p^a\le13$ | $1.264380\,10^{-60}$ | $7.397973\,10^{-53}$ | $1.338941\,10^{-56}$ | $1.338815\,10^{-56}$ | $(0,6,7)$ | $(0,1,2)$ | **MEASURED** |

The displayed gap is
$\min(\epsilon_{1,e},\epsilon_{0,o})-\epsilon_{0,e}$.  The JSON artifact
contains the full Arb balls rather than the shortened midpoints in this
table.

## Structural tests

**MEASURED.** Neither of the two sign-conjugation routes survives even at a
single registered point.  For entrywise-positive off diagonals, graph
propagation requires the product of the three original edge signs around
every triangle to be positive.  Each row above gives an Arb-certified
triangle where it is negative.  For nonpositive M-matrix off diagonals the
required triangle product is negative; the lexicographically first triangle
$(0,1,2)$ has three positive edges in every case, so it is an obstruction.
A scalar shift changes no off-diagonal entry and therefore cannot remove
either obstruction.

**MEASURED.** The deterministic search over row and column indices $0$ through
$11$ found both a positive and a negative minor at each order one through
four in every case.  Every selected determinant was then recomputed as an
Arb ball excluding zero.  One representative set at $x=13$ is:

| order | positive rows / columns | midpoint | negative rows / columns | midpoint |
|---:|---|---:|---|---:|
| 1 | $(0)/(0)$ | $4.5332844\,10^{-2}$ | $(0)/(6)$ | $-4.9812308\,10^{-2}$ |
| 2 | $(0,1)/(0,1)$ | $4.4973104\,10^{-7}$ | $(0,1)/(0,6)$ | $-1.8238103\,10^{-4}$ |
| 3 | $(0,1,2)/(0,1,4)$ | $2.3352497\,10^{-12}$ | $(0,1,2)/(0,1,6)$ | $-1.1358950\,10^{-10}$ |
| 4 | $(0,1,2,3)/(0,6,8,10)$ | $1.8489581\,10^{-12}$ | $(0,1,2,3)/(0,6,9,10)$ | $-2.8923702\,10^{-12}$ |

These witness pairs disprove a single strict sign-regular pattern for the
finite blocks.  They do not classify every minor.

## Mutations

**MEASURED.** Moving the continuous cutoff from $x=13$ to $x=13.25$ while
holding the arithmetic support fixed is a genuine mutation.  It preserves
the simple/even ordering, but changes the first positive-conjugation
obstruction from $(0,5,38)$ to $(0,6,7)$.

**MEASURED but degenerate as a mutation.** Deleting the base prime 13 at
$x=13$ is an exact no-op.  Its only atom is at $y=\log 13=L$.  Both the
diagonal formula $2(1-y/L)\cos(2\pi n y/L)$ and the off-diagonal sine
difference vanish there.  Accordingly, the matrix and finite spectrum are
unchanged.  This registered mutation cannot be counted as evidence of
robustness; it instead exposes an endpoint degeneracy in the proposed test.

## Interval method and the two discarded diagnostics

The primary replay used Python-FLINT 0.6.0 at 180 decimal digits.  The
archimedean hypergeometric/digamma formula, pole term, and every prime-power
term were evaluated directly as Arb balls; the even and odd blocks were
formed algebraically in the orthonormal parity basis.  Seven entries per
case overlap independent 180-digit `mpmath` evaluations after explicitly
accounting for decimal rounding.  `acb_mat.eig(algorithm="rump")` isolated
all eigenvalues; the three balls used in each ordering are disjoint by wide
margins.  Selected signed edges and minors were also evaluated directly as
Arb balls.

An earlier exploratory artifact, now discarded, displayed
`arb_contains_mpmath_rounding=false`: it had asked a 165-digit rounded decimal
point to lie inside a much narrower roughly $10^{-180}$ ball.  This was a bad
containment predicate, not a matrix discrepancy.  The final artifact instead
checks overlap with an explicit decimal-rounding ball, and all 56 checks pass.
The same exploratory artifact displayed `relative_residual_norm=nan` because
rounding made a mathematically nonnegative squared norm a tiny symmetric ball
before `sqrt`.  The final code intersects it with $[0,\infty)$ first; no NaN
remains.  Neither diagnostic was used to establish the eigenvalue ordering,
which comes from the direct Arb eigensolve.

At 180 digits the $x=20$ enclosed eigenvector residual was too wide relative
to its $5.49\,10^{-92}$ separating gap, although the eigenvalue balls were
already disjoint.  A registered-formula replay at 260 digits reduced the
even-ground relative residual upper bound to $1.30\,10^{-169}$ and retained
the same ordering.  Thus the residual route also resolves the hardest sampled
case after increasing precision.

## Reproduction artifacts

- `finite_lemma_audit.py`: independent Arb builder, structural search, and
  enclosed eigensolve.  SHA-256
  `2c3197d977e6f60fe11fe84326d03e596c2788df9fe5e11656907ed0228156e7`.
- `outputs/finite-lemma-audit.json`: all eight 180-digit runs.  SHA-256
  `4c9c18f62c172aa302737fa14bd90abb1334c233ae6b9c05aba34b4e6e73362a`.
- `outputs/finite-lemma-x20-dps260.json`: high-precision residual mutation.
  SHA-256
  `ffd7dd0bb365d49d0498d7227a4b1c0e6d2fe2ec4c26153e1235f673bd38e312`.

All three source audits report no target-data import and no scoring code.
