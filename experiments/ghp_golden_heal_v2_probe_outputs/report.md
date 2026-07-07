# GOLDEN-HEAL-v2 — coverage-stressed recoverability discriminator

**Classification: OUTCOME B — IRRATIONALITY-GENERIC (expected result)**

> Lane: engineering / verified-computation. **NOT physics evidence.** GOLDEN-HEAL v2 is a toy least-squares recoverability probe in a coverage-stressed regime; no outcome here is physics evidence. Outcome B (the expected result) is a statement about low-discrepancy geometry, not about phi being physically privileged, and even Outcome A would be a numerical-linear-algebra fingerprint requiring independent replication before any ledger upgrade beyond 'toy anomaly.'

## v1 verdict (STANDS — required citation, retro-tune guard)

GOLDEN-HEAL-v1 (GOLDEN_HEAL_PREREG_v1.md + ghp_golden_heal_probe.py) returned C_MECHANISM_NULL under its locked contract; that verdict STANDS and is not corrected or overturned by v2. v1 diagnosis: minimum survivors ~102 >> 2K=32 kept the system over-determined everywhere; all irrational/aperiodic arms tied at ceiling ~0.6996 (~1e-5 seed noise; random_irrational edged golden); rational arms collapsed by rank deficiency. GH-B monotone finding also stands. v2 is a NEW timestamped contract (GOLDEN_HEAL_PREREG_v2.md) testing the same mechanism in the coverage-stressed regime; it does not correct or overturn v1 — v1 answered its own contract correctly.

## Regime (the point of v2)

| d | survivors | vs 2K = 64 |
|---|---|---|
| 0.60 | 102 | over-determined |
| 0.70 | 77 | over-determined |
| 0.75 | 64 | EXACTLY determined **<- critical band** |
| 0.80 | 51 | UNDER-determined **<- critical band** |
| 0.85 | 38 | UNDER-determined **<- critical band** |
| 0.90 | 26 | UNDER-determined |

- v2 enters the coverage-stressed regime v1 never reached: exactly-determined at d=0.75 (64 = 2K) and under-determined at d >= 0.80. UNDERDETERMINED points are minimum-norm lstsq, logged and still scored, per the locked contract.

## Primary metric — critical-band CB ranking (pooled contiguous + adversarial modes)

| rank | arm | mean CB |
|---|---|---|
| 1 | silver | 0.5698 |
| 2 | bronze | 0.4788 |
| 3 | golden | 0.4322 |
| 4 | random_irrational | 0.4112 |
| 5 | rational_near | 0.3180 |
| 6 | random_positions | 0.0906 |
| 7 | rational_resonant | 0.0000 |

## Mean CB per mode (16 seeds)

| arm | contiguous | adversarial | random (descriptive) |
|---|---|---|---|
| golden | 0.6389 | 0.2254 | 0.2765 |
| silver | 0.6436 | 0.4959 | 0.2581 |
| bronze | 0.6386 | 0.3189 | 0.2408 |
| rational_near | 0.4191 | 0.2170 | 0.2557 |
| rational_resonant | 0.0000 | 0.0000 | 0.2843 |
| random_irrational | 0.5789 | 0.2435 | 0.2376 |
| random_positions | 0.1812 | 0.0000 | 0.2698 |

## Golden-vs-silver on CB (the ONLY place a phi claim can live)

| mode | mean gap (G-S) | sigma_between | golden wins | one-sided p | silver step (A1-A3)? |
|---|---|---|---|---|---|
| contiguous | -0.0046 | 0.0485 | 9/16 | 0.4018 | fail |
| adversarial | -0.2705 | 0.0539 | 0/16 | 1.0000 | fail |

## Verdict logic (locked thresholds, precedence A -> B -> C -> WATCH)

### mode: contiguous
- A1 golden>silver in >=12/16 seeds: **False** (9/16)
- A2 mean gap > sigma_between: **False** (-0.0046 vs 0.0485)
- A3 one-sided sign test p<0.05: **False** (p=0.4018)
- A4 ordering sane: **True**
- PASS-A this mode: **False**
- B floor checks (need mean gap >= 0.05 AND >= 12/16 wins):
  - golden_vs_rational_resonant: mean_gap=+0.6389, wins=16/16 -> ok
  - golden_vs_random_positions: mean_gap=+0.4577, wins=16/16 -> ok
  - silver_vs_rational_resonant: mean_gap=+0.6436, wins=16/16 -> ok
  - silver_vs_random_positions: mean_gap=+0.4624, wins=16/16 -> ok
  - bronze_vs_rational_resonant: mean_gap=+0.6386, wins=16/16 -> ok
  - bronze_vs_random_positions: mean_gap=+0.4574, wins=16/16 -> ok
- B all floors ok this mode: **True**

