# KAM-CALIBRATION-v1 — Chirikov standard-map golden-torus test

**Classification: FAIL_MECHANISM**

Preregistration: `experiments/KAM_CALIBRATION_PREREG_v1.md`. Cross-check ledger row: GH-RECOV (GOLDEN-HEAL v2).

## Method

Chirikov standard map on the cylinder, `p' = p + K sin(theta)`, `theta' = theta + p'` (mod 2pi) — **no phi in the map**. K_c(omega) measured by **Greene's residue criterion**: for each rotation number's continued-fraction convergents p_k/q_k, Newton-solve the period-q_k periodic orbit on the lift (net winding p_k), compute the residue R = (2 - tr M)/4 of its monodromy, and bisect K in [0,3] for the bounded->divergent transition. K_c is MEASURED; Greene's constant is never hardcoded.

## Measured K_c (descending)

| rank | arm | omega | K_c |
|---|---|---|---|
| 1 | noble_silver | 0.3819660113 | 0.972702 |
| 2 | golden | 0.6180339887 | 0.972336 |
| 3 | silver | 0.4142135624 | 0.957962 |
| 4 | bronze | 0.3027756377 | 0.902390 |
| 5 | generic_irr | 0.6931471806 | 0.886917 |
| 6 | rational | 0.6666666667 | 0.000000 |

## Validity gate

- K_c(golden) in [0.95,1.00]: **True** (got 0.972336)
- K_c(rational=2/3) < 0.05: **True** (got 0.000000)
- **Gate pass: True**

## Method-check (not a built-in)

Golden's measured K_c = **0.972336**. If the estimator is correct this should land near Greene's constant (~0.97). This is stated as a validation that the METHOD works, not a seeded input — 0.9716 appears nowhere in the estimator. Method-check PASSES.

## Golden vs silver

- K_c(golden) = 0.972336
- K_c(silver) = 0.957962
- margin_gs = K_c(golden) - K_c(silver) = **0.014374** (prereg requires >= 0.05 for a clear win)
- golden wins here: **True**

## Interpretation

FAIL-MECHANISM (per locked precedence: gate passed but margin_gs=0.0144 < 0.05). ESCALATE. Golden DOES edge silver (K_c golden=0.9723 vs silver=0.9580), but NOT by the preregistered clear margin of 0.05 — so the mechanism claim as stated ('phi is THE most robust torus, clearly beating silver') is NOT supported. The estimator is validated (gate passed; golden K_c=0.9723 recovers Greene's ~0.9716), so this is PHYSICS, not a bug. Structure observed: noble_silver K_c=0.9727 TIES/EXCEEDS golden=0.9723, and golden's cushion over silver is genuinely small (~0.014, consistent with the literature golden~0.9716 / silver~0.96). Reading: torus robustness is a NOBLE-TAIL property (golden and its noble cousin indistinguishable) rather than phi being uniquely and clearly dominant. This is the M-005 extremality-only picture, now visible even in the standard map. Action per prereg: re-audit estimator vs Greene 1979 (done — sound), then temper the master's KAM/Hurwitz-lane narrative: golden is top-tier but ties its noble cousin and only marginally exceeds silver; the '>= 0.05 clear win over silver' sub-claim is retracted. This is a NEGATIVE against the over-strong mechanism narrative, NEVER a positive GHP claim.

## Reconciliation with GH-RECOV

GH-RECOV (recovery PROXY): silver 0.570 > bronze 0.479 > golden 0.432 on critical-band recovery; golden lost the adversarial tear 0/16 seeds. HERE (KAM native, torus robustness): K_c(golden)=0.9723 vs K_c(silver)=0.9580; golden WINS here (margin_gs=0.0144). Golden edges silver here but only marginally (margin < 0.05, =0.0144) and TIES its noble cousin (noble_silver K_c=0.9727). So the direction still flips vs GH-RECOV (silver won recovery; golden nudges ahead on torus robustness), confirming recovery-quality and torus-robustness are DISTINCT properties -- but the standard map does NOT deliver a decisive golden-over-silver robustness win. The mechanism's strong form ('phi clearly the most robust') is not supported; robustness is a noble-TAIL property, golden not uniquely privileged. Reconciliation holds at the level of 'distinct properties'; the over-strong '>= 0.05 clear win' sub-claim is retracted (ESCALATE per prereg outcome C).

## Honesty guard

Golden is EXPECTED to win here (textbook Greene 1979) — a golden K_c-max CONFIRMS KNOWN KAM PHYSICS and is **NOT GHP evidence**, exactly as an in-band DMRG result confirms known CFT. Content lives ONLY in (a) the golden-vs-silver ordering and (b) the cross-check to GH-RECOV. K_c values were MEASURED, never seeded; the literal 0.9716/0.971635 is forbidden in the estimator and appears only as the prediction under test. The map is phi-free; phi enters only as one arm's target rotation number on identical footing with the others. Only outcome C (golden failing to top silver even here) would carry weight, and it would be a NEGATIVE against the mechanism narrative, never a positive GHP claim.

Runtime: 10.8 s.
