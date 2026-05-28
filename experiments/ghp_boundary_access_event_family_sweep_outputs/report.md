# Boundary Access Event Family Sweep

Configs:
- damage keeps `[0.06, 0.1, 0.16]`
- damage probabilities `[0.12, 0.22, 0.34]`
- trigger thresholds `[0.2, 0.28, 0.4]`

Event-score win counts:
- `{'event_stale': 27}`

Core-score win counts:
- `{'event_stale': 27}`

Interpretation:
- This checks which fallback family actually wins once explicit damage exists.
- If Fibonacci does not win the core score here, the stronger read is that event rescue matters more than Fibonacci structure in this lane.
