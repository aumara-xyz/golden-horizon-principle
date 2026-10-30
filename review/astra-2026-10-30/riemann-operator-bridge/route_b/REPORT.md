# Route B: complete Weil compressions and a bounded all-function certificate

**Date:** 30 October 2026. **Status:** executed; exact polynomial algebra and rigorous Arb ball enclosures, with numerical selectors and independent checks identified separately. No zero ordinates are inputs. No product authority or claim of RH.

## Outcome

The full authentic Weil form was assembled on normalized Legendre polynomials supported on [-L,L], at L=2/5 and 7/10, through degree 47. Both parities and their finite Schur complements remain positive at every inspected degree. There is no authentic failure degree in this range. The cutoff labeled 47 includes even degrees 0,2,...,46 and odd degrees 1,3,...,47.

A separate complete complement argument closes at L=2/5. It proves

$$W(f)\ge 10^{-4}\|f\|_2^2\quad\text{for all even }f,$$

and

$$W(f)\ge 0.009\|f\|_2^2\quad\text{for all odd }f,$$

supported on [-2/5,2/5] in the Weil form domain. In particular, every real function in that domain, decomposed as f=f_even+f_odd, satisfies

$$W(f)\ge\frac{1}{10000}\|f_{\mathrm{even}}\|_2^2+
\frac{9}{1000}\|f_{\mathrm{odd}}\|_2^2.$$

The form is invariant under reflection, so the even/odd cross term vanishes. Its real symmetric kernel also gives the Hermitian extension W(g+ih)=W(g)+W(h) for real g,h; equivalently this follows by cancelling the odd-in-frequency Fourier cross term. The same bound therefore extends to complex functions, with their complex even and odd components. In particular W(f)>=10^-4||f||² on the full form domain. This statement includes the infinite-dimensional complement; it is not inferred just from a finite positive matrix. It remains a fixed small-window certificate, and stronger historical window certificates already existed. It does not establish an all-L theorem or a new result on zeta zeros.

The simple norm-only Schur bound fails even for the finite authentic matrices. The actual finite Schur complement remains positive because that scalar bound discards essential structure.

The symmetric bounce mutation provides a sharper negative control than a ground-pair test: at L=.7 its odd finite compression becomes negative first at degree15, although all earlier odd compressions through degree13 are certified positive. This is an artificial modified form, not the authentic Weil form.

## 1. Definitions and the exact full-form computation

Use the unitary Fourier transform

$$F(t)=(2\pi)^{-1/2}\int_{-L}^{L}f(x)e^{-itx}\,dx,$$

with f extended by zero outside the interval. Define C_f(a)=integral f(x)overline(f(x+a))dx. The real quadratic form is

$$
W(f)=\int_{\mathbb R}a(t)|F(t)|^2dt
+2|\langle f,\cosh(x/2)\rangle|^2
-2|\langle f,\sinh(x/2)\rangle|^2
-2\sum_{\log n<2L}\frac{\Lambda(n)}{\sqrt n}\Re C_f(\log n),
$$

where a(t)=Re psi(1/4+it/2)-log(pi). The sum runs over prime powers. The equality endpoint contributes zero for interval-supported L² functions. Thus only n=2 is visible at L=.4, and n=2,3,4 at L=.7.

The form domain is the set of supported L² functions for which the positive logarithmically weighted Fourier integral is finite; the Archimedean part is bounded below and may be extended to +infinity outside that domain. The finite pole and translation terms are bounded. Our polynomial vectors belong to the form domain, including their endpoint jumps after zero extension.

### A complete time-domain identity

The digamma integral representation gives

$$
\operatorname{Arch}(f)=a(0)\|f\|^2+
2\int_0^\infty\frac{e^{-a/2}}{1-e^{-2a}}
\bigl(\|f\|^2-\Re C_f(a)\bigr)\,da.
$$

The bracket is nonnegative by the translation isometry. Since C_f(a)=0 when a>=2L,

$$
\operatorname{Arch}(f)=(a(0)+J_L)\|f\|^2+
2\int_0^{2L}\frac{e^{-a/2}}{1-e^{-2a}}
\bigl(\|f\|^2-\Re C_f(a)\bigr)\,da,
$$

