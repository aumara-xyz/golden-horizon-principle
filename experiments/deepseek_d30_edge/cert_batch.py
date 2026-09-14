#!/usr/bin/env python3
"""D30 Task 1: visible-form all-function floor certifications.

Replicates the D26/D27 patch procedure on weil_hidden_modes/d5_certify.py at MODULE
level (the exec-in-function form was the harness bug fixed here): L and T patched from
the source defaults, the (12..18) derivative loop dropped and the LDL check skipped
(the D24-repaired allowance), prime shifts restricted to the VISIBLE set, output JSON
lands in certs/. Every patch is asserted so a missed replacement fails loud.

Usage: python3 cert_batch.py <parity> <L> <T> <NE>
"""
import re, sys, time
from pathlib import Path

HERE = Path(__file__).parent
SRC = Path('/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes/d5_certify.py')
CERT_DIR = HERE / 'certs'

parity, LSTR, T, NE = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
TVAL = T
KN = 64

CERT_DIR.mkdir(exist_ok=True)
src = SRC.read_text()
needle = "L=arb('7/10'); T=120;"
assert needle in src, 'L/T needle missing'
src = src.replace(needle, f"L=arb('{LSTR}'); T={TVAL};")
src2 = re.sub(r"for k in \(12,13,14,15,16,17,18\):\n.*?\n.*?\n", "", src, flags=re.S)
assert src2 != src, 'k-loop needle missing'
src = src2
needle = "r0=ldl(A,'0')"
assert needle in src, 'ldl needle missing'
src = src.replace(needle, "r0={'positive':None}")
orig_pp = ("pp=[(arb(2).log(),2*arb(2).log()/arb(2).sqrt()),"
           "(arb(3).log(),2*arb(3).log()/arb(3).sqrt()),"
           "(2*arb(2).log(),2*arb(2).log()/2)]")
assert orig_pp in src, 'prime-list needle missing'
# VISIBLE SET per CONVENTIONS: shift u = log n is visible iff u < 2L.
import math
t1 = '(arb(2).log(),2*arb(2).log()/arb(2).sqrt())'
t2 = '(arb(3).log(),2*arb(3).log()/arb(3).sqrt())'
t3 = '(2*arb(2).log(),2*arb(2).log()/2)'
Lf = float(LSTR)
vis = [t1]
if math.log(3) < 2 * Lf: vis.append(t2)
if 2 * math.log(2) < 2 * Lf: vis.append(t3)
assert float(LSTR) in (0.4, 0.5, 0.6, 0.7)
src = src.replace(orig_pp, 'pp=[' + ','.join(vis) + ']  # D30: visible primes for L=' + LSTR)
print(f'[visible set] L={LSTR}: {len(vis)} shift(s): ' + ', '.join(['log2','log3','log4'][:len(vis)]), flush=True)
outname = f"d30_cert_visible_{parity}_L{LSTR}_T{TVAL}_N{NE}.json"
needle = 'open(f"d5_results_{PAR}_NE{NE}_pole{POLE:+d}.json","w")'
assert needle in src, 'out-path needle missing'
src = src.replace(needle, f'open(r"{CERT_DIR / outname}","w")')
needle = 'out={"run":5,'
assert needle in src, 'out-init needle missing'
src = src.replace(needle, ('out={"run":30,"L":LSTR,"T":TVAL,"visible_primes_only":True,'
                           '"minimizer_frozen_40dig":[mp.nstr(Vmp[i,0],40) for i in range(NE)],'
                           '"modes":[int(n) for n in ns],'))
sys.argv = ['d5_certify.py', str(NE), str(KN), parity, '1']
t0 = time.time()
exec(compile(src, f'd5_certify_patched_{parity}_{LSTR}_T{TVAL}', 'exec'))
print(f'VISIBLE CERT DONE {parity} L={LSTR} T={TVAL} N={NE} in {round(time.time()-t0)}s', flush=True)
