# Toy T3 — does the bell get purer with height? (before compute)
Data (Odlyzko): A = zeros 1-10^4 (T~1e4, ln(T/2pi)=7.4); B = 10^4 zeros at #10^12 (T=2.7e11, ln=24.5); C = 10^4 at #10^21 (T=1.4e20, ln=44.6); D = 10^4 at #10^22 (T=1.4e21, ln=46.9). Same sample size everywhere. Unfolding by local mean density ln(T/2pi)/(2pi).
PREDICTED 1: KS distance of spacings to the Wigner surmise falls with height: A > B > C >= D; A about 0.02-0.03, C and D below 0.015. (KS noise floor for n=10^4 is ~0.01, so C vs D may be indistinguishable.)
PREDICTED 2: number-variance saturation rises toward GUE with height: Sigma^2(L=30) ordered A < B < C <= D, with D within 0.15 of the GUE value 0.69.
PREDICTED 3: the prime-2 fingerprint period ln(T/2pi)/ln 2 = 10.7, 35, 64, 68 for A-D; the residual's best period (scan 3-90) lands within 15% of these for at least three of four. Kill: periods not tracking ln(T/2pi).
PREDICTED 4: pair-correlation L1 to GUE falls with height, A > D.
Overall kill: if C or D is farther from GUE than A on KS and pair correlation, "purer with height" is dead and the ledger says so.
