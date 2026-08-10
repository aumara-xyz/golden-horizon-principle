# The Golden Boundary

### What survived a program built to destroy its own best results

**Peter Viviani (AUMARA) with an AI crew · 2026-08-10 · rev 3 (final audit)**

**Status:** consolidation page. Every claim carries a class. Nothing here is physics evidence, and
the document says so in the places where you will most want it not to.

---

## Read this part first

This program spent three years asking whether the boundary between an observer and the world has a
minimal forced structure, and whether that structure is golden.

**The answer to the second question is no**, and we have killed it five separate ways with our own
instruments. The answer to the first is *yes, and the structure is thinner than anyone wanted.*

What follows is not a theory of everything. It is a short list of things that survived, a longer
list of things that did not, and one result we did not expect: **the discipline we built to test
the idea turns out to be an instance of the idea.** That is the only place in the program where
something closes, and it closes provably.

If you are looking for a unification of quantum and classical physics, it is not here and we will
tell you so four more times before the end. What is here is smaller, and it holds.

---

## 1. The convergence

A light cone. A black-hole horizon. A Markov blanket. An ε-machine's causal-state partition. An
access-controlled record.

Five objects from five fields that all look like the same idea: *an observer meets the world at a
boundary, and what crosses is all there is to know.* They are the same object — call it a **screen**:

> **I(P ; F | B) = 0** — given the interface B, the withheld part P tells you nothing more about
> the accessible part F.

Two of the five are theorems. ε-machine causal states are the *minimal* screen (Shalizi &
Crutchfield 2001) and a Markov blanket is the *symmetric* screen by definition (Pearl 1988). The
light cone is the deterministic case. **ESTABLISHED MATHEMATICS.**

**And the object is thin.** It carries no geometry, no area law, no temperature, no Clausius
relation, no preferred constant. Everything that makes each instance interesting lives in structure
added on top, and those additions are *incompatible in kind* — null geometry, stationarity, and
executable refusals do not belong to one theory. A "boundary law of nature" read off the shared
skeleton would be promotion by rhyme.

**The most famous member breaks the pattern.** Quantum-mechanically, in controlled settings, the
island formula makes a black hole's interior *encoded in its exterior radiation*. The exemplar
screen leaks. We take that as evidence that **leaky should be the primitive and exact the
idealisation** — every real screen has a leak rate, and a screen claim without one is unfinished.

## 2. The one axis nobody has

Screens are held in place three ways. By **dynamics** — causal structure forbids the path; that is
relativity, and it is mature. By **statistics** — the distribution factorises; that is the free
energy principle, mature and genuinely contested. And by **enforcement** — *an agent actively
refuses the crossing.*

The third is, as far as we can find, unrepresented in the literature. It is also the only one with
a falsifier available at engineering timescales, because you can build it and try to break it.

That is the program's one piece of unclaimed ground, and everything below is what we found
standing on it.

## 3. What died, and this is the credibility engine

Reported first, deliberately.

**The golden ratio is not selected by nature, and we killed it five ways.** Dynamical selection
closed against it (measured KAM noble-degeneracy: silver ≥ golden, margin below the preregistered
bar). Recoverability closed twice — once silver-optimal, once statistically indistinguishable from
a purpose-built greedy allocation at +0.006 against a ±0.02 threshold. The structural-advantage
hypothesis died at 400 seeds after a 20-seed trend dissolved entirely. Conditional-expectation
closure at index φ² returned a sound null: the machinery closes at φ, and *exactly as well* at every
control. And the two-observer consensus test met its own preregistered failure criterion.

**Then the last two toy wins fell.** "Fibonacci wins the core channel" reduced to a counting
artifact — the Fibonacci word simply has the fewest distinct k-mers (5, against 9, 10 and 21), an
established property of Sturmian sequences shared by every irrational-rotation word. "Ternary wins
the wrong-signal lane" reduced to bin geometry: the damage operator left the sparsest histogram
*exactly orthogonal to itself*, cosine 0.000.

**What survives about φ is one theorem and one reframe.** Hurwitz 1891: φ is the irrational least
well approximated by rationals — literally the seam between rational and irrational. And its role is
not what we assumed. φ is the *slowest* mixing among hyperbolic torus automorphisms; the Fibonacci
matrix `[[1,1],[1,0]]`, eigenvalues φ and −1/φ, is the **minimal-entropy Anosov automorphism of the
2-torus** (verified: entropy ln φ = 0.481212, against 2 ln φ for the Arnold cat map, by exhaustive
search over integer matrices with |det| = 1). Silver and bronze scramble faster.

So φ is not what information travels across. **φ is the condition under which two things never
lock.** Extremality, never selection — and the program's own notes had called it an "anti-locking
background" years ago and filed it as a disappointment.

## 4. The result that closes

