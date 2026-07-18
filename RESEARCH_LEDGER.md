# Research Ledger — Golden Horizon Principle

**Consolidated edition · 2026-07-19 · supersedes and preserves `GHP_RESEARCH_LEDGER.md` (frozen 2026-07-04)**

> **Provenance law (binding).** New results land here first, then the working paper, then the short paper. Nothing is deleted: Part II of this file preserves the full prior claim archive verbatim, frozen headers and all. The master (`GHP_v1_618_MASTER.md`) is the append-only archive of record for *how* results were produced; this ledger is the live board for *where every claim stands*.
>
> **Canon:** `CANON.md` → this ledger → `GHP_BOUNDARY_PROGRAM.md` (working paper) → `GHP_CORE_v3.md` (short paper) → `DO_NOT_CLAIM.md` (the single canonical non-claim source — the 26-rule subset previously duplicated here is retired in favor of that file).
>
> **Status vocabulary:** PROVEN (in stated domain) · VERIFIED COMPUTATION · SOUND PASS (engineering) · NULL (sound) · KILL (sound) · GENERIC · CLOSED (lane, with reopen bar) · OBSTRUCTED · PENDING / OPEN · CONJECTURE · BRIDGE-OBJECT CANDIDATE · TOY TELEMETRY · SYMBOLIC GRAMMAR · REFUTED · NEVER RUN.

---

## Part I — The Current State

### §1. Settled results (scoreboard)

