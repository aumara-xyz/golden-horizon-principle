# D10: an exact joint rewrite and a scoped obstruction

This is a derivation and a small ball-arithmetic check, not a new positivity
theorem. Its analogy with Viviani is joint accounting of terms, not an
identification of the Weil form with a triangle area or a physical geometry.

## Domain and conventions

First take complex `f` in `C_c^infinity((-L,L))`, extended by zero to the real
line. All identities below are then classical, all displayed differences are
integrable, and complex quadratic forms are interpreted as Hermitian forms.
Write

    g(u) = integral f(x+u) conjugate(f(x)) dx,
    F(t) = (2*pi)^(-1/2) integral f(x) exp(-itx) dx.

For the form domain on the finite interval, the archimedean integral is
finite when `integral log(2+|t|)|F(t)|^2 dt` is finite. The bounded prime and
pole terms do not alter this condition. Identities extend on this form
domain by form approximation, or by the translation/Plancherel identity for
the nonnegative jump integral. Outside it, the jump and archimedean terms
are `+infinity`; no subtraction of two infinite quantities is asserted.

The starting position-space formula is the one stated in
`../weil_hidden_modes/PREDICTIONS.md`, with `Re g(u)` for complex functions:

    W(f) = Pi(f) - (gamma+log(4*pi))*||f||^2
           + integral_0^infinity [||f||^2-exp(u/2) Re g(u)]/sinh(u) du
           - sum_n w_n Re g(log n),

where `w_n=2 Lambda(n)/sqrt(n)` and only prime powers satisfying
`log(n)<2L` contribute. Endpoint equality has zero overlap and can be omitted.
The pole is exactly

    Pi(f) = 2 |integral f(x) cosh(x/2) dx|^2
            - 2 |integral f(x) sinh(x/2) dx|^2.

This follows from `2 Re(M_+ conjugate(M_-))` with `M_+=C+S`, `M_-=C-S`.
In particular the odd pole is negative, not zero.

## The full jump-square rewrite

Set `D_u=||f(.+u)-f||^2=2||f||^2-2 Re g(u)`,
`k(u)=exp(u/2)/sinh(u)`, and `B=sum_n w_n` over the visible prime powers.
Then

    W(f) = (a0-B)||f||^2 + Pi(f)
           + (1/2) integral_0^infinity k(u) D_u du
           + (1/2) sum_n w_n D_log(n),

    a0 = psi(1/4)-log(pi)
       = -gamma-pi/2-3log(2)-log(pi).

Indeed the constant left by replacing `Re g(u)` by `||f||^2-D_u/2` is

    integral_0^infinity [1-exp(u/2)]/sinh(u) du = -pi/2-log(2).

For example, expand `1/sinh(u)=2 sum_(m>=0) exp(-(2m+1)u)` and integrate
the differences. The result is `psi(1/4)-psi(1/2)`, with
`psi(1/2)=-gamma-2log(2)`. The differences have one sign, so passage to
the series is justified by monotone convergence after changing sign.

Every jump-square term is nonnegative. The scalar term is negative and
the odd pole is negative. Thus this exact rewrite retains, rather than
proves, their required compensation. The prime sum in this rewrite is
finite: extending `B` alone to all prime powers would be invalid.

## The off-diagonal kernel and its sign

For disjointly supported test functions inside the interval, the continuous
off-diagonal Hermitian operator kernel of the full `W` is

    K(r) = 2cosh(r/2) - exp(r/2)/(2sinh(r)),  r=|x-y|>0.

The factor `1/2` in the second term results from symmetrizing the integral
over positive shifts into an integral over both signs. The pole contributes
`2cosh((x-y)/2)`. There are additionally negative prime-shift atoms

    -(w_n/2) [delta(y-x-log n)+delta(y-x+log n)].

The remaining scalar and near-diagonal renormalization do not affect
off-diagonal pairings of disjoint bumps.

Let `q=exp(r)>1`. Elementary simplification gives

    K(r) = (q^3-q-1) / [sqrt(q)*(q^2-1)].

Its denominator is positive and the numerator strictly increases for
`q>1`. Thus the unique sign transition is `r=log(rho)`, where
`rho^3-rho-1=0`. The appearance of this algebraic number is a consequence
of the fixed kernel, not a fitted constant or a golden-ratio hypothesis.

At `a=log(5/4)`, the two relevant values are exact:

    K(a)  = -19/(18 sqrt(5)) < 0,
    K(2a) = 5129/7380 > 0.

`kernel_test.py` encloses these independently by transcendental kernel
evaluation and by the displayed algebraic expressions, using 320-bit Arb.

## Actual smooth-bump restriction, not merely three plotted points