where

$$J_L=2\bigl[\operatorname{atanh}(e^{-L})+\arctan(e^{-L})\bigr].$$

This is the full Archimedean term, including the infinite-frequency contribution. No numerical Fourier truncation defines our full matrices.

### Exact polynomial correlations and rigorous moments

Use e_n(x)=sqrt((2n+1)/(2L)) P_n(x/L). For matching parities, the required unnormalized correlation is the exact rational polynomial

$$I_{nm}(r)=\int_{-1}^{1-r}P_n(u)P_m(u+r)du,\qquad r=a/L.$$

Its normalization is sqrt((2n+1)(2m+1))/2. Opposite-parity cross terms cancel in the symmetric quadratic form. In particular, I_nm(0)=2 delta_nm/(2n+1), checked exactly.

The remaining scalar moments reduce to

$$M_k(L)=\int_0^2 r^{k-1}q(Lr)dr,\qquad q(z)=\frac{z e^{z/2}}{\sinh z}.$$

The first512 Taylor coefficients of q are computed as exact rationals, starting 1,1/2,-1/24. The product formula for sinh gives, for |z|=rho<pi,

$$|q(z)|\le \frac{\rho e^{\rho/2}}{\sin\rho}=:M_\rho.$$

Indeed |sinh(z)/z|>=product(1-rho²/(pi²k²))=sin(rho)/rho. At rho=14/5 and 2L<=7/5, the Taylor ratio is at most1/2. The uniform remainder after K terms is bounded by

$$M_\rho\frac{(2L/\rho)^K}{1-2L/\rho}.$$

Multiplying by 2^k/k bounds the k-th moment error. All finite rational sums, transcendental constants, square roots, moments, pole coefficients, and prime correlations are enclosed in Arb at170 decimal digits. The largest moment radius at L=.7 is about2.109e-126. Matrix positivity claims use ball LDL pivots, not rounded eigenvalues.

Pole coefficients are evaluated as sqrt(2L(2n+1)) i_n(L/2), where i_n is the modified spherical Bessel function. Even pole signs are +2 and odd signs are -2.

## 2. Finite A/B/C and Schur results

The visible one-dimensional space consists of degrees0 through5, three basis vectors per parity. Increasing finite complements use total cutoff degrees11,19,31,47. The actual highest even degrees are10,18,30,46, respectively.

For Q_N partitioned as [[A,B],[B*,C_N]], the finite Schur complement is S_N=A-B C_N^-1 B*. No C_N is substituted for the infinite complement.

The following are representative numerical values selected from rigorous enclosing matrices. Certified lower floors and enclosed Rayleigh upper bounds are recorded separately in results.json.

| L | Parity | Cutoff | Minimum of full finite W | Minimum of finite Schur complement |
| ---: | --- | ---: | ---: | ---: |
| .4 | Even | 11 | 1.84540e-4 | 1.84548e-4 |
| .4 | Even | 47 | 1.81485e-4 | 1.81493e-4 |
| .4 | Odd | 11 | .0148421 | .0148470 |
| .4 | Odd | 47 | .0147177 | .0147233 |
| .7 | Even | 11 | 4.0895e-8 | 4.1443e-8 |
| .7 | Even | 47 | about4.29e-13 | about4.37e-13 |
| .7 | Odd | 11 | 3.5187e-7 | 3.5999e-7 |
| .7 | Odd | 47 | about2.6061e-10 | about2.7009e-10 |

At the largest L=.7 even compression, the certified eigenvalue bracket supplied by a lower LDL floor and an upper Rayleigh score is approximately [4.2413e-13,4.2887e-13]. Ordinary binary64 eigensolver last digits at this scale are not the certificate.

At cutoff47, the coarse sufficient margin using a certified Frobenius upper bound for B is approximately:

| L | Even scalar margin | Odd scalar margin |
| ---: | ---: | ---: |
| .4 | -.61535 | -.46995 |
| .7 | -4.37019 | -2.73486 |

These negative lower estimates do not show negative directions. The actual finite Schur complements are positive. There is no authentic degree ell* where positivity breaks among the tested compressions. This is a concrete example of why the scalar bound can fail while the matrix inequality holds.

