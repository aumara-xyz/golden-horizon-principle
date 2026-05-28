# Boundary Access Return-Loop Sweep

Configs:
- wake gains `[0.1, 0.22, 0.34, 0.42, 0.56]`
- wake decays `[0.45, 0.62, 0.78, 0.9]`
- mask keeps `[0.25, 0.38, 0.5]`

Best blended-diff config:
- wake gain `0.1`
- wake decay `0.9`
- mask keep `0.5`
- blended diff `0.011621`
- core diff `-0.001723`

Win counts:
- positive blended diff cases `24/60`
- positive core diff cases `0/60`

Interpretation:
- Weak return can help the blended score in some regimes.
- Return does not improve the core channel score in any tested regime.
- The current disciplined read is that recycled wake may add texture, but it does not yet improve the actual access-plus-recovery core package.
