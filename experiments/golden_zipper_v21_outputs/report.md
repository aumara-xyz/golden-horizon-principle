# Golden Zipper v21 - Revision Ablation Panel

Toy telemetry only. Not physics evidence. Not proof of GHP.

This panel removes direct reward for revision rate and revision size.

Key comparisons:
- real `surprise_only` downstream score: `0.683`
- real `model_revision_witness` downstream score: `0.663`
- best null `model_revision_witness`: `random_projection` at `0.708`

Interpretation:
- If model revision still wins without direct revision reward, the v19 signal is less likely to be score-selected.
- If null projection still wins, the toy is not geometry-specific.
- This remains experiment-only telemetry.
