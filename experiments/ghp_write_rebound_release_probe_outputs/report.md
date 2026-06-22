# WRR-001 Write-Rebound-Release Probe

Toy telemetry only. This tests whether ternary boundary actions leave distinct after-effects that improve future-state prediction.

| Probe | Status | Metric | Value | Safest Read |
| --- | --- | --- | --- | --- |
| WRR-001 | FAIL | surprise_gain_vs_memoryless / vs_write_only / vs_shuffled / leaky_gain / action_macro_f1 / harmful_error | `-0.0128 / -0.0130 / -0.0128 / -0.0000 / 0.7678 / 0.0000` | If this passes, write/witness/release events are not isolated labels: their rebound effects help predict future boundary surprise better than memoryless or write-only controls. |

## Metrics

| Policy | Split | Surprise MAE | Pressure MAE | Action Accuracy | Action Macro F1 | Rebound MI-like | Leakage | Harmful Error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| memoryless | train | 0.0279 | 0.1573 | 1.0000 | 1.0000 | 0.0945 | 0.0000 | 0.0000 |
| memoryless | test | 0.0280 | 0.1578 | 1.0000 | 1.0000 | 0.0949 | 0.0000 | 0.0000 |
| write_only_rebound | train | 0.0277 | 0.1573 | 0.9692 | 0.8427 | 0.0945 | 0.0000 | 0.0000 |
| write_only_rebound | test | 0.0278 | 0.1577 | 0.9677 | 0.8424 | 0.0949 | 0.0000 | 0.0000 |
| ternary_rebound | train | 0.0406 | 0.1573 | 0.9483 | 0.7649 | 0.0945 | 0.0000 | 0.0000 |
| ternary_rebound | test | 0.0408 | 0.1578 | 0.9471 | 0.7678 | 0.0949 | 0.0000 | 0.0000 |
| shuffled_receipt | train | 0.0279 | 0.1573 | 0.9819 | 0.9684 | 0.0945 | 0.0000 | 0.0000 |
| shuffled_receipt | test | 0.0280 | 0.1578 | 0.9818 | 0.9691 | 0.0949 | 0.0000 | 0.0000 |
| leaky_rebound | train | 0.0406 | 0.1573 | 0.9255 | 0.8782 | 0.0945 | 1.0000 | 0.0000 |
| leaky_rebound | test | 0.0408 | 0.1577 | 0.9254 | 0.8805 | 0.0949 | 1.0000 | 0.0000 |

## Paper-Safe Read

If promoted, the safe claim is that toy receipt events have after-effects: ternary write/witness/release state can improve prediction of future boundary surprise compared with memoryless or write-only controls.

Do not claim sonoluminescence proves GHP, AI experience, physical time, or consciousness.
