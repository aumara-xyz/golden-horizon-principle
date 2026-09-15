"""Visible-shift certified floor: d22_certify.py machinery with the prime set filtered to log n < 2L. argv: L T NE K parity"""
import sys, re, time
LSTR, TVAL, NE_, KN, PAR = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
src=open('/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes/d5_certify.py').read()
src=src.replace("L=arb('7/10'); T=120;", f"L=arb('{LSTR}'); T={TVAL};")
PREC=int(__import__("os").environ.get("PREC","192")); src=src.replace("ctx.prec=192", f"ctx.prec={PREC}"); assert f"ctx.prec={PREC}" in src
# visible-shift filter (D24 §4.1): keep only shifts u < 2L (touching endpoint has zero overlap)
src=src.replace("B=sum((w for _,w in pp),arb(0))", "pp=[(u,w) for (u,w) in pp]  # D34 CONTROL: deliberately WRONG set (keeps invisible shifts)\nB=sum((w for _,w in pp),arb(0))")
src=re.sub(r"for k in \(12,13,14,15,16,17,18\):\n.*?\n.*?\n", "", src, flags=re.S)
src=src.replace("r0=ldl(A,'0')", "r0={'positive':None}")
src=src.replace('out={"run":5,', 'out={"run":30,"L":LSTR,"T":TVAL,"visible_shifts":"CONTROL_WRONG_SET_ALL_SHIFTS","B_visible":B.str(15),"max_quadrature_error_bound_q":str(maxq),"minimizer_frozen_40dig":[mp.nstr(Vmp[i,0],40) for i in range(NE)],"modes":[int(n) for n in ns],')
src=src.replace('open(f"d5_results_{PAR}_NE{NE}_pole{POLE:+d}.json","w")', 'open(f"/Users/peterviviani/golden-horizon-principle/experiments/deepseek_d34_floor_axis/control_wrongset_cert_{PAR}_L{LSTR}_T{TVAL}_N{NE}.json","w")')
assert src.count("u < 2*L")==0  # D34 control: filter deliberately removed
sys.argv=['d5_certify.py', str(NE_), str(KN), PAR, '1']
t0=time.time(); exec(src); print('CERT DONE', PAR, LSTR, TVAL, NE_, 'visible', [str(u)[:6] for u,_ in pp], round(time.time()-t0), 's', flush=True)
