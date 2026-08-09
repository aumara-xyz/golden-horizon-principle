# The Screen Is Thin

### Five boundary objects, one skeleton, and what a governed record actually remembers

**Peter Viviani (AUMARA) with Claude Fable 5 · 2026-08-09**
**Status:** research note. Every claim carries a class. Nothing here is physics evidence.
Classes used: **EM** established mathematics · **EP** established physics · **IM** implemented and
measured · **EH** engineering hypothesis · **PM/PO** product / poetic metaphor · **UN** undetermined.

---

## 0. The one-paragraph version

A light cone, a black-hole horizon, a Markov blanket, an ε-machine's causal-state partition, and an
access-controlled record all look like the same idea: *an observer meets the world at a boundary,
and what crosses is all there is to know.* They are the same object — a **screen** — and the object
is **thin**. Two of the five are theorems; the rest are instances. The skeleton carries no geometry,
no thermodynamics, and no preferred constant. Everything that makes each instance interesting lives
in structure added on top, and those additions are mutually incompatible in kind. The most famous
member, the horizon, is the one that **fails** to be a screen once you take quantum mechanics
seriously. We give the definition, the four axes that separate the instances, one measured example
from a live governed system, and the certification law that limits what any two observers can ever
prove to each other.

---

## 1. The screen

**Definition (EM).** For a joint system with parts P (withheld), B (interface), F (accessible),
B is a **screen** iff

> **S1** I(P ; F | B) = 0

Strengthenings, each earned separately: **S2 minimality** (every B′ satisfying S1 admits
deterministic g with B = g(B′) a.s.); **S3 symmetry** (S1 in both directions — the blanket
condition); **S4 ε-screen** (I(P;F|B) ≤ ε).

**The five instances, with honest status:**

| instance | status |
|---|---|
| ε-machine causal states | **S1 + S2 by theorem.** Past ⊥ future given the causal state; minimal and a.e.-unique among prescient rivals. Shalizi & Crutchfield, *J. Stat. Phys.* 104:817 (2001). **EM** |
| Markov blanket | **S1 + S3 by definition.** Pearl (1988); boundary uniqueness needs the intersection property (holds for strictly positive distributions). **EM** |
| light cone / domain of dependence | **deterministic S1.** Data on a Cauchy slice determines the solution on its domain of dependence. **EP**, textbook |
| black-hole horizon | **S4, not S1 — the instance that leaks.** See §3. **EP**, setting-conditional |
| access-controlled record | **S1 iff every write path is mediated.** Measured: 0.086 nats with one bypass open, 7.6×10⁻⁷ nats fenced. **IM** on a calibrated model |

**The four axes that actually separate them** — this typology is the paper's first contribution
(**EH**, a classification, not a theorem):

1. **Direction** — one-way (horizon) vs two-way (blanket).
2. **Minimality** — only causal states satisfy S2.
3. **Exactness** — exact (S1) vs leaky (S4). Every physically realised instance we examined is S4.
4. **Maintenance** — *how the screen is held in place*: by **dynamics** (light cone), by
   **statistics** (blanket), or by **enforcement** (executable refusals). The third is, as far as we
   found, unrepresented in the literature and is the only one with a hard falsifier available at
   engineering timescales.

A fifth axis was added after this typology met a live control system: **state-dependence** — a
screen whose permitted budget varies with the system's own operating mode.

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

**The generalisation (EH):** in every instance, the payload is in the added structure, and the
additions are incompatible in kind — null geometry, stationarity, and executable refusals do not
belong to one theory. A "boundary law of nature" read off the shared skeleton would be
promotion-by-rhyme.

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

**The consequence for the typology:** the exemplar screen is S4, not S1. We take this as evidence
that **S4 should be the primitive and S1 the idealisation** — every real screen has a leak rate, and
a screen claim without (rate, ensemble, per-unit) attached is unfinished.

**A negative result we consider load-bearing (EH):** we attempted to unify the measured leaks —
horizon encoding, an access bypass in nats, a disclosure leak in bits, a certification shortfall,
and nonequilibrium blanket violation — into one budget. It **fails the commensurability check**.
They differ in ensemble (average-case / adversarial / model-counterfactual / fine-grained quantum),
in per-unit (sample / proof / pair / quantum / time), and in **role** — the certification shortfall
is not a flow at all; nothing crosses anything. A single scalar would equivocate on all three axes.
**Keep the ledger, refuse the sum.**

---

## 4. Observation is compression; generation is decompression

