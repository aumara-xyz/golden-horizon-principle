# GHP Structural Vs Case Memory Probe

Status: synthetic toy telemetry only.

This tests whether compact structural memory predicts gate outcomes better, with fewer bits, than raw case memory.

It does not prove consciousness or GHP physics.

## Results

### SVC-001: pass / generalization

- Metric: case_acc; structural_acc; shuffled_acc; random_policy_acc; case_surprise; structural_surprise; case_mdl; structural_mdl; shuffled_mdl
- Value: 0.8483; 0.9289; 0.5022; 0.9289; 0.7644; 0.3337; 17719.91; 6976.67; 11296.47
- Null hypothesis: Structural memory does not predict gate outcomes better or more compactly than case memory and controls.
- Safest read: Structural policy-like memory improves prediction, withheld-action generalization, and MDL over raw case memory. Randomized policy IDs do not hurt here, which suggests the win comes from structural features rather than policy-id memorization.
- Falsifier: Case memory or shuffled/randomized controls match structural memory, especially on withheld actions.

### SVC-002: pass

- Metric: case_withheld_acc; structural_withheld_acc; shuffled_withheld_acc; case_withheld_surprise; structural_withheld_surprise
- Value: 0.3128; 0.6480; 0.2263; 2.3219; 1.2418
- Null hypothesis: Structural memory does not generalize to withheld actions/resources better than case memory.
- Safest read: Structural memory generalizes across action family and policy shape instead of exact remembered episodes.
- Falsifier: Withheld action prediction collapses to case-memory or shuffled-control levels.

### SVC-003: pass

- Metric: case_near_miss_acc; structural_near_miss_acc; near_miss_count
- Value: 0.7924; 0.9064; 342
- Null hypothesis: Structural memory does not handle adversarial near-miss intents better than case memory.
- Safest read: Structural memory better distinguishes forbidden capability from missing/malformed authorization.
- Falsifier: Near-miss accuracy does not improve over case memory.

## Aukora Translation

```text
case memory = individual remembered gate episodes
structural memory = compact signed rule / policy shape
```

Hard rule:

```text
Compression is only useful if it preserves or improves prediction.
Structural memory may guide proposals.
Structural memory may never authorize effects.
```

## Gemini 20D Target

Port this into Aukora by comparing a case-memory predictor against a structural-memory predictor over `capability_refusal`, `authorization_refusal`, `malformed_refusal`, and `unknown_refusal`, including withheld actions/resources and near-miss intents.
