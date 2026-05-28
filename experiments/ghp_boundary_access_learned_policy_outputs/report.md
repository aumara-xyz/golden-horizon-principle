# Boundary Access Learned Policy

Best policy:
- `always_fresh` learned score `0.794`

Learned map:
- `missing/current->deep_trace;missing/delayed->deep_trace;missing/noisy->layered_recent_deep;overload/current->deep_trace;overload/delayed->fresh_echo;overload/noisy->deep_trace;wrong/current->layered_recent_deep;wrong/delayed->layered_recent_deep;wrong/noisy->layered_recent_deep`

Interpretation:
- This tests whether online contextual learning can recover a better rescue map than hand-written routing.
