# Preregistration — SILVER-OPT-SCALE v1 (mapping the die-off curve of the tear line)

- test_id: SILVER-OPT-SCALE-v1
- date_locked: **2026-08-01 (SIGNED)** — owner chat directive ("i approve everything that is waiting"), the follow-up SILVER-OPT-GEO's own verdict called for. Lane: constant/placement axis, GHP-independent (M-006).
- substrate law: identical to SILVER-OPT-GEO v1 — the archived GH-RECOV placement mechanism verbatim; the verified `silver_opt_geo_pipeline.py` is reused unmodified except for the size list.

## 1. The declared question

GEO found the silver tear advantage CI-solid at n=256 (Δ_sg = +0.278) and absent at n=512.
This contract maps the transition: sizes **{256, 320, 384, 448, 512, 640, 768, 1024}**,
geometries {adversarial_tear, periodic_stride} (where the effect lived), arms {golden, silver,
bronze, golden-shuffled, silver-shuffled}, seeds **5000–5099** (100, fresh), N/2K held at 4 as
in GEO, same metric, same CI machinery.

## 2. Branches (signed before data)

- **S1 — crossover located:** Δ_sg(tear) decreases monotonically (within CIs) from +0.02-exceeding at 256 to CI-including-0, with a declared crossover scale n* (last size whose CI excludes 0). The anomaly is characterized as finite-size with a measured die-off.
- **S0 — no reproduction:** the n=256 tear advantage fails to reproduce (CI includes 0) — inconsistent with GEO; both runs stand on the ledger and the discrepancy becomes its own question.
- **S2 — non-monotone:** the advantage re-emerges at any larger size with CI excluding 0 — the effect is not a simple finite-size die-off; report shape, no story.
- Anything else: UNRESOLVED, no re-cutting.

## 3. No-claims

Constant/placement axis; not GHP physics under any branch; no φ literal in code (derived only).

**Signed:** Peter Viviani (owner), by chat directive 2026-08-01.
