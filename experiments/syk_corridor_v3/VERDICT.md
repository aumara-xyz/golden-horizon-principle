# SYK-CORRIDOR-v3 — CERTIFIED RUN VERDICT

- label: **CERTIFIED-CANDIDATE** — the first execution of this corridor for which every
  certification gate holds, including the venue gate (`venue_is_nebius=true`,
  `ladder_is_extended=true`, `CERTIFIED_VERDICT=true` in the pipeline's mechanical
  roll-up). Cost: **≈ USD 2.56 of the 400 cap** (computed from recorded rate × instance
  lifetime; see RUN_LOG Entry 12).
- governing contract (SIGNED, byte-frozen, unmodified):
  `experiments/SYK_CORRIDOR_PREREG_v3.md`
  sha256 `446a3c1e2deab541770df2075398b5b845c48ca94d30b85405fa0dbdd134097f`
  (measured at run time; matches the ledger row).
- runtime, byte-unchanged and verified pre- AND post-run against the contract pin:
  `experiments/syk_corridor/pipeline.py`
  measured sha256 `5f079d8976f1e1bd05672169151dd2d73e953adc2a3f7a87961fc174f768d226`,
  which **MATCHES the contract's runtime pin exactly** (both checks logged in
  `results_nebius/run_v3_stageB.log`).
- sole verdict bookkeeper (byte-frozen): `experiments/op179_nu_to_beta.py`
  sha256 `b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e` (MATCHES pin).
  Buckets below were additionally recomputed locally by importing the same frozen module;
  they agree with the pipeline's embedded output exactly.
