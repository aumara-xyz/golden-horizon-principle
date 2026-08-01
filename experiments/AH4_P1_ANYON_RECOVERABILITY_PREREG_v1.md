# Preregistration — AH.4-P1 v1 (the anyon fusion-tree recoverability discriminator)

- test_id: AH4-P1-ANYON-RECOV-v1
- ledger_anchor: ledger row **AH.4-P1** ("the one unbuilt experiment that can still discriminate"); master AH.4 Priority 1; bridge object **B-022** (holographic recoverability / QEC), whose closure condition the ledger names as AH.4-P1. Supersedes nothing: the two prior recoverability runs (**GH-RECOV** 2026-07-03, proxy, silver-optimal; **K-RECOV-001** 2026-07-19, external allocation replication, generic) are both **negative and retained**. This is the third and structurally different form.
- date_locked: **UNSET — this document is not locked.** See §0.1 for the exact protocol.
- lane: **GHP discriminator.** Unlike KAM-CALIBRATION (calibration lane, not GHP evidence under either outcome), this test is designed so that one outcome is genuine evidence for GHP's Layer-3 bet and another falsifies the recoverability lane outright.
- runtime: Python 3 + numpy, deterministic, offline. Fusion-tree dimension kept small enough to be exact (no Monte-Carlo state approximation); target under 30 minutes single-core.
- revision: amended 2026-07-29 after external review, before locking. Changes: design notation corrected to 4 × 4 (§1.1), the classical arm removed from the factorial and demoted to a separate floor (§1.2), the lock protocol made explicit (§0.1), the outcome and kill rules made executable (§2.2–§2.3), and a confound found by gate 1 recorded with the control it requires (§2.4).

---

## 0. Why this test exists, and why the previous two could not settle it

Two recoverability experiments have run. Both returned negative for φ-specificity, and **both varied the same axis.**

- **GH-RECOV** (2026-07-03) compared *allocation constants* — golden vs silver vs bronze spreading — inside a fixed, generic code structure. Silver won (0.570 > bronze 0.479 > golden 0.432; golden 0/16 on the adversarial tear).
- **K-RECOV-001** (2026-07-19, external lab) compared *allocation schemes* — golden vs silver vs bronze vs exp-2 vs greedy-rank vs uniform — again inside a fixed, generic allocation structure. Any heavy tail crushed uniform (+15 points at 75% erasure); golden was statistically indistinguishable from purpose-built greedy (+0.006, under the ±0.02 bar).

Both asked: **is the number φ special?** The answer came back no, twice, from two laboratories. That question is settled and is not re-asked here.

Neither asked: **is the fusion-tree structure special?** No Fibonacci anyon fusion tree has ever been built in this programme. The ledger says so explicitly, and the short paper's §8 names this as the only remaining form whose pass-region could exclude the generic answer.

This matters because it is the one place where GHP's own founding lesson — *architecture is not dynamics* (short paper §3) — makes a prediction that has never been tested on the architecture side. Five dynamical searches for φ returned generic, exactly as that lesson predicts. The lesson also predicts that a **structural** probe should behave differently. If it does not, the lesson stops being a prediction and becomes a hedge, and the recoverability lane closes for good.

### 0.1 Lock protocol (explicit, because the two categories differ)

**Verification gates are exempt from the pre-signing prohibition and must run first.**
`ah4_p1_pentagon_gate.py` (gate 0) and `ah4_p1_braid_gate.py` (gate 1) check published
mathematics, carry no free parameters, admit no researcher degrees of freedom, and
have outcomes that were known from the literature in advance. Their failure would
invalidate the design, so running them *before* signing is required rather than
merely permitted. Neither is evidence for or against GHP under any outcome.

**The recoverability experiment itself may not run before signing.** That prohibition
covers any code that produces a fidelity number: the encoder, the erasure model, the
recovery routine and the scorer. `date_locked` is set when the lane signs, and no
fidelity number computed before that date may be reported.

Current state: gates 0 and 1 have run and passed. No experiment code exists.

---

## 1. Design (to be locked)

### 1.1 The two factors, varied independently

The design is a **4 × 4 factorial: 16 cells**, four fusion categories crossed with
four allocation constants. The failure of the prior two experiments was that they
varied one factor and held the other fixed, on the factor now known to be inert.

