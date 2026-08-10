# §10 — The method is an instance of the subject

*Drop-in addendum for `research/PAPER_THE_SCREEN_IS_THIN.md`. Drafted 2026-08-10.
Every claim below is either a formal restatement, a measured result in this corpus, or is
labelled as a synthesis rather than a discovery.*

---

The paper's object is the screen: an interface B with **I(P ; F | B) = 0**. The paper's finding is
that the object is thin — no geometry, no thermodynamics, no preferred constant.

This section reports something we did not expect and can demonstrate: **the discipline used to
produce this paper is itself an instance of the paper's object.** Not as analogy. As the same
conditional independence, with different variables substituted.

## 10.1 Three methodological laws, restated

Three rules were arrived at empirically, over months, by being wrong. Each is a screen.

**Precomputability.** If an observable O can be computed from the experimental setup S alone, then
O is a deterministic function of S, so

> I(world ; O | S) = 0

The setup screens off the world. This is exact, not analogy — a deterministic function of the
conditioning variable is independent of everything given that variable.

**Unchecked labels.** If nothing verifies a label, its value is fixed by whoever wrote it:

> I(substance ; label | author) = 0

**Self-verification.** A claimant who can produce their own check:

> I(truth ; verification | claimant) = 0

which is why a verification path must terminate at a capability the claimant structurally cannot
occupy — the requirement is precisely that *someone not screened off* must be in the path.

## 10.2 What follows, and this is the part that earns the section

If the laws are instances of S1, everything the paper establishes about screens applies to them.
Two consequences follow immediately, and neither had to be invented.

**S4 is primitive here too — so precomputability is a rate, not a predicate.** No real experiment
has I(world ; O | S) exactly zero. Define the **empirical yield**

> **Y(E) = I(world ; observable | setup)**, in bits.
> An experiment is admissible iff Y exceeds its null.

Y = 0 is a precomputable experiment. The **dead control** — running the experiment with the
mechanism under test replaced by something inert, rate-matched on every nuisance axis — is the
*estimator of Y*. It was invented independently four times in this corpus before anyone noticed it
was one method.

**The execution boundary is a corollary.** This program's execution clause was reached by
construction and attack, and its status as a theorem was open. It is the same statement:

> I(executed? ; R | verifier's inputs) = 0 whenever R = f(inputs)

It is a theorem, and it has **one** escape condition, not two: *R must not lie in the verifier's
computable closure.* The two named escapes — a secret the prover holds, a value injected mid-run by
a party the prover cannot impersonate — are two instances of that single condition, not an
exhaustive enumeration.

## 10.3 The evidence: thirteen failures, one shape

Each of the following was reported, or nearly reported, as a result before its yield was checked.
Different lanes, different years, different authors.

| failure | computable from the setup alone |
|---|---|
| operator-fingerprint gate | the operator list |
| pristine-meaning oracle | the clean source; operator-set independent |
| self-attesting gauntlet | the validator never opened its manifest |
| inert quantum substrate | state never evolved; output a function of input |
| TL/φ² v1 metric | roundoff on an eigenvalue that was zero **by theorem** |
| "Fibonacci wins the core channel" | k-mer support sizes 5 / 9 / 10 / 21 |
| "ternary wins the wrong-signal lane" | roll-orthogonality; fib cosine exactly 0.000 |
| the switcher's 0.928 | class prior 0.747 plus a hard-coded variant relabel |
| the rank-shape miracle | the damage generator; collapsed to 0.748 = the prior |
| golden_zipper v69 ranking | three of seven score terms pinned identical across arms |
| a frame digest | the head alone; the count argument coerced to zero |
| EXP-M v1 design | all counts pinned ⇒ every value precomputable, zero empirical DOF |
| the EXP-M maintenance curve | the world-map encoding — dead arm reproduced live to **ratio 1.000** |

**Status of the generalisation: SYNTHESIS, not discovery.** Sham controls in medicine, negative
controls in biology, and power analysis in statistics are each this principle inside one field.
What is claimed here is narrower and, we believe, unstated: that they are *one* principle, that its
formal content is a conditional independence, and that it therefore inherits the S4 correction —
yield is a rate and every experiment has one.

## 10.4 The mirror condition — the release-curve special case

Let a screen be maintained by active refusals *a*, tested by progressively releasing them and
measuring I(P ; F | B) under freeze(*a*). If the world-map is such that releasing a refusal on a
path publishes whatever that path carried, and every path carries secret-bearing content, then the
measured curve **rises monotonically regardless of whether the refusals were ever coupled to
secret-bearing paths.**

Measured: the dead-enforcement arm reproduced the live curve at rise 0.4659 against 0.4658, OLS
slope ratio **1.000**. The result was withdrawn.

General form: *any experiment that tests whether a gate does work by removing the gate yields a
monotone curve if removing the gate mechanically publishes what the gate hid.*

## 10.5 A worked example with a closed form

The framework's first product-facing result. An auditor requesting RFC 6962 inclusion proofs
accumulates leaf hashes at exactly **two per proof** — the requested leaf and its level-0 sibling,
an adjacent record never requested. After k proofs on an n-leaf tree the recipient holds

> **coverage(k) = 1 − (n − k)(n − k − 1) / ( n (n − 1) )**
> **k₅₀ = (1 − 1/√2)·n ≈ 0.2929 n**  ·  **k₉₀ ≈ 0.684 n**

Measured k₅₀/n at n = 256 / 1024 / 4096: 0.285 / 0.288 / 0.292. Closed form against brute force:
RMS 0.00244. Internal-node coverage leads leaf coverage — 0.68 when leaves are at 0.50; structure
leaks faster than content.

**A threshold was retracted in the process.** An earlier framing proposed a disclosure "Page time"
at half the entropy, by analogy to black-hole evaporation. The Page curve *turns* because Hawking
radiation is finite and correlations must surface; disclosure only accumulates. There is no knee.
The constant did not transfer and was withdrawn; the curve replaced it.

**And the instrument caught itself.** The first run reported a knee. Two defects, both the author's:
the predicted model assumed sampling with replacement (RMS 0.114) where the process draws without
(RMS 0.00244); and the knee threshold was set at 1e-4 while coverage advances in steps of 2/n =
0.00195 — *below the quantisation floor*, so a discrete staircase exceeded it automatically.

## 10.6 What this does and does not establish

It does not get physics. It unifies the paper's method with the paper's subject — which is smaller,
provable, and closes. The admissibility criterion is *derived* from S1 rather than bolted on; the
execution boundary is a corollary with one escape condition; and the discipline that produced every
result in this paper is the same object those results are about.

For a paper whose finding is that the screen is thin, the honest close is this: the skeleton carries
no physics, and it does carry the epistemology. That is the whole of what we claim for it.

*No-upgrade sentence: nothing here is physics evidence; the generalisation in §10.3 is a synthesis
of principles already known in their home fields; the closed form in §10.5 bounds what a recipient
holds and is not a confidentiality proof — hashes are not preimages.*
