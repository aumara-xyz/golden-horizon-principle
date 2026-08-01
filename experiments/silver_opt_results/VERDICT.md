# SILVER-OPT v1 — VERDICT

- test_id: SILVER-OPT-v1
- contract: `experiments/SILVER_OPT_PREREG_v1.md` (SIGNED 2026-08-01; SHA-256
  `034dbb47b56dcd956732d2873afac11e4748e8f093b46d82c6b07552a3f139d2`; untouched by this run)
- pipeline: `experiments/silver_opt_pipeline.py` (additive file; run once against the contract)
- data: `experiments/silver_opt_results/results.json`, `experiments/silver_opt_results/summary.md`
- runtime: python3 + numpy, deterministic, offline, single-core, ~0.5 s wall
- seeds: 2000–2019 (20, identical across cells); self-tests PASS at every size
  (budget conservation, layout size, zero-damage fidelity exactly 1, shuffled-control
  multiset equality, exact erased counts)

## Branch that fired: **UNRESOLVED**

Applied mechanically per prereg section 2, precedence H1 → H0 → H2:

| Branch | Criterion (locked) | Result |
|---|---|---|
| H1 silver-optimal | Δ_sn > +0.02 with 95% CI excluding 0 in ≥3 of 4 geometries at both larger sizes | **FAILS — 0 of 4 geometries.** Silver's advantage clears the margin with CI excluding 0 in **zero of the 36 cells** (majority-of-fractions rule and strict all-fractions rule agree). |
| H0 noble-plateau | all noble arms within ±0.02 of each other everywhere | **FAILS.** The noble arms separate by far more than ±0.02 in several cells; maximum noble pairwise gap 0.1608 (n=4000, f=0.75, periodic stride: golden 0.5325 vs bronze 0.3717). |
| H2 geometry artifact | silver's advantage exceeds +0.02 in at most one geometry (the adversarial tear) and nowhere else | **FAILS as operationalized.** The set of geometries with a qualifying silver advantage is **empty** — in particular silver has *no* advantage in the adversarial tear; golden leads there. The pipeline (committed before the run) required the advantage to exist in the tear for H2 to fire; a purely literal "at most one" reading would be satisfied vacuously by zero, but that reading contradicts H2's stated interpretation (demoting an advantage that exists). Both readings are disclosed here; the verdict stays UNRESOLVED rather than re-cutting criteria after data. |

Per the prereg: "Ambiguous outcomes (matching none of the three) are reported as
UNRESOLVED with no upgrade and no re-cutting of criteria after data."

## Key Δ values (median fidelity contrasts; full table in summary.md)

- **Δ_sn (silver − best non-silver noble), maximum anywhere:** +0.0192
  (n=1000, f=0.50, contiguous burst; 95% CI [+0.0000, +0.0283]) — below the
  +0.02 margin and the CI touches 0.
- **Adversarial tear (the GH-RECOV stressor), f=0.25:** Δ_sg (silver − golden) =
  **−0.0365** (n=250), **−0.0735** (n=1000), **−0.0492** (n=4000) — the sign is
  *golden-favored*, opposite to GH-RECOV's ~5σ silver line. At f ≥ 0.50 the tear
  ties all tier arms exactly (all extras sit inside the wiped prefix; Δ = 0).
- **Periodic stride, f=0.75:** Δ_sg = −0.0443 / −0.0482 / −0.1379 at
  n=250 / 1000 / 4000 — golden-favored, growing with size.
- **Largest silver-over-golden cell:** Δ_sg = +0.0991 (n=1000, f=0.50, burst),
  but bronze and greedy-rank sit above silver there, so Δ_sn = +0.0192 only.
- **Sanity anchors:** heavy-tailed arms beat uniform by ~+0.22 at f=0.75 under
  uniform-random erasure (K-RECOV-001 reported +15 pts — same shape); both
  shuffled tripwire controls (same numbers, permuted positions) degrade sharply
  wherever importance alignment matters (e.g., tear n=250 f=0.25: parents ~0.54–0.59,
  shuffled ~0.34), confirming the alignment, not the number multiset, carries the effect.

## What this run says about the anomaly (descriptive, no upgrade)

In this allocation-code family (integer-recurrence tier allocation over
Zipf-0.8 importance, budget 0.3n), the silver ≥ golden anomaly **did not
replicate**: silver never cleared the preregistered margin anywhere, and in the
two geometries where the noble arms separate cleanly (importance-targeted tear
at low damage, periodic stride at high damage) **golden** led. The four prior
instruments' silver line is therefore not a property of heavy-tailed
importance-aligned allocation as such; whatever produced it lives elsewhere
(e.g., in low-discrepancy *placement* geometry of the GH-RECOV type, not in
allocation *counts*). That observation is a lead for a future preregistration,
not a claim of this one. The ledger row outcome under the signed contract is
UNRESOLVED — no branch fired, no criteria are re-cut.

## No-claim sentences (prereg section 3, verbatim)

> Not GHP evidence; not φ physics; not a fusion-category statement (M-006 forbids the reading); not a universal coding-theory law from one family of synthetic codes. H1, if it lands, is an anomaly *characterized*, not an anomaly *explained* — explanation gets its own preregistration.

## Hard-law compliance

1. No existing file modified; all artifacts are new files (pipeline, results, this verdict).
2. φ appears nowhere in the erasure channel, damage geometries, layout, recovery
   rule, or scorer, and nowhere as a numeric literal in the pipeline: the golden
   arm is defined purely by the Fibonacci recurrence u₁=1, u₂=1, u_{k+1}=u_k+u_{k−1}
   (the fusion-path counting of τ⊗τ = 1⊕τ); its limiting ratio is reported only as
   a derived diagnostic (1.6180339887…, computed by iterating the recursion).
3. The refused shortcut does not arise: SILVER-OPT is *declared* constant-axis
   allocation characterization (prereg section 1) — no fusion tree is being
   approximated, and nothing here substitutes for AH.4-P1.
4. Built and run on branch `build/signed-runs-2026-08-01`; committed, not pushed.
5. All arms were computationally trivial at the locked parameters (full sweep
   ~0.5 s); no infeasibility clause invoked.
