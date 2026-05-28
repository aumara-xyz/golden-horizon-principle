# Golden Zipper Bundle

This folder is a Browser-GPT upload bundle for the Golden Zipper toy line.

It contains:

- `golden_zipper_sturmian_memory_toy.py`
  - v1 blended baseline
- `golden_zipper_v2_lib.py`
  - shared helper module for v2
- `golden_zipper_sturmian_pure_mode.py`
  - v2A: pure Sturmian / irrational rotation only
- `golden_zipper_spiral_window_mode.py`
  - v2B: observer-window / moving-window / bidirectional window split
- `golden_zipper_memory_policy_mode.py`
  - v2C: write / witness / release only after sequence generation
- `golden_zipper_robustness_sweep.py`
  - v3: threshold robustness sweep for anti-locking / delayed-retention tradeoff
- `golden_zipper_v4_null_test.py`
  - v4: adversarial null-test against noble/generic-irrational/artifact alternatives

Included output folders:

- `golden_zipper_outputs/`
- `golden_zipper_v2_sturmian_pure_outputs/`
- `golden_zipper_v2_spiral_window_outputs/`
- `golden_zipper_v2_memory_policy_outputs/`
- `golden_zipper_v3_robustness_outputs/`
- `golden_zipper_v4_outputs/`

Current high-level result:

- v1 was mixed and did **not** justify hardening the master as "Golden Zipper works"
- v2A pure mode: golden was anti-locking-strong but did not beat rationals on balance
- v2B spiral window mode: golden sat in a stronger anti-locking region under observer-window variation
- v2C memory mode: golden did not win every metric, but looked strongest on the anti-locking / delayed-retention tradeoff
- v3 robustness sweep: golden stayed top-tier across the threshold grid and won the most `#1` placements across policy settings
- v4 null test: the broader adversarial sweep supported **H3**, meaning the prior golden-looking edge did not survive the null suite cleanly enough for hardening

Correct success language:

> Golden slope did not win every metric, but may occupy the best anti-locking / delayed-retention tradeoff region.

For v3 specifically:

> Golden remains robustly top-tier in anti-locking / delayed-retention tradeoff across threshold sweeps.

For v4 specifically:

> The broader null suite supported H3: prior golden-looking advantage was still too sensitive to surrogate and policy artifacts for hardening.

Do not claim:

- confirmation
- proof of GHP
- proof that phi is the code of reality
- proof of VPH
- proof of consciousness
- write-law closure
- physics evidence