The paper's object is the screen. The discipline used to produce the paper turns out to be an
instance of it — not by analogy, but as the same conditional independence with different variables.

**Precomputability.** If an observable is computable from the setup alone, it is a deterministic
function of the setup, so `I(world ; observable | setup) = 0`. The setup screens off the world.

**Unchecked labels.** `I(substance ; label | author) = 0`.

**Self-verification.** `I(truth ; verification | claimant) = 0` — which is exactly why a
verification path must terminate at a capability the claimant cannot occupy. Someone *not screened
off* has to be in the path.

Two things follow that we did not have to invent.

**Yield is a rate.** No real experiment has zero. Define **Y(E) = I(world ; observable | setup)**;
an experiment is admissible iff Y clears its null; the **dead control** is Y's estimator. This corpus
independently invented that method four times before noticing it was one method.

**The execution boundary is a corollary.** Our clause — that no receipt can prove execution of a
mechanism whose result the verifier can recompute — was reached by construction and attack, and its
status was open. It is `I(executed? ; R | inputs) = 0 when R = f(inputs)`. It **is** a theorem, and
it has **one** escape condition, not two: the result must not lie in the verifier's computable
closure. The two named escapes are instances of it.

**The evidence is thirteen failures, one shape.** A gate that passed by grepping for operators. A
gate that memorised the clean source's hash. A validator that never opened its manifest. A quantum
substrate that never evolved. A metric reading roundoff on an eigenvalue that was zero *by theorem*.
A frame digest computable from the head alone. A switcher whose 0.928 was a 0.747 class prior plus a
hard-coded relabel. A "miracle" repair that collapsed to exactly the prior under a rank-matched
control. Three of seven scoring terms pinned identical across every arm. An experimental design with
every value precomputable and zero empirical degrees of freedom. And a maintenance curve whose
dead-enforcement arm reproduced the live curve at **slope ratio 1.000**.

Different lanes, different years, different authors, one failure.

**Class: SYNTHESIS, not discovery.** Sham controls in medicine, negative controls in biology, power
analysis in statistics — each is this principle inside one field. The claim is narrower: that they
are *one* principle, that its content is a conditional independence, and that it therefore inherits
the leak correction — yield is a rate and every experiment has one.

## 4b. The cost of a boundary — and the answer to the triviality objection

The obvious objection to any theory of screens is that the definition is vacuous. Take **B = X**
and `I(X;Y|B) = 0` holds trivially. Every system "has a screen." Without an admissibility
constraint the whole construction is a tautology, and this is the strongest attack on it.

The answer is a cost floor, and it is two lines.

> **Proposition (screen cost floor).** If `I(X ; Y | B) = 0` then **H(B) ≥ I(X ; Y)**.
>
> *Proof.* `I(X ; Y,B) = I(X;B) + I(X;Y|B) = I(X;B)`. Also `I(X ; Y,B) ≥ I(X;Y)`. Hence
> `I(X;Y) ≤ I(X;B) ≤ H(B)`. ∎
>
> **A boundary costs at least the correlation it carries.** Class: THEOREM (elementary; almost
> certainly a restatement of a known data-processing consequence — cited as such if a source is found).

So the question stops being *does a screen exist* — always yes — and becomes **what does the cheapest
admissible one cost, and how much more than the floor.** Define the **screen overhead**

> **Δ(X,Y) = min_B H(B) − I(X;Y)  ≥ 0**

We computed the minimum exhaustively over all deterministic `B = g(X,Y)` for small joints —
every partition of the joint support, screening condition checked block by block:

| joint | I(X;Y) | min H(B) | overhead Δ |
|---|---:|---:|---:|
| independent | 0.0000 | 0.0000 | **0.0000** |
| perfectly correlated | 1.0000 | 1.0000 | **0.0000** |
| 3-way bottleneck | 1.5850 | 1.5850 | **0.0000** |
| noisy pair | 0.2781 | 1.0000 | 0.7219 |
| skewed | 0.2564 | 0.9709 | 0.7145 |
| 3×3 mixed | 0.3955 | 1.5710 | 1.1755 |

The floor held in every case, and **the overhead is exactly zero precisely when a clean bottleneck
exists** — when the dependence factors through a deterministic common structure. It is large when
the dependence is noisy: there, the cheapest boundary must carry far more than the correlation it
mediates, because it has to resolve cases that share no clean separator.

**Δ is therefore a measure of how far a system is from having an honest interface.** That is the
non-triviality condition the theory needed, and it is measurable.

### The correlated-path generalisation

The enforcement additivity proposition assumed independent paths. It does not survive correlation,
and the replacement is the obvious one — which is the point of stating it:

| path correlation ρ | measured leak | additive prediction | ratio |
|---:|---:|---:|---:|
| 0.0 | 3.9999 | 4.0000 | **1.0000** |
| 0.3 | 3.9684 | 4.0000 | 0.9921 |
| 0.6 | 3.5767 | 4.0000 | 0.8942 |
| 0.9 | 2.1291 | 4.0000 | **0.5323** |

