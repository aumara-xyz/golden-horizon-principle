# Boundary Access Gated Return

Config:
- wake gain `0.22`
- wake decay `0.9`
- mask keep `0.5`
- pressure threshold `0.12`
- sparsity threshold `0.18`

Best family:
- `fibonacci_pressure_or_sparse_gate` score `0.630`

Best core family:
- `fibonacci_pressure_drift_gate` core score `0.700`

Reference comparison:
- no-return score `0.560`
- always-return score `0.630`
- pressure-or-sparse gate score `0.630`
- no-return core score `0.700`
- always-return core score `0.693`
- pressure-or-sparse gate core score `0.693`
- pressure-or-sparse gate rate `1.000`

Interpretation:
- This tests return as pressure relief instead of constant recycling.
- If a gated family beats both no-return and always-return on the core score, then return may matter only under stress.
- If no-return still wins, the anti-locking core remains the clearest live result.
