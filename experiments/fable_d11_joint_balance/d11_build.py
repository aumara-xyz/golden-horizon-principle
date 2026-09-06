"""D11.1: independent rebuild of H = M + beta*I and p at L=7/10, T=120, N=80 per parity, using Fable's own d5 machinery
(certified GL quadrature, elementary Bessel forms, 192-bit balls) -- NOT Opus's builder that D10 used. Exports ball strings."""
import sys, json, hashlib, time
sys.argv=['d5_certify.py','80','48',sys.argv[1],'1']
src=open('/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes/d5_certify.py').read()
cut=src.index("lam0=None; cert=None; statuses={}")
t0=time.time(); exec(src[:cut])
H=[[M[i][j]+(beta if i==j else 0) for j in range(NE)] for i in range(NE)]
out=dict(parity=PAR,N=NE,L='7/10',T=T,prec_bits=192,beta=beta.str(90),p=[v.str(90) for v in p],H=[[v.str(90) for v in r] for r in H],
         max_entry_radius=str(max(v.rad() for r in H for v in r)),builder='fable d5_certify.py machinery (exec up to LDL); independent of opus_d7_rebuild.py',
         build_seconds=time.time()-t0)
s=json.dumps(out,indent=1); open(f'd11_input_{PAR}.json','w').write(s); print(PAR,'built',out['build_seconds'],'s; sha256',hashlib.sha256(s.encode()).hexdigest()[:16],'max rad',out['max_entry_radius'])
