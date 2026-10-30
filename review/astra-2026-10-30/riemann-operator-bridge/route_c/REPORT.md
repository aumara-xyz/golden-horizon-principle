# Route C: a certified finite Cayley–Toeplitz test

**Date:** 30 October 2026.  
**Status:** exact algebra and finite interval certificates; no RH proof or new all-orders bound.  
**Authority:** research only. No repository changes were performed by this worker.

## 1. Outcome

The arithmetic construction produced certified Taylor-coefficient intervals for

$$H(w)=\frac{\xi'}{\xi}\!\left(\frac1{1-w}\right).$$

Every Toeplitz section through dimension 16 has positive outward-rounded LDL pivots. The first sixteen Schur parameters, indexed 0 through 15, are also certified strictly inside the unit disk. No zeta zero ordinate entered either calculation.

The symmetric off-line polynomial control fails exactly at dimension 3. Its negative direction is a rational vector with an exactly negative rational quadratic score.

The result illustrates why float64 sign tests are inadequate here: the authentic 16-by-16 section has all certified positive pivots, but a conventional float64 eigensolve reports a smallest eigenvalue around -3.6e-17. The last certified LDL pivot is approximately 1.0423e-50. A pivot and an eigenvalue are different quantities, but the rigorous pivot signs establish positive definiteness and therefore exclude the spurious negative floating eigenvalue.

This is a finite verification of a known criterion. It supplies no proof that the next parameter, or every later parameter, remains admissible.

## 2. The exact object and the prime-side limitation

Use the completed function

$$\xi(s)=\tfrac12s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s).$$

The Cayley map s=1/(1-w) takes the open unit disk onto Re(s)>1/2. The known positive-real criterion relates RH to the logarithmic derivative having positive real part in that half-plane. Writing

$$H(w)=a_0+\sum_{n\ge1}a_nw^n,$$

the real Caratheodory moments are c_0=a_0 and c_n=a_n/2 for n>=1. The finite section is

$$T_N=(c_{|i-j|})_{i,j=0}^{N-1}.$$

Positivity of every finite section, with the analytic correspondence, is an all-orders condition. Positivity of one finite section also covers its principal submatrices but not arbitrary larger sections.

The user requested a prime/Gamma-side construction. A literal truncated prime logarithmic-derivative series is invalid at the Taylor center s=1: its individual singular pieces diverge. This implementation instead uses **arithmetic Euler–Maclaurin continuation of the defining integer Dirichlet series**, combined with the Gamma contribution. It computes the same analytically continued zeta function that agrees with the Euler product where Re(s)>1. It is a valid arithmetic-side, no-zero-input construction, but it must not be described as direct summation of a convergent prime series at s=1.

The unit-disk analytic variable w is also distinct from the real compact logarithmic coordinate used by the Viviani/Mobius map. Their domains and operators are not silently identified.

## 3. Removing the pole before computing

Set h=s-1 and

$$G(h)=h\zeta(1+h),\qquad G(0)=1.$$

Then the apparent singularity cancels algebraically:

$$
\frac{\xi'}{\xi}(1+h)
=\frac1{1+h}-\frac{\log\pi}{2}
+\frac12\psi\!\left(\frac{1+h}{2}\right)
+\frac{G'(h)}{G(h)}.
$$

The code forms the jet of G through order 25, divides formal series with the exact constant G(0)=1, and forms H through order 24. No zero-free assumption on the whole disk is needed to compute this local jet.

The Gamma coefficients use

$$
\frac12\psi\!\left(\frac{1+h}{2}\right)
=-\frac\gamma2-\log2
+\sum_{k\ge1}(-1)^{k+1}(1-2^{-k-1})\zeta(k+1)h^k.
$$

Here gamma is obtained from the first coefficient of G, and the positive-integer zeta values are themselves evaluated with rational Euler–Maclaurin main terms and explicit remainders.

Finally h=w/(1-w). If q_k is the coefficient of h^k, the Cayley coefficients are

$$a_0=q_0,\qquad a_n=\sum_{k=1}^n\binom{n-1}{k-1}q_k.$$

The center value reproduces the exact known expression

$$a_0=1+\gamma/2-\log2-\tfrac12\log\pi
\approx0.02309570896612103381431024790649529162.$$

## 4. Analytic remainder and outward rounding

For the Euler–Maclaurin approximation retaining terms through B_(2K), the periodic Bernoulli remainder gives

$$
|R_{N,K}(s)|\le
\frac{2\zeta(2K)}{(2\pi)^{2K}}
\frac{|(s)_{2K}|N^{1-\Re s-2K}}{\Re s+2K-1}.
$$

On |s-1|<=1/2, use zeta(2K)<=1+1/(2K-1), 2*pi>6, and |s+j|<=j+3/2. This gives the explicitly rational bound

$$
E_{N,K}=
\frac{2(1+1/(2K-1))\prod_{j=1}^{2K}(j+1/2)\lceil\sqrt N\rceil}
{6^{2K}(2K-1/2)N^{2K}}.
$$

For G(h)=h*zeta(1+h), Cauchy's coefficient estimate on |h|=1/2 bounds its order-j remainder by E_(N,K)*2^(j-1), for j>=1. The constant remainder is exactly zero. Each of these bounds is inserted into the coefficient interval before differentiation, formal division, Gamma combination, or Cayley composition.

Integer zeta remainders use the corresponding rational specialization of the same integral bound. Pi is enclosed using Machin's identity with alternating rational arctangent sums. All rational-to-Decimal conversions and arithmetic endpoints use directed ROUND_FLOOR/ROUND_CEILING at 220 digits. Decimal's correctly rounded logarithm is enlarged by an adjacent representable number at each endpoint. This encloses logarithmic evaluation error as well as subsequent arithmetic rounding.

The primary parameters were N=256, K=48, and 220 digits. A secondary truncation used N=128, K=40, at the same precision. The primary and secondary coefficient enclosures overlap at every order through 24.

| Quantity | Primary N=256, K=48 | Secondary N=128, K=40 |
| --- | ---: | ---: |
| Bound for zeta remainder on the half-radius disk | <4.763e-156 | <3.290e-112 |
| Largest resulting Cayley coefficient interval width | <4.455e-143 | <3.078e-99 |

Agreement between the two runs is a consistency check. The explicit remainder and outward rounding, not agreement alone, establish the enclosures. The certificate depends on the stated analytic inequalities and correctness of the implementation/Decimal arithmetic; it is not a proof-assistant artifact.

## 5. Finite Toeplitz and Schur results

The LDL calculation uses interval arithmetic throughout. A positive lower endpoint for every pivot certifies a positive-definite section.

| Matrix dimension | Last pivot, approximately | Certified pivot sign | Float64 smallest eigenvalue, diagnostic only |
| ---: | ---: | --- | ---: |
| 2 | 3.7085736947e-5 | Positive | 1.8550e-5 |
| 4 | 1.0338172056e-10 | Positive | 5.1827e-12 |
| 6 | 8.0385426951e-17 | Positive | 1.7969e-18 |
| 8 | 2.9441247925e-23 | Positive | -1.7287e-18 |
| 10 | 8.4522652273e-30 | Positive | -2.7128e-18 |
| 12 | 1.5618855440e-36 | Positive | -3.4854e-17 |
| 14 | 1.3878907047e-43 | Positive | -6.1981e-18 |
| 16 | 1.0423247371e-50 | Positive | -3.6048e-17 |

The dimension-16 final-pivot interval has width approximately 1.214e-121, well separated from zero. Complete endpoints are in RESULTS.json.

For the Schur test, start with

$$S_0(w)=\frac{H(w)-a_0}{H(w)+a_0},\quad
\alpha_k=S_k(0),\quad
S_{k+1}(w)=\frac{S_k(w)-\alpha_k}{w(1-\alpha_kS_k(w))}.$$

All coefficients here are real. The first sixteen alpha intervals are strictly within (-1,1). Their approximate centers begin

| Index | Schur parameter |
| ---: | ---: |
| 0 | 0 |
| 1 | 0.999196806720853 |
| 2 | -0.998866411947907 |
| 3 | 0.999384679403830 |
| 4 | -0.999463491366725 |
| 5 | 0.999637513282095 |
| 15 | 0.999862094250987 |

The alternating near-boundary pattern is an observation over this finite list. It is not a proved sign law, monotonicity rule, bound for later parameters, or new invariant.

## 6. Exact negative control and its witness

Use

$$P_\delta(s)=\left((s-1/2)^2+1-\delta^2\right)^2+4\delta^2.$$

Both choices delta=0 and delta=1/5 have real coefficients and satisfy P(s)=P(1-s). Their logarithmic derivatives are composed with the same Cayley map and use the same coefficient-to-Toeplitz convention.

For delta=0, the moments are exactly

$$c_n=\frac85\Re\!\left[\left(\frac35+\frac45i\right)^n\right].$$

This is a positive measure with two atoms, each of weight 4/5, on the unit circle. Every Toeplitz section is positive semidefinite, and its rank is two once the dimension is at least two. Exact LDL therefore encounters a zero pivot at dimension three, as it should. A zero pivot in this control is not a failure of positivity.

More explicitly, let z=3/5+4i/5. Direct rational substitution gives

$$
H_0(w)=\frac{8(1-w^2)}{5-6w+5w^2}
=\frac45\left(\frac{z+w}{z-w}+\frac{\bar z+w}{\bar z-w}\right).
$$

For |w|<1, each summand has real part (1-|w|²)/|z-w|², or its conjugate-atom counterpart, strictly positive. This proves positivity on the entire open disk for the synthetic on-line control, independently of finite matrix checks.

For delta=1/5, the 1-by-1 and 2-by-2 sections are positive definite but the 3-by-3 section is indefinite. The first negative pivot is exactly

$$-\frac{18202985600000000}{176198188057040583}.$$

An explicit negative vector for that leading block is

$$v=\left(\frac{708601643}{667999143},
-\frac{14939087890126}{10848974081463},1\right),$$

and exact fraction arithmetic verifies that v^T T_3 v equals that negative pivot. Appending zeros gives a negative witness for every larger leading section.

Thus the test distinguishes line-centered from off-line synthetic zeros despite identical reflection/conjugation symmetries. The control is a polynomial, not a substitute zeta function.

## 7. Rational Mobius checks

On the real compact coordinate x=tanh(t/2), translation by log(n) is

$$T_n(x)=\frac{(n-1)+(n+1)x}{(n+1)+(n-1)x}.$$

The script verifies twelve exact fraction cases of composition T_m(T_n(x))=T_(mn)(x) and reflection -T_n(-x)=T_(1/n)(x). These identities also follow directly from matrix multiplication. The matrices M_n satisfy M_m M_n=2 M_(mn), and M_n/(2sqrt(n)) has determinant one and exact multiplicative composition.

Those representation identities do not force the Cayley Schur parameters to remain in the disk. No such all-orders arithmetic recurrence was derived here.

## 8. Scope, deviations, and replay

The plan was frozen before these runs, but this was exploratory work informed by preceding reports. The first run implemented Toeplitz checks; Schur-parameter enclosures and an explicit rational negative vector were then added as planned consistency/control outputs. A metadata flag for the center formula was changed from a symbolic assertion to a computed interval-overlap check. The final script was rerun and the completed outputs replaced the intermediate files.

No broad parameter search, higher matrix order, zeta-zero scan, repository write, or product action was performed. The third-party D25A/Slepian claims are outside this worker's scope.

Run from any directory:

~~~bash
python3 cayley_interval.py
~~~

The arithmetic enclosure uses only Python's standard library. NumPy is required only for the explicitly labelled floating eigenvalue diagnostics. The script writes RESULTS.json; PLAN.md is hashed into it. run-summary.json is a compact captured terminal summary from the final run.

## 9. Primary references

- J. C. Lagarias, *On a positivity property of the Riemann xi-function*, Acta Arithmetica 89 (1999), 217–234, DOI 10.4064/aa-89-3-217-234. Author copy: https://websites.umich.edu/~lagarias/doc/positivity.pdf . The text extraction of this scanned/encoded copy is poor; the criterion was also checked in Suzuki's explicit discussion.
- M. Suzuki, *Aspects of the screw function corresponding to the Riemann zeta-function*, https://arxiv.org/pdf/2206.03682 .
- NIST DLMF §25.2(iii), Euler–Maclaurin representations of zeta: https://dlmf.nist.gov/25.2#iii .
- NIST DLMF §24.8, Fourier expansions of periodic Bernoulli functions, supplying the standard supremum bound: https://dlmf.nist.gov/24.8 .
- NIST DLMF §5.15, especially the half-integer polygamma values in 5.15.3: https://dlmf.nist.gov/5.15 .
- Python 3.12 Decimal documentation, directed arithmetic and correctly rounded logarithms: https://docs.python.org/3.12/library/decimal.html .