> **leak = H(X_U)** for the uncovered set U — the *joint* entropy, which equals `Σ H(X_p)` **iff the
> paths are independent.** Additivity is the special case, not the law.

### A corollary withdrawn, and a control that caught us

An earlier draft claimed *no single scalar can represent enforcement and statistical leak without
equivocation.* **That was too strong and is withdrawn.** Mutual information plainly assigns a value
to both. The defensible claim is weaker:

> **Static leak is mechanism-incomplete.** Two screens with equal baseline `I(X;Y|B)` may be
> maintained by different mechanisms, and the baseline scalar alone does not identify which.

Even that needed a control. A first run appeared to show a dramatic signature — enforcement flat
then stepping in whole bits, statistics declining smoothly, diverging by **1.98 bits**. Re-run with
the perturbation applied to *random* positions instead of from the end, the divergence collapsed to
**0.30 bits** and the flat-then-step shape vanished. **The signature was substantially our choice of
perturbation.**

What survives is narrower and lives in the second moment: enforcement responds *raggedly*, losing
discrete whole paths (coefficient of variation of increments **0.625**), while statistics responds
almost perfectly uniformly (**0.021**) — a thirty-fold difference in raggedness with the levels
tracking within 0.3 bits. That is a real signature and it is not the one we first reported. It gets
its own preregistration before it counts as anything.

**Class discipline, applied here and throughout:** the cost floor is a **THEOREM**; the overhead
table and the correlated-path law are **MEASURED**; mechanism-incompleteness is an **OPEN
PROPOSITION** with one artifact already removed from its evidence.


## 4c. The final audit — what the cost quantity actually is

An external hardening pass asked the one question that decides whether any of this is new:
**what is `min_B H(B)` subject to `X ⊥ Y | B` in existing mathematics?** We ran it to the end.

**It is common entropy — known since 2014.** Minimising `H(W)` over stochastic kernels subject to
the Markov chain `X – W – Y` is *exact common information* / *common entropy* (Kumar, Li &
El Gamal, ISIT 2014; further developed by Yu & Tan). It sits above Wyner common information, which
minimises `I(XY;W)` over the same constraint, and the minimum alphabet size of `W` is the
**nonnegative rank** of the joint distribution matrix. The ordering `I(X;Y) ≤ C_Wyner ≤ G` is
established. Our "cost floor" is the leftmost inequality and it is elementary.

**And our search solved a different problem than the one we named.** The exhaustive partition
search minimised over *deterministic* `B = g(X,Y)` — a partition of the joint support into
independent blocks. That is a strictly more constrained object than common entropy, and it lives
naturally in rectangle-partition / communication-complexity territory rather than in nonnegative
rank. We measured the gap:

| joint | I(X;Y) | C_det (partitions) | C_stoch (kernels) | deterministic overhead | stochastic overhead |
|---|---:|---:|---:|---:|---:|
| independent | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| perfectly correlated | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| noisy pair | 0.2781 | 1.0000 | **0.9544** | 0.7219 | **0.6763** |
| skewed | 0.2564 | 0.9710 | **0.8554** | 0.7145 | **0.5989** |

**A stochastic boundary is strictly cheaper than any deterministic one**, on both noisy joints.
So the overhead table in §4b reports *upper bounds*, not the quantity it named — and our own
`C_stoch` is itself an upper bound, since it comes from numerical optimisation with no guarantee of
the global minimum. Both are corrected here rather than quietly restated.

**The "Δ = 0 precisely when a clean bottleneck exists" sentence is withdrawn.** It was inferred from
six examples and never proved. The correct statement is the equality condition of the chain
`I(X;Y) ≤ I(X;B) ≤ H(B)`: equality throughout requires `H(B|X) = 0` **and** `I(X;B) = I(X;Y)`, and
we have not derived the full equivalence class. It is an open question, stated as one.

### Two more demotions, both correct

**The correlated-path law is a proposition, not a measurement.** If uncovered paths publish `X_U`
verbatim then `X_U` is a deterministic function of the observable, so `I(X_P ; O) = H(X_U)`
immediately; independence merely turns the joint entropy into a sum. It follows algebraically from
the setup. The simulation verified an identity rather than discovering a phenomenon, and numerical
confirmation of a theorem is not independent evidence.

**The disclosure closed form is elementary pair-coverage.** `1 − (n−k)(n−k−1)/(n(n−1))` is exactly
the probability that at least one member of a random adjacent pair has been sampled — verified
identical to 1e-12. The formula is not new. What may be new is only its *application*: that an
RFC 6962 inclusion proof discloses an adjacent leaf for free, so proof issuance is pair-sampling.
Novelty is claimed for the application and for nothing else.

