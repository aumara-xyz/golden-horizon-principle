# Boundary Access Oracle-Gap Probe

Status: targeted hard-lane toy telemetry only.

- question: can legal local context learn when capacity should override order?
- mode: `scout`
- settings: scout grid, two train seeds, one held-out test seed, one trial per scenario, 64 time steps
- best policy: `oracle_order_or_capacity`
- overall held-out accuracy: `0.882`

Ranking:
- oracle_order_or_capacity: `0.882`
- capacity_context_calibrated_gate: `0.849`
- order_capacity_context_gate: `0.849`
- order_capacity_context_calibrated_gate: `0.847`
- full_local_context_gate: `0.847`
- full_local_context_calibrated_gate: `0.847`
- coherence_margin_gate: `0.844`
- score_only_calibrated_gate: `0.844`
- capacity_context_gate: `0.838`
- threshold_gate: `0.836`
- score_only_gate: `0.836`
- capacity_only: `0.824`
- order_plus_flow: `0.803`

Gate thresholds:
- score_only (6D): threshold `0.618`, train accuracy `0.834`, train open rate `0.060`
- capacity_context (24D): threshold `0.613`, train accuracy `0.838`, train open rate `0.060`
- order_capacity_context (49D): threshold `0.581`, train accuracy `0.848`, train open rate `0.070`
- full_local_context (55D): threshold `0.586`, train accuracy `0.850`, train open rate `0.070`

Order-vs-capacity buckets:
- both_correct: `0.745` (487)
- order_only: `0.058` (38)
- capacity_only: `0.080` (52)
- both_wrong: `0.118` (77)

Best-policy scenario map:
- cross_family_0.45: `1.000`
- cross_family_0.60: `1.000`
- current: `0.769`
- gaussian_mix_0.60: `0.802`
- permute_mix_0.60: `0.870`
- uniform_mix_0.60: `0.873`

Gate capture on the real oracle gap:
- coherence_margin_open / capacity_only: `0.615`
- coherence_margin_open / order_only: `0.132`
- threshold_open / capacity_only: `0.923`
- threshold_open / order_only: `0.684`
- score_only_gate_open / capacity_only: `0.712`
- score_only_gate_open / order_only: `0.395`
- score_only_calibrated_open / capacity_only: `0.577`
- score_only_calibrated_open / order_only: `0.079`
- capacity_context_gate_open / capacity_only: `0.673`
- capacity_context_gate_open / order_only: `0.316`
- capacity_context_calibrated_open / capacity_only: `0.615`
- capacity_context_calibrated_open / order_only: `0.053`
- order_capacity_context_gate_open / capacity_only: `0.788`
- order_capacity_context_gate_open / order_only: `0.289`
- order_capacity_context_calibrated_open / capacity_only: `0.654`
- order_capacity_context_calibrated_open / order_only: `0.132`
- full_local_context_gate_open / capacity_only: `0.788`
- full_local_context_gate_open / order_only: `0.316`
- full_local_context_calibrated_open / capacity_only: `0.635`
- full_local_context_calibrated_open / order_only: `0.105`
