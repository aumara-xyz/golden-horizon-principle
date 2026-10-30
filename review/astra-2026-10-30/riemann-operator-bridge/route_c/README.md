# Route C replay

Read REPORT.md for the derivation and exact scope. PLAN.md records the bounded exploratory plan. RESULTS.json contains complete coefficient and pivot intervals, Schur parameters, and exact controls. negative_control_certificate.json is the short rational failure witness.

## Run

Python 3.12 or later is recommended. The enclosure engine uses only standard-library Decimal, Fraction, integer arithmetic, and formal power series. NumPy is required for the explicitly noncertifying float64 eigenvalue diagnostics.

From this folder:

~~~bash
python3 cayley_interval.py
~~~

The run uses N=256/K=48 and N=128/K=40 Euler–Maclaurin truncations, 220 digits, a jet through order 24, Toeplitz sections through dimension 16, and sixteen Schur parameters **including alpha_0=0**. Runtime in the producing environment was approximately one second. No network, private repository, mpmath, SymPy, or zeta-zero data is required.

## Arithmetic audit notes

- Every Fraction-to-Decimal conversion computes a lower and upper endpoint with directed division. Integers enter Decimal exactly.
- Elementary interval operations use directed Context methods, not the default nearest-rounded result.
- Decimal logarithms are correctly nearest-rounded by the documented API and then enlarged outward by one representable number at each endpoint.
- Pi is enclosed from rational alternating-series bounds in Machin's identity.
- The only square-root bound in the analytic remainder uses integer isqrt followed by an exact ceiling. No floating square root enters the enclosure.
- Analytic Euler–Maclaurin remainder intervals are added before division/composition of Taylor series.
- Float conversion occurs only after the interval matrix has been built, for the separately labelled eigenvalue diagnostic.
- The on-line polynomial control has an exact positive two-atom representation; its zero LDL pivot reflects rank two, not indefiniteness.

This validates finite sections of an established RH-equivalent criterion. It neither establishes an all-orders Schur bound nor proves RH. The construction is arithmetic/Gamma continuation, not direct convergence of the prime logarithmic-derivative series at s=1.
