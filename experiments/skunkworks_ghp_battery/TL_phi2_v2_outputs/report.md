# TL_phi2_v2 — report (engineering lane; NOT physics evidence)
No result here proves GHP or observer-boundary selection; no ledger status may be upgraded on this basis (master hard rule 7).

**v2 fix:** v1's CQ_score measured cond(Gram) at closing levels — i.e. floating-point roundoff on a STRUCTURALLY-ZERO eigenvalue (every closing Gram is ILL, cond ~1e16-1e20), carrying no signal. v2 replaces it with a well-posed closure error: the operator-norm distance from the built E to the analytically-known Jones/Markov E, plus finite E residuals, plus a robust ABSOLUTE-tol rank test vs the JW-predicted truncation dimension. No division by / conditioning on a zero eigenvalue.

**Classification:** KILL-H1 / CONFIRM-H0 (machinery validated; phi INDISTINGUISHABLE / not special — expected outcome)

## 4a machinery-validity gate
- gate passed (all deltas, non-ILL n): **True**
  - phi: PASS (checked n=[2, 3])
  - sqrt2: PASS (checked n=[2])
  - 2cos_pi_7: PASS (checked n=[2, 3, 4, 5])
  - delta2: PASS (checked n=[2, 3, 4, 5, 6, 7])

## Robustness guard: well-posed rank test vs JW-predicted truncation
- rank test matches JW/Bratteli semisimple dim for every delta/n: **True**  (per-delta total mismatch: {'phi': 0, 'sqrt2': 0, '2cos_pi_7': 0, 'delta2': 0})
  This is option (c) of the fix: numeric negligible-ideal dimension (Gram eigenvalues below a FIXED absolute tol 1e-9, well-separated from the smallest genuine eigenvalue by the reported spectral gap) equals the analytic A_{l-1} truncated path count. A real, well-posed discriminator.

## 4b phi-distinctiveness (the scientific question)
| delta | index | CQ_score (med log10 closure_err; LOWER=cleaner) | worst closure_err | PPQ (max PP_err) |
|---|---|---|---|---|
| phi | 2.618034 | -15.2165 | 7.022e-16 | 0.000e+00 |
| sqrt2 | 2.000000 | -18.0000 | 0.000e+00 | 1.665e-16 |
| 2cos_pi_7 | 3.246980 | -18.0000 | 0.000e+00 | 2.776e-16 |
| delta2 | 4.000000 | -18.0000 | 0.000e+00 | 1.055e-15 |

- (i) CQ_score(phi) < every control by >=1.0 decade: **False**
- (ii) phi beats nearest-index control 2cos(pi/7) by >=1.0 decade: **False**
- (iii) PPQ(phi) tighter than min control PPQ by >=1 decade: **True**
- Spearman(CQ_score, index) over 4 deltas: **0.4000** (|rho|>=0.9 => generic/tracks-index kill: False)
- PASS-H1=False  KILL-H1/CONFIRM-H0=True

### Interpretation
- The well-posed closure error is at machine epsilon (<=~7e-16, i.e. a bit-exact E) for ALL four deltas at EVERY level, closing or not: the built E matches the analytic Jones/Markov E to full float precision regardless of index. The v1 'phi=18.5 vs sqrt2=18.7' spread has evaporated because it was roundoff on a structurally-zero eigenvalue, not a real closure difference. This is exactly the expected H0: clean closure and the Pimsner-Popa bound are generic to admissible indices; the golden ratio is not singled out.
- READABILITY CAVEAT (do NOT misread the CQ column): the ONLY nonzero component anywhere is phi's bimodule residual, ~5e-16..7e-16 (a few ulps, growing slowly with matrix dimension from accumulated float ops), while the three controls happen to land bit-exactly on 0. That is why phi's CQ_score (~-15) looks 'worse' than the controls (floored at -18 = log10(1e-18)). This -15-vs--18 gap is the SAME category of floating-point noise the v1 verifier flagged (a 0-vs-1e-16 non-difference), NOT a real phi disadvantage, and it points the WRONG way for H1 anyway. The KILL fires correctly and for the right reason (H1 needs phi to close >=1 decade CLEANER than every control; it does not — the controls tie-or-beat it at the epsilon floor).
- The robust rank test independently confirms the machinery is CORRECT (it reproduces the exact JW/Bratteli truncation dimension for every delta and n), so the null is a validated null, not a broken-code artifact.
- Circularity check honored: the Jones index phi^2=1+phi and 1/index=2-phi appear only as 4a sanity (PP_numeric recovers delta^-2 exactly) and as the analytic constant delta^-1 in the exact-E reference; they are definitional and are NOT used as H1 support.

## Per-delta, per-n detail

### phi  (delta=1.6180339887, index=2.618034, 1/index=0.3819660113, closing_l=4, l_param=5)
| n | dim | rank_num | JW_rank | rank_mis | nullity | spec_gap | closure_err | cond(Gram) | ILL | PP_num | PP_err | MC | IDEM | closing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 2 | 2 | 0 | 0 | inf | 0.00e+00 | 4.24e+00 | False | 0.38196601 | 0.00e+00 | 0.00e+00 | 0.00e+00 | False |
| 3 | 5 | 5 | 5 | 0 | 0 | inf | 5.44e-16 | 6.58e+01 | False | 0.38196601 | 0.00e+00 | 1.11e-16 | 4.44e-16 | False |
| 4 | 14 | 13 | 13 | 0 | 1 | 4.8e+15 | 5.87e-16 | 2.95e+16 | True | None | nan | 3.50e-16 | 4.44e-16 | True |
| 5 | 42 | 34 | 34 | 0 | 8 | 4.0e+13 | 6.28e-16 | 4.40e+17 | True | None | nan | 0.00e+00 | 4.44e-16 | True |
| 6 | 132 | 89 | 89 | 0 | 43 | 3.6e+12 | 6.66e-16 | 3.36e+18 | True | None | nan | 0.00e+00 | 4.44e-16 | True |
| 7 | 429 | 233 | 233 | 0 | 196 | 9.1e+11 | 7.02e-16 | 1.38e+20 | True | None | nan | 0.00e+00 | 4.44e-16 | True |

