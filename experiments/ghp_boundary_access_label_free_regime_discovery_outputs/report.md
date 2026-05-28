# Boundary Access Label-Free Regime Discovery

- best representation: `strange_features`
- held-out transfer alignment: `0.748`
- held-out best alignment (oracle remap): `0.748`

Ranking:
- strange_features: train-best `0.572`, test-transfer `0.748`, test-best `0.748`
- belief_features: train-best `0.597`, test-transfer `0.711`, test-best `0.711`
- groove_features: train-best `0.614`, test-transfer `0.653`, test-best `0.653`
- base_features: train-best `0.505`, test-transfer `0.584`, test-best `0.584`

Held-out scenario transfer:
- `base_features`
  - clean_current: `0.628`
  - cross_family_mid: `0.535`
  - delayed_uniform_mid: `0.596`
  - gaussian_mix_mid: `0.626`
  - permute_mix_mid: `0.626`
  - uniform_mix_mid: `0.492`
- `strange_features`
  - clean_current: `0.837`
  - cross_family_mid: `0.755`
  - delayed_uniform_mid: `0.579`
  - gaussian_mix_mid: `0.879`
  - permute_mix_mid: `0.855`
  - uniform_mix_mid: `0.577`
- `groove_features`
  - clean_current: `0.986`
  - cross_family_mid: `0.479`
  - delayed_uniform_mid: `0.538`
  - gaussian_mix_mid: `0.579`
  - permute_mix_mid: `0.715`
  - uniform_mix_mid: `0.620`
- `belief_features`
  - clean_current: `0.752`
  - cross_family_mid: `0.749`
  - delayed_uniform_mid: `0.560`
  - gaussian_mix_mid: `0.792`
  - permute_mix_mid: `0.802`
  - uniform_mix_mid: `0.605`
