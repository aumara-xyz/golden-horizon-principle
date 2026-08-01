# Preregistration — SILVER-OPT v1 (characterize the silver anomaly)

- test_id: SILVER-OPT-v1
- ledger_anchor: ledger row **SILVER-OPT** (OPEN, restored 2026-07-29); named in the v2.1 edition; roadmap item 1a.
- date_locked: **2026-08-01 (SIGNED)** (lock protocol as AH.4-P1 v1.1; hash recorded in the ledger at signing).
- lane: **constant-axis anomaly characterization. Explicitly GHP-independent** (M-006: no silver fusion category exists, so no structural reading is available; no branch of this test is GHP physics evidence).
- runtime: Python 3 + numpy, deterministic, offline, single-core.

## 0. The anomaly

Four independent instruments show silver ≥ golden: GH-RECOV's critical band and adversarial tear (~5σ for silver); T-111 sampler friction; T-112 rotation ranking; the SEL-CLOSE-001 KAM thresholds. Unexplained, φ-negative, and potentially the programme's first novel positive result about *something* — even if that something is low-discrepancy allocation, not φ.

## 1. Design (to be locked)

- **Arms (allocation constants):** golden, silver, bronze, exp-2, greedy-rank, uniform, plus two tripwire controls: φ-shuffled and silver-shuffled (same numbers, wrong places).
- **Sweep:** code sizes {250, 1000, 4000} shards; damage fractions {0.25, 0.50, 0.75}; **four damage geometries** — uniform-random erasure, contiguous burst, importance-targeted adversarial tear (the GH-RECOV stressor), periodic stride.
- **Metric:** recovery fidelity exactly as in K-RECOV-001 (Zipf-skewed importance, fixed redundancy budget scaled to size); 20 seeds per cell (seeds 2000–2019), identical across cells.
- **Statistic:** per-cell median across seeds; signed contrast Δ_sg = median silver − median golden and Δ_sn = median silver − best non-silver noble arm, each with 95% bootstrap CI (10,000 resamples).

## 2. The three hypotheses, each with its kill (signed before data)

| Branch | Pre-registered criterion | Reading |
|---|---|---|
| **H1 — silver-optimal (genuine)** | Δ_sn > +0.02 with CI excluding 0 in **at least three of four** damage geometries at the two larger code sizes | A genuinely new, GHP-independent result about low-discrepancy allocation codes. Publishable as applied mathematics; makes no φ or GHP claim. |
| **H0 — noble-plateau** | all noble arms within ±0.02 of each other everywhere | The 5σ line was regime-specific; the anomaly dissolves; ledger row closes honest-null. |
| **H2 — damage-geometry artifact** | silver's advantage exceeds +0.02 in **at most one** geometry (the adversarial tear) and nowhere else | The dramatic number is demoted before a referee does it for us; ledger row closes artifact. |

Ambiguous outcomes (matching none of the three) are reported as UNRESOLVED with no upgrade and no re-cutting of criteria after data.

## 3. What may not be claimed under any branch

Not GHP evidence; not φ physics; not a fusion-category statement (M-006 forbids the reading); not a universal coding-theory law from one family of synthetic codes. H1, if it lands, is an anomaly *characterized*, not an anomaly *explained* — explanation gets its own preregistration.

## 4. Finalization record (2026-08-01)

Design drafted by the symbiote lane under owner direction; builder: same. Margins inherit the K-RECOV-001 bar (±0.02), recorded as not power-derived.

**Signed:** Peter Viviani (owner) — signature given by chat directive to the symbiote lane. **Date (UTC):** 2026-08-01

*The lock is engaged: this file's SHA-256 at signing is recorded in the ledger; any post-signing edit to this document voids the run.*
