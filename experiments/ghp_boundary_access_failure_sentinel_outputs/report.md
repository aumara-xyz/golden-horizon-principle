# Boundary Access Failure Sentinel

Status: targeted hard-lane toy telemetry only.

- question: can legal local context detect when both order and capacity are wrong?
- mode: `scout`
- settings: scout grid, two train seeds, one held-out test seed, one trial per scenario, 64 time steps
- best sentinel: `order_capacity_context_sparse_5pct_false_alarm`
- open rate: `0.080`
- precision: `0.577`
- both-wrong recall: `0.390`

Ranking:
- order_capacity_context_sparse_5pct_false_alarm (49D): open `0.080`, precision `0.577`, recall `0.390`
- full_local_context_sparse_5pct_false_alarm (55D): open `0.086`, precision `0.500`, recall `0.364`
- score_only_sparse_5pct_false_alarm (6D): open `0.058`, precision `0.368`, recall `0.182`
- capacity_context_sparse_5pct_false_alarm (24D): open `0.061`, precision `0.325`, recall `0.169`
- order_capacity_context_default (49D): open `0.005`, precision `0.667`, recall `0.026`
- capacity_context_default (24D): open `0.006`, precision `0.500`, recall `0.026`
- full_local_context_default (55D): open `0.006`, precision `0.500`, recall `0.026`
- score_only_default (6D): open `0.000`, precision `0.000`, recall `0.000`

Sparse thresholds:
- score_only: threshold `0.249`, train both-wrong capture `0.247`, train both-correct false alarm `0.049`
- capacity_context: threshold `0.322`, train both-wrong capture `0.204`, train both-correct false alarm `0.049`
- order_capacity_context: threshold `0.344`, train both-wrong capture `0.377`, train both-correct false alarm `0.049`
- full_local_context: threshold `0.361`, train both-wrong capture `0.383`, train both-correct false alarm `0.049`

Best-sentinel bucket opens:
- both_wrong: `0.390` (77)
- both_correct: `0.045` (487)
- order_only: `0.000` (38)
- capacity_only: `0.000` (52)
