# Research Ledger — Golden Horizon Principle

**Consolidated edition · 2026-07-19 · supersedes and preserves `GHP_RESEARCH_LEDGER.md` (frozen 2026-07-04)**

> **Provenance law (binding).** New results land here first, then the working paper, then the short paper. Nothing is deleted: the full prior claim archive (111,151 bytes, 161 claim rows, frozen 2026-07-04) is preserved byte-for-byte at `archive/GHP_RESEARCH_LEDGER.2026-07-04.md` (sha256 `4b7ecf8e10ef4d81b5cf4cb455255ae78dbcc46ea07f653a3626064c879e5697`), frozen headers and all. The master (`GHP_v1_618_MASTER.md`) is the append-only archive of record for *how* results were produced; this ledger is the live board for *where every claim stands*.
>
> **Canon:** `CANON.md` → this ledger → `GHP_BOUNDARY_PROGRAM_v2.md` (working paper) → `GHP_CORE_v3.md` (short paper) → `DO_NOT_CLAIM.md` (the single canonical non-claim source — the 26-rule subset previously duplicated here is retired in favor of that file).
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
| M-006 | Two-families uniqueness: metallic means ∩ admissible quantum dimensions = {φ} | **PROVEN** (in domain) | 2026-07-29 | Jones 1983 index rigidity (d<2 ⇒ d=2cos(π/m)); silver 2.414 / bronze 3.303 / copper 4.236 all >2 → excluded from the discrete series; index >4 = continuum, no canonical category; φ=2cos(π/5) and φ²=φ+1 verified to machine precision | Metallic means are constant-controls only; structure-controls live on the 2cos(π/m) ladder (1, √2, φ = the AH.4-P1 arms). No metallic fusion category above gold exists — explains the constant-axis shape of GH-RECOV and K-RECOV-001 |
| M-003 | Golden-chain architecture/dynamics split (c=7/10) | **VERIFIED COMPUTATION** | — | Exact diagonalization; Feiguin 2007 | φ lives in architecture, not dynamics |
| SEL-CLOSE-001 | Dynamical selection of φ over metallic/noble rivals | **CLOSED** (two-tine fork, both fatal) | 2026-07-04 | KAM on-disk: noble_silver K_c=0.972702 ≥ golden 0.972336, margin 0.0144 < prereg 0.05 (`ghp_kam_standard_map_probe_outputs/summary.json`) + built-in-φ trap tine (TEE=0.643 conditional on Fibonacci category) | **IDENTITY proven, SELECTION dead.** Reopen only via the recorded 4-part bar (tests selection · φ-as-output with nothing golden inserted · pass-window excludes generic AND breaks noble-degeneracy · ledger-first prereg with a well-posed FAIL) |
| GH-RECOV | Recoverability, golden-spread proxy | **CLOSED vs φ-specificity** | 2026-07-03 | `ghp_golden_heal_probe.py` v1+v2 + 2 preregs; commit `8a3c6ead` | Mechanism real in synthetic code family (low-discrepancy beats random +0.34 pooled) but **silver-optimal** (silver 0.570 > bronze 0.479 > golden 0.432; adversarial tear golden 0/16, ~5σ for silver). Not GHP-memory recoverability. The genuine anyon fusion-tree code is still unbuilt |
| **K-RECOV-001** | Recoverability, external allocation replication | **GENERIC** | 2026-07-19 | Independent lab, seed-fixed, 20 seeds; 1,000 shards, Zipf importance, 300 budget, 25/50/75% erasure + burst; golden vs silver/bronze/exp2/greedy/uniform | Heavy tails beat uniform by +15pts @75% erasure; φ ≈ greedy-optimal within 1pt; margin +0.006 < ±0.02 threshold → **φ is a robust default convention, not an optimum** |
| SILVER-OPT | Characterize the silver anomaly (silver ≥ golden on four independent instruments) | **RUN 2026-08-01 — UNRESOLVED (no branch fired); anomaly ANTI-REPLICATED in this family** (prereg SHA `034dbb47…`, untouched) | named 2026-07-07 (v2.1 edition); restored 2026-07-29 | GH-RECOV critical band + adversarial tear (~5σ for silver); T-111 sampler friction; T-112 rotation ranking; SEL-CLOSE-001 KAM thresholds | Constant-axis anomaly (see M-006: no silver fusion category exists, so no structural reading). Three preregistered hypotheses, each with a kill: H1 silver-optimal (a GHP-independent result about low-discrepancy allocation) · H0 noble-plateau · H2 damage-geometry artifact. Not GHP physics under any branch |
| SILVER-OPT-GEO | Silver anomaly at its original address (placement geometry) | **RUN 2026-08-01 — UNRESOLVED (no branch fired); FIRST REAL CHARACTERIZATION: the tear line is SIZE-SPECIFIC** | run 2026-08-01 (contract SHA `9b429ba72092ef26…`, untouched; substrate verbatim, verifier PASS) | The original silver tear advantage REPRODUCES CI-solid at the original size (n=256: Δ_sg = +0.278 [+0.270, +0.288]) and VANISHES with slight reversal at doubled size (n=512: −0.0074 [−0.0118, −0.0014]). Shuffled tripwires collapse → the effect rides sequential low-discrepancy structure, not the point multiset. G1 failed only the both-sizes requirement; G0/G2 fail outright. A finite-size effect, real at its home size — not a fluke, not universal. Size-scaling follow-up requires its own signed contract |
| ZETA-CUBE-NULL | 27-bin ternary-digit statistic of zero ordinates (Riemann-adjacency lane, FENCED) | **RUN 2026-08-01 — NULL, as predicted** | contract SHA `5cd68a775979c495…`; run commit c1a32bc | S1 = 23.85 within pooled control band [14.61, 42.39]; S2 = 0.0636 within [0.0449, 0.0659] (400 stochastic replicates; primes = descriptive comparator only; implementation choices disclosed in run.py header) | Door closed with a receipt. σ-blindness recorded as formal property (F(σ+it) independent of σ): the mapping could never diagnose RH under any outcome — RH-CUBE-001 as an RH-relevant claim KILLED at definition (K3, external review concurring); cube retained as symbolic/visualization. v1.1 draft staged for the independent-reimplementation round |
| SYK-CORRIDOR | Direct-β revival-degradation corridor (Module C verbatim: "Γ ∼ 1/d^β where d = Hilbert space dimension") | **PREREG SIGNED/LOCKED 2026-08-01 — run authorized; ν-route CLOSED pending OP 179** | contract SHA `59a46ff9b19b05b6…`; converter SHA `b1fbb56f480a9385…` (both recorded here per lock protocol — run gate now open) | Official N ∈ {14,18,22} (N=10 telemetry only), 15-point κ grid with bracketing rule, seeds 5000–5039, bootstrap [0.30,1.50]/2000/5% edge-mass, R² ≥ 0.98, cross-size corr ≥ 0.99, HARD CAP 400 USD | Standard null β = 2 sits center-of-kill-window, outside both pass bands (assignment-independent): a genuinely losable test. Gate 5 / Kill Condition 9 live; CI-governs precedence binding via signed §4 | Constant/placement axis (M-006); not GHP physics under any branch |
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
| AH.4-P1 | **Genuine Fibonacci-anyon fusion-tree recoverability code** | **RUN 2026-08-01 — INTERACTION/MIXED (no upgrade)** | Prereg v1.1 signed/locked (SHA `44d60ed2…`), verifier-stamped build, 96 cells × 20 seeds, 0 aborts. Primary Δ(f)=fib−ising @ uniform: +0.011 / +0.065 / +0.101 at f=0.25/0.50/0.75 — every 95% CI includes 0, so NO structural advantage is certified; not flat either (|Δ|>0.02 at two fractions), so the §2.2 third branch fires. Point estimates lean Fibonacci and grow with damage but 20 seeds cannot certify them. Secondary, reported without upgrade: fib < z3 and fib < classical at every fraction under this dephasing-erasure + Petz channel (most CIs exclude 0). Axis-B not flat and direction REVERSED vs K-RECOV (uniform/golden high, silver/bronze low) — channel-dependence recorded. Per the signed outcome table, interaction gets its own future preregistration or the lane rests; no post-hoc story. Evidence: `experiments/ah4_p1_results/` |
| AH4-P1-POWERED | Powered structural sequel: 400 fresh seeds, declared high-damage rule | **RUN 2026-08-01 — KILL: structural-advantage hypothesis DEAD at n=12 under this channel** | v2 contract SHA `bcea7ce761484162…`; pipeline pinned byte-identical SHA `59fc150a67971c1a…`; The v1 20-seed trend (+0.065/+0.101) DID NOT REPLICATE at 400 seeds: Δ(0.50)=+0.0005 CI [−0.0102,+0.0317], Δ(0.75)=0.0000 (both arm medians exactly 0.5); trend slope dissolved (−0.0085, CI includes 0). Certified secondaries: fib < z3 AND fib < classical at every fraction (CIs exclude 0). Pipeline hash re-verified pre-run; burst sign-mixed, no veto. Per contract: no v3 with re-cut thresholds; a new channel family or new n is a new experiment with its own prereg. Evidence: `experiments/ah4_powered_results/` |
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

