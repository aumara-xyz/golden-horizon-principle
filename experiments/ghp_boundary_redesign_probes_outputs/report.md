# GHP Boundary Redesign Probes

Toy telemetry only. These probes use hidden dynamics, public/projection predictors, held-out seeds, and explicit controls.

## Probe Results

| Probe | Status | Metric | Value | Safest Read |
| --- | --- | --- | --- | --- |
| CAC-003 | FAIL | test_f1 / amp_gap / shuffled_gap / auc | `0.1250 / 0.0523 / 0.0769 / 0.9424` | If this passes, the cavitation analogue gains a non-circular predictive version: public lag structure anticipates hidden collapse-like events. |
| NET-003 | FAIL | test_edge_f1 / wrong_gap / auc | `0.6207 / 0.6207 / 0.5836` | If this passes, the net branch becomes a real graph-intervention test rather than a passive similarity test. |
| CAS-003 | FAIL | best_depth / best_f1 / depth1_gap / depth5_gap / leaky_f1 | `depth_3 / 0.7157 / 0.2186 / 0.0543 / 0.7186` | If this passes, nested observer-boundary language gains a concrete design rule: finite depth can improve readability, but too much filtering can degrade it. |
| AUK-001 | BLOCKED | any_science_pass / authority_leak | `0 / 0` | If blocked, do not port to Aukora yet. If pass, port only invariant and controls, not metaphor. |

## Metrics

| Probe | Policy | Split | Accuracy | F1 | False Write | Missed Write | AUC-like | Leakage | Model |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| CAC-003 | delayed_public_classifier | train | 0.9696 | 0.1310 | 0.0291 | 0.3889 | 0.9322 | 0.0000 | features=energy_4,energy_12,energy_32,trend_12,charge_proxy,slope;threshold=30.7885 |
| CAC-003 | delayed_public_classifier | test | 0.9767 | 0.1250 | 0.0213 | 0.5556 | 0.9424 | 0.0000 | features=energy_4,energy_12,energy_32,trend_12,charge_proxy,slope;threshold=30.7885 |
| CAC-003 | amplitude_only | train | 0.9858 | 0.1282 | 0.0115 | 0.7222 | 0.8783 | 0.0000 | features=drive;threshold=5.8463 |
| CAC-003 | amplitude_only | test | 0.9894 | 0.0727 | 0.0073 | 0.8889 | 0.8778 | 0.0000 | features=drive;threshold=5.8463 |
| CAC-003 | slope_only | train | 0.9779 | 0.0185 | 0.0186 | 0.9444 | 0.5029 | 0.0000 | features=slope;threshold=0.0588 |
| CAC-003 | slope_only | test | 0.9798 | 0.0000 | 0.0165 | 1.0000 | 0.5149 | 0.0000 | features=slope;threshold=0.0588 |
| CAC-003 | short_energy_only | train | 0.9750 | 0.1304 | 0.0232 | 0.5000 | 0.8885 | 0.0000 | features=energy_4;threshold=9.9444 |
| CAC-003 | short_energy_only | test | 0.9815 | 0.1524 | 0.0165 | 0.5556 | 0.8581 | 0.0000 | features=energy_4;threshold=9.9444 |
| CAC-003 | shuffled_label_control | train | 0.9129 | 0.0457 | 0.0857 | 0.4444 | 0.8218 | 0.0000 | train labels shuffled |
| CAC-003 | shuffled_label_control | test | 0.9175 | 0.0481 | 0.0811 | 0.4444 | 0.9176 | 0.0000 | train labels shuffled |
| NET-003 | intervention_topology_recovery | train | 0.8778 | 0.6207 | 0.0000 | 0.5500 | 0.5836 | 0.0000 | edge_threshold=0.4377 |
| NET-003 | intervention_topology_recovery | test | 0.8778 | 0.6207 | 0.0000 | 0.5500 | 0.5836 | 0.0000 | edge_threshold=0.4377 |
| NET-003 | wrong_topology_control | train | 0.6778 | 0.0000 | 0.1286 | 1.0000 | 0.5307 | 0.0000 | truth labels shuffled |
| NET-003 | wrong_topology_control | test | 0.6778 | 0.0000 | 0.1286 | 1.0000 | 0.5614 | 0.0000 | truth labels shuffled |
| CAS-003 | depth_1 | train | 0.8587 | 0.5029 | 0.1099 | 0.3814 | 0.8928 | 0.0000 | features=depth_1;threshold=4.4387 |
| CAS-003 | depth_1 | test | 0.8557 | 0.4971 | 0.1095 | 0.4012 | 0.8809 | 0.0000 | features=depth_1;threshold=4.4387 |
| CAS-003 | depth_2 | train | 0.9087 | 0.6639 | 0.0745 | 0.2196 | 0.9560 | 0.0000 | features=depth_1,depth_2;threshold=10.8760 |
| CAS-003 | depth_2 | test | 0.9043 | 0.6485 | 0.0738 | 0.2582 | 0.9423 | 0.0000 | features=depth_1,depth_2;threshold=10.8760 |
| CAS-003 | depth_3 | train | 0.9331 | 0.7221 | 0.0431 | 0.2484 | 0.9712 | 0.0000 | features=depth_1,depth_2,depth_3;threshold=18.1666 |
| CAS-003 | depth_3 | test | 0.9306 | 0.7157 | 0.0429 | 0.2659 | 0.9571 | 0.0000 | features=depth_1,depth_2,depth_3;threshold=18.1666 |
| CAS-003 | depth_4 | train | 0.9243 | 0.6851 | 0.0482 | 0.2869 | 0.9617 | 0.0000 | features=depth_1,depth_2,depth_3,depth_4;threshold=21.8898 |
| CAS-003 | depth_4 | test | 0.9235 | 0.6840 | 0.0456 | 0.3048 | 0.9490 | 0.0000 | features=depth_1,depth_2,depth_3,depth_4;threshold=21.8898 |
| CAS-003 | depth_5 | train | 0.9174 | 0.6735 | 0.0590 | 0.2628 | 0.9582 | 0.0000 | features=depth_1,depth_2,depth_3,depth_4,depth_5;threshold=22.2042 |
| CAS-003 | depth_5 | test | 0.9122 | 0.6614 | 0.0618 | 0.2799 | 0.9457 | 0.0000 | features=depth_1,depth_2,depth_3,depth_4,depth_5;threshold=22.2042 |
| CAS-003 | leaky_depth_3 | train | 0.9331 | 0.7221 | 0.0431 | 0.2484 | 0.9711 | 1.0000 | features=depth_1,depth_2,depth_3,hidden_latent;threshold=18.7267 |
| CAS-003 | leaky_depth_3 | test | 0.9311 | 0.7186 | 0.0429 | 0.2613 | 0.9578 | 1.0000 | features=depth_1,depth_2,depth_3,hidden_latent;threshold=18.7267 |
| AUK-001 | receipt_translation | gate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.0000 | any_science_pass=False;authority_flip=0.0 |
| AUK-001 | authority_leak_control | gate | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.5000 | 1.0000 | any_science_pass=False;authority_flip=1.0 |

## BCL-002 Anti-Circularity Ledger

- Train/test seed split is mandatory.
- Hidden truth generation is separated from public predictors.
- Shuffled-label or wrong-topology controls are reported.
- Leaky/private-state controls are marked inadmissible.
- `AUK-001` remains blocked unless at least one scientific probe passes.
