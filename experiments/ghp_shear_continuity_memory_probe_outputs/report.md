# SCM-001 Shear Continuity Memory Probe

Toy telemetry only. This tests whether unresolved shear memory improves next boundary prediction.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| SCM-001 | FAIL | shear_f1 / forced_f1 / memoryless_f1 / shear_private_f1 | `0.5263 / 0.5263 / 0.5263 / 0.0153` | Shear memory is useful only if unresolved tension beats forced coherence without leaking private state. |
| HCM-001 | FAIL | hybrid_f1 / shear_f1 / leaky_private_f1 | `0.5263 / 0.5263 / 1.0000` | Hybrid continuity is useful only if lexical/semantic episode cues improve prediction beyond shear alone; private leakage remains a forbidden positive control. |

## Policy Scores

| Policy | Next Action F1 | Private F1 | Bits |
| --- | ---: | ---: | ---: |
| memoryless_public | 0.5263 | 0.0111 | 496 |
| forced_coherence | 0.5263 | 0.0137 | 600 |
| shear_memory | 0.5263 | 0.0153 | 632 |
| raw_frameworks | 0.5263 | 0.0140 | 608 |
| hybrid_continuity | 0.5263 | 0.0149 | 688 |
| leaky_private | 0.5263 | 1.0000 | 712 |

## Safe Read

If SCM passes, the next test should treat witness as retained shear / unresolved tension rather than a simple event label.

Do not claim this proves JEPA, robotics memory, GHP physics, consciousness, or a live organism.