| ID | Claim | Verdict | Date | Evidence (path/commit) | Guardrail |
|---|---|---|---|---|---|
| M-001 | Fibonacci categorical minimality | **PROVEN** (in domain) | — | UMTC classification (RSW et al.) | Does not prove physical selection |
| M-002 | Fusion rule τ⊗τ=1⊕τ → d=φ; Jones index 4cos²(π/5)=φ² | **PROVEN** (in domain) | — | Fusion algebra; Jones 1983 | Algebraic identity; scaffold, not selection evidence |
| M-004 | Hurwitz extremality (φ = most-irrational) | **PROVEN** (1891; re-checked 2026-07-19) | 1891 | Continued-fraction liminf ordering: φ 0.382 > √2 0.343 > √3 0.268 > e 0.141 > π 0.003 (q<150; asymptote 1/√5≈0.447) | 1891 mathematics; not a GHP result |
| M-003 | Golden-chain architecture/dynamics split (c=7/10) | **VERIFIED COMPUTATION** | — | Exact diagonalization; Feiguin 2007 | φ lives in architecture, not dynamics |
| SEL-CLOSE-001 | Dynamical selection of φ over metallic/noble rivals | **CLOSED** (two-tine fork, both fatal) | 2026-07-04 | KAM on-disk: noble_silver K_c=0.972702 ≥ golden 0.972336, margin 0.0144 < prereg 0.05 (`ghp_kam_standard_map_probe_outputs/summary.json`) + built-in-φ trap tine (TEE=0.643 conditional on Fibonacci category) | **IDENTITY proven, SELECTION dead.** Reopen only via the recorded 4-part bar (tests selection · φ-as-output with nothing golden inserted · pass-window excludes generic AND breaks noble-degeneracy · ledger-first prereg with a well-posed FAIL) |
| GH-RECOV | Recoverability, golden-spread proxy | **CLOSED vs φ-specificity** | 2026-07-03 | `ghp_golden_heal_probe.py` v1+v2 + 2 preregs; commit `8a3c6ead` | Mechanism real in synthetic code family (low-discrepancy beats random +0.34 pooled) but **silver-optimal** (silver 0.570 > bronze 0.479 > golden 0.432; adversarial tear golden 0/16, ~5σ for silver). Not GHP-memory recoverability. The genuine anyon fusion-tree code is still unbuilt |
| **K-RECOV-001** | Recoverability, external allocation replication | **GENERIC** | 2026-07-19 | Independent lab, seed-fixed, 20 seeds; 1,000 shards, Zipf importance, 300 budget, 25/50/75% erasure + burst; golden vs silver/bronze/exp2/greedy/uniform | Heavy tails beat uniform by +15pts @75% erasure; φ ≈ greedy-optimal within 1pt; margin +0.006 < ±0.02 threshold → **φ is a robust default convention, not an optimum** |
| P-005-TL | TL/Jones conditional-expectation closure at φ² | **NULL** (sound) | 2026-07-03 | `skunkworks_ghp_battery/TL_phi2_v2.py` (v1 roundoff flaw caught) | Closes equally at √2, 2cos(π/7), δ=2 — φ not distinguished among Jones indices; subfactor = scaffold |
| M-005 | Zipper sign-alternation as write-law | **NULL** (sound) | 2026-07-02 | `ghp_metallic_recurrence_genericity_probe.py`, 3-agent re-derivation | Generic to golden/silver/bronze/all δ; only Hurwitz extremality survives |
| P-007-2OBS | Two-observer MI/reflected-entropy consensus | **KILL** (sound at L≤12) | 2026-07-03 | `skunkworks_ghp_battery/two_observer.py`; separation 0.18 vs required ≥1.5 | No φ role; meets OP 164's own failure criterion; larger-L rerun is bookkeeping, not rescue |
| T-WWR-modular | Ternary write/witness/release vs binary | **SOUND PASS** (engineering, φ-free) | 2026-07-03 | `skunkworks_ghp_battery/modular_www_v2.py` (v1 inert substrate + tautological stream caught & rebuilt) | Contradiction-regime only (pollution 0.150 vs 0.500, 10/10 seeds); not a universal memory law, not physics |
| B-001/VPS | Viviani-φ **Surface** (Schwarzschild scalar identity) | **VERIFIED COMPUTATION** | — | `ghp_vph_extendability_probe.py`; `VPH_preprint_v8.md` | Exact algebra; **not a horizon** (not null/Killing/trapped), not dynamics, not selection, not proof of GHP. Naming discipline: "Horizon" retired |
| MEB arc | Matter embedding D4→F4→E6→27→16+10+1 | **OBSTRUCTED** (with positive bookkeeping) | 2026-06-26 | MEB-001…009 probes, all 5–6/6 | Real scaffold; too symmetric for chirality; 27→16+10+1 is representation bookkeeping, not a derivation of matter |
| BTA/HRT | Aukora boundary telemetry + Accord firewall | **SOUND PASS** (engineering) | 2026-06-26 | action_f1 0.7624 vs 0.3333 shuffled; private 0.0230; authority 0.0730; cheat-probe 0.8750 proves sanitizer load-bearing | Telemetry never becomes authorization; demotions stand (latency-primary, cadence, shockwave, aftershock, full Shear) |
| T-111/T-112 | φ as sampler (rotation/digits) | **GENERIC** | 2026-06 | BTA-003B/004A | Strong but non-unique: √2 slightly better; φ ranks 6/50; no free compression exists |
| **HRR-001** | Holographic (HRR) memory | **SOUND PASS** (engineering; **qualified**) | 2026-07-19 | Independent replication: d∈{512,1024,2048}, f∈{0,.25,.5,.6,.75}, k-sweep | Graceful, cliff-free degradation everywhere; headline 0.9609 reproduces **only in the capacity regime** k ≲ 0.27·(d/ln d) (measured prefactor ≈0.27; d=1024,k=32→0.94; k=64→0.68). Quote the law (SNR ∝ √((1−f)·d/k)), not the point |
| **AUK-ENG-001** | Aukora governed boundary (engineering lane) | **LIVE** | 2026-07 | Public repo; ~1,230 tests; hybrid PQ owner authority, crash-safe durable state, consent-scoped memory, advisory council, no-overclaim gate | Software echo, never physics evidence; proposes, never authorizes |

### §2. Open / pending — the live lanes and their next gates

