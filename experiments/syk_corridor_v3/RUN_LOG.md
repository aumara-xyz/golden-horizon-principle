# SYK-CORRIDOR v3 — RUN LOG

Governing contract: `experiments/SYK_CORRIDOR_PREREG_v3.md`
(SIGNED 2026-08-02, sha256 `446a3c1e2deab541770df2075398b5b845c48ca94d30b85405fa0dbdd134097f`,
recorded in the RESEARCH_LEDGER row per the lock protocol — §8(a) discharged before this log
was opened).

This log is the operational record required by PREREG v3 §6 (cost estimate stated before
provisioning) and §8 (spend-precondition ordering). It is append-only; entries are
timestamped UTC.

---

## Entry 1 — pre-run pin verification (local, hash-check only) — 2026-08-01T23:20Z

Measured on the checkout at branch `syk/v3-2026-08-02`:

```
sha256(experiments/syk_corridor/pipeline.py)      = 5f079d8976f1e1bd05672169151dd2d73e953adc2a3f7a87961fc174f768d226   MATCHES contract pin
sha256(experiments/op179_nu_to_beta.py)           = b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e   MATCHES contract pin
sha256(experiments/SYK_CORRIDOR_PREREG_v3.md)     = 446a3c1e2deab541770df2075398b5b845c48ca94d30b85405fa0dbdd134097f   MATCHES ledger row
sha256(experiments/SYK_CORRIDOR_PREREG_v2.md)     = 7cdd8cfe6e902b3b27199b40bc63546f94551cab1a52c339343d6059816c7a5c   FROZEN, intact
sha256(experiments/SYK_CORRIDOR_PREREG_v1.md)     = 59a46ff9b19b05b6c99dd0a58fb14629aecb11e0e5c2a94662e465820843f3d0   FROZEN, intact
```

The v2→v3 pipeline diff (git `b53e3b0` → `1ba9bfb`) was reviewed line by line: all changes
are gate bookkeeping (§5 direct-β gates), ladder selection (§6 `--extended` /
`--venue-nebius`), output path (`results_v3.json`), and docstring/provenance text. No
physics arithmetic and no RNG call-order change — consistent with the contract's runtime
line ("changes NO physics arithmetic relative to the v2 bytes").

## Entry 2 — VENUE NOTE (owner-directed, operational) — 2026-08-01T23:20Z

Owner mandate 2026-08-02 (binding): zero heavy compute on the owner's machine (hardware
overheating). ALL diagonalization executes on Nebius. Where PREREG v3 uses "laptop" as a
venue word (§6 "laptop official ladder", §8(d) "LAPTOP OFFICIAL RUN"), the corresponding
stage is executed on the Nebius instance instead, by owner direction; venue is operational,
not physics — sizes, seeds, κ grid, pipeline bytes, and gate definitions are unchanged.
The local machine performs only: hash verification, script authoring, CLI orchestration,
and analysis of the returned result files.

## Entry 3 — v2-data reuse decision — 2026-08-01T23:20Z

Reuse of the committed v2 run data for N ∈ {14, 18, 22} is permitted only if the v3 pins
are byte-identical to the bytes that produced that data. They are not:
`results_v2.json` / `syk_corridor_v2/results.json` were produced by pipeline bytes
`f5ad157c…` (v2 pin), while the v3 contract pins `5f079d89…`. NOT byte-identical →
**no reuse**. The official ladder {14, 18, 22} is folded into the Nebius job (per the owner
mandate it may not be rerun locally), as stage A below.

## Entry 4 — §5 gate pre-check on in-hand v2 data (foreknown-failure screen) — 2026-08-01T23:20Z

Because the v3 revision is physics-identical, the v2 official numbers predict the stage-A
laptop-ladder column exactly (determinism disclosure, PREREG v3 §2). Mechanical pre-check
against `experiments/syk_corridor/results_v2.json` (primary column κ=0, sector-d lane):

- G-β1 (pooled log Γ vs log d fit R² ≥ 0.98 over {14,18,22}): computed R² = **0.99882** → predicts PASS.
- G-β2 (intercept interior of [0.30, 4.00]; < 5% bootstrap edge mass): intercept **2.7764**,
  CI95 [1.9020, 3.6204] — both endpoints strictly inside the interval, so edge mass at
  either edge is < 2.5% → predicts PASS.
