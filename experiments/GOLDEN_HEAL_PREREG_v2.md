# Preregistration — GOLDEN-HEAL v2 (the coverage-stressed recoverability discriminator)

- test_id: GOLDEN-HEAL-v2
- ledger_anchor: AH.4 Priority 1 (GHP Test #1), second and FINAL contract on the recoverability mechanism. Downstream of GOLDEN-HEAL-v1 (`experiments/GOLDEN_HEAL_PREREG_v1.md`, verdict C_MECHANISM_NULL — stands, see Section 0), T-111/T-112 (phi sampler side lab), M-005 (metallic-recurrence genericity null). Related bridge object B-025.
- date_locked: 2026-07-03 (locked AFTER v1's audited run and verdict, BEFORE any v2 pipeline code has been executed; see Section 0.3 for why this is not a retro-tune).
- lane: engineering / verified-computation. **NOT physics evidence.** No result here proves GHP, observer-boundary selection, or a write-law (master hard rule 7: software/toy results are NEVER physics evidence). A phi win here would be a numerical-linear-algebra fingerprint of low-discrepancy geometry under coverage stress, nothing more — and even that must clear the silver-tie exclusion before it earns the word "phi-specific."
- runtime: Python 3.9.6 + numpy 2.0.2 / scipy 1.13.1, deterministic, offline. All randomness seeded; seed list frozen in Section 1.5.
- honest prior: **I expect Outcome B (irrationality-generic), even in this regime.** Theory says any golden-vs-silver separation will be SMALL: Weyl equidistribution makes ALL irrational rotations asymptotically uniform; star-discrepancy constants for golden vs silver rotations differ only by modest constant factors; the Markov/Lagrange spectrum separates golden (sqrt5 ≈ 2.236, Hurwitz-extremal) from silver (sqrt8 ≈ 2.828) by a constant-factor gap of order tens of percent in the extremality constant — and far less than that is expected to survive into recovery scores after least-squares conditioning washes through. T-112 ranked phi_inv 6th of 50; T-111 had sqrt2 slightly BEAT phi; M-005 established phi-content across the metallic family is extremality-only. Outcome B is the most likely result and is fully acceptable. The point of v2 is solely to give the mechanism its ONE fair shot in the regime where it could manifest at all.

---

## 0. v1 verdict and regime diagnostic — the disclosed justification for v2

### 0.1 v1 verdict (STANDS, untouched)

GOLDEN-HEAL-v1 (`experiments/GOLDEN_HEAL_PREREG_v1.md` + `experiments/ghp_golden_heal_probe.py`, outputs at `experiments/ghp_golden_heal_probe_outputs/`) returned **C_MECHANISM_NULL under its locked contract. That verdict STANDS under v1's contract and is not reopened, softened, or superseded by this document.** v1's contract is untouched; v2 is a new, separately timestamped contract with its own thresholds.

### 0.2 v1 regime diagnostic (disclosed in the v1 report, verifier-confirmed)

- With v1's locked N=512, K=16 (2K=32 unknowns) and max damage 0.8, the MINIMUM survivor count over the entire grid was **~102 >> 32**. The least-squares system stayed heavily over-determined at EVERY grid point.
- Consequence: ALL irrational/aperiodic arms — golden, silver, bronze, random_irrational, and even random_positions — tied at the recovery ceiling **~0.6996** with differences **~1e-5** (pure seed noise; random_irrational actually edged golden). The two rational arms collapsed for the trivial reason (finite orbit -> rank-deficient design matrix), independent of damage.
- The coverage-stressed regime, where three-distance geometry determines whether reconstruction is possible at all, was **NEVER entered**. v1 was therefore faithful to its contract but structurally incapable of resolving golden-vs-silver.
- **GH-B stands and is NOT rerun:** the Fibonacci-convergent approach to golden was found to be MONOTONE — driven by the rational-period -> aperiodic transition — NOT the odd/even convergent oscillation the collaborator's intuition predicted. That descriptive negative is settled and carries forward unchanged.

### 0.3 Why v2 is a legitimate new contract, not a retro-tune

v2 tests the SAME mechanism hypothesis as v1 (three-distance uniform coverage + Hurwitz/KAM anti-resonance -> golden heals best) in the regime where it could actually manifest: survivor counts comparable to and BELOW the information-theoretic floor 2K, where the geometry of WHICH samples survive decides solvability. The v2 parameters (N, K, damage grid) are derived from deterministic survivor-count arithmetic (N x (1-d) vs 2K), not from any v2 recovery data — no v2 pipeline code has been run at lock time. Nothing in v1's verdict logic is altered; v1's C verdict is cited in every v2 report.

**Regime-hunt closure clause (locked):** v2 is the ONE disclosed rerun in the coverage-stressed regime. If v2 also returns C_MECHANISM_NULL, the recoverability-mechanism line is CLOSED at the ledger level. No v3 with further parameter shifts may claim preregistered status on this hypothesis.

---

## 0.5 Pinned constants (locked BEFORE any run; identical alphas to v1)

Rotation constants (each used ONLY as a rotation angle alpha in p_i = frac(i * alpha); nothing phi-flavored enters the signal, damage model, or metric):

- phi    = (1+sqrt(5))/2   = 1.6180339887498949 ; alpha_golden = frac(phi) = 0.6180339887498949
- silver = 1+sqrt(2)       = 2.4142135623730951 ; alpha_silver = frac = 0.4142135623730951
- bronze = (3+sqrt(13))/2  = 3.3027756377319946 ; alpha_bronze = frac = 0.3027756377319946

Irrationality ordering (Lagrange/Markov spectrum; the predicted recovery ordering under H1): golden (sqrt5, Hurwitz-extremal) > silver (2*sqrt2) > bronze (sqrt13) > rational controls > random-positions.

ARMS (all 7 identical to v1; single parametrized generator, no per-arm special-casing):

- ARM golden            : alpha = alpha_golden
- ARM silver            : alpha = alpha_silver  <-- THE REIGNING CHAMPION TO BEAT (T-112: silver beat golden once; v1: statistical tie at ceiling). NOT a strawman.
- ARM bronze            : alpha = alpha_bronze
- ARM rational_near     : alpha = 8/13 = 0.6153846... (hardest rational, closest to golden; expected to trivially collapse via rank deficiency — disclosed, carries no evidential weight)
- ARM rational_resonant : alpha = 1/2 (maximally resonant rational control)
- ARM random_irrational : alpha freshly drawn per seed (uniform on (0,1), rejected if within 1e-3 of any pinned alpha or any low-order rational p/q, q<=20)
- ARM random_positions  : N uniform-random positions (seeded), no rotation structure — the low-discrepancy floor

ADVERSARIAL NOTE (locked, restated from v1): the scientifically meaningful comparison is golden-vs-silver. A win over rational/random alone is EXPECTED, is textbook low-discrepancy (Weyl / Koksma-Hlawka), and earns NO phi claim — that is Outcome B by definition.

---

## 1. Construction (frozen)

### 1.1 Signal (phi-free by construction)

- Domain [0,1), **N = 256** sample slots on a uniform index grid i = 0..N-1.
- Ground truth: real bandlimited signal f(x) = sum_{k=1..K} [ a_k cos(2 pi k x) + b_k sin(2 pi k x) ], **K = 32** modes -> **2K = 64 unknowns** (the information-theoretic floor).
- Coefficients a_k, b_k ~ N(0,1) per seed, coefficient vector L2-normalized. Same signal across all arms within a seed. **No golden ratio, no Fibonacci, no phi anywhere in the signal, the band K, the grid, or the coefficients.**

### 1.2 Sample layout per arm

- Rotation arms: p_i = frac(i * alpha), i = 0..N-1, mapped to nearest grid slot; collisions resolved next-free-slot (collision rate logged per arm).
- random_positions: N uniform draws (seeded), mapped to grid identically.
- Observation: y_i = f(p_i) + eta_i, eta_i ~ N(0, sigma^2), **sigma = 1e-3** (frozen, as v1). Noise drawn once per seed for all N slots from a seeded stream and sliced by survival — identical procedure every arm.

### 1.3 Damage grid (frozen — the regime-crossing core of v2)

- Damage fractions d in **{0.60, 0.70, 0.75, 0.80, 0.85, 0.90}** (6-point grid).
- Erased count n_erased = round(d * N) (standard rounding, frozen). Survivor counts |S| = N - n_erased:

  | d    | erased | survivors | vs 2K = 64            |
  |------|--------|-----------|------------------------|
  | 0.60 | 154    | **102**   | ~1.6x over-determined  |
  | 0.70 | 179    | **77**    | ~1.2x over-determined  |
  | 0.75 | 192    | **64**    | EXACTLY determined     |
  | 0.80 | 205    | **51**    | under-determined       |
  | 0.85 | 218    | **38**    | under-determined       |
  | 0.90 | 230    | **26**    | deeply under-determined|

  The grid crosses the critical line 2K = 64 by construction: from ~1.6x over-determined through exactly-determined (d = 0.75) into under-determined (d >= 0.80). This is the regime v1 never entered.

### 1.4 Damage modes (THREE, frozen)

1. **CONTIGUOUS random-start**: remove a wrap-around block of n_erased consecutive sample INDICES; block start seeded. (Note: for rotation arms the survivors of an index-contiguous block are themselves a run of consecutive orbit points — a three-distance set — so this mode probes exactly the coverage geometry the mechanism claims.)
2. **ADVERSARIAL contiguous**: for each (arm, d, seed), compute recovery for ALL N = 256 possible block start positions and take the **WORST-case (minimum) clipped recovery**. Fully deterministic given the arm/seed data; the identical exhaustive procedure runs for every arm — no cherry-picking is possible. This tests anti-resonance at its sharpest: a schedule with resonant holes has a catastrophic worst block; a golden schedule should not. The argmin start is logged per (arm, d, seed) for diagnostics.
3. **RANDOM erasure**: remove a uniformly-random n_erased-subset of indices (seeded).

### 1.5 Recovery metric and seeds (phi-free)

- Reconstruct f-hat by least squares on the surviving (p_i, y_i): 2K-column cos/sin design matrix, numpy.linalg.lstsq, **rcond = 1e-10** (frozen, as v1). In the under-determined regime (|S| < 2K) lstsq returns the **minimum-norm** solution — logged UNDERDETERMINED, still scored; that is the point of v2.
- recovery(d) = 1 - ||f-hat - f|| / ||f||, **clipped to [0,1]** for all aggregation (raw values also stored). The adversarial-mode minimum is taken over clipped values (the scored quantity).
- **PRIMARY metric — CRITICAL-BAND recovery (CB)**: per (arm, mode, seed), CB = mean of clipped recovery over d in **{0.75, 0.80, 0.85}** (survivors {64, 51, 38} — the exactly-determined point and the first two under-determined points, where geometry decides solvability). ALL verdicts run on CB.
- **SECONDARY metric — AUR**: trapezoidal area under the recovery curve over the full 6-point grid, per (arm, mode, seed). Reported descriptively; carries NO verdict weight (locked — one primary metric, no double-dipping).
- **SEEDS (frozen list of 16)**: [9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016]. Sixteen consecutive integers, chosen as transparently arbitrary. (v1's list contained phi/Fibonacci digit strings — 1618, 6180, 1123, 5813 — which, while semantically inert as RNG labels, invited digit numerology; v2 removes even that.) Everything seed-dependent (coefficients, noise, block start in mode 1, random subset in mode 3, random_irrational alpha, random_positions) derives deterministically from the seed via fixed substreams frozen in the probe code before first run.

---

## 2. Hypothesis (H1) and null (H0)

- **H0 (EXPECTED — Outcome B):** even under coverage stress, recovery is IRRATIONALITY-GENERIC: golden ~ silver ~ bronze, all > rational_resonant and random_positions. phi is the extremal anchor of the ordering, not resolvably better than silver.
- **H1 (the one fair shot — Outcome A):** in the critical band, where which samples survive determines solvability, golden's Hurwitz-extremal coverage yields a recovery advantage over silver that is resolvable across seeds in BOTH contiguous modes — including the adversarial mode, where an anti-resonant schedule should have no catastrophic worst block.

This remains a null-favoring prereg: prior GHP work (T-111, T-112, M-005, GOLDEN-HEAL-v1) says silver ties or beats golden. H1 must clear a high, silver-excluding bar.

---

## 3. THREE PREREGISTERED OUTCOMES + WATCH (numeric, locked — MUST NOT be adjusted after seeing data)

All criteria run on the **CB metric**. Definitions:

- gap_s = CB_golden(seed s) - CB_silver(seed s), computed per mode.
- sigma_between(mode) = sample std (ddof=1) of {gap_s} over the 16 seeds, per mode.
- Sign test: exact one-sided binomial, P(X >= wins | n=16, p=1/2) < 0.05 (direction golden > silver is prespecified; ties gap_s = 0 count AGAINST golden). Note >= 12/16 wins gives p = 0.0384, so criteria A1 and A3 are jointly satisfiable at exactly 12 wins.
- "Both contiguous modes" = mode 1 (random-start) AND mode 2 (adversarial), each evaluated independently. Mode 3 (random erasure) is reported descriptively for all outcomes and carries no verdict weight; any directional reversal there is flagged in the report as a caveat without altering the verdict.

**(A) A_STRONG_PHI — requires ALL of, in BOTH contiguous modes independently:**
1. CB_golden > CB_silver in **>= 12/16 seeds**; AND
2. mean gap **> sigma_between(mode)** (resolvable above between-seed noise); AND
3. exact one-sided sign test **p < 0.05**; AND
4. ordering sane: mean CB_golden >= mean CB_bronze, AND mean CB_golden > mean CB of EACH of rational_near, rational_resonant, random_irrational, random_positions. (A phi "win" that inverts the irrationality ordering is INVALID — flagged, not a pass.)

**(B) B_IRRATIONALITY_GENERIC — declared when:** A fails at the silver step (criterion 1, 2, or 3 in either contiguous mode), AND each of golden, silver, bronze beats BOTH rational_resonant AND random_positions on CB by **mean gap >= 0.05** with **>= 12/16 seed wins**, in BOTH contiguous modes independently. Reported plainly as "low-discrepancy / irrationality is what matters; phi is the extremal anchor, not a unique write-point." (If A fails ONLY at criterion 4 with 1–3 passing, that is not B — it is WATCH, flagged as an ordering anomaly.)

**(C) C_MECHANISM_NULL — declared when:** mean(CB_golden - CB_random_positions) pooled over both contiguous modes x 16 seeds (32 paired values) **<= 0.05**. Even under coverage stress, golden's schedule buys nothing over structureless random positions: the three-distance/KAM recoverability mechanism fails to manifest, and per Section 0.3 the line is CLOSED.

**WATCH / underpowered — declared when none of A, B, C is clean.** Evaluation precedence is locked: A, then B, then C, then WATCH. No ledger status change beyond "machinery ran, discriminator inconclusive." Do NOT promote.

**The A pass-region EXCLUDES the silver tie BY CONSTRUCTION.** If golden's CB advantage over silver is within sigma_between or fails the sign test in either contiguous mode, it is a TIE and (at best) Outcome B, full stop — regardless of how golden compares to rational/random. A win over rational/random alone is textbook low-discrepancy = Outcome B, never a phi claim.

All thresholds (12/16, sigma_between, one-sided p < 0.05, 0.05 CB margin, pooled 0.05 null margin, mode requirements, precedence order) are locked NOW.

---

## 4. Numerology guard (locked)

- **No phi, Fibonacci, 1.618..., sqrt(5)-derived, or convergent constant may appear anywhere in the code except the rotation-angle definitions** (alpha_golden and the pinned arm alphas, plus rational_near = 8/13 which is an ARM definition, not machinery). Signal, band K, grid N, noise, damage model, metric, thresholds, and seeds are all phi-free. **AST-auditable, as v1**: the probe ships the same automated audit — walk the AST of the signal/damage/metric code paths and assert no numeric literal within tolerance of phi, 1/phi, sqrt5, or any Fibonacci ratio appears outside the pinned-constants block.
- **Retro-tune guard:** v2 parameters were fixed from survivor-count arithmetic before any v2 code ran (Section 0.3). v1's verdict stands under v1's contract and must be cited in every v2 report. It is FORBIDDEN to describe v2 as "correcting" or "overturning" v1; v1 answered its own contract correctly.
- **CIRCULAR / forbidden:** citing Hurwitz 1891 extremality as if the RESULT proved it — it is an input. "Golden had the best gap structure" is definitional (three-distance theorem); only a resolvable RECOVERY advantage over silver counts.
- **INVALID:** tuning N, K, sigma, the damage grid, the critical band, the seed list, or any threshold after inspecting v2 results; different code paths per arm; letting UNDERDETERMINED points drive the verdict without logging; treating the adversarial minimum as anything but the locked min-over-all-256-starts; presenting any outcome as physics evidence for GHP.
- **Rational-arm collapse is not evidence:** rational_near and rational_resonant are expected to fail by rank deficiency exactly as in v1; their collapse is disclosed in advance and earns no one anything.
- Forbidden-upgrade sentence: "GOLDEN-HEAL v2 is a toy least-squares recoverability probe in a coverage-stressed regime; no outcome here is physics evidence. Outcome B (the expected result) is a statement about low-discrepancy geometry, not about phi being physically privileged, and even Outcome A would be a numerical-linear-algebra fingerprint requiring independent replication before any ledger upgrade beyond 'toy anomaly.'"

---

## 5. Runtime discipline (locked)

- Adversarial mode costs N = 256 reconstructions per (arm, d, seed): 7 arms x 6 d x 16 seeds x 256 starts = 172,032 lstsq solves of size at most 102 x 64. Budget: **total wall time under ~3 minutes**.
- Mandatory optimization: the full design matrix A (N x 2K), position vector, signal values, and noise vector are fixed per (arm, seed) — **precompute once per (arm, seed), then slice rows per survivor set** for every damage value, mode, and block start. No recomputation of trig inside the start loop.
- Outputs: `experiments/ghp_golden_heal_v2_probe_outputs/` (summary.json with full config echo, per-(arm,mode,seed) CB and AUR tables, adversarial argmin starts, collision rates, UNDERDETERMINED flags, verdict logic trace; report.md citing v1's verdict per Section 4).
- Probe file: `experiments/ghp_golden_heal_v2_probe.py`, written AFTER this prereg is committed, run ONCE against this contract.

---

## 6. Ledger link

Row AH.4 (Priority 1) in `GHP_RESEARCH_LEDGER.md`. Prereg artifact pinned at `experiments/GOLDEN_HEAL_PREREG_v2.md` (this file). v1 contract pinned at `experiments/GOLDEN_HEAL_PREREG_v1.md`; **v1's C_MECHANISM_NULL verdict stands under v1's contract** and both contracts are reported together. No ledger status may be upgraded before an audited run against this contract; "pre-registered" may not be claimed without this pinned path+version. Outcome B is the honest expected result; Outcome C closes the mechanism line permanently per Section 0.3.
