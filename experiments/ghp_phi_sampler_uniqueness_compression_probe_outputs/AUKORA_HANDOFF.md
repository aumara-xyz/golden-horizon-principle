# BTA-004 Aukora Handoff

Do not port as live control yet.

Candidate worth testing later:

- Add `phi_rotation_sampler` only as an optional proposal scheduler.
- Compare it against `sqrt2_rotation`, van-der-Corput/Sobol-style controls, PRNG, argmax, and current sampler behavior.
- Use live sandbox traces only.

Non-candidates:

- Phi decimal digits as memory or address space.
- Base-N glyph density as compression proof.
- Generator compression as arbitrary-payload compression.
- Any sampler state as gate authority.

Promotion requirement:

- Improves retry/friction or exploration coverage on sandbox traces.
- Performs near the best low-discrepancy controls, not merely better than PRNG.
- Does not reconstruct private/authority state.
- Has no read path into gate/apply/OpenCode authority.

Latest lab statuses:

- BTA-004A: PASS - phi_rank=6/50; best=random_alpha_21:0.2238; phi=0.2298; random_median=0.2577; rational_best=0.3066
- BTA-004B: PASS - phi_generated_ratio=0.0156; random_payload_ratio=4.3308
- BTA-004C: PASS - capacity_spread_bits=3.43
