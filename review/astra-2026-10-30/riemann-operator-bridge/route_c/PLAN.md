# Route C bounded plan — 30 October 2026

This is exploratory research informed by the preceding report and the user's claims. No claim of blind preregistration is made. This plan is written before the new coefficient/matrix runs.

## Object

H(w)=(xi'/xi)(1/(1-w)), with xi(s)=s(s-1)pi^(-s/2)Gamma(s/2)zeta(s)/2. The Taylor center is s=1, where the apparent pole cancels. The associated Caratheodory Toeplitz moments are c0=a0 and cn=an/2 for n>=1, where H(w)=sum an w^n.

## Coefficients without zero input

Use Euler–Maclaurin continuation of the arithmetic series for zeta, first regularizing G(h)=h*zeta(1+h). Compute its Taylor jet with exact rational Bernoulli coefficients and Decimal interval arithmetic for logarithms. Combine G'/G with 1/(1+h), the Gamma logarithmic derivative, and -log(pi)/2. Compose h=w/(1-w) exactly at jet level. There is no use of a divergent prime series on the center and no zeta zero input. Euler–Maclaurin is arithmetic-side continuation of the same zeta function; it is not literally a truncated Euler product.

Attempt finite Toeplitz/Schur tests through order 16, with coefficient jet through order 24. Freeze primary Euler–Maclaurin N=256,K=48 and 220 Decimal digits. Compare a smaller independent truncation N=128,K=40 for coefficient stability. A priori remainder bounds, not agreement alone, govern any certified sign label. If interval inflation obstructs a pivot, report unresolved at that order rather than increasing scope repeatedly.

## Controls

Use exact rational jets for P_delta(s)=(((s-1/2)^2+1-delta^2)^2+4delta^2), H_delta(w)=P_delta'/P_delta evaluated at s=1/(1-w). Delta=0 has zeros on the symmetry line; delta=1/5 has symmetric off-line zeros. Evaluate matching finite orders. A passing symmetry control does not make it zeta.

Verify rational Mobius maps T_n(s)=((n-1)+(n+1)s)/((n+1)+(n-1)s), composition T_m T_n=T_(mn), and reflection conjugacy with T_(1/n), using exact fractions.

## Reporting

Separate exact algebra, analytic remainder bounds, outward-rounded finite calculations, floating eigenvalue diagnostics, and all-orders unproved claims. Record the first order detecting the bad polynomial and the largest certified authentic finite section. No result is an RH proof. No repository writes or product authority.
