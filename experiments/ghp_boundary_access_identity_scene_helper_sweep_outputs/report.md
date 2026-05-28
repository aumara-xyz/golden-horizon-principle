# Boundary Access Identity/Scene Helper Sweep

- helper gains `[0.0, 0.12, 0.25, 0.4]`
- total side gain `0.66`

Interpretation:
- This asks whether the self-vs-scene split is robust or just a helper-channel weighting artifact.
- If winners change as helper gain moves, then rescue target is context-sensitive rather than fixed.

Winner summary:
- helper `0.0` / missing: self=`deep_trace` scene=`deep_trace` direction=`deep_trace`
- helper `0.0` / wrong: self=`fresh_echo` scene=`fresh_echo` direction=`fresh_echo`
- helper `0.0` / overload: self=`layered_recent_deep` scene=`fresh_echo` direction=`layered_recent_deep`
- helper `0.12` / missing: self=`fresh_echo` scene=`fresh_echo` direction=`fresh_echo`
- helper `0.12` / wrong: self=`fresh_echo` scene=`fresh_echo` direction=`fresh_echo`
- helper `0.12` / overload: self=`deep_trace` scene=`fresh_echo` direction=`fresh_echo`
- helper `0.25` / missing: self=`fresh_echo` scene=`fresh_echo` direction=`fresh_echo`
- helper `0.25` / wrong: self=`layered_recent_deep` scene=`fresh_echo` direction=`fresh_echo`
- helper `0.25` / overload: self=`deep_trace` scene=`fresh_echo` direction=`deep_trace`
- helper `0.4` / missing: self=`deep_trace` scene=`deep_trace` direction=`deep_trace`
- helper `0.4` / wrong: self=`layered_recent_deep` scene=`layered_recent_deep` direction=`layered_recent_deep`
- helper `0.4` / overload: self=`deep_trace` scene=`deep_trace` direction=`deep_trace`
