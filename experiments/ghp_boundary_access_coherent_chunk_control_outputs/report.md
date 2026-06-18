# Boundary Access Coherent-Chunk Control

- question: does rank-shape repair survive when coherent outside signal is local-chunk-shaped instead of full-truth-shaped?
- best pack: `six_plus_rank_shape`
- dimensions: `13`
- overall held-out accuracy: `0.999`

Ranking:
- six_plus_rank_shape (13D): `0.999`
- rank_shape_only (7D): `0.997`
- damage_rank_only (3D): `0.991`
- baseline_six (6D): `0.824`
- six_plus_scramble_signature (8D): `0.816`

Best-pack scenario map:
- cross_family_0.00: `1.000`
- cross_family_0.15: `1.000`
- cross_family_0.30: `0.998`
- cross_family_0.45: `0.999`
- cross_family_0.60: `1.000`
- current: `1.000`
- delayed_uniform_0.00: `1.000`
- delayed_uniform_0.15: `1.000`
- delayed_uniform_0.30: `1.000`
- delayed_uniform_0.45: `0.999`
- delayed_uniform_0.60: `1.000`
- gaussian_mix_0.00: `1.000`
- gaussian_mix_0.15: `1.000`
- gaussian_mix_0.30: `1.000`
- gaussian_mix_0.45: `1.000`
- gaussian_mix_0.60: `0.999`
- permute_mix_0.00: `1.000`
- permute_mix_0.15: `1.000`
- permute_mix_0.30: `1.000`
- permute_mix_0.45: `1.000`
- permute_mix_0.60: `0.973`
- uniform_mix_0.00: `1.000`
- uniform_mix_0.15: `1.000`
- uniform_mix_0.30: `1.000`
- uniform_mix_0.45: `1.000`
- uniform_mix_0.60: `1.000`
