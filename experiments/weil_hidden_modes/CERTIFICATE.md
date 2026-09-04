# Finite Weil-form interval certificate

2026-09-05. MEASURED: rigorous ball-enclosed computation, not merely
high-precision convergence. Preregistered at d7430f3. No zero ordinates used.

## Exact finite statement

Let L=7/10 and f_j(x)=sin(j*pi*(x+L)/(2L))/sqrt(L) on [-L,L], zero
outside, for j=1,...,16. Let W be the real symmetric matrix of the prime-side
quadratic expression in PREDICTIONS.md. For every nonzero real coefficient
vector c, the validated calculation establishes

    c^T W c > 10^-12 sum_j c_j^2.

Equivalently, this expression exceeds 10^-12 ||f||_2^2 on this particular
16-dimensional span. This is a computer-assisted finite statement, relying
on the documented ball-arithmetic guarantees and correctness of the code and
formula implementation. It is not a formally verified proof or a claim of novelty.

It also bounds the four-visible-mode Schur complement S below by 10^-12 I:
for each nonzero x, minimize (x,y)^T W (x,y) over y. The positive hidden block
ensures a finite minimizer, and the bound exceeds 10^-12 ||x||^2 there.

## What was enclosed

The sine correlations are evaluated by elementary analytic formulas, separately
on positive shifts. Parity-forbidden cross entries are exactly zero. All
constants, prime logs, weights, pole terms and the exact tail beyond 2L use Arb
balls. For this support the authentic terms are p^m=2,3,4; shifted controls
include precisely those shifted powers inside support, with explicit boundary
checks. There is no omitted arithmetic tail within the stated compact support.

For the archimedean integral, integrate from epsilon=10^-40 to 2L using
acb.integral at 384 bits with relative/absolute targets 10^-35. The targets
are not assumed error bounds: the returned ball radius is carried forward.
The integrand's analytic continuation is meromorphic, and interval evaluation
returns nonfinite values when a pole cannot be excluded. There are no
variable-dependent logarithms or branch choices in this integrand.

The small omitted interval is bounded explicitly, not discarded. For the
symmetrized correlation G_ij, Cauchy–Schwarz and translation give

    |G_ij(u)| <= 1,
    |G_ij(u)-delta_ij| <= a_max*u,
    a_max = 16*pi/(2L).

The zero-extended sines have weak first derivatives in L2 because their
endpoint values vanish. Their derivative norms are j*pi/(2L), which justifies
the translation bound above. Therefore, for 0<u<=epsilon,

    |(delta_ij - exp(u/2)*G_ij(u))/sinh(u)|
        <= a_max + exp(epsilon/2)/2.

Adding a zero-centered ball of radius epsilon times this bound encloses the
omitted integral. The bound is less than 3.641e-39 per entry. Beyond 2L,
G=0 and the exact remaining integral is -log(tanh(L))*delta_ij.

The largest final authentic entry radius is less than 1.746e-34. Interval
LDL elimination on W-10^-12 I gives 16 strictly positive pivot balls, saved
in certified_results.json. This proves positive definiteness by congruence;
pivot values are not eigenvalues. Every update propagates interval uncertainty.

## Controls and mutations

| Model | N=8 | N=12 | N=16 |
|---|---|---|---|
| Archimedean-only | negative direction certified | same | same |
| Prime-log +10%, weights unchanged | negative direction certified | same | same |
| Prime-log -10%, weights unchanged | negative direction certified | same | same |
| Authentic | positive definite certified | same | same |

Controls ran before authentic arithmetic. Negative LDL pivots certify negative
directions since previous pivots exclude zero. These shifted models are
artificial controls, not alternate zeta functions. Predictions all survived.
An additional LDL implementation check covers a known positive matrix, an
indefinite matrix and a singular matrix. All 256 correlation-at-zero checks
enclose the orthonormality identities.

## What remains blocked

This resolves the error-bound question for these 16 modes at L=0.7. It does
not estimate the interaction with the infinitely many omitted modes, nor
cover all support widths. If the entire operator is partitioned into tested
and untested parts, the expression A-C D^-1 C* needs a justified infinite-tail
bound (and suitable domains/invertibility); finite positive pivots do not
provide it. Other analytic routes could avoid this inverse, but none has been
established here. A uniform strictly positive gap across all windows is not
required by RH; nonnegativity on all admissible tests is the relevant target.

UNVERIFIED: the infinite-dimensional conclusion, any new RH mechanism, or
novelty of the finite result. No new physical law or mirror interpretation
has been demonstrated by this computation.

## Reproduction and sources

Tested with Python 3.9 and python-flint 0.6.0, installed in an isolated temporary
virtual environment. Install that version in an environment of your choice,
then run `python experiments/weil_hidden_modes/certify.py` and
`python experiments/weil_hidden_modes/test_certify.py`.

- Form: [Connes–Consani (2021), equations (1)–(3)](https://alainconnes.org/wp-content/uploads/Selecta.pdf).
- [Arb real-ball representation](https://python-flint.readthedocs.io/en/latest/arb.html).
- [Complex integral API and analytic requirements](https://python-flint.readthedocs.io/en/latest/acb.html).
- [FLINT rigorous integration guarantee](https://flintlib.org/doc/acb_calc.html).