"Intelligence is compression" has a theorem-grade core only in the incomputable limit (Solomonoff
1964; Kolmogorov's invariance theorem) — at finite resources it is a heuristic (**PO**).

Its popular dual, "**observation is decompression**," is **false as stated** and the error is
directional. In every standard formalism of perception-as-coding — Barlow efficient coding, the
Information Bottleneck, predictive coding — **the observer is the encoder.** The phrase has exactly
one exact reading and it inverts the agent: an optimal entropy decoder driven by fair random bits
emits exact samples from the model at ≈ H(p) bits per sample (Knuth & Yao 1976; Han & Hoshi, *IEEE
TIT* 43:599, 1997). **Generation is decompression; observation is compression** (**EM**).

The surviving sentence: *the world decompresses; the observer compresses; the record is where they
meet.* (**PO**, pointed the right way.)

---

## 5. What two observers can ever prove to each other

Let X and Y be two observers' committed histories.

> **K_GK(X;Y) ≤ I(X;Y) ≤ C_W(X;Y)** (**EM**)

**Gács–Körner common information** K_GK (Gács & Körner, *Probl. Control Inf. Theory* 2:149, 1973;
Witsenhausen, *SIAM J. Appl. Math.* 28:100, 1975) is the maximal quantity both parties can extract
with certainty and agreement. Its teeth: **K_GK = 0 whenever the joint distribution is
indecomposable** — for generically correlated sources the certifiable common part is **exactly
zero**, no matter how large the mutual information.

Three consequences we consider the practically important part of this paper:

1. **Correlation certifies nothing.** Two systems can be strongly, genuinely correlated and able to
   prove *no shared bit* to each other. We demonstrated this constructively: a joint with
   I = 0.663 bits admits **zero** perfect common extractions across all non-constant map pairs.
   (**IM**)
2. **Canonicalisation manufactures the common part.** Byte-exact canonical form is not hygiene; it
   is the operation that moves content from the uncertifiable region into K. (**EH**)
3. **To certify more than K, you must disclose.** With public discussion the distillable *secret
   key* reaches I(X;Y) (Ahlswede & Csiszár, *IEEE TIT* 39:1121, 1993; independently Maurer) — and
   the public transcript *is* the disclosure. Plain common randomness with a rate-R link grows
   toward H(X), not I(X;Y). There is no third option. (**EM**)

**The design corollary (EH):** the I − K gap is exactly the correlation two observers can *feel*
and cannot *prove*. **That gap is where trust scores get invented.** A system that emits an
aggregate trust number is pricing uncertifiable correlation. Ours refuses to compute one.

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

The machine matches or beats raw order-3 context prediction held out (0.894 vs 0.910 bits/symbol) —
i.e. the state clustering compresses history without losing prediction. **IM.**

Two methodological results matter more than the numbers:

- **The apparent growth of memory with history length was estimator bias, and we proved it** by
  generating synthetic data from our own fitted 24-state machine — a system whose true state count
  is known — and reproducing the same growth. Calibration against a system with a known answer (the
  golden-mean shift: exactly 2 causal states, h = log φ) passed to four decimals. **IM.**
- **A day-invariant budget with churning content (UN, one system, three days):** C_μ held at
  2.8889 / 2.8827 / 2.8823 bits on three consecutive days while the recurrent-state inventory grew
  13 → 25 → 39. Candidate reading: *the law surface sets the memory budget; the session spends it.*
  Registered falsifier: at ≥ 3×10⁴ events, per-day C_μ must stay within ±0.3 bits while state counts
  vary by more than 2×, or the reading dies.

This is a **conserved boundary-sum candidate**, and we flag it as the shape of question named
independently in this program's archive (Addendum AI): *"in the right symmetric enclosure, interior
motion can vary while a boundary-sum remains invariant."* One system over three days is not an
invariant. It is a target with a kill condition.

---

## 7. The method is the result

Five times in this program's history — and twice more in the work reported here — an instrument was
caught by its own controls **before** its output was cited: a roundoff on a structurally-zero
eigenvalue; an inert quantum substrate; a Merkle verifier that trusted prover-supplied path
directions; two topological-memory instruments that failed their own sanity gates; a shuffle control
that over-split under skewed marginals and killed the hypothesis it was defending; a preregistered
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
standard answer** — and a test that cannot lose cannot inform. The physics lane is on hold until one
does.

---

*No-upgrade sentence: nothing in this note is physics evidence; no software result validates any
physical claim; no verdict here grants authority; membership is not occurrence; signing is not
world-truth; the beautiful parts remain beautiful and the receipts remain the territory.*
