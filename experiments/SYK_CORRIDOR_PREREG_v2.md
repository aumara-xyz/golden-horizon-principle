# Preregistration — SYK-CORRIDOR v2 (blocker-resolution contract for the OP 111 / OP 179 β corridor)

- test_id: SYK-CORRIDOR-v2
- ledger_anchor: ledger rows **P-002a**, **OP 111**, **OP 179**; night-close packet
  **`GHP-PACKET-20260802-01`** (the three contract-grounded blockers this document resolves);
  `experiments/syk_corridor/LAPTOP_REPORT.md` (the pipeline-validation run that surfaced them);
  working paper `GHP_BOUNDARY_PROGRAM_v2.md` §6.3 and §12.4 item 2; master §5.7 and §5.10A;
  `experiments/SYK_STANDARD_NULL_AUDIT.md`.
- relation to v1: `experiments/SYK_CORRIDOR_PREREG_v1.md` (SIGNED 2026-08-01, sha256
  `59a46ff9b19b05b6c99dd0a58fb14629aecb11e0e5c2a94662e465820843f3d0`) is **FROZEN and
  unmodified**, as are its run products `experiments/syk_corridor/LAPTOP_REPORT.md` and
  `experiments/syk_corridor/results_laptop.json`. This document is a **NEW contract**, not an
  edit of v1. It supersedes v1 for any future run of this corridor. Per v1's own lock
  protocol, no run may ever execute under v1 again (its d-convention reading failed the
  discriminator criterion; §2 below).
- date_locked: **2026-08-02 (SIGNED)** (lock protocol as v1: signature line completed,
  sentinel dated, SHA-256 of the signed file recorded in the ledger row, and only then may
  any corridor run execute; any post-signing edit to this document voids the run).
- lane: **GHP falsification lane** (carried verbatim from v1): per
  `GHP_BOUNDARY_PROGRAM_v2.md` §6.3, "the pass side is vacant ... and the meaningful
  commitment is the kill window," and "no SYK number may be reported as GHP support in
  either direction."