## 3. Artificial exponent controls and first finite failure degrees

Two control families retain the original Archimedean and pole terms and change only prime weights:

- Unsymmetrized: n^(-1/2) -> n^(-sigma).
- Bounce: n^(-1/2) -> n^(-1/2) cosh((sigma-1/2)log n).

Both sigma=.45 and.55 are retained. The bounce controls are identical by symmetry, which the ball calculation checks. This symmetry forces the derivative at sigma=.5 to vanish for every fixed wave; that fact is not evidence of a selected critical-line mechanism. No unspecified Pole_sigma is invented.

At L=.4, all tested compressions for these mild controls remain positive throughdegree47. At L=.7:

| Control | First negative even cutoff degree | First negative odd cutoff degree |
| --- | ---: | ---: |
| Authentic W | None through46 | None through47 |
| Unsym sigma=.45 | 2 | 9 |
| Unsym sigma=.55 | 6 | 3 |
| Bounce sigma=.45 or.55 | 4 | 15 |

Every earlier same-parity compression in each row was tested with unshifted ball LDL. For each first failure, a binary64 eigensolver selected a vector; that vector was then treated as an exact dyadic vector and its normalized full-W-control Rayleigh score was enclosed using Arb. Negative **upper endpoints** establish the control failures.

For the odd bounce control at degree15, the enclosed normalized score is approximately -6.5851633872114287e-5, with radius below4e-37 in the exported32-digit enclosure. The even bounce failure at degree4 is approximately -1.3093302583619288e-5. The actual vectors are in results.json.

Thus a positive score or favorable correlation signs for a selected lowest prolate pair do not establish positivity on the rest of the function space. Legendre degree is not itself an exact nodal count; no identification of those two notions is made.

The four prior polynomial counterexamples are retained as explicit normalized vectors and scored against every control. Their detailed values are in results.json.

## 4. The complete small-window certificate

This is an adaptive follow-up to a failed tail bound, not a blind prediction.

Define P(t)=sum_n 2Lambda(n)n^(-1/2)cos(t log n), B=sum_n 2Lambda(n)n^(-1/2), and beta=a(T)-B. To make the required monotonicity explicit, for x>0 the reciprocal series gives

$$\Re\psi(x+iy)=-\gamma+\sum_{k=0}^{\infty}
\left(\frac{1}{k+1}-\frac{k+x}{(k+x)^2+y^2}\right).$$

Each summand increases with |y|. The differentiated series converges locally uniformly, and its derivative is positive for y>0. Thus a(t) increases with |t|. Since P(t)<=B, a(t)-P(t)>=beta for |t|>=T. The lower form

$$
R_T(f)=\operatorname{Pole}(f)+\beta\|f\|^2
+\int_{|t|\le T}(a(t)-P(t)-\beta)|F(t)|^2dt
$$

satisfies W>=R_T for the entire form domain.

### Finite quadrature enclosure

At L=.4,T=32,N=48, the finite R_T block is enclosed using32-point Gauss rules on each unit interval of [0,32], then doubled within each parity. Arb supplies ball-enclosed Legendre roots and weights.

The ellipse parameter rho=2 on a unit panel has imaginary semiaxis3/8. Consequently both digamma arguments have real part at least1/16, so no digamma pole is crossed. The exact n-point error bound used is

$$\frac{64Mh}{15(1-\rho^{-2})\rho^{2n}},\qquad h=1/2.$$

This retains the factor corrected by D24. The complex cosine bound is cosh(log(n)*3/8). Each entire Fourier basis function obeys |F_n(z)|<=sqrt(L/pi)exp(L|Im z|), by Cauchy–Schwarz.

To bound digamma on the ellipse, evaluate its center and use |psi'(z)|<=eta^-2+eta^-1 for Re z>=eta=1/16, obtained from the reciprocal-square series. The argument radius is at mostsqrt(34)/16. This avoids an indeterminate wide-box special-function evaluation. The final total error per symmetric matrix entry is below1.773e-16, including both frequency halves. Arb arithmetic additionally encloses all roundoff.

