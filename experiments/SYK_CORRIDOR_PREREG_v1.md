# Preregistration — SYK-CORRIDOR v1 (the OP 111 / OP 179 β corridor, rebuilt)

- test_id: SYK-CORRIDOR-v1
- ledger_anchor: ledger rows **P-002a** ("SYK β corridor — NEVER RUN (no preregistered β ever
  computed)"), **OP 111** ("The converter + bucket logic (incl. quotient-confirmation branch),
  specified but never coded"), **OP 179** (operational definition of β_fusion, OPEN); working
  paper `GHP_BOUNDARY_PROGRAM_v2.md` §6.3 and §12.4 item 2; master §5.10A (bands, buckets,
  kill demotion), Addendum M.1 (quotient-confirmation third bucket), AE.8/AE.9 (exponent
  clarification and non-unique channel assignment).
- date_locked: **PENDING OWNER SIGNATURE** (lock protocol as AH.4-P1 v1.1: signature line
  completed, sentinel dated, SHA-256 of the signed file recorded in the ledger row, and only
  then may any corridor run execute; any post-signing edit to this document voids the run).
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
  **[OWNER-FILL: κ min / max / spacing]**, fixed at signing; no post-hoc grid extension after
  partial data are seen (per §5.10A.6.7 idiom: "No post-hoc extension").
- Seeds per size: **[OWNER-FILL: count and explicit seed range]**, fixed at signing; seed
  ranges from any prior partial run are EXCLUDED from analysis (no double-dipping, per the
  AH4-P1-POWERED v2 idiom).

## 2. Convergence criteria and finite-size acceptance test (fixed before any run)

- **Bootstrap rebuild — REQUIRED.** The prior bootstrap is void (verbatim, §6.3: "the
  ν-scaling-collapse bootstrap is **degenerate** (ν pegged at the grid ceiling)").
  Acceptance criterion, mechanical: the rebuilt bootstrap's ν search interval must contain
  the fitted ν strictly in its interior, and the bootstrap distribution must not place more
  than **[OWNER-FILL: %]** of its mass on either search-interval edge. A bootstrap that pegs
  at either edge is DEGENERATE and the run is not certifiable — rerun with a widened
  preregistered search interval counts as a new run under a new timestamp, not a patch.
- **Convergence criteria:** per-size collapse quality threshold and cross-size stability
  threshold **[OWNER-FILL: metric + numeric thresholds]** — the sources record a preliminary
  "Pearson 0.999 cross-size correlation" (master §6 "C3") as shape universality but define no
  acceptance threshold; the threshold is therefore an owner choice and MUST be numeric and
  signed before data.
- **Finite-size acceptance test:** the extrapolation form of ν (and its uncertainty) to the
  reported value is fixed here as **[OWNER-FILL: primary extrapolation form, e.g. the
  corridor's analogue of the §5.10A.6.7 "primary linear fit in 1/L ... bootstrap uncertainty
  on the extrapolated intercept" discipline]**. No alternative primary form may be introduced
  after partial data are seen; per §5.10A.6.7, "If partial data suggests a different
  extraction window or different relevant operator. That becomes a new timestamped
  preregistration."

## 3. The ν→β conversion port (the OP 179 gate) — REQUIRED BEFORE SIGNATURE

- The verdict is computed exclusively by `experiments/op179_nu_to_beta.py`, whose
  channel-exponent assignment is an **injected port with no default**.
- Per AE.9 the assignment is non-unique (candidates: magnitude-of-eigenvalue → 1.236, RMS
  form → 1.328, CFT-weight-based → 1.412, squared eigenvalues → 1.764). The owner must pin:
  - assignment name: **[OWNER-FILL]**
  - conversion function ν→β, written out explicitly: **[OWNER-FILL — MISSING-INPUT: no ν→β
    formula exists anywhere in the repo's documents; supplying one is the resolution of
    OP 179's operational-definition demand and must cite its derivation]**
- **Standard-null audit re-run — HARD GATE.** After the port is pinned and before any spend,
  `experiments/SYK_STANDARD_NULL_AUDIT.md` §6 must be re-executed under the pinned
  conversion: map ν = 1/2 (Louw et al. 2024 mean-field), ν_TCI = 5/9, and the ν ≈ 0.7
  tricritical/quotient lane through the converter. **If any standard ν-null lands in the pass
  band B1 under the pinned conversion, this preregistration is VOID and no compute is
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
  claim." Tolerance for "stably near": **[OWNER-FILL — MISSING-INPUT: M.1 supplies no
  number]**, passed explicitly to `m1_quotient_confirmation_flag`. The flag never upgrades
  any β bucket.
- §5.10A.5 forbid list carried in full: no retrospective narrowing, no retrospective
  widening, no kill-window reinterpretation, no silent supersession, no band-substitution
  escape.

## 5. Budget (the Nebius line)

- Compute venue: Nebius. **Budget cap for the entire corridor run (all sizes, all seeds,
  including reruns voided by degenerate bootstraps): [OWNER-FILL: hard cap in USD].**
- The cap is a kill switch, not a target: reaching the cap with an incomplete grid voids the
  run (an incomplete grid produces no verdict — the same refuse-to-emit discipline as
  `verdict_v3.py` on the DMRG side, §6.2).
- No spend of any size before: (a) this document is signed, (b) the §3 port is pinned,
  (c) the §3 standard-null audit re-run passes. This ordering is the §12.4 item 2 mandate:
  the check comes "before any compute is committed."

## 6. No-upgrade sentences (carried)

Until every gate above is discharged and the run completes under this signed protocol, no
SYK number may be reported as GHP support in either direction. An in-band result under a
pinned conversion whose standard-null placement was not first audited is not a pass; it is a
protocol violation. A kill closes Module C's strong claim, not GHP's architectural layer
(master §5.10A.4 survival table). A quotient-confirmation is a demotion, not a victory.
Software echoes may inform the theory; they do not confirm the physics.

**Signed:** ______________________ (owner) **Date (UTC):** ____________

*Until signed: no run. At signing, the SHA-256 of this file and of
`experiments/op179_nu_to_beta.py` are both recorded in the ledger row, so "verdict computed
by the preregistered bookkeeper, byte-identical" is checkable.*