### sqrt2  (delta=1.4142135624, index=2.000000, 1/index=0.5000000000, closing_l=3, l_param=4)
| n | dim | rank_num | JW_rank | rank_mis | nullity | spec_gap | closure_err | cond(Gram) | ILL | PP_num | PP_err | MC | IDEM | closing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 2 | 2 | 0 | 0 | inf | 0.00e+00 | 5.83e+00 | False | 0.50000000 | 1.67e-16 | 0.00e+00 | 0.00e+00 | False |
| 3 | 5 | 4 | 4 | 0 | 1 | 3.4e+15 | 0.00e+00 | 4.39e+16 | True | None | nan | 9.52e-18 | 0.00e+00 | True |
| 4 | 14 | 8 | 8 | 0 | 6 | 2.5e+14 | 0.00e+00 | 4.94e+18 | True | None | nan | 0.00e+00 | 0.00e+00 | True |
| 5 | 42 | 16 | 16 | 0 | 26 | 1.7e+14 | 0.00e+00 | 1.78e+18 | True | None | nan | 0.00e+00 | 0.00e+00 | True |
| 6 | 132 | 32 | 32 | 0 | 100 | 4.1e+13 | 0.00e+00 | 6.20e+18 | True | None | nan | 0.00e+00 | 0.00e+00 | True |
| 7 | 429 | 64 | 64 | 0 | 365 | 1.9e+13 | 0.00e+00 | 5.49e+19 | True | None | nan | 0.00e+00 | 0.00e+00 | True |

### 2cos_pi_7  (delta=1.8019377358, index=3.246980, 1/index=0.3079785284, closing_l=6, l_param=7)
| n | dim | rank_num | JW_rank | rank_mis | nullity | spec_gap | closure_err | cond(Gram) | ILL | PP_num | PP_err | MC | IDEM | closing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 2 | 2 | 0 | 0 | inf | 0.00e+00 | 3.49e+00 | False | 0.30797853 | 0.00e+00 | 0.00e+00 | 0.00e+00 | False |
| 3 | 5 | 5 | 5 | 0 | 0 | inf | 0.00e+00 | 3.01e+01 | False | 0.30797853 | 1.11e-16 | 1.11e-16 | 0.00e+00 | False |
| 4 | 14 | 14 | 14 | 0 | 0 | inf | 0.00e+00 | 6.18e+02 | False | 0.30797853 | 1.67e-16 | 8.33e-17 | 0.00e+00 | False |
| 5 | 42 | 42 | 42 | 0 | 0 | inf | 0.00e+00 | 3.66e+04 | False | 0.30797853 | 2.78e-16 | 2.78e-16 | 0.00e+00 | False |
| 6 | 132 | 131 | 131 | 0 | 1 | 6.9e+11 | 0.00e+00 | 8.33e+17 | True | None | nan | 1.37e-15 | 0.00e+00 | True |
| 7 | 429 | 417 | 417 | 0 | 12 | 1.6e+11 | 0.00e+00 | 9.50e+17 | True | None | nan | 0.00e+00 | 0.00e+00 | True |

### delta2  (delta=2.0000000000, index=4.000000, 1/index=0.2500000000, closing_l=None, l_param=None)
| n | dim | rank_num | JW_rank | rank_mis | nullity | spec_gap | closure_err | cond(Gram) | ILL | PP_num | PP_err | MC | IDEM | closing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 2 | 2 | 0 | 0 | inf | 0.00e+00 | 3.00e+00 | False | 0.25000000 | 2.78e-17 | 0.00e+00 | 0.00e+00 | False |
| 3 | 5 | 5 | 5 | 0 | 0 | inf | 0.00e+00 | 1.81e+01 | False | 0.25000000 | 0.00e+00 | 1.11e-16 | 0.00e+00 | False |
| 4 | 14 | 14 | 14 | 0 | 0 | inf | 0.00e+00 | 1.87e+02 | False | 0.25000000 | 1.11e-16 | 5.55e-17 | 0.00e+00 | False |
| 5 | 42 | 42 | 42 | 0 | 0 | inf | 0.00e+00 | 3.01e+03 | False | 0.25000000 | 4.72e-16 | 1.11e-16 | 0.00e+00 | False |
| 6 | 132 | 132 | 132 | 0 | 0 | inf | 0.00e+00 | 6.97e+04 | False | 0.25000000 | 7.49e-16 | 3.33e-16 | 0.00e+00 | False |
| 7 | 429 | 429 | 429 | 0 | 0 | inf | 0.00e+00 | 2.21e+06 | False | 0.25000000 | 1.05e-15 | 1.78e-15 | 0.00e+00 | False |

---
Headline: CQ_score(med log10 closure_err; lower=cleaner)  phi=-15.217  sqrt2=-18.000  2cos(pi/7)=-18.000  delta2=-18.000  ||  PPQ  phi=0.00e+00  sqrt2=1.67e-16  2cos(pi/7)=2.78e-16  delta2=1.05e-15  ||  Spearman(CQ,index)=0.400  ||  rank_test_clean=True
