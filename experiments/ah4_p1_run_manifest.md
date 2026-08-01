# AH.4-P1 run manifest — build declaration (committed before execution)

- test_id: AH4-P1-ANYON-RECOV-v1
- prereg (SIGNED, locked 2026-08-01, not modified by this build):
  `experiments/AH4_P1_ANYON_RECOVERABILITY_PREREG_v1.md`
- gate 0 (pentagon identity, PASS): `experiments/ah4_p1_pentagon_gate.py` —
  its category data (fusion rules, F-symbols, label sets) is imported by the
  pipeline as the single source of truth; the gate is re-run inside
  `--selftest` and must pass before any fidelity is computed.
- pipeline: `experiments/ah4_p1_pipeline.py` (one parametrised code path over
  (category, constant); the only per-arm inputs are DATA — the basis-string
  set and the carrier-to-label adjacency kind — never code branches)
- builder: symbiote lane (Fable session) under owner direction, per prereg §6.4
- build date: 2026-08-01; branch `build/signed-runs-2026-08-01`
- status at commit time: **self-tests run and passed; the 4 × 4 factorial has
  NOT been executed.** This manifest is the pre-execution declaration the
  prereg §1.4 requires. Outcome analysis, when run, follows prereg §2.2
  verbatim (primary constant `uniform`, scattered mode; burst reported
  separately as a stressor; Δ margin ±0.02; 10,000-resample bootstrap).

---

## 1. Locked parameters

| parameter | value |
|---|---|
| carriers n | 12 (locked; feasible — no infeasibility clause triggered) |
| logical dimension d_L | 2 (see §3 declaration and deviation note) |
| erasure fractions f | 0.25, 0.50, 0.75 → k = round(f·12) = 3, 6, 9 erased carriers |
| erasure modes | `scattered` (uniform k-subset), `burst` (contiguous block, §4) |
| seeds | 1000–1019 inclusive, identical across all 16 cells; they drive erasure-position draws ONLY |
| Axis A (structure) | fib, ising, z3, classical |
| Axis B (constant) | golden (1+√5)/2, silver 1+√2, bronze (3+√13)/2, uniform (c = 1) |

Axis-B constants are the metallic means, exact expressions above; `uniform`
is implemented as c = 1, which makes the importance profile exactly flat
through the same formula (no special case).

## 2. Arms and dimensions (declared and verified)

All four arms are presented to the identical channel / recovery / scorer as a
set of basis strings over 12 slots with labels in {0, 1, 2}, plus a declared
adjacency kind. Dimensions are verified against theory in `--selftest`
(test 2) with the theory value computed independently (Fibonacci recursion,
powers).

| arm | basis | slots | dim (built = theory) |
|---|---|---|---|
| fib | Bratteli fusion paths of 12 τ anyons, total charge vacuum; slot j = internal edge e_{j+1}, labels 1→0, τ→1 | 12 edges (e_12 = total charge, constant) | 89 = Fib(11), F1=F2=1 |
| ising | fusion paths of 12 σ anyons, vacuum sector; labels 1→0, σ→1, ψ→2 | 12 edges | 32 = 2^5 |
| z3 | free leaf charges in Z₃, total charge 0 mod 3; slot j = leaf charge | 12 leaves | 177147 = 3^11 |
| classical | 12-carrier product basis (bits), unconstrained | 12 leaves | 4096 = 2^12 |

Path enumeration uses the gate module's verified fusion multiplicities
(`fib_N`, `ising_N`) directly; the path arms' structure is therefore exactly
the fusion algebra whose pentagon consistency gate 0 certifies. The z3 and
classical arms are diagonal/classical: they run through the **same**
interfaces and the same closed-form scorer (§6), which never materialises a
dense matrix, so 3^11 is exact with no approximation.

Note on F-symbols: the locked channel (§4) dephases labels **in the
canonical left-to-right fusion-path basis**, and the code rule, recovery,
and scorer all operate in that same basis, so no recoupling (F-move) is
applied at runtime. The fusion category enters through the Bratteli path
constraints (which strings exist and how edges sit adjacent to carriers).
The F-symbols' role in this experiment is gate 0: certifying that the
category whose path space we use is a consistent associator.

