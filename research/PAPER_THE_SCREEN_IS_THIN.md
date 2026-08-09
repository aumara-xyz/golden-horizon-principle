# The Screen Is Thin

### Five boundary objects, one skeleton, and what a governed record actually remembers

**Peter Viviani (AUMARA) with Claude · v2, 2026-08-09**
**Status:** research note. Every claim carries a class. Nothing here is physics evidence.
Classes: **EM** established mathematics · **EP** established physics · **IM** implemented and
measured · **EH** engineering hypothesis · **PM/PO** product / poetic metaphor · **UN** undetermined.

---

## 0. Before the notation

A **screen** is an interface that stands between what you cannot reach and what you can, such that
everything reaching you passes through it. Light cones, black-hole horizons, Markov blankets, the
minimal memory of a predictive process, and an access-controlled record all look like that idea.
They are the same object, and this paper's finding is that **the object is thin** — it carries no
geometry, no thermodynamics, and no preferred constant.

**Thin is a result, not a shortfall.** A unification that entailed physics would be enormous and
would also be false; what is actually shared is a conditional-independence criterion, and every
instance's interesting content is added on top, in mutually incompatible ways. Naming the shared
part precisely is what lets you stop mistaking rhyme for mechanism.

**We claim no physics here.** No experiment in this program has a pass-region excluding the
standard answer. What we do claim: one definition, two theorems, five axes, one measured example
from a live system, a certification law that limits what any two observers can prove to each other,
and — new in v2 — the observation that the screen as usually written cannot express a boundary that
*acts to remain a boundary*, which is precisely the case we care most about.

*(New in v2: §1.4 the active half · §3.1 the blanket fails informatively · §5 the two formalisms
reconciled · §6.3 the day-invariant budget promoted · §8b misreadings this paper invites.)*

---

## 1. The screen

**Definition (EM).** For a joint system with parts P (withheld), B (interface), F (accessible),
B is a **screen** iff

> **S1** I(P ; F | B) = 0

Strengthenings, each earned separately: **S2 minimality** (every B′ satisfying S1 admits
deterministic g with B = g(B′) a.s.); **S3 symmetry** (S1 in both directions — the blanket
condition); **S4 ε-screen** (I(P;F|B) ≤ ε).

### 1.1 The five instances

| instance | status | acts? |
|---|---|---|
| ε-machine causal states | **S1 + S2 by theorem.** Past ⊥ future given the causal state; minimal and a.e.-unique among prescient rivals. Shalizi & Crutchfield, *J. Stat. Phys.* 104:817 (2001). **EM** | no |
| Markov blanket — **Pearl sense** | **S1 + S3 by definition.** A statistical property of a joint distribution; boundary uniqueness needs the intersection property. Pearl (1988). **EM** | no |
| Markov blanket — **Friston sense** | The same condition carried by a *dynamical* system with the interface split into sensory and active states (§1.4). **Not the same object as Pearl's** — conflating them is a documented error (Bruineberg, Dołęga, Dewhurst & Baltieri, *BBS* 45:e183, 2022). **EM/contested** | **yes** |
| light cone / domain of dependence | **deterministic S1.** Data on a Cauchy slice determines the solution on its domain of dependence. **EP**, textbook | no |
| black-hole horizon | **S4, not S1 — the instance that leaks.** §3. **EP**, setting-conditional | no |
| access-controlled record | **S1 iff every write path is mediated.** Measured: 0.086 nats with one bypass open, 7.6×10⁻⁷ nats fenced. **IM**, calibrated model | **yes** |

### 1.2 Four axes

1. **Direction** — one-way vs two-way.
2. **Minimality** — only causal states satisfy S2.
3. **Exactness** — exact (S1) vs leaky (S4). Every physically realised instance we examined is S4.
4. **Maintenance** — how the screen is held in place: by **dynamics** (light cone), by **statistics**
   (Pearl blanket), or by **enforcement** (executable refusals). The third appears unrepresented in
   the literature and is the only one with a hard falsifier at engineering timescales.

### 1.3 A fifth axis, from a live control system

**State-dependence** — a screen whose permitted budget varies with the system's own operating mode
(a resource-governed system may permit self-modification while healthy and only observation while
degraded). **EH.**

### 1.4 The active half — and what it costs the definition

