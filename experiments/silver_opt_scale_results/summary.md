# SILVER-OPT-SCALE v1 — sweep summary

Contract: `experiments/SILVER_OPT_SCALE_PREREG_v1.md` (signed 2026-08-01). Runner: `experiments/silver_opt_scale_results/run_scale.py` wrapping `experiments/silver_opt_geo_pipeline.py` UNMODIFIED. Deterministic; seeds 5000-5099; N/2K = 4 at every size.

## The deliverable — Delta_sg(tear) die-off curve

| n | golden med CB | silver med CB | D_sg (med) | 95% CI | CI excl 0 (+)? |
|---|---|---|---|---|---|
| 256 | 0.2070 | 0.4936 | +0.2866 | [+0.2778, +0.2952] | YES |
| 320 | 0.2139 | 0.2978 | +0.0839 | [+0.0489, +0.1236] | YES |
| 384 | 0.3601 | 0.4425 | +0.0824 | [+0.0419, +0.1162] | YES |
| 448 | 0.2620 | 0.2294 | -0.0326 | [-0.1004, -0.0119] | no |
| 512 | 0.2363 | 0.2340 | -0.0023 | [-0.0092, +0.0057] | no |
| 640 | 0.2388 | 0.2393 | +0.0005 | [-0.0040, +0.0076] | no |
| 768 | 0.2436 | 0.2423 | -0.0013 | [-0.0054, +0.0038] | no |
| 1024 | 0.2509 | 0.2598 | +0.0088 | [+0.0033, +0.0140] | YES |

## All cells (both geometries)

| size | geometry | golden | silver | bronze | gold-shuf | silv-shuf | D_sg (med) | 95% CI |
|---|---|---|---|---|---|---|---|---|
| 256 | adversarial_tear | 0.2070 | 0.4936 | 0.3788 | 0.0522 | 0.0537 | +0.2866 | [+0.2778, +0.2952] |
| 320 | adversarial_tear | 0.2139 | 0.2978 | 0.2140 | 0.0000 | 0.0000 | +0.0839 | [+0.0489, +0.1236] |
| 384 | adversarial_tear | 0.3601 | 0.4425 | 0.5063 | 0.0000 | 0.0000 | +0.0824 | [+0.0419, +0.1162] |
| 448 | adversarial_tear | 0.2620 | 0.2294 | 0.2298 | 0.0000 | 0.0000 | -0.0326 | [-0.1004, -0.0119] |
| 512 | adversarial_tear | 0.2363 | 0.2340 | 0.3182 | 0.0000 | 0.0000 | -0.0023 | [-0.0092, +0.0057] |
| 640 | adversarial_tear | 0.2388 | 0.2393 | 0.4198 | 0.0000 | 0.0000 | +0.0005 | [-0.0040, +0.0076] |
| 768 | adversarial_tear | 0.2436 | 0.2423 | 0.2439 | 0.0000 | 0.0000 | -0.0013 | [-0.0054, +0.0038] |
| 1024 | adversarial_tear | 0.2509 | 0.2598 | 0.2509 | 0.0000 | 0.0000 | +0.0088 | [+0.0033, +0.0140] |
| 256 | periodic_stride | 0.6063 | 0.6354 | 0.6242 | 0.2845 | 0.2907 | +0.0291 | [+0.0160, +0.0396] |
| 320 | periodic_stride | 0.6104 | 0.5218 | 0.6371 | 0.2799 | 0.2771 | -0.0887 | [-0.1212, -0.0741] |
| 384 | periodic_stride | 0.4252 | 0.4618 | 0.5177 | 0.2648 | 0.2704 | +0.0366 | [-0.0207, +0.1195] |
| 448 | periodic_stride | 0.4402 | 0.4240 | 0.6349 | 0.2308 | 0.2368 | -0.0162 | [-0.0247, -0.0087] |
| 512 | periodic_stride | 0.6249 | 0.6212 | 0.6132 | 0.1689 | 0.2139 | -0.0038 | [-0.0134, +0.0029] |
| 640 | periodic_stride | 0.6005 | 0.5042 | 0.6226 | 0.1974 | 0.2267 | -0.0963 | [-0.1446, -0.0750] |
| 768 | periodic_stride | 0.3297 | 0.2648 | 0.6343 | 0.1342 | 0.1302 | -0.0650 | [-0.1189, -0.0060] |
| 1024 | periodic_stride | 0.5592 | 0.3115 | 0.6215 | 0.1300 | 0.1282 | -0.2478 | [-0.2668, -0.2248] |

## Branch evaluation (mechanical)

```json
{
  "verdict": "S2_NON_MONOTONE",
  "n_star": null,
  "flags": {
    "s0_no_reproduction": false,
    "s1_crossover_located": false,
    "s2_non_monotone": true,
    "base_qual_256": true,
    "prefix_pattern": false,
    "monotone_within_cis": false,
    "n_leading_excl_pos": 3
  },
  "tear_curve": [
    {
      "n": 256,
      "delta_sg_median": 0.28660686156041676,
      "ci95": [
        0.2777564446411151,
        0.29520831517247176
      ],
      "ci_excludes_0_pos": true,
      "ci_includes_0": false
    },
    {
      "n": 320,
      "delta_sg_median": 0.08387897514060705,
      "ci95": [
        0.04892117589818348,
        0.12355337627781168
      ],
      "ci_excludes_0_pos": true,
      "ci_includes_0": false
    },
    {
      "n": 384,
      "delta_sg_median": 0.08237610878835327,
      "ci95": [
        0.04193514196349378,
        0.11624919693489379
      ],
      "ci_excludes_0_pos": true,
      "ci_includes_0": false
    },
    {
      "n": 448,
      "delta_sg_median": -0.03258011413559253,
      "ci95": [
        -0.10044588453366081,
        -0.011854857754829723
      ],
      "ci_excludes_0_pos": false,
      "ci_includes_0": false
    },
    {
      "n": 512,
      "delta_sg_median": -0.00227716493144281,
      "ci95": [
        -0.009234666367059568,
        0.005712736097722382
      ],
      "ci_excludes_0_pos": false,
      "ci_includes_0": true
    },
    {
      "n": 640,
      "delta_sg_median": 0.0004954728368374572,
      "ci95": [
        -0.00400091511901745,
        0.00757222462601412
      ],
      "ci_excludes_0_pos": false,
      "ci_includes_0": true
    },
    {
      "n": 768,
      "delta_sg_median": -0.0012929743533763305,
      "ci95": [
        -0.00535157357507535,
        0.0037713966063645152
      ],
      "ci_excludes_0_pos": false,
      "ci_includes_0": true
    },
    {
      "n": 1024,
      "delta_sg_median": 0.008835846240352663,
      "ci95": [
        0.00332922954120083,
        0.014022781540503333
      ],
      "ci_excludes_0_pos": true,
      "ci_includes_0": false
    }
  ],
  "rule": "S0 iff CI(256) includes 0 (evaluated first). S1 iff Delta_sg(256)>MARGIN with CI(256) excluding 0 positively, the positive-exclusion pattern is a strict prefix of the size list (dies off within range, never returns), and Delta_sg decreases monotonically within CIs (consecutive decrease OR CI overlap); n* = last size whose CI excludes 0. S2 iff the advantage re-emerges (CI excluding 0 positively at a size strictly above one whose CI includes 0). Precedence S0 -> S1 -> S2 -> UNRESOLVED; declared and committed before the sweep ran."
}
```

## No-claims (verbatim)

Constant/placement axis; not GHP physics under any branch; no phi literal in code (derived only).
