# Preregistration — AH.4-P1 v1 (the anyon fusion-tree recoverability discriminator)

- test_id: AH4-P1-ANYON-RECOV-v1
- ledger_anchor: ledger row **AH.4-P1** ("the one unbuilt experiment that can still discriminate"); master AH.4 Priority 1; bridge object **B-022** (holographic recoverability / QEC), whose closure condition the ledger names as AH.4-P1. Supersedes nothing: the two prior recoverability runs (**GH-RECOV** 2026-07-03, proxy, silver-optimal; **K-RECOV-001** 2026-07-19, external allocation replication, generic) are both **negative and retained**. This is the third and structurally different form.
- date_locked: DRAFT — not locked. No pipeline code for this test has been written or executed. This document must be signed and committed **before** any AH.4-P1 code runs.
- lane: **GHP discriminator.** Unlike KAM-CALIBRATION (calibration lane, not GHP evidence under either outcome), this test is designed so that one outcome is genuine evidence for GHP's Layer-3 bet and another falsifies the recoverability lane outright.
- runtime: Python 3 + numpy, deterministic, offline. Fusion-tree dimension kept small enough to be exact (no Monte-Carlo state approximation); target under 30 minutes single-core.

---

## 0. Why this test exists, and why the previous two could not settle it

Two recoverability experiments have run. Both returned negative for φ-specificity, and **both varied the same axis.**

- **GH-RECOV** (2026-07-03) compared *allocation constants* — golden vs silver vs bronze spreading — inside a fixed, generic code structure. Silver won (0.570 > bronze 0.479 > golden 0.432; golden 0/16 on the adversarial tear).
- **K-RECOV-001** (2026-07-19, external lab) compared *allocation schemes* — golden vs silver vs bronze vs exp-2 vs greedy-rank vs uniform — again inside a fixed, generic allocation structure. Any heavy tail crushed uniform (+15 points at 75% erasure); golden was statistically indistinguishable from purpose-built greedy (+0.006, under the ±0.02 bar).

Both asked: **is the number φ special?** The answer came back no, twice, from two laboratories. That question is settled and is not re-asked here.

Neither asked: **is the fusion-tree structure special?** No Fibonacci anyon fusion tree has ever been built in this programme. The ledger says so explicitly, and the short paper's §8 names this as the only remaining form whose pass-region could exclude the generic answer.

This matters because it is the one place where GHP's own founding lesson — *architecture is not dynamics* (short paper §3) — makes a prediction that has never been tested on the architecture side. Five dynamical searches for φ returned generic, exactly as that lesson predicts. The lesson also predicts that a **structural** probe should behave differently. If it does not, the lesson stops being a prediction and becomes a hedge, and the recoverability lane closes for good.

---

## 1. Design (to be locked)

### 1.1 The two axes, varied independently

The design is a **2 × k factorial**. The failure of the prior two experiments was that they were 1 × k on the wrong axis.

**Axis A — STRUCTURE (the untested axis).** The fusion category the code is built from:

- `A_fib` — **Fibonacci** anyons. Fusion rule τ ⊗ τ = 1 ⊕ τ. The GHP object.
- `A_ising` — **Ising** anyons. Fusion rules σ ⊗ σ = 1 ⊕ ψ, σ ⊗ ψ = σ, ψ ⊗ ψ = 1. **The primary structural control**: also non-abelian, also a modular tensor category, also physically realistic, different fusion algebra. This is the control that makes the test fair — it isolates *Fibonacci* rather than *non-abelian*.
- `A_abelian` — **Z₃ abelian** anyons. Non-trivial but pointed; no fusion multiplicity. Isolates *non-abelian-ness* from *Fibonacci-ness*.
- `A_classical` — a classical linear code matched on rate and block length. The floor.

**Axis B — CONSTANT (the settled axis, retained only as a control).** The allocation constant used to distribute importance across the tree's leaves: `golden`, `silver`, `bronze`, `uniform`.

Axis B is included **not because it is expected to matter** — two experiments say it does not — but because holding it fixed is what makes the Axis-A comparison interpretable, and because an unexpected Axis-B effect inside a genuine anyonic code would itself be a finding.

### 1.2 Single parametrised code path

One implementation, parametrised by (category, constant). **No per-arm special-casing**, per house rule. Every arm is fed through the identical erasure model, the identical recovery routine, and the identical scorer. Any arm requiring bespoke code is a design defect and must be fixed before locking, not patched at analysis time.

### 1.3 The numerology tripwire

φ must appear **nowhere** in the erasure model, the noise model, the scorer, or the recovery routine. It enters at exactly two places, both declared:

1. As the quantum dimension that *falls out of* the Fibonacci fusion rule — it is not put in; d² = d + 1 is forced by τ ⊗ τ = 1 ⊕ τ.
2. As one arm of Axis B, on identical footing with silver, bronze and uniform.

Building φ in and getting φ out proves nothing. The Ising arm's quantum dimension is √2, and the Z₃ arm's is 1; these are likewise forced, not chosen.

### 1.4 Task and erasure model (locked before any run)

