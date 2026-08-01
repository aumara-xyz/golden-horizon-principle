# Preregistration — SYK-CORRIDOR v3 (the VERDICT-§6 recorded path: certification re-scoped to the direct-β route, N-extended ladder with venue budget)

- test_id: SYK-CORRIDOR-v3
- ledger_anchor: ledger rows **P-002a**, **OP 111**, **OP 179**, **SYK-CORRIDOR**; packets
  **`GHP-PACKET-20260802-01`** and **`GHP-PACKET-20260802-02`**; the v2 official-run verdict
  **`experiments/syk_corridor_v2/VERDICT.md`** (its §6 is the recorded path this document
  contracts); `experiments/syk_corridor/LAPTOP_REPORT.md`; working paper
  `GHP_BOUNDARY_PROGRAM_v2.md` §6.3 and §12.4 item 2; master §5.7 and §5.10A;
  `experiments/SYK_STANDARD_NULL_AUDIT.md`.
- relation to v1 and v2: `experiments/SYK_CORRIDOR_PREREG_v1.md` (SIGNED 2026-08-01, sha256
  `59a46ff9b19b05b6c99dd0a58fb14629aecb11e0e5c2a94662e465820843f3d0`) and
  `experiments/SYK_CORRIDOR_PREREG_v2.md` (SIGNED 2026-08-02, sha256
  `7cdd8cfe6e902b3b27199b40bc63546f94551cab1a52c339343d6059816c7a5c`) are **FROZEN and
  unmodified**, as are their run products (`experiments/syk_corridor/LAPTOP_REPORT.md`,
  `experiments/syk_corridor/results_laptop.json`, `experiments/syk_corridor/results_v2.json`,
  `experiments/syk_corridor_v2/VERDICT.md`, `experiments/syk_corridor_v2/results.json`,
  `experiments/syk_corridor_v2/run_v2.log`). This document is a **NEW contract**, not an edit
  of either. It supersedes v2 for any future run of this corridor. Per the carried lock
  protocol, no run may ever execute under v1 or v2 again (v1's d-convention reading failed
  the discriminator criterion; v2's inherited ν-collapse certification gates fail
  deterministically on its pinned grid and seeds, and its official-size pin excludes the
  N-extension — both recorded mechanically in VERDICT.md §6).
- date_locked: **2026-08-02 (SIGNED)** (lock protocol as v1/v2: signature line completed,
  sentinel dated, SHA-256 of the signed file recorded in the ledger row, and only then may
  any corridor run execute; any post-signing edit to this document voids the run).
- lane: **GHP falsification lane** (carried verbatim from v1): per
  `GHP_BOUNDARY_PROGRAM_v2.md` §6.3, "the pass side is vacant ... and the meaningful
  commitment is the kill window," and "no SYK number may be reported as GHP support in
  either direction."
