# Boundary Access Continuity Fallback

Config:
- damage mask keep `0.1`
- damage probability `0.22`
- trigger threshold `0.28`
- nearby shift `3`
- delayed blend `0.55`

Best family:
- `stale_same` event score `0.693`

Best core family:
- `stale_same` core score `0.600`

Continuity comparison:
- stale same core score `0.600`
- nearby shift core score `0.527`
- delayed blend core score `0.600`

Interpretation:
- This tests whether stale wake rescue is real continuity or just easy fallback.
- If same-wake continuity clearly beats nearby, delayed, shuffled, and cross-family wake, then retained continuity is doing real work.
