# The Golden Horizon Principle — Working Paper

## The Boundary Program

**Version 1.0 · 2026-07-03 · Canonical working paper**

> This program takes seriously the possibility that reality is informational all the way down — that "there" is a structure of records on boundaries, not a place. It does not claim to have shown this. It claims to have built the discipline that could.

---

### What this document is

This is the **canonical working paper** of the Golden Horizon Principle (GHP): the full argument, every test protocol and its verdict, the mathematics, the bridge stack, the toy-model arcs, the engineering embodiment, and the open problems — organized *claim → test → verdict → guardrail*.

It is the distillation of the 15,635-line research master (`GHP_v1_618_MASTER.md`), which is now **frozen as an append-only archive of record**. Every claim below traces back to the master by section, open-problem (OP), or ledger ID, so the archive remains the provenance trail while this document is the thing you actually read. Nothing was deleted in the distillation; where a result was demoted, killed, or found generic, that is stated here as plainly as any success.

For the twelve-page version, read `GHP_CORE_v2.md`. For the live status of any single claim, read `GHP_RESEARCH_LEDGER.md`. For the document map, read `CANON.md`.

### How to read a GHP result

The one discipline that makes this program worth reading is that it separates three claims that are constantly, fatally conflated:

- **Layer 1 — Access.** Reality is accessed only as records at boundaries. *Solid, mainstream.* You may assert it.
- **Layer 2 — Ontology.** The relational structure of those records is *what there is* — there is no further "over there." *A live research bet in respectable company (Wheeler's "it from bit," relational quantum mechanics, QBism).* You may hold it and research it; you may not yet claim it.
- **Layer 3 — Architecture.** The readable boundary has a minimal, forced structure, and it is **Fibonacci**. *GHP's own specific, falsifiable bet — and the layer on which every dynamical test to date has come back generic.*

Every section below tells you which layer it is speaking to, and ends with a bolded **Status & guardrail** line stating exactly what is proven, conjectured, or killed. If you take one thing from the whole paper: **φ lives in the architecture, not the dynamics** — a conclusion the framework reached about itself early, and then confirmed against its own hopes four independent ways.

### The result in one paragraph

We took a beautiful conjecture and built a machine strict enough that it could not lie to us about it. What is *proven* is mathematical and narrow: Fibonacci is the minimal non-trivial boundary alphabet, its dimension is φ, and φ is the most-irrational number. What has been *killed or found generic* is every search for φ in dynamics. What *survives and is useful* is architectural, extremal, and engineering — including a governed observer-boundary software stack and a holographic memory that heals when you tear it. There is no proof here and no refutation; there is a proven spine, an honest map of an open bet, a working embodiment under governance, and one clean experiment that would decide the rest. This document is the full accounting.

---

## Table of contents

1. **Introduction — the question and the discipline** *(this section)*
2. **The Mathematical Spine** — what is actually proven
3. **Architecture vs Dynamics** — the founding lesson
4. **The Viviani-φ Horizon** — the exact GR anchor
5. **The Bridge Stack** — how boundary-first ontology connects to physics
6. **The β-band Physics Lane** — DMRG and SYK
7. **The 2026-07-03 Test Battery** — four fresh verdicts
8. **The Observer-Memory Program** — Golden Zipper and Boundary Access Channel
9. **The Matter-Embedding Lane** — D4 to E6, honest obstructions
10. **The Engineering Lane** — Aukora, Auma, and holographic memory
11. **Methodology** — the falsification machine
12. **Open Problems and the Discriminator Roadmap**
- **Appendix** — Do-Not-Claim rules, verified literature spine, provenance

---

## 01. Introduction — the question and the discipline

Every measurement anyone has ever made is a record on a boundary: a mark on a detector, a photon at a retina, a pattern frozen into the microwave background, a signed receipt in a ledger. We never touch the thing itself; we touch its trace at an interface. This is the ordinary situation of physics, sharpened by the holographic bound — the information in a region scales with the area of its boundary, not its volume.

GHP begins there and asks whether that boundary has a **minimal, forced architecture**, and whether that architecture is the Fibonacci/golden structure that category theory singles out as the simplest non-trivial anyonic one. The conjecture is genuinely beautiful, and beauty is exactly the failure mode this program was built to resist. So the work has been less about *believing* the conjecture than about constructing tests that could *kill* it — and reporting, without flinching, what they found.

What they found, across months of work distilled in the sections below, is a clean and slightly surprising shape. The mathematics that fixes φ is real but narrow and mostly imported (§2). The founding computation showed that a golden *architecture* does not force golden *dynamics* — the golden chain's low-energy physics is ordinary tricritical Ising, central charge 7/10, not φ (§3). The designated falsification lane (DMRG and SYK β exponents, §6) has produced no φ-dynamics support, and a 2026 theory audit showed the DMRG band as designed actually *contains* the standard-physics answer, so an in-band result confirms known conformal field theory rather than GHP. A fresh four-test battery (§7) returned three verdicts against a φ-dynamical reading and one φ-free engineering pass — and, more valuably, caught two of its own tests measuring artifacts and killed them before report. The long observer-memory (§8) and matter-embedding (§9) arcs produced honest engineering-phenomenology and honest mathematical obstructions respectively, with exact-golden claims demoted in both. The one lane that flatly *works* is the engineering embodiment (§10): a governed observer-boundary, a model burned on its real architecture, and a holographic memory that degrades gracefully — all explicitly walled off from counting as physics evidence.

The bridges that *could* connect the boundary-first ontology of Layer 2 to physics (§5) are named honestly as imported machinery around an open problem, none constructed. And the program's most transferable output (§11) turns out not to be the Fibonacci conjecture at all but the **falsification machine** built to test it: preregistration with signed kill windows, no-upgrade sentences, adversarial verification, a numerology tripwire, and a ledger that preserves its own failures. That machine is why the nulls in this document are trustworthy and why a surviving claim would mean something.

The paper closes (§12) on the single strategic gap that now organizes everything: GHP has no test where its prediction *differs numerically* from standard physics. The way forward is one rule — no compute for a test whose pass-region contains the ordinary answer — and one target: the observable where φ has actually survived is architecture, and the sharpest architectural observable is **recoverability**. Does a Fibonacci code heal from damage measurably better than matched non-golden codes? That experiment, preregistered so its pass-region excludes the generic answer, is the whole ballgame. Everything before it was learning where not to look.

**Status & guardrail:** This introduction asserts only Layer 1 (access via boundary records) as established. Layers 2 and 3 are, respectively, a held research bet and a falsifiable conjecture under active test; nothing in this paper should be read as claiming either is proven, and no engineering or in-band-CFT result anywhere below counts as physics evidence for GHP.

---

---

## 02. The Mathematical Spine — what is actually proven

This section states the theorem-grade core of GHP without inflation. Everything here is either established mainstream mathematics or an exact algebraic consequence of it. Nothing here is physics evidence for GHP; the boundary between the proven mathematics and the physical conjecture that hangs it onto nature is drawn explicitly at the end. Two facts do the load-bearing work — categorical minimality and the Fibonacci fusion rule — and one commonly-cited fact, the φ² Jones index, is demoted here from "evidence" to "scaffold" on the strength of a preregistered null (P-005).

### 2.1 Categorical minimality (M-001) — theorem-grade

**Claim (master §2.1).** Among unitary *modular* categories containing at least one non-invertible simple object, the Fibonacci category is the unique minimizer of total quantum dimension D² = Σᵢ dᵢ², at D² = 1 + φ² = 2 + φ ≈ 3.618.

The proof is a chain of three imported classification results, not a GHP construction:

1. A non-invertible simple object of Frobenius–Perron dimension below 2 must have dimension 2cos(π/m), integer m ≥ 4 (Jones 1983); the smallest is √2.
2. Rank-2 fusion categories are classified (Ostrik 2003); in the unitary case only Fibonacci survives, and the upgrade to unitary *modular* at rank 2 is fixed by the low-rank modular classification (Rowell–Stong–Wang 2009).
3. Any rank ≥ 3 with a non-invertible object of dimension ≥ √2 already gives D² ≥ 1 + 1 + 2 = 4 > 2 + φ.

So Fibonacci is the unique minimizer. The result is **imported, not derived**: GHP contributes the framing (minimum-cost boundary architecture), not the theorems. A corollary strengthens the reading physically without adding a claim: among *braiding-universal* categories, Fibonacci is still the minimum — the next universal competitor, SU(2)₃, costs exactly twice as much (D² ≈ 7.236). Ising (D² = 4) is cheaper than SU(2)₃ but is not braiding-universal.

**What the theorem does not say.** It does not say nature settles boundaries at this minimum — that is the §5 conjecture. It also carries a scoping subtlety (master §2.3): minimality holds for *chiral* Fibonacci (D² = 2 + φ), whereas the doubled/Drinfeld-center realization has D² ≈ 13.09. Identifying the observer with the chiral edge rather than the doubled bulk is a physical postulate (§5.2), not part of the theorem. Prior drafts slid the categorical result and its physical reading together; they are kept separate here.

### 2.2 The fusion rule and the origin of φ (M-002) — theorem-grade

**Claim (master §2.4).** Fibonacci has two simple objects, vacuum 1 and anyon τ, with fusion τ ⊗ τ = 1 ⊕ τ. Taking quantum dimensions gives d_τ² = 1 + d_τ, whose unique positive root is d_τ = φ.

This is the entire honest source of the golden ratio in GHP: φ is an **exact algebraic consequence of a fusion rule, not a fit and not a measured constant.** The anyon is self-dual and fusion is time-invertible. It is also worth stating what τ is not: it is an emergent quasiparticle of a 2D string-net condensate (Levin–Wen 2005), not a fundamental particle. The architecture therefore asks only that a boundary support a topological phase whose excitations minimize D²; it does not posit exotic fundamental matter. M-002 is imported fusion-algebra; GHP's only move is to treat this algebra as the source object rather than a curiosity.

### 2.3 Dimensional selection (master §2.6) — imported topology, conditional reading

For 1D strand-like objects, non-trivial knotting is topologically stable only in exactly three spatial dimensions: 2D has no over/under crossing, and in ≥ 4 spatial dimensions any 1D knot unties. This is standard knot topology (with Berera et al. 2015 "knotty inflation" as a physics instance). GHP's use of it is **conditional, not a theorem**: *if* the boundary encodes bulk structure through braiding, *then* the projection must land in three spatial dimensions. The conditional depends on a holographic dictionary between a 2D categorical boundary and 3+1D bulk that GHP does not construct and does not claim to possess. The topology is solid; the physical inference is a hypothesis flagged as such (master's own §2.6 scoping).

### 2.4 The quotient principle and the φ² index (master §2.7, §2.8) — SCAFFOLD, and a null

