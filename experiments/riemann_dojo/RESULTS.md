# Riemann Dojo — RESULTS (2026-09-14)

The Dojo is the execution court for Weil-form candidates: a candidate wave goes
in, an interval-certified receipt comes out. Built 2026-09-14 (Antigravity);
verified by independent re-run the same morning (OpenCode).

## Components

| File | Role |
|---|---|
| `dojo_court.py` | Arb interval evaluation of W(f) at 320-bit precision: Legendre basis, prime overlaps via quadrature, Bessel pole term, 13-order derivative tail bounds, Hale–Trefethen-style quadrature error allowance with the ρ-factor that D24's repair established |
| `dojo_runner.py` | The hunter loop: queries `auma-gen-8` (:8010) for candidate JSON, scores it through the court, feeds the receipt back for the next round |
| `step0-clean-room-verify.py` | Independent re-derivation of three saved matrix entries from raw quadrature definitions |
| `d25-stage-c-verify.py` | Independent Stage-C evaluation of `d22_cand2_odd_L0.4` at T=256 |

## Verified receipts (2026-09-14)

1. **Step-0 clean-room** — entries (1,1), (1,3), (21,41) recomputed from scratch
   and checked against `fable_d22_test2/d22_cert_odd_L0.4_T160_N160.json`:
   entry (21,41) = `0.0899647662393185913 ± 8.46e-23` vs saved `± 8.35e-23`.
   **ALL TARGET ENTRIES VALIDATED — 21-digit overlap.** The saved-matrix chain
   gains its missing independent-reproduction link for these entries.

2. **Court self-test** — wave [1.0, 0.1, 0.01] on degrees [1,3,5], L=0.4, odd,
   T=128: `W ∈ [0.5173511…, 0.7487975…]`, compact precision ~1e-31,
   `is_certified_positive: true`.

3. **D25 Stage-C** — `d22_cand2_odd_L0.4` (80 modes, T=256):
   `W ∈ [0.01506568428585107…, 0.04685651518377426…]`, certified positive.
   Reproduces the claimed bracket `[0.01506, 0.04685]` digit-for-digit.

## Status ledger

| Item | Status | Note |
|---|---|---|
| Step-0 three entries | `MEASURED` (reproduced) | independent implementation, interval match |
| Dojo court positivity receipts | `MEASURED` (functional) | conditional on the court's bound validity below |
| D25 Stage A/B (μ_vis = 1.41715765e-2; gate ratio 1.025) | `MEASURED` (float-grade) | `eigvalsh`/ray-energy; reproduces the reduced-form values already in `d22_cand2_odd_L0.4.json`; NOT a certificate — exact/rational checked under D24 discipline is the next step |
| Court quadrature/tail bound validity | `UNVERIFIED` | needs the D24-style audit (the factor-ρ² repair) applied to `Cq` and the tail-bound formula before receipts are called certified externally |
| RH connection | unchanged ceilings | finite windows cannot prove RH; the corpus's Open 2 (monotone invariant) remains the structural question |

## Conventions used by the runner

- Support [-L, L], Legendre basis `P_n(x/L)`; odd parity for the destructive
  pole term `-2S²`.
- Visible prime powers at L=0.4: n=2 only.