**S1 describes a passive interface.** It constrains what information crosses B and says *nothing
about who writes B*. Two systems can both satisfy S1 while differing completely in whether the
interface is written by P, by F, or by itself.

The free-energy-principle literature carries the missing structure in its notation: the blanket is
partitioned

> **b = (r, a)** — **sensory** states r, influenced by external but not internal states, and
> **active** states a, influenced by internal but not external states.

Three consequences, stated in order of confidence:

**(i) This is a decomposition of the object, not a new axis (EM).** B = (r, a) refines *what the
interface is*, orthogonally to any property of the flow across it.

**(ii) It induces a sixth axis: does the screen act? (EH)** Is a ≠ ∅? This is **not** a refinement
of axis 1. Direction asks which way information crosses; the active half asks which side holds
write-authority over which part of the interface. Axis 1 *constrains* it — a strictly inward
one-way screen has a = ∅ necessarily — but does not determine it: two-way does not imply acting.
The axis discriminates our instances non-trivially: only the Friston blanket and the record act.

**(iii) The unification with axis 4 is real but PARTIAL, and we report the negative half.**
Enforcement-maintenance **requires** active states — a refusal is an internal-state-driven change
to what exists externally, so a screen held in place by refusals has a ≠ ∅ necessarily. **The
converse fails.** An organism has active states and is maintained by non-equilibrium dynamics, not
by refusals; a thermostat acts and enforces nothing in this sense. So

> **enforcement-maintained ⊊ active.**

The differentia is self-reference: under enforcement, **the active states are themselves typed,
recorded entries in the very record the screen governs.** A refusal is not merely a state change;
it is an event carrying a reason, written to the chain the law protects. A cell membrane's ion
pumps act without logging their own pumping into a record that the membrane then protects.

This is a partial unification, not a merge: axis 4's third value *refines* the sixth axis rather
than coinciding with it. We state it as such because the alternative — announcing that our two
contributions are secretly one — would be exactly the promotion-by-rhyme this paper warns against.

*Live instance, from this paper's own production: while writing it, the governing law refused two
of the authoring process's own write attempts, and each refusal was itself committed to the chain
as a receipt. The screen acted, and its action entered the record it protects.* **IM.**

---

## 2. What the skeleton does not carry

The screen contains no null structure, no area law, no temperature, no Clausius relation, and no
preferred constant. The cleanest demonstration is Jacobson's 1995 derivation of the Einstein
equations "as an equation of state" (*Phys. Rev. Lett.* 75:1260). It is theorem-grade **conditional
on six assumptions** (**EP**): local Lorentz invariance; the Unruh temperature; entropy strictly
proportional to horizon area with a single universal constant η; heat as boost-energy flux; the
Clausius relation δQ = T dS on *every* local Rindler horizon; and local energy-momentum
conservation. The output fixes G = 1/(4ħη) and leaves Λ, in Jacobson's own words, "as enigmatic as
ever." Remove any assumption and gravity does not appear.

**The generalisation (EH):** in every instance the payload is in the added structure, and the
additions are incompatible in kind — null geometry, non-equilibrium dynamics, and executable
refusals do not belong to one theory. A "boundary law of nature" read off the shared skeleton would
be promotion-by-rhyme.

---

## 3. The famous one leaks

Classically a horizon annihilates the interior→exterior channel outright. Quantum-mechanically, in
controlled settings (JT gravity with a non-gravitating bath; doubly-holographic braneworlds), the
island formula

> S(R) = min ext [ Area(∂I)/4G + S_semicl(R ∪ I) ]

makes the radiation's fine-grained entropy follow the unitary Page curve: interior degrees of
freedom end up **encoded** in the exterior (Penington 1905.08255; Almheiri–Engelhardt–Marolf–
Maxfield 1905.08762; replica wormholes 1911.11977, 1911.12333; review *Rev. Mod. Phys.* 93:035002).
**EP**, setting-conditional.

Three fences, because this result is routinely overread. It licenses **no causal escape** and **no
white hole** — encoding is not transport. Its extension to evaporating 4D black holes in flat space
is **conjectural**. And it does not settle the infalling observer's experience.

**The consequence for the typology:** the exemplar screen is S4, not S1. **S4 should be the
primitive and S1 the idealisation** — every real screen has a leak rate, and a screen claim without
(rate, ensemble, per-unit) attached is unfinished.

