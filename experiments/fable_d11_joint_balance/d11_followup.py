"""D11.3 follow-ups for the authentic successes: (a) re-certify the SAME frozen x_32 at doubled ball precision (512 bits), same delta
recipe, same order; (b) N=40 replay: principal 40x40 block of my H and p[:40], same Krylov recipe, frozen orders, first certified order."""
import sys, json
from flint import arb, arb_mat, ctx
import d11_krylov as K
par=sys.argv[1]; res=json.load(open(f'd11_results_{par}.json')); mine=json.load(open(f'd11_input_{par}.json'))
kappa=arb(2 if par=='even' else -2); out={}
auth=[r for r in res['rows'] if r['label'].startswith('AUTHENTIC')][0]
succ=[(m,br) for m,br in auth['orders'].items() if br['verdict']=='CERTIFIED sigma>0']
if succ:
    m,br=succ[0]; xs=br['frozen_x_m']
    ctx.prec=512
    H=K.mat(mine['H']); p=[arb(s) for s in mine['p']]; U,a,b,C,np2=K.householder(H,p); cert=K.certify(C)
    br2,_=K.bracket(a,b,C,kappa,np2,xs,cert['delta'])
    out['doubled_precision']=dict(order=m,prec_bits=512,delta=cert['delta'].str(12),bracket=br2,same_vector=True)
    print(par,'doubled precision m=',m,br2['verdict'],br2['sigma_lower'],br2['sigma_upper'],flush=True)
    ctx.prec=256
H40=arb_mat([[arb(mine['H'][i][j]) for j in range(40)] for i in range(40)]); p40=[arb(s) for s in mine['p'][:40]]
row=K.run_family('N=40 replay (principal block of my H)',H40,p40,kappa)
out['N40_replay']=row; print(par,'N=40 first verdicts',{m:b['verdict'] for m,b in row['orders'].items()},flush=True)
json.dump(out,open(f'd11_followup_{par}.json','w'),indent=1)
