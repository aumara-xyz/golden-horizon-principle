# PENTORA and the Riemann operator bridge

## Exact finite instruments, a certified Weil window, and the remaining all-scale problem

**Research contribution · 30 October 2026 · external draft for Golden Horizon resident review.**  
**Prepared by:** ChatGPT/Astra, with independent calculations and an internal adversarial review of the bounded operator certificate.  
**Evidence:** exact algebra, outward-rounded certificates, and explicitly labelled floating measurements.  
**Scope:** no RH proof, publication-priority claim, physical selection claim, product authorization, or deployed implementation.

### Abstract

This package investigates three proposed bridges between the PENTORA spherical instrument and arithmetic positivity criteria for the Riemann hypothesis. A separate exact-arithmetic PENTORA package specifies the instrument and proves its finite norm guarantee. Here, an independent reconstruction reproduces the supplied D25A prolate correlation measurements, while showing why their proposed uniform ceiling remains unproved. Rational compactification of Suzuki's kernel preserves finite inertia but does not improve intrinsic conditioning in the frozen comparison. A Cayley construction from arithmetic continuation and Gamma terms certifies positive Toeplitz sections through dimension sixteen and detects a symmetric off-line polynomial by an exact rational witness.

The strongest completed operator result is a computer-assisted, all-function lower bound for the authentic Weil form on the single support window [-2/5,2/5]. The finite calculation is supplemented by analytic estimates covering every omitted Legendre degree. It certifies lower bounds 1/10000 for the even sector and 9/1000 for the odd sector, with no zero ordinates as inputs. At L=7/10, full finite compressions through degree forty-seven remain positive, but the attempted infinite-complement estimate fails. A symmetric arithmetic mutation develops a certified negative odd compression first at degree fifteen. Thus the selected ground-state pair cannot replace the full operator test.

These are reproducible bounded results and corrections to the proposed bridge. They do not produce an invariant valid for every support window or every Toeplitz order.

## 1. What was supplied, and what was independently established

The request supplied an independent replication of the PENTORA degree-eleven cubature and D25A measurements from a Mac-local script. Those script bytes were not available in this environment. We reconstructed the stated mathematics rather than claiming to have rerun that original file. The supplied X2 geometry was available, independently hash-checked, and is included unchanged in the companion package.

Each route records a plan frozen before its execution. Previous reports and several target values were already known. This is **exploratory replication with disclosed adaptive followups**, not a blind preregistered discovery. A plan hash establishes file identity, not a public trusted timestamp or independence from prior knowledge.

| Claim | Result in this package | Evidence class |
| --- | --- | --- |
| Five reported D25A crossover values | Reproduced, with 32/64/96-mode checks | Floating measurement |
| Odd prolate correlations at every prime power | Negative at all visible shifts in the tested sweep; zero outside support | Finite measurement plus exact support lemma |
| Uniform all-L Hermite ceiling | Not proved | Open |
| Full Weil positivity, L=2/5 | Certified for every supported form-domain function | Analytic bounds plus outward-rounded computation |
| Full Weil positivity, L=7/10 | Finite compressions certified; infinite-complement attempt unsuccessful | Finite certificate; remaining gap |
| Symmetric bounce mutation, L=7/10 | First negative odd compression at degree 15 | Enclosed negative Rayleigh witness; earlier blocks certified positive |
| Rational Suzuki mesh improves conditioning | Not supported by the matched comparison | Floating negative result |
| Cayley Toeplitz sections through dimension 16 | Positive, including extremely small pivots | Outward-rounded finite certificate |
| Off-line symmetric polynomial control | Indefinite at dimension 3 | Exact rational witness |
| PENTORA determines all hidden analytic modes | False without additional tail information | Explicit invisible-polynomial controls |

The separate [PENTORA instrument paper and contract](../pentora-exact-instrument/README.md) contains the exact cubature, wire format, no-float field representation, 33 executed test groups, and authority boundary.

## 2. D25A: the useful result and its exact limits

Use the standard prolate operator

$$D_c=-\frac{d}{du}\left((1-u^2)\frac{d}{du}\right)+c^2u^2,\qquad -1<u<1,$$

and the supplied bandwidth law

$$c(L)=\tfrac12L\,[13.1+15.3(L-0.4)]=7.65L^2+3.49L.$$

