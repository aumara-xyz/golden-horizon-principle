# The mirror-inertia lemma

## Statement

Let `Z` be a finite set with an involution `j: Z -> Z`. Let `J` be the induced linear
operator on `C^Z`, `(Ja)_z=a_(jz)`, and define the Hermitian form

`Q_J(a)=<a,Ja>`.

If `j` has `f` fixed points and `p` two-cycles, then the inertia of `Q_J` is

`(number positive, number zero, number negative) = (f+p, 0, p)`.

In particular, `Q_J` is positive semidefinite on all of `C^Z` if and only if `j` has no
two-cycles.

## Proof

Reorder the basis so that the fixed points come first and the members of every two-cycle
are adjacent. The matrix of `J` is then the orthogonal direct sum of `f` blocks `[1]` and
`p` blocks

```text
M = [[0, 1],
     [1, 0]].
```

The block `[1]` has eigenvalue `+1`. For `M`, the vectors

`e_plus=(1,1)/sqrt(2)` and `e_minus=(1,-1)/sqrt(2)`

have eigenvalues `+1` and `-1`. Adding block inertias proves the formula. No numerical
approximation is involved.

## Riemann interpretation—and its limit

For the zero symmetry, use the anti-holomorphic mirror

`j(s)=1-conj(s)`.

Its fixed set is exactly `Re(s)=1/2`. Thus a zero on the critical line is a fixed point,
whereas a zero away from the line belongs to a two-cycle. In a finite amplitude model, the
mirror-odd observer `(1,-1)/sqrt(2)` detects that two-cycle as a negative direction.

This is the elementary block algebra beneath the positivity side of Weil's criterion; it
is not a new proof of that criterion. The actual Weil form is defined on an analytic class
of test functions, and the explicit formula equates its zero-side pairing with a geometric
side containing the archimedean term and prime powers. One cannot assign arbitrary,
independent amplitudes to infinitely many zeros without proving the required interpolation
and convergence statements.

The finite lemma therefore identifies the missing step rather than bypassing it:

`show Q_prime(f) >= 0 for every admissible f, using only the geometric/prime side.`

If that were proved on the full test-function space, Weil's criterion would give RH. A
Cholesky factorization of a finite sampled matrix is insufficient unless its positivity,
domain, and convergence remain uniform as the window and dimension tend to infinity.

## Observer lesson

If observers are restricted to the mirror-even subspace, every swap block looks positive.
The negative direction lives entirely in the mirror-odd subspace. Therefore “the observer
is in the middle” cannot mean that only symmetric observations are permitted: doing so
would remove the very measurements capable of detecting an off-line pair.

Likewise, replacing `J` by `J+cI` makes every two-cycle block positive semidefinite when
`c>=1`. This explains why regularization and finite precision require explicit accounting:
they can cover the negative direction rather than eliminate it.

## Primary context

- Enrico Bombieri, *Remarks on Weil's quadratic functional in the theory of prime
  numbers, I* (2000): the Weil functional is positive semidefinite exactly under RH.
- Alain Connes and Caterina Consani, *Weil positivity and Trace formula, the archimedean
  place* (2020/2021): operator-theoretic positivity via compressed scaling action and
  Sonin/prolate spaces.
- Xuefeng Zhu, *Weil positivity in compact windows* (2026): certified positivity on a
  finite support window and quantification of the barrier to extending that method.
