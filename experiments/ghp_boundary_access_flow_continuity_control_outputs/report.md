# Boundary Access Flow-Continuity Control

- question: does the chooser improve when it tracks local order moving through time?
- best pack: `order_plus_flow`
- dimensions: `25`
- overall held-out accuracy: `0.852`

Ranking:
- order_plus_flow (25D): `0.852`
- baseline_plus_order_flow (31D): `0.818`
- order_relation_only (8D): `0.786`
- baseline_plus_flow (23D): `0.776`
- flow_only (17D): `0.754`
- baseline_six (6D): `0.726`

Best-pack scenario map:
- cross_family_0.00: `0.862`
- cross_family_0.15: `0.871`
- cross_family_0.30: `0.811`
- cross_family_0.45: `0.796`
- cross_family_0.60: `0.718`
- current: `0.850`
- delayed_uniform_0.00: `0.861`
- delayed_uniform_0.15: `0.869`
- delayed_uniform_0.30: `0.870`
- delayed_uniform_0.45: `0.859`
- delayed_uniform_0.60: `0.848`
- gaussian_mix_0.00: `0.873`
- gaussian_mix_0.15: `0.851`
- gaussian_mix_0.30: `0.860`
- gaussian_mix_0.45: `0.860`
- gaussian_mix_0.60: `0.867`
- permute_mix_0.00: `0.851`
- permute_mix_0.15: `0.857`
- permute_mix_0.30: `0.862`
- permute_mix_0.45: `0.865`
- permute_mix_0.60: `0.877`
- uniform_mix_0.00: `0.857`
- uniform_mix_0.15: `0.863`
- uniform_mix_0.30: `0.877`
- uniform_mix_0.45: `0.867`
- uniform_mix_0.60: `0.855`
