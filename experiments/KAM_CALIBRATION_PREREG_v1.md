# Preregistration — KAM-CALIBRATION v1 (the standard-map golden-torus test)

- test_id: KAM-CALIBRATION-v1
- ledger_anchor: CALIBRATION for GH-RECOV (ledger row GH-RECOV; master AH.4 Priority 1; GH-RECOV v1+v2 committed at `8a3c6ead0e056bd28737f4c5557f67233c82cfa7`). This is NOT a new GHP discriminator. It runs the KAM/anti-resonance MECHANISM that GH-RECOV's recovery task was a PROXY for, in that mechanism's native habitat (the Chirikov standard map), to reconcile GH-RECOV's silver-win against the textbook expectation that golden is the last torus to break. Related: M-005 (phi-content is extremality-only), GOLDEN-HEAL-v1/v2 prereg contracts.
- date_locked: 2026-07-03 (locked BEFORE any KAM-CALIBRATION pipeline code has been executed).
- lane: calibration / verified-computation confirming KNOWN physics (Greene 1979). **NOT GHP evidence under either outcome.** A golden win here CONFIRMS textbook KAM theory (Greene's residue criterion, K_c ~ 0.971635) exactly as an in-band DMRG result confirms known CFT — it is expected, it is not novel, and it may NOT be reported as GHP evidence. The entire scientific value is (a) the golden-vs-silver ordering and (b) the cross-check to GH-RECOV.
- runtime: Python 3 + numpy, deterministic, offline, target well under 3 minutes. Newton on periodic orbits up to period ~a few hundred; fixed convergent depth, fixed Newton tolerance, bisection on K.

---

## 0. Why this test exists (the honest scientific motive)

GOLDEN-HEAL v2 (ledger GH-RECOV) found, in a coverage-stressed reconstruction PROXY, that SILVER (1+sqrt2) heals from damage better than golden — critical-band ranking silver 0.570 > bronze 0.479 > golden 0.432 ~ random-irrational 0.411, and in the adversarial worst-case-block tear golden beat silver in 0/16 seeds (~5 sigma in silver's favor). That is a NULL against phi-specificity of recovery quality.

But GOLDEN-HEAL was built on a KAM/anti-resonance mechanism hypothesis: "phi is the last torus to break as perturbation rises, so a golden-spread code is the most damage-resistant." The recovery task was a PROXY for that KAM mechanism, not KAM itself. KAM-CALIBRATION runs the mechanism in its NATIVE habitat — the Chirikov standard map — where Greene (1979) established that the golden-mean invariant circle is the LAST to survive as the kick strength K rises, breaking at K_c ~ 0.971635 (Greene's constant).

**The calibration logic (both outcomes informative):**
- If golden IS the most robust torus here (highest K_c) but LOST the GOLDEN-HEAL recovery proxy, then **recovery-quality != torus-robustness**: the proxy did NOT capture the KAM mechanism, and GH-RECOV's silver-win says nothing about KAM. This RECONCILES the two results and sharpens what "recoverability" should have meant.
- If golden is NOT the most robust torus even in the standard map, then our entire KAM mechanism story is WRONG, and GH-RECOV's silver-win is the tip of a deeper misunderstanding that must be escalated.

---

## 1. Design (locked)

### 1.1 Map (phi-free by construction)

Chirikov standard map on the cylinder:

    p'     = p + K sin(theta)
    theta' = theta + p'        (mod 2pi)

**NO phi, no golden ratio, no Fibonacci, no sqrt5 appears anywhere in the map, the kick, or the K grid.** phi enters ONLY as a target rotation number of one arm, on identical footing with every other arm.

### 1.2 Arms (the rotation numbers tested, locked)

Each arm is a target rotation number omega, fed through the identical K_c estimator. Single parametrized code path; no per-arm special-casing.

- ARM golden        : omega_g = (sqrt5 - 1)/2 = 0.6180339887498949  — CF [0;1,1,1,1,...] (all-ones, Hurwitz-extremal). The predicted winner; textbook K_c ~ 0.9716.
- ARM silver        : omega_s = sqrt2 - 1     = 0.4142135623730951  — CF [0;2,2,2,2,...]. **THE GOLDEN-HEAL CHAMPION.** Silver beat golden in GH-RECOV; for the KAM mechanism story to hold, golden must beat silver HERE by a clear K_c margin.
- ARM bronze        : omega_b = (sqrt13 - 3)/2 = 0.3027756377319946 — CF [0;3,3,3,3,...].
- ARM noble_silver  : omega_n = eventually-all-ones noble control, CF [0;2,1,1,1,1,...] = (sqrt5 - 1)/2 shifted: value = 1/(2 + (1/phi... )) computed from its CF, a noble number NOT equal to golden. Tests whether robustness is the NOBLE TAIL (eventual all-ones) or phi SPECIFICALLY. Measured value pinned in Section 1.4.
- ARM rational      : omega_r = 2/3 = 0.6666666666666667 — finite CF [0;1,2]; a resonant rational, expected to have K_c ~ 0 (no invariant circle survives any finite kick because the orbit is periodic / resonant).
- ARM generic_irr   : omega_x = frac(ln 2) = 0.6931471805599453 — a generic irrational with unbounded CF partial quotients (well-approximable, far from noble). Expected to break at low K_c.

### 1.3 K_c estimation method (Greene's residue criterion — PREFERRED, locked)

For each arm omega, estimate K_c(omega) = the kick strength at which the invariant circle of rotation number omega is destroyed, via **Greene's residue criterion**:

1. Compute the continued-fraction convergents p_k/q_k of omega up to a fixed depth (frozen: convergents with denominator q_k up to a cap Q_max = 400; use all convergents with q_k <= Q_max, minimum 4 convergents).
2. For a given K, each convergent p_k/q_k labels a periodic orbit of period q_k (rotation number p_k/q_k). Find it by **Newton's method** on the q_k-fold iterate of the map, solving for a fixed point of the map^{q_k} with net theta-winding p_k * 2pi and net p-winding constrained by the periodicity. Fixed Newton tolerance (frozen: 1e-12 on the residual 2-norm), fixed max iterations (frozen: 60), seeded from the linear-in-K continuation / previous-K solution.
3. Compute the **residue** R_k = (2 - tr M_k)/4 of the linearized monodromy matrix M_k (the Jacobian of map^{q_k} at the periodic orbit).
4. **Greene's criterion:** the invariant circle of rotation number omega EXISTS iff the residue sequence {R_k} stays bounded and converges to a finite limit (~0.25 at criticality for the golden mean; more generally bounded and non-diverging); it is DESTROYED when R_k -> infinity (|R_k| grows without bound with k).
5. **Bisect on K** to find K_c(omega): the transition K at which the convergent-residue sequence flips from bounded (torus exists) to divergent (torus destroyed). Frozen bisection: K in [0, 3], tolerance 1e-4 in K, decision rule = "residue of the deepest available convergent (largest q_k <= Q_max) exceeds a fixed divergence threshold R_div = 1.0" (locked; R_div chosen well above the ~0.25 critical fixed point and below the runaway regime).

Deterministic. Fixed convergent depth (Q_max = 400), fixed Newton tolerance (1e-12), fixed bisection tolerance (1e-4), fixed R_div = 1.0. **K_c values are MEASURED by this procedure, never seeded or hardcoded.** The number 0.9716 (Greene's constant) is a PREDICTION to be recovered, NOT an input — it must not appear as a literal anywhere in the estimator.

Acceptable alternative (implementer's choice, must be justified in the report if used instead): a frequency-map / rotation-number-diffusion converse-KAM estimate — measure the drift of the numerically-computed rotation number of an orbit initialized near omega as K rises, and take K_c where the rotation number ceases to be locally constant (torus destroyed -> rotation number starts diffusing). If chosen, it must be equally deterministic, apply identically to all arms, and its parameters frozen before the run.

### 1.4 Pinned constants (measured/derived at lock time; used only as rotation-number targets)

- golden : omega_g = (sqrt5 - 1)/2   = 0.6180339887498949
- silver : omega_s = sqrt2 - 1        = 0.4142135623730951
- bronze : omega_b = (sqrt13 - 3)/2   = 0.3027756377319946
- noble_silver : omega_n from CF [0;2,1,1,1,...] = 0.5675918792439982 (value = 1/(2 + 1/phi); measured to be irrational, noble, and NOT equal to any other arm; final value recomputed from its CF in code, this literal is documentation only)
- rational : omega_r = 2/3             = 0.6666666666666667
- generic_irr : omega_x = frac(ln 2)   = 0.6931471805599453

All rotation-number targets are frozen NOW. The map and estimator contain no phi-flavored literal.

---

## 2. Preregistered prediction (locked)

**PRIMARY PREDICTION:** K_c(golden) is the **HIGHEST** of all arms (the golden torus is the most robust). Expected ordering:

    golden ~ noble_silver  >  silver  >  bronze  >  generic_irr  >>  rational (~0)

**Golden must specifically beat silver by a clear K_c margin** (silver won GH-RECOV; here silver must LOSE for the KAM mechanism story to hold).

Predicted anchor value: K_c(golden) ~ 0.9716 (Greene's constant) — recovered by measurement, NOT hardcoded. Its recovery within tolerance is itself a validity check on the estimator.

---

## 3. Three preregistered outcomes + validity gate (locked — MUST NOT be adjusted after seeing data)

Define margin_gs = K_c(golden) - K_c(silver). "Clear margin" is locked as **margin_gs >= 0.05** (well above the bisection tolerance 1e-4 and estimator noise).

**VALIDITY GATE (must pass or the whole run is void, not any outcome):** K_c(golden) must be recovered in the window **[0.95, 1.00]** (brackets Greene's 0.971635 with tolerance for the finite-Q_max, finite-bisection estimator), AND K_c(rational=2/3) must be **< 0.05** (a resonant rational supports no invariant circle at finite kick). If the estimator fails either sanity check, the run is VOID (estimator bug) — NOT a physics result; fix the estimator and rerun before reading any arm ordering.

**(A) PASS-KAM — declared when:** validity gate passes AND K_c(golden) is the strict maximum over all arms AND margin_gs >= 0.05 (golden clearly beats silver). This is the EXPECTED outcome. It CONFIRMS Greene 1979. **Interpretation:** recovery-quality != torus-robustness. The GOLDEN-HEAL recovery proxy did NOT capture the KAM mechanism, so GH-RECOV's silver-win says nothing about which torus is most robust. The two results are RECONCILED: golden is the most robust torus (KAM), silver is the best recovery code (a different, low-discrepancy property). **This is NOT GHP evidence** (see Section 4).

**(B) PARTIAL-NOBLE — declared when:** validity gate passes AND golden clearly beats silver (margin_gs >= 0.05) BUT noble_silver ties or exceeds golden (K_c(noble_silver) >= K_c(golden) - 0.05). **Interpretation:** robustness tracks the NOBLE TAIL (eventual all-ones CF), not phi UNIQUELY. Still reconciles against silver (golden beats the GH-RECOV champion), but sharpens that the operative property is nobility, consistent with M-005's extremality-only finding. Not GHP evidence.

**(C) FAIL-MECHANISM — declared when:** validity gate passes AND golden does NOT top silver (margin_gs < 0.05, i.e. golden ties or loses to silver on K_c). **Interpretation:** a REAL SURPRISE. If golden is not even the most robust torus in the standard map — the one setting where Greene established it should be — then our KAM/anti-resonance mechanism story is WRONG, and GH-RECOV's silver-win is the visible tip of a deeper misunderstanding. **ESCALATE**: re-examine the estimator against Greene 1979 line by line; if the estimator is sound and golden still loses, the mechanism narrative underpinning the whole GOLDEN-HEAL lane collapses and must be retracted from the master's KAM/Hurwitz lane.

Evaluation precedence is locked: VALIDITY GATE, then A, then B, then C.

---

## 4. Numerology / honesty guard (locked)

- **Golden is EXPECTED to win here (textbook Greene 1979).** A golden win is therefore **NOT a GHP result** and must NOT be reported as one. It is a calibration confirming known KAM physics, exactly as an in-band DMRG result confirms known CFT. Content lives ONLY in (a) the golden-vs-silver ordering and (b) the cross-check to GH-RECOV.
- **K_c values must be MEASURED, not seeded.** The literals 0.9716 / 0.971635 (Greene's constant) MUST NOT appear anywhere in the estimator or bisection code; they may appear only in this prereg and in the report as the PREDICTION being tested. AST-auditable: the probe ships an audit asserting no Greene-constant literal (0.9716 +/- 1e-3) and no phi/1-over-phi/sqrt5 literal appears in the map or estimator code paths (arms' rotation-number targets are the only permitted irrational-target literals, and they are recomputed from CF/closed form in code).
- **The map is phi-free.** phi enters only as one arm's target rotation number, on identical footing with silver, bronze, noble, rational, and generic-irrational arms. Same code path for every arm.
- **CIRCULAR / forbidden:** citing Greene 1979 as if this run PROVED it (Greene is the textbook input this run RECOVERS); calling a golden K_c-max "GHP evidence"; hardcoding 0.9716; claiming PASS-KAM says anything about GHP beyond reconciling GH-RECOV.
- **Cross-check to GH-RECOV is the deliverable, not a phi claim:** PASS-KAM means recovery-quality and torus-robustness are DIFFERENT properties — golden wins one (KAM robustness, textbook), silver wins the other (recovery, GH-RECOV). Neither makes phi physically privileged.
- Forbidden-upgrade sentence: "KAM-CALIBRATION v1 is a verified-computation calibration that recovers textbook KAM physics (Greene 1979); no outcome here is GHP evidence. A golden K_c-max is EXPECTED and confirms known physics — its only value is reconciling GH-RECOV's silver-win by showing recovery-quality and torus-robustness are distinct properties. Only outcome C (golden failing to top silver even in the standard map) would carry new weight, and it would be a NEGATIVE against our mechanism narrative, never a positive GHP claim."

---

## 5. Runtime discipline (locked)

- Newton on periodic orbits up to period q_k <= Q_max = 400, 6 arms x (convergents per arm ~4-10) x bisection depth (~15 halvings of [0,3] to 1e-4). Reuse previous-K / previous-convergent solution as Newton seed (continuation) to keep iterations low. Budget: total wall time under ~3 minutes.
- Outputs: `experiments/ghp_kam_calibration_probe_outputs/` (summary.json with full config echo, per-arm K_c, per-arm convergent list and residue-at-K_c trace, validity-gate results, verdict logic trace; report.md that (i) states the outcome, (ii) prints the golden-vs-silver margin, (iii) prints the explicit cross-check to GH-RECOV, and (iv) carries the Section 4 forbidden-upgrade sentence verbatim and cites the GH-RECOV ledger row).
- Probe file: `experiments/ghp_kam_calibration_probe.py`, written AFTER this prereg is committed, run ONCE against this contract.

---

## 6. Ledger link

Calibration for row GH-RECOV in `GHP_RESEARCH_LEDGER.md` (master AH.4 Priority 1). Prereg artifact pinned at `experiments/KAM_CALIBRATION_PREREG_v1.md` (this file). No ledger status may be upgraded on the basis of a golden win — a golden win confirms Greene 1979 and is not GHP evidence. The only ledger-relevant products are: (a) the golden-vs-silver K_c ordering, appended as a reconciliation note to GH-RECOV, and (b) an escalation flag if outcome C fires. "Pre-registered" may not be claimed without this pinned path+version.