- G-β3 (Γ > 0 at every size; IC-7 window ≥ 5 points; ≤ 1% invalid resamples): Γ =
  {4.77e-05, 4.51e-06, 3.16e-07} all > 0; windows {45, 53, 66} points; invalid resamples
  0/2000 → predicts PASS.

No foreknown gate failure. The §8(d)-forbidden case ("a paid run against a laptop-foreknown
gate failure") does not obtain; proceeding to the estimate.

## Entry 5 — §6/§8(e) COST ESTIMATE, stated before provisioning — 2026-08-01T23:25Z

Queried live from the Nebius billing calculator (project `project-e00v3avmpr00fzcxq8s6x7`):

- Instance: platform **cpu-d3**, preset **32vcpu-128gb** = **0.7936 USD/hr**
  (cheapest-adequate: the contract's stated node class is "32+ vCPU, ≥ 32 GB RAM"; the
  16-vCPU preset is cheaper but halves LAPACK throughput on the d=4096 diagonalizations,
  and cpu-e2/cpu-d3 price identically, so cpu-d3 32vcpu is taken).
- Boot disk: 64 GiB NETWORK_SSD = **0.00622 USD/hr**.
- Wall-time budget: stage A (official ladder {14,18,22}, no ladder flags) ≈ 1 h; stage B
  (`--venue-nebius`, extended ladder {14,18,22,24,26}) ≈ 3–5.5 h (N=26 sector d = 4096:
  640 diagonalizations dominate); setup + transfer ≈ 0.5 h. Budgeted ceiling **8 h**.

**Estimate: 0.7936 + 0.0062 ≈ 0.80 USD/hr × ≤ 8 h ≈ 6.40 USD (upper bound ~10 USD with
retries).** This is far below the 400 USD hard cap and below the contract's own "well
under 50 USD" expectation → provisioning is permitted. The cap remains a kill switch: if
consumption approaches the cap the run stops void with no verdict.

Deprovision is unconditional at run end (certified, non-certified, void, or crash), per §6.

## Entry 6 — provisioning record — 2026-08-01T23:21Z (retro-logged at 00:40Z)

Instance `computeinstance-e00bxfxapwqb0874ny` (`syk-corridor-v3`, cpu-d3 32vcpu-128gb,
boot 64 GiB NETWORK_SSD, public IP 195.242.13.180) created 23:21Z, RUNNING ~23:23Z.
Spec file: `experiments/syk_corridor_v3/nebius_instance.yaml`. Pinned files uploaded;
remote sha256 of `pipeline.py` and `op179_nu_to_beta.py` verified byte-identical to the
contract pins before any execution (recorded in `run_v3_stageA.log`).

## Entry 7 — STAGE A: the §8(d) official-ladder run — completed 2026-08-02T00:35Z

Executed on the Nebius instance per the Entry-2 owner venue note (contract venue word:
"laptop"): `python3 pipeline.py` with NO ladder flags — official ladder {14, 18, 22},
N = 10 telemetry, seeds 5000–5039, pinned κ grid. Wall ~72 min (N=22 sweep 515 s,
ν-bootstrap 3643 s on this core class). Post-run remote hashes re-verified: MATCH pins.

Result (`results_v3_stageA_official_ladder.json`, also committed at the pinned path
`experiments/syk_corridor/results_v3.json` BEFORE the certified run executes, so the
certified write to the same path destroys no evidence):

- SELF-TESTS: ALL PASSED → not void.
- G-β1: pooled log Γ vs log d R² = 0.99882 ≥ 0.98 → **PASS**.
- G-β2: intercept 2.77637, strictly interior of [0.30, 4.00]; bootstrap edge mass
  low 0.000 / high 0.005, both < 0.05 → **PASS** (not DEGENERATE).
- G-β3: Γ > 0 at every size; IC-7 windows 45/53/66 points ≥ 5; invalid resamples
  0/2000 ≤ 1% → **PASS**.
- Venue gate alone unpassed (as §8(d) excepts): `venue_is_nebius=false` because the
  `--venue-nebius` assertion belongs to the certified extended run only; roll-up
  correctly labels stage A PIPELINE-VALIDATION ONLY.
- Reproduction check: γ, intercept, CI, and every bucket agree with the frozen v2
  official numbers to ≤ ~1e-12 relative (cross-BLAS floating-point rounding on the
  cloud LAPACK vs the laptop's); all bucket labels identical
  (point OUTSIDE / CI UNCLASSIFIED_BY_RULE at κ=0, sector-d lane).

**§8(d) DISCHARGED (no void, all three direct-β gates pass). Spend gate for the
certified extended run is open.**

## Entry 8 — stage B LAPACK backend note — 2026-08-02T00:42Z

The instance's stock `python3-numpy` links the single-threaded reference BLAS/LAPACK
(measured: eigvalsh d=4096 ≈ 52.7 s → the N=26 column alone would be ~9.4 h). For the
certified run the system LAPACK alternative is switched to the threaded OpenBLAS
(`libopenblas0-pthread` via `update-alternatives`) — an environment-level change only;
the byte-pinned pipeline and bookkeeper are untouched (hashes re-verified pre-run).
Stage A above ran entirely on the reference backend; the ≤1e-12 stage-A-vs-v2 agreement
already bounds the cross-LAPACK effect at far below every gate threshold.

## Entry 9 — recovery note — 2026-08-02T01:00Z

The orchestrating host process died after stage B was launched under nohup (2026-08-02T00:36:31Z).
Recovery per owner directive: SSH re-attach to the SAME instance (no second instance provisioned);
job PID 9856 (`python3 -u pipeline.py --venue-nebius`) found alive mid-sweep (N=24 column done,
N=26 in progress); polled bounded until completion. No relaunch was needed.

## Entry 10 — STAGE B: the certified §8(f) extended run — completed 2026-08-02T02:29:23Z

Executed on the pinned Nebius venue with `--venue-nebius` (extended ladder {14,18,22,24,26},
N=10 telemetry, seeds 5000–5039, pinned κ grid, OpenBLAS backend per Entry 8; pipeline and
bookkeeper hashes verified byte-identical to the contract pins pre- AND post-run, logged in
`run_v3_stageB.log`). Wall times: sweep N=22 82.0 s / N=24 323.3 s / N=26 1963.0 s;
ν-bootstrap (telemetry lane) 4338 s. SELF-TESTS: ALL PASSED. Job ran to normal exit.

- G-β1: pooled log Γ vs log d R² = 0.99755 ≥ 0.98 → **PASS**.
- G-β2: intercept 2.70101 strictly interior of [0.30, 4.00]; bootstrap edge mass 0.000 / 0.000 → **PASS**.
- G-β3: Γ > 0 at every official size; IC-7 windows 45/53/66/67/72 points ≥ 5; invalid resamples 0/2000 → **PASS**.
- Venue gate: `venue_is_nebius=true`, `ladder_is_extended=true` → **CERTIFIED_VERDICT=true**, status CERTIFIED-CANDIDATE.
- ν telemetry lane: collapse crossing κ_c = 23.95 with only 1 grid point above → bracketing rule
  NOT satisfied → ν lane and crossing-adjacent column **VOID**, exactly as PREREG v3 §3 disclosed
  for large N; the certified direct-β verdict is unaffected (contract text).

## Entry 11 — retrieval + evidence chain — 2026-08-02T02:30Z

`results_v3.json` retrieved; sha256
`f5909585a6cbed8a026e146d1edcd0e1ce2924950f516fa9475ed6f2fa1adfc8` identical remote and local.
Copies: `experiments/syk_corridor/results_v3.json` (the pinned output path — overwriting the
stage-A file, which was committed to git at 5420479 before provisioning per §8(d), so no
evidence destroyed), `experiments/syk_corridor_v3/results_nebius/results_v3_stageB_certified.json`
(raw), `experiments/syk_corridor_v3/results.json` (provenance-wrapped), plus `run_v3_stageB.log`.

## Entry 12 — DEPROVISION (unconditional) + cost actual — 2026-08-02T02:31Z

Instance `computeinstance-e00bxfxapwqb0874ny` deleted 02:30:21Z→02:31:02Z; verified absent from
the instance list; its boot disk `syk-corridor-v3-boot` verified absent from the disk list
(auto-deleted with the instance). No standing infrastructure survives this contract.
Pre-existing instances of other lanes (aukora-crucible-h100, aukora-g0-41707f91, both STOPPED
since before this corridor) were not touched.

Cost actual (computed from the recorded rate × instance lifetime; lifetime 2026-08-01T23:18:47Z
→ 2026-08-02T02:31:02Z = 3.204 h; rate 0.7936 + 0.0062 USD/hr): **≈ 2.56 USD** of the 400 USD
hard cap (estimate was ≈ 6.40; both stages ran on the one instance). Cap never approached.
