# MEB-003 — D4 Chirality Obstruction Probe

## Status

This is a mathematical hardening probe, not physics evidence.

It asks whether the bare 24-cell / D4 root scaffold can produce intrinsic chirality without an extra orientation-breaking rule.

It does **not** derive weak interactions, Standard Model chirality, fermions, matter, or anomaly cancellation.

## Results

| Probe | Metric | Value | Control | Verdict |
|---|---:|---:|---:|---|
| MEB-003A | central_symmetry_score | 1.000000 | 0.000000 | PASS |
| MEB-003B | reflection_closure_score | 1.000000 | 0.000000 | PASS |
| MEB-003C | chirality_imbalance_lower_is_nonchiral | 0.002454 | 0.025000 | PASS |
| MEB-003D | orientation_breaking_needed | 1.000000 | 0.000000 | PASS |
| MEB-003E | symmetry_cancellation_score | 1.000000 | 0.000000 | PASS |

Pass count: **5/5**.

## Interpretation

- The bare D4 / 24-cell scaffold is highly symmetric and non-chiral.
- That is useful as a guardrail: it blocks premature claims that D4 alone gives chiral matter.
- Any future matter-embedding bridge needs an additional orientation-breaking mechanism, projection, or dynamical sector.
- The symmetry-cancellation result is only a toy cancellation scaffold, not Standard Model anomaly cancellation.

## Next Test

MEB-004 should test candidate orientation-breaking mechanisms:

```text
Can a non-arbitrary projection, boundary condition, or triality choice
break D4 symmetry while preserving enough cancellation structure
to remain mathematically disciplined?
```

## Do Not Claim

- Do not claim D4 derives chiral fermions.
- Do not claim D4 derives the weak interaction.
- Do not claim the symmetry-cancellation score is anomaly cancellation.
- Do not claim this closes the Matter Embedding Gap.
