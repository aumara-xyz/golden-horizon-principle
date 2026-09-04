# Interpretation and prediction ledger

This implements a finite restriction of the geometric Weil form, rather than a
chosen positive wave operator. Source conventions are equations (1)–(3) of
Connes–Consani (2021), https://alainconnes.org/wp-content/uploads/Selecta.pdf.
The multiplicative variable is changed to x=exp(u); pole terms are retained.
The source's restricted positivity theorems are NOT claimed to certify these runs.

## Measured numerical results

At L=0.4, N=16 the authentic minimum is 0.00021923362545. Removing prime terms
gives -0.0592112; shifting prime-log positions by +10% or -10%, with weights kept,
gives -0.0496330 and -0.0284887. These are explicitly altered-comb controls,
not bona fide alternative L-functions. Every control ran before the authentic arm.

At L=0.7 the visible four-mode minimum is 4.54625e-6. Including twelve additional
modes yields a Schur minimum about 1.83e-12, below the conservative 1e-11
reporting floor. At L=1 numerical minima around -7e-14 are unresolved: these are
not evidence of negative Weil values or an RH counterexample.

Normalized coupling approaches one, but its final digits are unreliable when the
blocks become ill-conditioned. In particular, a displayed value slightly above one
must NOT be interpreted as a rigorous crossing of the positivity threshold.

## Validation

Three quadrature orders (96,192,384) change matrix norms by approximately 1e-13.
Two archimedean integral representations agree to about 6e-15. These checks do not
bound a shared systematic error. An independent scalar check uses the analytic
autocorrelation of the first cosine mode and adaptive scipy.integrate.quad:
at L=0.4 it gives Q=0.007846963097555223, versus the 96-order matrix entry
0.007846963097521645 (difference 3.36e-14).

No eigenvalues were clipped and no positive diagonal regularizer was added.
No rigorous interval bounds, infinite-tail certificate, or positivity theorem was obtained.
The real symmetric basis matrix extends to complex coefficient vectors as a
Hermitian form; both spatial parities are retained. This spatial parity is not
the zero-amplitude mirror involution of the earlier toy.

## Frozen predictions retained

- Authentic finite matrices positive or unresolved: MATCH on tested grid.
- Hidden modes reduce visible minimum: MATCH on computed, resolved-block cases.
- Controls can also be positive: no such example in this grid; this anticipated
  possibility was not observed. All tested control minima were negative.
- No uniform margin emerges: no uniform margin established; three windows and
  sixteen modes cannot prove its absence in any general sense.

## What the observer elimination actually says

For W=[[A,C],[C*,D]] and D positive definite, completing the square gives
Q(x,y) = x*(A-CD^-1 C*)x + ||D^(1/2)(y+D^-1 C*x)||^2.
Thus revealing hidden modes cannot improve the minimum energy available to a
fixed visible vector. Their optimized correction CD^-1 C* is positive semidefinite.
This is standard Schur-complement algebra. The unresolved task is to control
this correction and the omitted modes for the actual Weil form, without numerical
regularization or an assumption of RH. A uniform strictly positive gap is not
required for RH; nonnegativity on all admissible functions is the target.

## Next bounded task

Recompute L=0.7 at 80 and 160 digits, with independently bounded quadrature error,
then enclose the Schur minimum. A finite numerical square root alone would add
no structural explanation. The experiment identifies cancellation to resolve,
not a new proof mechanism. This work is committed locally only.
