# Boundary Access Gate Hardening

Status: scout telemetry only; shortened run for directional testing.

- question: can the capacity alarm become less blunt by separating coherent outside flow from other hard motion?
- scout settings: 64 time steps, one trial per scenario, two train seeds, one held-out test seed
- best policy: `oracle_order_or_capacity`
- overall held-out accuracy: `0.882`

Ranking:
- oracle_order_or_capacity: `0.882`
- coherence_margin_gate: `0.844`
- coherence_linear_gate: `0.843`
- coherence_disagreement_gate: `0.843`
- opportunity_linear_gate: `0.838`
- threshold_gate: `0.836`
- capacity_only: `0.824`
- order_plus_flow: `0.803`

Selected threshold gate:
- require_disagreement: `True`
- min_capacity_margin: `0.05`
- max_order_margin: `0.5499999999999999`
- train_accuracy: `0.823170731707317`
- train_open_rate: `0.12728658536585366`

Best-policy scenario map:
- cross_family_0.45: `1.000`
- cross_family_0.60: `1.000`
- current: `0.769`
- gaussian_mix_0.60: `0.802`
- permute_mix_0.60: `0.870`
- uniform_mix_0.60: `0.873`

Gate open rates:
- opportunity_linear_gate / cross_family_0.45: `0.182`
- opportunity_linear_gate / cross_family_0.60: `0.128`
- opportunity_linear_gate / current: `0.017`
- opportunity_linear_gate / gaussian_mix_0.60: `0.027`
- opportunity_linear_gate / permute_mix_0.60: `0.037`
- opportunity_linear_gate / uniform_mix_0.60: `0.055`
- coherence_linear_gate / cross_family_0.45: `0.929`
- coherence_linear_gate / cross_family_0.60: `0.954`
- coherence_linear_gate / current: `0.239`
- coherence_linear_gate / gaussian_mix_0.60: `0.000`
- coherence_linear_gate / permute_mix_0.60: `0.000`
- coherence_linear_gate / uniform_mix_0.60: `0.073`
- coherence_disagreement_gate / cross_family_0.45: `0.162`
- coherence_disagreement_gate / cross_family_0.60: `0.156`
- coherence_disagreement_gate / current: `0.026`
- coherence_disagreement_gate / gaussian_mix_0.60: `0.000`
- coherence_disagreement_gate / permute_mix_0.60: `0.000`
- coherence_disagreement_gate / uniform_mix_0.60: `0.018`
- coherence_margin_gate / cross_family_0.45: `0.152`
- coherence_margin_gate / cross_family_0.60: `0.156`
- coherence_margin_gate / current: `0.026`
- coherence_margin_gate / gaussian_mix_0.60: `0.000`
- coherence_margin_gate / permute_mix_0.60: `0.000`
- coherence_margin_gate / uniform_mix_0.60: `0.018`
- threshold_gate / cross_family_0.45: `0.162`
- threshold_gate / cross_family_0.60: `0.156`
- threshold_gate / current: `0.077`
- threshold_gate / gaussian_mix_0.60: `0.081`
- threshold_gate / permute_mix_0.60: `0.111`
- threshold_gate / uniform_mix_0.60: `0.100`
