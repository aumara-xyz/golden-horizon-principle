# SYK-CORRIDOR-v2 — OFFICIAL LAPTOP RUN VERDICT

- label: **PIPELINE-VALIDATION** (laptop venue; the contract's certified run is the
  Nebius execution only — section 6(d) remains undischarged; no cloud spend occurred:
  **USD 0.00 of the 400 cap**)
- governing contract (SIGNED, byte-frozen, unmodified):
  `experiments/SYK_CORRIDOR_PREREG_v2.md`
  sha256 `7cdd8cfe6e902b3b27199b40bc63546f94551cab1a52c339343d6059816c7a5c` (measured at run time)
- runtime, byte-unchanged and verified pre- AND post-run against the contract pin:
  `experiments/syk_corridor/pipeline.py`
  measured sha256 `f5ad157c871a061a7244ed3767b9abe0affa034f1bdaac668343650a71c34511`,
  which **MATCHES the contract's runtime pin exactly** (both checks logged in
  `run_v2.log` and recorded in `results.json` wrapper_provenance)
- sole verdict bookkeeper (byte-frozen): `experiments/op179_nu_to_beta.py`
  sha256 `b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e` (MATCHES pin)
- wrapper: `experiments/syk_corridor_v2/run_v2.py` (hash verification + subprocess
  execution + output wrap only; no physics, no band arithmetic, no golden-ratio literals)
- raw outputs: `experiments/syk_corridor/results_v2.json` (the pinned output path the
  contract names) and `experiments/syk_corridor_v2/results.json` (same content wrapped
  with provenance); log: `experiments/syk_corridor_v2/run_v2.log`
- date_utc: 2026-08-01T22:33:22Z (wall time 2420.9 s)
- grid as run (all pinned values obeyed exactly): official N in {14, 18, 22}; N = 10
  telemetry only (fit ban CARRIED — no N = 10 number entered any fit or bucket); seeds
  5000–5039 inclusive, 40 per (N, kappa) point; the v2 kappa grid
  [0, 1.00, 1.25, 1.57, 1.98, 2.48, 3.11, 3.90, 4.90, 6.15, 7.71, 9.68, 12.15, 15.24,
  19.13, 24.00]; bootstrap 2000 resamples everywhere; nu search interval [0.30, 1.50].
- route: **direct-beta PRIMARY** (contract section 5 carrying v1 3.1), under the
  section 1 resolved d convention (d = sector Hilbert dimension, 2^(N/2 - 1)). The
  nu-route stayed CLOSED: the `ChannelExponentAssignment` port was never filled,
  `nu_to_beta_verdict` was never called, `m1_quotient_confirmation_flag` was never
  called. Collapse-nu below is telemetry only.

## 1. Discriminator gate (contract section 2) — status at run time

The contract self-classified the corridor as **discriminating** at signing: under the
resolved d convention the generic GUE / Fermi-golden-rule standard answer lies outside
both pass bands (its laptop anchor: intercept 2.776, 95% CI [1.902, 3.620], entirely
above the B1/B2 pass ceiling 1.618034). The contract therefore did NOT self-limit to
pipeline-validation-only language, and its section 6 spend gate (c) is discharged. This
run reproduces that anchor exactly (determinism disclosed in the contract's section 2
honesty note 2). Venue, not the discriminator, is what keeps THIS run at
pipeline-validation status.

## 2. Primary result — direct-beta at kappa = 0, pinned sector-d convention

Measured Gamma (disorder-averaged over the 40 pinned seeds):

| N | d_sector | Gamma |
|---|---|---|
| 10 (telemetry) | 16 | 4.340e-4 |
| 14 | 64 | 4.770e-5 |
| 18 | 256 | 4.509e-6 |
| 22 | 1024 | 3.164e-7 |

Fits per the pinned protocol (pairwise log-log slopes at pair midpoints, primary linear
fit in 1/N to the intercept, bootstrap 2000 resamples, 0 invalid):

| lane | beta pairs (mid-N 16, 20) | pooled slope | **beta intercept (1/N to 0)** | 95% CI |
|---|---|---|---|---|
| **PINNED v2: d = sector Hilbert dim** | 1.7016, 1.9166 | 1.809 | **2.776** | [1.902, 3.620] |
| SUPERSEDED diagnostic: d ~ 2^N | 0.8508, 0.9583 | 0.905 | 1.388 | [0.951, 1.810] |

op179 buckets, mechanical output of the byte-frozen bookkeeper (PIPELINE-VALIDATION
output, not a certified verdict):

- **PINNED convention (kappa = 0): point rule OUTSIDE; CI rule UNCLASSIFIED_BY_RULE**
  (the CI [1.902, 3.620] straddles the kill window K = [1.95, 2.05] without lying
  inside it and without touching B1). Per the signed precedence the CI rule governs
  when a CI exists: **Kill Condition 9 does not fire**, and nothing passes.
- SUPERSEDED diagnostic (kappa = 0): point rule IN_BAND; CI rule BOUNDARY_REGION —
  retained only so the effect of the section 1 erratum stays visible; this lane
  decides nothing.

Physics reading, validation-grade only: at kappa = 0 the system IS the generic-GUE
standard null; the sector-d pairwise slopes climb 1.70 to 1.92 toward the golden-rule
value 2 exactly as RMT predicts, and the 1/N intercept overshoots to 2.776 through the
slowly varying many-body bandwidth at small d (all disclosed in the contract's
section 2). The pipeline reproduces known physics where known physics is the answer.

## 3. Crossing-adjacent column (contract section 4 operative reading)

