# Preregistration — SILVER-OPT-GEO v1 (hunting the anomaly where it actually lived)

- test_id: SILVER-OPT-GEO-v1
- date_locked: **PENDING OWNER SIGNATURE** (standard lock protocol).
- anchor: SILVER-OPT v1 verdict **UNRESOLVED — anomaly anti-replicated** in the allocation-count family (2026-08-01); its recorded descriptive lead: if the four-instrument silver line is real, it lives in low-discrepancy **placement geometry** of the GH-RECOV type, not allocation counts. This test goes to that address.
- runtime: Python 3 + numpy, laptop, deterministic. Substrate: the archived GH-RECOV probe's placement mechanism (`ghp_golden_heal_probe.py` family, commit 8a3c6ead) reused **verbatim** as the code substrate — the original home of the ~5σ silver line — wrapped, not rewritten.

## 1. Design

- Arms: golden, silver, bronze placement rotations + uniform-random placement + two shuffled tripwires (golden-shuffled, silver-shuffled: same offsets, permuted positions).
- Sweep: the original GH-RECOV damage set INCLUDING its critical band and adversarial tear, plus the two geometries where v1 found golden-favored reversals (periodic stride, contiguous burst). Code sizes as in the original probe plus one size up.
- Seeds: 4000–4099 (100). Metric: the original probe's recovery score, unmodified.

## 2. Branches (each with its kill, signed before data)

| Branch | Criterion | Reading |
|---|---|---|
| **G1 — silver-geometry-real** | silver > golden by > 0.02 with 95% CI excluding 0 in ≥ 3 of 4 geometry classes, reproducing the original band/tear result at 100 seeds | The anomaly is real and placement-geometric. GHP-independent applied-math finding; publishable; still not φ physics. |
| **G0 — dissolved** | all noble placement arms within ±0.02 everywhere | The original ~5σ line does not survive more seeds; propose a dated errata note on GH-RECOV's silver remark (body untouched, errata idiom). |
| **G2 — reversed/artifact** | golden ≥ silver beyond +0.02 with CI excluding 0 in ≥ 2 geometry classes | Consistent with 2026-08-01: the silver line was an artifact of the original configuration; errata proposal as G0, plus the reversal recorded. |

Ambiguous → UNRESOLVED, no re-cutting, follow-ups need new contracts.

## 3. No-claims

Constant/placement axis only (M-006 forbids any structural reading: no silver fusion category exists). Not GHP evidence under any branch. The four-instrument line's other three instruments (T-111, T-112, KAM) are separately governed and untouched by this result.

**Signed:** ______________________ (owner) **Date (UTC):** ____________
