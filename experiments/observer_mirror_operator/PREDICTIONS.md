# OBSERVER-MIRROR-OPERATOR v0 — preregistration

- Date locked: 2026-09-04
- Construction uses no primes and no zeta zeros.
- Status: operator skeleton only; no RH claim under any outcome.

## Frozen operator

Let `H_N = C^(2N+1) direct-sum C^(2N+1)` represent the visible and mirror sectors,
with Fourier labels `n=-N,...,N`. Propagation is

`D = diag(R_(1/3), R_(1/phi))`,

where `R_alpha[n,n] = exp(2*pi*i*n*alpha)`. The first side is periodic; the second is
quasiperiodic. Couple them with the symmetric unitary seam

`B = [[sqrt(1-q), i sqrt(q)], [i sqrt(q), sqrt(1-q)]] tensor I`,

using the fixed `q=exp(-2*pi*0.1)`. One time step is `U=B D`. The observer is the
orthogonal projection `P` onto the visible sector. The apparent one-sided evolution is
the compression `P U P`; radiation is norm transferred into `(I-P)H_N`.

At `N=40`, form the inverse Cayley transform

`H = i (I + exp(i*0.137) U) (I - exp(i*0.137) U)^(-1)`.

The phase shift avoids a pole and is fixed before computation.

Use a normalized Gaussian Fourier packet centered at `n=7`, width 5, initially entirely
visible. Evolve for 2,000 steps. Controls replace `1/phi` by `2/5`, `sqrt(2)-1`, and 200
uniform random angles, seed 20260904; controls run before the authentic case. The primary
recurrence score is the maximum full-state fidelity with the initial state over steps
100 through 2,000. Smaller means a more strongly delayed return.

## Predictions

1. **PREDICTED:** `U` is unitary and the Cayley `H` is self-adjoint to `1e-11`.
2. **PREDICTED:** total norm remains one while visible norm varies, giving an exact model
   of globally conserved information that looks radiative to the observer.
3. **PREDICTED:** the irrational sector delays full-state recurrence relative to the
   rational `2/5` control, but `phi` does not beat 95% of random irrational controls under
   this whole-operator statistic.
4. **PREDICTED:** the eigenphase spacings are not closer to GUE than both Poisson and GOE.
5. **PREDICTED:** self-adjointness is obtained, but the construction generates neither
   zeta's prime trace nor its `T log T` count. Thus it supplies the first box—real spectrum—
   while leaving the zeta-identification box completely open.

## Measure-theoretic boundary

Rationals and irrationals are both dense, so there is no spatial interface between them.
Moreover, rationals have Lebesgue measure zero; in ordinary `L^2([0,1])`, projection onto
functions supported only on rationals is the zero projection. The two-sector construction
is therefore an explicit modeling choice, not a discovered physical boundary.