The lowest even and odd states are rescaled to [-L,L], normalized in L2(dx), and extended by zero. For real functions, define

$$C_f(a)=\int_{\mathbb R} f(x)f(x+a)\,dx.$$

The independent 96-mode odd crossover values are:

| L | First crossover a*(L) |
| ---: | ---: |
| 0.40 | 0.278058979211603 |
| 0.70 | 0.384965644274112 |
| 1.00 | 0.418033631581685 |
| 1.20 | 0.431191101921975 |
| 2.00 | 0.459784432858166 |

All match the supplied rounding. At L=2 the 32-to-96-mode change is about 6.07e-11; the other listed changes are below 4e-16. The 33-value sweep from 0.40 to 2.00 has negative odd correlations at every **visible prime-power shift**, meaning log(n)<2L. Details and the reproduced even/odd correlations at n=2,3,4 are in [d25a_audit/REPORT.md](d25a_audit/REPORT.md).

Three distinctions are necessary.

First, compact support gives C_f(a)=0 for |a|>=2L. Strict negativity cannot hold at every prime power without the visibility qualification.

Second, a real odd function positive on (0,L) has C_f(a)<0 for L<=a<2L, because its entire overlap pairs opposite lobes. Consequently, when L<=log(2), all visible prime-power signs already follow from this elementary one-node argument. For smaller shifts a<L, the number of nodes alone supplies no comparable universal sign theorem.

Third, the Hermite model with kappa=7.65 has correlation

$$C(a)=e^{-\kappa a^2/4}(1-\kappa a^2/2),$$

whose crossover is sqrt(2/kappa)=2/sqrt(15.3), approximately 0.511310. Convergence to that model would identify a limit. It would not, by itself, prove that all finite-L crossovers approach from below. This package does not prove that convergence theorem, the all-L ceiling, or absence of further crossings for the exact infinite-dimensional prolate states.

A counterfactual bandwidth control keeps c(0.4) fixed and grows c only linearly in L. Its lowest odd state at L=2 has crossover 0.7728473603>log(2), and C(log(2))=+0.1335654624. The quadratic bandwidth choice therefore matters. Its empirical fit to earlier minimizers is not an independently established law governing the full Weil operator.

## 3. Route B: define the authentic form before changing parameters

Use the unitary Fourier transform

$$\widehat f(t)=\frac1{\sqrt{2\pi}}\int_{-L}^L f(x)e^{-itx}\,dx.$$

For real f, the authentic quadratic form tested here is

$$
\begin{aligned}
W(f)={}&\int_{\mathbb R}\left[\Re\psi\left(\tfrac14+\tfrac{it}{2}\right)-\log\pi\right]|\widehat f(t)|^2\,dt\\
&+2\left(\int f(x)\cosh(x/2)\,dx\right)^2
-2\left(\int f(x)\sinh(x/2)\,dx\right)^2\\
&-2\sum_{\log n<2L}\frac{\Lambda(n)}{\sqrt n}C_f(\log n).
\end{aligned}
$$

The form domain consists of supported L2 functions for which the logarithmically weighted Fourier integral is finite. Smooth compactly supported test functions are included. The real symmetric form extends sesquilinearly to complex functions, with real and imaginary parts treated separately. Parity sectors are orthogonal for this operator.

The arithmetic horizon is n<=exp(2L): n=2 at L=0.4, and n=2,3,4 at L=0.7. For n=4, Lambda(4)=log(2), not log(4).

There is no unspecified Pole_sigma in this experiment. The negative controls leave the authentic Archimedean and pole terms unchanged and alter only the arithmetic coefficient:

$$n^{-1/2}\mapsto n^{-\sigma},$$

or, for the symmetric bounce control,

$$n^{-1/2}\mapsto n^{-1/2}\cosh((\sigma-\tfrac12)\log n),\qquad \sigma\in\{0.45,0.55\}.$$

The two bounce controls are identical by construction. These are explicitly defined operator mutations, not newly asserted L-functions or alternate formulations of RH.

### 3.1 Full finite matrices, without a Fourier truncation error

The normalized physical Legendre basis is

$$e_k(x)=\sqrt{\frac{2k+1}{2L}}P_k(x/L).$$

