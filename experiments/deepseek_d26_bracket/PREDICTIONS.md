# D26 bracket pilot — prediction ledger (committed BEFORE any compute)

Base: codex/metatron-prime-return-v0 @ c178993. Executor: DeepSeek 4.1 Flash.
Scope: D24/D25 protocol; L=0.4 odd; trial-4 frozen wave; visible primes only;
no new rooms; no reselection except the one preregistered move; caps 60 CPU-min.

## Definitions (corrected per D26 Task 0)

- Wave enclosure: W(f) ∈ [W_lo, W_hi] for the FROZEN wave. D25 measured
  [0.01519288, 0.01563021], width 2.9% of the wave's own score.
- Infimum bracket: [ell, W_hi] with ell the ALL-FUNCTION certified floor
  (ell ≤ m_R ≤ m_W). D25's finite-N floor is not such an ell; the honest
  D25-era infimum ratio is ≥ 0.01563021/0.0141716 = 1.1029 (open).

## Predictions (before compute)

1. **Schur extension (visible primes, L=0.4 odd, N=160, T=160, K=64)**:
   eps values at x=TL=64 are astronomically small (redundant-form precedent:
   eps_D ~1e-362, eps_C ~1e-178, eps_p ~1e-988); I predict the all-function
   floor ell lands within 1e-6 BELOW the finite floor: ell ∈ [0.0141705, 0.0141716].
2. **T=512 infimum ratio**: 0.01563021/ell ≈ 1.1029-1.1030 → the 10% gate FAILS
   at T=512, as Astra states.
3. **Move (a) T=1024 (preregistered)**: the wave's tail mass at T=512 is
   1.26e-4; with |F|^2 ~ t^-10 decay the T=1024 upper should collapse the
   enclosure toward W_true in [0.01519, 0.01520]. Predicted infimum ratio at
   T=1024: 1.071-1.073 → **the bracket CLOSES via move (a), ratio ≤ 1.10**.
4. **Court audit (Task 3)**: expect the code to match the D24 §4.3 derivation
   line-for-line with the abs_upper/upper fix in place; planted controls:
   omitted tail REJECTED, crossing-zero UNRESOLVED, wrong pole sign changes
   score, mismatched norm fails.
5. If (a) fails, move (b): the unconstrained N=160 visible minimizer, frozen,
   scored the same way; predicted W ≈ its Rayleigh quotient ~0.0142 + small,
   likely closing at T=1024 too.

## Labels

ell = interval-certified all-function floor (if the Schur certifies);
wave scores = interval enclosures for a fixed wave; no RH claim; court bounds
audited as Task 3 of this directive; if the audit finds a defect, every
downstream number carries "court unaudited/defective" and the run stops.
