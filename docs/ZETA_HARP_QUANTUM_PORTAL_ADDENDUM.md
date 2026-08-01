# Addendum — The Zeta Harp Quantum Portal (externally authored directive, adopted)

- author: GPT 5.6 (external reviewer), 2026-08-01; adopted by owner directive the same
  night, under the standing external-contributions channel
  (`review/EXTERNAL_CONTRIBUTIONS.md`).
- grounding at adoption (resident lane, machine-verified BEFORE adoption): the central
  identity

      M(t) = 2 A_N Re<w_N|psi(t)>,   A_N = sum_{n=1}^{N} n^(-1/2),  N = floor(sqrt(t/2pi))

  was checked exact to better than 1e-31 at t = 4300, 4400, 4500 with <psi|psi> = 1,
  and re-verified in this build (residuals < 1e-37 at 40 decimal digits; float64
  pipeline residuals < 3e-15 across the full window grid plus t = 1e4 and t = 1e6;
  see `experiments/zeta_harp_quantum/outputs/overlap_identity.json`).
- provenance: this file is the ADOPTION RECORD. The directive's content is stated here
  as adopted; the complete original text as delivered lives with the delivery channel
  (same convention as `docs/ZETA_HARP_26_CHAMBER_ADDENDUM.md`). Where this file quotes
  the directive directly, the quotation is marked.
- status: governing spec for the Quantum Portal research layer
  (`research/quantum/` + `experiments/zeta_harp_quantum/`). The claim corrections below
  are BINDING and machine-enforced by the claim linter
  (`experiments/zeta_harp_quantum/tests/test_quantum_portal.py`, test 25). The standing
  Riemann fence applies in full. The ZETA-CUBE NULL
  (`experiments/zeta_cube_null/VERDICT.md`) is carried, not hidden.

## The five claim corrections (A-E, binding)

Each correction states the fact, then the rejected phrasing. Rejected phrasings may
never appear as claims anywhere in this repository; they appear below only as marked
quotations, and the linter enforces exactly that.

**A. Qubit-vs-qutrit basis facts.** A qubit has a two-state basis {|0>, |1>}; a qutrit
has a three-state basis, here labeled {|-1>, |0>, |+1>} (equivalently {0, 1, 2}). The
Trinity labels {-1, 0, +1} are a LABELING of a qutrit basis — a naming choice, not a
physical identification.
Rejected claim [REJECTED-CLAIM]: "Trinity is a qubit".

**B. The genuine two-pole superposition.** |B> = (|-1> + |+1>)/sqrt(2) is a genuine
superposition of the two pole states, and it is a DIFFERENT state from |0>. |0> is a
basis state — one outcome label among three — and calling a basis state a superposition
is simply false.
Rejected claims [REJECTED-CLAIM]: "0 is superposition"; "zero is superposition".

**C. The Harp is classical.** The Zeta Harp evaluates the Riemann-Siegel main sum by
classical deterministic arithmetic (JavaScript floats in the instrument, numpy/mpmath
here). Nothing in it prepares, evolves, or measures a physical quantum state.
Rejected claim [REJECTED-CLAIM]: "the Harp is a quantum computer" / "the Harp is a quantum simulator".

**D. Quantum-COMPATIBLE, not advantaged.** The overlap formulation shows the main sum
embeds exactly in the state-vector formalism (a 27-dimensional Hilbert space suffices at
N = 26). Compatibility is all that is shown: no speedup, no resource win, no hardware
superiority is claimed, and state preparation is treated throughout as an assumed oracle
whose cost is not claimed.
Rejected claim [REJECTED-CLAIM]: "quantum advantage".

**E. A zero is a vanishing overlap, not an event.** On the critical line, a zero of the
main sum is the analytic condition Re<w_N|psi(t)> = 0 — a real-valued function of t
passing through zero (with the O(t^(-1/4)) remainder separating this from a zero of the
full Z(t), a distinction always carried). It is never a measurement event, never a
collapse, and no observer participates in it.
Rejected claims [REJECTED-CLAIM]: "zero is quantum collapse"; "observer creates the zero".

Additional standing rejections carried from the program's fences
[REJECTED-CLAIM]: "ahead of Flatiron"; "cube confirms"; "classical shortcut to RH";
and any claim of RH support — nothing in this layer is evidence for or against the
Riemann Hypothesis.

## The three-layer separation

Every statement in the Quantum Portal layer belongs to exactly one layer and is labeled
by where it lives:

1. **EXACT SCIENCE** — theorems and machine-checked identities: the Riemann-Siegel main
   sum, the window arithmetic N(t), the overlap identity and its two-line proof, the
   bijection properties of the register mappings. Lives in
   `research/quantum/ZETA_HARP_QUTRIT_OVERLAP_BRIDGE.md` and the test battery.
2. **QUANTUM-INFORMATION EMBEDDING** — chosen representations with no physical claim:
   the 3x3x3 register, term-to-state mappings, Hadamard-test readout, tensor-train
   benchmarks with controls. Lives in `experiments/zeta_harp_quantum/`. Everything here
   is classical simulation of finite-dimensional linear algebra.
3. **SYMBOLIC-INSTALLATION** — the portal language of the instrument and the site.
   Permitted only with the required qualifier (next section), and never upstream into
   layers 1-2.

## Allowed installation language (with required qualifier)

The following phrases are permitted in symbolic-installation contexts ONLY when
accompanied by the qualifier — verbatim or visibly equivalent:

> *symbolic-installation layer: an interface convention, not a physics claim and not a
> computational claim.*

Allowed list:

- "the Quantum Portal" (naming the research layer and its instrument room)
- "the portal opens on the 26-term window"
- "|0,0,0> is the interface anchor" / "the reserved reference basis state"
- "reading the Harp through the qutrit window"
- "the register holds the 26 strings"
- "the observer selects the portal" (in the sense of the governing sentence below:
  a choice of representation, never a physical act on the mathematics)

Anything not on this list that implies mechanism, computation, or physics must be
promoted to layer 1 or 2 with receipts, or not said.

## The six research questions (as adopted)

1. **RQ1 (OVERLAP-EXACT).** Is the N-term Riemann-Siegel main sum exactly representable
   as 2 A_N times the real overlap of two normalized states in an N-dimensional (or
   padded qudit) register across the full 26-term window, and does the representation
   remain exact at machine tolerance as N grows (t = 1e4, 1e6, ...)?
2. **RQ2 (REGISTER-MAP).** Which bijections of the 26 active terms onto the 26
   noncentral three-qutrit basis states preserve which structure, and does any reported
   quantity depend on the choice of mapping? (Required answer discipline: report all
   mappings neutrally; no mapping search for pretty results.)
3. **RQ3 (HADAMARD-READ).** Can Re<w|psi> and Im<w|psi> be read out by a standard
   Hadamard test in pure state-vector simulation, exactly when noiseless and with
   binomial shot convergence when sampled — with state preparation declared an assumed
   oracle whose cost is not claimed?
4. **RQ4 (RESOURCE-COUNT).** What are the honest resource counts for the same 26
   amplitudes in a 5-qubit (32-state) versus 3-qutrit (27-state) register, and what — if
   anything — do unused-state counts imply? (Bound answer: nothing about hardware
   superiority.)
5. **RQ5 (TENSOR-COMPRESS).** Does the Harp amplitude vector at fixed t compress under
   tensor-train decomposition differently from matched controls, at stated ordering and
   stated tolerance, and how does the answer scale with N?
   (ZETA-HARP-TENSOR-COMPRESS-v1; see
   `research/quantum/ZETA_HARP_TENSOR_COMPRESSION_PLAN.md`.)
6. **RQ6 (PRIOR-ART).** Where does the exact-overlap formulation sit in the existing
   literature? Novelty is NOT established; the search program is
   `research/quantum/ZETA_HARP_QUANTUM_PRIOR_ART.md`.

## Register status and anchors

- The 3x3x3 layout is a CHOSEN three-qutrit register — never a zeta-derived topology.
- The ZETA-CUBE NULL verdict is carried alongside this layer, not hidden: the one cube
  experiment run to verdict came back NULL.
- |0,0,0> is the RESERVED REFERENCE BASIS STATE / INTERFACE ANCHOR. It carries exactly
  zero amplitude in every mapping (machine-tested) and is never a physical observer.

## Governing sentence

The directive's final governing sentence, as adopted (quoted):

> "The observer selects the portal through which the mathematics becomes readable."

Read strictly at the symbolic-installation layer with its required qualifier: selecting
a portal is choosing a representation — a register, a mapping, a readout — through which
known mathematics is displayed. The mathematics is unchanged by the choice; the
machine-checked mapping-invariance and basis-permutation tests are the enforcement of
that sentence's honest reading.