**Factor A — STRUCTURE (the untested factor), 4 levels.** The fusion category the code is built from:

- `A_fib` — **Fibonacci** anyons. Fusion rule τ ⊗ τ = 1 ⊕ τ. The GHP object. Quantum dimension φ, forced.
- `A_ising` — **Ising** anyons. σ ⊗ σ = 1 ⊕ ψ, σ ⊗ ψ = σ, ψ ⊗ ψ = 1. **The primary structural control**: also non-abelian, also a modular tensor category, also physically realistic, different fusion algebra. This is the control that makes the test fair, isolating *Fibonacci* rather than *non-abelian*. Quantum dimension √2, forced.
- `A_su2_4` — **SU(2)₄**, quantum dimension √3, forced. A second non-abelian rung, included so that Factor A has an interior point rather than only its two endpoints. Without it, any monotone trend in dimension is indistinguishable from a two-point difference.
- `A_abelian` — **Z₃ abelian** anyons. Non-trivial but pointed; no fusion multiplicity; dimension 1. Isolates *non-abelian-ness* from *Fibonacci-ness*.

**Factor B — CONSTANT (the settled factor, retained as control), 4 levels.** The allocation constant distributing importance across the tree's leaves: `uniform`, `golden`, `silver`, `bronze`.

Factor B is included **not because it is expected to matter** — two experiments say it does not — but because holding it fixed is what makes the Factor-A comparison interpretable, and because an unexpected Factor-B effect inside a genuine anyonic code would itself be a finding.

### 1.2 The classical floor is NOT a cell

A classical linear code has no fusion-tree basis, so it cannot be run through the
identical encoder and recovery routine and cannot be a level of Factor A without
requiring a bespoke code path, which §1.3 forbids.

It is therefore **excluded from the factorial** and run separately as a reference
floor: a rate-matched and block-length-matched classical code, subjected to the
*same erasure masks* (identical seeds and identical erased-index sets) and scored
by the *same fidelity metric* reduced to its classical special case. It is reported
alongside the factorial as context and **may not enter any contrast, any kill
condition, or any pass criterion.**

### 1.3 Single parametrised code path

One implementation, parametrised by (category, constant). **No per-arm special-casing**, per house rule. Every cell is fed through the identical erasure model, the identical recovery routine, and the identical scorer. Any cell requiring bespoke code is a design defect and must be fixed before locking, not patched at analysis time.

### 1.4 The numerology tripwire

φ must appear **nowhere** in the erasure model, the noise model, the scorer, or the recovery routine. It enters at exactly two places, both declared:

1. As the quantum dimension that *falls out of* the Fibonacci fusion rule. It is not put in; d² = d + 1 is forced by τ ⊗ τ = 1 ⊕ τ.
2. As one level of Factor B, on identical footing with uniform, silver and bronze.

Building φ in and getting φ out proves nothing. The other categories' dimensions are likewise forced: √2, √3 and 1.

**A related guard, made mechanical.** `quantum_dimension_admissibility.py` records the
Jones (1983) index bound: dimensions in the discrete series are 2cos(π/n) < 2, so of
the metallic means only gold is admissible and φ is the unique member of both
families. There is no silver or bronze category to add as a further arm, and Ising's
√2 is *not* the silver mean. This is committed so the question does not have to be
re-answered from memory.

### 1.5 Task and erasure model (locked before any run)

- Encode a fixed logical payload into the fusion-tree basis of *n* anyons.
- Apply erasure at fractions f ∈ {0.25, 0.50, 0.75}, plus a burst/adversarial-block tear, matching GH-RECOV's stressor so the three experiments are comparable. Four erasure conditions in total.
- Erasure masks are generated once per (seed, fraction) and **shared byte-identically across all 16 cells and the classical floor**, so no cell can be advantaged by an easier draw.
- Attempt recovery; score fidelity of the recovered logical state.
- **20 seeds per cell**, fixed and recorded in advance. 16 cells × 4 conditions × 20 seeds = 1,280 runs, plus 80 classical floor runs.

---

## 2. The discriminating prediction, and why its pass-region excludes the generic answer

This is the section the ledger's admission criterion turns on.

