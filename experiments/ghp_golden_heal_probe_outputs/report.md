# GOLDEN-HEAL-v1 — recoverability discriminator (GHP Test #1)

**Classification: OUTCOME C — MECHANISM-NULL**

> Lane: engineering / verified-computation. **NOT physics evidence.** GOLDEN-HEAL is a toy least-squares recoverability probe; no outcome here is physics evidence, and Outcome B (the expected result) is a statement about low-discrepancy geometry, not about phi being physically privileged.

## Ranking by recovery-AUR (pooled across modes)

| rank | arm | pooled mean AUR |
|---|---|---|
| 1 | random_irrational | 0.6996 |
| 2 | golden | 0.6996 |
| 3 | bronze | 0.6996 |
| 4 | silver | 0.6996 |
| 5 | random_positions | 0.6996 |
| 6 | rational_near | 0.1688 |
| 7 | rational_resonant | 0.0205 |

## Regime diagnostic (read the verdict WITH this)

- band unknowns 2K = **32**; minimum survivors at max locked damage (0.8) = **102**.
- under-determined regime reached at any grid point: **False**.
- Locked N=512/K=16/damage<=0.8 keeps survivors (min ~102) far above 2K=32 at every grid point, so the coverage-stressed regime where three-distance geometry could separate the irrational arms is NEVER entered. Any irrational rotation (and even uniform-random positions) reconstructs the K=16 band near-perfectly; the rational arms fail only because a rational rotation visits a finite point set (rank-deficient design), independent of damage. The Outcome-C reading below is therefore faithful to the locked contract but UNDERPOWERED by construction for the golden-vs-silver question.

## Golden-vs-silver (the ONLY place a phi claim can live)

| mode | mean gap (G-S) | sigma_between | golden wins | sign-test p | resolvable? |
|---|---|---|---|---|---|
| contiguous | +0.0000 | 0.0000 | 8/12 | 0.388 | no |
| random | +0.0000 | 0.0000 | 8/12 | 0.388 | no |

## Per-mode AUR (mean across 12 seeds)

| arm | contiguous | random |
|---|---|---|
| golden | 0.6996 | 0.6996 |
| silver | 0.6996 | 0.6996 |
| bronze | 0.6996 | 0.6996 |
| rational_near | 0.1688 | 0.1688 |
| rational_resonant | 0.0205 | 0.0205 |
| random_irrational | 0.6996 | 0.6996 |
| random_positions | 0.6996 | 0.6996 |

## Verdict logic (locked thresholds)

### mode: contiguous
- cond1 golden>silver in >=8/12 seeds: **True** (8/12)
- cond2 mean gap > sigma_between: **False** (+0.0000 vs 0.0000)
- cond3 sign-test p<0.05: **False** (p=0.388)
- cond4 ordering intact: **False**
- PASS-A this mode: **False**
- B: all champions beat floors: **False**
- C: golden - random_positions = +0.0000 (<= 0.02 => null: True)

### mode: random
- cond1 golden>silver in >=8/12 seeds: **True** (8/12)
- cond2 mean gap > sigma_between: **False** (+0.0000 vs 0.0000)
- cond3 sign-test p<0.05: **False** (p=0.388)
- cond4 ordering intact: **False**
- PASS-A this mode: **False**
- B: all champions beat floors: **False**
- C: golden - random_positions = +0.0000 (<= 0.02 => null: True)

**PASS-A (both modes): False** | **CONFIRM-B: False** | **CONFIRM-C: True**

## GH-B — Fibonacci-convergent oscillation (EXPLORATORY, cannot pass/kill)

Golden reference AUR (pooled): contiguous=0.6996, random=0.6996

| n | F(n+1)/F(n) | side of phi | AUR contig | AUR random | AUR-side (contig) |
|---|---|---|---|---|---|
| 2 | 1.500000 | below | 0.0205 | 0.0205 | below |
| 3 | 1.666667 | above | 0.0310 | 0.0310 | below |
| 4 | 1.600000 | below | 0.0507 | 0.0507 | below |
| 5 | 1.625000 | above | 0.1013 | 0.1013 | below |
| 6 | 1.615385 | below | 0.1688 | 0.1688 | below |
| 7 | 1.619048 | above | 0.2987 | 0.2987 | below |
| 8 | 1.617647 | below | 0.6997 | 0.6984 | above |
| 9 | 1.618182 | above | 0.6996 | 0.6996 | below |
| 10 | 1.617978 | below | 0.6996 | 0.6996 | above |
| 11 | 1.618056 | above | 0.6996 | 0.6996 | above |
| 12 | 1.618026 | below | 0.6996 | 0.6996 | above |
| 13 | 1.618037 | above | 0.6996 | 0.6996 | above |

Alternation score (fraction of consecutive AUR-side flips): contiguous=0.27, random=0.45. DESCRIPTIVE ONLY. Cannot trigger pass or kill. High alternation score (~1.0) would suggest AUR(convergent) oscillates above/below AUR(golden) tracking the odd/even convergent bracket.

## Numerology guard

- phi-free audit of signal/metric functions: **PASSED** (runtime grep found no phi/1.618/golden/fibonacci token).
- phi enters ONLY as one rotation angle among the arms.
- Outcome-A pass region EXCLUDES the silver-tie region by construction: content lives only in golden-vs-silver; within-sigma_between => TIE => Outcome B.
- A win over rational/random alone earns NO phi claim (textbook low-discrepancy).
