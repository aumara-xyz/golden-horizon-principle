# Boundary Access Gated Return Sweep

Configs:
- pressure thresholds `[0.12, 0.25, 0.38, 0.5, 0.62]`
- sparsity thresholds `[0.18, 0.3, 0.42, 0.54]`
- gate modes `['pressure_soft', 'pressure_drift', 'pressure_or_sparse', 'pressure_and_sparse']`

References:
- no-return core score `0.699793`
- always-return core score `0.693397`

Best core config:
- gate mode `pressure_drift`
- pressure threshold `0.62`
- sparsity threshold `0.42`
- gate rate `0.000000`
- core diff vs no-return `0.000001`
- core diff vs always-return `0.006396`
- blended diff vs no-return `0.000001`

Win counts:
- positive core vs no-return `13/80`
- positive core vs always-return `71/80`
- positive core vs both `13/80`

Interpretation:
- This asks whether return only helps when it is actually gated by pressure instead of flowing constantly.
- If some gated configs beat both no-return and always-return on the core score, then return may matter as a conditional stabilizer.
- If they do not, the current honest read stays with the anti-locking core and treats return as secondary texture at best.