### §5. Toy arcs (condensed; full rows preserved in the archive of record)

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
| LIT-RH001 | Lapidus–Maier 1995; Lapidus–van Frankenhuijsen, *Fractal Geometry, Complex Dimensions and Zeta Functions* | fractal strings / spectral geometry | ternary (middle-thirds Cantor) geometry has complex dimensions in periodic vertical progressions (period 2π/log 3, machine-verified: `experiments/riemann_adjacency_gate_2026-07-29.py`); RH ⟺ an inverse spectral problem for fractal strings, solvable for all dimensions in (0,1) except 1/2 | GHP, VPH, φ-selection, Luminara, or any claim that ternary structure proves anything about zeta zeros | cite as external analogue only |
| LIT-RH002 | Deligne 1974 (Weil I); Deninger 1998 ICM; Connes–Consani 2009–2024 incl. arXiv:2401.08401; Mazur / Morishita, *Knots and Primes* (Springer 2012, 2nd ed. 2024) | arithmetic geometry / arithmetic topology | RH analogue PROVEN over finite fields via Frobenius eigenvalues; the missing-geometry diagnosis for Spec Z is a widely held heuristic, not established; Deninger: primes as closed orbits of a conjectured flow; arithmetic topology: compactified Spec Z as 3-manifold, primes as knots, linking ↔ Legendre for p≡q≡1 mod 4 | GHP, VPH, φ, Luminara glyph knots, or any claim that a geometric RH proof exists or is imminent | cite as prior-art context only |
| LIT-RH003 | Hardy Z-function (standard analytic number theory); Glaisher 1878 hyperfactorial asymptotics | analytic number theory | critical-line zeros = sign changes of the real oscillating Z(t) (all-zeros-as-crossings ⟺ RH + odd multiplicity); hyperfactorial chain 1, 4, 27 (H(3)=108) has growth constant A with ln A = 1/12 − ζ′(−1), machine-verified | numerology about 108, 27, or balanced ternary as zeta structure; any pulse-metaphor upgrade to physics | cite as external mathematics only |
| LIT-RH004 | He, Jejjala, Minic 2015, "From Veneziano to Riemann: A String Theory Statement of the Riemann Hypothesis" (arXiv:1501.01975, VERIFIED-BY-RETRIEVAL 2026-08-01) | string amplitudes / analytic number theory | the published string–zeta bridge: the Veneziano amplitude expressed through gamma-function and zeta ratios; known RH-equivalent criteria restated via amplitude properties. Source for the Observatory's "Veneziano Bridge" context room (equation audit required before the room ships) | any claim that the 26-term Riemann–Siegel window IS bosonic string theory's D=26 (shared number, different mechanisms: anomaly cancellation vs the cutoff floor(sqrt(t/2π))); any RH-support claim | cite as prior-art context only |
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

