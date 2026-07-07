# Preregistration — GOLDEN-HEAL v1 (the recoverability discriminator)

- test_id: GOLDEN-HEAL-v1
- ledger_anchor: AH.4 Priority 1 (GHP Test #1). Sits downstream of T-111/T-112 (phi sampler side lab) and M-005 (metallic-recurrence genericity null). Related bridge object B-025 (Boundary Access Channel: access + recovery + redundancy).
- date_locked: 2026-07-03
- lane: engineering / verified-computation. **NOT physics evidence.** No result here proves GHP, observer-boundary selection, or a write-law (master hard rule 7: software/toy results are NEVER physics evidence). A phi win here would be a numerical-linear-algebra fingerprint of low-discrepancy geometry, nothing more — and even that must clear the silver-tie exclusion below before it earns the word "phi-specific."
- runtime: Python 3.9.6 + numpy 2.0.2 / scipy 1.13.1, deterministic, offline. All randomness seeded; seed list frozen below.
- honest prior: **I expect Outcome B (irrationality-generic).** T-112 already ranked phi_inv 6th of 50 and had sqrt2_rotation slightly BEAT phi on sampler friction (T-111). M-005 established that the surviving phi-content across the metallic family is extremality-via-Hurwitz only, not a unique mechanism. So the default, fully-acceptable result is golden ~ silver ~ bronze > rational > random, and it must be reported as that, NOT dressed up as a phi win.

---

## 0. Pinned constants (locked BEFORE any run)

Golden-angle / rotation constants (each used ONLY as a rotation angle alpha in x_i = (i * alpha) mod 1; nothing phi-flavored enters the signal or the metric):

- phi   = (1+sqrt(5))/2      = 1.6180339887498949 ; alpha_golden = frac(phi) = 1/phi = phi-1 = 0.6180339887498949
- silver = 1+sqrt(2)          = 2.4142135623730951 ; alpha_silver = frac = sqrt(2)-1 = 0.4142135623730951
- bronze = (3+sqrt(13))/2     = 3.3027756377319946 ; alpha_bronze = frac = 0.3027756377319946
- (Only the fractional part matters for an irrational rotation on the circle; frac(alpha) and alpha give the identical orbit. We pin frac for clarity.)

Irrationality ordering (Lagrange/Markov spectrum; the predicted recovery ordering under H1):
  golden (Lagrange const sqrt5, WORST-approximable, Hurwitz 1891 extremal)
  > silver (Lagrange 2*sqrt2)
  > bronze (Lagrange sqrt13)
  > rational controls (finite continued fraction; NOT irrational)
  > random-positions (no low-discrepancy structure at all).

CONTROLS (identical code path, single parametrized generator — no per-arm special-casing):
- ARM golden   : alpha = alpha_golden
- ARM silver   : alpha = alpha_silver   <-- THE REIGNING CHAMPION TO BEAT (T-112: silver beat golden once). This is NOT a strawman.
- ARM bronze   : alpha = alpha_bronze
- ARM rational_near : alpha = 8/13 = 0.6153846... (best low-order rational near alpha_golden; a Fibonacci convergent F7/F8-adjacent — deliberately the HARDEST rational, closest to golden, so a golden win here cannot be dismissed as "any decent number beats a bad rational")
- ARM rational_resonant : alpha = 1/2 = 0.5 (deliberately resonant / maximally periodic-hole-prone rational control)
- ARM random_irrational : alpha = a freshly drawn irrational per seed (uniform on (0,1), rejected if within 1e-3 of any pinned alpha or a low-order rational p/q, q<=20) — controls for "is it just irrationality, any irrationality?"
- ARM random_positions : sample point positions uniformly at random on the index grid, NO rotation structure at all — the low-discrepancy floor.

ADVERSARIAL NOTE (locked): golden is the extremal irrational but silver and bronze are GENUINE low-discrepancy champions, not strawmen. The scientifically meaningful comparison is golden-vs-silver. A win over rational/random alone is EXPECTED and proves only "low-discrepancy helps," which is textbook (Weyl/Koksma-Hlawka) and earns NO phi claim.

---

## 1. Construction (frozen)

### 1.1 Signal (phi-free by construction)
- Domain: unit interval [0,1), N = 512 sample slots on a uniform index grid i = 0..N-1.
- Ground-truth signal: a known K-dimensional real bandlimited signal,
    f(x) = sum_{k=1..K} [ a_k cos(2 pi k x) + b_k sin(2 pi k x) ],  K = 16 (bandwidth frozen).
  Coefficients a_k, b_k drawn N(0,1) per seed, then the coefficient vector is L2-normalized so ||f|| is seed-independent. **No golden ratio, no Fibonacci, no phi anywhere in the signal, the band K, the grid, or the coefficients.**
- The signal is the SAME across all arms within a seed (identical a_k,b_k). Arms differ ONLY in which sample positions the rotation lays down and which survive damage.

### 1.2 Sample layout per arm
- For rotation arms: sample positions p_i = frac(i * alpha) for i = 0..N-1, i.e. the low-discrepancy sequence the arm's alpha generates. Map each p_i to the nearest grid slot; collisions resolved by next-free-slot (logged; collision rate reported per arm).
- For random_positions: p_i = N uniform draws (seeded), mapped to grid.
- Observation model: y_i = f(p_i) + eta,  eta ~ N(0, sigma^2), sigma frozen at 1e-3 (light noise so least-squares is well-posed but not trivially exact). Noise realization seeded and IDENTICAL across arms within a seed (so arms see the same noise on corresponding surviving samples where alignable; noise is re-drawn per surviving-sample set but from the same seeded stream).

### 1.3 Damage model (BOTH modes, frozen)
Two erasure modes, run independently:
- **CONTIGUOUS-in-index erasure**: remove a contiguous block of d*N consecutive sample INDICES (wrap-around block, block start seeded). This is the adversarial case for periodic schedules (a resonant hole wipes a coherent band).
- **RANDOM erasure**: remove a uniformly-random d*N subset of indices (seeded).
- Damage fractions d in {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8} (frozen 8-point grid).
- Surviving samples S = the un-erased (p_i, y_i) pairs.

### 1.4 Recovery metric (phi-free)
- Reconstruct f-hat by LEAST-SQUARES from the surviving samples S: solve the 2K-column design matrix (cos/sin up to k=K) against y over S; use numpy.linalg.lstsq (rcond frozen at 1e-10). Under-determined regime (|S| < 2K) is EXPECTED at high damage and handled by the minimum-norm lstsq solution (logged as UNDERDETERMINED, still scored — coverage of surviving fragment is exactly what the three-distance theorem is supposed to help).
- recovery(d) = 1 - ||f-hat - f|| / ||f||   (normalized reconstruction error; clipped to [0,1] for aggregation, raw value also stored).
- **AUR = area under the recovery curve** over the 8 damage fractions (trapezoidal), per arm, per erasure mode, per seed. This scalar AUR is the single primary quantity.
- SEEDS: frozen list of 12 seeds = [1618, 2718, 3141, 1414, 1732, 2236, 4142, 1123, 5813, 2971, 6180, 8090] (>= 10 required; 12 used). Everything seed-dependent (coefficients, noise, block start, random subset, random_irrational alpha, random_positions) derives deterministically from the seed.

---

## 2. Hypothesis (H1) and null (H0)

- **H0 (primary, EXPECTED — Outcome B):** recovery is IRRATIONALITY-GENERIC. golden ~ silver ~ bronze (mutually indistinguishable across seeds), all > rational_near > rational_resonant > random. phi is the extremal ANCHOR of the ordering but not resolvably better than silver. This matches T-111/T-112 and M-005 and is a fully reportable, non-disappointing result.
- **H1 (the interesting, harder claim — Outcome A):** golden is DISTINGUISHED — its AUR beats silver's by a margin resolvable across seeds, exceeding both between-seed noise and the section-4 threshold. This would be the first phi fingerprint that is not built-in, not definitional, not 2007-CFT — worth escalating.

This is deliberately a null-favoring prereg: prior GHP work says silver ties or beats golden. H1 must clear a high, silver-excluding bar.

---

## 3. THREE PREREGISTERED OUTCOMES (all honest, all reportable)

- **(A) STRONG phi-specificity** — golden's AUR beats silver's by a margin resolvable across seeds. Numeric: golden wins (AUR_golden > AUR_silver) in >= 8 of 12 seeds (both erasure modes must independently show >= 8/12), AND the mean AUR gap (AUR_golden - AUR_silver) exceeds the between-seed noise band (defined section 4). The anomaly worth escalating.
- **(B) IRRATIONALITY-GENERIC** (the EXPECTED null, fully acceptable) — golden ~ silver ~ bronze, all > rational > random. Report as "low-discrepancy / irrationality is what matters; phi is the extremal anchor, not a unique write-point," matching the program's phi-as-anti-locking-anchor finding. MUST NOT be dressed up as a phi win.
- **(C) MECHANISM-NULL** — golden is NOT better than rational/random (golden's AUR does not clear the rational_resonant or random arms by the section-4 low-discrepancy margin). Kills the recoverability mechanism itself; the three-distance/KAM story fails to manifest in this toy.

---

## 4. Kill-or-pass rule (NUMERIC, locked — MUST NOT be adjusted after seeing data)

Between-seed noise band: sigma_between = pooled std of per-seed (AUR_golden - AUR_silver) across the 12 seeds. "Resolvable" means |mean gap| > sigma_between (i.e. mean gap exceeds one between-seed standard deviation) AND a paired sign test on the 12 per-seed gaps rejects tie at p < 0.05 (>= 10/12 same-sign, or the exact binomial equivalent).

Compute per erasure mode (contiguous, random) SEPARATELY; a verdict requires the mode-consistency stated in each rule.

- **PASS-A (STRONG phi-specificity) — requires ALL of:**
  1. AUR_golden > AUR_silver in >= 8/12 seeds, in BOTH erasure modes independently; AND
  2. mean(AUR_golden - AUR_silver) > sigma_between (resolvable above between-seed noise), in BOTH modes; AND
  3. paired sign test rejects golden==silver tie at p < 0.05, in BOTH modes; AND
  4. golden also >= bronze and > all rational/random arms (ordering intact — a phi win that INVERTS the irrationality ordering is INVALID, flagged, not a pass).
- **CONFIRM-B (IRRATIONALITY-GENERIC, expected) — declared when:**
  - PASS-A fails at step 1, 2, or 3 (golden and silver indistinguishable) AND golden, silver, bronze all beat rational_resonant and random by the low-discrepancy margin below. This is a POSITIVE result about low-discrepancy, reported plainly.
- **CONFIRM-C (MECHANISM-NULL) — declared when:**
  - golden does NOT beat rational_resonant AND random by the low-discrepancy margin: mean(AUR_golden) - mean(AUR_random_positions) <= 0.02 (2% of the normalized recovery scale) pooled across seeds. The mechanism did not manifest.
- **Low-discrepancy margin (used in B and C):** an arm "beats" a floor arm iff mean AUR advantage >= 0.02 AND wins >= 9/12 seeds.
- **Decision when neither A nor B nor C is clean:** record as **WATCH / underpowered**; no ledger status change beyond "machinery ran, discriminator inconclusive." Do NOT promote.

All thresholds (8/12, sigma_between, p<0.05, 0.02 margin, 9/12) are locked NOW.

---

## 5. Numerology guard (locked)

- **The pass-region for Outcome A EXCLUDES the silver-tie region by construction.** Content lives ONLY in the golden-vs-silver comparison. If golden's advantage over silver is within sigma_between, it is a TIE and Outcome B, full stop — regardless of how golden compares to rational/random.
- **No phi constant may enter the signal, the band K, the grid, the coefficients, the noise, or the recovery metric.** phi appears ONLY as one rotation angle alpha_golden among the arms; everything else is identical across arms. (Auditable: a grep of the signal/metric code for phi/1.618/fibonacci must return nothing.)
- **A win over rational/random alone earns NO phi claim** — that is textbook low-discrepancy (Weyl equidistribution / Koksma-Hlawka), predicted for ALL the irrational arms, and is exactly Outcome B.
- **CIRCULAR / forbidden:** citing that golden is the worst-approximable irrational as if the RESULT proved it — Hurwitz 1891 is an input, not an output. Reporting "golden had the best gap structure" is definitional (three-distance theorem); only a resolvable RECOVERY advantage over silver counts.
- **INVALID:** tuning N, K, sigma, the damage grid, the seed list, or any threshold after inspecting results; using different code paths per arm; letting an UNDERDETERMINED point silently drive the verdict without logging; presenting any outcome as physics evidence for GHP.
- Forbidden-upgrade sentence: "GOLDEN-HEAL is a toy least-squares recoverability probe; no outcome here is physics evidence, and Outcome B (the expected result) is a statement about low-discrepancy geometry, not about phi being physically privileged."

---

## 6. Convergent-oscillation sub-probe GH-B (EXPLORATORY / DESCRIPTIVE — NOT a kill test)

Crediting the collaborator's intuition that phi is the "smoothest / uncatchable" anchor the Fibonacci convergents oscillate INTO:
- Run the same recovery pipeline with alpha = F(n+1)/F(n) for n = 2..13 (the Fibonacci convergents 3/2, 5/3, 8/5, 13/8, ... -> phi).
- These convergents alternate above/below phi (odd/even convergents bracket the limit). Descriptively test whether AUR(convergent_n) converges to AUR(golden) by OSCILLATING above and below it, matching the convergent bracket structure (odd convergents on one side, even on the other).
- This is reported as a DESCRIPTIVE curve + oscillation-sign table only. It CANNOT trigger a pass or kill. It is here to characterize the approach-to-limit texture, honoring the "convergents oscillate into the smoothest anchor" picture, without letting a suggestive oscillation become an evidence claim.

---

## 7. Ledger link

Row AH.4 (Priority 1) in `GHP_RESEARCH_LEDGER.md`. Prereg artifact pinned at `experiments/GOLDEN_HEAL_PREREG_v1.md` (this file). No ledger status may be upgraded before an audited run against this contract; per GHP discipline, "pre-registered" may not be claimed without this pinned path+version, and Outcome B is the honest expected result to report if the data lands there.
