# Boundary Access Deep Groove

Config:
- damage mask keep `0.1`
- damage probability `0.22`
- trigger threshold `0.28`
- deep decay `0.97`
- medium delay `4`
- frozen step `12`
- layer blend `0.58`

Best family:
- `layered_recent_deep` event score `0.693`

Best core family:
- `layered_recent_deep` core score `0.600`

Depth comparison:
- fresh echo core score `0.600`
- short delay core score `0.600`
- deep trace core score `0.600`
- layered recent + deep core score `0.600`

Interpretation:
- This asks whether rescue is strongest from fresh local continuity, delayed continuity, or deeper retained identity trace.
- If deep or layered families beat fresh echo, then the repair lane looks more like identity continuity than immediate local recall.
