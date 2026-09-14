#!/usr/bin/env python3
"""D26 Task 1: run the D22 certify machinery (d5_certify.py text-patched) with
the VISIBLE prime set only for L=0.4 odd, T=160, N=160, K=64.

Nothing in fable_d22_test2/ or weil_hidden_modes/ is edited: the source is read,
patched in memory, and executed with argv; output lands in this directory.
"""
import sys, re, time
sys.path.insert(0, '/Users/peterviviani/golden-horizon-principle/experiments/fable_d22_test2')

LSTR, TVAL, NE_, KN, PAR = '0.4', 160, 160, 64, 'even'
src = open('/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes/d5_certify.py').read()
src = src.replace("L=arb('7/10'); T=120;", f"L=arb('{LSTR}'); T={TVAL};")
src = re.sub(r"for k in \(12,13,14,15,16,17,18\):\n.*?\n.*?\n", "", src, flags=re.S)
src = src.replace("r0=ldl(A,'0')", "r0={'positive':None}")
# VISIBLE PRIMES ONLY (D26 Task 1): drop n=3 and n=4 from the hardcoded list
src = src.replace(
    "pp=[(arb(2).log(),2*arb(2).log()/arb(2).sqrt()),(arb(3).log(),2*arb(3).log()/arb(3).sqrt()),(2*arb(2).log(),2*arb(2).log()/2)]",
    "pp=[(arb(2).log(),2*arb(2).log()/arb(2).sqrt())]  # D26: visible primes only")
src = src.replace('out={"run":5,', 'out={"run":26,"L":LSTR,"T":TVAL,"visible_primes_only":True,"minimizer_frozen_40dig":[mp.nstr(Vmp[i,0],40) for i in range(NE)],"modes":[int(n) for n in ns],')
src = src.replace('open(f"d5_results_{PAR}_NE{NE}_pole{POLE:+d}.json","w")',
                  'open(f"/Users/peterviviani/golden-horizon-principle/experiments/deepseek_d26_bracket/d27_cert_visible_evenL04_{PAR}_L{LSTR}_T{TVAL}_N{NE}.json","w")')
sys.argv = ['d5_certify.py', str(NE_), str(KN), PAR, '1']
t0 = time.time()
exec(src)
print('VISIBLE CERT DONE', PAR, LSTR, TVAL, NE_, round(time.time() - t0), 's', flush=True)
