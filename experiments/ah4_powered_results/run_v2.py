#!/usr/bin/env python3
"""AH4-P1-POWERED v2 runner + analyzer (ADD-only wrapper).

Contract: experiments/AH4_P1_POWERED_PREREG_v2.md (SIGNED 2026-08-01).
Pipeline: experiments/ah4_p1_pipeline.py, byte-locked at SHA-256
59fc150a67971c1a2af65915e2233b681c88f8e3ba4b9fb0147a40da17e2cbc2 —
this wrapper verifies that hash before importing and NEVER edits the file.

SEED INJECTION DISCLOSURE (required by the run order): the pinned pipeline
hardcodes its v1 seeds as the module-level global `SEEDS = tuple(range(1000,
1020))`, which `full_run()` reads at call time.  This wrapper imports the
byte-identical pipeline module and then reassigns the module attribute
`SEEDS = tuple(range(3000, 3400))` (400 fresh seeds, v1 seeds excluded)
before invoking `full_run()`.  No line of the pipeline file is modified;
the injection is an in-memory attribute assignment on the imported module
object only.  Everything else (arms, constants, fractions, modes, channel,
recovery, scorer) runs exactly as pinned.

Analysis (mechanical application of the signed v2 rules):
  - Primary: Delta(f) = median(fib) - median(ising) at constant `uniform`,
    scattered mode, per fraction; 95% CI from 10,000 paired bootstrap
    resamples of the 400 seeds (percentile 2.5/97.5 of the resampled
    median difference).
  - PASS iff Delta(0.50) > +0.02 AND Delta(0.75) > +0.02, each CI
    excluding 0.  KILL otherwise.  f = 0.25 reported, not gating.
  - Secondary (non-gating): trend slope of Delta vs f with bootstrap CI;
    fib-z3 and fib-classical contrasts at uniform/scattered per fraction,
    certified (CI excludes 0) or dissolved.
  - Burst mode: reported, no veto.

The golden ratio appears nowhere in this wrapper; the only sanctioned
appearance remains the Axis-B allocation constant inside the pinned
pipeline (prereg v1 section 1.3).
"""

import hashlib
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE_PATH = os.path.join(HERE, "..", "ah4_p1_pipeline.py")
PINNED_SHA256 = "59fc150a67971c1a2af65915e2233b681c88f8e3ba4b9fb0147a40da17e2cbc2"

V2_SEEDS = tuple(range(3000, 3400))          # 400 fresh seeds, signed
N_BOOT = 10_000                              # paired resamples, signed
MARGIN = 0.02                                # signed PASS margin
BOOT_SEED = 20260801                         # analyzer-only RNG stream
RAW_PATH = os.path.join(HERE, "raw_run_v2.json")
RESULTS_PATH = os.path.join(HERE, "results.json")


def verify_and_import():
    with open(PIPELINE_PATH, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    if digest != PINNED_SHA256:
        raise SystemExit("BLOCKED: pipeline hash mismatch: %s" % digest)
    spec = importlib.util.spec_from_file_location("ah4_p1_pipeline",
                                                  PIPELINE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod):
    # Disclosed injection: module attribute only; file stays byte-identical.
    mod.SEEDS = V2_SEEDS
    mod.full_run(RAW_PATH)
    with open(RAW_PATH) as fh:
        return json.load(fh)


def cell(raw, arm, const, f, mode):
    key = "%s|%s|f%.2f|%s" % (arm, const, f, mode)
    return np.asarray(raw["cells"][key], dtype=np.float64)


def paired_median_diff(a, b, idx):
    """Point estimate and bootstrap distribution of median(a)-median(b)
    under paired resampling (same seed indices for both arms)."""
    point = float(np.median(a) - np.median(b))
    boot = np.median(a[idx], axis=1) - np.median(b[idx], axis=1)
    return point, boot


def ci95(boot):
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return [float(lo), float(hi)]


def slope(fs, ds):
    fs = np.asarray(fs, dtype=np.float64)
    fc = fs - fs.mean()
    return (fc * (ds - np.mean(ds, axis=-1, keepdims=True))).sum(axis=-1) \
        / (fc * fc).sum()


def analyze(raw):
    fractions = raw["fractions"]
    n_seeds = len(raw["seeds"])
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, n_seeds, size=(N_BOOT, n_seeds))

    out = {"test_id": "AH4-P1-POWERED-v2",
           "contract": "experiments/AH4_P1_POWERED_PREREG_v2.md",
           "pipeline_sha256": PINNED_SHA256,
           "seeds": [V2_SEEDS[0], V2_SEEDS[-1]],
           "n_seeds": n_seeds, "n_boot": N_BOOT,
           "primary_constant": "uniform", "primary_mode": "scattered"}

    def contrast_block(arm_b, mode):
        block = {}
        boots = []
        for f in fractions:
            a = cell(raw, "fib", "uniform", f, mode)
            b = cell(raw, arm_b, "uniform", f, mode)
            point, boot = paired_median_diff(a, b, idx)
            block["f%.2f" % f] = {"delta": point, "ci95": ci95(boot),
                                  "ci_excludes_0": bool(
                                      ci95(boot)[0] > 0 or ci95(boot)[1] < 0)}
            boots.append(boot)
        return block, np.stack(boots, axis=1)

    # ---- primary: fib - ising, uniform, scattered
    primary, boot_mat = contrast_block("ising", "scattered")
    out["primary_fib_minus_ising"] = primary

    def gate(f):
        e = primary["f%.2f" % f]
        return e["delta"] > MARGIN and e["ci95"][0] > 0

    p50, p75 = gate(0.50), gate(0.75)
    out["gates"] = {
        "f0.50_pass": p50, "f0.75_pass": p75,
        "rule": "PASS iff Delta(0.50) > +0.02 AND Delta(0.75) > +0.02, "
                "each 95% CI excluding 0; f=0.25 reported not gating"}
    out["verdict"] = "PASS" if (p50 and p75) else "KILL"

    # ---- secondary a: trend slope of Delta vs f
    point_ds = np.array([primary["f%.2f" % f]["delta"] for f in fractions])
    s_point = float(slope(fractions, point_ds))
    s_boot = slope(fractions, boot_mat)
    out["secondary_trend_slope"] = {
        "slope": s_point, "ci95": ci95(s_boot),
        "ci_excludes_0": bool(ci95(s_boot)[0] > 0 or ci95(s_boot)[1] < 0)}

    # ---- secondary b: v1 surprise contrasts at 400 seeds
    for arm_b in ("z3", "classical"):
        block, _ = contrast_block(arm_b, "scattered")
        for f in fractions:
            e = block["f%.2f" % f]
            e["status"] = "certified" if e["ci_excludes_0"] else "dissolved"
        out["secondary_fib_minus_%s" % arm_b] = block

    # ---- burst: reported, no veto
    burst, _ = contrast_block("ising", "burst")
    out["burst_fib_minus_ising"] = burst

    # ---- medians per arm at uniform/scattered, for the record
    out["uniform_scattered_medians"] = {
        arm: {"f%.2f" % f: float(np.median(
            cell(raw, arm, "uniform", f, "scattered")))
            for f in fractions}
        for arm in ("fib", "ising", "z3", "classical")}

    return out


def main():
    mod = verify_and_import()
    raw = run(mod)
    if raw["seeds"] != list(V2_SEEDS):
        raise SystemExit("BLOCKED: raw run does not carry the v2 seeds")
    out = analyze(raw)
    with open(RESULTS_PATH, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("wrote %s" % RESULTS_PATH)
    print("VERDICT: %s" % out["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
