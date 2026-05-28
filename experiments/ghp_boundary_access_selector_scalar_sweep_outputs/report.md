# Boundary Access Selector Scalar Sweep

- best scalar form:
  `score = a*novel_but_fits - b*foreign_pressure + c*wake_pull - d*belief_tension`

- best coefficients: `a=1.0, b=2.0, c=2.0, d=0.0`
- held-out accuracy: `0.793`
- train accuracy: `0.795`

Top candidates:
- `a=1.0, b=2.0, c=2.0, d=0.0` -> test `0.793`, train `0.795`
- `a=1.0, b=2.0, c=1.0, d=0.0` -> test `0.792`, train `0.795`
- `a=1.0, b=1.0, c=2.0, d=0.0` -> test `0.792`, train `0.794`
- `a=1.0, b=2.0, c=0.0, d=0.0` -> test `0.786`, train `0.789`
- `a=1.0, b=1.0, c=1.0, d=0.0` -> test `0.785`, train `0.788`
- `a=2.0, b=2.0, c=2.0, d=0.0` -> test `0.785`, train `0.788`
- `a=1.0, b=2.0, c=2.0, d=1.0` -> test `0.785`, train `0.787`
- `a=1.0, b=0.0, c=2.0, d=0.0` -> test `0.785`, train `0.787`
- `a=1.0, b=1.0, c=2.0, d=1.0` -> test `0.783`, train `0.785`
- `a=1.0, b=2.0, c=1.0, d=1.0` -> test `0.782`, train `0.785`

Held-out noise breakdown:
- noise `0.2`: `0.774`
- noise `0.3`: `0.812`
- noise `0.4`: `0.792`