**The generic answer is already known and is now the baseline, not the finding.** K-RECOV established that any heavy-tailed allocation beats uniform by a wide margin. That effect lives entirely on **Factor B**. It will reproduce here, it is expected, and **it may not be reported as evidence for anything.**

**The GHP prediction is a statement about Factor A with Factor B held fixed:**

> With the allocation constant held fixed, recovery fidelity under matched erasure differs measurably between fusion categories, and the Fibonacci arm is favoured.

**The pass-region excludes the generic answer by construction**, because the generic answer is *flatness in Factor A*. A generic-random outcome is not merely uninformative here — it is the falsifying outcome, pre-registered as such below.

### 2.1 The primary contrast (φ-free by construction)

The headline test is run at **Factor B = `uniform` only**, so that no metallic constant
appears anywhere in the primary comparison. Define, for each erasure condition *f*:

    Δ(f) = mean_fidelity(A_fib, uniform, f) − mean_fidelity(A_ising, uniform, f)

- **Aggregation:** cell mean over its 20 seeds. Seeds are paired across cells (identical erasure masks), so Δ(f) is computed as the mean of the 20 paired per-seed differences.
- **Uncertainty:** two-sided 95% confidence interval on the paired mean difference, via the paired *t* distribution on 19 degrees of freedom.
- **Multiplicity:** four conditions, Holm-corrected at family-wise α = 0.05.
- Every other cell is **secondary and exploratory**. No secondary result may trigger a pass or avert a kill.

### 2.2 Decision rule (executable, no judgement at analysis time)

| Verdict | Condition, stated so it can be evaluated by a script |
|---|---|
| **STRUCTURE FAVOURED** | Δ(f) > +0.02 with the Holm-adjusted 95% CI lower bound also > 0, in **at least 3 of the 4** erasure conditions. |
| **FLAT IN A** (kill) | \|Δ(f)\| ≤ 0.02 with the 95% CI contained inside [−0.02, +0.02] in **all 4** conditions. This is an equivalence result, not a failure to reject. |
| **TRACKS B** | Within a fixed category, the range of cell means across the four constants exceeds 0.02 by the same CI rule, while Δ(f) does not qualify as STRUCTURE FAVOURED. |
| **INTERACTION ONLY** | Neither main effect qualifies, and the category × constant interaction term in a two-way ANOVA is significant at α = 0.05. |
| **INDETERMINATE** | None of the above. Reported as such; **it is not a pass**, and it does not license a redesign into a fourth proxy (§2.6). |

The ±0.02 margin is carried from K-RECOV-001 for cross-experiment comparability. It is
**not** derived from a power calculation for this design, and that is an open question
for the lane before signing (§7 of the handoff).

### 2.3 Kill conditions (signed before data)

1. **Primary kill.** A verdict of FLAT IN A closes AH.4-P1 negative and closes B-022 with it.
2. **Non-abelian confound.** If Fibonacci beats classical and abelian but does **not** beat Ising, the finding is "non-abelian structure helps," **not** "Fibonacci helps." It must be reported under that name. GHP's Layer-3 bet is specifically Fibonacci, and a non-abelian win does not pay it out.
3. **Monotonicity check.** If fidelity increases monotonically with quantum dimension across 1 → √2 → √3 → φ, the result is about *dimension*, not about Fibonacci, and must be reported as such. `A_su2_4` exists to make this detectable.
4. **Anti-self-sealing.** A negative result closes the lane. It may not be reissued as a fourth proxy with a new stressor. Reopening requires the four-part bar already recorded for SEL-CLOSE-001.

### 2.4 A confound found by gate 1, and the control it requires

Recorded because it was found *after* the first draft and *before* signing, by running
`ah4_p1_braid_gate.py`.

Braiding three anyons generates a group of operations. Measured, counted up to global
phase: the **Ising** image is **finite, exactly 24 elements** — which is the order of
the single-qubit Clifford group modulo phase, consistent with the textbook result that
Ising braiding is Clifford-only and hence Gottesman-Knill simulable. The **Fibonacci**
image is **unbounded** (still growing at 69,900 elements), dense in SU(2), and
universal by braiding alone.

**The confound.** If the Fibonacci arm recovers better, two explanations are live:

