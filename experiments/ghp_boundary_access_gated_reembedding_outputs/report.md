# Boundary Access Gated Re-embedding

- question: can capacity act as a gated alarm instead of a general chooser?
- training: targeted hard-lane grid on train seeds; held-out test seeds
- best policy: `oracle_order_or_capacity`
- overall held-out accuracy: `0.868`

Ranking:
- oracle_order_or_capacity: `0.868`
- trained_capacity_gate: `0.837`
- disagreement_capacity_gate: `0.837`
- capacity_only: `0.824`
- order_plus_flow: `0.809`

Best-policy scenario map:
- cross_family_0.30: `0.879`
- cross_family_0.45: `1.000`
- cross_family_0.60: `0.999`
- current: `0.805`
- delayed_uniform_0.60: `0.790`
- gaussian_mix_0.60: `0.799`
- permute_mix_0.60: `0.817`
- uniform_mix_0.60: `0.854`

Gate-open rates:
- cross_family_0.30: `0.016`
- cross_family_0.45: `0.118`
- cross_family_0.60: `0.152`
- current: `0.009`
- delayed_uniform_0.60: `0.017`
- gaussian_mix_0.60: `0.050`
- permute_mix_0.60: `0.050`
- uniform_mix_0.60: `0.094`
