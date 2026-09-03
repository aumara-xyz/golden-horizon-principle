# R5.5a run log

All commands ran in `/private/tmp/aukora-millennium-codex` on macOS arm64. No command read `research/millennium-lab-v1/zeros.txt` or invoked a zeta-zero evaluator.

1. Installed `python-flint==0.8.0`, `mpmath==1.3.0`, and `sympy==1.14.0` into the disposable path `/tmp/codex-r5-python311` under Homebrew Python 3.11. The first attempt to install current python-flint under system Python 3.9 correctly failed its Python-version constraint; `python-flint==0.6.0` was not used for the final certificate.
2. Ran `python3 .../screen_jensen.py --exhaustive-limit 100000 --log-points 768 --output .../screen-results.json`. Exit status: 0. Recorded internal elapsed time: 19.01752495765686 seconds.
3. Ran `PYTHONPATH=/tmp/codex-r5-python311 /opt/homebrew/bin/python3.11 .../certify_jensen.py --digits 70 --output .../certificates.json`. Exit status: 0. Recorded internal elapsed time: 51.91791081428528 seconds.
4. Parsed all 36 interval-certificate rows. Count with classification other than `hyperbolic`: 0. Each row has an exact rational Sturm root count equal to its degree and Hermite inertia `[degree, 0, 0]`.
5. Ran the static forbidden-input audit

   `rg -n "zetazero|zeros\\.txt|14\\.134725|21\\.022039|25\\.010857" screen_jensen.py certify_jensen.py`

   It returned no matches.

The broad screen is nonrigorous wherever its JSON marks binary64 cancellation as indeterminate. The Arb rows are finite certificates only at their listed shifts; they do not fill those gaps.