The organizing schema — "dynamics is the residue after quotienting out architecture" — is realized computationally as a coset central-charge identity, SO(7)₁/(G₂)₁ giving c = 7/2 − 14/5 = 7/10. As an *arithmetic identity* this is correct. As a *bridge* to a physical mechanism it is explicitly open (master's Open Problem 13; the algebraic quotient of §2.7 and the holographic projection of §2.6 are different operations, and their compatibility is unproven).

The tempting piece here is the **Jones subfactor index**. The smallest non-trivial finite-depth index is 4cos²(π/5) = φ² (Jones 1983), matching d_τ². This is genuine, beautiful mathematics: a subfactor inclusion N ⊂ M models "architecture embedded in a larger observable algebra," with the residue formalizable as the conditional expectation E : M → N. GHP repeatedly reached for this as if the φ² coincidence were evidence that φ is privileged in the finite-access machinery.

**It is not, and a preregistered test says so.** P-005-TL (ledger; `TL_phi2_v2.py`) ran the Temperley–Lieb / conditional-expectation closure at δ = φ against controls at δ = √2 (index 2), δ = 2cos(π/7) (index 3.247), and δ = 2 (index 4). Result: a **sound null** (2026-07-03, adversarially re-verified after a v1 roundoff-on-a-structurally-zero-eigenvalue flaw was caught and fixed). The machinery closes cleanly at φ — and *exactly as cleanly* at every control. φ's one nonzero residual is marginally *worse* than the controls', not better. The conclusion the paper must carry: **the subfactor / conditional-expectation apparatus is real machinery for finite-access forgetting, but φ is not distinguished within it.** The φ²-index is therefore SCAFFOLD (established math, structurally useful) and must never be cited as evidence of φ-specificity. The x² = x + 1 "bridge" (§2.8) between the Fibonacci fixed point and the Schwarzschild γ = r/r_s = φ identity is, by the master's own labeling, a conjectural structural observation — same equation is not same object — and inherits none of the φ-privilege the null just removed.

### 2.5 Hurwitz extremality (master §5.4) — the one surviving φ-specific fact

The single dynamical-adjacent fact that is *both* rigorous *and* φ-specific is **Hurwitz's theorem (1891)**: among all irrationals, the numbers equivalent to φ under the modular group are the hardest to approximate by rationals — φ is the slowest-converging irrational. This is 1891 mathematics, correctly credited, and it is not a GHP result. Its GHP reading is disciplined: it explains why, *within* an already-fixed band, the φ edge is the attractor that resists commensurate phase-locking (master §5.4 Layer 3, OP 155). It does not derive the band — the master's post-v0.670 correction is explicit that the band's endpoints come from the fusion-matrix spectrum, not from Diophantine robustness.

Two guardrails attach. First, KAM (Kolmogorov–Arnold–Moser) is real and its golden-tori-last-to-dissolve statement is proven, but it is imported dynamics applied by analogy, not a GHP derivation. Second, Hurwitz extremality is genuinely φ-specific in a way most GHP "golden" claims are not: the metallic-recurrence "zipper" behavior once read as a write-law is a **sound null** (M-005) — the sign-alternation is generic to the whole silver/bronze/metallic family; only Hurwitz extremality survives the golden-vs-control comparison. That single surviving fact is exactly the extremal, architectural kind — not a dynamical one.

### The honest boundary

Stack the three layers and keep them from blurring. (1) *Reality is accessed only as boundary records* — solid, mainstream. (2) *A boundary-first ontology* ("no over there") — a live research bet in respectable company (Wheeler's it-from-bit, relational QM, QBism); held, not proven. (3) *The readable boundary's minimal architecture is Fibonacci* — GHP's specific bet. The mathematics in this section belongs almost entirely to a fourth, narrower category: **theorems about categories** (minimality, fusion) and **an extremality fact** (Hurwitz), which are true independent of whether nature is boundary-first at all. The leap from "Fibonacci is the minimal braiding-universal architecture" to "nature's boundary *is* Fibonacci" is physical conjecture, and every *dynamical* test of it in this program has come back generic or killed (P-005 null; the golden-chain lands on tricritical-Ising c = 7/10, not φ — §3). What survives is architectural and extremal, which is the master's own founding conclusion: **φ lives in the architecture, not the dynamics.**

**Status & guardrail:** Categorical minimality (M-001) and the fusion rule (M-002) are theorem-grade imported mathematics that fix φ exactly; the φ² Jones index is real machinery but SCAFFOLD, not φ-specificity evidence (P-005 sound null); Hurwitz extremality is the one surviving φ-specific fact; everything connecting this mathematics to physics remains conjecture, and no result here is evidential support for GHP as physics.

---

## 03. Architecture vs Dynamics — the founding lesson

This is the most important conceptual result in the program, and the one every reader should take away first: **golden architecture does not force golden dynamics.** The minimal topological architecture at the boundary is Fibonacci (§2, theorem-grade). But the low-energy *physics* that architecture supports is not φ-structured at all — it flows to the tricritical-Ising universality class with central charge c ≈ 7/10. This is not a disappointment the program has to explain away. It is a sharp, self-imposed limit that separates GHP from numerology, and it is now confirmed four independent ways by the 2026-07-03 battery.

### 3.1 The golden chain: exact φ in the architecture

The canonical many-body realization of Fibonacci structure is the *golden chain* — a periodic chain of N interacting Fibonacci anyons with Hamiltonian H = −Σ P_{i,i+1}, where P projects onto the trivial fusion channel. This Hamiltonian generates a representation of the Temperley-Lieb algebra with loop parameter d = φ. We exact-diagonalize it (no stochastic elements) for N = 4 through 24, resolving the vacuum and τ sectors via the topological symmetry operator Y, with commutator check ‖[H,Y]‖ ≈ 10⁻¹⁵ (master §3.1).

On the **architecture** side the result is exact and clean (§3.2). At N = 20 the leading Schmidt-eigenvalue ratio is φ to eleven decimal places; the reduced-density ratio is φ²; the τ/vacuum sector ratio is φ² to six places. These are not fitted parameters — they are Fibonacci fusion-space dimension identities confirmed by computation. Critically, a cut-position scan (positions 2, 4, 6, 8, 10 at N = 12, 16, 20) finds the leading golden ratio at *every* bipartition, not only at the midpoint. The golden architecture is a **bulk property** of the chain, not a bipartition artifact.

### 3.2 The dynamics land on c ≈ 7/10, not φ

On the **dynamics** side the same chain refuses to be golden (§3.3). The extracted central charge is 0.69909 (vacuum) and 0.6971 (pairwise, N = 24), both converging on c = 7/10, not φ. The gap ratio at N = 20 is 1.0835 (not φ); the gap-scaling exponent z is 0.989 (consistent with conformal z = 1, not φ); the cross-sector gap ratio is ≈ 7.22 (not φ). The low-energy physics is the tricritical-Ising minimal model M(4,5), c = 7/10 — a universality class with no golden ratio in its critical data.

The two sides connect through a known algebraic fact, not a coincidence: the tricritical-Ising CFT realizes Fibonacci *non-invertible* symmetry, and the coset construction SO(7)₁/(G₂)₁ gives exactly c = 7/2 − 14/5 = 7/10, where (G₂)₁ is the Fibonacci topological phase (§3.4). The dynamics are algebraically the **quotient** obtained by factoring the golden architecture out. This is the program's organizing schema — *dynamics is the residue after quotienting out architecture* — but it is a schema, not a derivation, and the paper never lets it pretend otherwise.

### 3.3 The negative results are load-bearing

The founding lesson was forced by failures, and the paper reports them as prominently as any pass (master §4). Every attempt to make a *dynamical* observable come out golden has failed: the SYK spectral form factor gave the exponent the *opposite sign* from β = φ (ruled out); a refined SYK exponent came back inconclusive; in a coupled-oscillator test φ lost to control irrationals 18 of 27 times; and the golden-chain gap ratio, gap scaling, and cross-sector ratio are all non-φ as above. These are not clutter. They are the reason the honest statement is sharp:

> GHP is strongest read as an **architectural** principle, not as a claim that golden ratios generically govern dynamical exponents.

### 3.4 Independent confirmation: the τ defect line survives RG flow

The split is not an artifact of our one chain. The 2024–2026 non-invertible-symmetry literature exhibits it in a controlled theoretical setting (§3.5). Perturb tricritical Ising (c = 7/10) by the relevant operator φ_(2,1); it flows to plain Ising (c = 1/2). Under this flow, published Thermodynamic-Bethe-Ansatz and Non-Linear-Integral-Equation analyses show the **Fibonacci τ topological defect line survives intact** — it commutes with the perturbation because φ_(2,1) is a singlet under the Fibonacci action. The quantum dimension d_τ = φ and the fusion rule τ ⊗ τ = 1 ⊕ τ are preserved between UV and IR fixed points, while the central charge collapses from 7/10 to 1/2. The *architecture* rides the flow; the *dynamics* change dramatically. Non-invertible symmetry acts as an 't Hooft anomaly-matching condition. This upgrades the lesson from a property of one system to a general feature of RG flows that preserve non-invertible symmetry.

### 3.5 Selection probability ≠ critical exponent

A specific discipline rule guards the split from its most tempting misreading (§5.1A). Inside the Fibonacci category the fusion-probability weights are P(τ) = d_τ²/D² = φ²/(2+φ) ≈ 0.7236 and P(1) = 1/(2+φ) ≈ 0.2764, defining a *selection window* [0.276, 0.724]. This number is φ-structured because d_τ = φ — but it lives in the **selection** lane, not the **dynamics** lane. It is emphatically *not* the c ≈ 7/10 residual, and it must never be conflated with a critical exponent:

> **~0.724 is a selection probability, not a critical exponent. c ≈ 7/10 remains the dynamics residual.**

The two numbers may eventually speak to one another, but the framework has not earned the right to collapse them, and §5.1A explicitly forbids doing so.

### 3.6 The 2026-07-03 battery: the lesson confirmed a fourth time

The founding split has now been re-confirmed by four independent tests from the current battery, each landing exactly where this lesson predicts — architecture and extremality survive; dynamics comes back generic or killed (ledger M-003, P-002, P-005-TL, P-007-2OBS, M-005):

1. **DMRG β-band (P-002).** Seven of nine hardened sector-preserving rerun points are clean (two heaviest still computing). A 2026-07-03 theory audit (Feiguin et al. 2007, PRL 98, 160409) finds the mass deformation couples to the tricritical-Ising σ′ operator (dimension 7/8), predicting β_null = 8/9 ≈ 0.889 — *inside* the preregistered band [1/φ, φ]. So an in-band result would confirm known 2007-era CFT, **not** GHP; only β ≈ φ = 1.618 would be a genuine anomaly. This recurs an earlier identical exercise on the sister operator ε′ (dimension 6/5 → ν = 5/4 = 1.25), already recorded at master §5.10A / AE.8–AE.9.

2. **Two-observer consensus (P-007-2OBS).** A sound kill at L ≤ 12: the golden-chain mutual-information slope is statistically indistinguishable from same-central-charge CFT controls (separation 0.18 against a required ≥ 1.5). This directly satisfies OP 164's *own* preregistered φ-failure criterion — "if no φ role emerges in the proportionality, the invariance hypothesis is weakened." No φ role emerged. Larger-L confirmation is running.

3. **Temperley-Lieb / φ² Jones closure (P-005-TL).** A sound null: the conditional-expectation machinery closes cleanly at index φ² — but *exactly as well* as at controls (index 2, index 2cos(π/7) ≈ 3.247, index 4). φ's one nonzero residual is marginally *worse* than the controls'. The machinery is real; φ is not privileged within it.

4. **Metallic-recurrence "zipper" (M-005).** A sound null: the sign-alternation behavior is generic to the entire metallic-mean family (silver, bronze, all δ). The single φ-specific dynamical-adjacent fact that survives is **Hurwitz extremality** — φ is the slowest-converging, hardest-to-rationally-approximate irrational (Hurwitz 1891, master §5.4). That is 1891 mathematics, correctly credited, and it is architectural/extremal, not dynamical.

The shape is unmistakable and consistent across all four: everything **architectural** (categorical minimality, M-001/M-002), **extremal** (Hurwitz), or **engineering** survives; every **dynamical** φ-claim has come back generic or killed. φ lives in the architecture, not the dynamics.

### 3.7 Why this is a strength

Three layers must never blur, and this section holds them apart. (1) Reality is accessed only as boundary records — solid, mainstream. (2) A boundary-first ontology ("no over there") is a live research bet in respectable company (Wheeler's it-from-bit, Relational QM, QBism) — held, not proven. (3) The readable boundary's minimal architecture is Fibonacci — GHP's specific bet, and the layer where every *dynamical* test has come back generic. The founding lesson is precisely the seam between layer 3's architectural success and its dynamical silence. A theory that claimed φ everywhere would be unfalsifiable numerology; a theory that draws a sharp line — φ in the architecture, c = 7/10 in the dynamics, and *reports its own kills* — is doing science. The limit is the credibility.

**Status & guardrail:** Golden **architecture** in the Fibonacci chain is exact and confirmed as a bulk property (theorem-grade, §3.2); golden **dynamics** is falsified — the chain's low-energy physics is tricritical-Ising c ≈ 7/10, not φ (§3.3–§3.5), a split now re-confirmed four independent ways by the 2026-07-03 battery — and no in-band CFT exponent, selection probability, or engineering result is ever evidence for GHP dynamics.

---

## 04. The Viviani-φ Horizon — the exact GR anchor

Everything else in this program is a comparison — golden against control, an exponent against a band, a null against a pass. This section is the one place where φ appears *exactly*, with no comparison and no residual. It is worth stating precisely what that exactness buys, because it buys much less than the name suggests. (Master §5.1C; floor theorems §5.1Z; ledger B-001, T-107.)

### 4.1 The identity

In Schwarzschild geometry, impose on the static-observer time-dilation factor γ(r) = 1/√(1 − r_s/r) the single self-referential condition **γ(r) = r/r_s** — the redshift factor equals the horizon-normalized radius. Squaring and reducing gives x² − x − 1 = 0 with x = r/r_s, whose positive root is φ = (1+√5)/2. The surface sits at

**r = φ·r_s**,

exactly and uniquely. This is the same quadratic that defines Fibonacci's quantum dimension in §4's categorical floor — the one algebraic fact the architecture side and the gravity side genuinely share.

The physically load-bearing form is coordinate-invariant. Writing ξ = ∂_t for the timelike Killing vector, the condition is

**√(−g(ξ,ξ)) · r = r_s**,

a product of two scalars — the Killing-vector norm and the areal radius r — each invariant in Schwarzschild. This is what makes the object survive coordinate-artifact discipline (§4.4), and it is the *entire* content of the anchor. Everything below is deformation and decoration.

### 4.2 Extensions across the metric families

The identity deforms cleanly, and the deformations are honest about where φ persists and where it drifts (§5.1C.1, master items G–H):

- **Reissner-Nordström (charge q = r_Q/r_s):** single branch, exact closed form x(q) = (1 + √(5 − 4q²))/2. At q = 0, x = φ; at extremality q = 1/2, x = 3/2, coinciding with the Schwarzschild photon sphere. No frame-dragging, so no observer split.
- **Kerr (spin α = a/r_s):** the surface bifurcates by observer family. A *static* observer preserves r = φ·r_s on the equator in Boyer-Lindquist r for all spin; a zero-angular-momentum observer follows a quintic whose root is φ at α = 0 and drifts down as α² with the exact leading coefficient (3√5 − 5)/10. Coordinate caveat: in Kerr, Boyer-Lindquist r is not the areal radius, so the invariant form is coordinate-specific in the rotating case.
- **Schwarzschild-Tangherlini (d = n+2 dimensions):** the master equation x^(n−1) − x^(n−3) − 1 = 0 has a unique, dimension-decreasing positive root. n = 2 gives φ; n = 3 gives √2; n = 4 the plastic constant; n = 5 gives √φ. So the 4D golden value is the n = 2 member of a structured algebraic family — not a standalone coincidence, but also not a distinction φ holds alone.

Circular-geodesic invariants at r = φ·r_s reduce to closed form: specific energy E/m = √2 (via the one-line identity φ³(2φ − 3) = 1), angular momentum L/m = φ^(5/2), frequency Ω² = 1/(4φ+2). These survived independent hostile re-derivation (§5.1C.2-A) with no math error found.

### 4.3 What the adversarial review killed and cooled

The credibility of this anchor rests on what it *lost* under review, logged in full at §5.1C.2-A:

- **The dimensional-lift conjecture (OP 144) is CLOSED — FAILED.** The pairing "4D orbital √2 equals the 5D radius √2" is an algebraic coincidence: r = √2·r_s is exactly the 5D photon sphere, where timelike orbital energy diverges. There is no structural lift.
- **The VPH circular orbit is unbound and unstable.** E/m = √2 > 1 places it inside the marginally-bound radius; matter there escapes or plunges. The earlier "transient capture in accretion flows" reading was retracted as an overclaim.
- **Astrophysical frequency bands are coincidence, not attribution.** Ω(VPH) lands near HFQPO / GRAVITY / EHT bands, but no transfer function or residence-time argument exists; nothing observed is attributed to this surface.
- **Naming was cooled.** The object is called "Horizon" in the evocative sense of a distinguished bounding surface only. It is **not** a null hypersurface, not a Killing horizon, not a trapped surface, not a curvature singularity. The preprint's referee-driven "Viviani-φ Surface (VPS)" naming is the more honest label and is used interchangeably here.

### 4.4 Coordinate-artifact discipline

GR's standard warning is that an apparent boundary may be a coordinate artifact: Schwarzschild's r_s looks singular in one chart and is extendable in another. The VPS-extendability probe T-107 / VPH-EXT-001 (Addendum AZ; `experiments/ghp_vph_extendability_probe.py`) applies exactly this test. Result: the exact identity holds to machine precision (residuals ~2.2×10⁻¹⁶); the Killing norm is finite and nonzero and curvature is finite at the surface (so it is not a horizon or singularity); and critically, replacing r with an arbitrary monotone radial coordinate and imposing the same-looking equation produces *fake* fixed points that **move** (nearest bad-coordinate offset 0.382), while the invariant-scalar root does not (root spread 0.000). The VPS is admissible **because it is a scalar identity in Killing-norm and areal radius, not because a chosen coordinate happened to look golden.**

### 4.5 Prior art and the sonoluminescence quarantine

φ has appeared in black-hole physics before, and this section credits it: golden ratio in Schwarzschild-Kottler null-geodesic turning points (**LIT-V001**, Cruz-Olivares & Villanueva 2017); golden ratio in optical geometry / orbit structure (**LIT-V002**, Coelho & Herdeiro 2009); photon-sphere radius bounds (**LIT-V003**, Hod 2013); plus Nieto 2011, Davies 1989, and Sonnino-Nardone 2024 (§5.1C.1 item J). Those are orbital or extremal results; the self-referential static-observer time-dilation fixed point appears to be distinct, but the novelty claim is explicitly *provisional* — a hostile scan of Chandrasekhar, Frolov-Novikov, and MTW is not a formal literature review.

The sonoluminescence analogy is quarantined by rule (VPH-SONO-001, Addendum AZ.4). Acoustic-cavitation collapse converting hidden boundary structure into visible emission is *boundary-readability language only*. It does not support the identity, does not derive φ, implies no over-unity energy, and does not upgrade the surface into any dynamical, thermodynamic, or causal horizon.

### 4.6 What this is and is not

The three-layer discipline of this paper applies sharply here. This is a genuine result at **Layer 1** (reality-as-boundary-record) and a clean algebraic fact of textbook GR. It is *suggestive* for **Layer 3** (the Fibonacci-architecture bet), because the anchor's defining equation is φ's defining equation. But it is **not** evidence *for* Layer 3: the surface is not a horizon, carries no dynamics, derives no matter content, and does not close the proposed φ² Jones-index bridge to Fibonacci (§5.1C.1 item I leaves that at the obstruction-sketch stage). It proves that φ sits at an algebraically minimal geometric condition in GR — and nothing about whether nature *selects* it.

**Status & guardrail:** The r = φ·r_s identity is a **proven**, coordinate-invariant, hostile-review-hardened exact fact of Schwarzschild GR (with clean RN/Kerr/Tangherlini deformations); it is **not** a horizon, dynamics, physical evidence, proof of GHP, or the closed Fibonacci bridge — the dimensional-lift conjecture is **killed**, novelty is provisional, and the sonoluminescence analogy is quarantined as language only.

---

## 05. The Bridge Stack — how boundary-first ontology connects to physics

This is the intellectual heart of "there's no over there." Before any bridge is drawn, three layers must be held apart, because the whole credibility of the program lives in the gaps between them:

- **Layer 1 — reality is accessed only as boundary records.** You never touch the thing; you touch its readable trace on a boundary you can write to. This is solid and mainstream: it is the shared content of information-theoretic physics, holography, and any operational reading of measurement.
- **Layer 2 — boundary-first ontology, "no over there."** The boundary is not a window onto a prior interior; the record *is* the ontological primitive. This is a live research bet in respectable company — Wheeler's it-from-bit, Rovelli's relational QM, QBism. It is held, not proven.
- **Layer 3 — the readable boundary's minimal architecture is Fibonacci.** GHP's specific bet. This is where every *dynamical* test has come back generic or killed. The architectural, extremal, and engineering results survive; the claim that φ governs the *dynamics* of the boundary does not.

The care demanded here is specifically the Layer 2 / Layer 3 seam. Layer 2 is a stance about what a boundary record *is*; it is compatible with any number of architectures, including boring ones. Layer 3 adds a substantive, falsifiable claim about *which* architecture the readable boundary minimally is. It is entirely coherent to hold Layer 2 and reject Layer 3 — indeed, most of GHP's own dynamical tests now point exactly there. Conflating the two is the single most tempting error in this program: a boundary-first reader nods along at "no over there," and the nod gets silently upgraded into assent to "…and it is Fibonacci." It is not. The bridges below are the machinery that *would* license the upgrade. Every one of them is currently an open construction, and the two that have been tested directly failed to distinguish φ.

The "bridge stack" is the honest map of candidate machineries that would let Layer 2 cash out into Layer-1 physics — and, at their most ambitious, license the Layer-3 upgrade. None of these bridges is constructed or closed. Each imports real, externally-verified mathematics and names what that mathematics *would* explain if the identification held. The identification does not yet hold anywhere. The distinction that runs through every entry: importing machinery is not the same as closing a bridge, and a bridge closing at Layer 2 (finite access is algebraic, recovery is QEC-shaped) does not close it at Layer 3 (…and the distinguished architecture is φ).

### B-020 — Conditional expectation / finite access (§2.7, §5.18K)

The import is operator-algebraic: an inclusion of von Neumann algebras N ⊂ M with Jones index [M:N], and the conditional expectation E : M → N that formalizes "the observer's accessible algebra is a smaller sector bought at the price of forgetting the whole" (§5.18K.1). The minimal finite-depth index is φ² (Jones 1983), matching the Fibonacci quantum dimension squared. This would explain *finite access* — who can read what — as an algebraic fact rather than a postulate, and would route the Dynamics Gap through Tomita–Takesaki modular flow (Connes–Rovelli thermal time).

This is exactly the Layer 2 / Layer 3 seam in miniature. At Layer 2 the bridge closes cleanly: finite access genuinely *is* a conditional expectation, and forgetting genuinely *has* an index — the machinery is real, mainstream, and does what it says. The Layer-3 escalation — that φ² is the *distinguished* index, the one nature selects — is the part that fails. The direct test (P-005-TL, Temperley–Lieb / Jones closure at index φ²) is a **sound null**: the closure lands at δ=φ (index φ²=2.618) exactly as well as at the controls (√2 index 2, 2cos(π/7) index 3.247, δ=2 index 4), and φ's one nonzero residual is marginally *worse* than the controls'. An earlier v1 metric flaw — measuring roundoff on a structurally-zero eigenvalue — was caught and fixed before this verdict was reported, which is itself part of the discipline: the null was verified, not stumbled into. The machinery is real; φ is not privileged within it. What B-020 *would* have explained, had φ won, is the selection principle itself (OP 3) — why the observer's algebra sits at the minimal admissible index rather than any other. It did not win. Cite B-020 as a bridge-object route (who-can-read-what vocabulary), never as a write-law and never as evidence that φ is distinguished among admissible Jones indices.

### B-021 — Shared-interface / reflected-entropy consensus (§5.18C, OP 164, Addendum V)

The single-observer framework is far stronger than the multi-observer one (§5.18C). B-021 imports holographic quantum-information machinery — reflected entropy and the entanglement-wedge cross-section, with the Dutta–Faulkner theorem S_R(A:B) = 2·E_W(A:B) exact in holographic states — to ask what the *analogue of fusion for observers* is. The honest answer in §5.18C is that τ⊗τ = 1⊕τ is only an analogy; a real two-observer law needs a shared subspace, a consistency constraint, and a repairable-vs-branch-forming rule. The candidate functional (Addendum V) is written form-only, with the architectural scale left as one of five φ-structured candidates and the envelope reverse-engineered "for algebraic convenience, not derived" — two free parameters, so any real prediction must be a dimensionless ratio surviving both choices.

OP 164 (opened in master v0.680) stated the target precisely and, crucially, *pre-registered its own φ-failure criterion*: a quantitative law relating mutual information between observer-patches to shared-interface geometry, "with φ-structured surface tension as governing architectural constant… if no φ role emerges in the proportionality, the invariance hypothesis is weakened." The two-observer test (P-007-2OBS) is a **sound kill at L≤12**: the golden-chain slope is statistically indistinguishable from same-central-charge controls (Ising, XX, Heisenberg), separation 0.18 against a required ≥1.5. No φ role emerged. This directly meets OP 164's own preregistered failure criterion. A larger-L (12, 14, 16) confirmation rerun is in progress; until it lands, B-021 stays a bridge-object candidate and shared-interface *vocabulary only*, treated as a real demotion.

### B-022 — Holographic recoverability / QEC (§8.34A.13, Addendum Q)

The import here is quantum error correction and holographic QEC: TQFT / Chern–Simons / Fibonacci anyons supply a braid-memory grammar, while QEC supplies a recoverable-boundary-memory grammar (§8.34A.13, the TQFT-QEC Observer Boundary Bridge). The proposed toy is the Fibonacci Turaev–Viro Observer Boundary Toy, in which a braid is a written memory, the code subspace is the recoverable self, and rupture is failure of topological error correction. This would explain *persistence under partial access or damage* — why a boundary record survives erasure — using established machinery (Witten, Kitaev, Freedman–Larsen–Wang, Levin–Wen, holographic QEC). Unlike B-020 and B-021, B-022 has not been driven to a golden-vs-control verdict: the Turaev–Viro toy is a scaffold pointer, not yet a scored experiment, so its status is "external machinery imported, φ-claim untested." That untested state is a reason for *more* caution, not less. The section itself carries the explicit guardrail: no Fibonacci holographic code exists yet, black holes do not literally untie knots, and consciousness is not a Fibonacci anyon code. Cite B-022 as recoverability context only — the grammar for how a record persists, with no claim that the persisting record is φ-structured.

### B-024 — Multi-scale FEP / Markov blankets

The import is the free-energy-principle state partition: a Markov blanket splitting internal, external, sensory, and active states (density ρ_MB), extended in the multi-scale FEP literature to nested blankets-within-blankets. This is the best current statistical scaffold for the *observer-side skin* — the private-to-public corridor by which hidden state becomes readable, and the object that makes "no over there" operational rather than slogan-shaped: the blanket is precisely the surface at which there stops being an accessible interior. It supplies observer-boundary vocabulary and, in the consensus functional above, the ρ_MB gradient |∇ρ_MB| that modulates the reflected-entropy envelope. B-024 has no direct φ-test of its own; it is imported as *structure*, not tested as a claim, which is exactly why it must not be over-read. The guardrail is firm: use FEP as boundary and corridor vocabulary only; do not identify the free-energy principle with the final GHP law. FEP is a scaffold for stating the question, not a selection principle that answers it.

### B-025 — The Boundary Access Channel (composite; current best target)

The bridge lab's central finding is that the strongest candidate is *not any single outside theory* but a composite. The working sketch is:

> **O_t = (M_t, N_t, E_t, ρ_MB, R_t, Red_t, S_shared)**

reading, term by term: M_t the ambient algebra, N_t the observer-accessible sub-algebra, E_t the (time-indexed) conditional expectation = finite access (B-020); ρ_MB the Markov-blanket density = observer skin (B-024); R_t recoverability = QEC persistence (B-022); Red_t redundancy across fragments; S_shared the shared-overlap / reflected-entropy consensus measure (B-021). The composite states the actual GHP question at Layer 3: *does the rule by which hidden state becomes finite-access, recoverable, redundant, and shareable select a smaller stable architecture — and is that architecture Fibonacci?* The preregistered test compares Fibonacci branching against binary abelian, generic ternary, and non-Fibonacci non-abelian variants, scored on access fidelity, recovery after erasure, redundancy, shared overlap, macro effective information, and failure under over-compression.

The evidence so far is toy telemetry and is treated as such (T-019 through T-040+). Fibonacci wins the *core channel* score in the swept configurations but loses most *blended* configurations to recycled-return controls, supporting an "anti-locking core plus recycled-return modifier" reading rather than a "Fibonacci wins everything" reading. Per the Operator Guardrail, none of this is physics evidence: it is a toy channel probing whether a boundary-access grammar could in principle favor a smaller architecture. The Boundary Access Channel is the current best composite *target*, explicitly not a derived result.

### B-027 — Aukora governed portal (engineering analogue)

B-027 is the strongest practical *portal* analogue: the Aukora governed-boundary map, in which hidden/private/process state crosses a governed boundary into readable records through identity, grant, scope, effect, receipt, and revocation, with explicit memory-boundary custody. It is genuinely useful for making the portal formalism concrete — what a real write/witness/release boundary must track. It is also, per Addendum O, "echo not evidence." Software success — governed telemetry, the Auma burn, 96%-recall holographic HRR memory — is *never* evidential support for GHP physics. B-027 informs the vocabulary of O_t; it does not confirm it.

### The shape of the bridge stack

Read together, the stack tells one consistent story. Every bridge that touches *dynamics* — the φ²-index closure (P-005-TL), the two-observer consensus law (P-007-2OBS, killing its own OP 164 criterion), the metallic-recurrence zipper (M-005, generic to all metallic means) — has come back generic or killed. What survives is architectural (Fibonacci categorical minimality M-001/M-002, theorem-grade in domain), extremal (Hurwitz: φ the slowest-converging irrational, 1891 mathematics), and engineering (modular write/witness/release, φ-free, confirms only the AU/E-001 reading). φ lives in the architecture, not the dynamics — the master's own founding conclusion (the golden chain lands on tricritical-Ising c=7/10, not φ), now confirmed four independent ways. The Boundary Access Channel is where GHP would, if anywhere, find φ in the *access grammar* rather than the dynamics; that test is built but not decided.

**Status & guardrail:** All six bridges (B-020, B-021, B-022, B-024, B-025, B-027) import real external machinery and name real explananda, but NONE is constructed or closed; the two bridges tested directly returned a sound null (B-020/P-005-TL) and a sound kill against its own preregistered φ-criterion (B-021/P-007-2OBS), the composite O_t=(M_t,N_t,E_t,ρ_MB,R_t,Red_t,S_shared) is a toy-telemetry target not a derivation, and no software or benchmark result (B-027) is ever physics evidence for GHP.

---

## 06. The β-band Physics Lane — DMRG and SYK

This section documents the program's designated falsification lane: the two independent numerical corridors built to test whether φ governs *dynamics*, not just architecture. Both were pre-registered — the decision rule fixed in writing before data — precisely so that a null could not be talked away afterward. As of 2026-07-03, the honest reading is that neither corridor has produced GHP support, and a 2026-07-03 theory audit shows the DMRG band as designed has weak discriminating power. This is reported here in full, because a lane whose failures are hidden is not a falsification lane at all.

### 6.1 What the lane was built to decide

Module C — the "physics spine" of §§5.4–5.7 — makes one sharp empirical commitment: a finite quantum observer with bounded memory and anharmonic dynamics should show revival degradation scaling as Γ ∼ 1/d^β with Hilbert-space dimension d (§5.7, §5.10). Two candidate exponents were placed in opposition from the start:

- **β ≈ 2.0** — GUE (generic Gaussian-unitary) universality. The observer is a real finite system but structurally undistinguished. φ plays no dynamical role.
- **β ≈ φ ≈ 1.618** — critical universality. The observer sits *at* the quantum-classical phase transition, and the golden architecture of §§2–4 shows up in the scaling exponent itself.

The framing is deliberately adversarial to GHP's own ambition: the pre-registered kill window K = [1.95, 2.05] (§5.10A.2) is the generic-observer target, and hitting it fires **Kill Condition 9** (§5.10, §6.2 kill list) — Module C loses its physics spine and the framework retains only its architectural (Module R) and engineering (Module A) content. The pre-registered *pass* band is B1 = [1/φ, φ] ≈ [0.618, 1.618], the magnitudes of the two eigenvalues {φ, −1/φ} of the Fibonacci fusion matrix N_τ (derived theorem-grade in §5.10B via the Verlinde formula). The four-bucket decision rule of §5.10A.6.3 — strong-pass neighborhoods of φ^{±1}, in-band, φ^{±2} boundary, and kill — was frozen before any output was generated.

Two physically distinct systems were enlisted to probe this single number in two different universality routes: a **1+1D golden-chain DMRG corridor** (§5.10A.6) and a **0+1D mass-deformed SYK corridor** (§5.7, §6). Independence is the whole point: if both land in-band, that is convergent evidence; if one lands and the other does not, the framework weakens specifically in the non-landing class (§5.10A.6.5).

### 6.2 The DMRG corridor: pre-registration, telemetry, and the 2026-07-03 discriminating-power problem

The golden-chain test (§5.10A.6, ledger **P-002**) is specified down to the grid: the Feiguin–Trebst–Ludwig–Troyer–Wang Fibonacci-anyon chain (PRL 98, 160409, 2007), whose undeformed antiferromagnetic continuum limit is tricritical Ising with c = 7/10; a relevant mass deformation λ·σ_mass implemented as staggered bond dimerization; DMRG at χ_max = 400 over L ∈ {24, 48, 72, 96, 120}; a fixed eight-point λ sweep with log-ratio 1.5; and a linear-in-1/L extrapolation of the fitted exponent with bootstrap error bars (§5.10A.6.7). Pre-registration timestamp 2026-04-22T06:53Z, committed in `.epsilon/research/D2_oscillation_band/D2_BAND_PREREG_v2.md`.

The first TeNPy telemetry (§5.10A.7, v0.701) was honest about being messy: L=24 clean as a sanity check, but L=48 and L=72 showed negative-gap artifacts diagnosed as DMRG sector-ordering pathology, with a suggestive near-critical gap collapse at L=72, λ≈0.0675. Per discipline, no exponent was extracted from artifact-bearing gaps; a sector-preserving rerun was mandated (§5.10A.8) and **OP 184** opened to ask whether the positive-gap points yield a β(L) fit inside the band. The current sector-preserving rerun stands at **7 of 9 hardened points clean, the two heaviest (L=72, L=96 at λ=0.2278125) still computing**.

The decisive development is a **2026-07-03 theory audit** (recorded in ledger P-002). Reading Feiguin et al. 2007 carefully, the mass deformation used here couples to the tricritical-Ising **σ′ operator** (scaling dimension Δ = 7/8, ≈85% confidence), which predicts a standard-CFT null exponent **β_null = 8/9 ≈ 0.889** — and 8/9 sits *inside* the pre-registered band [1/φ, φ]. This is the crux: **the band as designed contains the standard-CFT null.** An in-band DMRG result would therefore confirm known 2007-era conformal field theory, not GHP. The genuinely anomalous outcome — the only one that would discriminate — is a result clustering near φ = 1.618, well separated from 8/9 and from the runner-up candidate 5/4. The band's *lower* half is exactly where boring, expected CFT physics lives.

This is not a new failure mode; it is a recurrence. The master already contains the identical exercise on the *sister* operator ε′ (dim 6/5, giving ν = 5/4 = 1.25, likewise inside the band) in Addenda **AE.8 and AE.9**. AE.8 draws the sharp line: the band bounds a *fusion-channel* exponent β_fusion (derived from the N_τ spectrum), which is a **different quantity** from any CFT correlation-length exponent ν. That 5/4 falls inside [1/φ, φ] is flagged there as **coincidental** — both happen to involve small integers and φ — not as the band predicting 5/4. AE.9 logs a "suggestive post-diction" giving 1.236 within 1.1% of 5/4, then immediately disowns it: the channel-exponent assignment is non-unique (alternatives give 1.412, 1.764, 1.328), and matching a pre-known CFT number is post-hoc, not prediction. The band still has **no operational bridge to a measured exponent** — that gap is **OP 179**, and it remains open.

The corrected verdict wrapper, `syk/golden_chain_dmrg/rerun_sector_preserving/verdict_v3.py`, enforces this discipline mechanically: it requires full-grid completeness, a real 95% bootstrap CI, both pre-registered decision rules (the §5.10A.6.3 point-rule and the D2_BAND_PREREG_v2 Option-B CI-rule), and it reports the **distance to β_null = 8/9 alongside the verdict**. Correctly, it *refuses to emit a verdict* while 2 of 9 points are still in flight. When it does run, an in-band pass must be reported as "CFT-consistent, pipeline validated" — never as GHP support.

### 6.3 The SYK corridor: no pre-registered β has ever been computed

The SYK arm (§5.7, §6 "C3: Mass-Deformed SYK Transition", ledger **P-002** sibling) is the corridor the master historically treated as the sharpest test — the "weekend test" (§5.10) reducible to a laptop run at N ≈ 18–22. The measured quantity is the transition exponent ν in mass-deformed SYK₄, even-parity sector, across N = 10, 14, 18, 22. The master's preliminary framing — repeated in §5.7, §5.10, and §6.0 — was "**ν trending above 0.618 toward 0.7**," with §6 adding that the four-size data favor ν closer to 0.7 than to 1/φ, which would *falsify the original ν = 1/φ prediction*. Addendum **M.1** (and **OP 111**) then added a disciplined fourth branch: a stable ν ≈ 0.7 landing in the tricritical/quotient lane "may count as **quotient-confirmation** rather than failure" — Module C weakened, not killed. This is a legitimate pre-registered branch, not after-the-fact rescue, but it must be honestly labeled as a demotion of the strong φ-critical claim.

The 2026-07-03 audit exposes something more basic and more damaging to any claim of a SYK result: **no pre-registered β has ever actually been computed for this corridor.** The pipeline was broken. Ledger **P-002a** records that twelve SYK/C3 scripts hardcoded a stale path (`/Users/peterviviani/EPSILON/`, now an unrelated Next.js project) instead of the real working tree; all twelve were fixed and syntax-verified 2026-07-03. Worse, the N=22 40-seed hardening run (tight7×40) **died mid-seed**, and its κ grid no longer brackets the crossing; N=10 is banned from official fits by the project's own doorway note yet the pre-registration is written over all four sizes; the ν-scaling-collapse bootstrap is **degenerate** (ν pegged at the grid ceiling); and **no script exists that converts a collapse-ν into the pre-registered β_crit or applies the decision buckets.** The "ν trending toward 0.7" language, in other words, describes a preliminary that the current pipeline cannot even reproduce cleanly, let alone certify against the band.

The honest status of the SYK corridor is therefore: **the pass side is vacant** — there is no computed, pre-registered β to evaluate — and **the meaningful commitment is the kill window.** Kill Condition 9 remains live and well-defined: a stable in-K result would demote Module C. Everything on the pass side awaits a repaired pipeline, a completed N=22 run, and a written ν→β conversion protocol satisfying OP 179's operational-definition demand. Until then, no SYK number may be reported as GHP support in either direction.

### 6.4 Reading both corridors together

Placed side by side, the two arms tell one story. The DMRG band, as designed, is dominated on its lower half by the standard-CFT null (8/9), so only a φ-clustered result would be anomalous — and the heaviest points that could reach toward φ are exactly the ones still computing. The SYK arm has never produced a certifiable pre-registered exponent, and its only firm content is a kill window. In neither corridor has a golden-vs-control comparison come back favoring φ dynamics. This is fully consistent with the program's founding architecture-vs-dynamics lesson (§§3–4): the golden chain's *own* dynamics flow to tricritical-Ising c = 7/10, **not** to φ. Every dynamical φ-probe in the wider 2026-07-03 battery (the two-observer consensus kill P-007, the metallic-recurrence null M-005, the TL/φ² sound null P-005) points the same way. φ lives in the architecture and in extremality (Hurwitz), not in the measured dynamical exponents — which is the master's own conclusion, now reached from the falsification lane as well.

None of this touches the categorical layer. Kill Condition 9 and any in-band-null on either corridor demote only the §5.7 *critical-observer* claim; Fibonacci minimality (§2.1, ledger M-001), the golden-chain architecture (§3.2), the c≈7/10 residue, and Hurwitz maximal irrationality (§5.4) all survive by the master's own preserved kill table (§5.10A.4). The operational rule from that table governs the entire lane: *φ remains architecture-facing unless and until a distinct dynamical derivation forces it back* — and no such derivation has arrived.

**Status & guardrail:** The DMRG corridor is 7/9 clean with 2 heavy points pending, but its band contains the standard-CFT null β_null=8/9, so as designed it has weak discriminating power and only a φ≈1.618 result would be anomalous (P-002, §5.10A, AE.8/AE.9, OP 184); the SYK corridor has *no* pre-registered β ever computed — pipeline repaired 2026-07-03 but the run is incomplete, the bootstrap degenerate, and no ν→β converter exists — so its only meaningful commitment is the kill window (P-002/P-002a, §5.7, §6, M.1/OP 111, Kill Condition 9); every result is to be evaluated by `verdict_v3.py`, an in-band DMRG pass reported as "CFT-consistent, not GHP," and no SYK number reported as support in either direction.

---

## 07. The 2026-07-03 Test Battery — four fresh verdicts

On 2026-07-03 the program ran a five-test battery against fresh exported snapshots and preregistered contracts. Four of those tests reached a defensible verdict; the fifth (the SYK corridor audit) is treated in §08. The four verdicts are: one sound null (P-005-TL), one sound kill (P-007-2OBS), one sound engineering pass (T-WWR-modular), and one sound null (M-005). Read plainly, three of the four came back against a phi-dynamical reading, and the one pass is phi-free engineering. That is not a disappointing session; it is the session working exactly as designed. Every result below was locked to a numeric kill-or-pass rule *before* the run (see `experiments/TL_phi2_PREREG_v1.md`, `experiments/MODULAR_WWW_PREREG_v1.md`), and two of the four had a first-version method flaw caught and refused before any number was reported. That refusal machinery is the point of this section, so we lead with it.

### The credibility engine: two tests caught cheating and killed before report

The battery produced its most important result about *itself*. Two of the four tests were built, run, and then found — by adversarial re-verification, not by the original author's charity — to be measuring an artifact rather than the claimed quantity. Both were rebuilt and only the honest v2 numbers appear in the ledger.

First, the TL/phi^2 closure test (P-005). The v1 closure-quality metric was reading floating-point roundoff on a *structurally zero* eigenvalue — the Jones–Wenzl projector p_4 vanishes identically at delta=phi ([4]_delta = 0 there by construction), so the "residual" v1 was scoring was numerical dust on a quantity that is exactly zero as a theorem. A metric that measures roundoff will happily report whatever the conditioning of the day gives you, and could have been dressed as a phi signal. It was caught, the eigenvalue's structural-zero status was logged as *expected* (the prereg had pre-committed to exactly this degeneracy at §1.2), and v2 re-derived the comparison on a well-posed conditioning metric. Second, the modular write/witness/release test (T-WWR-modular). Its v1 quantum substrate was inert — a unitary-only channel that never left the maximally-mixed state, so the "memory" being stressed was not evolving at all — and its contradiction stream was tautological (perfectly antipodal payloads that any policy trivially separates). Both flaws would have manufactured an easy, meaningless pass. v2 replaced the substrate with a genuine CPTP dissipative channel and the contradiction stream with a non-tautological partial-cosine generator, and was independently reproduced.

The meta-point, stated without ornament: the verification machine caught two of its own tests cheating and refused to report them. A program that only shows you its clean runs is indistinguishable from a program that discards its dirty ones. This one shows the dirty runs and the surgery. That is the credibility engine — not any single verdict, but the demonstrated willingness to kill a favorable-looking result on method grounds before it reaches the ledger.

### P-005-TL — TL / phi^2 conditional expectation: SOUND NULL

The Temperley–Lieb / Jones conditional-expectation machinery is real and closes cleanly. The phi^2 Jones index (index = delta^2 = 2.618, the Fibonacci/A4 fusion category) is a genuine finite-access algebraic object, and it is the bridge-object route B-020 has always pointed at. The test asked the sharper question the prereg forced: does phi *close better* than admissible controls? It does not. The machinery satisfies Pimsner–Popa and Markov consistency equally well at delta=phi and at sqrt2 (index 2, Ising/A3), at 2cos(pi/7) (index 3.247, A6), and at delta=2 (the series boundary). Crucially, phi is *not* the minimal index — Ising's index 2 sits below it — so any "phi is special because its index is small" claim was forbidden at the outset. On the closure-quality metric, phi's one nonzero residual came out marginally *worse* than the controls', not better. The prereg's H0 held and H1 was killed by its own locked margins.

The honest reading: B-020's finite-access conditional-expectation route is real machinery, not numerology, and it remains a legitimate bridge-object vocabulary. But phi is not distinguished *within* that machinery. Closure quality tracks index magnitude and category depth, not the golden ratio. This is a null, reported as prominently as any pass, and it is exactly the null the prereg predicted it would most honestly be. It is worth being explicit about what was avoided: because phi's defining quantum integer [4]_delta is exactly zero, a naive report could have recovered "index = phi^2 = 2.618" or "1/index = 2 - phi" and paraded arithmetic as discovery. The prereg pre-labeled both as circular sanity checks, forbidden from H1 support, precisely so that a recovered definitional identity could never be mistaken for a phi signal. The v1 flaw was the same trap wearing a numeric disguise, and the discipline is what caught it.

### P-007-2OBS — two-observer consensus: SOUND KILL

This is the sharpest result in the battery because it answers a question the program asked of *itself* years earlier. Open Problem 164 (opened in master v0.680, §8.34A.8) posed a quantitative law relating the mutual information between two observer-patches to their shared-interface geometry, with a phi-structured surface tension as the governing architectural constant — and it wrote its own falsification clause: *"if no phi role emerges in the proportionality, the invariance hypothesis of §8.34A.4 is weakened."* The two-observer consensus test is the direct empirical instrument for that clause. By exact diagonalization at L<=12, the golden-chain mutual-information / reflected-entropy scaling slope was compared against Ising, XX, and Heisenberg CFT controls, all normalized by central charge so the comparison is fair. The golden slope is statistically indistinguishable from the same-central-charge controls: separation 0.18 against a required 1.5. No phi role emerged.

By OP 164's own preregistered criterion, this is a kill. B-021 (the shared-interface / consensus functional bridge object) may not be promoted beyond bridge-object-candidate on the strength of this — it is a real demotion. A larger-L confirmation run (L = 12, 14, 16) is in progress to close the low-L caveat, but the L<=12 verdict is already clean enough to state as a kill rather than a hint. The program set a trap for its own central invariance hypothesis and the hypothesis walked into it.

### T-WWR-modular — modular write/witness/release: SOUND PASS (engineering)

The one positive in the battery, and it is carefully bounded. On a genuine dissipative modular-flow channel, a ternary boundary-update policy (write / witness-quarantine / release) beat both a binary policy and two fair degenerate-ternary controls (random-third, rate-matched-binary) — but *only* on contradiction-handling. Pollution came in at 0.15 for ternary against 0.50 for binary, with the paired advantage holding in 10 of 10 seeds and a 95% CI excluding zero. On the other three regimes (delayed-meaning, overload, concept-drift) ternary was null. That per-regime honesty is the tell of a real result: a policy that wins everywhere is usually cheating, and the prereg specifically required ternary to *not lose* on retention or pollution anywhere for the win to count.

The reading is bounded by the prereg's own §8.5 numerology clause: this run contains no phi, no Fibonacci, no golden structure anywhere in the Hamiltonian, the update rule, or the metrics. It is phi-free engineering telemetry. It confirms the existing AU / E-001 reading — hybrid selective witness as an optional, targeted quarantine mechanism, not a universal memory law — and it discovers nothing new about phi. Per the Operator Guardrail and Addendum O, this is echo, not evidence: a software policy beating another software policy is never evidential support for GHP physics, and this pass is filed strictly as engineering.

### M-005 — metallic-recurrence genericity: SOUND NULL

The "zipper" sign-alternation behavior — the NegaFibonacci backward sign-alternation once floated as an observer write-law image — turns out to be generic to the entire metallic-mean family. Under exact integer and Decimal arithmetic, re-derived by three independent agents, the golden (delta=1), silver (delta=2), and bronze (delta=3) recurrences all show identical backward sign-alternation, forward sign-stability, and the same seed-dependent mirror structure. There is no phi-specific content in the zipper. The only phi-specific fact that survives this neighborhood is Hurwitz extremality (Hurwitz 1891, master §5.4 / §1522): phi is the slowest-converging irrational, the hardest to approximate rationally — genuine 1891 mathematics, correctly credited, and the sole surviving phi-specific dynamical-adjacent fact. NegaFibonacci sign-crossing is not a write-law, not a selection mechanism, and not evidence the observer sits at a privileged F_0 = 0 boundary.

### The shape of the four verdicts

Read together, the battery repeats the master's own founding lesson four independent ways. Every phi-*dynamical* claim tested here came back generic (P-005, M-005) or killed (P-007). Everything that survived is *architectural* (Fibonacci categorical minimality M-001 / fusion rule M-002, theorem-grade within domain), *extremal* (Hurwitz, 1891), or *engineering* (T-WWR-modular, explicitly non-evidential). The same reading disciplines the DMRG beta-band test (P-002, §08): a 2026-07-03 theory audit (Feiguin et al. 2007) found the mass deformation couples to the tricritical-Ising sigma-prime operator (dimension 7/8), predicting a null exponent beta_null = 8/9 ~ 0.889 that sits *inside* the preregistered band [1/phi, phi]. So an in-band DMRG result would confirm known 2007-era CFT, not GHP — only a result clustering near beta = phi = 1.618, well separated from 8/9, would be a genuine anomaly. That recurs an earlier identical exercise on the sister operator epsilon-prime already in the master (AE.8 / AE.9), and it is a standing reminder that an in-band exponent is never, by itself, GHP support. This is the recurring result of the whole program, now sharpened: phi lives in the architecture, not the dynamics. The three-layer discipline holds — (1) reality accessed only as boundary records is solid mainstream; (2) boundary-first ontology is a live, respectable research bet held not proven; (3) GHP's specific bet that the readable boundary's minimal architecture is Fibonacci is precisely where every *dynamical* test, including these four, has come back generic. The architectural layer is where the surviving content sits.

**Status & guardrail:** Of the four 2026-07-03 verdicts, P-005-TL and M-005 are sound nulls (machinery real, phi not privileged), P-007-2OBS is a sound kill meeting OP 164's own preregistered phi-failure criterion, and T-WWR-modular is a sound engineering pass (phi-free, echo not evidence per Addendum O); two v1 method flaws were adversarially caught and killed before report, and no result here is claimed as physics evidence for GHP.

---

## 08. The Observer-Memory Program — Golden Zipper and Boundary Access Channel

This section distills roughly three months of local toy-model work: the Golden Zipper observer-memory sequence (ledger T-005..T-018, versions v4 through v66) and the Boundary Access Channel (ledger T-019..T-080, versions spanning the branch-family, rescue, repair, and switcher lanes). It is the longest continuous empirical arc in the program. It is also, deliberately, the arc where the phi-specific hypotheses were tested to destruction. What follows reports the arc's shape and its honest conclusion — not every version — and states plainly which claims survived and which did not.

This is engineering phenomenology, not physics. Nothing below is evidence for any GHP physical claim. Per the Operator Guardrail and Addendum O ("echo, not evidence"), a toy-model comparison that a branching family wins is a fact about the toy, never about the world. The value here is different and real: these toys sharpen the *shape* of the questions — what a finite observer-boundary would have to do to write, hold, and recover a durable record — and they discipline us by killing the tidy phi-uniqueness story we would have preferred to find.

### 8.1 The Golden Zipper: what memory the toy actually rewarded

The Zipper arc began as a search for a golden write-mechanism and became, honestly, an inventory of what helps recall in a small memory toy and what does not. Two clean positives survived repeated reruns and stand as the arc's strongest signal.

First: **relational, groove-style memory beats isolated storage.** Across the knot-slot and path-phase groove families (T-006, T-007), storing an identity as a *relation held in a groove* — a trace carrying its own path history and its position relative to neighbors — recalled more reliably than storing it as an isolated, point-like value. Field *presence* mattered more than field *shape* (T-010): removing the relational field hurt, but the specific geometry of the field was largely interchangeable, and a flat local smoothing nearly matched the full field (T-018). The lesson is non-point structure, not a privileged shape.

Second: **recall works best when context tints the same groove.** Region-first, context-conditioned recall (T-008) recovered identity more reliably than time-indexed lookup; time helped as an echo, not as identity. Nested observer windows plus a moderate prediction-error band ("moderate mismatch beats exact-match," T-012, T-013) formed the cleanest local rule. The field-memory sub-lane (T-011) added that *binding* and *nested multiscale windows* both help, while shuffled phase and field-shape specificity stay weak — and when the full field-stack was tightened (T-017, T-018), hierarchy-specific gains collapsed toward parity once extra stacked and local variants were allowed. The robust package is "some relational field, held across nested windows, tinted by context," not any one privileged binding geometry.

Plasticity and rewrite layers (T-014, T-015, T-016) were a genuine *negative*: in these implementations, plastic, reconsolidating, or frame-recoloring recall did not beat rigid storage. We report that as prominently as the positives — a program that only advertised its wins would not be trustworthy, and this program's credibility is precisely its willingness to log the rewrite layers that failed.

Crucially, **exact golden uniqueness did not survive.** No version isolated phi as *the* write-mechanism. The most defensible reading of phi in this arc, carried into the master's Addendum AT.3, is that phi functions as an **anti-locking core / background** — the most resistance-to-rational-locking ratio in KAM/continued-fraction intuition — *not* a direct write-point. phi is where the flow does not collapse into perfect repetition; it is not the thing that decides what gets written.

### 8.2 The Boundary Access Channel: Fibonacci as core-channel family, not universal winner

The Boundary Access Channel (B-025) was built to make a fair comparison: Fibonacci branching against binary, generic ternary, and non-Fibonacci controls, scored on access, recovery, and redundancy under a finite observer's bounded view. The arc's honest verdict is layered.

On the **core-channel package** — the normal-flow lane where a bounded observer reads a legal, current interface — **Fibonacci is the most stable family under access + recovery + redundancy** (T-019..T-021, T-045, T-046, T-048). It won the core score in every tested config and across every tested seed in the integrated dual-cost harness, surviving both access costs and repair-switch costs. This is the closest thing the arc produced to a durable Fibonacci-favoring result, and it is why the branch family is worth keeping in the vocabulary at all.

But it is emphatically **not a universal winner.** Two systematic exceptions were mapped carefully:

- **Return is not a free upgrade.** Once recycled wake actually re-enters the channel with decay (T-022..T-025), Fibonacci *no-return* beat Fibonacci *return* on the core score in every tested regime. Gated and event-triggered return (T-026..T-028) never beat no-return on the core; under explicit damage, a plain **stale-memory / continuity fallback** beat Fibonacci-structured rescue (T-028, T-029). Rescue depended on retained wake continuity, not on branch structure.

- **Generic ternary wins the high-noise and wrong-signal lanes.** In turbulence, Fibonacci leads at low noise but **generic ternary takes over from the mid-noise regime onward** (T-047, T-048), stable across all tested seeds. The crossover was mapped to a fuzzy shoulder near noise 0.20–0.40, not a knife-edge, and it survived rescue-policy changes, marking it as a branch-family effect rather than a policy artifact (T-051..T-053). Hardening then narrowed *why*: the handoff is specific to **internal-contradiction damage** — uniform-smear and *wrong-signal* corruption (rolled, reversed, permuted internal scramble) favor ternary, while *coherent cross-family* wrong-signal returns the win to Fibonacci (T-054..T-058). Ternary looks tuned to internal contradiction, not to foreign structure as such. This is the same signature the modular write/witness/release lane found independently (§ on Aukora / E-001, ledger T-004): ternary's edge is a *contradiction-handling* edge, and it is phi-free.

### 8.3 The switcher lane: a chooser exists, but not a one-line law

The most interesting late object was not a branching family but a **switcher**: can a bounded observer decide *which* repair geometry to use — coherence-tether vs contradiction-scrubber — from local boundary symptoms alone, without illegal access to hidden truth? A linear probe on local-only features reached ~0.89 held-out accuracy (T-059), and a groove-aware "does it fit the current song or press into a knot" pack reached ~0.928 (T-062), surviving red-team checks for helper-alignment leakage (T-063). The chooser appears real and portable across noise worlds (T-064).

The discipline showed twice. Label-free clustering did **not** cleanly recover the two regimes on its own (T-065): the chooser looks more like a trained object than a self-evident split in feature space. And a "rank-shape" repair that seemed to rescue every hard lane near-perfectly was **demoted** by an adversarial rank-matched control (T-069..T-071) — the miracle was reading the toy's own damage-generator, not a general law. What survived rank-matching was a weaker but honest *order-plus-flow* signal (T-072, T-073) and a specialized *integration-capacity* alarm for coherent-foreign flow that needs gating rather than fusion (T-075..T-080). No single scalar captured the chooser (T-066); it needs roughly five to six local axes (T-067). The arc ended pointing at a "pause / refetch" sentinel for the rows where neither repair head is reliable (T-080) — a live object, not a closed one.

### 8.4 What the arc means, and the layers it must not blur

The value is a research direction in **engineering phenomenology of a finite observer-boundary**: relational memory over isolated memory; context-tinted recall; Fibonacci as a stable core-channel family; generic ternary for internal contradiction; a learnable-but-multifactor repair chooser. These are honest, comparative, control-anchored findings about toys.

They must not be smuggled across the three layers the program keeps separate. Layer 1 — reality accessed only as boundary records — is solid mainstream. Layer 2 — boundary-first ontology — is a live, respectable research bet (Wheeler, RQM, QBism), held not proven. Layer 3 — that the readable boundary's minimal architecture is *specifically* Fibonacci — is GHP's own bet, and this arc is exactly where its *dynamical* form came back generic: phi read as anti-locking background, not write-point; Fibonacci won a core lane but lost the noise and wrong-signal lanes; and the independent metallic-genericity null (M-005) plus the OP-164 two-observer kill (P-007, meeting that OP's own pre-registered phi-failure criterion) confirm the same verdict from other directions. phi lives in the *architecture* (categorical minimality M-001/M-002, Hurwitz extremality), not the *dynamics* — the master's founding conclusion, and this arc is its most sustained honest test.

**Status & guardrail:** PROVEN nothing physical here; ESTABLISHED as toy-model engineering phenomenology that relational-groove memory beats isolated memory, that context-tinted recall is strongest, that Fibonacci is the most stable *core-channel* family under access+recovery+redundancy while generic ternary wins high-noise/internal-contradiction lanes, and that a multifactor repair-chooser is learnable; KILLED the claims of exact golden write-uniqueness and of any universal Fibonacci win — phi reads only as anti-locking background, and none of this is or may be cited as GHP physics evidence (Operator Guardrail; Addendum O; ledger T-005..T-080; master Addendum AT.3, §5.361/OP 164).

---

## 09. The Matter-Embedding Lane — D4 to E6, honest obstructions

This lane asks the sharpest question that can be asked of any boundary-first program: if reality is accessed only as boundary records, and the readable boundary's architecture is discrete, can any *non-arbitrary* discrete structure carry Standard Model matter — gauge groups, charges, chirality, generations — without hand-labeling? The honest answer developed across ledger rows T-117..T-125 (probes MEB-001..MEB-009, master §5.18D, §10A.1) is: **no derivation exists**. What exists is a mathematical scaffold that gets progressively less arbitrary, with two genuinely positive representation-theoretic results and, just as prominently, a string of constructive *obstructions* that killed the easy hopes. This section reports both. The framing throughout is the master's own §5.18D "Matter Embedding Gap [major open bridge]": this is scaffold, explicitly **not** physics.

### The 24-cell / D4 scaffold is real but too symmetric (T-117, T-118)

The starting object is the 24-cell — the unique self-dual regular 4-polytope, whose 24 vertices are the roots of the D4 root system. MEB-001 (T-117) established that this is not an arbitrary choice of 24 points: against random 24-point controls, the D4 roots pass root integrity, exact 4D isotropy, minimum-separation, noisy-shear label stability, signed-permutation equivariance, and low D4-near quantization error — six for six. So the 24-cell earns its place as a *candidate discrete label alphabet*. That is the entire positive claim, and the tempting "12 fermion + 8 gluon + 3 weak + 1 Higgs = 24" counting in §10A.1 is flagged in the master itself as **not a derivation**.

MEB-002 (T-118) then ran the first demotion. Asking whether D4 hands you Standard-Model bookkeeping without labels, the probe found 16 algorithmic A2-like ("color-like") sub-root systems, but the stricter, honest A2 + A1 + rank-1-residual decomposition under the exact root-subsystem rule **failed** — 2 of 5 checks passed. The nontrivial color-like scaffold is there; the direct SU(3)×SU(2)×U(1) map is not established.

### The chirality obstruction — the load-bearing negative result (T-119, T-120)

The strongest result of the whole lane is a *negative* one, and it is genuinely constructive. Chirality — the left/right asymmetry of the weak interaction — is the crux of any matter embedding. MEB-003 (T-119) showed the bare D4/24-cell scaffold is **too symmetric to generate it**: central symmetry, reflection closure, near-zero chirality imbalance, orientation-breaking necessity, and toy symmetry cancellation all pass (5/5) *as an obstruction*. Every root has its antipode; the structure is centrally symmetric by construction, so no intrinsic handedness can live in it. MEB-004 (T-120) closed the obvious escape: naive orientation-breaking rules (Weyl-chamber, spinor-axis, random-axis, best-of-random) are either still *choiceful* — you put the asymmetry in by hand — or they destroy the antipodal/cancellation structure you needed (5/5 as obstruction).

The lesson is exact and worth stating plainly: **a symmetric root crystal cannot produce chiral fermions by itself.** Any real matter bridge needs an *additional* orientation-breaking mechanism — a projection, a boundary condition, or a dynamical/categorical sector — that the geometry alone does not supply. This is the single most useful thing the lane has produced, precisely because it forecloses a class of overclaims a less disciplined program would have made.

### F4 is a better alphabet, still non-chiral (T-121, T-122)

F4 is the principled next scaffold: D4 plus a second dual layer of 24 roots, reflection-closed and antipode-clean. MEB-005 (T-121) confirmed F4 as a real upgrade — better than bare D4 on a toy nearest-root coverage metric (6/6) — so as a *boundary alphabet* it is strictly stronger. But MEB-006 (T-122) delivered the second demotion in the same shape as the first: natural F4-root quotient projections keep the scaffold readable but remain **non-chiral**, and halfspace cuts that would force chirality **destroy** the antipodal/cancellation structure (6/6). A bigger, cleaner crystal buys a better alphabet and buys *no* matter. The obstruction is stable across scaffolds — it is a property of centrally-symmetric root systems, not of D4 specifically.

### E6 and the 27 — the first clean representation-level bookkeeping (T-123, T-124, T-125)

The obstructions pointed to a specific conclusion: the problem is not "a bigger root crystal," it is that *roots are the wrong data*. MEB-007 (T-123) confirmed this threshold. E6 is a serious exceptional scaffold and contains the D4/24-cell corridor internally, but E6 *roots alone* remain centrally symmetric and non-chiral, and halfspace cuts still fail the chirality-plus-cancellation discipline (6/6). Roots, at any rank, do not solve matter embedding.

The first genuine signal appears one level up, in *representation* (weight) data. MEB-008 (T-124) verified that the E6 minuscule **27**-weight orbit is non-self-conjugate, has an exact conjugate **27**-bar partner, sums to zero total weight, has uniform norm, and a compact inner-product signature (6/6). Non-self-conjugacy is the first structural feature in the lane that even *rhymes* with a matter/antimatter distinction — though the master is explicit that this is bookkeeping, not physical chirality, and that the 27 weights are not particles.

MEB-009 (T-125) is the strongest current result. Using an explicit inverse-Cartan complement charge — a *rule*, not a hand-label — the E6 **27** branches into **16 + 10 + 1** blocks across the two conjugate D5-like complements. Crucially, this passed against controls: a naive-coordinate control does **not** produce the split, random integer charge maps did not hit it in the tested sample, and the conjugate **27**-bar carries the opposite charge signature (6/6). This is real representation-theoretic bookkeeping with the right control structure. And it must be read with the master's own guardrail intact: 16 + 10 + 1 is the *known* branching of the E6 27 in grand-unified representation theory, textbook material where the 16 is an SO(10) spinor slot. **The probe recovers standard mathematics under a disciplined rule; it does not derive SO(10) physics, a Standard Model generation, hypercharge, anomaly cancellation, particles, or matter.** No dynamics selected E6, no dynamics selected the 27, and nothing in the lane connects any of this to the golden-boundary hypothesis that is the rest of the program's subject.

### Where this sits in the three-layer picture

Nothing in this lane touches Layer 3 (the specific Fibonacci bet) — it is pure exceptional-Lie-theory scaffolding that would read identically under any boundary ontology. It is best understood as an *architecture* exercise: a search for the least-arbitrary discrete alphabet the readable boundary could use, conducted honestly enough to publish its obstructions. The 24-cell is non-arbitrary; symmetric crystals cannot chiralize; the 27's 16+10+1 branching is clean bookkeeping. That is the whole honest yield. Consistent with the program's overall shape (§5.18D remains a named open gap), the *architectural* facts here survive and every step toward *physics* has been correctly demoted or deferred, never claimed.

**Status & guardrail:** *Proven* — the D4/24-cell is a non-arbitrary discrete label alphabet (MEB-001), symmetric root systems (D4, F4, E6) cannot generate chirality by themselves (MEB-003/004/006/007, a constructive obstruction), and the E6 minuscule 27 branches cleanly to 16+10+1 under a controlled rule (MEB-008/009). *Conjectured/deferred* — any bridge from this scaffold to actual matter, which the master lists as the open Matter Embedding Gap (§5.18D). *Not claimed anywhere* — no Standard Model gauge group, charge, generation, hypercharge, anomaly cancellation, chiral fermion, or particle is derived; this lane is mathematical scaffold, not a physics derivation.

---

## 10. The Engineering Lane — Aukora, Auma, and holographic memory

**The governing rule, stated first and repeated at the end.** Everything in this section is software. It is the strongest *practical* analogue we have built of a governed observer-boundary — a system in which private process crosses into public record under an explicit law — and it is *categorically not evidence for GHP physics*. This is not a hedge; it is the master's founding discipline (Addendum O: "software echoes may inform the theory, sharpen its variables, and reveal design consequences; they do not confirm the physics"). A working benchmark tells you the engineering is sound. It tells you nothing about whether nature uses the same law. We report this lane because good engineering scaffolding sharpens what a formal boundary write-law must *satisfy*, and because a program that hid its most impressive-looking results would be less honest, not more — but the Operator Guardrail holds throughout: no software success is ever evidential support for the physics.

### 10.1 The Aukora governed portal

Aukora (ledger B-027, master AG.4A) turns observer-boundary language into a bounded software architecture that can be attacked locally. The clean translation is four rules: the model *proposes*, the kernel *authorizes*, the *receipt* decides what became durable, and memory updates *only* from verified boundary contact. The load-bearing invariant is **propose-not-authorize**: the reasoning layer never grants itself effect. Every crossing carries identity, grant, scope, effect, receipt, and revocation. This is a governed portal in the literal engineering sense — hidden/private/process state crosses into readable records only through a receipt-bearing membrane — and it is exactly the kind of finite-access, memory-boundary discipline the GHP boundary object *would* need at the mathematical level. That structural rhyme is why the lane exists. It is not a reason to believe the rhyme is physical.

Crucially, Aukora is where GHP-shaped claims go to be *falsified*, not confirmed. The lane's value is that failure is cheap and informative: it sharpens the boundary object. Under that discipline, most of GHP's more romantic software claims died here — latency-as-carrier, Fibonacci cadence windows, write-shockwave aftereffects, the full "Shear Engine" — each demoted for failing controls (master AY.4). What survived is narrow and buildable.

### 10.2 HRT public telemetry: predicts boundary mode, cannot reconstruct authority

The Horizon Radiation Trace (HRT) work (ledger E-002, T-099..T-110; master Addendum AY) narrows the governed boundary to one survived, preregistered invariant:

> public trace → boundary mode, while public trace ↛ private state and public trace ↛ authority.

In plain terms: safe public telemetry can describe *what kind* of boundary event occurred — write, witness, or release — while remaining unable to recover the hidden interior or grant/predict legal authority. The measured result under adversarial holdout (BTA-001): boundary-mode prediction reaches action-F1 **0.7624** against a shuffled control of **0.3333**, while private-state reconstruction sits at **0.0230** and authority reconstruction at **0.0730** — both near chance. The test's honesty check is instructive: when the probe was allowed to cheat by reading raw private fields directly, private reconstruction jumped to **0.8750** (HRT-001) — which is exactly why the allowlist sanitizer and recursive forbidden-field scanner are load-bearing, not decorative. The invariant holds only because leakage is mechanically prevented, not assumed. The witness footprint is not dead space: it registers as an active held-tension plateau (WPF-001, action-F1 0.9983, private 0.0272), consistent with "witness" as unresolved quarantine rather than null trace. The Accord promotion lattice (T-108..T-110) then hardens the handoff: typed telemetry may be logged as *evidence* for later analysis, but the recursive firewall rejects every private/authority fixture with **zero authority leaks**, and there is no read-path from telemetry into gate authorization. The build law is deliberately modest: **build a boundary stethoscope, not a gate.**

This is a genuinely strong engineering result — a public boundary can be made informative about its own mode while staying provably uninformative about its secrets and its permissions. It is precisely the separation of *readable projection* from *hidden interior and authority* that a boundary-first ontology asks for. And it is still telemetry. It supports no claim about Markov blankets, Hawking radiation, entanglement-wedge cross-sections, holography, or the write-law (master AY.8). Timing is secondary evidence at most; the "boundary mode" it predicts is a software receipt category, not a horizon.

### 10.3 Auma: weights are stance, memory is tools

The Auma 32B work grounds the same discipline in a live model architecture. The organizing distinction is **weights = stance, memory = tools**: the model's trained weights hold disposition and skill, while durable, situation-specific knowledge lives outside the weights in a governed memory organ that the model queries through tools rather than absorbs into itself. This matters because it keeps the authority law enforceable — memory can *suggest*, synthesis can *draft*, a verifier can *reject*, and Aukora authority decides. Nothing benchmark-derived becomes weights; nothing recalled becomes authority. The memory dojo (T-082 lineage, skunkworks lab) confirmed the unglamorous engineering lesson repeatedly: plain lexical recall is insufficient, a trained semantic *perceiver* layer is needed, and contradictory-but-valid receipts require a third gate keyed on current state, active head revision, and time corridor. The surviving contribution is the ternary write/witness/release memory discipline (E-001 / T-004), which beats binary handling *specifically on contradiction* (pollution 0.15 vs 0.50, 10/10 seeds) and is null elsewhere — φ-free engineering that confirms the existing AU/E-001 reading and, again, is not physics evidence. An 8-model fusion review (`ghp_aukora_mega_mind_fusion_review`) returned unanimous YELLOW: the architecture is genuinely advanced, every guarantee is self-attested, and it is correctly scoped as "ready for disabled shadow-import *review*" — not import, not promotion. That is the discipline working: an impressive artifact held at arm's length until independently reproduced.

### 10.4 The holographic HRR memory result

The one place this lane produces a clean, preregistered, confirmed *positive* is holographic memory (skunkworks_holographic_memory; HRR per Plate 1995, SDM per Kanerva 1988 — established mathematics, correctly credited, not a GHP invention). Key-value pairs are bound by circular convolution into a single superposition trace and recalled by correlation plus cosine cleanup against a 256-item codebook. Pass/fail criteria were written and frozen *before* any output. The headline: the **hologram-cut test**. Zero out half the trace (fraction f = 0.5) and recall accuracy is still **0.9609**, versus **1.0000** with the trace intact — a 96% ratio, with a smooth SNR-limited decline and no cliff (max single-step drop 0.33), exactly as SNR ∼ √((1−f)·d/k) predicts. Capacity scales as k\*₉₀ ∝ d/ln(d) (R² = 0.986, beating linear d), and crosstalk rises monotonically with codebook similarity. All three predeclared criteria pass: **HOLOGRAPHIC PROPERTIES CONFIRMED (engineering).**

Ninety-six-percent recall from half a memory is a real, reproducible property of distributed superposition storage, and it is the natural candidate for a **fourth Kira perceiver** — a memory organ whose recall degrades gracefully rather than shattering, sitting alongside the existing perceiver stack as governed, advisory, shadow-mode-only. But note precisely what is confirmed: that a specific well-known encoding is robust to erasure. The word "holographic" here is the information-theoretic sense of Plate's HRR, *not* a claim that the universe stores itself this way (Addendum O, item 7, states this exactly). Recoverability-under-damage is real machinery (ledger B-022); it is imported as recoverability context only.

### 10.5 What this lane does and does not license

Locate the claim on the three layers this paper keeps distinct. **Layer 1** — reality accessed only as boundary records — is solid mainstream, and Aukora is a faithful *engineering instance* of it. **Layer 2** — the boundary-first ontology, "no over there" — is the live research bet in respectable company (Wheeler's it-from-bit, RQM, QBism); Aukora *illustrates* how such a boundary could be governed, but illustration is not confirmation. **Layer 3** — that the readable boundary's minimal architecture is specifically Fibonacci — gets *nothing* from this lane. Consistent with the whole program, every φ-flavored dynamical claim here (Fibonacci cadence, φ-timing, φ-sampler storage semantics) came back generic or killed under controls; what survived is architectural (propose-not-authorize, evidence-never-authority), extremal, or plain good engineering (graceful degradation). φ lives in the architecture, not the dynamics — the master's founding conclusion, echoed here a fourth time, in software.

**Status & guardrail:** Aukora's receipt-bearing governed boundary, the Auma weights-as-stance / memory-as-tools discipline, and the 96%-recall-from-half-a-trace holographic memory result are all *confirmed as engineering* and stand as the strongest practical analogue of a governed observer-boundary we have built — and none of them is, or will ever be, evidence for GHP physics.

---

## 11. Methodology — the falsification machine

The physical conjecture at the center of this program — that the readable boundary's minimal architecture is Fibonacci — may not survive. This section argues that it does not have to. GHP's most transferable output is not the conjecture but the machine built to try to kill it. The machine is a stack of interlocking disciplines that turned a sprawling, mythically-framed, multi-year synthesis into something that produces preregistered predictions, records its own failures on the page, and has repeatedly caught its own tests cheating. What follows distills that machine into a reusable protocol. It is drawn from the master's front-matter hard rules, the Operator Guardrail (master §259–266), the §5.19 Self-Sealing Warning, the §5.19A One-Page Kill-Condition Sheet, the Epistemic Discipline Index (master §273–318), and the ledger's Promotion / Demotion / Do-Not-Claim rules.

### 11.1 Preregistration with signed kill windows

Before data, we fix the band, the analysis rules, and the outcome that kills the claim — then freeze all three with a timestamp. The canonical instance is the SYK / golden-chain β-extraction: a preregistered band [1/φ, φ] with an explicit **kill window [1.95, 2.05]** (§5.10A, §5.19A). An in-window result demotes the physical spine on the page, without renegotiation. The rule that gives this teeth is the **anti-rescue clause** (§5.19A): when a kill condition triggers, the demotion is recorded in the section and the changelog; a narrower replacement hypothesis may be opened only with a *new* timestamp and *new* failure criteria. You do not get to move the goalposts after seeing the ball. The corollary, learned the hard way this session, is that a preregistration is only real if its protocol path and version are pinned before the run. The SYK Module-C corridor failed this test: twelve pipeline scripts were found hardcoding a stale path, the hardening run died mid-seed, and no script ever converted the collapse exponent into the preregistered β. The verdict in the ledger is blunt — *no preregistered β has ever actually been computed for this corridor* (P-002a). That honesty is the point: an unfired kill window is worth more than a fired one that was never really loaded.

### 11.2 No-upgrade sentences

Every hardening pass in the master ends with the same litany: *No prior content removed. No gate upgrades. No ToE inflation. No physics evidence. No consciousness evidence. No write-law closure.* This is not boilerplate; it is a structural brake. Framework-scale programs die by accretion — each pass quietly promoting last pass's analogy into this pass's evidence — and the no-upgrade sentence makes each increment declare, explicitly, that it changed nothing about status. A pass that wants to promote a claim must say so and meet a threshold (§11.5); silence defaults to no change. This converts the default direction of drift from inflation to conservation.

### 11.3 Adversarial verification

Results are re-derived by independent agents whose job is to break them, and the program treats a suspiciously clean pass as a bug until proven otherwise. This caught two tests cheating in the 2026-07-03 battery. The TL/φ² closure (P-005-TL) passed a v1 metric that turned out to be reading roundoff on a structurally-zero eigenvalue; once fixed, φ closed no better than its controls. The ternary write/witness/release probe (T-WWR-modular) passed a v1 whose substrate was inert — unitary-only, never leaving the maximally-mixed state — over a tautological, perfectly-antipodal contradiction stream; rebuilt with a genuine dissipative channel and a non-tautological stream, it still passed, but now honestly. The earlier "rank-shape miracle" (T-069 → T-071) is the template: a repair that rescued every lane almost perfectly was traced, under a rank-matched adversarial control, to separability the toy's own damage generator had baked in. **A result that looks too good is a claim about your test harness, not about nature**, until an adversary has failed to break it.

### 11.4 Ledger-first, with nulls preserved

The ledger is the unit of record, not the prose. Every object carries an ID, a status, an evidence type, and a next step, and **nulls and kills are logged as prominently as passes** — preserved verbatim as anti-self-sealing evidence (Demotion Rules; R-001a). This is the direct operational form of §5.19: a theory that deletes its failures can always claim its incompleteness is a feature, so the failures stay on the page. The 2026-07-03 state is mostly failures, and the ledger shows all of them: the TL/φ² sound null (P-005-TL), the two-observer sound kill that met OP 164's own preregistered φ-failure criterion (P-007), the metallic-recurrence sound null showing the "zipper" is generic to silver and bronze means (M-005), and the DMRG audit showing an in-band β would merely confirm 2007-era CFT (P-002). A reader can reconstruct the program's honest posture from the ledger alone. That is the test of a good ledger.

### 11.5 Promotion, demotion, and the three do-not-claim layers

Promotion requires crossing a real evidentiary threshold, not sounding coherent: mathematical promotion needs theorem-grade closure inside a stated domain; physical promotion needs a defined bridge object, an explicit failure condition, and support stronger than toy telemetry; engineering promotion needs multi-seed stability and sensible baselines. Demotion fires whenever a cleaner framing shows the claim was too strong. Underneath sits the **three-layer separation** that must never blur: (1) reality is accessed only as boundary records — solid, mainstream; (2) a boundary-first ontology, "no over there" — a live research bet in respectable company (Wheeler's it-from-bit, relational QM, QBism), held, not proven; (3) that the boundary's minimal architecture is specifically Fibonacci — GHP's own bet, where every *dynamical* test has come back generic or killed. The Do-Not-Claim list enforces the boundaries between these layers one violation at a time (do not claim toy telemetry is physics; do not claim an in-band CFT exponent confirms GHP; do not claim the write-law is solved).

### 11.6 The numerology tripwire and the sycophancy signal

Two guards protect against the failure modes most fatal to a φ-themed program. The **numerology tripwire**: φ appearing in a formula is never content; content exists *only* in a golden-versus-control comparison where the golden case measurably separates from matched controls. This is what converted the metallic-recurrence "zipper" and the TL/φ² closure from apparent wins into honest nulls — the controls kept pace. The **sycophancy signal**: the author runs six models in parallel, and *universal agreement across them is a sycophancy signal, not validation* (front-matter; §5.21). Five models agreeing is a reason to look harder for what they all missed, not to flatten the disagreement. External numerical rankings ("8.9/10", "top-3 ToE") are declined in their entirety (Addendum S), and the Operator Guardrail forbids any software, benchmark, or training success from ever supporting a physics claim (§261). Engineering that works — the governed-boundary telemetry, the 96%-recall holographic memory — is "echo, not evidence" (Addendum O).

### 11.7 Time-boxed demotion

Finally, the machine has a clock. The §5.19 expiration conditions are permanent and dated: if by April 2028 no functor connects two proven obstruction domains, the unification claim downgrades from conjecture to analogy; if by April 2027 no numerical estimate exists for the holographic decoherence threshold, that prediction downgrades to qualitative speculation. A conjecture that cannot buy indefinite deferral is a conjecture that can lose.

Taken together these seven disciplines are the reusable contribution. They are what let this program report, without flinching, that in the 2026-07-03 state every φ-*dynamical* claim came back generic or killed while everything *architectural*, *extremal*, and *engineering* survived — and to treat that asymmetry as the finding rather than a disappointment. The falsification machine outlives the conjecture it was built to test.

**Status & guardrail:** The methodology is GHP's most transferable output and holds regardless of the physical conjecture's fate; the machinery (preregistration with signed kill windows, no-upgrade sentences, adversarial verification, ledger-first null preservation, the numerology tripwire, three-layer separation, sycophancy guards, and time-boxed demotion) is proven-useful engineering discipline — it caught two tests cheating this session and is not itself evidence for any GHP physical claim.

---

## 12. Open Problems and the Discriminator Roadmap

### 12.1 The single strategic gap

Every preceding section reports the same shape of result. Fibonacci survives as *architecture* (categorical minimality M-001, fusion rule M-002; master §2.1), as an *extremal* fact (Hurwitz slowest-converging irrationality; 1891 mathematics, §5.4), and as *engineering* (governed-boundary telemetry, holographic memory recall). Every claim that φ governs *dynamics* has come back generic or dead. This is not an accident of which tests we happened to run. It is a structural property of the test battery, and naming it precisely is the most important thing this section does.

**The gap:** GHP currently has no test whose numerical prediction differs from standard physics. Every pass-region we have ever pre-registered *contains the standard-physics answer inside it.* Three examples make this concrete:

- **The DMRG β-band (P-002, OP 184).** The pre-registered band is `[1/φ, φ] = [0.618, 1.618]`. The 2026-07-03 theory audit (Feiguin et al. 2007, *PRL* 98 160409) established that the mass deformation couples to the tricritical-Ising σ′ operator (dimension 7/8), which predicts `β_null = 8/9 ≈ 0.889` — *inside* the band. So an in-band result confirms known 2007-era CFT, not GHP. Only a value clustering at `β ≈ φ = 1.618`, cleanly separated from 8/9 and from the runner-up 5/4, would be a genuine anomaly. This exactly recurs the earlier sister-operator exercise on ε′ (dim 6/5 → 1.25) already logged at master AE.8/AE.9.
- **The φ² Jones-index closure (P-005-TL).** The conditional-expectation machinery closes cleanly at index φ² — but it closes *equally cleanly* at √2, at 2cos(π/7), and at δ=2. The machinery is real; φ is not privileged inside it (§6).
- **The two-observer consensus law (P-007, OP 164).** The golden-chain mutual-information slope was statistically indistinguishable from same-central-charge controls (separation 0.18 against a required 1.5). This met OP 164's own pre-registered φ-failure criterion, and is a **sound kill** at L≤12.

In each case the honest reading is that the standard-physics null lives inside the region we would have called a pass. A test that cannot fail when standard physics is right cannot support GHP when GHP is right.

### 12.2 The discriminator criterion

The response is a hard budget rule, stated once and enforced everywhere downstream:

> **No new compute is spent on any test whose pass-region contains the standard-physics answer.**

This retires most of the historical pipeline. The DMRG β-band, having been shown to contain `8/9` inside `[1/φ, φ]`, is **no longer a discriminator** — the two heaviest points (L72, L96) may finish for completeness and pipeline validation, but any in-band result must be reported as "CFT-consistent, pipeline validated," never as GHP support (master §5.10A.6.3; ledger P-002). The φ²-index closure is retired as a discriminator for the same reason. The two-observer law is retired *by its own kill*. What survives the criterion is a much shorter list, and it is organized around a single observation: **the only place φ has ever survived is architecture, and the sharpest architectural observable available to us is recoverability.**

### 12.3 The top candidate: Fibonacci boundary-code recoverability

The one open test that is genuinely discriminating is master **AH.4 Priority 1** — the Fibonacci boundary-code recoverability test.

Construct an explicit finite boundary code from Fibonacci fusion data: an encoding map, a logical subspace, a physical boundary alphabet, a recoverability criterion, and a threshold-failure criterion. Then damage it and measure how well it recovers. Compare, under identical damage and identical stated constraints, against matched non-Fibonacci finite alphabets, generic anyon categories, and simple stabilizer / tensor-network toy codes.

- **Success:** Fibonacci structure arises as minimal, uniquely robust, or threshold-favorable — a Fibonacci code recovers from damage *better than* matched non-Fibonacci controls.
- **Failure:** Fibonacci appears only by manual insertion, or shows no recovery advantage.

This is the right candidate for exactly one reason. **Recoverability is an architectural observable.** It is not a dynamical exponent (where φ died four times), not a spectral quantity (where the standard null sits inside every band), and not a benchmark score (which the Operator Guardrail forbids as evidence regardless). It asks a question about the *structure* of the code — the only layer where φ has ever earned its place. And crucially, there is no reason to expect the standard-physics answer to sit inside a golden-vs-control recovery comparison: a generic stabilizer code has no privileged relationship to φ, so a robust Fibonacci margin over matched controls would be a result standard physics does not already predict. This is the first test in the program whose pass-region plausibly *excludes* the standard null.

The design discipline is inherited from the surrounding open problems: recoverability preservation and non-tautological φ-introduction are already specified as closure conditions in the compression-map program (master OP 187), and the recoverability grammar itself is imported as external machinery only (B-022, master Addendum V §V.3). Content must live entirely in the *golden-vs-control comparison* — never in the appearance of φ in isolation.

### 12.4 The concrete next experiments, in priority order

The following is the committed roadmap. It is ordered by how directly each item can produce a number that differs from standard physics — the discriminator criterion applied as a ranking function.

1. **Fibonacci boundary-code recoverability (AH.4 Priority 1; the flagship).** Build the code, damage it, and race it against matched non-Fibonacci alphabets, generic anyon codes, and stabilizer/tensor-network toys under a pre-registered recovery metric and threshold. This is the one test whose pass-region does not contain the standard null. It absorbs and sharpens the earlier Boundary-Access-Channel toy sequence (ledger T-019 through T-080), which repeatedly found Fibonacci acting as an "anti-locking core" but never under a clean, pre-registered, damage-and-recover protocol against matched controls. **This is where new compute goes.**

2. **The SYK Module C corridor kill window (P-002 sibling; OP 111).** This is the *only other* window whose result genuinely means something, because no pre-registered β has ever actually been computed for it. The pipeline was broken — twelve scripts pointed at a stale, unrelated directory (now fixed, 2026-07-03), the N=22 seed run died mid-seed, the ν-collapse bootstrap is degenerate (ν pegged at the grid ceiling), and no ν→β conversion script exists. First fix the pipeline; then compute a real β under the OP 111 decision branch, which was written precisely to handle a stable ν≈0.7 result without either silently losing it or lazily overclaiming it. The corridor's kill window is real *only* if the standard null can fall outside it — this must be checked against the same σ′/8-9 audit that retired the DMRG band before any compute is committed.

3. **OP 3 / OP 157 — derive the selection principle rather than assume it (master OP 3, OP 157; AH.4 Priority 5).** Reframe selection in fixed-point / category-aware language so Fibonacci is picked out *by constraints*, not by preference — a discrete candidate space, an admissibility criterion, a minimality functional, and a comparison against nearby categories. OP 157 (derive Postulate P) is the dynamical half of the same problem; its P1/P2 sub-postulates are scaffold-level (months of subfactor verification), while P3/P4 remain multi-year (master §5.10C, U.3). This is a *theory* track, not a compute track: it costs derivation, not GPU-hours, and so is unconstrained by the discriminator budget.

4. **OP 164 — the shared-interface functional, as theory only (master OP 164; U.2; AH.4 Priority 2).** The two-observer *numerical* test is killed (§12.1). What remains open is whether the reflected-entropy / Markov-blanket bridge `S_R(A:B) = 2·E_W(A:B) = f(ρ_MB, σ_φ)` admits a form in which φ enters as a non-trivial proportionality, extremum, or stability condition rather than definitionally. Pebble 1 (master Addendum AA) currently leaves the architectural scale ambiguous among five φ-structured candidates. No new consensus-simulation compute is warranted; the work is to derive the functional, and any φ-free result re-opens OP 3 from a second direction.

5. **OP 184 — close out the DMRG band for the archive, not for evidence.** Let the two heaviest sector-preserving rerun points finish, apply both pre-registered decision rules (master §5.10A.6.3 point-rule and the D2_BAND_PREREG_v2 Option B CI-rule), and report the `β_null = 8/9` distance alongside the verdict. Any in-band pass is logged as CFT-consistent and pipeline-validating. This item is *bookkeeping*, included so the frozen master's β-band commitment is honestly retired rather than left dangling.

The larger-L confirmation runs already in flight — two-observer at L∈{12,14,16} (P-007) and the DMRG heavies — are completions of already-decided results, not new discriminators. They close the record; they do not change the strategy.

### 12.5 What would actually move the program

A single clean win on item 1 — a Fibonacci code that recovers from matched damage measurably better than its non-Fibonacci controls, under a pre-registered margin, reproduced across independent seeds — would be the first result in GHP's history that standard physics does not already contain. Nothing else on this list has that property. That is why recoverability, and not any dynamical exponent, is where the next real compute is spent. The rest is theory (items 3–4) or archival honesty (items 2, 5). The program's founding lesson — φ lives in the architecture, not the dynamics — is now confirmed four independent ways (P-002, P-005-TL, P-007, M-005), and the roadmap is simply that lesson taken seriously: stop testing φ where it has already died, and test it in the one layer where it has always lived.

**Status & guardrail:** The strategic gap (no test where GHP's prediction differs numerically from standard physics; every pass-region contains the standard null) is **established**, and the discriminator criterion (no new compute on tests whose pass-region contains the standard-physics answer) is **committed**; the Fibonacci boundary-code recoverability test (master AH.4 Priority 1) is **the single active discriminator and unrun** — everything else on the roadmap is either a theory-track derivation (OP 3/157/164) or archival close-out of results already killed or retired (P-005-TL, P-007, OP 184); no software, benchmark, or toy-telemetry result on this roadmap is ever evidence for GHP physics.

---

## Appendix

### A. Do-Not-Claim rules (carried verbatim from the master archive)

Do not claim: toy telemetry is physics evidence · software success validates GHP · symbolic or cross-tradition material is proof · an in-band conformal-field-theory exponent confirms GHP · a SYK β result exists before a traceable, audited run and pinned preregistration · a result is pre-registered without a pinned preregistration path and version · the Viviani-φ Horizon proves GHP · the Ricci toy proves GHP · Markov trace logic forces Fibonacci · the Fibonacci Markov kernel proves physical selection · memory creates the external world · the write-law is solved · ternary witness is a universal memory law · φ uniquely wins the observer-memory toys · Golden Zipper toy telemetry is physics evidence · science-spirituality, myth, meaning, qualia, or the hero's journey proves the physics · breath practice, Tao, I Ching, Kabbalah, or Buddhism is scientific proof · the consciousness-container conjecture has been achieved · Aukora software success opens a literal reality portal, proves agent consciousness, or upgrades the Ring-0 ceremony before the live hard gates are exercised · D4/F4/E6 root systems derive Standard Model matter, chirality, or generations.

### B. Verified literature spine (what each source does and does not support)

The full annotated spine lives in the ledger (`LIT-*` rows). Its governing rule: *no paper enters the proof chain unless it supplies a theorem, derivation, bridge object, or falsification path directly relevant to a stated GHP claim.* Category-theory sources (Rowell–Stong–Wang; Edie-Michell) support categorical minimality but not physical selection. Operator-algebra sources (Kosaki; Fewster) support the conditional-expectation/split-property machinery but not a write-law. Holographic-QI sources (Dutta–Faulkner reflected entropy; and successors) supply shared-interface vocabulary but not a consensus law. QEC sources (Verlinde–Verlinde; Parikh–Verlinde) supply recoverability context but not Fibonacci or GHP. GR prior-art sources (Cruz-Olivares–Villanueva; Coelho–Herdeiro) support the Viviani-φ surface as prior-art-consistent but not as a horizon. Analogue sources (trapped-ion Fibonacci drive; acoustic cavitation/sonoluminescence) are cited strictly as external analogues with surrounding metaphysics quarantined.

### C. Provenance and the sunset

This document and `GHP_CORE_v2.md` were assembled 2026-07-03 by distilling the research master and the claim ledger. The master (`GHP_v1_618_MASTER.md`) is frozen as the append-only archive; the earlier core share paper (`GHP_CORE_SHARE_PAPER.md`, core-v0.023) is superseded and banner-marked. The distillation rule was: **nothing left behind** — every claim, null, and kill in the archive is carried into this working paper or the ledger. An archive claim not reflected in the canon is a bug to be flagged, not a silent omission.

Two integrity notes recorded during assembly: (1) a `LIT-C001` (Carr 2022) reference added earlier was lost to a multi-writer race during the 2026-06-23 master-consolidation commit and has been restored to the ledger; (2) one master range (~lines 12000–13500) failed to distill on its first swarm pass and warrants a targeted re-read for completeness — noted here rather than silently omitted.

### D. What would change these conclusions

The physical spine falsifies if the SYK β lands cleanly in the kill window [1.95, 2.05], if the recoverability discriminator shows Fibonacci codes with no advantage over matched non-golden codes, or if categorical minimality is shown misapplied to the physical setting. It gains real (non-decisive) support only from a *discriminating* observable — one where GHP's prediction differs from the standard one and the data favor GHP. As of 2026-07-03, no such discriminating result exists, and building the experiment that could produce one (§12) is the program's first priority.

---

*The Golden Horizon Principle is a conjecture under test, an engineering practice under governance, and a methodology under no illusions. Held together, honestly, that is more than most frameworks ever earn.*
