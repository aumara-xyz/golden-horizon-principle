# BTA-005 Aukora Handoff

Candidate to test in Aukora later:

`MDL process memory = generator_id + seed/state + residual corrections`

Use only on public sandbox traces. Compare:

- raw compressed receipt history
- structural summary memory
- phi-rotation generator + residuals
- sqrt2 / vdc / argmax / PRNG controls + residuals

Promotion metrics:

- `rule_bits + residual_bits < compressed_raw_receipt_bits`
- prediction accuracy does not collapse
- residuals remain explicit, auditable, and replayable
- private/authority reconstruction stays near chance
- no sampler or memory summary can authorize action

Do not promote:

- phi digits as memory
- generator compression as arbitrary-payload compression
- sampler state as identity or authority

Latest lab statuses:

- BTA-005A: PASS - phi_ratio=0.0192; prng_ratio=2.2615
- BTA-005B: PASS - mixed_ratio=2.5855; human_ratio=0.5352; phi_ratio=0.0192
- BTA-005C: PASS - argmax_ratio=0.1541
