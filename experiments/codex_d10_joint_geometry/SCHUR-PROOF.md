# D10: pole-directed finite completion of squares

This is standard linear algebra applied to interval-enclosed finite matrices,
not a new positivity theorem. Input matrices are principal blocks of the
replayed D7 lower-envelope operator at L=7/10 and T=120. They are NOT the full
Weil operator. The existing builder supplies H=R_120 minus its signed pole.
The authentic pole coefficient is kappa=+2 in the even sector and -2 in the
odd sector. Controls leave support, basis, pole vector, beta and cutoff fixed.

## The prescribed axis and exact identity

Let p be the cosh/sinh moment vector, n_p=p^T p>0, and q=p/sqrt(n_p).
The direction is fixed before inspecting an eigenvector. Set v=q+e_0 and
U=-I+2vv^T/(v^Tv). Since q has unit norm and q_0 is positive here,
v^Tv=2(1+q_0)>0, U is an exact real orthogonal matrix and Ue_0=q.
The code evaluates these identities with balls and checks that all residual
entries enclose zero. Orthogonality follows algebraically for the exact p;
it is not inferred merely from a numerically small residual. No congruence
norm correction is omitted: this first transformation is exactly orthogonal.

Write

    U^T H U = [[a,b^T],[b,C]].

For f=U(t,g), and if C is positive definite,

    f^T(H+kappa pp^T)f
      = (g+C^-1 b t)^T C (g+C^-1 b t)
        + [a+kappa n_p-b^T C^-1 b] t^2.

Thus sigma=a+kappa n_p-b^T C^-1 b is the remaining scalar inequality.
The critical coefficient is (b^T C^-1 b-a)/n_p. It is a positivity threshold
ONLY when C>0. The algebraic scalar is still reported for certified invertible
indefinite C, but it is then not a positivity criterion. If C invertibility
is unresolved, the script reports UNVERIFIED and does not divide by a guessed
gap. Positive C and sigma are equivalent to positivity of this finite matrix;
they do not independently explain positivity of the complete Weil form.

## Certified eigenvalue enclosures and inertia

For each symmetric ball matrix A, mpmath at 70 decimal digits supplies an
approximate orthogonal eigenbasis. Its decimal entries are frozen and parsed
as exact real decimals V. Arb computes D=V^T A V and G=V^T V. Gershgorin gives
g_lo I <= G <= g_hi I, with g_lo>0 certified; this proves V is invertible.
If d_lo is the minimum lower endpoint of the Gershgorin intervals of D, then

    lambda_min(A) >= d_lo/g_hi  when d_lo>0,
    lambda_min(A) >= d_lo/g_lo  otherwise.

An independently evaluated Rayleigh quotient of the frozen first column of V
gives an upper endpoint. This supplies the reported interval for lambda_min.
A negative Rayleigh upper endpoint is a negative finite-matrix witness; the
exact decimal vector and its enclosed score are exported. It is never called
a negative witness for the full W.

If every Gershgorin interval of D lies strictly on one side of zero, deforming
D to its diagonal while scaling off-diagonals by a factor from 1 to 0 cannot
cross zero. This certifies the positive and negative eigenvalue counts.
Let d be the minimum distance of these intervals from zero. Then

    ||A^-1|| <= g_hi/d,

because A^-1=V D^-1 V^T and ||V||^2<=g_hi. This certified inverse bound is
also valid in the indefinite case. Midpoint eigenvalue lists and counts below
1e-3 are explicitly labeled numerical diagnostics, not certified thresholds.

## Stable residual enclosure instead of interval elimination

An approximate x=C_mid^-1 b_mid is frozen as exact decimals. Arb evaluates
r=b-Cx and a certified lower bound d_C on the distance of C's spectrum from
zero. The identities

    b^T C^-1 b = 2b^T x-x^T Cx+r^T C^-1 r,
    ||C^-1 b-x|| <= ||r||/d_C

give enclosures without unstable interval Gaussian elimination. The residual
quadratic correction lies in [0,||r||^2/d_C] for positive C, in its negative
reflection for negative C, and in the symmetric interval otherwise. This is
second order in the residual and preserves cancellation in sigma.

The completion is checked on an exact-decimal test vector in two ways: direct
evaluation in the original coordinates against the transformed block score,
and the exact residual-corrected identity

    block score = (g+xt)^T C(g+xt)
                  +(a+kappa n_p-x^TCx)t^2+2t g^T(b-Cx).

No approximate solve is silently treated as exact. The response norm and
cancellation factor are enclosures; the latter is reported only if sigma's
interval excludes zero.

## Controls, serialization and repair ledger

Seven planted controls run before each input is analyzed: positive,
indefinite and negative matrices with certified inertia and independent
Rayleigh scores; singular and interval-ambiguous matrices that must refuse
invertibility; and positive/negative Schur completions. Hostile arithmetic
models run before authentic table acceptance. The pole-sign mutation is
reported even when its matrix stays positive.

The first planted positive Schur control detected NaN in a residual norm:
generic interval multiplication r_i*r_i can extend below zero when r_i
straddles zero. The implementation was repaired to bound each absolute
magnitude first and take square roots only of sums of nonnegative endpoint
bounds. A finite-export assertion now rejects all NaN/infinite values. This
was a control-detected implementation repair, not a changed prediction.

Every scalar is exported as a ball and as separate lower/upper endpoint
enclosures. The complete endpoint strings are reparsed, and any asserted sign
must survive that round trip. Saved negative witness coefficients preserve
the full frozen decimals. `schur.py verify` reparses those decimal vectors,
checks each input hash, and independently evaluates H plus the pole rather
than using the already assembled R matrix. All 13 reported negative finite
witnesses passed this check (seven even, six odd). Input file SHA256 hashes are included. All analysis
uses the same machine and Arb stack as D7 and D9; this is not independent-
library validation. No all-window statement follows.