The collapse fit produced kappa_c = 16.46 with 13 deformed grid points below and 2
above — the mechanical bracketing rule ("strictly interior with at least two grid
points on each side") is **satisfied**, so the crossing-adjacent column at the nearest
grid point kappa = 15.24 was produced as pinned:

| lane | beta intercept | 95% CI | point bucket | CI bucket |
|---|---|---|---|---|
| PINNED sector-d | 2.618 | [-1.152, 6.472] | BOUNDARY | BOUNDARY_REGION |
| SUPERSEDED 2^N | 1.309 | [-0.576, 3.236] | IN_BAND | BOUNDARY_REGION |

The CI spanning roughly [-1.2, 6.5] carries no discriminating content; it is telemetry
adjacent to the primary column, reported as pinned. (beta(kappa) point telemetry across
the grid: 2.78 to 2.67 at the ends under the pinned convention, with unstable
ramp-window fits — including negative slopes — in the crossover region
kappa = 1.98 to 3.90, where the SFF is not GUE-shaped. Telemetry only; enters nothing.)

## 4. nu telemetry lane — DEGENERATE by the contract's own mechanical rules

| check | pinned rule | result | outcome |
|---|---|---|---|
| crossing bracket | kappa_c strictly interior, >= 2 grid pts each side | kappa_c = 16.46: 13 below, 2 above | PASS (not void) |
| bootstrap non-degeneracy | nu in (0.30, 1.50) interior; <= 5% edge mass | fitted nu = 1.50 = search CEILING; **99.8%** of 2000 resamples in the highest grid cell; nu CI [1.50, 1.50] | **DEGENERATE — not certifiable** (carried v1 section 2) |
| per-size collapse R^2 | >= 0.98 | 0.830 / 0.972 / 0.925 | FAIL |
| cross-size correlation | >= 0.99 | 0.971 / 0.957 / 0.997 | FAIL |

Note the mirror image of the v1 laptop run: under the v1 grid nu pegged at the search
FLOOR (0.30, 100% low-edge mass); under the v2 re-derived grid it pegs at the CEILING
(1.50, 99.8% high-edge mass). The re-derived grid fixed the bracketing void (blocker
(b) as scoped), but the collapse itself still fails the pinned quality gates. No nu
number here entered any bucket, verdict, or gate, and none may.

## 5. Certification gate roll-up (from results_v2.json)

| gate | state |
|---|---|
| venue is Nebius | NO (laptop) |
| crossing bracketing | PASS |
| nu bootstrap non-degenerate | **FAIL (99.8% edge mass at search ceiling)** |
| collapse R^2 >= 0.98 | FAIL |
| cross-size corr >= 0.99 | FAIL |
| Gamma operationalization source-pinned | YES (contract section 4) |
| **CERTIFIED VERDICT** | **NO — PIPELINE-VALIDATION ONLY** |

## 6. Is the Nebius extension authorized by the contract's own terms?

Stated mechanically, in three parts:

1. **Discriminator authorization: YES.** Section 2's gate passed at signing (standard
   answer outside both pass bands), so section 6(c) is discharged and Nebius spend is
   PERMITTED by the contract — this corridor is not in the
   pipeline-validation-language-only, zero-spend branch.
2. **But a v2-pinned Nebius run cannot certify.** Section 6(d) requires executing the
   byte-pinned pipeline unchanged. That pipeline is deterministic in (N, kappa, seed)
   and uses a fixed bootstrap generator, and this run shows its certification gates
   (nu non-degeneracy, collapse R^2, cross-size correlation) **fail deterministically**
   on the pinned grid and seeds. A Nebius execution would flip only the venue gate and
   reproduce the other failures (floating-point library differences cannot plausibly
   move 99.8% edge mass under 5% or R^2 = 0.83 above 0.98), yielding
   CERTIFIED_VERDICT = false at cloud prices. Spending against a mechanically
   foreknown non-certifiable outcome buys venue provenance for a run that still cannot
   issue a certified verdict. Additionally, section 6(a) is not yet fully discharged:
   the v2 contract and pipeline SHA-256s are not yet recorded in a RESEARCH_LEDGER.md
   row (they are recorded in results.json and here).
3. **Bigger N is NOT authorized by v2.** The official-size pin (v1 section 1, carried
   by section 5: fits use N in {14, 18, 22} only) and the byte-pin of the pipeline
   (which hardcodes those sizes) mean an extrapolation extended to larger N is outside
   this contract. Per the contract's own idiom ("a widened grid is a new timestamped
   preregistration"), an N-extended corridor — which is also what could cure the
   degenerate collapse and the small-d overshoot in the beta intercept — requires a
   new signed prereg (v3) before any spend.

**Bottom line: zero Nebius spend is the correct action under the contract as signed.**
Not because the discriminator failed (it passed), but because the certified run's
remaining gates are already known to fail on the pinned grid/seeds, and the scientifically
useful extension (larger N) is outside the v2 pins. Recommendation recorded for the
owner: a v3 prereg that (i) keeps the section 1 d-convention erratum and the section 4
Gamma pinning, (ii) re-scopes or drops the nu-collapse certification gates (the
direct-beta primary route never needed them), and (iii) pins an N-extended size ladder
with a venue budget, would make the first paid run capable of certifying.

## 7. No-upgrade sentences (contract section 7, verbatim, in force)

Until every gate above is discharged and the run completes under this signed protocol, no
SYK number may be reported as GHP support in either direction. An in-band result under a
pinned conversion whose standard-null placement was not first audited is not a pass; it is a
protocol violation. A kill closes Module C's strong claim, not GHP's architectural layer
(master §5.10A.4 survival table). A quotient-confirmation is a demotion, not a victory.
Software echoes may inform the theory; they do not confirm the physics.
