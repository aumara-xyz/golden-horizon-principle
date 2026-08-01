# SYK-CORRIDOR-v1 — LAPTOP RUN REPORT

- label: **PRELIMINARY-LAPTOP / PIPELINE-VALIDATION** (not the certified corridor run)
- date_utc: 2026-08-01T14:44:34Z
- branch: night/run-2026-08-01
- governing contract (SIGNED, unmodified):
  `experiments/SYK_CORRIDOR_PREREG_v1.md`
  sha256 `59a46ff9b19b05b6c99dd0a58fb14629aecb11e0e5c2a94662e465820843f3d0`
- verdict bookkeeper (unmodified, sole source of bucket logic):
  `experiments/op179_nu_to_beta.py`
  sha256 `b1fbb56f480a938523fcd5a3ff1dfd8d34ae4597e96ca49f280d6bbbefa1694e`
- pipeline: `experiments/syk_corridor/pipeline.py` (new file, this run)
- raw output: `experiments/syk_corridor/results_laptop.json`
- spend: **USD 0.00** of the 400 cap. No Nebius (or any cloud) compute was committed.
- route executed: **direct-β primary** per prereg §3.1. The ν-route stayed CLOSED:
  the `ChannelExponentAssignment` port was never filled, `nu_to_beta_verdict` was
  never called, `m1_quotient_confirmation_flag` was never called. Collapse-ν below
  is telemetry only.

## 0. Why this is not the certified run

1. **Venue.** Prereg §5 pins "Compute venue: Nebius." This execution is a laptop
   run of the identical exact-diagonalization arithmetic. Everything below is
   therefore PRELIMINARY-LAPTOP; the contract's certified verdict remains unissued.
2. **Pinned pipeline absent from repo.** The prereg's runtime line names "the
   repaired SYK/C3 pipeline (twelve scripts...)". Those scripts are not in this
   repository (master U.4 locates them under `.epsilon/…`, an external tree).
   `pipeline.py` is a rebuild; every non-pinned choice it makes is disclosed as
   IC-1…IC-7 in its docstring and summarized in §5 below.
3. Per prereg §6: **no SYK number in this report is GHP support in either
   direction.**

## 1. What ran (all pinned values obeyed exactly)

- Sizes: official N ∈ {14, 18, 22}; N = 10 generated as telemetry only (fit ban
  CARRIED; no N = 10 number enters any fit or bucket).
- Seeds: 5000–5039 inclusive, 40 per size, per (N, κ) point.
- κ grid: the pinned 15-point grid [0, 15.8, …, 18.0].
- Model: Majorana SYK₄ (⟨J²_ijkl⟩ = 6J²/N³, J = 1, per master §5.10 pseudocode /
  U.4 j4_scale = 1.0) + random 2-fermion mass term (IC-2 normalization
  ⟨K²_ij⟩ = κ²/N, j2_scale = 1.0), even-parity sector, exact diagonalization
  (sector dims 16 / 64 / 256 / 1024).
- Self-tests (all PASSED, log in results): Hermiticity to 0; even-parity block
  exactness to 0; determinism under fixed seed (byte-identical H, sha256
  checked); level-repulsion sanity — SYK₄ at κ = 0 gives ⟨r⟩ = 0.5811 (6-seed
  self-test) and 0.591–0.598 across all four sizes in the pinned sweep, against
  GUE ≈ 0.5996 (SYK₄ at N mod 8 ∈ {2,6} is GUE class) vs Poisson ≈ 0.3863.
- Bootstrap: 2000 resamples everywhere, per the contract.

## 2. ν telemetry lane — VOID by the contract's own mechanical rules

The pinned void machinery fired, and fired correctly:

| check | pinned rule | result | outcome |
|---|---|---|---|
| crossing bracket | κ_c strictly interior, ≥ 2 grid pts each side | fitted κ_c = 17.95: 13 below, **1 above** | **FAIL → run VOID** (prereg §1) |
| bootstrap non-degeneracy | ν ∈ (0.30, 1.50) interior; ≤ 5% edge mass | fitted ν = 0.30 = search FLOOR; **100%** of 2000 resamples in the lowest grid cell | **DEGENERATE → not certifiable** (prereg §2) |
| per-size collapse R² | ≥ 0.98 | −324 / −35 / −36 (no collapse) | FAIL |
| cross-size correlation | ≥ 0.99 | 0.9991 / 0.9985 / 0.9997 | PASS |