### Infinite Legendre complement

For the normalized Fourier basis,

$$|F_n(t)|^2\le\frac{L(2n+1)}{\pi}\frac{(LT)^{2n}}{((2n+1)!!)^2},\quad |t|\le T.$$

This follows from the integral representation of spherical Bessel j_n. Consecutive bounds have ratio (LT)²/((2n+1)(2n+3)), decreasing in n. Summing the geometric envelope over every n>=48 gives the squared Hilbert–Schmidt bound tau for the restricted Fourier transform of the entire omitted space.

Let M=max(a(T)-a(0),2B). The lower-form correction multiplier on [-T,T] has absolute value at most M. Thus the omitted-block lower bound and cross-block upper bound are

$$d=\beta-M\tau-2\varepsilon_p^2,$$

$$c=M\sqrt\tau+2\|p_N\|\varepsilon_p.$$

Here the unitary Fourier transform followed by restriction to [-T,T] is a contraction: its operator norm is at most 1. Its restriction to the omitted Legendre subspace has operator norm at most sqrt(tau), because the Hilbert–Schmidt bound dominates the operator norm. Consequently the multiplier's low/high cross block has norm at most M sqrt(tau), and its omitted diagonal block has norm at most M tau. These estimates control every omitted mode and their arbitrary linear combinations, not merely individual basis vectors.

The pole tail epsilon_p is bounded by the modified spherical Bessel coefficient envelope; ||p_N||<=sqrt(2L)exp(L/2) is sufficient for either parity. All sums and comparisons use outward ball bounds. The resulting numbers are:

| Quantity | Enclosure / conservative bound |
| --- | ---: |
| beta | approximately .647559995860208 |
| tau | <2.080e-44 |
| pole tail squared | <1.211e-218 |
| d | >.64755 |
| c | <1.01e-21 |
| Finite even R_T floor | >.00010106 |
| Finite odd R_T floor | >.009283 |

To prove a full-space floor mu, check m_A>mu, d>mu, and (m_A-mu)(d-mu)>c². The rational targets mu_even=1/10000 and mu_odd=9/1000 pass. The code exports simplified rational constants, and verify_scalar_certificate.py independently checks the final scalar implication using Fraction arithmetic on the outward exported endpoints.

### The bound that failed

The initial frozen choice T=160,N=48 gives an extremely loose low-frequency trace estimate for the omitted Legendre degrees. Even after replacing it with the Fourier contraction bound1, the complement lower estimates are approximately -6.35 at L=.4 and -8.31 at L=.7. Those are failed lower estimates, not negative witnesses.

The successful adaptive retry reduces T to32 only at L=.4, where beta is already positive and LT is small relative to48. At L=.7, T must exceed roughly119 merely to make this beta positive, creating a different cutoff/mode tradeoff. No new all-function certificate at L=.7 is claimed here. Existing D24 certificates at that window are historical source evidence, not replayed results from this computation.

## 5. A measure-correct spherical lift and what cubature evaluates

Fix a unit axis a and normalized spherical area dmu=dOmega/(4pi). Define

$$ (U_Lf)(n)=\sqrt{2L}\,f(L\,a\cdot n). $$

Since the coordinate z=a dot n is uniform on [-1,1] with density1/2,

$$\int_{S^2}|U_Lf|^2d\mu=L\int_{-1}^1|f(Lz)|^2dz=\int_{-L}^{L}|f(x)|^2dx.$$

This is an isometry onto the axisymmetric subspace. The one-dimensional polynomial span of degrees0..5 maps into a **six-dimensional** subspace of the full36-dimensional spherical H_5 space. Choosing an axis does not identify the other angular sectors with extra original interval degrees of freedom.

PENTORA's exact cubature therefore evaluates the norm and inner products in this lifted finite subspace. If A=P_5 W P_5 is the correctly derived six-dimensional compressed form/operator, then U_L A g is again degree<=5 and

$$\langle f,Ag\rangle=\sum_iw_i\overline{U_Lf(n_i)}\,U_LAg(n_i).$$