### mode: adversarial
- A1 golden>silver in >=12/16 seeds: **False** (0/16)
- A2 mean gap > sigma_between: **False** (-0.2705 vs 0.0539)
- A3 one-sided sign test p<0.05: **False** (p=1.0000)
- A4 ordering sane: **False**
- PASS-A this mode: **False**
- B floor checks (need mean gap >= 0.05 AND >= 12/16 wins):
  - golden_vs_rational_resonant: mean_gap=+0.2254, wins=16/16 -> ok
  - golden_vs_random_positions: mean_gap=+0.2254, wins=16/16 -> ok
  - silver_vs_rational_resonant: mean_gap=+0.4959, wins=16/16 -> ok
  - silver_vs_random_positions: mean_gap=+0.4959, wins=16/16 -> ok
  - bronze_vs_rational_resonant: mean_gap=+0.3189, wins=16/16 -> ok
  - bronze_vs_random_positions: mean_gap=+0.3189, wins=16/16 -> ok
- B all floors ok this mode: **True**

- **PASS-A (both modes): False**
- Silver step (A1-A3) both modes: False
- **B floors both modes: True**
- **C pooled mean(CB_golden - CB_random_positions) over 32 paired values: +0.3416 (<= 0.05 => C: False)**
- **VERDICT: B_IRRATIONALITY_GENERIC**

## Adversarial mode — worst-block anatomy

(mean over 16 seeds; 'catastrophe depth' = mean-over-all-256-starts minus worst-case, i.e. how much a schedule's WORST block underperforms its typical block)

| arm | d=0.60 worst / depth | d=0.70 worst / depth | d=0.75 worst / depth | d=0.80 worst / depth | d=0.85 worst / depth | d=0.90 worst / depth |
|---|---|---|---|---|---|---|
| golden | 0.998 / 0.000 | 0.997 / 0.001 | 0.086 / 0.896 | 0.372 / 0.180 | 0.218 / 0.145 | 0.109 / 0.121 |
| silver | 0.999 / 0.000 | 0.997 / 0.001 | 0.875 / 0.118 | 0.382 / 0.174 | 0.230 / 0.137 | 0.117 / 0.115 |
| bronze | 0.998 / 0.000 | 0.998 / 0.001 | 0.367 / 0.613 | 0.372 / 0.189 | 0.218 / 0.152 | 0.115 / 0.120 |
| rational_near | 0.943 / 0.027 | 0.640 / 0.198 | 0.000 / 0.292 | 0.406 / 0.146 | 0.245 / 0.121 | 0.144 / 0.088 |
| rational_resonant | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| random_irrational | 0.998 / 0.001 | 0.931 / 0.060 | 0.161 / 0.603 | 0.344 / 0.207 | 0.225 / 0.138 | 0.124 / 0.107 |
| random_positions | 0.390 / 0.537 | 0.000 / 0.379 | 0.000 / 0.003 | 0.000 / 0.211 | 0.000 / 0.281 | 0.028 / 0.189 |

## Mode 3 — random erasure (descriptive ONLY, no verdict weight)

- golden - silver mean CB gap: +0.0184 (10/16 golden wins); direction REVERSED vs the contiguous mode (flagged as caveat only).

## Secondary metric — AUR (descriptive, no verdict weight)

| arm | contiguous | adversarial | random |
|---|---|---|---|
| golden | 0.2261 | 0.1612 | 0.1543 |
| silver | 0.2274 | 0.2020 | 0.1511 |
| bronze | 0.2266 | 0.1754 | 0.1520 |
| rational_near | 0.1800 | 0.1313 | 0.1478 |
| rational_resonant | 0.0000 | 0.0000 | 0.1507 |
| random_irrational | 0.2170 | 0.1594 | 0.1592 |
| random_positions | 0.1122 | 0.0202 | 0.1546 |

## Grid snapping — collision rates (per arm, over 16 seeds)

| arm | mean collisions | min | max |
|---|---|---|---|
| golden | 40.0 | 40 | 40 |
| silver | 42.0 | 42 | 42 |
| bronze | 70.0 | 70 | 70 |
| rational_near | 243.0 | 243 | 243 |
| rational_resonant | 254.0 | 254 | 254 |
| random_irrational | 94.2 | 21 | 220 |
| random_positions | 126.8 | 113 | 139 |

## Numerology guard

- AST audit of signal/damage/metric code paths: **PASSED** (10 functions: build_signal_coeffs, grid_design_matrix, snap_to_slots, recover_and_score, block_start, random_erase_mask, critical_band_mean, aur_trapz, one_sided_sign_p, run_arm_seed).
- phi enters ONLY as pinned rotation angles (rational_near = 8/13 is an arm definition, not machinery).
- Seed list 9001..9016 — phi-digit strings removed (v1 had 1618/6180/1123/5813).
- A pass-region EXCLUDES the silver tie by construction; a win over rational/random alone is textbook low-discrepancy = Outcome B, never a phi claim.
- Rational-arm collapse is pre-disclosed (v1: literal rank deficiency; v2 grid-snapped analogue: catastrophic coverage holes under contiguous damage) and carries no evidential weight.
- Regime-hunt closure clause: not triggered (verdict != C).

_Runtime: 80.7s. Deterministic: python3 + numpy, all substreams seeded from the frozen seed list._