- runtime: **`experiments/syk_corridor/pipeline.py`, byte-pinned at sha256
  `f5ad157c871a061a7244ed3767b9abe0affa034f1bdaac668343650a71c34511`** (the v2 revision;
  the laptop run's as-run bytes, sha256
  `873ae281dd563b607e550a2cba593471e40c7879dceb65731610158d269aaca7`, are preserved in git
  history and their frozen outputs are never rewritten — v2 writes
  `experiments/syk_corridor/results_v2.json`), plus `experiments/op179_nu_to_beta.py`
  (sha256 `b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e`) as the sole
  verdict bookkeeper. No physics code may be written for the verdict step outside that
  module. The hash direction is one-way (this contract pins the pipeline; the pipeline
  does not embed this contract's hash), so both hashes are checkable without circularity.

---

## 0. Why this contract exists — the three blockers, each resolved BY SOURCE

The v1-governed laptop pipeline-validation run (`experiments/syk_corridor/LAPTOP_REPORT.md`)
and the ledger packet `GHP-PACKET-20260802-01` recorded three contract-grounded blockers that
stopped all Nebius spend ("NEBIUS BLOCKED BY THE MACHINE ITSELF, ZERO SPEND"). Verbatim, the
packet's owner-decision line:

> OWNER DECISIONS REQUIRED before any SYK spend: (a) resolve the d convention by signed
> erratum or new prereg; (b) re-derive the κ grid under the resolved normalization; (c) pin
> the Γ operationalization in writing.

This document is that new prereg: §1 resolves (a), §3 resolves (b), §4 resolves (c). Every
resolution below is grounded in a quoted repo source or in the laptop run's own recorded
measurements; nothing is reconstructed from memory. Everything not explicitly changed in
§§1–4 is inherited from v1 verbatim (§5).

## 1. ERRATUM — the d convention, resolved (blocker (a))

**The two conflicting source lines, quoted verbatim.**

Master `GHP_v1_618_MASTER.md` §5.7 ("Revival Degradation: the Module C physics spine") — the
SOURCE definition of the observable:

> Revival degradation rate:        Γ ∼ 1/d^β   where d = Hilbert space dimension

Master `GHP_v1_618_MASTER.md` §5.10A.1 glossary — the shorthand v1 §3.1 pinned:

> **Critical exponent β_crit.** Continuous real number governing finite-N
> revival-degradation scaling in the Module C pipeline: revival ∝ 1/d^{β_crit} with
> d ~ 2^N. This is the β used throughout §5.7 and §5.10. Measurable on a continuum.

**The conflict.** For the corridor's actual simulated system — Majorana SYK₄ — these two
statements disagree. The Majorana arithmetic, written out:

- The system has N Majorana fermions ψ₁ … ψ_N with {ψ_a, ψ_b} = δ_ab.
- N Majorana fermions pair into N/2 Dirac fermions, i.e. N/2 qubits under Jordan–Wigner.
- The full Hilbert-space dimension is therefore **2^(N/2)**, not 2^N.
- The simulated system is the even-fermion-parity sector (v1 §1, "even-parity sector",
  carried), whose dimension is **2^(N/2 − 1)**: d = 16 / 64 / 256 / 1024 for
  N = 10 / 14 / 18 / 22 (the laptop run's measured sector dims, LAPTOP_REPORT §3).
- Because 2^(N/2) and 2^(N/2 − 1) differ by a fixed factor of 2, log d differs by a
  constant offset across sizes and every log-log slope (hence every fitted β) is
  **identical** under the two; the full-space vs sector distinction is immaterial to β.
  The 2^N vs 2^(N/2) distinction is NOT immaterial: it doubles log d per unit N and
  therefore **halves every fitted β**.

**The resolution (source definition outranks glossary shorthand).** §5.7 is the physics
definition of the observable — the Module C spine that the glossary itself defers to ("This
is the β used throughout §5.7"). The glossary's "d ~ 2^N" is a scaling shorthand, correct
for a system of N qubits but wrong by a square root for a system of N Majorana fermions.
Where an exact source definition and a glossary shorthand conflict, the definition governs.
**PINNED for this corridor: d = the actual Hilbert-space dimension of the simulated
system — the even-parity Majorana sector, d = 2^(N/2 − 1).** The v1 "d ~ 2^N" reading is
retained in the pipeline output as a SUPERSEDED diagnostic lane only, so the effect of the
erratum stays permanently visible in the data.

**Erratum note for the master.** Glossary line "revival ∝ 1/d^{β_crit} with d ~ 2^N"
(§5.10A.1) should be read as "with d the Hilbert-space dimension of the observer system
(d ~ 2^N for an N-qubit system; d = 2^(N/2) for N Majorana fermions)". This contract is
the signed record of that reading; the master file itself is not edited by this lane.

## 2. THE GATE — discriminator placement under the resolved convention

The governing criterion, verbatim (`GHP_CORE_v3.md` §8, quoted in
`SYK_STANDARD_NULL_AUDIT.md` §1):

> **The rule (the discriminator criterion):** *No new compute for any test whose pass-region
> contains the standard-physics answer.* A test that cannot fail cannot inform.

Bands and window, verbatim (`GHP_v1_618_MASTER.md` §5.10A.2, quoted in
`SYK_STANDARD_NULL_AUDIT.md` §3):

> **Primary band B1: β_crit ∈ [1/φ, φ] = [0.618034, 1.618034].**
>
> **Extended band B2: β_crit ∈ [1/φ², φ] = [0.381966, 1.618034].**
>
> **Kill window K: β_crit ∈ [1.95, 2.05].**

**The standard-physics answer under the resolved convention.** Analytically: the
assignment-independent standard null is β_crit = 2 (Fermi golden rule under GUE, master
§5.10A.1, quoted in full in `SYK_STANDARD_NULL_AUDIT.md` §4) — and that calculation is a
statement about Γ vs the Hilbert-space dimension, i.e. it lives in the §1 resolved
convention. Empirically, the laptop run is the anchor (LAPTOP_REPORT §3, measured at κ = 0
over the pinned seeds): under the superseded "d ~ 2^N" reading the generic answer computed
to an intercept of **1.388**, 95% CI [0.951, 1.810] — INSIDE pass band B1, which is what
blocked v1. Under the resolved convention (sector Hilbert dimension) the same measured
Γ values give:

- pairwise slopes **1.702 → 1.917** (climbing toward the golden-rule value 2 exactly as
  RMT predicts as d grows),
- 1/N-extrapolated intercept **2.776**, 95% CI **[1.902, 3.620]** (the finite-size
  overshoot above 2 is the slowly varying many-body bandwidth at small d, disclosed in
  LAPTOP_REPORT §3).

**Placement, stated honestly with its CI.** The laptop generic answer under the resolved
convention sits near 2.8: the point estimate 2.776 lies **outside B1, outside B2, and above
the kill window K**; its entire 95% CI [1.902, 3.620] lies **above the B1/B2 pass ceiling
1.618034** (lower edge 1.902, clear of the pass side by the full CI margin) and straddles
K from just below its floor 1.95 to well above. The infinite-d analytic limit is 2, the
center of K. Under the resolved convention the generic GUE / Fermi-golden-rule answer
therefore lands **in or above the kill window and nowhere near the pass bands**.

**Verdict of the gate: the standard-physics answer is NOT inside any pass band → the
corridor discriminates → the Nebius run is PERMITTED under this contract** (subject to §6).
Had the resolved convention placed the standard answer inside B1 or B2, this contract would
have self-limited to pipeline-validation language and ZERO cloud spend; it does not.

Two honesty notes, binding:

1. The empirical anchor is PRELIMINARY-LAPTOP. Its role here is only discriminator
   placement (a §12.4-item-2 pre-compute check), not physics support; per §7 no SYK number
   is GHP support in either direction.
2. Because exact diagonalization is deterministic in (N, κ, seed) and §5 carries the v1
   seeds 5000–5039, the certified run's κ = 0 primary column is expected to reproduce the
   laptop numbers; the certified run certifies **venue plus the now-pinned definitions**
   (and produces the new deformed-grid columns, which are all new data under the §3 grid).
   This is disclosed so the certification cannot be mistaken for an independent
   replication of the κ = 0 column.

## 3. The κ grid, re-derived from the laptop run's measured crossover (blocker (b))

**Pinned mass-term normalization (promoted from disclosed IC-2 to PINNED; the grid is
derived under it and is meaningless without it).** Verbatim from the laptop pipeline's
disclosure (`pipeline.py` IC-2, as run):

> Mass term: H2 = i * sum_{i<j} K_ij psi_i psi_j with K_ij Gaussian,
> variance kappa^2 / N (the standard SYK_2 normalization; j2_scale = 1.0
> per U.4).

**The empirical crossover under that normalization.** Verbatim, LAPTOP_REPORT §2:

> ⟨r⟩ at κ ≥ 15.8 is already 0.41–0.45 everywhere, ordered r₂₂ > r₁₈ > r₁₄ with no
> common crossing in-grid; a discarded 6-seed pilot at seeds 1–6 located the
> midpoint crossovers near κ ≈ 4 / 9 / 10 for N = 14 / 18 / 22

**The v2 grid (pinned at signing; derived from those numbers, not copied from v1).** A
common log-spaced grid over [1, 24]: 15 deformed points at ratio 24^(1/14) ≈ 1.2548,
rounded to two decimals, plus the κ = 0 pure-SYK₄ reference point (reference only —
excluded from the collapse fit; it is the §4 primary Γ column):

> **κ ∈ [0, 1.00, 1.25, 1.57, 1.98, 2.48, 3.11, 3.90, 4.90, 6.15, 7.71, 9.68, 12.15,
> 15.24, 19.13, 24.00]**

Derivation and bracketing check against the measured per-size crossovers (design margin:
at least three deformed points strictly on each side of every measured crossing):

| N | measured crossover κ_c | deformed points below | deformed points above |
|---|---|---|---|
| 14 | ≈ 4 | 7 (1.00 … 3.90) | 8 (4.90 … 24.00) |
| 18 | ≈ 9 | 8 (1.00 … 7.71) | 5 (9.68 … 24.00) |
| 22 | ≈ 10 | 9 (1.00 … 9.68) | 4 (12.15 … 24.00) |

The lower endpoint 1.00 sits a factor 4 below the smallest measured crossing and the upper
endpoint 24.00 a factor 2.4 above the largest, so the bracketing survives substantial drift
between the 6-seed pilot and the pinned 40-seed statistics. Log spacing gives uniform
resolution in log κ across the factor-2.5 spread of the per-size crossings.

**Bracketing rule, carried verbatim from v1 §1** (the mechanical void rule the grid must
satisfy at fit time):

> **the fitted crossing must be strictly interior with at least two grid points on each
> side, else the run is void**; no post-hoc grid extension after partial data are seen (per
> §5.10A.6.7 idiom: "No post-hoc extension"); a widened grid is a new timestamped
> preregistration.

## 4. Γ pinning (blocker (c)) — IC-3/IC-4 promoted from disclosed choices to PINNED

The v1 gap, verbatim (LAPTOP_REPORT §5): "IC-3 Γ operationalization and IC-4 κ-placement
are not source-pinned ... A certified run must pin them in writing." This section is that
writing. The next run is certified against the following written definitions, quoted
exactly from LAPTOP_REPORT.md's own wording (§3), which the pinned pipeline implements
byte-identically:

**Γ operationalization (IC-3), PINNED:**

> Γ operationalization (IC-3, disclosed, **not source-pinned**): Γ := fitted linear
> slope of the disorder-averaged normalized spectral form factor
> g(t) = |Tr e^{−iHt}|²/d²_sector on its mechanically detected ramp window. The SFF
> is the object master §5.7 names as "The test"; under GUE universality this Γ
> scales as 1/d²_sector, reproducing the pinned assignment-independent standard
> null β_crit = 2 (Fermi golden rule under GUE, master §5.10A.1) when d is the
> sector Hilbert dimension.

(The phrase "disclosed, **not source-pinned**" travels inside the quote as the historical
record of what this section changes: as of this signing the definition IS pinned.)

**κ placement (IC-4), PINNED:**

> Primary column κ = 0 (IC-4: the undeformed SYK₄ point of the pinned grid; no κ is
> pinned for Γ by any source). The crossing-adjacent column was, per the pinned rule,
> **not produced** because the crossing fit is VOID (§2 above).

Operative reading under v2: the primary Γ column (the one the §5 verdict route buckets) is
κ = 0; if and only if the §3 crossing fit is valid (bracketing rule satisfied,
non-degenerate bootstrap), β at the grid point nearest the fitted crossing is additionally
produced and reported alongside, as telemetry adjacent to the primary column.

**Mechanical constants.** The ramp-window detection constants, SFF time grid, and
freeze-and-reuse rule for bootstrap resamples (IC-7), and the remaining implementation
choices IC-1 and IC-5/IC-6, are frozen operationally by this contract's byte-pin of
`pipeline.py` (runtime line above): the certified run must execute that exact file, so no
disclosed choice can drift between signing and run.

## 5. Everything else — inherited from v1 VERBATIM

The following v1 pins govern unchanged, incorporated by reference to the frozen v1 file
(sha256 above), with their defining v1 text quoted where numeric:

- **Sizes and fit ban (v1 §1):** official fits use N ∈ {14, 18, 22} only; N = 10 generated
  as telemetry, "may not enter any fit, extrapolation, or bucket decision."
- **Seeds (v1 §1):** "40 disorder seeds per size, explicit range 5000–5039 inclusive, per
  (N, κ) point" (with §2 honesty note 2 above disclosing the deterministic κ = 0 overlap
  with the laptop validation run).
- **Bootstrap gates (v1 §2):** ν search interval "[0.30, 1.50]" with "2000 bootstrap
  resamples"; fitted ν strictly interior; no more than "5%" of bootstrap mass in the
  outermost grid cell at either edge, else DEGENERATE → not certifiable; "All bootstrap
  operations in this corridor use 2000 resamples."
- **Convergence (v1 §2):** per-size collapse "R² ≥ 0.98", cross-size collapse correlation
  "≥ 0.99".
- **Finite-size acceptance (v1 §2):** "a primary linear fit in 1/N over the official sizes
  N ∈ {14, 18, 22}, with bootstrap uncertainty (2000 resamples) on the extrapolated
  intercept," applied to the direct-β primary observable and identically to the ν
  telemetry lane.
- **Verdict route (v1 §3.1):** PRIMARY route is direct-β; buckets applied DIRECTLY by
  `op179_nu_to_beta.py` (`beta_bucket_point` / `beta_bucket_ci`), no channel-exponent
  assignment on this route — under the §1 resolved d convention.
- **ν-route (v1 §3.2): CLOSED**, `ChannelExponentAssignment` port explicitly UNFILLED,
  `nu_to_beta_verdict` and `m1_quotient_confirmation_flag` never called; collapse-ν is
  telemetry only; the quotient-confirmation tolerance remains MISSING-INPUT and travels
  with the closed route; any reopening re-arms the v1 §3.2 standard-null hard gate.
- **Decision rule and precedence (v1 §4, in full):** CI governs when a CI is reported
  ("when a confidence interval is reported, the CI rule governs Kill Condition 9; the
  point rule alone governs only if no CI exists"); bands B1/B2 and kill window K as quoted
  in §2 above; the §5.10A.6.3 point rule and §5.10A.3 Option-B CI rule as written; kill
  flip fires Gate 5 / Kill Condition 9 with the master §5.10A.4 consequence, no
  renegotiation; the §5.10A.5 forbid list carried in full.
- **Budget (v1 §5):** compute venue Nebius; "hard cap 400 USD" for the entire corridor run
  including voided reruns; the cap is a kill switch, not a target; an incomplete grid at
  cap produces no verdict.
- **No-upgrade sentences (v1 §6, in full).**

## 6. Spend preconditions (the §12.4 item 2 ordering, re-armed for v2)

No spend of any size before, in order:

- (a) this document is signed and its SHA-256 plus the pinned pipeline SHA-256 are
  recorded in the ledger row (lock protocol, header);
- (b) the §1 d-convention erratum is in force (it is, at signing);
- (c) **the §2 discriminator gate passes** — it does, at signing, under the resolved
  convention: the standard answer lies outside both pass bands. Had it not, this contract
  would carry pipeline-validation language only and Nebius would be forbidden;
- (d) the run executes the byte-pinned pipeline on the pinned Nebius venue under the $400
  hard cap, with the `--venue-nebius` assertion, writing `results_v2.json` only.

## 7. No-upgrade sentences (carried verbatim in force from v1 §6)

Until every gate above is discharged and the run completes under this signed protocol, no
SYK number may be reported as GHP support in either direction. An in-band result under a
pinned conversion whose standard-null placement was not first audited is not a pass; it is a
protocol violation. A kill closes Module C's strong claim, not GHP's architectural layer
(master §5.10A.4 survival table). A quotient-confirmation is a demotion, not a victory.
Software echoes may inform the theory; they do not confirm the physics.

**Signed:** Peter Viviani (owner), by morning directive 2026-08-02 ("Continue on with
whatever you need to do. I approve whatever you need"), ratifying the source-grounded
resolutions above. **Date (UTC):** 2026-08-02

*Until signed: no run. At signing, the SHA-256 of this file and of
`experiments/syk_corridor/pipeline.py` (v2 revision) are both recorded in the ledger row,
alongside the already-recorded `experiments/op179_nu_to_beta.py` hash, so "verdict computed
by the preregistered bookkeeper on the preregistered pipeline, byte-identical" is
checkable.*