- `GHP-PACKET-20260719-01` — Consolidated ledger edition. New rows: K-RECOV-001 (external recoverability replication, generic), HRR-001 (capacity-law qualification), AUK-ENG-001, REINMANN-2026-07-18 (refutation). Retired the duplicated 26-rule Do-Not-Claim subset in favor of `DO_NOT_CLAIM.md`. Added ID crosswalk (§10). Reworded GH-RECOV's "mechanism CONFIRMED" to "mechanism real in synthetic code family" per Do-Not-Claim phrasing. Frozen-May-2026 headers preserved in the archive of record for provenance.
- `GHP-PACKET-20260729-01` — Two-families packet. New rows: M-006 (two-families uniqueness, proven in domain), SILVER-OPT (silver-anomaly characterization, OPEN — restored from the v2.1 edition archived this day). Same-day repo events: v2.1/v1.1 editions landed as archived editions of record (PR #1); AH.4-P1 structural preregistration merged DRAFT/UNSIGNED with its gate-0 pentagon check independently re-run and passing (PR #5). Core bumped to v3.1; working paper gains Addendum (v2.1) 2026-07-29 (B.1 two-families + control doctrine, B.2 capability ladder, B.3 SILVER-OPT restoration). Capability-ladder braid-computation receipt pending.
- `GHP-PACKET-20260729-02` — Riemann adjacency packet. New LIT rows RH001/RH002/RH003 (fractal strings; the geometric route incl. primes-as-knots; Hardy Z pulse + Glaisher chain), all analogue/prior-art only, five-referee adversarial verification 2026-07-29. Working paper gains Addendum B.4 (the Riemann adjacency map, fenced). Receipt: `experiments/riemann_adjacency_gate_2026-07-29.py` (all gates pass). RH posture recorded: neither proof nor disproof of RH informs GHP; A.3 quarantine untouched.
- `GHP-PACKET-20260801-01` — Signing packet. AH.4-P1 v1.1 and SILVER-OPT v1 preregistrations SIGNED by the owner (chat directive, 2026-08-01) and locked; signed-file hashes recorded on their rows (`44d60ed27855079e…`, `034dbb47b56dcd95…`). Builds authorized in that order. Post-signing edits to either prereg void the corresponding run.
- `GHP-PACKET-20260801-02` — First signed-run packet. Both same-day-signed experiments executed under their locked contracts. AH.4-P1: INTERACTION/MIXED (no certified structural advantage, no kill; fib−ising point estimates grow with damage but no CI excludes 0; fib trails both floor controls under this channel — honest datum, no upgrade). SILVER-OPT: UNRESOLVED — H1 0/36 cells, H0 fails (max noble gap 0.161), H2 empty-set; the adversarial-tear sign REVERSED (golden leads: Δ_sg −0.037/−0.074/−0.049 at f=0.25 across sizes); sanity anchors held (heavy-tails-beat-uniform reproduces at random erasure; shuffled tripwires collapse). Descriptive lead recorded without upgrade: the four-instrument silver line is not a property of heavy-tailed allocation counts; if real it lives in placement geometry (GH-RECOV type). Follow-ups, if any, require their own preregistrations.
- `GHP-PACKET-20260801-03` — Second signing packet. AH4-P1-POWERED v2 (contract `bcea7ce761484162…`, pipeline pinned `59fc150a67971c1a…`) and SILVER-OPT-GEO v1 (`9b429ba72092ef26…`) SIGNED by owner chat directive; runs authorized in that order. SYK remains gated: the nu-to-beta channel-exponent assignment is a physics decision that must be preregistered BEFORE any corridor data exists (AE.8/AE.9 non-uniqueness; window-closing law); a decision memo is being drafted rather than defaulted.
- `GHP-PACKET-20260801-04` — Third run packet, the decisive one. AH4-P1-POWERED: **KILL** — the one suggestive structural trend in program history dissolved at 20× seeding; Fibonacci certified BELOW both floor controls under this channel; the structural-advantage hypothesis at n=12/this-channel is dead with no re-cut path. SILVER-OPT-GEO: UNRESOLVED mechanically, but the anomaly received its first genuine characterization — real and strong at its original size, absent at 2×, structure-riding (shuffles collapse). Gifts landed: the Zeta Harp instrument (`experiments/zeta_harp/`) and the SYK assignment decision memo (`experiments/SYK_ASSIGNMENT_DECISION_MEMO.md`). All runs under locked signed contracts, add-only, hash-verified, mechanical verdicts, zero upgrades.
- `GHP-PACKET-20260801-05` — Night packet. ZETA-CUBE-NULL v1: NULL as predicted; digit-cube door closed; σ-blindness formalized; RH-CUBE-001 killed at definition with external reviewer (GPT 5.6) concurrence; v1.1 draft staged for independent reimplementation with externally authored statistics. SYK corridor contract SIGNED on the direct-β route (Module C source-grounded), both hashes on the row, run gate open, $400 cap. External review adopted: hash-level sign-off floor for the Riemann lane, 54-incidences terminology, torus-label errata pending, harp 'computed spectral' rename queued, branch protection (no force-push/delete) enabled.
- `GHP-PACKET-20260801-06` — 26-Chamber packet. Externally authored 26-Phase Chamber addendum ADOPTED (GPT 5.6): window numerics machine-verified to every supplied decimal (N = 25/26/27 at the boundaries of [2π·26², 2π·27²)); three-layer separation binding (SCIENCE: exact T^26 phase state / ANALOGY: labeled string-theory resonance, never equivalence / PUBLISHED-BRIDGE: LIT-RH004); "+1 observer" fixed as interface metaphor under the symbolic layer; RH and cube firewalls carried. External-contributions channel opened (`review/EXTERNAL_CONTRIBUTIONS.md`): draft-PR-only, verifier-stamped, owner-adjudicated, attribution preserved.
- *(prior packets preserved verbatim in the archive of record, incl. `GHP-PACKET-20260704-01` — the SEL-CLOSE-001 settlement packet.)*

---

## Archive of record — the frozen 2026-07-04 ledger

> The complete prior `GHP_RESEARCH_LEDGER.md` (111,151 bytes, 161 claim rows, frozen 2026-07-04, headers frozen "May 2026" retained for provenance) is preserved **byte-for-byte** at **`archive/GHP_RESEARCH_LEDGER.2026-07-04.md`** — sha256 `4b7ecf8e10ef4d81b5cf4cb455255ae78dbcc46ea07f653a3626064c879e5697`, git blob `f7f5b73167678d035a6432d7f94e862aa512eec7`. Nothing was deleted or edited. Where the frozen archive disagrees with Part I of this ledger, **Part I is current** (notably: SEL-CLOSE-001 and GH-RECOV are now settled results, and the Bridge Order's "P-002 as best falsification lane" is stale — the lane reports pipeline-validation at best). The frozen archive also remains visible in git history on `main` at `GHP_RESEARCH_LEDGER.md` prior to this hardening branch.
