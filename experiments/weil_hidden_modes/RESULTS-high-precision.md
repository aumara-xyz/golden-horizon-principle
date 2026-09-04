# High-precision hidden-mode continuation

MEASURED, 2026-09-05. Predictions committed at `96ce678` before computation.
No zeta zero ordinates used. L=0.7, first four modes visible; same sine basis
and prime-side formula as the original experiment. No Fable files changed.

## Results

At 160 decimal digits and Gauss–Legendre order 128:

| Matrix | N=16 minimum |
|---|---:|
| Archimedean-only control | -0.709590273808237 |
| Prime-log +10% control | -0.119856832952302 |
| Prime-log -10% control | -0.196723423206333 |
| Authentic | +1.892390535499608e-12 |

Controls ran before authentic arithmetic at each precision/order. Shifted
controls preserve weights and include all shifted prime powers in support;
they are artificial controls, not alternative L-functions.

| N (mutation) | Full minimum | Hidden-block minimum | Schur minimum |
|---|---:|---:|---:|
| 8 | 1.65568989765e-9 | 0.0234749488044 | 1.65937587499e-9 |
| 12 | 2.82568157228e-11 | 0.00479046792878 | 2.83614315616e-11 |
| 16 | 1.89239053550e-12 | 0.00199876092057 | 1.90057903662e-12 |

The visible minimum is 4.54624609962e-6. At N=16 the ratio of Schur to
visible minimum is 4.18054587229e-7: a reduction by 2,392,032.12.
This compares minima of two forms on the same visible coordinates; it is
not a claim that every vector loses this fraction of its quadratic value.

## Independent checks and limits

Replaced nested integration with exact elementary sine-correlation formulas.
Adaptive mpmath integration checks of five correlations and four pole integrals
agreed within 3e-61 at 60 digits. All 256 zero-shift orthonormality checks passed
the 1e-55 threshold. Run `python3 experiments/weil_hidden_modes/test_high_precision.py`.

For the authentic N=16 minimum, changing order 64 to 128 at 160 digits changes
the result by about 1.54e-89. The 80-digit calculations differ from the
160-digit/order-128 reference by at most 3.10e-80 (from saved decimal values).
The two archimedean formulas differ in matrix Frobenius norm by approximately
9.49e-160 in the final run. These formulas share their correlation and quadrature
implementation, so this is a normalization check, not independent certification.

The earlier double-precision minimum, 1.818336064e-12, was about 3.9% below
the refined value. The sign is now reproducibly positive numerically; the old
digits were not reliable. Original results and predictions remain unchanged.

UNVERIFIED: rigorous positivity. Neither Gauss quadrature truncation nor
roundoff is enclosed by interval bounds. Extra precision and order agreement
are convergence evidence, not proof. Python-flint/Arb is not installed in the
tested Python environment; no interval certificate was produced.

Prediction ledger: all predictions in PREDICTIONS-high-precision.md survived
these tests (positive authentic finite minima, negative controls, persistent
hidden-mode cancellation). The original experiment's anticipation that controls
might also be positive was not observed and remains in its original ledger.

## Honest interpretation

We resolved a numerical ambiguity in a finite restriction of a known Weil form.
We did not find a new positivity principle, a new operator, or a proof of RH.
The unresolved task is to control all omitted modes; numerical positivity of
each tested truncation does not do that. A positive lower bound uniform across
all expanding windows is not required by RH. The next bounded deliverable is a
validated enclosure of this finite Schur minimum, followed by a separate analytic
tail estimate if one can be found. Neither is supplied here.

Source for the form: Connes–Consani, *Weil positivity and Trace formula,
the archimedean place* (2021), equations (1)–(3),
https://alainconnes.org/wp-content/uploads/Selecta.pdf.

Reproduce: `python3 experiments/weil_hidden_modes/high_precision.py`.
Full outputs: `high_precision_results.json`.
