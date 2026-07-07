# TL_phi2 — report (engineering lane; NOT physics evidence)
No result here proves GHP or observer-boundary selection; no ledger status may be upgraded on this basis (master hard rule 7).

**Classification:** KILL-H1 / CONFIRM-H0 (machinery validated; phi INDISTINGUISHABLE / not special — expected outcome)

## 4a machinery-validity gate
- gate passed (all deltas, non-ILL n): **True**
  - phi: PASS (checked n=[2, 3])
  - sqrt2: PASS (checked n=[2])
  - 2cos_pi_7: PASS (checked n=[2, 3, 4, 5])
  - delta2: PASS (checked n=[2, 3, 4, 5, 6, 7, 8])

## 4b phi-distinctiveness (the scientific question)
| delta | index | CQ_score (med log10 cond) | PPQ (max PP_err) |
|---|---|---|---|
| phi | 2.618034 | 18.5264 | 0.000e+00 |
| sqrt2 | 2.000000 | 18.7429 | 1.665e-16 |
| 2cos_pi_7 | 3.246980 | 17.9778 | 2.776e-16 |
| delta2 | 4.000000 | 3.4784 | 2.276e-15 |

- (i) CQ_score(phi) < every control by >=1.0 decade: **False**
- (ii) phi beats nearest-index control 2cos(pi/7) by >=1.0 decade: **False**
- (iii) PPQ(phi) tighter than min control PPQ by >=1 decade: **True**
- Spearman(CQ_score, index) over 4 deltas: **-1.0000** (|rho|>=0.9 => generic/tracks-index kill: True)
- PASS-H1=False  KILL-H1/CONFIRM-H0=True

### Interpretation
- Note on rule (iii): PPQ(phi) reads as 0.0 only because phi's PP_err is computable at just n=2,3 (all n>=4 are ILL/excluded) and comes out bit-exact there, while controls round at the ~1e-16 level. A 0 vs 1e-16 gap is floating-point noise, NOT a real order-of-magnitude PP advantage. Rule (iii) firing True is therefore an artifact; it does not support H1 because PASS-H1 requires (i) AND (ii) AND (iii), and (i)/(ii) both fail decisively. The classification correctly ignores it.
- CQ_score tracks index magnitude with Spearman rho = -1.000: the never-closing control delta=2 (index 4) is by far the BEST conditioned, and the three closing deltas (phi, sqrt2, 2cos(pi/7)) all pile up near log10(cond) ~ 18 at their own closing levels. phi's closing Gram is NOT better conditioned than the controls; it is essentially tied with 2cos(pi/7) (the nearest-index control) and worse than delta=2. This is exactly the expected H0: clean closure and the Pimsner-Popa bound are generic to admissible indices, and the golden ratio is not singled out.
- Circularity check honored: the Jones index phi^2=1+phi and 1/index=2-phi appear only as 4a sanity (PP_numeric recovers delta^-2 exactly); they are definitional and are NOT used as H1 support.

## Per-delta, per-n detail

### phi  (delta=1.6180339887, index=2.618034, 1/index=0.3819660113, closing_l=4)
| n | dim | cond(Gram) | ILL | nullity | degen_JW | PP_num | PP_err | PP_pos_min | MC | IDEM | closing |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 4.236e+00 | False | 0 | False | 0.38196601 | 0.000e+00 | -6.420e-17 | 0.000e+00 | 0.000e+00 | False |
| 3 | 5 | 6.582e+01 | False | 0 | False | 0.38196601 | 0.000e+00 | -2.524e-16 | 1.110e-16 | 4.441e-16 | False |
| 4 | 14 | 2.950e+16 | True | 1 | False | None | nan | nan | 3.500e-16 | 4.441e-16 | True |
| 5 | 42 | 4.398e+17 | True | 8 | True | None | nan | nan | 0.000e+00 | 4.441e-16 | True |
| 6 | 132 | 3.361e+18 | True | 43 | True | None | nan | nan | 0.000e+00 | 4.441e-16 | True |
| 7 | 429 | 1.383e+20 | True | 196 | True | None | nan | nan | 0.000e+00 | 4.441e-16 | True |
| 8 | 1430 | 2.330e+20 | True | 820 | True | None | nan | nan | 0.000e+00 | 4.441e-16 | True |

