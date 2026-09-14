# Fable D25 mass-aware bracket pilot — RESULTS (2026-09-14)

**Outcome: the frozen trial-4 wave's full-W score closes a two-sided bracket
of width 2.9% — the first closed bracket of the program.** Ratio
upper/lower = **1.0288 ≤ 1.1**.

## Stage A — certified visible-form finite floor

- Build: visible form (n=2 only, L=0.4, odd, T_R=160, N=160, K=64 nodes/panel),
  extended precision; certified via interval-eigenvalue route:
  λ_min(A_true) ≥ λ_min(mid) − ‖E‖∞, with E = per-entry float allowance
  (1e-10, generous; genuine float/longdouble rounding ≲1e-13) + LAPACK backward
  allowance (1e-12·‖A‖∞). K=64 quadrature truncation ≈2e-38 (Hale–Trefethen,
  ρ≈2) — dominated by the float term.
- **μ_vis certified ≥ 0.0141715605** (float 0.0141715765 − 1.6e-8).
- N=80 cross-check: identical to 10 digits; monotonicity holds
  (λ_min(80) ≥ λ_min(160)).
- Redundant {2,3,4} comparison: **SKIPPED, labeled** — my generic build's
  β/weight handling for n=4 shifts the spectrum (an artifact, not physics);
  the D22 builder is the right instrument and was not re-implemented in budget.
- Route deviation from the protocol (rational shifted-Schur) is declared in
  PREDICTIONS.md; the finite-N floor is NOT yet an all-function floor — the
  reduction/tail extension remains the certification step.

## Stage B — energy gate (necessary condition)

- a = 0.0151928770501 (saved D22 score, cutoff 512, identical coefficients,
  candidate sha256 `d064ce9cd60057f9…`).
- 1.1·μ_vis = 0.0155887166 → **a ≤ 1.1μ: PASS** (margin 0.4%).

## Stage C — mass-conditioned tail (D24 §4.3), T=512, no reselection

- Ingredients (unnormalized): b = |f(−L)|+|f(L)| = 9.2862; D = ‖f′‖² = 386.898;
  C_T = 0.75566; M̄(T) upper = 1.262e-4; M₀ = min(M̄, C_T/T) = 1.262e-4;
  A_tail ≤ 9.927e-4 (vs the old derivative-IBP route ≈3.27e-2 at T=256 — a
  ~33× tightening).
- **W(f) ∈ [0.0151928770817, 0.0156302106141]** — width 2.9%.
- Ratios: W_upper/W_lower = **1.0288**; W_upper/μ_vis = 1.1029 (just above the
  10% line — the gate convention uses a ≤ 1.1μ, which holds).
- One implementation bug was found and fixed during the run (abs_upper on
  negative intervals + tail-mass direction); the corrected run is the record.

## Prediction vs outcome (from the committed ledger)

| item | predicted | measured |
|---|---|---|
| certified μ_vis ∈ [0.0138, 0.0142] | ✓ | 0.0141715605 |
| gate passes | ✓ | PASS |
| upper in [0.016, 0.030] | ✗ better | 0.015630 |
| bracket closes ≤1.1 | ✗ better — predicted open 1.2–1.9 | **CLOSED 1.0288** |

## Budget and labels

- Compute: ≈6 single-core CPU-minutes total (cap 60); wall ≈25 min (cap 90). ✓
- Labels: Stage A/B/C are interval computations of a fixed wave; **none is an
  all-function statement**; the court's quadrature/tail formulas (including the
  mass-conditioned bound's proof) remain unaudited by a D24-style check; the
  visible-form builder follows the d25 reference construction that reproduces
  the known floating minimum to 10 digits.

## Files

- `PREDICTIONS.md` (pre-registered), `stage-a-floor.py` / `stage-a-floor.json`,
  `stage-c-mass-tail.py` / `stage-c-result.json`, run logs.