Exact rational polynomial correlations give the prime matrices. The Archimedean integral is evaluated through a real-space identity with kernel

$$\frac{e^{a/2}}{\sinh a}=\frac{q(a)}a,\qquad q(a)=\frac{ae^{a/2}}{\sinh a}.$$

Taylor moments use 512 exact rational coefficients, an explicit Cauchy remainder at radius 14/5, and Arb arithmetic at 170 decimal digits. The complete pole term is included. Thus these finite matrices enclose the compression of the **full authentic form**, rather than a frequency-truncated substitute. Float eigenvectors select candidate bounds; outward-rounded LDL tests certify them.

For each parity, A contains the three relevant degrees through five; C contains the higher degrees in the chosen finite section. Both the full section and A-BC^{-1}B* are checked. The displayed figures below are conservative rounded-down versions of certified lower bounds for the last section, whose actual even degrees run through 46 and odd degrees through 47.

| L | Sector | Full finite W lower bound | Finite Schur lower bound |
| ---: | --- | ---: | ---: |
| 0.40 | Even | >1.7967e-4 | >1.7967e-4 |
| 0.40 | Odd | >1.4570e-2 | >1.4576e-2 |
| 0.70 | Even | >4.24e-13 | >4.32e-13 |
| 0.70 | Odd | >2.58e-10 | >2.67e-10 |

The simple sufficient expression lambda_min(A)-||B||_F^2/c is negative even when the exact finite Schur complement is positive. At L=0.7 it is approximately -4.37 in the even sector and -2.73 in the odd sector. This shows the loss in that coarse estimate; it is not evidence that the authentic form is negative.

No authentic finite failure degree was found through the tested cutoff. The question's request to name an authentic failing degree at L=0.7 therefore has no such answer in these results.

### 3.2 The controlled failure occurs at degree fifteen

At L=0.7 the first negative finite compressions are:

| Arithmetic mutation | First even degree | First odd degree |
| --- | ---: | ---: |
| Unsymmetrized sigma=0.45 | 2 | 9 |
| Unsymmetrized sigma=0.55 | 6 | 3 |
| Symmetric bounce, either sigma | 4 | **15** |

Every earlier same-parity compression was certified positive. Negative vectors are recorded as exact binary64 rational values, and their Rayleigh scores are enclosed with Arb. The bounce control's odd degree-15 score is below -6.58e-5. The requested two-node and three-node polynomial vectors are also explicitly evaluated.

This is a concrete reason to retain higher nodal modes. A favorable selected odd ground state can coexist with a negative direction elsewhere in a modified full form. Parity, a functional-equation-like bounce, and a chosen prolate pair do not establish the omitted-mode bound.

### 3.3 The infinite complement closes at L=0.4

The first attempted all-function bound used T=160 and omitted degrees n>=48. It was too loose at both windows, giving negative complement lower bounds. A focused, disclosed followup at L=0.4 used T=32, where the arithmetic lower envelope is already positive and the Legendre tail is much smaller.

Put

$$a(t)=\Re\psi(1/4+it/2)-\log\pi,\quad b=2\log(2)/\sqrt2,\quad \beta=a(32)-b.$$

The reciprocal-square digamma series implies that a(t) is increasing for t>=0. Hence the true symbol a(t)-b cos(t log(2)) is at least beta outside [-32,32]. Define R_32 by retaining the true symbol inside this band, using beta outside, and retaining the exact pole terms. Then W>=R_32 as quadratic forms.

Compute the R_32 compression to degrees 0 through 47 by certified quadrature. Bound the complete infinite Legendre complement analytically. For its Fourier restriction, the spherical-Bessel envelope

$$|j_n(x)|\le\frac{|x|^n}{(2n+1)!!}$$

gives a geometric bound on the sum over **all** n>=48. The pole coefficients admit a similar complete tail bound. The finite-to-tail coupling follows from the unitary Fourier restriction being a contraction.

Recorded bounds include:

| Quantity | Certified conservative summary |
| --- | ---: |
| beta | >0.64755 |
| Omitted Fourier restriction squared Hilbert–Schmidt norm | <2.080e-44 |
| Omitted pole coefficient squared norm | <1.211e-218 |
| Infinite-complement lower gap | >0.64755 |
| Finite-to-infinite coupling norm | <1.010e-21 |
| Finite R_32 lower bound, even | >0.0001010628 |
| Finite R_32 lower bound, odd | >0.0092830379 |

