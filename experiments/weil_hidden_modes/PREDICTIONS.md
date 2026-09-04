# Weil hidden modes — frozen 2026-09-05 before computation

Construct the geometric Weil form with no zero ordinates. Source: Connes–Consani,
https://alainconnes.org/wp-content/uploads/Selecta.pdf, equations (1)–(3).
For real f supported on [-L,L], put g(u)=integral f(x+u)f(x) dx.
Q = 2 (integral f exp(x/2)) (integral f exp(-x/2))
 -(gamma+log(4*pi))*g(0)
 + integral_0^infinity [g(0)-exp(u/2)g(u)]/sinh(u) du
 - 2 sum_(p,m) log(p)/p^(m/2) g(m log p).

Basis: normalized Dirichlet sines on [-L,L], extended by zero.
These endpoint-vanishing functions are used for numerical form evaluation, not claimed
as a smooth test-function certificate. L=0.4,0.7,1.0; N=4,8,12,16.
Visible block: first four modes. Hidden block: remaining modes.
Compute D minimum eigenvalue, Schur minimum eigenvalue, and normalized coupling
norm ||A^(-1/2) C D^(-1/2)|| when A and D are resolved positive.

Gauss quadrature orders 96/192/384; report differences as convergence diagnostics,
NOT rigorous error bounds. Compare two equivalent archimedean integral formulas.
No interval certificate or infinite-dimensional conclusion will be claimed.
Controls before authentic matrices: omit arithmetic; shift each prime log by +10%,
keeping its weight; and shift by -10%. Include all prime powers relevant after shift.
Surviving positivity is mutated by doubling N and enlarging L (frozen above).

PREDICTED: finite authentic matrices positive or numerically unresolved; hidden modes
reduce the visible minimum; controls can also be positive; no uniform margin emerges.
Failed predictions remain. Finite Cholesky is not an explicit infinite factorization.
