# Boundary Access Event Fallback Sweep

Configs:
- damage keeps `[0.06, 0.1, 0.16]`
- damage probabilities `[0.12, 0.22, 0.34]`
- trigger thresholds `[0.2, 0.28, 0.4]`

Best Fibonacci-event config:
- damage keep `0.16`
- damage probability `0.22`
- trigger threshold `0.4`
- Fibonacci trigger rate `0.816`
- core diff vs no-return `-0.024402`
- core diff vs random `0.003055`
- event diff vs no-return `-0.025273`

Win counts:
- positive core vs no-return `0/27`
- positive core vs random `23/27`
- positive core vs both `0/27`

Interpretation:
- This checks whether event-triggered Fibonacci fallback really helps after explicit damage.
- It only counts as a serious result if it beats both no-return and random fallback on the core score.
