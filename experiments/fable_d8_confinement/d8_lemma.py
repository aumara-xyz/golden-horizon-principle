"""D8 steps 2-3: truncated-translation lemma controls and prime-sum bounds. numpy/scipy, floating (not a certificate)."""
import numpy as np, json, math
from scipy.linalg import eigh
def primes_powers(L):
    out=[]
    for p in (2,3,5,7,11,13):
        k=1
        while k*math.log(p)<=2*L: out.append((p,k,k*math.log(p),2*math.log(p)/p**(k/2))); k+=1
    return out
def lemma(a,L): N=math.ceil(2*L/a-1e-15) if a<2*L else 1; return math.cos(math.pi/(N+1)),N
res={}
# C1 path matrix
c1={}
for N in range(1,13):
    P=np.diag(np.ones(N-1),1)+np.diag(np.ones(N-1),-1) if N>1 else np.zeros((1,1))
    c1[N]=float(abs(eigh(P,eigvals_only=True)[-1]-2*math.cos(math.pi/(N+1))))
res['C1_path_eig_err']=c1
# grid operator: cells h=2L/M, shift by k cells (zero padding) ; symmetric part
def shift_sym(M,k,periodic=False):
    S=np.zeros((M,M))
    for i in range(M):
        j=i+k
        if j<M: S[i,j]+=0.5; S[j,i]+=0.5
        elif periodic: S[i,j%M]+=0.5; S[j%M,i]+=0.5
    return S
def top(S): return float(eigh(S,eigvals_only=True)[-1])
# C4 single-shift grid vs lemma, C2 periodic, C3 enlargement
c4=[]; M=1400
for L in (0.4,0.7,0.8,1.0):
    h=2*L/M
    for p,k,a,w in primes_powers(L):
        kc=round(a/h); a_eff=kc*h; lem,N=lemma(a_eff,L)
        c4.append(dict(L=L,n=p**k,a=a,a_grid=a_eff,N=N,lemma=lem,grid_top=top(shift_sym(M,kc)),periodic_top=top(shift_sym(M,kc,True))))
res['C4_single_shift_grid_vs_lemma']=c4
res['C3_enlargement']=[dict(L=L,N=lemma(math.log(2),L)[1],loss=1-lemma(math.log(2),L)[0],approx=math.pi**2/(2*(lemma(math.log(2),L)[1]+1)**2)) for L in (0.4,0.7,1.0,2.0,4.0,8.0)]
# Step 3: c_L, B_L, joint sup on grid (authentic; shifts rounded to grid), perturbations, periodic
tab={}
for L in (0.4,0.7,0.8,1.0):
    h=2*L/M; pp=primes_powers(L); B=sum(w for *_,w in pp); c=sum(w*lemma(a,L)[0] for _,_,a,w in pp)
    def joint(scale,periodic=False):
        S=sum(w*shift_sym(M,round(scale*a/h),periodic) for _,_,a,w in pp); return top(S)
    cpert={s:sum(w*lemma(s*a,L)[0] for _,_,a,w in pp) for s in (0.9,1.1)}
    tab[L]=dict(prime_powers=[p**k for p,k,_,_ in pp],B=B,c_single=c,ratio=c/B,joint_grid=joint(1.0),joint_grid_scaled09=joint(0.9),joint_grid_scaled11=joint(1.1),
                c_single_scaled09=cpert[0.9],c_single_scaled11=cpert[1.1],periodic_joint=joint(1.0,True),
                T_env_B=2*math.pi*math.exp(B),T_env_c=2*math.pi*math.exp(c))
    print(L,{k:(round(v,5) if isinstance(v,float) else v) for k,v in tab[L].items()},flush=True)
res['step3']=tab
json.dump(res,open('d8_lemma_results.json','w'),indent=1)
