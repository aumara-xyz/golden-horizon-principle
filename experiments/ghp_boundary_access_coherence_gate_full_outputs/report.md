# Boundary Access Coherence Gate Full Rerun

Status: full-size targeted hard-lane toy telemetry only.

- question: does the coherent-foreign gate survive the full target scenario grid?
- settings: target hard-lane scenarios, all train seeds, all held-out test seeds, three trials per scenario, full time horizon
- best policy: `oracle_order_or_capacity`
- overall held-out accuracy: `0.868`

Ranking:
- oracle_order_or_capacity: `0.868`
- coherence_linear_gate: `0.840`
- coherence_disagreement_gate: `0.840`
- coherence_margin_gate: `0.840`
- opportunity_linear_gate: `0.838`
- threshold_gate: `0.833`
- capacity_only: `0.824`
- order_plus_flow: `0.809`

Selected threshold gate:
- require_disagreement: `True`
- min_capacity_margin: `0.1`
- max_order_margin: `0.5499999999999999`
- train_accuracy: `0.8244550874792298`
- train_open_rate: `0.0730133906753983`

Best-policy scenario map:
- cross_family_0.30: `0.879`
- cross_family_0.45: `1.000`
- cross_family_0.60: `0.999`
- current: `0.805`
- delayed_uniform_0.60: `0.790`
- gaussian_mix_0.60: `0.799`
- permute_mix_0.60: `0.817`
- uniform_mix_0.60: `0.854`

Gate open rates:
- opportunity_linear_gate / cross_family_0.30: `0.017`
- opportunity_linear_gate / cross_family_0.45: `0.120`
- opportunity_linear_gate / cross_family_0.60: `0.153`
- opportunity_linear_gate / current: `0.009`
- opportunity_linear_gate / delayed_uniform_0.60: `0.012`
- opportunity_linear_gate / gaussian_mix_0.60: `0.053`
- opportunity_linear_gate / permute_mix_0.60: `0.057`
- opportunity_linear_gate / uniform_mix_0.60: `0.090`
- coherence_linear_gate / cross_family_0.30: `0.884`
- coherence_linear_gate / cross_family_0.45: `0.961`
- coherence_linear_gate / cross_family_0.60: `0.974`
- coherence_linear_gate / current: `0.380`
- coherence_linear_gate / delayed_uniform_0.60: `0.004`
- coherence_linear_gate / gaussian_mix_0.60: `0.001`
- coherence_linear_gate / permute_mix_0.60: `0.001`
- coherence_linear_gate / uniform_mix_0.60: `0.024`
- coherence_disagreement_gate / cross_family_0.30: `0.031`
- coherence_disagreement_gate / cross_family_0.45: `0.119`
- coherence_disagreement_gate / cross_family_0.60: `0.157`
- coherence_disagreement_gate / current: `0.022`
- coherence_disagreement_gate / delayed_uniform_0.60: `0.001`
- coherence_disagreement_gate / gaussian_mix_0.60: `0.001`
- coherence_disagreement_gate / permute_mix_0.60: `0.000`
- coherence_disagreement_gate / uniform_mix_0.60: `0.002`
- coherence_margin_gate / cross_family_0.30: `0.027`
- coherence_margin_gate / cross_family_0.45: `0.117`
- coherence_margin_gate / cross_family_0.60: `0.153`
- coherence_margin_gate / current: `0.022`
- coherence_margin_gate / delayed_uniform_0.60: `0.001`
- coherence_margin_gate / gaussian_mix_0.60: `0.001`
- coherence_margin_gate / permute_mix_0.60: `0.000`
- coherence_margin_gate / uniform_mix_0.60: `0.002`
- threshold_gate / cross_family_0.30: `0.018`
- threshold_gate / cross_family_0.45: `0.099`
- threshold_gate / cross_family_0.60: `0.144`
- threshold_gate / current: `0.049`
- threshold_gate / delayed_uniform_0.60: `0.018`
- threshold_gate / gaussian_mix_0.60: `0.055`
- threshold_gate / permute_mix_0.60: `0.105`
- threshold_gate / uniform_mix_0.60: `0.083`
