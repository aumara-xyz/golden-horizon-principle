# High-precision continuation — frozen before computation

PREDICTED: at L=0.7, N=16, the authentic Weil matrix and its four-visible-mode
Schur complement have positive smallest eigenvalues of order 1e-12. The
archimedean-only and both shifted-prime controls remain negative. Hidden-mode
cancellation remains strong. Wrong predictions will be retained.

Use 80 and 160 decimal digits, analytic sine autocorrelations (replacing the
previous nested numerical integral), and Gauss–Legendre orders 64 and 128.
Run controls before the authentic matrix at each precision/order. Mutation:
evaluate principal restrictions N=8,12,16. Compare the two equivalent
archimedean formulas. No zero ordinates enter.

Report convergence, matrix minima, hidden-block minima, Schur minima and
the ratio of Schur to visible minimum. Agreement is MEASURED, not a rigorous
sign enclosure. Interval-certified positivity remains UNVERIFIED unless a
validated quadrature bound is actually supplied. A finite positive matrix
does not establish RH or control the omitted infinite tail.
