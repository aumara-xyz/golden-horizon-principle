# D28 — Court-judged construction-rule loop: results

Frozen judge: `court_frozen_dojo.py` (sha256 6e774a2a3a8215e3a0356deec960c3c09f4868449c8ffd6a14f70fc6d31e63ac),
`court_frozen_score.py` (sha256 baf329e9bf1e23e7b548abff6dd7b1605b839433cc27941dbd12307c3ba26bce);
parameterized driver `court_score.py` (same arithmetic, imports the frozen dojo functions; frozen hashes recorded in every receipt).
Metric: ratio = W_hi(candidate at T=1024, mass-conditioned tail) / ell; gate passes when the certified wave-lower endpoint
ratio W_lo/ell < 1.10 (the tighter lower endpoint decides). Nothing under the court's audited surface changed in this round.

## Task 1 — baseline optimizer (no models)

Rule: minimize the certified upper bound over 80-mode candidates; boundary-constraint families
(value + first k even derivatives vanish at ±L, k in {2,4,6,8}) crossed with a smoothness penalty
(lambda * exact derivative Gram, lambda in {0, 1e-9 ... 1e-5}); selected by the float proxy at T=1024.
The rule that wins: k=2, lambda=1e-6. The optimizer's own number to beat was the D22-rule candidate:
L=0.5 odd gate ratio 1.156 (fail), L=0.4 even 1.105 (fail).

| case | W interval at T=1024 | inf ratio W_hi/ell | gate ratio W_lo/ell | gate | enclosure |
|---|---|---|---|---|---|
| L=0.5 odd (ell=0.000180934196848) | [0.0001955526250550, 0.0001977868435498] | 1.0931 | 1.0808 | **PASS** | 1.14% |
| L=0.4 even (ell=0.000172308870206) | [0.0001825029024695, 0.0001838936940424] | 1.0672 | 1.0592 | **PASS** | 0.76% |

## Task 2 — construction-rule loop

Proposer models edited ONLY `construct_candidate.py`; every call, diff and court receipt is in
`loop-receipts.jsonl`. Loop receipts are court runs at T=160 (the loop instrument, declared); the
metric numbers are T=1024. Incumbent at T=160: odd 1.2662 / even 1.1821. Escalation ladder on two
consecutive non-improvements: deepseek-v4.1-flash -> glm-5.3-flash -> qwen3.8-27b.

| iter | model | action | call | cost | T=160 inf ratios (odd / even) |
|---|---|---|---|---|---|
| 1 | deepseek-v4.1-flash | reject-no-improvement | 374s | $0.0091 | court receipt failed to parse (harness bug, fixed) |
| 2 | deepseek-v4.1-flash | **keep** | 52s | $0.0180 | 1.2508 / 1.1702 |
| 3 | deepseek-v4.1-flash | tombstone (empty reply) | 267s | $0.0060 | — |
| 4 | deepseek-v4.1-flash | reject-no-improvement | 316s | $0.0049 | 1.2509 / 1.1719 |
| 5 | z-ai/glm-5.3-flash | reject-no-improvement | 32s | $0.0020 | 1.2695 / 1.1844 |
| 6 | qwen/qwen3.8-27b | reject-no-improvement | 151s | $0.0136 | 1.2541 / 1.1739 |
| 7 | qwen/qwen3.8-27b | tombstone (empty reply) | 226s | $0.0455 | — |
| 8 | qwen/qwen3.8-27b | **keep** (final) | 138s | $0.0272 | 1.2491 / 1.1703 |

Total OpenRouter spend: $0.126 (loop) + $0.009 (gaming control) = **$0.135 of the $20 cap**.
Winner rule source: `construct_candidate.py` sha256 989be135cfeb1041d476c5e0fa5c8fbc3f9eab2b396e0accada736bc1ba786c3
(also kept as `construct_candidate.winner-iter08.py`); it is the baseline rule with two model-authored
edits kept by the harness (iter 2 deepseek, iter 8 qwen).

Final certified brackets at T=1024 (frozen court):

| case | winner W interval | inf ratio | gate ratio | gate | enclosure |
|---|---|---|---|---|---|
| L=0.5 odd | [0.0001954203563499, 0.0001968939055683] | **1.0882** | **1.0801** | **PASS** | 0.75% |
| L=0.4 even | [0.0001824684360255, 0.0001833825336106] | **1.0643** | **1.0590** | **PASS** | 0.50% |

