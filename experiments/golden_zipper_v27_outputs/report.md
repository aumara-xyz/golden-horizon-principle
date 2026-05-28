# Golden Zipper v27 - Branch Shootout

Toy telemetry only. Not physics evidence. Not proof of GHP.

Shared anchors:
bounded_cf_2, fib_13_21, golden, pi_mod1, random_cf_1, silver

Winner by mean generic score: `model_revision_witness` with `0.456`

Runner-up:
- `boundary_pocket` with `0.363`

Winner details:
- best anchor: `pi_mod1`
- mean witness conversion: `0.002`
- mean write persistence: `0.058`
- density gap: `-0.106`
- block gap: `-0.121`
- markov gap: `-0.077`

Interpretation:
- This shootout removes family-specific scoring and asks which branch gives cleaner witness-to-write behavior under the same downstream score.
- A durable winner should keep positive null gaps while also preserving witness conversion and write persistence.
