# BTA-003 Aukora Handoff

Do not port this yet as live behavior. Treat it as a side-lab sampler candidate.

Safe candidate:

- `phi_rotation_sampler`: `x = (x + 1/phi) mod 1`
- map `x` through the current token/action probability CDF
- compare against PRNG, argmax, van-der-Corput/Sobol, sqrt2 rotation, and phi digit controls

Hard laws:

- sampler proposes only
- gate authorizes
- sampler state is not authority
- timing is not authority
- phi decimal digits are not assumed normal
- no cryptographic or identity use

Promotion requirement:

- lower retry/friction than PRNG and argmax on live sandbox traces
- no worse than other low-discrepancy controls by more than a small tolerance
- no private/authority reconstruction
- no telemetry-to-gate read path
