# Fable D25 mass-aware bracket pilot — prediction ledger (committed BEFORE any certificate run)

Protocol: `astra_d24_review/PREDICTIONS.md` (frozen 2026-09-13). Scope: ONE gated
experiment, odd ζ at L=0.4, trial-4 frozen wave, no reselection, no new rooms, no
T4000. Budget: ≤60 single-core CPU-min, ≤90 wall-min, hard stop on gate failure.

## Predictions (made before running)

1. **Certified visible-form floor**: the floating visible minimum is ~0.0141716.
   Under the corrected K=64 allowance (ρ² factor, K-node definition) and a
   conservative certified interval route, I expect the certified μ_vis in
   [0.0138, 0.0142]. If μ_vis < a/1.1 = 0.013812 (a = 0.0151928770501), the
   energy gate FAILS and the pilot stops at Stage B scoped no-go.
2. **Energy gate**: a/μ_vis ≈ 1.072–1.100 if μ_vis lands near 0.0141 → gate
   PASSES as a necessary condition (expected).
3. **Mass-conditioned tail at T=512**: the old T=256 upper 0.04686 is
   tail-dominated (~0.0327 tail bound at T=256). The D24 §4.3 bound conditions
   on actual mass; I expect the upper to drop into [0.016, 0.030]. If it lands
   ≤ 0.0166 = 1.1×W_lower(0.01519), the bracket closes.
4. **Bracket prediction**: I expect an OPEN bracket with ratio ~1.2–1.9 —
   improved from 3.1× but not closed. If wrong in the favorable direction:
   first two-sided bracket of the program.

## Deviations (declared in advance)

- If the full 256-bit Arb matrix build (160×160, K=64/panel) exceeds the CPU
  budget, fall back to certifying a SMALLER first: build at N=80/T_R=160 and
  report the finite-minimum comparison (N=80 vs N=160 enclosures) without
  advertising an all-function floor. All results labeled accordingly.
- The rational shifted-Schur replay (D24 tooling) is reused where its inputs
  match the visible form; otherwise the certified interval-eigenvalue route
  (λ_min(A) ≥ λ_min(mid) − ‖rad‖∞ on the symmetric enclosure) is used and
  labeled as such.