Use centers `x_1=-a`, `x_2=0`, `x_3=a`, and open intervals of radius
`epsilon=1/100` about them. The script encloses all interval calculations
and verifies that these intervals are disjoint, lie in `(-7/10,7/10)`, and
all cross distances are less than `log(2)`. Consequently every prime-shift
cross pairing between different bumps vanishes exactly.

For neighboring intervals, distances belong to
`[a-2epsilon,a+2epsilon]`; for the outer pair they belong to
`[2a-2epsilon,2a+2epsilon]`. Natural interval evaluation of `K` certifies it
strictly negative throughout the first interval and strictly positive
throughout the second.

Choose any nonzero nonnegative real smooth bump `b_i` in each open
interval, normalized in `L2`. They are orthonormal by disjoint support.
Their full-form off-diagonal entries are exactly

    W_ij = integral integral K(|x-y|) b_i(x) b_j(y) dx dy,  i != j.

The product has strictly positive integral and the kernel has the verified
strict sign throughout its support. Therefore this actual three-dimensional
restriction has off-diagonal signs `(-,-,+)` in edge order `(12,23,13)`.
No claim about this restriction's eigenvalues is inferred from those signs.

## What diagonal gauges cannot do

For a real sign gauge `s_i in {-1,+1}`, off-diagonal entries change to
`s_i s_j W_ij`. Their product around a triangle is unchanged because every
`s_i` occurs twice. The original product is positive. Three strictly
negative edges would have negative product. Thus no such gauge makes all
edges nonpositive; the script enumerates all eight to check the claim.

A positive diagonal scaling does not change any sign. For unit complex
phases, making an already real nonzero edge real negative requires phase
differences `0` for negative edges and `pi` for positive edges. The same
cycle-product obstruction applies. Arbitrary nonlocal changes of basis
are not excluded.

The corresponding continuum obstruction is to a pointwise diagonal
phase/positive gauge that makes the whole off-diagonal kernel real
nonpositive almost everywhere. Such a gauge would impose consistent edge
phases on almost every triple of points in the three neighborhoods, which
the same product identity forbids.

For a sufficiently regular strictly positive real comparison function `h`
and compactly supported `g`, the usual ground-state identity has the form

    W(hg) - integral h(x)(Wh)(x) |g(x)|^2 dx
      = -(1/2) integral integral K(x,y) h(x)h(y)
                                      |g(x)-g(y)|^2 dx dy,

including the prime atoms. The local scalar terms cancel. This identity
can first be read with a near-diagonal cutoff and then passed to the form
limit where the displayed quantities are defined. Its right-hand side is
not a nonnegative-conductance energy when `K` has the above signs.

The obstruction is therefore **only** to a local diagonal-gauge
positive-conductance pairwise-square representation of the full form.
It does not say `W` is indefinite, exclude a remainder that compensates
signed jumps, exclude a nonlocal sum of squares, or obstruct RH itself.

## Controls that enforce that limited conclusion

1. Removing the pole leaves continuous kernel
   `-exp(r/2)/(2sinh(r))<0`. Its three edges have no sign-cycle obstruction.
   This does not imply positivity of the entire pole-free form, whose
   diagonal and other terms still matter.
2. Reversing only the positive long edge removes this triangle obstruction.
   This is an artificial signed-edge mutation, not a modified zeta function.
3. Let `v=(1,-1,1)` and `A=(1/2)I+vv^T`. It has the same frustrated
   triangle, but exactly

       x^* A x = (1/2) sum_i |x_i|^2 + |x_1-x_2+x_3|^2,

   with eigenvalues `1/2,1/2,7/2`. This is a joint three-variable square,
   not a sum of positive difference edges. Replacing every off-diagonal
   entry by minus its absolute value gives eigenvalues `-1/2,5/2,5/2`.
   The all-ones vector has Rayleigh quotient `-1/2` for this comparison
   matrix. Independent edge replacement thus destroys positivity here.

The last matrix is a deliberately independent control, not a discretization
of the Weil kernel. Its lesson is exact but modest: failure of one pairwise
representation does not prevent a joint positive representation.

## Reproduction and epistemic status

Run `kernel_test.py` using python-flint 0.6.0. It records source and
prediction hashes, exact endpoint enclosures, controls and all eight gauges
in `kernel_results.json`; every reported endpoint sign is reparsed before
acceptance. The analytic identity and sign-cycle argument are elementary
derivations, with interval arithmetic checking the specified neighborhoods.
This is not a formally machine-checked proof, a new RH theorem, or evidence
for a physical hologram or observer mechanism. It shares the lab's machine
and Arb implementation.
