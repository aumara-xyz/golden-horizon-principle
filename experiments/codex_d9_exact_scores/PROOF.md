# Bounds used by the D9 scalar computation

These are text proofs feeding interval calculations, not formal proof-assistant certificates. Two additional Codex readers checked the formulas and current code. All share the same arithmetic environment; this is not independent-library validation.

## Fixed function and exact arithmetic term

L=7/10, f(x)=sum_n v_n sqrt((2n+1)/(2L)) P_n(x/L) on [-L,L], zero outside. The coefficients v_n are the saved exact decimal strings, not later optimized variables. Normalize all scores by the interval-enclosed exact squared norm. In unnormalized Legendre coefficients b_n, ||f||²=sum_n 2L b_n²/(2n+1).

For a in [0,2L), the shift correlation is

I_a=(2L-a)/2 integral_{-1}^1 f(a/2+(2L-a)u/2) f(-a/2+(2L-a)u/2) du.

The integrand has degree <=2d. Gauss-Legendre with K=d+1 is exactly integrating this polynomial at mathematical nodes and weights; Arb root/weight enclosures and interval evaluation account for numerical error. Here d=158 even or159 odd, so K=159 or160; a second pass with K+16 checks overlap. For a>=2L the correlation is zero (touching endpoints have measure zero).

The full prime functional is sum_{n=2,3,4} w_n I_log(n). The pole is +2C² for even and -2S² for odd, where integral P_n(x/L)e^{x/2}dx=2L i_n(L/2). No frequency tail is omitted from these terms.

## Compact archimedean integral

F(t)=(2pi)^(-1/2) integral f(x)e^{-ixt}dx. For a pure real parity candidate, H(t)=i^parity F(t) is real, and |F(t)|²=H(t)². Its analytic continuation is H(z)², not |F(z)|². Evaluate H by the spherical-Bessel transform of the Legendre basis.

The analytic continuation of a(t)=Re psi(1/4+it/2)-log pi is

A(z)=[psi(1/4+iz/2)+psi(1/4-iz/2)]/2-log pi.

Unit panels have halfwidth h=1/2. For rho=1.9, their Bernstein ellipses have imaginary semiaxis b=h(rho-rho^-1)/2<1/2, hence avoid the digamma poles. If delta=1/4-b/2>0 and |s|<=zmax on either digamma argument, its series gives

|psi(s)| <= gamma+1/delta+|s| sum_{k>=1}1/k² <=1+1/delta+2 zmax.

The code bounds zmax by the sum of the maximum absolute real and imaginary coordinates and includes log pi for A. Cauchy-Schwarz on f gives |H(z)²|<=(L/pi)||f||² exp(2Lb) throughout the ellipse.

Gauss with K nodes is exact to degree2K-1 and its positive weights sum to2. Chebyshev coefficients bounded by2M rho^-k give polynomial truncation error <=2M rho^(1-2K)/(rho-1). Integral and quadrature norms sum to4, hence panel error <=h*8M rho/((rho-1)rho^(2K)). Sum panels and double for negative frequencies. K=64 in the authentic runs; 64/80-node overlap was checked for controls and both frozen candidates on [0,2]. All values, nodes and weights are balls.

## Upper and lower bounds for the entire omitted archimedean tail

For z=1/4+it/2, compare the digamma defining sum with its integral, cell by cell:

|psi(z)-log z| <= integral_0^infinity |u+z|^-2 du <= pi/t.

Indeed the sum-minus-integral error of (n+z)^-1 on each cell is bounded by the integral of |(u+z)^-2| on that cell; the logarithmic endpoint limit gives log z. Therefore

a(t)<=log t-log(2pi)+pi/t+1/(8t²).

At T>=128 the code verifies pi/T+1/(8T²)<log(2pi), proving a(t)<=log t on the whole tail. Also a(t) is increasing for t>0: differentiating its digamma series gives -Im psi'(1/4+it/2)/2>0. Arb verifies a(T)>0.

For m integrations by parts define b_j=|f^(j)(L)|+|f^(j)(-L)|, j<m, and D_m=||f^(m)||² on the interval. Do not discard boundary jumps of the zero extension. Define

J_p=T^(1-p)[log(T)/(p-1)+1/(p-1)²],
E_m=(1/pi)sum_{j,k<m} b_j b_k J_(j+k+2),
H_m=D_m log(T)/T^(2m).

The first term bounds the weighted squared Fourier norm of the boundary contribution. The second uses Plancherel on the mth derivative restricted to the interval and monotonicity of log(t)/t^(2m), valid for logT>=1/(2m). Weighted triangle inequality then proves

0<=integral_{|t|>T} a(t)|F(t)|²dt <= (sqrt(E_m)+sqrt(H_m))².

Derivatives are computed entirely in Legendre coefficients: b'_k=(2k+1)/L sum_{n>k,n-k odd}b_n; endpoint derivatives are sums with signs, and their L2 norms use orthogonality. Interval arithmetic encloses cancellation in those sums. Orders1..12 were preregistered; take the smallest valid upper bound.

For a lower bound, Plancherel gives tailmass=||f||²-integral_{-T}^T |F|². Its nonnegative lower bound multiplied by a(T) is a valid lower bound for the archimedean tail. Combining this with the compact integral and the upper bound yields an interval for the FULL archimedean integral, not just a frequency-envelope score.

## Exact forms and quantifiers

W=A_full+pole-prime. R_theta=W-theta(c_L||f||²-prime). Both are evaluated on the SAME fixed f. A negative upper endpoint proves R_theta has a negative witness. A positive lower endpoint proves positivity only on that candidate, not on all functions.

Separately, conditional on D7 W>=mI, m=1.031e-13, the prime operator satisfies -B I<=P<=B I. Thus R_theta>=[m-theta(c_L+B)]I. At theta=1e-14 the bracket is >5.69e-14. This is an all-function consequence of the pre-existing D7 certificate, not of the new candidate tests. It directly excludes the D8 claim that every theta>0 fails.
