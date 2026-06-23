# BTA-003 Phi Coordinate Sampler Probe

Toy telemetry only. This checks phi as a deterministic proposal sampler, not as physics evidence or authority.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| BTA-003A | PASS | generator_bits_constant / ratio_1k / ratio_20k | `True / 6.14 / 122.71` | Generator-vs-storage compression is real but generic: a compact formula can emit arbitrary-length phi prefixes; this does not make phi unique. |
| BTA-003B | PASS | best_sampler / phi_friction / prng_friction / phi_digits_friction / argmax_friction | `sqrt2_rotation / 0.2297 / 0.3582 / 0.3609 / 1.0317` | Phi rotation promotes only if it reduces local friction versus PRNG, phi-decimal digits, and argmax; losing to another low-discrepancy control is not a failure of the sampler idea. |
| BTA-003C | FAIL | best_sampler / phi_ternary / prng_ternary / phi_always / authority_flips | `phi_write_only / 3.7121 / 3.5753 / 3.5658 / 0` | Ternary pointer semantics promote only if Write/Witness/Release lowers friction without creating any authority path. |

## Sampler Shootout

| Sampler | Friction | L1 | Repeat | Coverage | Surprise |
| --- | ---: | ---: | ---: | ---: | ---: |
| sqrt2_rotation | 0.2284 | 0.0116 | 0.0609 | 1.0000 | 0.8384 |
| phi_rotation | 0.2297 | 0.0129 | 0.0669 | 1.0000 | 0.8384 |
| vdc_base2 | 0.2333 | 0.0112 | 0.0816 | 1.0000 | 0.8382 |
| prng | 0.3582 | 0.0545 | 0.2355 | 1.0000 | 0.8363 |
| phi_digits | 0.3609 | 0.0494 | 0.2345 | 1.0000 | 0.8328 |
| periodic_lattice | 0.3970 | 0.1057 | 0.3058 | 1.0000 | 0.8343 |
| argmax | 1.0317 | 0.3593 | 0.9765 | 0.8542 | 0.5946 |

## Ternary Boundary Tuning

| Sampler | Friction | L1 | Repeat | Coverage | Surprise |
| --- | ---: | ---: | ---: | ---: | ---: |
| phi_write_only | 3.5555 | 0.0151 | 0.0690 | 1.0000 | 0.8341 |
| phi_reset_only | 3.5628 | 0.0147 | 0.0742 | 1.0000 | 0.8347 |
| phi_always_advance | 3.5658 | 0.0129 | 0.0757 | 1.0000 | 0.8340 |
| prng_ternary | 3.5753 | 0.0491 | 0.2417 | 1.0000 | 0.8332 |
| phi_ternary | 3.7121 | 0.5521 | 0.3183 | 0.9740 | 0.8969 |

## Safe Read

The useful version of BTA-003 is phi as a low-discrepancy coordinate generator. It can be tested as proposal scheduling / anti-clumping. Decimal digits of phi are a control, not the foundation, because phi normality is not proven.

If promoted to Aukora, this remains proposal guidance only. It must not enter gate authorization, cryptographic authority, identity, or proof language.
