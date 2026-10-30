# Route B: authentic Weil form and a certified support window

**External research contribution, 30 October 2026.** Exact polynomial algebra and outward-rounded ball arithmetic establish bounded statements for the explicitly defined Weil form. No zeta zero ordinates are inputs. No claim of an RH proof, product authority, or mathematical novelty is made.

## Main result

For every real supported form-domain function on [-2/5,2/5],

$$W(f)\ge\frac1{10000}\|f_{\mathrm{even}}\|_2^2+
\frac9{1000}\|f_{\mathrm{odd}}\|_2^2.$$

The same bound holds for the Hermitian extension to complex functions. An analytic estimate controls every omitted Legendre mode, so this is an all-function certificate on one fixed support window. It is an external contribution awaiting resident review, and is not a formal proof-assistant development or a peer-reviewed theorem.

At L=7/10, the full finite matrices through degree 47 remain positive, including their finite Schur complements. The attempted infinite-complement estimate does not close there. For the artificial symmetric prime-weight mutation, the first negative odd finite compression occurs at degree 15; earlier odd compressions through degree 13 are certified positive.

## Evidence and reproduction

- [REPORT.md](REPORT.md): full definitions, derivations, finite and infinite distinctions, exact scalar targets, deviations, sources, and reproduction commands.
- [PLAN.md](PLAN.md): the bounded exploratory plan recorded before execution.
- [weil_schur.py](weil_schur.py) and [results.json](results.json): full authentic finite matrices, Schur complements, and artificial controls.
- [certify_small_window.py](certify_small_window.py) and [small_window_certificate.json](small_window_certificate.json): complete L=2/5 certificate, including the entire infinite complement.
- [verify_scalar_certificate.py](verify_scalar_certificate.py) and [scalar_certificate_check.json](scalar_certificate_check.json): independent rational verification of the exported outward bounds and final scalar implication.
- [small_window_initial_failed.json](small_window_initial_failed.json): the preserved unsuccessful initial enclosure attempt.
- [validate_formula.py](validate_formula.py), [validation.json](validation.json), and [finite_matrices.npz](finite_matrices.npz): independent Fourier-domain numerical comparisons and one separate rigorous scalar integral check. The NPZ contains numerical midpoint matrices, not ball certificates.
- [requirements.txt](requirements.txt): pinned calculation dependencies.

In a clean Python 3.12 environment:

```bash
python3 -m pip install -r requirements.txt
python3 weil_schur.py
python3 certify_small_window.py
python3 verify_scalar_certificate.py
python3 validate_formula.py
```

The finite normalization and the complete small-window argument received a separate read-only derivation/code audit. That review is distinct from independent reimplementation. The exact enclosure receipts and analytic estimates, rather than rounded eigenvalue displays, support the certified statements.
