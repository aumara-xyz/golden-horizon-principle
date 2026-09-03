"""Erdős #7 fast scorer: best-found bare-house count for odd L (UPPER bound on the true minimum u(L)).
Greedy (largest brushes first? no: smallest steps paint most) + simulated annealing on starts. Deterministic seed."""
import sys, json, time, random, math
def divisors(L): return [d for d in range(2,L+1) if L%d==0]
def score(L, ds, starts):
    cov=bytearray(L)
    for d,r in zip(ds,starts):
        if r<0: continue
        for n in range(r,L,d): cov[n]=1
    return L-sum(cov)
def best_bare(L, iters=200000, seed=1, restarts=4):
    ds=divisors(L); rng=random.Random(seed); best=(L,None)
    for rs in range(restarts):
        # greedy: brushes in increasing step; each picks the start covering the most uncovered
        cov=bytearray(L); starts=[]
        for d in ds:
            bestr,bestgain=-1,0
            for r in range(d):
                g=sum(1 for n in range(r,L,d) if not cov[n])
                if g>bestgain: bestr,bestgain=r,g
            starts.append(bestr)
            if bestr>=0:
                for n in range(bestr,L,d): cov[n]=1
        cur=score(L,ds,starts); T=2.0
        for it in range(iters):
            i=rng.randrange(len(ds)); old=starts[i]; starts[i]=rng.randrange(ds[i])
            new=score(L,ds,starts)
            if new<=cur or rng.random()<math.exp((cur-new)/T): cur=new
            else: starts[i]=old
            T=max(0.05,T*0.99997)
            if cur<best[0]: best=(cur,list(starts))
            if cur==0: return 0,starts
        rng.seed(seed+rs+1)
    return best
if __name__=="__main__":
    Ls=[int(a) for a in sys.argv[1].split(",")]; iters=int(sys.argv[2]) if len(sys.argv)>2 else 60000; out=[]
    for L in Ls:
        t=time.time(); b,st=best_bare(L,iters=iters); sig=sum(divisors(L))+1
        out.append({"L":L,"best_bare_found":b,"spare_strokes":sig-2*L,"seconds":round(time.time()-t,1)})
        print(f"L={L} best_bare={b} spare={sig-2*L} t={time.time()-t:.0f}s",flush=True); json.dump(out,open("r7-score.json","w"),indent=1)
        if b==0: print("!!! ZERO — verify by hand before believing",st)
    print("SCORE DONE")
