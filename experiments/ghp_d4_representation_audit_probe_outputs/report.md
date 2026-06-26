# MEB-002 — D4 Representation Audit Probe

## Status

This is a mathematical scaffold probe, not physics evidence.

It asks whether the 24-cell / D4 root system contains algorithmically discoverable A2 + A1 + rank-1-residual structure more cleanly than random 24-point controls.

It does **not** derive SU(3) x SU(2) x U(1), Standard Model charges, chirality, hypercharge, generations, masses, particles, or matter.

## Results

| Probe | Metric | Value | Control | Verdict |
|---|---:|---:|---:|---|
| MEB-002A | algorithmic_A2_subsystem_count | 16.000000 | 0.000000 | PASS |
| MEB-002B | algorithmic_A2_plus_A1_extension_count | 0.000000 | 0.000000 | MIXED |
| MEB-002C | residual_U1_like_charge_bins_lower_than_24 | 999.000000 | 24.000000 | MIXED |
| MEB-002D | rank_coverage_score | 0.000000 | 0.000000 | FAIL |
| MEB-002E | support_variety | 4.000000 | 0.000000 | PASS |

Pass count: **2/5**.

## Interpretation

- D4 contains algorithmically discoverable A2-like hexagonal sub-root scaffolds.
- The stricter A2 + A1 + rank-1-residual decomposition did **not** pass in this exact root-subsystem test.
- This blocks the premature claim that D4 directly gives SU(3) x SU(2) x U(1)-like bookkeeping.
- The result is still useful because it upgrades the A2/color-like scaffold while demoting the full Standard-Model-like mapping.

## Next Test

MEB-003 should test chirality and anomaly-like constraints:

```text
Can a D4-derived scaffold produce asymmetric left/right representation
bookkeeping without manual sign choices, and does it obey any
nontrivial cancellation law under controls?
```

## Do Not Claim

- Do not claim this derives the Standard Model.
- Do not claim A2 is literally SU(3) color here.
- Do not claim A1 is literally weak isospin here.
- Do not claim the residual axis is hypercharge.
- Do not claim this closes the Matter Embedding Gap.