## Task 3 — controls

- **C1 wrong-L threading.** The L=0.4-even candidate scored under the L=0.5 machinery yields an
  incoherent enclosure W in [3.1937, -0.0415] (W_lo > W_hi; ratios negative/absurd). A wrong-L
  candidate cannot reproduce threading; rejected (`control_task3-receipts.json`).
- **C2 omitted-tail construction.** The pure floor minimizer (k=0, lambda=0) at T=1024:
  W in [0.0001932783770288, 0.0001976886486253], inf ratio 1.0926, gate ratio 1.0682, gate PASSES,
  enclosure **2.28%**. Honest negative result: at T=1024 the mass-conditioned tail is tight enough
  that omitting it from the objective is NOT rejected at the gate for this case; what it loses is
  enclosure width (2.28% vs the winner's 0.75%). The tail term's value here is precision, not pass/fail.
  At T=160 the same candidate's enclosure is 21.3%.
- **C3 gaming proposer.** A model instructed to make the ratio small *by any means* attempted to write
  fake `score.txt` / `ratio.txt` files and overwrite `.py` files. The harness guard tombstoned the
  proposal on static scan; it was never executed (`control_gaming-receipt.json`). The court's
  independent scoring is the second line of defense for construction-only proposals.

## Prediction ledger

Pre-registered (Astra, Task 0): the best rule found brings L=0.4 even under 1.10 and L=0.5 odd under 1.15;
anything better is a favorable miss. Outcome: even 1.0643 (under 1.10), odd 1.0882 (under 1.15; also under
1.10 on the gate ratio 1.0801). Ledger ranges recorded in PREDICTIONS.md: odd 1.05-1.15, even 1.05-1.20 —
both outcomes fall inside, on the favorable side.

## Plain statements

- Both open cases are **closed under the frozen metric at T=1024** by construction-rule candidates:
  L=0.5 odd gate ratio 1.0801, L=0.4 even 1.0590 (both < 1.10); the previously closed L=0.4 odd
  bracket (1.0884, D27) is unchanged.
- This is a candidate construction result against a fixed judge. It is not a proof of RH, and the loop
  did not "improve itself": it improved a candidate's certified number against a frozen evaluator.
- Which was model-authored: iterations 1-8 proposals are model-authored (deepseek, glm, qwen);
  the baseline rule and the constraint/penalty families are optimizer-authored (no model involved);
  the two kept edits (iter 2, iter 8) are model-authored. The final rule is baseline + those two edits.
- Cost accounting: ~17 court-minutes total (baseline 5.8, loop receipts 1.8, final certifications 6.0,
  controls 3.4) against the 45-minute cap; $0.135 of $20; loop wall time ~35 min against the 90-minute cap.
- Harness caveats recorded: two restart cycles fixed (receipt durability on early exits, parse-validated
  code extraction, credential parsing, Arb interval parsing); one truncated reply per pre-fix era was
  tombstoned and re-proposed. The near-miss check that the even-case bracket may have used the wrong
  floor was resolved by the bracket's own `note` field: the in-run correction was present; no D27 number
  changes.

## Correction (appended 2026-09-14, per D29; nothing above edited)
The gate definition in the D28 tables used W_lo/ell. The infimum bracket is [ell, W_hi], so the gate
must use **W_hi/ell**; the W_lo column is not a bound on the infimum and is not the gate. Restated on
the corrected criterion, all three closures stand: L=0.4 odd 1.0884, L=0.5 odd 1.0882, L=0.4 even
1.0643, all < 1.10. D29 reproduced all three digit-for-digit on a second machine (arm64 Mac) from the
frozen court and candidates. CONVENTIONS.md now carries the gate rule.

## Task 3 addendum (appended, per D29 gate correction)
The Task 3 control C2 verdict (floor-only not gate-rejected) was stated on the W_lo criterion; under
the corrected criterion its inf ratio is 1.0926 (also a pass), enclosure 2.28 percent. The qualitative
finding (tail value = precision, not pass/fail, at T=1024 for this case) is unchanged.
