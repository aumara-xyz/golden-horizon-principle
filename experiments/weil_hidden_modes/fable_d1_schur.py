"""D1: mode-index block splitting diagnostic on Codex's sine-basis Weil matrix, N=48. Uses Codex's certify.py functions unmodified."""
import sys, json, time
sys.path.insert(0,"/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes")
from flint import arb, ctx
from certify import archimedean, corr, prime_terms
import mpmath as mp
t0=time.time(); ctx.prec=160; L,N,eps=arb('7/10'),48,arb('1e-25')
arch,cutoff=archimedean(L,N,eps,tolerance='1e-20')
w=[r.copy() for r in arch]
for u,weight in prime_terms(L,arb(1)):
    for i in range(1,N+1):
        for j in range(i,N+1):
            w[i-1][j-1]-=weight*corr(i,j,u,L); w[j-1][i-1]=w[i-1][j-1]
mp.mp.dps=45
W=mp.matrix([[mp.mpf(w[i][j].mid().str(45,radius=False)) for j in range(N)] for i in range(N)])
out={"N":N,"prec_bits":160,"max_entry_radius":str(max(v.rad() for r in w for v in r)),"build_s":time.time()-t0}
for parity,label in [(0,"even"),(1,"odd")]:
    ids=list(range(parity,N,2)); low=[i for i in ids if i<32]; high=[i for i in ids if i>=32]
    sub=lambda I,J: mp.matrix([[W[i,j] for j in J] for i in I])
    A,D,C,Full=sub(low,low),sub(high,high),sub(low,high),sub(ids,ids)
    eA,vA=mp.eigsy(A); eD=mp.eigsy(D)[0]; eF=mp.eigsy(Full)[0]
    iA=min(range(len(low)),key=lambda k:eA[k]); xi=vA[:,iA]
    Cx=C.T*xi; k=(Cx.T*(D**-1)*Cx)[0]
    Cn=mp.sqrt(mp.fsum(C[i,j]**2 for i in range(C.rows) for j in range(C.cols)))
    out[label]={"lambda_min_A(1..32)":mp.nstr(min(eA),8),"lambda_min_D(33..48)":mp.nstr(min(eD),8),"lambda_min_full48":mp.nstr(min(eF),8),
        "||C||_F":mp.nstr(Cn,6),"naive_schur_ok(||C||^2<lminA*lminD)":bool(Cn**2<min(eA)*min(eD)),"coupling_energy_k_along_xi":mp.nstr(k,8),"k_over_lambda_min_A":mp.nstr(k/min(eA),6),
        "second_A":mp.nstr(sorted(eA)[1],6)}
    print(label,out[label],flush=True)
json.dump(out,open("d1_results.json","w"),indent=1); print("D1 DONE",time.time()-t0)
