# A pure sine-tail lower bound for the fixed-window Weil form

Scope: real f in H_0^1(-L,L), extended by zero. Set omega_j=j*pi/(2L)
and phi_j(x)=sin(omega_j(x+L))/sqrt(L). Assume <f,phi_j>=0 for j<=N.
The estimate is elementary and carries no novelty claim.

Use the unitary Fourier transform F(t)=(2*pi)^(-1/2) integral f(x)e^(-itx) dx.
Write the fixed-window prime-side expression as

    Q(f) = P(f) + integral a(t)|F(t)|^2 dt
                       - sum_(p,m) w_(p,m) integral cos(u_(p,m)t)|F(t)|^2 dt,
    a(t) = Re psi(1/4+it/2) - log(pi),
    P(f) = 2 (integral f exp(x/2)) (integral f exp(-x/2)).

Here w=2log(p)/p^(m/2); include only shifts u=m log(p)<2L. Shifted controls
change u and included terms, not weights. This Fourier expression follows
from the same explicit formula used in the finite certificate; see
[Connes–Consani](https://alainconnes.org/wp-content/uploads/Selecta.pdf).
The log multiplier has finite integral for H_0^1 functions.

## Fourier leakage estimate

For 0<R<omega_(N+1), direct integration gives, when |t|<=R and j>N,

    |integral phi_j(x)e^(-itx) dx|
        <= 2 omega_j / [sqrt(L)(omega_j^2-R^2)].

Expand f in the sine basis and apply Cauchy–Schwarz. Using
sum_(j>N) 1/j^2 <= 1/N and integrating over [-R,R] with the normalization
1/(2*pi) gives

    integral_(-R)^R |F(t)|^2 dt <= eta ||f||_2^2,
    eta = min(1, 16LR / [pi^3 N (1-(R/omega_(N+1))^2)^2]).

The bound extends from finite sums by L2 continuity of the restricted
Fourier transform. It concerns the entire tail, not just a diagonal entry.

## Archimedean and arithmetic bounds

The digamma series gives, with y=t/2 and b_k=k+1/4,

    a(t)-a(0) = sum_(k>=0) y^2/[b_k(b_k^2+y^2)].

Thus a(t) increases with |t|. Also

    a(0) = -EulerGamma - pi/2 - 3log(2) - log(pi).

Splitting the Fourier integral at R and using Parseval yields

    integral a(t)|F(t)|^2 dt
        >= [a(R)-(a(R)-a(0))*eta] ||f||_2^2.

Since each cosine is at most 1 and every w is positive, the negative
arithmetic part is bounded below by -B||f||_2^2, B=sum w. For L=7/10,
the authentic shifts come from 2,3,4, with B approximately2.9419735252.
This worst-case bound loses arithmetic phase information, explaining why
the same bound works for the shifted controls.

## Pole term and parity

For even f, P(f)=2|<f,cosh(x/2)>|^2>=0. For odd f,

    P(f)=-2|<f,sinh(x/2)>|^2
         >= -2(sinh(L)-L)||f||_2^2.

Combining the inequalities proves

    Q(f_even) >= [a(R)-(a(R)-a(0))*eta-B] ||f_even||_2^2,
    Q(f_odd)  >= [a(R)-(a(R)-a(0))*eta-B
                          -2(sinh(L)-L)] ||f_odd||_2^2.

Parity decoupling extends the minimum of the two constants to arbitrary
real f in this pure tail. H1 convergence of sine partial sums justifies
passing the form inequalities to the stated test class.

## Validated constants and remaining issue

pure_tail_bound.py evaluates these formulas with Arb balls, at
L=7/10, N=4096, R=256. It encloses the even coefficient above0.5600 and
the odd coefficient above0.4428. This is an analytic inequality with
validated constants, not a numerical fit to finitely many high modes.

The bound does NOT include mixtures with modes j<=4096. The mixed form
is not removed by spatial parity unless the two functions have opposite
parity. Controlling that remaining interaction is a separate task.