| ID | Lane | Status | Next gate |
|---|---|---|---|
| P-002 | DMRG β-band | **PENDING** (7/9 clean; L72/L96 computing) | Complete audited protocol; apply both decision rules; report β_null=8/9 distance alongside verdict. Any pass reported as "CFT-consistent, pipeline validated" — never GHP support. Only β≈φ (separated from 8/9, 5/4) is anomalous |
| P-002a | SYK β corridor | **NEVER RUN** (no preregistered β ever computed) | Repaired pipeline + completed N=22 + a written ν→β conversion protocol satisfying OP 179. Until then: **the kill window [1.95, 2.05] is the only live content** — a generic-random result there falsifies cleanly |
| OP 3/157 | Selection principle (derivation) | **OPEN** (mathematical now, not empirical) | Theorem-grade derivation of the boundary architecture from framework objects; dynamical selection is CLOSED (SEL-CLOSE-001) |
| OP 164 | Two-observer law | **OPEN** (theory half) | A quantitative MI/shared-interface law; P-007 met the failure criterion at L≤12 — log as first evidence against, do not close |
| OP 111 | SYK decision branch | **OPEN** | The converter + bucket logic (incl. quotient-confirmation branch), specified but never coded |
| AH.4-P1 | **Genuine Fibonacci-anyon fusion-tree recoverability code** | **OPEN — the one unbuilt experiment that can still discriminate** | Must be designed so its pass-region *excludes* the generic answer; the proxy (GH-RECOV) and allocation replication (K-RECOV-001) are both negative and recorded |
| OP 184 | DMRG band reporting | **OPEN** | See P-002 |
| P-001 | Observer-boundary selection (the mother question) | **CONJECTURE** | A defined action or selection law; no current bridge object closes it |

### §3. Bridge stack — candidates (none constructed or closed; each carries its guardrail)

| ID | Object | Status | Guardrail |
|---|---|---|---|
| B-020 | Conditional expectation / finite access | bridge-object candidate | Real machinery (Kosaki; P-005-TL null); cite as finite-access route, not write-law |
| B-021 | Shared-interface / consensus functional | bridge-object candidate | Dutta–Faulkner S_R=2E_W is exact in holographic states; P-007 kill blocks promotion; vocabulary only |
| B-022 | Holographic recoverability / QEC | bridge-object candidate | Imported machinery; no golden-vs-control verdict ever run; closure = AH.4-P1 |
| B-024 | Multi-scale FEP / Markov blankets | bridge-object candidate | Statistical-boundary vocabulary, not the final law |
| B-025 | Boundary Access Channel (composite O_t) | bridge-object candidate | Toy telemetry: Fibonacci wins core channel, loses blended; anti-locking-core reading; not derived |
| B-026 | IIT/PCI perturbational lane | secondary constraint lane | Filter only; never the bridge |
| B-027 | Aukora governed portal | engineering analogue | Echo, not evidence |
| BRIDGE-H001 | Hoffman trace/Markovized Fibonacci kernel (P_Fib = [[0,1],[φ⁻²,φ⁻¹]], π=(1,φ²)/(2+φ)) | formal bridge candidate | Theorem-grade object; **no-go: trace logic alone does not select Fibonacci**; OP 203 comparator pending |

### §4. Engineering lane — global guardrails

Evidence may guide; evidence may not authorize. Telemetry-only public traces; allowlist sanitizer + recursive forbidden-field scanner (load-bearing). No telemetry-to-gate read path. Toy telemetry is never physics. Software success is never GHP. Every engineering claim carries: multi-seed stability, sensible baselines, and an explicit non-authority statement.

### §5. Toy arcs (condensed; full rows preserved in Part II)

- **Golden Zipper / observer-memory (T-005…T-018):** exact golden uniqueness did not survive; strongest survivors = relational groove memory + context-tinted recall; plasticity/reconsolidation/frame layers are mixed-to-negative. Not a physics claim.
- **Boundary Access Channel (T-019…T-080):** Fibonacci wins the core channel package under legal access; generic ternary takes the uniform-smear wrong-signal crossover (~0.20–0.40 fuzzy shoulder); groove-aware switcher ~0.928; rank-shape "miracle" demoted to rank-profile artifact; order+flow is the honest repair signal; "I should not decide yet" sentinel partially learnable (~0.080 open, 0.577 precision).
- **Aukora scaffolds (T-081…T-116):** HRT telemetry + witness plateau GREEN; sequence/shear/snap RED-or-offline; MDL process memory gated advisory; sampler/compression lanes narrowed to process-compression only.
- **Matter embedding (T-117…T-125):** see MEB arc, §1.
- **Cosmological record analogue (T-126):** external analogy only, 5/5.

