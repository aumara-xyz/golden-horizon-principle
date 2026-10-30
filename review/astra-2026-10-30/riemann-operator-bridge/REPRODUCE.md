# Reproduce the research package

The producing environment used Python 3.12.14. The recorded NumPy, SciPy, and Python-FLINT versions are pinned in requirements.txt. No network or zeta-zero data is used by the calculations after dependencies are installed.

From this folder:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 d25a_audit/run.py
python3 route_a/run.py
python3 route_b/weil_schur.py
python3 route_b/validate_formula.py
python3 route_b/certify_small_window.py
python3 route_b/verify_scalar_certificate.py
python3 route_c/cayley_interval.py
~~~

Each script resolves its own file location. It writes results next to its source and leaves the preceding run plan intact. Run in a disposable checkout if preserving the exact published receipts is important. Elapsed times and last-bit floating diagnostics may differ across platforms. Interval signs and exact rational identities are the substantive outputs.

The numerical midpoint archive route_b/finite_matrices.npz is a convenience artifact, not the interval certificate. The authoritative enclosure receipts are the JSON files and their generating code, together with the explicit analytic bounds in each report. The failed preliminary tail bound and first indeterminate quadrature enclosure are retained and labelled.

The companion PENTORA exact oracle requires only the standard library:

~~~bash
cd ../pentora-exact-instrument
python3 test_reference.py
~~~

It checks 33 mathematical and input/refusal groups. It is not an X2 Wasm build, fuel test, adoption, or runtime authorization test.

## Evidence classes

- **Exact:** rational/algebraic identities and finite negative witnesses.
- **Certified computational:** outward-rounded interval/ball calculations with a stated analytic remainder and a reproducible proof argument.
- **Measured:** float64 eigensolvers, correlations, condition estimates, and selected numerical diagnostics.
- **Unproved:** all-L crossover bounds, all-window Weil positivity, all-order Schur conditions, and an RH proof.

No floating agreement or plan hash upgrades the last two classes to the first two. No source digest alone certifies an external analytic residual.
