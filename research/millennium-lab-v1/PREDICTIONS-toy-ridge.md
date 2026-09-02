# Toy T1 — is the critical line a ridge of every Li energy? (written before compute)
Setup: contribution of a zero quadruple {beta+i gam, 1-beta+i gam, conjugates} to lambda_n is c_n(beta,gam) = 2 Re[(1-(1-1/rho)^n) + (1-(1-1/rho')^n)].
At beta=1/2 the quadruple is a double zero on the line. Test: sign of D_n = c_n(0.51,gam) - c_n(0.5,gam) for n=1..500 and gam = first 100 zero heights.
PREDICTED: n=1 is a ridge for every gam (D_1 < 0), from the derivative done by hand.
PREDICTED: NOT a ridge for all n. Because |1-1/rho| = 1 exactly on the line, the on-line term is 2-2cos(n theta) and the off-line twins have r1<1<r2, so D_n ~ -2cos(n theta)(r1^n + r2^n - 2): ridge when cos(n theta)>0, valley when cos<0. Fraction of valleys over (n,gam) approaches ~1/2.
PREDICTED: every on-line term 2-2cos(n theta) is >= 0; so Li positivity is termwise on the line, never a local-max property. The real content: |rho-1| = |rho| iff Re rho = 1/2 (the zero is equidistant from 0 and 1).
Kill: if D_n < 0 for all n and gam, my hand derivation of the oscillation is wrong and "ridge" survives.