1. the fusion structure itself carries the recoverability, or
2. the Fibonacci recovery routine simply has a richer operation set to search.

The second is a much weaker claim, and the design as first drafted would have reported
either as "structure carries recoverability."

**The control.** The recovery routine is given a **matched operation budget**: each arm
may apply at most *B* elementary braid operations drawn from its own group, with *B*
fixed across arms and recorded before the run. The primary contrast in §2.1 is
evaluated at matched *B*.

- Fibonacci favoured **at matched B** ⇒ the advantage is structural.
- Fibonacci favoured **only at unbounded B** ⇒ the advantage is operational richness. A real result, a different one, and it must be reported under that name rather than as the Layer-3 payout.

### 2.5 What may not be claimed under any outcome

- That a positive result proves the physical selection of φ. It would show a recoverability advantage for one fusion category in a simulated code, which is **engineering evidence about an architecture**, not evidence that nature selects it.
- That any result here bears on the SYK corridor, the DMRG band, or the dynamical-selection lane, all of which are separately governed.
- That software success constitutes physics evidence. The standing rule holds: *software echoes may inform the theory; they do not confirm the physics.*

### 2.6 Anti-self-sealing

INDETERMINATE is not a licence to rebuild. Any successor design must be preregistered
as a new test_id with its own kill conditions, and must state in its §0 why this
version was indeterminate.

---

## 3. Cost, and an honest statement of build difficulty

This is the expensive item in the programme's remaining queue, and the prereg should say so plainly rather than let it be discovered mid-build.

The Fibonacci arm requires correct F-symbols satisfying the pentagon identity, a fusion-tree basis with multiplicity handled properly, and a recovery routine that operates in that basis rather than on a vector of amplitudes. The other non-abelian arms require the same machinery with different symbols. **This is the real work**, and a shortcut that approximates the fusion tree by a generic weighted allocation reproduces GH-RECOV exactly and answers nothing — that shortcut is the specific failure mode this document exists to prevent.

**Gate 0 (done).** `ah4_p1_pentagon_gate.py` verifies the F-symbols satisfy the pentagon identity: Fibonacci 1.110e-16 over 48 non-trivial index assignments, Ising 2.220e-16 over 132, Z₃ exactly 0 over 81. A fidelity computed in a basis whose associator is wrong is a number about nothing.

**Gate 1 (done).** `ah4_p1_braid_gate.py` verifies the braid-group images and sizes the §2.4 confound.

**Gate 2 (outstanding).** The hexagon identity, checking the R-symbols against the F-symbols. Now required rather than optional, because §2.4 makes braiding load-bearing. **`A_su2_4` has no gate coverage yet** and must be added to gates 0 and 1 before signing.

---

## 4. Relationship to the standing discriminator criterion

The short paper §8 rule is: *no new compute for any test whose pass-region contains the standard-physics answer.*

- The **DMRG band** correctly fails this rule: its band contains β = 8/9, the ordinary CFT answer, so no new compute is warranted and it may be reported as pipeline validation only.
- **AH.4-P1 as designed here passes it**, because the generic answer (flat in Factor A) is the pre-registered falsifier rather than a pass.

This test is therefore admissible under the programme's own standing rule. That admissibility is the entire justification for building it, and it is the reason the factorial structure is not optional decoration.

---

## 5. Provenance

Drafted 2026-07-29 from the symbiote lane, as an external contribution to AH.4-P1. The factorial framing came from a topological-deformation pass over the GHP canon which independently reached the programme's own architecture-versus-dynamics conclusion, and which identified that both prior recoverability experiments varied the constant factor while leaving the structural factor untouched.

Amended the same day after external review raised four defects in the first draft
(design notation, the classical arm's code path, the lock protocol, and non-executable
decision rules) and after gate 1 exposed the operation-budget confound in §2.4. All
five were fixed before locking. The revision history is recorded rather than folded in
silently.

**Status: DRAFT, unsigned, not locked.** Nothing here is evidence. The physics content — the fusion-category machinery, the F-symbols, the recovery routine — belongs to the GHP lane and is not supplied by this document. What is supplied is the experimental design, the decision rules, and the kill conditions, committed before any data exists, per law 8.
