# Codex Round 5b predictions — frozen before computation

Base: `lab/millennium-v1` at `83b3a56`.  The only questions in this round are the frozen Q1 discriminator and the frozen Q2 commutator.  No zeta-zero ordinate may enter a construction, parameter, root label, homotopy, precision choice, or plotting window.  A separate scorer is the only program allowed to evaluate reference ordinates.

## Q1 — the discriminator

For each $x=\lambda^2\in\{9,13,14\}$ and $N=120$, construct the same zero-integral $h_\lambda\in\operatorname{span}(h_{0,\lambda},h_{4,\lambda})$ and exact piecewise projection of $k_\lambda=E(h_\lambda)$ used in Round 5.  Use 200 decimal working digits and Legendre cutoff 200.  The raw candidate is the normalized complex coefficient vector.  Its inversion-even mutation is obtained by orthogonal projection before normalization.  The true comparison is the converged 400-digit finite-Weil ground vector already constructed without target data; its 100-digit version is not used for the reported error because the near-null eigensolve is too ill-conditioned at that precision.

The even transform's first 61 positive roots are enumerated by sign brackets on a grid fixed at 32 subdivisions of the Fourier-lattice spacing; the first 60 are retained.  Raw roots have no canonical positive ordering, so their labels are **UNVERIFIED** and frozen as coefficient-homotopy continuations from those even roots, without resorting, using 8 equal homotopy steps.  Four- and sixteen-step continuations, a 64-subdivision even enumeration, direct-transform residuals, and the unused guard root are numerical audits, not alternate labels.  The scoring errors are

\[
 e^{W}_{x,k}=|w_{x,k}-\gamma_k|,\qquad
 e^{R}_{x,k}=|z^{R}_{x,k}-\gamma_k|,\qquad
 e^{E}_{x,k}=|z^{E}_{x,k}-\gamma_k|,
\]

where the raw error is the complex modulus.  Report $e^W,e^R,e^R/e^W,e^E,e^E/e^W$ for $k=1,\ldots,20$, and plot all three unsmoothed profiles for $k=1,\ldots,60$ in three fixed panels, one per $x$, with a logarithmic error axis and automatic extrema-only padding.

**PREDICTED Q1-A (the $10^{-30}$ crossing).**

| $x$ | raw $e_{x,1}<10^{-30}$? | even $e_{x,1}<10^{-30}$? |
|---:|:---:|:---:|
| 9 | no | no |
| 13 | no | no |
| 14 | yes | yes |

The prediction uses only Round-5 construction diagnostics and the already disclosed $x=13$ control; it is frozen before the Round-5b scorer exists.

For each variant define $d_R=\log_{10}(e^R_{x,1}/e^W_{x,1})$ and $d_E=\log_{10}(e^E_{x,1}/e^W_{x,1})$.  Equality at a boundary belongs to the lower band.  If either $d\leq10$, the finite-Euler-product accuracy is **VOID** as arithmetic evidence.  Only if both $d_R>20$ and $d_E>20$ is the statement “the finite Weil matrix carries arithmetic accuracy beyond the dilation identity” **MEASURED**.  Every other combination is **UNVERIFIED**, with the raw-label qualification retained.  I predict $x=9$ lands in the intermediate band and $x=13,14$ land above 20 orders for both variants.

## Q2 — the commutator

CCM's $PW_\lambda$ acts on $L^2([-\lambda,\lambda],dy)$, whereas $QW_\lambda^N$ acts on $E_N\subset L^2([\lambda^{-1},\lambda],d^*u)$.  The dilation map $E$ is neither unitary nor canonically invertible, so this round does not manufacture an operator $E PW_\lambda E^{-1}$.

Instead freeze the literal endpoint-preserving unitary identification $t=\log u\in[-a,a]$, $a=\log\lambda$, and $y=(\lambda/a)t$.  Compress the transported classical operator to the published shifted Fourier basis $V_n$, $-N\leq n\leq N$, through its weak quadratic form.  With $x=\lambda^2$, its exact matrix is

\[
 P_{nn}=\frac{2\pi^2}{3}n^2+\frac{4\pi^2}{3}x^2,
 \qquad
 P_{mn}=\frac{8x^2-2mn}{(m-n)^2}\quad(m\ne n).
\]

No scalar shift or rescaling is applied.  Use the unshifted, real-symmetric finite Weil matrix $M=QW_\lambda^N$ at $x\in\{9,13,14,16\}$, $N=120$, and 100 decimal working digits.  Report

\[
 c_F=\frac{\|[M,P]\|_F}{\|M\|_F\|P\|_F},\qquad
 r_\xi=\frac{\|[M,P]\xi\|_2}{\|\xi\|_2},\qquad
 \rho=\frac{r_\xi}{\Delta},
\]

where $\xi$ is that matrix's normalized global ground state and $\Delta$ is its positive global ground-state gap, obtained after comparing both parity sectors.  The commutator order is $[M,P]=MP-PM$.  Full-basis Frobenius norms are primary; parity blocks provide an independent assembly check.

Controls use the same $P$.  The archimedean-only matrix deletes every arithmetic atom.  The pseudo-prime matrix uses PCG64DXSM seed `52025001`, draws bases uniformly on $[2,x]$ with acceptance probability $\log 2/\log b$, includes their powers through $x$, and rejects whole draws until both the authentic base count and authentic atom count match: $(4,7)$ at $x=9$, $(6,9)$ at $x=13,14$, and $(6,10)$ at $x=16$.  Every control uses its own ground state and gap.

**PREDICTED Q2-A (ground action).**  For the authentic matrix, $\rho>1$ at each of $x=9,13,14,16$—indeed by many orders—so this literal commuting-operator route is dead as-is.  I also predict $\rho>1$ for every pseudo-prime and archimedean-only control.  I make no prediction for their rank ordering in $c_F$.

An authentic $\rho<1$ with both matched controls above one is not described as a mechanism unless all three preregistered checks pass: (1) the closed entries of $P$ agree with independent 100-digit quadrature of the weak form; (2) the full-basis commutator action agrees with a separately assembled parity-block action and with the eigenvector identity for $[M,P]\xi$; (3) a fresh 180-digit matrix/eigensolve preserves the classification with eigensolve residual below $10^{-20}\Delta$.  Otherwise it is **UNVERIFIED**.  A result with authentic $\rho>1$ is **MEASURED** only for this affine-Galerkin realization; it does not exclude other prolate bridges.