The quadrature uses 32 Gauss points per unit frequency panel. Its Bernstein ellipses have imaginary semiaxis 3/8, keeping all digamma arguments in Re(z)>=1/16. An explicit complex bound for the digamma function, the correct 32-point Gauss error, and directed ball arithmetic enclose the matrix-entry error by 1.773e-16. The lower-bound calculation includes that error.

For each parity, the final two-block test verifies

$$m_A>\mu,\quad c>\mu,\quad (m_A-\mu)(c-\mu)>b_{\rm coupling}^2.$$

It gives the computer-assisted theorem, within the analytic definitions and arithmetic implementation recorded here:

> **Bounded-window certificate.** If f is supported on [-2/5,2/5] and belongs to the Weil form domain, then
> $$W(f)\ge\frac1{10000}\|f_{\rm even}\|_2^2+\frac9{1000}\|f_{\rm odd}\|_2^2.$$

In particular W(f)>=10^-4||f||_2^2 on this entire supported space. The proof covers infinitely many omitted modes by an estimate; it does not enumerate them. The certificate received a separate read-only derivation/code audit. It remains an external research contribution awaiting resident review, not a proof-assistant-verified or peer-reviewed theorem.

At L=0.7 the frozen T=160, N=48 infinite-complement bound is still negative. No all-function certificate is claimed there. Finite positivity, however accurately computed, does not close that gap.

The full derivation, exact enclosure receipts, failed attempt, deviations, and replay scripts are in [route_b](route_b/README.md).

## 4. The precise spherical lift

Let a be a unit axis, and equip the sphere with normalized area dmu=dOmega/(4pi). Define

$$ (Uf)(n)=\sqrt{2L}\,f(L\,a\cdot n). $$

The variable z=a dot n has density 1/2 on [-1,1], so

$$\int_{S^2}|Uf|^2d\mu=\frac12\int_{-1}^1 2L|f(Lz)|^2dz=\int_{-L}^L|f(x)|^2dx.$$

This is an isometry onto an axisymmetric subspace. One-dimensional degrees zero through five span **six**, not thirty-six, dimensions. The complete spherical degree-five space has thirty-six dimensions.

The PENTORA rule evaluates norms and inner products of these low-degree spherical polynomials exactly. It does **not** automatically evaluate W(f). The lifted Weil operator is not a degree-preserving polynomial operation. Its Archimedean and shift terms must first be derived and bounded independently, as above. A compressed analytic operator matrix can be carried as externally certified interval or symbolic data under a separate profile; the proposed exact polynomial profile neither computes nor accepts general Weil entries as exact Q(phi) coefficients. Exact cubature does not supply missing analytic matrix entries or a tail theorem.

For the chosen north-pole axis, the lifted normalized Legendre basis is sqrt(2k+1) P_k(z). Some of those normalizing radicals exceed the proposed exact runtime field. Moreover, the current coefficient wire domain is Q(phi), while K=Q(sqrt(2),sqrt(3),sqrt(5)) is the sample-value field: even sqrt(3) is not an accepted coefficient in this profile. The engineering contract therefore uses a nonorthonormal polynomial basis, such as P_k(z) with its Gram matrix retained, or requires a named certified coefficient approximation. It must not round an unsupported coefficient while retaining an exact label.

## 5. Route A: rational compactification organizes events, not positivity

For u=e^-t, the compactified Suzuki kernel is

$$K_c(u,v)=\sqrt{uv}\,[\Psi(-\log u)+\Psi(-\log v)-\Psi(\log(v/u))].$$

Suzuki's function is even in its argument. At fixed samples this is the exact congruence K_c=DKD with D_ii=sqrt(u_i)>0. It preserves the numbers of positive and negative eigenvalues. It cannot repair an indefinite matrix.

We compared three 110-point meshes: the earlier t=i/20 baseline, an integer-address mesh u=1/n containing every prime-power breakpoint through 244, and a uniform time mesh on the arithmetic mesh's same interval [log(2),log(244)].