### sqrt2  (delta=1.4142135624, index=2.000000, 1/index=0.5000000000, closing_l=3)
| n | dim | cond(Gram) | ILL | nullity | degen_JW | PP_num | PP_err | PP_pos_min | MC | IDEM | closing |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 5.828e+00 | False | 0 | False | 0.50000000 | 1.665e-16 | -9.434e-17 | 0.000e+00 | 0.000e+00 | False |
| 3 | 5 | 4.392e+16 | True | 1 | False | None | nan | nan | 9.524e-18 | 0.000e+00 | True |
| 4 | 14 | 4.936e+18 | True | 6 | True | None | nan | nan | 0.000e+00 | 0.000e+00 | True |
| 5 | 42 | 1.778e+18 | True | 26 | True | None | nan | nan | 0.000e+00 | 0.000e+00 | True |
| 6 | 132 | 6.199e+18 | True | 100 | True | None | nan | nan | 0.000e+00 | 0.000e+00 | True |
| 7 | 429 | 5.489e+19 | True | 365 | True | None | nan | nan | 0.000e+00 | 0.000e+00 | True |
| 8 | 1430 | 1.224e+20 | True | 1302 | True | None | nan | nan | 0.000e+00 | 0.000e+00 | True |

### 2cos_pi_7  (delta=1.8019377358, index=3.246980, 1/index=0.3079785284, closing_l=6)
| n | dim | cond(Gram) | ILL | nullity | degen_JW | PP_num | PP_err | PP_pos_min | MC | IDEM | closing |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 3.494e+00 | False | 0 | False | 0.30797853 | 0.000e+00 | 3.753e-18 | 0.000e+00 | 0.000e+00 | False |
| 3 | 5 | 3.014e+01 | False | 0 | False | 0.30797853 | 1.110e-16 | -1.594e-16 | 1.110e-16 | 0.000e+00 | False |
| 4 | 14 | 6.184e+02 | False | 0 | False | 0.30797853 | 1.665e-16 | -2.047e-16 | 8.327e-17 | 0.000e+00 | False |
| 5 | 42 | 3.659e+04 | False | 0 | False | 0.30797853 | 2.776e-16 | -2.807e-15 | 2.776e-16 | 0.000e+00 | False |
| 6 | 132 | 8.326e+17 | True | 1 | False | None | nan | nan | 1.366e-15 | 0.000e+00 | True |
| 7 | 429 | 9.502e+17 | True | 12 | True | None | nan | nan | 0.000e+00 | 0.000e+00 | True |
| 8 | 1430 | 2.530e+19 | True | 89 | True | None | nan | nan | 0.000e+00 | 0.000e+00 | True |

### delta2  (delta=2.0000000000, index=4.000000, 1/index=0.2500000000, closing_l=None)
- note: no closing level observed (Gram never degenerates through N=8): CQ_score uses all n as the structural fallback for a non-closing control (prereg sec 5).
| n | dim | cond(Gram) | ILL | nullity | degen_JW | PP_num | PP_err | PP_pos_min | MC | IDEM | closing |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 3.000e+00 | False | 0 | False | 0.25000000 | 2.776e-17 | -5.776e-19 | 0.000e+00 | 0.000e+00 | False |
| 3 | 5 | 1.811e+01 | False | 0 | False | 0.25000000 | 0.000e+00 | -6.582e-17 | 1.110e-16 | 0.000e+00 | False |
| 4 | 14 | 1.875e+02 | False | 0 | False | 0.25000000 | 1.110e-16 | -1.658e-16 | 5.551e-17 | 0.000e+00 | False |
| 5 | 42 | 3.009e+03 | False | 0 | False | 0.25000000 | 4.718e-16 | -6.071e-16 | 1.110e-16 | 0.000e+00 | False |
| 6 | 132 | 6.967e+04 | False | 0 | False | 0.25000000 | 7.494e-16 | -9.612e-16 | 3.331e-16 | 0.000e+00 | False |
| 7 | 429 | 2.207e+06 | False | 0 | False | 0.25000000 | 1.055e-15 | -1.147e-14 | 1.776e-15 | 0.000e+00 | False |
| 8 | 1430 | 9.180e+07 | False | 0 | False | 0.25000000 | 2.276e-15 | -9.217e-14 | 6.661e-16 | 0.000e+00 | False |

---
Headline: CQ_score  phi=18.526  sqrt2=18.743  2cos(pi/7)=17.978  delta2=3.478  ||  PPQ  phi=0.00e+00  sqrt2=1.67e-16  2cos(pi/7)=2.78e-16  delta2=2.28e-15  ||  Spearman(CQ,index)=-1.000