## 3. Code space (d_L = 2) — declaration and single selection rule

**Declaration:** d_L = 2, embeddable in every arm (89, 32, 177147, 4096 ≥ 2;
asserted in self-test 3).

**Deviation note (recorded, not hidden):** prereg §1.4 phrases the payload as
"the largest dimension embeddable in all four arms' code spaces at n = 12,
declared in the run manifest before execution." Read against the *physical
sector* dimensions, that formula would give d_L = 32 (the minimum arm
dimension). The owner's build directive of 2026-08-01 — the same authority
that signed the prereg — locks d_L = 2, and this manifest declares d_L = 2
accordingly, before execution, as the prereg requires. The discrepancy
between the §1.4 formula and the locked value is recorded here so it cannot
be discovered later; it does not touch the pass/kill rule (§2.2), which is
dimension-agnostic.

**The single deterministic selection rule (identical across arms):**

1. Importance profile: w_i = c^(−i/2) over positions i = 1..12, where c is
   the Axis-B allocation constant (c = 1 → flat). Only the *ranking* induced
   by w matters, so normalisation is irrelevant.
2. Signature: sig(s) = Σ_i w_i · ν_i(s), where ν_i(s) is the numeric label
   of slot i of basis string s (numeric maps in §2; vacuum/0 → 0).
3. Rank all D basis strings by (sig, lexicographic string) ascending —
   lexicographic tie-break makes the rule total and deterministic (ties
   occur under the uniform profile).
4. |0_L⟩ = uniform-amplitude superposition of the first ⌊D/2⌋ strings;
   |1_L⟩ = uniform-amplitude superposition of the remaining ⌈D/2⌉.

The codewords are orthonormal by construction (disjoint supports; asserted
for every arm × constant in self-test 3). On the classical arm with the flat
profile this rule bisects the product basis by weighted majority — the
coherent analogue of a repetition-style split — which is how the prereg's
"repetition-style" description of the classical arm is realised **without
any classical-specific code**.

## 4. Channel — exact Kraus structure

For a draw (seed, f, mode):

- k = round(f·12) ∈ {3, 6, 9}.
- `scattered`: E = uniform random k-subset of carriers {0..11}.
- `burst`: E = {off, off+1, …, off+k−1}, off drawn uniformly from
  {0..12−k} (non-wraparound contiguous block).
- RNG: `numpy.random.default_rng([seed, f_index, mode_index])` — fully
  deterministic, and **identical across all arms and constants** for a given
  (f, mode, seed), so every cell sees the same erasure patterns. Seeds enter
  the pipeline nowhere else.

Dephased slot set S(E):

- **path arms:** the internal edges adjacent to erased carriers. Carrier c
  (0-indexed) sits between edges e_c and e_{c+1} of the fusion chain
  (1-indexed edges; e_0, the charge before the first carrier, is the fixed
  vacuum and is not a slot). S(E) = ∪_{c∈E} {c−1, c} ∩ [0, 11] in 0-indexed
  slot columns. Slot 11 (e_12, the total charge) is constant across the
  sector, so dephasing it is a no-op; it is retained for uniformity rather
  than special-cased away.
- **product arms:** S(E) = E (the erased leaves themselves).

**Kraus operators.** Let κ range over joint label assignments to the slots
in S(E), and let P_κ be the orthogonal projector onto the span of basis
strings whose S(E)-restriction equals κ. The channel is the pinching

    N(ρ) = Σ_κ P_κ ρ P_κ ,     Σ_κ P_κ = 𝟙 ,

i.e. complete dephasing of the S(E) labels: the environment learns κ (the
pairing information adjacent to the erased carriers) and all coherence
between different κ-sectors is lost. N is exactly trace-preserving
(projectors partition the basis; asserted in self-test 8). No other noise is
applied. φ appears nowhere in this channel.

## 5. Recovery — Petz (transpose) map, identical for every arm

With σ = P_code / d_L (the maximally mixed code state):

    R(X) = σ^{1/2} N†( N(σ)^{−1/2} X N(σ)^{−1/2} ) σ^{1/2}