### 3.1 The blanket fails too, and that is support rather than an omission

The instance classed **exact-by-definition** also fails in practice, and the failure is the second
independent line of evidence for treating S4 as primitive. Real out-of-equilibrium systems
generically violate the blanket condition: solenoidal (divergence-free, probability-current) flows
break the required conditional independence unless parameters are fine-tuned. See the critique
literature on the free energy principle's particular-physics claims. **EM/contested — see §9 on
citation status.**

Two corrections to how this is usually framed:

- **FEP is not restricted to biology.** Its non-equilibrium-steady-state formulation claims any
  system that resists dissipation, which is a claim about physics generally. **That universality
  claim is itself live and contested** — which is precisely what the critiques dispute. State both
  halves or neither.
- **FEP is not a special case of the screen, and the screen does not generalise FEP.** The blanket
  is S1+S3 — a *strengthening* — and FEP carries dynamics, a variational objective, and an
  interpretation of internal states as parameterising beliefs, none of which the screen has. We
  treat it as **an instance that fails informatively**: not validation, not subsumption.

**No basins, no attractors.** Causal states are equivalence classes of histories, not points in a
continuous space that settle into basins; attractor-dynamics tests do not apply to them, and this
paper contains no 27-state machine to run such a test on. Recorded because the suggestion has been
made to us twice.

---

## 4. Observation is compression; generation is decompression

