import sys, json, time, math
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
def divisors(L):
    return [d for d in range(2,L+1) if L%d==0]
def sigma(n): return sum(d for d in range(1,n+1) if n%d==0)
def build(L):
    ds=divisors(L); var={}; k=0
    for d in ds:
        for r in range(d): k+=1; var[(d,r)]=k
    clauses=[]
    for d in ds:
        lits=[var[(d,r)] for r in range(d)]
        enc=CardEnc.atmost(lits=lits,bound=1,top_id=k,encoding=EncType.ladder); clauses.extend(enc.clauses); k=max(k,enc.nv)
    for n in range(L):
        clauses.append([var[(d,n%d)] for d in ds])
    return var,clauses,k
def solve(L,timeout):
    var,clauses,k=build(L); s=Cadical153(bootstrap_with=clauses); t=time.time()
    # crude timeout via propagation budget loop
    res=s.solve(); dt=time.time()-t
    model=s.get_model() if res else None; s.delete()
    if res:
        chosen=[(d,r) for (d,r),v in var.items() if model[v-1]>0]
        covered=set();
        for d,r in chosen: covered.update(range(r,L,d))
        assert len(covered)==L, "SAT model failed exact check"
        return True,dt,chosen
    return False,dt,None
if __name__=="__main__":
    mode=sys.argv[1]
    if mode=="control":
        ok,dt,ch=solve(12,60); print("control L=12 SAT:",ok,ch); sys.exit(0)
    Lmax=int(sys.argv[2]); out=[]; t0=time.time()
    sig=[0]*(Lmax+1)
    for d in range(1,Lmax+1):
        for m in range(d,Lmax+1,d): sig[m]+=d
    for L in range(3,Lmax+1,2):
        if sig[L]<2*L: continue
        if L%9 and L%15: continue
        sat,dt,ch=solve(L,300); harmonic=sum(1/d for d in divisors(L))
        out.append({"L":L,"sat":sat,"seconds":round(dt,2),"sum_1_over_d":round(harmonic,4),"n_divisors":len(divisors(L))})
        print(f"L={L} sat={sat} t={dt:.1f}s sum1/d={harmonic:.3f} ndiv={len(divisors(L))}",flush=True)
        if sat: print("!!! SAT FOUND",ch,flush=True); break
        json.dump(out,open("r7-scan.json","w"),indent=1)
    print("SCAN DONE",time.time()-t0)
