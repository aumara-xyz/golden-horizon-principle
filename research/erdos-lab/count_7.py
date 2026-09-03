"""Erdős #7, counting version: minimum number of bare houses u(L) for odd L, one start per odd divisor d>1 of L. MaxSAT (RC2): hard = at-most-one start per brush; soft = each house covered (weight 1). Symmetry: fix the start of brush 3 at house 0 when 3|L (translation)."""
import sys, json, time
from pysat.formula import WCNF
from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2
def divisors(L): return [d for d in range(2,L+1) if L%d==0]
def umin(L, timeout=None):
    ds=divisors(L); var={}; k=0
    for d in ds:
        for r in range(d): k+=1; var[(d,r)]=k
    w=WCNF()
    for d in ds:
        enc=CardEnc.atmost(lits=[var[(d,r)] for r in range(d)],bound=1,top_id=k,encoding=EncType.ladder); k=max(k,enc.nv)
        for c in enc.clauses: w.append(c)
    if L%3==0: w.append([var[(3,0)]])           # translation symmetry: brush 3 starts at house 0
    for n in range(L): w.append([var[(d,n%d)] for d in ds],weight=1)
    t=time.time(); best=None
    with RC2(w, solver="cd15", adapt=True, exhaust=True, minz=True) as rc2:
        m=rc2.compute(); cost=rc2.cost
    chosen=[(d,r) for (d,r),v in var.items() if m[v-1]>0]; covered=set()
    for d,r in chosen: covered.update(range(r,L,d))
    assert L-len(covered)==cost
    return cost, time.time()-t, chosen
if __name__=="__main__":
    if sys.argv[1]=="control":
        print("L=6 brushes 2,3,6 -> bare:", umin(6)[:2]); print("L=12 -> bare:", umin(12)[:2]); sys.exit()
    Ls=[int(a) for a in sys.argv[1].split(",")]; out=[]
    for L in Ls:
        cost,dt,ch=umin(L); s=sum(1/d for d in divisors(L))
        out.append({"L":L,"min_bare":cost,"seconds":round(dt,1),"sum_1_over_d":round(s,4),"brushes_used":len(ch)}); print(f"L={L} min_bare={cost} t={dt:.1f}s sum1/d={s:.3f} used={len(ch)}/{len(divisors(L))}",flush=True)
        json.dump(out,open("r7-count.json","w"),indent=1)
    print("COUNT DONE")
