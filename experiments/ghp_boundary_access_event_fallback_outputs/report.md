# Boundary Access Event Fallback

Config:
- normal mask keep `0.5`
- damage mask keep `0.1`
- damage probability `0.22`
- damage trigger threshold `0.28`
- fallback gain `0.32`
- wake decay `0.9`

Best family:
- `event_stale` event score `0.693`

Best core family:
- `event_stale` core score `0.600`

Reference comparison:
- no-return event score `0.661`
- no-return core score `0.559`
- event-fibonacci event score `0.629`
- event-fibonacci core score `0.527`
- event-fibonacci trigger rate `0.970`

Interpretation:
- This tests return as a fallback after explicit damage, not as normal flow.
- The question is whether Fibonacci fallback rescues a damaged channel better than no-return and stronger controls.
