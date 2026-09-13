"""D22: parameterized certified R_{L,T} lower bound (all functions) — Fable's d5_certify.py machinery with L, T, NE, parity from argv.
Produces d22_cert_{parity}_L{L}_T{T}_N{NE}.json including the frozen eigenbasis minimizer (40 digits) for exact scoring."""
import sys, re, time
LSTR, TVAL, NE_, KN, PAR = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
src=open('/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes/d5_certify.py').read()
src=src.replace("L=arb('7/10'); T=120;", f"L=arb('{LSTR}'); T={TVAL};")
src=re.sub(r"for k in \(12,13,14,15,16,17,18\):\n.*?\n.*?\n", "", src, flags=re.S)   # drop the interval-LDL loop (cond ~1e14; not used)
src=src.replace("r0=ldl(A,'0')", "r0={'positive':None}")
src=src.replace('out={"run":5,', 'out={"run":22,"L":LSTR,"T":TVAL,"minimizer_frozen_40dig":[mp.nstr(Vmp[i,0],40) for i in range(NE)],"modes":[int(n) for n in ns],')
src=src.replace('open(f"d5_results_{PAR}_NE{NE}_pole{POLE:+d}.json","w")', 'open(f"d22_cert_{PAR}_L{LSTR}_T{TVAL}_N{NE}.json","w")')
sys.argv=['d5_certify.py', str(NE_), str(KN), PAR, '1']
t0=time.time(); exec(src); print('CERT DONE', PAR, LSTR, TVAL, NE_, round(time.time()-t0), 's', flush=True)