where N† = N (a pinching with Hermitian Kraus projectors is self-adjoint)
and inverses are pseudo-inverses on the support of N(σ). R is
trace-preserving on that support. φ appears nowhere in this construction.

## 6. Scorer — entanglement fidelity, and derivation D1 of the closed form

Score = entanglement fidelity of R∘N on the logical space:
F_e = ⟨Ω| (𝟙 ⊗ R∘N)(|Ω⟩⟨Ω|) |Ω⟩ with |Ω⟩ = (1/√2)(|0⟩|0_L⟩ + |1⟩|1_L⟩).

**Derivation D1** (what the fast path computes; verified against a literal
construction in self-test 7):

- Kraus of R∘N: B_{λκ} = σ^{1/2} P_λ N(σ)^{−1/2} P_κ, and
  F_e = Σ_{λκ} |Tr(σ B_{λκ})|².
- N(σ)^{−1/2} is block-diagonal over κ (it commutes with every P_κ), so
  P_λ N(σ)^{−1/2} P_κ = δ_{λκ} P_κ N(σ)^{−1/2} P_κ: cross-terms vanish.
- Per block, with u_a = P_κ|a_L⟩, U = [u_0, u_1], G_κ = Uᵀ U (2×2 Gram),
  the block of N(σ) is B_κ = ½ U Uᵀ, whose pseudo-inverse square root is
  √2 · U G_κ^{−3/2} Uᵀ. Then Tr(σ^{3/2} P_κ N(σ)^{−1/2} P_κ)
  = 2^{−3/2} Tr(Uᵀ B_κ^{−1/2} U) = 2^{−3/2} · √2 · Tr(G_κ^{1/2})
  = ½ Tr √G_κ.
- Therefore  **F_e = (1/4) Σ_κ ( Tr √G_κ )²**, with
  (Tr √G)² = Tr G + 2 √det G for a 2×2 PSD matrix.
- Bounds: Σ_κ Tr G_κ = 2 exactly, and (Tr √G)² ≤ 2 Tr G gives F_e ≤ 1;
  F_e ≥ 0 termwise. With disjoint-support codewords G_κ is diagonal and
  F_e = ½ + ½ Σ_κ √(g_{0κ} g_{1κ}) — one half plus half the Bhattacharyya
  overlap between the two codewords' distributions over dephased-label
  outcomes: coherence survives exactly to the extent the environment's
  record cannot distinguish the codewords.

The fast path computes G_κ for every κ by weighted bincount over basis
strings (base-3 slot keys) — exact for all arms including 3^11-dimensional
z3, no dense matrices, no sampling.

**Independent verifier** (`entanglement_fidelity_dense`, self-test only, fib
and ising arms): builds the purified state on C² ⊗ C^D explicitly, applies
the pinching, the N(σ)^{−1/2} sandwich (eigendecomposition pseudo-inverse,
threshold 1e−12·λ_max), the second pinching, and the σ^{1/2} sandwich as
literal matrices, including all cross-Kraus terms, and asserts trace
preservation at both stages. Agreement with the closed form: max |diff|
= 6.7e−16 over 16 configurations (2 arms × 2 constants × 2 fractions ×
2 modes). φ appears nowhere in the scorer.

## 7. φ tripwire audit (prereg §1.3)

The golden ratio appears in the pipeline in exactly one place: the Axis-B
constant table (`CONSTANTS["golden"]`), which feeds only the importance
profile of the code-space selection rule, on identical footing with silver,
bronze, and uniform. It appears **nowhere** in the erasure channel, the
noise model, the recovery routine, or the scorer (§§4–6 are φ-free by
inspection; the channel and Petz map contain no numerical constants at all
beyond ½-powers of 2 forced by d_L = 2). The Fibonacci quantum dimension is
never used by the pipeline; it remains an *output* of τ⊗τ = 1⊕τ, checked at
gate 0. The refused shortcut (prereg §3) was not taken: the fusion tree is
represented exactly (89 Bratteli paths with their fusion-rule constraints),
not approximated by any generic weighted-allocation scheme; the Axis-B
profile chooses a code space *inside* the exact tree basis, it does not
replace the tree.

