# SILVER-OPT-GEO v1 — sweep summary

Contract: `experiments/SILVER_OPT_GEO_PREREG_v1.md` (signed 2026-08-01). Pipeline: `experiments/silver_opt_geo_pipeline.py`. Substrate reused verbatim from `experiments/ghp_golden_heal_v2_probe.py` (GH-RECOV family) and `experiments/silver_opt_pipeline.py`. Deterministic; seeds 4000-4099.

## Per-cell medians (CB) and the silver-vs-golden contrast

| size | geometry | golden | silver | bronze | unif-rand | gold-shuf | silv-shuf | D_sg (med) | 95% CI | G1? | G2? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 256 | contiguous_burst | 0.6337 | 0.6358 | 0.6311 | 0.1423 | 0.2849 | 0.2915 | +0.0021 | [-0.0138, +0.0163] | no | no |
| 256 | adversarial_tear | 0.2141 | 0.4923 | 0.3826 | 0.0000 | 0.0572 | 0.0616 | +0.2782 | [+0.2695, +0.2881] | YES | no |
| 256 | uniform_random | 0.2841 | 0.2818 | 0.2839 | 0.2862 | 0.2782 | 0.2998 | -0.0023 | [-0.0273, +0.0117] | no | no |
| 256 | periodic_stride | 0.6114 | 0.6382 | 0.6322 | 0.2883 | 0.2723 | 0.2673 | +0.0268 | [+0.0164, +0.0423] | YES | no |
| 512 | contiguous_burst | 0.6355 | 0.6321 | 0.6343 | 0.1189 | 0.2014 | 0.1778 | -0.0034 | [-0.0129, +0.0041] | no | no |
| 512 | adversarial_tear | 0.2374 | 0.2300 | 0.2940 | 0.0000 | 0.0000 | 0.0000 | -0.0074 | [-0.0118, -0.0014] | no | no |
| 512 | uniform_random | 0.2291 | 0.2329 | 0.2445 | 0.1506 | 0.2603 | 0.1881 | +0.0038 | [-0.0805, +0.0880] | no | no |
| 512 | periodic_stride | 0.6212 | 0.6161 | 0.6192 | 0.1718 | 0.2544 | 0.1937 | -0.0052 | [-0.0176, +0.0051] | no | no |

## Branch evaluation (mechanical)

```json
{
  "verdict": "UNRESOLVED",
  "g1_silver_geometry_real": false,
  "g1_classes_qualifying": [],
  "g0_dissolved_noble_plateau": false,
  "g2_reversed_artifact": false,
  "g2_classes_qualifying": [],
  "class_rule": "class qualifies iff its cell criterion holds at BOTH sizes; G1 needs >=3/4 classes, G2 >=2/4; precedence G1 -> G0 -> G2 -> UNRESOLVED (declared pre-run in this pipeline)"
}
```

## No-claims (verbatim)

Constant/placement axis only (M-006 forbids any structural reading: no silver fusion category exists). Not GHP evidence under any branch. The four-instrument line's other three instruments (T-111, T-112, KAM) are separately governed and untouched by this result.
