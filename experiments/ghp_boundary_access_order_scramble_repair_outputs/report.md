# Boundary Access Order-Scramble Repair

- question: can rank-shape repair rescue high internal permutation without hurting normal lanes?
- best train set: `uniform_only`
- best pack: `six_plus_rank_shape`
- dimensions: `13`
- overall held-out accuracy: `1.000`

Ranking:
- uniform_only / six_plus_rank_shape (13D): `1.000`
- uniform_plus_permute / rank_shape_only (7D): `1.000`
- uniform_plus_permute / six_plus_rank_shape (13D): `1.000`
- uniform_plus_permute / damage_rank_only (3D): `1.000`
- uniform_only / rank_shape_only (7D): `1.000`
- uniform_only / damage_rank_only (3D): `1.000`
- uniform_only / baseline_six (6D): `0.825`
- uniform_only / six_plus_scramble_signature (8D): `0.816`
- uniform_plus_permute / baseline_six (6D): `0.770`
- uniform_plus_permute / six_plus_scramble_signature (8D): `0.767`
- uniform_only / helper_rank_only (4D): `0.748`
- uniform_only / scramble_signature_only (2D): `0.748`
- uniform_plus_permute / helper_rank_only (4D): `0.748`
- uniform_plus_permute / scramble_signature_only (2D): `0.748`

Best-pack scenario map:
- cross_family_0.00: `1.000`
- cross_family_0.15: `1.000`
- cross_family_0.30: `1.000`
- cross_family_0.45: `1.000`
- cross_family_0.60: `1.000`
- current: `1.000`
- delayed_uniform_0.00: `1.000`
- delayed_uniform_0.15: `1.000`
- delayed_uniform_0.30: `1.000`
- delayed_uniform_0.45: `1.000`
- delayed_uniform_0.60: `1.000`
- gaussian_mix_0.00: `1.000`
- gaussian_mix_0.15: `1.000`
- gaussian_mix_0.30: `1.000`
- gaussian_mix_0.45: `1.000`
- gaussian_mix_0.60: `1.000`
- permute_mix_0.00: `1.000`
- permute_mix_0.15: `1.000`
- permute_mix_0.30: `1.000`
- permute_mix_0.45: `1.000`
- permute_mix_0.60: `1.000`
- uniform_mix_0.00: `1.000`
- uniform_mix_0.15: `1.000`
- uniform_mix_0.30: `1.000`
- uniform_mix_0.45: `1.000`
- uniform_mix_0.60: `1.000`