## 8. Self-test protocol and output (run 2026-08-01, exit 0)

`python3 experiments/ah4_p1_pipeline.py --selftest` — all 30 checks passed,
1.1 s single-core (the full factorial is comfortably under the prereg's
30-minute budget). "Machine precision" for the f = 0 check is < 1e−12
(the z3 arm accumulates 1.77e5 float terms; observed 9.1e−13).

```
AH.4-P1 pipeline self-tests
============================================================

1. pentagon gate (gate 0 must still pass)
  [PASS] pentagon[fib]  max residual 1.110e-16 over 48 assignments
  [PASS] pentagon[ising]  max residual 2.220e-16 over 132 assignments
  [PASS] pentagon[z3]  max residual 0.000e+00 over 81 assignments

2. dimensions vs theory
  [PASS] dim[fib]  built 89, theory Fib(11) = 89 (F1=F2=1)
  [PASS] basis-strings-distinct[fib]
  [PASS] dim[ising]  built 32, theory 2^5 = 32
  [PASS] basis-strings-distinct[ising]
  [PASS] dim[z3]  built 177147, theory 3^11 = 177147
  [PASS] basis-strings-distinct[z3]
  [PASS] dim[classical]  built 4096, theory 2^12 = 4096
  [PASS] basis-strings-distinct[classical]

3. code space: d_L = 2 embeddable, codewords orthonormal
  [PASS] embeddable[fib]
  [PASS] orthonormal[fib, all constants]
  [PASS] embeddable[ising]
  [PASS] orthonormal[ising, all constants]
  [PASS] embeddable[z3]
  [PASS] orthonormal[z3, all constants]
  [PASS] embeddable[classical]
  [PASS] orthonormal[classical, all constants]

4. f = 0 gives fidelity 1.0 to machine precision (every arm)
  [PASS] f0[fib]  max |F-1| = 0.000e+00
  [PASS] f0[ising]  max |F-1| = 0.000e+00
  [PASS] f0[z3]  max |F-1| = 9.059e-13
  [PASS] f0[classical]  max |F-1| = 1.110e-16

5. fidelities within [0,1] (sweep: all arms/constants/f/modes, seeds 1000-1004)
  [PASS] bounds  observed range [0.500000, 1.000000] over 480 evaluations

6. determinism under fixed seed (recompute from scratch)
  [PASS] deterministic  24 values bitwise identical
  [PASS] erasure draws reproducible

7. closed-form scorer vs literal dense Petz construction
  [PASS] closed-form == dense Petz  max |diff| = 6.661e-16 over 16 comparisons (fib+ising)

8. channel is a partition (Kraus projectors sum to identity)
  [PASS] partition[fib]  sum Tr G_kappa = 2.000000000000000 (expect 2)
  [PASS] partition[ising]  sum Tr G_kappa = 2.000000000000000 (expect 2)
  [PASS] partition[z3]  sum Tr G_kappa = 2.000000000000000 (expect 2)
  [PASS] partition[classical]  sum Tr G_kappa = 1.999999999999999 (expect 2)

============================================================
SELF-TESTS ALL PASSED
```

## 9. Environment note

numpy 2.0.2 on macOS/Accelerate emits spurious "divide by zero / overflow /
invalid encountered in matmul" RuntimeWarnings on *any* matmul (reproduced
with an all-ones 50×50 product). The pipeline filters exactly that message;
correctness is carried by the explicit assertions and the dense-vs-closed-
form cross-check, not by FP flags.

## 10. How to run

```
python3 experiments/ah4_p1_pipeline.py --selftest   # gate + 30 self-tests
python3 experiments/ah4_p1_pipeline.py --run        # 16 cells x 3 f x 2 modes x 20 seeds
                                                    # -> experiments/ah4_p1_results.json
```

The `--run` output is raw per-seed fidelities only; the §2.2 decision rule
(Δ contrasts, bootstrap CIs, STRUCTURAL ADVANTAGE / PRIMARY KILL /
INTERACTION-MIXED verdict) is a separate analysis step against that file and
is governed entirely by the signed prereg.
