# Boundary Access Return Loop

Best family:
- `fibonacci_no_return_loop` score `0.621`

Best core family:
- `fibonacci_no_return_loop` core score `0.700`

Fibonacci return loop:
- blended rank `2/5`
- core rank `2/5`
- access fidelity `0.959`
- recovery gain `0.000`
- shared overlap `1.000`
- wake gain `0.000`
- wake balance `0.823`

Fibonacci return vs no-return:
- return score `0.612`
- no-return score `0.621`
- return core score `0.683`
- no-return core score `0.700`

Interpretation:
- This is the first toy where the wake actually goes back into the channel with decay.
- The question is not whether the same thing returns.
- The question is whether recycled-but-altered return helps preserve readable, recoverable, shared structure.