"Intelligence is compression" has a theorem-grade core only in the incomputable limit (Solomonoff
1964; Kolmogorov's invariance theorem) — at finite resources it is a heuristic (**PO**).

Its popular dual, "**observation is decompression**," is **false as stated**, and the error is
directional. In every standard formalism of perception-as-coding — Barlow efficient coding, the
Information Bottleneck, predictive coding — **the observer is the encoder.** The phrase has exactly
one exact reading and it inverts the agent: an optimal entropy decoder driven by fair random bits
emits exact samples from the model at ≈ H(p) bits per sample (Knuth & Yao 1976; Han & Hoshi, *IEEE
TIT* 43:599, 1997). **Generation is decompression; observation is compression** (**EM**).

The surviving sentence: *the world decompresses; the observer compresses; the record is where they
meet.* (**PO**, pointed the right way.)

---

## 5. Two observer formalisms, reconciled

This program also carries an observer tuple **O_t = (B, X_t, H_t, S, Q)** — law surface, current
state, committed history, pinned semantics, and the reference relation. How does it relate to
S1–S4?

**They are different kinds of object, and the tuple is the weaker one.** The tuple is a *list of
components*; the screen is a *criterion*. S1 is therefore **a property the tuple's B may or may not
have**, not a restatement of it — and it is testable, which is the whole point: we tested it and
got 0.086 nats versus 7.6×10⁻⁷.

**We decline to promote the tuple to primary.** A conditional-independence criterion can fail; a
list of labels cannot. Only the first kind of object earns a place in a research program.

§1.4 partly closes the gap: the tuple's **Q** — the reference relation, the outward-facing query
function — is where the tuple meets the screen's **active half a**. Queries and refusals both cross
outward. That is a structural correspondence, not an identity, and we leave it there. **EH.**

---

## 6. A measured screen

We reconstructed the ε-machine of a live governed system's append-only receipt chain — every action
and every refusal, hash-linked, ~10⁴ events — under preregistered protocols with kill conditions
fixed before each run.

| quantity | value |
|---|---|
| statistical complexity C_μ | **≈ 2.7–2.9 bits** |
| entropy rate h_μ | **≈ 0.59 bits / event** |
| recurrent causal states | **19–24** |
| held-out predictive gain vs order-0 | **~1.7 bits / symbol** |

The machine matches or beats raw order-3 context prediction held out (0.894 vs 0.910 bits/symbol).
**IM.**

### 6.1 The growth was the instrument

The apparent growth of memory with history length was **estimator bias, and we proved it** — by
generating synthetic data from our own fitted 24-state machine, a system whose true state count is
known, and reproducing the same growth. Calibration against a known-answer system (the golden-mean
shift: exactly 2 causal states, h = log φ) passed to four decimals. **IM.**

### 6.2 Out-of-time transfer

A machine fitted on the frozen past predicts the following ~6,000 unseen events at 0.90 bits/symbol
against 1.71 for the marginal, but trails a machine fitted on those days by 0.12 — mild drift. The
stream also carries structure beyond the fitted machine at 10⁴ events. **IM.**

### 6.3 A day-invariant budget with churning content

**The closest thing in this corpus to a novel empirical claim.**

| day | C_μ (bits) | recurrent states |
|---|---|---|
| 1 | **2.8889** | 13 |
| 2 | **2.8827** | 25 |
| 3 | **2.8823** | 39 |

The *size* of the boundary memory held to the third decimal across three days while the *inventory*
of states tripled. Candidate reading: **the law surface sets the memory budget; the session spends
it.**

**One system over three days is not an invariant.** Registered falsifier, fixed before the data
that would test it: at ≥ 3×10⁴ events, per-day C_μ must stay within ±0.3 bits while per-day state
counts vary by more than 2×, or the reading dies. A known instrument defect must be repaired first
(the shuffle-calibration ladder does not scale with sample size). **UN.**

---

## 7. The method is the result

Seven times in this program — three of them in the work reported here — an instrument was caught by
its own controls **before** its output was cited: a roundoff on a structurally-zero eigenvalue; an
inert quantum substrate; a Merkle verifier that trusted prover-supplied path directions; two
topological-memory instruments that failed their own sanity gates; a shuffle control that
over-split under skewed marginals and killed the hypothesis it was meant to defend; a preregistered
fit window that caught a lattice transient; and a phase-lock test whose tolerance saturated so
completely that its verdict had to be voided rather than reported.

**The self-catch rate is the most reproducible finding in the corpus, and it is the reason any other
number here deserves belief.** A research program's real output is not its positive results. It is
the rate at which it destroys its own.

---

## 8. What we are not claiming

φ enters this program only as **extremality**, never as selection: it is the irrational least well
approximated by rationals (Hurwitz 1891) and the minimal expansion among hyperbolic torus
automorphisms — the *slowest possible* mixing, with silver and bronze analogues that mix faster.
Every dynamical-selection test this program has run has returned null, kill, or generic. That is
recorded as our central negative result, not a footnote.

We claim no physics. **No experiment yet exists in this program whose pass-region excludes the
standard answer** — and a test that cannot lose cannot inform.

## 8b. Misreadings this paper invites

Each of these has been produced by a reader, most of them by language models given the abstract
without the paper.

1. **That "thin" means incomplete.** Thin is the finding. A shared skeleton that entailed physics
   would be a much larger claim and a false one.
2. **That the shared skeleton licenses a boundary law of nature.** §2: the payload is in the added
   assumptions, and they are incompatible in kind.
3. **That the island formula licenses transport, or a white hole.** §3: encoding is not escape.
   Nothing exits.
4. **That the receipt chain is a Page curve.** It is not. The chain is a C-lane measurement of one
   log; no entropy of Hawking radiation appears anywhere in it.
5. **That observation is decompression.** §4: the direction is inverted, and the correct version is
   already a theorem about entropy decoders.

**On how misreadings propagate.** One model, given only a summary, invented section titles this
paper does not contain and protocols it could not run — including a request to derive Lorentz
invariance from a receipt chain. A second pass then built a formally typeset specification *on top
of the first hallucination*, complete with LaTeX and section numbering. Apparent credibility rose
while evidence went to zero. We record it because the lesson generalises past this paper:
**detail is not evidence.**

---

## 9. Citation status

Anchors for §3.1 (the FEP particular-physics critiques and the NESS universality formulation) were
being verified against primary sources at the time of this revision and are marked
**UNDETERMINED** rather than stated with false precision. The Pearl/Friston blanket distinction
(Bruineberg et al., *BBS* 45:e183, 2022, DOI 10.1017/S0140525X21002351) is verified. Readers should
treat any §3.1 citation not carrying a DOI here as pending. A widely recommended FEP bibliography
repository was last updated in mid-2021 and predates the entire critique literature above; it is
useful for classical orientation and not for this argument.

---

*No-upgrade sentence: nothing in this note is physics evidence; no software result validates any
physical claim; no verdict here grants authority; membership is not occurrence; signing is not
world-truth; the beautiful parts remain beautiful and the receipts remain the territory.*