- venue: Nebius instance `computeinstance-e00bxfxapwqb0874ny` (`syk-corridor-v3`, cpu-d3
  32vcpu-128gb), `--venue-nebius` asserted; **deprovisioned unconditionally** at run end and
  verified absent (instance and boot disk), per contract §6. Owner venue note (RUN_LOG
  Entry 2): the §8(d) official-ladder stage ALSO ran on this instance by owner direction
  (zero heavy compute on the owner's machine); venue is operational, not physics — sizes,
  seeds, grid, bytes, and gates unchanged. Stage A discharged §8(d) with all three direct-β
  gates passing and its `results_v3.json` committed before provisioning of the certified
  stage (commit 5420479).
- raw outputs: `experiments/syk_corridor/results_v3.json` (the pinned output path;
  sha256 `f5909585a6cbed8a026e146d1edcd0e1ce2924950f516fa9475ed6f2fa1adfc8`, byte-identical
  remote and retrieved), mirrored raw in `results_nebius/results_v3_stageB_certified.json`
  and provenance-wrapped in `results.json` here.
- date_utc: 2026-08-02T02:29:23Z. SELF-TESTS: ALL PASSED (hermiticity, even-parity block,
  determinism, level repulsion, op179 bucket import). **The run is not void.**
- grid as run (all pinned values obeyed exactly): official ladder **N ∈ {14, 18, 22, 24, 26}**
  (the §6 extended ladder; sector d = 64, 256, 1024, 2048, 4096 under the §1 pinned
  convention d = 2^(N/2 − 1)); N = 10 telemetry only (fit ban carried — no N = 10 number
  entered any fit or bucket); seeds 5000–5039 inclusive, 40 per (N, κ) point; the pinned
  κ grid [0, 1.00, 1.25, 1.57, 1.98, 2.48, 3.11, 3.90, 4.90, 6.15, 7.71, 9.68, 12.15,
  15.24, 19.13, 24.00]; bootstrap 2000 resamples everywhere.
- route: **direct-β PRIMARY** (contract §7 carrying v1 §3.1), under the §1 resolved
  d convention. The ν-route stayed CLOSED: `ChannelExponentAssignment` never filled,
  `nu_to_beta_verdict` never called, `m1_quotient_confirmation_flag` never called.

## 1. Certification gates (contract §5 + venue) — all discharged

| gate | pinned threshold | measured | result |
|---|---|---|---|
| G-β1 fit quality | pooled log Γ vs log d R² ≥ 0.98 | R² = 0.997555 | **PASS** |
| G-β2 intercept non-degeneracy | strictly interior of [0.30, 4.00]; < 5% edge mass per edge (2000 resamples) | intercept 2.70101; edge mass 0.000 / 0.000; DEGENERATE=false | **PASS** |
| G-β3 per-size Γ convergence | Γ > 0 at every official size; IC-7 window ≥ 5 points; ≤ 1% invalid resamples | Γ > 0 at all 5 sizes; windows 45/53/66/67/72; invalid 0/2000 | **PASS** |
| venue | `--venue-nebius` on the pinned Nebius venue, extended ladder | asserted; ladder {14,18,22,24,26} | **PASS** |

The retired ν-collapse gates (contract §5) were computed and reported in the telemetry
lane only; per the contract they decide nothing. For the record their values on this run:
per-size collapse R² {0.785, 0.929, 0.964, 0.961, 0.938}, ν bootstrap edge mass high 0.70 —
values that would have failed the retired v1/v2 gates, which is precisely the recorded
reason v3 re-scoped certification to the direct-β route the verdict actually uses.

## 2. Primary result — direct-β at κ = 0, pinned sector-d convention, full ladder

Measured Γ (disorder-averaged over the 40 pinned seeds):

| N | d_sector | Γ |
|---|---|---|
| 10 (telemetry) | 16 | 4.340e-4 |
| 14 | 64 | 4.770e-5 |
| 18 | 256 | 4.509e-6 |
| 22 | 1024 | 3.164e-7 |
| 24 | 2048 | 1.109e-7 |
| 26 | 4096 | 2.115e-8 |

Fits per the pinned protocol (pairwise log-log slopes at pair midpoints, primary linear
fit in 1/N to the intercept — now overdetermined with four midpoints, discharging the
IC-5 caveat as the contract stated; bootstrap 2000 resamples, 0 invalid):

| lane | β pairs (mid-N 16, 20, 23, 25) | pooled slope | **β intercept (1/N → 0)** | 95% CI |
|---|---|---|---|---|
| **PINNED: d = sector Hilbert dim** | 1.7016, 1.9166, 1.5125, 2.3905 | 1.8335 | **2.70101** | [2.27940, 3.10749] |
| SUPERSEDED diagnostic: d ~ 2^N | 0.8508, 0.9583, 0.7562, 1.1953 | 0.9168 | 1.35050 | [1.13970, 1.55375] |

Symmetry-class disclosure follow-through (contract §6, binding): the N = 24 point sits in
the undisclosed-class column (no repo source pins its class; standard RMT places
N mod 8 = 0 in the orthogonal class). The pairwise slopes visibly zig-zag around it
(1.5125 for the 22–24 pair, 2.3905 for the 24–26 pair), consistent with the disclosed
possible prefactor offset. Per the contract, **no size exclusion or re-cut was performed**;
the gates adjudicated mechanically on the full pinned ladder and passed (G-β1 R² 0.997555).

## 3. THE MECHANICAL VERDICT (byte-frozen op179 buckets; CI governs)

Primary certified lane (κ = 0, pinned sector-d convention):

- **point bucket** for β = 2.70101: **BOUNDARY** (the point falls in the upper boundary
  neighborhood of the extended band as derived algebraically inside the frozen bookkeeper).
- **CI bucket** for [2.27940, 3.10749]: **OUTSIDE_BAND** — the CI is not inside B1, does
  not overlap B1 (B1 ceiling 1.618034), is not inside K, and does not overlap
  K = [1.95, 2.05] (CI floor 2.27940 > 2.05).
- **Precedence (v1 §4, carried):** "when a confidence interval is reported, the CI rule
  governs Kill Condition 9; the point rule alone governs only if no CI exists." A CI is
  reported. **The CI rule governs. VERDICT: OUTSIDE BAND.**
- **Gate 5 / Kill Condition 9: does NOT fire** (`kill_condition_9_fires("OUTSIDE_BAND") =
  False`, frozen bookkeeper). The kill window was not hit: the certified CI lies entirely
  above K.
- Per the sourced rule text carried in the bookkeeper: outside band is "Non-kill,
  non-pass" — the corridor result neither supports nor kills; the module does not get to
  widen B1 retrospectively.

Superseded diagnostic lane (d ~ 2^N): point IN_BAND, CI STRONG_PASS — reported because the
§1 erratum requires the lane to stay permanently visible, and **forbidden from the verdict**:
it is the convention the signed erratum superseded. It is listed here as a diagnostic row
only and may not be quoted as a result.

ν telemetry lane: the collapse crossing fit landed at κ_c = 23.95 with only one grid point
above → the carried bracketing rule is NOT satisfied → **ν lane and crossing-adjacent
column VOID**, exactly as §3 of the contract disclosed could happen at the extension sizes
("if it does, the ν lane and crossing column void and the certified direct-β verdict is
unaffected"). The certified direct-β verdict above is unaffected.

## 4. Standing of the result

- **Certification status: CERTIFIED.** Venue, ladder, pins, self-tests, and all three
  direct-β gates hold on the same execution; this is the corridor's first certified verdict.
- **The certified verdict is OUTSIDE BAND (non-kill, non-pass).** Under the sourced CI
  rule this is the "outside band" branch: not consistent with the corridor's pass bands,
  and not a kill — the kill window [1.95, 2.05] is excluded by the certified CI, whose
  floor is 2.27940.
- What this does NOT do, mechanically: it does not fire Gate 5 / Kill Condition 9; it does
  not place the corridor in B1 or B2; it does not authorize any widening of the bands; it
  does not upgrade the superseded-convention diagnostic row into a result.
- Recorded observation, no interpretation attached: the infinite-d analytic standard null
  is 2 (center of K, master §5.10A.1, carried); the certified CI floor 2.27940 sits above
  it, and the finite-size intercept remains above the standard-null center on the extended
  ladder, with the N = 24 symmetry-class caveat of §2 disclosed above.

## 5. No-upgrade sentences (contract §9, verbatim, in force)

Until every gate above is discharged and the run completes under this signed protocol, no
SYK number may be reported as GHP support in either direction. An in-band result under a
pinned conversion whose standard-null placement was not first audited is not a pass; it is a
protocol violation. A kill closes Module C's strong claim, not GHP's architectural layer
(master §5.10A.4 survival table). A quotient-confirmation is a demotion, not a victory.
Software echoes may inform the theory; they do not confirm the physics.
