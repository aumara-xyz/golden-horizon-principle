# R5.5a rogue Jensen audit

## Outcome

**UNVERIFIED:** no primary cubic horizon was located. The registered prediction of a finite horizon with approximately quadratic scaling therefore has no measured exponent. It is not replaced by an extrapolation.

The fast screen checked every integer shift through `51112 = floor(256 * 14.13^2)` for the lowest gamma. For gamma 100 and 1000 it checked every shift through 100000 and 768 fixed geometric checkpoints extending respectively to 2560000 and 256000000. No resolved negative discriminant occurred for degree 2, 3, or 4. The entire registered cubic range for gamma 14.13 remained above the screen's cancellation floor. Binary64 cancellation still makes the late cubic ranges for the two larger gammas and most late quartics indeterminate; `screen-results.json` records that limitation rather than interpreting rounded signs.

The 70-decimal-digit interval replay certified all degree-2, degree-3, and degree-4 Jensen polynomials at four diagnostic stress shifts for each gamma. These shifts were selected after the broad screen failed to bracket a horizon; they were not preregistered mutations:

| gamma | certified shifts |
|---:|---|
| 14.13 | 0, 37, 199, 51112 |
| 100 | 0, 460, 10000, 2560000 |
| 1000 | 0, 6907, 1000000, 256000000 |

Every one of these 36 polynomials passed all three requested checks: disjoint Arb root balls compatible with real roots, an exact rational Sturm count equal to the degree, and positive-definite Arb plus exact-rational Hermite matrices. This is a set of finite point certificates, not a proof for the intervening shifts. Because there is no certified horizon, there is no predecessor/horizon pair to certify. The requested horizon row must therefore read **UNVERIFIED** for all three gammas.

The small degrees appear insensitive to this near-negative-axis quadratic multiplier. Detecting the inserted nonreal zero pair may require degree growing with gamma; that is an interpretation of the computation, not a theorem established here.

## Coefficient construction

The computation uses the standard positive theta kernel

\[
 \Phi(u)=\sum_{k\ge1}\left(2\pi^2k^4e^{9u/2}-3\pi k^2e^{5u/2}\right)e^{-\pi k^2e^{2u}},
\]

with

\[
 8\xi(1/2+z)=32\int_0^\infty \Phi(u)\cosh(zu)\,du,
 \qquad
 \gamma(n)=\frac{32n!}{(2n)!}\int_0^\infty\Phi(u)u^{2n}\,du.
\]

This is the theta-integral normalization used in the Jensen-polynomial literature; see Griffin, Ono, Rolen, and Zagier, [*Jensen polynomials for the Riemann zeta function and other sequences*](https://arxiv.org/abs/1902.07321), and Griffin, Ono, Rolen, Thorner, Tripp, and Wagner, [*Jensen Polynomials for the Riemann Xi Function*](https://arxiv.org/abs/1910.01227).

For `delta = 1/4`, multiplication by the registered rogue factor gives the exact coefficient recurrence

\[
 \gamma_\Gamma(n)=\gamma(n)+b_\Gamma n\gamma(n-1)
 +c_\Gamma n(n-1)\gamma(n-2),
\]

where

\[
 b_\Gamma=\frac{2(\Gamma^2-\delta^2)}{(\Gamma^2+\delta^2)^2},
 \qquad c_\Gamma=\frac{1}{(\Gamma^2+\delta^2)^2}.
\]

No zero ordinate, zeta evaluator, zero file, fitted window, or root target enters either script.

## Interval method

`certify_jensen.py` encloses each positive theta summand with `acb.integral` after a saddle-centred change of variables. Its logarithmic derivative

\[
 \frac{2n}{u}+\frac52+\frac{2a}{a-3}-a,
 \qquad a=2\pi k^2e^{2u},
\]

is strictly decreasing. Endpoint values therefore give one-sided exponential bounds on both omitted integration tails. Successive theta summands have a pointwise ratio bounded by its value at `u=0`; a geometric majorant encloses the omitted tail of the theta sum. The resulting coefficient balls feed Arb polynomial root isolation and an Arb Hermite matrix.

For the independent rational checks, each Arb coefficient interval is written to `certificates.json`, its exact binary midpoint is converted to a rational, and SymPy performs an exact Sturm count and exact Hermite-matrix inertia calculation. A positive Arb discriminant and positive Arb Hermite leading minors show that the coefficient uncertainty does not straddle the hyperbolicity boundary at any certified point.

## Reproduction

The certificate runtime used Homebrew Python 3.11 because the system Python 3.9 cannot install `python-flint==0.8.0`.

```sh
/opt/homebrew/bin/python3.11 -m pip install --target /tmp/codex-r5-python311 -r requirements-certify.txt
python3 screen_jensen.py --exhaustive-limit 100000 --log-points 768 --output screen-results.json
PYTHONPATH=/tmp/codex-r5-python311 /opt/homebrew/bin/python3.11 certify_jensen.py --digits 70 --output certificates.json
```

`screen-results.json` is the broad nonrigorous search. `certificates.json` is the interval/rational replay, including every integral enclosure, omitted-tail bound, polynomial coefficient interval, root ball, Sturm count, and Hermite result.