- Encode a fixed logical payload into the fusion-tree basis of *n* anyons.
- Apply erasure at fractions f ∈ {0.25, 0.50, 0.75} plus a burst/adversarial-block tear, matching GH-RECOV's stressor so the three experiments are comparable.
- Attempt recovery; score fidelity of the recovered logical state.
- 20 seeds per cell, fixed and recorded in advance.

---

## 2. The discriminating prediction, and why its pass-region excludes the generic answer

This is the section the ledger's admission criterion turns on.

**The generic answer is already known and is now the baseline, not the finding.** K-RECOV established that any heavy-tailed allocation beats uniform by a wide margin. That effect lives entirely on **Axis B**. It will reproduce here, it is expected, and **it may not be reported as evidence for anything.**

**The GHP prediction is a statement about Axis A with Axis B held fixed:**

> With the allocation constant held fixed, recovery fidelity under matched erasure differs measurably between fusion categories, and the Fibonacci arm is favoured.

**The pass-region excludes the generic answer by construction**, because the generic answer is *flatness in Axis A*. A generic-random outcome is not merely uninformative here — it is the falsifying outcome, pre-registered as such below.

### 2.1 Outcome table (all four cells informative)

| Result | Reading |
|---|---|
| **Tracks Axis A, flat in Axis B** | The architecture carries recoverability and the constant does not. This is GHP's §3 thesis confirmed at the one site still able to test it, and it is consistent with all five dynamical nulls. **The strongest available outcome.** |
| **Flat in Axis A, tracks Axis B** | Recoverability is a property of the allocation constant, not the structure. Contradicts GH-RECOV and K-RECOV, both of which found the constant generic. Would require explaining before any claim. |
| **Flat in both** | The recoverability lane is dead. **Kill.** B-022 closes negative and AH.4 Priority 1 is retired. |
| **Interaction only** | Neither axis alone; the effect requires a specific pairing. Genuinely interesting, and it gets its own preregistration rather than a post-hoc story here. |

### 2.2 Kill conditions (signed before data)

1. **Primary kill.** If the Fibonacci arm's recovery fidelity does not exceed the **Ising** arm by a margin greater than **±0.02** (the K-RECOV bar, retained for comparability) at any erasure fraction, with the allocation constant held fixed, then the structural claim is refused and AH.4-P1 closes negative.
2. **Non-abelian confound.** If Fibonacci beats classical and abelian but does **not** beat Ising, the finding is "non-abelian structure helps," **not** "Fibonacci helps." This must be reported under that name. GHP's Layer-3 bet is specifically Fibonacci, and a non-abelian win does not pay it out.
3. **Anti-self-sealing.** A negative result closes the lane. It may not be reissued as a fourth proxy with a new stressor. Reopening requires the four-part bar already recorded for SEL-CLOSE-001.

### 2.3 What may not be claimed under any outcome

- That a positive result proves the physical selection of φ. It would show a recoverability advantage for one fusion category in a simulated code, which is **engineering evidence about an architecture**, not evidence that nature selects it.
- That any result here bears on the SYK corridor, the DMRG band, or the dynamical-selection lane, all of which are separately governed.
- That software success constitutes physics evidence. The standing rule holds: *software echoes may inform the theory; they do not confirm the physics.*

---

## 3. Cost, and an honest statement of build difficulty

This is the expensive item in the programme's remaining queue, and the prereg should say so plainly rather than let it be discovered mid-build.

The Fibonacci arm requires correct F-symbols satisfying the pentagon identity, a fusion-tree basis with multiplicity handled properly, and a recovery routine that operates in that basis rather than on a vector of amplitudes. The Ising arm requires the same machinery with different symbols. **This is the real work**, and a shortcut that approximates the fusion tree by a generic weighted allocation reproduces GH-RECOV exactly and answers nothing — that shortcut is the specific failure mode this document exists to prevent.

**Suggested gate before spending the build:** implement the Fibonacci and Ising F-symbols and verify the pentagon equation numerically to machine precision. If the pentagon check does not pass, no recoverability number computed downstream means anything. That check is cheap, it is a hard pass/fail, and it should be committed as a standalone verification before the experiment is built.

---

## 4. Relationship to the standing discriminator criterion

The short paper §8 rule is: *no new compute for any test whose pass-region contains the standard-physics answer.*

- The **DMRG band** correctly fails this rule: its band contains β = 8/9, the ordinary CFT answer, so no new compute is warranted and it may be reported as pipeline validation only.
- **AH.4-P1 as designed here passes it**, because the generic answer (flat in Axis A) is the pre-registered falsifier rather than a pass.

This test is therefore admissible under the programme's own standing rule. That admissibility is the entire justification for building it, and it is the reason the 2 × k structure is not optional decoration.

---

## 5. Provenance

Drafted 2026-07-29 from the symbiote lane, as an external contribution to AH.4-P1. The 2 × k factorial framing came from a topological-deformation pass over the GHP canon which independently reached the programme's own architecture-versus-dynamics conclusion, and which identified that both prior recoverability experiments varied the constant axis while leaving the structural axis untouched.

**Status: DRAFT, unsigned, not locked.** Nothing here is evidence. The physics content — the fusion-category machinery, the F-symbols, the recovery routine — belongs to the GHP lane and is not supplied by this document. What is supplied is the experimental design, the outcome table, and the kill conditions, committed before any data exists, per law 8.