Reading: under the standard SYK₂ mass normalization (IC-2), the
chaotic-integrable crossover sits **below** the pinned grid at all official sizes
(⟨r⟩ at κ ≥ 15.8 is already 0.41–0.45 everywhere, ordered r₂₂ > r₁₈ > r₁₄ with no
common crossing in-grid; a discarded 6-seed pilot at seeds 1–6 located the
midpoint crossovers near κ ≈ 4 / 9 / 10 for N = 14 / 18 / 22). The collapse
optimizer therefore pegged κ_c at the top of the span and ν at the search floor.
This reproduces, in mirror image, the prior recorded failure ("its κ grid no
longer brackets the crossing … ν pegged at the grid ceiling", boundary v2 §6.3)
— and demonstrates the contract's void rules fire mechanically instead of
emitting a number. The cross-size correlation ≈ 0.999 matches the source's
recorded "Pearson 0.999 cross-size correlation" shape-universality note (master
§6) while both stricter criteria fail — evidence the R²/bracketing gates add
real discrimination beyond shape universality.

Pairwise-collapse extrapolation (pinned §2 form, telemetry): ν pairs 0.30 / 0.30
→ intercept 0.30 — degenerate with the above, carries no content. **No ν number
here may enter any bucket, verdict, or gate (prereg §3.2), and none did.**

## 3. Direct-β lane (primary route) — PRELIMINARY-LAPTOP numbers

Γ operationalization (IC-3, disclosed, **not source-pinned**): Γ := fitted linear
slope of the disorder-averaged normalized spectral form factor
g(t) = |Tr e^{−iHt}|²/d²_sector on its mechanically detected ramp window. The SFF
is the object master §5.7 names as "The test"; under GUE universality this Γ
scales as 1/d²_sector, reproducing the pinned assignment-independent standard
null β_crit = 2 (Fermi golden rule under GUE, master §5.10A.1) when d is the
sector Hilbert dimension. Primary column κ = 0 (IC-4: the undeformed SYK₄ point
of the pinned grid; no κ is pinned for Γ by any source). The crossing-adjacent
column was, per the pinned rule, **not produced** because the crossing fit is
VOID (§2 above).

Measured Γ (κ = 0, disorder-averaged over the 40 pinned seeds):

| N | d_sector | Γ |
|---|---|---|
| 10 (telemetry) | 16 | 4.34e-4 |
| 14 | 64 | 4.77e-5 |
| 18 | 256 | 4.51e-6 |
| 22 | 1024 | 3.16e-7 |

β per the pinned protocol (pairwise log-log slopes at pair midpoints → primary
linear fit in 1/N → intercept; bootstrap 2000 resamples, 0 invalid):

| d convention | β pairs (N=16, N=20) | pooled slope | **β intercept (1/N → 0)** | 95% CI |
|---|---|---|---|---|
| **d ~ 2^N (pinned, prereg §3.1 / glossary)** | 0.851, 0.958 | 0.905 | **1.388** | [0.951, 1.810] |
| d = sector Hilbert dim (diagnostic) | 1.702, 1.917 | 1.809 | **2.776** | [1.902, 3.620] |

op179 buckets, applied mechanically by the byte-frozen bookkeeper
(PRELIMINARY-LAPTOP; **not a certified verdict**):

- pinned d ~ 2^N: point rule **IN_BAND**; CI rule **BOUNDARY_REGION** — per the
  signed §4 precedence the CI rule governs, and a boundary-region CI "Does NOT
  count as pass or kill". Kill Condition 9 does not fire.
- diagnostic d_sector: point rule **OUTSIDE**; CI rule **UNCLASSIFIED_BY_RULE**
  (CI [1.90, 3.62] straddles K without touching B1). Kill Condition 9 does not
  fire.

β(κ) telemetry across the whole pinned grid is flat (1.31–1.39 pinned-d;
2.62–2.78 sector-d) — the deformed points at κ ≥ 15.8 are all in the
post-crossover regime under IC-2, so no critical enhancement is visible in-grid.

Physics reading, laptop-grade only: at κ = 0 the system IS the generic-GUE
standard null, and the sector-dimension pairwise slopes climb 1.70 → 1.92 toward
the golden-rule value 2 exactly as RMT predicts (the residual deficit is the
slowly varying many-body bandwidth at small d; the 1/N intercept overshoots to
2.78 for the same reason). The pipeline reproduces known physics where known
physics is the answer. Nothing here is a φ-signal in either direction.

## 4. FINDING THAT GATES CERTIFICATION — the d-convention conflict

Master §5.7 defines Γ ~ 1/d^β with "d = Hilbert space dimension"; the §5.10A.1
glossary (and therefore prereg §3.1, which pins the glossary reading) says
"d ~ 2^N". For a Majorana system these disagree: the Hilbert dimension is
2^(N/2) (sector 2^(N/2−1)), not 2^N. The factor 2 in the exponent halves every
fitted β. Consequence, now demonstrated numerically: **under the pinned d ~ 2^N
convention the generic-GUE standard-physics answer computes to β ≈ 0.9–1.0 —
INSIDE the pass band B1 — not β = 2 in the kill window.** The §3.1 claim that
"the direct-β standard null is β_crit = 2 … at the center of the kill window"
(and the §5 gate (c) discharge that relied on it) is true only under
d = Hilbert dimension. Under the literal pinned convention the corridor would
fail the `GHP_CORE_v3.md` §8 discriminator criterion ("No new compute for any
test whose pass-region contains the standard-physics answer").

**Before any Nebius spend, the owner must resolve the d convention in a new
timestamped preregistration (or an owner-signed erratum to the glossary
reading).** This is a §12.4-item-2-class check surfaced by pipeline validation,
exactly what a pre-compute laptop pass is for. Nothing in this paragraph is a
physics claim; it is arithmetic on the pinned definitions.

## 5. Other certification caveats (disclosed implementation choices)

- IC-2 mass normalization: the `.epsilon` convention that placed the crossing
  near κ ≈ 16.9 is not recoverable from this repository. Under the standard
  ⟨K²⟩ = κ²/N used here, the pinned grid does not bracket the crossing at any
  official size (hence the §2 VOID). A certified run needs the mass-term
  normalization pinned by the owner (or the original scripts recovered), or a
  new preregistered grid.
- IC-3 Γ operationalization and IC-4 κ-placement are not source-pinned (OP 179's
  "specify the observable, the data pipeline, and the fit protocol" is,
  operationally, still the open item for the direct-β route too). A certified
  run must pin them in writing.
- IC-5 per-size β via pairwise midpoints: with three official sizes the §2
  "linear fit in 1/N" over per-size direct-β slopes is exactly determined by two
  pairwise slopes; the intercept inherits their full finite-size drift (visible
  above). The certified protocol should state this or add sizes.
- Seed-range note for the record: prereg §1's disjointness rationale predates
  SILVER-OPT-SCALE v1 (commit b24b81d), which consumed seed integers 5000–5099
  in an unrelated pipeline on this branch. The prereg's exclusion clause binds
  only prior runs of THIS corridor, so the pinned 5000–5039 remains valid; noted
  for transparency.

## 6. Certification gate roll-up (from results_laptop.json)

| gate | state |
|---|---|
| venue is Nebius | NO (laptop) |
| crossing bracketing | FAIL → ν-lane VOID |
| ν bootstrap non-degenerate | FAIL (100% edge mass at search floor) |
| collapse R² ≥ 0.98 | FAIL |
| cross-size corr ≥ 0.99 | PASS (0.999) |
| Γ operationalization source-pinned | NO |
| **CERTIFIED VERDICT** | **NO — PIPELINE-VALIDATION ONLY** |

## 7. No-upgrade sentences (carried verbatim in spirit from prereg §6)

No SYK number in this report is GHP support in either direction. The
PRELIMINARY-LAPTOP buckets above are mechanical outputs on non-certified
numbers; they neither pass nor kill anything. A kill, were one ever certified,
closes Module C's strong claim, not GHP's architectural layer. Software echoes
may inform the theory; they do not confirm the physics.
