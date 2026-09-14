#!/usr/bin/env python3
"""Verify the D25 Stage-C bracket claim for cand2 odd L=0.4, T=256."""
import json, sys
sys.path.insert(0, '/Users/peterviviani/golden-horizon-principle/experiments/riemann_dojo')
from dojo_court import evaluate_wave

cand = json.load(open('/Users/peterviviani/golden-horizon-principle/experiments/fable_d22_test2/d22_cand2_odd_L0.4.json'))
modes = cand['modes']
coeffs = [str(c) for c in cand['minimizer_frozen_40dig']]
print(f"modes: {len(modes)} from {modes[:4]}... to {modes[-2:]}", flush=True)
receipt = evaluate_wave('0.4', 'odd', modes, coeffs, T_cutoff=256)
print(json.dumps(receipt, indent=1))
