# Preregistration — SYK-CORRIDOR v1 (the OP 111 / OP 179 β corridor, rebuilt)

- test_id: SYK-CORRIDOR-v1
- ledger_anchor: ledger rows **P-002a** ("SYK β corridor — NEVER RUN (no preregistered β ever
  computed)"), **OP 111** ("The converter + bucket logic (incl. quotient-confirmation branch),
  specified but never coded"), **OP 179** (operational definition of β_fusion, OPEN); working
  paper `GHP_BOUNDARY_PROGRAM_v2.md` §6.3 and §12.4 item 2; master §5.10A (bands, buckets,
  kill demotion), Addendum M.1 (quotient-confirmation third bucket), AE.8/AE.9 (exponent
  clarification and non-unique channel assignment).
- date_locked: **2026-08-01 (SIGNED)** (lock protocol as AH.4-P1 v1.1: signature line
  completed, sentinel dated, SHA-256 of the signed file recorded in the ledger row, and only
  then may any corridor run execute; any post-signing edit to this document voids the run).
- ratification basis: the operational fills below are the recommended values of
  `experiments/SYK_ASSIGNMENT_DECISION_MEMO.md` §5, ratified by the owner's blanket chat
  directive of 2026-08-01 ("i approve everything that is waiting... push all this now").
  The §3 route decision is resolved by source (master Module C §5.7 and §5.10A.1 glossary,
  quoted verbatim in §3 below), not by invention.
- lane: **GHP falsification lane.** Per `GHP_BOUNDARY_PROGRAM_v2.md` §6.3, until this
  document is signed and its gates discharged, "the pass side is vacant ... and the meaningful
  commitment is the kill window," and "no SYK number may be reported as GHP support in either
  direction."
- runtime: the repaired SYK/C3 pipeline (twelve scripts path-fixed and syntax-verified
  2026-07-03 per ledger P-002a), plus `experiments/op179_nu_to_beta.py` as the sole verdict
  bookkeeper. No physics code may be written for the verdict step outside that module.

---

## 0. Why this prereg exists

Verbatim, `GHP_BOUNDARY_PROGRAM_v2.md` §6.3: "no pre-registered β has ever actually been
computed for this corridor." This document is the corridor's first complete pre-commitment:
every analysis choice below is fixed before any new seed is generated, per the master's
§5.10A.5 discipline ("The band is the commitment"). Fields marked **[OWNER-FILL]** are
choices the sources do not determine; they must be filled and signed BEFORE any run. Fields
marked **MISSING-INPUT** are definitions the repo's documents do not contain; they cannot be
invented by an agent and remain open until the owner (or a cited source) supplies them.

## 1. The measured quantity and the locked grid

- Measured quantity (verbatim, `GHP_BOUNDARY_PROGRAM_v2.md` §6.3): "the transition exponent
  ν in mass-deformed SYK₄, even-parity sector, across N = 10, 14, 18, 22."
- **Locked minimum N:** the run is incomplete unless **N = 22 is fully completed** (the prior
  attempt is void: "the N=22 40-seed hardening run (tight7×40) **died mid-seed**", §6.3).
- **N = 10 fit ban — CARRIED.** Verbatim, §6.3: "N=10 is banned from official fits by the
  project's own doorway note yet the pre-registration is written over all four sizes." This
  prereg resolves that inconsistency in the ban's favor: **official fits use N ∈ {14, 18, 22}
  only.** N = 10 data may be generated and reported as telemetry but may not enter any fit,
  extrapolation, or bucket decision.
- **κ grid:** must bracket the crossing before any fit is attempted (the prior grid failure is
  on record: "its κ grid no longer brackets the crossing," §6.3). Concrete grid:
  **κ ∈ [0, 15.8, 16.2, 16.4, 16.6, 16.7, 16.8, 16.85, 16.9, 16.95, 17.0, 17.1, 17.2, 17.5,
  18.0]** (the memo §5 recommended grid: the prior AI4 grid kept as a subset, extended on
  both sides), fixed at signing, with the memo's mechanical bracketing rule: **the fitted
  crossing must be strictly interior with at least two grid points on each side, else the
  run is void**; no post-hoc grid extension after partial data are seen (per §5.10A.6.7
  idiom: "No post-hoc extension"); a widened grid is a new timestamped preregistration.