This is a valid exact node evaluation **after A's entries have been derived**. Applying W to a polynomial does not generally produce a polynomial. The cubature does not manufacture the Archimedean coefficients or turn a nonpolynomial output into degree5. The full form and complement estimates above supply the additional arithmetic information.

The computation uses algebraic square roots and transcendental ball enclosures off the no-float product core. A production research frame must preserve that provenance and uncertainty rather than calling these values exact rational output.

## 6. Validation and deviations

- Full finite matrices used170 decimal digits with512 exact Taylor coefficients and analytic Cauchy remainders. Floating eigensolvers selected candidates; Arb LDL and Rayleigh enclosures validated the claims.
- The complete small-window certificate used100 decimal digits,32-point Gauss rules, corrected analytic remainders, and a full complement bound.
- Sixteen independent Fourier-domain numerical comparisons, using two cutoffs and four low-degree waves at each L, put the time-domain Archimedean values inside their predicted finite-plus-tail ranges. Those comparisons are float64 validation, not the rigorous certificate.
- One independent Acb integral at L=.7,k=1 overlaps the rational-Taylor moment enclosure. Its absolute value is approximately1.80024032365284086458549.
- The initial plan named complex-ball integration for every scalar moment. A pilot showed that approach was slow. It was replaced by the faster rigorous rational-Taylor/Cauchy method; the independent integral is retained as a check.
- The first compact-frequency certificate attempt used direct wide-box Acb digamma for an ellipse majorant, which returned indeterminate. It could not certify the matrix inverse and was recorded as a failed attempt. An analytic derivative majorant replaced it. The initial odd target .01 also exceeded the numerical R32 minimum; the advertised exact odd target was reduced to .009 and then certified. No failed target is presented as passed.
- The original T160/N48 tail failure was retained. T32 at L=.4 was one targeted adaptive retry prompted by the cutoff/basis mismatch.
- A separate agent independently reviewed the full time-domain formula, finite correlation construction, and complete small-window proof. The read-only audit checked Fourier normalization, parity cancellation, the digamma ellipse bounds, the Gauss constant, the complete Fourier and pole tails, and the final two-by-two scalar implication. The audit found no remaining mathematical inconsistency. This review is distinct from an independent implementation or a formal proof-assistant check.
- No new windows, no all-L recurrence, and no RH proof were attempted or claimed.

## 7. Reproduction and sources

Use Python3.12 and the versions in requirements.txt. In a clean virtual environment:

~~~bash
python3 -m pip install -r requirements.txt
python3 weil_schur.py
python3 certify_small_window.py
python3 verify_scalar_certificate.py
python3 validate_formula.py
~~~

The isolated local dependency directory used during this run is not part of the research package. The finite_matrices.npz file supports the independent Fourier check; it contains numerical midpoint matrices, not the ball certificates.

Primary references:

- NIST DLMF5.9.16, digamma integral representation: https://dlmf.nist.gov/5.9.E16 .
- NIST DLMF4.36.1, product formula for sinh: https://dlmf.nist.gov/4.36.E1 .
- Hale and Trefethen, *New Quadrature Formulas from Conformal Maps*, SIAM J. Numer. Anal.46(2),930–948(2008), Theorem2.1, n-point convention in equation2.2: https://www.math.stonybrook.edu/~bishop/classes/math401.F09/Hale-Trefethen.pdf .
- Trefethen (2008), Theorem 4.5, equation 4.14, supplies an independent check of the Gauss error constant: its n+1-node convention gives exponent 2n+2, equivalently 2m for m nodes as used here: https://www.math.stonybrook.edu/~bishop/classes/math401.F09/Trefethen-Quad.pdf .
- python-flint0.9.0 ball arithmetic and certified Legendre roots/weights: https://python-flint.readthedocs.io/en/latest/arb.html .
- The pinned project D24 audit at golden-horizon-principle revision c0db2ebcac5cd1a72d700c61d4a4070f5b7e5e55 supplied the prior normalization and the distinction W>=R_T. This work independently rebuilt the new full matrices and the L=.4 certificate.

These are bounded computational certificates in a specified mathematical model, using standard arbitrary-precision interval software. They are not a formal proof-assistant development or a claim of new published mathematics.
