# Boundary Access Channel Sweep

Configs:
- balance targets `[0.45, 0.6, 0.75]`
- fragment budgets `[64, 96, 160]`
- mask keeps `[0.25, 0.35, 0.5]`

Fibonacci average ranks:
- blended score `3.04`
- no-balance score `1.00`
- channel-core score `1.00`

Win counts:
- blended `{'fibonacci': 9, 'fibonacci_alt_return': 4, 'fibonacci_fibblock_return': 14}`
- no-balance `{'fibonacci': 27}`
- channel-core `{'fibonacci': 27}`

Alternating-return control:
- included as `fibonacci_alt_return`
- purpose: test "recycled but altered return" without claiming a full negative-Fibonacci derivation

Fibonacci-block return control:
- included as `fibonacci_fibblock_return`
- purpose: test recycled return in growing Fibonacci-sized segments instead of raw every-other-step flipping

Interpretation:
- if Fibonacci keeps winning channel-core but not blended score, that supports the anti-locking-core reading more than the "wins everything" reading
- if the alternating-return control helps, the recycled-information intuition may be worth formalizing
- if generic non-Fibonacci families match or beat Fibonacci across all score views, the strong minimal-architecture claim weakens