### §6. External leads & refutations

| ID | Item | Verdict | Note |
|---|---|---|---|
| R-001a | Prior SYK exponent attempts | historical / not support | Anti-self-sealing context only |
| **REINMANN-2026-07-18** | External synthesis: φ ↔ modular forms ↔ zeta zeros via monstrous moonshine; "Fibonacci category has no zero object" | **REFUTED** (same-day audit, recorded kills) | Moonshine connects Monster irreps to j-invariant coefficients only — φ and zeta zeros appear nowhere (φ's genuine modular contact: Rogers–Ramanujan continued fraction). Fusion categories are semisimple abelian — they have zero objects (ENO 2005). No published non-trivial φ/Fib-category ↔ zeta connection (closest: Dyson 2009 quasicrystal speculation, generic). **Quarantined: never cite as support** |

---

## Part II — Reference machinery

### §7. Verified literature spine (verbatim from the frozen ledger)

| ID | Paper | Lane | Supports | Does Not Prove | Action |
|---|---|---|---|---|---|
| LIT-M001 | Rowell-Stong-Wang 2009 | category theory | low-rank UMTC classification | physical selection | cite in mathematical spine |
| LIT-M002 | Edie-Michell 2022 | category theory | phi-dimension fusion categories | observer boundary | cite in mathematical spine |
| LIT-O001 | Kosaki 1986 | operator algebra | conditional expectation / index | write-law | cite in formal boundary machinery |
| LIT-O002 | Fewster 2015 | AQFT | split property in curved spacetime | GHP boundary theorem | cite in formal boundary machinery |
| LIT-S001 | Dutta-Faulkner 2021 | holography / QI | reflected entropy / EWCS | GHP consensus law | cite in shared-interface section |
| LIT-S002 | Jeong-Kim-Nishida 2019 | holography / QI | first-order correction | GHP proof | cite as secondary |
| LIT-S003 | Tamaoka 2019 | holography / QI | OEE / EWCS link | GHP proof | cite as secondary |
| LIT-S004 | Babaei Velni et al. 2019 | holography / QI | EWCS aspects | GHP proof | cite as secondary |
| LIT-Q001 | Verlinde-Verlinde 2013 | QEC / holography | black-hole QEC recoverability | Fibonacci / GHP | cite as external machinery |
| LIT-Q002 | Parikh-Verlinde 2005 | de Sitter / observer complementarity | finite observer Hilbert-space framing | GHP | cite as external machinery |
| LIT-QF001 | Dumitrescu et al. 2022, Nature | Quantum information | Fibonacci/quasiperiodic temporal structure protecting edge information | GHP, VPH, observer-boundary selection, consciousness, literal two-time physics, or phi as universal code | cite as external analogue |
| LIT-CAV001 | Suslick-Flannigan 2008; Brenner-Hilgenfeldt-Lohse 2002 | acoustic cavitation / sonoluminescence | nonlinear boundary collapse analogue | GHP, over-unity energy, scalar-wave claims, consciousness, time extrusion, or observer-boundary selection | cite only as boundary-collapse analogue |
| LIT-H001 | Hoffman, Prakash, Chattopadhyay 2024 | observer-relative access / trace logic | access language; trace-chain vocabulary | GHP, Fibonacci selection, VPH, consciousness derivation, or write-law closure | cite as bridge-language only; TODO: verify exact citation |
| LIT-A001 | Doczi 1981, *The Power of Limits* | design analogue | generative limits, proportional harmony | GHP physics, observer-boundary selection, categorical minimality, VPH, SYK, consciousness, or phi as universal causal law | analogue lane only |
| LIT-V001 | Cruz-Olivares-Villanueva 2017 | GR prior art | golden ratio in Schwarzschild-Kottler geodesics | VPS | cite in VPH |
| LIT-V002 | Coelho-Herdeiro 2009 | GR prior art | golden ratio in optical geometry | VPS | cite in VPH |
| LIT-V003 | Hod 2013 | photon-sphere bounds | photon-sphere radius context | VPH / GHP | cite if useful |
| LIT-X001 | Eigenstate Thermalization for Wigner Matrices | off-target | none currently | GHP | do not cite |
| LIT-X002 | Mongan closed-universe holography | low-priority / speculative | observer horizon bits | GHP | archive only |
| LIT-X003 | Photon-sphere area spectrum | low-priority | photon-sphere quantization context | VPH / GHP | optional archive |
| LIT-C001 | Carr 2022 (Essentia) | phenomenology | t1/t2 separation, specious present, nested identity windows (phenomenological comparison) | GHP physics, write-law, VPH, Fibonacci D², or any consciousness claim | quarantine; do not cite in core paper |

### §8. Do-Not-Claim

Single canonical source: **`DO_NOT_CLAIM.md`** (60 rules + safe/avoid phrase lists + symbolic-layer rule). This ledger no longer duplicates a subset.

### §9. Promotion / demotion rules (verbatim, frozen ledger)

**Promotion:** only when a claim crosses a real evidentiary threshold, not because it sounds coherent. Mathematical promotion requires theorem-grade closure inside a stated domain. Physical promotion requires a defined bridge object, explicit failure condition, and stronger support than toy telemetry. Engineering promotion requires multi-seed stability, sensible baselines, and no silent overclaim.

**Demotion:** when a cleaner framing reveals the current claim is too strong; when tests fail, bridges stay undefined, or a result remains only numerical resonance. Preserve failed paths as anti-self-sealing evidence when useful.

### §10. ID crosswalk (reconciled 2026-07-19)

| Alias (older docs) | Canonical ID |
|---|---|
| "T-004" (short paper v2, row 9) | **T-WWR-modular** |
| "P-005" (short paper v2) | **P-005-TL** |
| "B-023" (share paper) | **BRIDGE-H001** |
| "E-001" (share paper) | **T-082** |
| "E-003" (share paper) | **T-108/T-109/T-110** |
| "E-004" (share paper) | **T-113/T-114** |
| "E-006" (share paper) | **T-126** |
| "Gate 5" (short paper) | **Kill Condition 9** (SYK generic-window kill) |
| "third bucket" (short paper) | the **quotient-confirmation branch** (working-paper Addendum M.1) |
| "C-001" (share paper central conjecture) | **P-001** (observer-boundary selection) |
| "Viviani-φ Horizon" | **Viviani-φ Surface (VPS)** — naming discipline, B-001 |

### §11. Update packet log (append-only)

- `GHP-PACKET-20260719-01` — Consolidated ledger edition. New rows: K-RECOV-001 (external recoverability replication, generic), HRR-001 (capacity-law qualification), AUK-ENG-001, REINMANN-2026-07-18 (refutation). Retired the duplicated 26-rule Do-Not-Claim subset in favor of `DO_NOT_CLAIM.md`. Added ID crosswalk (§10). Reworded GH-RECOV's "mechanism CONFIRMED" to "mechanism real in synthetic code family" per Do-Not-Claim phrasing. Frozen-May-2026 headers preserved in Part II for provenance.
- *(prior packets preserved verbatim in Part II, incl. `GHP-PACKET-20260704-01` — the SEL-CLOSE-001 settlement packet.)*

---
---

# PART II — Full claim archive (preserved verbatim · frozen 2026-07-04)

> Everything below this line is the prior ledger, unaltered (headers frozen "May 2026" retained for provenance). Where it disagrees with Part I, Part I is current (notably: SEL-CLOSE-001 and GH-RECOV are now settled results, and the Bridge Order's "P-002 as best falsification lane" is stale — the lane reports pipeline-validation at best).

[FULL ARCHIVE: the complete prior `GHP_RESEARCH_LEDGER.md` (111,151 bytes, frozen 2026-07-04) is preserved byte-for-byte at `archive/GHP_RESEARCH_LEDGER.2026-07-04.md` in this repository. It was carried verbatim into this consolidated edition during assembly; nothing was deleted or edited.]