- Seeds per size: **40 disorder seeds per size, explicit range 5000–5039 inclusive, per
  (N, κ) point**, N ∈ {14, 18, 22} for official fits (N = 10 telemetry only, per the carried
  ban), fixed at signing; seed ranges from any prior partial run are EXCLUDED from analysis
  (no double-dipping, per the AH4-P1-POWERED v2 idiom); 5000–5039 is disjoint from the
  consumed ranges on this branch (AH4-P1-POWERED v2: 3000–3399; SILVER-OPT-GEO v1:
  4000–4099), and any seeds from the dead tight7×40 partial run are EXCLUDED regardless.

## 2. Convergence criteria and finite-size acceptance test (fixed before any run)

- **Bootstrap rebuild — REQUIRED.** The prior bootstrap is void (verbatim, §6.3: "the
  ν-scaling-collapse bootstrap is **degenerate** (ν pegged at the grid ceiling)").
  Acceptance criterion, mechanical: the rebuilt bootstrap's ν search interval is
  **[0.30, 1.50]** with **2000 bootstrap resamples**; the fitted ν must lie strictly in the
  interval's interior, and the bootstrap distribution must not place more than **5%** of its
  mass within the outermost grid cell at either edge of the search interval. A bootstrap
  that pegs at either edge is DEGENERATE and the run is not certifiable — rerun with a
  widened preregistered search interval counts as a new run under a new timestamp, not a
  patch. (Under the §3 primary route the collapse-ν is telemetry, but this non-degeneracy
  criterion still binds: a degenerate ν bootstrap voids certification of the run.) All
  bootstrap operations in this corridor use 2000 resamples.
- **Convergence criteria:** per-size scaling-collapse quality **R² ≥ 0.98**, and cross-size
  collapse correlation **≥ 0.99** — the sources record a preliminary "Pearson 0.999
  cross-size correlation" (master §6 "C3") as shape universality but define no acceptance
  threshold; 0.99 is deliberately below the preliminary so the criterion does not smuggle in
  the old data's performance as a requirement (memo §5).
- **Finite-size acceptance test:** the extrapolation of the primary observable (and its
  uncertainty) to the reported value is fixed here as the corridor's analogue of the
  §5.10A.6.7 discipline, verbatim from the master: "extrapolate β(L) to β_crit with a
  primary linear fit in 1/L and bootstrap uncertainty on the extrapolated intercept" —
  i.e. for this corridor, **a primary linear fit in 1/N over the official sizes
  N ∈ {14, 18, 22}, with bootstrap uncertainty (2000 resamples) on the extrapolated
  intercept**, applied to the §3 primary observable (the direct-β fit slope), and identically
  to the ν telemetry lane. No alternative primary form may be introduced after partial data
  are seen; per §5.10A.6.7, "If partial data suggests a different extraction window or
  different relevant operator. That becomes a new timestamped preregistration."

## 3. The verdict route — RESOLVED AT SIGNING: PRIMARY ROUTE IS DIRECT-β

**Resolution basis (by source, not invention).** The master's Module C defines the
corridor's β DIRECTLY as revival-degradation scaling, with no ν intermediary. Verbatim,
`GHP_v1_618_MASTER.md` §5.7 ("Revival Degradation: the Module C physics spine"):

> Revival degradation rate:        Γ ∼ 1/d^β   where d = Hilbert space dimension

and verbatim, `GHP_v1_618_MASTER.md` §5.10A.1 glossary:

> **Critical exponent β_crit.** Continuous real number governing finite-N
> revival-degradation scaling in the Module C pipeline: revival ∝ 1/d^{β_crit} with
> d ~ 2^N. This is the β used throughout §5.7 and §5.10. Measurable on a continuum.

This is the original preregistered observable — β_crit is defined in β space by Module C
itself. Therefore:

### 3.1 PRIMARY route — direct-β (pinned at signing)

- **Measure Γ(d)** (revival degradation rate per §5.7) across the official sizes
  N ∈ {14, 18, 22}, with d ~ 2^N per the §5.10A.1 glossary (N = 10 telemetry only).
- **Fit log Γ vs log d**; the fitted slope's magnitude is β_crit at that size; extrapolate
  per §2 (primary linear fit in 1/N, bootstrap uncertainty on the extrapolated intercept).
- **Apply the β buckets of `experiments/op179_nu_to_beta.py` DIRECTLY**: the point verdict
  by `beta_bucket_point` (§5.10A.6.3 four-bucket rule as written) and the CI verdict by
  `beta_bucket_ci` (§5.10A.3 Option-B explicit-CI rule as written), with the §4 precedence
  (CI governs when a CI is reported). **NO channel-exponent assignment is needed on this
  route**: the buckets are defined in β space and the direct-β route never passes through ν.
  The `ChannelExponentAssignment` port and `nu_to_beta_verdict` are NOT invoked.
- **Standard-null placement on this route — already complete and favorable.** Per
  `experiments/SYK_STANDARD_NULL_AUDIT.md` §4, the direct-β standard null is β_crit = 2
  (Fermi golden rule under GUE, master §5.10A.1), sitting at the center of the kill window K
  and outside both B1 and B2 — and per the decision memo §4, this placement is
  **assignment-independent**. The pass region is clean of the standard-physics answer on the
  direct-β route; the `GHP_CORE_v3.md` §8 discriminator criterion ("No new compute for any
  test whose pass-region contains the standard-physics answer") is satisfied for this route.

### 3.2 ν-route — CLOSED pending OP 179 (assignment port explicitly UNFILLED)

- The ν→β conversion route is **CLOSED**. The channel-exponent assignment (the injected
  port `ChannelExponentAssignment` of `experiments/op179_nu_to_beta.py`, which has no
  default) is **explicitly left unfilled** at signing. No ν-derived number may enter any
  bucket, verdict, or gate under this preregistration. Collapse-ν results are recorded as
  telemetry only.
- Per AE.9 the assignment is non-unique (candidates: magnitude-of-eigenvalue → 1.236, RMS
  form → 1.328, CFT-weight-based → 1.412, squared eigenvalues → 1.764), and no ν→β formula
  exists anywhere in the repo's documents (MISSING-INPUT; the OP 179 operational-definition
  demand remains OPEN for this route).
- **Candidate A context (chosen-by-argument note, carried without being pinned):**
  Candidate A (magnitude-of-eigenvalue, β_crit ≈ 1.236) is the only source-defined
  candidate — the only one with a written calculation (AE.9 §5.10A.3); the complete written
  provenance of B, C, and D is a single sentence with no derivation (decision memo §2.3).
  Its honest caveat is carried verbatim (AE.9, why-not-a-derivation, item ii): "(ii)
  ν_TCI = 5/4 is the M(4,5) order-parameter exponent, a quantity known before this
  calculation was performed. Hitting 1.236 is post-hoc agreement, not prediction." This
  context does NOT pin the port.
- **Standard-null audit re-run — HARD GATE, carried for any ν-route reopening.** If a
  future timestamped preregistration reopens the ν-route by pinning the port,
  `experiments/SYK_STANDARD_NULL_AUDIT.md` §6 must first be re-executed under the pinned
  conversion: map ν = 1/2 (Louw et al. 2024 mean-field), ν_TCI = 5/9, and the ν ≈ 0.7
  tricritical/quotient lane through the converter. **If any standard ν-null lands in the
  pass band B1 under the pinned conversion, that preregistration is VOID and no compute is
  committed** — per `GHP_CORE_v3.md` §8: "No new compute for any test whose pass-region
  contains the standard-physics answer."

## 4. Decision rule (signed before data; executed by op179_nu_to_beta.py verbatim)

- **Rule precedence (owner signs this explicitly):** when a confidence interval is
  reported, the CI rule governs Kill Condition 9; the point rule alone governs only
  if no CI exists. Basis: master §5.10A.3 (boundary-region CI "Does NOT count as
  pass or kill") and §5.10A.4 ("within stable error bars"). A run that cannot
  produce a non-degenerate CI at the preregistered thresholds is reported as
  capability-statement only — it can neither pass nor kill.

- Bands: B1 = [1/φ, φ] = [0.618034, 1.618034]; B2 = [1/φ², φ]; **Kill window K =
  [1.95, 2.05]** (master §5.10A.2, quoted in full in the converter docstring).
- Point rule: the §5.10A.6.3 four-bucket rule as written (Strong pass / In-band / Boundary /
  Kill; outside reported as such, never reclassified).
- CI rule: the §5.10A.3 Option-B explicit-CI rule as written.
- **Kill flip:** a KILL bucket fires **Gate 5 / Kill Condition 9** ("Gate 5" ≡ "Kill
  Condition 9" per `GHP_BOUNDARY_PROGRAM_v2.md` §0.2 E-1). Consequence on the page, without
  renegotiation, per master §5.10A.4: "the critical φ-dynamics claim is false"; Module C is
  demoted; "φ remains architecture-facing unless and until a distinct dynamical derivation
  forces it back." No "the observer happened to sample β ≈ 2 this run" escape (§5.10A.5
  item 3).
- **Quotient-confirmation third bucket (Addendum M.1 / OP 111; "third bucket" per
  `GHP_CORE_v3.md` Appendix B):** if ν lands stably near the tricritical/quotient lane
  (ν ≈ 0.7), the result is recorded as quotient-confirmation — "Module C may be weakened,
  not killed" — and per §6.3 "must be honestly labeled as a demotion of the strong φ-critical
  claim." Tolerance for "stably near": **remains MISSING-INPUT (M.1 supplies no number),
  and the field travels with the CLOSED ν-route (§3.2)**: the flag
  `m1_quotient_confirmation_flag` takes ν, the ν-route is closed under this
  preregistration, and no number may be invented by an agent — therefore **no
  quotient-confirmation flag may be emitted by this run**; ν ≈ 0.7 telemetry is recorded as
  telemetry only. Supplying the tolerance is part of any future ν-route reopening under a
  new timestamped preregistration. The flag never upgrades any β bucket.
- §5.10A.5 forbid list carried in full: no retrospective narrowing, no retrospective
  widening, no kill-window reinterpretation, no silent supersession, no band-substitution
  escape.

## 5. Budget (the Nebius line)

- Compute venue: Nebius. **Budget cap for the entire corridor run (all sizes, all seeds,
  including reruns voided by degenerate bootstraps): hard cap 400 USD.**
- The cap is a kill switch, not a target: reaching the cap with an incomplete grid voids the
  run (an incomplete grid produces no verdict — the same refuse-to-emit discipline as
  `verdict_v3.py` on the DMRG side, §6.2).
- No spend of any size before: (a) this document is signed, (b) the §3 verdict route is
  resolved — DISCHARGED AT SIGNING: direct-β primary (§3.1), ν-route closed with the
  assignment port unfilled (§3.2), (c) the standard-null placement for the primary route is
  clean — DISCHARGED AT SIGNING per §3.1: the direct-β standard null β_crit = 2 sits inside
  K and outside B1/B2 (`SYK_STANDARD_NULL_AUDIT.md` §4), assignment-independent. This
  ordering is the §12.4 item 2 mandate: the check comes "before any compute is committed."
  Any future ν-route reopening re-arms the §3.2 hard gate before any further spend.

## 6. No-upgrade sentences (carried)

Until every gate above is discharged and the run completes under this signed protocol, no
SYK number may be reported as GHP support in either direction. An in-band result under a
pinned conversion whose standard-null placement was not first audited is not a pass; it is a
protocol violation. A kill closes Module C's strong claim, not GHP's architectural layer
(master §5.10A.4 survival table). A quotient-confirmation is a demotion, not a victory.
Software echoes may inform the theory; they do not confirm the physics.

**Signed:** Peter Viviani (owner), by chat directive 2026-08-01 (ratifying the decision
memo's recommended fills). **Date (UTC):** 2026-08-01

*Until signed: no run. At signing, the SHA-256 of this file and of
`experiments/op179_nu_to_beta.py` are both recorded in the ledger row, so "verdict computed
by the preregistered bookkeeper, byte-identical" is checkable.*
