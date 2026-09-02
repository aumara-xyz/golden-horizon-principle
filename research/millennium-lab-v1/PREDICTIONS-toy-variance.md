# Toy T2 — Berry's number variance: the primes as a defect in the zeros (before compute)
Statistic: Sigma^2(L) = variance of the number of unfolded zeros in a window of length L, over random window starts. GUE exact: L - 2*int_0^L (L-x) (sin(pi x)/(pi x))^2 dx, grows like ln(L)/pi^2 forever. Poisson: L.
Data: Odlyzko 100k zeros; two height bands: zeros 1-20000 (T~2.4e4, ln(T/2pi)=8.2) and 80001-100000 (T~7e4, ln(T/2pi)=9.3). Control: GUE matrices (no saturation, no bumps), Poisson.
PREDICTED 1: for L <= 2, zeros track GUE within 0.05 in both bands.
PREDICTED 2: saturation: at L=30 the zeros sit below GUE by at least 0.15 (GUE(30) ~ 0.57), and the curve is flat-ish beyond L~10 rather than growing. GUE matrices do not saturate.
PREDICTED 3: the residual (zeros minus a smooth fit) oscillates with period ln(T/2pi)/ln 2: ~11.9 in the low band, ~13.4 in the high band. The dominant Fourier period of the residual over 3<=L<=60 shifts upward between bands by ~1.5. Kill: no oscillation, or period not tracking ln(T/2pi).
PREDICTED 4: the low band saturates at a LOWER level than the high band (saturation ~ (1/pi^2) ln ln T rises with T).