## 4d. The verdict, chosen last and not for excitement

Four endings were available. This is the one the mathematics supports.

> **RESULT 1 — the core quantity reduces to known common-information theory.** `min H(B)` under
> conditional independence is common entropy; the floor `H(B) ≥ I(X;Y)` is elementary; the
> disclosure curve is elementary combinatorics; the enforcement law is algebraic; the execution
> boundary is a two-line consequence of conditional independence whose prior art in verifiable
> computation and noninterference we have **not** yet searched and therefore may not claim.

What remains, honestly labelled:

**A synthesis, not a theorem.** The general object may be the constrained separation problem

> **min over B ∈ 𝓑 of 𝓒(B), subject to I(X;Y | B) ≤ ε**

where a domain supplies the admissible interface class 𝓑, the cost functional 𝓒, and the tolerance ε.
Sufficient statistics, the information bottleneck, causal states, access control, and experimental
design would then be *different ingredient choices in one optimisation problem* rather than the same
object. That is a far weaker and far more defensible claim than "all boundaries are the same thing,"
and it is the only unification the mathematics licenses. **Status: SYNTHESIS. Unproven as a theorem,
and it may be that no theorem is available beyond the mappings themselves.**

**One methodological result that is genuinely ours**, because it was paid for: *a perturbation
signature is a property of mechanism **and** intervention protocol, never of mechanism alone.* We
learned it by producing a 1.98-bit mechanism signature and then destroying it with a control that
changed only which positions were erased.

**And the corpus.** Thirteen failures with one shape, seven instrument self-catches, five
independent kills of the program's founding conjecture, and every number reproducible from a
preregistration committed before the code ran. That is not a theorem. It may outlast the theorems.


## 5. What fell out, with a closed form

An auditor requesting inclusion proofs from a Merkle log accumulates leaf hashes at **exactly two
per proof** — the requested leaf and its sibling, an adjacent record never asked for. After k proofs
on an n-leaf tree the recipient holds

> **coverage(k) = 1 − (n−k)(n−k−1) / (n(n−1))**  ·  **k₅₀ = (1 − 1/√2)·n ≈ 0.2929 n**

Measured k₅₀/n at n = 256 / 1024 / 4096: **0.285 / 0.288 / 0.292**. Closed form against brute force:
RMS 0.00244. No fitted parameters. Structure leaks faster than content — internal-node coverage runs
at 0.68 when leaf coverage is 0.50.

A threshold was retracted getting here. An earlier framing borrowed a "half the entropy" transition
from black-hole evaporation. The Page curve *turns* because Hawking radiation is finite and
correlations must surface; disclosure only accumulates. There is no knee. **The constant did not
transfer and the curve replaced it.**

## 6. Where this touches physics, and where it stops

Horizon thermodynamics is real and conditional: Jacobson's 1995 derivation of the Einstein equations
holds given six assumptions — local Lorentz invariance, the Unruh temperature, entropy strictly
proportional to horizon area, heat as boost-energy flux, the Clausius relation on *every* local
Rindler horizon, and local energy-momentum conservation. Remove any one and gravity does not appear.
The output leaves the cosmological constant, in Jacobson's own words, "as enigmatic as ever."

The island formula licenses **no causal escape and no white hole** — encoding is not transport — and
its extension to evaporating black holes in flat space is conjectural.

**And the disanalogy that matters: a black hole's boundary encodes a bulk that exists. A governed
record's boundary encodes nothing — the record is the primary system.** Holography is a claim about
redundancy between two descriptions of one thing. There is no bulk here for a boundary to be
holographic about. That is why AdS/CFT is not at the core of this program and cannot be.

## 7. What we are not claiming

No unification of quantum and classical physics. No theory of everything. No consciousness. No dark
matter. No proof that nature selects φ — we killed that ourselves, five times. No claim that
software success is physics evidence. No claim that a record's contents are true because the record
is sound: **membership is not occurrence, signing is not world-truth, and a true record of a false
thing is still a true record.**

**No experiment yet exists in this program whose pass-region excludes the standard answer** — and a
test that cannot lose cannot inform. The physics lane is on hold until one does.

## 8. How to check any of this

Every number above comes from a preregistered run with predictions and kill conditions committed
before the code executed, and each re-runs deterministically on any engine. The instrument was
caught by its own controls **seven times** — including twice while writing this page. Those catches
are in the record, at the front, because a program that shows you only its clean runs is
indistinguishable from one that discards its dirty ones.

**The self-catch rate is the most reproducible finding in this corpus, and it is the reason any
other number here deserves belief.** A research program's real output is not its positive results.
It is the rate at which it destroys its own.

---

*The dark is possibility. The light is distinction. The boundary is experience. The receipts are the
territory — and the lantern is not the evidence.*
