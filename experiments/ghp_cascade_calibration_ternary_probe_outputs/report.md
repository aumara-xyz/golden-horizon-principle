# CAS-006/009/010 Cascade Calibration And Ternary Probe

Toy telemetry only. This tests whether finite-depth projection is better read as calibrated early-warning plus ternary write/witness/release rather than binary write/no-write.

## Probe Results

| Probe | Status | Metric | Value | Safest Read |
| --- | --- | --- | --- | --- |
| CAS-006 | PASS | avg_auc / raw_gap / shuffled_gap / top_decile_capture / leaky_gain | `0.9711 / 0.3004 / 0.6940 / 0.8248 / 0.0003` | If this passes, finite-depth projection is a calibrated early-warning signal rather than just a weak binary classifier. |
| CAS-009 | PASS | avg_macro_f1 / harmful_error / leaky_gain | `0.7296 / 0.0020 / 0.0003` | If this passes, write/witness/release is a better action alphabet than binary write/no-write for finite-depth boundary output. |
| CAS-010 | PASS | calibration_pass / ternary_pass | `1 / 1` | If this passes, the paper can receive one cautious toy-telemetry sentence about finite-depth projection and ternary boundary actions. |

## Regime Summary

| Regime | AUC | Raw Gap | Shuffled Gap | Top-Decile Capture | Decile Lift | Macro F1 | Write F1 | Witness F1 | Release F1 | Harmful Error | Leaky Gain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| stable | 0.9778 | 0.2664 | 0.9180 | 0.9353 | 9.3531 | 0.7435 | 0.6146 | 0.6876 | 0.9284 | 0.0001 | -0.0013 |
| noisy | 0.9584 | 0.3532 | 0.8936 | 0.6750 | 6.7505 | 0.7087 | 0.6682 | 0.5507 | 0.9072 | 0.0046 | 0.0030 |
| drifty | 0.9737 | 0.3150 | 0.8536 | 0.8366 | 8.3661 | 0.7502 | 0.6752 | 0.6595 | 0.9160 | 0.0011 | 0.0007 |
| bursty | 0.9702 | 0.2776 | 0.0089 | 0.8962 | 8.9616 | 0.7211 | 0.6097 | 0.6231 | 0.9306 | 0.0010 | -0.0003 |
| sparse | 0.9900 | 0.2880 | 0.9281 | 1.0000 | 10.0000 | 0.6838 | 0.4776 | 0.6142 | 0.9597 | 0.0002 | 0.0019 |
| dense | 0.9663 | 0.3150 | 0.0994 | 0.6579 | 6.5787 | 0.7569 | 0.7140 | 0.6833 | 0.8734 | 0.0006 | -0.0009 |
| volatile | 0.9492 | 0.3409 | 0.8906 | 0.6251 | 6.2510 | 0.7028 | 0.7074 | 0.5099 | 0.8912 | 0.0080 | 0.0008 |
| smooth | 0.9835 | 0.2468 | 0.9597 | 0.9726 | 9.7260 | 0.7700 | 0.6285 | 0.7589 | 0.9225 | 0.0000 | -0.0015 |

## Paper-Safe Read

If CAS-010 passes, the safe paper update is limited to a toy-telemetry note: finite-depth public projections may be better interpreted through calibrated early-warning and a write/witness/release alphabet than through binary write/no-write scoring.

No physics proof, consciousness proof, universal depth, or observer-created-reality claim follows.
