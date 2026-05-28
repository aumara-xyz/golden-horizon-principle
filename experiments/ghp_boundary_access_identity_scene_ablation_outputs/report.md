# Boundary Access Identity vs Scene Ablation

- helper gain `0.12`
- rescue gain `0.54`

Winners:
- missing / self: `fresh_echo` `0.699`
- missing / scene: `fresh_echo` `0.700`
- missing / direction: `fresh_echo` `0.698`
- wrong / self: `deep_trace` `0.889`
- wrong / scene: `fresh_echo` `0.889`
- wrong / direction: `fresh_echo` `0.889`
- overload / self: `deep_trace` `0.793`
- overload / scene: `fresh_echo` `0.793`
- overload / direction: `deep_trace` `0.793`

Interpretation:
- This weakens the helper channel so rescue has to do more real work.
- If the winners split here, then earlier alignment was partly a side-information artifact.
