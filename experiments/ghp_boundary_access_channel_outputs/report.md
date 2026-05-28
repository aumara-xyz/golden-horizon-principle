# Boundary Access Channel Toy

Best family:
- `tribonacci_control` score `0.798`

Fibonacci:
- rank `2/4`
- score `0.789`
- access fidelity `0.991`
- recovery gain `0.015`
- redundancy score `0.982`
- shared overlap `0.982`
- compression stability `0.990`
- structure balance `0.762`

Sensitivity:
- no-balance best `fibonacci` with Fibonacci rank `1/4`
- channel-core best `fibonacci` with Fibonacci rank `1/4`

Interpretation:
- This is a branching-channel toy, not a proof of physics.
- The score rewards the combined package of access, recovery, redundancy, shared overlap, compression stability, and a moderate structure-balance target.
- Fibonacci does not win the current blended score.
- Fibonacci does win when the extra structure-balance preference is removed and we score the core channel package directly.
- Binary can win on redundancy by being too repetitive.
- Ternary can win on diversity by being too diffuse.
- The interesting question is whether Fibonacci helps the whole package at once.
