# BTA-004 Phi Sampler Uniqueness & Compression Envelope

Toy telemetry only. This probes phi as a proposal-sampling and generator-compression candidate, not as physics evidence.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| BTA-004A | PASS | phi_rank / best / random_median / rational_best | `phi_rank=6/50; best=random_alpha_21:0.2238; phi=0.2298; random_median=0.2577; rational_best=0.3066` | Phi is useful only if it behaves like a strong low-discrepancy sampler; this test does not allow uniqueness unless it beats the broader irrational family. |
| BTA-004B | PASS | generator compression ratio on generated vs arbitrary payload | `phi_generated_ratio=0.0156; random_payload_ratio=4.3308` | Generator compression works on generated structure, not arbitrary data. This supports proposal scheduling, not universal compression. |
| BTA-004C | PASS | same integer encoded across bases | `capacity_spread_bits=3.43` | Changing base changes symbol count and glyph density, but not the information content of the underlying state. |

## Top Samplers

| Rank | Sampler | Friction | Alpha | Repeat | L1 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | random_alpha_21 | 0.2238 | 0.530867 | 0.0534 | 0.0126 |
| 2 | random_alpha_27 | 0.2260 | 0.436484 | 0.0568 | 0.0123 |
| 3 | sqrt2_minus_1 | 0.2287 | 0.414214 | 0.0613 | 0.0120 |
| 4 | silver_inv | 0.2287 | 0.414214 | 0.0613 | 0.0120 |
| 5 | random_alpha_26 | 0.2293 | 0.552391 | 0.0548 | 0.0125 |
| 6 | phi_inv | 0.2298 | 0.618034 | 0.0670 | 0.0138 |
| 7 | random_alpha_22 | 0.2316 | 0.558068 | 0.0560 | 0.0125 |
| 8 | random_alpha_31 | 0.2353 | 0.617471 | 0.0669 | 0.0101 |
| 9 | random_alpha_32 | 0.2403 | 0.320717 | 0.0832 | 0.0136 |
| 10 | random_alpha_20 | 0.2407 | 0.691342 | 0.0886 | 0.0111 |
| 11 | random_alpha_33 | 0.2408 | 0.734748 | 0.1097 | 0.0103 |
| 12 | random_alpha_03 | 0.2409 | 0.680674 | 0.0826 | 0.0138 |

## Compression Envelope

| Payload | Raw Bits | Zlib Bits | Best Generator | Patch Bits | Mismatch | Ratio |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| phi_generated | 12288 | 1008 | phi_inv | 192 | 0.0000 | 0.0156 |
| sqrt2_generated | 12288 | 1144 | sqrt2_minus_1 | 192 | 0.0000 | 0.0156 |
| random_payload | 12288 | 18192 | e_minus_2 | 53217 | 0.8630 | 4.3308 |
| structured_periodic | 12288 | 584 | sqrt3_minus_1_frac | 52407 | 0.8499 | 4.2649 |

## Base Encoding Check

| Encoding | Base | Symbols | Capacity Bits | Zlib Bits |
| --- | ---: | ---: | ---: | ---: |
| base2 | 2 | 330 | 330.00 | 672 |
| base10 | 10 | 100 | 332.19 | 544 |
| base16 | 16 | 83 | 332.00 | 536 |
| base36 | 36 | 64 | 330.88 | 560 |
| base62 | 62 | 56 | 333.43 | 512 |

## Safe Read

This strengthens the sampler lane and weakens the uniqueness/compression overclaim lane. The useful object is a bounded proposal scheduler: deterministic, cheap, non-clumping, and comparable against other low-discrepancy controls.

Do not promote phi digits, base-N glyph density, or generator compression into authority, identity, physics, or universal compression claims.