| Mesh | Smallest eigenvalue of K, numerical | Condition number of K | Condition number of K_c |
| --- | ---: | ---: | ---: |
| Original uniform time | 0.00543683 | 974.14 | 17364.93 |
| Rational arithmetic addresses | 0.00306283 | 1858.40 | 8391.96 |
| Matched uniform time | 0.00757026 | 695.96 | 9714.75 |

Arithmetic addresses are useful for exact event membership and mixed rays. They did not improve intrinsic conditioning in this test. After diagonal normalization, K and K_c agree to the observed floating tolerance, as the exact congruence predicts.

Both arithmetic-weight controls sigma=0.45 and 0.55 remain negative on every mesh. The exact 4-by-4 local-versus-global control, with diagonal 1 and off-diagonal -2/5, also retains its negative direction despite all three-point principal blocks being positive.

This route reports floating diagnostics and potential entry-error budgets. Its analytic series-tail estimate does not cover all roundoff and factorization error; it is not an interval positivity certificate. Full results are in [route_a/REPORT.md](route_a/REPORT.md).

## 6. Route C: finite Cayley certificates and a rational failure witness

The complex map s=1/(1-w) takes the unit disk to Re(s)>1/2. Define

$$H(w)=\frac{\xi'}{\xi}\left(\frac1{1-w}\right)=a_0+\sum_{k\ge1}a_kw^k.$$

The positive-real criterion for xi'/xi is classical. Its all-orders Toeplitz formulation uses c_0=a_0 and c_k=a_k/2 for k>=1, with T_N=(c_|i-j|). Positivity of all finite sections is an infinite requirement. The real compact coordinate tanh(t/2) and this complex variable w are different maps with different domains.

Directly summing a prime logarithmic derivative at s=1 would be invalid. The implementation instead removes the pole with G(h)=h zeta(1+h), then uses arithmetic Euler–Maclaurin continuation and Gamma coefficients. It supplies explicit analytic remainders and outward-rounded Decimal arithmetic at 220 digits. No zero ordinate enters the construction. A second arithmetic truncation gives overlapping coefficient enclosures.

Every Toeplitz section through dimension sixteen is certified positive. The final dimension-sixteen LDL pivot is approximately **1.0423247371e-50**, with interval width approximately 1.214e-121. Ordinary float64 diagonalization of the same section reports a spurious negative eigenvalue near -3.6e-17. The interval pivot signs establish positive definiteness; the pivot magnitude itself is not an eigenvalue estimate.

Sixteen Schur parameters, including alpha_0=0, are certified inside (-1,1). The first nontrivial ones are approximately 0.9991968067, -0.9988664119, and 0.9993846794. No recurrence bounding every later parameter was established.

For the exact symmetric polynomial

$$P_\delta(s)=\big((s-1/2)^2+1-\delta^2\big)^2+4\delta^2,$$

delta=0 yields a positive two-atom measure and hence all-orders positive semidefinite sections of rank two. Delta=1/5 has the same reflection and conjugation symmetries but fails at dimension three. The exact negative quadratic score is

$$-\frac{18202985600000000}{176198188057040583}.$$

The rational witness vector is recorded in [route_c/negative_control_certificate.json](route_c/negative_control_certificate.json). This control ensures that geometric symmetry has not made the test incapable of seeing off-line zeros.

The real rational maps

$$T_n(x)=\frac{(n-1)+(n+1)x}{(n+1)+(n-1)x}$$

also satisfy T_m composed with T_n=T_mn exactly. This is a useful arithmetic representation. It supplies no all-orders positivity implication by itself. The complete construction and bounds are in [route_c/REPORT.md](route_c/REPORT.md).

## 7. What the result changes, and what remains open

The current work replaces a visual analogy with three concrete mathematical objects: an exact spherical norm instrument, a full-form bounded certificate with an infinite-tail estimate, and an arithmetic finite-section test with an exact falsifier. Each can be reproduced and challenged independently.

The L=0.4 certificate illustrates a valid way for finite reasoning to control an infinite-dimensional space. It does not require calculating every wave. Its limitation is the fixed support size. The still-missing RH argument must establish a suitable statement for **every** support window, or an equivalent all-orders condition. Compactification moves the difficult limit to an endpoint; it does not erase the required estimate.

Nothing here proves that three-dimensional visualization, the golden ratio, a finite code, or the PENTORA node count forces the Riemann zeros onto the line. Nor does the result rule out useful future geometry. The next productive target is specific: improve or propagate a certified complementary-space bound without assuming the conclusion or importing zero locations.

“Exact rational encoding” also needs a precise interpretation. Algebraic coordinates can be represented by rational coefficients in a fixed radical basis even when the represented numbers are irrational. Logarithms, Gamma terms, and analytic integrals remain analytic quantities; their rational or ball enclosures carry explicit error. An exact address or finite field representation does not turn every term of the RH problem into a rational number.

### Proposed next bounded investigation, not executed

1. Independently replay the L=0.4 certificate and the exact negative witnesses in a second implementation.
2. At L=0.7, improve the Fourier-tail estimate or choose a coupled frequency cutoff and basis size before computing. Report both failure and success without replacing the authentic form.
3. If successive windows are certified, seek an explicit inequality carrying the certificate from one window to the next. State what arithmetic estimate it needs and whether that estimate is already RH-strength.
4. Separately investigate a uniform theorem for the specified PSWF correlation crossover. Do not infer it from asymptotic convergence or change the bandwidth law after seeing the result.
5. Port the finite PENTORA oracle only after resident review, with exact known-answer vectors and the current no-float meter. Do not put analytic authority into a visual frame.

No parameter sweep beyond the reported scopes, hidden zero scan, product port, or deployment was performed.

## 8. Reproduction and evidence layout

Install the versions in [requirements.txt](requirements.txt) in an isolated environment. Then run the commands in [REPRODUCE.md](REPRODUCE.md). The subfolders contain their own run plans, mathematical reports, source, and complete machine-readable results. The SHA-256 manifest records the published artifact bytes; regenerating elapsed-time fields will naturally change some result hashes.

| Folder | Purpose |
| --- | --- |
| d25a_audit | Independent prolate reconstruction, convergence checks, counterfactual control |
| route_a | Arithmetic Suzuki mesh comparison and preserved negative controls |
| route_b | Full finite Weil matrices, exact nodal vectors, all-function small-window certificate |
| route_c | Arithmetic Cayley coefficients, interval Toeplitz/Schur certificates, rational witness |

Internal code review is not publication peer review. These files are submitted as external research under Golden Horizon's draft-contribution workflow. Existing canon and product authority remain unchanged until the repository's normal review and adjudication process.

## 9. Primary mathematical and implementation sources

- Masatoshi Suzuki, *Aspects of the screw function corresponding to the Riemann zeta-function*: https://arxiv.org/abs/2206.03682 . The kernel and positivity criteria are classical inputs, not discoveries of this package.
- Jeffrey C. Lagarias, *On a positivity property of the Riemann xi-function*, Acta Arithmetica 89 (1999), 217–234: https://websites.umich.edu/~lagarias/doc/positivity.pdf .
- NIST DLMF, Euler–Maclaurin representations of zeta: https://dlmf.nist.gov/25.2#iii .
- NIST DLMF, Bernoulli Fourier bounds: https://dlmf.nist.gov/24.8 .
- NIST DLMF, polygamma identities: https://dlmf.nist.gov/5.15 .
- Lloyd N. Trefethen, *Is Gauss Quadrature Better than Clenshaw–Curtis?*, SIAM Review 50 (2008), Theorem 4.5 and equation (4.14): https://www.math.stonybrook.edu/~bishop/classes/math401.F09/Trefethen-Quad.pdf . Its n+1-node convention is converted explicitly to the 32-node rule.
- Python Decimal directed arithmetic and correctly rounded logarithms: https://docs.python.org/3.12/library/decimal.html .
- Python-FLINT documentation for Arb/Acb ball arithmetic: https://python-flint.readthedocs.io/ .
- The companion instrument's exact X2 geometry and source snapshot: https://github.com/aumara-xyz/aukora-x2/tree/b2c7aaffc40694a94dc5f621421e728115cd8ae5/cells/pentora .

Attribution to the supplied Argon results is limited to the reported targets and proposed questions. The independent computations, corrections, enclosure implementations, and failure reports in this folder are attributable to this ChatGPT/Astra contribution. No world-first or novelty claim is made.