- runtime: **`experiments/syk_corridor/pipeline.py`, byte-pinned at sha256
  `5f079d8976f1e1bd05672169151dd2d73e953adc2a3f7a87961fc174f768d226`** (the v3 revision;
  the v2 official-run bytes, sha256
  `f5ad157c871a061a7244ed3767b9abe0affa034f1bdaac668343650a71c34511`, and the v1 laptop-run
  bytes, sha256 `873ae281dd563b607e550a2cba593471e40c7879dceb65731610158d269aaca7`, are
  preserved in git history and their frozen outputs are never rewritten — v3 writes
  `experiments/syk_corridor/results_v3.json`), plus `experiments/op179_nu_to_beta.py`
  (sha256 `b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e`) as the sole
  verdict bookkeeper. No physics code may be written for the verdict step outside that
  module. The hash direction is one-way (this contract pins the pipeline; the pipeline
  does not embed this contract's hash), so both hashes are checkable without circularity.
  The v3 pipeline revision changes NO physics arithmetic relative to the v2 bytes
  (Hamiltonian build, spectra, r-statistic, SFF, ramp windows, collapse machinery,
  pairwise-β extrapolation, and the bootstrap RNG call order are unchanged); it adds the
  §5 gate bookkeeping, the §6 ladder selection, and the v3 output path only.

---

## 0. Why this contract exists — the recorded path, quoted

The v2 official laptop run (`experiments/syk_corridor_v2/VERDICT.md`) discharged the
discriminator gate and validated the pipeline, and its §6 then recorded, mechanically, why
zero Nebius spend was correct under v2 and what a v3 must contain. Verbatim:

> Recommendation recorded for the owner: a v3 prereg that (i) keeps the section 1
> d-convention erratum and the section 4 Gamma pinning, (ii) re-scopes or drops the
> nu-collapse certification gates (the direct-beta primary route never needed them), and
> (iii) pins an N-extended size ladder with a venue budget, would make the first paid run
> capable of certifying.

This document is that v3 prereg, and nothing else: §1 and §4 implement (i) by carrying the
v2 resolutions verbatim; §5 implements (ii); §6 implements (iii). Everything not explicitly
changed in §§1–6 is inherited verbatim (§7).

## 1. CARRIED UNCHANGED — the d-convention erratum (v2 §1, in force)

The v2 §1 erratum is carried in full, unmodified, by reference to the frozen v2 file
(sha256 above). Its operative resolution, quoted verbatim:

> **The resolution (source definition outranks glossary shorthand).** §5.7 is the physics
> definition of the observable — the Module C spine that the glossary itself defers to ("This
> is the β used throughout §5.7"). The glossary's "d ~ 2^N" is a scaling shorthand, correct
> for a system of N qubits but wrong by a square root for a system of N Majorana fermions.
> Where an exact source definition and a glossary shorthand conflict, the definition governs.
> **PINNED for this corridor: d = the actual Hilbert-space dimension of the simulated
> system — the even-parity Majorana sector, d = 2^(N/2 − 1).** The v1 "d ~ 2^N" reading is
> retained in the pipeline output as a SUPERSEDED diagnostic lane only, so the effect of the
> erratum stays permanently visible in the data.

And its erratum note for the master, quoted verbatim:

> **Erratum note for the master.** Glossary line "revival ∝ 1/d^{β_crit} with d ~ 2^N"
> (§5.10A.1) should be read as "with d the Hilbert-space dimension of the observer system
> (d ~ 2^N for an N-qubit system; d = 2^(N/2) for N Majorana fermions)". This contract is
> the signed record of that reading; the master file itself is not edited by this lane.

For the §6 extension sizes the same pinned convention gives d = 2^(N/2 − 1) = 2048 (N = 24)
and 4096 (N = 26).

## 2. CARRIED AS DISCHARGED — the discriminator gate (v2 §2)

The governing criterion (`GHP_CORE_v3.md` §8, quoted in `SYK_STANDARD_NULL_AUDIT.md` §1 and
in v2 §2) and the bands/window (`GHP_v1_618_MASTER.md` §5.10A.2, quoted in v2 §2) are
incorporated by reference to the frozen v2 file; no band arithmetic is restated here (the
byte-frozen bookkeeper `op179_nu_to_beta.py` derives all band constants algebraically).

The gate itself was discharged at v2 signing and re-verified by the v2 official run
(VERDICT.md §1): under the §1 resolved convention the generic GUE / Fermi-golden-rule
standard answer measures, on the laptop anchor, at intercept **2.776** with 95% CI
**[1.902, 3.620]** — entirely above the shared B1/B2 pass ceiling (the upper endpoint of
both pass bands as quoted in v2 §2), in or above the kill window K = [1.95, 2.05], and
nowhere near the pass bands; the infinite-d analytic limit is 2, the center of K
(assignment-independent standard null, master §5.10A.1). **The corridor discriminates; the
standard-physics answer is not inside any pass band; that placement CARRIES to this
contract as already discharged** — the §1 convention, the §4 Γ operationalization, and the
κ = 0 primary column are unchanged, so the placement audit needs no re-derivation. The two
binding honesty notes of v2 §2 carry verbatim: (1) the anchor is PRELIMINARY-LAPTOP and
serves discriminator placement only; (2) exact diagonalization is deterministic in
(N, κ, seed), so any rerun's κ = 0 laptop-ladder column reproduces the laptop numbers —
certification certifies venue plus the pinned definitions, and (now) the new extension-size
data, not an independent replication of the κ = 0 laptop-ladder column.

## 3. CARRIED — the κ grid (v2 §3, verbatim), with the bracketing rule scoped

The v2 §3 grid is carried verbatim, including its pinned IC-2 mass-term normalization
("variance kappa^2 / N ... j2_scale = 1.0 per U.4", quoted in v2 §3 from the pipeline
disclosure) and its derivation record:

> **κ ∈ [0, 1.00, 1.25, 1.57, 1.98, 2.48, 3.11, 3.90, 4.90, 6.15, 7.71, 9.68, 12.15,
> 15.24, 19.13, 24.00]**

The bracketing rule is carried verbatim from v1 §1 via v2 §3:

> **the fitted crossing must be strictly interior with at least two grid points on each
> side, else the run is void**; no post-hoc grid extension after partial data are seen (per
> §5.10A.6.7 idiom: "No post-hoc extension"); a widened grid is a new timestamped
> preregistration.

**Scoping, made explicit by this contract (this is the established operative reading, not a
new rule):** the collapse fit whose crossing this rule brackets belongs to the CLOSED
ν-route, which is telemetry only (v1 §3.2, carried); and v2 §4's operative reading already
made the crossing-adjacent β column conditional on that fit ("if and only if the §3
crossing fit is valid (bracketing rule satisfied, non-degenerate bootstrap), β at the grid
point nearest the fitted crossing is additionally produced"). Accordingly, under v3 the
"void" of the bracketing rule voids the ν telemetry lane and the crossing-adjacent column —
exactly as the v1 laptop run already recorded it ("ν telemetry lane — VOID", LAPTOP_REPORT
§2, while the direct-β primary lane ran) — and is not a certification gate for the direct-β
verdict. Disclosed consequence for the extended ladder: the measured crossovers grow with N
(κ ≈ 4 / 9 / 10 at N = 14 / 18 / 22, LAPTOP_REPORT §2), so at N = 24/26 the collapse
crossing may approach the grid top and the bracketing rule may fail there; if it does, the
ν lane and crossing column void and the certified direct-β verdict is unaffected.

## 4. CARRIED UNCHANGED — the Γ pinning (v2 §4, in force)

The v2 §4 pinned definitions govern unchanged; the pinned pipeline implements them
byte-identically (the v3 revision does not touch this arithmetic). Quoted verbatim from
v2 §4:

**Γ operationalization (IC-3), PINNED:**

> Γ operationalization (IC-3, disclosed, **not source-pinned**): Γ := fitted linear
> slope of the disorder-averaged normalized spectral form factor
> g(t) = |Tr e^{−iHt}|²/d²_sector on its mechanically detected ramp window. The SFF
> is the object master §5.7 names as "The test"; under GUE universality this Γ
> scales as 1/d²_sector, reproducing the pinned assignment-independent standard
> null β_crit = 2 (Fermi golden rule under GUE, master §5.10A.1) when d is the
> sector Hilbert dimension.

(As in v2: the phrase "disclosed, **not source-pinned**" travels inside the quote as the
historical record of what v2 §4 changed; the definition IS pinned.)

**κ placement (IC-4), PINNED:**

> Primary column κ = 0 (IC-4: the undeformed SYK₄ point of the pinned grid; no κ is
> pinned for Γ by any source). The crossing-adjacent column was, per the pinned rule,
> **not produced** because the crossing fit is VOID (§2 above).

Operative reading (v2 §4, carried, with the §3 scoping above): the primary Γ column — the
one the verdict route buckets — is κ = 0; the crossing-adjacent column is produced if and
only if the crossing fit is valid, as telemetry adjacent to the primary column. The
ramp-window detection constants, SFF time grid, bootstrap freeze-and-reuse rule (IC-7), and
the remaining implementation choices IC-1/IC-5/IC-6 remain frozen operationally by this
contract's byte-pin of `pipeline.py`.

## 5. RE-SCOPED CERTIFICATION — ν-collapse gates retired; direct-β gates pinned

**Retirement of the inherited ν-collapse certification gates.** These four gates are legacy
machinery of the CLOSED ν-route, mistakenly carried by v2 §5 as certification requirements
for a route that never uses a ν number (the recorded finding of VERDICT.md §6.2). Each is
retired for this route with the v1 defining text (as quoted in v2 §5) preserved:

1. *ν search interval* — the v1 §2 pin "ν search interval "[0.30, 1.50]" ... fitted ν
   strictly interior" is RETIRED-FOR-THIS-ROUTE: it constrains a collapse parameter the
   direct-β verdict never reads.
2. *ν bootstrap edge-mass* — the v1 §2 pin "no more than "5%" of bootstrap mass in the
   outermost grid cell at either edge, else DEGENERATE → not certifiable" is
   RETIRED-FOR-THIS-ROUTE: its DEGENERATE flag bound certification to the closed lane's
   bootstrap, which fails deterministically on the pinned grid and seeds (VERDICT.md §4).
3. *per-size collapse R²* — the v1 §2 pin "per-size collapse "R² ≥ 0.98"" is
   RETIRED-FOR-THIS-ROUTE: it scores the quality of a scaling collapse that is telemetry
   only.
4. *cross-size correlation* — the v1 §2 pin "cross-size collapse correlation "≥ 0.99"" is
   RETIRED-FOR-THIS-ROUTE: it scores the same telemetry collapse and decides nothing for
   the direct-β verdict.

All four remain COMPUTED and REPORTED in the pipeline's ν telemetry lane for continuity
(the effect of this retirement stays permanently visible in the data, as the §1 erratum's
diagnostic lane does for the d convention); none may enter any bucket, verdict, or
certification gate.

**The direct-β certification gates, PINNED (replacing them; all applied to the §4 primary
column κ = 0 over the official ladder of the run, by the byte-pinned pipeline,
mechanically):**

- **G-β1 (fit quality):** the pooled linear fit of log Γ vs log d across the official
  ladder has **R² ≥ 0.98**. (R² is invariant under the affine map between the two log-d
  conventions, so this gate is well-defined independent of the §1 lane labels.)
- **G-β2 (bootstrap non-degeneracy of the intercept):** on the declared β search interval
  **[0.30, 4.00]**, the extrapolated 1/N intercept (the P-6 finite-size acceptance object,
  v1 §2 carried) is strictly interior, and **fewer than 5%** of the 2000 bootstrap
  resamples fall at or beyond either edge of the interval; else DEGENERATE → not
  certifiable. (The interval is declared here, once, before any v3 data exist; it contains
  both pass bands, the kill window, and the laptop anchor with its full CI, so it
  constrains degeneracy, not outcomes.)
- **G-β3 (per-size Γ measurement convergence, per the pinned IC definitions):** at every
  official-ladder size, the IC-3 fitted Γ is strictly positive on a frozen IC-7 ramp
  window containing **at least 5 points** (the IC-7 mechanical widening threshold), and
  **at most 1%** of the 2000 bootstrap resamples are invalid (non-positive resampled Γ at
  any size).

Bootstrap resample count (2000 everywhere) and the P-6 finite-size acceptance (primary
linear fit in 1/N over the official ladder, bootstrap uncertainty on the extrapolated
intercept) are carried verbatim from v1 §2 via v2 §5. With the §6 five-size certified
ladder, the 1/N fit runs over four pairwise midpoints and is overdetermined — discharging
the recorded IC-5 caveat ("The certified protocol should state this or add sizes",
LAPTOP_REPORT §5: this protocol does both).

## 6. THE LADDER — official sizes, cloud extension, venue budget

**Laptop official ladder (unchanged):** N ∈ {14, 18, 22}; N = 10 telemetry only (fit ban
carried verbatim from v1 §1: N = 10 "may not enter any fit, extrapolation, or bucket
decision").

**EXTENSION, authorized for the cloud venue only:** N ∈ {24, 26} (sector dimensions 2048
and 4096 under the §1 pinned convention). The certified run's official ladder is
**N ∈ {14, 18, 22, 24, 26}**. The extension sizes may not be run on the laptop as official
data; the pipeline's `--extended` mode without the venue flag is a diagnostic mode and is
never certifiable. This pin implements VERDICT.md §6.3, which recorded that bigger N was
outside v2's scope and that "an N-extended corridor — which is also what could cure the
degenerate collapse and the small-d overshoot in the beta intercept — requires a new signed
prereg (v3) before any spend": this section is that prereg text.

**Seeds (unchanged):** 5000–5039 inclusive, 40 per (N, κ) point, at every ladder size
including the extension sizes (v1 §1 carried; the determinism disclosure of §2 applies to
the laptop-ladder columns; every N = 24 and N = 26 number is new data).

**Symmetry-class disclosure (binding honesty note):** the repo source quoted in
LAPTOP_REPORT §1 — "SYK₄ at N mod 8 ∈ {2,6} is GUE class" — covers N = 26 (26 mod 8 = 2)
but NOT N = 24 (24 mod 8 = 0); no repo source states the N = 24 symmetry class
(MISSING-INPUT as a repo citation; the standard RMT classification places N mod 8 = 0 in
the orthogonal class). Consequence disclosed before any data exist: a symmetry-class
prefactor offset at N = 24 could depress the G-β1 fit R² or bend the intercept; the gates
adjudicate this mechanically, and **no post-hoc size exclusion or re-cut is permitted** —
if the extended-ladder fit fails a gate, the run is not certifiable, full stop.

**Venue budget line (the §6-(iii) "venue budget" of the recorded path):**

- Compute venue: Nebius (v1 §5 carried), asserted by `--venue-nebius`.
- **Hard cap: 400 USD** for the entire corridor run including voided reruns, carried
  verbatim from v1 §5: the cap "is a kill switch, not a target; an incomplete grid at cap
  produces no verdict."
- **Estimated cost, stated before provisioning:** the extension adds 640 exact
  diagonalizations per size (40 seeds × 16 κ points) at sector dimensions 2048 and 4096;
  on a single CPU node (32+ vCPU, ≥ 32 GB RAM) the expected wall time is order 4–12 hours
  and the expected cost at prevailing Nebius CPU-node rates is **well under 50 USD**. The
  operator MUST restate a concrete estimate (instance type × hourly rate × expected hours)
  in the run log before provisioning; if that estimate reaches the hard cap, provisioning
  is forbidden.
- **Deprovision unconditional:** the instance is deprovisioned at run end regardless of
  outcome — certified, non-certified, void, or crash. No standing infrastructure survives
  this contract.

## 7. Everything else — inherited VERBATIM

The following govern unchanged, incorporated by reference to the frozen v1 and v2 files
(SHA-256s in the header), with defining v1/v2 text quoted where numeric:

- **Verdict route (v1 §3.1, carried by v2 §5):** PRIMARY route is direct-β; buckets applied
  DIRECTLY by `op179_nu_to_beta.py` (`beta_bucket_point` / `beta_bucket_ci`), no
  channel-exponent assignment on this route — under the §1 resolved d convention.
- **ν-route (v1 §3.2, carried): CLOSED**, `ChannelExponentAssignment` port explicitly
  UNFILLED, `nu_to_beta_verdict` and `m1_quotient_confirmation_flag` never called;
  collapse-ν is telemetry only; the quotient-confirmation tolerance remains MISSING-INPUT
  and travels with the closed route; any reopening re-arms the v1 §3.2 standard-null hard
  gate.
- **Decision rule and precedence (v1 §4, in full, carried by v2 §5):** CI governs when a CI
  is reported ("when a confidence interval is reported, the CI rule governs Kill
  Condition 9; the point rule alone governs only if no CI exists"); bands B1/B2 and kill
  window K as quoted in v2 §2; the §5.10A.6.3 point rule and §5.10A.3 Option-B CI rule as
  written; kill flip fires Gate 5 / Kill Condition 9 with the master §5.10A.4 consequence,
  no renegotiation; the §5.10A.5 forbid list carried in full.
- **Bootstrap resample count (v1 §2):** "All bootstrap operations in this corridor use 2000
  resamples."
- **Mass-term normalization and grid derivation record (v2 §3, in full).**
- **Output discipline:** the run writes `results_v3.json` only; all v1/v2 outputs are
  frozen evidence.

## 8. Spend preconditions (the §12.4 item 2 ordering, re-armed for v3)

No Nebius spend of any size before, in order:

- (a) this document is signed and its SHA-256 plus the pinned pipeline SHA-256 are
  recorded in the ledger row (lock protocol, header);
- (b) the §1 d-convention erratum is in force (it is, at signing — carried from v2);
- (c) the §2 discriminator gate is discharged (it is, at signing — carried from v2, where
  it passed under the resolved convention; had it not, this contract would carry
  pipeline-validation language only and Nebius would be forbidden);
- (d) **the v3 LAPTOP OFFICIAL RUN completes without void**: the byte-pinned pipeline,
  executed with no ladder flags on the laptop official ladder {14, 18, 22}, self-tests
  passing, produces the §4 primary column and **discharges all three §5 direct-β gates**
  (G-β1, G-β2, G-β3; the venue gate alone excepted), writing
  `experiments/syk_corridor/results_v3.json`. VOID here means mechanically: any self-test
  failure, a primary column that cannot be produced (invalid Γ at any laptop-ladder size),
  or any of G-β1/G-β2/G-β3 FAIL. A void laptop run blocks all spend; so does any gate
  failure — a paid run against a laptop-foreknown gate failure repeats the exact mistake
  v2 §6.2 recorded, and is forbidden. The laptop run's `results_v3.json` is committed to
  git before any provisioning, so the certified execution's write to the same pinned
  output path never destroys evidence;
- (e) the §6 cost estimate is restated concretely in the run log before provisioning, under
  the cap;
- (f) the certified run executes the byte-pinned pipeline unchanged on the pinned Nebius
  venue with the `--venue-nebius` assertion (which selects the extended ladder
  {14, 18, 22, 24, 26}), under the 400 USD hard cap, writing `results_v3.json` only;
  deprovision is unconditional at run end.

## 9. No-upgrade sentences (carried verbatim in force from v1 §6 via v2 §7)

Until every gate above is discharged and the run completes under this signed protocol, no
SYK number may be reported as GHP support in either direction. An in-band result under a
pinned conversion whose standard-null placement was not first audited is not a pass; it is a
protocol violation. A kill closes Module C's strong claim, not GHP's architectural layer
(master §5.10A.4 survival table). A quotient-confirmation is a demotion, not a victory.
Software echoes may inform the theory; they do not confirm the physics.

**Signed:** Peter Viviani (owner), by standing directive 2026-08-02 ("get the tests on
Nebius ASAP... I approve whatever you need"), ratifying the v2 VERDICT section-6 path.
**Date (UTC):** 2026-08-02

*Until signed: no run. At signing, the SHA-256 of this file and of
`experiments/syk_corridor/pipeline.py` (v3 revision) are both recorded in the ledger row,
alongside the already-recorded `experiments/op179_nu_to_beta.py` hash, so "verdict computed
by the preregistered bookkeeper on the preregistered pipeline, byte-identical" is
checkable.*
